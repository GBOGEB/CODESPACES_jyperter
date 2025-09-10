"""Utility functions to estimate helium densities and flow velocities.

This module provides helpers to compute ideal-gas densities and to build a
flow table for circular pipes.  The NIST density at 300 K and 1 atm is used as a
reference to scale ideal-gas values for other pressures.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

import pandas as pd

R = 8.314462618  # J/(mol*K)
M_HE = 4.002602e-3  # kg/mol
MU_HE_300K = 1.96e-5  # Pa*s, dynamic viscosity of helium at 300 K
T_REF = 300.0  # K

# Compressibility adjustment derived from the NIST value at 1 atm / 300 K.
IDEAL_RHO_1ATM = (101325 * M_HE) / (R * T_REF)
NIST_RHO_1ATM = 0.16250385946666235
Z_FACTOR = NIST_RHO_1ATM / IDEAL_RHO_1ATM


def rho_ideal(pressure_pa: float, temperature_k: float = T_REF) -> float:
    """Return ideal-gas density of helium in kg/m^3."""
    return pressure_pa * M_HE / (R * temperature_k)


def rho_nist_estimate(pressure_pa: float) -> float:
    """Approximate the NIST density at 300 K for a given pressure.

    The NIST table value at 1 atm differs slightly from the ideal-gas law.
    We apply the same compressibility factor to other pressures to obtain a
    lightweight estimate when the full table is unavailable.
    """
    return rho_ideal(pressure_pa) * Z_FACTOR


@dataclass
class FlowRow:
    dn_mm: float
    mass_flow_g_s: float
    area_m2: float
    velocity_design: float
    velocity_nist: float
    vol_flow_m3_h: float
    vol_flow_Nm3_h: float
    reynolds_design: float


def build_flow_table(mass_flows: Iterable[float], diameters_mm: Iterable[float],
                     rho_design: float = 0.168,
                     rho_nist: float = NIST_RHO_1ATM) -> pd.DataFrame:
    """Generate a flow table.

    Parameters
    ----------
    mass_flows: g/s values
    diameters_mm: pipe diameters in mm
    rho_design: design density kg/m^3
    rho_nist: density for sensitivity kg/m^3
    """
    rows = []
    for dn in diameters_mm:
        d_m = dn / 1000.0
        area = math.pi * (d_m / 2) ** 2
        for m_g_s in mass_flows:
            m_kg_s = m_g_s / 1000.0
            v_design = m_kg_s / (rho_design * area)
            v_nist = m_kg_s / (rho_nist * area)
            q_m3_s = m_kg_s / rho_design
            q_m3_h = q_m3_s * 3600.0
            q_Nm3_h = m_kg_s / 0.1785 * 3600.0  # standard density at 0C/1 atm
            reynolds = rho_design * v_design * d_m / MU_HE_300K
            rows.append(FlowRow(
                dn_mm=dn,
                mass_flow_g_s=m_g_s,
                area_m2=area,
                velocity_design=v_design,
                velocity_nist=v_nist,
                vol_flow_m3_h=q_m3_h,
                vol_flow_Nm3_h=q_Nm3_h,
                reynolds_design=reynolds,
            ))
    return pd.DataFrame(rows)


def nist_isobar_table() -> pd.DataFrame:
    """Return a table of NIST densities at 300 K for selected isobars."""
    atm_pressures = [1, 2, 5, 10, 15]
    rows = []
    for atm in atm_pressures:
        p_pa = atm * 101325
        rows.append({
            "pressure_atm": atm,
            "pressure_Pa": p_pa,
            "rho_ideal": rho_ideal(p_pa),
            "rho_nist_est": rho_nist_estimate(p_pa),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    # Generate the NIST isobar table and flow table CSV files.
    nist_df = nist_isobar_table()
    nist_df.to_csv("data/helium_nist_300K.csv", index=False)

    flows = [1, 5, 10, 20, 40, 100]
    dns = [25, 50, 100, 150, 200]
    flow_df = build_flow_table(flows, dns)
    flow_df.to_csv("data/helium_flow_table.csv", index=False)

    print("Wrote data/helium_nist_300K.csv and data/helium_flow_table.csv")
