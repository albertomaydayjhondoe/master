"""
Implementaciones dummy para desarrollo sin GPU
"""
from typing import Dict, Any, List, Optional, Union
import random
import time

class DummyYoloDetector:
    def __init__(self, model_path: str = None):
        self.model_path = model_path or "dummy_yolo.pt"
        
    def detect(self, image_data: bytes) -> Dict[str, Any]:
        time.sleep(0.1)  # Simular procesamiento
        return {
            "detections": [
                {
                    "class_name": "person",
                    "confidence": 0.85,
                    "bbox": [100, 100, 200, 300],
                    "social_relevant": True
                }
            ],
            "total_detections": 1,
            "processing_time_ms": 100
        }

class DummyAnomalyDetector:
    def detect_anomaly(self, data: Any) -> Dict[str, Any]:
        return {
            "is_anomaly": False,
            "confidence": 0.1,
            "anomaly_type": None
        }

class DummyScreenshotAnalyzer:
    def analyze(self, screenshot: bytes) -> Dict[str, Any]:
        return {
            "content_type": "video",
            "engagement_score": 0.75,
            "is_shadowbanned": False
        }
