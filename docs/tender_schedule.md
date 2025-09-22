# Tender Schedule

## Legend

| Marker | Meaning | Color |
|--------|---------|-------|
| [★] | Tender Launch | Blue |
| [▲] | Evaluation Close | Purple |
| [●] | PO Baseline | Green |
| [●●] | PO +2m delay | Orange |
| [●●●] | PO +4m delay | Red |
| ■■ | Activity span | Grey |

## Baseline Schedule

| Phase | Start | End | Duration (mo) | Milestone | Marker | Color |
|-------|-------|-----|---------------|-----------|--------|-------|
| Prep | Sep-25 | Oct-25 | 2 | | | Grey |
| Launch | Nov-25 | Nov-25 | 1 | Tender | ★ | Blue |
| Evaluation | Nov-25 | Mar-26 | 4 | Close | ▲ | Purple |
| Negotiation | Apr-26 | May-26 | 2 | | | Grey |
| Drafting | Jun-26 | Dec-26 | 7 | | | Grey |
| Approvals | Jan-27 | Mar-27 | 3 | | | Grey |
| PO Signature | Jun-27 | Jun-27 | 1 | PO Base | ● | Green |
| PO Delay+2m | Aug-27 | Aug-27 | 1 | PO Slip | ●● | Orange |
| PO Delay+4m | Oct-27 | Oct-27 | 1 | PO Slip | ●●● | Red |
| Final Acceptance | Apr-30 | Apr-30 | 1 | Acceptance | ♦ | Grey |

## Test Runner

Use `scripts/schedule_runner.py` to export the baseline schedule and generate sensitivity runs. Example:

```bash
python scripts/schedule_runner.py
```

Adjust negotiation or legal durations by passing arguments to `rerun_schedule` in the script.
