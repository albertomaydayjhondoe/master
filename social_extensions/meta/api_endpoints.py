"""
Meta Ads API Endpoints
FastAPI endpoints for Meta Ads campaign management and optimization
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
import uuid

# Import Meta components
try:
    from social_extensions.meta.meta_automator import (
        MetaAdsAutomator, CampaignBrief, TargetingSpec, Creative, 
        CampaignObjective, OptimizationGoal, BidStrategy, CreativeType,
        AdMetrics, MLInsight, create_meta_automator
    )
    from social_extensions.meta.meta_action_generator import (
        MetaActionGenerator, MetaActionType, create_meta_action_generator
    )
except ImportError:
    # Fallback for development
    print("⚠️ Meta modules not available - using placeholders")
    MetaAdsAutomator = object
    MetaActionGenerator = object

# Import from existing ML system
try:
    from ml_core.action_generation.action_generator import ActionRequest, GeneratedAction
    from config.app_settings import get_settings
except ImportError:
    ActionRequest = dict
    GeneratedAction = dict
    get_settings = lambda: {'DUMMY_MODE': True}

# Pydantic models for API
class TargetingSpecAPI(BaseModel):
    countries: List[str]
    age_min: int = Field(default=18, ge=13, le=65)
    age_max: int = Field(default=65, ge=18, le=65)
    genders: Optional[List[int]] = None
    interests: Optional[List[str]] = None
    behaviors: Optional[List[str]] = None
    custom_audiences: Optional[List[str]] = None
    lookalike_audiences: Optional[List[str]] = None
    detailed_targeting: Optional[Dict[str, Any]] = None

class CreativeAPI(BaseModel):
    name: str
    type: str  # single_image, single_video, carousel, collection
    title: str = Field(max_length=125)
    body: str = Field(max_length=500)
    call_to_action: str
    link_url: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

class CampaignBriefAPI(BaseModel):
    campaign_name: str = Field(max_length=100)
    objective: str  # REACH, TRAFFIC, ENGAGEMENT, etc.
    budget_total: float = Field(gt=0)
    start_date: datetime
    end_date: datetime
    targeting: TargetingSpecAPI
    creatives: List[CreativeAPI] = Field(min_items=1, max_items=10)
    optimization_goal: str = "CONVERSIONS"
    bid_strategy: str = "LOWEST_COST_WITHOUT_CAP"
    pixel_id: Optional[str] = None
    conversion_event: str = "Purchase"

class CampaignCreateResponse(BaseModel):
    campaign_id: str
    adset_ids: List[str]
    ad_ids: List[str]
    status: str
    message: str

class MetricsResponse(BaseModel):
    campaign_id: str
    metrics: List[Dict[str, Any]]
    summary: Dict[str, float]
    date_range: str

class OptimizationRequest(BaseModel):
    campaign_id: str
    optimization_type: str = "auto"  # auto, budget, creative, audience
    target_roas: Optional[float] = None
    max_cpa: Optional[float] = None
    force_execute: bool = False

class OptimizationResponse(BaseModel):
    campaign_id: str
    actions_generated: int
    actions_executed: int
    results: List[Dict[str, Any]]
    next_optimization: datetime

class MetaInsightAPI(BaseModel):
    insight_type: str
    score: float
    confidence: float
    recommendation: str
    impact_estimate: Dict[str, float]

class AccountHealthResponse(BaseModel):
    account_id: str
    overall_health: str  # excellent, good, fair, poor
    active_campaigns: int
    total_spend_24h: float
    avg_roas_24h: float
    avg_cpa_24h: float
    issues: List[str]
    recommendations: List[MetaInsightAPI]

# Router setup
router = APIRouter(prefix="/api/v1/meta", tags=["Meta Ads"])
logger = logging.getLogger(__name__)

# Global instances (will be properly initialized)
meta_automator: Optional[MetaAdsAutomator] = None
action_generator: Optional[MetaActionGenerator] = None

def get_meta_automator() -> MetaAdsAutomator:
    """Dependency to get Meta automator instance"""
    global meta_automator
    if meta_automator is None:
        raise HTTPException(status_code=503, detail="Meta automator not initialized")
    return meta_automator

def get_action_generator() -> MetaActionGenerator:
    """Dependency to get Meta action generator instance"""
    global action_generator
    if action_generator is None:
        raise HTTPException(status_code=503, detail="Meta action generator not initialized")
    return action_generator

# Campaign Management Endpoints

@router.post("/campaigns/create", response_model=CampaignCreateResponse)
async def create_campaign(
    brief: CampaignBriefAPI,
    background_tasks: BackgroundTasks,
    automator: MetaAdsAutomator = Depends(get_meta_automator)
) -> CampaignCreateResponse:
    """Create new Meta Ads campaign from brief"""
    
    try:
        logger.info(f"🚀 Creating Meta campaign: {brief.campaign_name}")
        
        # Convert API model to internal model
        campaign_brief = CampaignBrief(
            campaign_name=brief.campaign_name,
            objective=CampaignObjective(brief.objective),
            budget_total=brief.budget_total,
            start_date=brief.start_date,
            end_date=brief.end_date,
            targeting=TargetingSpec(
                countries=brief.targeting.countries,
                age_min=brief.targeting.age_min,
                age_max=brief.targeting.age_max,
                genders=brief.targeting.genders,
                interests=brief.targeting.interests,
                behaviors=brief.targeting.behaviors,
                custom_audiences=brief.targeting.custom_audiences,
                lookalike_audiences=brief.targeting.lookalike_audiences,
                detailed_targeting=brief.targeting.detailed_targeting
            ),
            creatives=[
                Creative(
                    creative_id=str(uuid.uuid4()),
                    name=c.name,
                    type=CreativeType(c.type),
                    title=c.title,
                    body=c.body,
                    call_to_action=c.call_to_action,
                    link_url=c.link_url,
                    image_url=c.image_url,
                    video_url=c.video_url,
                    thumbnail_url=c.thumbnail_url
                ) for c in brief.creatives
            ],
            optimization_goal=OptimizationGoal(brief.optimization_goal),
            bid_strategy=BidStrategy(brief.bid_strategy),
            pixel_id=brief.pixel_id,
            conversion_event=brief.conversion_event
        )
        
        # Create campaign
        result = await automator.create_campaign_from_brief(campaign_brief)
        
        if result.get('status') == 'success':
            # Schedule initial optimization check
            background_tasks.add_task(
                schedule_optimization_check,
                result['campaign_id'],
                delay_hours=2
            )
            
            return CampaignCreateResponse(
                campaign_id=result['campaign_id'],
                adset_ids=result['adset_ids'],
                ad_ids=result['ad_ids'],
                status='success',
                message=f'Campaign created successfully with {len(result["ad_ids"])} ads'
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to create campaign: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        logger.error(f"❌ Error creating campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns/{campaign_id}/metrics", response_model=MetricsResponse)
async def get_campaign_metrics(
    campaign_id: str,
    hours: int = 24,
    automator: MetaAdsAutomator = Depends(get_meta_automator)
) -> MetricsResponse:
    """Get comprehensive campaign metrics"""
    
    try:
        logger.info(f"📊 Getting metrics for campaign: {campaign_id}")
        
        # Get metrics from automator
        metrics = await automator.get_campaign_metrics(campaign_id, hours // 24 or 1)
        
        if not metrics:
            raise HTTPException(
                status_code=404,
                detail=f"No metrics found for campaign {campaign_id}"
            )
        
        # Convert to API format
        metrics_data = [
            {
                'timestamp': m.timestamp.isoformat(),
                'impressions': m.impressions,
                'clicks': m.clicks,
                'spend': m.spend,
                'conversions': m.conversions,
                'conversion_value': m.conversion_value,
                'ctr': m.ctr,
                'cpc': m.cpc,
                'cpm': m.cpm,
                'cpa': m.cpa,
                'roas': m.roas,
                'adset_id': m.adset_id,
                'ad_id': m.ad_id
            }
            for m in metrics
        ]
        
        # Calculate summary
        total_spend = sum(m.spend for m in metrics)
        total_conversions = sum(m.conversions for m in metrics)
        total_conversion_value = sum(m.conversion_value for m in metrics)
        total_impressions = sum(m.impressions for m in metrics)
        total_clicks = sum(m.clicks for m in metrics)
        
        summary = {
            'total_spend': total_spend,
            'total_conversions': total_conversions,
            'total_conversion_value': total_conversion_value,
            'overall_roas': total_conversion_value / total_spend if total_spend > 0 else 0,
            'overall_cpa': total_spend / total_conversions if total_conversions > 0 else 0,
            'overall_ctr': total_clicks / total_impressions * 100 if total_impressions > 0 else 0,
            'avg_cpc': total_spend / total_clicks if total_clicks > 0 else 0
        }
        
        return MetricsResponse(
            campaign_id=campaign_id,
            metrics=metrics_data,
            summary=summary,
            date_range=f"Last {hours} hours"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/campaigns/{campaign_id}/optimize", response_model=OptimizationResponse)
async def optimize_campaign(
    campaign_id: str,
    request: OptimizationRequest,
    background_tasks: BackgroundTasks,
    automator: MetaAdsAutomator = Depends(get_meta_automator),
    action_gen: MetaActionGenerator = Depends(get_action_generator)
) -> OptimizationResponse:
    """Run ML-powered campaign optimization"""
    
    try:
        logger.info(f"🔧 Optimizing campaign: {campaign_id}")
        
        # Get current metrics
        metrics = await automator.get_campaign_metrics(campaign_id, 1)
        if not metrics:
            raise HTTPException(
                status_code=404,
                detail=f"Campaign {campaign_id} not found or has no metrics"
            )
        
        # Build action request
        action_request = ActionRequest(
            request_id=str(uuid.uuid4()),
            platform='meta',
            platform_data={
                'meta': {
                    'account_id': automator.ad_account_id,
                    'metrics': metrics,
                    'budget_remaining': 1000.0,  # Get from campaign
                    'objectives': ['CONVERSIONS'],
                    'target_roas': request.target_roas or 3.0,
                    'max_cpa': request.max_cpa or 50.0,
                    'window_hours': 24
                }
            },
            context={'optimization_type': request.optimization_type},
            timestamp=datetime.now()
        )
        
        # Generate optimization actions
        actions = await action_gen.generate_actions(action_request)
        
        # Execute actions if requested
        executed_results = []
        if request.force_execute and actions:
            # Convert actions to ML insights for automator
            insights = []
            for action in actions:
                if hasattr(action, 'parameters'):
                    insights.append(MLInsight(
                        insight_id=action.action_id,
                        campaign_id=campaign_id,
                        insight_type=action.action_type,
                        score=action.confidence,
                        confidence=action.confidence,
                        recommended_action={
                            'type': action.action_type,
                            **action.parameters
                        },
                        generated_at=datetime.now()
                    ))
            
            # Execute optimizations
            if insights:
                execution_result = await automator.optimize_campaign(campaign_id, insights)
                executed_results = execution_result.get('actions', [])
        
        # Schedule next optimization
        next_optimization = datetime.now() + timedelta(hours=6)
        background_tasks.add_task(
            schedule_optimization_check,
            campaign_id,
            delay_hours=6
        )
        
        return OptimizationResponse(
            campaign_id=campaign_id,
            actions_generated=len(actions),
            actions_executed=len(executed_results),
            results=[
                {
                    'action_id': getattr(action, 'action_id', 'unknown'),
                    'action_type': getattr(action, 'action_type', 'unknown'),
                    'confidence': getattr(action, 'confidence', 0),
                    'executed': request.force_execute,
                    'reasoning': getattr(action, 'reasoning', '')
                }
                for action in actions
            ],
            next_optimization=next_optimization
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error optimizing campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/accounts/{account_id}/health", response_model=AccountHealthResponse)
async def get_account_health(
    account_id: str,
    automator: MetaAdsAutomator = Depends(get_meta_automator)
) -> AccountHealthResponse:
    """Get comprehensive account health assessment"""
    
    try:
        logger.info(f"🏥 Checking health for account: {account_id}")
        
        # Get all active campaigns
        active_campaigns = list(automator.active_campaigns.keys())
        
        # Aggregate 24h metrics
        all_metrics = []
        for campaign_id in active_campaigns:
            metrics = await automator.get_campaign_metrics(campaign_id, 1)
            all_metrics.extend(metrics)
        
        if not all_metrics:
            return AccountHealthResponse(
                account_id=account_id,
                overall_health="unknown",
                active_campaigns=0,
                total_spend_24h=0,
                avg_roas_24h=0,
                avg_cpa_24h=0,
                issues=[],
                recommendations=[]
            )
        
        # Calculate health metrics
        total_spend = sum(m.spend for m in all_metrics)
        total_conversion_value = sum(m.conversion_value for m in all_metrics)
        total_conversions = sum(m.conversions for m in all_metrics)
        
        avg_roas = total_conversion_value / total_spend if total_spend > 0 else 0
        avg_cpa = total_spend / total_conversions if total_conversions > 0 else float('inf')
        
        # Determine health status
        health_score = 0
        issues = []
        
        if avg_roas >= 3.0:
            health_score += 40
        elif avg_roas >= 2.0:
            health_score += 25
        else:
            issues.append("Low ROAS performance")
        
        if avg_cpa <= 30:
            health_score += 30
        elif avg_cpa <= 50:
            health_score += 20
        else:
            issues.append("High cost per acquisition")
        
        if total_spend > 0:
            health_score += 20
        else:
            issues.append("No spending activity")
        
        if len(active_campaigns) > 0:
            health_score += 10
        else:
            issues.append("No active campaigns")
        
        # Health classification
        if health_score >= 80:
            overall_health = "excellent"
        elif health_score >= 60:
            overall_health = "good"
        elif health_score >= 40:
            overall_health = "fair"
        else:
            overall_health = "poor"
        
        # Generate recommendations
        recommendations = []
        if avg_roas < 2.0:
            recommendations.append(MetaInsightAPI(
                insight_type="roas_improvement",
                score=avg_roas,
                confidence=0.8,
                recommendation="Consider optimizing targeting and creative performance",
                impact_estimate={"roas_increase": 0.5, "confidence": 0.7}
            ))
        
        if avg_cpa > 50:
            recommendations.append(MetaInsightAPI(
                insight_type="cpa_reduction",
                score=avg_cpa,
                confidence=0.75,
                recommendation="Implement bid cap strategies to control costs",
                impact_estimate={"cpa_reduction": 15.0, "confidence": 0.6}
            ))
        
        return AccountHealthResponse(
            account_id=account_id,
            overall_health=overall_health,
            active_campaigns=len(active_campaigns),
            total_spend_24h=total_spend,
            avg_roas_24h=avg_roas,
            avg_cpa_24h=avg_cpa if avg_cpa != float('inf') else 0,
            issues=issues,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"❌ Error checking account health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Utility endpoints

@router.post("/webhooks/conversions")
async def handle_conversion_webhook(
    data: Dict[str, Any],
    automator: MetaAdsAutomator = Depends(get_meta_automator)
):
    """Handle Meta Conversions API webhook"""
    
    try:
        logger.info("📥 Received conversion webhook")
        
        # Validate webhook (implement signature verification)
        # This is a placeholder - implement proper verification
        
        # Process conversion event
        if automator.pixel_manager:
            success = await automator.pixel_manager.send_conversion_event(data)
            
            if success:
                return {"status": "success", "message": "Conversion event processed"}
            else:
                raise HTTPException(status_code=400, detail="Failed to process conversion")
        else:
            return {"status": "info", "message": "Pixel manager not configured"}
            
    except Exception as e:
        logger.error(f"❌ Error processing conversion webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config/example")
async def get_example_config():
    """Get example configuration for Meta Ads setup"""
    
    return {
        "meta_config": {
            "app_id": "your_facebook_app_id",
            "app_secret": "your_facebook_app_secret", 
            "access_token": "your_long_lived_access_token",
            "ad_account_id": "1234567890",
            "page_id": "0987654321",
            "pixel_id": "your_pixel_id"
        },
        "action_generator_config": {
            "meta": {
                "min_roas_threshold": 2.0,
                "max_cpa_threshold": 50.0,
                "budget_scale_factor": 1.2,
                "confidence_threshold": 0.6
            }
        }
    }

# Background tasks

async def schedule_optimization_check(campaign_id: str, delay_hours: int):
    """Schedule automatic optimization check"""
    
    try:
        await asyncio.sleep(delay_hours * 3600)  # Convert to seconds
        
        # This would trigger automatic optimization
        # In production, this should be handled by a proper task queue
        logger.info(f"🔄 Automatic optimization check for campaign: {campaign_id}")
        
    except Exception as e:
        logger.error(f"❌ Error in scheduled optimization: {e}")

# Initialization function

def initialize_meta_endpoints(meta_config: Dict[str, Any], 
                            action_config: Dict[str, Any]):
    """Initialize Meta endpoints with configuration"""
    
    global meta_automator, action_generator
    
    try:
        # Initialize Meta automator
        meta_automator = create_meta_automator(meta_config)
        logger.info("✅ Meta automator initialized")
        
        # Initialize action generator
        action_generator = create_meta_action_generator(action_config)
        logger.info("✅ Meta action generator initialized")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Meta endpoints: {e}")
        return False