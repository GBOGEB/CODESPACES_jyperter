# GBOGEB Level 1 — CODESPACES Jupyter

Status: `PC1_CONTROL_PLANE`
Target: `LEVEL_1_0`
Role: `RUNTIME_PROPERTY_NOTEBOOK_WORKER`

## Index

Human Level-1 navigator. Machine state: `level1/ssot.json`; gate manifest: `level1/manifest.json`; reusable skill: `skill/`; executable kernel arrives in PC2.

Existing capability is reused: `src/zip_pipeline.py` provides executable ZIP processing and `tools/extract_slide_previews.py` provides a concrete artifact-processing utility. Level-1 adds a small interoperability/control layer rather than replacing either tool.

Three MIP cycles: PC1 census/control, PC2 executable skill/runtime/agents, PC3 DMAIC + measured-only PCA/BT + CI orchestration proof. Structural targets are 0.3333 -> 0.7500 -> 1.0000; observed Level-1.0 requires a green exact-head PC3 self-test.

## AOD

AOD = **Architecture–Orchestration–Decision**.

### Architecture

Owns notebook/CLI experimentation, ZIP processing, artifact/property probes and deterministic worker receipts.

### Orchestration

Local: `input -> utility/runtime -> measured result -> receipt`. Federated: `worker receipt -> pipeline hub -> CODEX/KEB -> ABACUS/DOW -> child disposition` when requested.

### Decision authority

May validate its own runtime/environment/results and emit exact-SHA/output digests. Must not elevate exploratory/notebook output into authoritative QPS engineering evidence without an explicit source and parent/child acceptance chain.
