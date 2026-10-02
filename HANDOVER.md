# CODESPACES_jyperter — Current Repository Handover

handover_date: 2026-10-02  
control_baseline_main: `641360f789a6f1fce15f46ae68158adf6c7c8a48`  
repository: `GBOGEB/CODESPACES_jyperter`  
repository_role: `RUNTIME_PROPERTY_NOTEBOOK_WORKER`  
level1_status: `PC3_LEVEL1_CANDIDATE`  
level1_target: `LEVEL_1_0`  
authority_transfer: `false`

> This is the **current repository restart/control handover**. It describes durable repository role, authority, executable entry points and next work. It is not a release receipt and does not manufacture CI, engineering, compliance or source-authority credit. Verify execution state at the exact SHA in GitHub Actions.

## 1. Restart rule

Do not restart from the original GitHub Codespaces/Jupyter starter state and do not use the former root HEPAK handover as current repository authority.

Continue from live repository state:

```text
REFRESH LIVE main
→ READ open/merged PRs
→ VERIFY exact-SHA workflow evidence
→ REPAIR only measured repo-local defects
→ KEEP runtime proof separate from engineering authority
→ MERGE only on admissible exact-head proof
→ POST-MERGE main readback
→ PROMOTE only measured residuals
```

The pre-existing HEPAK Agent Integration Helper handover is preserved as historical context at:

```text
handover/archive/HANDOVER_HEPAK_AGENT_INTEGRATION_HELPER_v1.1_2025-08-15.md
```

That archive is **not** the current root control surface.

## 2. Current repository role

This repository has evolved from a Codespaces/Jupyter template into an active runtime and artifact-processing workbench.

Primary durable roles:

- execute local notebook, CLI and property probes;
- process heterogeneous engineering artifacts;
- emit deterministic runtime/property receipts and output digests;
- provide controlled QPLANT/QPS transformation workbenches;
- expose a human execution/status console;
- participate as a federated worker without inheriting upstream/downstream engineering authority.

Repository-local authority is anchored by:

- `.mesh/MESH_DOCK.yaml`
- `LEVEL1.md`
- `level1/ssot.json`
- `level1/manifest.json`

The Level-1 SSOT states that this worker may execute local probes, validate deterministic results and emit exact-SHA receipts. It must not promote exploratory output to authoritative QPS evidence, invent property-source authority or transfer child engineering authority.

## 3. Canonical execution surfaces

| Purpose | Entry point |
|---|---|
| Level-1 census / MIP / orchestration / analytics / self-test | `level1/runtime.py` |
| DMAIC Measure artifact framework | `src/measure_phase/` |
| Sequential ZIP processing | `src/zip_pipeline.py` |
| PowerPoint preview/digital-twin hints | `tools/extract_slide_previews.py` |
| QPS W111 sanitized power/utility workbench | `tools/qps_w111_power_utility_preview.py` |
| MCP human web console | `gui_candidate_bundle/gui_flask.py` |
| MCP desktop fallback | `gui_candidate_bundle/gui_launcher.py` |
| Repository artifact census/search | `scripts/repo_artifact_index.py` |
| QPLANT tender support | `src/qplant_tender.py`, `qplant_bundle/` |
| General test admission | `make test` |
| CI/control workflows | `.github/workflows/` |

## 4. Minimum local proof

Install repository dependencies and execute the normal admission path:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
make test
```

Current `make test` semantics are:

```text
critical Flake8: E9,F63,F7,F82
→ pytest
→ coverage report for src/
```

A green run therefore proves the **current admission contract**, not closure of all historical style/static-analysis debt.

Focused Level-1 proof:

```bash
python level1/runtime.py census
python level1/runtime.py mip
python level1/runtime.py orchestrate
python level1/runtime.py pca
python level1/runtime.py bt
python level1/runtime.py self-test
```

Focused GUI proof:

```bash
python -m pytest -q gui_candidate_bundle/tests
```

## 5. Evidence and authority invariant

Runtime success may prove that a script executed, a transformation reproduced, an output digest matches, or a defined calculation returned a result.

Runtime success does **not** by itself prove:

- QPS compliance;
- source-document correctness;
- design acceptance;
- bidder/offer correctness;
- contractual acceptance;
- engineering approval;
- child-repository disposition.

Exploratory/notebook output requires an explicit source and acceptance chain before it can be promoted beyond runtime evidence.

## 6. Current Level-1 state

Machine state: `level1/ssot.json`  
Gate manifest: `level1/manifest.json`

Declared state:

```text
status: PC3_LEVEL1_CANDIDATE
target: LEVEL_1_0
gate_count: 12
promotion: 12/12 census gates + green exact-head Level 1 MIP proof
```

Structure or local self-test alone must not be rewritten as observed Level-1.0.

## 7. CI and publication surfaces

Important workflows include:

- `.github/workflows/ci.yml`
- `.github/workflows/index.yml`
- `.github/workflows/level1-mip.yml`
- `.github/workflows/mcp-gui-candidate.yml`
- `.github/workflows/qps-w111-power-utility-workbench.yml`
- `.github/workflows/controlled-property-table.yml`
- `.github/workflows/helium-property-boundary.yml`
- `.github/workflows/qplant-build.yml`
- `.github/workflows/standalone-profile-runner.yml`
- `.github/workflows/triage-repo-index.yml`
- `.github/workflows/value-extraction-smoke.yml`
- `.github/workflows/w107-runtime-proof.yml`
- `.github/workflows/req-changelog.yml`

GitHub Pages is an active publication surface. GitHub Releases had no published release at the control baseline.

Workflow state is time-dependent: **read the exact SHA in Actions rather than copying a green/queued/red claim from this handover.**

## 8. Known structural debt

The following are open improvement edges, not silently completed work:

### P1 — Repository hygiene

Measure and classify tracked generated/runtime/history content, especially:

- tracked `venv/`;
- generated outputs and dashboards;
- large historical/runtime artifacts;
- source vs evidence vs disposable state boundaries.

Deletion requires dependency/reproducibility proof first.

### P2 — Package identity

`pyproject.toml` still identifies the Python project as:

```text
dmaic-measure-phase 1.0.0
```

That remains meaningful for the Measure subsystem but no longer describes the full repository. Reconcile package identity only after deciding whether this remains a multi-tool workbench or becomes a formally packaged runtime platform.

### P3 — Level-1 closure

Measure the exact 12-gate residual for:

```text
PC3_LEVEL1_CANDIDATE → LEVEL_1_0
```

Promote only after executed exact-head proof.

### P4 — Release infrastructure

Pages publication exists, but a governed point-release contract is still needed before publishing a GitHub Release. Define:

- release identity/version SSOT;
- source vs generated artifact boundary;
- required receipts/hashes;
- CI/reproducibility gates;
- release notes/changelog contract;
- outward artifact policy.

## 9. Next execution order

```text
P0 CURRENT HANDOVER / CONTROL COHERENCE
  root HANDOVER.md current
  historical HEPAK handover archived
  stale-root assertion in pytest
        ↓
P1 REPOSITORY HYGIENE CENSUS
  tracked venv/generated/history inventory
  dependency + reproducibility classification
  delete/move only proven disposable state
        ↓
P2 PACKAGE IDENTITY RECONCILIATION
  subsystem package vs repository platform decision
  pyproject metadata aligned without invented version bump
        ↓
P3 LEVEL-1 CLOSURE
  exact 12-gate census
  repair measured residual only
  exact-head Level 1 MIP proof
  promote only if fully observed
        ↓
P4 RELEASE INFRASTRUCTURE
  release identity + artifact contract
  release gate
  release receipts
  first governed GitHub Release
```

## 10. Handover maintenance rule

The root `HANDOVER.md` must remain a **repository-level current restart/control surface**.

It must not be replaced by:

- a subsystem-specific historical handover;
- generated runtime prose;
- notebook-only state;
- a release claim unsupported by exact-SHA evidence.

The test `tests/test_root_handover_contract.py` protects these minimum invariants.

## 11. Current authoritative navigation

| Need | Start here |
|---|---|
| Current repository overview | `README.md` |
| Current restart/control handover | `HANDOVER.md` |
| Level-1 role and promotion contract | `LEVEL1.md` |
| Level-1 machine state | `level1/ssot.json` |
| Federation role/authority | `.mesh/MESH_DOCK.yaml` |
| Measure subsystem detail | `README_MEASURE.md` |
| GUI-specific handover | `gui_candidate_bundle/HANDOVER.md` |
| Historical handovers | `handover/` |
| Repository index | `triage/repo_index/` |
| CI | `.github/workflows/` |

---

### Restart message

```text
CODESPACES_jyperter
→ refresh live main and exact workflow state
→ treat README.md + HANDOVER.md + LEVEL1.md + level1/ssot.json as the current control/navigation set
→ preserve authority_transfer=false
→ do not promote runtime evidence into engineering authority
→ complete repository hygiene before package-identity changes
→ close Level-1 only on measured 12/12 + exact-head proof
→ build release infrastructure only after control/hygiene/identity closure
```
