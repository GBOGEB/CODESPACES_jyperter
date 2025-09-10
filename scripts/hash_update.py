#!/usr/bin/env python3
"""Update hash values in GLOBAL_index.json."""
import argparse
import hashlib
import json
from pathlib import Path

def file_hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", required=True)
    args = ap.parse_args()

    path = Path(args.index)
    idx = json.loads(path.read_text(encoding="utf-8"))
    for art in idx.get("artefacts", []):
        p = Path(art["path"])
        if p.exists():
            art["hash"] = file_hash(p)
    path.write_text(json.dumps(idx, indent=2), encoding="utf-8")
    print("UPDATED", path)

if __name__ == "__main__":
    main()
