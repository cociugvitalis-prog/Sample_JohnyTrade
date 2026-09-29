import tempfile
import unittest

from johny_trade.storage import Storage


class TestStorage(unittest.TestCase):
    def test_source_log_deduplication(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            storage = Storage(tmp.name)
            storage.insert_source_log(
                source_name="BBC",
                source_url="https://www.bbc.com/example",
                item_type="news",
                summary="summary",
                dedupe_hash="abc",
                published_at_utc="2026-01-01T00:00:00+00:00",
            )
            storage.insert_source_log(
                source_name="BBC",
                source_url="https://www.bbc.com/example",
                item_type="news",
                summary="summary",
                dedupe_hash="abc",
                published_at_utc="2026-01-01T00:00:00+00:00",
            )
            self.assertEqual(storage.count_rows("source_log"), 1)


if __name__ == "__main__":
    unittest.main()
