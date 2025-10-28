"""
TikTok Integration for Advanced Meta Ads System
Sistema de integración TikTok con capacidades de cross-platform
"""

from .musical_tiktok_system import (
    TikTokMusicalGenre,
    TikTokMusicalContext,
    TikTokCampaignConfig,
    TikTokMusicalMLPredictor,
    TikTokMusicalCampaignOptimizer,
    TikTokViralMetrics
)

from .tiktok_cross_platform_system import (
    TikTokCrossPlatformIntegration,
    TikTokMetaIntegration,
    TikTokYouTubeIntegration,
    CrossPlatformCampaignManager
)

__version__ = "2.0.0"
__author__ = "Advanced Meta Ads Team"
__description__ = "TikTok Integration with Cross-Platform Capabilities for Meta Ads System"

# Configuración por defecto
DEFAULT_TIKTOK_CONFIG = {
    "budget_default": 400,
    "campaign_duration_days": 10,
    "target_cpm_default": 4.5,
    "target_ctr_default": 3.5,
    "viral_threshold": 0.75,
    "cross_platform_enabled": True,
    "meta_integration_enabled": True,
    "youtube_boost_enabled": True
}

# Géneros musicales soportados
SUPPORTED_GENRES = [genre.value for genre in TikTokMusicalGenre]

# Métricas de integración cross-platform
CROSS_PLATFORM_METRICS = [
    "tiktok_to_meta_conversion",
    "meta_to_tiktok_retargeting", 
    "youtube_boost_from_tiktok",
    "viral_cross_pollination",
    "audience_expansion_rate",
    "platform_synergy_score"
]

__all__ = [
    # Core TikTok Musical System
    "TikTokMusicalGenre",
    "TikTokMusicalContext", 
    "TikTokCampaignConfig",
    "TikTokMusicalMLPredictor",
    "TikTokMusicalCampaignOptimizer",
    "TikTokViralMetrics",
    
    # Cross-Platform Integration
    "TikTokCrossPlatformIntegration",
    "TikTokMetaIntegration", 
    "TikTokYouTubeIntegration",
    "CrossPlatformCampaignManager",
    
    # Configuration
    "DEFAULT_TIKTOK_CONFIG",
    "SUPPORTED_GENRES",
    "CROSS_PLATFORM_METRICS"
]