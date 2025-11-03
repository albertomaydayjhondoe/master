"""
MÓDULO 7: SINCRONIZACIÓN SEMÁNTICO VISUAL Y GENERACIÓN DE EDITS VIRALES

Sistema avanzado de generación automática de edits virales que combina:
- Análisis semántico de audio para identificar momentos clave
- Base de datos inteligente de clips visuales clasificados 
- Sincronización perfecta audio-visual usando ML
- Selección viral basada en algoritmos predictivos
- Generación de variantes A/B para testing
- Aprendizaje continuo de performance

Integración completa con arquitectura multi-rama:
- RAMA TIKTOK ML: ML Core + Device Farm + Ultralytics
- RAMA META: Meta Ads + GoLogin + Automation  
- RAMA TELEGRAM: Like4Like system + Multi-account

Author: AI Agent
Created: 2024-11-02
"""

from .audio_analyzer import AudioAnalyzer
from .visual_clip_database import VisualClipDatabase
from .semantic_synchronizer import SemanticSynchronizer
from .viral_fragment_selector import ViralFragmentSelector
from .ab_testing_variants import ABTestingVariants
from .ml_integration import MLIntegration
from .continuous_learning import ContinuousLearning
from .api_gateway_module7 import APIGatewayModule7

__version__ = "1.0.0"
__author__ = "AI Agent - TikTok ML System"

# Verificar dependencias del sistema
try:
    from config.app_settings import is_dummy_mode
    DUMMY_MODE = is_dummy_mode()
except ImportError:
    DUMMY_MODE = True

# Configuración global del módulo
MODULE7_CONFIG = {
    "name": "Video Generation Module",
    "version": __version__,
    "dummy_mode": DUMMY_MODE,
    "integrations": {
        "ml_core": True,
        "meta_ads": True, 
        "telegram": True,
        "device_farm": True,
        "gologin": True
    }
}

__all__ = [
    "AudioAnalyzer",
    "VisualClipDatabase", 
    "SemanticSynchronizer",
    "ViralFragmentSelector",
    "ABTestingVariants",
    "MLIntegration",
    "ContinuousLearning",
    "APIGatewayModule7",
    "MODULE7_CONFIG"
]