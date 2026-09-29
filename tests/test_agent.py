import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from johny_trade.agent import JohnyTradeAgent
from johny_trade.config import Settings
from johny_trade.models import COTPosition


class TestAgent(unittest.TestCase):
    def test_run_cycle_handles_stale_and_missing(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            settings = Settings(db_path=tmp.name, freshness_hours=24)
            agent = JohnyTradeAgent(settings)
            now = datetime.now(timezone.utc)
            payload = {
                "market_snapshots": [
                    {
                        "instrument": "EURUSD",
                        "timeframe": "15m",
                        "observed_at": now - timedelta(hours=1),
                        "change_15m": 0.1,
                        "change_1h": 0.1,
                        "change_4h": 0.1,
                        "atr": 0.002,
                        "trend": "uptrend",
                        "key_driver": "DXY",
                        "source": "api",
                    },
                    {
                        "instrument": "GBPUSD",
                        "timeframe": "1h",
                        "observed_at": now - timedelta(hours=30),
                        "change_15m": -0.1,
                        "change_1h": -0.1,
                        "change_4h": -0.1,
                        "atr": 0.003,
                        "trend": "downtrend",
                        "key_driver": "DXY",
                        "source": "api",
                    },
                ],
                "correlation_inputs": {
                    "DXY:EURUSD": {
                        "left": [100 + i for i in range(130)],
                        "right": [200 - i for i in range(130)],
                    }
                },
                "cot_positions": [
                    COTPosition(
                        contract="6E",
                        long_positions=100,
                        short_positions=120,
                        previous_long=90,
                        previous_short=110,
                    )
                ],
                "macro_events": ["Fed speaker in 4h"],
                "news_items": [
                    {
                        "title": "Dollar rises",
                        "summary": "Summary",
                        "url": "https://www.reuters.com/markets/example",
                        "impact": "high impact",
                        "sentiment": "negative",
                        "source": "Reuters",
                        "published_at": now - timedelta(hours=2),
                    }
                ],
            }
            report = agent.run_cycle(payload)
            self.assertIn("stale data: GBPUSD 1h", report)
            self.assertEqual(agent.storage.count_rows("market_snapshots"), 2)
            self.assertGreaterEqual(agent.storage.count_rows("correlations"), 1)
            self.assertEqual(agent.storage.count_rows("source_log"), 1)


if __name__ == "__main__":
    unittest.main()
