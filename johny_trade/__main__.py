from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from .agent import JohnyTradeAgent
from .config import Settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Johny Trade agent cycle")
    parser.add_argument("--payload", help="Path to JSON payload")
    parser.add_argument("--db-path", default=None)
    args = parser.parse_args()

    settings = Settings(db_path=args.db_path) if args.db_path else Settings()
    agent = JohnyTradeAgent(settings)

    if not args.payload:
        payload = {
            "market_overview": "No payload provided, generated empty digest.",
            "market_snapshots": [],
            "correlation_inputs": {},
            "cot_positions": [],
            "macro_events": [],
            "news_items": [],
        }
    else:
        with open(args.payload, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        payload = raw
        for snap in payload.get("market_snapshots", []):
            snap["observed_at"] = datetime.fromisoformat(snap["observed_at"])
        for news in payload.get("news_items", []):
            news["published_at"] = datetime.fromisoformat(news["published_at"])

    report = agent.run_cycle(payload)
    print(report)


if __name__ == "__main__":
    main()
