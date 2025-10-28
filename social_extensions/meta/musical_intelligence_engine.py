"""
Meta Ads Musical Intelligence System - Sistema de Predicción Contextual
Integra modelos ML especializados con contexto musical para optimización automática
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from .musical_context_system import (
    MusicalGenre, PixelProfile, CampaignContext, MusicalContext,
    musical_context_db, create_trap_pixel, create_reggaeton_pixel, create_corrido_pixel
)
from .musical_ml_models import (
    MusicalMLEnsemble, MLPrediction, musical_ml_ensemble
)

logger = logging.getLogger(__name__)

@dataclass
class OptimizationDecision:
    """Decisión de optimización automática"""
    campaign_id: str
    decision_type: str  # "scale_up", "scale_down", "pause", "modify_targeting", "creative_refresh"
    confidence: float
    reasoning: List[str]
    
    # Acciones específicas
    budget_multiplier: Optional[float] = None
    new_targeting_suggestions: Optional[Dict[str, Any]] = None
    creative_modifications: Optional[Dict[str, Any]] = None
    
    # Timeline
    execute_at: datetime
    review_at: datetime
    
    # Resultados esperados
    expected_improvement: Dict[str, float]

@dataclass
class CampaignInsights:
    """Insights completos de una campaña musical"""
    campaign_id: str
    genre: str
    
    # Performance actual vs esperado
    performance_analysis: Dict[str, Any]
    ml_prediction: MLPrediction
    optimization_decision: OptimizationDecision
    
    # Comparaciones contextuales
    genre_percentile: float  # Percentil dentro del género
    pixel_performance_vs_history: float
    market_position: str  # "leading", "average", "lagging"
    
    # Oportunidades detectadas
    scaling_opportunity: Optional[Dict[str, Any]]
    viral_potential: Optional[Dict[str, Any]]
    audience_expansion: Optional[Dict[str, Any]]
    
    generated_at: datetime

class MusicalIntelligenceEngine:
    """Motor de inteligencia musical para Meta Ads"""
    
    def __init__(self):
        self.ml_ensemble = musical_ml_ensemble
        self.context_db = musical_context_db
        self.optimization_history: List[OptimizationDecision] = []
        
        # Thresholds configurables
        self.scale_up_threshold = 0.8  # Confidence para escalar
        self.pause_threshold = 0.3     # Confidence para pausar
        self.viral_detection_threshold = 0.7
        
    async def analyze_campaign_intelligence(self, campaign_id: str) -> CampaignInsights:
        """Análisis completo de inteligencia de campaña"""
        
        if campaign_id not in self.context_db.campaigns:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        campaign = self.context_db.campaigns[campaign_id]
        
        # 1. Predicción ML especializada
        ml_prediction = self.ml_ensemble.predict_campaign_performance(campaign)
        
        # 2. Análisis de contexto
        performance_analysis = self.context_db.analyze_campaign_context(campaign_id)
        
        # 3. Decisión de optimización
        optimization_decision = await self._generate_optimization_decision(campaign, ml_prediction)
        
        # 4. Análisis comparativo
        genre_percentile = await self._calculate_genre_percentile(campaign)
        pixel_vs_history = self._calculate_pixel_performance_vs_history(campaign)
        market_position = self._determine_market_position(campaign, ml_prediction)
        
        # 5. Detectar oportunidades
        opportunities = await self._detect_opportunities(campaign, ml_prediction)
        
        insights = CampaignInsights(
            campaign_id=campaign_id,
            genre=campaign.pixel_profile.musical_context.genre.value,
            performance_analysis=performance_analysis,
            ml_prediction=ml_prediction,
            optimization_decision=optimization_decision,
            genre_percentile=genre_percentile,
            pixel_performance_vs_history=pixel_vs_history,
            market_position=market_position,
            scaling_opportunity=opportunities.get("scaling"),
            viral_potential=opportunities.get("viral"),
            audience_expansion=opportunities.get("audience"),
            generated_at=datetime.now()
        )
        
        logger.info(f"Generated comprehensive insights for campaign {campaign_id}")
        return insights
    
    async def _generate_optimization_decision(
        self, 
        campaign: CampaignContext, 
        ml_prediction: MLPrediction
    ) -> OptimizationDecision:
        """Generar decisión de optimización automática"""
        
        decision_type = "maintain"
        confidence = 0.5
        reasoning = []
        budget_multiplier = 1.0
        expected_improvement = {}
        
        # Lógica de decisión basada en ML + contexto
        if ml_prediction.prob_scale_worthy > self.scale_up_threshold:
            decision_type = "scale_up"
            confidence = ml_prediction.prob_scale_worthy
            budget_multiplier = min(2.0, 1 + ml_prediction.confidence)
            reasoning.append(f"Alta probabilidad de éxito al escalar ({ml_prediction.prob_scale_worthy:.2%})")
            reasoning.append(f"CTR predicho: {ml_prediction.predicted_ctr:.3f}")
            expected_improvement = {
                "reach_increase": 0.5 * budget_multiplier,
                "conversion_increase": 0.3 * budget_multiplier
            }
            
        elif ml_prediction.confidence < self.pause_threshold:
            decision_type = "pause"
            confidence = 1 - ml_prediction.confidence
            budget_multiplier = 0.0
            reasoning.append(f"Baja confianza en performance ({ml_prediction.confidence:.2%})")
            reasoning.append("Recomendado pausar y revisar estrategia")
            expected_improvement = {
                "cost_saving": campaign.budget * 0.8,
                "opportunity_cost_avoided": campaign.budget * 0.3
            }
            
        elif ml_prediction.predicted_ctr < campaign.pixel_profile.avg_ctr * 0.7:
            decision_type = "modify_targeting"
            confidence = 0.7
            reasoning.append("Performance por debajo del historial del pixel")
            reasoning.append("Targeting necesita optimización")
            expected_improvement = {
                "ctr_improvement": 0.25,
                "cpv_improvement": -0.15
            }
            
        elif ml_prediction.prob_viral_potential > self.viral_detection_threshold:
            decision_type = "scale_up"
            confidence = ml_prediction.prob_viral_potential
            budget_multiplier = 2.5  # Escalar agresivamente para contenido viral
            reasoning.append(f"¡POTENCIAL VIRAL DETECTADO! ({ml_prediction.prob_viral_potential:.2%})")
            reasoning.append("Escalar agresivamente para capitalizar momento viral")
            expected_improvement = {
                "viral_reach_multiplier": 5.0,
                "brand_awareness_boost": 3.0
            }
        
        # Timing de ejecución
        execute_at = datetime.now() + timedelta(minutes=15)  # Dar tiempo para revisión
        review_at = execute_at + timedelta(hours=6)  # Revisar resultados
        
        return OptimizationDecision(
            campaign_id=campaign.campaign_id,
            decision_type=decision_type,
            confidence=confidence,
            reasoning=reasoning,
            budget_multiplier=budget_multiplier,
            execute_at=execute_at,
            review_at=review_at,
            expected_improvement=expected_improvement
        )
    
    async def _calculate_genre_percentile(self, campaign: CampaignContext) -> float:
        """Calcular percentil de performance dentro del género"""
        genre = campaign.pixel_profile.musical_context.genre
        
        # Obtener todas las campañas del mismo género
        genre_campaigns = [
            c for c in self.context_db.campaigns.values() 
            if c.pixel_profile.musical_context.genre == genre and c.current_ctr > 0
        ]
        
        if len(genre_campaigns) < 3:
            return 0.5  # No hay suficientes datos
        
        # Calcular percentil basado en CTR
        ctr_values = sorted([c.current_ctr for c in genre_campaigns])
        
        if campaign.current_ctr <= 0:
            return 0.1  # Performance muy baja
        
        # Encontrar posición
        position = len([ctr for ctr in ctr_values if ctr <= campaign.current_ctr])
        percentile = position / len(ctr_values)
        
        return percentile
    
    def _calculate_pixel_performance_vs_history(self, campaign: CampaignContext) -> float:
        """Performance vs historial del pixel"""
        pixel = campaign.pixel_profile
        
        if pixel.avg_ctr <= 0 or campaign.current_ctr <= 0:
            return 0.5
        
        ratio = campaign.current_ctr / pixel.avg_ctr
        
        # Normalizar a escala 0-1
        if ratio >= 2.0:
            return 1.0  # Excepcional
        elif ratio >= 1.5:
            return 0.8  # Muy bueno
        elif ratio >= 1.0:
            return 0.6  # Bueno
        elif ratio >= 0.8:
            return 0.4  # Regular
        else:
            return 0.2  # Malo
    
    def _determine_market_position(self, campaign: CampaignContext, prediction: MLPrediction) -> str:
        """Determinar posición en el mercado"""
        
        if prediction.prob_high_performance > 0.8 and campaign.current_ctr > 0.025:
            return "leading"
        elif prediction.prob_high_performance > 0.5 and campaign.current_ctr > 0.015:
            return "average"
        else:
            return "lagging"
    
    async def _detect_opportunities(
        self, 
        campaign: CampaignContext, 
        prediction: MLPrediction
    ) -> Dict[str, Any]:
        """Detectar oportunidades específicas"""
        opportunities = {}
        
        # Oportunidad de escalado
        if prediction.prob_scale_worthy > 0.6:
            opportunities["scaling"] = {
                "type": "budget_scaling",
                "confidence": prediction.prob_scale_worthy,
                "recommended_multiplier": min(3.0, 1 + prediction.confidence * 2),
                "reasoning": "Alta probabilidad de éxito al escalar presupuesto",
                "estimated_roi_increase": prediction.prob_scale_worthy * 0.8
            }
        
        # Potencial viral
        if prediction.prob_viral_potential > 0.5:
            opportunities["viral"] = {
                "type": "viral_content",
                "confidence": prediction.prob_viral_potential,
                "actions": [
                    "Escalar presupuesto agresivamente",
                    "Expandir a audiencias similares",
                    "Crear variaciones de la creatividad",
                    "Activar notificaciones en tiempo real"
                ],
                "estimated_reach_multiplier": prediction.prob_viral_potential * 10
            }
        
        # Expansión de audiencia
        if campaign.current_ctr > prediction.predicted_ctr * 1.2:
            opportunities["audience"] = {
                "type": "audience_expansion",
                "confidence": 0.7,
                "suggested_expansions": [
                    f"Lookalike basado en mejores conversores",
                    f"Expandir grupo etario ±5 años",
                    f"Probar países similares culturalmente"
                ],
                "expected_performance_retention": 0.8
            }
        
        return opportunities
    
    async def execute_optimization_decision(self, decision: OptimizationDecision) -> Dict[str, Any]:
        """Ejecutar decisión de optimización (simulado)"""
        
        logger.info(f"Executing optimization: {decision.decision_type} for campaign {decision.campaign_id}")
        
        # En producción, aquí iría la integración con Facebook Ads API
        execution_result = {
            "campaign_id": decision.campaign_id,
            "action": decision.decision_type,
            "executed_at": datetime.now(),
            "success": True,
            "changes_made": {}
        }
        
        if decision.decision_type == "scale_up" and decision.budget_multiplier:
            execution_result["changes_made"]["budget_increase"] = f"{decision.budget_multiplier}x"
            
        elif decision.decision_type == "pause":
            execution_result["changes_made"]["status"] = "paused"
            
        elif decision.decision_type == "modify_targeting":
            execution_result["changes_made"]["targeting"] = "optimized_for_performance"
        
        # Guardar en historial
        self.optimization_history.append(decision)
        
        return execution_result
    
    def get_genre_intelligence_summary(self, genre: MusicalGenre) -> Dict[str, Any]:
        """Resumen de inteligencia por género"""
        
        # Estadísticas del género
        genre_campaigns = [
            c for c in self.context_db.campaigns.values() 
            if c.pixel_profile.musical_context.genre == genre
        ]
        
        if not genre_campaigns:
            return {"error": f"No campaigns found for genre {genre.value}"}
        
        # Métricas agregadas
        avg_ctr = sum(c.current_ctr for c in genre_campaigns) / len(genre_campaigns)
        avg_cpv = sum(c.current_cpv for c in genre_campaigns if c.current_cpv > 0) / max(1, len([c for c in genre_campaigns if c.current_cpv > 0]))
        
        high_performers = [c for c in genre_campaigns if c.current_ctr > avg_ctr * 1.5]
        
        # Insights del modelo especializado
        model_insights = self.ml_ensemble.get_genre_insights(genre)
        
        return {
            "genre": genre.value,
            "total_campaigns": len(genre_campaigns),
            "performance_metrics": {
                "avg_ctr": avg_ctr,
                "avg_cpv": avg_cpv,
                "high_performer_rate": len(high_performers) / len(genre_campaigns)
            },
            "model_status": model_insights,
            "optimization_opportunities": len([
                d for d in self.optimization_history 
                if d.decision_type == "scale_up" and d.confidence > 0.7
            ]),
            "generated_at": datetime.now().isoformat()
        }

# Instancia global del motor de inteligencia
musical_intelligence = MusicalIntelligenceEngine()

# Función de utilidad para análisis rápido
async def quick_campaign_analysis(campaign_id: str) -> Dict[str, Any]:
    """Análisis rápido de campaña para dashboard"""
    try:
        insights = await musical_intelligence.analyze_campaign_intelligence(campaign_id)
        
        return {
            "campaign_id": campaign_id,
            "genre": insights.genre,
            "performance_grade": _calculate_performance_grade(insights),
            "recommended_action": insights.optimization_decision.decision_type,
            "confidence": insights.optimization_decision.confidence,
            "key_insights": insights.ml_prediction.genre_specific_insights[:3],
            "market_position": insights.market_position,
            "viral_potential": insights.ml_prediction.prob_viral_potential > 0.5
        }
    except Exception as e:
        logger.error(f"Error in quick analysis for {campaign_id}: {e}")
        return {"error": str(e)}

def _calculate_performance_grade(insights: CampaignInsights) -> str:
    """Calcular nota de performance A-F"""
    score = 0
    
    # Factor de percentil del género (40%)
    score += insights.genre_percentile * 0.4
    
    # Factor de ML prediction confidence (30%)
    score += insights.ml_prediction.confidence * 0.3
    
    # Factor de performance vs historial pixel (20%)
    score += insights.pixel_performance_vs_history * 0.2
    
    # Factor de probabilidad de alto rendimiento (10%)
    score += insights.ml_prediction.prob_high_performance * 0.1
    
    if score >= 0.9:
        return "A+"
    elif score >= 0.8:
        return "A"
    elif score >= 0.7:
        return "B"
    elif score >= 0.6:
        return "C"
    elif score >= 0.5:
        return "D"
    else:
        return "F"