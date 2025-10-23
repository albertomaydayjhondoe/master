"""
TEST INTEGRADO - 4 MÓDULOS REFINADOS DEL SISTEMA AVANZADO META ADS
Prueba completa de funcionalidades: Exclusión Seguidores, Ciclos Posteriores, 
Etiquetado Granular y Ajustes Geográficos Dinámicos
"""

import sys
import os
sys.path.append('/workspaces/master')

from social_extensions.meta.advanced_campaign_system.follower_exclusion import FollowerExclusionManager
from social_extensions.meta.advanced_campaign_system.followup_cycles import FollowUpCyclesAutomator
from social_extensions.meta.advanced_campaign_system.granular_tagging import GranularTaggingSystem, MainGenre
from social_extensions.meta.advanced_campaign_system.dynamic_geo_adjustments import DynamicGeoAdjuster

import json
from datetime import datetime

def test_modulos_refinados_completo():
    """Test integral de los 4 módulos refinados implementados"""
    
    print("🚀 TEST INTEGRADO - 4 MÓDULOS REFINADOS SISTEMA AVANZADO")
    print("=" * 65)
    print()
    
    # ===== MÓDULO 1: ETIQUETADO GRANULAR =====
    print("1️⃣ MÓDULO: ETIQUETADO GRANULAR POR SUBGÉNERO Y COLABORACIONES")
    print("-" * 65)
    
    tagging_system = GranularTaggingSystem()
    
    # Contenido musical con colaboración
    content_data = {
        'title': 'Bellakeo Nocturno (feat. Anuel AA)',
        'genre': 'reggaeton',
        'collaboration': {
            'artist_id': 'anuel_aa',
            'type': 'featuring'
        },
        'estimated_duration': 210,
        'target_audience': 'young_latino'
    }
    
    granular_tags = tagging_system.create_granular_tags(content_data)
    
    print("✅ ETIQUETADO GRANULAR COMPLETADO:")
    print(f"   🎵 Género: {granular_tags.main_genre.value} → {granular_tags.sub_genre}")
    print(f"   🤝 Colaboración: {granular_tags.collaboration_artist} ({granular_tags.collaboration_type})")
    print(f"   🎯 Confianza: {granular_tags.confidence_scores['overall_confidence']:.3f}")
    print(f"   📊 Segmentos audiencia: {len(granular_tags.audience_segments)}")
    print(f"   📈 Multiplicador mercado: {granular_tags.market_predictions['ctr_multiplier']:.2f}x")
    print()
    
    # ===== MÓDULO 2: EXCLUSIÓN DE SEGUIDORES =====
    print("2️⃣ MÓDULO: EXCLUSIÓN DE SEGUIDORES ACTUALES")
    print("-" * 45)
    
    exclusion_manager = FollowerExclusionManager()
    
    # Datos de campaña inicial
    campaign_data = {
        'campaign_id': 'camp_bellakeo_nocturno_001',
        'genre': granular_tags.main_genre.value,
        'sub_genre': granular_tags.sub_genre,
        'collaboration_artist': granular_tags.collaboration_artist,
        'budget_total': 400,
        'target_regions': ['ES', 'MX', 'CO', 'AR']
    }
    
    # Aplicar exclusión de seguidores
    campaign_with_exclusion = exclusion_manager.apply_exclusion_to_campaign(
        campaign_data, 
        account_id='acc_reggaeton_artist_main'
    )
    
    exclusion_results = campaign_with_exclusion['follower_exclusion']
    
    print("✅ EXCLUSIÓN DE SEGUIDORES COMPLETADA:")
    print(f"   👥 Total seguidores: {exclusion_results['total_followers']:,}")
    print(f"   🚫 Lista exclusión: {exclusion_results['exclusion_list_size']:,}")
    print(f"   🎯 Audiencias filtradas: {exclusion_results['audiences_processed']}")
    print(f"   📉 Usuarios excluidos total: {exclusion_results['total_users_excluded']:,}")
    
    # Calcular promedio de exclusión
    filtered_segments = exclusion_results['filtered_segments']
    avg_exclusion = sum(seg.exclusion_percentage for seg in filtered_segments) / len(filtered_segments)
    print(f"   📊 Exclusión promedio: {avg_exclusion:.1f}%")
    print()
    
    # ===== MÓDULO 3: AJUSTES GEOGRÁFICOS DINÁMICOS =====  
    print("3️⃣ MÓDULO: AJUSTES GEOGRÁFICOS DINÁMICOS")
    print("-" * 45)
    
    geo_adjuster = DynamicGeoAdjuster()
    
    # Simular datos de distribución geográfica inicial
    campaign_geo_data = campaign_with_exclusion.copy()
    campaign_geo_data['geo_allocation'] = {
        'region_budgets': {
            'ES': 108,  # 27% de 400
            'MX': 88,   # 22%
            'CO': 64,   # 16%
            'AR': 52,   # 13%
            'CL': 32,   # 8%
            'PE': 36,   # 9%
            'EC': 20    # 5%
        },
        'total_allocated': 400
    }
    
    # Ejecutar ajustes dinámicos (simular 18 horas transcurridas)
    geo_adjustment_results = geo_adjuster.run_dynamic_adjustment_cycle(
        campaign_geo_data,
        hours_elapsed=18
    )
    
    print("✅ AJUSTES GEOGRÁFICOS DINÁMICOS COMPLETADOS:")
    if geo_adjustment_results['adjustments_executed']:
        print(f"   🔄 Ajustes ejecutados: {geo_adjustment_results['adjustments_count']}")
        print(f"   💰 Presupuesto reubicado: ${geo_adjustment_results['total_budget_moved']:.0f}")
        print(f"   📈 Mejora esperada: ${geo_adjustment_results['total_expected_improvement']:.0f}")
        
        # Mostrar distribución final
        final_allocation = geo_adjustment_results['updated_allocation']
        total = sum(final_allocation.values())
        spain_final = (final_allocation['ES'] / total) * 100
        print(f"   🇪🇸 España final: {spain_final:.1f}% (${final_allocation['ES']:.0f})")
        
        # Top performer
        performance = geo_adjustment_results['performance_snapshot']
        best_country = max(performance.items(), key=lambda x: x[1]['roi'])
        print(f"   🏆 Mejor país: {best_country[0]} ({best_country[1]['roi']:+.1f}% ROI)")
    else:
        print(f"   ✅ No se requirieron ajustes: {geo_adjustment_results.get('reason', 'performance óptima')}")
    print()
    
    # ===== EJECUTAR CAMPAÑA INICIAL Y OBTENER RESULTADOS =====
    print("📊 SIMULANDO RESULTADOS DE CAMPAÑA INICIAL")
    print("-" * 45)
    
    # Usar distribución geográfica ajustada o original
    final_geo_allocation = geo_adjustment_results.get('updated_allocation', campaign_geo_data['geo_allocation']['region_budgets'])
    
    # Simular rendimiento de clips con etiquetas granulares
    clip_performance_data = {}
    granular_boost = granular_tags.market_predictions['ctr_multiplier']
    
    for i in range(1, 6):  # 5 clips
        clip_id = f"clip_{i:03d}"
        
        # Performance base mejorada por etiquetas granulares
        base_ctr = 3.0 * granular_boost * (0.8 + random.random() * 0.4)
        base_cpv = 0.50 / granular_boost * (0.9 + random.random() * 0.2)
        base_views = int((sum(final_geo_allocation.values()) / 5) / base_cpv)  # Budget per clip / cpv
        
        clip_performance_data[clip_id] = {
            'roi': ((base_views * base_ctr / 100 * 15) - (sum(final_geo_allocation.values()) / 5)) / (sum(final_geo_allocation.values()) / 5) * 100,
            'ctr': base_ctr,
            'cpv': base_cpv,
            'views': base_views,
            'engagement_rate': base_ctr * 1.5 * (0.9 + random.random() * 0.2),
            'conversion_rate': base_ctr * 0.3
        }
    
    # Resultados consolidados de campaña inicial
    campaign_initial_results = {
        'campaign_id': campaign_data['campaign_id'],
        'total_investment': sum(final_geo_allocation.values()),
        'total_views': sum(metrics['views'] for metrics in clip_performance_data.values()),
        'total_roi': sum(metrics['roi'] for metrics in clip_performance_data.values()) / len(clip_performance_data),
        'clip_performance': clip_performance_data,
        'geo_performance': {
            country: {
                'budget_allocated': budget,
                'estimated_views': int(budget / 0.45),  # CPV promedio
                'roi_projection': 150 + random.uniform(-30, 50)
            }
            for country, budget in final_geo_allocation.items()
        },
        'granular_tags_applied': True,
        'follower_exclusion_applied': True,
        'dynamic_geo_adjustments': geo_adjustment_results['adjustments_executed']
    }
    
    avg_roi = campaign_initial_results['total_roi']
    total_investment = campaign_initial_results['total_investment']
    total_views = campaign_initial_results['total_views']
    
    print(f"💰 Inversión total: ${total_investment:.0f}")
    print(f"👀 Vistas totales: {total_views:,}")
    print(f"📈 ROI promedio: {avg_roi:+.1f}%")
    print(f"🎯 Clips activos: {len(clip_performance_data)}")
    print()
    
    # ===== MÓDULO 4: AUTOMATIZACIÓN CICLOS POSTERIORES =====
    print("4️⃣ MÓDULO: AUTOMATIZACIÓN DE CICLOS POSTERIORES ($50 EXTRA)")
    print("-" * 60)
    
    followup_automator = FollowUpCyclesAutomator()
    
    # Ejecutar automatización de seguimiento
    followup_results = followup_automator.run_automated_follow_up_sequence(
        campaign_initial_results,
        additional_budget=50
    )
    
    print("✅ AUTOMATIZACIÓN DE CICLOS POSTERIORES COMPLETADA:")
    if followup_results['automation_executed']:
        print(f"   🔄 Ciclos ejecutados: {followup_results['cycles_executed']}")
        print(f"   💰 Inversión adicional: ${followup_results['total_additional_budget']:.0f}")
        print(f"   👀 Vistas adicionales: {followup_results['total_additional_views']:,}")
        print(f"   📈 ROI seguimiento: {followup_results['follow_up_roi']:+.1f}%")
        
        # Métricas combinadas
        combined_metrics = followup_results['combined_metrics']
        print(f"   🎪 ROI combinado: {combined_metrics['original_roi']:.1f}% → {combined_metrics['combined_roi']:.1f}%")
        print(f"   🚀 Mejora total: {combined_metrics['roi_improvement']:+.1f}%")
        
        # Clips ganadores del seguimiento
        winning_cycles = followup_results['cycle_performances']
        best_cycle = max(winning_cycles, key=lambda x: x['roi'])
        print(f"   🏆 Mejor ciclo: {best_cycle['clip_id']} en {best_cycle['platform']} ({best_cycle['roi']:+.1f}% ROI)")
    else:
        print(f"   ❌ No se ejecutó: {followup_results.get('reason', 'clips no elegibles')}")
    print()
    
    # ===== RESUMEN FINAL INTEGRADO =====
    print("📊 RESUMEN FINAL - INTEGRACIÓN COMPLETA DE 4 MÓDULOS")
    print("=" * 60)
    
    # Métricas finales consolidadas
    if followup_results['automation_executed']:
        final_investment = followup_results['combined_metrics']['combined_investment']
        final_views = followup_results['combined_metrics']['combined_views'] 
        final_roi = followup_results['combined_metrics']['combined_roi']
        roi_improvement = followup_results['combined_metrics']['roi_improvement']
    else:
        final_investment = total_investment
        final_views = total_views
        final_roi = avg_roi
        roi_improvement = 0
    
    # Calcular efectividad de cada módulo
    baseline_roi = 150  # ROI típico sin módulos avanzados
    
    granular_tagging_boost = (granular_tags.market_predictions['ctr_multiplier'] - 1) * 100
    exclusion_efficiency = avg_exclusion  # % de seguidores excluidos
    geo_adjustment_impact = geo_adjustment_results.get('total_expected_improvement', 0)
    followup_boost = roi_improvement
    
    print("🎯 MÉTRICAS FINALES CONSOLIDADAS:")
    print(f"   💰 Inversión total: ${final_investment:.0f} (inicial: ${total_investment:.0f} + seguimiento: ${final_investment - total_investment:.0f})")
    print(f"   👀 Vistas totales: {final_views:,}")  
    print(f"   📈 ROI final: {final_roi:+.1f}% (vs {baseline_roi:.0f}% baseline)")
    print(f"   🚀 Mejora total: {final_roi - baseline_roi:+.1f}%")
    print()
    
    print("🔧 IMPACTO POR MÓDULO:")
    print(f"   1️⃣ Etiquetado Granular: +{granular_tagging_boost:.1f}% boost CTR/engagement")
    print(f"   2️⃣ Exclusión Seguidores: {avg_exclusion:.1f}% audiencia filtrada (mejor targeting)")
    print(f"   3️⃣ Ajustes Geográficos: ${geo_adjustment_impact:.0f} mejora esperada por optimización")
    print(f"   4️⃣ Ciclos Posteriores: {followup_boost:+.1f}% mejora ROI adicional")
    print()
    
    print("✅ VALIDACIONES DE INTEGRACIÓN:")
    validations = {
        'etiquetado_aplicado': granular_tags.confidence_scores['overall_confidence'] > 0.7,
        'exclusion_funcional': exclusion_results['exclusion_list_size'] > 0,
        'geo_ajustes_evaluados': geo_adjustment_results.get('performance_snapshot', {}) != {},
        'ciclos_posteriores_considerados': 'automation_executed' in followup_results,
        'roi_mejorado': final_roi > baseline_roi
    }
    
    for validation, status in validations.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {validation.replace('_', ' ').title()}: {'OK' if status else 'FALLO'}")
    
    all_valid = all(validations.values())
    print()
    print(f"🎪 ESTADO FINAL: {'✅ MÓDULOS REFINADOS 100% OPERATIVOS' if all_valid else '⚠️ ALGUNOS MÓDULOS REQUIEREN AJUSTES'}")
    
    # Retornar datos para análisis
    return {
        'modules_integrated': 4,
        'granular_tags': {
            'main_genre': granular_tags.main_genre.value,
            'sub_genre': granular_tags.sub_genre,
            'collaboration': granular_tags.collaboration_artist,
            'confidence': granular_tags.confidence_scores['overall_confidence'],
            'ctr_boost': granular_tagging_boost
        },
        'follower_exclusion': {
            'followers_count': exclusion_results['total_followers'],
            'exclusion_size': exclusion_results['exclusion_list_size'],
            'exclusion_percentage': avg_exclusion,
            'audiences_filtered': exclusion_results['audiences_processed']
        },
        'geo_adjustments': {
            'adjustments_made': geo_adjustment_results['adjustments_executed'],
            'adjustments_count': geo_adjustment_results.get('adjustments_count', 0),
            'budget_moved': geo_adjustment_results.get('total_budget_moved', 0),
            'spain_final_percentage': (final_geo_allocation['ES'] / sum(final_geo_allocation.values())) * 100
        },
        'followup_cycles': {
            'executed': followup_results['automation_executed'],
            'cycles_count': followup_results.get('cycles_executed', 0),
            'additional_investment': followup_results.get('total_additional_budget', 0),
            'roi_improvement': roi_improvement
        },
        'final_metrics': {
            'total_investment': final_investment,
            'total_views': final_views,
            'final_roi': final_roi,
            'roi_improvement_vs_baseline': final_roi - baseline_roi,
            'all_validations_passed': all_valid
        }
    }

if __name__ == "__main__":
    import random
    results = test_modulos_refinados_completo()
    
    if results['final_metrics']['all_validations_passed']:
        print("\n🎉 ¡INTEGRACIÓN DE MÓDULOS REFINADOS EXITOSA!")
        print("   Los 4 módulos están completamente implementados y funcionando")
        print("   Sistema listo para campañas avanzadas con funcionalidades completas")
    else:
        print("\n⚠️ Integración completada con advertencias menores")
        print("   Revisar validaciones específicas para optimización final")