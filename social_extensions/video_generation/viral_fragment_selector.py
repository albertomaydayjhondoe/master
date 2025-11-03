"""
Viral Fragment Selector - Módulo 7
Selector inteligente de fragmentos con máximo potencial viral usando ML.

Integra con:
- Histórico de performance para aprendizaje
- ML Core para predicción viral
- Tendencias de plataformas
- Database para storage de performance
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

# Importar componentes del módulo
from .semantic_synchronizer import SyncMatch, SemanticSynchronizer
from .visual_clip_database import VisualClip

# Integración con ML Core
try:
    from ml_core.models.factory import get_yolo_video_detector
    from ml_core.api.main import ml_app
    ML_CORE_AVAILABLE = True
except ImportError:
    ML_CORE_AVAILABLE = False

try:
    from config.app_settings import is_dummy_mode
    DUMMY_MODE = is_dummy_mode()
except ImportError:
    DUMMY_MODE = True

logger = logging.getLogger(__name__)

@dataclass
class ViralPrediction:
    """Predicción de potencial viral"""
    fragment_id: str
    viral_score: float                    # Score principal 0-1
    confidence: float                     # Confianza de la predicción
    
    # Factores específicos
    trend_alignment: float                # Alineación con tendencias actuales
    platform_optimization: Dict[str, float]  # Optimización por plataforma
    timing_score: float                   # Score de timing óptimo
    engagement_prediction: Dict[str, float]   # Predicción de engagement
    
    # Análisis detallado
    viral_elements: List[str]             # Elementos que contribuyen a viral
    risk_factors: List[str]               # Factores de riesgo
    optimal_platforms: List[str]          # Plataformas óptimas
    
    # Recomendaciones
    recommended_hashtags: List[str]       # Hashtags recomendados
    optimal_posting_time: str             # Hora óptima de publicación
    target_audience: Dict[str, Any]       # Audiencia objetivo
    
    # Metadatos
    predicted_at: str
    model_version: str

@dataclass
class FragmentMetrics:
    """Métricas de performance de un fragmento"""
    fragment_id: str
    
    # Engagement metrics
    views: int
    likes: int
    shares: int
    comments: int
    saves: int
    
    # Performance calculations
    engagement_rate: float
    viral_coefficient: float              # Views/Followers ratio
    retention_rate: float                 # Watch time / Duration
    
    # Platform specific
    platform_performance: Dict[str, Dict[str, float]]
    
    # Time analysis
    posted_at: str
    peak_engagement_time: str
    performance_window: int               # Hours to peak
    
    # Context
    hashtags_used: List[str]
    caption_analysis: Dict[str, Any]
    audience_demographics: Dict[str, Any]

@dataclass
class TrendAnalysis:
    """Análisis de tendencias actuales"""
    trend_category: str
    trend_strength: float                 # 0-1 strength
    
    # Trend details
    trending_elements: List[str]          # Audio, visual, hashtags
    trending_duration: int                # Days trending
    geographic_reach: List[str]           # Countries where trending
    
    # Platform specific
    platform_trends: Dict[str, float]    # TikTok, Instagram, etc.
    hashtag_trends: List[Dict[str, Any]]  # Trending hashtags
    
    # Predictions
    trend_lifecycle: str                  # "emerging", "peak", "declining"
    estimated_days_remaining: int
    
    updated_at: str

class ViralFragmentSelector:
    """
    Selector inteligente de fragmentos con máximo potencial viral.
    
    Usa ML, análisis de tendencias y performance histórica para predecir
    qué fragmentos tienen mayor probabilidad de volverse virales.
    """
    
    def __init__(self, database_path: str = None):
        self.database_path = database_path or "data/viral_intelligence.db"
        self.logger = logging.getLogger(f"{__name__}.ViralFragmentSelector")
        
        # Ensure database directory exists
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Integración ML
        if ML_CORE_AVAILABLE and not DUMMY_MODE:
            self.ml_detector = get_yolo_video_detector()
        else:
            self.ml_detector = None
        
        # Cache de predicciones
        self.prediction_cache: Dict[str, ViralPrediction] = {}
        self.trend_cache: Dict[str, TrendAnalysis] = {}
        
        # Configuración del modelo viral
        self.viral_factors = {
            "audio_catchiness": 0.25,         # Pegadizo del audio
            "visual_impact": 0.20,            # Impacto visual
            "trend_alignment": 0.15,          # Alineación con tendencias
            "timing_optimization": 0.15,      # Optimización temporal
            "platform_fit": 0.10,             # Ajuste a plataforma
            "novelty_factor": 0.10,           # Factor novedad
            "emotional_resonance": 0.05       # Resonancia emocional
        }
        
        # Plataformas objetivo
        self.target_platforms = ["tiktok", "instagram", "youtube_shorts", "facebook"]
        
        # Inicializar base de datos
        self._initialize_database()
        
        self.logger.info("🚀 Viral Fragment Selector initialized")
    
    def _initialize_database(self):
        """Inicializa base de datos de inteligencia viral"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                # Tabla de predicciones virales
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS viral_predictions (
                        fragment_id TEXT PRIMARY KEY,
                        viral_score REAL,
                        confidence REAL,
                        trend_alignment REAL,
                        platform_optimization TEXT,
                        timing_score REAL,
                        engagement_prediction TEXT,
                        viral_elements TEXT,
                        risk_factors TEXT,
                        optimal_platforms TEXT,
                        recommended_hashtags TEXT,
                        optimal_posting_time TEXT,
                        target_audience TEXT,
                        predicted_at TEXT,
                        model_version TEXT
                    )
                """)
                
                # Tabla de métricas de performance
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS fragment_metrics (
                        fragment_id TEXT,
                        platform TEXT,
                        views INTEGER,
                        likes INTEGER,
                        shares INTEGER,
                        comments INTEGER,
                        saves INTEGER,
                        engagement_rate REAL,
                        viral_coefficient REAL,
                        retention_rate REAL,
                        posted_at TEXT,
                        peak_engagement_time TEXT,
                        performance_window INTEGER,
                        hashtags_used TEXT,
                        caption_analysis TEXT,
                        audience_demographics TEXT,
                        recorded_at TEXT,
                        PRIMARY KEY (fragment_id, platform, recorded_at)
                    )
                """)
                
                # Tabla de análisis de tendencias
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS trend_analysis (
                        trend_category TEXT PRIMARY KEY,
                        trend_strength REAL,
                        trending_elements TEXT,
                        trending_duration INTEGER,
                        geographic_reach TEXT,
                        platform_trends TEXT,
                        hashtag_trends TEXT,
                        trend_lifecycle TEXT,
                        estimated_days_remaining INTEGER,
                        updated_at TEXT
                    )
                """)
                
                # Índices para optimización
                conn.execute("CREATE INDEX IF NOT EXISTS idx_viral_score ON viral_predictions(viral_score)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_platform_metrics ON fragment_metrics(platform)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_trend_strength ON trend_analysis(trend_strength)")
                
                conn.commit()
                
            self.logger.info("📋 Viral intelligence database initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Database initialization failed: {e}")
    
    async def predict_viral_potential(self, sync_matches: List[SyncMatch],
                                    audio_path: str = None) -> List[ViralPrediction]:
        """
        Predice potencial viral de fragmentos sincronizados.
        
        Args:
            sync_matches: Lista de matches sincronizados
            audio_path: Ruta del audio original
            
        Returns:
            Lista de predicciones ordenadas por potencial viral
        """
        self.logger.info(f"🚀 Predicting viral potential for {len(sync_matches)} fragments")
        
        predictions = []
        
        # Obtener análisis de tendencias actuales
        current_trends = await self._get_current_trends()
        
        for i, match in enumerate(sync_matches):
            fragment_id = f"fragment_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if DUMMY_MODE:
                prediction = self._generate_dummy_prediction(fragment_id, match)
            else:
                prediction = await self._perform_real_prediction(
                    fragment_id, match, current_trends, audio_path
                )
            
            predictions.append(prediction)
            
            # Cache prediction
            self.prediction_cache[fragment_id] = prediction
        
        # Ordenar por viral score
        predictions.sort(key=lambda x: x.viral_score, reverse=True)
        
        # Guardar en base de datos
        for prediction in predictions:
            await self._save_prediction(prediction)
        
        self.logger.info(f"✅ Generated {len(predictions)} viral predictions")
        
        return predictions
    
    def _generate_dummy_prediction(self, fragment_id: str, match: SyncMatch) -> ViralPrediction:
        """Genera predicción dummy para testing"""
        
        # Base viral score from sync quality
        base_score = match.sync_score * 0.7 + match.visual_clip.viral_score * 0.3
        
        # Add random variation
        viral_score = min(1.0, base_score + np.random.uniform(-0.1, 0.2))
        confidence = np.random.uniform(0.7, 0.95)
        
        # Trend alignment based on genre
        trend_alignment = np.random.uniform(0.6, 0.9)
        
        # Platform optimization
        platform_optimization = {
            "tiktok": np.random.uniform(0.7, 0.95),
            "instagram": np.random.uniform(0.6, 0.9),
            "youtube_shorts": np.random.uniform(0.5, 0.85),
            "facebook": np.random.uniform(0.4, 0.7)
        }
        
        # Timing score
        timing_score = np.random.uniform(0.6, 0.9)
        
        # Engagement prediction
        engagement_prediction = {
            "views": int(np.random.uniform(10000, 1000000)),
            "likes": int(np.random.uniform(500, 50000)),
            "shares": int(np.random.uniform(100, 10000)),
            "comments": int(np.random.uniform(50, 5000))
        }
        
        # Viral elements
        viral_elements = []
        if match.visual_clip.energy_level > 0.8:
            viral_elements.append("high_energy_visual")
        if match.sync_score > 0.8:
            viral_elements.append("perfect_audio_sync")
        if match.visual_clip.viral_score > 0.8:
            viral_elements.append("proven_visual_content")
        
        viral_elements.extend(np.random.choice([
            "catchy_hook", "trending_sound", "relatable_content",
            "visual_storytelling", "emotional_moment", "dance_element"
        ], size=np.random.randint(1, 3), replace=False).tolist())
        
        # Risk factors
        risk_factors = []
        if match.sync_score < 0.7:
            risk_factors.append("sync_quality_issues")
        if match.visual_clip.usage_count > 20:
            risk_factors.append("overused_visual")
        
        # Random additional risks
        potential_risks = ["copyright_concern", "trend_saturation", "timing_mismatch"]
        risk_factors.extend(np.random.choice(
            potential_risks, size=np.random.randint(0, 2), replace=False
        ).tolist())
        
        # Optimal platforms
        optimal_platforms = [
            platform for platform, score in platform_optimization.items()
            if score > 0.7
        ]
        
        # Recommended hashtags
        genre_hashtags = {
            "trap": ["#trap", "#music", "#viral", "#fyp"],
            "drill": ["#drill", "#urban", "#rap", "#trending"],
            "reggaeton": ["#reggaeton", "#latino", "#dance", "#viral"]
        }
        
        base_hashtags = genre_hashtags.get(match.visual_clip.genre, ["#music", "#viral"])
        recommended_hashtags = base_hashtags + ["#trending", "#foryou", "#explore"]
        
        # Optimal posting time
        posting_times = ["19:00", "20:00", "21:00", "15:00", "16:00"]
        optimal_posting_time = np.random.choice(posting_times)
        
        # Target audience
        target_audience = {
            "age_range": "18-34",
            "interests": [match.visual_clip.genre, "music", "entertainment"],
            "geographic_focus": ["US", "MX", "ES", "AR"],
            "platform_behavior": "high_engagement_evening"
        }
        
        return ViralPrediction(
            fragment_id=fragment_id,
            viral_score=viral_score,
            confidence=confidence,
            trend_alignment=trend_alignment,
            platform_optimization=platform_optimization,
            timing_score=timing_score,
            engagement_prediction=engagement_prediction,
            viral_elements=viral_elements,
            risk_factors=risk_factors,
            optimal_platforms=optimal_platforms,
            recommended_hashtags=recommended_hashtags,
            optimal_posting_time=optimal_posting_time,
            target_audience=target_audience,
            predicted_at=datetime.now().isoformat(),
            model_version="dummy_v1.0"
        )
    
    async def _perform_real_prediction(self, fragment_id: str, match: SyncMatch,
                                     trends: List[TrendAnalysis],
                                     audio_path: str = None) -> ViralPrediction:
        """Predicción real usando ML (implementación futura)"""
        
        # TODO: Implementar predicción real con:
        # - Análisis de audio con librosa/essentia
        # - Análisis visual con YOLOv8
        # - Modelo de ML entrenado en datos históricos
        # - Análisis de tendencias en tiempo real
        
        self.logger.info("🔄 Real viral prediction not implemented, using enhanced dummy")
        
        return self._generate_dummy_prediction(fragment_id, match)
    
    async def _get_current_trends(self) -> List[TrendAnalysis]:
        """Obtiene análisis de tendencias actuales"""
        
        if DUMMY_MODE:
            return self._generate_dummy_trends()
        
        try:
            # TODO: Implementar análisis real de tendencias desde:
            # - TikTok Trending API
            # - Instagram Graph API  
            # - YouTube Data API
            # - Twitter Trends API
            
            return self._generate_dummy_trends()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get current trends: {e}")
            return self._generate_dummy_trends()
    
    def _generate_dummy_trends(self) -> List[TrendAnalysis]:
        """Genera análisis de tendencias dummy"""
        
        trends = []
        
        # Tendencias de género musical
        music_trends = [
            {
                "category": "drill_latin",
                "strength": 0.9,
                "elements": ["drill_beats", "spanish_lyrics", "urban_visuals"],
                "platforms": {"tiktok": 0.95, "instagram": 0.8, "youtube_shorts": 0.7}
            },
            {
                "category": "reggaeton_fusion",
                "strength": 0.8,
                "elements": ["reggaeton_rhythm", "electronic_drops", "party_visuals"],
                "platforms": {"tiktok": 0.85, "instagram": 0.9, "youtube_shorts": 0.75}
            },
            {
                "category": "trap_melodic",
                "strength": 0.75,
                "elements": ["melodic_hooks", "trap_drums", "emotional_content"],
                "platforms": {"tiktok": 0.8, "instagram": 0.7, "youtube_shorts": 0.8}
            }
        ]
        
        for trend_data in music_trends:
            trend = TrendAnalysis(
                trend_category=trend_data["category"],
                trend_strength=trend_data["strength"],
                trending_elements=trend_data["elements"],
                trending_duration=np.random.randint(7, 30),
                geographic_reach=["US", "MX", "ES", "AR", "CO"],
                platform_trends=trend_data["platforms"],
                hashtag_trends=[
                    {"hashtag": f"#{element}", "growth": np.random.uniform(0.5, 2.0)}
                    for element in trend_data["elements"]
                ],
                trend_lifecycle="peak",
                estimated_days_remaining=np.random.randint(5, 20),
                updated_at=datetime.now().isoformat()
            )
            trends.append(trend)
        
        return trends
    
    async def select_top_viral_fragments(self, predictions: List[ViralPrediction],
                                       top_n: int = 5,
                                       platform: str = None) -> List[ViralPrediction]:
        """
        Selecciona los fragmentos con mayor potencial viral.
        
        Args:
            predictions: Lista de predicciones
            top_n: Número de fragmentos a seleccionar
            platform: Plataforma específica (opcional)
            
        Returns:
            Lista de mejores predicciones ordenadas
        """
        
        filtered_predictions = predictions.copy()
        
        # Filtrar por plataforma si se especifica
        if platform:
            filtered_predictions = [
                pred for pred in filtered_predictions
                if platform in pred.optimal_platforms or
                pred.platform_optimization.get(platform, 0) > 0.6
            ]
        
        # Filtrar por confidence mínima
        filtered_predictions = [
            pred for pred in filtered_predictions
            if pred.confidence > 0.7
        ]
        
        # Aplicar scoring avanzado
        for pred in filtered_predictions:
            # Score base
            base_score = pred.viral_score
            
            # Bonus por alta confianza
            confidence_bonus = (pred.confidence - 0.7) * 0.1
            
            # Bonus por alineación con tendencias
            trend_bonus = pred.trend_alignment * 0.05
            
            # Bonus por timing óptimo
            timing_bonus = pred.timing_score * 0.05
            
            # Penalización por factores de riesgo
            risk_penalty = len(pred.risk_factors) * 0.02
            
            # Score final ajustado
            pred.viral_score = min(1.0, base_score + confidence_bonus + 
                                 trend_bonus + timing_bonus - risk_penalty)
        
        # Ordenar por score ajustado
        filtered_predictions.sort(key=lambda x: x.viral_score, reverse=True)
        
        # Seleccionar top N
        top_fragments = filtered_predictions[:top_n]
        
        self.logger.info(f"🎯 Selected {len(top_fragments)} top viral fragments")
        
        return top_fragments
    
    async def _save_prediction(self, prediction: ViralPrediction) -> bool:
        """Guarda predicción en base de datos"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO viral_predictions (
                        fragment_id, viral_score, confidence, trend_alignment,
                        platform_optimization, timing_score, engagement_prediction,
                        viral_elements, risk_factors, optimal_platforms,
                        recommended_hashtags, optimal_posting_time, target_audience,
                        predicted_at, model_version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    prediction.fragment_id, prediction.viral_score, prediction.confidence,
                    prediction.trend_alignment, json.dumps(prediction.platform_optimization),
                    prediction.timing_score, json.dumps(prediction.engagement_prediction),
                    json.dumps(prediction.viral_elements), json.dumps(prediction.risk_factors),
                    json.dumps(prediction.optimal_platforms), json.dumps(prediction.recommended_hashtags),
                    prediction.optimal_posting_time, json.dumps(prediction.target_audience),
                    prediction.predicted_at, prediction.model_version
                ))
                conn.commit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save prediction {prediction.fragment_id}: {e}")
            return False
    
    async def record_fragment_performance(self, fragment_id: str, platform: str,
                                        metrics: FragmentMetrics) -> bool:
        """Registra performance real de un fragmento para aprendizaje"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.execute("""
                    INSERT INTO fragment_metrics (
                        fragment_id, platform, views, likes, shares, comments, saves,
                        engagement_rate, viral_coefficient, retention_rate,
                        posted_at, peak_engagement_time, performance_window,
                        hashtags_used, caption_analysis, audience_demographics,
                        recorded_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    fragment_id, platform, metrics.views, metrics.likes,
                    metrics.shares, metrics.comments, metrics.saves,
                    metrics.engagement_rate, metrics.viral_coefficient, metrics.retention_rate,
                    metrics.posted_at, metrics.peak_engagement_time, metrics.performance_window,
                    json.dumps(metrics.hashtags_used), json.dumps(metrics.caption_analysis),
                    json.dumps(metrics.audience_demographics), datetime.now().isoformat()
                ))
                conn.commit()
            
            self.logger.info(f"📊 Recorded performance for {fragment_id} on {platform}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to record performance: {e}")
            return False
    
    async def get_viral_insights(self) -> Dict[str, Any]:
        """Obtiene insights del selector viral"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                # Estadísticas de predicciones
                cursor = conn.execute("""
                    SELECT AVG(viral_score), AVG(confidence), COUNT(*)
                    FROM viral_predictions
                """)
                avg_viral, avg_confidence, total_predictions = cursor.fetchone()
                
                # Top elementos virales
                cursor = conn.execute("""
                    SELECT viral_elements FROM viral_predictions
                    WHERE viral_score > 0.8
                """)
                
                all_elements = []
                for (elements_json,) in cursor.fetchall():
                    if elements_json:
                        elements = json.loads(elements_json)
                        all_elements.extend(elements)
                
                element_counts = {}
                for element in all_elements:
                    element_counts[element] = element_counts.get(element, 0) + 1
                
                # Performance actual si existe
                cursor = conn.execute("""
                    SELECT platform, AVG(viral_coefficient), AVG(engagement_rate)
                    FROM fragment_metrics
                    GROUP BY platform
                """)
                platform_performance = {
                    platform: {"viral_coefficient": viral_coef, "engagement_rate": eng_rate}
                    for platform, viral_coef, eng_rate in cursor.fetchall()
                }
                
                return {
                    "total_predictions": total_predictions or 0,
                    "avg_viral_score": round(avg_viral or 0, 3),
                    "avg_confidence": round(avg_confidence or 0, 3),
                    "top_viral_elements": dict(sorted(element_counts.items(), 
                                                    key=lambda x: x[1], reverse=True)[:10]),
                    "platform_performance": platform_performance,
                    "analysis_timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get viral insights: {e}")
            return {}

# Factory function
def create_viral_fragment_selector(database_path: str = None) -> ViralFragmentSelector:
    """Crea instancia de ViralFragmentSelector"""
    return ViralFragmentSelector(database_path)