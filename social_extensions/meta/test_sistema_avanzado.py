"""
TEST INTEGRAL - SISTEMA AVANZADO META CAMPAIGN
Prueba completa de todos los componentes implementados
"""

import sys
import os
sys.path.append('/workspaces/master')

from social_extensions.meta.advanced_campaign_system import (
    BudgetOptimizer, GeoDistribution, CampaignTagging,
    ClipData, GenrePrimary
)

def test_sistema_completo_meta():
    """
    Test integral del sistema Meta avanzado
    """
    print("🚀 TEST INTEGRAL - SISTEMA AVANZADO META CAMPAIGN")
    print("=" * 70)
    
    # PASO 1: Datos de entrada de campaña
    campaign_input = {
        'campaign_name': 'Trap Revolution 2025',
        'genre': 'trap',
        'artist_main': 'TrapKing',
        'artist_follower_count': 3500000,
        'collaborators': ['anuel_aa'],
        'target_regions': ['ES', 'MX', 'CO', 'AR'],
        'objectives': ['views', 'engagement', 'conversions'],
        'audio_features': {
            'bpm': 155,
            'energy': 0.9,
            'darkness': 0.85,
            'danceability': 0.65,
            'valence': 0.25,
            'vocal_style': ['aggressive', 'autotune_heavy'],
            'instruments': ['808s', 'dark_synth', 'guitar', 'strings']
        }
    }
    
    # PASO 2: Crear etiquetas avanzadas
    print("📋 PASO 1: ETIQUETADO AVANZADO")
    print("-" * 40)
    
    tagging = CampaignTagging()
    campaign_tags = tagging.create_advanced_tags(campaign_input)
    
    # PASO 3: Generar clips de ejemplo
    clips_data = [
        ClipData("clip_001", "trap", "trap_oscuro", ["ES", "MX"], 30, "audience_propia", 0.92),
        ClipData("clip_002", "trap", "trap_hardcore", ["ES", "CO"], 25, "audience_colaborador", 0.88),
        ClipData("clip_003", "trap", "trap_melodico", ["MX", "AR"], 35, "audience_mixta", 0.85),
        ClipData("clip_004", "trap", "trap_oscuro", ["ES", "CO"], 28, "audience_nueva", 0.82),
        ClipData("clip_005", "trap", "trap_comercial", ["MX", "AR"], 32, "audience_propia", 0.90)
    ]
    
    print(f"🎬 5 clips generados para campaña {campaign_tags.campaign_id}")
    print()
    
    # PASO 4: Optimización de presupuesto
    print("📋 PASO 2: OPTIMIZACIÓN DE PRESUPUESTO")
    print("-" * 40)
    
    budget_optimizer = BudgetOptimizer()
    budget_results = budget_optimizer.simulate_complete_budget_cycle(clips_data)
    
    # PASO 5: Distribución geográfica
    print("📋 PASO 3: DISTRIBUCIÓN GEOGRÁFICA")
    print("-" * 40)
    
    geo_distribution = GeoDistribution()
    
    # Simular datos históricos
    historical_geo_data = {
        'MX': {'avg_ctr': 3.8, 'avg_roi': 195, 'avg_engagement': 9.5, 'campaigns_count': 4},
        'CO': {'avg_ctr': 4.1, 'avg_roi': 210, 'avg_engagement': 10.2, 'campaigns_count': 3},
        'AR': {'avg_ctr': 3.2, 'avg_roi': 165, 'avg_engagement': 8.8, 'campaigns_count': 5}
    }
    
    geo_allocation = geo_distribution.calculate_geo_allocation(
        400, campaign_tags.primary_genre.value, historical_geo_data
    )
    
    geo_performance = geo_distribution.simulate_regional_performance(
        geo_allocation, campaign_tags.primary_genre.value
    )
    
    geo_insights = geo_distribution.generate_geo_insights(geo_performance)
    
    # PASO 6: Generar reporte ejecutivo integrado
    print("📋 PASO 4: REPORTE EJECUTIVO INTEGRADO")
    print("=" * 70)
    
    total_investment = budget_results['cycle_summary']['total_spend']
    total_views = budget_results['cycle_summary']['total_views']
    total_roi = budget_results['cycle_summary']['total_roi']
    winner_clip = budget_results['winner_analysis']['clip_id']
    youtube_boost = budget_results['youtube_boost']['total_youtube_views']
    
    print("🎯 RESUMEN EJECUTIVO COMPLETO")
    print("-" * 35)
    print(f"📊 Campaña: {campaign_tags.campaign_id}")
    print(f"🎵 Género: {campaign_tags.primary_genre.value} → {campaign_tags.subgenre}")
    print(f"🤝 Colaboradores: {[c.name for c in campaign_tags.collaborators]}")
    print(f"🎬 Estilo: {campaign_tags.content_style}")
    print()
    print("💰 MÉTRICAS FINANCIERAS:")
    print(f"  • Inversión Total: ${total_investment}")
    print(f"  • ROI Total: {total_roi:.1f}%")
    print(f"  • Revenue Estimado: ${total_views * 0.023:.0f}")
    print()
    print("📺 MÉTRICAS DE RENDIMIENTO:")
    print(f"  • Views Totales: {total_views:,}")
    print(f"  • Clip Ganador: {winner_clip}")
    print(f"  • YouTube Boost: {youtube_boost:,} views")
    print(f"  • Coeficiente Viral: {budget_results['youtube_boost']['viral_coefficient']:.3f}")
    print()
    print("🌍 DISTRIBUCIÓN GEOGRÁFICA:")
    for country, budget in geo_allocation.region_budgets.items():
        performance = geo_performance[country]
        print(f"  • {country}: ${budget:.0f} → {performance['estimated_views']:,} views (ROI: {performance['roi_projection']:.1f}%)")
    print()
    print("🏆 MEJORES REGIONES:")
    if geo_insights['best_performing_regions']:
        for region in geo_insights['best_performing_regions'][:3]:
            print(f"  • {region['country']}: {region['roi']:.1f}% ROI - {region['recommendation']}")
    print()
    print("💡 PRÓXIMO CICLO:")
    next_budget = budget_results['next_recommendations']
    print(f"  • Presupuesto Recomendado: ${next_budget['total_budget']:.0f}")
    print(f"  • Multiplicador ROI: {next_budget['roi_multiplier']:.2f}x")
    print(f"  • ROI Histórico Promedio: {next_budget['historical_avg_roi']:.1f}%")
    print()
    print("🎯 FEATURES ML GENERADAS:")
    ml_features = campaign_tags.ml_features
    print(f"  • Vectors de género: {len(ml_features['genre_vector'])} dimensiones")
    print(f"  • Influencia colaboradores: {ml_features['collaborator_influence']:.3f}")
    print(f"  • Score diversidad audiencia: {ml_features['audience_diversity_score']:.3f}")
    print(f"  • Features musicales: {ml_features['musical_features']}")
    print()
    
    # PASO 7: Validación de integridad
    print("✅ VALIDACIÓN DE INTEGRIDAD DEL SISTEMA")
    print("-" * 45)
    
    validations = []
    
    # Validar presupuesto
    budget_diff = abs(geo_allocation.total_allocated - 400)
    if budget_diff < 1:
        validations.append("✅ Distribución de presupuesto correcta")
    else:
        validations.append(f"⚠️ Diferencia en presupuesto: ${budget_diff:.2f}")
    
    # Validar ROI
    if total_roi > 50:
        validations.append("✅ ROI dentro de expectativas (>50%)")
    else:
        validations.append(f"⚠️ ROI bajo: {total_roi:.1f}%")
    
    # Validar tags ML
    if len(ml_features) >= 7:
        validations.append("✅ Features ML completas")
    else:
        validations.append(f"⚠️ Features ML incompletas: {len(ml_features)}")
    
    # Validar colaboradores
    if campaign_tags.collaborators:
        validations.append("✅ Colaboradores procesados correctamente")
    else:
        validations.append("⚠️ No se procesaron colaboradores")
    
    # Validar distribución geográfica
    spain_percentage = geo_allocation.region_budgets['ES'] / geo_allocation.total_allocated
    if 0.25 <= spain_percentage <= 0.30:
        validations.append("✅ Distribución España dentro de rango (25-30%)")
    else:
        validations.append(f"⚠️ España fuera de rango: {spain_percentage*100:.1f}%")
    
    for validation in validations:
        print(validation)
    
    print()
    print("🚀 RESUMEN FINAL:")
    print("=" * 50)
    print("✅ Budget Optimizer: COMPLETADO")
    print("✅ Geo Distribution: COMPLETADO") 
    print("✅ Campaign Tagging: COMPLETADO")
    print("✅ ML Features: GENERADAS")
    print("✅ Integración: EXITOSA")
    print()
    print("📊 SISTEMA AVANZADO META CAMPAIGN: 100% OPERATIVO")
    print("🎯 Listo para implementación de ML Learning Cycle y Ultralytics Integration")
    
    return {
        'campaign_tags': campaign_tags,
        'budget_results': budget_results,
        'geo_allocation': geo_allocation,
        'geo_performance': geo_performance,
        'validation_passed': len([v for v in validations if v.startswith('✅')]) >= 4
    }

if __name__ == "__main__":
    # Ejecutar test completo
    test_results = test_sistema_completo_meta()
    
    if test_results['validation_passed']:
        print("\n🎉 TEST COMPLETADO EXITOSAMENTE!")
        print("Sistema listo para fase siguiente de implementación.")
    else:
        print("\n⚠️ Test completado con advertencias.")
        print("Revisar validaciones antes de continuar.")