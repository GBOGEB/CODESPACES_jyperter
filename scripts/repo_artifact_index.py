#!/usr/bin/env python3
"""Build a deterministic, offline-searchable inventory of tracked repository artifacts.

Outputs:
  triage/repo_index/ARTIFACT_INDEX.yaml  - grouped by artifact type, paths alphabetical
  triage/repo_index/FILE_INDEX.tsv       - flat grep-friendly inventory

Search examples:
  python scripts/repo_artifact_index.py --grep QPLANT
  python scripts/repo_artifact_index.py --grep "ALAT|compliance" --regex --scope CORE
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "triage" / "repo_index"
YAML_PATH = OUT_DIR / "ARTIFACT_INDEX.yaml"
TSV_PATH = OUT_DIR / "FILE_INDEX.tsv"
GENERATED = {
    "triage/repo_index/ARTIFACT_INDEX.yaml",
    "triage/repo_index/FILE_INDEX.tsv",
}
SCOPES = ("CORE", "ENVIRONMENT_VENDOR", "ARCHIVE_BACKUP", "GENERATED_OUTPUT")
ENVIRONMENT_ROOTS = {"venv", ".venv", "node_modules", "vendor", "site-packages"}
ARCHIVE_ROOTS = {"archive", "archives", "backup", "backups"}
OUTPUT_ROOTS = {
    "build", "dist", "output", "outputs", "generated", "metrics", ".gui_runs", ".ndjson"
}
TEXT_EXTENSIONS = {
    ".bat", ".c", ".cfg", ".conf", ".cpp", ".css", ".csv", ".env", ".h",
    ".html", ".ini", ".ipynb", ".java", ".js", ".json", ".jsx", ".log",
    ".md", ".mjs", ".ps1", ".py", ".rst", ".sh", ".sql", ".toml", ".ts",
    ".tsx", ".txt", ".xml", ".yaml", ".yml",
}
TYPE_NAMES = {
    ".bat": "Batch", ".c": "C", ".cfg": "Config", ".conf": "Config",
    ".cpp": "C++", ".css": "CSS", ".csv": "CSV", ".doc": "DOC",
    ".docx": "DOCX", ".h": "Header", ".html": "HTML", ".ini": "INI",
    ".ipynb": "Notebook", ".java": "Java", ".js": "JavaScript", ".json": "JSON",
    ".jsx": "JavaScript", ".md": "Markdown", ".mjs": "JavaScript", ".pdf": "PDF",
    ".png": "PNG", ".ppt": "PPT", ".pptx": "PPTX", ".ps1": "PowerShell",
    ".py": "Python", ".rst": "RST", ".sh": "Shell", ".sql": "SQL",
    ".svg": "SVG", ".toml": "TOML", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".txt": "Text", ".xls": "XLS", ".xlsx": "XLSX", ".xml": "XML",
    ".yaml": "YAML", ".yml": "YAML", ".zip": "ZIP",
}


def run_git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def tracked_paths() -> list[str]:
    raw = subprocess.check_output(["git", "-C", str(ROOT), "ls-files", "-z"])
    return sorted(
        (p.decode("utf-8", errors="surrogateescape") for p in raw.split(b"\0") if p),
        key=str.casefold,
    )


def git_mode_sha(path: str) -> tuple[str, str]:
    line = run_git("ls-files", "-s", "--", path)
    if not line:
        return "", ""
    first = line.splitlines()[0]
    mode, obj_sha, _stage_path = first.split(maxsplit=2)
    return mode, obj_sha


def artifact_type(path: str, mode: str) -> str:
    if mode == "160000":
        return "Gitlink"
    name = Path(path).name
    if name == "Dockerfile" or name.startswith("Dockerfile."):
        return "Dockerfile"
    if name == "Makefile":
        return "Makefile"
    if name.upper().startswith("LICENSE"):
        return "License"
    suffix = Path(path).suffix.lower()
    return TYPE_NAMES.get(suffix, suffix[1:].upper() if suffix else "No extension")


def artifact_scope(path: str) -> str:
    p = Path(path)
    parts = [part.casefold() for part in p.parts]
    first = parts[0] if parts else ""
    name = p.name.casefold()
    if first in ENVIRONMENT_ROOTS or any(part in {"site-packages", "node_modules"} for part in parts):
        return "ENVIRONMENT_VENDOR"
    if first in ARCHIVE_ROOTS or ".backup_" in name or name.endswith((".bak", ".bak2", ".old", ".orig")):
        return "ARCHIVE_BACKUP"
    if first in OUTPUT_ROOTS or "/generated/" in f"/{path.casefold()}/":
        return "GENERATED_OUTPUT"
    return "CORE"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def build_records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for rel in tracked_paths():
        if rel in GENERATED:
            continue
        mode, git_sha = git_mode_sha(rel)
        full = ROOT / rel
        kind = "gitlink" if mode == "160000" else "file"
        if full.is_file():
            size = full.stat().st_size
            digest = sha256_file(full)
        else:
            size = 0
            digest = git_sha if mode == "160000" else "UNAVAILABLE"
        suffix = full.suffix.lower()
        records.append({
            "path": rel,
            "type": artifact_type(rel, mode),
            "scope": artifact_scope(rel),
            "size_bytes": size,
            "sha256": digest,
            "git_object": git_sha,
            "kind": kind,
            "text_searchable": suffix in TEXT_EXTENSIONS or full.name in {"Makefile", "Dockerfile"},
        })
    return records


def render_yaml(records: list[dict[str, object]]) -> str:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    scopes: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in records:
        groups[str(row["type"])].append(row)
        scopes[str(row["scope"])].append(row)
    source_sha = run_git("rev-parse", "HEAD")
    repo = run_git("config", "--get", "remote.origin.url") or "unknown"
    lines = [
        "schema: triage-repo-artifact-index/v0.2",
        f"repository: {yaml_quote(repo)}",
        f"indexed_source_sha: {source_sha}",
        f"artifact_count: {len(records)}",
        f"total_size_bytes: {sum(int(r['size_bytes']) for r in records)}",
        "ordering: artifact_type_then_path_casefold",
        "scope_summary:",
    ]
    for scope in SCOPES:
        rows = scopes.get(scope, [])
        lines.extend([
            f"  {scope}:",
            f"    count: {len(rows)}",
            f"    total_size_bytes: {sum(int(r['size_bytes']) for r in rows)}",
        ])
    lines.extend([
        "generated_files_excluded:",
        *[f"  - {yaml_quote(p)}" for p in sorted(GENERATED, key=str.casefold)],
        "artifact_types:",
    ])
    for type_name in sorted(groups, key=str.casefold):
        rows = sorted(groups[type_name], key=lambda r: str(r["path"]).casefold())
        lines.extend([
            f"  {yaml_quote(type_name)}:",
            f"    count: {len(rows)}",
            f"    total_size_bytes: {sum(int(r['size_bytes']) for r in rows)}",
            "    artifacts:",
        ])
        for row in rows:
            lines.extend([
                f"      - path: {yaml_quote(str(row['path']))}",
                f"        scope: {row['scope']}",
                f"        kind: {row['kind']}",
                f"        size_bytes: {row['size_bytes']}",
                f"        sha256: {yaml_quote(str(row['sha256']))}",
                f"        git_object: {yaml_quote(str(row['git_object']))}",
                f"        text_searchable: {'true' if row['text_searchable'] else 'false'}",
            ])
    return "\n".join(lines) + "\n"


def render_tsv(records: list[dict[str, object]]) -> str:
    header = "type\tscope\tpath\tkind\tsize_bytes\tsha256\tgit_object\ttext_searchable\n"
    rows = []
    for row in sorted(records, key=lambda r: (str(r["type"]).casefold(), str(r["path"]).casefold())):
        rows.append("\t".join([
            str(row["type"]), str(row["scope"]), str(row["path"]), str(row["kind"]),
            str(row["size_bytes"]), str(row["sha256"]), str(row["git_object"]),
            "1" if row["text_searchable"] else "0",
        ]))
    return header + "\n".join(rows) + "\n"


def grep_repo(pattern: str, regex: bool, case_sensitive: bool, max_matches: int, scope: str | None) -> int:
    flags = 0 if case_sensitive else re.IGNORECASE
    expr = re.compile(pattern if regex else re.escape(pattern), flags)
    matches = 0
    for row in build_records():
        if scope and row["scope"] != scope:
            continue
        if not row["text_searchable"]:
            continue
        path = ROOT / str(row["path"])
        if not path.is_file():
            continue
        try:
            with path.open("r", encoding="utf-8", errors="replace") as handle:
                for lineno, line in enumerate(handle, 1):
                    if expr.search(line):
                        print(f"{row['scope']}\t{row['path']}:{lineno}:{line.rstrip()}")
                        matches += 1
                        if matches >= max_matches:
                            return 0
        except OSError as exc:
            print(f"WARN {row['path']}: {exc}", file=sys.stderr)
    return 0 if matches else 1


def write_outputs(records: list[dict[str, object]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    YAML_PATH.write_text(render_yaml(records), encoding="utf-8")
    TSV_PATH.write_text(render_tsv(records), encoding="utf-8")


def check_outputs(records: list[dict[str, object]]) -> int:
    expected = {YAML_PATH: render_yaml(records), TSV_PATH: render_tsv(records)}
    failures = []
    for path, content in expected.items():
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            failures.append(str(path.relative_to(ROOT)))
    if failures:
        print("OUT_OF_DATE " + " ".join(failures))
        return 1
    print(f"PASS artifact_index count={len(records)} size={sum(int(r['size_bytes']) for r in records)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write YAML and TSV inventory")
    parser.add_argument("--check", action="store_true", help="verify committed inventory matches tracked files")
    parser.add_argument("--grep", help="offline search across text-capable tracked files")
    parser.add_argument("--regex", action="store_true", help="treat --grep as a regular expression")
    parser.add_argument("--case-sensitive", action="store_true")
    parser.add_argument("--scope", choices=SCOPES, help="limit grep to one artifact scope")
    parser.add_argument("--max-matches", type=int, default=500)
    args = parser.parse_args()
    if args.grep is not None:
        return grep_repo(args.grep, args.regex, args.case_sensitive, args.max_matches, args.scope)
    records = build_records()
    if args.write:
        write_outputs(records)
    if args.check:
        return check_outputs(records)
    if not args.write and not args.check:
        by_scope: dict[str, int] = defaultdict(int)
        by_type: dict[str, int] = defaultdict(int)
        for row in records:
            by_scope[str(row["scope"])] += 1
            by_type[str(row["type"])] += 1
        for scope in SCOPES:
            print(f"SCOPE\t{scope}\t{by_scope[scope]}")
        for key in sorted(by_type, key=str.casefold):
            print(f"TYPE\t{key}\t{by_type[key]}")
        print(f"TOTAL\t{len(records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
