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

# Reference density retained from the historical implementation. It is a single-point
# reference, not a pressure-dependent property table.
IDEAL_RHO_1ATM = (101325 * M_HE) / (R * T_REF)
REFERENCE_RHO_1ATM = 0.16250385946666235
REFERENCE_DENSITY_RATIO = REFERENCE_RHO_1ATM / IDEAL_RHO_1ATM

# Backward-compatible constants. New code should prefer REFERENCE_* names above.
NIST_RHO_1ATM = REFERENCE_RHO_1ATM
Z_FACTOR = REFERENCE_DENSITY_RATIO

DensityBackend = Callable[[float, float], float]


def rho_ideal(pressure_pa: float, temperature_k: float = T_REF) -> float:
    """Return ideal-gas density of helium in kg/m^3."""
    return pressure_pa * M_HE / (R * temperature_k)


def rho_reference_ratio_estimate(
    pressure_pa: float,
    temperature_k: float = T_REF,
) -> float:
    """Return the historical constant-ratio density sensitivity estimate.

    Evidence class: DERIVED / REFERENCE-RATIO. The same ratio between one reference
    density and the ideal-gas value is applied at every pressure. This is intentionally
    lightweight and must not be represented as a pressure-dependent NIST, HEPAK or
    CoolProp result.
    """
    return rho_ideal(pressure_pa, temperature_k) * REFERENCE_DENSITY_RATIO


def rho_nist_estimate(pressure_pa: float) -> float:
    """Compatibility alias for the historical API.

    Deprecated semantic name: this does *not* query NIST at the requested pressure.
    New code should use :func:`rho_reference_ratio_estimate`.
    """
    return rho_reference_ratio_estimate(pressure_pa, T_REF)


def density_at(
    pressure_pa: float,
    temperature_k: float = T_REF,
    backend: DensityBackend | None = None,
) -> tuple[float, str]:
    """Return density and an explicit evidence/source label.

    If ``backend`` is supplied it is responsible for returning kg/m^3 for the given
    pressure [Pa] and temperature [K]. This keeps licensed HEPAK, optional CoolProp, or
    independently controlled reference-table adapters outside the lightweight core.
    """
    if backend is None:
        return (
            rho_reference_ratio_estimate(pressure_pa, temperature_k),
            "REFERENCE_RATIO_ESTIMATE",
        )
    value = float(backend(pressure_pa, temperature_k))
    if value <= 0:
        raise ValueError("density backend must return a positive kg/m^3 value")
    return value, getattr(backend, "evidence_label", backend.__name__)


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
        """Compatibility view of the historical column name."""
        return self.velocity_reference


def build_flow_table(
    mass_flows: Iterable[float],
    diameters_mm: Iterable[float],
    rho_design: float = 0.168,
    rho_reference: float = REFERENCE_RHO_1ATM,
) -> pd.DataFrame:
    """Generate a flow table from controlled or explicitly supplied densities."""
    rows = []
    for dn in diameters_mm:
        d_m = dn / 1000.0
        area = math.pi * (d_m / 2) ** 2
        for m_g_s in mass_flows:
            m_kg_s = m_g_s / 1000.0
            v_design = m_kg_s / (rho_design * area)
            v_reference = m_kg_s / (rho_reference * area)
            q_m3_s = m_kg_s / rho_design
            q_m3_h = q_m3_s * 3600.0
            q_nm3_h = m_kg_s / 0.1785 * 3600.0
            reynolds = rho_design * v_design * d_m / MU_HE_300K
            rows.append(
                FlowRow(
                    dn_mm=dn,
                    mass_flow_g_s=m_g_s,
                    area_m2=area,
                    velocity_design=v_design,
                    velocity_reference=v_reference,
                    vol_flow_m3_h=q_m3_h,
                    vol_flow_Nm3_h=q_nm3_h,
                    reynolds_design=reynolds,
                )
            )
    frame = pd.DataFrame(rows)
    # Preserve the historical export column for consumers while making its semantics
    # explicit in a new canonical column.
    frame["velocity_nist"] = frame["velocity_reference"]
    return frame


def reference_isobar_table(
    density_backend: DensityBackend | None = None,
) -> pd.DataFrame:
    """Return selected 300 K isobars with explicit density evidence labels."""
    rows = []
    for atm in [1, 2, 5, 10, 15]:
        pressure_pa = atm * 101325
        density, source = density_at(pressure_pa, T_REF, density_backend)
        rows.append(
            {
                "pressure_atm": atm,
                "pressure_Pa": pressure_pa,
                "rho_ideal": rho_ideal(pressure_pa),
                "rho_reference_or_backend": density,
                "density_evidence": source,
            }
        )
    return pd.DataFrame(rows)


def nist_isobar_table() -> pd.DataFrame:
    """Compatibility export using the historical constant-ratio estimate.

    The returned ``rho_nist_est`` column is retained for older consumers, but the table
    now also includes ``density_evidence=REFERENCE_RATIO_ESTIMATE`` so it cannot be
    mistaken for a multi-pressure property-library result.
    """
    frame = reference_isobar_table()
    frame["rho_nist_est"] = frame["rho_reference_or_backend"]
    return frame


if __name__ == "__main__":
    reference_df = reference_isobar_table()
    reference_df.to_csv("data/helium_reference_300K.csv", index=False)

    # Historical filename retained for compatibility; its evidence column is explicit.
    legacy_df = nist_isobar_table()
    legacy_df.to_csv("data/helium_nist_300K.csv", index=False)

    flows = [1, 5, 10, 20, 40, 100]
    dns = [25, 50, 100, 150, 200]
    flow_df = build_flow_table(flows, dns)
    flow_df.to_csv("data/helium_flow_table.csv", index=False)

    print(
        "Wrote data/helium_reference_300K.csv, data/helium_nist_300K.csv "
        "and data/helium_flow_table.csv"
    )
