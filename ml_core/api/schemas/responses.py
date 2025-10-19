"""Response models for API endpoints using Pydantic.

This module defines the expected response payloads for each endpoint.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class ScreenshotAnalysisResponse(BaseModel):
    detected_elements: List[Dict[str, Any]] = Field(
        ..., 
        description="Lista de elementos detectados en la imagen"
    )
    processing_time: float = Field(
        ...,
        description="Tiempo de procesamiento en segundos",
        ge=0
    )
    screen_state: str = Field(
        ...,
        description="Estado general de la pantalla"
    )
    recommendation: str = Field(
        ...,
        description="Recomendación de acción"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "detected_elements": [
                    {
                        "type": "like_button",
                        "confidence": 0.95,
                        "coordinates": {"x": 100, "y": 200}
                    }
                ],
                "processing_time": 0.45,
                "screen_state": "normal",
                "recommendation": "safe_to_interact"
            }
        }

class AnomalyDetectionResponse(BaseModel):
    anomaly_detected: bool = Field(..., description="Si se detectó anomalía")
    anomaly_type: str = Field(..., description="Tipo de anomalía detectada")
    confidence: float = Field(
        ...,
        description="Confianza de la detección",
        ge=0,
        le=1
    )
    recommendation: str = Field(..., description="Acción recomendada")
    cooldown_period: int = Field(
        ...,
        description="Periodo de espera recomendado en segundos",
        ge=0
    )

    class Config:
        json_schema_extra = {
            "example": {
                "anomaly_detected": True,
                "anomaly_type": "rate_limit_warning",
                "confidence": 0.85,
                "recommendation": "pause",
                "cooldown_period": 1800
            }
        }

class TimeSlot(BaseModel):
    hour: int = Field(..., description="Hora del día (0-23)", ge=0, le=23)
    score: float = Field(..., description="Score de engagement", ge=0, le=1)
    estimated_reach: int = Field(..., description="Alcance estimado", ge=0)
    confidence: float = Field(..., description="Confianza de la predicción", ge=0, le=1)

class PostingTimeResponse(BaseModel):
    best_times: List[TimeSlot] = Field(..., description="Mejores horas para publicar")
    recommended_next_post: Dict[str, Any] = Field(
        ...,
        description="Recomendación para siguiente post"
    )
    account_momentum: float = Field(
        ...,
        description="Momentum actual de la cuenta",
        ge=0,
        le=1
    )
    daily_post_limit: int = Field(
        ...,
        description="Límite diario de posts recomendado",
        ge=1
    )

    class Config:
        json_schema_extra = {
            "example": {
                "best_times": [
                    {
                        "hour": 9,
                        "score": 0.85,
                        "estimated_reach": 8000,
                        "confidence": 0.9
                    }
                ],
                "recommended_next_post": {
                    "timestamp": datetime.now().isoformat(),
                    "confidence": 0.85,
                    "estimated_views": 10000
                },
                "account_momentum": 0.75,
                "daily_post_limit": 3
            }
        }

class AffinityResponse(BaseModel):
    affinity_scores: Dict[str, float] = Field(
        ...,
        description="Scores de afinidad por cuenta"
    )
    engagement_recommendations: List[Dict[str, Any]] = Field(
        ...,
        description="Recomendaciones de engagement"
    )
    cluster_info: Dict[str, Any] = Field(
        ...,
        description="Información del cluster"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "affinity_scores": {
                    "acc_1": 0.85,
                    "acc_2": 0.65
                },
                "engagement_recommendations": [
                    {
                        "account_id": "acc_1",
                        "recommended_actions": ["like", "follow"],
                        "engagement_score": 0.85
                    }
                ],
                "cluster_info": {
                    "cluster_id": 3,
                    "cluster_size": 20,
                    "cluster_theme": "dance"
                }
            }
        }