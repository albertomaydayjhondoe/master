"""Factory module for ML models with dummy/production mode support.

This module provides factory functions to create ML model instances,
supporting both dummy implementations for development/testing and
production implementations via environment variable configuration.
"""
from typing import Any
import os

def is_dummy_mode() -> bool:
    return os.getenv("DUMMY_MODE", "true").lower() == "true"

def get_env(var_name: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(var_name, default)

# Lazy import helper
from scripts.import_by_path import import_by_path

__all__ = [
    'get_yolo_screenshot_detector',
    'get_yolo_video_detector', 
    'get_affinity_model',
    'get_anomaly_detector',
    'get_yolo_coco_detector'
]


def _load_impl(env_var: str, default_callable: Any) -> Any:
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

# COCO pretrained implementation
from .yolo_coco_pretrained import YoloCOCOPretrainedDetector as _YoloCOCOPretrained


def get_yolo_screenshot_detector(*args, **kwargs) -> Any:
    # Si DUMMY_MODE=false y no hay implementación específica, usar COCO pretrained
    if not is_dummy_mode() and not get_env("YOLO_SCREENSHOT_IMPL"):
        return _YoloCOCOPretrained(*args, **kwargs)
    
    Impl = _load_impl("YOLO_SCREENSHOT_IMPL", _YoloScreenshotDummy)
    return Impl(*args, **kwargs)


def get_yolo_coco_detector(*args, **kwargs) -> Any:
    """Factory específica para detector COCO."""
    return _YoloCOCOPretrained(*args, **kwargs)


def get_yolo_video_detector(*args, **kwargs) -> Any:
    Impl = _load_impl("YOLO_VIDEO_IMPL", _YoloVideoDummy)
    return Impl(*args, **kwargs)


def get_affinity_model(*args, **kwargs) -> Any:
    Impl = _load_impl("AFFINITY_MODEL_IMPL", _AffinityDummy)
    return Impl(*args, **kwargs)


def get_anomaly_detector(*args, **kwargs) -> Any:
    Impl = _load_impl("ANOMALY_IMPL", _AnomalyDummy)
    return Impl(*args, **kwargs)
