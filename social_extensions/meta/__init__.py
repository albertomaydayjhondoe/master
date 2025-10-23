"""
Meta Ads Integration Module
Complete Facebook/Instagram advertising automation with ML optimization
"""

# Main components
try:
    from .meta_automator import (
        MetaAdsAutomator, CampaignBrief, TargetingSpec, Creative,
        CampaignObjective, OptimizationGoal, BidStrategy, CreativeType,
        AdMetrics, MLInsight, MetaPixelManager, create_meta_automator
    )
    from .meta_action_generator import (
        MetaActionGenerator, MetaActionType, MetaActionContext,
        create_meta_action_generator
    )
    from .api_endpoints import router as meta_router, initialize_meta_endpoints
    from .monitoring import (
        MetaAdsMonitor, MetaAlert, PerformanceMetric, CampaignHealthScore,
        AlertSeverity, MetricType, create_meta_ads_monitor
    )
    from .production_config import (
        MetaProductionConfig, create_meta_production_config,
        initialize_meta_production
    )
    
    META_AVAILABLE = True
    
except ImportError as e:
    # Graceful degradation if dependencies missing
    print(f"⚠️ Meta Ads module not fully available: {e}")
    META_AVAILABLE = False
    
    # Placeholder classes
    class MetaAdsAutomator:
        def __init__(self, *args, **kwargs):
            pass
    
    class MetaActionGenerator:
        def __init__(self, *args, **kwargs):
            pass
    
    class MetaAdsMonitor:
        def __init__(self, *args, **kwargs):
            pass
    
    class MetaProductionConfig:
        def __init__(self, *args, **kwargs):
            pass
    
    def create_meta_automator(config):
        return MetaAdsAutomator()
    
    def create_meta_action_generator(config):
        return MetaActionGenerator()
    
    def create_meta_ads_monitor(config):
        return MetaAdsMonitor()
    
    def create_meta_production_config():
        return MetaProductionConfig()
    
    def initialize_meta_endpoints(*args):
        return False
    
    def initialize_meta_production(*args):
        return {'status': 'error', 'meta_initialized': False}
    
    meta_router = None

__all__ = [
    'MetaAdsAutomator', 'MetaActionGenerator', 'MetaAdsMonitor', 'MetaProductionConfig',
    'CampaignBrief', 'TargetingSpec', 'Creative', 'MetaAlert', 'CampaignHealthScore',
    'create_meta_automator', 'create_meta_action_generator', 'create_meta_ads_monitor',
    'create_meta_production_config', 'initialize_meta_production',
    'meta_router', 'initialize_meta_endpoints',
    'META_AVAILABLE'
]

from .meta_automator import MetaAdsAutomator, create_meta_automator

__all__ = ['MetaAdsAutomator', 'create_meta_automator']