from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STEP_DEFINITIONS = (
    ("S1", "Codex IDE / Orchestrator", "author"),
    ("S2", "GitHub CI", "verify"),
    ("S3", "RedHat / Container Executor", "execute"),
    ("S4", "MASTER.doc Parser / RTM", "transform"),
    ("S5", "Human Outputs Dashboard", "publish"),
)

STATUS_META = {
    "success": {"label": "PASS", "color": "#1f7a4d", "background": "#dff5e8"},
    "fail": {"label": "FAIL", "color": "#a61b1b", "background": "#fde7e7"},
    "running": {"label": "RUNNING", "color": "#075985", "background": "#e0f2fe"},
    "pending": {"label": "PENDING", "color": "#5f6368", "background": "#eef1f4"},
    "cancelled": {"label": "CANCELLED", "color": "#8a4b08", "background": "#fff1d6"},
    "blocked": {"label": "BLOCKED", "color": "#7e22ce", "background": "#f3e8ff"},
    "unknown": {"label": "UNKNOWN", "color": "#4b5563", "background": "#f3f4f6"},
}

GITHUB_STATUS_MAP = {
    "success": "success",
    "failure": "fail",
    "failed": "fail",
    "timed_out": "fail",
    "action_required": "fail",
    "startup_failure": "fail",
    "cancelled": "cancelled",
    "stale": "cancelled",
    "in_progress": "running",
    "queued": "pending",
    "requested": "pending",
    "waiting": "pending",
    "pending": "pending",
    "neutral": "unknown",
    "skipped": "unknown",
    None: "pending",
}


@dataclass
class StepState:
    id: str
    name: str
    role: str
    status: str = "pending"
    source: str = "default"
    detail: str = "No execution evidence yet"
    updated_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["visual"] = STATUS_META.get(self.status, STATUS_META["unknown"])
        return data


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_status(value: Any) -> str:
    if value is None:
        return "pending"
    key = str(value).strip().lower()
    if key in STATUS_META:
        return key
    return GITHUB_STATUS_MAP.get(key, "unknown")


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def write_step_status(
    path: Path, step_id: str, status: str, detail: str | None = None
) -> dict[str, Any]:
    """Update one status while preserving every unrelated manifest field."""
    data = load_manifest(path)
    statuses = data.setdefault("step_status", {})
    if not isinstance(statuses, dict):
        statuses = {}
        data["step_status"] = statuses
    statuses[step_id] = normalize_status(status)

    evidence = data.setdefault("step_evidence", {})
    if not isinstance(evidence, dict):
        evidence = {}
        data["step_evidence"] = evidence
    evidence[step_id] = {
        "detail": detail or "Status updated by MCP GUI",
        "updated_at": utc_now(),
        "writer": "gui_candidate_bundle",
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(tmp, path)
    return data


def build_steps(
    manifest: dict[str, Any],
    github: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    statuses = (
        manifest.get("step_status", {})
        if isinstance(manifest.get("step_status", {}), dict)
        else {}
    )
    evidence = (
        manifest.get("step_evidence", {})
        if isinstance(manifest.get("step_evidence", {}), dict)
        else {}
    )
    github = github or {}
    steps: list[dict[str, Any]] = []

    for step_id, name, role in STEP_DEFINITIONS:
        status = normalize_status(statuses.get(step_id))
        source = "manifest" if step_id in statuses else "default"
        detail = "No execution evidence yet"
        updated_at = None

        if isinstance(evidence.get(step_id), dict):
            detail = str(evidence[step_id].get("detail") or detail)
            updated_at = evidence[step_id].get("updated_at")

        if step_id in github:
            status = normalize_status(github[step_id].get("status"))
            source = "github"
            detail = str(github[step_id].get("detail") or detail)
            updated_at = github[step_id].get("updated_at") or updated_at

        steps.append(
            StepState(
                step_id,
                name,
                role,
                status,
                source,
                detail,
                updated_at,
            ).to_dict()
        )
    return steps
