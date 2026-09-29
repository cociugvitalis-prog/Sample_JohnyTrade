from __future__ import annotations

from datetime import datetime, timezone
from math import sqrt
from statistics import mean
from typing import Iterable, Sequence

from .models import COTPosition


def calculate_cot_signal(position: COTPosition) -> dict:
    net = position.long_positions - position.short_positions
    previous_net = position.previous_long - position.previous_short
    net_change = net - previous_net
    ratio = (position.long_positions / position.short_positions) if position.short_positions else None
    bias = "bullish" if net > 0 else "bearish" if net < 0 else "neutral"
    return {
        "contract": position.contract,
        "net": net,
        "previous_net": previous_net,
        "net_change": net_change,
        "long_short_ratio": ratio,
        "bias": bias,
    }


def calculate_returns(values: Sequence[float]) -> list[float]:
    if len(values) < 2:
        return []
    returns: list[float] = []
    for prev, current in zip(values, values[1:]):
        if prev == 0:
            returns.append(0.0)
        else:
            returns.append((current - prev) / prev)
    return returns


def _pearson(x: Sequence[float], y: Sequence[float]) -> float:
    mx = mean(x)
    my = mean(y)
    cov = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sx = sqrt(sum((a - mx) ** 2 for a in x))
    sy = sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return 0.0
    return cov / (sx * sy)


def correlation_strength(value: float) -> str:
    v = abs(value)
    if v >= 0.8:
        return "very strong"
    if v >= 0.6:
        return "strong"
    if v >= 0.4:
        return "moderate"
    if v >= 0.2:
        return "weak"
    return "very weak"


def rolling_correlation_summary(
    series_a: Sequence[float],
    series_b: Sequence[float],
    periods: Iterable[int] = (20, 60, 120),
) -> list[dict]:
    returns_a = calculate_returns(series_a)
    returns_b = calculate_returns(series_b)
    results: list[dict] = []
    for period in periods:
        if len(returns_a) < period or len(returns_b) < period:
            continue
        current_a = returns_a[-period:]
        current_b = returns_b[-period:]
        current = _pearson(current_a, current_b)

        previous = None
        if len(returns_a) >= period + 1 and len(returns_b) >= period + 1:
            previous = _pearson(returns_a[-period - 1 : -1], returns_b[-period - 1 : -1])

        delta = None if previous is None else current - previous
        direction = "positive" if current >= 0 else "negative"
        unstable = abs(current) < 0.2 or (delta is not None and abs(delta) > 0.25)
        warning = "correlation weakened or unstable" if unstable else ""
        results.append(
            {
                "period": period,
                "value": current,
                "direction": direction,
                "strength": correlation_strength(current),
                "delta_vs_previous": delta,
                "warning": warning,
                "calculated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
        )
    return results


def classify_trend(changes: Sequence[float]) -> str:
    if all(c > 0 for c in changes):
        return "uptrend"
    if all(c < 0 for c in changes):
        return "downtrend"
    return "mixed"
