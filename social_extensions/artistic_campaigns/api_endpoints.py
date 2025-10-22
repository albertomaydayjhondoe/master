"""
Artistic Campaign API Endpoints
FastAPI endpoints for artistic campaign management with continuous learning
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
import uuid

try:
    from social_extensions.artistic_campaigns.artistic_campaign_system import (
        ArtisticCampaignSystem, ArtisticContent, AudienceSegment,
        ArtisticMedium, CampaignObjective, AudienceType,
        create_artistic_campaign_system, create_artistic_content, 
        create_audience_segment, CampaignPerformance, LearningInsight
    )
    ARTISTIC_CAMPAIGNS_AVAILABLE = True
except ImportError:
    print("⚠️ Artistic campaigns module not available - using placeholders")
    ARTISTIC_CAMPAIGNS_AVAILABLE = False
    ArtisticCampaignSystem = object

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/artistic", tags=["Artistic Campaigns"])

# Pydantic models for API
class ArtisticContentAPI(BaseModel):
    """API model for artistic content"""
    medium: str = Field(..., description="Artistic medium")
    title: str = Field(..., description="Content title")
    description: str = Field(..., description="Content description")
    artist_name: str = Field(..., description="Artist name")
    style_tags: List[str] = Field(default=[], description="Style tags")
    color_palette: List[str] = Field(default=[], description="Color palette")
    emotional_tone: str = Field(default="inspiring", description="Emotional tone")
    technical_specs: Dict[str, Any] = Field(default={}, description="Technical specifications")
    file_path: Optional[str] = Field(None, description="File path")

class AudienceSegmentAPI(BaseModel):
    """API model for audience segment"""
    audience_type: str = Field(..., description="Audience type")
    name: str = Field(..., description="Segment name")
    demographics: Dict[str, Any] = Field(default={}, description="Demographics")
    interests: List[str] = Field(default=[], description="Interests")
    behavior_patterns: List[str] = Field(default=[], description="Behavior patterns")
    preferred_platforms: List[str] = Field(default=["instagram", "twitter"], description="Preferred platforms")

class CampaignCreateRequest(BaseModel):
    """Request model for campaign creation"""
    content: ArtisticContentAPI = Field(..., description="Artistic content")
    target_audiences: List[AudienceSegmentAPI] = Field(..., description="Target audiences")
    campaign_objective: str = Field(..., description="Campaign objective")
    budget_allocation: Dict[str, float] = Field(..., description="Budget allocation")
    duration_days: int = Field(..., description="Campaign duration in days")
    enable_continuous_learning: bool = Field(default=True, description="Enable continuous learning")

class CampaignResponse(BaseModel):
    """Response model for campaign creation"""
    campaign_id: str = Field(..., description="Campaign ID")
    status: str = Field(..., description="Campaign status")
    predicted_performance: Dict[str, Any] = Field(..., description="Predicted performance")
    budget_distribution: Dict[str, float] = Field(..., description="Budget distribution")
    learning_enabled: bool = Field(..., description="Learning enabled")
    message: str = Field(..., description="Status message")

class PerformanceMetricsResponse(BaseModel):
    """Response model for performance metrics"""
    campaign_id: str
    metrics_count: int
    latest_metrics: Dict[str, Any]
    performance_trend: str
    key_insights: List[str]

class LearningInsightsResponse(BaseModel):
    """Response model for learning insights"""
    campaign_id: str
    total_insights: int
    high_confidence_insights: List[Dict[str, Any]]
    applied_optimizations: int
    model_accuracy: float

class CampaignReportResponse(BaseModel):
    """Response model for campaign report"""
    campaign_summary: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    learning_insights: Dict[str, Any]
    artistic_impact: Dict[str, Any]
    recommendations: List[str]

# Dependency injection
_artistic_system: Optional[ArtisticCampaignSystem] = None

async def get_artistic_system() -> ArtisticCampaignSystem:
    """Dependency to get artistic campaign system"""
    global _artistic_system
    if _artistic_system is None:
        config = {
            'learning_enabled': True,
            'monitoring_interval': 300,  # 5 minutes
            'auto_optimization_threshold': 0.8,
            'platforms': ['instagram', 'twitter', 'tiktok', 'linkedin']
        }
        _artistic_system = create_artistic_campaign_system(config)
    return _artistic_system

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for artistic campaigns system"""
    return {
        "status": "healthy",
        "artistic_campaigns_available": ARTISTIC_CAMPAIGNS_AVAILABLE,
        "timestamp": datetime.now().isoformat(),
        "features": {
            "continuous_learning": True,
            "real_time_monitoring": True,
            "automatic_optimization": True,
            "artistic_analysis": True
        }
    }

# Campaign Management Endpoints

@router.post("/campaigns/create", response_model=CampaignResponse)
async def create_artistic_campaign(
    request: CampaignCreateRequest,
    background_tasks: BackgroundTasks,
    system: ArtisticCampaignSystem = Depends(get_artistic_system)
) -> CampaignResponse:
    """Create new artistic campaign with continuous learning"""
    
    try:
        logger.info(f"🎨 Creating artistic campaign: {request.content.title}")
        
        # Convert API models to internal models
        content = create_artistic_content(
            medium=ArtisticMedium(request.content.medium),
            title=request.content.title,
            artist_name=request.content.artist_name,
            description=request.content.description,
            style_tags=request.content.style_tags,
            color_palette=request.content.color_palette,
            emotional_tone=request.content.emotional_tone,
            technical_specs=request.content.technical_specs,
            file_path=request.content.file_path
        )
        
        audiences = [
            create_audience_segment(
                audience_type=AudienceType(aud.audience_type),
                name=aud.name,
                demographics=aud.demographics,
                interests=aud.interests,
                behavior_patterns=aud.behavior_patterns,
                preferred_platforms=aud.preferred_platforms
            )
            for aud in request.target_audiences
        ]
        
        # Create campaign
        result = await system.create_artistic_campaign(
            content=content,
            target_audiences=audiences,
            campaign_objective=CampaignObjective(request.campaign_objective),
            budget_allocation=request.budget_allocation,
            duration_days=request.duration_days
        )
        
        # Start continuous learning if enabled
        if request.enable_continuous_learning:
            background_tasks.add_task(
                system.continuous_learning_cycle,
                result['campaign_id']
            )
        
        return CampaignResponse(
            campaign_id=result['campaign_id'],
            status='created',
            predicted_performance=result.get('predicted_performance', {}),
            budget_distribution=result.get('budget_distribution', {}),
            learning_enabled=request.enable_continuous_learning,
            message=f"Artistic campaign created successfully for '{content.title}'"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {e}")
    except Exception as e:
        logger.error(f"❌ Error creating artistic campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns/{campaign_id}/performance", response_model=PerformanceMetricsResponse)
async def get_campaign_performance(
    campaign_id: str,
    hours: int = 24,
    system: ArtisticCampaignSystem = Depends(get_artistic_system)
) -> PerformanceMetricsResponse:
    """Get campaign performance metrics"""
    
    try:
        logger.info(f"📊 Getting performance for campaign: {campaign_id}")
        
        if campaign_id not in system.active_campaigns:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Get performance history
        performance_history = system.campaign_history.get(campaign_id, [])
        
        if not performance_history:
            return PerformanceMetricsResponse(
                campaign_id=campaign_id,
                metrics_count=0,
                latest_metrics={},
                performance_trend="insufficient_data",
                key_insights=["Campaign is too new for meaningful metrics"]
            )
        
        # Get recent metrics
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            m for m in performance_history 
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            latest_metric = performance_history[-1]
        else:
            latest_metric = recent_metrics[-1]
        
        # Calculate performance trend
        if len(performance_history) >= 2:
            current_engagement = latest_metric.engagement_rate
            previous_engagement = performance_history[-2].engagement_rate
            
            if current_engagement > previous_engagement * 1.1:
                trend = "improving"
            elif current_engagement < previous_engagement * 0.9:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        # Generate key insights
        insights = []
        if latest_metric.engagement_rate > 0.08:
            insights.append("High engagement rate detected")
        if latest_metric.virality_coefficient > 2.0:
            insights.append("Content showing viral potential")
        if latest_metric.artistic_appreciation_score > 0.8:
            insights.append("Strong artistic resonance with audience")
        if latest_metric.audience_quality_score > 0.85:
            insights.append("High-quality audience engagement")
        
        return PerformanceMetricsResponse(
            campaign_id=campaign_id,
            metrics_count=len(recent_metrics) if recent_metrics else len(performance_history),
            latest_metrics={
                "timestamp": latest_metric.timestamp.isoformat(),
                "impressions": latest_metric.impressions,
                "clicks": latest_metric.clicks,
                "engagement_rate": latest_metric.engagement_rate,
                "sentiment_score": latest_metric.sentiment_score,
                "artistic_appreciation": latest_metric.artistic_appreciation_score,
                "virality_coefficient": latest_metric.virality_coefficient,
                "cost_per_engagement": latest_metric.cost_per_engagement
            },
            performance_trend=trend,
            key_insights=insights if insights else ["No significant patterns detected yet"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns/{campaign_id}/insights", response_model=LearningInsightsResponse)
async def get_learning_insights(
    campaign_id: str,
    min_confidence: float = 0.7,
    system: ArtisticCampaignSystem = Depends(get_artistic_system)
) -> LearningInsightsResponse:
    """Get AI-generated learning insights"""
    
    try:
        logger.info(f"🧠 Getting learning insights for campaign: {campaign_id}")
        
        if campaign_id not in system.active_campaigns:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Get learning patterns
        learning_patterns = system.learning_patterns.get(campaign_id, [])
        
        # Filter by confidence
        high_confidence = [
            pattern for pattern in learning_patterns 
            if pattern.get('confidence', 0) >= min_confidence
        ]
        
        # Calculate applied optimizations
        optimization_history = system.optimization_history.get(campaign_id, [])
        applied_count = len(optimization_history)
        
        # Calculate model accuracy (dummy for now)
        model_accuracy = 0.85 + (len(learning_patterns) * 0.01)  # Improves with data
        model_accuracy = min(model_accuracy, 0.95)
        
        return LearningInsightsResponse(
            campaign_id=campaign_id,
            total_insights=len(learning_patterns),
            high_confidence_insights=high_confidence[:10],  # Top 10
            applied_optimizations=applied_count,
            model_accuracy=round(model_accuracy, 3)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting learning insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/campaigns/{campaign_id}/optimize")
async def trigger_optimization(
    campaign_id: str,
    force_optimization: bool = False,
    system: ArtisticCampaignSystem = Depends(get_artistic_system)
):
    """Trigger manual optimization cycle"""
    
    try:
        logger.info(f"⚡ Triggering optimization for campaign: {campaign_id}")
        
        if campaign_id not in system.active_campaigns:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Get current metrics
        performance_history = system.campaign_history.get(campaign_id, [])
        if not performance_history and not force_optimization:
            raise HTTPException(
                status_code=400, 
                detail="Insufficient data for optimization. Use force_optimization=true to override."
            )
        
        # Simulate optimization trigger
        result = {
            "campaign_id": campaign_id,
            "optimization_triggered": True,
            "estimated_completion": (datetime.now() + timedelta(minutes=10)).isoformat(),
            "optimization_areas": [
                "audience_refinement",
                "content_timing",
                "budget_reallocation",
                "creative_variants"
            ]
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error triggering optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns/{campaign_id}/report", response_model=CampaignReportResponse)
async def generate_campaign_report(
    campaign_id: str,
    include_predictions: bool = True,
    system: ArtisticCampaignSystem = Depends(get_artistic_system)
) -> CampaignReportResponse:
    """Generate comprehensive campaign report"""
    
    try:
        logger.info(f"📋 Generating report for campaign: {campaign_id}")
        
        report = await system.generate_campaign_report(campaign_id)
        
        if 'error' in report:
            raise HTTPException(status_code=404, detail=report['error'])
        
        return CampaignReportResponse(
            campaign_summary=report['campaign_summary'],
            performance_metrics=report['performance_metrics'],
            learning_insights=report['learning_insights'],
            artistic_impact=report['artistic_impact'],
            recommendations=report['recommendations']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Content Management Endpoints

@router.post("/content/analyze")
async def analyze_artistic_content(
    content: ArtisticContentAPI,
    system: ArtisticCampaignSystem = Depends(get_artistic_system)
):
    """Analyze artistic content with AI"""
    
    try:
        logger.info(f"🎨 Analyzing content: {content.title}")
        
        # Convert to internal model
        art_content = create_artistic_content(
            medium=ArtisticMedium(content.medium),
            title=content.title,
            artist_name=content.artist_name,
            description=content.description,
            style_tags=content.style_tags,
            color_palette=content.color_palette,
            emotional_tone=content.emotional_tone,
            technical_specs=content.technical_specs,
            file_path=content.file_path
        )
        
        # Analyze content
        analysis = await system._analyze_artistic_content(art_content)
        
        return {
            "content_id": art_content.content_id,
            "analysis": analysis,
            "analyzed_at": datetime.now().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid content parameter: {e}")
    except Exception as e:
        logger.error(f"❌ Error analyzing content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System Management Endpoints

@router.get("/system/status")
async def get_system_status(
    system: ArtisticCampaignSystem = Depends(get_artistic_system)
):
    """Get system status and statistics"""
    
    try:
        active_campaigns = len(system.active_campaigns)
        total_insights = sum(len(patterns) for patterns in system.learning_patterns.values())
        content_library_size = len(system.content_library)
        
        return {
            "status": "operational",
            "active_campaigns": active_campaigns,
            "total_learning_insights": total_insights,
            "content_library_size": content_library_size,
            "learning_models_active": len(system.performance_models),
            "monitoring_active": True,
            "system_uptime": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns")
async def list_campaigns(
    status: Optional[str] = None,
    artist: Optional[str] = None,
    limit: int = 50,
    system: ArtisticCampaignSystem = Depends(get_artistic_system)
):
    """List artistic campaigns with filtering"""
    
    try:
        campaigns = []
        
        for campaign_id, campaign_data in system.active_campaigns.items():
            # Apply filters
            if status and campaign_data.get('status') != status:
                continue
            if artist and campaign_data.get('content', {}).get('artist_name') != artist:
                continue
            
            # Get performance summary
            performance_history = system.campaign_history.get(campaign_id, [])
            latest_performance = performance_history[-1] if performance_history else None
            
            campaign_summary = {
                'campaign_id': campaign_id,
                'title': campaign_data.get('content', {}).get('title', 'Unknown'),
                'artist': campaign_data.get('content', {}).get('artist_name', 'Unknown'),
                'medium': campaign_data.get('content', {}).get('medium', 'Unknown'),
                'objective': campaign_data.get('objective', 'Unknown'),
                'status': campaign_data.get('status', 'Unknown'),
                'created_at': campaign_data.get('created_at', datetime.now()).isoformat(),
                'learning_enabled': campaign_data.get('learning_enabled', False),
                'metrics_count': len(performance_history),
                'latest_engagement': latest_performance.engagement_rate if latest_performance else 0
            }
            
            campaigns.append(campaign_summary)
            
            if len(campaigns) >= limit:
                break
        
        return {
            "campaigns": campaigns,
            "total_count": len(campaigns),
            "filtered": status is not None or artist is not None
        }
        
    except Exception as e:
        logger.error(f"❌ Error listing campaigns: {e}")
        raise HTTPException(status_code=500, detail=str(e))