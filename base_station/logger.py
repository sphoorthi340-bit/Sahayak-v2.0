"""SQLite persistence for Sahayak telemetry events."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from .packet_parser import Event


CREATE_EVENTS_SQL = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    received_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    raw TEXT NOT NULL,
    t_ms INTEGER,
    node INTEGER,
    event_type TEXT NOT NULL,
    origin INTEGER,
    sequence INTEGER,
    previous_hop INTEGER,
    next_hop INTEGER,
    hop INTEGER,
    ttl INTEGER,
    rssi INTEGER,
    snr REAL,
    queue INTEGER,
    retry INTEGER,
    state TEXT,
    outcome TEXT,
    scenario_id TEXT,
    firmware_version TEXT
)
"""


class EventLogger:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(database_path)
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.database_path)
        self.connection.execute(CREATE_EVENTS_SQL)
        self.connection.commit()

    def log(self, event: Event, scenario_id: str | None = None,
            firmware_version: str | None = None) -> None:
        self.connection.execute(
            """
            INSERT INTO events (
                raw, t_ms, node, event_type, origin, sequence,
                previous_hop, next_hop, hop, ttl, rssi, snr, queue,
                retry, state, outcome, scenario_id, firmware_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.raw, event.t_ms, event.node, event.event_type,
                event.origin, event.sequence, event.previous_hop,
                event.next_hop, event.hop, event.ttl, event.rssi, event.snr,
                event.queue, event.retry, event.state, event.outcome,
                scenario_id, firmware_version,
            ),
        )
        self.connection.commit()

    def log_many(self, events: Iterable[Event]) -> None:
        for event in events:
            self.log(event)

    def count(self) -> int:
        row = self.connection.execute("SELECT COUNT(*) FROM events").fetchone()
        return int(row[0]) if row else 0

    def close(self) -> None:
        self.connection.close()
