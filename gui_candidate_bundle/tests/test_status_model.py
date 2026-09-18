import json
from pathlib import Path

from gui_candidate_bundle.status_model import (
    build_steps,
    load_manifest,
    normalize_status,
    write_step_status,
)


def test_normalize_github_states():
    assert normalize_status("success") == "success"
    assert normalize_status("failure") == "fail"
    assert normalize_status("in_progress") == "running"
    assert normalize_status("cancelled") == "cancelled"
    assert normalize_status("unexpected-value") == "unknown"


def test_manifest_write_preserves_unrelated_fields(tmp_path: Path):
    manifest = tmp_path / "handover_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "lineage": {"sha": "abc"},
                "step_status": {"S1": "success"},
            }
        ),
        encoding="utf-8",
    )

    write_step_status(
        manifest,
        "S4",
        "failure",
        "unit-test red",
    )
    data = load_manifest(manifest)

    assert data["lineage"] == {"sha": "abc"}
    assert data["step_status"]["S1"] == "success"
    assert data["step_status"]["S4"] == "fail"
    assert data["step_evidence"]["S4"]["detail"] == "unit-test red"


def test_github_evidence_overrides_manifest_for_same_step():
    manifest = {
        "step_status": {
            "S2": "fail",
            "S3": "success",
        }
    }
    steps = build_steps(
        manifest,
        {
            "S2": {
                "status": "success",
                "detail": "CI #12",
            }
        },
    )
    by_id = {step["id"]: step for step in steps}

    assert by_id["S2"]["status"] == "success"
    assert by_id["S2"]["source"] == "github"
    assert by_id["S3"]["source"] == "manifest"
