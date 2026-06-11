#!/usr/bin/env python3
"""Compare artifact hashes in an index file against the files on disk.

Exits with code 1 if any indexed artifact hash differs from the current
on-disk content; exits 0 when everything matches.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

def file_hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    """Exit nonzero when any indexed artifact hash differs from disk."""
    ap = argparse.ArgumentParser(
        description="Verify that artifact hashes stored in an index file match disk."
    )
    ap.add_argument("--index", required=True, help="Path to the index JSON file")
    args = ap.parse_args()

    idx = json.loads(Path(args.index).read_text(encoding="utf-8"))
    artifacts = idx.get("artefacts", [])
    had_diff = False

    for a in artifacts:
        raw_path = a.get("path")
        if not raw_path:
            print(f"[WARN] artefact entry missing 'path' field: {a.get('id', '<unknown>')}")
            continue
        path = Path(raw_path)
        if not path.exists():
            print(f"[WARN] missing {path}")
            continue
        new_hash = file_hash(path)
        old_hash = a.get("hash", "")
        if old_hash and new_hash != old_hash:
            print(f"[DIFF] {path} hash changed")
            had_diff = True
    sys.exit(1 if had_diff else 0)


if __name__ == "__main__":
    main()
