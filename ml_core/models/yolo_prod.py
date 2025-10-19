"""Production YOLOv8 implementation for TikTok screenshot analysis.

This module provides a concrete implementation using Ultralytics YOLOv8 for
production use. To use this implementation:

1. Install requirements:
   pip install ultralytics torch

2. Set environment variable:
   export YOLO_SCREENSHOT_IMPL=ml_core.models.yolo_prod.YoloScreenshotDetector
   export DUMMY_MODE=false

3. Provide model weights in config/ml/model_config.yaml
"""
from typing import Dict, Any, List
import io
from PIL import Image
import torch
from ultralytics import YOLO


class YoloScreenshotDetector:
    """Production YOLO detector for TikTok UI elements.

    This class loads a trained YOLOv8 model and provides the same interface
    as the dummy detector but with real inference.
    """

    def __init__(self, model_path: str = None, device: str = None) -> None:
        """Initialize YOLO detector.

        Args:
            model_path: Path to YOLOv8 weights (required in production)
            device: Device to run inference on ('cpu', 'cuda', etc)
        """
        if not model_path:
            raise ValueError("model_path is required for production YOLO")

        self.model_path = model_path
        self.device = device or "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load model
        self.model = YOLO(model_path)
        self.model.to(self.device)

        # Element type mapping
        self.type_map = {
            0: "like_button",
            1: "follow_button", 
            2: "comment_button",
            3: "video_player",
            4: "profile_icon",
            5: "share_button",
            6: "text_overlay",
            7: "thumbnail",
            8: "user_avatar"
        }

    def detect(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """Run inference on screenshot.
        
        Args:
            image_bytes: Raw bytes of the screenshot image

        Returns:
            List of detections with type, confidence and coordinates
        """
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Run inference
        results = self.model(image, device=self.device)
        
        # Process detections
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Get coordinates (normalized -> pixel)
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                
                # Get class and confidence
                cls = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                
                detections.append({
                    "type": self.type_map.get(cls, "unknown"),
                    "confidence": round(conf, 3),
                    "coordinates": {
                        "x": int((x1 + x2) / 2),  # Center X
                        "y": int((y1 + y2) / 2),  # Center Y
                        "width": int(x2 - x1),
                        "height": int(y2 - y1),
                        "bbox": [int(x1), int(y1), int(x2), int(y2)]
                    }
                })
        
        return detections

    def train(
        self,
        data_yaml: str,
        epochs: int = 100,
        imgsz: int = 640,
        batch: int = 16
    ) -> None:
        """Fine-tune model on custom data.
        
        Args:
            data_yaml: Path to data.yaml with dataset configuration
            epochs: Number of training epochs
            imgsz: Input image size
            batch: Batch size
        """
        self.model.train(
            data=data_yaml,
            epochs=epochs,
            imgsz=imgsz,
            batch=batch,
            device=self.device
        )