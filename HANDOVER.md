HEPAK – Agent Integration Helper Refactor

Handover & Runtime Summary (v1.1)
Date: 2025‑08‑15 (Europe/Brussels)

1. Purpose & Scope
•Stabilize and de‑risk the helper used to analyze Python sources and propose agent templates.
•Add observability (structured logging, timings, persistent metrics) for DMAIC tracking and AHT trends.
•Harden the problems exporter so ruff/mypy results reliably land under index_outputs/.
•Keep behavior backward‑compatible (plans & templates unchanged in shape).

2. What You Get (At a Glance)
•Refactored AGENT_INTEGRATION_HELPER.py with:
•Structured logging (-v/-vv/-q)
•Configurable discovery (--include/--exclude/--size-limit-mb/--follow-symlinks)
•In‑run cache (avoid re‑parsing unchanged files in the same run)
•Metrics output (--metrics-out) + debug summary (--debug-run)
•Robust scripts/export_problems.py:
•Works as script or module
•Prefers mypy JSON; tolerant fallback parser
•Writes index_outputs/problems.json
•A repeatable snapshot flow to generate a single markdown runtime summary for handover.

⸻

3. Planned vs. Outcome

AreaPlannedOutcome
LoggingReplace prints, add verbosity flags✅ logging + -v/-vv/-q
DiscoveryAdd include/exclude, size, symlink opts✅ --include/--exclude/--size-limit-mb/--follow-symlinks
PerformanceAvoid re‑parse within run✅ mtime‑based in‑run cache
DecouplingAvoid heavy imports at module import time✅ Orchestrator only referenced in generated templates
MetricsPersist timings & counts for DMAIC✅ --metrics-out → JSON
Debug UXQuick outcome without opening JSONs✅ --debug-run (top‑5)
Problems exportResilient ruff/mypy capture✅ JSON first; fallback OK
DocsClear handover + how‑to✅ This document

Still to do (next iteration):
•KPI aggregation across runs (extend scripts/kpi_snapshot.py or add metrics_aggregate.py)
•Optional parallel analysis for large repos
•Cross‑run cache (persisted on disk)
•GUI pass (separate): same metrics & debug panel

⸻

4. How to Run (three steps)

4.1 Analyze, Plan, Generate Templates + Metrics

python AGENT_INTEGRATION_HELPER.py \\
  --project-root . \\
  --analyze --generate-plan --generate-templates \\
  --include "src/**/*.py" \\
  --exclude "venv/" "build/**" \\
  --size-limit-mb 10 \\
  --report index_outputs/integration_report.json \\
  --output-dir generated_agents \\
  --metrics-out index_outputs/integration_metrics.json \\
  --debug-run \\
  -v

4.2 Export Static Analysis Problems (ruff + mypy)

python scripts/export_problems.py

Outputs index_outputs/problems.json.

4.3 Produce a One‑File Runtime Snapshot (Markdown)

python scripts/handover_snapshot.py

Outputs index_outputs/HANDOVER_RUNTIME_SUMMARY.md.

⸻

5. Artifacts & Locations
•index_outputs/integration_report.json – plan & recommendations
•index_outputs/integration_metrics.json – timings (discovery/analysis/plan/templates), counts, args
•index_outputs/problems.json – normalized ruff/mypy issues
•gener...generated_agents/*.py – generated agent templates

Keep these directories in CI artifacts and commits to track DMAIC/AHT over time.

⸻

6. KPIs, AHT & How We Measure

Now captured per run in integration_metrics.json:
•durations_s.discovery, analysis, plan, templates
•discovered_count, analyzed_count
•Plan summary: high_potential, medium_potential, low_potential
•args echo for reproducibility

Recommended KPIs (roll‑ups across runs):
•AHT Discovery/Analysis/Plan/Templates: mean/median/95p
•Coverage: analyzed_count / discovered_count
•Yield: high_potential / analyzed_count
•Stability: runs without exceptions (%)

Next step: extend scripts/kpi_snapshot.py to ingest integration_metrics.json and problems.json, and write a small data/kpi.json or data/kpi.csv with trends.

⸻

7. Change Log (Conventional Commits)
•feat(helper): structured logging, verbosity flags
•feat(helper): configurable discovery (include/exclude/size/symlink)
•feat(helper): in‑run AST cache (mtime keyed)
•feat(helper): --metrics-out JSON + --debug-run
•refactor(helper): decouple import‑time orchestrator dependency
•fix(scripts): robust package/script path handling in export_problems.py
•feat(scripts): prefer mypy JSON; fallback parser hardened
•docs(handover): this file

Tag suggestion: integration-helper-v1.1 (2025‑08‑15)

⸻

8. Repository Navigation (quick map)

HEPAK/
├─ AGENT_INTEGRATION_HELPER.py          # refactored helper (CLI)
├─ generated_agents/                    # output: agent templates (*.py)
├─ index_outputs/                       # output: reports & KPIs
│  ├─ integration_report.json
│  ├─ integration_metrics.json
│  ├─ problems.json
│  └─ HANDOVER_RUNTIME_SUMMARY.md
└─ scripts/
   ├─ export_problems.py               # ruff/mypy → problems.json
   └─ handover_snapshot.py             # builds the one-file runtime summary


⸻

9. Troubleshooting
•NameError: os/time not defined – fixed by imports in helper (present in v1.1)
•ImportError: attempted relative import (export_problems.py) – run as shown; script now handles both modes
•mypy parsing errors – script prefers JSON; fallback text parser is tolerant
•No outputs? – ensure index_outputs/ exists or let the tools create it; confirm --report/--metrics-out paths

⸻

10. Word‑Style Summary (≈120 words)

This iteration modernizes the HEPAK Agent Integration Helper with structured logging, configurable file discovery, and in‑run caching to improve efficiency and maintainability while preserving output formats. The CLI now emits measurable timings and counts and can persist a metrics JSON for DMAIC/AHT tracking. A new --debug-run flag prints a concise summary of top recommendations. The problems exporter is hardened to capture ruff/mypy findings reliably and write them under index_outputs/. Artifacts are standardized for CI archival and future trend analysis. Next, we’ll aggregate KPIs across runs, explore parallel analysis for large repositories, add a persisted cross‑run cache, and apply the same metrics/debug pattern to the GUI in a separate, low‑risk iteration.

⸻

11. Appendix A — Minimal Snapshot Script

Save as scripts/handover_snapshot.py. It collects current artifacts and writes index_outputs/HANDOVER_RUNTIME_SUMMARY.md. No external deps beyond stdlib.

#!/usr/bin/env python3
import json, os, datetime
from pathlib import Path

OUT_DIR = Path("index_outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)
SUMMARY = OUT_DIR / "HANDOVER_RUNTIME_SUMMARY.md"

def _read(path):
    p = Path(path)
    if not p.exists():
        return None
    with p.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return None

def main() -> None:
    metrics = _read(OUT_DIR / "integration_metrics.json")
    report  = _read(OUT_DIR / "integration_report.json")
    problems = _read(OUT_DIR / "problems.json")

    gen_dir = Path("generated_agents")
    gen_count = len(list(gen_dir.glob("*.py"))) if gen_dir.exists() else 0

    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

    lines = [
        "# HEPAK – Runtime Summary",
        f"_Generated: {ts}_",
        "",
        "## Metrics",
    ]

    if metrics:
        d = metrics.get("durations_s", {})
        lines += [
            f"- Discovery: {d.get('discovery', 'n/a')} s",
            f"- Analysis:  {d.get('analysis',  'n/a')} s",
            f"- Plan:      {d.get('plan',      'n/a')} s",
            f"- Templates: {d.get('templates', 'n/a')} s",
            f"- Discovered files: {metrics.get('discovered_count', 'n/a')}",
            f"- Analyzed files:   {metrics.get('analyzed_count', 'n/a')}",
            "",
            "### Plan Summary",
        ]
        summ = (metrics.get("summary") or {})
        lines += [
            f"- High potential:   {summ.get('high_potential', 'n/a')}",
            f"- Medium potential: {summ.get('medium_potential', 'n/a')}",
            f"- Low potential:    {summ.get('low_potential', 'n/a')}",
        ]
    else:
        lines += ["- No `integration_metrics.json` found. Run the helper first."]

    lines += ["", "## Problems"]
    if problems:
        if isinstance(problems, dict):
            total = problems.get("total", None)
            if total is not None:
                lines += [f"- Reported issues: {total}"]
            else:
                lines += [f"- Problems keys: {list(problems.keys())[:6]}..."]
        else:
            lines += ["- Problems present (non-dict format)"]
    else:
        lines += ["- No `problems.json` found. Run `scripts/export_problems.py`."]

    lines += ["", "## Generated Agent Templates", f"- Count: {gen_count}"]

    if report:
        lines += ["", "## Integration Report (brief)"]
        if isinstance(report, dict) and "summary" in report:
            lines += [f"- Summary: {report['summary'][:400]}..."]
        else:
            lines += ["- Report loaded (structure varies)."]
    else:
        lines += ["", "## Integration Report", "- Not found."]

    SUMMARY.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {SUMMARY}")

if __name__ == "__main__":
    main()

Run:

python scripts/handover_snapshot.py


⸻

12. Appendix B — Suggested Next Steps (Actionable)
1.KPI Aggregation (preferred next)

•Extend scripts/kpi_snapshot.py to read index_outputs/integration_metrics.json + problems.json,
compute AHT per stage & rolling trends, write data/kpi.json (and/or CSV).

2.Performance

•Add --workers N to helper; parallelize AST analysis with concurrent.futures.

3.Cross‑Run Cache

•Persist cache on disk using file path + size + mtime key to skip parsing on subsequent runs.

4.GUI Iteration (separate PR)

•Mirror CLI metrics (gui_metrics.json), add “Debug” panel (top‑5 recommendations), verbosity toggle.

⸻

If you want, I can also produce a ZIP manifest outline (for CI artifact packing) or draft the kpi_snapshot.py update next.
