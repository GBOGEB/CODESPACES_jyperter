#!/usr/bin/env python3
"""
pandoc_export.py — convert MD to DOCX/PDF using Pandoc if installed
"""
import subprocess, sys, shutil, pathlib

def convert(md_path: str, out_docx: str = None, out_pdf: str = None):
    if shutil.which("pandoc") is None:
        print("[warn] Pandoc not found; please install to enable conversions.")
        return
    if out_docx:
        subprocess.run(["pandoc", md_path, "-o", out_docx], check=True)
    if out_pdf:
        subprocess.run(["pandoc", md_path, "-o", out_pdf], check=True)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: pandoc_export.py input.md output.docx [output.pdf]")
        sys.exit(1)
    md = sys.argv[1]; docx = sys.argv[2]
    pdf = sys.argv[3] if len(sys.argv) > 3 else None
    convert(md, docx, pdf)
