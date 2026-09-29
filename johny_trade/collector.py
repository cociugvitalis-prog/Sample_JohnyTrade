from __future__ import annotations

import json
import logging
import time
from hashlib import sha256
from typing import Any
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class SourceAccessError(RuntimeError):
    pass


class SourceRegistry:
    def __init__(self, allowed_domains: set[str]) -> None:
        self.allowed_domains = allowed_domains

    def assert_allowed(self, url: str) -> None:
        host = urlparse(url).netloc.lower()
        if not any(host.endswith(domain) for domain in self.allowed_domains):
            raise SourceAccessError(f"Source '{host}' is not allowed")


class HTTPClient:
    def __init__(self, timeout_seconds: int, retry_count: int, retry_backoff_seconds: float, logger: logging.Logger | None = None) -> None:
        self.timeout_seconds = timeout_seconds
        self.retry_count = retry_count
        self.retry_backoff_seconds = retry_backoff_seconds
        self.logger = logger or logging.getLogger(__name__)

    def fetch_json(self, url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        headers = headers or {"User-Agent": "JohnyTrade/1.0"}
        last_error: Exception | None = None
        for attempt in range(1, self.retry_count + 1):
            try:
                req = Request(url, headers=headers)
                with urlopen(req, timeout=self.timeout_seconds) as response:
                    return json.loads(response.read().decode("utf-8"))
            except (URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
                self.logger.error("fetch_json attempt %s failed for %s: %s", attempt, url, exc)
                if attempt < self.retry_count:
                    time.sleep(self.retry_backoff_seconds * attempt)
        raise RuntimeError(f"Failed to fetch data from {url}") from last_error


def make_dedupe_hash(*parts: str) -> str:
    normalized = "||".join(parts)
    return sha256(normalized.encode("utf-8")).hexdigest()
