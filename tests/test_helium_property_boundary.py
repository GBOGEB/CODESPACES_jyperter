import pytest

from src.helium_flow import (
    REFERENCE_RHO_1ATM,
    build_flow_table,
    density_at,
    nist_isobar_table,
    reference_isobar_table,
    rho_ideal,
    rho_nist_estimate,
    rho_reference_ratio_estimate,
)


def test_historical_alias_preserves_numeric_behavior():
    pressure = 5 * 101325.0
    assert rho_nist_estimate(pressure) == rho_reference_ratio_estimate(pressure)


def test_default_density_is_explicitly_reference_ratio():
    density, evidence = density_at(101325.0)
    assert evidence == "REFERENCE_RATIO_ESTIMATE"
    assert density == REFERENCE_RHO_1ATM


def test_injected_backend_is_used_and_labelled():
    def controlled_backend(pressure_pa: float, temperature_k: float) -> float:
        assert pressure_pa == 200000.0
        assert temperature_k == 300.0
        return 0.333

    controlled_backend.evidence_label = "CONTROLLED_TEST_BACKEND"
    density, evidence = density_at(200000.0, backend=controlled_backend)
    assert density == 0.333
    assert evidence == "CONTROLLED_TEST_BACKEND"


def test_reference_table_exposes_evidence_class():
    frame = reference_isobar_table()
    assert set(frame["density_evidence"]) == {"REFERENCE_RATIO_ESTIMATE"}
    assert len(frame) == 5


def test_legacy_table_keeps_old_column_with_new_evidence_label():
    frame = nist_isobar_table()
    assert "rho_nist_est" in frame.columns
    assert set(frame["density_evidence"]) == {"REFERENCE_RATIO_ESTIMATE"}


@pytest.mark.parametrize("pressure, temperature", [(-1.0, 300.0), (0.0, 300.0), (101325.0, 0.0)])
def test_non_physical_state_fails_closed(pressure, temperature):
    with pytest.raises(ValueError):
        rho_ideal(pressure, temperature)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"mass_flows": [1], "diameters_mm": [0]},
        {"mass_flows": [-1], "diameters_mm": [50]},
        {"mass_flows": [1], "diameters_mm": [50], "rho_design": 0.0},
        {"mass_flows": [1], "diameters_mm": [50], "rho_reference": -0.1},
    ],
)
def test_flow_table_rejects_non_physical_inputs(kwargs):
    with pytest.raises(ValueError):
        build_flow_table(**kwargs)


def test_flow_table_is_not_consumed_once_per_diameter():
    frame = build_flow_table(iter([1, 5]), [25, 50])
    assert len(frame) == 4


def test_empty_flow_table_keeps_schema():
    frame = build_flow_table([], [25])
    assert frame.empty
    assert {"velocity_reference", "velocity_nist"} <= set(frame.columns)
