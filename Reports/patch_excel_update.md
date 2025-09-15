# Excel Parser Integration Patch

## Summary
- Shifted planning & scheduling to rely on Excel as the primary data engine.
- Introduced `LOCAL_XCEL_ENGINE` and `LOCAL_XCEL_EXPORT` execution blocks.
- Updated repository layout to add `ActiveDocs/`, `Outputs/excel/`, and new reporting paths.

## Repository Layout
```
/ActiveDocs/
 ├── MASTER.docx
 ├── MASTER.xlsx   ← planning/scheduling master tables
 └── MASTER.pptx

/Outputs/
 ├── word/
 ├── excel/
 │    ├── tables_csv/    ← all extracted tables as CSV
 │    └── tables_xlsx/   ← same tables exported as clean Excel files
 └── ppt/

/Reports/
 ├── TOOL_BASIC.md
 ├── schedule_index.md   ← consolidated planning/scheduling tables
 ├── patch_*.md
 └── decision_readout_*.md
```

## Excel Engine
```python
import pandas as pd
from pathlib import Path
import datetime

BASE = Path("Outputs/excel")
CSV_DIR = BASE / "tables_csv"
XLSX_DIR = BASE / "tables_xlsx"
CSV_DIR.mkdir(parents=True, exist_ok=True)
XLSX_DIR.mkdir(parents=True, exist_ok=True)

def parse_excel(path="ActiveDocs/MASTER.xlsx"):
    xl = pd.ExcelFile(path)
    exported = []
    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        if df.empty:
            continue
        csv_file = CSV_DIR / f"{sheet}.csv"
        xlsx_file = XLSX_DIR / f"{sheet}.xlsx"
        df.to_csv(csv_file, index=False)
        df.to_excel(xlsx_file, index=False)
        exported.append({
            "sheet": sheet,
            "rows": len(df),
            "cols": len(df.columns),
            "csv": str(csv_file),
            "xlsx": str(xlsx_file)
        })
    return exported

def build_schedule_index(exported):
    out_file = Path("Reports/schedule_index.md")
    stamp = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"# 📅 Schedule Index\n_Date: {stamp}_\n\n")
        f.write("| Sheet | Rows | Cols | CSV | Excel |\n")
        f.write("|-------|------|------|-----|-------|\n")
        for e in exported:
            f.write(f"| {e['sheet']} | {e['rows']} | {e['cols']} | {e['csv']} | {e['xlsx']} |\n")
    print(f"✅ Schedule index built → {out_file}")

if __name__ == "__main__":
    exported = parse_excel()
    build_schedule_index(exported)
```

## Manifest Integration
`session_handover.json`
```json
{
  "outputs": {
    "outline": "Outputs/word/outline.csv",
    "comments": "Outputs/word/comments.csv",
    "requirements": "Outputs/word/requirements.csv",
    "excel_tables_csv": "Outputs/excel/tables_csv/",
    "excel_tables_xlsx": "Outputs/excel/tables_xlsx/"
  },
  "reports": {
    "unified_md": "Reports/TOOL_BASIC.md",
    "schedule_index": "Reports/schedule_index.md"
  }
}
```

## Workflow Impact
1. Planner's Excel is the source of truth.
2. Pipeline exports machine-readable CSV and stakeholder-friendly XLSX tables.
3. `schedule_index.md` catalogues all planning tables.
4. Enables DMAIC patch and decision readouts with KPI tracking.

