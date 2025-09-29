# Coldbox Heat Balance (4.5 K Equivalent)

This document summarizes the heat load conversion and mass-flow data for the coldbox. All loads are converted to a 4.5 K equivalent to allow direct comparison.

The 4.5 K equivalent load for any component is computed from the actual load \(Q_T\) at temperature \(T\) via:

\[
Q_{4.5\,\text{K}} = Q_T \times \frac{\text{COP}_{4.5\,\text{K}}}{\text{COP}_T}
\]

For the present system the overall 4.5 K equivalent heat load should add up to **3.4 kW**.

## Load breakdown

| Description | Temperature (K) | Load (W) | 4.5 K Equivalent (W) |
|-------------|-----------------|---------:|---------------------:|
| 2 K cold load | 2 | 900 | 2041 |
| 4.5 K stage miscellaneous | 4.5 | 1359 | 1359 |
| **Total** | | | **3400** |

## Mass-flow summary

- 47 g/s helium supply at 4.5 K and 3 bar (≈50 g/s from master data).
- 45 g/s return at 2 K and 32 mbar.
- 2 g/s warm return (superheated He via coupler).
- 80 g/s supply at 40 K with 60 K return.
- Remaining coldbox flows in the warm section at 14 bar(a) and 300 K through WCS‑HP / QRB‑HP.
- VLP outlet from QRB‑VLP at 450 mbar and 300 K.

All numerical values are repeated in `../data/coldbox_heat_balance.csv` for traceability and import into spreadsheet tools.

## Reproducibility

The CSV file listed above enables repeatable recalculation of the total load.  Each line records the original temperature, the measured heat load, and the derived 4.5 K equivalent using the equation given earlier.
