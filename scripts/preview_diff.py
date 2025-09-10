#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

def file_hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["in", "out", "both"], default="both")
    ap.add_argument("--index", required=True)
    args = ap.parse_args()

    idx = json.loads(Path(args.index).read_text(encoding="utf-8"))
    artifacts = idx.get("artefacts", [])
    had_diff = False

    for a in artifacts:
        path = Path(a["path"])
        if not path.exists():
            print(f"[WARN] missing {path}")
            continue
        new_hash = file_hash(path)
        old_hash = a.get("hash", "")
        if old_hash and new_hash != old_hash:
            print(f"[DIFF] {path} hash changed")
            had_diff = True
    raise SystemExit(1 if had_diff else 0)

if __name__ == "__main__":
    main()
