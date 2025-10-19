from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
import os

api_key_header = APIKeyHeader(name="X-API-Key")

app = FastAPI(
    title="TikTok Viral ML System",
    description="ML-powered system for TikTok automation (Dummy Version)",
    version="0.1.0"
)

# Dummy API key for development
DUMMY_API_KEY = "dummy_development_key"

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dummy security check
async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != DUMMY_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# Import routers
from ml_core.api.endpoints import (
    screenshot_analysis,
    anomaly_detection,
    posting_predictor,
    affinity_calculator
)

# Include routers
app.include_router(screenshot_analysis.router, prefix="/api/v1", tags=["Screenshot Analysis"])
app.include_router(anomaly_detection.router, prefix="/api/v1", tags=["Anomaly Detection"])
app.include_router(posting_predictor.router, prefix="/api/v1", tags=["Posting Time"])
app.include_router(affinity_calculator.router, prefix="/api/v1", tags=["Affinity"])

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