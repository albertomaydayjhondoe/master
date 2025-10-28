from typing import Any
from config.app_settings import get_env
from scripts.import_by_path import import_by_path

__all__ = ['get_adb_controller', 'get_device_manager']


def get_adb_controller(*args, **kwargs) -> Any:
    """Return an ADB controller implementation.

    In production mode, uses real ADB with physical devices.
    In dummy mode, uses simulation for development.
    """
    from config.app_settings import is_dummy_mode
    
    if is_dummy_mode():
        from .adb_controller import ADBController as ADBControllerDummy
        return ADBControllerDummy(*args, **kwargs)
    else:
        # Production mode: real ADB controller
        dotted = get_env("ADB_CONTROLLER_IMPL")
        if dotted:
            Impl = import_by_path(dotted)
            return Impl(*args, **kwargs)
        else:
            # Default production implementation
            from .adb_real import ADBControllerReal
            return ADBControllerReal(*args, **kwargs)


def get_device_manager(*args, **kwargs) -> Any:
    """Get device manager instance (alias for get_adb_controller)."""
    return get_adb_controller(*args, **kwargs)
