"""Utility to import a class or function via dotted path string.

Example: import_by_path('ml_core.models.yolo_screenshot.YoloScreenshotDetector')
returns the class object.
"""
import importlib
from typing import Any


def import_by_path(dotted: str) -> Any:
    module_name, _, attr = dotted.rpartition(".")
    if not module_name:
        raise ImportError(f"Invalid dotted path: {dotted}")
    mod = importlib.import_module(module_name)
    return getattr(mod, attr)
