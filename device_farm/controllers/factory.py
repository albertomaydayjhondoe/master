from typing import Any
from config.app_settings import is_dummy_mode

if is_dummy_mode():
    from .adb_controller import ADBController as ADBControllerDummy


    def get_adb_controller(*args, **kwargs) -> Any:
        return ADBControllerDummy(*args, **kwargs)
else:
    def get_adb_controller(*args, **kwargs) -> Any:
        raise RuntimeError("Production ADBController factory not implemented")
