from pathlib import Path

import gui_candidate_bundle.gui_flask as gui


def test_home_renders_numbered_blocks_and_text_status(
    monkeypatch,
    tmp_path: Path,
):
    manifest = tmp_path / "handover_manifest.json"
    manifest.write_text(
        '{"step_status":{"S1":"success","S4":"fail"}}',
        encoding="utf-8",
    )
    monkeypatch.setattr(gui, "MANIFEST_PATH", manifest)
    monkeypatch.setattr(gui, "fetch_github_status", lambda: {})

    response = gui.app.test_client().get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "BLOCK 1" in body
    assert "BLOCK 5" in body
    assert "PASS" in body
    assert "FAIL" in body
    assert "Workflow rendering" in body
    assert "Mermaid mirrors the same status model" in body


def test_status_api_matches_manifest(monkeypatch, tmp_path: Path):
    manifest = tmp_path / "handover_manifest.json"
    manifest.write_text(
        '{"step_status":{"S3":"cancelled"}}',
        encoding="utf-8",
    )
    monkeypatch.setattr(gui, "MANIFEST_PATH", manifest)
    monkeypatch.setattr(gui, "fetch_github_status", lambda: {})

    response = gui.app.test_client().get("/api/status")
    payload = response.get_json()
    by_id = {step["id"]: step for step in payload["steps"]}

    assert by_id["S3"]["status"] == "cancelled"
    assert by_id["S3"]["visual"]["label"] == "CANCELLED"


def test_github_run_maps_to_s2(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "workflow_runs": [
                    {
                        "status": "completed",
                        "conclusion": "success",
                        "name": "MCP GUI",
                        "run_number": 42,
                        "updated_at": "2026-09-18T14:00:00Z",
                        "html_url": "https://example.invalid/run/42",
                    }
                ]
            }

    monkeypatch.setattr(
        gui.requests,
        "get",
        lambda *args, **kwargs: Response(),
    )

    status = gui.fetch_github_status()

    assert status["S2"]["status"] == "success"
    assert "#42" in status["S2"]["detail"]


def test_open_artifact_rejects_path_escape():
    response = gui.app.test_client().get(
        "/open/../../etc/passwd"
    )
    assert response.status_code == 404


def test_missing_parser_records_blocked(
    monkeypatch,
    tmp_path: Path,
):
    manifest = tmp_path / "handover_manifest.json"
    manifest.write_text(
        '{"lineage":{"sha":"keep-me"}}',
        encoding="utf-8",
    )
    monkeypatch.setattr(gui, "MANIFEST_PATH", manifest)
    monkeypatch.setattr(
        gui,
        "PARSER_PATH",
        tmp_path / "missing.py",
    )

    response = gui.app.test_client().post(
        "/run_parser",
        follow_redirects=False,
    )
    data = gui.load_manifest(manifest)

    assert response.status_code == 303
    assert data["lineage"]["sha"] == "keep-me"
    assert data["step_status"]["S4"] == "blocked"
