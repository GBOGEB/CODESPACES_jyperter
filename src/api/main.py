"""FastAPI service exposing artefact graph and KPI data."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from fastapi import FastAPI

ROOT = Path(__file__).resolve().parent.parent.parent

app = FastAPI()


@app.get("/index")
def read_index() -> dict:
    """Return SEC index data."""
    index_path = ROOT / "sec_index.json"
    if index_path.exists():
        return json.loads(index_path.read_text())
    return {"sections": []}


@app.get("/kpis")
def read_kpis() -> dict:
    """Return KPI thresholds."""
    kpi_path = ROOT / "kpi_template.yml"
    if kpi_path.exists():
        return yaml.safe_load(kpi_path.read_text())
    return {}
