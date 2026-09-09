#!/usr/bin/env python3
"""Compatibility entrypoint for the workspace index.

The original implementation recursively scanned every Python file and therefore treated the
checked-in ``venv/`` tree as authored engineering content. The repository now has a richer,
deterministic artifact census in ``scripts/repo_artifact_index.py`` that classifies CORE,
ENVIRONMENT_VENDOR, ARCHIVE_BACKUP and GENERATED_OUTPUT content and supports offline grep.

This module preserves the historical ``python app/index_repo.py`` command while delegating
index generation to that canonical implementation. It also writes a compact ``INDEX.md``
summary for humans, derived from the generated TSV rather than a second filesystem crawl.
"""
from __future__ import annotations

import csv
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_SCRIPT = ROOT / "scripts" / "repo_artifact_index.py"
TSV = ROOT / "triage" / "repo_index" / "FILE_INDEX.tsv"
OUT = ROOT / "INDEX.md"


def regenerate() -> None:
    subprocess.run([sys.executable, str(INDEX_SCRIPT), "--write"], cwd=ROOT, check=True)


def load_rows() -> list[dict[str, str]]:
    with TSV.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def render(rows: list[dict[str, str]]) -> str:
    by_scope = Counter(row["scope"] for row in rows)
    bytes_by_scope: dict[str, int] = defaultdict(int)
    by_type = Counter(row["type"] for row in rows)
    core = [row for row in rows if row["scope"] == "CORE"]
    largest_core = sorted(core, key=lambda r: int(r["size_bytes"]), reverse=True)[:25]

    lines = [
        "# WORKSPACE INDEX",
        "",
        "> Generated from `triage/repo_index/FILE_INDEX.tsv`. Do not infer engineering density from",
        "> raw repository file counts; environment/vendor content is classified separately.",
        "",
        "## Scope Summary",
        "",
        "| Scope | Files | Bytes |",
        "| --- | ---: | ---: |",
    ]
    for scope in ("CORE", "ENVIRONMENT_VENDOR", "ARCHIVE_BACKUP", "GENERATED_OUTPUT"):
        lines.append(f"| {scope} | {by_scope.get(scope, 0)} | {bytes_by_scope.get(scope, 0)} |")
    lines += ["", "## Artifact Types", ""]
    for kind in sorted(by_type, key=str.casefold):
        lines.append(f"- **{kind}**: {by_type[kind]}")
    lines += ["", "## Largest CORE Artifacts", ""]
    for row in largest_core:
        lines.append(f"- `{row['path']}` ({row['size_bytes']} bytes; {row['type']})")
    lines += [
        "",
        "## Offline Search",
        "",
        "```bash",
        "python scripts/repo_artifact_index.py --grep QPLANT --scope CORE",
        "python scripts/repo_artifact_index.py --grep 'helium|heat balance|relief' --regex --scope CORE",
        "python scripts/repo_artifact_index.py --grep 'RTM|compliance|negotiation' --regex --scope CORE",
        "```",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    regenerate()
    rows = load_rows()
    for row in rows:
        # Keep byte arithmetic in one place and avoid a second filesystem scan.
        pass
    global_bytes = defaultdict(int)
    for row in rows:
        global_bytes[row["scope"]] += int(row["size_bytes"])
    # render() intentionally computes structure from TSV; inject byte totals by rebuilding the
    # small table here to keep compatibility and readability.
    by_scope = Counter(row["scope"] for row in rows)
    by_type = Counter(row["type"] for row in rows)
    core = [row for row in rows if row["scope"] == "CORE"]
    largest_core = sorted(core, key=lambda r: int(r["size_bytes"]), reverse=True)[:25]
    lines = [
        "# WORKSPACE INDEX",
        "",
        "> Generated from `triage/repo_index/FILE_INDEX.tsv`. The checked-in environment/vendor",
        "> tree is intentionally separated from authored engineering content.",
        "",
        "## Scope Summary",
        "",
        "| Scope | Files | Bytes |",
        "| --- | ---: | ---: |",
    ]
    for scope in ("CORE", "ENVIRONMENT_VENDOR", "ARCHIVE_BACKUP", "GENERATED_OUTPUT"):
        lines.append(f"| {scope} | {by_scope.get(scope, 0)} | {global_bytes.get(scope, 0)} |")
    lines += ["", "## Artifact Types", ""]
    for kind in sorted(by_type, key=str.casefold):
        lines.append(f"- **{kind}**: {by_type[kind]}")
    lines += ["", "## Largest CORE Artifacts", ""]
    for row in largest_core:
        lines.append(f"- `{row['path']}` ({row['size_bytes']} bytes; {row['type']})")
    lines += [
        "",
        "## Offline Search",
        "",
        "```bash",
        "python scripts/repo_artifact_index.py --grep QPLANT --scope CORE",
        "python scripts/repo_artifact_index.py --grep 'helium|heat balance|relief' --regex --scope CORE",
        "python scripts/repo_artifact_index.py --grep 'RTM|compliance|negotiation' --regex --scope CORE",
        "```",
        "",
    ]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT} from {TSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
