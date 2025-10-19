"""Dummy Discord notifier used in local/testing environment.

Does not make network calls; stores the last dispatched message for tests.
"""
from typing import Dict, Any
import json


class DiscordNotifier:
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url
        self.last_message = None

    def send(self, alert: Dict[str, Any]) -> None:
        # In dummy mode, we only record the message and print
        self.last_message = alert
        print("[DiscordNotifier] Alert:", json.dumps(alert))
