"""
Continuous Learning - Módulo 7
Sistema de aprendizaje continuo que mejora las generaciones futuras basado en performance.

Integra con:
- Database para storage de aprendizajes
- ML Core para refinamiento de modelos
- Performance data de todas las plataformas
"""

import asyncio
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import sqlite3
from pathlib import Path
import pickle
from collections import defaultdict

# Importar componentes del módulo
from .ab_testing_variants import VariantPerformance, ABTestSetup
from .viral_fragment_selector import ViralPrediction, FragmentMetrics
from .semantic_synchronizer import SyncMatch
from .visual_clip_database import VisualClip

# Integración con sistema existente
try:
    from config.app_settings import is_dummy_mode
    DUMMY_MODE = is_dummy_mode()
except ImportError:
    DUMMY_MODE = True

try:
    from database.models import Base, engine
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class LearningPattern:
    """Patrón aprendido del sistema"""
    pattern_id: str
    pattern_type: str                    # "sync", "viral", "timing", "platform"
    pattern_data: Dict[str, Any]         # Datos del patrón
    
    # Performance metrics
    success_rate: float                  # Tasa de éxito del patrón
    avg_viral_score: float               # Score viral promedio
    sample_size: int                     # Número de muestras
    
    # Context
    platforms: List[str]                 # Plataformas donde aplica
    genres: List[str]                    # Géneros musicales
    audience_segments: List[str]         # Segmentos de audiencia
    
    # Temporal patterns
    optimal_times: List[str]             # Horarios óptimos
    seasonal_factors: Dict[str, float]   # Factores estacionales
    
    # Confidence and validity
    confidence: float                    # Confianza en el patrón
    last_validated: str                  # Última validación
    
    # Metadata
    discovered_at: str
    updated_at: str

@dataclass
class PerformanceInsight:
    """Insight derivado del análisis de performance"""
    insight_id: str
    insight_type: str                    # "optimization", "warning", "opportunity"
    
    # Insight data
    title: str
    description: str
    recommendation: str
    impact_level: str                    # "low", "medium", "high", "critical"
    
    # Supporting data
    supporting_metrics: Dict[str, float]
    confidence: float
    
    # Actionability
    actionable: bool
    implementation_effort: str           # "low", "medium", "high"
    expected_improvement: float          # % de mejora esperada
    
    # Context
    applicable_to: List[str]             # IDs de variantes/tests aplicables
    
    created_at: str

@dataclass
class ModelUpdate:
    """Actualización de modelo basada en aprendizaje"""
    update_id: str
    model_component: str                 # "sync", "viral_prediction", "timing"
    
    # Update details
    update_type: str                     # "weight_adjustment", "threshold_change", "new_feature"
    old_parameters: Dict[str, Any]
    new_parameters: Dict[str, Any]
    
    # Performance impact
    expected_improvement: float
    validation_score: float
    
    # Metadata
    applied_at: Optional[str] = None
    rollback_data: Optional[Dict[str, Any]] = None

class ContinuousLearning:
    """
    Sistema de aprendizaje continuo para mejora automática.
    
    Analiza performance histórica, identifica patrones exitosos,
    y refina automáticamente los algoritmos para futuras generaciones.
    """
    
    def __init__(self, database_path: str = None):
        self.database_path = database_path or "data/continuous_learning.db"
        self.logger = logging.getLogger(f"{__name__}.ContinuousLearning")
        
        # Ensure database directory exists
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Learning data storage
        self.learned_patterns: Dict[str, LearningPattern] = {}
        self.performance_insights: Dict[str, PerformanceInsight] = {}
        self.model_updates: List[ModelUpdate] = []
        
        # Learning configuration
        self.learning_config = {
            "min_sample_size": 10,           # Mínimo de muestras para patrón válido
            "confidence_threshold": 0.7,     # Confianza mínima para aplicar
            "improvement_threshold": 0.05,   # Mejora mínima para actualización
            "validation_period_days": 7,     # Período de validación
            "max_patterns": 1000,            # Máximo patrones almacenados
            "learning_rate": 0.1             # Tasa de aprendizaje
        }
        
        # Performance tracking
        self.performance_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Model weights and parameters
        self.current_model_weights = {
            "sync_factors": {
                "genre_match": 0.25,
                "energy_match": 0.20,
                "tempo_match": 0.15,
                "viral_potential": 0.15,
                "freshness": 0.10,
                "timing_optimization": 0.15
            },
            "viral_factors": {
                "audio_catchiness": 0.25,
                "visual_impact": 0.20,
                "trend_alignment": 0.15,
                "timing_optimization": 0.15,
                "platform_fit": 0.10,
                "novelty_factor": 0.10,
                "emotional_resonance": 0.05
            },
            "platform_optimization": {
                "tiktok": {"duration_weight": 0.3, "trend_weight": 0.4, "visual_weight": 0.3},
                "instagram": {"duration_weight": 0.2, "trend_weight": 0.3, "visual_weight": 0.5},
                "youtube_shorts": {"duration_weight": 0.4, "trend_weight": 0.2, "visual_weight": 0.4}
            }
        }
        
        # Initialize database
        self._initialize_database()
        
        self.logger.info("🧠 Continuous Learning system initialized")
    
    def _initialize_database(self):
        """Inicializa base de datos de aprendizaje"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                # Tabla de patrones aprendidos
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS learning_patterns (
                        pattern_id TEXT PRIMARY KEY,
                        pattern_type TEXT,
                        pattern_data TEXT,
                        success_rate REAL,
                        avg_viral_score REAL,
                        sample_size INTEGER,
                        platforms TEXT,
                        genres TEXT,
                        audience_segments TEXT,
                        optimal_times TEXT,
                        seasonal_factors TEXT,
                        confidence REAL,
                        last_validated TEXT,
                        discovered_at TEXT,
                        updated_at TEXT
                    )
                """)
                
                # Tabla de insights de performance
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS performance_insights (
                        insight_id TEXT PRIMARY KEY,
                        insight_type TEXT,
                        title TEXT,
                        description TEXT,
                        recommendation TEXT,
                        impact_level TEXT,
                        supporting_metrics TEXT,
                        confidence REAL,
                        actionable BOOLEAN,
                        implementation_effort TEXT,
                        expected_improvement REAL,
                        applicable_to TEXT,
                        created_at TEXT
                    )
                """)
                
                # Tabla de actualizaciones de modelo
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS model_updates (
                        update_id TEXT PRIMARY KEY,
                        model_component TEXT,
                        update_type TEXT,
                        old_parameters TEXT,
                        new_parameters TEXT,
                        expected_improvement REAL,
                        validation_score REAL,
                        applied_at TEXT,
                        rollback_data TEXT
                    )
                """)
                
                # Tabla de historial de performance
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS performance_history (
                        record_id TEXT PRIMARY KEY,
                        variant_id TEXT,
                        test_id TEXT,
                        platform TEXT,
                        metrics TEXT,
                        timestamp TEXT
                    )
                """)
                
                # Índices
                conn.execute("CREATE INDEX IF NOT EXISTS idx_pattern_type ON learning_patterns(pattern_type)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_pattern_confidence ON learning_patterns(confidence)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_insight_type ON performance_insights(insight_type)")
                
                conn.commit()
                
            self.logger.info("📋 Learning database initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Database initialization failed: {e}")
    
    async def learn_from_ab_test(self, ab_test: ABTestSetup,
                                performance_data: Dict[str, List[VariantPerformance]]) -> List[LearningPattern]:
        """
        Aprende patrones de un test A/B completado.
        
        Args:
            ab_test: Setup del test A/B
            performance_data: Datos de performance por variante
            
        Returns:
            Lista de patrones aprendidos
        """
        
        self.logger.info(f"🧠 Learning from A/B test: {ab_test.test_name}")
        
        learned_patterns = []
        
        # Analizar performance por tipo de variante
        variant_performance = {}
        
        for variant in ab_test.variants:
            variant_id = variant.variant_id
            performances = performance_data.get(variant_id, [])
            
            if performances:
                # Calcular métricas agregadas
                total_views = sum(p.views for p in performances)
                total_engagement = sum(p.likes + p.shares + p.comments + p.saves for p in performances)
                avg_viral_coefficient = np.mean([p.viral_coefficient for p in performances])
                
                engagement_rate = total_engagement / total_views if total_views > 0 else 0
                
                variant_performance[variant_id] = {
                    "variant_type": variant.variant_type.value,
                    "engagement_rate": engagement_rate,
                    "viral_coefficient": avg_viral_coefficient,
                    "total_views": total_views,
                    "platforms": list(set(p.platform for p in performances)),
                    "configuration": variant.configuration.parameters
                }
        
        # Identificar patrones por tipo de variante
        patterns_by_type = defaultdict(list)
        for variant_id, perf in variant_performance.items():
            patterns_by_type[perf["variant_type"]].append(perf)
        
        # Aprender patrones por tipo
        for variant_type, performances in patterns_by_type.items():
            if len(performances) >= 2:  # Mínimo 2 variantes para comparar
                pattern = await self._analyze_variant_type_pattern(
                    variant_type, performances, ab_test
                )
                if pattern:
                    learned_patterns.append(pattern)
        
        # Aprender patrones de timing
        timing_pattern = await self._analyze_timing_patterns(ab_test, performance_data)
        if timing_pattern:
            learned_patterns.append(timing_pattern)
        
        # Aprender patrones de plataforma
        platform_patterns = await self._analyze_platform_patterns(ab_test, performance_data)
        learned_patterns.extend(platform_patterns)
        
        # Guardar patrones aprendidos
        for pattern in learned_patterns:
            await self._save_learning_pattern(pattern)
            self.learned_patterns[pattern.pattern_id] = pattern
        
        self.logger.info(f"✅ Learned {len(learned_patterns)} patterns from test: {ab_test.test_name}")
        
        return learned_patterns
    
    async def _analyze_variant_type_pattern(self, variant_type: str, performances: List[Dict],
                                          ab_test: ABTestSetup) -> Optional[LearningPattern]:
        """Analiza patrones por tipo de variante"""
        
        # Encontrar mejor performance
        best_performance = max(performances, key=lambda x: x["engagement_rate"])
        avg_engagement = np.mean([p["engagement_rate"] for p in performances])
        
        # Solo crear patrón si hay diferencia significativa
        if best_performance["engagement_rate"] > avg_engagement * 1.1:  # 10% mejor
            
            pattern_data = {
                "variant_type": variant_type,
                "optimal_configuration": best_performance["configuration"],
                "performance_improvement": (best_performance["engagement_rate"] - avg_engagement) / avg_engagement,
                "sample_metrics": {
                    "best_engagement_rate": best_performance["engagement_rate"],
                    "avg_engagement_rate": avg_engagement,
                    "best_viral_coefficient": best_performance["viral_coefficient"]
                }
            }
            
            pattern_id = f"variant_{variant_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            return LearningPattern(
                pattern_id=pattern_id,
                pattern_type="variant_optimization",
                pattern_data=pattern_data,
                success_rate=best_performance["engagement_rate"],
                avg_viral_score=best_performance["viral_coefficient"],
                sample_size=len(performances),
                platforms=list(set().union(*[p["platforms"] for p in performances])),
                genres=[],  # TODO: Extract from test context
                audience_segments=[],
                optimal_times=[],
                seasonal_factors={},
                confidence=min(0.9, len(performances) / 10),  # More samples = higher confidence
                last_validated=datetime.now().isoformat(),
                discovered_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
        
        return None
    
    async def _analyze_timing_patterns(self, ab_test: ABTestSetup,
                                     performance_data: Dict[str, List[VariantPerformance]]) -> Optional[LearningPattern]:
        """Analiza patrones de timing óptimo"""
        
        timing_performance = defaultdict(list)
        
        # Agregar performance por hora
        for variant_id, performances in performance_data.items():
            for perf in performances:
                if hasattr(perf, 'peak_engagement_time') and perf.peak_engagement_time:
                    hour = perf.peak_engagement_time.split(':')[0]
                    timing_performance[hour].append(perf.engagement_rate)
        
        if len(timing_performance) >= 3:  # Mínimo 3 horas diferentes
            # Encontrar hora con mejor engagement promedio
            hour_averages = {
                hour: np.mean(rates) for hour, rates in timing_performance.items()
            }
            
            best_hour = max(hour_averages.keys(), key=lambda h: hour_averages[h])
            best_avg = hour_averages[best_hour]
            overall_avg = np.mean([rate for rates in timing_performance.values() for rate in rates])
            
            if best_avg > overall_avg * 1.15:  # 15% mejor
                pattern_data = {
                    "optimal_hour": best_hour,
                    "performance_by_hour": hour_averages,
                    "improvement_factor": best_avg / overall_avg,
                    "sample_distribution": {hour: len(rates) for hour, rates in timing_performance.items()}
                }
                
                pattern_id = f"timing_{best_hour}h_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                return LearningPattern(
                    pattern_id=pattern_id,
                    pattern_type="timing_optimization",
                    pattern_data=pattern_data,
                    success_rate=best_avg,
                    avg_viral_score=0.0,  # Not applicable for timing
                    sample_size=sum(len(rates) for rates in timing_performance.values()),
                    platforms=[],
                    genres=[],
                    audience_segments=[],
                    optimal_times=[f"{best_hour}:00"],
                    seasonal_factors={},
                    confidence=min(0.9, len(timing_performance) / 24),
                    last_validated=datetime.now().isoformat(),
                    discovered_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
        
        return None
    
    async def _analyze_platform_patterns(self, ab_test: ABTestSetup,
                                       performance_data: Dict[str, List[VariantPerformance]]) -> List[LearningPattern]:
        """Analiza patrones específicos por plataforma"""
        
        platform_patterns = []
        platform_performance = defaultdict(list)
        
        # Agregar performance por plataforma
        for performances in performance_data.values():
            for perf in performances:
                platform_performance[perf.platform].append({
                    "engagement_rate": perf.engagement_rate,
                    "viral_coefficient": perf.viral_coefficient,
                    "completion_rate": perf.completion_rate,
                    "ctr": perf.ctr
                })
        
        # Analizar cada plataforma
        for platform, performances in platform_performance.items():
            if len(performances) >= self.learning_config["min_sample_size"]:
                
                avg_engagement = np.mean([p["engagement_rate"] for p in performances])
                avg_viral = np.mean([p["viral_coefficient"] for p in performances])
                avg_completion = np.mean([p["completion_rate"] for p in performances])
                
                # Identificar características destacadas de la plataforma
                standout_metrics = {}
                if avg_engagement > 0.05:  # Above 5%
                    standout_metrics["high_engagement"] = avg_engagement
                if avg_viral > 0.02:  # Above 2%
                    standout_metrics["viral_potential"] = avg_viral
                if avg_completion > 0.8:  # Above 80%
                    standout_metrics["high_completion"] = avg_completion
                
                if standout_metrics:
                    pattern_data = {
                        "platform": platform,
                        "avg_metrics": {
                            "engagement_rate": avg_engagement,
                            "viral_coefficient": avg_viral,
                            "completion_rate": avg_completion
                        },
                        "standout_characteristics": standout_metrics,
                        "optimization_recommendations": self._generate_platform_recommendations(
                            platform, standout_metrics
                        )
                    }
                    
                    pattern_id = f"platform_{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    pattern = LearningPattern(
                        pattern_id=pattern_id,
                        pattern_type="platform_optimization",
                        pattern_data=pattern_data,
                        success_rate=avg_engagement,
                        avg_viral_score=avg_viral,
                        sample_size=len(performances),
                        platforms=[platform],
                        genres=[],
                        audience_segments=[],
                        optimal_times=[],
                        seasonal_factors={},
                        confidence=min(0.9, len(performances) / 50),
                        last_validated=datetime.now().isoformat(),
                        discovered_at=datetime.now().isoformat(),
                        updated_at=datetime.now().isoformat()
                    )
                    
                    platform_patterns.append(pattern)
        
        return platform_patterns
    
    def _generate_platform_recommendations(self, platform: str, metrics: Dict[str, float]) -> List[str]:
        """Genera recomendaciones específicas por plataforma"""
        
        recommendations = []
        
        if platform == "tiktok":
            if "high_engagement" in metrics:
                recommendations.append("Prioritize TikTok for high-engagement content")
            if "viral_potential" in metrics:
                recommendations.append("Use TikTok for maximum viral reach")
        
        elif platform == "instagram":
            if "high_completion" in metrics:
                recommendations.append("Instagram shows high completion rates - optimize for retention")
            if "high_engagement" in metrics:
                recommendations.append("Instagram audience is highly engaged - focus on visual quality")
        
        elif platform == "youtube_shorts":
            if "viral_potential" in metrics:
                recommendations.append("YouTube Shorts has viral potential - leverage algorithm optimization")
        
        return recommendations
    
    async def generate_performance_insights(self, lookback_days: int = 30) -> List[PerformanceInsight]:
        """
        Genera insights basados en performance histórica.
        
        Args:
            lookback_days: Días hacia atrás para analizar
            
        Returns:
            Lista de insights generados
        """
        
        self.logger.info(f"🔍 Generating performance insights (last {lookback_days} days)")
        
        insights = []
        
        # Cargar datos históricos
        historical_data = await self._load_historical_performance(lookback_days)
        
        if not historical_data:
            return insights
        
        # Insight 1: Mejores horarios
        timing_insight = await self._generate_timing_insight(historical_data)
        if timing_insight:
            insights.append(timing_insight)
        
        # Insight 2: Plataformas con mejor ROI
        platform_insight = await self._generate_platform_insight(historical_data)
        if platform_insight:
            insights.append(platform_insight)
        
        # Insight 3: Patrones de contenido exitoso
        content_insight = await self._generate_content_insight(historical_data)
        if content_insight:
            insights.append(content_insight)
        
        # Insight 4: Oportunidades de optimización
        optimization_insights = await self._generate_optimization_insights(historical_data)
        insights.extend(optimization_insights)
        
        # Guardar insights
        for insight in insights:
            await self._save_performance_insight(insight)
            self.performance_insights[insight.insight_id] = insight
        
        self.logger.info(f"✅ Generated {len(insights)} performance insights")
        
        return insights
    
    async def _load_historical_performance(self, days: int) -> List[Dict[str, Any]]:
        """Carga datos históricos de performance"""
        
        if DUMMY_MODE:
            # Generar datos dummy para testing
            return self._generate_dummy_historical_data(days)
        
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM performance_history 
                    WHERE timestamp > ?
                    ORDER BY timestamp DESC
                """, (cutoff_date,))
                
                rows = cursor.fetchall()
                
                historical_data = []
                for row in rows:
                    data = {
                        "record_id": row[0],
                        "variant_id": row[1],
                        "test_id": row[2],
                        "platform": row[3],
                        "metrics": json.loads(row[4]) if row[4] else {},
                        "timestamp": row[5]
                    }
                    historical_data.append(data)
                
                return historical_data
                
        except Exception as e:
            self.logger.error(f"❌ Failed to load historical data: {e}")
            return []
    
    def _generate_dummy_historical_data(self, days: int) -> List[Dict[str, Any]]:
        """Genera datos históricos dummy"""
        
        data = []
        platforms = ["tiktok", "instagram", "youtube_shorts", "meta_ads"]
        
        for day in range(days):
            date = datetime.now() - timedelta(days=day)
            
            for platform in platforms:
                for hour in [17, 18, 19, 20, 21]:  # Peak hours
                    
                    record = {
                        "record_id": f"dummy_{day}_{platform}_{hour}",
                        "variant_id": f"variant_{np.random.randint(1, 10)}",
                        "test_id": f"test_{np.random.randint(1, 5)}",
                        "platform": platform,
                        "metrics": {
                            "engagement_rate": np.random.uniform(0.02, 0.12),
                            "viral_coefficient": np.random.uniform(0.005, 0.05),
                            "completion_rate": np.random.uniform(0.6, 0.95),
                            "views": np.random.randint(1000, 20000),
                            "likes": np.random.randint(50, 1500)
                        },
                        "timestamp": date.replace(hour=hour).isoformat()
                    }
                    
                    data.append(record)
        
        return data
    
    async def _generate_timing_insight(self, historical_data: List[Dict[str, Any]]) -> Optional[PerformanceInsight]:
        """Genera insight de timing óptimo"""
        
        hour_performance = defaultdict(list)
        
        for record in historical_data:
            timestamp = datetime.fromisoformat(record["timestamp"])
            hour = timestamp.hour
            engagement = record["metrics"].get("engagement_rate", 0)
            hour_performance[hour].append(engagement)
        
        if len(hour_performance) >= 12:  # Al menos 12 horas diferentes
            hour_averages = {h: np.mean(rates) for h, rates in hour_performance.items()}
            best_hours = sorted(hour_averages.keys(), key=lambda h: hour_averages[h], reverse=True)[:3]
            
            best_hour = best_hours[0]
            best_avg = hour_averages[best_hour]
            overall_avg = np.mean([avg for avg in hour_averages.values()])
            
            if best_avg > overall_avg * 1.2:  # 20% mejor
                
                insight_id = f"timing_insight_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                return PerformanceInsight(
                    insight_id=insight_id,
                    insight_type="optimization",
                    title=f"Optimal Posting Time: {best_hour}:00",
                    description=f"Content posted at {best_hour}:00 shows {((best_avg - overall_avg) / overall_avg * 100):.1f}% higher engagement than average.",
                    recommendation=f"Schedule future content releases around {best_hour}:00 for maximum engagement.",
                    impact_level="high",
                    supporting_metrics={
                        "best_hour_engagement": best_avg,
                        "average_engagement": overall_avg,
                        "improvement_factor": best_avg / overall_avg,
                        "sample_size": len(hour_performance[best_hour])
                    },
                    confidence=min(0.9, len(hour_performance[best_hour]) / 50),
                    actionable=True,
                    implementation_effort="low",
                    expected_improvement=(best_avg - overall_avg) / overall_avg,
                    applicable_to=["all_future_content"],
                    created_at=datetime.now().isoformat()
                )
        
        return None
    
    async def _generate_platform_insight(self, historical_data: List[Dict[str, Any]]) -> Optional[PerformanceInsight]:
        """Genera insight de performance por plataforma"""
        
        platform_performance = defaultdict(list)
        
        for record in historical_data:
            platform = record["platform"]
            engagement = record["metrics"].get("engagement_rate", 0)
            viral_coeff = record["metrics"].get("viral_coefficient", 0)
            
            platform_performance[platform].append({
                "engagement": engagement,
                "viral": viral_coeff
            })
        
        if len(platform_performance) >= 2:
            platform_averages = {}
            for platform, metrics in platform_performance.items():
                avg_engagement = np.mean([m["engagement"] for m in metrics])
                avg_viral = np.mean([m["viral"] for m in metrics])
                platform_averages[platform] = {
                    "engagement": avg_engagement,
                    "viral": avg_viral,
                    "combined_score": avg_engagement * 0.7 + avg_viral * 0.3
                }
            
            best_platform = max(platform_averages.keys(), 
                              key=lambda p: platform_averages[p]["combined_score"])
            
            best_score = platform_averages[best_platform]["combined_score"]
            avg_score = np.mean([scores["combined_score"] for scores in platform_averages.values()])
            
            if best_score > avg_score * 1.15:  # 15% mejor
                
                insight_id = f"platform_insight_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                return PerformanceInsight(
                    insight_id=insight_id,
                    insight_type="optimization",
                    title=f"Top Performing Platform: {best_platform.title()}",
                    description=f"{best_platform.title()} consistently outperforms other platforms with {((best_score - avg_score) / avg_score * 100):.1f}% higher combined performance score.",
                    recommendation=f"Allocate more budget and content to {best_platform.title()} for better ROI.",
                    impact_level="high",
                    supporting_metrics={
                        "best_platform_score": best_score,
                        "average_platform_score": avg_score,
                        "platform_breakdown": platform_averages
                    },
                    confidence=0.85,
                    actionable=True,
                    implementation_effort="medium",
                    expected_improvement=(best_score - avg_score) / avg_score,
                    applicable_to=["budget_allocation", "content_strategy"],
                    created_at=datetime.now().isoformat()
                )
        
        return None
    
    async def _generate_content_insight(self, historical_data: List[Dict[str, Any]]) -> Optional[PerformanceInsight]:
        """Genera insight de patrones de contenido exitoso"""
        
        # Analizar correlación entre métricas
        high_performers = [
            record for record in historical_data
            if record["metrics"].get("engagement_rate", 0) > 0.08  # Top 8% engagement
        ]
        
        if len(high_performers) >= 10:
            avg_completion = np.mean([
                record["metrics"].get("completion_rate", 0) for record in high_performers
            ])
            
            avg_viral = np.mean([
                record["metrics"].get("viral_coefficient", 0) for record in high_performers
            ])
            
            insight_id = f"content_insight_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            return PerformanceInsight(
                insight_id=insight_id,
                insight_type="opportunity",
                title="High-Engagement Content Patterns",
                description=f"Top performing content has {avg_completion:.1%} completion rate and {avg_viral:.1%} viral coefficient.",
                recommendation="Focus on content that maintains viewer attention throughout and has shareable elements.",
                impact_level="medium",
                supporting_metrics={
                    "high_performer_completion": avg_completion,
                    "high_performer_viral": avg_viral,
                    "sample_size": len(high_performers)
                },
                confidence=0.8,
                actionable=True,
                implementation_effort="high",
                expected_improvement=0.15,
                applicable_to=["content_creation", "editing_strategy"],
                created_at=datetime.now().isoformat()
            )
        
        return None
    
    async def _generate_optimization_insights(self, historical_data: List[Dict[str, Any]]) -> List[PerformanceInsight]:
        """Genera insights de oportunidades de optimización"""
        
        insights = []
        
        # Insight: Contenido con bajo engagement
        low_performers = [
            record for record in historical_data
            if record["metrics"].get("engagement_rate", 0) < 0.03  # Below 3%
        ]
        
        if len(low_performers) > len(historical_data) * 0.3:  # Más del 30%
            
            common_platforms = defaultdict(int)
            for record in low_performers:
                common_platforms[record["platform"]] += 1
            
            worst_platform = max(common_platforms.keys(), key=lambda p: common_platforms[p])
            
            insight_id = f"optimization_low_engagement_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            warning_insight = PerformanceInsight(
                insight_id=insight_id,
                insight_type="warning",
                title="High Rate of Low-Engagement Content",
                description=f"{len(low_performers)} out of {len(historical_data)} content pieces show low engagement (<3%). {worst_platform.title()} has the most low-performers.",
                recommendation=f"Review content strategy for {worst_platform.title()} and implement engagement optimizations.",
                impact_level="critical",
                supporting_metrics={
                    "low_performer_count": len(low_performers),
                    "total_content": len(historical_data),
                    "low_performer_rate": len(low_performers) / len(historical_data),
                    "worst_platform": worst_platform
                },
                confidence=0.9,
                actionable=True,
                implementation_effort="medium",
                expected_improvement=0.25,
                applicable_to=[worst_platform, "content_review"],
                created_at=datetime.now().isoformat()
            )
            
            insights.append(warning_insight)
        
        return insights
    
    async def apply_learned_optimizations(self) -> List[ModelUpdate]:
        """
        Aplica optimizaciones aprendidas a los modelos actuales.
        
        Returns:
            Lista de actualizaciones aplicadas
        """
        
        self.logger.info("🔧 Applying learned optimizations to models")
        
        model_updates = []
        
        # Optimizar pesos de sincronización
        sync_update = await self._optimize_sync_weights()
        if sync_update:
            model_updates.append(sync_update)
        
        # Optimizar factores virales
        viral_update = await self._optimize_viral_factors()
        if viral_update:
            model_updates.append(viral_update)
        
        # Optimizar por plataforma
        platform_updates = await self._optimize_platform_factors()
        model_updates.extend(platform_updates)
        
        # Aplicar actualizaciones
        for update in model_updates:
            success = await self._apply_model_update(update)
            if success:
                update.applied_at = datetime.now().isoformat()
                await self._save_model_update(update)
                self.model_updates.append(update)
        
        self.logger.info(f"✅ Applied {len(model_updates)} model optimizations")
        
        return model_updates
    
    async def _optimize_sync_weights(self) -> Optional[ModelUpdate]:
        """Optimiza pesos de factores de sincronización"""
        
        # Buscar patrones de sincronización exitosos
        sync_patterns = [
            pattern for pattern in self.learned_patterns.values()
            if pattern.pattern_type == "variant_optimization" and
            pattern.pattern_data.get("variant_type") == "visual"
        ]
        
        if len(sync_patterns) >= 3:
            # Calcular nuevos pesos basados en patrones exitosos
            current_weights = self.current_model_weights["sync_factors"].copy()
            
            # Ajustar pesos basado en éxito de patrones
            successful_patterns = [p for p in sync_patterns if p.success_rate > 0.06]
            
            if successful_patterns:
                # Incrementar peso de factores exitosos
                new_weights = current_weights.copy()
                improvement_factor = np.mean([p.success_rate for p in successful_patterns]) / 0.05  # Baseline 5%
                
                # Ajustar pesos proporcionalmente
                if improvement_factor > 1.2:
                    new_weights["viral_potential"] *= min(1.3, improvement_factor)
                    new_weights["freshness"] *= min(1.2, improvement_factor * 0.8)
                    
                    # Renormalizar
                    total_weight = sum(new_weights.values())
                    new_weights = {k: v / total_weight for k, v in new_weights.items()}
                    
                    update_id = f"sync_weights_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    return ModelUpdate(
                        update_id=update_id,
                        model_component="sync_weights",
                        update_type="weight_adjustment",
                        old_parameters=current_weights,
                        new_parameters=new_weights,
                        expected_improvement=(improvement_factor - 1.0) * 0.1,  # Conservative estimate
                        validation_score=np.mean([p.confidence for p in successful_patterns])
                    )
        
        return None
    
    async def _optimize_viral_factors(self) -> Optional[ModelUpdate]:
        """Optimiza factores de predicción viral"""
        
        # Buscar patrones virales exitosos
        viral_patterns = [
            pattern for pattern in self.learned_patterns.values()
            if pattern.avg_viral_score > 0.03  # Above 3% viral coefficient
        ]
        
        if len(viral_patterns) >= 5:
            current_factors = self.current_model_weights["viral_factors"].copy()
            
            # Analizar qué factores correlacionan con éxito viral
            high_viral = [p for p in viral_patterns if p.avg_viral_score > 0.05]
            
            if high_viral:
                new_factors = current_factors.copy()
                
                # Incrementar peso de trend_alignment si es consistente
                if len([p for p in high_viral if "trend" in str(p.pattern_data)]) > len(high_viral) * 0.6:
                    new_factors["trend_alignment"] *= 1.2
                
                # Incrementar timing_optimization si patrones de timing son exitosos
                timing_success = len([p for p in high_viral if p.pattern_type == "timing_optimization"])
                if timing_success > 0:
                    new_factors["timing_optimization"] *= (1 + timing_success * 0.1)
                
                # Renormalizar
                total_weight = sum(new_factors.values())
                new_factors = {k: v / total_weight for k, v in new_factors.items()}
                
                update_id = f"viral_factors_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                return ModelUpdate(
                    update_id=update_id,
                    model_component="viral_prediction",
                    update_type="weight_adjustment",
                    old_parameters=current_factors,
                    new_parameters=new_factors,
                    expected_improvement=0.08,  # 8% improvement
                    validation_score=np.mean([p.confidence for p in high_viral])
                )
        
        return None
    
    async def _optimize_platform_factors(self) -> List[ModelUpdate]:
        """Optimiza factores específicos por plataforma"""
        
        updates = []
        
        platform_patterns = [
            pattern for pattern in self.learned_patterns.values()
            if pattern.pattern_type == "platform_optimization"
        ]
        
        for pattern in platform_patterns:
            platform = pattern.pattern_data.get("platform")
            if platform and platform in self.current_model_weights["platform_optimization"]:
                
                current_config = self.current_model_weights["platform_optimization"][platform].copy()
                
                # Ajustar pesos basado en métricas destacadas
                standout = pattern.pattern_data.get("standout_characteristics", {})
                new_config = current_config.copy()
                
                if "high_engagement" in standout:
                    new_config["visual_weight"] *= 1.15  # Más peso a visual
                
                if "viral_potential" in standout:
                    new_config["trend_weight"] *= 1.2   # Más peso a tendencias
                
                if "high_completion" in standout:
                    new_config["duration_weight"] *= 1.1  # Ajustar duración
                
                # Renormalizar
                total_weight = sum(new_config.values())
                new_config = {k: v / total_weight for k, v in new_config.items()}
                
                if new_config != current_config:
                    update_id = f"platform_{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    update = ModelUpdate(
                        update_id=update_id,
                        model_component=f"platform_{platform}",
                        update_type="weight_adjustment",
                        old_parameters=current_config,
                        new_parameters=new_config,
                        expected_improvement=pattern.success_rate * 0.1,
                        validation_score=pattern.confidence
                    )
                    
                    updates.append(update)
        
        return updates
    
    async def _apply_model_update(self, update: ModelUpdate) -> bool:
        """Aplica actualización de modelo"""
        
        try:
            component = update.model_component
            new_params = update.new_parameters
            
            # Aplicar según el componente
            if component == "sync_weights":
                self.current_model_weights["sync_factors"] = new_params
            elif component == "viral_prediction":
                self.current_model_weights["viral_factors"] = new_params
            elif component.startswith("platform_"):
                platform = component.split("_")[1]
                self.current_model_weights["platform_optimization"][platform] = new_params
            
            self.logger.info(f"✅ Applied model update: {update.update_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to apply model update {update.update_id}: {e}")
            return False
    
    async def _save_learning_pattern(self, pattern: LearningPattern) -> bool:
        """Guarda patrón aprendido en base de datos"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO learning_patterns (
                        pattern_id, pattern_type, pattern_data, success_rate, avg_viral_score,
                        sample_size, platforms, genres, audience_segments, optimal_times,
                        seasonal_factors, confidence, last_validated, discovered_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern.pattern_id, pattern.pattern_type, json.dumps(pattern.pattern_data),
                    pattern.success_rate, pattern.avg_viral_score, pattern.sample_size,
                    json.dumps(pattern.platforms), json.dumps(pattern.genres),
                    json.dumps(pattern.audience_segments), json.dumps(pattern.optimal_times),
                    json.dumps(pattern.seasonal_factors), pattern.confidence,
                    pattern.last_validated, pattern.discovered_at, pattern.updated_at
                ))
                conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to save learning pattern: {e}")
            return False
    
    async def _save_performance_insight(self, insight: PerformanceInsight) -> bool:
        """Guarda insight de performance en base de datos"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO performance_insights (
                        insight_id, insight_type, title, description, recommendation,
                        impact_level, supporting_metrics, confidence, actionable,
                        implementation_effort, expected_improvement, applicable_to, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    insight.insight_id, insight.insight_type, insight.title, insight.description,
                    insight.recommendation, insight.impact_level, json.dumps(insight.supporting_metrics),
                    insight.confidence, insight.actionable, insight.implementation_effort,
                    insight.expected_improvement, json.dumps(insight.applicable_to), insight.created_at
                ))
                conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to save performance insight: {e}")
            return False
    
    async def _save_model_update(self, update: ModelUpdate) -> bool:
        """Guarda actualización de modelo en base de datos"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO model_updates (
                        update_id, model_component, update_type, old_parameters,
                        new_parameters, expected_improvement, validation_score,
                        applied_at, rollback_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    update.update_id, update.model_component, update.update_type,
                    json.dumps(update.old_parameters), json.dumps(update.new_parameters),
                    update.expected_improvement, update.validation_score,
                    update.applied_at, json.dumps(update.rollback_data) if update.rollback_data else None
                ))
                conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to save model update: {e}")
            return False
    
    async def get_learning_summary(self) -> Dict[str, Any]:
        """Obtiene resumen del sistema de aprendizaje"""
        
        return {
            "learning_status": {
                "total_patterns": len(self.learned_patterns),
                "total_insights": len(self.performance_insights),
                "total_updates": len(self.model_updates),
                "last_learning_session": max([p.updated_at for p in self.learned_patterns.values()]) if self.learned_patterns else None
            },
            "pattern_breakdown": {
                pattern_type: len([p for p in self.learned_patterns.values() if p.pattern_type == pattern_type])
                for pattern_type in set(p.pattern_type for p in self.learned_patterns.values())
            },
            "insight_breakdown": {
                insight_type: len([i for i in self.performance_insights.values() if i.insight_type == insight_type])
                for insight_type in set(i.insight_type for i in self.performance_insights.values())
            },
            "model_status": {
                "current_weights": self.current_model_weights,
                "updates_applied": len([u for u in self.model_updates if u.applied_at]),
                "average_improvement": np.mean([u.expected_improvement for u in self.model_updates]) if self.model_updates else 0
            },
            "learning_config": self.learning_config,
            "generated_at": datetime.now().isoformat()
        }

# Factory function
def create_continuous_learning(database_path: str = None) -> ContinuousLearning:
    """Crea instancia de ContinuousLearning"""
    return ContinuousLearning(database_path)