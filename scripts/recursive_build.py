#!/usr/bin/env python3
"""Stub recursive build script.
Parses GLOBAL_index.json and writes a generated metrics file.

The default output path is ``metrics/generated_metrics.json`` to avoid
colliding with the curated KPI document at ``metrics/metrics.json``.
"""
import argparse
import json
from pathlib import Path

def main() -> None:
    """Write a small metrics file from the supplied global index."""
    ap = argparse.ArgumentParser(
        description="Parse GLOBAL_index.json and emit a generated metrics file."
    )
    ap.add_argument("--index", required=True, help="Path to GLOBAL_index.json")
    ap.add_argument(
        "--out",
        default="metrics/generated_metrics.json",
        help="Output path for the generated metrics file (default: metrics/generated_metrics.json)",
    )
    ap.add_argument("--smoke", action="store_true", help="Set smoke flag in output")
    args = ap.parse_args()

    idx = json.loads(Path(args.index).read_text(encoding="utf-8"))
    metrics = {
        "artefact_count": len(idx.get("artefacts", [])),
        "smoke": args.smoke,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print("WROTE", args.out)

if __name__ == "__main__":
    main()
