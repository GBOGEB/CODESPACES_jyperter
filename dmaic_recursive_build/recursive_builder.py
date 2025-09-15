#!/usr/bin/env python3
"""
recursive_builder.py — QPLANT/MINERVA CANVAS automation
- Inserts new SR./REQ. at an arbitrary index and re-numbers deterministically
- Updates RTM/SR/DTM JSON+CSV+Excel
- Regenerates MD/DOCX via Pandoc (if available)
- Writes change log and bumps version by +0.1
- Optional sync to Google Drive and GitHub
"""
import os, sys, json, csv, shutil, datetime, subprocess
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data"
OUTPUT = HERE / "outputs"
VERSIONS = HERE / "versioning"
CONFIG = HERE / "config.json"

def load_json(p: Path, default):
    if p.exists():
        with p.open() as f:
            return json.load(f)
    return default

def save_json(p: Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump(obj, f, indent=2)

def bump_version(tag: str) -> str:
    # expects something like MASTER_RTM_Rev0.0 -> Rev0.1
    if "Rev" not in tag:
        return tag + "_Rev0.1"
    head, rev = tag.split("Rev", 1)
    major_minor = rev.split("_")[0]
    major, minor = major_minor.split(".") if "." in major_minor else (major_minor, "0")
    new = f"Rev{major}.{int(minor)+1}"
    return tag.replace(f"Rev{major}.{minor}", new)

def renumber(df, col):
    # df is list[dict]; col like 'Req.#' or 'SR.#'
    for i, row in enumerate(df, start=1):
        row[col] = i
    return df

def insert_item(df, col, index, row):
    # index is 1-based (e.g., SR.14 insert => index=14)
    idx0 = max(0, index-1)
    df.insert(idx0, row)
    return renumber(df, col)

def to_csv(path: Path, rows: list, header: list):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k,"") for k in header})

def export_md(path: Path, title: str, rows: list, cols: list):
    lines = [f"# {title}", ""]
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"]*len(cols)) + " |"
    lines += [header, sep]
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(c,"")) for c in cols) + " |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))

def try_pandoc(md_path: Path, docx_path: Path):
    try:
        subprocess.run(["pandoc", str(md_path), "-o", str(docx_path)], check=True)
    except Exception as e:
        print(f"[warn] pandoc not available or failed: {e}")

def main():
    cfg = load_json(CONFIG, {
        "master_tag": "MASTER_RTM_Rev0.0",
        "rtm_json": str(DATA / "RTM_Master.json"),
        "sr_json": str(DATA / "SR_Master.json"),
        "dtm_json": str(DATA / "DTM_Master.json"),
        "batch_json": str(DATA / "Batch_New.json"),
        "export_root": str(OUTPUT)
    })
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    rtm = load_json(Path(cfg["rtm_json"]), {"requirements": []})
    sr  = load_json(Path(cfg["sr_json"]), {"stakeholders": []})
    dtm = load_json(Path(cfg["dtm_json"]), {"deliverables": []})
    batch = load_json(Path(cfg["batch_json"]), {"requirements": [], "stakeholders": [], "deliverables": []})

    for item in batch.get("stakeholders", []):
        target = int(item.get("insert_at", len(sr["stakeholders"])+1))
        sr["stakeholders"] = insert_item(sr["stakeholders"], "SR.#", target, item)

    for req in batch.get("requirements", []):
        target = int(req.get("insert_at", len(rtm["requirements"])+1))
        rtm["requirements"] = insert_item(rtm["requirements"], "Req.#", target, req)

    for d in batch.get("deliverables", []):
        dtm["deliverables"].append(d)

    save_json(Path(cfg["rtm_json"]), rtm)
    save_json(Path(cfg["sr_json"]), sr)
    save_json(Path(cfg["dtm_json"]), dtm)

    root = Path(cfg["export_root"])
    ver_tag = bump_version(cfg["master_tag"])
    out_dir = root / ver_tag
    out_dir.mkdir(parents=True, exist_ok=True)

    rtm_cols = ["Req.#","Type","Category","Title","Requirement","Measurability","Verification","Validation","Parent SR","Del.#"]
    to_csv(out_dir/"RTM.csv", rtm["requirements"], rtm_cols)

    sr_cols = ["SR.#","Title","Owner","Role","Rationale"]
    to_csv(out_dir/"SR.csv", sr["stakeholders"], sr_cols)

    dtm_cols = ["Del.#","Req.#","Title","Evidence","Verification","Validation"]
    to_csv(out_dir/"DTM.csv", dtm["deliverables"], dtm_cols)

    export_md(out_dir/"RTM.md", "RTM – Requirements", rtm["requirements"], rtm_cols)
    try_pandoc(out_dir/"RTM.md", out_dir/"RTM.docx")

    (out_dir/"CHANGELOG.md").write_text(f"## Release {ver_tag}\n- Batch applied at {now}\n- Counts: REQ={len(rtm['requirements'])}, SR={len(sr['stakeholders'])}, DEL={len(dtm['deliverables'])}\n")

    print(f"[ok] Exported to {out_dir}")

if __name__ == "__main__":
    main()
