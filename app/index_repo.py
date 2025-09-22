import pathlib
import os
import re
import json
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "INDEX.md"

EXCLUDE = {".git", ".venv", "__pycache__", ".mypy_cache", ".pytest_cache", ".vscode", ".idea"}

def tree(path, prefix=""):
    entries = [e for e in sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower())) if e.name not in EXCLUDE]
    lines = []
    for i, e in enumerate(entries):
        tee = "└── " if i == len(entries) - 1 else "├── "
        lines.append(prefix + tee + e.name)
        if e.is_dir():
            ext = "    " if i == len(entries) - 1 else "│   "
            lines.extend(tree(e, prefix + ext))
    return lines

def main_files(root: pathlib.Path, k=20):
    code = list(root.rglob("*.py"))
    return sorted(code, key=lambda p: p.stat().st_size, reverse=True)[:k]

def word_cloud(root: pathlib.Path, k=50):
    words = Counter()
    for p in root.rglob("*.py"):
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        words.update(w for w in re.findall(r"[A-Za-z_]{3,}", txt) if not w.isupper())
    return words.most_common(k)

def write_index():
    lines = []
    lines += ["# WORKSPACE INDEX", ""]
    lines += ["## Directory Tree", "```text", *tree(ROOT), "```", ""]
    lines += ["## Main Files (by size)"]
    for p in main_files(ROOT):
        lines.append(f"- `{p.relative_to(ROOT)}` ({p.stat().st_size} bytes)")
    lines += ["", "## Word Cloud (top tokens)"]
    wc = word_cloud(ROOT)
    lines += ["```text", *[f"{w:>20} : {n}" for w, n in wc], "```", ""]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    write_index()
