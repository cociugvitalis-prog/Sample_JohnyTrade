from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class MarketSnapshot:
    instrument: str
    price: float
    change_15m: float
    change_1h: float
    change_4h: float
    change_1d: float
    atr: Optional[float]
    trend: str
    support: Optional[float]
    resistance: Optional[float]
    volume: Optional[float]
    key_driver: str
    source: str
    observed_at: datetime


@dataclass(frozen=True)
class NewsItem:
    title: str
    summary: str
    url: str
    impact: str
    sentiment: str
    source: str
    published_at: datetime


@dataclass(frozen=True)
class MacroEvent:
    name: str
    country: str
    importance: str
    event_time: datetime
    source: str


@dataclass(frozen=True)
class COTPosition:
    contract: str
    long_positions: int
    short_positions: int
    previous_long: int
    previous_short: int
