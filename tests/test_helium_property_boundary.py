from src.helium_flow import (
    REFERENCE_RHO_1ATM,
    density_at,
    nist_isobar_table,
    reference_isobar_table,
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
