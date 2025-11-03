"""
ML Integration - Módulo 7
Bridge de integración entre el Módulo 7 y otros sistemas ML.

Integra con:
- Meta Ads para distribución automática
- Device Farm para testing orgánico
- Analytics para performance tracking
"""

import asyncio
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json

# Importar componentes del módulo
from .ab_testing_variants import ABTestSetup, EditVariant, VariantPerformance
from .viral_fragment_selector import ViralPrediction

# Integración con Meta Ads
try:
    from social_extensions.meta.meta_automator import (
        MetaAdsAutomator, CampaignBrief, TargetingSpec, Creative,
        CampaignObjective, OptimizationGoal, BidStrategy, CreativeType
    )
    META_ADS_AVAILABLE = True
except ImportError:
    META_ADS_AVAILABLE = False

# Integración con Device Farm
try:
    from device_farm.controllers.device_manager import DeviceManager
    DEVICE_FARM_AVAILABLE = True
except ImportError:
    DEVICE_FARM_AVAILABLE = False

# Integración con Telegram
try:
    from telegram_automation.main_bot import TelegramBot
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

try:
    from config.app_settings import is_dummy_mode
    DUMMY_MODE = is_dummy_mode()
except ImportError:
    DUMMY_MODE = True

logger = logging.getLogger(__name__)

@dataclass
class DistributionConfig:
    """Configuración para distribución de variantes"""
    enable_meta_ads: bool = True
    enable_device_farm: bool = True
    enable_telegram: bool = False
    
    # Meta Ads config
    meta_daily_budget: float = 50.0
    meta_target_audience: Dict[str, Any] = None
    meta_campaign_objective: str = "REACH"
    
    # Device Farm config
    device_count: int = 5
    engagement_actions: List[str] = None
    testing_duration_hours: int = 24
    
    # Telegram config
    telegram_groups: List[str] = None
    telegram_priority: str = "medium"

@dataclass
class DistributionResult:
    """Resultado de distribución"""
    variant_id: str
    distribution_channels: List[str]
    meta_campaign_id: Optional[str] = None
    device_tasks: List[str] = None
    telegram_queued: bool = False
    
    estimated_reach: int = 0
    estimated_cost: float = 0.0
    distribution_timestamp: str = ""

class MLIntegration:
    """
    Bridge de integración ML para distribución automática de variantes virales.
    
    Conecta el Módulo 7 con Meta Ads, Device Farm, y Telegram para
    distribución y testing automatizado de edits virales.
    """
    
    def __init__(self, meta_automator: MetaAdsAutomator = None,
                 device_manager = None,
                 telegram_bot = None):
        
        self.meta_automator = meta_automator
        self.device_manager = device_manager 
        self.telegram_bot = telegram_bot
        
        self.logger = logging.getLogger(f"{__name__}.MLIntegration")
        
        # Tracking de distribuciones activas
        self.active_distributions: Dict[str, List[DistributionResult]] = {}
        
        # Configuración por defecto
        self.default_config = DistributionConfig(
            meta_target_audience={
                "countries": ["US", "MX", "ES", "AR"],
                "age_min": 18,
                "age_max": 34,
                "interests": ["music", "viral_content", "entertainment"]
            },
            engagement_actions=["like", "share", "comment", "follow"]
        )
        
        # Verificar integraciones disponibles
        self.integrations_status = {
            "meta_ads": META_ADS_AVAILABLE and self.meta_automator is not None,
            "device_farm": DEVICE_FARM_AVAILABLE and self.device_manager is not None,
            "telegram": TELEGRAM_AVAILABLE and self.telegram_bot is not None
        }
        
        self.logger.info(f"🔗 ML Integration initialized - Integrations: {self.integrations_status}")
    
    async def distribute_ab_test(self, ab_test: ABTestSetup,
                               config: DistributionConfig = None) -> Dict[str, List[DistributionResult]]:
        """
        Distribuye test A/B automáticamente en todas las plataformas.
        
        Args:
            ab_test: Setup del test A/B
            config: Configuración de distribución
            
        Returns:
            Resultados de distribución por variante
        """
        
        use_config = config or self.default_config
        
        self.logger.info(f"🚀 Distributing A/B test: {ab_test.test_name}")
        
        distribution_results = {}
        
        # Distribuir cada variante
        for variant in ab_test.variants:
            variant_results = []
            
            # Meta Ads Distribution
            if use_config.enable_meta_ads and self.integrations_status["meta_ads"]:
                meta_result = await self._distribute_to_meta_ads(
                    variant, ab_test, use_config
                )
                if meta_result:
                    variant_results.append(meta_result)
            
            # Device Farm Distribution
            if use_config.enable_device_farm and self.integrations_status["device_farm"]:
                device_result = await self._distribute_to_device_farm(
                    variant, ab_test, use_config
                )
                if device_result:
                    variant_results.append(device_result)
            
            # Telegram Distribution
            if use_config.enable_telegram and self.integrations_status["telegram"]:
                telegram_result = await self._distribute_to_telegram(
                    variant, ab_test, use_config
                )
                if telegram_result:
                    variant_results.append(telegram_result)
            
            distribution_results[variant.variant_id] = variant_results
        
        # Guardar distribuciones activas
        self.active_distributions[ab_test.test_id] = distribution_results
        
        # Calcular estadísticas
        total_channels = sum(len(results) for results in distribution_results.values())
        total_estimated_reach = sum(
            result.estimated_reach 
            for results in distribution_results.values()
            for result in results
        )
        
        self.logger.info(f"✅ A/B test distributed - {total_channels} channels, estimated reach: {total_estimated_reach:,}")
        
        return distribution_results
    
    async def _distribute_to_meta_ads(self, variant: EditVariant, ab_test: ABTestSetup,
                                    config: DistributionConfig) -> Optional[DistributionResult]:
        """Distribuye variante en Meta Ads"""
        
        try:
            if DUMMY_MODE:
                return self._create_dummy_meta_result(variant)
            
            self.logger.info(f"📊 Creating Meta Ads campaign for variant: {variant.variant_id}")
            
            # Configurar targeting
            targeting = TargetingSpec(
                countries=config.meta_target_audience.get("countries", ["US"]),
                age_min=config.meta_target_audience.get("age_min", 18),
                age_max=config.meta_target_audience.get("age_max", 34),
                interests=config.meta_target_audience.get("interests", ["music"])
            )
            
            # Configurar creative basado en la variante
            creative_title = f"Viral {variant.variant_type.value.title()} Edit"
            creative_description = f"Optimized for {', '.join(variant.configuration.target_platforms)}"
            
            if variant.hashtags:
                creative_description += f" {' '.join(variant.hashtags[:3])}"
            
            creative = Creative(
                creative_id=f"creative_{variant.variant_id}",
                name=creative_title,
                type=CreativeType.VIDEO,
                title=creative_title,
                body=creative_description,
                call_to_action="LEARN_MORE"
            )
            
            # Crear campaign brief
            campaign_brief = CampaignBrief(
                campaign_name=f"{ab_test.test_name}_{variant.variant_type.value}",
                objective=CampaignObjective.REACH,
                optimization_goal=OptimizationGoal.REACH,
                bid_strategy=BidStrategy.LOWEST_COST_WITHOUT_CAP,
                daily_budget=config.meta_daily_budget * (variant.allocation_percentage / 100),
                targeting=targeting,
                creatives=[creative],
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(hours=ab_test.test_duration_hours)
            )
            
            # Crear campaña
            campaign_result = await self.meta_automator.create_campaign_from_brief(campaign_brief)
            
            if campaign_result and "campaign_id" in campaign_result:
                return DistributionResult(
                    variant_id=variant.variant_id,
                    distribution_channels=["meta_ads"],
                    meta_campaign_id=campaign_result["campaign_id"],
                    estimated_reach=int(config.meta_daily_budget * 100),  # Estimate
                    estimated_cost=config.meta_daily_budget,
                    distribution_timestamp=datetime.now().isoformat()
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Meta Ads distribution failed for {variant.variant_id}: {e}")
            return None
    
    def _create_dummy_meta_result(self, variant: EditVariant) -> DistributionResult:
        """Crea resultado dummy para Meta Ads"""
        return DistributionResult(
            variant_id=variant.variant_id,
            distribution_channels=["meta_ads"],
            meta_campaign_id=f"dummy_campaign_{variant.variant_id}",
            estimated_reach=np.random.randint(5000, 20000),
            estimated_cost=np.random.uniform(20, 80),
            distribution_timestamp=datetime.now().isoformat()
        )
    
    async def _distribute_to_device_farm(self, variant: EditVariant, ab_test: ABTestSetup,
                                       config: DistributionConfig) -> Optional[DistributionResult]:
        """Distribuye variante en Device Farm"""
        
        try:
            if DUMMY_MODE:
                return self._create_dummy_device_result(variant, config)
            
            self.logger.info(f"📱 Scheduling Device Farm tasks for variant: {variant.variant_id}")
            
            # Configurar tareas para dispositivos
            device_tasks = []
            
            for platform in variant.configuration.target_platforms:
                if platform in ["tiktok", "instagram"]:
                    task_config = {
                        "variant_id": variant.variant_id,
                        "platform": platform,
                        "actions": config.engagement_actions,
                        "duration_hours": config.testing_duration_hours,
                        "hashtags": variant.hashtags,
                        "priority": "high" if variant.viral_prediction and variant.viral_prediction.viral_score > 0.8 else "medium"
                    }
                    
                    # TODO: Implementar creación real de tareas en Device Farm
                    task_id = await self._create_device_task(task_config)
                    if task_id:
                        device_tasks.append(task_id)
            
            if device_tasks:
                return DistributionResult(
                    variant_id=variant.variant_id,
                    distribution_channels=["device_farm"],
                    device_tasks=device_tasks,
                    estimated_reach=len(device_tasks) * 1000,  # Aproximado
                    estimated_cost=0.0,  # Orgánico
                    distribution_timestamp=datetime.now().isoformat()
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Device Farm distribution failed for {variant.variant_id}: {e}")
            return None
    
    def _create_dummy_device_result(self, variant: EditVariant, config: DistributionConfig) -> DistributionResult:
        """Crea resultado dummy para Device Farm"""
        task_count = min(config.device_count, len(variant.configuration.target_platforms))
        
        return DistributionResult(
            variant_id=variant.variant_id,
            distribution_channels=["device_farm"],
            device_tasks=[f"dummy_task_{i}_{variant.variant_id}" for i in range(task_count)],
            estimated_reach=task_count * np.random.randint(800, 1200),
            estimated_cost=0.0,
            distribution_timestamp=datetime.now().isoformat()
        )
    
    async def _create_device_task(self, task_config: Dict[str, Any]) -> Optional[str]:
        """Crea tarea en Device Farm"""
        
        # TODO: Implementar integración real con Device Farm
        # Por ahora retornamos ID simulado
        task_id = f"task_{task_config['variant_id']}_{task_config['platform']}"
        
        self.logger.info(f"📱 Created device task: {task_id}")
        return task_id
    
    async def _distribute_to_telegram(self, variant: EditVariant, ab_test: ABTestSetup,
                                    config: DistributionConfig) -> Optional[DistributionResult]:
        """Distribuye variante en Telegram Like4Like"""
        
        try:
            if DUMMY_MODE:
                return self._create_dummy_telegram_result(variant)
            
            self.logger.info(f"💬 Queuing Telegram tasks for variant: {variant.variant_id}")
            
            # Configurar mensaje para Telegram
            telegram_message = {
                "variant_id": variant.variant_id,
                "content_type": "video_edit",
                "priority": config.telegram_priority,
                "hashtags": variant.hashtags,
                "target_groups": config.telegram_groups or ["general"],
                "estimated_engagement": variant.viral_prediction.engagement_prediction if variant.viral_prediction else {}
            }
            
            # TODO: Implementar integración real con Telegram Bot
            telegram_queued = await self._queue_telegram_message(telegram_message)
            
            if telegram_queued:
                return DistributionResult(
                    variant_id=variant.variant_id,
                    distribution_channels=["telegram"],
                    telegram_queued=True,
                    estimated_reach=len(config.telegram_groups or []) * 500,  # Aproximado
                    estimated_cost=0.0,  # Orgánico
                    distribution_timestamp=datetime.now().isoformat()
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Telegram distribution failed for {variant.variant_id}: {e}")
            return None
    
    def _create_dummy_telegram_result(self, variant: EditVariant) -> DistributionResult:
        """Crea resultado dummy para Telegram"""
        return DistributionResult(
            variant_id=variant.variant_id,
            distribution_channels=["telegram"],
            telegram_queued=True,
            estimated_reach=np.random.randint(2000, 8000),
            estimated_cost=0.0,
            distribution_timestamp=datetime.now().isoformat()
        )
    
    async def _queue_telegram_message(self, message_config: Dict[str, Any]) -> bool:
        """Cola mensaje en sistema Telegram"""
        
        # TODO: Implementar integración real con Telegram Bot
        self.logger.info(f"💬 Queued Telegram message for variant: {message_config['variant_id']}")
        return True
    
    async def collect_performance_data(self, test_id: str) -> Dict[str, List[VariantPerformance]]:
        """
        Recolecta datos de performance de todas las distribuciones.
        
        Args:
            test_id: ID del test A/B
            
        Returns:
            Datos de performance por variante y canal
        """
        
        if test_id not in self.active_distributions:
            return {}
        
        performance_data = {}
        distributions = self.active_distributions[test_id]
        
        for variant_id, distribution_results in distributions.items():
            variant_performance = []
            
            for distribution in distribution_results:
                
                # Recolectar de Meta Ads
                if "meta_ads" in distribution.distribution_channels and distribution.meta_campaign_id:
                    meta_performance = await self._collect_meta_performance(distribution.meta_campaign_id)
                    if meta_performance:
                        variant_performance.extend(meta_performance)
                
                # Recolectar de Device Farm
                if "device_farm" in distribution.distribution_channels and distribution.device_tasks:
                    device_performance = await self._collect_device_performance(distribution.device_tasks)
                    if device_performance:
                        variant_performance.extend(device_performance)
                
                # Recolectar de Telegram
                if "telegram" in distribution.distribution_channels and distribution.telegram_queued:
                    telegram_performance = await self._collect_telegram_performance(variant_id)
                    if telegram_performance:
                        variant_performance.extend(telegram_performance)
            
            performance_data[variant_id] = variant_performance
        
        return performance_data
    
    async def _collect_meta_performance(self, campaign_id: str) -> List[VariantPerformance]:
        """Recolecta performance de Meta Ads"""
        
        if DUMMY_MODE:
            return [self._generate_dummy_meta_performance(campaign_id)]
        
        try:
            # TODO: Implementar recolección real de métricas Meta Ads
            metrics = await self.meta_automator.get_campaign_metrics(campaign_id)
            
            if metrics:
                # Convertir métricas a VariantPerformance
                performance = VariantPerformance(
                    variant_id=campaign_id,
                    platform="meta_ads",
                    impressions=metrics[0].impressions if metrics else 0,
                    views=metrics[0].clicks if metrics else 0,
                    likes=metrics[0].post_engagements if metrics else 0,
                    shares=metrics[0].post_shares if metrics else 0,
                    comments=metrics[0].post_comments if metrics else 0,
                    saves=metrics[0].post_saves if metrics else 0,
                    ctr=metrics[0].ctr if metrics else 0.0,
                    engagement_rate=metrics[0].engagement_rate if metrics else 0.0,
                    viral_coefficient=0.0,  # Calcular
                    completion_rate=0.8,  # Estimar
                    unique_viewers=metrics[0].unique_clicks if metrics else 0,
                    repeat_viewers=0,
                    demographic_breakdown={},
                    performance_by_hour={},
                    peak_engagement_time="19:00",
                    spend=metrics[0].spend if metrics else 0.0,
                    cpm=metrics[0].cpm if metrics else 0.0,
                    cpc=metrics[0].cpc if metrics else 0.0,
                    recorded_at=datetime.now().isoformat(),
                    period_start=(datetime.now() - timedelta(hours=24)).isoformat(),
                    period_end=datetime.now().isoformat()
                )
                
                return [performance]
            
        except Exception as e:
            self.logger.error(f"❌ Failed to collect Meta performance: {e}")
        
        return []
    
    def _generate_dummy_meta_performance(self, campaign_id: str) -> VariantPerformance:
        """Genera performance dummy de Meta Ads"""
        
        impressions = np.random.randint(5000, 25000)
        views = int(impressions * np.random.uniform(0.05, 0.15))
        likes = int(views * np.random.uniform(0.02, 0.08))
        
        return VariantPerformance(
            variant_id=campaign_id,
            platform="meta_ads", 
            impressions=impressions,
            views=views,
            likes=likes,
            shares=int(views * np.random.uniform(0.005, 0.02)),
            comments=int(views * np.random.uniform(0.001, 0.01)),
            saves=int(views * np.random.uniform(0.01, 0.05)),
            ctr=views / impressions,
            engagement_rate=likes / views,
            viral_coefficient=np.random.uniform(0.01, 0.05),
            completion_rate=np.random.uniform(0.6, 0.9),
            unique_viewers=int(views * 0.9),
            repeat_viewers=int(views * 0.1),
            demographic_breakdown={"age_18_24": 0.4, "age_25_34": 0.6},
            performance_by_hour={},
            peak_engagement_time="19:00",
            spend=np.random.uniform(20, 80),
            cpm=np.random.uniform(2, 8),
            cpc=np.random.uniform(0.2, 1.0),
            recorded_at=datetime.now().isoformat(),
            period_start=(datetime.now() - timedelta(hours=24)).isoformat(),
            period_end=datetime.now().isoformat()
        )
    
    async def _collect_device_performance(self, task_ids: List[str]) -> List[VariantPerformance]:
        """Recolecta performance de Device Farm"""
        
        if DUMMY_MODE:
            return [self._generate_dummy_device_performance(task_id) for task_id in task_ids[:2]]
        
        # TODO: Implementar recolección real de Device Farm
        return []
    
    def _generate_dummy_device_performance(self, task_id: str) -> VariantPerformance:
        """Genera performance dummy de Device Farm"""
        
        views = np.random.randint(800, 1500)
        likes = int(views * np.random.uniform(0.05, 0.12))
        
        return VariantPerformance(
            variant_id=task_id,
            platform="device_farm_organic",
            impressions=views,
            views=views,
            likes=likes,
            shares=int(views * np.random.uniform(0.01, 0.03)),
            comments=int(views * np.random.uniform(0.005, 0.02)),
            saves=int(views * np.random.uniform(0.02, 0.08)),
            ctr=1.0,  # Orgánico
            engagement_rate=likes / views,
            viral_coefficient=np.random.uniform(0.02, 0.08),
            completion_rate=np.random.uniform(0.7, 0.95),
            unique_viewers=views,
            repeat_viewers=0,
            demographic_breakdown={},
            performance_by_hour={},
            peak_engagement_time="20:00",
            spend=0.0,
            cpm=0.0,
            cpc=0.0,
            recorded_at=datetime.now().isoformat(),
            period_start=(datetime.now() - timedelta(hours=24)).isoformat(),
            period_end=datetime.now().isoformat()
        )
    
    async def _collect_telegram_performance(self, variant_id: str) -> List[VariantPerformance]:
        """Recolecta performance de Telegram"""
        
        if DUMMY_MODE:
            return [self._generate_dummy_telegram_performance(variant_id)]
        
        # TODO: Implementar recolección real de Telegram
        return []
    
    def _generate_dummy_telegram_performance(self, variant_id: str) -> VariantPerformance:
        """Genera performance dummy de Telegram"""
        
        views = np.random.randint(2000, 6000)
        likes = int(views * np.random.uniform(0.03, 0.09))
        
        return VariantPerformance(
            variant_id=variant_id,
            platform="telegram_like4like",
            impressions=views,
            views=views,
            likes=likes,
            shares=int(views * np.random.uniform(0.008, 0.025)),
            comments=int(views * np.random.uniform(0.003, 0.015)),
            saves=int(views * np.random.uniform(0.015, 0.06)),
            ctr=1.0,  # Orgánico
            engagement_rate=likes / views,
            viral_coefficient=np.random.uniform(0.015, 0.06),
            completion_rate=np.random.uniform(0.8, 0.95),
            unique_viewers=views,
            repeat_viewers=0,
            demographic_breakdown={},
            performance_by_hour={},
            peak_engagement_time="18:00",
            spend=0.0,
            cpm=0.0,
            cpc=0.0,
            recorded_at=datetime.now().isoformat(),
            period_start=(datetime.now() - timedelta(hours=24)).isoformat(),
            period_end=datetime.now().isoformat()
        )
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Obtiene estado de todas las integraciones"""
        
        return {
            "integrations": self.integrations_status,
            "active_distributions": len(self.active_distributions),
            "dummy_mode": DUMMY_MODE,
            "capabilities": {
                "meta_ads_distribution": self.integrations_status["meta_ads"],
                "device_farm_testing": self.integrations_status["device_farm"],
                "telegram_like4like": self.integrations_status["telegram"],
                "performance_collection": True,
                "ab_testing": True
            },
            "status_timestamp": datetime.now().isoformat()
        }

# Factory function
def create_ml_integration(meta_automator: MetaAdsAutomator = None,
                         device_manager = None,
                         telegram_bot = None) -> MLIntegration:
    """Crea instancia de MLIntegration"""
    return MLIntegration(meta_automator, device_manager, telegram_bot)