"""
Advanced Campaign System - Budget Optimizer
Optimización automática de presupuesto con ciclos de reinversión
"""

import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class ClipData:
    """Datos de clip individual"""
    id: str
    genre: str
    subgenre: str
    target_regions: List[str]
    duration: int
    audience_type: str
    estimated_quality: float = 0.8

@dataclass
class ClipMetrics:
    """Métricas de rendimiento de clip"""
    ctr: float
    cpc: float
    cpv: float
    views: int
    engagement_rate: float
    conversion_rate: float
    total_spend: float
    roi: float

class BudgetOptimizer:
    """Optimizador automático de presupuesto con ciclos de reinversión"""
    
    def __init__(self):
        self.initial_budget = 400
        self.youtube_reinvestment = 50
        self.clip_metrics = {}
        self.historical_performance = []
        
        # Factores de rendimiento por género
        self.genre_multipliers = {
            'trap': {'ctr_base': 3.2, 'cpc_base': 0.45, 'engagement_base': 8.5},
            'reggaeton': {'ctr_base': 3.8, 'cpc_base': 0.42, 'engagement_base': 9.2},
            'rap': {'ctr_base': 2.9, 'cpc_base': 0.48, 'engagement_base': 7.8},
            'corrido': {'ctr_base': 2.5, 'cpc_base': 0.52, 'engagement_base': 7.1}
        }
        
        # Factores regionales
        self.regional_multipliers = {
            'ES': 1.15,  # España - mayor CPM pero mejor conversión
            'MX': 1.0,   # México - baseline
            'CO': 0.95,  # Colombia
            'AR': 0.92,  # Argentina  
            'CL': 0.88,  # Chile
            'PE': 0.85   # Perú
        }
    
    def simulate_initial_cycle(self, clips_data: List[ClipData]) -> Tuple[Dict[str, ClipMetrics], str]:
        """
        Simula ciclo inicial con $400 para 5 clips
        Retorna métricas por clip y clip ganador
        """
        print("💰 INICIANDO CICLO INICIAL - $400 DISTRIBUCIÓN")
        print("-" * 50)
        
        budget_per_clip = self.initial_budget / len(clips_data)  # $80 por clip
        simulated_results = {}
        
        for clip in clips_data:
            print(f"🎬 Simulando clip {clip.id} ({clip.genre} - {clip.subgenre})")
            
            # Obtener multiplicadores base por género
            genre_data = self.genre_multipliers.get(clip.genre, self.genre_multipliers['trap'])
            
            # Calcular métricas realistas
            base_ctr = genre_data['ctr_base']
            base_cpc = genre_data['cpc_base'] 
            base_engagement = genre_data['engagement_base']
            
            # Aplicar variabilidad realista
            ctr = base_ctr * random.uniform(0.7, 1.4) * clip.estimated_quality
            cpc = base_cpc * random.uniform(0.85, 1.25)
            
            # Calcular métricas derivadas
            estimated_clicks = (budget_per_clip / cpc)
            estimated_impressions = estimated_clicks / (ctr / 100)
            cpv = cpc * 0.85  # Factor de conversión click-to-view
            views = int(estimated_clicks * 1.2)  # Views > clicks
            engagement_rate = base_engagement * random.uniform(0.8, 1.3)
            conversion_rate = random.uniform(0.8, 2.5)  # % de conversiones
            
            # Calcular ROI
            estimated_revenue = views * 0.024  # $0.024 valor por view
            roi = ((estimated_revenue - budget_per_clip) / budget_per_clip) * 100
            
            metrics = ClipMetrics(
                ctr=round(ctr, 2),
                cpc=round(cpc, 3),
                cpv=round(cpv, 3),
                views=views,
                engagement_rate=round(engagement_rate, 1),
                conversion_rate=round(conversion_rate, 2),
                total_spend=budget_per_clip,
                roi=round(roi, 1)
            )
            
            simulated_results[clip.id] = metrics
            
            print(f"  📊 CTR: {metrics.ctr}% | CPV: ${metrics.cpv} | Views: {metrics.views:,}")
            print(f"  💰 Spend: ${metrics.total_spend} | ROI: {metrics.roi}%")
            print()
        
        # Identificar clip ganador
        winner_clip = self.identify_winner(simulated_results)
        print(f"🏆 CLIP GANADOR: {winner_clip}")
        print(f"🎯 Métricas ganadoras: {simulated_results[winner_clip].__dict__}")
        print()
        
        return simulated_results, winner_clip
    
    def identify_winner(self, performance_results: Dict[str, ClipMetrics]) -> str:
        """Identifica clip ganador basado en score compuesto"""
        scores = {}
        
        for clip_id, metrics in performance_results.items():
            # Score compuesto: ROI (40%) + CTR (30%) + Engagement (30%)
            roi_score = max(0, metrics.roi) / 100  # Normalizar ROI
            ctr_score = metrics.ctr / 5.0  # Normalizar CTR
            engagement_score = metrics.engagement_rate / 15.0  # Normalizar engagement
            
            composite_score = (roi_score * 0.4) + (ctr_score * 0.3) + (engagement_score * 0.3)
            scores[clip_id] = composite_score
        
        winner = max(scores.keys(), key=lambda k: scores[k])
        return winner
    
    def execute_reinvestment_cycle(self, winner_clip: str, winner_metrics: ClipMetrics) -> Dict:
        """
        Ejecuta reinversión de $50 en clip ganador para YouTube
        """
        print("🚀 EJECUTANDO REINVERSIÓN YOUTUBE - $50")
        print("-" * 50)
        
        # Simular boost de YouTube con $50 adicionales
        youtube_cpm_factor = 0.75  # YouTube 25% más barato que Meta
        youtube_engagement_boost = 1.4  # YouTube 40% más engagement
        
        additional_impressions = (self.youtube_reinvestment / (winner_metrics.cpc * youtube_cpm_factor)) * 1000
        additional_views = int(additional_impressions * (winner_metrics.ctr / 100) * 1.3)
        
        # Calcular potencial viral
        viral_coefficient = self.calculate_viral_coefficient(winner_metrics)
        organic_boost = additional_views * viral_coefficient
        
        youtube_metrics = {
            'additional_budget': self.youtube_reinvestment,
            'additional_views': additional_views,
            'organic_boost_views': int(organic_boost),
            'total_youtube_views': additional_views + int(organic_boost),
            'cross_platform_engagement': winner_metrics.engagement_rate * youtube_engagement_boost,
            'viral_coefficient': viral_coefficient,
            'youtube_roi': self.calculate_youtube_roi(additional_views + int(organic_boost), self.youtube_reinvestment)
        }
        
        print(f"📺 YouTube Views Pagadas: {additional_views:,}")
        print(f"🔥 Boost Orgánico: {int(organic_boost):,}")
        print(f"📈 Total YouTube: {youtube_metrics['total_youtube_views']:,}")
        print(f"💎 Coeficiente Viral: {viral_coefficient:.3f}")
        print(f"💰 YouTube ROI: {youtube_metrics['youtube_roi']:.1f}%")
        print()
        
        return youtube_metrics
    
    def calculate_viral_coefficient(self, metrics: ClipMetrics) -> float:
        """Calcula coeficiente viral basado en métricas"""
        # Factores que contribuyen a viralidad
        engagement_factor = min(metrics.engagement_rate / 10.0, 1.0)
        ctr_factor = min(metrics.ctr / 4.0, 1.0)
        conversion_factor = min(metrics.conversion_rate / 2.0, 1.0)
        
        viral_coefficient = (engagement_factor * 0.5) + (ctr_factor * 0.3) + (conversion_factor * 0.2)
        
        # Boost adicional si métricas son excepcionales
        if metrics.engagement_rate > 12 and metrics.ctr > 4.5:
            viral_coefficient *= 1.25
        
        return round(viral_coefficient, 3)
    
    def calculate_youtube_roi(self, total_views: int, investment: float) -> float:
        """Calcula ROI de inversión en YouTube"""
        # Valor por view en YouTube (ligeramente menor que Meta)
        youtube_value_per_view = 0.021
        estimated_revenue = total_views * youtube_value_per_view
        roi = ((estimated_revenue - investment) / investment) * 100
        return round(roi, 1)
    
    def calculate_next_cycle_budget(self, historical_performance: List[Dict]) -> Dict:
        """
        Calcula presupuesto óptimo para siguiente ciclo basado en ROI histórico
        """
        if not historical_performance:
            return {
                'total_budget': self.initial_budget,
                'clips_budget': self.initial_budget * 0.88,
                'youtube_budget': self.initial_budget * 0.12
            }
        
        # Analizar tendencia de ROI
        recent_cycles = historical_performance[-3:]  # Últimos 3 ciclos
        avg_roi = sum([cycle.get('total_roi', 0) for cycle in recent_cycles]) / len(recent_cycles)
        
        # Calcular multiplicador basado en rendimiento
        if avg_roi > 200:
            roi_multiplier = 1.3  # Aumentar 30% si ROI > 200%
        elif avg_roi > 150:
            roi_multiplier = 1.15  # Aumentar 15% si ROI > 150%
        elif avg_roi > 100:
            roi_multiplier = 1.05  # Aumentar 5% si ROI > 100%
        elif avg_roi > 50:
            roi_multiplier = 1.0   # Mantener si ROI > 50%
        else:
            roi_multiplier = 0.85  # Reducir 15% si ROI < 50%
        
        recommended_budget = self.initial_budget * roi_multiplier
        
        print("📊 ANÁLISIS PARA PRÓXIMO CICLO")
        print("-" * 50)
        print(f"💹 ROI Promedio Histórico: {avg_roi:.1f}%")
        print(f"⚡ Multiplicador Aplicado: {roi_multiplier:.2f}x")
        print(f"💰 Presupuesto Recomendado: ${recommended_budget:.0f}")
        
        return {
            'total_budget': recommended_budget,
            'clips_budget': recommended_budget * 0.88,  # 88% para clips
            'youtube_budget': recommended_budget * 0.12,  # 12% para YouTube
            'roi_multiplier': roi_multiplier,
            'historical_avg_roi': avg_roi
        }
    
    def simulate_complete_budget_cycle(self, clips_data: List[ClipData]) -> Dict:
        """
        Simula ciclo completo de presupuesto: inicial → reinversión → próximo ciclo
        """
        print("🎯 SIMULACIÓN COMPLETA DE CICLO DE PRESUPUESTO")
        print("=" * 60)
        
        # Paso 1: Ciclo inicial
        initial_results, winner = self.simulate_initial_cycle(clips_data)
        
        # Paso 2: Reinversión YouTube  
        youtube_results = self.execute_reinvestment_cycle(winner, initial_results[winner])
        
        # Paso 3: Calcular métricas totales del ciclo
        total_spend = self.initial_budget + self.youtube_reinvestment
        total_views = sum([metrics.views for metrics in initial_results.values()]) + youtube_results['total_youtube_views']
        total_revenue = total_views * 0.023  # Valor promedio por view
        total_roi = ((total_revenue - total_spend) / total_spend) * 100
        
        # Paso 4: Guardar en histórico
        cycle_data = {
            'timestamp': datetime.now(),
            'total_spend': total_spend,
            'total_views': total_views,
            'total_revenue': total_revenue,
            'total_roi': total_roi,
            'winner_clip': winner,
            'youtube_boost': youtube_results['total_youtube_views']
        }
        self.historical_performance.append(cycle_data)
        
        # Paso 5: Recomendaciones para próximo ciclo
        next_cycle_budget = self.calculate_next_cycle_budget(self.historical_performance)
        
        print("📋 RESUMEN EJECUTIVO DEL CICLO")
        print("=" * 60)
        print(f"💰 Inversión Total: ${total_spend}")
        print(f"👀 Views Totales: {total_views:,}")
        print(f"💎 Revenue Total: ${total_revenue:.0f}")
        print(f"🚀 ROI Total: {total_roi:.1f}%")
        print(f"🏆 Clip Ganador: {winner}")
        print(f"📺 Boost YouTube: {youtube_results['total_youtube_views']:,} views")
        print(f"💡 Próximo Presupuesto: ${next_cycle_budget['total_budget']:.0f}")
        print()
        
        return {
            'cycle_summary': cycle_data,
            'initial_performance': initial_results,
            'youtube_boost': youtube_results,
            'next_recommendations': next_cycle_budget,
            'winner_analysis': {
                'clip_id': winner,
                'metrics': initial_results[winner].__dict__,
                'viral_coefficient': youtube_results['viral_coefficient']
            }
        }

# Ejemplo de uso
if __name__ == "__main__":
    # Crear datos de clips de ejemplo
    clips_example = [
        ClipData("clip_001", "trap", "trap_oscuro", ["ES", "MX"], 30, "audience_propia", 0.9),
        ClipData("clip_002", "trap", "trap_melodico", ["ES", "CO"], 25, "audience_colaborador", 0.85),
        ClipData("clip_003", "trap", "trap_comercial", ["MX", "AR"], 35, "audience_mixta", 0.8),
        ClipData("clip_004", "trap", "trap_oscuro", ["ES", "CL"], 28, "audience_nueva", 0.75),
        ClipData("clip_005", "trap", "trap_melodico", ["CO", "PE"], 32, "audience_propia", 0.88)
    ]
    
    # Ejecutar simulación
    optimizer = BudgetOptimizer()
    results = optimizer.simulate_complete_budget_cycle(clips_example)
    
    print("✅ Simulación de Budget Optimizer completada exitosamente!")