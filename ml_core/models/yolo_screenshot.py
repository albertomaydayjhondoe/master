from typing import Dict, Any, List
import random

class YoloScreenshotDetector:
    """Dummy wrapper for a YOLO-based screenshot detector.

    Production code should instantiate this class with a path to a trained
    YOLO model and implement `detect` to return real detections.
    """

    def __init__(self, model_path: str = None, device: str = "cpu") -> None:
        self.model_path = model_path
        self.device = device

    def detect(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        # Return simulated detections similar to the API endpoint expectations
        elements = [
            "like_button",
            "follow_button",
            "comment_button",
            "video_player",
            "profile_icon",
        ]
        return [
            {
                "type": random.choice(elements),
                "confidence": round(random.uniform(0.7, 0.99), 2),
                "coordinates": {"x": random.randint(50, 1000), "y": random.randint(50, 2000)},
            }
            for _ in range(random.randint(2, 6))
        ]
