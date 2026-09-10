import hashlib
import json
from pathlib import Path

import pytest

from src.helium_flow import density_at
from src.property_table_backend import ControlledPropertyTable


def _write_table(tmp_path: Path):
    table = tmp_path / "points.csv"
    table.write_text("pressure_pa,temperature_k,density_kg_m3\n300000,4.5,12.5\n", encoding="utf-8")
    return table, hashlib.sha256(table.read_bytes()).hexdigest()


def test_test_mode_accepts_fixture_but_never_production_credit(tmp_path: Path):
    table, table_sha = _write_table(tmp_path)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({
        "source_class": "SAMPLE",
        "source_id": "fixture-only",
        "source_sha256": "",
        "table_sha256": table_sha,
        "freshness": "NOT_APPLICABLE",
        "production_credit_allowed": True
    }), encoding="utf-8")
    backend = ControlledPropertyTable(table, manifest, mode="TEST")
    rho, label = density_at(300000, 4.5, backend)
    assert rho == 12.5
    assert label == "SAMPLE:fixture-only"
    assert backend.receipt()["production_credit_allowed"] is False


def test_production_rejects_sample_or_stale_source(tmp_path: Path):
    table, table_sha = _write_table(tmp_path)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({
        "source_class": "SAMPLE",
        "source_id": "bad-production-fixture",
        "source_sha256": "a" * 64,
        "table_sha256": table_sha,
        "freshness": "CURRENT",
        "production_credit_allowed": True
    }), encoding="utf-8")
    with pytest.raises(ValueError, match="non-authoritative property source class"):
        ControlledPropertyTable(table, manifest, mode="PRODUCTION")


def test_production_requires_exact_hash_and_exact_requested_point(tmp_path: Path):
    table, table_sha = _write_table(tmp_path)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({
        "source_class": "HEPAK_CONTROLLED_EXPORT",
        "source_id": "controlled-test-shape",
        "source_sha256": "b" * 64,
        "table_sha256": table_sha,
        "freshness": "CURRENT",
        "production_credit_allowed": True
    }), encoding="utf-8")
    backend = ControlledPropertyTable(table, manifest, mode="PRODUCTION")
    assert backend(300000, 4.5) == 12.5
    with pytest.raises(KeyError, match="generate/bind the required point explicitly"):
        backend(300000, 5.0)
