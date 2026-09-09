#!/usr/bin/env python3
"""Small deterministic runner for the standalone engineering workspace.

The historical entrypoint only printed the requested profile. This runner intentionally
reuses existing accepted repo capabilities instead of creating a new orchestration layer.
Profiles execute bounded commands and emit a machine-readable receipt.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "standalone_pipeline_receipt.json"

PROFILES = {
    "index": [
        [sys.executable, "app/index_repo.py"],
    ],
    "qplant-smoke": [
        [sys.executable, "scripts/build_index.py", "--check"],
        [
            sys.executable,
            "scripts/recursive_build.py",
            "--index",
            "GLOBAL_index.json",
            "--out",
            "outputs/qplant_legacy_metrics.json",
            "--smoke",
        ],
    ],
    "default": [
        [sys.executable, "app/index_repo.py"],
        [sys.executable, "scripts/build_index.py", "--check"],
        [
            sys.executable,
            "scripts/recursive_build.py",
            "--index",
            "GLOBAL_index.json",
            "--out",
            "outputs/qplant_legacy_metrics.json",
            "--smoke",
        ],
    ],
}


def run(profile: str) -> dict:
    if profile not in PROFILES:
        raise ValueError(f"Unknown profile {profile!r}; choose from {sorted(PROFILES)}")

    receipt = {
        "schema": "codespaces-standalone-pipeline-receipt/v0.1",
        "profile": profile,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "commands": [],
        "status": "RUNNING",
        "authority_boundary": (
            "Standalone execution/diagnostic evidence only. QPS bidder compliance and release "
            "credit require explicit child source binding in cryoplant-project."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)

    try:
        for command in PROFILES[profile]:
            print("+", " ".join(command), flush=True)
            completed = subprocess.run(
                command,
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            entry = {
                "command": command,
                "returncode": completed.returncode,
                "stdout_tail": completed.stdout[-4000:],
                "stderr_tail": completed.stderr[-4000:],
            }
            receipt["commands"].append(entry)
            if completed.stdout:
                print(completed.stdout, end="")
            if completed.stderr:
                print(completed.stderr, end="", file=sys.stderr)
            if completed.returncode != 0:
                receipt["status"] = "FAIL"
                receipt["failed_command"] = command
                return receipt
        receipt["status"] = "PASS"
        return receipt
    finally:
        receipt["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        OUT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        print(f"receipt: {OUT}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile",
        default="default",
        choices=sorted(PROFILES),
        help="bounded standalone execution profile",
    )
    args = parser.parse_args()
    receipt = run(args.profile)
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
