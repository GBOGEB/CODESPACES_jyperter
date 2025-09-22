# QPLANT / MINERVA — MCB Orchestration Handover (v4.3)

**Date (UTC):** 2025-09-14 08:02:09

This handover consolidates the session outputs into an operable package for the **Management/Model/Minimum Change Board (MCB) orchestration**.

---

## 1. Scope & Baseline

- Baseline comprises **5 MASTER CANVAS** and automation toolchain (Python, Word/Excel VBA, Pandoc helper).
- Versioning convention: **MASTER_Name_RevN.n** (increment **0.1** per accepted batch).
- DMAIC control embedded; recursive builder supports **insert-at-position** with deterministic **renumbering** for **SR.#** and **Req.#**.

---

## 2. Artifact Inventory (Downloads)

### 2.1 Governance & DMAIC
- DMAIC Report (MD): `DMAIC_Iteration_v4.3.md`
- DMAIC Report (TXT): `DMAIC_Iteration_v4.3.txt`

### 2.2 Automation – Python
- Recursive Builder: `recursive_builder.py`
- Pandoc Export Helper: `pandoc_export.py`
- Drive/GitHub Sync Stubs: `drive_github_sync.py`

### 2.3 Office Automation – VBA
- Word Formatting Macro: `Word_QPLANT_Format.bas`
- Excel RTM Macro Pack: `Excel_QPLANT_RTM.bas`

### 2.4 Session Doc
- Cover Document (DOCX): `QPLANT_Recursive_Build_DMAIC_v4.3.docx`

### 2.5 Data Samples / Templates
- RTM Traceability (CSV): `RTM_Traceability_V4.1.csv`
- RTM Traceability (JSON): `RTM_Traceability_V4.1.json`
- RTM Excel (XLSX): `RTM_Traceability_V4.1.xlsx`

---

## 3. Configuration (edit and place alongside scripts)

- Config template (download & adjust): [config.json](config.json)

```json
{
  "master_tag": "MASTER_RTM_Rev0.0",
  "rtm_json": "data/RTM_Master.json",
  "sr_json": "data/SR_Master.json",
  "dtm_json": "data/DTM_Master.json",
  "batch_json": "data/Batch_New.json",
  "export_root": "outputs"
}
```

**Master JSON templates (empty/skeleton):**
- RTM master: [data/RTM_Master.json](data/RTM_Master.json)
- SR master:  [data/SR_Master.json](data/SR_Master.json)
- DTM master: [data/DTM_Master.json](data/DTM_Master.json)
- Batch sample: [data/Batch_New.json](data/Batch_New.json)

---

## 4. Orchestration Procedures (MCB)

### 4.1 Batch Intake (10–30 items typical)
1. Author prepares **Batch_New.json** with proposed **SR./Req./Del.** items including optional `insert_at` (1-based).
2. Submit batch to MCB queue with **impact note** (affected ADR/OCD/OTC).

### 4.2 Build & Validate
```bash
python recursive_builder.py
# outputs/<MASTER_RTM_RevX.Y> created
python pandoc_export.py outputs/<MASTER_RTM_RevX.Y>/RTM.md outputs/<MASTER_RTM_RevX.Y>/RTM.docx
```

### 4.3 Office QA
- Import **RTM.csv** into Excel sheet **RTM_Traceability** then run:
  - `RTM_InsertAndRenumber` (if manual insert)  
  - `RTM_CheckMeasurability` (flags missing measurability)
- Apply **Word** macro `QPLANT_ApplyStylesAndNumbering` to contract docs for **Heading 1/2/3** and **a)b)c)** clause lists.

### 4.4 Decision & Release
- MCB reviews generated **CHANGELOG.md** under the new release folder; if accepted, approve **Rev +0.1**.
- Optional: Run Drive/GitHub sync.

---

## 5. Integration (Drive / GitHub)

### 5.1 Google Drive (Colab)
- Mount Drive in Colab and run builder (see notebook stub): [notebooks/GoogleColab_QPLANT_Orchestration.ipynb](notebooks/GoogleColab_QPLANT_Orchestration.ipynb)

### 5.2 GitHub
- Use repository with `/data`, `/outputs`, `/versioning`.
- Add a CI workflow to publish artifacts on push (template): [.github/workflows/qplant-build.yml](.github/workflows/qplant-build.yml)

---

## 6. Numbering & Formatting Rules

- **Req.#** and **SR.#** are **unique anchors**; inserts **shift** following items; renumber performed by builder/macros.
- **Deliverable (Del.#)** is the **explicit measurability** child of **Req.#** (V&V linkage mandatory).
- **Word styles:** Heading 1 → “1.”, Heading 2 → “1.1.”, Heading 3 → “1.1.1”.  
- **RFO clause outline:** “a) b) c)” levels for contractual addenda.

---

## 7. Acceptance Criteria (per release)

1. 100% SR→Req coverage; 100% Req→Del coverage; 100% Req has V&V methods.  
2. ADR DD.# has parent SR.# and linked impacted Req.#.  
3. OCD has failure/recovery matrices bound to interfaces (TP1/TP2).  
4. OTC scoring sheet generated; QA/QC standards referenced in each measurable Req.#.  
5. Exports succeed (CSV/MD/DOCX); macros pass; changelog present.

---

## 8. Roles & RACI

- **Owner (AFA)** – Approves contract & gateway decisions.  
- **MMO (MINERVA)** – QA/Change governance; Risk & Issue registers.  
- **QPLANT** – System owner (design, integration, lifecycle).  
- **QCELL (TP1)** – Service requestor. **QPLANT (TP2)** – Service provider.  
- **TCO** – Requirements management oversight.

---

## 9. Appendices

- Sample batch JSON schema and fields (see Batch_New.json).  
- Safety & reliability notes (pneumatic vs. motorized actuation): evaluate MTBF/PFD in OCD risk tables and ADR decisions.  
- Materials annex & code references (e.g., 304L vs 316L) to remain in **Canvas 5 Reference Annex**.

---

**End of Handover**
