"""Dummy Selenium wrapper that simulates a browser session attached to a GoLogin profile.

In production, this should control a real browser instance (e.g., via CDP or Selenium).
"""
from typing import Dict, Any
import time
import random


class SeleniumWrapper:
    def __init__(self, profile: Dict[str, Any]):
        self.profile = profile
        self.current_url = None
        self.history = []

    def open(self, url: str) -> Dict[str, Any]:
        # Simulate navigation delay
        time.sleep(random.uniform(0.01, 0.05))
        self.current_url = url
        self.history.append(url)
        return {"status": "ok", "url": url, "timestamp": time.time()}

    def screenshot(self) -> bytes:
        # Return a minimal PNG header to simulate a screenshot
        return b"\x89PNG\r\n\x1a\n"

    def close(self) -> None:
        self.current_url = None
