"""
🚀 API ENDPOINTS PARA EXTENSIONES AVANZADAS

FastAPI endpoints para integrar las tres extensiones con el sistema:
- /sentiment/analyze - Análisis de sentimientos de videos
- /trends/mine - Detección de tendencias culturales
- /growth/simulate - Simulación de crecimiento y ROI
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio
import logging

from ml_core.extensions import (
    FeedbackSentimentEngine,
    CulturalTrendMiner, 
    NetworkGrowthSimulator,
    create_sentiment_engine,
    create_trend_miner,
    create_growth_simulator
)
from ml_core.extensions.growth_simulator import (
    SimulationScenario,
    Platform,
    CampaignObjective
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/extensions", tags=["Advanced Extensions"])

# Global instances (initialized on startup)
sentiment_engine: Optional[FeedbackSentimentEngine] = None
trend_miner: Optional[CulturalTrendMiner] = None
growth_simulator: Optional[NetworkGrowthSimulator] = None

# === PYDANTIC MODELS ===

class SentimentAnalysisRequest(BaseModel):
    video_id: str = Field(..., description="ID del video a analizar")
    platform: str = Field("youtube", description="Plataforma (youtube, tiktok, instagram)")
    max_comments: int = Field(500, ge=50, le=2000, description="Máximo comentarios a analizar")

class SentimentAnalysisResponse(BaseModel):
    video_id: str
    platform: str
    total_comments: int
    organic_comments: int
    sentiment_distribution: Dict[str, float]
    emotion_distribution: Dict[str, float] 
    dominant_topics: List[tuple]
    top_keywords: List[tuple]
    engagement_sentiment_correlation: float
    recommendation: str
    analyzed_at: datetime

class TrendMiningRequest(BaseModel):
    platforms: List[str] = Field(["tiktok", "youtube", "spotify"], description="Plataformas a analizar")
    artist_profile: Optional[Dict[str, Any]] = Field(None, description="Perfil del artista para relevancia")
    max_trends_per_platform: int = Field(50, ge=10, le=200)

class TrendMiningResponse(BaseModel):
    timestamp: datetime
    trends_by_platform: Dict[str, int]
    merged_trends_count: int
    top_emerging_trends: List[Dict[str, Any]]
    artist_relevant_trends: List[Dict[str, Any]]
    mining_stats: Dict[str, Any]

class GrowthSimulationRequest(BaseModel):
    scenarios: List[Dict[str, Any]] = Field(..., description="Escenarios a simular")
    optimization: bool = Field(False, description="Aplicar optimización Q-Learning")
    compare_platforms: bool = Field(False, description="Comparar entre plataformas")

class GrowthSimulationResponse(BaseModel):
    simulation_results: List[Dict[str, Any]]
    optimization_recommendation: Optional[Dict[str, Any]]
    platform_comparison: Optional[Dict[str, Any]]
    campaign_report: Dict[str, Any]
    computed_at: datetime

# === STARTUP/SHUTDOWN ===

async def initialize_extensions():
    """Inicializa las tres extensiones"""
    global sentiment_engine, trend_miner, growth_simulator
    
    logger.info("🚀 Inicializando extensiones avanzadas...")
    
    try:
        # Initialize Sentiment Engine
        sentiment_engine = create_sentiment_engine()
        await sentiment_engine.initialize()
        logger.info("✅ Feedback Sentiment Engine inicializado")
        
        # Initialize Trend Miner
        trend_miner = create_trend_miner()
        await trend_miner.initialize()
        logger.info("✅ Cultural Trend Miner inicializado")
        
        # Initialize Growth Simulator
        growth_simulator = create_growth_simulator()
        await growth_simulator.initialize()
        logger.info("✅ Network Growth Simulator inicializado")
        
        logger.info("🎯 Todas las extensiones inicializadas correctamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error inicializando extensiones: {e}")
        return False

# === SENTIMENT ANALYSIS ENDPOINTS ===

@router.post("/sentiment/analyze", response_model=SentimentAnalysisResponse)
async def analyze_video_sentiment(request: SentimentAnalysisRequest):
    """
    🧠 ANÁLISIS DE SENTIMIENTOS DE VIDEO
    
    Analiza comentarios de un video para entender recepción del público:
    - Extrae comentarios de la plataforma especificada
    - Análisis de sentimientos con DistilBERT
    - Detección emocional avanzada
    - Topic modeling con BERTopic
    - Recomendaciones actionables
    """
    if not sentiment_engine:
        raise HTTPException(status_code=503, detail="Sentiment Engine no inicializado")
    
    try:
        logger.info(f"🔍 Analizando sentimientos: {request.platform} video {request.video_id}")
        
        # Ejecutar análisis
        summary = await sentiment_engine.analyze_video_feedback(
            video_id=request.video_id,
            platform=request.platform,
            max_comments=request.max_comments
        )
        
        if not summary:
            raise HTTPException(status_code=404, detail="No se pudo analizar el video")
        
        # Convertir a response model
        response = SentimentAnalysisResponse(
            video_id=summary.video_id,
            platform=summary.platform,
            total_comments=summary.total_comments,
            organic_comments=summary.organic_comments,
            sentiment_distribution=summary.sentiment_distribution,
            emotion_distribution=summary.emotion_distribution,
            dominant_topics=summary.dominant_topics,
            top_keywords=summary.top_keywords,
            engagement_sentiment_correlation=summary.engagement_sentiment_correlation,
            recommendation=summary.recommendation,
            analyzed_at=datetime.now()
        )
        
        logger.info(f"✅ Análisis completado: {summary.organic_comments} comentarios orgánicos analizados")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error en análisis de sentimientos: {e}")
        raise HTTPException(status_code=500, detail=f"Error en análisis: {str(e)}")

@router.get("/sentiment/video/{video_id}")
async def get_sentiment_history(video_id: str, platform: str = "youtube"):
    """Obtiene historial de análisis de sentimientos para un video"""
    if not sentiment_engine:
        raise HTTPException(status_code=503, detail="Sentiment Engine no disponible")
    
    try:
        # Implementar consulta a base de datos
        # Por ahora retorna respuesta básica
        return {
            "video_id": video_id,
            "platform": platform,
            "analyses_count": 0,
            "latest_analysis": None,
            "sentiment_trend": "stable"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === TREND MINING ENDPOINTS ===

@router.post("/trends/mine", response_model=TrendMiningResponse)
async def mine_cultural_trends(request: TrendMiningRequest):
    """
    🔥 DETECCIÓN DE TENDENCIAS CULTURALES
    
    Escanea múltiples plataformas para detectar microtendencias emergentes:
    - TikTok Creative Center
    - YouTube Trending
    - Spotify Charts
    - Reddit comunidades musicales
    - Análisis cross-platform
    - Filtrado por relevancia del artista
    """
    if not trend_miner:
        raise HTTPException(status_code=503, detail="Trend Miner no inicializado")
    
    try:
        logger.info(f"⛏️ Minando tendencias en plataformas: {request.platforms}")
        
        # Ejecutar minería diaria completa
        mining_result = await trend_miner.mine_daily_trends()
        
        # Obtener tendencias relevantes para el artista si se proporciona perfil
        artist_relevant_trends = []
        if request.artist_profile:
            relevant_trends = await trend_miner.get_artist_relevant_trends(
                artist_profile=request.artist_profile,
                max_trends=20
            )
            artist_relevant_trends = [
                {
                    "keyword": trend.keyword,
                    "platform": trend.platform,
                    "growth_rate": trend.growth_rate,
                    "phase": trend.phase.value,
                    "confidence_score": trend.confidence_score,
                    "estimated_peak_date": trend.estimated_peak_date,
                    "related_keywords": trend.related_keywords
                }
                for trend in relevant_trends
            ]
        
        # Formatear top emerging trends
        top_emerging = [
            {
                "keyword": trend.keyword,
                "platform": trend.platform,
                "growth_rate": trend.growth_rate,
                "phase": trend.phase.value,
                "mentions_count": trend.mentions_count,
                "confidence_score": trend.confidence_score
            }
            for trend in mining_result.get('top_emerging', [])[:10]
        ]
        
        response = TrendMiningResponse(
            timestamp=mining_result['timestamp'],
            trends_by_platform=mining_result['trends_by_platform'],
            merged_trends_count=mining_result['merged_trends_count'],
            top_emerging_trends=top_emerging,
            artist_relevant_trends=artist_relevant_trends,
            mining_stats=mining_result['stats']
        )
        
        logger.info(f"✅ Minería completada: {mining_result['merged_trends_count']} tendencias detectadas")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error en minería de tendencias: {e}")
        raise HTTPException(status_code=500, detail=f"Error en minería: {str(e)}")

@router.get("/trends/keywords/trending")
async def get_trending_keywords(limit: int = 20, phase: Optional[str] = None):
    """Obtiene keywords más trending del momento"""
    if not trend_miner:
        raise HTTPException(status_code=503, detail="Trend Miner no disponible")
    
    try:
        from ml_core.extensions.trend_miner import TrendPhase
        
        phase_filter = None
        if phase:
            try:
                phase_filter = TrendPhase(phase)
            except ValueError:
                raise HTTPException(status_code=400, detail="Fase inválida")
        
        trends = await trend_miner.storage.get_trending_keywords(
            limit=limit,
            phase_filter=phase_filter
        )
        
        trending_keywords = [
            {
                "keyword": trend.keyword,
                "platform": trend.platform,
                "growth_rate": trend.growth_rate,
                "phase": trend.phase.value,
                "confidence": trend.confidence_score,
                "detected_at": trend.detected_at
            }
            for trend in trends
        ]
        
        return {
            "keywords": trending_keywords,
            "total_count": len(trending_keywords),
            "filters_applied": {"phase": phase, "limit": limit}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === GROWTH SIMULATION ENDPOINTS ===

@router.post("/growth/simulate", response_model=GrowthSimulationResponse)
async def simulate_growth_scenarios(request: GrowthSimulationRequest):
    """
    📈 SIMULACIÓN DE CRECIMIENTO DE RED
    
    Simula múltiples escenarios de campaña usando Monte Carlo y Q-Learning:
    - Predicción de ROI por plataforma y timing
    - Análisis de riesgo con intervalos de confianza
    - Optimización automática con reinforcement learning
    - Comparativa entre plataformas
    - Recomendaciones de inversión
    """
    if not growth_simulator:
        raise HTTPException(status_code=503, detail="Growth Simulator no inicializado")
    
    try:
        logger.info(f"🎲 Simulando {len(request.scenarios)} escenarios de crecimiento")
        
        # Convertir scenarios dict a objetos SimulationScenario
        scenarios = []
        for i, scenario_dict in enumerate(request.scenarios):
            try:
                scenario = SimulationScenario(
                    scenario_id=scenario_dict.get('scenario_id', f'scenario_{i}'),
                    budget_eur=float(scenario_dict['budget_eur']),
                    platform=Platform(scenario_dict['platform']),
                    objective=CampaignObjective(scenario_dict.get('objective', 'views')),
                    duration_days=int(scenario_dict.get('duration_days', 7)),
                    content_type=scenario_dict.get('content_type', 'video'),
                    timing=scenario_dict.get('timing', {'day_of_week': 5, 'hour': 20})
                )
                scenarios.append(scenario)
            except Exception as e:
                logger.warning(f"Error procesando escenario {i}: {e}")
                continue
        
        if not scenarios:
            raise HTTPException(status_code=400, detail="No se pudieron procesar los escenarios")
        
        # Ejecutar simulaciones
        simulation_results = await growth_simulator.simulate_campaign_scenarios(scenarios)
        
        # Formatear resultados
        formatted_results = []
        for result in simulation_results:
            formatted_results.append({
                "scenario_id": result.scenario.scenario_id,
                "platform": result.scenario.platform.value,
                "budget_eur": result.scenario.budget_eur,
                "predicted_roi_percentage": result.predicted_roi_percentage,
                "predicted_views": result.predicted_views,
                "predicted_followers": result.predicted_followers,
                "roi_confidence_interval": [result.roi_ci_lower, result.roi_ci_upper],
                "probability_positive_roi": result.probability_positive_roi,
                "simulation_confidence": result.simulation_confidence,
                "break_even_days": result.break_even_point_days
            })
        
        # Optimización opcional
        optimization_recommendation = None
        if request.optimization and scenarios:
            try:
                opt_result = await growth_simulator.optimize_campaign_strategy(scenarios[0])
                if opt_result:
                    optimization_recommendation = {
                        "action_type": opt_result.action_type,
                        "expected_improvement": opt_result.expected_improvement,
                        "confidence_score": opt_result.confidence_score,
                        "reasoning": opt_result.reasoning,
                        "optimized_scenario": {
                            "platform": opt_result.scenario.platform.value,
                            "budget_eur": opt_result.scenario.budget_eur,
                            "predicted_roi": opt_result.predicted_result.predicted_roi_percentage
                        }
                    }
            except Exception as e:
                logger.warning(f"Error en optimización: {e}")
        
        # Comparación de plataformas opcional
        platform_comparison = None
        if request.compare_platforms and scenarios:
            try:
                comparison_results = await growth_simulator.compare_platform_strategies(scenarios[0])
                platform_comparison = {
                    platform.value: {
                        "predicted_roi": result.predicted_roi_percentage,
                        "predicted_views": result.predicted_views,
                        "confidence": result.simulation_confidence
                    }
                    for platform, result in comparison_results.items()
                }
            except Exception as e:
                logger.warning(f"Error en comparación: {e}")
        
        # Generar reporte
        campaign_report = growth_simulator.generate_campaign_report(simulation_results)
        
        response = GrowthSimulationResponse(
            simulation_results=formatted_results,
            optimization_recommendation=optimization_recommendation,
            platform_comparison=platform_comparison,
            campaign_report=campaign_report,
            computed_at=datetime.now()
        )
        
        logger.info(f"✅ Simulación completada: {len(formatted_results)} resultados generados")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error en simulación de crecimiento: {e}")
        raise HTTPException(status_code=500, detail=f"Error en simulación: {str(e)}")

@router.post("/growth/optimize-budget")
async def optimize_budget_allocation(
    total_budget: float = Field(..., gt=0, description="Presupuesto total a distribuir"),
    platforms: List[str] = Field(..., description="Plataformas para optimizar")
):
    """Optimiza distribución de presupuesto entre plataformas"""
    if not growth_simulator:
        raise HTTPException(status_code=503, detail="Growth Simulator no disponible")
    
    try:
        # Convertir strings a Platform enums
        platform_enums = []
        for platform_str in platforms:
            try:
                platform_enums.append(Platform(platform_str))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Plataforma inválida: {platform_str}")
        
        # Ejecutar optimización
        optimal_allocation = await growth_simulator.find_optimal_budget_allocation(
            total_budget=total_budget,
            platforms=platform_enums
        )
        
        # Formatear respuesta
        allocation_result = {
            platform.value: allocation
            for platform, allocation in optimal_allocation.items()
        }
        
        return {
            "total_budget": total_budget,
            "optimal_allocation": allocation_result,
            "efficiency_scores": {
                # Calculado internamente pero no expuesto en esta versión
            },
            "recommendation": f"Distribuir presupuesto priorizando {max(allocation_result.items(), key=lambda x: x[1])[0]}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === STATUS Y HEALTH ENDPOINTS ===

@router.get("/status")
async def get_extensions_status():
    """Estado de las extensiones avanzadas"""
    return {
        "sentiment_engine": sentiment_engine is not None,
        "trend_miner": trend_miner is not None,
        "growth_simulator": growth_simulator is not None,
        "all_initialized": all([sentiment_engine, trend_miner, growth_simulator]),
        "timestamp": datetime.now()
    }

@router.post("/initialize")
async def initialize_extensions_endpoint(background_tasks: BackgroundTasks):
    """Inicializa extensiones en background"""
    background_tasks.add_task(initialize_extensions)
    return {"message": "Inicialización de extensiones iniciada en background"}

# === UTILITY ENDPOINTS ===

@router.get("/platforms")
async def get_supported_platforms():
    """Lista plataformas soportadas"""
    return {
        "platforms": [platform.value for platform in Platform],
        "campaign_objectives": [obj.value for obj in CampaignObjective]
    }

# Export router
extensions_router = router