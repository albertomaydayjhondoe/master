from fastapi import APIRouter, File, UploadFile, Depends
from typing import Dict, Any
import random
import time

router = APIRouter()

# Dummy responses for screenshot analysis
DUMMY_ELEMENTS = [
    "like_button",
    "follow_button",
    "comment_button",
    "video_player",
    "profile_icon"
]

@router.post("/analyze_screenshot", response_model=Dict[str, Any])
async def analyze_screenshot(
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    # Simulate processing time
    time.sleep(0.5)
    
    return {
        "detected_elements": [
            {
                "type": random.choice(DUMMY_ELEMENTS),
                "confidence": round(random.uniform(0.85, 0.99), 2),
                "coordinates": {
                    "x": random.randint(100, 900),
                    "y": random.randint(100, 1800)
                }
            } for _ in range(random.randint(3, 6))
        ],
        "processing_time": round(random.uniform(0.1, 0.8), 2),
        "screen_state": "normal",
        "recommendation": "safe_to_interact"
    }