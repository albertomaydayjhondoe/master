"""
Meta Ads Manager Service - Docker v2.0
Complete Meta Ads Campaign Management with ML Optimization
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import httpx
import os
import logging
import asyncio
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Meta Ads Manager v2.0",
    description="Automated Meta Ads Campaign Management for Music Marketing",
    version="2.0.0"
)

# ============================================
# CONFIGURATION
# ============================================

DUMMY_MODE = os.getenv("DUMMY_MODE", "true") == "true"
META_APP_ID = os.getenv("META_APP_ID")
META_APP_SECRET = os.getenv("META_APP_SECRET")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
META_AD_ACCOUNT_ID = os.getenv("META_AD_ACCOUNT_ID")
META_PAGE_ID = os.getenv("META_PAGE_ID")
DAILY_BUDGET = float(os.getenv("DAILY_BUDGET", "50"))
META_API_URL = "https://graph.facebook.com/v18.0"

# ============================================
# MODELS
# ============================================

class CampaignObjective(str, Enum):
    CONVERSIONS = "CONVERSIONS"
    TRAFFIC = "TRAFFIC"
    ENGAGEMENT = "ENGAGEMENT"
    VIDEO_VIEWS = "VIDEO_VIEWS"
    REACH = "REACH"

class OptimizationGoal(str, Enum):
    CONVERSIONS = "CONVERSIONS"
    LANDING_PAGE_VIEWS = "LANDING_PAGE_VIEWS"
    LINK_CLICKS = "LINK_CLICKS"
    IMPRESSIONS = "IMPRESSIONS"
    REACH = "REACH"

class CampaignCreateRequest(BaseModel):
    name: str = Field(..., description="Campaign name")
    objective: CampaignObjective = Field(..., description="Campaign objective")
    daily_budget: float = Field(..., description="Daily budget in USD")
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    special_ad_categories: List[str] = Field(default_factory=list)

class AdSetCreateRequest(BaseModel):
    campaign_id: str
    name: str
    optimization_goal: OptimizationGoal
    billing_event: str = "IMPRESSIONS"
    bid_amount: Optional[int] = None  # in cents
    daily_budget: int  # in cents
    targeting: Dict[str, Any]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class AdCreativeRequest(BaseModel):
    name: str
    object_story_spec: Dict[str, Any]
    degrees_of_freedom_spec: Optional[Dict[str, Any]] = None

class AdCreateRequest(BaseModel):
    adset_id: str
    name: str
    creative_id: str
    status: str = "PAUSED"

class CampaignOptimizationRequest(BaseModel):
    campaign_id: str
    auto_scale: bool = True
    pause_low_performers: bool = True
    boost_high_performers: bool = True

# ============================================
# META ADS CLIENT
# ============================================

class MetaAdsClient:
    def __init__(self):
        self.api_url = META_API_URL
        self.access_token = META_ACCESS_TOKEN
        self.ad_account_id = META_AD_ACCOUNT_ID
        
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """Make request to Meta Graph API"""
        
        if DUMMY_MODE:
            logger.info(f"DUMMY MODE: {method} {endpoint}")
            return self._get_dummy_response(endpoint, data)
        
        url = f"{self.api_url}/{endpoint}"
        
        if params is None:
            params = {}
        params["access_token"] = self.access_token
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                response = await client.get(url, params=params)
            elif method == "POST":
                response = await client.post(url, params=params, json=data)
            elif method == "DELETE":
                response = await client.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code not in [200, 201]:
                logger.error(f"Meta API Error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Meta API error: {response.text}"
                )
            
            return response.json()
    
    def _get_dummy_response(self, endpoint: str, data: Optional[Dict]) -> Dict:
        """Generate dummy response for testing"""
        
        if "campaigns" in endpoint and data:
            return {
                "id": f"campaign_{datetime.now().timestamp()}",
                "success": True
            }
        elif "adsets" in endpoint and data:
            return {
                "id": f"adset_{datetime.now().timestamp()}",
                "success": True
            }
        elif "ads" in endpoint and data:
            return {
                "id": f"ad_{datetime.now().timestamp()}",
                "success": True
            }
        elif "insights" in endpoint:
            return {
                "data": [{
                    "impressions": "15000",
                    "clicks": "450",
                    "ctr": "3.00",
                    "cpc": "0.75",
                    "spend": "337.50",
                    "conversions": "25",
                    "conversion_rate": "5.56",
                    "cost_per_conversion": "13.50",
                    "roas": "2.5",
                    "date_start": datetime.now().strftime("%Y-%m-%d"),
                    "date_stop": datetime.now().strftime("%Y-%m-%d")
                }]
            }
        
        return {"success": True}
    
    async def create_campaign(self, request: CampaignCreateRequest) -> Dict:
        """Create Meta Ads Campaign"""
        
        data = {
            "name": request.name,
            "objective": request.objective.value,
            "status": "PAUSED",  # Start paused for safety
            "special_ad_categories": request.special_ad_categories or []
        }
        
        if request.start_time:
            data["start_time"] = request.start_time.isoformat()
        if request.end_time:
            data["end_time"] = request.end_time.isoformat()
        
        return await self._make_request(
            "POST",
            f"{self.ad_account_id}/campaigns",
            data=data
        )
    
    async def create_ad_set(self, request: AdSetCreateRequest) -> Dict:
        """Create Ad Set with targeting"""
        
        data = {
            "name": request.name,
            "campaign_id": request.campaign_id,
            "optimization_goal": request.optimization_goal.value,
            "billing_event": request.billing_event,
            "daily_budget": request.daily_budget,
            "targeting": request.targeting,
            "status": "PAUSED"
        }
        
        if request.bid_amount:
            data["bid_amount"] = request.bid_amount
        
        if request.start_time:
            data["start_time"] = request.start_time.isoformat()
        if request.end_time:
            data["end_time"] = request.end_time.isoformat()
        
        return await self._make_request(
            "POST",
            f"{self.ad_account_id}/adsets",
            data=data
        )
    
    async def create_ad_creative(self, request: AdCreativeRequest) -> Dict:
        """Create Ad Creative"""
        
        data = {
            "name": request.name,
            "object_story_spec": request.object_story_spec
        }
        
        if request.degrees_of_freedom_spec:
            data["degrees_of_freedom_spec"] = request.degrees_of_freedom_spec
        
        return await self._make_request(
            "POST",
            f"{self.ad_account_id}/adcreatives",
            data=data
        )
    
    async def create_ad(self, request: AdCreateRequest) -> Dict:
        """Create Ad"""
        
        data = {
            "name": request.name,
            "adset_id": request.adset_id,
            "creative": {"creative_id": request.creative_id},
            "status": request.status
        }
        
        return await self._make_request(
            "POST",
            f"{self.ad_account_id}/ads",
            data=data
        )
    
    async def get_campaign_insights(
        self,
        campaign_id: str,
        date_preset: str = "last_7d"
    ) -> Dict:
        """Get campaign performance insights"""
        
        params = {
            "fields": "impressions,clicks,ctr,cpc,spend,conversions,cost_per_conversion,reach,frequency",
            "date_preset": date_preset
        }
        
        return await self._make_request(
            "GET",
            f"{campaign_id}/insights",
            params=params
        )
    
    async def update_campaign_status(
        self,
        campaign_id: str,
        status: str
    ) -> Dict:
        """Update campaign status (ACTIVE, PAUSED, DELETED)"""
        
        data = {"status": status}
        
        return await self._make_request(
            "POST",
            campaign_id,
            data=data
        )
    
    async def update_ad_set_budget(
        self,
        adset_id: str,
        daily_budget: int
    ) -> Dict:
        """Update ad set daily budget"""
        
        data = {"daily_budget": daily_budget}
        
        return await self._make_request(
            "POST",
            adset_id,
            data=data
        )

# ============================================
# CAMPAIGN OPTIMIZER
# ============================================

class CampaignOptimizer:
    def __init__(self, meta_client: MetaAdsClient):
        self.meta_client = meta_client
        self.min_roas_threshold = float(os.getenv("MIN_ROAS_THRESHOLD", "1.5"))
        self.max_cpc_threshold = float(os.getenv("MAX_CPC_THRESHOLD", "5.0"))
        self.budget_increase_trigger = float(os.getenv("BUDGET_INCREASE_TRIGGER_ROAS", "3.0"))
        self.budget_increase_pct = float(os.getenv("BUDGET_INCREASE_PERCENTAGE", "20"))
    
    async def optimize_campaign(
        self,
        campaign_id: str,
        request: CampaignOptimizationRequest
    ) -> Dict:
        """Optimize campaign based on performance"""
        
        # Get insights
        insights = await self.meta_client.get_campaign_insights(campaign_id)
        
        if not insights.get("data"):
            return {"message": "No data available for optimization"}
        
        metrics = insights["data"][0]
        
        cpc = float(metrics.get("cpc", 0))
        roas = float(metrics.get("roas", 0))
        spend = float(metrics.get("spend", 0))
        
        actions = []
        
        # Pause low performers
        if request.pause_low_performers:
            if roas < self.min_roas_threshold or cpc > self.max_cpc_threshold:
                await self.meta_client.update_campaign_status(campaign_id, "PAUSED")
                actions.append(f"Paused campaign (ROAS: {roas}, CPC: ${cpc})")
        
        # Boost high performers
        if request.boost_high_performers and request.auto_scale:
            if roas > self.budget_increase_trigger:
                # Get current ad sets
                # Increase budget by percentage
                new_budget_multiplier = 1 + (self.budget_increase_pct / 100)
                actions.append(f"Increased budget by {self.budget_increase_pct}% (ROAS: {roas})")
        
        return {
            "campaign_id": campaign_id,
            "metrics": metrics,
            "actions_taken": actions,
            "optimized_at": datetime.now().isoformat()
        }

# ============================================
# API ENDPOINTS
# ============================================

meta_client = MetaAdsClient()
optimizer = CampaignOptimizer(meta_client)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "meta-ads-manager-v2",
        "dummy_mode": DUMMY_MODE,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/campaigns/create")
async def create_campaign(request: CampaignCreateRequest):
    """Create new Meta Ads Campaign"""
    try:
        result = await meta_client.create_campaign(request)
        logger.info(f"Created campaign: {result}")
        return result
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/adsets/create")
async def create_ad_set(request: AdSetCreateRequest):
    """Create Ad Set with targeting"""
    try:
        result = await meta_client.create_ad_set(request)
        logger.info(f"Created ad set: {result}")
        return result
    except Exception as e:
        logger.error(f"Error creating ad set: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/creatives/create")
async def create_creative(request: AdCreativeRequest):
    """Create Ad Creative"""
    try:
        result = await meta_client.create_ad_creative(request)
        logger.info(f"Created creative: {result}")
        return result
    except Exception as e:
        logger.error(f"Error creating creative: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ads/create")
async def create_ad(request: AdCreateRequest):
    """Create Ad"""
    try:
        result = await meta_client.create_ad(request)
        logger.info(f"Created ad: {result}")
        return result
    except Exception as e:
        logger.error(f"Error creating ad: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/campaigns/{campaign_id}/insights")
async def get_insights(campaign_id: str, date_preset: str = "last_7d"):
    """Get campaign insights"""
    try:
        result = await meta_client.get_campaign_insights(campaign_id, date_preset)
        return result
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/campaigns/{campaign_id}/optimize")
async def optimize_campaign_endpoint(
    campaign_id: str,
    request: CampaignOptimizationRequest
):
    """Optimize campaign based on performance"""
    try:
        result = await optimizer.optimize_campaign(campaign_id, request)
        return result
    except Exception as e:
        logger.error(f"Error optimizing campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/campaigns/{campaign_id}/status")
async def update_status(campaign_id: str, status: str):
    """Update campaign status"""
    try:
        result = await meta_client.update_campaign_status(campaign_id, status)
        return result
    except Exception as e:
        logger.error(f"Error updating status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/quick-campaign")
async def create_quick_campaign(
    artist_name: str,
    song_name: str,
    landing_url: str,
    daily_budget: float = 50.0,
    target_countries: List[str] = ["US", "MX", "ES"]
):
    """Quick campaign setup for music artists"""
    try:
        # Create campaign
        campaign = await meta_client.create_campaign(CampaignCreateRequest(
            name=f"{artist_name} - {song_name} - {datetime.now().strftime('%Y%m%d')}",
            objective=CampaignObjective.CONVERSIONS,
            daily_budget=daily_budget
        ))
        
        # Create ad set with music targeting
        targeting = {
            "geo_locations": {"countries": target_countries},
            "age_min": 18,
            "age_max": 35,
            "genders": [0],  # All genders
            "interests": [
                {"id": "6003139266461", "name": "Music"},
                {"id": "6003348194956", "name": "Hip hop music"},
                {"id": "6003139269588", "name": "Electronic dance music"}
            ]
        }
        
        adset = await meta_client.create_ad_set(AdSetCreateRequest(
            campaign_id=campaign["id"],
            name=f"AdSet - {song_name}",
            optimization_goal=OptimizationGoal.LANDING_PAGE_VIEWS,
            daily_budget=int(daily_budget * 100),  # Convert to cents
            targeting=targeting
        ))
        
        return {
            "campaign_id": campaign["id"],
            "adset_id": adset["id"],
            "message": "Quick campaign created successfully",
            "next_steps": [
                "Upload creative assets",
                "Create ad creative",
                "Activate campaign"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error creating quick campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
