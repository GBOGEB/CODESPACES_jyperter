"""Regression guards for canonical-source versus disposable/generated state."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _tracked_paths() -> set[str]:
    raw = subprocess.check_output(["git", "-C", str(ROOT), "ls-files", "-z"])
    return {
        item.decode("utf-8", errors="surrogateescape")
        for item in raw.split(b"\0")
        if item
    }


def test_virtual_environments_are_not_tracked() -> None:
    tracked = _tracked_paths()
    forbidden_prefixes = ("venv/", ".venv/", "env/", "ENV/")
    offenders = sorted(
        path for path in tracked if path.startswith(forbidden_prefixes)
    )
    assert offenders == [], (
        "virtual-environment state must be reconstructed from declared "
        f"dependencies, not committed: {offenders[:10]}"
    )


def test_generated_repository_census_is_not_tracked() -> None:
    tracked = _tracked_paths()
    generated = {
        "triage/repo_index/ARTIFACT_INDEX.yaml",
        "triage/repo_index/FILE_INDEX.tsv",
    }
    assert tracked.isdisjoint(generated), (
        "repository census is generated evidence and must not be canonical source"
    )


def test_hygiene_receipt_is_present() -> None:
    receipt = ROOT / "triage" / "repo_hygiene" / "P1_REPOSITORY_HYGIENE_CURRENT.yaml"
    assert receipt.is_file()
    text = receipt.read_text(encoding="utf-8")
    assert "authority_transfer: false" in text
    assert "PC3_LEVEL1_CANDIDATE" in text
