#!/usr/bin/env python3
"""Validate or refresh the curated GLOBAL_index.json.

GLOBAL_index.json is a small, curated structural/lineage index. It is not the
full repository census; the latter lives under triage/repo_index and is built by
scripts/repo_artifact_index.py.

This checker deliberately preserves baselines and artefacts instead of replacing
the rich index with only {directories, sections}.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REPOSITORY = "GBOGEB/CODESPACES_jyperter"
SCHEMA = "1.0"
SECTIONS = [
    {"id": "SEC-01", "title": "Execution Flow Diagram", "status": "planned"},
    {"id": "SEC-02", "title": "Makefile and VSCode Tasking", "status": "planned"},
    {"id": "SEC-03", "title": "Recursive Model", "status": "planned"},
    {"id": "SEC-04", "title": "Artefact Structure", "status": "planned"},
    {"id": "SEC-05", "title": "Patch and ZIP Bundles", "status": "planned"},
    {"id": "SEC-06", "title": "GitHub Workflow Steps", "status": "planned"},
    {"id": "SEC-07", "title": "Semantic Tracking Spec", "status": "planned"},
]


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_index(root: Path, data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    if data.get("repository") != REPOSITORY:
        errors.append(f"repository must be {REPOSITORY}")
    if data.get("sections") != SECTIONS:
        errors.append("sections differ from controlled SEC-01..SEC-07 table")

    directories = data.get("directories")
    if not isinstance(directories, list):
        errors.append("directories must be an array")
    else:
        if directories != sorted(set(directories), key=str.casefold):
            errors.append("directories must be unique and alphabetically sorted")
        for rel in directories:
            if not isinstance(rel, str) or not (root / rel).is_dir():
                errors.append(f"indexed directory missing: {rel!r}")

    baselines = data.get("baselines")
    baseline_tags: set[str] = set()
    if not isinstance(baselines, list):
        errors.append("baselines must be an array")
    else:
        for row in baselines:
            if not isinstance(row, dict) or not row.get("tag"):
                errors.append("every baseline must have a tag")
                continue
            tag = str(row["tag"])
            if tag in baseline_tags:
                errors.append(f"duplicate baseline tag: {tag}")
            baseline_tags.add(tag)

    artefacts = data.get("artefacts")
    artifact_ids: set[str] = set()
    if not isinstance(artefacts, list):
        errors.append("artefacts must be an array")
    else:
        for row in artefacts:
            if not isinstance(row, dict):
                errors.append("every artefact must be an object")
                continue
            artifact_id = str(row.get("id", ""))
            rel = str(row.get("path", ""))
            if not artifact_id or artifact_id in artifact_ids:
                errors.append(f"duplicate or missing artefact id: {artifact_id!r}")
            artifact_ids.add(artifact_id)
            if row.get("baseline_tag") not in baseline_tags:
                errors.append(f"unknown baseline for {artifact_id}: {row.get('baseline_tag')!r}")
            path = root / rel
            if not rel or not path.is_file():
                errors.append(f"artefact path missing for {artifact_id}: {rel!r}")
                continue
            expected = file_hash(path)
            if row.get("hash") != expected:
                errors.append(f"hash mismatch for {artifact_id}: {rel}")

    return errors


def refresh_index(root: Path, data: dict[str, Any]) -> dict[str, Any]:
    """Normalize controlled fields while preserving curated lineage metadata."""
    data["schema"] = SCHEMA
    data["repository"] = REPOSITORY
    data["sections"] = SECTIONS
    directories = [str(x) for x in data.get("directories", []) if (root / str(x)).is_dir()]
    data["directories"] = sorted(set(directories), key=str.casefold)
    for row in data.get("artefacts", []):
        if not isinstance(row, dict):
            continue
        path = root / str(row.get("path", ""))
        if path.is_file():
            row["hash"] = file_hash(path)
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate without modifying GLOBAL_index.json")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    index_path = root / "GLOBAL_index.json"
    if not index_path.exists():
        print("GLOBAL_index.json is missing")
        return 1

    data = json.loads(index_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        print("GLOBAL_index.json must contain a JSON object")
        return 1

    if args.check:
        errors = validate_index(root, data)
        if errors:
            for error in errors:
                print(f"FAIL: {error}")
            return 1
        print(f"PASS GLOBAL_index artefacts={len(data.get('artefacts', []))} directories={len(data.get('directories', []))}")
        return 0

    data = refresh_index(root, data)
    index_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    errors = validate_index(root, data)
    if errors:
        for error in errors:
            print(f"FAIL after refresh: {error}")
        return 1
    print("UPDATED GLOBAL_index.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
