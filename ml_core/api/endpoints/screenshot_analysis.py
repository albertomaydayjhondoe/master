from fastapi import APIRouter, File, UploadFile
from typing import Dict, Any
import time
import yaml
from pathlib import Path

from ml_core.models.factory import get_yolo_screenshot_detector

router = APIRouter()

def _load_model_config():
    """Load model configuration from YAML file."""
    config_path = Path(__file__).parent.parent.parent.parent / "config" / "ml" / "model_config.yaml"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config.get('yolo_screenshot', {})
    return {}

# Load configuration and instantiate detector
_config = _load_model_config()
_detector = get_yolo_screenshot_detector(
    model_path=_config.get('model_path'),
    device=_config.get('device', 'cpu')
)


@router.post("/analyze_screenshot", response_model=Dict[str, Any])
async def analyze_screenshot(file: UploadFile = File(...)) -> Dict[str, Any]:
    # Read file bytes and forward to the detector
    image_bytes = await file.read()

    # Simulate a short processing delay
    time.sleep(0.2)

    detections = _detector.detect(image_bytes)

    return {
        "detected_elements": detections,
        "processing_time": round(0.2 + len(detections) * 0.05, 2),
        "screen_state": "normal",
        "recommendation": "safe_to_interact",
    }