"""Example health checks that tie scrapers and alert manager together.

This module shows how monitoring might detect problems and raise alerts.
"""
from typing import Dict, Any
from monitoring.metrics.scraper import scrape_all
from monitoring.alerts.alert_manager import AlertManager


def run_health_checks(alert_manager: AlertManager) -> Dict[str, Any]:
    metrics = scrape_all()
    # Simple rules for demo purposes
    ml = metrics["ml"]
    if ml.get("anomaly_rate", 0) > 0.15:
        alert_manager.raise_alert("ml_core", "high", "High anomaly rate", ml)

    df = metrics["device_farm"]
    if df.get("failed_actions_rate", 0) > 0.03:
        alert_manager.raise_alert("device_farm", "medium", "Failed actions rate high", df)

    wf = metrics["workflows"]
    if wf.get("last_run_failures", 0) > 2:
        alert_manager.raise_alert("orchestration", "medium", "Recent workflow failures", wf)

    return metrics
