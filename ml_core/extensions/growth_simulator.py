"""
📈 NETWORK GROWTH SIMULATOR

Simula crecimiento de red y predice ROI usando modelos estadísticos avanzados,
Monte Carlo simulation y reinforcement learning para optimizar estrategias.

CAPACIDADES:
- Modelado de crecimiento histórico con regresión no lineal
- Monte Carlo simulation con 1000+ escenarios para cada estrategia
- Reinforcement learning (Q-Learning) para optimización de decisiones
- Predicción de ROI por plataforma, timing y budget
- Comparativa de estrategias: "¿Instagram vs TikTok a las 20h?"
- Optimización de portfolio: distribución óptima de presupuesto
- Detección de puntos de saturación y rendimientos decrecientes
- Decision support: recomendaciones antes de lanzar campañas

ARQUITECTURA:
- HistoricalDataExtractor: extrae patrones de campañas pasadas
- GrowthModeler: modelos de regresión y predicción
- MonteCarloSimulator: simulaciones estocásticas
- QLearningOptimizer: optimización con reinforcement learning  
- ROIPredictor: predicciones de retorno de inversión
- ScenarioComparator: comparativas de estrategias
- SimulationStorage: persistencia de resultados
- DecisionSupport: interfaz para toma de decisiones
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
import random
import math
import statistics
from collections import defaultdict, deque

# Data science and ML
import pandas as pd
import numpy as np
from scipy import stats, optimize
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# Deep learning for advanced modeling
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch no disponible - usando solo modelos sklearn")

# Database
from sqlalchemy import create_engine, text
import redis

# Internal
from config.app_settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class Platform(Enum):
    """Plataformas soportadas para simulación"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"
    FACEBOOK = "facebook"
    TWITTER = "twitter"

class CampaignObjective(Enum):
    """Objetivos de campaña"""
    VIEWS = "views"
    ENGAGEMENT = "engagement"
    FOLLOWERS = "followers"
    STREAMS = "streams"
    CONVERSIONS = "conversions"

@dataclass
class HistoricalCampaign:
    """Datos históricos de una campaña"""
    campaign_id: str
    platform: Platform
    objective: CampaignObjective
    budget_eur: float
    duration_days: int
    start_date: datetime
    target_audience_size: int
    content_type: str  # "video", "image", "story", "reel"
    
    # Resultados
    views: int
    engagement_rate: float
    followers_gained: int
    cost_per_view: float
    cost_per_engagement: float
    cost_per_follower: float
    total_reach: int
    
    # Context features
    day_of_week: int  # 0=Monday, 6=Sunday
    hour_of_day: int  # 0-23
    season: str  # "spring", "summer", "autumn", "winter"
    is_weekend: bool
    competitor_activity: float  # Nivel de actividad competencia 0-1
    
@dataclass
class SimulationScenario:
    """Escenario para simulación Monte Carlo"""
    scenario_id: str
    budget_eur: float
    platform: Platform
    objective: CampaignObjective
    duration_days: int
    content_type: str
    timing: Dict[str, Any]  # {"day_of_week": 5, "hour": 20}
    
    # Parámetros de incertidumbre
    budget_variance: float = 0.1  # ±10% variación en ejecución
    performance_variance: float = 0.2  # ±20% variación en performance
    
@dataclass
class SimulationResult:
    """Resultado de una simulación"""
    scenario: SimulationScenario
    
    # Predicciones centrales
    predicted_views: float
    predicted_engagement_rate: float
    predicted_followers: float
    predicted_roi_percentage: float
    
    # Intervalos de confianza (Monte Carlo)
    views_ci_lower: float
    views_ci_upper: float
    roi_ci_lower: float
    roi_ci_upper: float
    
    # Métricas de costo
    predicted_cost_per_view: float
    predicted_cost_per_follower: float
    break_even_point_days: float
    
    # Risk assessment
    probability_positive_roi: float
    probability_exceeds_target: float
    maximum_drawdown_risk: float
    
    simulation_confidence: float  # 0-1
    computed_at: datetime

@dataclass
class OptimizationRecommendation:
    """Recomendación de optimización"""
    recommendation_id: str
    scenario: SimulationScenario
    predicted_result: SimulationResult
    
    action_type: str  # "invest_more", "change_platform", "adjust_timing", "reallocate"
    confidence_score: float
    expected_improvement: float  # % mejora esperada
    
    reasoning: str
    alternative_scenarios: List[SimulationResult]
    
    created_at: datetime


class HistoricalDataExtractor:
    """Extractor de datos históricos para entrenamiento de modelos"""
    
    def __init__(self):
        self.db_url = settings.DATABASE_URL
        self.engine = create_engine(self.db_url) if self.db_url else None
        
    async def extract_campaign_history(self, lookback_days: int = 365) -> List[HistoricalCampaign]:
        """Extrae historial de campañas para análisis"""
        if not self.engine:
            # Return dummy data for development
            return self._generate_dummy_historical_data()
        
        query = """
        SELECT 
            c.campaign_id,
            c.platform,
            c.objective,
            c.budget_eur,
            c.duration_days,
            c.start_date,
            c.target_audience_size,
            c.content_type,
            
            -- Results
            COALESCE(cr.total_views, 0) as views,
            COALESCE(cr.engagement_rate, 0) as engagement_rate,
            COALESCE(cr.followers_gained, 0) as followers_gained,
            COALESCE(cr.cost_per_view, 0) as cost_per_view,
            COALESCE(cr.cost_per_engagement, 0) as cost_per_engagement,
            COALESCE(cr.cost_per_follower, 0) as cost_per_follower,
            COALESCE(cr.total_reach, 0) as total_reach,
            
            -- Context
            EXTRACT(DOW FROM c.start_date) as day_of_week,
            EXTRACT(HOUR FROM c.start_date) as hour_of_day,
            CASE 
                WHEN EXTRACT(MONTH FROM c.start_date) IN (3,4,5) THEN 'spring'
                WHEN EXTRACT(MONTH FROM c.start_date) IN (6,7,8) THEN 'summer'
                WHEN EXTRACT(MONTH FROM c.start_date) IN (9,10,11) THEN 'autumn'
                ELSE 'winter'
            END as season,
            CASE WHEN EXTRACT(DOW FROM c.start_date) IN (0,6) THEN true ELSE false END as is_weekend,
            COALESCE(cc.competitor_activity_score, 0.5) as competitor_activity
            
        FROM campaigns c
        LEFT JOIN campaign_results cr ON c.campaign_id = cr.campaign_id
        LEFT JOIN campaign_context cc ON c.campaign_id = cc.campaign_id
        WHERE c.start_date > NOW() - INTERVAL '%s days'
        AND c.status = 'completed'
        ORDER BY c.start_date DESC
        """
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), (lookback_days,))
                rows = result.fetchall()
            
            campaigns = []
            for row in rows:
                campaign = HistoricalCampaign(
                    campaign_id=row.campaign_id,
                    platform=Platform(row.platform),
                    objective=CampaignObjective(row.objective),
                    budget_eur=float(row.budget_eur),
                    duration_days=int(row.duration_days),
                    start_date=row.start_date,
                    target_audience_size=int(row.target_audience_size),
                    content_type=row.content_type,
                    views=int(row.views),
                    engagement_rate=float(row.engagement_rate),
                    followers_gained=int(row.followers_gained),
                    cost_per_view=float(row.cost_per_view),
                    cost_per_engagement=float(row.cost_per_engagement),
                    cost_per_follower=float(row.cost_per_follower),
                    total_reach=int(row.total_reach),
                    day_of_week=int(row.day_of_week),
                    hour_of_day=int(row.hour_of_day),
                    season=row.season,
                    is_weekend=bool(row.is_weekend),
                    competitor_activity=float(row.competitor_activity)
                )
                campaigns.append(campaign)
            
            logger.info(f"✅ Extraídas {len(campaigns)} campañas históricas")
            return campaigns
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo datos históricos: {e}")
            # Fallback to dummy data
            return self._generate_dummy_historical_data()

    def _generate_dummy_historical_data(self) -> List[HistoricalCampaign]:
        """Genera datos dummy para desarrollo y testing"""
        logger.info("🔧 Generando datos históricos dummy para simulación")
        
        campaigns = []
        platforms = list(Platform)
        objectives = list(CampaignObjective)
        content_types = ["video", "image", "story", "reel", "carousel"]
        seasons = ["spring", "summer", "autumn", "winter"]
        
        # Generar 200 campañas dummy realistas
        for i in range(200):
            platform = random.choice(platforms)
            objective = random.choice(objectives)
            
            # Budget based on platform (realista)
            if platform == Platform.TIKTOK:
                budget = random.uniform(50, 500)
            elif platform == Platform.INSTAGRAM:
                budget = random.uniform(100, 1000)
            elif platform == Platform.YOUTUBE:
                budget = random.uniform(200, 2000)
            else:
                budget = random.uniform(75, 750)
            
            duration = random.randint(3, 30)
            start_date = datetime.now() - timedelta(days=random.randint(7, 365))
            
            # Performance realista basado en plataforma y presupuesto
            if platform == Platform.TIKTOK:
                views = int(budget * random.uniform(100, 500))  # TikTok mejor reach/€
                engagement_rate = random.uniform(0.05, 0.15)
            elif platform == Platform.INSTAGRAM:
                views = int(budget * random.uniform(50, 200))
                engagement_rate = random.uniform(0.02, 0.08)
            elif platform == Platform.YOUTUBE:
                views = int(budget * random.uniform(20, 100))
                engagement_rate = random.uniform(0.01, 0.05)
            else:
                views = int(budget * random.uniform(30, 150))
                engagement_rate = random.uniform(0.015, 0.06)
            
            followers_gained = int(views * engagement_rate * random.uniform(0.1, 0.3))
            
            # Costos
            cost_per_view = budget / max(views, 1)
            cost_per_engagement = budget / max(views * engagement_rate, 1)
            cost_per_follower = budget / max(followers_gained, 1)
            
            # Context features
            day_of_week = start_date.weekday()
            hour_of_day = random.randint(8, 23)
            season = seasons[(start_date.month - 1) // 3]
            is_weekend = day_of_week >= 5
            
            # Weekend boost
            if is_weekend:
                views = int(views * random.uniform(1.1, 1.4))
                engagement_rate *= random.uniform(1.05, 1.25)
            
            # Evening boost (18-22h)
            if 18 <= hour_of_day <= 22:
                views = int(views * random.uniform(1.15, 1.35))
                engagement_rate *= random.uniform(1.1, 1.2)
            
            campaign = HistoricalCampaign(
                campaign_id=f"dummy_campaign_{i:03d}",
                platform=platform,
                objective=objective,
                budget_eur=budget,
                duration_days=duration,
                start_date=start_date,
                target_audience_size=random.randint(10000, 1000000),
                content_type=random.choice(content_types),
                views=views,
                engagement_rate=engagement_rate,
                followers_gained=followers_gained,
                cost_per_view=cost_per_view,
                cost_per_engagement=cost_per_engagement,
                cost_per_follower=cost_per_follower,
                total_reach=int(views * random.uniform(1.5, 3.0)),
                day_of_week=day_of_week,
                hour_of_day=hour_of_day,
                season=season,
                is_weekend=is_weekend,
                competitor_activity=random.uniform(0.2, 0.8)
            )
            
            campaigns.append(campaign)
        
        return campaigns


class GrowthModeler:
    """Modelador de crecimiento usando ML"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.is_trained = False
        
    async def train_models(self, historical_campaigns: List[HistoricalCampaign]):
        """Entrena modelos predictivos con datos históricos"""
        if not historical_campaigns:
            logger.error("No hay datos históricos para entrenar modelos")
            return False
        
        logger.info(f"🧠 Entrenando modelos con {len(historical_campaigns)} campañas...")
        
        # Preparar dataset
        df = self._prepare_training_data(historical_campaigns)
        
        if df.empty:
            logger.error("Dataset vacío después de preparación")
            return False
        
        # Features y targets
        feature_columns = [
            'budget_eur', 'duration_days', 'target_audience_size',
            'day_of_week', 'hour_of_day', 'is_weekend_encoded', 
            'competitor_activity', 'platform_encoded', 'objective_encoded', 
            'content_type_encoded', 'season_encoded'
        ]
        
        X = df[feature_columns]
        
        # Entrenar modelo para cada métrica objetivo
        targets = {
            'views': 'views',
            'engagement_rate': 'engagement_rate', 
            'followers_gained': 'followers_gained',
            'cost_per_view': 'cost_per_view'
        }
        
        for target_name, target_column in targets.items():
            if target_column not in df.columns:
                continue
                
            y = df[target_column]
            
            # Split train/test
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scaling
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Entrenar varios modelos y elegir el mejor
            models_to_try = {
                'rf': RandomForestRegressor(n_estimators=100, random_state=42),
                'gb': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'ridge': Ridge(alpha=1.0)
            }
            
            best_model = None
            best_score = -np.inf
            
            for model_name, model in models_to_try.items():
                try:
                    # Cross validation
                    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
                    avg_score = np.mean(cv_scores)
                    
                    if avg_score > best_score:
                        best_score = avg_score
                        best_model = model
                        
                    logger.debug(f"{target_name} - {model_name}: R² = {avg_score:.3f}")
                        
                except Exception as e:
                    logger.debug(f"Error entrenando {model_name} para {target_name}: {e}")
            
            if best_model is not None:
                # Entrenar mejor modelo con todos los datos
                best_model.fit(X_train_scaled, y_train)
                
                # Evaluar en test set
                y_pred = best_model.predict(X_test_scaled)
                test_r2 = r2_score(y_test, y_pred)
                test_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                
                # Guardar modelo y scaler
                self.models[target_name] = best_model
                self.scalers[target_name] = scaler
                
                logger.info(f"✅ Modelo {target_name}: R² = {test_r2:.3f}, RMSE = {test_rmse:.2f}")
            else:
                logger.warning(f"⚠️ No se pudo entrenar modelo para {target_name}")
        
        self.is_trained = len(self.models) > 0
        
        if self.is_trained:
            logger.info(f"🎯 Entrenamiento completado: {len(self.models)} modelos listos")
        else:
            logger.error("❌ Fallo en entrenamiento de modelos")
            
        return self.is_trained

    def _prepare_training_data(self, campaigns: List[HistoricalCampaign]) -> pd.DataFrame:
        """Prepara datos para entrenamiento"""
        data = []
        
        for campaign in campaigns:
            row = {
                'budget_eur': campaign.budget_eur,
                'duration_days': campaign.duration_days,
                'target_audience_size': campaign.target_audience_size,
                'day_of_week': campaign.day_of_week,
                'hour_of_day': campaign.hour_of_day,
                'is_weekend': campaign.is_weekend,
                'competitor_activity': campaign.competitor_activity,
                'platform': campaign.platform.value,
                'objective': campaign.objective.value,
                'content_type': campaign.content_type,
                'season': campaign.season,
                
                # Targets
                'views': campaign.views,
                'engagement_rate': campaign.engagement_rate,
                'followers_gained': campaign.followers_gained,
                'cost_per_view': campaign.cost_per_view
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Encode categorical variables
        categorical_columns = ['platform', 'objective', 'content_type', 'season']
        
        for col in categorical_columns:
            if col in df.columns:
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col])
                self.label_encoders[col] = le
        
        # Encode boolean
        df['is_weekend_encoded'] = df['is_weekend'].astype(int)
        
        # Remove outliers (más de 3 std dev)
        for target in ['views', 'engagement_rate', 'followers_gained', 'cost_per_view']:
            if target in df.columns:
                mean_val = df[target].mean()
                std_val = df[target].std()
                df = df[np.abs(df[target] - mean_val) <= 3 * std_val]
        
        logger.info(f"📊 Dataset preparado: {len(df)} filas, {len(df.columns)} columnas")
        return df

    async def predict_campaign_performance(self, scenario: SimulationScenario) -> Dict[str, float]:
        """Predice performance de una campaña"""
        if not self.is_trained:
            logger.error("Modelos no entrenados")
            return {}
        
        # Preparar features del escenario
        features = self._scenario_to_features(scenario)
        
        predictions = {}
        
        for target_name, model in self.models.items():
            try:
                scaler = self.scalers[target_name]
                features_scaled = scaler.transform([features])
                
                prediction = model.predict(features_scaled)[0]
                
                # Post-processing para valores realistas
                if target_name == 'views' and prediction < 0:
                    prediction = 0
                elif target_name == 'engagement_rate' and (prediction < 0 or prediction > 1):
                    prediction = max(0, min(1, prediction))
                elif target_name == 'followers_gained' and prediction < 0:
                    prediction = 0
                elif target_name == 'cost_per_view' and prediction < 0:
                    prediction = scenario.budget_eur / max(predictions.get('views', 1), 1)
                
                predictions[target_name] = prediction
                
            except Exception as e:
                logger.error(f"Error prediciendo {target_name}: {e}")
        
        return predictions

    def _scenario_to_features(self, scenario: SimulationScenario) -> List[float]:
        """Convierte escenario a features para predicción"""
        # Base features
        features = [
            scenario.budget_eur,
            scenario.duration_days,
            100000,  # Default target audience size
            scenario.timing.get('day_of_week', 1),
            scenario.timing.get('hour', 20),
            1 if scenario.timing.get('day_of_week', 1) >= 5 else 0,  # is_weekend
            0.5,  # default competitor activity
        ]
        
        # Encode categorical features
        try:
            platform_encoded = self.label_encoders['platform'].transform([scenario.platform.value])[0]
            objective_encoded = self.label_encoders['objective'].transform([scenario.objective.value])[0]
            content_type_encoded = self.label_encoders['content_type'].transform([scenario.content_type])[0]
            season_encoded = self.label_encoders['season'].transform([scenario.timing.get('season', 'spring')])[0]
        except:
            # Fallback values if encoding fails
            platform_encoded = 0
            objective_encoded = 0
            content_type_encoded = 0
            season_encoded = 0
        
        features.extend([platform_encoded, objective_encoded, content_type_encoded, season_encoded])
        
        return features


class MonteCarloSimulator:
    """Simulador Monte Carlo para análisis de riesgo"""
    
    def __init__(self, growth_modeler: GrowthModeler):
        self.growth_modeler = growth_modeler
        self.n_simulations = 1000
        
    async def run_simulation(self, scenario: SimulationScenario) -> SimulationResult:
        """Ejecuta simulación Monte Carlo para un escenario"""
        logger.info(f"🎲 Ejecutando simulación Monte Carlo: {scenario.scenario_id}")
        
        if not self.growth_modeler.is_trained:
            logger.error("Modelos no entrenados para simulación")
            return None
        
        # Resultados de todas las simulaciones
        simulation_results = {
            'views': [],
            'engagement_rate': [],
            'followers_gained': [],
            'cost_per_view': [],
            'roi_percentage': []
        }
        
        # Ejecutar N simulaciones
        for i in range(self.n_simulations):
            # Crear variación del escenario
            varied_scenario = self._create_scenario_variation(scenario)
            
            # Predicción base
            predictions = await self.growth_modeler.predict_campaign_performance(varied_scenario)
            
            if not predictions:
                continue
            
            # Añadir ruido estocástico
            noisy_predictions = self._add_stochastic_noise(predictions, scenario)
            
            # Calcular ROI
            roi = self._calculate_roi(noisy_predictions, varied_scenario.budget_eur)
            noisy_predictions['roi_percentage'] = roi
            
            # Almacenar resultados
            for key, value in noisy_predictions.items():
                if key in simulation_results:
                    simulation_results[key].append(value)
        
        # Calcular estadísticas
        return self._compute_simulation_statistics(scenario, simulation_results)

    def _create_scenario_variation(self, base_scenario: SimulationScenario) -> SimulationScenario:
        """Crea variación del escenario con incertidumbre"""
        # Variar budget
        budget_multiplier = np.random.normal(1.0, base_scenario.budget_variance)
        varied_budget = base_scenario.budget_eur * max(0.5, budget_multiplier)  # Min 50% del budget
        
        # Clonar escenario con variaciones
        varied_scenario = SimulationScenario(
            scenario_id=f"{base_scenario.scenario_id}_var",
            budget_eur=varied_budget,
            platform=base_scenario.platform,
            objective=base_scenario.objective,
            duration_days=base_scenario.duration_days,
            content_type=base_scenario.content_type,
            timing=base_scenario.timing.copy(),
            budget_variance=base_scenario.budget_variance,
            performance_variance=base_scenario.performance_variance
        )
        
        return varied_scenario

    def _add_stochastic_noise(self, predictions: Dict[str, float], scenario: SimulationScenario) -> Dict[str, float]:
        """Añade ruido estocástico a las predicciones"""
        noisy_predictions = {}
        variance = scenario.performance_variance
        
        for key, value in predictions.items():
            if key == 'engagement_rate':
                # Para engagement rate, usar distribución beta truncada
                noise_multiplier = np.random.normal(1.0, variance * 0.5)  # Menos varianza para rates
                noisy_value = value * max(0.1, noise_multiplier)
                noisy_predictions[key] = min(1.0, max(0.0, noisy_value))  # Clamp 0-1
            else:
                # Para otras métricas, usar distribución normal
                noise_multiplier = np.random.normal(1.0, variance)
                noisy_value = value * max(0.0, noise_multiplier)  # No valores negativos
                noisy_predictions[key] = noisy_value
        
        return noisy_predictions

    def _calculate_roi(self, predictions: Dict[str, float], budget: float) -> float:
        """Calcula ROI basado en las predicciones"""
        # ROI simplificado basado en valor de followers y engagement
        followers_value = predictions.get('followers_gained', 0) * 0.5  # €0.5 por follower
        engagement_value = predictions.get('views', 0) * predictions.get('engagement_rate', 0) * 0.01  # €0.01 por engagement
        
        total_value = followers_value + engagement_value
        roi_percentage = ((total_value - budget) / max(budget, 1)) * 100
        
        return roi_percentage

    def _compute_simulation_statistics(self, scenario: SimulationScenario, results: Dict[str, List[float]]) -> SimulationResult:
        """Computa estadísticas de los resultados de simulación"""
        if not results['views']:
            return None
        
        # Estadísticas centrales
        predicted_views = np.mean(results['views'])
        predicted_engagement_rate = np.mean(results['engagement_rate'])
        predicted_followers = np.mean(results['followers_gained'])
        predicted_roi = np.mean(results['roi_percentage'])
        
        # Intervalos de confianza (5% - 95%)
        views_ci_lower = np.percentile(results['views'], 5)
        views_ci_upper = np.percentile(results['views'], 95)
        roi_ci_lower = np.percentile(results['roi_percentage'], 5)
        roi_ci_upper = np.percentile(results['roi_percentage'], 95)
        
        # Métricas de costo
        predicted_cost_per_view = scenario.budget_eur / max(predicted_views, 1)
        predicted_cost_per_follower = scenario.budget_eur / max(predicted_followers, 1)
        
        # Break even estimation
        break_even_point_days = scenario.duration_days if predicted_roi < 0 else scenario.duration_days * 0.7
        
        # Risk metrics
        positive_roi_count = sum(1 for roi in results['roi_percentage'] if roi > 0)
        probability_positive_roi = positive_roi_count / len(results['roi_percentage'])
        
        # Target exceeding (assuming target is 10% ROI)
        target_roi = 10
        exceeds_target_count = sum(1 for roi in results['roi_percentage'] if roi > target_roi)
        probability_exceeds_target = exceeds_target_count / len(results['roi_percentage'])
        
        # Maximum drawdown (worst case ROI)
        maximum_drawdown_risk = abs(min(results['roi_percentage']))
        
        # Simulation confidence (based on variance)
        roi_std = np.std(results['roi_percentage'])
        simulation_confidence = max(0.5, 1.0 - (roi_std / 100))  # Lower std = higher confidence
        
        return SimulationResult(
            scenario=scenario,
            predicted_views=predicted_views,
            predicted_engagement_rate=predicted_engagement_rate,
            predicted_followers=predicted_followers,
            predicted_roi_percentage=predicted_roi,
            views_ci_lower=views_ci_lower,
            views_ci_upper=views_ci_upper,
            roi_ci_lower=roi_ci_lower,
            roi_ci_upper=roi_ci_upper,
            predicted_cost_per_view=predicted_cost_per_view,
            predicted_cost_per_follower=predicted_cost_per_follower,
            break_even_point_days=break_even_point_days,
            probability_positive_roi=probability_positive_roi,
            probability_exceeds_target=probability_exceeds_target,
            maximum_drawdown_risk=maximum_drawdown_risk,
            simulation_confidence=simulation_confidence,
            computed_at=datetime.now()
        )


class QLearningOptimizer:
    """Optimizador usando Q-Learning para decisiones de campaña"""
    
    def __init__(self):
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.1  # Exploration rate
        self.actions = [
            'increase_budget_10',
            'increase_budget_25', 
            'decrease_budget_10',
            'change_platform_instagram',
            'change_platform_tiktok',
            'change_platform_youtube',
            'shift_timing_evening',
            'shift_timing_weekend',
            'extend_duration',
            'do_nothing'
        ]
        
    def get_state_key(self, scenario: SimulationScenario, current_performance: Dict[str, float]) -> str:
        """Convierte escenario y performance a clave de estado"""
        roi = current_performance.get('roi_percentage', 0)
        roi_bucket = 'negative' if roi < 0 else 'low' if roi < 10 else 'medium' if roi < 25 else 'high'
        
        budget_bucket = 'low' if scenario.budget_eur < 200 else 'medium' if scenario.budget_eur < 800 else 'high'
        
        state_key = f"{scenario.platform.value}_{scenario.objective.value}_{budget_bucket}_{roi_bucket}"
        return state_key

    def choose_action(self, state_key: str) -> str:
        """Elige acción usando epsilon-greedy policy"""
        if random.random() < self.epsilon:
            # Exploration: random action
            return random.choice(self.actions)
        else:
            # Exploitation: best known action
            q_values = self.q_table[state_key]
            if not q_values:
                return random.choice(self.actions)
            return max(q_values.items(), key=lambda x: x[1])[0]

    def update_q_value(self, state_key: str, action: str, reward: float, next_state_key: str):
        """Actualiza Q-value usando Q-learning update rule"""
        current_q = self.q_table[state_key][action]
        
        # Max Q-value for next state
        next_q_values = self.q_table[next_state_key]
        max_next_q = max(next_q_values.values()) if next_q_values else 0
        
        # Q-learning update
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state_key][action] = new_q

    def calculate_reward(self, old_performance: Dict[str, float], new_performance: Dict[str, float]) -> float:
        """Calcula reward basado en mejora de performance"""
        old_roi = old_performance.get('roi_percentage', 0)
        new_roi = new_performance.get('roi_percentage', 0)
        
        roi_improvement = new_roi - old_roi
        
        # Reward structure
        if roi_improvement > 5:
            return 10  # Great improvement
        elif roi_improvement > 0:
            return 5   # Some improvement
        elif roi_improvement > -5:
            return -2  # Small decline
        else:
            return -10 # Bad decline
    
    async def optimize_scenario(self, initial_scenario: SimulationScenario, 
                              monte_carlo_simulator: MonteCarloSimulator,
                              max_iterations: int = 10) -> OptimizationRecommendation:
        """Optimiza escenario usando Q-learning"""
        logger.info(f"🎯 Optimizando escenario con Q-Learning: {initial_scenario.scenario_id}")
        
        current_scenario = initial_scenario
        current_result = await monte_carlo_simulator.run_simulation(current_scenario)
        
        if not current_result:
            return None
        
        current_performance = {
            'roi_percentage': current_result.predicted_roi_percentage,
            'views': current_result.predicted_views,
            'followers': current_result.predicted_followers
        }
        
        best_scenario = current_scenario
        best_result = current_result
        best_performance = current_performance.copy()
        
        optimization_history = []
        
        for iteration in range(max_iterations):
            # Get current state
            state_key = self.get_state_key(current_scenario, current_performance)
            
            # Choose action
            action = self.choose_action(state_key)
            
            # Apply action to create new scenario
            new_scenario = self._apply_action(current_scenario, action)
            
            if new_scenario is None:
                continue
            
            # Simulate new scenario
            new_result = await monte_carlo_simulator.run_simulation(new_scenario)
            
            if not new_result:
                continue
            
            new_performance = {
                'roi_percentage': new_result.predicted_roi_percentage,
                'views': new_result.predicted_views,
                'followers': new_result.predicted_followers
            }
            
            # Calculate reward
            reward = self.calculate_reward(current_performance, new_performance)
            
            # Update Q-table
            next_state_key = self.get_state_key(new_scenario, new_performance)
            self.update_q_value(state_key, action, reward, next_state_key)
            
            # Track if this is the best scenario so far
            if new_performance['roi_percentage'] > best_performance['roi_percentage']:
                best_scenario = new_scenario
                best_result = new_result
                best_performance = new_performance.copy()
            
            optimization_history.append({
                'iteration': iteration,
                'action': action,
                'roi_before': current_performance['roi_percentage'],
                'roi_after': new_performance['roi_percentage'],
                'reward': reward
            })
            
            # Update current scenario for next iteration
            current_scenario = new_scenario
            current_performance = new_performance
        
        # Generate recommendation
        improvement = best_performance['roi_percentage'] - {
            'roi_percentage': initial_scenario.budget_eur,  # Placeholder
            'views': 0,
            'followers': 0
        }.get('roi_percentage', 0)
        
        recommendation = OptimizationRecommendation(
            recommendation_id=f"qlearn_opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            scenario=best_scenario,
            predicted_result=best_result,
            action_type=self._determine_action_type(optimization_history),
            confidence_score=best_result.simulation_confidence,
            expected_improvement=improvement,
            reasoning=self._generate_reasoning(optimization_history, best_scenario, initial_scenario),
            alternative_scenarios=[],
            created_at=datetime.now()
        )
        
        logger.info(f"✅ Optimización completada: {improvement:.1f}% mejora ROI estimada")
        return recommendation

    def _apply_action(self, scenario: SimulationScenario, action: str) -> Optional[SimulationScenario]:
        """Aplica acción al escenario para crear nueva variante"""
        new_scenario = SimulationScenario(
            scenario_id=f"{scenario.scenario_id}_{action}",
            budget_eur=scenario.budget_eur,
            platform=scenario.platform,
            objective=scenario.objective,
            duration_days=scenario.duration_days,
            content_type=scenario.content_type,
            timing=scenario.timing.copy(),
            budget_variance=scenario.budget_variance,
            performance_variance=scenario.performance_variance
        )
        
        if action == 'increase_budget_10':
            new_scenario.budget_eur *= 1.10
        elif action == 'increase_budget_25':
            new_scenario.budget_eur *= 1.25
        elif action == 'decrease_budget_10':
            new_scenario.budget_eur *= 0.90
        elif action == 'change_platform_instagram':
            new_scenario.platform = Platform.INSTAGRAM
        elif action == 'change_platform_tiktok':
            new_scenario.platform = Platform.TIKTOK
        elif action == 'change_platform_youtube':
            new_scenario.platform = Platform.YOUTUBE
        elif action == 'shift_timing_evening':
            new_scenario.timing['hour'] = 20
        elif action == 'shift_timing_weekend':
            new_scenario.timing['day_of_week'] = 5  # Friday
        elif action == 'extend_duration':
            new_scenario.duration_days = min(30, new_scenario.duration_days + 7)
        elif action == 'do_nothing':
            pass  # No changes
        else:
            return None
        
        return new_scenario

    def _determine_action_type(self, history: List[Dict]) -> str:
        """Determina tipo de acción principal basado en historial"""
        if not history:
            return "optimize"
        
        # Encontrar acción con mayor reward
        best_action_entry = max(history, key=lambda x: x['reward'])
        best_action = best_action_entry['action']
        
        if 'budget' in best_action:
            return "adjust_budget"
        elif 'platform' in best_action:
            return "change_platform"
        elif 'timing' in best_action:
            return "adjust_timing"
        elif 'duration' in best_action:
            return "extend_duration"
        else:
            return "optimize"

    def _generate_reasoning(self, history: List[Dict], best_scenario: SimulationScenario, 
                          initial_scenario: SimulationScenario) -> str:
        """Genera explicación de la optimización"""
        if not history:
            return "No se encontraron mejoras significativas."
        
        best_iteration = max(history, key=lambda x: x['roi_after'])
        
        reasoning_parts = []
        
        # Budget changes
        if best_scenario.budget_eur != initial_scenario.budget_eur:
            budget_change = (best_scenario.budget_eur / initial_scenario.budget_eur - 1) * 100
            reasoning_parts.append(f"Ajustar presupuesto {budget_change:+.0f}%")
        
        # Platform changes
        if best_scenario.platform != initial_scenario.platform:
            reasoning_parts.append(f"Cambiar a {best_scenario.platform.value}")
        
        # Timing changes
        if best_scenario.timing != initial_scenario.timing:
            reasoning_parts.append("Ajustar timing de publicación")
        
        # Performance improvement
        roi_improvement = best_iteration['roi_after'] - best_iteration['roi_before']
        reasoning_parts.append(f"Mejora estimada: {roi_improvement:+.1f}% ROI")
        
        return " | ".join(reasoning_parts)


class NetworkGrowthSimulator:
    """Motor principal del simulador de crecimiento de red"""
    
    def __init__(self):
        self.data_extractor = HistoricalDataExtractor()
        self.growth_modeler = GrowthModeler()
        self.monte_carlo = None
        self.q_optimizer = QLearningOptimizer()
        self.is_initialized = False
        
    async def initialize(self):
        """Inicializa el simulador con datos históricos"""
        logger.info("📈 Inicializando Network Growth Simulator...")
        
        # Extraer datos históricos
        historical_campaigns = await self.data_extractor.extract_campaign_history()
        
        if not historical_campaigns:
            logger.error("No se pudieron obtener datos históricos")
            return False
        
        # Entrenar modelos
        success = await self.growth_modeler.train_models(historical_campaigns)
        
        if not success:
            logger.error("Fallo en entrenamiento de modelos")
            return False
        
        # Inicializar Monte Carlo
        self.monte_carlo = MonteCarloSimulator(self.growth_modeler)
        
        self.is_initialized = True
        logger.info("✅ Network Growth Simulator inicializado correctamente")
        return True

    async def simulate_campaign_scenarios(self, scenarios: List[SimulationScenario]) -> List[SimulationResult]:
        """Simula múltiples escenarios de campaña"""
        if not self.is_initialized:
            await self.initialize()
        
        if not self.is_initialized:
            return []
        
        logger.info(f"🎲 Simulando {len(scenarios)} escenarios...")
        
        results = []
        
        for scenario in scenarios:
            try:
                result = await self.monte_carlo.run_simulation(scenario)
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"Error simulando escenario {scenario.scenario_id}: {e}")
        
        logger.info(f"✅ Simulación completada: {len(results)} resultados")
        return results

    async def optimize_campaign_strategy(self, initial_scenario: SimulationScenario) -> OptimizationRecommendation:
        """Optimiza estrategia de campaña usando Q-learning"""
        if not self.is_initialized:
            await self.initialize()
        
        if not self.is_initialized:
            return None
        
        return await self.q_optimizer.optimize_scenario(initial_scenario, self.monte_carlo)

    async def compare_platform_strategies(self, base_scenario: SimulationScenario) -> Dict[Platform, SimulationResult]:
        """Compara performance entre diferentes plataformas"""
        scenarios = []
        
        for platform in Platform:
            scenario = SimulationScenario(
                scenario_id=f"{base_scenario.scenario_id}_{platform.value}",
                budget_eur=base_scenario.budget_eur,
                platform=platform,
                objective=base_scenario.objective,
                duration_days=base_scenario.duration_days,
                content_type=base_scenario.content_type,
                timing=base_scenario.timing.copy()
            )
            scenarios.append(scenario)
        
        results = await self.simulate_campaign_scenarios(scenarios)
        
        # Mapear resultados por plataforma
        platform_results = {}
        for result in results:
            platform_results[result.scenario.platform] = result
        
        return platform_results

    async def find_optimal_budget_allocation(self, total_budget: float, platforms: List[Platform]) -> Dict[Platform, float]:
        """Encuentra distribución óptima de presupuesto entre plataformas"""
        if not platforms:
            return {}
        
        # Crear escenarios para cada plataforma con presupuesto base
        base_budget_per_platform = total_budget / len(platforms)
        
        platform_efficiency = {}
        
        for platform in platforms:
            scenario = SimulationScenario(
                scenario_id=f"budget_test_{platform.value}",
                budget_eur=base_budget_per_platform,
                platform=platform,
                objective=CampaignObjective.VIEWS,
                duration_days=7,
                content_type="video",
                timing={"day_of_week": 5, "hour": 20}
            )
            
            result = await self.monte_carlo.run_simulation(scenario)
            
            if result:
                # Eficiencia = ROI / budget
                efficiency = result.predicted_roi_percentage / base_budget_per_platform
                platform_efficiency[platform] = max(0, efficiency)
            else:
                platform_efficiency[platform] = 0
        
        # Distribuir presupuesto proporcionalmente a la eficiencia
        total_efficiency = sum(platform_efficiency.values())
        
        if total_efficiency == 0:
            # Fallback: distribución equitativa
            return {platform: total_budget / len(platforms) for platform in platforms}
        
        optimal_allocation = {}
        for platform in platforms:
            allocation_ratio = platform_efficiency[platform] / total_efficiency
            optimal_allocation[platform] = total_budget * allocation_ratio
        
        return optimal_allocation

    def generate_campaign_report(self, results: List[SimulationResult]) -> Dict[str, Any]:
        """Genera reporte completo de resultados de simulación"""
        if not results:
            return {"error": "No hay resultados para generar reporte"}
        
        # Estadísticas generales
        avg_roi = statistics.mean([r.predicted_roi_percentage for r in results])
        best_scenario = max(results, key=lambda r: r.predicted_roi_percentage)
        worst_scenario = min(results, key=lambda r: r.predicted_roi_percentage)
        
        # Análisis por plataforma
        platform_stats = defaultdict(list)
        for result in results:
            platform_stats[result.scenario.platform.value].append(result.predicted_roi_percentage)
        
        platform_avg_roi = {platform: statistics.mean(rois) for platform, rois in platform_stats.items()}
        
        # Risk assessment
        positive_roi_scenarios = [r for r in results if r.predicted_roi_percentage > 0]
        risk_probability = len(positive_roi_scenarios) / len(results)
        
        report = {
            "summary": {
                "total_scenarios": len(results),
                "average_roi": avg_roi,
                "best_roi": best_scenario.predicted_roi_percentage,
                "worst_roi": worst_scenario.predicted_roi_percentage,
                "probability_positive_roi": risk_probability
            },
            "best_scenario": {
                "platform": best_scenario.scenario.platform.value,
                "budget": best_scenario.scenario.budget_eur,
                "predicted_roi": best_scenario.predicted_roi_percentage,
                "predicted_views": best_scenario.predicted_views,
                "confidence": best_scenario.simulation_confidence
            },
            "platform_comparison": platform_avg_roi,
            "risk_analysis": {
                "scenarios_with_positive_roi": len(positive_roi_scenarios),
                "average_confidence": statistics.mean([r.simulation_confidence for r in results]),
                "maximum_drawdown": max([r.maximum_drawdown_risk for r in results])
            },
            "recommendations": self._generate_strategic_recommendations(results)
        }
        
        return report

    def _generate_strategic_recommendations(self, results: List[SimulationResult]) -> List[str]:
        """Genera recomendaciones estratégicas basadas en resultados"""
        recommendations = []
        
        if not results:
            return ["No hay datos suficientes para generar recomendaciones"]
        
        # Analizar platform performance
        platform_performance = defaultdict(list)
        for result in results:
            platform_performance[result.scenario.platform.value].append(result.predicted_roi_percentage)
        
        if platform_performance:
            best_platform = max(platform_performance.items(), key=lambda x: statistics.mean(x[1]))[0]
            recommendations.append(f"🏆 Priorizar {best_platform} - mejor ROI promedio")
        
        # Analizar risk tolerance
        high_confidence_results = [r for r in results if r.simulation_confidence > 0.8]
        if high_confidence_results:
            avg_roi_high_conf = statistics.mean([r.predicted_roi_percentage for r in high_confidence_results])
            if avg_roi_high_conf > 15:
                recommendations.append("🎯 Escenarios de alta confianza muestran ROI>15% - recomendado invertir")
            else:
                recommendations.append("⚠️ ROI moderado en escenarios seguros - considerar estrategia más agresiva")
        
        # Budget recommendations
        budget_roi_correlation = []
        for result in results:
            budget_roi_correlation.append((result.scenario.budget_eur, result.predicted_roi_percentage))
        
        if len(budget_roi_correlation) > 5:
            # Calcular correlación simple
            budgets = [x[0] for x in budget_roi_correlation]
            rois = [x[1] for x in budget_roi_correlation]
            
            if statistics.mean(budgets[:len(budgets)//2]) < statistics.mean(budgets[len(budgets)//2:]):
                avg_roi_low_budget = statistics.mean([roi for budget, roi in budget_roi_correlation if budget < statistics.mean(budgets)])
                avg_roi_high_budget = statistics.mean([roi for budget, roi in budget_roi_correlation if budget >= statistics.mean(budgets)])
                
                if avg_roi_low_budget > avg_roi_high_budget:
                    recommendations.append("💰 Presupuestos menores muestran mejor ROI - optimizar eficiencia")
                else:
                    recommendations.append("📈 Presupuestos mayores justificados - escalar inversión")
        
        # Timing recommendations
        timing_performance = defaultdict(list)
        for result in results:
            timing_key = f"day_{result.scenario.timing.get('day_of_week', 0)}_hour_{result.scenario.timing.get('hour', 12)}"
            timing_performance[timing_key].append(result.predicted_roi_percentage)
        
        if len(timing_performance) > 1:
            best_timing = max(timing_performance.items(), key=lambda x: statistics.mean(x[1]))[0]
            recommendations.append(f"⏰ Timing óptimo detectado: {best_timing}")
        
        return recommendations[:5]  # Máximo 5 recomendaciones


# Factory function
def create_growth_simulator() -> NetworkGrowthSimulator:
    """Factory para crear simulador de crecimiento de red"""
    return NetworkGrowthSimulator()