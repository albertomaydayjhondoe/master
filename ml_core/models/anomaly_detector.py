from typing import Dict, Any
import random

class AnomalyDetector:
    """Dummy anomaly detector for screenshots and account behavior.

    Production implementations should return structured anomaly detections with
    confidence scores and suggested remediation steps.
    """

    def __init__(self, model_path: str = None):
        self.model_path = model_path

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        # 85% chance of no anomaly in dummy mode
        if random.random() < 0.85:
            return {"anomaly": False, "type": "none", "confidence": round(random.uniform(0.9, 0.99), 2)}
        else:
            return {"anomaly": True, "type": random.choice(["captcha", "shadowban", "rate_limit"]), "confidence": round(random.uniform(0.6, 0.95), 2)}
