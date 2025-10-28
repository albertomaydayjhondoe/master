"""
Meta Ads Integration for TikTok Viral ML System

This module provides comprehensive Meta Ads automation with ML-driven optimization.
🔥 NEW: Musical Intelligence System with contextual genre analysis!

Compatible with dummy mode for development without actual Meta Ads API access.
"""

import logging
from typing import Dict, Any, Optional

# Import configuration and utilities
try:
    from ...config.app_settings import is_dummy_mode
except ImportError:
    # Fallback para cuando no se puede importar
    def is_dummy_mode():
        import os
        return os.getenv('DUMMY_MODE', 'true').lower() == 'true'

logger = logging.getLogger(__name__)

# Core Meta Ads components
try:
    from .meta_automator import (
        MetaAdsAutomator,
        MetaAccountManager, 
        MetaCampaignManager,
        MetaAdSetManager,
        MetaCreativeManager,
        MetaInsight
    )
    
    from .meta_action_generator import (
        MetaActionGenerator,
        MetaActionType,
        MetaActionContext
    )
    
    from .api_endpoints import (
        get_meta_automator,
        get_action_generator
    )
    
    from .monitoring import (
        MetaAdsMonitor,
        MetaAlert,
        MetaMetrics
    )
    
    from .production_config import (
        MetaProductionConfig,
        setup_production_meta_environment,
        validate_meta_production_setup
    )
    
    # 🎵 NEW: Musical Intelligence System
    from .musical_context_system import (
        MusicalGenre,
        PixelProfile,
        CampaignContext,
        MusicalContext,
        musical_context_db,
        create_trap_pixel,
        create_reggaeton_pixel,
        create_corrido_pixel
    )
    
    from .musical_ml_models import (
        MusicalMLEnsemble,
        TrapModel,
        ReggatonModel,
        musical_ml_ensemble
    )
    
    from .musical_intelligence_engine import (
        MusicalIntelligenceEngine,
        CampaignInsights,
        OptimizationDecision,
        musical_intelligence,
        quick_campaign_analysis
    )
    
    from .musical_intelligence_api import (
        musical_api
    )
    
    from .demo_sistema_musical import (
        demo_sistema_musical_completo,
        test_sistema_basico,
        caso_uso_trap_viralizado
    )
    
    META_COMPONENTS_AVAILABLE = True
    MUSICAL_INTELLIGENCE_AVAILABLE = True
    logger.info("🎯 Meta Ads components loaded successfully")
    logger.info("🎵 Musical Intelligence System loaded successfully")
    
except ImportError as e:
    logger.warning(f"Meta Ads components not available: {e}")
    
    # Dummy implementations
    class DummyMetaAdsAutomator:
        def __init__(self, *args, **kwargs):
            logger.info("🎭 Using dummy Meta Ads automator")
    
    MetaAdsAutomator = DummyMetaAdsAutomator
    META_COMPONENTS_AVAILABLE = False
    MUSICAL_INTELLIGENCE_AVAILABLE = False

# Export main components
__all__ = [
    # Core Meta Ads
    'MetaAdsAutomator',
    'MetaActionGenerator', 
    'MetaAdsMonitor',
    'MetaProductionConfig',
    'get_meta_automator',
    'get_action_generator',
    
    # Musical Intelligence System 🎵
    'MusicalGenre',
    'PixelProfile',
    'CampaignContext',
    'MusicalIntelligenceEngine',
    'musical_intelligence',
    'musical_context_db',
    'musical_ml_ensemble',
    'musical_api',
    
    # Helper functions
    'create_trap_pixel',
    'create_reggaeton_pixel', 
    'create_corrido_pixel',
    'quick_campaign_analysis',
    'demo_sistema_musical_completo',
    
    # Status flags
    'META_COMPONENTS_AVAILABLE',
    'MUSICAL_INTELLIGENCE_AVAILABLE'
]

def get_meta_system_status() -> Dict[str, Any]:
    """Get status of Meta Ads system including Musical Intelligence"""
    return {
        "components_available": META_COMPONENTS_AVAILABLE,
        "musical_intelligence": MUSICAL_INTELLIGENCE_AVAILABLE,
        "dummy_mode": is_dummy_mode(),
        "modules_loaded": len(__all__),
        "ready_for_production": META_COMPONENTS_AVAILABLE and not is_dummy_mode(),
        "supported_genres": [genre.value for genre in MusicalGenre] if MUSICAL_INTELLIGENCE_AVAILABLE else [],
        "capabilities": [
            "Meta Ads automation",
            "Musical context analysis", 
            "Genre-specific ML models",
            "Automatic optimization",
            "Viral potential detection",
            "Contextual targeting"
        ] if MUSICAL_INTELLIGENCE_AVAILABLE else ["Basic Meta Ads automation"]
    }

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