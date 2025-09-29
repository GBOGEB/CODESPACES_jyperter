#!/usr/bin/env python3
"""Generate a JSON index of repository directories and pipeline sections."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

EXCLUDE = {'.git', '__pycache__', '.pytest_cache'}

# Static section table used for high level project tracking.  The IDs mirror
# the "SEC-*" labels referenced in design discussions and provide a minimal
# status field that tooling can inspect or update.
SECTIONS = [
    {"id": "SEC-01", "title": "Execution Flow Diagram", "status": "planned"},
    {"id": "SEC-02", "title": "Makefile and VSCode Tasking", "status": "planned"},
    {"id": "SEC-03", "title": "Recursive Model", "status": "planned"},
    {"id": "SEC-04", "title": "Artefact Structure", "status": "planned"},
    {"id": "SEC-05", "title": "Patch and ZIP Bundles", "status": "planned"},
    {"id": "SEC-06", "title": "GitHub Workflow Steps", "status": "planned"},
    {"id": "SEC-07", "title": "Semantic Tracking Spec", "status": "planned"},
]


def list_dirs(root: Path) -> list[str]:
    """Return sorted relative paths of all directories under *root*.

    Args:
        root: Repository root path.

    Returns:
        Sorted list of directory paths relative to *root*, excluding
        version-control and cache directories.
    """

    return sorted(
        str(path.relative_to(root))
        for path in root.rglob('*')
        if path.is_dir() and not any(part in EXCLUDE for part in path.parts)
    )


def build_index(root: Path) -> dict[str, list[str]]:
    """Build index data structure for *root*.

    The resulting mapping contains both the directory listing and an initial
    set of section descriptors used for traceability across documentation and
    tooling.
    """

    return {"directories": list_dirs(root), "sections": SECTIONS}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check", action="store_true", help="only verify index is up-to-date"
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    index_path = root / "GLOBAL_index.json"
    data = build_index(root)

    if args.check:
        if not index_path.exists():
            print("GLOBAL_index.json is missing")
            return 1
        existing = json.loads(index_path.read_text())
        if existing != data:
            print("GLOBAL_index.json is out of date")
            return 1
        return 0

    index_path.write_text(json.dumps(data, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
