"""
Meta Ads Musical Intelligence API - Endpoints inteligentes para campañas musicales
API que expone todo el sistema de inteligencia musical contextual
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import logging

from .musical_context_system import (
    MusicalGenre, PixelProfile, CampaignContext, MusicalContext,
    create_trap_pixel, create_reggaeton_pixel, create_corrido_pixel,
    musical_context_db
)
from .musical_intelligence_engine import (
    musical_intelligence, quick_campaign_analysis, CampaignInsights,
    OptimizationDecision
)
from .musical_ml_models import musical_ml_ensemble

logger = logging.getLogger(__name__)

# Pydantic models para requests
from pydantic import BaseModel

class CreatePixelRequest(BaseModel):
    pixel_id: str
    name: str
    genre: str
    theme: str
    target_countries: List[str]
    primary_audience_age: tuple[int, int] = (18, 35)

class CreateCampaignRequest(BaseModel):
    campaign_id: str
    pixel_id: str
    budget: float
    target_countries: List[str]
    target_age_range: tuple[int, int]
    target_gender: Optional[str] = None

class UpdateCampaignMetricsRequest(BaseModel):
    campaign_id: str
    current_ctr: float
    current_cpv: float
    current_watch_time: float
    impressions: int
    clicks: int
    conversions: int = 0

class OptimizationConfigRequest(BaseModel):
    scale_up_threshold: Optional[float] = None
    pause_threshold: Optional[float] = None
    viral_detection_threshold: Optional[float] = None

# Router para la API musical
musical_api = FastAPI(
    title="Meta Ads Musical Intelligence API",
    description="API inteligente para campañas musicales con ML contextual",
    version="1.0.0"
)

@musical_api.get("/")
async def root():
    """Información de la API"""
    return {
        "message": "Meta Ads Musical Intelligence API",
        "version": "1.0.0",
        "capabilities": [
            "Análisis contextual por género musical",
            "Predicciones ML especializadas",
            "Optimización automática",
            "Detección de potencial viral",
            "Insights en tiempo real"
        ],
        "supported_genres": [genre.value for genre in MusicalGenre],
        "active_campaigns": len(musical_context_db.campaigns),
        "active_pixels": len(musical_context_db.pixels)
    }

# === GESTIÓN DE PIXELS ===

@musical_api.post("/pixels/create")
async def create_pixel(request: CreatePixelRequest):
    """Crear un nuevo pixel musical con configuración inteligente"""
    
    try:
        genre = MusicalGenre(request.genre.lower())
    except ValueError:
        raise HTTPException(400, f"Género no soportado: {request.genre}")
    
    # Crear pixel según el género
    if genre == MusicalGenre.TRAP:
        pixel = create_trap_pixel(request.pixel_id, request.name, request.theme)
    elif genre == MusicalGenre.REGGAETON:
        pixel = create_reggaeton_pixel(request.pixel_id, request.name, request.theme)
    elif genre == MusicalGenre.CORRIDO:
        pixel = create_corrido_pixel(request.pixel_id, request.name, request.theme)
    else:
        # Pixel genérico para otros géneros
        pixel = PixelProfile(
            pixel_id=request.pixel_id,
            name=request.name,
            musical_context=MusicalContext(
                genre=genre,
                theme=request.theme,
                language="es"
            )
        )
    
    # Configurar países objetivo
    pixel.performance_by_country = {country: {} for country in request.target_countries}
    
    # Añadir a la base de datos
    musical_context_db.add_pixel(pixel)
    
    # Obtener expectativas del género
    expectations = musical_context_db.get_genre_expectations(
        genre, 
        request.target_countries[0] if request.target_countries else None
    )
    
    logger.info(f"Created {genre.value} pixel: {request.pixel_id}")
    
    return {
        "pixel_id": request.pixel_id,
        "genre": genre.value,
        "created_at": pixel.created_at.isoformat(),
        "genre_expectations": expectations,
        "optimization_focus": expectations.get("optimization_focus", []),
        "recommended_budget_range": f"€{pixel.optimal_budget_range[0]}-{pixel.optimal_budget_range[1]}"
    }

@musical_api.get("/pixels/{pixel_id}")
async def get_pixel_info(pixel_id: str):
    """Obtener información completa de un pixel"""
    
    if pixel_id not in musical_context_db.pixels:
        raise HTTPException(404, f"Pixel {pixel_id} not found")
    
    pixel = musical_context_db.pixels[pixel_id]
    genre = pixel.musical_context.genre
    
    # Obtener insights del modelo especializado
    model_insights = musical_ml_ensemble.get_genre_insights(genre)
    
    return {
        "pixel_info": {
            "pixel_id": pixel.pixel_id,
            "name": pixel.name,
            "genre": genre.value,
            "theme": pixel.musical_context.theme,
            "primary_audience": pixel.primary_audience.value,
            "total_campaigns": pixel.total_campaigns,
            "performance": {
                "avg_ctr": pixel.avg_ctr,
                "avg_cpv": pixel.avg_cpv,
                "avg_watch_time": pixel.avg_watch_time
            }
        },
        "genre_intelligence": model_insights,
        "status": pixel.status
    }

@musical_api.get("/pixels")
async def list_pixels():
    """Listar todos los pixels con resumen de performance"""
    
    pixels_summary = []
    
    for pixel in musical_context_db.pixels.values():
        genre_summary = musical_intelligence.get_genre_intelligence_summary(
            pixel.musical_context.genre
        )
        
        pixels_summary.append({
            "pixel_id": pixel.pixel_id,
            "name": pixel.name,
            "genre": pixel.musical_context.genre.value,
            "campaigns_count": pixel.total_campaigns,
            "avg_performance": pixel.avg_ctr,
            "status": pixel.status,
            "genre_rank": genre_summary.get("performance_metrics", {}).get("high_performer_rate", 0)
        })
    
    return {
        "total_pixels": len(pixels_summary),
        "pixels": pixels_summary,
        "genres_represented": list(set(p["genre"] for p in pixels_summary))
    }

# === GESTIÓN DE CAMPAÑAS ===

@musical_api.post("/campaigns/create")
async def create_campaign(request: CreateCampaignRequest):
    """Crear nueva campaña con análisis predictivo inicial"""
    
    if request.pixel_id not in musical_context_db.pixels:
        raise HTTPException(400, f"Pixel {request.pixel_id} not found")
    
    pixel = musical_context_db.pixels[request.pixel_id]
    
    # Crear contexto de campaña
    campaign = CampaignContext(
        campaign_id=request.campaign_id,
        pixel_profile=pixel,
        budget=request.budget,
        target_countries=request.target_countries,
        target_age_range=request.target_age_range,
        target_gender=request.target_gender
    )
    
    # Añadir a la base de datos
    musical_context_db.add_campaign(campaign)
    
    # Hacer predicción inicial
    initial_prediction = musical_ml_ensemble.predict_campaign_performance(campaign)
    
    logger.info(f"Created campaign {request.campaign_id} for {pixel.musical_context.genre.value} pixel")
    
    return {
        "campaign_id": request.campaign_id,
        "pixel_genre": pixel.musical_context.genre.value,
        "initial_prediction": {
            "predicted_ctr": initial_prediction.predicted_ctr,
            "predicted_cpv": initial_prediction.predicted_cpv,
            "confidence": initial_prediction.confidence,
            "viral_potential": initial_prediction.prob_viral_potential,
            "scale_probability": initial_prediction.prob_scale_worthy
        },
        "genre_insights": initial_prediction.genre_specific_insights,
        "optimization_recommendations": initial_prediction.optimization_suggestions,
        "created_at": campaign.started_at.isoformat()
    }

@musical_api.post("/campaigns/{campaign_id}/metrics")
async def update_campaign_metrics(campaign_id: str, request: UpdateCampaignMetricsRequest):
    """Actualizar métricas de campaña y obtener análisis inteligente"""
    
    if campaign_id not in musical_context_db.campaigns:
        raise HTTPException(404, f"Campaign {campaign_id} not found")
    
    campaign = musical_context_db.campaigns[campaign_id]
    
    # Actualizar métricas
    campaign.current_ctr = request.current_ctr
    campaign.current_cpv = request.current_cpv
    campaign.current_watch_time = request.current_watch_time
    campaign.impressions = request.impressions
    campaign.clicks = request.clicks
    campaign.conversions = request.conversions
    
    # Análisis inteligente automático
    insights = await musical_intelligence.analyze_campaign_intelligence(campaign_id)
    
    return {
        "campaign_id": campaign_id,
        "metrics_updated": True,
        "performance_analysis": {
            "performance_grade": _calculate_performance_grade(insights),
            "genre_percentile": f"{insights.genre_percentile:.1%}",
            "market_position": insights.market_position,
            "vs_pixel_history": f"{insights.pixel_performance_vs_history:.1%}"
        },
        "ml_insights": {
            "confidence": insights.ml_prediction.confidence,
            "viral_potential": insights.ml_prediction.prob_viral_potential,
            "scale_recommendation": insights.optimization_decision.decision_type,
            "key_insights": insights.ml_prediction.genre_specific_insights
        },
        "next_action": {
            "action": insights.optimization_decision.decision_type,
            "confidence": insights.optimization_decision.confidence,
            "reasoning": insights.optimization_decision.reasoning
        }
    }

@musical_api.get("/campaigns/{campaign_id}/intelligence")
async def get_campaign_intelligence(campaign_id: str):
    """Obtener análisis completo de inteligencia de campaña"""
    
    if campaign_id not in musical_context_db.campaigns:
        raise HTTPException(404, f"Campaign {campaign_id} not found")
    
    # Análisis completo
    insights = await musical_intelligence.analyze_campaign_intelligence(campaign_id)
    
    return {
        "campaign_intelligence": {
            "campaign_id": insights.campaign_id,
            "genre": insights.genre,
            "performance_grade": _calculate_performance_grade(insights),
            "market_position": insights.market_position,
            "percentile_in_genre": f"{insights.genre_percentile:.1%}",
            
            "ml_prediction": {
                "predicted_ctr": insights.ml_prediction.predicted_ctr,
                "predicted_cpv": insights.ml_prediction.predicted_cpv,
                "confidence": insights.ml_prediction.confidence,
                "viral_potential": insights.ml_prediction.prob_viral_potential,
                "scale_probability": insights.ml_prediction.prob_scale_worthy
            },
            
            "optimization": {
                "recommended_action": insights.optimization_decision.decision_type,
                "confidence": insights.optimization_decision.confidence,
                "reasoning": insights.optimization_decision.reasoning,
                "budget_multiplier": insights.optimization_decision.budget_multiplier,
                "execute_at": insights.optimization_decision.execute_at.isoformat()
            },
            
            "opportunities": {
                "scaling": insights.scaling_opportunity,
                "viral": insights.viral_potential,
                "audience_expansion": insights.audience_expansion
            },
            
            "genre_insights": insights.ml_prediction.genre_specific_insights,
            "optimization_suggestions": insights.ml_prediction.optimization_suggestions
        },
        "generated_at": insights.generated_at.isoformat()
    }

@musical_api.post("/campaigns/{campaign_id}/optimize")
async def execute_optimization(campaign_id: str, background_tasks: BackgroundTasks):
    """Ejecutar optimización automática de campaña"""
    
    if campaign_id not in musical_context_db.campaigns:
        raise HTTPException(404, f"Campaign {campaign_id} not found")
    
    # Obtener decisión de optimización
    insights = await musical_intelligence.analyze_campaign_intelligence(campaign_id)
    decision = insights.optimization_decision
    
    # Ejecutar en background
    background_tasks.add_task(
        musical_intelligence.execute_optimization_decision,
        decision
    )
    
    return {
        "optimization_initiated": True,
        "action": decision.decision_type,
        "confidence": decision.confidence,
        "reasoning": decision.reasoning,
        "expected_improvement": decision.expected_improvement,
        "execution_time": decision.execute_at.isoformat(),
        "review_time": decision.review_at.isoformat()
    }

# === ANÁLISIS POR GÉNERO ===

@musical_api.get("/genres/{genre}/intelligence")
async def get_genre_intelligence(genre: str):
    """Obtener inteligencia completa de un género musical"""
    
    try:
        musical_genre = MusicalGenre(genre.lower())
    except ValueError:
        raise HTTPException(400, f"Género no soportado: {genre}")
    
    intelligence_summary = musical_intelligence.get_genre_intelligence_summary(musical_genre)
    
    return {
        "genre_intelligence": intelligence_summary,
        "market_insights": {
            "total_campaigns": intelligence_summary.get("total_campaigns", 0),
            "average_performance": intelligence_summary.get("performance_metrics", {}),
            "optimization_opportunities": intelligence_summary.get("optimization_opportunities", 0)
        },
        "model_status": intelligence_summary.get("model_status", {}),
        "generated_at": datetime.now().isoformat()
    }

@musical_api.get("/genres/comparison")
async def compare_genres():
    """Comparación de performance entre géneros"""
    
    genre_comparison = {}
    
    for genre in MusicalGenre:
        if any(p.musical_context.genre == genre for p in musical_context_db.pixels.values()):
            summary = musical_intelligence.get_genre_intelligence_summary(genre)
            
            genre_comparison[genre.value] = {
                "campaigns_count": summary.get("total_campaigns", 0),
                "avg_performance": summary.get("performance_metrics", {}).get("avg_ctr", 0),
                "high_performer_rate": summary.get("performance_metrics", {}).get("high_performer_rate", 0),
                "model_trained": summary.get("model_status", {}).get("is_trained", False)
            }
    
    # Ranking por performance
    ranked_genres = sorted(
        genre_comparison.items(),
        key=lambda x: x[1]["avg_performance"],
        reverse=True
    )
    
    return {
        "genre_comparison": genre_comparison,
        "performance_ranking": [{"genre": genre, "avg_ctr": data["avg_performance"]} for genre, data in ranked_genres],
        "best_performing_genre": ranked_genres[0][0] if ranked_genres else None,
        "total_genres_active": len(genre_comparison)
    }

# === DASHBOARD Y REPORTING ===

@musical_api.get("/dashboard/summary")
async def get_dashboard_summary():
    """Resumen ejecutivo para dashboard"""
    
    total_campaigns = len(musical_context_db.campaigns)
    total_pixels = len(musical_context_db.pixels)
    
    # Campañas activas con buen rendimiento
    high_performing_campaigns = []
    viral_candidates = []
    optimization_needed = []
    
    for campaign_id in musical_context_db.campaigns.keys():
        quick_analysis = await quick_campaign_analysis(campaign_id)
        
        if quick_analysis.get("performance_grade", "F") in ["A+", "A"]:
            high_performing_campaigns.append(quick_analysis)
        
        if quick_analysis.get("viral_potential", False):
            viral_candidates.append(quick_analysis)
            
        if quick_analysis.get("recommended_action") in ["pause", "modify_targeting"]:
            optimization_needed.append(quick_analysis)
    
    return {
        "summary": {
            "total_campaigns": total_campaigns,
            "total_pixels": total_pixels,
            "high_performing_campaigns": len(high_performing_campaigns),
            "viral_candidates": len(viral_candidates),
            "campaigns_needing_optimization": len(optimization_needed)
        },
        "top_performers": high_performing_campaigns[:5],
        "viral_opportunities": viral_candidates[:3],
        "optimization_alerts": optimization_needed[:5],
        "genre_distribution": {
            genre.value: len([
                p for p in musical_context_db.pixels.values() 
                if p.musical_context.genre == genre
            ]) for genre in MusicalGenre
        },
        "generated_at": datetime.now().isoformat()
    }

@musical_api.get("/campaigns")
async def list_campaigns():
    """Listar todas las campañas con análisis rápido"""
    
    campaigns_list = []
    
    for campaign_id in musical_context_db.campaigns.keys():
        analysis = await quick_campaign_analysis(campaign_id)
        campaigns_list.append(analysis)
    
    return {
        "total_campaigns": len(campaigns_list),
        "campaigns": sorted(campaigns_list, key=lambda x: x.get("confidence", 0), reverse=True)
    }

# === CONFIGURACIÓN ===

@musical_api.post("/config/optimization")
async def update_optimization_config(request: OptimizationConfigRequest):
    """Actualizar configuración de optimización"""
    
    if request.scale_up_threshold is not None:
        musical_intelligence.scale_up_threshold = request.scale_up_threshold
    
    if request.pause_threshold is not None:
        musical_intelligence.pause_threshold = request.pause_threshold
        
    if request.viral_detection_threshold is not None:
        musical_intelligence.viral_detection_threshold = request.viral_detection_threshold
    
    return {
        "config_updated": True,
        "current_config": {
            "scale_up_threshold": musical_intelligence.scale_up_threshold,
            "pause_threshold": musical_intelligence.pause_threshold,
            "viral_detection_threshold": musical_intelligence.viral_detection_threshold
        }
    }

# Función helper para calcular grade
def _calculate_performance_grade(insights: CampaignInsights) -> str:
    """Calcular nota de performance"""
    from .musical_intelligence_engine import _calculate_performance_grade as calc_grade
    return calc_grade(insights)

# Endpoint de health check
@musical_api.get("/health")
async def health_check():
    """Health check de la API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "musical_context_db": len(musical_context_db.campaigns) > 0 or len(musical_context_db.pixels) > 0,
            "ml_ensemble": len(musical_ml_ensemble.models) > 0,
            "intelligence_engine": True
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(musical_api, host="0.0.0.0", port=8000)