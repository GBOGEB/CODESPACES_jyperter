# MCP GUI candidate bundle

A human-centric launcher for the MCP recursive handover lane.

## Interfaces

- Flask: `python gui_candidate_bundle/gui_flask.py`
- Tkinter: `python gui_candidate_bundle/gui_launcher.py`
- Status API: `GET http://127.0.0.1:5000/api/status`
- Focused tests: `python -m pytest -q gui_candidate_bundle/tests`

Install focused dependencies with:

```bash
python -m pip install -r gui_candidate_bundle/requirements.txt
```

The dashboard binds local state from `handover_manifest.json` and can enrich **BLOCK 2 / S2** with the latest run of `.github/workflows/mcp-gui-candidate.yml`. Set `GITHUB_TOKEN` when needed; public-repository reads can also work without a token. Override repository/workflow/branch with `GITHUB_REPO`, `MCP_GITHUB_WORKFLOW`, and `MCP_GITHUB_BRANCH`.

The GUI does not convert missing evidence into success. A missing parser is displayed and recorded as `BLOCKED`. Manifest writes preserve unrelated fields.
