#!/usr/bin/env python3
"""Update hash values in GLOBAL_index.json and any section index files that
share the same artefact entries (e.g. docs/diagrams/index.json).

Both files must stay in sync; this script refreshes all of them in one pass
so that running it never leaves hashes inconsistent between the global index
and the section indices.
"""
import argparse
import hashlib
import json
from pathlib import Path

# Section index files that mirror a subset of GLOBAL_index.json artefacts.
# Extend this list whenever a new section index is added to the repository.
_SECTION_INDICES = [
    "docs/diagrams/index.json",
]


def file_hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _refresh_index(path: Path, hash_map: dict[str, str]) -> None:
    """Rewrite *path* with updated hashes from *hash_map* (id -> new hash)."""
    idx = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    for art in idx.get("artefacts", []):
        new_hash = hash_map.get(art.get("id", ""))
        if new_hash is not None and art.get("hash") != new_hash:
            art["hash"] = new_hash
            changed = True
    if changed:
        path.write_text(json.dumps(idx, indent=2), encoding="utf-8")
        print("UPDATED", path)


def main() -> None:
    """Refresh artifact hashes stored in the supplied global index file."""
    ap = argparse.ArgumentParser(
        description="Refresh artefact hashes in GLOBAL_index.json and section indices."
    )
    ap.add_argument("--index", required=True, help="Path to GLOBAL_index.json")
    args = ap.parse_args()

    path = Path(args.index)
    idx = json.loads(path.read_text(encoding="utf-8"))

    # Build id -> new_hash map while updating the global index in memory.
    hash_map: dict[str, str] = {}
    for art in idx.get("artefacts", []):
        p = Path(art["path"])
        if p.exists():
            new_hash = file_hash(p)
            art["hash"] = new_hash
            hash_map[art["id"]] = new_hash

    path.write_text(json.dumps(idx, indent=2), encoding="utf-8")
    print("UPDATED", path)

    # Propagate updated hashes to section indices.
    root = path.parent
    for rel in _SECTION_INDICES:
        section_path = root / rel
        if section_path.exists():
            _refresh_index(section_path, hash_map)


if __name__ == "__main__":
    main()
