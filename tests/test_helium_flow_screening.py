import warnings

import pytest

from src.helium_flow import (
    NIST_RHO_1ATM,
    P_REF,
    build_flow_table,
    rho_ideal,
    rho_screening_estimate,
)


def test_reference_scaled_density_matches_reference_point():
    assert rho_screening_estimate(P_REF, warn_outside_reference_range=False) == pytest.approx(
        NIST_RHO_1ATM, rel=1e-12
    )


def test_screening_warns_for_high_pressure_use():
    with pytest.warns(RuntimeWarning, match="screening approximation"):
        rho_screening_estimate(15 * P_REF)


def test_flow_table_keeps_legacy_and_truthful_velocity_columns():
    df = build_flow_table([100], [150])
    assert len(df) == 1
    assert "velocity_reference" in df.columns
    assert "velocity_nist" in df.columns
    assert df.loc[0, "velocity_reference"] == pytest.approx(df.loc[0, "velocity_nist"])


def test_invalid_states_fail_closed():
    with pytest.raises(ValueError):
        rho_ideal(-1)
    with pytest.raises(ValueError):
        build_flow_table([1], [0])
