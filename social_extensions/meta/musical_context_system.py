"""
Meta Ads Musical Context System - Base de Datos Inteligente
Sistema que entiende géneros musicales y optimiza campañas por contexto
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
import json

class MusicalGenre(Enum):
    """Géneros musicales soportados"""
    TRAP = "trap"
    REGGAETON = "reggaeton"  
    RAP = "rap"
    CORRIDO = "corrido"
    AFROBEAT = "afrobeat"
    DANCEHALL = "dancehall"
    LATIN_POP = "latin_pop"
    URBAN = "urban"

class EnergyLevel(Enum):
    """Niveles de energía musical"""
    LOW = "low"          # 0-40 BPM equivalent
    MEDIUM = "medium"    # 40-80 BPM equivalent  
    HIGH = "high"        # 80-120 BPM equivalent
    EXTREME = "extreme"  # 120+ BPM equivalent

class AudienceProfile(Enum):
    """Perfiles de audiencia principal"""
    YOUNG_MALE = "young_male"           # 16-25 hombres
    YOUNG_FEMALE = "young_female"       # 16-25 mujeres
    ADULT_MALE = "adult_male"           # 26-40 hombres
    ADULT_FEMALE = "adult_female"       # 26-40 mujeres
    MIXED_YOUTH = "mixed_youth"         # 18-28 mixto
    MATURE = "mature"                   # 30+ mixto

@dataclass
class MusicalContext:
    """Contexto musical de un pixel/campaña"""
    genre: MusicalGenre
    energy_level: EnergyLevel
    theme: str  # "street", "party", "real_talk", "love", etc.
    vibe: str   # "aggressive", "chill", "energetic", "emotional"
    language: str  # "es", "en", "pt", etc.
    regional_style: Optional[str] = None  # "mexican_trap", "colombian_reggaeton"
    bpm_range: Optional[Tuple[int, int]] = None
    target_mood: Optional[str] = None  # "motivational", "party", "sad", etc.

@dataclass  
class PixelProfile:
    """Perfil completo de un pixel musical"""
    pixel_id: str
    name: str
    musical_context: MusicalContext
    primary_audience: AudienceProfile
    
    # Performance histórico
    avg_ctr: float = 0.0
    avg_cpv: float = 0.0
    avg_watch_time: float = 0.0
    total_campaigns: int = 0
    
    # Métricas de contexto
    performance_by_country: Dict[str, Dict[str, float]] = field(default_factory=dict)
    performance_by_age: Dict[str, Dict[str, float]] = field(default_factory=dict) 
    optimal_budget_range: Tuple[float, float] = (100.0, 1000.0)
    
    # Metadatos
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    status: str = "active"

@dataclass
class CampaignContext:
    """Contexto completo de una campaña musical"""
    campaign_id: str
    pixel_profile: PixelProfile
    
    # Configuración de campaña
    budget: float
    target_countries: List[str]
    target_age_range: Tuple[int, int]
    target_gender: Optional[str] = None
    
    # Métricas en tiempo real
    current_ctr: float = 0.0
    current_cpv: float = 0.0
    current_watch_time: float = 0.0
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    
    # Análisis contextual
    performance_label: str = "unknown"  # "high", "medium", "low"
    genre_performance_rank: Optional[float] = None  # Percentile within genre
    context_score: float = 0.0  # Overall contextual performance
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)
    last_optimized: Optional[datetime] = None

# Configuraciones predefinidas por género
GENRE_EXPECTATIONS = {
    MusicalGenre.TRAP: {
        "expected_ctr": 1.8,
        "expected_cpv": 0.031,
        "optimal_watch_time": 12.5,
        "best_audiences": [AudienceProfile.YOUNG_MALE, AudienceProfile.MIXED_YOUTH],
        "optimization_focus": ["retargeting", "watch_time", "engagement"],
        "budget_efficiency": "medium",
        "scale_threshold": 2.0  # CTR threshold to scale
    },
    MusicalGenre.REGGAETON: {
        "expected_ctr": 2.7,
        "expected_cpv": 0.021,
        "optimal_watch_time": 18.9,
        "best_audiences": [AudienceProfile.YOUNG_FEMALE, AudienceProfile.MIXED_YOUTH],
        "optimization_focus": ["top_funnel", "broad_interest", "lookalike"],
        "budget_efficiency": "high", 
        "scale_threshold": 2.5
    },
    MusicalGenre.RAP: {
        "expected_ctr": 1.2,
        "expected_cpv": 0.038,
        "optimal_watch_time": 9.5,
        "best_audiences": [AudienceProfile.ADULT_MALE, AudienceProfile.YOUNG_MALE],
        "optimization_focus": ["precise_targeting", "quality_over_quantity"],
        "budget_efficiency": "low",
        "scale_threshold": 1.8
    },
    MusicalGenre.CORRIDO: {
        "expected_ctr": 2.1,
        "expected_cpv": 0.025,
        "optimal_watch_time": 15.2,
        "best_audiences": [AudienceProfile.ADULT_MALE, AudienceProfile.MATURE],
        "optimization_focus": ["regional_targeting", "cultural_relevance"],
        "budget_efficiency": "medium",
        "scale_threshold": 2.2
    },
    MusicalGenre.AFROBEAT: {
        "expected_ctr": 2.3,
        "expected_cpv": 0.023,
        "optimal_watch_time": 16.8,
        "best_audiences": [AudienceProfile.YOUNG_FEMALE, AudienceProfile.MIXED_YOUTH],
        "optimization_focus": ["dance_trending", "viral_potential"],
        "budget_efficiency": "high",
        "scale_threshold": 2.4
    }
}

# Configuraciones por región
REGIONAL_MODIFIERS = {
    "spain": {
        MusicalGenre.TRAP: {"ctr_modifier": 0.9, "cpv_modifier": 1.1},
        MusicalGenre.REGGAETON: {"ctr_modifier": 1.2, "cpv_modifier": 0.85},
        MusicalGenre.RAP: {"ctr_modifier": 0.8, "cpv_modifier": 1.15}
    },
    "mexico": {
        MusicalGenre.CORRIDO: {"ctr_modifier": 1.5, "cpv_modifier": 0.7},
        MusicalGenre.REGGAETON: {"ctr_modifier": 1.3, "cpv_modifier": 0.8},
        MusicalGenre.TRAP: {"ctr_modifier": 1.1, "cpv_modifier": 0.95}
    },
    "colombia": {
        MusicalGenre.REGGAETON: {"ctr_modifier": 1.4, "cpv_modifier": 0.75},
        MusicalGenre.AFROBEAT: {"ctr_modifier": 1.2, "cpv_modifier": 0.85}
    },
    "argentina": {
        MusicalGenre.TRAP: {"ctr_modifier": 1.2, "cpv_modifier": 0.9},
        MusicalGenre.RAP: {"ctr_modifier": 1.0, "cpv_modifier": 1.0}
    }
}

class MusicalContextDatabase:
    """Base de datos en memoria para contextos musicales"""
    
    def __init__(self):
        self.pixels: Dict[str, PixelProfile] = {}
        self.campaigns: Dict[str, CampaignContext] = {}
        self.genre_stats: Dict[MusicalGenre, Dict[str, Any]] = {}
        
        # Inicializar stats por género
        for genre in MusicalGenre:
            self.genre_stats[genre] = {
                "total_campaigns": 0,
                "avg_performance": 0.0,
                "top_countries": [],
                "optimal_budgets": [],
                "success_patterns": {}
            }
    
    def add_pixel(self, pixel: PixelProfile) -> None:
        """Agregar un nuevo pixel al sistema"""
        self.pixels[pixel.pixel_id] = pixel
        
    def add_campaign(self, campaign: CampaignContext) -> None:
        """Agregar una nueva campaña con contexto"""
        self.campaigns[campaign.campaign_id] = campaign
        
        # Actualizar estadísticas del género
        genre = campaign.pixel_profile.musical_context.genre
        self.genre_stats[genre]["total_campaigns"] += 1
    
    def get_genre_expectations(self, genre: MusicalGenre, country: str = None) -> Dict[str, Any]:
        """Obtener expectativas ajustadas por género y país"""
        base_expectations = GENRE_EXPECTATIONS.get(genre, {})
        
        if country and country.lower() in REGIONAL_MODIFIERS:
            modifiers = REGIONAL_MODIFIERS[country.lower()].get(genre, {})
            
            # Aplicar modificadores regionales
            adjusted = base_expectations.copy()
            if "ctr_modifier" in modifiers:
                adjusted["expected_ctr"] = base_expectations.get("expected_ctr", 1.0) * modifiers["ctr_modifier"]
            if "cpv_modifier" in modifiers:
                adjusted["expected_cpv"] = base_expectations.get("expected_cpv", 0.03) * modifiers["cpv_modifier"]
                
            return adjusted
        
        return base_expectations
    
    def analyze_campaign_context(self, campaign_id: str) -> Dict[str, Any]:
        """Analizar el contexto completo de una campaña"""
        if campaign_id not in self.campaigns:
            return {"error": "Campaign not found"}
        
        campaign = self.campaigns[campaign_id]
        genre = campaign.pixel_profile.musical_context.genre
        
        # Obtener expectativas del género
        expectations = self.get_genre_expectations(
            genre, 
            campaign.target_countries[0] if campaign.target_countries else None
        )
        
        # Calcular performance vs expectativas
        performance_analysis = {
            "genre": genre.value,
            "expected_vs_actual": {
                "ctr": {
                    "expected": expectations.get("expected_ctr", 0),
                    "actual": campaign.current_ctr,
                    "ratio": campaign.current_ctr / expectations.get("expected_ctr", 0.01) if expectations.get("expected_ctr") else 0
                },
                "cpv": {
                    "expected": expectations.get("expected_cpv", 0),
                    "actual": campaign.current_cpv,
                    "ratio": expectations.get("expected_cpv", 0.01) / max(campaign.current_cpv, 0.001) if campaign.current_cpv > 0 else 0
                }
            },
            "optimization_recommendations": self._get_optimization_recommendations(campaign, expectations),
            "scale_decision": self._should_scale_campaign(campaign, expectations)
        }
        
        return performance_analysis
    
    def _get_optimization_recommendations(self, campaign: CampaignContext, expectations: Dict[str, Any]) -> List[str]:
        """Generar recomendaciones de optimización basadas en contexto"""
        recommendations = []
        
        # Análisis de CTR
        ctr_ratio = campaign.current_ctr / expectations.get("expected_ctr", 0.01) if expectations.get("expected_ctr") else 0
        if ctr_ratio < 0.8:
            recommendations.append(f"CTR bajo para {campaign.pixel_profile.musical_context.genre.value} - probar nuevas creatividades")
        elif ctr_ratio > 1.2:
            recommendations.append("CTR excelente - considerar escalar presupuesto")
        
        # Análisis de CPV
        if campaign.current_cpv > 0:
            cpv_ratio = expectations.get("expected_cpv", 0.03) / campaign.current_cpv
            if cpv_ratio < 0.8:
                recommendations.append("CPV alto - optimizar targeting o creatividades")
        
        # Recomendaciones específicas por género
        focus_areas = expectations.get("optimization_focus", [])
        for focus in focus_areas:
            if focus == "retargeting" and campaign.conversions > 50:
                recommendations.append("Crear audiencia de retargeting con conversores")
            elif focus == "broad_interest" and ctr_ratio > 1.0:
                recommendations.append("Expandir a audiencias similares (lookalike)")
        
        return recommendations
    
    def _should_scale_campaign(self, campaign: CampaignContext, expectations: Dict[str, Any]) -> Dict[str, Any]:
        """Decidir si escalar una campaña basado en contexto"""
        scale_threshold = expectations.get("scale_threshold", 2.0)
        
        scale_decision = {
            "should_scale": False,
            "confidence": 0.0,
            "recommended_action": "maintain",
            "budget_multiplier": 1.0
        }
        
        if campaign.current_ctr >= scale_threshold:
            scale_decision.update({
                "should_scale": True,
                "confidence": min(campaign.current_ctr / scale_threshold, 2.0),
                "recommended_action": "scale_up",
                "budget_multiplier": 1.5 if campaign.current_ctr < scale_threshold * 1.5 else 2.0
            })
        elif campaign.current_ctr < scale_threshold * 0.6:
            scale_decision.update({
                "should_scale": False,
                "confidence": 0.8,
                "recommended_action": "pause_or_optimize", 
                "budget_multiplier": 0.7
            })
        
        return scale_decision

# Instancia global de la base de datos
musical_context_db = MusicalContextDatabase()

# Funciones de utilidad para crear contextos rápidamente
def create_trap_pixel(pixel_id: str, name: str, theme: str = "street") -> PixelProfile:
    """Crear un pixel de trap con configuración predeterminada"""
    return PixelProfile(
        pixel_id=pixel_id,
        name=name,
        musical_context=MusicalContext(
            genre=MusicalGenre.TRAP,
            energy_level=EnergyLevel.HIGH,
            theme=theme,
            vibe="aggressive",
            language="es"
        ),
        primary_audience=AudienceProfile.YOUNG_MALE
    )

def create_reggaeton_pixel(pixel_id: str, name: str, theme: str = "party") -> PixelProfile:
    """Crear un pixel de reggaetón con configuración predeterminada"""
    return PixelProfile(
        pixel_id=pixel_id,
        name=name,
        musical_context=MusicalContext(
            genre=MusicalGenre.REGGAETON,
            energy_level=EnergyLevel.HIGH,
            theme=theme,
            vibe="energetic",
            language="es"
        ),
        primary_audience=AudienceProfile.YOUNG_FEMALE
    )

def create_corrido_pixel(pixel_id: str, name: str, theme: str = "story") -> PixelProfile:
    """Crear un pixel de corrido con configuración predeterminada"""
    return PixelProfile(
        pixel_id=pixel_id,
        name=name,
        musical_context=MusicalContext(
            genre=MusicalGenre.CORRIDO,
            energy_level=EnergyLevel.MEDIUM,
            theme=theme,
            vibe="emotional",
            language="es",
            regional_style="mexican_corrido"
        ),
        primary_audience=AudienceProfile.ADULT_MALE
    )