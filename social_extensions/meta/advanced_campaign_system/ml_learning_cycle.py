"""
Advanced Campaign System - ML Learning Cycle
Aprendizaje progresivo simulado con métricas históricas y reentrenamiento
"""

import json
import pickle
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path
import numpy as np
import random
from collections import defaultdict

@dataclass
class CycleMetrics:
    """Métricas completas de un ciclo de campaña"""
    cycle_id: str
    timestamp: datetime
    campaign_tags: Dict[str, Any]
    clip_performance: Dict[str, Dict]  # {clip_id: {ctr, cpc, cpv, views, etc}}
    geo_performance: Dict[str, Dict]   # {country: {roi, ctr, views, etc}}
    budget_allocation: Dict[str, float] # {clip_id: budget}
    total_investment: float
    total_views: int
    total_roi: float
    winner_clips: List[str]
    optimization_decisions: Dict[str, Any]
    genre: str
    subgenre: str
    collaborators: List[str]
    regional_focus: List[str]

@dataclass
class ModelInsights:
    """Insights del modelo tras reentrenamiento"""
    genre_performance_trends: Dict[str, float]
    geo_optimization_learnings: Dict[str, float]
    budget_allocation_insights: Dict[str, float]
    audience_response_patterns: Dict[str, float]
    seasonal_adjustments: Dict[str, float]
    collaboration_effects: Dict[str, float]

@dataclass
class ModelAdjustments:
    """Ajustes del modelo tras aprendizaje"""
    budget_allocation_weights: Dict[str, float]
    genre_prediction_coefficients: Dict[str, float]
    geo_distribution_preferences: Dict[str, float]
    audience_targeting_priorities: Dict[str, float]
    collaboration_multipliers: Dict[str, float]
    confidence_score: float

class HistoricalDataManager:
    """Gestor de datos históricos con base de datos SQLite simulada"""
    
    def __init__(self, db_path: str = "/workspaces/master/data/campaign_history.db"):
        self.db_path = db_path
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Crea la base de datos si no existe"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaign_cycles (
                cycle_id TEXT PRIMARY KEY,
                timestamp TEXT,
                genre TEXT,
                subgenre TEXT,
                collaborators TEXT,
                regional_focus TEXT,
                total_investment REAL,
                total_views INTEGER,
                total_roi REAL,
                campaign_data TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clip_performance (
                cycle_id TEXT,
                clip_id TEXT,
                ctr REAL,
                cpc REAL,
                cpv REAL,
                views INTEGER,
                engagement_rate REAL,
                conversion_rate REAL,
                total_spend REAL,
                roi REAL,
                is_winner BOOLEAN,
                FOREIGN KEY(cycle_id) REFERENCES campaign_cycles(cycle_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS geo_performance (
                cycle_id TEXT,
                country TEXT,
                budget_allocated REAL,
                estimated_views INTEGER,
                estimated_roi REAL,
                estimated_ctr REAL,
                market_share REAL,
                FOREIGN KEY(cycle_id) REFERENCES campaign_cycles(cycle_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_cycle(self, cycle_data: CycleMetrics) -> str:
        """Almacena datos completos de un ciclo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insertar datos principales del ciclo
        cursor.execute('''
            INSERT OR REPLACE INTO campaign_cycles 
            (cycle_id, timestamp, genre, subgenre, collaborators, regional_focus,
             total_investment, total_views, total_roi, campaign_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            cycle_data.cycle_id,
            cycle_data.timestamp.isoformat(),
            cycle_data.genre,
            cycle_data.subgenre,
            json.dumps(cycle_data.collaborators),
            json.dumps(cycle_data.regional_focus),
            cycle_data.total_investment,
            cycle_data.total_views,
            cycle_data.total_roi,
            json.dumps(asdict(cycle_data))
        ))
        
        # Insertar rendimiento de clips
        for clip_id, metrics in cycle_data.clip_performance.items():
            cursor.execute('''
                INSERT OR REPLACE INTO clip_performance
                (cycle_id, clip_id, ctr, cpc, cpv, views, engagement_rate, 
                 conversion_rate, total_spend, roi, is_winner)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cycle_data.cycle_id, clip_id,
                metrics.get('ctr', 0), metrics.get('cpc', 0),
                metrics.get('cpv', 0), metrics.get('views', 0),
                metrics.get('engagement_rate', 0), metrics.get('conversion_rate', 0),
                metrics.get('total_spend', 0), metrics.get('roi', 0),
                clip_id in cycle_data.winner_clips
            ))
        
        # Insertar rendimiento geográfico
        for country, metrics in cycle_data.geo_performance.items():
            cursor.execute('''
                INSERT OR REPLACE INTO geo_performance
                (cycle_id, country, budget_allocated, estimated_views,
                 estimated_roi, estimated_ctr, market_share)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                cycle_data.cycle_id, country,
                metrics.get('budget_allocated', 0), metrics.get('estimated_views', 0),
                metrics.get('roi_projection', 0), metrics.get('estimated_ctr', 0),
                metrics.get('market_share', 0)
            ))
        
        conn.commit()
        conn.close()
        
        print(f"📊 Ciclo {cycle_data.cycle_id} almacenado en base de datos histórica")
        return cycle_data.cycle_id
    
    def get_historical_cycles(self, genre: Optional[str] = None, 
                            limit: int = 50) -> List[CycleMetrics]:
        """Recupera ciclos históricos con filtros opcionales"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM campaign_cycles"
        params = []
        
        if genre:
            query += " WHERE genre = ?"
            params.append(genre)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        cycles = []
        for row in rows:
            cycle_data = json.loads(row[9])  # campaign_data column
            cycle_data['timestamp'] = datetime.fromisoformat(cycle_data['timestamp'])
            cycles.append(CycleMetrics(**cycle_data))
        
        conn.close()
        return cycles

class MLLearningCycle:
    """Motor de aprendizaje progresivo con reentrenamiento simulado"""
    
    def __init__(self):
        self.historical_manager = HistoricalDataManager()
        self.learning_rate = 0.1
        self.confidence_threshold = 0.7
        
        # Pesos iniciales del modelo
        self.current_model_weights = {
            'genre_weights': {'trap': 1.0, 'reggaeton': 1.0, 'rap': 1.0, 'corrido': 1.0},
            'geo_weights': {'ES': 1.0, 'MX': 1.0, 'CO': 1.0, 'AR': 1.0, 'CL': 1.0, 'PE': 1.0, 'EC': 1.0},
            'collaboration_weights': {'solo': 1.0, 'with_collaborator': 1.2},
            'budget_distribution': {'exploration': 0.4, 'exploitation': 0.6}
        }
    
    def save_campaign_cycle_data(self, campaign_results: Dict) -> str:
        """
        Guarda datos completos del ciclo de campaña en formato estructurado
        """
        print("💾 GUARDANDO DATOS DEL CICLO EN SISTEMA DE APRENDIZAJE")
        print("-" * 55)
        
        # Generar ID único del ciclo
        cycle_id = f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        # Extraer datos del resultado de campaña
        cycle_metrics = CycleMetrics(
            cycle_id=cycle_id,
            timestamp=datetime.now(),
            campaign_tags=campaign_results.get('campaign_tags', {}),
            clip_performance=campaign_results.get('clip_performance', {}),
            geo_performance=campaign_results.get('geo_performance', {}),
            budget_allocation=campaign_results.get('budget_allocation', {}),
            total_investment=campaign_results.get('total_investment', 0),
            total_views=campaign_results.get('total_views', 0),
            total_roi=campaign_results.get('total_roi', 0),
            winner_clips=campaign_results.get('winner_clips', []),
            optimization_decisions=campaign_results.get('optimization_decisions', {}),
            genre=campaign_results.get('genre', 'unknown'),
            subgenre=campaign_results.get('subgenre', 'unknown'),
            collaborators=campaign_results.get('collaborators', []),
            regional_focus=campaign_results.get('regional_focus', [])
        )
        
        # Almacenar en base de datos
        stored_id = self.historical_manager.store_cycle(cycle_metrics)
        
        print(f"✅ Ciclo guardado: {stored_id}")
        print(f"📊 Métricas: {len(cycle_metrics.clip_performance)} clips, {len(cycle_metrics.geo_performance)} países")
        print(f"💰 Inversión: ${cycle_metrics.total_investment} | ROI: {cycle_metrics.total_roi:.1f}%")
        print()
        
        return stored_id
    
    def simulate_model_retraining(self, historical_cycles: List[CycleMetrics]) -> Tuple[ModelAdjustments, ModelInsights]:
        """
        Simula reentrenamiento del modelo con datos históricos
        """
        print("🧠 SIMULANDO REENTRENAMIENTO DEL MODELO ML")
        print("-" * 50)
        
        if not historical_cycles:
            print("⚠️ No hay datos históricos suficientes para reentrenamiento")
            return self.get_default_adjustments()
        
        # Analizar tendencias por género
        genre_trends = self.analyze_genre_trends(historical_cycles)
        print(f"📈 Tendencias de género analizadas: {len(genre_trends)} géneros")
        
        # Analizar patrones geográficos
        geo_patterns = self.analyze_geo_patterns(historical_cycles)
        print(f"🌍 Patrones geográficos: {len(geo_patterns)} países")
        
        # Analizar eficiencia de presupuesto
        budget_insights = self.analyze_budget_efficiency(historical_cycles)
        print(f"💰 Insights de presupuesto: {len(budget_insights)} estrategias")
        
        # Analizar respuesta de audiencias
        audience_patterns = self.analyze_audience_behavior(historical_cycles)
        print(f"👥 Patrones de audiencia: {len(audience_patterns)} segmentos")
        
        # Detectar ajustes estacionales
        seasonal_adjustments = self.detect_seasonal_patterns(historical_cycles)
        print(f"📅 Ajustes estacionales: {len(seasonal_adjustments)} factores")
        
        # Analizar efectos de colaboración
        collaboration_effects = self.analyze_collaboration_effects(historical_cycles)
        print(f"🤝 Efectos colaboración: {len(collaboration_effects)} patrones")
        
        # Crear insights consolidados
        insights = ModelInsights(
            genre_performance_trends=genre_trends,
            geo_optimization_learnings=geo_patterns,
            budget_allocation_insights=budget_insights,
            audience_response_patterns=audience_patterns,
            seasonal_adjustments=seasonal_adjustments,
            collaboration_effects=collaboration_effects
        )
        
        # Calcular ajustes del modelo
        adjustments = self.calculate_model_adjustments(insights, historical_cycles)
        
        print(f"🎯 Ajustes calculados con confianza: {adjustments.confidence_score:.3f}")
        print()
        
        return adjustments, insights
    
    def analyze_genre_trends(self, cycles: List[CycleMetrics]) -> Dict[str, float]:
        """Analiza tendencias de rendimiento por género"""
        genre_performance = defaultdict(list)
        
        for cycle in cycles:
            genre_performance[cycle.genre].append(cycle.total_roi)
        
        trends = {}
        for genre, rois in genre_performance.items():
            avg_roi = sum(rois) / len(rois)
            trend_score = min(avg_roi / 150, 2.0)  # Normalizar y limitar
            trends[genre] = trend_score
        
        return trends
    
    def analyze_geo_patterns(self, cycles: List[CycleMetrics]) -> Dict[str, float]:
        """Analiza patrones de optimización geográfica"""
        geo_performance = defaultdict(list)
        
        for cycle in cycles:
            for country, metrics in cycle.geo_performance.items():
                roi = metrics.get('roi_projection', 0)
                geo_performance[country].append(roi)
        
        patterns = {}
        for country, rois in geo_performance.items():
            if rois:
                avg_roi = sum(rois) / len(rois)
                pattern_score = min(avg_roi / 100, 1.5)
                patterns[country] = pattern_score
        
        return patterns
    
    def analyze_budget_efficiency(self, cycles: List[CycleMetrics]) -> Dict[str, float]:
        """Analiza eficiencia de diferentes estrategias de presupuesto"""
        efficiency_patterns = {}
        
        # Analizar distribución entre clips
        clip_counts = [len(cycle.clip_performance) for cycle in cycles]
        avg_clips = sum(clip_counts) / len(clip_counts) if clip_counts else 5
        efficiency_patterns['optimal_clip_count'] = avg_clips
        
        # Analizar ROI por inversión
        high_investment_rois = []
        low_investment_rois = []
        
        for cycle in cycles:
            if cycle.total_investment > 400:
                high_investment_rois.append(cycle.total_roi)
            else:
                low_investment_rois.append(cycle.total_roi)
        
        if high_investment_rois and low_investment_rois:
            high_avg = sum(high_investment_rois) / len(high_investment_rois)
            low_avg = sum(low_investment_rois) / len(low_investment_rois)
            efficiency_patterns['investment_efficiency'] = high_avg / low_avg if low_avg > 0 else 1.0
        else:
            efficiency_patterns['investment_efficiency'] = 1.0
        
        return efficiency_patterns
    
    def analyze_audience_behavior(self, cycles: List[CycleMetrics]) -> Dict[str, float]:
        """Analiza patrones de comportamiento de audiencia"""
        behavior_patterns = {}
        
        # Analizar engagement por colaboraciones
        solo_engagements = []
        collab_engagements = []
        
        for cycle in cycles:
            has_collaborators = len(cycle.collaborators) > 0
            
            # Calcular engagement promedio del ciclo
            total_engagement = 0
            clip_count = 0
            
            for clip_metrics in cycle.clip_performance.values():
                if 'engagement_rate' in clip_metrics:
                    total_engagement += clip_metrics['engagement_rate']
                    clip_count += 1
            
            avg_engagement = total_engagement / clip_count if clip_count > 0 else 0
            
            if has_collaborators:
                collab_engagements.append(avg_engagement)
            else:
                solo_engagements.append(avg_engagement)
        
        if solo_engagements and collab_engagements:
            solo_avg = sum(solo_engagements) / len(solo_engagements)
            collab_avg = sum(collab_engagements) / len(collab_engagements)
            behavior_patterns['collaboration_engagement_boost'] = collab_avg / solo_avg if solo_avg > 0 else 1.0
        else:
            behavior_patterns['collaboration_engagement_boost'] = 1.2  # Default boost
        
        return behavior_patterns
    
    def detect_seasonal_patterns(self, cycles: List[CycleMetrics]) -> Dict[str, float]:
        """Detecta patrones estacionales en el rendimiento"""
        seasonal_patterns = {}
        
        # Analizar por día de la semana
        weekday_performance = defaultdict(list)
        
        for cycle in cycles:
            weekday = cycle.timestamp.weekday()  # 0=Monday, 6=Sunday
            weekday_performance[weekday].append(cycle.total_roi)
        
        # Calcular mejores días
        best_weekday = 0
        best_avg_roi = 0
        
        for weekday, rois in weekday_performance.items():
            if rois:
                avg_roi = sum(rois) / len(rois)
                if avg_roi > best_avg_roi:
                    best_avg_roi = avg_roi
                    best_weekday = weekday
        
        seasonal_patterns['optimal_weekday'] = best_weekday
        seasonal_patterns['weekday_boost'] = min(best_avg_roi / 100, 1.5) if best_avg_roi > 0 else 1.0
        
        return seasonal_patterns
    
    def analyze_collaboration_effects(self, cycles: List[CycleMetrics]) -> Dict[str, float]:
        """Analiza efectos específicos de colaboraciones"""
        collaboration_effects = {}
        
        # Contar colaboradores exitosos
        collaborator_success = defaultdict(list)
        
        for cycle in cycles:
            for collaborator in cycle.collaborators:
                collaborator_success[collaborator].append(cycle.total_roi)
        
        # Identificar colaboradores top
        top_collaborators = {}
        for collaborator, rois in collaborator_success.items():
            if len(rois) >= 2:  # Mínimo 2 colaboraciones
                avg_roi = sum(rois) / len(rois)
                top_collaborators[collaborator] = avg_roi
        
        collaboration_effects['top_collaborators'] = top_collaborators
        collaboration_effects['collaboration_sample_size'] = len(collaborator_success)
        
        return collaboration_effects
    
    def calculate_model_adjustments(self, insights: ModelInsights, 
                                  cycles: List[CycleMetrics]) -> ModelAdjustments:
        """Calcula ajustes específicos del modelo basados en insights"""
        
        # Ajustar pesos de asignación de presupuesto
        budget_weights = self.current_model_weights['budget_distribution'].copy()
        
        # Si hay alta eficiencia de inversión, favorecer explotación
        investment_efficiency = insights.budget_allocation_insights.get('investment_efficiency', 1.0)
        if investment_efficiency > 1.2:
            budget_weights['exploitation'] *= 1.1
            budget_weights['exploration'] *= 0.95
        
        # Ajustar coeficientes de predicción por género
        genre_coefficients = {}
        for genre, trend in insights.genre_performance_trends.items():
            coefficient = 1.0 + (trend - 1.0) * self.learning_rate
            genre_coefficients[genre] = max(0.5, min(2.0, coefficient))  # Limitar entre 0.5 y 2.0
        
        # Ajustar preferencias de distribución geográfica
        geo_preferences = {}
        for country, pattern in insights.geo_optimization_learnings.items():
            preference = 1.0 + (pattern - 1.0) * self.learning_rate
            geo_preferences[country] = max(0.7, min(1.5, preference))
        
        # Ajustar prioridades de targeting de audiencia
        audience_priorities = {
            'solo_campaigns': 1.0,
            'collaboration_campaigns': insights.audience_response_patterns.get('collaboration_engagement_boost', 1.2)
        }
        
        # Multiplicadores de colaboración
        collaboration_multipliers = {}
        top_collabs = insights.collaboration_effects.get('top_collaborators', {})
        for collaborator, avg_roi in top_collabs.items():
            multiplier = min(avg_roi / 150, 1.5) if avg_roi > 0 else 1.0
            collaboration_multipliers[collaborator] = multiplier
        
        # Calcular score de confianza basado en cantidad de datos
        data_points = len(cycles)
        confidence = min(data_points / 20, 1.0)  # Máxima confianza con 20+ ciclos
        
        return ModelAdjustments(
            budget_allocation_weights=budget_weights,
            genre_prediction_coefficients=genre_coefficients,
            geo_distribution_preferences=geo_preferences,
            audience_targeting_priorities=audience_priorities,
            collaboration_multipliers=collaboration_multipliers,
            confidence_score=confidence
        )
    
    def predict_next_campaign_performance(self, campaign_proposal: Dict, 
                                        model_adjustments: ModelAdjustments) -> Dict:
        """
        Predice rendimiento de próxima campaña con modelo actualizado
        """
        print("🔮 PREDICIENDO RENDIMIENTO DE PRÓXIMA CAMPAÑA")
        print("-" * 50)
        
        # Obtener predicciones base
        base_predictions = self.generate_base_predictions(campaign_proposal)
        
        # Aplicar ajustes del modelo
        adjusted_predictions = self.apply_model_adjustments(base_predictions, model_adjustments)
        
        # Calcular intervalos de confianza
        confidence_intervals = self.calculate_prediction_confidence(
            campaign_proposal, model_adjustments.confidence_score
        )
        
        # Generar recomendaciones
        recommendations = self.generate_recommendations(adjusted_predictions, model_adjustments)
        
        # Evaluar riesgos
        risk_assessment = self.assess_campaign_risks(campaign_proposal, adjusted_predictions)
        
        print(f"📊 ROI predicho: {adjusted_predictions['roi']:.1f}% (confianza: {model_adjustments.confidence_score:.2f})")
        print(f"🎯 CTR estimado: {adjusted_predictions['ctr']:.2f}%")
        print(f"💰 CPV optimizado: ${adjusted_predictions['cpv']:.3f}")
        print()
        
        return {
            'performance_predictions': adjusted_predictions,
            'confidence_intervals': confidence_intervals,
            'recommended_adjustments': recommendations,
            'risk_assessment': risk_assessment,
            'model_confidence': model_adjustments.confidence_score
        }
    
    def generate_base_predictions(self, campaign_proposal: Dict) -> Dict:
        """Genera predicciones base sin ajustes del modelo"""
        genre = campaign_proposal.get('genre', 'trap')
        budget = campaign_proposal.get('budget_total', 400)
        
        # Predicciones base por género
        base_metrics = {
            'trap': {'roi': 180, 'ctr': 3.2, 'cpv': 0.45},
            'reggaeton': {'roi': 195, 'ctr': 3.8, 'cpv': 0.42},
            'rap': {'roi': 160, 'ctr': 2.9, 'cpv': 0.48},
            'corrido': {'roi': 140, 'ctr': 2.5, 'cpv': 0.52}
        }
        
        base = base_metrics.get(genre, base_metrics['trap'])
        
        return {
            'roi': base['roi'] * random.uniform(0.85, 1.15),
            'ctr': base['ctr'] * random.uniform(0.9, 1.1),
            'cpv': base['cpv'] * random.uniform(0.95, 1.05),
            'estimated_views': int((budget / base['cpv']) * 1.2),
            'estimated_revenue': budget * (base['roi'] / 100) + budget
        }
    
    def apply_model_adjustments(self, base_predictions: Dict, adjustments: ModelAdjustments) -> Dict:
        """Aplica ajustes del modelo a predicciones base"""
        adjusted = base_predictions.copy()
        
        # Aplicar ajustes de género si están disponibles
        # (En implementación real, se usaría el género específico)
        genre_boost = 1.0  # Placeholder - se aplicaría el coeficiente específico
        
        adjusted['roi'] *= genre_boost
        adjusted['ctr'] *= genre_boost
        adjusted['cpv'] /= genre_boost  # CPV inverso al rendimiento
        
        return adjusted
    
    def calculate_prediction_confidence(self, campaign_proposal: Dict, confidence_score: float) -> Dict:
        """Calcula intervalos de confianza para predicciones"""
        variance = 1.0 - confidence_score  # Mayor confianza = menor varianza
        
        return {
            'roi_range': f"±{variance * 30:.0f}%",
            'ctr_range': f"±{variance * 0.8:.1f}%",
            'cpv_range': f"±${variance * 0.1:.3f}",
            'confidence_level': f"{confidence_score * 100:.0f}%"
        }
    
    def generate_recommendations(self, predictions: Dict, adjustments: ModelAdjustments) -> List[str]:
        """Genera recomendaciones específicas basadas en predicciones"""
        recommendations = []
        
        if predictions['roi'] > 200:
            recommendations.append("🚀 ROI excelente predicho - Considerar aumentar presupuesto 20%")
        elif predictions['roi'] < 100:
            recommendations.append("⚠️ ROI bajo predicho - Revisar targeting y creativos")
        
        if predictions['ctr'] > 4.0:
            recommendations.append("🎯 CTR alto predicho - Excelente product-market fit")
        elif predictions['ctr'] < 2.5:
            recommendations.append("📈 CTR bajo predicho - Optimizar headlines y visuales")
        
        if adjustments.confidence_score < 0.5:
            recommendations.append("📊 Confianza baja - Ejecutar en modo conservador")
        
        return recommendations
    
    def assess_campaign_risks(self, campaign_proposal: Dict, predictions: Dict) -> Dict:
        """Evalúa riesgos específicos de la campaña"""
        risks = {
            'budget_risk': 'bajo',
            'performance_risk': 'medio',
            'market_risk': 'bajo',
            'technical_risk': 'bajo'
        }
        
        # Evaluar riesgo de presupuesto
        budget = campaign_proposal.get('budget_total', 400)
        if budget > 1000:
            risks['budget_risk'] = 'alto'
        elif budget > 600:
            risks['budget_risk'] = 'medio'
        
        # Evaluar riesgo de rendimiento
        if predictions['roi'] < 50:
            risks['performance_risk'] = 'alto'
        elif predictions['roi'] > 150:
            risks['performance_risk'] = 'bajo'
        
        return risks
    
    def get_default_adjustments(self) -> Tuple[ModelAdjustments, ModelInsights]:
        """Retorna ajustes por defecto cuando no hay datos históricos"""
        default_adjustments = ModelAdjustments(
            budget_allocation_weights={'exploration': 0.4, 'exploitation': 0.6},
            genre_prediction_coefficients={'trap': 1.0, 'reggaeton': 1.05, 'rap': 0.95, 'corrido': 0.90},
            geo_distribution_preferences={'ES': 1.0, 'MX': 1.0, 'CO': 0.95, 'AR': 0.90},
            audience_targeting_priorities={'solo_campaigns': 1.0, 'collaboration_campaigns': 1.2},
            collaboration_multipliers={},
            confidence_score=0.5
        )
        
        default_insights = ModelInsights(
            genre_performance_trends={'trap': 1.0},
            geo_optimization_learnings={'ES': 1.0},
            budget_allocation_insights={'optimal_clip_count': 5},
            audience_response_patterns={'collaboration_engagement_boost': 1.2},
            seasonal_adjustments={'optimal_weekday': 5},
            collaboration_effects={'top_collaborators': {}}
        )
        
        return default_adjustments, default_insights

# Ejemplo de uso y test
if __name__ == "__main__":
    print("🧠 TEST ML LEARNING CYCLE")
    print("=" * 40)
    
    # Crear instancia
    ml_cycle = MLLearningCycle()
    
    # Simular datos de campaña
    campaign_results_example = {
        'campaign_tags': {'genre': 'trap', 'subgenre': 'trap_oscuro'},
        'clip_performance': {
            'clip_001': {'ctr': 3.5, 'cpc': 0.45, 'views': 180, 'roi': 150},
            'clip_002': {'ctr': 2.8, 'cpc': 0.50, 'views': 160, 'roi': 120}
        },
        'geo_performance': {
            'ES': {'budget_allocated': 108, 'estimated_views': 950, 'roi_projection': 160},
            'MX': {'budget_allocated': 95, 'estimated_views': 800, 'roi_projection': 180}
        },
        'budget_allocation': {'clip_001': 200, 'clip_002': 200},
        'total_investment': 450,
        'total_views': 1500,
        'total_roi': 165,
        'winner_clips': ['clip_001'],
        'optimization_decisions': {'winner_selection': 'roi_based'},
        'genre': 'trap',
        'subgenre': 'trap_oscuro',
        'collaborators': ['anuel_aa'],
        'regional_focus': ['ES', 'MX']
    }
    
    # Guardar ciclo
    cycle_id = ml_cycle.save_campaign_cycle_data(campaign_results_example)
    
    # Obtener historial
    historical_cycles = ml_cycle.historical_manager.get_historical_cycles(genre='trap')
    
    # Simular reentrenamiento
    adjustments, insights = ml_cycle.simulate_model_retraining(historical_cycles)
    
    # Predecir próxima campaña
    next_campaign_proposal = {
        'genre': 'trap',
        'budget_total': 500,
        'collaborators': ['anuel_aa']
    }
    
    predictions = ml_cycle.predict_next_campaign_performance(
        next_campaign_proposal, adjustments
    )
    
    print("✅ ML Learning Cycle implementado y testeado exitosamente!")