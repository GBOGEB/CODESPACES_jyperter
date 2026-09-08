# TRIAGE Renegade Self-Repo Analysis — W01

Repository: `GBOGEB/CODESPACES_jyperter`  
Observed head: `8728de0b22a5ba07c8d7daf61da21d04267bd7b5`  
Authority: discovery / independent engineering evidence only  
Release credit: none until accepted by the applicable primary repo at an exact SHA.

## Why this repo matters

This is a large legacy engineering workspace with QPLANT/QSYS calculations, tender material, recursive-build/index machinery, slide tooling, and many unrelated exploratory assets. Its size and heterogeneity make wholesale federation unsafe. The correct use is targeted nuance extraction.

## Unique candidate value

1. Helium-flow and density utilities (`src/helium_flow.py`).
2. Cold-box heat-balance calculations and data (`docs/coldbox_heat_balance.md`, `data/coldbox_heat_balance.csv`).
3. QSYS/SBS and pressure/unit conventions (`docs/qsys_sbs_scss.md`).
4. S-header relief input set (`params/s_header.yml`).
5. Tender/schedule helpers and older engineering narrative that may expose assumptions not carried into current canonical material.
6. Recursive artefact-index patterns in `GLOBAL_index.json` that may be useful for census/lineage design.

## Known self-repo defect before promotion

`GLOBAL_index.json` identifies its repository as `GBOGEB/GBOGEB`, which does not match this repository. Treat that index as stale/partially migrated until repaired and revalidated. No lineage claim derived from that field should be promoted before correction.

## Duplication / scrub policy

- Do not import entire calculators or narrative trees into cryoplant-project.
- Compare numerical outputs and assumptions against current QPLANT canonical values.
- Retain only deltas: different source basis, unit convention, boundary condition, equation, test, or result.
- If two implementations agree, record the second one as independent replication evidence rather than a second SSOT.
- Unrelated Codespaces/demo/tooling content is N/A to TRIAGE and should not be federated.

## Initial smoke targets

- import `src.helium_flow`
- parse `params/s_header.yml`
- verify `data/coldbox_heat_balance.csv` is readable and consistent with the accompanying narrative
- inspect repository identity fields before using recursive index outputs

## Proposed route

Engineering/numerical nuance -> `GBOGEB/cryoplant-project`.  
Independent calculation/test evidence -> `GBOGEB/ABACUS`.  
Only reusable federation or artifact-index mechanics -> `GBOGEB/CODEX` / TRIAGE incubator.

## Promotion gate

Exact source SHA + smoke PASS + explicit unique delta + canonical target owner + accepted disposition + no authority collision + reproducible calculation/provenance receipt.
