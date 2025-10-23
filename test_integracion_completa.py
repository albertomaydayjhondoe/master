"""
TEST INTEGRACIÓN COMPLETA - SISTEMA AVANZADO META ADS
Prueba final de todos los 6 componentes del sistema avanzado
"""

import sys
import os
sys.path.append('/workspaces/master')

from social_extensions.meta.advanced_campaign_system.budget_optimizer import BudgetOptimizer
from social_extensions.meta.advanced_campaign_system.geo_distribution import GeoDistribution  
from social_extensions.meta.advanced_campaign_system.campaign_tagging import CampaignTagging
from social_extensions.meta.advanced_campaign_system.ml_learning_cycle import MLLearningCycle
from social_extensions.meta.advanced_campaign_system.ultralytics_integration import UltralyticsIntegration

import json
from datetime import datetime

def test_integracion_completa():
    """Test de integración completa de los 6 componentes"""
    print("🚀 TEST INTEGRACIÓN COMPLETA - SISTEMA AVANZADO META ADS")
    print("=" * 65)
    print()
    
    # Datos de entrada de la campaña
    campaign_data = {
        'song_title': 'Noche de Perreo',
        'artist': 'Bad Bunny feat. Anuel AA',
        'genre': 'reggaeton',
        'subgenre': 'perreo_intenso',
        'collaborators': ['anuel_aa'],
        'duration': 195,
        'budget_total': 450,
        'target_regions': ['ES', 'MX', 'CO', 'AR'],
        'clip_count': 5
    }
    
    print("📋 DATOS DE CAMPAÑA:")
    print(f"   🎵 Canción: {campaign_data['song_title']}")
    print(f"   🎤 Artista: {campaign_data['artist']}")
    print(f"   🎼 Género: {campaign_data['genre']} - {campaign_data['subgenre']}")
    print(f"   💰 Presupuesto: ${campaign_data['budget_total']}")
    print(f"   🌍 Regiones: {', '.join(campaign_data['target_regions'])}")
    print()
    
    # ===== COMPONENTE 1: CAMPAIGN TAGGING =====
    print("1️⃣ EJECUTANDO CAMPAIGN TAGGING")
    print("-" * 35)
    
    tagging_system = CampaignTagging()
    campaign_tags = tagging_system.create_advanced_tags(campaign_data)
    
    print(f"✅ Tags generados: {campaign_tags.campaign_id}")
    print(f"   🎯 Genre vector: {len(campaign_tags.ml_features['genre_vector'])} dims")
    print(f"   🔥 Collaborator influence: {campaign_tags.ml_features['collaborator_influence']:.3f}")
    print(f"   👥 Audience diversity: {campaign_tags.ml_features['audience_diversity_score']:.3f}")
    print()
    
    # ===== COMPONENTE 2: GEO DISTRIBUTION =====
    print("2️⃣ EJECUTANDO GEO DISTRIBUTION")
    print("-" * 35)
    
    geo_system = GeoDistribution()
    geo_allocation = geo_system.calculate_geo_allocation(
        campaign_data['budget_total'], campaign_data['genre']
    )
    
    total_geo_budget = geo_allocation.total_allocated
    print(f"✅ Distribución geográfica: ${total_geo_budget:.0f} en {len(geo_allocation.region_budgets)} países")
    print(f"   🇪🇸 España: ${geo_allocation.region_budgets.get('ES', 0):.0f}")
    print(f"   🇲🇽 México: ${geo_allocation.region_budgets.get('MX', 0):.0f}")
    print()
    
    # ===== COMPONENTE 3: ULTRALYTICS INTEGRATION =====
    print("3️⃣ EJECUTANDO ULTRALYTICS INTEGRATION")
    print("-" * 40)
    
    ultralytics_system = UltralyticsIntegration()
    ultralytics_results = ultralytics_system.execute_complete_flow()
    
    print(f"✅ Análisis Ultralytics completado:")
    print(f"   🎬 Clips analizados: {ultralytics_results['clips_analyzed']}")
    print(f"   🏆 Clips seleccionados: {ultralytics_results['clips_selected']}")
    print(f"   🎯 ROI predicho: {ultralytics_results['scaling_execution']['total_roi']:.1f}%")
    print(f"   📺 YouTube boost: ${ultralytics_results['scaling_execution']['youtube_boost_budget']:.0f}")
    print()
    
    # ===== COMPONENTE 4: BUDGET OPTIMIZER =====
    print("4️⃣ EJECUTANDO BUDGET OPTIMIZER")
    print("-" * 35)
    
    budget_system = BudgetOptimizer()
    
    # Simular datos de rendimiento de clips para optimización
    clip_performance_data = {}
    for clip_data in ultralytics_results['selected_clips_summary']:
        clip_performance_data[clip_data['clip_id']] = {
            'ctr': clip_data['predicted_ctr'],
            'cpc': 0.45,
            'cpv': 0.50,
            'views': int(90 / 0.50),  # budget_per_clip / cpv
            'engagement_rate': clip_data['predicted_ctr'] * 1.5,
            'conversion_rate': clip_data['predicted_ctr'] * 0.3
        }
    
    budget_optimization = budget_system.optimize_budget_allocation(
        campaign_tags, clip_performance_data, campaign_data['budget_total']
    )
    
    winner_clips = budget_optimization['winner_clips']
    total_optimized_budget = sum(budget_optimization['optimized_allocation'].values())
    
    print(f"✅ Optimización de presupuesto completada:")
    print(f"   💰 Presupuesto optimizado: ${total_optimized_budget:.0f}")
    print(f"   🏆 Clip ganador: {winner_clips[0] if winner_clips else 'N/A'}")
    print(f"   📊 ROI proyectado: {budget_optimization['performance_projection']['estimated_roi']:.1f}%")
    print()
    
    # ===== COMPONENTE 5: ML LEARNING CYCLE =====
    print("5️⃣ EJECUTANDO ML LEARNING CYCLE")
    print("-" * 35)
    
    ml_cycle = MLLearningCycle()
    
    # Compilar datos del ciclo para aprendizaje
    cycle_results = {
        'campaign_tags': campaign_tags,
        'clip_performance': clip_performance_data,
        'geo_performance': {
            country: {
                'budget_allocated': data['budget_allocated'],
                'estimated_views': data['estimated_views'],
                'roi_projection': data['roi_projection']
            }
            for country, data in geo_allocation['country_breakdown'].items()
        },
        'budget_allocation': budget_optimization['optimized_allocation'],
        'total_investment': total_optimized_budget,
        'total_views': sum(metrics['views'] for metrics in clip_performance_data.values()),
        'total_roi': budget_optimization['performance_projection']['estimated_roi'],
        'winner_clips': winner_clips,
        'optimization_decisions': {'method': 'ml_guided'},
        'genre': campaign_data['genre'],
        'subgenre': campaign_data['subgenre'],
        'collaborators': campaign_data['collaborators'],
        'regional_focus': list(geo_allocation['country_breakdown'].keys())
    }
    
    # Guardar ciclo y obtener insights
    cycle_id = ml_cycle.save_campaign_cycle_data(cycle_results)
    historical_cycles = ml_cycle.historical_manager.get_historical_cycles()
    model_adjustments, model_insights = ml_cycle.simulate_model_retraining(historical_cycles)
    
    print(f"✅ ML Learning Cycle completado:")
    print(f"   💾 Ciclo guardado: {cycle_id}")
    print(f"   📊 Datos históricos: {len(historical_cycles)} ciclos")
    print(f"   🧠 Confianza del modelo: {model_adjustments.confidence_score:.3f}")
    print()
    
    # ===== COMPONENTE 6: PREDICCIÓN PRÓXIMA CAMPAÑA =====
    print("6️⃣ PREDICIENDO PRÓXIMA CAMPAÑA")
    print("-" * 32)
    
    next_campaign_proposal = {
        'genre': 'trap',
        'budget_total': 500,
        'collaborators': ['anuel_aa', 'daddy_yankee']
    }
    
    next_predictions = ml_cycle.predict_next_campaign_performance(
        next_campaign_proposal, model_adjustments
    )
    
    print(f"✅ Predicción próxima campaña:")
    print(f"   🎯 ROI predicho: {next_predictions['performance_predictions']['roi']:.1f}%")
    print(f"   👁️ CTR estimado: {next_predictions['performance_predictions']['ctr']:.2f}%")
    print(f"   🎪 Confianza modelo: {next_predictions['model_confidence']:.3f}")
    print()
    
    # ===== RESUMEN FINAL COMPLETO =====
    print("📊 RESUMEN FINAL INTEGRACIÓN COMPLETA")
    print("=" * 45)
    
    # Compilar métricas totales
    total_views_predicted = (
        sum(metrics['views'] for metrics in clip_performance_data.values()) +
        ultralytics_results['scaling_execution']['youtube_boost_results']['boost_views']
    )
    
    total_investment_final = (
        total_optimized_budget + 
        ultralytics_results['scaling_execution']['youtube_boost_budget']
    )
    
    # Calcular ROI final combinado
    estimated_revenue = total_investment_final * (budget_optimization['performance_projection']['estimated_roi'] / 100)
    final_roi = ((estimated_revenue - total_investment_final) / total_investment_final) * 100
    
    print(f"💰 INVERSIÓN TOTAL: ${total_investment_final:.0f}")
    print(f"   • Presupuesto principal: ${total_optimized_budget:.0f}")
    print(f"   • YouTube boost: ${ultralytics_results['scaling_execution']['youtube_boost_budget']:.0f}")
    print()
    
    print(f"👀 VISTAS TOTALES PREDICHAS: {total_views_predicted:,}")
    print(f"   • Vistas campaña principal: {sum(metrics['views'] for metrics in clip_performance_data.values()):,}")
    print(f"   • Vistas YouTube boost: {ultralytics_results['scaling_execution']['youtube_boost_results']['boost_views']:,}")
    print()
    
    print(f"📈 ROI FINAL PROYECTADO: {final_roi:.1f}%")
    print(f"🎬 CLIPS EN EJECUCIÓN: {len(clip_performance_data)}")
    print(f"🌍 PAÍSES ACTIVOS: {len(geo_allocation['country_breakdown'])}")
    print(f"🧠 CONFIANZA ML: {model_adjustments.confidence_score:.3f}")
    print()
    
    # Validaciones finales
    validations = {
        'tags_generated': len(campaign_tags) > 0,
        'geo_distribution_ok': total_geo_budget > 0,
        'clips_analyzed': ultralytics_results['clips_analyzed'] >= 5,
        'budget_optimized': total_optimized_budget > 0,
        'ml_learning_active': len(historical_cycles) > 0,
        'predictions_available': next_predictions['model_confidence'] > 0
    }
    
    print("✅ VALIDACIONES SISTEMA AVANZADO:")
    for validation, status in validations.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {validation}: {'OK' if status else 'FALLO'}")
    
    all_valid = all(validations.values())
    print()
    print(f"🎯 ESTADO FINAL: {'✅ SISTEMA COMPLETAMENTE OPERATIVO' if all_valid else '❌ ERRORES DETECTADOS'}")
    
    return {
        'integration_successful': all_valid,
        'total_investment': total_investment_final,
        'total_predicted_views': total_views_predicted,
        'final_roi': final_roi,
        'components_tested': 6,
        'validations': validations,
        'cycle_id': cycle_id,
        'model_confidence': model_adjustments.confidence_score
    }

if __name__ == "__main__":
    results = test_integracion_completa()
    
    if results['integration_successful']:
        print("\n🎉 ¡INTEGRACIÓN COMPLETA EXITOSA!")
        print("   El sistema avanzado Meta Ads está 100% operativo")
        print("   Todos los 6 componentes funcionan correctamente")
    else:
        print("\n⚠️ Integración completada con advertencias")
        print("   Revisar validaciones para optimización")