"""
Main - Machine Learning and Device Automation API

This module is part of the TikTok ML Branch system.
Maintained as part of the universal automation platform.
"""

import os
from typing import Optional, Dict, Any
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

api_key_header = APIKeyHeader(name="X-API-Key")

app = FastAPI(
    title="TikTok Viral ML System",
    description="""
    Sistema de automatización TikTok basado en ML.
    
    Este sistema proporciona endpoints para:
    - Análisis de screenshots mediante YOLO
    - Detección de anomalías y shadowbans
    - Predicción de mejores momentos para publicar
    - Cálculo de afinidad entre cuentas
    
    Ver documentación detallada en docs/api_integration.md
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Screenshot Analysis", "description": "Endpoints para analizar screenshots"},
        {"name": "Anomaly Detection", "description": "Endpoints para detectar anomalías"},
        {"name": "Posting Time", "description": "Endpoints para predecir momentos óptimos"},
        {"name": "Affinity", "description": "Endpoints para calcular afinidad"}
    ]
)

# Dummy API key for development
DUMMY_API_KEY = "dummy_development_key"

# Schema para respuesta de error
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "invalid_request",
                "message": "Missing required field: account_id",
                "details": {
                    "field": "account_id",
                    "code": "missing_field"
                }
            }
        }

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security check
DUMMY_API_KEY = os.getenv("API_KEY", "dummy-key")

async def verify_api_key(api_key: Optional[str] = Depends(api_key_header)):
    if api_key != DUMMY_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# Import routers
try:
    from ml_core.api.endpoints import (
        screenshot_analysis,
        anomaly_detection,
        posting_predictor,
        affinity_calculator
    )
    from ml_core.meta_automation.api import endpoints as meta_endpoints

    # Include routers
    app.include_router(screenshot_analysis.router, prefix="/api/v1", tags=["Screenshot Analysis"])
    app.include_router(anomaly_detection.router, prefix="/api/v1", tags=["Anomaly Detection"])
    app.include_router(posting_predictor.router, prefix="/api/v1", tags=["Posting Time"])
    app.include_router(affinity_calculator.router, prefix="/api/v1", tags=["Affinity"])
    app.include_router(meta_endpoints.router, tags=["Meta Marketing Automation"])
except ImportError:
    # Endpoints not implemented yet - running in basic mode
    pass

@app.get("/")
async def root():
    return {
        "status": "ok",
        "version": "0.1.0",
        "mode": "dummy"
    }


@app.get("/health")
async def health():
    """Simple health endpoint used by docker healthchecks and orchestration."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    # Auto-load .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )