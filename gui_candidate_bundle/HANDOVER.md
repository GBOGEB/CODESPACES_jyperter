# BIOS / GLOB handover — MCP GUI candidate

## Authority

Repository authority: `GBOGEB/CODESPACES_jyperter`. This package extends the already-merged MCP GUI lane rather than creating a second dashboard source of truth.

## BIOS seed message

```text
[BIOS HANDOVER :: MCP HUMAN EXECUTION CONSOLE]
Purpose: expose MCP recursive execution as five numbered human-readable blocks.
Primary UI: gui_candidate_bundle/gui_flask.py
Desktop fallback: gui_candidate_bundle/gui_launcher.py
State model: gui_candidate_bundle/status_model.py
SSOT status input: handover_manifest.json
Optional live CI evidence: GitHub Actions workflow mcp-gui-candidate.yml
Safety rule: never infer PASS from missing evidence; missing executable/artefact is shown as BLOCKED/not present.
Human rule: status must be expressed in text and colour; colour alone is non-authoritative.
Next consumer: code editor / Codespaces / committee reviewer.
Run: python gui_candidate_bundle/gui_flask.py
Focused proof: python -m pytest -q gui_candidate_bundle/tests
```

## GLOB seed / restart message

```text
[GLOB :: MCP_GUI_CANDIDATE]
repo=GBOGEB/CODESPACES_jyperter
entry=gui_candidate_bundle/gui_flask.py
state=handover_manifest.json
status_api=/api/status
blocks=S1..S5
ci=.github/workflows/mcp-gui-candidate.yml
proof=python -m pytest -q gui_candidate_bundle/tests
invariant=manifest fields preserved on GUI writes
invariant=repository path traversal denied
invariant=GitHub API absence degrades to manifest/default, never false PASS
invariant=Mermaid/cards/API share one status model
next=connect concrete producer receipts for S1/S3/S4/S5 as those executors become repository-native
```

## 3P* + MIP receipt

- 3PR Refresh: current `main`, prior GUI merge lineage, existing CI conventions, and open PR state refreshed.
- 3PR Probe: prototype defects identified: non-existent artefact links, destructive manifest write, weak status semantics, unsafe open route, and no focused CI.
- 3PR Rank: P0 preserve manifest/evidence truth; P1 safe human rendering and tests; P2 optional live CI enrichment.
- MIP Modernize: shared status model, repository-root pathing, POST execution, atomic manifest write, bounded API timeout.
- MIP Innovate: cards + Mermaid + JSON use one model with numbered blocks and accessible text+colour status.
- MIP Perpetuate: focused pytest suite, dedicated workflow, BIOS/GLOB restart contract.
