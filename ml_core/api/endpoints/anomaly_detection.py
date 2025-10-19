from fastapi import APIRouter
from typing import Dict, Any
import random
import time

from ml_core.api.schemas.requests import AnomalyDetectionRequest
from ml_core.api.schemas.responses import AnomalyDetectionResponse

router = APIRouter()

# Dummy anomaly types
ANOMALY_TYPES = [
    "none",
    "captcha_detected",
    "shadowban_suspected",
    "rate_limit_warning",
    "unusual_pattern"
]

@router.post(
    "/detect_anomaly",
    response_model=AnomalyDetectionResponse,
    description="Detecta anomalías en el comportamiento de una cuenta",
    responses={
        200: {
            "description": "Análisis exitoso de anomalías",
            "content": {
                "application/json": {
                    "example": {
                        "anomaly_detected": True,
                        "anomaly_type": "rate_limit_warning",
                        "confidence": 0.85,
                        "recommendation": "pause",
                        "cooldown_period": 1800
                    }
                }
            }
        },
        400: {"description": "Petición inválida"},
        403: {"description": "API key inválida"}
    }
)
async def detect_anomaly(data: AnomalyDetectionRequest) -> AnomalyDetectionResponse:
    # Simulate processing time
    time.sleep(0.3)
    
    # 80% chance of no anomaly
    if random.random() < 0.8:
        anomaly_type = "none"
        confidence = round(random.uniform(0.90, 0.99), 2)
    else:
        anomaly_type = random.choice(ANOMALY_TYPES[1:])
        confidence = round(random.uniform(0.70, 0.95), 2)
    
    return AnomalyDetectionResponse(
        anomaly_detected=anomaly_type != "none",
        anomaly_type=anomaly_type,
        confidence=confidence,
        recommendation="pause" if anomaly_type != "none" else "continue",
        cooldown_period=random.randint(300, 3600) if anomaly_type != "none" else 0
    )