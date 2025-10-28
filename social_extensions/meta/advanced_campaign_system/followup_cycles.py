"""
Advanced Campaign System - Follow-up Cycles Automation
Automatización de ciclos posteriores con presupuesto adicional en clips ganadores
"""

import json
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid

@dataclass
class FollowUpCycle:
    """Configuración de un ciclo de seguimiento"""
    cycle_id: str
    parent_campaign_id: str
    winner_clips: List[str]
    additional_budget: float
    target_platform: str  # youtube, meta_extended, tiktok_boost
    cycle_type: str  # reinforcement, expansion, cross_platform
    start_timestamp: datetime
    expected_duration_hours: int
    
@dataclass
class CyclePerformance:
    """Rendimiento de un ciclo de seguimiento"""
    cycle_id: str
    clip_id: str
    invested_amount: float
    views_generated: int
    ctr_achieved: float
    cpv_achieved: float
    roi_percentage: float
    engagement_metrics: Dict[str, float]
    conversion_data: Dict[str, any]

class FollowUpCyclesAutomator:
    """Automatizador de ciclos posteriores con presupuesto adicional"""
    
    def __init__(self):
        self.active_cycles = {}
        self.cycle_history = []
        
        # Configuración de automatización
        self.automation_settings = {
            'auto_trigger_threshold_roi': 150,  # ROI mínimo para trigger automático
            'additional_budget_default': 50,    # Presupuesto adicional por defecto
            'max_follow_up_cycles': 3,          # Máximo 3 ciclos de seguimiento
            'cycle_gap_hours': 2,               # Espera entre ciclos (horas)
            'winner_selection_top_n': 2,        # Top N clips para seguimiento
            'platform_priorities': ['youtube', 'meta_extended', 'tiktok_boost']
        }
        
        # Multiplicadores por plataforma para ciclos de seguimiento
        self.platform_multipliers = {
            'youtube': {'ctr_boost': 1.4, 'cpv_improvement': 0.7, 'engagement_boost': 1.6},
            'meta_extended': {'ctr_boost': 1.1, 'cpv_improvement': 0.9, 'engagement_boost': 1.2},
            'tiktok_boost': {'ctr_boost': 1.8, 'cpv_improvement': 0.6, 'engagement_boost': 2.1}
        }
    
    def identify_winner_clips(self, campaign_metrics: Dict) -> List[Dict]:
        """
        Identifica clips ganadores basado en métricas de performance
        """
        print("🏆 IDENTIFICANDO CLIPS GANADORES PARA SEGUIMIENTO")
        print("-" * 50)
        
        clip_performance = campaign_metrics.get('clip_performance', {})
        
        if not clip_performance:
            print("⚠️ No hay datos de performance de clips disponibles")
            return []
        
        # Calcular score combinado para cada clip
        clip_scores = []
        
        for clip_id, metrics in clip_performance.items():
            roi = metrics.get('roi', 0)
            ctr = metrics.get('ctr', 0)
            views = metrics.get('views', 0)
            engagement = metrics.get('engagement_rate', 0)
            
            # Score combinado: ROI (40%) + CTR (25%) + Views (20%) + Engagement (15%)
            combined_score = (
                roi * 0.40 +
                ctr * 25 * 0.25 +  # Normalizar CTR a escala similar
                (views / 1000) * 0.20 +  # Views en miles
                engagement * 10 * 0.15   # Engagement normalizado
            )
            
            clip_scores.append({
                'clip_id': clip_id,
                'roi': roi,
                'ctr': ctr,
                'views': views,
                'engagement_rate': engagement,
                'combined_score': combined_score
            })
        
        # Ordenar por score descendente
        clip_scores.sort(key=lambda x: x['combined_score'], reverse=True)
        
        # Filtrar clips que superen el threshold de ROI
        roi_threshold = self.automation_settings['auto_trigger_threshold_roi']
        qualified_clips = [
            clip for clip in clip_scores 
            if clip['roi'] > roi_threshold
        ]
        
        # Tomar top N clips
        top_n = self.automation_settings['winner_selection_top_n']
        winner_clips = qualified_clips[:top_n]
        
        print(f"📊 Clips analizados: {len(clip_scores)}")
        print(f"✅ Clips cualificados (ROI >{roi_threshold}%): {len(qualified_clips)}")
        print(f"🏅 Clips seleccionados para seguimiento: {len(winner_clips)}")
        
        for i, clip in enumerate(winner_clips, 1):
            print(f"   {i}. {clip['clip_id']}: ROI {clip['roi']:.1f}%, Score {clip['combined_score']:.2f}")
        print()
        
        return winner_clips
    
    def plan_follow_up_cycles(self, winner_clips: List[Dict], 
                             parent_campaign: Dict,
                             additional_budget: float = None) -> List[FollowUpCycle]:
        """
        Planifica ciclos de seguimiento para clips ganadores
        """
        print("📅 PLANIFICANDO CICLOS DE SEGUIMIENTO")
        print("-" * 35)
        
        if additional_budget is None:
            additional_budget = self.automation_settings['additional_budget_default']
        
        planned_cycles = []
        
        # Distribuir presupuesto entre clips ganadores
        budget_per_clip = additional_budget / len(winner_clips) if winner_clips else 0
        
        for i, clip_data in enumerate(winner_clips):
            clip_id = clip_data['clip_id']
            roi = clip_data['roi']
            
            # Determinar mejor plataforma según ROI
            if roi > 200:
                target_platform = 'youtube'  # Mejor ROI -> YouTube
                cycle_type = 'expansion'
                duration_hours = 24
            elif roi > 175:
                target_platform = 'tiktok_boost'  # ROI bueno -> TikTok boost
                cycle_type = 'cross_platform'
                duration_hours = 18
            else:
                target_platform = 'meta_extended'  # ROI moderado -> Meta extended
                cycle_type = 'reinforcement'
                duration_hours = 12
            
            # Crear ciclo de seguimiento
            cycle_start = datetime.now() + timedelta(hours=self.automation_settings['cycle_gap_hours'] * (i + 1))
            
            cycle = FollowUpCycle(
                cycle_id=f"followup_{uuid.uuid4().hex[:8]}",
                parent_campaign_id=parent_campaign.get('campaign_id', 'unknown'),
                winner_clips=[clip_id],
                additional_budget=budget_per_clip,
                target_platform=target_platform,
                cycle_type=cycle_type,
                start_timestamp=cycle_start,
                expected_duration_hours=duration_hours
            )
            
            planned_cycles.append(cycle)
            
            print(f"📋 Ciclo {i+1}: {clip_id}")
            print(f"   💰 Presupuesto: ${budget_per_clip:.0f}")
            print(f"   📺 Plataforma: {target_platform}")
            print(f"   🎯 Tipo: {cycle_type}")
            print(f"   ⏰ Inicio: {cycle_start.strftime('%d/%m %H:%M')}")
            print(f"   ⏱️ Duración: {duration_hours}h")
            print()
        
        return planned_cycles
    
    def execute_follow_up_cycle(self, cycle: FollowUpCycle, 
                               original_metrics: Dict) -> CyclePerformance:
        """
        Ejecuta un ciclo de seguimiento individual
        """
        print(f"🚀 EJECUTANDO CICLO DE SEGUIMIENTO: {cycle.cycle_id}")
        print("-" * 50)
        
        clip_id = cycle.winner_clips[0]  # Primer clip (puede expandirse a múltiples)
        
        # Obtener multiplicadores de la plataforma
        platform_mults = self.platform_multipliers.get(cycle.target_platform, {
            'ctr_boost': 1.0, 'cpv_improvement': 1.0, 'engagement_boost': 1.0
        })
        
        # Métricas base del clip original
        original_clip_metrics = original_metrics.get('clip_performance', {}).get(clip_id, {})
        base_ctr = original_clip_metrics.get('ctr', 3.0)
        base_cpv = original_clip_metrics.get('cpv', 0.50)
        base_engagement = original_clip_metrics.get('engagement_rate', 4.0)
        
        # Calcular métricas mejoradas
        improved_ctr = base_ctr * platform_mults['ctr_boost'] * random.uniform(0.9, 1.1)
        improved_cpv = base_cpv * platform_mults['cpv_improvement'] * random.uniform(0.9, 1.1)
        improved_engagement = base_engagement * platform_mults['engagement_boost'] * random.uniform(0.9, 1.1)
        
        # Calcular vistas generadas
        views_generated = int(cycle.additional_budget / improved_cpv)
        
        # Calcular conversiones simuladas (asumiendo $15 por conversión)
        conversion_rate = improved_ctr / 100 * random.uniform(0.8, 1.2)
        conversions = int(views_generated * conversion_rate / 100)
        revenue_generated = conversions * 15  # $15 por conversión
        
        # Calcular ROI del ciclo
        roi_percentage = ((revenue_generated - cycle.additional_budget) / cycle.additional_budget) * 100
        
        # Métricas adicionales de engagement
        engagement_metrics = {
            'likes': int(views_generated * improved_engagement / 100 * 0.6),
            'shares': int(views_generated * improved_engagement / 100 * 0.15),
            'comments': int(views_generated * improved_engagement / 100 * 0.08),
            'saves': int(views_generated * improved_engagement / 100 * 0.12),
            'click_throughs': int(views_generated * improved_ctr / 100)
        }
        
        # Datos de conversión
        conversion_data = {
            'total_conversions': conversions,
            'conversion_rate': conversion_rate,
            'revenue_generated': revenue_generated,
            'cost_per_conversion': cycle.additional_budget / conversions if conversions > 0 else 0,
            'platform': cycle.target_platform
        }
        
        # Crear objeto de performance
        performance = CyclePerformance(
            cycle_id=cycle.cycle_id,
            clip_id=clip_id,
            invested_amount=cycle.additional_budget,
            views_generated=views_generated,
            ctr_achieved=improved_ctr,
            cpv_achieved=improved_cpv,
            roi_percentage=roi_percentage,
            engagement_metrics=engagement_metrics,
            conversion_data=conversion_data
        )
        
        print(f"📺 Plataforma: {cycle.target_platform}")
        print(f"💰 Inversión: ${cycle.additional_budget:.0f}")
        print(f"👀 Vistas generadas: {views_generated:,}")
        print(f"📊 CTR mejorado: {improved_ctr:.2f}% (+{((improved_ctr/base_ctr-1)*100):+.1f}%)")
        print(f"💵 CPV mejorado: ${improved_cpv:.3f} ({((improved_cpv/base_cpv-1)*100):+.1f}%)")
        print(f"🔥 Engagement: {improved_engagement:.1f}% (+{((improved_engagement/base_engagement-1)*100):+.1f}%)")
        print(f"🎯 Conversiones: {conversions}")
        print(f"💎 ROI ciclo: {roi_percentage:+.1f}%")
        print()
        
        return performance
    
    def run_automated_follow_up_sequence(self, campaign_results: Dict, 
                                        additional_budget: float = 50) -> Dict:
        """
        Ejecuta secuencia completa de seguimiento automático
        """
        print("🤖 AUTOMATIZACIÓN COMPLETA DE CICLOS DE SEGUIMIENTO")
        print("=" * 55)
        
        # 1. Identificar clips ganadores
        winner_clips = self.identify_winner_clips(campaign_results)
        
        if not winner_clips:
            print("❌ No se encontraron clips elegibles para seguimiento")
            return {
                'automation_executed': False,
                'reason': 'no_qualified_clips',
                'threshold_roi': self.automation_settings['auto_trigger_threshold_roi']
            }
        
        # 2. Planificar ciclos
        planned_cycles = self.plan_follow_up_cycles(
            winner_clips, 
            campaign_results,
            additional_budget
        )
        
        # 3. Ejecutar cada ciclo
        cycle_performances = []
        total_additional_investment = 0
        total_additional_views = 0
        total_additional_revenue = 0
        
        for cycle in planned_cycles:
            print(f"⏳ Simulando espera hasta: {cycle.start_timestamp.strftime('%d/%m %H:%M')}")
            
            performance = self.execute_follow_up_cycle(cycle, campaign_results)
            cycle_performances.append(performance)
            
            total_additional_investment += performance.invested_amount
            total_additional_views += performance.views_generated
            total_additional_revenue += performance.conversion_data['revenue_generated']
        
        # 4. Calcular ROI total de seguimiento
        total_follow_up_roi = ((total_additional_revenue - total_additional_investment) / total_additional_investment) * 100 if total_additional_investment > 0 else 0
        
        # 5. Compilar resultados finales
        automation_results = {
            'automation_executed': True,
            'cycles_planned': len(planned_cycles),
            'cycles_executed': len(cycle_performances),
            'total_additional_budget': total_additional_investment,
            'total_additional_views': total_additional_views,
            'total_additional_revenue': total_additional_revenue,
            'follow_up_roi': total_follow_up_roi,
            'cycle_performances': [
                {
                    'cycle_id': perf.cycle_id,
                    'clip_id': perf.clip_id,
                    'invested': perf.invested_amount,
                    'views': perf.views_generated,
                    'roi': perf.roi_percentage,
                    'platform': planned_cycles[i].target_platform
                }
                for i, perf in enumerate(cycle_performances)
            ],
            'automation_timestamp': datetime.now().isoformat(),
            'settings_used': self.automation_settings
        }
        
        print("📊 RESUMEN AUTOMATIZACIÓN:")
        print(f"   🔄 Ciclos ejecutados: {len(cycle_performances)}")
        print(f"   💰 Inversión adicional: ${total_additional_investment:.0f}")
        print(f"   👀 Vistas adicionales: {total_additional_views:,}")
        print(f"   💎 ROI seguimiento: {total_follow_up_roi:+.1f}%")
        
        # Calcular mejora sobre campaña original
        original_investment = campaign_results.get('total_investment', 400)
        original_views = campaign_results.get('total_views', 10000)
        original_roi = campaign_results.get('total_roi', 150)
        
        combined_investment = original_investment + total_additional_investment
        combined_views = original_views + total_additional_views
        combined_revenue = (original_investment * (original_roi / 100 + 1)) + total_additional_revenue
        combined_roi = ((combined_revenue - combined_investment) / combined_investment) * 100
        
        print(f"   📈 ROI combinado: {original_roi:.1f}% → {combined_roi:.1f}% ({combined_roi - original_roi:+.1f}%)")
        print(f"   🚀 Boost total vistas: +{((combined_views / original_views - 1) * 100):+.1f}%")
        print()
        
        automation_results['combined_metrics'] = {
            'original_investment': original_investment,
            'combined_investment': combined_investment,
            'original_views': original_views,
            'combined_views': combined_views,
            'original_roi': original_roi,
            'combined_roi': combined_roi,
            'roi_improvement': combined_roi - original_roi
        }
        
        return automation_results

# Test del módulo
if __name__ == "__main__":
    print("🧪 TEST FOLLOW-UP CYCLES AUTOMATION")
    print("=" * 40)
    
    # Crear instancia del automatizador
    automator = FollowUpCyclesAutomator()
    
    # Datos simulados de campaña original
    campaign_results = {
        'campaign_id': 'camp_test_001',
        'total_investment': 400,
        'total_views': 12500,
        'total_roi': 165.5,
        'clip_performance': {
            'clip_001': {'roi': 185.2, 'ctr': 3.8, 'views': 3500, 'engagement_rate': 6.2},
            'clip_002': {'roi': 155.7, 'ctr': 3.1, 'views': 2800, 'engagement_rate': 4.8},
            'clip_003': {'roi': 142.3, 'ctr': 2.7, 'views': 2200, 'engagement_rate': 4.1},
            'clip_004': {'roi': 178.9, 'ctr': 3.5, 'views': 3000, 'engagement_rate': 5.9},
            'clip_005': {'roi': 125.4, 'ctr': 2.3, 'views': 1000, 'engagement_rate': 3.2}
        }
    }
    
    # Ejecutar automatización completa
    results = automator.run_automated_follow_up_sequence(
        campaign_results,
        additional_budget=50
    )
    
    print("✅ TEST COMPLETADO")
    if results['automation_executed']:
        print(f"   Ciclos ejecutados: {results['cycles_executed']}")
        print(f"   ROI seguimiento: {results['follow_up_roi']:+.1f}%")
        print(f"   Mejora ROI total: {results['combined_metrics']['roi_improvement']:+.1f}%")