from typing import Any
from config.app_settings import get_env
from scripts.import_by_path import import_by_path

__all__ = ['get_adb_controller']


def get_adb_controller(*args, **kwargs) -> Any:
    """Return an ADB controller implementation.

    The environment variable `ADB_CONTROLLER_IMPL` may contain a dotted path to
    a class to import (e.g. `device_farm.controllers.adb_real.ADBController`).
    If not set, use the dummy ADB controller.
    """
    dotted = get_env("ADB_CONTROLLER_IMPL")
    if dotted:
        Impl = import_by_path(dotted)
        return Impl(*args, **kwargs)

    from .adb_controller import ADBController as ADBControllerDummy

    return ADBControllerDummy(*args, **kwargs)
