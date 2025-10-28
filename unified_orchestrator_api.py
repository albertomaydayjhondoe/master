"""
🚀 UNIFIED ORCHESTRATOR API V3
FastAPI service para el sistema unificado V3
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import asyncio
from datetime import datetime

# Import unified system
from unified_system_v3 import UnifiedCommunityManagerSystem

app = FastAPI(
    title="Unified Orchestrator API V3",
    description="API para sistema de auto-viralización de Community Manager",
    version="3.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize system
system = UnifiedCommunityManagerSystem(dummy_mode=False)

# ═════════════════════════════════════════════════════════════
# MODELS
# ═════════════════════════════════════════════════════════════

class LaunchCampaignRequest(BaseModel):
    video_path: str
    artist_name: str
    song_name: str
    genre: str = "Music"
    daily_ad_budget: float = 50.0
    target_countries: Optional[List[str]] = None

class MonitorChannelRequest(BaseModel):
    youtube_channel_id: str
    auto_launch: bool = True
    virality_threshold: float = 0.70
    max_campaigns_per_day: int = 2
    daily_ad_budget_per_video: float = 50.0
    target_countries: Optional[List[str]] = None
    check_interval_hours: int = 6

# ═════════════════════════════════════════════════════════════
# ENDPOINTS
# ═════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    return {
        "service": "Unified Orchestrator API V3",
        "version": "3.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "launch": "/launch",
            "monitor": "/monitor-channel",
            "analytics": "/analytics/{campaign_id}",
            "optimize": "/optimize/{campaign_id}"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "unified_orchestrator": "up",
            "ml_core": "checking...",
            "meta_ads": "checking...",
            "n8n": "checking..."
        }
    }

@app.post("/launch")
async def launch_campaign(
    request: LaunchCampaignRequest,
    background_tasks: BackgroundTasks
):
    """
    Lanza campaña viral para un video individual
    """
    try:
        # Launch campaign (async in background)
        result = await system.launch_viral_video_campaign(
            video_path=request.video_path,
            artist_name=request.artist_name,
            song_name=request.song_name,
            genre=request.genre,
            daily_ad_budget=request.daily_ad_budget,
            target_countries=request.target_countries or ["US", "MX", "ES"]
        )
        
        return {
            "status": "success",
            "campaign_id": result.get("campaign_id"),
            "message": "Campaign launched successfully",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/monitor-channel")
async def monitor_channel(
    request: MonitorChannelRequest,
    background_tasks: BackgroundTasks
):
    """
    Inicia monitoreo 24/7 de canal de YouTube
    """
    try:
        # Start monitor (run once, then schedule)
        result = await system.monitor_and_viralize_channel(
            youtube_channel_id=request.youtube_channel_id,
            auto_launch=request.auto_launch,
            virality_threshold=request.virality_threshold,
            max_campaigns_per_day=request.max_campaigns_per_day,
            daily_ad_budget_per_video=request.daily_ad_budget_per_video,
            target_countries=request.target_countries or ["US", "MX", "ES"],
            check_interval_hours=request.check_interval_hours
        )
        
        # Schedule background task for continuous monitoring
        # background_tasks.add_task(continuous_monitor, request)
        
        return {
            "status": "success",
            "message": "Channel monitor started",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/{campaign_id}")
async def get_analytics(campaign_id: str):
    """
    Obtiene analytics de una campaña
    """
    try:
        analytics = await system.get_campaign_analytics(campaign_id)
        
        return {
            "status": "success",
            "campaign_id": campaign_id,
            "data": analytics
        }
    
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Campaign not found: {campaign_id}")

@app.post("/optimize/{campaign_id}")
async def optimize_campaign(campaign_id: str):
    """
    Optimiza campaña en curso
    """
    try:
        optimizations = await system.optimize_ongoing_campaign()
        
        return {
            "status": "success",
            "campaign_id": campaign_id,
            "optimizations": optimizations
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ═════════════════════════════════════════════════════════════
# RUN
# ═════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
