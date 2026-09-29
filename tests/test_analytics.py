import unittest

from johny_trade.analytics import calculate_cot_signal, rolling_correlation_summary
from johny_trade.models import COTPosition


class TestAnalytics(unittest.TestCase):
    def test_cot_signal(self):
        signal = calculate_cot_signal(
            COTPosition(contract="6E", long_positions=120_000, short_positions=95_000, previous_long=118_000, previous_short=100_000)
        )
        self.assertEqual(signal["net"], 25_000)
        self.assertEqual(signal["previous_net"], 18_000)
        self.assertEqual(signal["net_change"], 7_000)
        self.assertEqual(signal["bias"], "bullish")

    def test_rolling_correlation(self):
        a = [100 + i for i in range(130)]
        b = [200 + i * 2 for i in range(130)]
        rows = rolling_correlation_summary(a, b)
        periods = {row["period"] for row in rows}
        self.assertEqual(periods, {20, 60, 120})
        for row in rows:
            self.assertEqual(row["direction"], "positive")
            self.assertGreater(row["value"], 0.9)


if __name__ == "__main__":
    unittest.main()
