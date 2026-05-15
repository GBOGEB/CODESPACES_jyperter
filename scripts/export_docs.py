#!/usr/bin/env python3
"""Stub document export script.
Copies Markdown files from docs/ to out/.
"""
import argparse
import shutil
from pathlib import Path

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="docs")
    ap.add_argument("--out", default="out")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(exist_ok=True)
    for md in Path(args.src).rglob("*.md"):
        shutil.copy(md, out / md.name)
        print("COPIED", md, "->", out / md.name)

if __name__ == "__main__":
    main()
