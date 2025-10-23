"""
Advanced Campaign System - Geo Distribution
Distribución geográfica adaptativa España/LATAM con reajuste automático
"""

import random
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta

@dataclass
class RegionalData:
    """Datos de rendimiento regional"""
    country_code: str
    avg_ctr: float
    avg_cpm: float
    avg_roi: float
    avg_engagement: float
    conversion_rate: float
    audience_size: int
    competition_level: float

@dataclass
class GeoAllocation:
    """Asignación geográfica de presupuesto"""
    region_budgets: Dict[str, float]
    total_allocated: float
    spain_percentage: float
    latam_percentage: float
    optimization_score: float

class GeoDistribution:
    """Distribución geográfica adaptativa con optimización automática"""
    
    def __init__(self):
        self.spain_fixed_percentage = 0.27  # 27% fijo para España
        self.latam_countries = ['MX', 'CO', 'AR', 'CL', 'PE', 'EC']
        self.performance_history = {}
        
        # Datos base de rendimiento por país (simulados realistas)
        self.country_baselines = {
            'ES': RegionalData('ES', 3.8, 6.2, 185, 9.1, 2.3, 47000000, 0.85),
            'MX': RegionalData('MX', 3.2, 4.1, 165, 8.7, 2.1, 128000000, 0.75),
            'CO': RegionalData('CO', 3.5, 3.8, 175, 9.3, 2.4, 50000000, 0.68),
            'AR': RegionalData('AR', 3.1, 4.3, 155, 8.2, 1.9, 45000000, 0.72),
            'CL': RegionalData('CL', 2.9, 4.8, 140, 7.8, 1.8, 19000000, 0.78),
            'PE': RegionalData('PE', 2.7, 3.2, 135, 8.1, 2.0, 33000000, 0.65),
            'EC': RegionalData('EC', 2.8, 3.5, 130, 7.9, 1.7, 18000000, 0.62)
        }
        
        # Factores de género por región
        self.genre_regional_multipliers = {
            'trap': {
                'ES': 1.15, 'MX': 1.20, 'CO': 1.25, 'AR': 1.10, 'CL': 1.05, 'PE': 1.08, 'EC': 1.12
            },
            'reggaeton': {
                'ES': 1.10, 'MX': 1.30, 'CO': 1.35, 'AR': 1.15, 'CL': 1.08, 'PE': 1.18, 'EC': 1.22
            },
            'rap': {
                'ES': 1.05, 'MX': 1.10, 'CO': 1.12, 'AR': 1.20, 'CL': 1.15, 'PE': 1.05, 'EC': 1.08
            }
        }
    
    def calculate_geo_allocation(self, total_budget: float, genre: str = 'trap', 
                               historical_data: Optional[Dict] = None) -> GeoAllocation:
        """
        Calcula asignación geográfica adaptativa
        """
        print("🌍 CALCULANDO DISTRIBUCIÓN GEOGRÁFICA ADAPTATIVA")
        print("-" * 55)
        
        # Presupuesto fijo España
        spain_budget = total_budget * self.spain_fixed_percentage
        latam_budget = total_budget * (1 - self.spain_fixed_percentage)
        
        print(f"🇪🇸 España (fijo {self.spain_fixed_percentage*100:.0f}%): ${spain_budget:.0f}")
        print(f"🌎 LATAM disponible: ${latam_budget:.0f}")
        print()
        
        # Optimizar distribución LATAM
        if historical_data:
            latam_distribution = self.optimize_latam_distribution(
                latam_budget, historical_data, genre
            )
            optimization_score = self.calculate_optimization_score(historical_data)
        else:
            latam_distribution = self.initial_latam_distribution(latam_budget, genre)
            optimization_score = 0.75  # Score inicial estimado
        
        # Combinar asignaciones
        final_allocation = {
            'ES': spain_budget,
            **latam_distribution
        }
        
        # Verificar total
        total_allocated = sum(final_allocation.values())
        
        print("💰 DISTRIBUCIÓN FINAL:")
        for country, budget in final_allocation.items():
            percentage = (budget / total_budget) * 100
            print(f"  🏴 {country}: ${budget:.0f} ({percentage:.1f}%)")
        
        print(f"\n✅ Total asignado: ${total_allocated:.0f} (diferencia: ${total_budget - total_allocated:.2f})")
        print(f"📊 Score de optimización: {optimization_score:.3f}")
        print()
        
        return GeoAllocation(
            region_budgets=final_allocation,
            total_allocated=total_allocated,
            spain_percentage=self.spain_fixed_percentage,
            latam_percentage=1 - self.spain_fixed_percentage,
            optimization_score=optimization_score
        )
    
    def initial_latam_distribution(self, latam_budget: float, genre: str) -> Dict[str, float]:
        """
        Distribución inicial LATAM basada en potencial de mercado y género
        """
        print("🎯 DISTRIBUCIÓN INICIAL LATAM (sin datos históricos)")
        
        # Scores base por país considerando audiencia y competencia
        base_scores = {}
        genre_multipliers = self.genre_regional_multipliers.get(genre, self.genre_regional_multipliers['trap'])
        
        for country in self.latam_countries:
            country_data = self.country_baselines[country]
            genre_multiplier = genre_multipliers.get(country, 1.0)
            
            # Score compuesto: audiencia (40%) + ROI base (30%) + competencia (30%)
            audience_score = min(country_data.audience_size / 128000000, 1.0)  # Normalizar con México
            roi_score = country_data.avg_roi / 200  # Normalizar
            competition_score = 1 - country_data.competition_level  # Invertir (menos competencia = mejor)
            
            base_score = (audience_score * 0.4) + (roi_score * 0.3) + (competition_score * 0.3)
            base_scores[country] = base_score * genre_multiplier
        
        # Distribuir presupuesto proporcionalmente
        total_score = sum(base_scores.values())
        distribution = {}
        
        for country, score in base_scores.items():
            allocation_percentage = score / total_score
            budget_allocation = latam_budget * allocation_percentage
            distribution[country] = budget_allocation
            
            print(f"  🎯 {country}: Score {score:.3f} → ${budget_allocation:.0f}")
        
        return distribution
    
    def optimize_latam_distribution(self, latam_budget: float, historical_data: Dict, genre: str) -> Dict[str, float]:
        """
        Optimiza distribución LATAM basada en rendimiento histórico
        """
        print("📈 OPTIMIZACIÓN LATAM CON DATOS HISTÓRICOS")
        
        performance_scores = {}
        genre_multipliers = self.genre_regional_multipliers.get(genre, self.genre_regional_multipliers['trap'])
        
        for country in self.latam_countries:
            regional_data = historical_data.get(country, {})
            baseline = self.country_baselines[country]
            genre_multiplier = genre_multipliers.get(country, 1.0)
            
            # Métricas históricas (si existen)
            historical_ctr = regional_data.get('avg_ctr', baseline.avg_ctr)
            historical_roi = regional_data.get('avg_roi', baseline.avg_roi)
            historical_engagement = regional_data.get('avg_engagement', baseline.avg_engagement)
            campaigns_count = regional_data.get('campaigns_count', 1)
            
            # Scores normalizados
            ctr_score = min(historical_ctr / 5.0, 1.0)  # CTR normalizado
            roi_score = min(historical_roi / 300, 1.0)   # ROI normalizado
            engagement_score = min(historical_engagement / 12.0, 1.0)  # Engagement normalizado
            
            # Bonus por experiencia (más campañas = más confianza)
            experience_bonus = min(campaigns_count / 10, 0.2)  # Máximo 20% bonus
            
            # Score final compuesto
            performance_score = (
                (ctr_score * 0.35) + 
                (roi_score * 0.35) + 
                (engagement_score * 0.20) + 
                experience_bonus
            ) * genre_multiplier
            
            performance_scores[country] = performance_score
            
            print(f"  📊 {country}: CTR {historical_ctr:.1f}% | ROI {historical_roi:.0f}% | Score {performance_score:.3f}")
        
        # Distribuir con suavizado (evitar cambios drásticos)
        total_score = sum(performance_scores.values())
        distribution = {}
        
        for country, score in performance_scores.items():
            optimized_percentage = score / total_score
            
            # Suavizado: 70% optimizado + 30% distribución equitativa
            equal_percentage = 1 / len(self.latam_countries)
            final_percentage = (optimized_percentage * 0.7) + (equal_percentage * 0.3)
            
            budget_allocation = latam_budget * final_percentage
            distribution[country] = budget_allocation
        
        return distribution
    
    def calculate_optimization_score(self, historical_data: Dict) -> float:
        """
        Calcula score de optimización basado en datos históricos
        """
        if not historical_data:
            return 0.75
        
        # Evaluar calidad de datos históricos
        countries_with_data = len([c for c in self.latam_countries if c in historical_data])
        data_coverage = countries_with_data / len(self.latam_countries)
        
        # Evaluar consistencia de datos
        consistency_scores = []
        for country in self.latam_countries:
            if country in historical_data:
                data_points = len([k for k in historical_data[country].keys() if k.startswith('avg_')])
                consistency_scores.append(min(data_points / 5, 1.0))  # 5 métricas esperadas
        
        avg_consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.5
        
        # Score final
        optimization_score = (data_coverage * 0.6) + (avg_consistency * 0.4)
        return round(optimization_score, 3)
    
    def simulate_regional_performance(self, allocation: GeoAllocation, genre: str, 
                                    campaign_duration: int = 10) -> Dict[str, Dict]:
        """
        Simula rendimiento por región para próximo ciclo
        """
        print("🎮 SIMULANDO RENDIMIENTO REGIONAL")
        print("-" * 40)
        
        simulated_performance = {}
        genre_multipliers = self.genre_regional_multipliers.get(genre, self.genre_regional_multipliers['trap'])
        
        for country, budget in allocation.region_budgets.items():
            baseline = self.country_baselines[country]
            genre_multiplier = genre_multipliers.get(country, 1.0)
            
            # Calcular métricas simuladas
            effective_cpm = baseline.avg_cpm * random.uniform(0.9, 1.1)
            effective_ctr = baseline.avg_ctr * genre_multiplier * random.uniform(0.85, 1.15)
            
            estimated_impressions = int((budget / effective_cpm) * 1000)
            estimated_clicks = int(estimated_impressions * (effective_ctr / 100))
            estimated_views = int(estimated_clicks * 1.25)  # Views > clicks
            
            # Métricas de engagement
            estimated_engagement = baseline.avg_engagement * genre_multiplier * random.uniform(0.9, 1.1)
            estimated_conversions = int(estimated_views * (baseline.conversion_rate / 100))
            
            # ROI projection
            estimated_revenue = estimated_views * 0.023  # Valor por view
            roi_projection = ((estimated_revenue - budget) / budget) * 100
            
            performance_data = {
                'budget_allocated': budget,
                'estimated_impressions': estimated_impressions,
                'estimated_ctr': round(effective_ctr, 2),
                'estimated_clicks': estimated_clicks,
                'estimated_views': estimated_views,
                'estimated_engagement': round(estimated_engagement, 1),
                'estimated_conversions': estimated_conversions,
                'cpm': round(effective_cpm, 2),
                'estimated_revenue': round(estimated_revenue, 2),
                'roi_projection': round(roi_projection, 1),
                'market_share': round(budget / sum(allocation.region_budgets.values()) * 100, 1)
            }
            
            simulated_performance[country] = performance_data
            
            print(f"🏴 {country}: ${budget:.0f} → {estimated_views:,} views (ROI: {roi_projection:.1f}%)")
        
        print()
        return simulated_performance
    
    def generate_geo_insights(self, performance_data: Dict[str, Dict]) -> Dict:
        """
        Genera insights geográficos para optimización futura
        """
        insights = {
            'best_performing_regions': [],
            'underperforming_regions': [],
            'optimization_opportunities': [],
            'regional_recommendations': {}
        }
        
        # Analizar rendimiento
        roi_threshold_high = 150
        roi_threshold_low = 50
        
        for country, data in performance_data.items():
            roi = data['roi_projection']
            
            if roi > roi_threshold_high:
                insights['best_performing_regions'].append({
                    'country': country,
                    'roi': roi,
                    'recommendation': 'Aumentar presupuesto +20%'
                })
            elif roi < roi_threshold_low:
                insights['underperforming_regions'].append({
                    'country': country,
                    'roi': roi,
                    'recommendation': 'Reducir presupuesto -15% o mejorar targeting'
                })
        
        # Recomendaciones específicas
        for country, data in performance_data.items():
            country_recommendations = []
            
            if data['estimated_ctr'] < 2.5:
                country_recommendations.append("Mejorar creativos para aumentar CTR")
            if data['cpm'] > 5.5:
                country_recommendations.append("Optimizar targeting para reducir CPM")
            if data['estimated_engagement'] < 7.0:
                country_recommendations.append("Ajustar contenido para mayor engagement")
            
            insights['regional_recommendations'][country] = country_recommendations
        
        return insights

# Ejemplo de uso
if __name__ == "__main__":
    # Datos históricos de ejemplo
    historical_example = {
        'MX': {'avg_ctr': 3.5, 'avg_roi': 180, 'avg_engagement': 9.2, 'campaigns_count': 5},
        'CO': {'avg_ctr': 3.8, 'avg_roi': 195, 'avg_engagement': 9.8, 'campaigns_count': 3},
        'AR': {'avg_ctr': 2.9, 'avg_roi': 145, 'avg_engagement': 8.1, 'campaigns_count': 4}
    }
    
    # Ejecutar distribución geográfica
    geo_dist = GeoDistribution()
    
    print("🌍 SIMULACIÓN DISTRIBUCIÓN GEOGRÁFICA TRAP")
    print("=" * 60)
    
    # Distribución inicial
    allocation = geo_dist.calculate_geo_allocation(400, 'trap', historical_example)
    
    # Simular rendimiento
    performance = geo_dist.simulate_regional_performance(allocation, 'trap')
    
    # Generar insights
    insights = geo_dist.generate_geo_insights(performance)
    
    print("💡 INSIGHTS REGIONALES:")
    print("-" * 30)
    
    if insights['best_performing_regions']:
        print("🏆 Mejores regiones:")
        for region in insights['best_performing_regions']:
            print(f"  • {region['country']}: {region['roi']:.1f}% ROI - {region['recommendation']}")
    
    if insights['underperforming_regions']:
        print("⚠️ Regiones con bajo rendimiento:")
        for region in insights['underperforming_regions']:
            print(f"  • {region['country']}: {region['roi']:.1f}% ROI - {region['recommendation']}")
    
    print("\n✅ Simulación de Distribución Geográfica completada!")