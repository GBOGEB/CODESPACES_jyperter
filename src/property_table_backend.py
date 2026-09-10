"""Hash-bound helium density table adapter for controlled property evidence.

This module intentionally contains no QPS property values. Production values must arrive
through a manifest-bound external table generated from HEPAK, controlled CoolProp, or an
independently controlled reference table. Historical/reference-ratio estimates remain in
``helium_flow.py`` as comparative tooling only.
"""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

ALLOWED_PRODUCTION_SOURCE_CLASSES = {
    "HEPAK_CONTROLLED_EXPORT",
    "COOLPROP_CONTROLLED_EXPORT",
    "REFERENCE_TABLE_CONTROLLED",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class PropertyPoint:
    pressure_pa: float
    temperature_k: float
    density_kg_m3: float


class ControlledPropertyTable:
    """Callable density backend compatible with ``helium_flow.density_at``."""

    def __init__(self, table_path: str | Path, manifest_path: str | Path, *, mode: str = "PRODUCTION"):
        self.table_path = Path(table_path)
        self.manifest_path = Path(manifest_path)
        self.mode = mode
        if mode not in {"PRODUCTION", "TEST", "COMPARATIVE"}:
            raise ValueError(f"unsupported mode: {mode}")

        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.manifest = manifest
        self.source_class = str(manifest.get("source_class", ""))
        self.source_id = str(manifest.get("source_id", ""))
        self.source_sha256 = str(manifest.get("source_sha256", ""))
        self.table_sha256 = str(manifest.get("table_sha256", ""))
        self.freshness = str(manifest.get("freshness", "UNKNOWN"))
        self.production_credit_allowed = bool(manifest.get("production_credit_allowed", False))

        actual_table_sha = _sha256(self.table_path)
        if actual_table_sha != self.table_sha256:
            raise ValueError(f"property table SHA256 mismatch: expected {self.table_sha256}, got {actual_table_sha}")

        if mode == "PRODUCTION":
            if self.source_class not in ALLOWED_PRODUCTION_SOURCE_CLASSES:
                raise ValueError(f"non-authoritative property source class in production: {self.source_class}")
            if len(self.source_sha256) != 64 or any(c not in "0123456789abcdef" for c in self.source_sha256):
                raise ValueError("production property manifest requires source_sha256")
            if self.freshness != "CURRENT":
                raise ValueError(f"production property source must be CURRENT, got {self.freshness}")
            if not self.production_credit_allowed:
                raise ValueError("production property manifest explicitly disallows production credit")
        else:
            # Test/comparative tables are useful, but their values cannot silently become
            # production evidence merely because they satisfy the numeric schema.
            self.production_credit_allowed = False

        self.points = self._read_points()
        if not self.points:
            raise ValueError("property table is empty")
        self.evidence_label = f"{self.source_class}:{self.source_id}"

    def _read_points(self) -> list[PropertyPoint]:
        rows: list[PropertyPoint] = []
        with self.table_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            required = {"pressure_pa", "temperature_k", "density_kg_m3"}
            if not required.issubset(reader.fieldnames or []):
                raise ValueError(f"property table missing columns: {sorted(required)}")
            for row in reader:
                point = PropertyPoint(
                    pressure_pa=float(row["pressure_pa"]),
                    temperature_k=float(row["temperature_k"]),
                    density_kg_m3=float(row["density_kg_m3"]),
                )
                if point.pressure_pa <= 0 or point.temperature_k <= 0 or point.density_kg_m3 <= 0:
                    raise ValueError(f"invalid non-positive property point: {point}")
                rows.append(point)
        return rows

    def __call__(self, pressure_pa: float, temperature_k: float) -> float:
        """Return an exact table point; interpolation is deliberately not implicit."""
        matches = [
            p for p in self.points
            if abs(p.pressure_pa - pressure_pa) <= 1e-9 and abs(p.temperature_k - temperature_k) <= 1e-9
        ]
        if len(matches) != 1:
            raise KeyError(
                f"no unique controlled property point for P={pressure_pa} Pa, T={temperature_k} K; "
                "generate/bind the required point explicitly"
            )
        return matches[0].density_kg_m3

    def receipt(self) -> dict:
        return {
            "classification": "CONTROLLED_PROPERTY_BACKEND_RECEIPT",
            "mode": self.mode,
            "source_class": self.source_class,
            "source_id": self.source_id,
            "source_sha256": self.source_sha256,
            "table_sha256": self.table_sha256,
            "freshness": self.freshness,
            "point_count": len(self.points),
            "production_credit_allowed": self.production_credit_allowed,
            "interpolation": "DISABLED_FAIL_CLOSED",
        }
