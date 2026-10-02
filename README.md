# GBOGEB / CODESPACES_jyperter

> **Runtime property, artifact-processing and notebook workbench for the GBOGEB engineering toolchain**

Originally created from the GitHub Codespaces Jupyter template, this repository is now an active execution node rather than a blank notebook sandbox. It contains executable artifact-processing utilities, a DMAIC Measure implementation, QPLANT/QPS support tooling, a governed Level-1 runtime, reproducibility workbenches, a human execution console, repository indexing, tests and GitHub Actions automation.

**Live-state snapshot:** inspected against `main@83bfeea95956807015a86e16ef84ff129b36065e` on 2026-10-02. The latest `main` CI, global-index check, requirement changelog and GitHub Pages deployment all completed successfully.

---

## 1. System intent

The repository currently serves several related purposes:

1. **Runtime / notebook worker** — execute local probes, notebooks and deterministic property calculations.
2. **Artifact-processing workbench** — classify, parse, index, rank and transform heterogeneous engineering artifacts.
3. **Controlled reproducibility node** — emit exact-output receipts and deterministic projections for downstream engineering workflows.
4. **Human execution surface** — expose local status and governed execution through a small Flask/Tkinter console.
5. **Federated worker** — participate in the wider GBOGEB CODEX / KEB / ABACUS ecosystem without claiming authority that belongs to source or child repositories.

The repository-local mesh contract is explicit:

- ring: `R1_ACTIVE_EXECUTION`
- role: `RUNTIME_PROPERTY_NOTEBOOK_WORKER`
- local SSOT: `level1/ssot.json`
- may: execute local probes, validate deterministic results, emit exact-SHA receipts
- must not: promote exploratory output to authoritative QPS truth, invent property authority, or transfer child authority

See `.mesh/MESH_DOCK.yaml` and `LEVEL1.md` for the current control model.

---

## 2. What is implemented now

| Capability | Current implementation | Key entry points |
|---|---|---|
| DMAIC Measure / heterogeneous artifact handling | Classification, parsers, indexing, ranking, cache, metrics and KEB integration | `src/measure_phase/`, `README_MEASURE.md` |
| ZIP execution pipeline | Extract → compile smoke test → optional dry run → pytest → delete successful source ZIP | `src/zip_pipeline.py` |
| PowerPoint preview / digital twin hints | Extract slide text, shape/bullet counts, style hints and deterministic HTML preview | `tools/extract_slide_previews.py` |
| QPS W111 workbench | Sanitized power/utility preview plus repeatability receipt and CI proof | `tools/qps_w111_power_utility_preview.py`, `triage/W111_QPS_POWER_UTILITY_WORKBENCH.yaml` |
| Level-1 governed runtime | Census, MIP, orchestration, measured-only PCA/BT and exact-head self-test receipt | `level1/runtime.py`, `LEVEL1.md` |
| MCP human execution console | Flask dashboard, desktop launcher, shared status model and status API | `gui_candidate_bundle/` |
| Repository artifact census | Exact tracked-file inventory, SHA256 metadata and grep-friendly index | `scripts/repo_artifact_index.py`, `triage/repo_index/` |
| QPLANT engineering bundle | Requirements, interfaces, options and RTM support data | `qplant_bundle/`, `src/qplant_tender.py` |
| Engineering documentation | Cryogenic/process notes, requirements, contractual execution and traceability material | `docs/` |
| CI / control automation | Main CI plus focused property, Level-1, GUI, W111, indexing and runtime workflows | `.github/workflows/` |

The repository also contains historical handovers, generated outputs, dashboards, metrics, examples and exploratory notebooks. They are useful context but are not all equal in authority.

---

## 3. Architecture at a glance

```text
CODESPACES_jyperter/
├── .devcontainer/                 # Codespaces development environment
├── .github/workflows/             # CI and focused reproducibility gates
├── .mesh/MESH_DOCK.yaml           # Federation role / authority contract
├── level1/
│   ├── ssot.json                  # Level-1 machine state
│   ├── manifest.json              # Gate manifest
│   └── runtime.py                 # Census / MIP / orchestration / PCA / BT / self-test
├── gui_candidate_bundle/
│   ├── gui_flask.py               # Human web execution console
│   ├── gui_launcher.py            # Tkinter fallback
│   ├── status_model.py            # Shared fail-closed status model
│   └── tests/
├── src/
│   ├── measure_phase/             # DMAIC Measure artifact framework
│   ├── api/                       # API surface
│   ├── outlook_manager/           # Outlook/PST support tooling
│   ├── helium_flow.py             # Runtime engineering calculation support
│   ├── property_table_backend.py  # Property-table backend
│   ├── qplant_tender.py           # QPLANT tender support
│   └── zip_pipeline.py            # Sequential ZIP processing utility
├── tools/
│   ├── extract_slide_previews.py
│   └── qps_w111_power_utility_preview.py
├── scripts/                       # Indexing, changelog, build, KPI and control utilities
├── notebooks/                     # Jupyter / Colab experiments and orchestration notebooks
├── qplant_bundle/                 # RTM / interfaces / options / requirements
├── triage/                        # Measured workbench and repository-index evidence
├── docs/                          # Engineering and traceability documentation
├── README_MEASURE.md              # Measure subsystem detail
├── LEVEL1.md                      # Current Level-1 role and gate contract
└── Makefile                       # Critical lint + pytest/coverage entry point
```

---

## 4. Quick start

### GitHub Codespaces

The repository still supports the original Codespaces use case, but the environment is no longer a blank canvas. Open a Codespace on the repository and work from the checked-out branch.

### Local Python environment

The package metadata declares Python `>=3.8`. The primary CI workflow currently runs Python 3.11; some focused reproducibility workflows use Python 3.12.

```bash
python -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

make test
```

On Windows PowerShell, activate with:

```powershell
.\.venv\Scripts\Activate.ps1
```

### What `make test` means today

```text
critical Flake8 gate
    ↓
pytest
    ↓
coverage report for src/
```

The lint gate intentionally blocks critical classes only:

```text
E9, F63, F7, F82
```

This was introduced so historical formatting/style debt does not prevent behavioral tests from executing. Therefore **green CI means the repository passes its current admission gate; it does not mean all legacy Flake8/style debt is closed.**

---

## 5. Core execution paths

### 5.1 Level-1 runtime

The Level-1 runtime is the clearest machine-controlled entry point for the repository's governed worker role.

```bash
python level1/runtime.py census
python level1/runtime.py mip
python level1/runtime.py orchestrate
python level1/runtime.py pca
python level1/runtime.py bt
python level1/runtime.py self-test
```

Important behavior:

- PCA requires measured multivariate observations and must defer when inputs are insufficient.
- Bradley-Terry requires observed pairwise comparisons and must defer when none are supplied.
- Synthetic self-test data proves code paths only; it is not engineering evidence.
- Level-1 runtime success does not create QPS compliance or design authority.

The declared status in `LEVEL1.md` remains:

```text
PC3_LEVEL1_CANDIDATE
target: LEVEL_1_0
```

Promotion to `LEVEL_1_0` requires all defined gates plus green exact-head execution of the dedicated Level-1 workflow.

---

### 5.2 MCP human execution console

Install the focused GUI dependencies:

```bash
python -m pip install -r gui_candidate_bundle/requirements.txt
```

Run the web console:

```bash
python gui_candidate_bundle/gui_flask.py
```

Desktop fallback:

```bash
python gui_candidate_bundle/gui_launcher.py
```

Focused proof:

```bash
python -m pytest -q gui_candidate_bundle/tests
```

The Flask surface exposes:

```text
GET http://127.0.0.1:5000/api/status
```

The GUI is deliberately fail-closed:

- missing evidence is never rendered as PASS;
- missing executable/parser evidence is shown as `BLOCKED`;
- unrelated manifest fields are preserved during writes;
- repository path traversal is denied;
- optional GitHub Actions enrichment degrades to manifest/default state rather than manufacturing success.

See `gui_candidate_bundle/README.md` and `gui_candidate_bundle/HANDOVER.md`.

---

### 5.3 ZIP processing pipeline

`src/zip_pipeline.py` processes ZIP archives sequentially:

1. extract to a temporary directory;
2. byte-compile all Python files;
3. execute `run_pipeline.py --dry-run` when present;
4. run `pytest`;
5. delete the original ZIP after successful processing.

Run it with:

```bash
python -m src.zip_pipeline <dir1> <dir2> ...
```

> **Destructive behavior:** a successfully processed source ZIP is removed. Use copies or a controlled ingress directory when preservation is required.

A pytest exit code of 5 ("no tests collected") is treated as non-failing by this utility.

---

### 5.4 PowerPoint slide preview generator

Generate a lightweight text/style projection of a PPTX:

```bash
python tools/extract_slide_previews.py \
  --pptx path/to/deck.pptx \
  --outdir output/slide_preview \
  --limit 20
```

Outputs:

- `slide_texts.json` — extracted slide content and counts
- `slide_digital_twins.json` — compact summaries and style hints
- `slide_preview.html` — simple deterministic HTML cards

The title/background heuristic is intentionally lightweight. It is a preview aid, not a PowerPoint rendering engine.

---

### 5.5 QPS W111 sanitized power/utility workbench

The W111 lane renders a sanitized, non-authoritative engineering projection and proves deterministic output by rendering twice and comparing the resulting HTML byte-for-byte.

Example:

```bash
python tools/qps_w111_power_utility_preview.py \
  --input triage/fixtures/W111_power_utility_sanitized_smoke.json \
  --html /tmp/power_utility.html \
  --receipt /tmp/receipt.json
```

The focused workflow is:

```text
.github/workflows/qps-w111-power-utility-workbench.yml
```

Its role is tooling transformation and reproducibility proof. Processing PASS is not an automatic engineering/compliance PASS.

---

### 5.6 Offline repository index

Build the tracked-artifact census:

```bash
python scripts/repo_artifact_index.py
```

Search the generated index:

```bash
python scripts/repo_artifact_index.py --grep QPLANT
python scripts/repo_artifact_index.py --grep ALAT
python scripts/repo_artifact_index.py --grep 'ALAT|compliance|negotiation' --regex
```

Generated control files:

- `triage/repo_index/ARTIFACT_INDEX.yaml`
- `triage/repo_index/FILE_INDEX.tsv`

Binary files are indexed by identity, path, size and hash but are skipped by text grep.

---

## 6. DMAIC Measure subsystem

`src/measure_phase/` is a substantive subsystem, not just notebook scaffolding.

Implemented parser families include:

- ZIP
- Markdown
- Visio
- Word
- PDF
- PowerPoint

The subsystem also includes:

- artifact classification;
- SQLite/FTS-style indexing;
- multidimensional ranking;
- local priority caching;
- KPI/metrics collection;
- KEB interface support;
- workflow synchronization utilities.

The detailed subsystem documentation remains in `README_MEASURE.md`.

Note that `pyproject.toml` is still named `dmaic-measure-phase` version `1.0.0`. That metadata accurately describes this subsystem but no longer describes the full repository scope.

---

## 7. CI, control and publication

The repository currently contains multiple focused workflows, including:

- `ci.yml` — dependency validation, critical lint, pytest/coverage, SEC-index check and patch artifact
- `index.yml` — global index consistency
- `level1-mip.yml` — Level-1 exact-head control proof
- `mcp-gui-candidate.yml` — GUI proof
- `qps-w111-power-utility-workbench.yml` — deterministic W111 rendering proof
- `controlled-property-table.yml`
- `helium-property-boundary.yml`
- `qplant-build.yml`
- `standalone-profile-runner.yml`
- `triage-repo-index.yml`
- `value-extraction-smoke.yml`
- `w107-runtime-proof.yml`
- `req-changelog.yml`

At the inspected `main` head:

| Surface | State |
|---|---|
| Main CI | GREEN |
| Global index check | GREEN |
| Requirement changelog | GREEN |
| GitHub Pages build/deployment | GREEN |
| GitHub Releases | none published |

The repository therefore has an active deployment surface but no versioned GitHub release train yet.

---

## 8. Authority and evidence rules

This repository deliberately distinguishes **execution success** from **engineering authority**.

### Runtime evidence may prove

- a script executed;
- a deterministic transformation reproduced;
- a parser or renderer handled a defined input;
- a measured property calculation returned a result;
- a receipt matches a specific source/head/output state.

### Runtime evidence does not automatically prove

- QPS compliance;
- bidder/offer correctness;
- source-document authority;
- design acceptance;
- contractual acceptance;
- child-repository disposition;
- engineering approval.

Exploratory notebook output must be promoted only through an explicit source and acceptance chain.

---

## 9. Current development edges

The repository is operational, but its structure reflects several generations of work. The main cleanup/evolution edges are now clear:

1. **Align package identity with repository identity**  
   `pyproject.toml` still describes only the DMAIC Measure subsystem. Decide whether the repo remains a multi-tool workbench or becomes a formally packaged runtime platform, then update package/project metadata accordingly.

2. **Separate canonical source from generated/history content**  
   The tracked tree includes large generated/historical areas, including a tracked `venv/`. These inflate repository size and blur the distinction between source, evidence, outputs and disposable runtime state.

3. **Replace or quarantine stale top-level handover material**  
   The root `HANDOVER.md` is a 2025 HEPAK helper handover and is not a current whole-repository description. It should either be moved under historical handovers or replaced by a current governed handover.

4. **Close style/static-analysis debt separately from the critical CI gate**  
   Current CI intentionally gates only high-severity Flake8 classes. Broader formatting/static-analysis cleanup should be measured and burned down without reintroducing a false-green or pre-test blocker.

5. **Finish Level-1 promotion evidence**  
   Keep `PC3_LEVEL1_CANDIDATE` until the complete 12-gate target and exact-head workflow proof are explicitly recorded as achieved.

6. **Formalize release packaging**  
   GitHub Pages is active, but no GitHub Release has been published. A future release should define what is source, what is generated, what receipts are required, and what binaries/artifacts belong outside Git.

7. **Keep authority boundaries explicit as integrations grow**  
   New CODEX/KEB/ABACUS/QPS integrations should continue to emit provenance and deterministic receipts without silently inheriting engineering authority.

---

## 10. Recommended navigation

| Need | Start here |
|---|---|
| Repository role / governance | `LEVEL1.md`, `.mesh/MESH_DOCK.yaml` |
| DMAIC Measure internals | `README_MEASURE.md`, `src/measure_phase/` |
| Human execution console | `gui_candidate_bundle/README.md` |
| Level-1 execution | `level1/runtime.py` |
| ZIP archive processing | `src/zip_pipeline.py` |
| PowerPoint preview | `tools/extract_slide_previews.py` |
| QPS W111 preview | `tools/qps_w111_power_utility_preview.py` |
| Repository census/search | `triage/repo_index/README.md` |
| QPLANT working bundle | `qplant_bundle/` |
| CI behavior | `.github/workflows/`, `Makefile` |
| Engineering docs | `docs/` |

---

## 11. Repository status summary

```text
ORIGINAL STATE
GitHub Codespaces + Jupyter starter
        │
        ▼
CURRENT STATE
multi-purpose runtime / artifact / engineering workbench
        │
        ├── DMAIC Measure artifact framework
        ├── governed Level-1 runtime
        ├── MCP human execution console
        ├── ZIP / PPTX / property tooling
        ├── QPLANT / QPS support workbenches
        ├── repository census + traceability utilities
        ├── focused CI / reproducibility workflows
        └── GitHub Pages publication
```

This README intentionally avoids GitHub sidebar metadata such as stars, watchers, forks, language percentages, deployment counts and contributor counts. Those values are live repository metadata, not durable project documentation.

---

## License

MIT. See `LICENSE`.

## Provenance

Repository: `GBOGEB/CODESPACES_jyperter`

This root README is intended to describe the **current repository role and executable surfaces**. Subsystem documentation remains authoritative for subsystem-specific behavior, while engineering authority continues to follow the explicit source/acceptance chain defined by the wider GBOGEB federation.
