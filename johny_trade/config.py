from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    db_path: str = field(default_factory=lambda: os.getenv("JOHNY_DB_PATH", "johny_trade.db"))
    request_timeout_seconds: int = field(default_factory=lambda: int(os.getenv("JOHNY_REQUEST_TIMEOUT_SECONDS", "10")))
    request_retry_count: int = field(default_factory=lambda: int(os.getenv("JOHNY_REQUEST_RETRY_COUNT", "3")))
    request_retry_backoff_seconds: float = field(
        default_factory=lambda: float(os.getenv("JOHNY_REQUEST_RETRY_BACKOFF_SECONDS", "1"))
    )
    collection_interval_seconds: int = field(default_factory=lambda: int(os.getenv("JOHNY_COLLECTION_INTERVAL_SECONDS", "900")))
    freshness_hours: int = field(default_factory=lambda: int(os.getenv("JOHNY_FRESHNESS_HOURS", "24")))
    log_level: str = field(default_factory=lambda: os.getenv("JOHNY_LOG_LEVEL", "INFO"))


TRACKED_INSTRUMENTS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD",
    "DXY", "XAUUSD", "WTI", "US10Y", "SPX", "NDX", "VIX",
]

TIMEFRAMES = ["15m", "1h", "4h", "1d"]

CORRELATION_PAIRS = [
    ("DXY", "EURUSD"),
    ("DXY", "XAUUSD"),
    ("DXY", "USDJPY"),
    ("XAUUSD", "US10Y"),
    ("USDJPY", "US10Y"),
    ("AUDUSD", "USDCNH"),
    ("USDCAD", "WTI"),
    ("GBPUSD", "EURUSD"),
    ("SPX", "VIX"),
    ("NDX", "VIX"),
]
