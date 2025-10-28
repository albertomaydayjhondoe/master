"""
Advanced Campaign System - Módulo de Campañas Avanzadas Meta
Sistema completo de optimización, distribución geográfica y etiquetado
"""

from .budget_optimizer import BudgetOptimizer, ClipData, ClipMetrics
from .geo_distribution import GeoDistribution, RegionalData, GeoAllocation
from .campaign_tagging import CampaignTagging, CampaignTags, CollaboratorProfile, MusicalElements, GenrePrimary, AudienceType

__all__ = [
    'BudgetOptimizer',
    'ClipData', 
    'ClipMetrics',
    'GeoDistribution',
    'RegionalData',
    'GeoAllocation', 
    'CampaignTagging',
    'CampaignTags',
    'CollaboratorProfile',
    'MusicalElements',
    'GenrePrimary',
    'AudienceType'
]

__version__ = "1.0.0"