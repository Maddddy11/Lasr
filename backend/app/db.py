from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    complexity_score REAL NOT NULL,
    pii_types TEXT NOT NULL,
    redaction_count INTEGER NOT NULL,
    estimated_cost REAL NOT NULL,
    estimated_carbon REAL NOT NULL,
    latency_ms INTEGER NOT NULL,
    status TEXT NOT NULL
);
"""


def get_connection(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()


def insert_event(db_path: str, payload: dict[str, Any]) -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO events (
              timestamp, user_id, role, provider, model, complexity_score,
              pii_types, redaction_count, estimated_cost, estimated_carbon,
              latency_ms, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["timestamp"],
                payload["user_id"],
                payload["role"],
                payload["provider"],
                payload["model"],
                payload["complexity_score"],
                json.dumps(payload["pii_types"]),
                payload["redaction_count"],
                payload["estimated_cost"],
                payload["estimated_carbon"],
                payload["latency_ms"],
                payload["status"],
            ),
        )
        conn.commit()


def list_events(db_path: str, limit: int = 100) -> list[dict[str, Any]]:
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT timestamp, user_id, role, provider, model, complexity_score,
                   pii_types, redaction_count, estimated_cost, estimated_carbon,
                   latency_ms, status
            FROM events
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    events: list[dict[str, Any]] = []
    for row in rows:
        event = dict(row)
        event["pii_types"] = json.loads(event["pii_types"])
        events.append(event)
    return events
