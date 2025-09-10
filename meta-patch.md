# Meta Patch

This file contains the content necessary to reconstruct the conversation tracking scaffolding. Each block is prefixed by the target file path.

```path:sql/schema.sql
CREATE TABLE IF NOT EXISTS convo_session (
  session_id      TEXT PRIMARY KEY,
  title           TEXT,
  started_at_utc  DATETIME,
  ended_at_utc    DATETIME,
  project_tag     TEXT,
  risk_level      TEXT
);

CREATE TABLE IF NOT EXISTS convo_turn (
  session_id      TEXT,
  turn_id         INTEGER,
  speaker         TEXT,
  ts_utc          DATETIME,
  token_count_est INTEGER,
  text            TEXT,
  topic_hash      TEXT,
  turn_flag       TEXT,
  PRIMARY KEY (session_id, turn_id)
);

CREATE TABLE IF NOT EXISTS convo_kpi (
  session_id       TEXT PRIMARY KEY,
  total_turns      INTEGER,
  user_turns       INTEGER,
  assistant_turns  INTEGER,
  avg_tokens_turn  REAL,
  window_bursts    INTEGER,
  stickiness_score REAL,
  hot_zone_ratio   REAL,
  cold_zone_ratio  REAL
);
```

```path:scripts/kpi_pipeline.py
"""Minimal KPI pipeline for chat session analytics.

This script loads a JSON export describing a chat session, normalizes it
into a SQLite database using `sql/schema.sql`, computes simple KPIs and
emits a Markdown report. It implements the conceptual steps from the
contract specification.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Dict, Any

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"
REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


def load_export_json(path: Path) -> Dict[str, Any]:
    """Load exported chat JSON."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_to_sql(data: Dict[str, Any], db_path: Path | str = ":memory:") -> sqlite3.Connection:
    """Populate SQLite DB with session and turn data."""
    conn = sqlite3.connect(db_path)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    session = data["session"]
    turns = data["turns"]

    conn.execute(
        """
        INSERT OR REPLACE INTO convo_session
        (session_id, title, started_at_utc, ended_at_utc, project_tag, risk_level)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            session["session_id"],
            session.get("title"),
            session.get("started_at_utc"),
            session.get("ended_at_utc"),
            session.get("project_tag"),
            session.get("risk_level"),
        ),
    )

    for turn in turns:
        conn.execute(
            """
            INSERT INTO convo_turn
            (session_id, turn_id, speaker, ts_utc, token_count_est, text, topic_hash, turn_flag)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session["session_id"],
                turn["turn_id"],
                turn["speaker"],
                turn.get("ts_utc"),
                turn.get("token_count_est"),
                turn.get("text"),
                turn.get("topic_hash"),
                turn.get("turn_flag"),
            ),
        )

    conn.commit()
    return conn


def compute_kpis(conn: sqlite3.Connection, session_id: str) -> Dict[str, Any]:
    """Compute basic KPIs for the session."""
    cur = conn.cursor()
    kpi: Dict[str, Any] = {}

    user_turns, assistant_turns, total_turns = cur.execute(
        """
        SELECT
            SUM(CASE WHEN speaker='user' THEN 1 ELSE 0 END) AS user_turns,
            SUM(CASE WHEN speaker='assistant' THEN 1 ELSE 0 END) AS assistant_turns,
            COUNT(*) AS total_turns
        FROM convo_turn WHERE session_id = ?
        """,
        (session_id,),
    ).fetchone()

    kpi["user_turns"] = user_turns or 0
    kpi["assistant_turns"] = assistant_turns or 0
    kpi["total_turns"] = total_turns or 0

    (avg_tokens_turn,) = cur.execute(
        "SELECT AVG(token_count_est) FROM convo_turn WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    kpi["avg_tokens_turn"] = avg_tokens_turn or 0

    (topic_shifts,) = cur.execute(
        """
        SELECT SUM(
          CASE WHEN topic_hash <> LAG(topic_hash) OVER (ORDER BY turn_id)
               THEN 1 ELSE 0 END)
        FROM convo_turn WHERE session_id = ?
        """,
        (session_id,),
    ).fetchone()
    kpi["topic_shifts"] = topic_shifts or 0

    hot_ratio, cold_ratio = cur.execute(
        """
        SELECT
            AVG(CASE WHEN turn_flag='HOT' THEN 1 ELSE 0 END) AS hot_zone_ratio,
            AVG(CASE WHEN turn_flag='COLD' THEN 1 ELSE 0 END) AS cold_zone_ratio
        FROM convo_turn WHERE session_id = ?
        """,
        (session_id,),
    ).fetchone()
    kpi["hot_zone_ratio"] = hot_ratio or 0
    kpi["cold_zone_ratio"] = cold_ratio or 0

    conn.execute(
        """
        INSERT OR REPLACE INTO convo_kpi
        (session_id, total_turns, user_turns, assistant_turns, avg_tokens_turn,
         window_bursts, stickiness_score, hot_zone_ratio, cold_zone_ratio)
        VALUES (?, ?, ?, ?, ?, 0, 0, ?, ?)
        """,
        (
            session_id,
            kpi["total_turns"],
            kpi["user_turns"],
            kpi["assistant_turns"],
            kpi["avg_tokens_turn"],
            kpi["hot_zone_ratio"],
            kpi["cold_zone_ratio"],
        ),
    )
    conn.commit()
    return kpi


def render_screen_summary(kpi: Dict[str, Any]) -> str:
    """Render KPI summary for screen output."""
    lines = ["Session KPI Summary:"]
    for key, value in kpi.items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def write_md_report(session_id: str, kpi: Dict[str, Any]) -> Path:
    """Write Markdown report for the session."""
    REPORTS_DIR.mkdir(exist_ok=True)
    report_path = REPORTS_DIR / f"{session_id}.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Chat Session Report\n\nSession ID: {session_id}\n\n")
        for key, value in kpi.items():
            f.write(f"- **{key}**: {value}\n")
    return report_path


def kpi_pipeline(export_json: Path, db_path: Path | str = ":memory:") -> Dict[str, Any]:
    """Run the KPI pipeline end-to-end."""
    data = load_export_json(export_json)
    conn = normalize_to_sql(data, db_path=db_path)
    session_id = data["session"]["session_id"]
    kpi = compute_kpis(conn, session_id)
    write_md_report(session_id, kpi)
    return kpi


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compute KPIs for a chat JSON export")
    parser.add_argument("export_json", type=Path, help="Path to export JSON file")
    parser.add_argument("--db", type=Path, default=Path("kpi.db"), help="SQLite database path")
    args = parser.parse_args()

    metrics = kpi_pipeline(args.export_json, db_path=args.db)
    print(render_screen_summary(metrics))
```

```path:reports/CURRENT_CHAT_REPORT.md
# Chat Session Report

Session ID: CURRENT_SESSION_YYYYMMDDThhmmssZ

## KPI Snapshot

| Metric | Value |
| ------ | ----- |
| total_turns | <compute> |
| user_turns | <compute> |
| assistant_turns | <compute> |
| avg_tokens_turn | <compute> |
| topic_shifts | <compute> |
| stickiness_score | <compute> |
| hot_zone_ratio | <compute> |
| cold_zone_ratio | <compute> |

## DMAIC Log

- Define: Planned capture of chat session.
- Measure: KPIs computed.
- Analyze: TBD.
- Improve: TBD.
- Control: TBD.
```

```path:indices/index_of_sessions.json
{
  "CURRENT_SESSION_YYYYMMDDThhmmssZ": {
    "title": "Chat History Indexing & KPIs",
    "hash": "<raw_export_hash>"
  }
}
```

