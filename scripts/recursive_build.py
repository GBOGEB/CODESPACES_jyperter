#!/usr/bin/env python3
"""Stub recursive build script.
Parses GLOBAL_index.json and writes metrics/metrics.json.
"""
import argparse
import json
from pathlib import Path

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", required=True)
    ap.add_argument("--out", default="metrics/metrics.json")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    idx = json.loads(Path(args.index).read_text(encoding="utf-8"))
    metrics = {
        "artefact_count": len(idx.get("artefacts", [])),
        "smoke": args.smoke,
    }
    Path(args.out).write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print("WROTE", args.out)

if __name__ == "__main__":
    main()
