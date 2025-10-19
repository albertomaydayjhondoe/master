from typing import Any
from config.app_settings import is_dummy_mode


if is_dummy_mode():
    # Import dummy implementations
    from .yolo_screenshot import YoloScreenshotDetector as YoloScreenshotDetectorDummy
    from .yolo_video import YoloVideoDetector as YoloVideoDetectorDummy
    from .affinity_model import AffinityModel as AffinityModelDummy
    from .anomaly_detector import AnomalyDetector as AnomalyDetectorDummy


    def get_yolo_screenshot_detector(*args, **kwargs) -> Any:
        return YoloScreenshotDetectorDummy(*args, **kwargs)


    def get_yolo_video_detector(*args, **kwargs) -> Any:
        return YoloVideoDetectorDummy(*args, **kwargs)


    def get_affinity_model(*args, **kwargs) -> Any:
        return AffinityModelDummy(*args, **kwargs)


    def get_anomaly_detector(*args, **kwargs) -> Any:
        return AnomalyDetectorDummy(*args, **kwargs)
else:
    # Production factories should be implemented to import real models
    def get_yolo_screenshot_detector(*args, **kwargs):
        raise RuntimeError("Production YoloScreenshotDetector factory not implemented")


    def get_yolo_video_detector(*args, **kwargs):
        raise RuntimeError("Production YoloVideoDetector factory not implemented")


    def get_affinity_model(*args, **kwargs):
        raise RuntimeError("Production AffinityModel factory not implemented")


    def get_anomaly_detector(*args, **kwargs):
        raise RuntimeError("Production AnomalyDetector factory not implemented")
