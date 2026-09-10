"""Helium density and flow helpers with an explicit property-evidence boundary.

The historical implementation used one reference density at 300 K / 1 atm to derive a
constant density-ratio correction and then labelled extrapolated values as a "NIST
estimate". That is useful for quick sensitivity work, but it is not equivalent to a
multi-pressure NIST/HEPAK/CoolProp property evaluation.

This module now calls that method ``reference_ratio_estimate`` and keeps
``rho_nist_estimate`` only as a compatibility alias. A caller may inject a real property
backend for pressure-dependent density without changing the downstream flow-table logic.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Iterable

import pandas as pd

R = 8.314462618  # J/(mol*K)
M_HE = 4.002602e-3  # kg/mol
MU_HE_300K = 1.96e-5  # Pa*s, dynamic viscosity of helium at 300 K
T_REF = 300.0  # K

IDEAL_RHO_1ATM = (101325 * M_HE) / (R * T_REF)
REFERENCE_RHO_1ATM = 0.16250385946666235
REFERENCE_DENSITY_RATIO = REFERENCE_RHO_1ATM / IDEAL_RHO_1ATM
NIST_RHO_1ATM = REFERENCE_RHO_1ATM
Z_FACTOR = REFERENCE_DENSITY_RATIO
DensityBackend = Callable[[float, float], float]


def rho_ideal(pressure_pa: float, temperature_k: float = T_REF) -> float:
    return pressure_pa * M_HE / (R * temperature_k)


def rho_reference_ratio_estimate(pressure_pa: float, temperature_k: float = T_REF) -> float:
    """Historical constant-ratio sensitivity estimate; not NIST/HEPAK/CoolProp evidence."""
    return rho_ideal(pressure_pa, temperature_k) * REFERENCE_DENSITY_RATIO


def rho_nist_estimate(pressure_pa: float) -> float:
    """Deprecated compatibility alias; this does not query NIST at requested pressure."""
    return rho_reference_ratio_estimate(pressure_pa, T_REF)


def _backend_label(backend: DensityBackend) -> str:
    """Return a stable evidence label for functions or callable backend objects."""
    explicit = getattr(backend, "evidence_label", None)
    if explicit:
        return str(explicit)
    name = getattr(backend, "__name__", None)
    if name:
        return str(name)
    return backend.__class__.__name__


def density_at(
    pressure_pa: float,
    temperature_k: float = T_REF,
    backend: DensityBackend | None = None,
) -> tuple[float, str]:
    """Return density and an explicit evidence/source label."""
    if backend is None:
        return rho_reference_ratio_estimate(pressure_pa, temperature_k), "REFERENCE_RATIO_ESTIMATE"
    value = float(backend(pressure_pa, temperature_k))
    if value <= 0:
        raise ValueError("density backend must return a positive kg/m^3 value")
    return value, _backend_label(backend)


@dataclass
class FlowRow:
    dn_mm: float
    mass_flow_g_s: float
    area_m2: float
    velocity_design: float
    velocity_reference: float
    vol_flow_m3_h: float
    vol_flow_Nm3_h: float
    reynolds_design: float

    @property
    def velocity_nist(self) -> float:
        return self.velocity_reference


def build_flow_table(
    mass_flows: Iterable[float],
    diameters_mm: Iterable[float],
    rho_design: float = 0.168,
    rho_reference: float = REFERENCE_RHO_1ATM,
) -> pd.DataFrame:
    rows = []
    for dn in diameters_mm:
        d_m = dn / 1000.0
        area = math.pi * (d_m / 2) ** 2
        for m_g_s in mass_flows:
            m_kg_s = m_g_s / 1000.0
            v_design = m_kg_s / (rho_design * area)
            v_reference = m_kg_s / (rho_reference * area)
            q_m3_s = m_kg_s / rho_design
            rows.append(FlowRow(
                dn_mm=dn,
                mass_flow_g_s=m_g_s,
                area_m2=area,
                velocity_design=v_design,
                velocity_reference=v_reference,
                vol_flow_m3_h=q_m3_s * 3600.0,
                vol_flow_Nm3_h=m_kg_s / 0.1785 * 3600.0,
                reynolds_design=rho_design * v_design * d_m / MU_HE_300K,
            ))
    frame = pd.DataFrame(rows)
    frame["velocity_nist"] = frame["velocity_reference"]
    return frame


def reference_isobar_table(density_backend: DensityBackend | None = None) -> pd.DataFrame:
    rows = []
    for atm in [1, 2, 5, 10, 15]:
        pressure_pa = atm * 101325
        density, source = density_at(pressure_pa, T_REF, density_backend)
        rows.append({
            "pressure_atm": atm,
            "pressure_Pa": pressure_pa,
            "rho_ideal": rho_ideal(pressure_pa),
            "rho_reference_or_backend": density,
            "density_evidence": source,
        })
    return pd.DataFrame(rows)


def nist_isobar_table() -> pd.DataFrame:
    frame = reference_isobar_table()
    frame["rho_nist_est"] = frame["rho_reference_or_backend"]
    return frame


if __name__ == "__main__":
    reference_df = reference_isobar_table()
    reference_df.to_csv("data/helium_reference_300K.csv", index=False)
    legacy_df = nist_isobar_table()
    legacy_df.to_csv("data/helium_nist_300K.csv", index=False)
    build_flow_table([1, 5, 10, 20, 40, 100], [25, 50, 100, 150, 200]).to_csv(
        "data/helium_flow_table.csv", index=False
    )
    print("Wrote reference, compatibility and flow tables")
