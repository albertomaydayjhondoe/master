from fastapi import APIRouter, File, UploadFile
from typing import Dict, Any
import time

from ml_core.models import YoloScreenshotDetector

router = APIRouter()

# Instantiate a dummy detector (production should configure model paths)
_detector = YoloScreenshotDetector()


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