import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Baseline schedule definition
BASE_SCHEDULE = [
    {"Phase": "Prep", "Start": "2025-09", "End": "2025-10", "Duration (mo)": 2, "Milestone": "", "Marker": "", "Color": "Grey"},
    {"Phase": "Launch", "Start": "2025-11", "End": "2025-11", "Duration (mo)": 1, "Milestone": "Tender", "Marker": "★", "Color": "Blue"},
    {"Phase": "Evaluation", "Start": "2025-11", "End": "2026-03", "Duration (mo)": 4, "Milestone": "Close", "Marker": "▲", "Color": "Purple"},
    {"Phase": "Negotiation", "Start": "2026-04", "End": "2026-05", "Duration (mo)": 2, "Milestone": "", "Marker": "", "Color": "Grey"},
    {"Phase": "Drafting", "Start": "2026-06", "End": "2026-12", "Duration (mo)": 7, "Milestone": "", "Marker": "", "Color": "Grey"},
    {"Phase": "Approvals", "Start": "2027-01", "End": "2027-03", "Duration (mo)": 3, "Milestone": "", "Marker": "", "Color": "Grey"},
    {"Phase": "PO Signature", "Start": "2027-06", "End": "2027-06", "Duration (mo)": 1, "Milestone": "PO Base", "Marker": "●", "Color": "Green"},
    {"Phase": "PO Delay+2m", "Start": "2027-08", "End": "2027-08", "Duration (mo)": 1, "Milestone": "PO Slip", "Marker": "●●", "Color": "Orange"},
    {"Phase": "PO Delay+4m", "Start": "2027-10", "End": "2027-10", "Duration (mo)": 1, "Milestone": "PO Slip", "Marker": "●●●", "Color": "Red"},
]

# DataFrame for baseline (without computed acceptance)
BASE_DF = pd.DataFrame(BASE_SCHEDULE)


def rerun_schedule(shift_negotiation: int = 0, shift_legal: int = 0) -> pd.DataFrame:
    """Return schedule DataFrame with optional shifts applied.

    Parameters
    ----------
    shift_negotiation: int
        Month shift applied to the negotiation phase.
    shift_legal: int
        Additional months applied to PO & downstream milestones.
    """
    df_copy = BASE_DF.copy()

    # Adjust negotiation phase
    if shift_negotiation:
        start_month = 4 + shift_negotiation
        end_month = 5 + shift_negotiation
        df_copy.loc[df_copy["Phase"] == "Negotiation", ["Start", "End"]] = [
            f"2026-{start_month:02d}",
            f"2026-{end_month:02d}",
        ]

    # Compute base PO date
    base_po_date = datetime(2027, 6, 1)
    po_date = base_po_date + relativedelta(months=shift_negotiation + shift_legal)
    po_month = po_date.strftime("%Y-%m")

    df_copy.loc[df_copy["Phase"] == "PO Signature", ["Start", "End"]] = [po_month, po_month]

    # Adjust sensitivity markers relative to new PO date
    delay_2_month = (po_date + relativedelta(months=2)).strftime("%Y-%m")
    delay_4_month = (po_date + relativedelta(months=4)).strftime("%Y-%m")
    df_copy.loc[df_copy["Phase"] == "PO Delay+2m", ["Start", "End"]] = [delay_2_month, delay_2_month]
    df_copy.loc[df_copy["Phase"] == "PO Delay+4m", ["Start", "End"]] = [delay_4_month, delay_4_month]

    # Final Acceptance occurs 34 months after PO
    acceptance_date = po_date + relativedelta(months=34)
    acceptance_month = acceptance_date.strftime("%Y-%m")

    acceptance_row = {
        "Phase": "Final Acceptance",
        "Start": acceptance_month,
        "End": acceptance_month,
        "Duration (mo)": 1,
        "Milestone": "Acceptance",
        "Marker": "♦",
        "Color": "Grey",
    }

    # Append or replace Final Acceptance row
    if "Final Acceptance" in df_copy["Phase"].values:
        df_copy.loc[df_copy["Phase"] == "Final Acceptance"] = acceptance_row
    else:
        df_copy = pd.concat([df_copy, pd.DataFrame([acceptance_row])], ignore_index=True)

    return df_copy


if __name__ == "__main__":
    # Baseline export with acceptance row computed
    baseline_df = rerun_schedule()
    baseline_df.to_excel("tender_schedule_colored.xlsx", index=False)

    # Example test run with shifts
    test_df = rerun_schedule(shift_negotiation=2, shift_legal=2)
    test_df.to_excel("tender_schedule_test.xlsx", index=False)

    print("Exports complete:")
    print(" - tender_schedule_colored.xlsx (baseline)")
    print(" - tender_schedule_test.xlsx (example test run)")
