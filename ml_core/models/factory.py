"""Factory module for ML models with dummy/production mode support.

This module provides factory functions to create ML model instances,
supporting both dummy implementations for development/testing and
production implementations via environment variable configuration.
"""
from typing import Any
from config.app_settings import is_dummy_mode, get_env

# Lazy import helper
from scripts.import_by_path import import_by_path

__all__ = [
    'get_yolo_screenshot_detector',
    'get_yolo_video_detector', 
    'get_affinity_model',
    'get_anomaly_detector'
]


def _load_impl(env_var: str, default_callable):
    """Load implementation from env var dotted path or return default callable."""
    dotted = get_env(env_var)
    if dotted:
        cls = import_by_path(dotted)
        return cls
    return default_callable


# Default dummy implementations
from .yolo_screenshot import YoloScreenshotDetector as _YoloScreenshotDummy
from .yolo_video import YoloVideoDetector as _YoloVideoDummy
from .affinity_model import AffinityModel as _AffinityDummy
from .anomaly_detector import AnomalyDetector as _AnomalyDummy


def get_yolo_screenshot_detector(*args, **kwargs) -> Any:
    if is_dummy_mode():
        return _YoloScreenshotDummy(*args, **kwargs)
    else:
        # Production mode: use real YOLOv8 implementation
        from .yolo_prod import YoloScreenshotDetector as _YoloScreenshotProd
        return _YoloScreenshotProd(*args, **kwargs)


def get_yolo_video_detector(*args, **kwargs) -> Any:
    if is_dummy_mode():
        return _YoloVideoDummy(*args, **kwargs)
    else:
        # Production mode: use real YOLOv8 video implementation
        from .yolo_prod import YoloScreenshotDetector as _YoloVideoProd
        return _YoloVideoProd(*args, **kwargs)


def get_affinity_model(*args, **kwargs) -> Any:
    if is_dummy_mode():
        return _AffinityDummy(*args, **kwargs)
    else:
        # Production mode: real ML affinity model
        from .affinity_model import AffinityModel as _AffinityProd
        return _AffinityProd(*args, **kwargs)


def get_anomaly_detector(*args, **kwargs) -> Any:
    if is_dummy_mode():
        return _AnomalyDummy(*args, **kwargs)
    else:
        # Production mode: real anomaly detection with ML
        from .anomaly_detector import AnomalyDetector as _AnomalyProd
        return _AnomalyProd(*args, **kwargs)
