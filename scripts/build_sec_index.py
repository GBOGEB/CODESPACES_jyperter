#!/usr/bin/env python3
"""Generate index.json from SEC sections in markdown files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC_RE = re.compile(r"^(SEC-\d+):\s*(.*)")


def collect_sections(root: Path) -> list[dict[str, str]]:
    """Collect SEC sections from all markdown files under *root*."""
    sections: list[dict[str, str]] = []
    for path in root.rglob("*.md"):
        for line in path.read_text(encoding="utf-8").splitlines():
            match = SEC_RE.match(line)
            if match:
                sections.append(
                    {"id": match.group(1), "title": match.group(2), "file": str(path.relative_to(root))}
                )
    return sections


def build_index(root: Path) -> dict[str, list[dict[str, str]]]:
    return {"sections": collect_sections(root)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="only verify index is up to date")
    args = parser.parse_args()

    index_path = ROOT / "sec_index.json"
    data = build_index(ROOT)

    if args.check:
        if not index_path.exists():
            print("sec_index.json is missing")
            return 1
        existing = json.loads(index_path.read_text())
        if existing != data:
            print("sec_index.json is out of date")
            return 1
        return 0

    index_path.write_text(json.dumps(data, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
