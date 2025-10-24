"""Scaffold production factory templates and provide instructions.

Run this script to generate `ml_core/models/factory_prod_template.py` and
`device_farm/controllers/factory_prod_template.py` which you can adapt when
moving from dummy to production.
"""
from pathlib import Path


ML_TEMPLATE = '''"""Production factory template for models.

Replace the placeholder implementations with your real model loaders.
"""
from typing import Any


def get_yolo_screenshot_detector(*args, **kwargs) -> Any:
    # TODO: import and return your real YoloScreenshotDetector
    raise NotImplementedError()


def get_yolo_video_detector(*args, **kwargs) -> Any:
    raise NotImplementedError()


def get_affinity_model(*args, **kwargs) -> Any:
    raise NotImplementedError()


def get_anomaly_detector(*args, **kwargs) -> Any:
    raise NotImplementedError()

'''

DEVICE_TEMPLATE = '''"""Production factory template for device controllers.

Replace the placeholder with your Appium/ADB production controller.
"""
from typing import Any


def get_adb_controller(*args, **kwargs) -> Any:
    # TODO: import and return your real ADBController
    raise NotImplementedError()

'''


def main():
    Path("ml_core/models/factory_prod_template.py").write_text(ML_TEMPLATE)
    Path("device_farm/controllers/factory_prod_template.py").write_text(DEVICE_TEMPLATE)
    print("Templates created:")
    print(" - ml_core/models/factory_prod_template.py")
    print(" - device_farm/controllers/factory_prod_template.py")
    print("\nNext steps:")
    print("1) Implement the templates with real implementations.")
    print("2) Set environment variables to point to production classes, e.g:")
    print("   export YOLO_SCREENSHOT_IMPL=ml_core.models.my_impl.YoloScreenshotDetector")
    print("   export ADB_CONTROLLER_IMPL=device_farm.controllers.my_adb.ADBController")


if __name__ == '__main__':
    main()
