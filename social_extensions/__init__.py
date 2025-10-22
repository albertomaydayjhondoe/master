"""
Social Extensions Integration Module
Integrates social media extensions with the main TikTok ML system
"""

import os
import sys
from pathlib import Path

# Add social extensions to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Main imports
from .social_orchestrator import SocialMediaOrchestrator, create_social_orchestrator, SocialPlatform
from .instagram.instagram_automator import get_instagram_automator, InstagramAnalytics
from .twitter.twitter_automator import get_twitter_automator, TwitterAnalytics  
from .linkedin.linkedin_automator import get_linkedin_automator, LinkedInAnalytics
from .whatsapp.whatsapp_automator import get_whatsapp_automator, WhatsAppAnalytics

__version__ = "1.0.0"
__author__ = "Social Extensions Team"
__description__ = "Universal Social Media Automation Extensions for TikTok ML System"

# Factory pattern integration for main system
SOCIAL_EXTENSIONS_REGISTRY = {
    'orchestrator': SocialMediaOrchestrator,
    'instagram': get_instagram_automator,
    'twitter': get_twitter_automator,
    'linkedin': get_linkedin_automator,
    'whatsapp': get_whatsapp_automator
}

def get_social_platform(platform_name: str, **kwargs):
    """
    Factory function to get social platform automator
    Compatible with main system factory pattern
    """
    if platform_name.lower() in SOCIAL_EXTENSIONS_REGISTRY:
        factory_func = SOCIAL_EXTENSIONS_REGISTRY[platform_name.lower()]
        if platform_name.lower() == 'orchestrator':
            return factory_func(kwargs.get('config_file'))
        else:
            return factory_func(**kwargs)
    else:
        raise ValueError(f"Unsupported social platform: {platform_name}")

# Integration endpoints for ml_core/api
async def social_campaign_endpoint(campaign_data: dict):
    """API endpoint for launching social media campaigns"""
    orchestrator = create_social_orchestrator()
    return await orchestrator.launch_cross_platform_campaign(campaign_data)

async def social_analytics_endpoint():
    """API endpoint for social media analytics"""
    orchestrator = create_social_orchestrator()
    return await orchestrator.comprehensive_analytics_dashboard()

async def social_engagement_endpoint(engagement_config: dict):
    """API endpoint for unified engagement sessions"""
    orchestrator = create_social_orchestrator()
    return await orchestrator.unified_engagement_session(
        duration_minutes=engagement_config.get('duration', 60),
        engagement_strategy=engagement_config.get('strategy', {})
    )

# Available platforms
SUPPORTED_PLATFORMS = [
    SocialPlatform.INSTAGRAM,
    SocialPlatform.TWITTER, 
    SocialPlatform.LINKEDIN,
    SocialPlatform.WHATSAPP
]

# Export all main components
__all__ = [
    'SocialMediaOrchestrator',
    'create_social_orchestrator',
    'SocialPlatform',
    'get_instagram_automator',
    'get_twitter_automator', 
    'get_linkedin_automator',
    'get_whatsapp_automator',
    'InstagramAnalytics',
    'TwitterAnalytics',
    'LinkedInAnalytics', 
    'WhatsAppAnalytics',
    'get_social_platform',
    'social_campaign_endpoint',
    'social_analytics_endpoint',
    'social_engagement_endpoint',
    'SUPPORTED_PLATFORMS'
]