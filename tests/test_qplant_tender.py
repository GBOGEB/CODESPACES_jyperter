from pathlib import Path

import pandas as pd
import pytest

from qplant_tender import update_qplant_schedule

pytest.importorskip("openpyxl")


def create_base_workbook(path: Path) -> None:
    """Create a minimal workbook with List and Detailed Monitoring sheets."""
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        pd.DataFrame({"Project": ["ACC", "PTF", "FPF", "NFS"]}).to_excel(
            writer, sheet_name="List", index=False
        )
        monitor_cols = [
            "Element",
            "Description",
            "Mnemonic",
            "SPOC",
            "Dossier",
            "Launch",
            "Eval",
            "Neg",
            "PO",
            "Scenario",
            "M16 Conceptual",
            "M18 Detailed",
            "M23 Manufacturing",
            "M44 Provisional Acceptance",
        ]
        pd.DataFrame(columns=monitor_cols).to_excel(
            writer, sheet_name="Detailed Monitoring ATS Tenders", index=False
        )


def test_update_qplant_schedule(tmp_path: Path) -> None:
    workbook = tmp_path / "Detailing tender Process of ATS Tenders.xlsx"
    create_base_workbook(workbook)

    output = update_qplant_schedule(workbook)

    list_df = pd.read_excel(workbook, sheet_name="List")
    monitor_df = pd.read_excel(workbook, sheet_name="Detailed Monitoring ATS Tenders")

    assert "QPLANT" in list_df["Project"].values
    assert (monitor_df["Mnemonic"] == "QPL").sum() == 3  # baseline + sensitivities
    assert output.exists()
