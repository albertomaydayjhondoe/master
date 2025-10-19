"""Request models for API endpoints using Pydantic.

This module defines the expected request payloads for each endpoint.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class AnomalyDetectionRequest(BaseModel):
    account_id: str = Field(..., description="ID de la cuenta a analizar")
    recent_actions: Optional[List[str]] = Field(
        default=[],
        description="Lista de acciones recientes realizadas por la cuenta"
    )
    context: Optional[Dict[str, Any]] = Field(
        default={},
        description="Contexto adicional para la detección de anomalías"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "account_id": "acc_123",
                "recent_actions": ["like", "follow", "comment"],
                "context": {"device_id": "dev_1", "session_duration": 3600}
            }
        }

class PostingTimeRequest(BaseModel):
    account_id: str = Field(..., description="ID de la cuenta para predicción")
    timezone: Optional[str] = Field(
        default="UTC",
        description="Zona horaria para las predicciones"
    )
    historical_data: Optional[Dict[str, Any]] = Field(
        default={},
        description="Datos históricos de engagement opcionales"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "account_id": "acc_123",
                "timezone": "Europe/Madrid",
                "historical_data": {
                    "avg_views": 5000,
                    "peak_hours": [9, 18, 20]
                }
            }
        }

class AffinityRequest(BaseModel):
    account_ids: List[str] = Field(
        ...,
        description="Lista de IDs de cuenta para calcular afinidad",
        min_items=1
    )
    context: Optional[Dict[str, Any]] = Field(
        default={},
        description="Contexto adicional para el cálculo"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "account_ids": ["acc_1", "acc_2", "acc_3"],
                "context": {
                    "content_type": "dance",
                    "engagement_threshold": 0.5
                }
            }
        }