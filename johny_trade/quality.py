from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Callable, Iterable, Tuple, TypeVar

T = TypeVar("T")


def ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def is_fresh(timestamp: datetime, now: datetime | None = None, freshness_hours: int = 24) -> bool:
    now = ensure_utc(now or datetime.now(timezone.utc))
    ts = ensure_utc(timestamp)
    return now - ts <= timedelta(hours=freshness_hours)


def split_fresh_stale(items: Iterable[T], timestamp_getter: Callable[[T], datetime], freshness_hours: int = 24) -> Tuple[list[T], list[T]]:
    fresh: list[T] = []
    stale: list[T] = []
    now = datetime.now(timezone.utc)
    for item in items:
        (fresh if is_fresh(timestamp_getter(item), now=now, freshness_hours=freshness_hours) else stale).append(item)
    return fresh, stale


def missing_fields(payload: dict, required_fields: list[str]) -> list[str]:
    missing: list[str] = []
    for field in required_fields:
        value = payload.get(field)
        if value is None or value == "":
            missing.append(field)
    return missing
