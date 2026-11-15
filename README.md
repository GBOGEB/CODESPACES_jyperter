# CODESPACES_jyperter — runtime, artifact-processing and notebook workbench

<!-- markdownlint-disable MD001 MD013 MD022 MD029 MD031 MD032 MD033 MD040 MD060 -->

[![CI](https://img.shields.io/github/actions/workflow/status/GBOGEB/CODESPACES_jyperter/ci.yml?branch=main&style=flat-square&label=CI)](https://github.com/GBOGEB/CODESPACES_jyperter/actions/workflows/ci.yml)
[![Runtime: Python 3.11](https://img.shields.io/badge/runtime-Python%203.11-blue?style=flat-square)](.github/workflows/ci.yml)
[![State: quiet since 26 Oct 2026](https://img.shields.io/badge/state-quiet%20since%2026%20Oct%202026-lightgrey?style=flat-square)](#6-status-and-open-gates)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

> **Started from the GitHub Codespaces Jupyter template, now an execution node of the GBOGEB toolchain: it classifies, parses and indexes engineering artifacts, runs deterministic property calculations and emits reproducible receipts — without claiming engineering authority.**

## At a glance

| | |
|---|---|
| **Domain** | Runtime and notebook work for engineering artifacts: DMAIC Measure artifact handling, ZIP and PPTX processing, property tables, the W111 power/utility workbench, a small MCP execution console |
| **EPICs carried here** | **Level-1 runtime worker** ([LEVEL1.md](LEVEL1.md)) · **DMAIC Measure** ([README_MEASURE.md](README_MEASURE.md)) · **QPS W111** workbench ([triage](triage/)) · development edges in [§6](#6-status-and-open-gates). No GitHub issues are open. |
| **Owner and decision authority** | Repository owner **GBOGEB**: admission to the default branch, releases and every external grant. No agent, bot or CI verdict holds this authority. |
| **Role in the federation** | A *runtime worker* (ring `R1_ACTIVE_EXECUTION`, role `RUNTIME_PROPERTY_NOTEBOOK_WORKER`): it executes and receipts; source and child repositories keep authority. |
| **Owns** | `src/measure_phase/`, `src/zip_pipeline.py`, `tools/` previews, `level1/` runtime, `gui_candidate_bundle/`, the repository artifact index |
| **Does not own** | QPS compliance, offer correctness and design acceptance (cryoplant-project) · KEB receipts and governance (CODEX) · DOW runtime (ABACUS) |
| **Status snapshot** | `main@f8eae42`, read 15 November 2026 — 0 open issues, 0 open PRs. [Details ↓](#6-status-and-open-gates) |

**New here?** Read [§1](#1-why-codespaces_jyperter-exists--bios), then the route that matches you:

| I want to… | Open this first |
|---|---|
| Know the role and rules | [`LEVEL1.md`](LEVEL1.md), [`.mesh/MESH_DOCK.yaml`](.mesh/MESH_DOCK.yaml), [`HANDOVER.md`](HANDOVER.md) |
| Use the artifact framework | [`README_MEASURE.md`](README_MEASURE.md) and [`src/measure_phase/`](src/measure_phase/) |
| Run the console | [`gui_candidate_bundle/README.md`](gui_candidate_bundle/README.md) |
| Search the repository | [`triage/repo_index/README.md`](triage/repo_index/README.md) |
| Set up and test | [Run it locally](#7-run-it-locally) |

## 1. Why CODESPACES_jyperter exists — BIOS

**B — Baseline.** Package metadata still reads `dmaic-measure-phase` 1.0.0, which names one subsystem rather than the whole workbench. No GitHub Release exists. The current handover is dated 2 Oct 2026.

**I — Identity and integrity.** Runs emit exact-output receipts bound to source, head and output; the artifact index records SHA-256 for every tracked file.

**O — Orchestration with ownership.** The local SSOT is `level1/ssot.json`; Level-1 status stays `PC3_LEVEL1_CANDIDATE` until the 12-gate proof is recorded.

**S — Safety and source-qualified status.** Execution success is not engineering authority: notebook output is promoted only through an explicit source and acceptance chain.

**Where authority lives:** [`LEVEL1.md`](LEVEL1.md) · [`level1/ssot.json`](level1/ssot.json) · [`.mesh/MESH_DOCK.yaml`](.mesh/MESH_DOCK.yaml) · [`HANDOVER.md`](HANDOVER.md).

## 2. From source to decision

1. Artifacts arrive (documents, slides, archives, data).
2. Measure classifies, parses, indexes and ranks them.
3. Tools transform or preview deterministically and write receipts.
4. CI re-runs the focused proofs on the exact head.
5. Receipts go to federation consumers; authority stays with the source or child repository.

## 3. What is inside

| Block | Native source | Input → output | Boundary |
|---|---|---|---|
| DMAIC Measure | [`src/measure_phase/`](src/measure_phase/) | Heterogeneous artifacts → classes, parsed content, index, rank | Classification, not authority |
| ZIP pipeline | [`src/zip_pipeline.py`](src/zip_pipeline.py) | Archive → compile smoke, dry run, pytest | Deletes the source ZIP only after success |
| PPTX preview | [`tools/extract_slide_previews.py`](tools/extract_slide_previews.py) | Slides → text, counts, HTML preview | Hints, not semantics |
| W111 workbench | [`tools/qps_w111_power_utility_preview.py`](tools/qps_w111_power_utility_preview.py) | Sanitized data → preview + repeatability receipt | Sanitized inputs only |
| Level-1 runtime | [`level1/runtime.py`](level1/runtime.py) | Census, MIP, PCA/BT on measured data, self-test | Candidate status |
| MCP console | [`gui_candidate_bundle/`](gui_candidate_bundle/README.md) | Status model → Flask dashboard, launcher | Local use |
| Artifact census | [`scripts/repo_artifact_index.py`](scripts/repo_artifact_index.py) | Tracked files → SHA-256 index | Inventory |

### Architecture at a glance

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

### Core execution paths

#### 5.1 Level-1 runtime

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

#### 5.2 MCP human execution console

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

#### 5.3 ZIP processing pipeline

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

#### 5.4 PowerPoint slide preview generator

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

#### 5.5 QPS W111 sanitized power/utility workbench

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

#### 5.6 Offline repository index

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

### DMAIC Measure subsystem

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

## 4. Where CODESPACES_jyperter sits in the federation

| Neighbour | Keeps | Interface with CODESPACES_jyperter |
|---|---|---|
| [CODEX](https://github.com/GBOGEB/CODEX) | Federation governance, contracts, wave roll-up | KEB integration of Measure outputs |
| [ABACUS](https://github.com/GBOGEB/ABACUS) | DMAIC runtime, CI repair at source | Runtime peer |
| [cryoplant-project](https://github.com/GBOGEB/cryoplant-project) (private) | QPS engineering SSOT and release identity | Owns QPS acceptance |
| [pipeline-automation-hub](https://github.com/GBOGEB/pipeline-automation-hub) | Routing, JADE census, Mission Control | Routes Level-1 receipts |

## 5. Process diagrams

Declared architecture, not a run receipt.

## 6. Status and open gates

**Snapshot: `main@f8eae42`, read 15 November 2026.** Rows point at live owners; open the link for the current position.

| Gate | Status | What would close it |
|---|---|---|
| CI | Main CI **green** 26 Oct 2026 (critical Flake8 classes only, then pytest) | Broader lint debt burned down separately |
| Pages | Static Pages deploy succeeded 21 Oct; the Jekyll workflow's last run was cancelled the same day | Owner keeps one Pages workflow |
| Package identity | `pyproject.toml` describes only the Measure subsystem | Decide workbench vs packaged runtime; update metadata |
| Release | No GitHub Release | Define source, generated output and receipts for a release |
| Level-1 | `PC3_LEVEL1_CANDIDATE` | 12-gate exact-head proof recorded |
| Resolved since the 2 Oct snapshot | No `venv/` is tracked any more; root `HANDOVER.md` is now a current handover | — |

## 7. Run it locally

CI runs Python **3.11** (`pyproject.toml` allows ≥ 3.8; some focused workflows use 3.12).

#### GitHub Codespaces

The repository still supports the original Codespaces use case, but the environment is no longer a blank canvas. Open a Codespace on the repository and work from the checked-out branch.

#### Local Python environment

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

#### What `make test` means today

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

## 8. Evidence rules and non-compensation

- **Execution ≠ authority**: a receipt proves a run, not QPS compliance, offer correctness or design acceptance.
- **Promote through a chain**: notebook output needs an explicit source and acceptance path.
- **Exact head**: receipts bind source, head and output.

## 9. Repository map and next actions

| Folder | Open it for |
|---|---|
| [`src/`](src/) | Measure framework, ZIP pipeline, QPLANT helpers |
| [`tools/`](tools/) | Previews and workbenches |
| [`level1/`](level1/) | Level-1 runtime |
| [`gui_candidate_bundle/`](gui_candidate_bundle/) | Execution console |
| [`triage/`](triage/) | Index and W111 records |
| [`docs/`](docs/) | Engineering notes |
| [`tests/`](tests/) | Tests |

**Next actions** (match §6): align package identity → one Pages workflow → define a release → record the Level-1 proof.

---

BIOS: Baseline · Identity · Orchestration · Safety. Admission authority: **GBOGEB**. Licence: [MIT](LICENSE). Landing R2 on the [GEMINI skeleton](https://github.com/GBOGEB/GEMINI/blob/main/docs/landing/LANDING_SKELETON.md), snapshot `main@f8eae42`.
