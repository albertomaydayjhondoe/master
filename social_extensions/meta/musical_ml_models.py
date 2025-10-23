"""
Meta Ads Musical ML Models - Modelos especializados por género musical
Sistema de ML que aprende patrones específicos de cada género musical
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging
from abc import ABC, abstractmethod

from .musical_context_system import (
    MusicalGenre, PixelProfile, CampaignContext, 
    GENRE_EXPECTATIONS, musical_context_db
)

logger = logging.getLogger(__name__)

@dataclass
class MLFeatures:
    """Features para el modelo ML contextual"""
    # Features básicas de campaña
    budget: float
    target_age_avg: float
    target_countries_count: int
    
    # Features musicales/contextuales  
    genre_encoded: Dict[str, int]  # One-hot encoding del género
    energy_level: int  # 1-4 (low to extreme)
    audience_match_score: float  # Qué tan bien match hace la audiencia con el género
    
    # Features históricas del pixel
    pixel_avg_ctr: float
    pixel_avg_cpv: float
    pixel_total_campaigns: int
    
    # Features de timing y contexto
    day_of_week: int
    hour_of_day: int
    season: int  # 1-4
    
    # Features de competencia y mercado
    market_saturation: float  # Estimación de saturación del género en el país
    regional_affinity: float  # Afinidad regional con el género

@dataclass
class MLPrediction:
    """Predicción del modelo ML contextual"""
    predicted_ctr: float
    predicted_cpv: float
    predicted_conversion_rate: float
    confidence: float
    
    # Probabilidades de rendimiento
    prob_high_performance: float  # P(rendimiento > percentil 75)
    prob_scale_worthy: float  # P(merece escalar)
    prob_viral_potential: float  # P(potencial viral)
    
    # Explicabilidad
    feature_importance: Dict[str, float]
    genre_specific_insights: List[str]
    optimization_suggestions: List[str]

class BaseGenreModel(ABC):
    """Clase base para modelos especializados por género"""
    
    def __init__(self, genre: MusicalGenre):
        self.genre = genre
        self.model = None
        self.is_trained = False
        self.feature_importance = {}
        self.training_history = []
        
    @abstractmethod
    def extract_features(self, campaign: CampaignContext) -> MLFeatures:
        """Extraer features específicas del género"""
        pass
    
    @abstractmethod
    def predict(self, features: MLFeatures) -> MLPrediction:
        """Hacer predicción específica del género"""
        pass
    
    @abstractmethod
    def train(self, training_data: List[CampaignContext]) -> Dict[str, Any]:
        """Entrenar modelo con datos específicos del género"""
        pass

class TrapModel(BaseGenreModel):
    """Modelo especializado en música trap"""
    
    def __init__(self):
        super().__init__(MusicalGenre.TRAP)
        # Parámetros específicos del trap
        self.viral_threshold = 0.025  # CTR mínimo para considerarse viral
        self.optimal_watch_time = 12.5
        self.retargeting_efficiency = 1.4
    
    def extract_features(self, campaign: CampaignContext) -> MLFeatures:
        """Features específicas para trap"""
        pixel = campaign.pixel_profile
        
        # Calcular audience match score para trap
        audience_match = self._calculate_trap_audience_match(campaign)
        
        # Regional affinity para trap
        regional_affinity = self._get_trap_regional_affinity(campaign.target_countries)
        
        return MLFeatures(
            budget=campaign.budget,
            target_age_avg=(campaign.target_age_range[0] + campaign.target_age_range[1]) / 2,
            target_countries_count=len(campaign.target_countries),
            genre_encoded={"trap": 1, "reggaeton": 0, "rap": 0, "corrido": 0},
            energy_level=3,  # Trap is typically high energy
            audience_match_score=audience_match,
            pixel_avg_ctr=pixel.avg_ctr,
            pixel_avg_cpv=pixel.avg_cpv,
            pixel_total_campaigns=pixel.total_campaigns,
            day_of_week=datetime.now().weekday(),
            hour_of_day=datetime.now().hour,
            season=((datetime.now().month - 1) // 3) + 1,
            market_saturation=self._estimate_trap_saturation(campaign.target_countries),
            regional_affinity=regional_affinity
        )
    
    def predict(self, features: MLFeatures) -> MLPrediction:
        """Predicción específica para trap usando patrones conocidos"""
        
        # Base expectations para trap
        base_ctr = GENRE_EXPECTATIONS[MusicalGenre.TRAP]["expected_ctr"]
        base_cpv = GENRE_EXPECTATIONS[MusicalGenre.TRAP]["expected_cpv"]
        
        # Ajustar basado en features
        predicted_ctr = base_ctr
        predicted_cpv = base_cpv
        
        # Factor de audiencia
        if features.audience_match_score > 0.8:
            predicted_ctr *= 1.3
            predicted_cpv *= 0.85
        elif features.audience_match_score < 0.5:
            predicted_ctr *= 0.7
            predicted_cpv *= 1.2
        
        # Factor regional
        predicted_ctr *= (1 + features.regional_affinity * 0.5)
        predicted_cpv *= (1 - features.regional_affinity * 0.3)
        
        # Factor de saturación del mercado
        if features.market_saturation > 0.7:
            predicted_ctr *= 0.8
            predicted_cpv *= 1.15
        
        # Factor de presupuesto (trap responde bien a presupuestos medios)
        if 200 <= features.budget <= 800:
            predicted_ctr *= 1.1
        elif features.budget > 1500:
            predicted_ctr *= 0.9  # Diminishing returns
        
        # Calcular probabilidades
        prob_high_performance = min(predicted_ctr / base_ctr / 1.5, 0.95)
        prob_scale_worthy = prob_high_performance * 0.8 if predicted_ctr > self.viral_threshold else 0.3
        prob_viral_potential = (predicted_ctr / self.viral_threshold) * 0.4 if predicted_ctr > self.viral_threshold * 0.8 else 0.1
        
        # Insights específicos de trap
        insights = []
        if features.audience_match_score < 0.6:
            insights.append("Audiencia no optimizada para trap - considerar targeting masculino 18-25")
        if features.budget < 300:
            insights.append("Presupuesto bajo para trap - incrementar a 400-600€ para mejor performance")
        if features.regional_affinity > 0.8:
            insights.append("Excelente match regional para trap - potencial de viralización alta")
        
        # Sugerencias de optimización
        optimizations = []
        if predicted_ctr < base_ctr * 0.8:
            optimizations.append("Probar creatividades más agresivas/urbanas")
            optimizations.append("Enfocar en retargeting de usuarios engaged")
        if predicted_cpv > base_cpv * 1.2:
            optimizations.append("Refinar targeting - eliminar audiencias de bajo rendimiento")
        
        return MLPrediction(
            predicted_ctr=predicted_ctr,
            predicted_cpv=predicted_cpv,
            predicted_conversion_rate=predicted_ctr * 0.15,  # Trap has moderate conversion
            confidence=0.75 + features.pixel_total_campaigns * 0.01,  # More campaigns = more confidence
            prob_high_performance=prob_high_performance,
            prob_scale_worthy=prob_scale_worthy,
            prob_viral_potential=prob_viral_potential,
            feature_importance={
                "audience_match": 0.35,
                "regional_affinity": 0.25,
                "budget": 0.15,
                "pixel_history": 0.15,
                "market_saturation": 0.10
            },
            genre_specific_insights=insights,
            optimization_suggestions=optimizations
        )
    
    def train(self, training_data: List[CampaignContext]) -> Dict[str, Any]:
        """Entrenar con datos de campañas trap"""
        trap_campaigns = [c for c in training_data if c.pixel_profile.musical_context.genre == MusicalGenre.TRAP]
        
        if len(trap_campaigns) < 10:
            return {"error": "Insufficient trap training data", "campaigns_needed": 10 - len(trap_campaigns)}
        
        # Análisis de patrones en trap
        high_performers = [c for c in trap_campaigns if c.current_ctr > self.viral_threshold]
        
        # Actualizar parámetros basado en datos reales
        if high_performers:
            avg_high_ctr = np.mean([c.current_ctr for c in high_performers])
            avg_high_budget = np.mean([c.budget for c in high_performers])
            
            # Ajustar thresholds
            self.viral_threshold = avg_high_ctr * 0.8
        
        self.is_trained = True
        training_result = {
            "model_type": "trap_specialized",
            "training_campaigns": len(trap_campaigns),
            "high_performers": len(high_performers),
            "updated_viral_threshold": self.viral_threshold,
            "training_date": datetime.now().isoformat()
        }
        
        self.training_history.append(training_result)
        return training_result
    
    def _calculate_trap_audience_match(self, campaign: CampaignContext) -> float:
        """Calcular qué tan bien match hace la audiencia con trap"""
        score = 0.5  # Base score
        
        age_avg = (campaign.target_age_range[0] + campaign.target_age_range[1]) / 2
        
        # Trap funciona mejor con jóvenes 16-28
        if 16 <= age_avg <= 28:
            score += 0.3
        elif age_avg > 35:
            score -= 0.2
        
        # Países donde el trap funciona bien
        trap_friendly_countries = ["spain", "argentina", "chile", "mexico"]
        if any(country.lower() in trap_friendly_countries for country in campaign.target_countries):
            score += 0.2
        
        return min(score, 1.0)
    
    def _get_trap_regional_affinity(self, countries: List[str]) -> float:
        """Afinidad regional con el trap"""
        trap_affinity = {
            "spain": 0.9, "argentina": 0.8, "chile": 0.7,
            "mexico": 0.6, "colombia": 0.5, "usa": 0.8
        }
        
        if not countries:
            return 0.5
        
        affinities = [trap_affinity.get(country.lower(), 0.3) for country in countries]
        return np.mean(affinities)
    
    def _estimate_trap_saturation(self, countries: List[str]) -> float:
        """Estimar saturación del mercado trap"""
        # Simulación de saturación por país (en producción vendría de datos reales)
        saturation_data = {
            "spain": 0.6, "argentina": 0.4, "mexico": 0.7,
            "colombia": 0.5, "chile": 0.3
        }
        
        if not countries:
            return 0.5
        
        saturations = [saturation_data.get(country.lower(), 0.5) for country in countries]
        return np.mean(saturations)

class ReggatonModel(BaseGenreModel):
    """Modelo especializado en reggaetón"""
    
    def __init__(self):
        super().__init__(MusicalGenre.REGGAETON)
        self.viral_threshold = 0.035  # Reggaetón tiene CTR más alto
        self.optimal_watch_time = 18.9
        self.female_audience_bonus = 1.3
    
    def extract_features(self, campaign: CampaignContext) -> MLFeatures:
        """Features específicas para reggaetón"""
        pixel = campaign.pixel_profile
        audience_match = self._calculate_reggaeton_audience_match(campaign)
        regional_affinity = self._get_reggaeton_regional_affinity(campaign.target_countries)
        
        return MLFeatures(
            budget=campaign.budget,
            target_age_avg=(campaign.target_age_range[0] + campaign.target_age_range[1]) / 2,
            target_countries_count=len(campaign.target_countries),
            genre_encoded={"trap": 0, "reggaeton": 1, "rap": 0, "corrido": 0},
            energy_level=4,  # Reggaetón is extreme energy
            audience_match_score=audience_match,
            pixel_avg_ctr=pixel.avg_ctr,
            pixel_avg_cpv=pixel.avg_cpv,
            pixel_total_campaigns=pixel.total_campaigns,
            day_of_week=datetime.now().weekday(),
            hour_of_day=datetime.now().hour,
            season=((datetime.now().month - 1) // 3) + 1,
            market_saturation=self._estimate_reggaeton_saturation(campaign.target_countries),
            regional_affinity=regional_affinity
        )
    
    def predict(self, features: MLFeatures) -> MLPrediction:
        """Predicción específica para reggaetón"""
        
        base_ctr = GENRE_EXPECTATIONS[MusicalGenre.REGGAETON]["expected_ctr"]
        base_cpv = GENRE_EXPECTATIONS[MusicalGenre.REGGAETON]["expected_cpv"]
        
        predicted_ctr = base_ctr
        predicted_cpv = base_cpv
        
        # Reggaetón funciona MUCHO mejor con audiencia femenina
        if features.audience_match_score > 0.8:
            predicted_ctr *= self.female_audience_bonus
            predicted_cpv *= 0.75
        
        # Factor regional (reggaetón es muy regional)
        predicted_ctr *= (1 + features.regional_affinity * 0.8)
        predicted_cpv *= (1 - features.regional_affinity * 0.4)
        
        # Reggaetón escala muy bien con presupuesto
        if features.budget > 500:
            predicted_ctr *= min(1.4, 1 + (features.budget / 1000) * 0.3)
        
        # Horarios peak para reggaetón (fines de semana)
        if features.day_of_week >= 5:  # Sábado/Domingo
            predicted_ctr *= 1.2
        
        prob_high_performance = min(predicted_ctr / base_ctr / 1.3, 0.9)
        prob_scale_worthy = prob_high_performance * 0.9  # Reggaetón escala muy bien
        prob_viral_potential = (predicted_ctr / self.viral_threshold) * 0.6 if predicted_ctr > self.viral_threshold else 0.2
        
        insights = []
        if features.audience_match_score > 0.8:
            insights.append("Excelente match de audiencia para reggaetón - alta probabilidad de viralización")
        if features.regional_affinity < 0.5:
            insights.append("Baja afinidad regional - considerar países latinos")
        if features.budget > 800:
            insights.append("Presupuesto óptimo para reggaetón - género con alto ROI")
        
        optimizations = []
        if predicted_ctr > self.viral_threshold:
            optimizations.append("¡Potencial viral detectado! Escalar agresivamente")
            optimizations.append("Crear lookalike audiences de top performers")
        
        return MLPrediction(
            predicted_ctr=predicted_ctr,
            predicted_cpv=predicted_cpv,
            predicted_conversion_rate=predicted_ctr * 0.22,  # Reggaetón converts well
            confidence=0.8 + features.pixel_total_campaigns * 0.015,
            prob_high_performance=prob_high_performance,
            prob_scale_worthy=prob_scale_worthy,
            prob_viral_potential=prob_viral_potential,
            feature_importance={
                "audience_match": 0.4,
                "regional_affinity": 0.3,
                "budget": 0.2,
                "timing": 0.1
            },
            genre_specific_insights=insights,
            optimization_suggestions=optimizations
        )
    
    def train(self, training_data: List[CampaignContext]) -> Dict[str, Any]:
        """Entrenar modelo reggaetón"""
        reggaeton_campaigns = [c for c in training_data if c.pixel_profile.musical_context.genre == MusicalGenre.REGGAETON]
        
        if len(reggaeton_campaigns) < 8:  # Menos datos necesarios - reggaetón es más predecible
            return {"error": "Insufficient reggaeton training data"}
        
        # Análisis de patrones exitosos
        viral_campaigns = [c for c in reggaeton_campaigns if c.current_ctr > self.viral_threshold]
        
        self.is_trained = True
        return {
            "model_type": "reggaeton_specialized",
            "training_campaigns": len(reggaeton_campaigns),
            "viral_campaigns": len(viral_campaigns),
            "viral_rate": len(viral_campaigns) / len(reggaeton_campaigns) if reggaeton_campaigns else 0
        }
    
    def _calculate_reggaeton_audience_match(self, campaign: CampaignContext) -> float:
        """Match específico para reggaetón"""
        score = 0.5
        
        age_avg = (campaign.target_age_range[0] + campaign.target_age_range[1]) / 2
        
        # Reggaetón funciona mejor con 16-30, especialmente mujeres
        if 16 <= age_avg <= 30:
            score += 0.4
        
        # Boost por países latinos
        latin_countries = ["colombia", "puerto_rico", "dominican_republic", "mexico", "venezuela"]
        if any(country.lower() in latin_countries for country in campaign.target_countries):
            score += 0.3
        
        return min(score, 1.0)
    
    def _get_reggaeton_regional_affinity(self, countries: List[str]) -> float:
        """Afinidad regional reggaetón"""
        reggaeton_affinity = {
            "colombia": 0.95, "puerto_rico": 0.98, "dominican_republic": 0.92,
            "mexico": 0.85, "venezuela": 0.9, "panama": 0.88, "spain": 0.7
        }
        
        if not countries:
            return 0.5
        
        affinities = [reggaeton_affinity.get(country.lower(), 0.4) for country in countries]
        return np.mean(affinities)
    
    def _estimate_reggaeton_saturation(self, countries: List[str]) -> float:
        """Saturación específica reggaetón"""
        # Reggaetón generalmente tiene menos saturación que trap
        saturation_data = {
            "colombia": 0.3, "mexico": 0.4, "spain": 0.5,
            "puerto_rico": 0.6, "usa": 0.7
        }
        
        if not countries:
            return 0.4
        
        saturations = [saturation_data.get(country.lower(), 0.4) for country in countries]
        return np.mean(saturations)

class MusicalMLEnsemble:
    """Ensemble de modelos especializados por género musical"""
    
    def __init__(self):
        self.models = {
            MusicalGenre.TRAP: TrapModel(),
            MusicalGenre.REGGAETON: ReggatonModel(),
            # TODO: Agregar RapModel, CorridoModel, etc.
        }
        
        self.ensemble_weights = {
            MusicalGenre.TRAP: 1.0,
            MusicalGenre.REGGAETON: 1.0,
        }
    
    def predict_campaign_performance(self, campaign: CampaignContext) -> MLPrediction:
        """Predicción usando el modelo especializado del género"""
        genre = campaign.pixel_profile.musical_context.genre
        
        if genre not in self.models:
            # Fallback a modelo genérico
            logger.warning(f"No specialized model for genre {genre}, using generic prediction")
            return self._generic_prediction(campaign)
        
        model = self.models[genre]
        features = model.extract_features(campaign)
        prediction = model.predict(features)
        
        # Agregar contexto del ensemble
        prediction.genre_specific_insights.insert(0, f"Predicción usando modelo especializado en {genre.value}")
        
        return prediction
    
    def train_all_models(self, training_data: List[CampaignContext]) -> Dict[str, Any]:
        """Entrenar todos los modelos especializados"""
        results = {}
        
        for genre, model in self.models.items():
            try:
                training_result = model.train(training_data)
                results[genre.value] = training_result
                logger.info(f"Trained {genre.value} model: {training_result}")
            except Exception as e:
                results[genre.value] = {"error": str(e)}
                logger.error(f"Failed to train {genre.value} model: {e}")
        
        return results
    
    def get_genre_insights(self, genre: MusicalGenre) -> Dict[str, Any]:
        """Obtener insights específicos del género"""
        if genre not in self.models:
            return {"error": "Genre model not available"}
        
        model = self.models[genre]
        return {
            "genre": genre.value,
            "viral_threshold": getattr(model, 'viral_threshold', 0.02),
            "is_trained": model.is_trained,
            "training_history": model.training_history,
            "specialization_features": model.feature_importance
        }
    
    def _generic_prediction(self, campaign: CampaignContext) -> MLPrediction:
        """Predicción genérica cuando no hay modelo especializado"""
        return MLPrediction(
            predicted_ctr=1.5,
            predicted_cpv=0.035,
            predicted_conversion_rate=0.08,
            confidence=0.5,
            prob_high_performance=0.3,
            prob_scale_worthy=0.2,
            prob_viral_potential=0.1,
            feature_importance={},
            genre_specific_insights=["Usando modelo genérico - considera crear modelo especializado"],
            optimization_suggestions=["Recopilar más datos para crear modelo especializado"]
        )

# Instancia global del ensemble
musical_ml_ensemble = MusicalMLEnsemble()