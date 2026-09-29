from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


SCHEMA = """
CREATE TABLE IF NOT EXISTS market_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instrument TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    observed_at_utc TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    source TEXT NOT NULL,
    quality_status TEXT NOT NULL,
    updated_at_utc TEXT NOT NULL,
    UNIQUE(instrument, timeframe, observed_at_utc, source)
);

CREATE TABLE IF NOT EXISTS correlations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_key TEXT NOT NULL,
    period INTEGER NOT NULL,
    observed_at_utc TEXT NOT NULL,
    value REAL NOT NULL,
    direction TEXT NOT NULL,
    strength TEXT NOT NULL,
    delta_vs_previous REAL,
    warning TEXT,
    payload_json TEXT NOT NULL,
    UNIQUE(pair_key, period, observed_at_utc)
);

CREATE TABLE IF NOT EXISTS cot_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract TEXT NOT NULL,
    report_date_utc TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    source TEXT NOT NULL,
    UNIQUE(contract, report_date_utc)
);

CREATE TABLE IF NOT EXISTS news_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    published_at_utc TEXT NOT NULL,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    sentiment TEXT NOT NULL,
    impact TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    UNIQUE(url, published_at_utc)
);

CREATE TABLE IF NOT EXISTS macro_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_key TEXT NOT NULL,
    event_time_utc TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    source TEXT NOT NULL,
    UNIQUE(event_key, event_time_utc)
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_time_utc TEXT NOT NULL,
    freshness_window_hours INTEGER NOT NULL,
    body TEXT NOT NULL,
    missing_data_json TEXT NOT NULL,
    stale_data_json TEXT NOT NULL,
    created_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS source_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    item_type TEXT NOT NULL,
    published_at_utc TEXT,
    fetched_at_utc TEXT NOT NULL,
    summary TEXT NOT NULL,
    dedupe_hash TEXT NOT NULL,
    UNIQUE(dedupe_hash)
);
"""


class Storage:
    def __init__(self, db_path: str) -> None:
        self.db_path = str(Path(db_path))
        self._init_db()

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def insert_market_snapshot(self, instrument: str, timeframe: str, observed_at_utc: str, payload: dict, source: str, quality_status: str) -> None:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO market_snapshots (instrument, timeframe, observed_at_utc, payload_json, source, quality_status, updated_at_utc)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (instrument, timeframe, observed_at_utc, json.dumps(payload, ensure_ascii=False, default=str), source, quality_status, now),
            )

    def insert_correlation(self, pair_key: str, correlation: dict, observed_at_utc: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO correlations (
                    pair_key, period, observed_at_utc, value, direction, strength, delta_vs_previous, warning, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pair_key,
                    correlation["period"],
                    observed_at_utc,
                    correlation["value"],
                    correlation["direction"],
                    correlation["strength"],
                    correlation["delta_vs_previous"],
                    correlation["warning"],
                    json.dumps(correlation, ensure_ascii=False),
                ),
            )

    def insert_source_log(
        self,
        source_name: str,
        source_url: str,
        item_type: str,
        summary: str,
        dedupe_hash: str,
        published_at_utc: str | None = None,
    ) -> None:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO source_log (source_name, source_url, item_type, published_at_utc, fetched_at_utc, summary, dedupe_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (source_name, source_url, item_type, published_at_utc, now, summary, dedupe_hash),
            )

    def insert_report(self, report_time_utc: str, freshness_window_hours: int, body: str, missing_data: list[str], stale_data: list[str]) -> None:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO reports (report_time_utc, freshness_window_hours, body, missing_data_json, stale_data_json, created_at_utc)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (report_time_utc, freshness_window_hours, body, json.dumps(missing_data), json.dumps(stale_data), now),
            )

    def count_rows(self, table: str) -> int:
        with self._connect() as conn:
            row = conn.execute(f"SELECT COUNT(1) FROM {table}").fetchone()
            return int(row[0]) if row else 0
