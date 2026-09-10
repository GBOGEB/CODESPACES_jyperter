# DMAIC Click-Pulse Ledger - CODESPACES_jyperter

Date: 2026-09-10
Mode: fast human-click analogue: click, observe, change, record, repeat.

## Pulse Rule

Every pulse must advance one frame only. A frame can be a census, command, repair, proof, or next-red capture. Brute force is allowed only when each attempt leaves a receipt.

## Cadence

| Pulse | Interval | DMAIC Phase | Effort Mode | Target | Exit Condition |
| --- | --- | --- | --- | --- | --- |
| P0 | 0-15 min | Define | Scan | Repo role and surfaces | MIP tracker merged or accepted |
| P1 | 15-30 min | Measure | Census | Files, notebooks, CI, runners | Census counts recorded |
| P2 | 30-60 min | Analyse | First red | Broken command or stale path | First failure captured exactly |
| P3 | 60-90 min | Improve | Repair | Minimal runner/notebook path | Command changes behaviour |
| P4 | 90-120 min | Control | Receipt | Exact-head smoke proof | SHA-bound proof recorded |

## First Clicks

1. Count notebooks, tests, workflow files, scripts, and runtime debris.
2. Try canonical smoke command from README/Makefile.
3. If red, recurse on first red only.
4. If green, bind receipt and move to notebook execution.

## Brute Force Guard

Do not widen scope after a failure. Spend effort on the observed failure until it changes state, then click again.
