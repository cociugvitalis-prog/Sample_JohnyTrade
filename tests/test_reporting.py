import unittest

from johny_trade.reporting import generate_report


class TestReporting(unittest.TestCase):
    def test_report_sections(self):
        report = generate_report(
            {
                "market_overview": "neutral",
                "instrument_rows": [
                    {
                        "instrument": "EURUSD",
                        "direction": "uptrend",
                        "change_15m": 0.1,
                        "change_1h": 0.2,
                        "change_4h": 0.3,
                        "driver": "DXY pullback",
                        "volatility": "moderate",
                        "quality": "fresh",
                    }
                ],
                "correlations": [
                    {
                        "pair": "DXY:EURUSD",
                        "period": 20,
                        "value": -0.8,
                        "direction": "negative",
                        "strength": "strong",
                        "delta": 0.1,
                        "warning": "",
                    }
                ],
                "cot": [{"contract": "6E", "net": 1, "net_change": 1, "bias": "bullish"}],
                "news": [{"impact": "high impact", "sentiment": "neutral", "title": "headline", "source": "Reuters"}],
            }
        )
        self.assertIn("1) Report time", report)
        self.assertIn("14) Neutral conclusion", report)
        self.assertIn("FACTUAL DATA", report)
        self.assertIn("SCENARIOS (NOT TRADING RECOMMENDATIONS)", report)


if __name__ == "__main__":
    unittest.main()
