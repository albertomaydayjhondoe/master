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
    
    from .api_endpoints import router as artistic_router
    
    from .monitoring import (
        ArtisticCampaignMonitor,
        ArtisticAlert,
        LearningMetric,
        ArtisticHealthScore,
        create_artistic_monitor
    )
    
    ARTISTIC_CAMPAIGNS_AVAILABLE = True
    
except ImportError as e:
    print(f"⚠️ Artistic campaigns dependencies not available: {e}")
    ARTISTIC_CAMPAIGNS_AVAILABLE = False
    
    # Provide placeholder classes
    class ArtisticCampaignSystem:
        pass
    
    class ArtisticCampaignMonitor:
        pass
    
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