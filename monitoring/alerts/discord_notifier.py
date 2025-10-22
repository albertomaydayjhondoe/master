"""Dummy Discord notifier used in local/testing environment.

Does not make network calls; stores the last dispatched message for tests.
"""
from typing import Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class DiscordNotifier:
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url
        self.last_message = None

    def send(self, alert: Dict[str, Any]) -> None:
        # In dummy mode, we only record the message and log
        self.last_message = alert
        logger.info("Discord alert sent: %s", json.dumps(alert))
