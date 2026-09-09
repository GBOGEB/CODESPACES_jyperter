"""Lightweight helium density and pipe-flow screening utilities.

This module is intentionally a *screening* tool.  It uses the ideal-gas law and
one 300 K / 1 atm NIST reference point.  It is not a HEPAK/CoolProp/NIST property
engine and must not be used to close cryogenic or high-pressure acceptance
predicates without an independent property calculation.
"""
from __future__ import annotations

import math
import warnings
from dataclasses import dataclass
from typing import Iterable

import pandas as pd

R = 8.314462618  # J/(mol*K)
M_HE = 4.002602e-3  # kg/mol
MU_HE_300K = 1.96e-5  # Pa*s, dynamic viscosity of helium at 300 K
T_REF = 300.0  # K
P_REF = 101325.0  # Pa

# Single reference-point correction.  It is deliberately *not* called a general
# compressibility model because Z varies with state.
IDEAL_RHO_1ATM = (P_REF * M_HE) / (R * T_REF)
NIST_RHO_1ATM = 0.16250385946666235
REFERENCE_DENSITY_RATIO = NIST_RHO_1ATM / IDEAL_RHO_1ATM
SCREENING_PRESSURE_LIMIT_PA = 2.0 * P_REF


def rho_ideal(pressure_pa: float, temperature_k: float = T_REF) -> float:
    """Return ideal-gas helium density in kg/m^3."""
    if pressure_pa <= 0 or temperature_k <= 0:
        raise ValueError("pressure_pa and temperature_k must be positive")
    return pressure_pa * M_HE / (R * temperature_k)


def rho_screening_estimate(
    pressure_pa: float,
    temperature_k: float = T_REF,
    *,
    warn_outside_reference_range: bool = True,
) -> float:
    """Return a reference-scaled density for rough warm-helium screening.

    The correction factor is derived from exactly one NIST state (300 K, 1 atm).
    Above roughly 2 atm, or away from 300 K, callers should normally use a real
    property source.  A warning makes that boundary visible instead of silently
    implying NIST accuracy.
    """
    if warn_outside_reference_range and (
        pressure_pa > SCREENING_PRESSURE_LIMIT_PA or abs(temperature_k - T_REF) > 30.0
    ):
        warnings.warn(
            "reference-scaled helium density is only a screening approximation; "
            "use HEPAK/CoolProp/NIST state data for governed calculations",
            RuntimeWarning,
            stacklevel=2,
        )
    return rho_ideal(pressure_pa, temperature_k) * REFERENCE_DENSITY_RATIO


def rho_nist_estimate(pressure_pa: float) -> float:
    """Backward-compatible alias for the historical 300 K screening estimate.

    Deprecated name: this function does not evaluate a NIST EOS/table at the
    requested pressure.  New code should call :func:`rho_screening_estimate`.
    """
    warnings.warn(
        "rho_nist_estimate is a screening approximation, not a pressure-specific "
        "NIST property lookup; use rho_screening_estimate or a governed property source",
        DeprecationWarning,
        stacklevel=2,
    )
    return rho_screening_estimate(pressure_pa)


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
        """Compatibility alias retained for older CSV/notebook consumers."""
        return self.velocity_reference


def build_flow_table(
    mass_flows: Iterable[float],
    diameters_mm: Iterable[float],
    rho_design: float = 0.168,
    rho_reference: float = NIST_RHO_1ATM,
) -> pd.DataFrame:
    """Generate a warm-helium pipe-flow screening table.

    ``rho_design`` and ``rho_reference`` are explicit inputs.  This function does
    not infer a governed thermodynamic state from pressure alone.
    """
    if rho_design <= 0 or rho_reference <= 0:
        raise ValueError("densities must be positive")
    rows = []
    for dn in diameters_mm:
        if dn <= 0:
            raise ValueError("diameters must be positive")
        d_m = dn / 1000.0
        area = math.pi * (d_m / 2) ** 2
        for m_g_s in mass_flows:
            if m_g_s < 0:
                raise ValueError("mass flows cannot be negative")
            m_kg_s = m_g_s / 1000.0
            v_design = m_kg_s / (rho_design * area)
            v_reference = m_kg_s / (rho_reference * area)
            q_m3_s = m_kg_s / rho_design
            q_m3_h = q_m3_s * 3600.0
            q_Nm3_h = m_kg_s / 0.1785 * 3600.0  # legacy normal-density convention
            reynolds = rho_design * v_design * d_m / MU_HE_300K
            rows.append(
                FlowRow(
                    dn_mm=dn,
                    mass_flow_g_s=m_g_s,
                    area_m2=area,
                    velocity_design=v_design,
                    velocity_reference=v_reference,
                    vol_flow_m3_h=q_m3_h,
                    vol_flow_Nm3_h=q_Nm3_h,
                    reynolds_design=reynolds,
                )
            )
    df = pd.DataFrame(rows)
    # Preserve the historical exported column name for downstream compatibility,
    # but also expose the truthful name to new consumers.
    if not df.empty:
        df["velocity_nist"] = df["velocity_reference"]
    return df


def reference_isobar_table() -> pd.DataFrame:
    """Return ideal and single-reference-scaled 300 K screening values."""
    atm_pressures = [1, 2, 5, 10, 15]
    rows = []
    for atm in atm_pressures:
        p_pa = atm * P_REF
        rows.append(
            {
                "pressure_atm": atm,
                "pressure_Pa": p_pa,
                "rho_ideal": rho_ideal(p_pa),
                "rho_reference_scaled": rho_screening_estimate(
                    p_pa, warn_outside_reference_range=False
                ),
                "property_quality": "SCREENING_SINGLE_REFERENCE_POINT",
            }
        )
    return pd.DataFrame(rows)


def nist_isobar_table() -> pd.DataFrame:
    """Backward-compatible table name; values are screening estimates only."""
    warnings.warn(
        "nist_isobar_table does not contain pressure-specific NIST EOS values; "
        "use reference_isobar_table",
        DeprecationWarning,
        stacklevel=2,
    )
    df = reference_isobar_table().copy()
    df["rho_nist_est"] = df["rho_reference_scaled"]
    return df


if __name__ == "__main__":
    ref_df = reference_isobar_table()
    ref_df.to_csv("data/helium_reference_screening_300K.csv", index=False)

    # Keep the old filename for compatibility, but its columns now label quality.
    legacy_df = ref_df.rename(columns={"rho_reference_scaled": "rho_nist_est"})
    legacy_df.to_csv("data/helium_nist_300K.csv", index=False)

    flows = [1, 5, 10, 20, 40, 100]
    dns = [25, 50, 100, 150, 200]
    flow_df = build_flow_table(flows, dns)
    flow_df.to_csv("data/helium_flow_table.csv", index=False)

    print("Wrote screening/reference helium flow tables; governed property use requires HEPAK/CoolProp/NIST data")
