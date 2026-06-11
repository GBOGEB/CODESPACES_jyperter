---
id: ARTF_20250910_0004__BLOCK_010__MASTER_of_SLUG
block: BLOCK_010
title: MASTER_of_SLUG — Integrated Map & DMAIC Controls
baseline_tag: BASELINE_2025-09-10_01
owner: GBO
---

# Integrated Orchestration Map

## ASCII Portrait
```
[BLOCK_000] INPUT SOURCES (KEN)
  • MASTER.docx / RTM.xlsx / GLOBAL_index.json
  • Session artefacts / External regs / Supplier specs
      |
      v
[BLOCK_010] RECURSIVE BUILD ORCHESTRATOR (Codex≈MCB)
  • Cross-reference baseline; resolve links
  • Decide LOCAL vs CLOUD execution; enqueue jobs
  • Safe-state + retry (backoff), idempotent rebuild
      |                           \
      |                            \__ Telemetry feed (8001/9001/7001)
      v
+---------------------------+         +------------------------------+
| [BLOCK_020] LOCAL EXEC    |         | [BLOCK_030] CLOUD EXEC       |
|  - venv, Spyder GUI       |         |  - Codex batch / runners     |
|  - Jupyter (8001)         |         |  - GitHub Actions (CI/CD)    |
|  - Docker term (9001)     |         |  - Heavy compute offload     |
|  - DMAIC agent (7001)     |         |  - Auto patch/PR integration |
+-------------+-------------+         +---------------+--------------+
              |                                       |
              +-------------------+  +----------------+
                                  v  v
                     [BLOCK_040] DMAIC LOOPS
                       • LOCAL: test(8001), debug(9001), refactor(7001)
                       • GLOBAL: coverage, stability, reproducibility
                                  |
                                  v
                     [BLOCK_050] TELEMETRY & LOGGING
                       • KPI store (metrics.csv, metrics.json)
                       • Run logs / artefact hashes
                                  |
                                  v
                     [BLOCK_060] CI/CD HOOKS
                       • smoke-test.yml / recursive-build.yml / export-docs.yml
                       • preview-diff guard (input↔output)
                       • Golden Thread prove-out
                                  |
                                  v
                     [BLOCK_070] BASELINE UPDATE
                       • Update GLOBAL_index.json, section index.json
                       • Tag: BASELINE_<yyyy-mm-dd>_<iter>
```

## ASCII Landscape
```
[BLOCK_000] INPUTS --> [BLOCK_010] ORCHESTRATOR --> [BLOCK_020] LOCAL
                                  \--> [BLOCK_030] CLOUD
                                                     |
                                                     v
                      [BLOCK_040] DMAIC (LOCAL+GLOBAL) --> [BLOCK_050] TELEMETRY
                                                                |
                                                                v
                      [BLOCK_060] CI/CD (smoke | recursive | export | preview-diff)
                                                                |
                                                                v
                      [BLOCK_070] BASELINE & INDEX
```

## Mermaid Diagrams
- Portrait: `docs/diagrams/master_portrait.mmd`
- Landscape: `docs/diagrams/master_landscape.mmd`
- Local DMAIC Zoom: `docs/diagrams/local_dmaic_zoom.mmd`

## KPIs
See `metrics/metrics.csv` and `metrics/metrics.json` for current and target values.

## Controls
- Bi-directional preview-diff enforced via `scripts/preview_diff.py`.
- Artefact hashes maintained in `GLOBAL_index.json`.
- Baselines tagged `BASELINE_<date>_<iter>`.
