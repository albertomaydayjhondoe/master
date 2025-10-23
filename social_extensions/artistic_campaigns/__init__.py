"""
Artistic Campaigns Module
Sistema completo de campañas artísticas con aprendizaje continuo
"""

try:
    from .artistic_campaign_system import (
        ArtisticCampaignSystem,
        ArtisticContent, 
        AudienceSegment,
        CampaignPerformance,
        LearningInsight,
        ArtisticMedium,
        CampaignObjective,
        AudienceType,
        create_artistic_campaign_system,
        create_artistic_content,
        create_audience_segment
    )
    
    from .monitoring import (
        ArtisticCampaignMonitor,
        ArtisticAlert,
        LearningMetric,
        ArtisticHealthScore,
        create_artistic_monitor
    )
    
    from .api_endpoints import router as artistic_router
    
    ARTISTIC_CAMPAIGNS_AVAILABLE = True
    
except ImportError as e:
    print(f"⚠️ Artistic campaigns dependencies not available: {e}")
    ARTISTIC_CAMPAIGNS_AVAILABLE = False
    
    # Provide placeholder classes for import safety
    class ArtisticCampaignSystem:
        def __init__(self, config=None):
            self.config = config or {}
            print("🎭 DUMMY: Using placeholder ArtisticCampaignSystem")
    
    class ArtisticCampaignMonitor:
        def __init__(self, config=None):
            self.config = config or {}
            print("🎭 DUMMY: Using placeholder ArtisticCampaignMonitor")
    
    class ArtisticContent:
        pass
    class AudienceSegment:
        pass
    class CampaignPerformance:
        pass
    class LearningInsight:
        pass
    class ArtisticAlert:
        pass
    class LearningMetric:
        pass
    class ArtisticHealthScore:
        pass
    
    # Enum placeholders
    class ArtisticMedium:
        VISUAL_ART = "visual_art"
        DIGITAL_ART = "digital_art"
        PHOTOGRAPHY = "photography"
        NFT = "nft"
    
    class CampaignObjective:
        BRAND_AWARENESS = "brand_awareness"
        ENGAGEMENT = "engagement"
        SALES = "sales"
    
    class AudienceType:
        ART_COLLECTORS = "art_collectors"
        DIGITAL_NATIVES = "digital_natives"
    
    # Factory functions
    def create_artistic_campaign_system(config=None):
        return ArtisticCampaignSystem(config)
    
    def create_artistic_monitor(config=None):
        return ArtisticCampaignMonitor(config)
    
    def create_artistic_content(*args, **kwargs):
        return ArtisticContent()
    
    def create_audience_segment(*args, **kwargs):
        return AudienceSegment()
    
    # Router placeholder
    try:
        from fastapi import APIRouter
        artistic_router = APIRouter(prefix="/artistic", tags=["Artistic Campaigns Dummy"])
        
        @artistic_router.get("/health")
        async def dummy_health():
            return {"status": "dummy_mode", "artistic_campaigns": "placeholder"}
            
    except ImportError:
        artistic_router = None

__version__ = "1.0.0"

__all__ = [
    # Main system
    "ArtisticCampaignSystem",
    "create_artistic_campaign_system",
    
    # Data models
    "ArtisticContent",
    "AudienceSegment", 
    "CampaignPerformance",
    "LearningInsight",
    
    # Enums
    "ArtisticMedium",
    "CampaignObjective",
    "AudienceType",
    
    # Helpers
    "create_artistic_content",
    "create_audience_segment",
    
    # Monitoring
    "ArtisticCampaignMonitor",
    "ArtisticAlert",
    "LearningMetric", 
    "ArtisticHealthScore",
    "create_artistic_monitor",
    
    # API
    "artistic_router",
    
    # Availability
    "ARTISTIC_CAMPAIGNS_AVAILABLE"
]