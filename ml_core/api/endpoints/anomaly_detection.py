from fastapi import APIRouter
from typing import Dict, Any
import random
import time

router = APIRouter()

# Dummy anomaly types
ANOMALY_TYPES = [
    "none",
    "captcha_detected",
    "shadowban_suspected",
    "rate_limit_warning",
    "unusual_pattern"
]

@router.post("/detect_anomaly", response_model=Dict[str, Any])
async def detect_anomaly(
    data: Dict[str, Any]
) -> Dict[str, Any]:
    # Simulate processing time
    time.sleep(0.3)
    
    # 80% chance of no anomaly
    if random.random() < 0.8:
        anomaly_type = "none"
        confidence = round(random.uniform(0.90, 0.99), 2)
    else:
        anomaly_type = random.choice(ANOMALY_TYPES[1:])
        confidence = round(random.uniform(0.70, 0.95), 2)
    
    return {
        "anomaly_detected": anomaly_type != "none",
        "anomaly_type": anomaly_type,
        "confidence": confidence,
        "recommendation": "pause" if anomaly_type != "none" else "continue",
        "cooldown_period": random.randint(300, 3600) if anomaly_type != "none" else 0
    }