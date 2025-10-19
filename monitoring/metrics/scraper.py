"""Dummy metrics scrapers for ML, device farm and workflows.

These functions simulate scraping metrics so the alerting system can run in
dummy mode. Production implementations should replace these with real
collectors (Prometheus, direct DB queries, etc.).
"""
from typing import Dict, Any, List
import random
import time


def scrape_ml_metrics() -> Dict[str, Any]:
    """Return simulated ML metrics (loss, accuracy, last_retrain timestamps)."""
    return {
        "gpu_util": round(random.uniform(0.0, 1.0), 2),
        "last_retrain_secs": random.randint(0, 7 * 24 * 3600),
        "anomaly_rate": round(random.uniform(0.0, 0.2), 3),
    }


def scrape_device_metrics() -> Dict[str, Any]:
    """Return simulated device farm metrics."""
    return {
        "connected_devices": random.randint(5, 10),
        "avg_response_ms": random.randint(20, 800),
        "failed_actions_rate": round(random.uniform(0.0, 0.05), 3),
    }


def scrape_workflow_metrics() -> Dict[str, Any]:
    """Return simulated orchestration/workflow metrics."""
    return {
        "workflows_running": random.randint(0, 10),
        "last_run_failures": random.randint(0, 5),
        "queued_jobs": random.randint(0, 50),
    }


def scrape_all() -> Dict[str, Any]:
    return {
        "timestamp": time.time(),
        "ml": scrape_ml_metrics(),
        "device_farm": scrape_device_metrics(),
        "workflows": scrape_workflow_metrics(),
    }
