from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Sequence

from .analytics import calculate_cot_signal, rolling_correlation_summary
from .collector import make_dedupe_hash
from .config import CORRELATION_PAIRS, Settings
from .quality import missing_fields, split_fresh_stale
from .reporting import generate_report
from .storage import Storage


class JohnyTradeAgent:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        logging.basicConfig(level=getattr(logging, self.settings.log_level.upper(), logging.INFO))
        self.logger = logging.getLogger(self.__class__.__name__)
        self.storage = Storage(self.settings.db_path)

    def run_cycle(self, payload: dict) -> str:
        now = datetime.now(timezone.utc)
        required = ["market_snapshots", "correlation_inputs", "cot_positions", "macro_events", "news_items"]
        missing = missing_fields(payload, required)

        snapshots = payload.get("market_snapshots", [])
        fresh_snapshots, stale_snapshots = split_fresh_stale(
            snapshots,
            timestamp_getter=lambda item: item["observed_at"],
            freshness_hours=self.settings.freshness_hours,
        )

        for snap in snapshots:
            quality = "fresh" if snap in fresh_snapshots else "stale"
            self.storage.insert_market_snapshot(
                instrument=snap["instrument"],
                timeframe=snap["timeframe"],
                observed_at_utc=snap["observed_at"].astimezone(timezone.utc).isoformat(timespec="seconds"),
                payload=snap,
                source=snap.get("source", "unknown"),
                quality_status=quality,
            )

        correlation_rows: list[dict] = []
        correlation_inputs = payload.get("correlation_inputs", {})
        for left, right in CORRELATION_PAIRS:
            key = f"{left}:{right}"
            pair_data = correlation_inputs.get(key)
            if not pair_data:
                continue
            summary = rolling_correlation_summary(pair_data["left"], pair_data["right"])
            for row in summary:
                self.storage.insert_correlation(pair_key=key, correlation=row, observed_at_utc=now.isoformat(timespec="seconds"))
                correlation_rows.append({
                    "pair": key,
                    "period": row["period"],
                    "value": row["value"],
                    "direction": row["direction"],
                    "strength": row["strength"],
                    "delta": row["delta_vs_previous"],
                    "warning": row["warning"],
                })

        cot_rows = [calculate_cot_signal(item) for item in payload.get("cot_positions", [])]

        for news in payload.get("news_items", []):
            dedupe_hash = make_dedupe_hash(news["url"], news["published_at"].isoformat(), news["title"])
            self.storage.insert_source_log(
                source_name=news["source"],
                source_url=news["url"],
                item_type="news",
                summary=news.get("summary", ""),
                dedupe_hash=dedupe_hash,
                published_at_utc=news["published_at"].astimezone(timezone.utc).isoformat(timespec="seconds"),
            )

        report_data = self._build_report_data(payload, correlation_rows, cot_rows, stale_snapshots, missing)
        report_text = generate_report(report_data)
        self.storage.insert_report(
            report_time_utc=now.isoformat(timespec="seconds"),
            freshness_window_hours=self.settings.freshness_hours,
            body=report_text,
            missing_data=missing,
            stale_data=[f"{item['instrument']}:{item['timeframe']}" for item in stale_snapshots],
        )
        return report_text

    def _build_report_data(
        self,
        payload: dict,
        correlation_rows: Sequence[dict],
        cot_rows: Sequence[dict],
        stale_snapshots: Sequence[dict],
        missing_fields_list: Sequence[str],
    ) -> dict:
        rows = []
        for snap in payload.get("market_snapshots", []):
            rows.append(
                {
                    "instrument": snap["instrument"],
                    "direction": snap.get("trend", "mixed"),
                    "change_15m": snap.get("change_15m", 0),
                    "change_1h": snap.get("change_1h", 0),
                    "change_4h": snap.get("change_4h", 0),
                    "driver": snap.get("key_driver", "n/a"),
                    "volatility": snap.get("atr", "n/a"),
                    "quality": "stale" if snap in stale_snapshots else "fresh",
                }
            )

        missing_or_stale = [f"missing payload: {name}" for name in missing_fields_list]
        missing_or_stale.extend([f"stale data: {item['instrument']} {item['timeframe']}" for item in stale_snapshots])

        return {
            "market_overview": payload.get("market_overview", "Mixed market conditions."),
            "instrument_rows": rows,
            "dxy_impact": payload.get("dxy_impact", "DXY impact requires confirmation."),
            "us10y_impact": payload.get("us10y_impact", "US10Y impact requires confirmation."),
            "correlations": correlation_rows,
            "cot": cot_rows,
            "macro": payload.get("macro_events", []),
            "news": payload.get("news_items", []),
            "bullish": payload.get("bullish", "Data supports a bullish scenario, but scenario requires confirmation."),
            "bearish": payload.get("bearish", "Data supports a bearish scenario, but scenario requires confirmation."),
            "risks": payload.get("risks", "Correlation instability and event risk."),
            "missing_or_stale": missing_or_stale,
            "conclusion": payload.get("conclusion", "Data supports scenarios; signal absent without additional confirmation."),
            "factual_data": payload.get("factual_data", "Market prices, event timestamps, and source links."),
            "calculated_metrics": payload.get("calculated_metrics", "15m/1h/4h changes, ATR proxy, rolling correlations 20/60/120."),
            "correlation_notes": payload.get("correlation_notes", "Correlations are dynamic and may weaken."),
            "interpretation": payload.get("interpretation", "Interpretation is neutral and non-promissory."),
            "scenario_notes": payload.get("scenario_notes", "Scenarios are informational, not trading advice."),
        }
