# GBOGEB Level 1 — CODESPACES Jupyter

Status: `PC3_LEVEL1_CANDIDATE`
Target: `LEVEL_1_0`
Role: `RUNTIME_PROPERTY_NOTEBOOK_WORKER`

## Index

Human Level-1 navigator. Machine state: `level1/ssot.json`; gate manifest: `level1/manifest.json`; reusable skill: `skill/`; executable kernel: `level1/runtime.py`.

Existing capability is reused: `src/zip_pipeline.py` provides executable ZIP processing and `tools/extract_slide_previews.py` provides a concrete artifact-processing utility. Level-1 adds a small interoperability/control layer rather than replacing either tool.

Three MIP cycles: PC1 census/control, PC2 executable skill/runtime/agents, PC3 DMAIC + measured-only PCA/BT + CI orchestration proof. Structural target on this branch is 12/12 = 1.0000; observed Level-1.0 requires a green exact-head PC3 self-test.

## AOD

AOD = **Architecture–Orchestration–Decision**.

### Architecture

Owns notebook/CLI experimentation, ZIP processing, artifact/property probes and deterministic worker receipts.

### Orchestration

Local: `input -> utility/runtime -> measured result -> receipt`. Federated: `worker receipt -> pipeline hub -> CODEX/KEB -> ABACUS/DOW -> child disposition` when requested.

### Decision authority

May validate its own runtime/environment/results and emit exact-SHA/output digests. Must not elevate exploratory/notebook output into authoritative QPS engineering evidence without an explicit source and parent/child acceptance chain.

## DMAIC

- **Define:** bind role, inputs/outputs, native runtime anchors, authority and the fixed 12-gate denominator.
- **Measure:** execute `python level1/runtime.py census`; record exact tested SHA, missing gates and native-runtime visibility.
- **Analyze:** use the MIP missing-gate list first; PCA/BT only consume measured observations or explicit comparisons.
- **Improve:** repair the smallest executable gap, reuse healthy code, and add cross-capability edges only with explicit authority limits.
- **Control:** exact-head CI compiles the kernel, exercises census/MIP/orchestration, proves no-input PCA/BT DEFER, runs self-test and uploads receipts. The first red becomes the next recursive repair.

MIP = **Modernize (repair/reuse), Innovate (new useful nodes/edges/functions), Perpetuate (repeat exact-SHA execution and receipts).**

## PCA

PCA is a measured multivariate priority diagnostic, not a governance score generator. `python level1/runtime.py pca --input rows.json` accepts real numeric observations. Fewer than three observations, fewer than two variables or zero variance must DEFER. Synthetic self-test rows prove code only and are never project evidence. PCA can prioritize experiments/workers; it cannot create engineering or compliance credit.

## BT

Bradley–Terry is an observed pairwise priority diagnostic. `python level1/runtime.py bt --input comparisons.json` accepts real `[winner, loser]` comparisons. No comparisons must DEFER. BT may rank repair/feature alternatives but cannot replace source evidence, property validation or child disposition.

## Level-1.0 DoV

`LEVEL_1_0` requires all 12 gates true and a green exact-head `Level 1 MIP` workflow. Structure without executed CI remains candidate only. No engineering/compliance/negotiation credit is created by this bootstrap.
