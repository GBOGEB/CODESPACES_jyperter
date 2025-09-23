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
