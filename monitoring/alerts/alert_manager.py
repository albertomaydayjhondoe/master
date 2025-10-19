"""Simple in-memory alert manager for dummy mode.

Keeps a list of recent alerts and supports registering notifier callbacks.
"""
from typing import Dict, Any, List, Callable
import time
import threading


class AlertManager:
    def __init__(self):
        self._alerts: List[Dict[str, Any]] = []
        self._notifiers: List[Callable[[Dict[str, Any]], None]] = []
        self._lock = threading.Lock()

    def register_notifier(self, fn: Callable[[Dict[str, Any]], None]):
        self._notifiers.append(fn)

    def raise_alert(self, component: str, severity: str, message: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        alert = {
            "timestamp": time.time(),
            "component": component,
            "severity": severity,
            "message": message,
            "details": details or {},
        }
        with self._lock:
            self._alerts.append(alert)
        # Dispatch to notifiers asynchronously
        for n in self._notifiers:
            try:
                n(alert)
            except Exception:
                # Notifier errors should not break alerting
                pass
        return alert

    def recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._alerts[-limit:])
