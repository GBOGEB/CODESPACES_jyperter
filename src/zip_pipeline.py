from __future__ import annotations

"""Utilities for processing collections of ZIP archives.

This module discovers ZIP files inside one or more base directories and
processes them sequentially.  For each archive the following steps are
performed:

1. Extract the ZIP to a temporary directory.
2. Run smoke tests by byte-compiling all Python files.
3. Run an optional dry run if a ``run_pipeline.py`` script is present.
4. Execute integration tests via ``pytest``.
5. Remove the original ZIP file once processing succeeds.

The module is intentionally simple and aims to provide a reliable example
of how a ZIP processing pipeline could be automated.  It can be invoked as a
script or its functions can be imported and reused.
"""

from pathlib import Path
import subprocess
import tempfile
import zipfile
from typing import Iterable, List


def discover_zip_files(base_dirs: Iterable[str]) -> List[Path]:
    """Return a sorted list of all ``.zip`` files under ``base_dirs``."""
    paths: List[Path] = []
    for base in base_dirs:
        paths.extend(Path(base).rglob("*.zip"))
    return sorted(paths)


def run_smoke_tests(extracted_dir: str | Path) -> None:
    """Byte-compile all Python files to ensure they are syntactically valid."""
    extracted = Path(extracted_dir)
    py_files = list(extracted.rglob("*.py"))
    if not py_files:
        return
    cmd = ["python", "-m", "py_compile", *map(str, py_files)]
    subprocess.run(cmd, check=True)


def run_dry_run(extracted_dir: str | Path) -> None:
    """Execute ``run_pipeline.py --dry-run`` if the script exists."""
    candidate = Path(extracted_dir) / "run_pipeline.py"
    if candidate.exists():
        subprocess.run(["python", str(candidate), "--dry-run"], check=True)


def run_integration_tests(extracted_dir: str | Path) -> None:
    """Run ``pytest`` inside the extracted directory.

    ``pytest`` returns exit code 5 when no tests are collected.  This is not
    considered a failure for the purposes of the pipeline.
    """
    result = subprocess.run(["pytest"], cwd=extracted_dir)
    if result.returncode not in (0, 5):
        raise subprocess.CalledProcessError(result.returncode, result.args)


def process_zip(zip_path: str | Path) -> None:
    """Process ``zip_path`` using the defined pipeline and delete the archive."""
    zip_path = Path(zip_path)
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmpdir)
        run_smoke_tests(tmpdir)
        run_dry_run(tmpdir)
        run_integration_tests(tmpdir)
    zip_path.unlink()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process ZIP archives")
    parser.add_argument("base_dirs", nargs="+", help="Directories to search for ZIP files")
    args = parser.parse_args()

    for zip_file in discover_zip_files(args.base_dirs):
        process_zip(zip_file)
