from __future__ import annotations

from datetime import datetime, timezone


def _fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.4f}"


def generate_report(report_data: dict) -> str:
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines: list[str] = []

    lines.append(f"1) Report time (UTC): {generated_at}")
    lines.append("   Data freshness window: last 24 hours")
    lines.append("")
    lines.append("2) Market state summary")
    lines.append(f"   {report_data.get('market_overview', 'No summary available')}\n")

    lines.append("3) Instrument table")
    lines.append("   instrument | direction | 15m/1h/4h | key driver | volatility | data quality")
    for row in report_data.get("instrument_rows", []):
        lines.append(
            "   "
            + f"{row['instrument']} | {row['direction']} | {row['change_15m']}/{row['change_1h']}/{row['change_4h']} | "
            + f"{row['driver']} | {row['volatility']} | {row['quality']}"
        )

    lines.append("\n4) DXY impact on EURUSD, XAUUSD, USDJPY")
    lines.append(f"   {report_data.get('dxy_impact', 'n/a')}")

    lines.append("5) US10Y impact on USDJPY and XAUUSD")
    lines.append(f"   {report_data.get('us10y_impact', 'n/a')}")

    lines.append("6) Correlations")
    for c in report_data.get("correlations", []):
        lines.append(
            "   "
            + f"{c['pair']} period={c['period']} corr={_fmt(c['value'])} dir={c['direction']} "
            + f"strength={c['strength']} delta={_fmt(c['delta'])} warning={c['warning'] or '-'}"
        )

    lines.append("7) COT signals")
    for cot in report_data.get("cot", []):
        lines.append(
            "   "
            + f"{cot['contract']} net={cot['net']} change={cot['net_change']} bias={cot['bias']}"
        )

    lines.append("8) Macro events")
    for event in report_data.get("macro", []):
        lines.append(f"   {event}")

    lines.append("9) News classification")
    for news in report_data.get("news", []):
        lines.append(f"   [{news['impact']}] [{news['sentiment']}] {news['title']} ({news['source']})")

    lines.append("10) Bullish scenario")
    lines.append(f"   {report_data.get('bullish', 'Signal absent')}")

    lines.append("11) Bearish scenario")
    lines.append(f"   {report_data.get('bearish', 'Signal absent')}")

    lines.append("12) Conflicting signals and risks")
    lines.append(f"   {report_data.get('risks', 'n/a')}")

    lines.append("13) Missing or stale data")
    for item in report_data.get("missing_or_stale", []):
        lines.append(f"   {item}")

    lines.append("14) Neutral conclusion")
    lines.append(f"   {report_data.get('conclusion', 'Data supports scenarios, but requires confirmation.')}\n")

    lines.append("---")
    lines.append("FACTUAL DATA")
    lines.append(report_data.get("factual_data", "n/a"))
    lines.append("CALCULATED METRICS")
    lines.append(report_data.get("calculated_metrics", "n/a"))
    lines.append("CORRELATIONS")
    lines.append(report_data.get("correlation_notes", "n/a"))
    lines.append("ANALYTICAL INTERPRETATION")
    lines.append(report_data.get("interpretation", "n/a"))
    lines.append("SCENARIOS (NOT TRADING RECOMMENDATIONS)")
    lines.append(report_data.get("scenario_notes", "n/a"))

    return "\n".join(lines)
