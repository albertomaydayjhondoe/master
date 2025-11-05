#!/usr/bin/env python3
"""
🎵 TRAP ARTIST API - PRODUCTION
===============================
FastAPI principal para el sistema del artista trap
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import trap artist system
from trap_artist_manager import get_trap_artist_manager
from social_extensions.longcat_satellites_secure import get_secure_satellite_manager

# FastAPI app
app = FastAPI(
    title="Neural Forge Trap Artist API",
    description="Sistema de campañas virales para TrapStar ML",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global managers
trap_manager = None
satellite_manager = None

@app.on_event("startup")
async def startup_event():
    """Initialize systems on startup"""
    global trap_manager, satellite_manager
    
    print("🎵 Initializing Neural Forge Trap Artist API...")
    
    try:
        trap_manager = await get_trap_artist_manager()
        satellite_manager = await get_secure_satellite_manager()
        print("✅ Systems initialized successfully")
    except Exception as e:
        print(f"❌ Initialization error: {e}")

# Pydantic models
class CampaignRequest(BaseModel):
    song_title: str
    lyrics_prompt: Optional[str] = ""
    budget_override: Optional[float] = None

class ArtistInfo(BaseModel):
    name: str
    genre: str
    budget: float
    revenue_share: float

# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🎵 Neural Forge Trap Artist API",
        "artist": os.getenv('TRAP_ARTIST_NAME', 'TrapStar ML'),
        "version": "2.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "trap_manager": trap_manager is not None,
            "satellite_manager": satellite_manager is not None
        }
    }

@app.get("/artist/info")
async def get_artist_info() -> ArtistInfo:
    """Get trap artist information"""
    if not trap_manager:
        raise HTTPException(status_code=503, detail="Trap manager not initialized")
    
    dashboard = trap_manager.get_artist_dashboard()
    
    return ArtistInfo(
        name=dashboard['artist_info']['name'],
        genre=dashboard['artist_info']['genre'],
        budget=dashboard['campaign_config']['total_budget'],
        revenue_share=float(dashboard['revenue_sharing']['artist_cut'].replace('%', ''))
    )

@app.get("/satellites/status")
async def get_satellites_status():
    """Get satellites status"""
    if not satellite_manager:
        raise HTTPException(status_code=503, detail="Satellite manager not initialized")
    
    status = satellite_manager.get_status()
    
    return {
        "initialized": status.get("initialized", False),
        "satellites_count": len(satellite_manager.satellites),
        "satellites": [
            {
                "id": sat_id,
                "name": f"Satellite {sat_id}",
                "status": "active"
            }
            for sat_id in satellite_manager.satellites.keys()
        ]
    }

@app.post("/campaign/create")
async def create_campaign(request: CampaignRequest, background_tasks: BackgroundTasks):
    """Create new viral campaign"""
    if not trap_manager:
        raise HTTPException(status_code=503, detail="Trap manager not initialized")
    
    try:
        # Launch campaign in background
        campaign_result = await trap_manager.create_viral_campaign(
            song_title=request.song_title,
            lyrics_prompt=request.lyrics_prompt or ""
        )
        
        return {
            "success": True,
            "message": f"Campaña '{request.song_title}' creada exitosamente",
            "campaign_data": campaign_result,
            "estimated_reach": "500K-1M usuarios"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating campaign: {str(e)}")

@app.get("/campaigns/history")
async def get_campaigns_history():
    """Get campaigns history"""
    try:
        campaigns_dir = Path("logs/trap_campaigns")
        if not campaigns_dir.exists():
            return {"campaigns": [], "total": 0}
        
        campaigns = []
        for file in campaigns_dir.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    campaign_data = json.load(f)
                    campaigns.append({
                        "file": file.name,
                        "song": campaign_data.get("campaign_info", {}).get("song", "Unknown"),
                        "budget": campaign_data.get("campaign_info", {}).get("budget", 0),
                        "launch_time": campaign_data.get("campaign_info", {}).get("launch_time", ""),
                        "success": campaign_data.get("campaign_results", {}).get("content_generated", {}).get("success", False)
                    })
            except Exception as e:
                continue
        
        # Sort by launch time (newest first)
        campaigns.sort(key=lambda x: x["launch_time"], reverse=True)
        
        return {
            "campaigns": campaigns,
            "total": len(campaigns),
            "total_budget": sum(c["budget"] for c in campaigns)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching campaigns: {str(e)}")

@app.get("/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary"""
    try:
        # Get campaign history
        campaigns_response = await get_campaigns_history()
        campaigns = campaigns_response["campaigns"]
        
        # Calculate summary
        total_campaigns = len(campaigns)
        total_budget = sum(c["budget"] for c in campaigns)
        successful_campaigns = len([c for c in campaigns if c["success"]])
        
        # Estimate metrics (mock data for demo)
        estimated_reach = total_campaigns * 750000  # 750K average per campaign
        estimated_revenue = total_budget * 0.15  # 15% ROI estimate
        
        return {
            "total_campaigns": total_campaigns,
            "successful_campaigns": successful_campaigns,
            "total_budget": total_budget,
            "estimated_reach": estimated_reach,
            "estimated_revenue": estimated_revenue,
            "success_rate": (successful_campaigns / total_campaigns * 100) if total_campaigns > 0 else 0,
            "average_budget": total_budget / total_campaigns if total_campaigns > 0 else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")

@app.post("/test/campaign")
async def test_campaign():
    """Test campaign creation"""
    try:
        test_request = CampaignRequest(
            song_title=f"Test Track {datetime.now().strftime('%H%M%S')}",
            lyrics_prompt="Test lyrics for trap beat with AI elements"
        )
        
        result = await create_campaign(test_request, BackgroundTasks())
        return {
            "test_status": "success",
            "result": result
        }
        
    except Exception as e:
        return {
            "test_status": "error",
            "error": str(e)
        }

@app.get("/system/status")
async def get_system_status():
    """Get complete system status"""
    try:
        # Artist info
        artist_info = await get_artist_info()
        
        # Satellites status
        satellites_status = await get_satellites_status()
        
        # Analytics
        analytics = await get_analytics_summary()
        
        return {
            "artist": artist_info,
            "satellites": satellites_status,
            "analytics": analytics,
            "system": {
                "api_version": "2.0.0",
                "uptime": "operational",
                "last_check": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching system status: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)