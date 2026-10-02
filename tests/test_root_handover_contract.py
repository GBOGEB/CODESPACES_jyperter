"""Control tests for the repository-level root handover."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROOT_HANDOVER = ROOT / "HANDOVER.md"
HEPAK_ARCHIVE = (
    ROOT
    / "handover"
    / "archive"
    / "HANDOVER_HEPAK_AGENT_INTEGRATION_HELPER_v1.1_2025-08-15.md"
)


def test_root_handover_is_current_repository_control_surface() -> None:
    """The root handover must describe the current repository, not legacy HEPAK."""
    text = ROOT_HANDOVER.read_text(encoding="utf-8")

    required_markers = (
        "# CODESPACES_jyperter — Current Repository Handover",
        "repository_role: `RUNTIME_PROPERTY_NOTEBOOK_WORKER`",
        "level1_status: `PC3_LEVEL1_CANDIDATE`",
        "authority_transfer: `false`",
        "## 9. Next execution order",
        "P1 REPOSITORY HYGIENE CENSUS",
        "P2 PACKAGE IDENTITY RECONCILIATION",
        "P3 LEVEL-1 CLOSURE",
        "P4 RELEASE INFRASTRUCTURE",
    )
    for marker in required_markers:
        assert marker in text, f"root handover missing current control marker: {marker}"

    stale_root_markers = (
        "HEPAK – Agent Integration Helper Refactor",
        "Date: 2025‑08‑15 (Europe/Brussels)",
        "Tag suggestion: integration-helper-v1.1",
    )
    for marker in stale_root_markers:
        assert marker not in text, f"legacy handover content regressed into root: {marker}"


def test_legacy_hepak_handover_is_preserved_as_history() -> None:
    """Historical content remains available without carrying current authority."""
    assert HEPAK_ARCHIVE.is_file()
    archive = HEPAK_ARCHIVE.read_text(encoding="utf-8")
    assert archive.startswith("HEPAK – Agent Integration Helper Refactor")
    assert "Date: 2025‑08‑15 (Europe/Brussels)" in archive
