from typing import Any
from config.app_settings import is_dummy_mode, get_env

# Lazy import helper
from scripts.import_by_path import import_by_path


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
    Impl = _load_impl("YOLO_SCREENSHOT_IMPL", _YoloScreenshotDummy)
    return Impl(*args, **kwargs)


def get_yolo_video_detector(*args, **kwargs) -> Any:
    Impl = _load_impl("YOLO_VIDEO_IMPL", _YoloVideoDummy)
    return Impl(*args, **kwargs)


def get_affinity_model(*args, **kwargs) -> Any:
    Impl = _load_impl("AFFINITY_MODEL_IMPL", _AffinityDummy)
    return Impl(*args, **kwargs)


def get_anomaly_detector(*args, **kwargs) -> Any:
    Impl = _load_impl("ANOMALY_IMPL", _AnomalyDummy)
    return Impl(*args, **kwargs)
