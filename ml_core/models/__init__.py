"""Model integration surface for ML components (Ultralytics wrappers).

This package contains lightweight stubs used in dummy mode. Production
implementations should provide concrete classes that load YOLOv8 models and
perform inference.
"""

from .yolo_screenshot import YoloScreenshotDetector
from .yolo_video import YoloVideoDetector
from .affinity_model import AffinityModel
from .anomaly_detector import AnomalyDetector

__all__ = [
    "YoloScreenshotDetector",
    "YoloVideoDetector",
    "AffinityModel",
    "AnomalyDetector",
]
