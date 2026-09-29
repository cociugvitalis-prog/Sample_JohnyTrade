import unittest
from datetime import datetime, timedelta, timezone

from johny_trade.quality import is_fresh, missing_fields


class TestQuality(unittest.TestCase):
    def test_is_fresh(self):
        now = datetime.now(timezone.utc)
        self.assertTrue(is_fresh(now - timedelta(hours=2), now=now, freshness_hours=24))
        self.assertFalse(is_fresh(now - timedelta(hours=26), now=now, freshness_hours=24))

    def test_missing_fields(self):
        payload = {"market_snapshots": [], "news_items": []}
        required = ["market_snapshots", "correlation_inputs", "news_items"]
        self.assertEqual(missing_fields(payload, required), ["correlation_inputs"])


if __name__ == "__main__":
    unittest.main()
