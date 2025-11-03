"""
A/B Testing Variants - Módulo 7
Sistema de generación y testing de múltiples variantes de edits virales.

Integra con:
- Meta Ads para distribución A/B
- Device Farm para testing orgánico
- Analytics para comparación de performance
"""

import asyncio
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import uuid
from enum import Enum
import itertools

# Importar componentes del módulo
from .semantic_synchronizer import SyncMatch, SemanticSynchronizer
from .viral_fragment_selector import ViralPrediction, ViralFragmentSelector
from .visual_clip_database import VisualClip

# Integración con Meta Ads
try:
    from social_extensions.meta.meta_automator import MetaAdsAutomator
    META_ADS_AVAILABLE = True
except ImportError:
    META_ADS_AVAILABLE = False

# Integración con Device Farm
try:
    from device_farm.controllers.device_manager import DeviceManager
    DEVICE_FARM_AVAILABLE = True
except ImportError:
    DEVICE_FARM_AVAILABLE = False

try:
    from config.app_settings import is_dummy_mode
    DUMMY_MODE = is_dummy_mode()
except ImportError:
    DUMMY_MODE = True

logger = logging.getLogger(__name__)

class VariantType(Enum):
    """Tipos de variantes de A/B testing"""
    TIMING_VARIANT = "timing"           # Diferentes puntos de inicio
    VISUAL_VARIANT = "visual"           # Diferentes clips visuales
    DURATION_VARIANT = "duration"       # Diferentes duraciones
    TRANSITION_VARIANT = "transition"   # Diferentes transiciones
    PLATFORM_VARIANT = "platform"      # Optimizado por plataforma
    AUDIENCE_VARIANT = "audience"       # Optimizado por audiencia

@dataclass
class VariantConfiguration:
    """Configuración para generar variantes"""
    variant_type: VariantType
    parameters: Dict[str, Any]          # Parámetros específicos del tipo
    target_platforms: List[str]         # Plataformas objetivo
    target_audience: Dict[str, Any]     # Audiencia objetivo
    expected_performance: Dict[str, float]  # Performance esperada

@dataclass
class EditVariant:
    """Variante individual de edit viral"""
    variant_id: str
    variant_type: VariantType
    
    # Contenido del edit
    sync_matches: List[SyncMatch]       # Matches sincronizados
    total_duration: float               # Duración total
    transition_effects: List[str]       # Efectos de transición
    
    # Configuración
    configuration: VariantConfiguration # Config específica
    viral_prediction: ViralPrediction   # Predicción viral
    
    # A/B Testing setup
    test_group: str                     # Grupo de testing
    allocation_percentage: float        # % de tráfico asignado
    
    # Optimización
    hashtags: List[str]                 # Hashtags específicos
    caption_template: str               # Template de caption
    posting_schedule: Dict[str, str]    # Horario por plataforma
    
    # Metadatos
    created_at: str
    status: str                         # "draft", "testing", "paused", "winning"

@dataclass
class ABTestSetup:
    """Configuración de experimento A/B"""
    test_id: str
    test_name: str
    
    # Configuración del test
    variants: List[EditVariant]         # Variantes a testear
    control_variant_id: str             # Variante de control
    test_duration_hours: int            # Duración del test
    
    # Distribución de tráfico
    traffic_allocation: Dict[str, float] # % por variante
    target_sample_size: int             # Tamaño muestral objetivo
    
    # Métricas objetivo
    primary_metric: str                 # Métrica principal
    secondary_metrics: List[str]        # Métricas secundarias
    success_criteria: Dict[str, float]  # Criterios de éxito
    
    # Configuración de plataformas
    platform_distribution: Dict[str, float]  # % por plataforma
    audience_targeting: Dict[str, Any]  # Targeting de audiencia
    
    # Estado del test
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    status: str = "draft"               # "draft", "running", "completed", "paused"

@dataclass
class VariantPerformance:
    """Performance de una variante específica"""
    variant_id: str
    platform: str
    
    # Métricas de engagement
    impressions: int
    views: int
    likes: int
    shares: int
    comments: int
    saves: int
    
    # Métricas calculadas
    ctr: float                          # Click-through rate
    engagement_rate: float              # Total engagement / Views
    viral_coefficient: float            # Shares / Views
    completion_rate: float              # % que vio completo
    
    # Métricas de audiencia
    unique_viewers: int
    repeat_viewers: int
    demographic_breakdown: Dict[str, Any]
    
    # Métricas temporales
    performance_by_hour: Dict[str, Dict[str, int]]
    peak_engagement_time: str
    
    # Costos (para Meta Ads)
    spend: float
    cpm: float                          # Cost per mille
    cpc: float                          # Cost per click
    
    # Timestamps
    recorded_at: str
    period_start: str
    period_end: str

class ABTestingVariants:
    """
    Sistema de generación y testing A/B de variantes de edits virales.
    
    Genera múltiples variantes, las distribuye en Meta Ads y Device Farm,
    y analiza performance para determinar ganadores.
    """
    
    def __init__(self, meta_automator: MetaAdsAutomator = None,
                 device_manager = None,
                 viral_selector: ViralFragmentSelector = None):
        
        self.meta_automator = meta_automator
        self.device_manager = device_manager
        self.viral_selector = viral_selector or ViralFragmentSelector()
        
        self.logger = logging.getLogger(f"{__name__}.ABTestingVariants")
        
        # Storage para tests activos
        self.active_tests: Dict[str, ABTestSetup] = {}
        self.variant_performance: Dict[str, List[VariantPerformance]] = {}
        
        # Configuraciones por defecto
        self.default_variant_configs = {
            VariantType.TIMING_VARIANT: {
                "start_offsets": [0, 5, 10, 15],  # Segundos de offset
                "duration": 15
            },
            VariantType.VISUAL_VARIANT: {
                "max_alternatives": 3,
                "genre_variance": 0.2
            },
            VariantType.DURATION_VARIANT: {
                "durations": [10, 15, 20, 30]
            },
            VariantType.TRANSITION_VARIANT: {
                "transitions": ["cut", "fade", "beat_sync", "zoom"]
            },
            VariantType.PLATFORM_VARIANT: {
                "tiktok": {"aspect_ratio": "9:16", "max_duration": 60},
                "instagram": {"aspect_ratio": "9:16", "max_duration": 30},
                "youtube_shorts": {"aspect_ratio": "9:16", "max_duration": 60}
            }
        }
        
        self.logger.info("🧪 A/B Testing Variants system initialized")
    
    async def generate_variants(self, base_sync_matches: List[SyncMatch],
                              viral_predictions: List[ViralPrediction],
                              variant_types: List[VariantType] = None,
                              max_variants: int = 8) -> List[EditVariant]:
        """
        Genera múltiples variantes para A/B testing.
        
        Args:
            base_sync_matches: Matches base para variaciones
            viral_predictions: Predicciones virales
            variant_types: Tipos de variantes a generar
            max_variants: Máximo número de variantes
            
        Returns:
            Lista de variantes generadas
        """
        
        variant_types = variant_types or [
            VariantType.TIMING_VARIANT,
            VariantType.VISUAL_VARIANT,
            VariantType.DURATION_VARIANT,
            VariantType.TRANSITION_VARIANT
        ]
        
        self.logger.info(f"🧪 Generating variants for {len(variant_types)} types")
        
        all_variants = []
        
        # Generar variantes por tipo
        for variant_type in variant_types:
            type_variants = await self._generate_variants_by_type(
                base_sync_matches, viral_predictions, variant_type
            )
            all_variants.extend(type_variants)
        
        # Limitar número total de variantes
        if len(all_variants) > max_variants:
            # Ordenar por predicción viral y tomar las mejores
            all_variants.sort(
                key=lambda v: v.viral_prediction.viral_score, 
                reverse=True
            )
            all_variants = all_variants[:max_variants]
        
        # Asignar IDs únicos
        for i, variant in enumerate(all_variants):
            variant.variant_id = f"variant_{uuid.uuid4().hex[:8]}"
            variant.created_at = datetime.now().isoformat()
            variant.status = "draft"
        
        self.logger.info(f"✅ Generated {len(all_variants)} variants")
        
        return all_variants
    
    async def _generate_variants_by_type(self, base_matches: List[SyncMatch],
                                       predictions: List[ViralPrediction],
                                       variant_type: VariantType) -> List[EditVariant]:
        """Genera variantes de un tipo específico"""
        
        variants = []
        config = self.default_variant_configs.get(variant_type, {})
        
        if variant_type == VariantType.TIMING_VARIANT:
            # Variantes con diferentes puntos de inicio
            for offset in config.get("start_offsets", [0, 5, 10]):
                adjusted_matches = self._adjust_timing(base_matches, offset)
                
                variant = EditVariant(
                    variant_id="",  # Will be set later
                    variant_type=variant_type,
                    sync_matches=adjusted_matches,
                    total_duration=sum(m.audio_duration for m in adjusted_matches),
                    transition_effects=["standard"],
                    configuration=VariantConfiguration(
                        variant_type=variant_type,
                        parameters={"start_offset": offset},
                        target_platforms=["tiktok", "instagram"],
                        target_audience={"age_range": "18-34"},
                        expected_performance={"engagement_rate": 0.05 + offset * 0.01}
                    ),
                    viral_prediction=predictions[0] if predictions else None,
                    test_group=f"timing_{offset}s",
                    allocation_percentage=0.25,
                    hashtags=["#timing", "#viral", "#music"],
                    caption_template="Perfect timing ⏰ #{genre} #{trend}",
                    posting_schedule={"tiktok": "19:00", "instagram": "20:00"},
                    created_at="",
                    status="draft"
                )
                variants.append(variant)
        
        elif variant_type == VariantType.VISUAL_VARIANT:
            # Variantes con diferentes clips visuales
            max_alternatives = config.get("max_alternatives", 3)
            
            for i in range(min(max_alternatives, len(base_matches))):
                # Crear variante con clips alternativos
                alt_matches = await self._find_alternative_visuals(base_matches)
                
                variant = EditVariant(
                    variant_id="",
                    variant_type=variant_type,
                    sync_matches=alt_matches,
                    total_duration=sum(m.audio_duration for m in alt_matches),
                    transition_effects=["smooth_fade"],
                    configuration=VariantConfiguration(
                        variant_type=variant_type,
                        parameters={"visual_alternative": i + 1},
                        target_platforms=["tiktok", "instagram", "youtube_shorts"],
                        target_audience={"interests": ["visual_content", "music"]},
                        expected_performance={"engagement_rate": 0.06}
                    ),
                    viral_prediction=predictions[i] if i < len(predictions) else predictions[0],
                    test_group=f"visual_alt_{i+1}",
                    allocation_percentage=0.2,
                    hashtags=["#visual", "#alternative", "#style"],
                    caption_template="Different vibes ✨ #{genre} #{mood}",
                    posting_schedule={"tiktok": "18:00", "instagram": "19:00"},
                    created_at="",
                    status="draft"
                )
                variants.append(variant)
        
        elif variant_type == VariantType.DURATION_VARIANT:
            # Variantes con diferentes duraciones
            for duration in config.get("durations", [15, 20, 30]):
                adjusted_matches = self._adjust_duration(base_matches, duration)
                
                variant = EditVariant(
                    variant_id="",
                    variant_type=variant_type,
                    sync_matches=adjusted_matches,
                    total_duration=duration,
                    transition_effects=["duration_optimized"],
                    configuration=VariantConfiguration(
                        variant_type=variant_type,
                        parameters={"target_duration": duration},
                        target_platforms=["tiktok", "youtube_shorts"],
                        target_audience={"attention_span": "variable"},
                        expected_performance={"completion_rate": max(0.3, 1.0 - duration/60)}
                    ),
                    viral_prediction=predictions[0] if predictions else None,
                    test_group=f"duration_{duration}s",
                    allocation_percentage=0.25,
                    hashtags=[f"#{duration}second", "#quick", "#viral"],
                    caption_template=f"Perfect {duration}s edit 🎬 #{genre}",
                    posting_schedule={"tiktok": "17:00", "youtube_shorts": "18:00"},
                    created_at="",
                    status="draft"
                )
                variants.append(variant)
        
        elif variant_type == VariantType.TRANSITION_VARIANT:
            # Variantes con diferentes transiciones
            for transition in config.get("transitions", ["cut", "fade"]):
                enhanced_matches = self._apply_transitions(base_matches, transition)
                
                variant = EditVariant(
                    variant_id="",
                    variant_type=variant_type,
                    sync_matches=enhanced_matches,
                    total_duration=sum(m.audio_duration for m in enhanced_matches),
                    transition_effects=[transition],
                    configuration=VariantConfiguration(
                        variant_type=variant_type,
                        parameters={"transition_style": transition},
                        target_platforms=["tiktok", "instagram"],
                        target_audience={"style_preference": transition},
                        expected_performance={"visual_appeal": 0.7}
                    ),
                    viral_prediction=predictions[0] if predictions else None,
                    test_group=f"transition_{transition}",
                    allocation_percentage=0.2,
                    hashtags=[f"#{transition}edit", "#transitions", "#smooth"],
                    caption_template=f"Smooth {transition} transitions 🎨 #{genre}",
                    posting_schedule={"tiktok": "20:00", "instagram": "21:00"},
                    created_at="",
                    status="draft"
                )
                variants.append(variant)
        
        return variants
    
    def _adjust_timing(self, matches: List[SyncMatch], offset: float) -> List[SyncMatch]:
        """Ajusta timing de matches con offset"""
        adjusted = []
        for match in matches:
            new_match = match
            new_match.audio_start += offset
            adjusted.append(new_match)
        return adjusted
    
    async def _find_alternative_visuals(self, matches: List[SyncMatch]) -> List[SyncMatch]:
        """Encuentra clips visuales alternativos"""
        # TODO: Implementar búsqueda de alternativas en VisualClipDatabase
        # Por ahora retornamos matches originales con variación simulada
        
        alt_matches = []
        for match in matches:
            # Simular clip alternativo
            alt_clip = match.visual_clip
            alt_clip.viral_score *= np.random.uniform(0.9, 1.1)  # Small variation
            
            alt_match = match
            alt_match.visual_clip = alt_clip
            alt_matches.append(alt_match)
        
        return alt_matches
    
    def _adjust_duration(self, matches: List[SyncMatch], target_duration: float) -> List[SyncMatch]:
        """Ajusta duración total de matches"""
        current_duration = sum(m.audio_duration for m in matches)
        scale_factor = target_duration / current_duration
        
        adjusted = []
        for match in matches:
            new_match = match
            new_match.audio_duration *= scale_factor
            new_match.visual_duration = min(
                new_match.visual_clip.duration,
                new_match.audio_duration
            )
            adjusted.append(new_match)
        
        return adjusted
    
    def _apply_transitions(self, matches: List[SyncMatch], transition_type: str) -> List[SyncMatch]:
        """Aplica efectos de transición específicos"""
        enhanced = []
        for match in matches:
            new_match = match
            new_match.transition_type = transition_type
            
            # Ajustar fade in/out según tipo de transición
            if transition_type == "smooth_fade":
                new_match.fade_in = 0.5
                new_match.fade_out = 0.5
            elif transition_type == "cut":
                new_match.fade_in = 0.0
                new_match.fade_out = 0.0
            elif transition_type == "beat_sync":
                new_match.fade_in = 0.1
                new_match.fade_out = 0.1
            
            enhanced.append(new_match)
        
        return enhanced
    
    async def create_ab_test(self, variants: List[EditVariant],
                           test_name: str,
                           test_duration_hours: int = 24,
                           primary_metric: str = "engagement_rate") -> ABTestSetup:
        """
        Crea configuración de test A/B.
        
        Args:
            variants: Variantes a testear
            test_name: Nombre del test
            test_duration_hours: Duración en horas
            primary_metric: Métrica principal de éxito
            
        Returns:
            Configuración del test A/B
        """
        
        test_id = f"abtest_{uuid.uuid4().hex[:8]}"
        
        # Calcular distribución de tráfico
        num_variants = len(variants)
        base_allocation = 0.8 / num_variants  # 80% para variants, 20% para control
        
        traffic_allocation = {}
        for i, variant in enumerate(variants):
            if i == 0:  # Primera variante como control
                traffic_allocation[variant.variant_id] = 0.2
                variant.allocation_percentage = 20.0
            else:
                traffic_allocation[variant.variant_id] = base_allocation
                variant.allocation_percentage = base_allocation * 100
        
        # Configurar test
        ab_test = ABTestSetup(
            test_id=test_id,
            test_name=test_name,
            variants=variants,
            control_variant_id=variants[0].variant_id,
            test_duration_hours=test_duration_hours,
            traffic_allocation=traffic_allocation,
            target_sample_size=10000,  # Objetivo de views
            primary_metric=primary_metric,
            secondary_metrics=["viral_coefficient", "completion_rate", "shares"],
            success_criteria={
                "engagement_rate": 0.05,
                "viral_coefficient": 0.02,
                "statistical_significance": 0.95
            },
            platform_distribution={
                "tiktok": 0.6,
                "instagram": 0.3,
                "youtube_shorts": 0.1
            },
            audience_targeting={
                "age_range": "18-34",
                "interests": ["music", "entertainment", "viral_content"],
                "geographic": ["US", "MX", "ES", "AR"]
            },
            status="draft"
        )
        
        # Guardar test activo
        self.active_tests[test_id] = ab_test
        
        self.logger.info(f"🧪 Created A/B test: {test_name} with {len(variants)} variants")
        
        return ab_test
    
    async def start_ab_test(self, test_id: str) -> bool:
        """
        Inicia test A/B distribuyendo variantes en plataformas.
        
        Args:
            test_id: ID del test a iniciar
            
        Returns:
            True si se inició correctamente
        """
        
        if test_id not in self.active_tests:
            self.logger.error(f"❌ Test {test_id} not found")
            return False
        
        ab_test = self.active_tests[test_id]
        
        self.logger.info(f"🚀 Starting A/B test: {ab_test.test_name}")
        
        try:
            # Distribuir en Meta Ads
            if META_ADS_AVAILABLE and self.meta_automator:
                await self._deploy_to_meta_ads(ab_test)
            
            # Distribuir en Device Farm
            if DEVICE_FARM_AVAILABLE and self.device_manager:
                await self._deploy_to_device_farm(ab_test)
            
            # Actualizar estado
            ab_test.status = "running"
            ab_test.started_at = datetime.now().isoformat()
            
            self.logger.info(f"✅ A/B test {test_id} started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start A/B test {test_id}: {e}")
            return False
    
    async def _deploy_to_meta_ads(self, ab_test: ABTestSetup):
        """Despliega variantes en Meta Ads"""
        
        if DUMMY_MODE:
            self.logger.info("🎭 Dummy Meta Ads deployment")
            return
        
        for variant in ab_test.variants:
            # Crear campaña específica para la variante
            campaign_config = {
                "campaign_name": f"{ab_test.test_name}_Variant_{variant.variant_id}",
                "budget_percentage": variant.allocation_percentage,
                "targeting": ab_test.audience_targeting,
                "hashtags": variant.hashtags,
                "posting_schedule": variant.posting_schedule
            }
            
            # TODO: Implementar creación real de campaña Meta Ads
            self.logger.info(f"📊 Deployed variant {variant.variant_id} to Meta Ads")
    
    async def _deploy_to_device_farm(self, ab_test: ABTestSetup):
        """Despliega variantes en Device Farm"""
        
        if DUMMY_MODE:
            self.logger.info("🎭 Dummy Device Farm deployment")
            return
        
        for variant in ab_test.variants:
            # Configurar dispositivos para testear la variante
            device_config = {
                "variant_id": variant.variant_id,
                "test_duration": ab_test.test_duration_hours,
                "platforms": variant.configuration.target_platforms,
                "engagement_actions": ["like", "share", "comment"]
            }
            
            # TODO: Implementar distribución real en Device Farm
            self.logger.info(f"📱 Deployed variant {variant.variant_id} to Device Farm")
    
    async def collect_performance_data(self, test_id: str) -> Dict[str, List[VariantPerformance]]:
        """
        Recolecta datos de performance de todas las variantes.
        
        Args:
            test_id: ID del test
            
        Returns:
            Datos de performance por variante
        """
        
        if test_id not in self.active_tests:
            return {}
        
        ab_test = self.active_tests[test_id]
        performance_data = {}
        
        for variant in ab_test.variants:
            variant_performance = []
            
            # Recolectar de Meta Ads
            if META_ADS_AVAILABLE and self.meta_automator:
                meta_performance = await self._get_meta_performance(variant.variant_id)
                variant_performance.extend(meta_performance)
            
            # Recolectar de Device Farm
            if DEVICE_FARM_AVAILABLE and self.device_manager:
                device_performance = await self._get_device_performance(variant.variant_id)
                variant_performance.extend(device_performance)
            
            # Simular datos para dummy mode
            if DUMMY_MODE:
                dummy_performance = self._generate_dummy_performance(variant)
                variant_performance.extend(dummy_performance)
            
            performance_data[variant.variant_id] = variant_performance
        
        # Guardar en cache
        self.variant_performance[test_id] = performance_data
        
        return performance_data
    
    def _generate_dummy_performance(self, variant: EditVariant) -> List[VariantPerformance]:
        """Genera datos de performance dummy"""
        
        performances = []
        
        for platform in variant.configuration.target_platforms:
            # Simular métricas realistas
            impressions = np.random.randint(1000, 10000)
            views = int(impressions * np.random.uniform(0.1, 0.3))
            likes = int(views * np.random.uniform(0.02, 0.08))
            shares = int(views * np.random.uniform(0.005, 0.02))
            comments = int(views * np.random.uniform(0.001, 0.01))
            saves = int(views * np.random.uniform(0.01, 0.05))
            
            performance = VariantPerformance(
                variant_id=variant.variant_id,
                platform=platform,
                impressions=impressions,
                views=views,
                likes=likes,
                shares=shares,
                comments=comments,
                saves=saves,
                ctr=views / impressions,
                engagement_rate=(likes + shares + comments + saves) / views,
                viral_coefficient=shares / views,
                completion_rate=np.random.uniform(0.4, 0.8),
                unique_viewers=int(views * 0.9),
                repeat_viewers=int(views * 0.1),
                demographic_breakdown={
                    "age_18_24": 0.4,
                    "age_25_34": 0.35,
                    "age_35_44": 0.25
                },
                performance_by_hour={
                    f"{h}:00": {
                        "views": np.random.randint(10, 100),
                        "engagement": np.random.randint(1, 20)
                    }
                    for h in range(24)
                },
                peak_engagement_time="19:00",
                spend=np.random.uniform(10, 100),
                cpm=np.random.uniform(1, 5),
                cpc=np.random.uniform(0.1, 0.5),
                recorded_at=datetime.now().isoformat(),
                period_start=(datetime.now() - timedelta(hours=24)).isoformat(),
                period_end=datetime.now().isoformat()
            )
            performances.append(performance)
        
        return performances
    
    async def _get_meta_performance(self, variant_id: str) -> List[VariantPerformance]:
        """Obtiene performance de Meta Ads"""
        # TODO: Implementar obtención real de métricas Meta Ads
        return []
    
    async def _get_device_performance(self, variant_id: str) -> List[VariantPerformance]:
        """Obtiene performance de Device Farm"""
        # TODO: Implementar obtención real de métricas Device Farm
        return []
    
    async def analyze_test_results(self, test_id: str) -> Dict[str, Any]:
        """
        Analiza resultados del test A/B y determina ganador.
        
        Args:
            test_id: ID del test a analizar
            
        Returns:
            Análisis completo con ganador y insights
        """
        
        if test_id not in self.active_tests:
            return {"error": "Test not found"}
        
        ab_test = self.active_tests[test_id]
        performance_data = await self.collect_performance_data(test_id)
        
        if not performance_data:
            return {"error": "No performance data available"}
        
        # Calcular métricas agregadas por variante
        variant_metrics = {}
        
        for variant_id, performances in performance_data.items():
            total_views = sum(p.views for p in performances)
            total_engagement = sum(p.likes + p.shares + p.comments + p.saves for p in performances)
            total_shares = sum(p.shares for p in performances)
            
            if total_views > 0:
                avg_engagement_rate = total_engagement / total_views
                avg_viral_coefficient = total_shares / total_views
                avg_completion_rate = np.mean([p.completion_rate for p in performances])
            else:
                avg_engagement_rate = 0
                avg_viral_coefficient = 0
                avg_completion_rate = 0
            
            variant_metrics[variant_id] = {
                "total_views": total_views,
                "engagement_rate": avg_engagement_rate,
                "viral_coefficient": avg_viral_coefficient,
                "completion_rate": avg_completion_rate,
                "total_shares": total_shares,
                "platforms": len(performances)
            }
        
        # Determinar ganador basado en métrica principal
        primary_metric = ab_test.primary_metric
        winner_id = max(
            variant_metrics.keys(),
            key=lambda v: variant_metrics[v].get(primary_metric, 0)
        )
        
        winner_variant = next(v for v in ab_test.variants if v.variant_id == winner_id)
        control_id = ab_test.control_variant_id
        
        # Calcular mejora vs control
        winner_metric = variant_metrics[winner_id][primary_metric]
        control_metric = variant_metrics[control_id][primary_metric]
        
        improvement = ((winner_metric - control_metric) / control_metric * 100) if control_metric > 0 else 0
        
        # Análisis de significancia estadística (simplificado)
        statistical_significance = self._calculate_statistical_significance(
            variant_metrics[winner_id], variant_metrics[control_id]
        )
        
        analysis_result = {
            "test_id": test_id,
            "test_name": ab_test.test_name,
            "winner": {
                "variant_id": winner_id,
                "variant_type": winner_variant.variant_type.value,
                "improvement_vs_control": round(improvement, 2),
                "statistical_significance": statistical_significance
            },
            "all_variants": variant_metrics,
            "recommendations": self._generate_recommendations(
                winner_variant, variant_metrics, ab_test
            ),
            "insights": self._extract_insights(variant_metrics, ab_test),
            "analyzed_at": datetime.now().isoformat()
        }
        
        self.logger.info(f"📊 Test analysis complete. Winner: {winner_id} (+{improvement:.1f}%)")
        
        return analysis_result
    
    def _calculate_statistical_significance(self, winner_metrics: Dict, control_metrics: Dict) -> float:
        """Calcula significancia estadística (simplificado)"""
        # Implementación simplificada - en producción usar test estadístico real
        winner_views = winner_metrics["total_views"]
        control_views = control_metrics["total_views"]
        
        if winner_views > 1000 and control_views > 1000:
            return 0.95  # Alta confianza con suficientes datos
        elif winner_views > 500 and control_views > 500:
            return 0.85  # Confianza media
        else:
            return 0.70  # Baja confianza
    
    def _generate_recommendations(self, winner_variant: EditVariant,
                                variant_metrics: Dict, ab_test: ABTestSetup) -> List[str]:
        """Genera recomendaciones basadas en resultados"""
        
        recommendations = []
        
        # Recomendación del ganador
        recommendations.append(
            f"Implement {winner_variant.variant_type.value} variant as default"
        )
        
        # Análisis de plataformas
        best_platform = max(
            ab_test.platform_distribution.keys(),
            key=lambda p: variant_metrics[winner_variant.variant_id]["total_views"]
        )
        recommendations.append(f"Focus budget on {best_platform} platform")
        
        # Análisis temporal
        if winner_variant.viral_prediction and winner_variant.viral_prediction.timing_score > 0.8:
            recommendations.append(
                f"Use optimal posting time: {winner_variant.posting_schedule}"
            )
        
        return recommendations
    
    def _extract_insights(self, variant_metrics: Dict, ab_test: ABTestSetup) -> List[str]:
        """Extrae insights del análisis"""
        
        insights = []
        
        # Insight de performance general
        avg_engagement = np.mean([
            metrics["engagement_rate"] for metrics in variant_metrics.values()
        ])
        insights.append(f"Average engagement rate: {avg_engagement:.1%}")
        
        # Insight de viral potential
        avg_viral = np.mean([
            metrics["viral_coefficient"] for metrics in variant_metrics.values()
        ])
        insights.append(f"Average viral coefficient: {avg_viral:.1%}")
        
        # Insight de duración
        best_duration = None
        for variant in ab_test.variants:
            if variant.variant_type == VariantType.DURATION_VARIANT:
                duration = variant.configuration.parameters.get("target_duration")
                if duration:
                    insights.append(f"Duration {duration}s showed strong performance")
                    break
        
        return insights

# Factory function
def create_ab_testing_variants(meta_automator: MetaAdsAutomator = None,
                             device_manager = None,
                             viral_selector: ViralFragmentSelector = None) -> ABTestingVariants:
    """Crea instancia de ABTestingVariants"""
    return ABTestingVariants(meta_automator, device_manager, viral_selector)