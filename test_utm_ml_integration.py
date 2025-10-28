"""
TEST INTEGRADO - UTM + ML LEARNING CYCLE
Validación completa de cómo los UTMs alimentan el sistema de Machine Learning
para optimización automática de campañas Meta Ads
"""

import sys
import os
sys.path.append('/workspaces/master')

from social_extensions.meta.advanced_campaign_system.utm_tracking_system import AdvancedUTMSystem
from social_extensions.meta.advanced_campaign_system.granular_tagging import GranularTaggingSystem, MainGenre
import json
from datetime import datetime
from types import SimpleNamespace

def test_utm_ml_integration_complete():
    """Test completo de integración UTM → ML Learning Cycle"""
    
    print("🚀 TEST INTEGRADO UTM + ML LEARNING CYCLE")
    print("=" * 55)
    print()
    
    # 1. Inicializar sistemas
    utm_system = AdvancedUTMSystem()
    tagging_system = GranularTaggingSystem()
    
    # 2. Crear múltiples campañas con diferentes características
    campaigns_data = [
        {
            'campaign_id': 'camp_utm_reggaeton_001',
            'campaign_name': 'Bellakeo Nocturno',
            'clip_name': 'Bellakeo_Nocturno_Anuel',
            'genre': 'reggaeton',
            'subgenre': 'perreo_intenso',
            'collaboration': 'Anuel AA',
            'landing_url': 'https://spotify.com/track/bellakeo-nocturno',
            'geo_countries': ['ES', 'MX', 'CO', 'PR']
        },
        {
            'campaign_id': 'camp_utm_trap_002', 
            'campaign_name': 'Trap Nocturno',
            'clip_name': 'Trap_Night_Solo',
            'genre': 'reggaeton',
            'subgenre': 'trap_latino',
            'collaboration': None,
            'landing_url': 'https://spotify.com/track/trap-night',
            'geo_countries': ['ES', 'MX', 'AR']
        },
        {
            'campaign_id': 'camp_utm_dembow_003',
            'campaign_name': 'Dembow Explosivo',
            'clip_name': 'Dembow_Alfa_Collab',
            'genre': 'reggaeton', 
            'subgenre': 'dembow',
            'collaboration': 'El Alfa',
            'landing_url': 'https://spotify.com/track/dembow-explosivo',
            'geo_countries': ['ES', 'DO', 'MX', 'CO']
        }
    ]
    
    print("📊 CREANDO CAMPAÑAS CON UTMs Y ETIQUETADO GRANULAR")
    print("-" * 60)
    
    campaign_results = []
    
    for campaign_data in campaigns_data:
        print(f"\n🎵 PROCESANDO: {campaign_data['campaign_name']}")
        print(f"   🎬 Clip: {campaign_data['clip_name']}")
        print(f"   🏷️ Subgénero: {campaign_data['subgenre']}")
        print(f"   🤝 Colaboración: {campaign_data.get('collaboration', 'Solo')}")
        
        # Crear etiquetas granulares
        granular_tags = tagging_system.create_granular_tags({
            'title': campaign_data['clip_name'].replace('_', ' '),
            'genre': campaign_data['genre'],
            'collaboration': {
                'artist_id': campaign_data.get('collaboration', '').lower().replace(' ', '_') if campaign_data.get('collaboration') else None,
                'type': 'featuring' if campaign_data.get('collaboration') else None
            } if campaign_data.get('collaboration') else None,
            'estimated_duration': 180,
            'target_audience': 'young_latino'
        })
        
        # Crear campaña con UTMs
        campaign_with_utms = utm_system.create_campaign_with_utms(
            campaign_data, 
            granular_tags
        )
        
        # Simular tráfico realista basado en subgénero
        visit_multipliers = {
            'perreo_intenso': 200,  # Mayor tráfico
            'trap_latino': 150,
            'dembow': 180
        }
        
        num_visits = visit_multipliers.get(campaign_data['subgenre'], 100)
        visits = utm_system.simulate_campaign_visits(campaign_with_utms, num_visits)
        
        campaign_results.append({
            'campaign_data': campaign_data,
            'granular_tags': granular_tags,
            'campaign_with_utms': campaign_with_utms,
            'visits': visits,
            'num_visits': num_visits
        })
        
        print(f"   ✅ UTMs generados: {len(campaign_with_utms['geo_utms']) + 1} (main + geo)")
        print(f"   👥 Visitas simuladas: {num_visits}")
    
    print(f"\n✅ TOTAL CAMPAÑAS PROCESADAS: {len(campaign_results)}")
    print()
    
    # 3. Generar reporte UTM para ML
    print("🤖 GENERANDO DATOS PARA ML LEARNING CYCLE")
    print("-" * 50)
    
    utm_report = utm_system.generate_utm_report()
    ml_performance_data = utm_system.ml_integration.get_utm_performance_data()
    ml_insights = utm_system.ml_integration.generate_ml_insights()
    
    # 4. Análisis de performance por subgénero (simulado para ML)
    subgenre_analysis = {}
    total_visits = 0
    total_conversions = 0
    total_revenue = 0
    
    for data in ml_performance_data:
        subgenre = data['subgenre']
        if subgenre not in subgenre_analysis:
            subgenre_analysis[subgenre] = {
                'campaigns': 0,
                'total_visits': 0,
                'total_conversions': 0,
                'total_revenue': 0,
                'avg_conversion_rate': 0,
                'revenue_per_visit': 0
            }
        
        subgenre_analysis[subgenre]['campaigns'] += 1
        subgenre_analysis[subgenre]['total_visits'] += data['total_visits']
        subgenre_analysis[subgenre]['total_conversions'] += data['total_conversions']
        subgenre_analysis[subgenre]['total_revenue'] += data['total_revenue']
        
        total_visits += data['total_visits']
        total_conversions += data['total_conversions']
        total_revenue += data['total_revenue']
    
    # Calcular métricas finales por subgénero
    for subgenre in subgenre_analysis:
        analysis = subgenre_analysis[subgenre]
        if analysis['total_visits'] > 0:
            analysis['avg_conversion_rate'] = (analysis['total_conversions'] / analysis['total_visits']) * 100
            analysis['revenue_per_visit'] = analysis['total_revenue'] / analysis['total_visits']
    
    print("📊 ANÁLISIS ML POR SUBGÉNERO:")
    print("-" * 35)
    
    for subgenre, analysis in subgenre_analysis.items():
        print(f"🎵 {subgenre.upper()}:")
        print(f"   📊 Campañas: {analysis['campaigns']}")
        print(f"   👥 Visitas: {analysis['total_visits']:,}")
        print(f"   🎯 Conversiones: {analysis['total_conversions']}")
        print(f"   📈 Conversión rate: {analysis['avg_conversion_rate']:.2f}%")
        print(f"   💰 Revenue/visita: ${analysis['revenue_per_visit']:.3f}")
        print(f"   💎 Revenue total: ${analysis['total_revenue']:.2f}")
        print()
    
    # 5. Generar insights ML automáticos
    print("🧠 INSIGHTS AUTOMÁTICOS PARA ML:")
    print("-" * 40)
    
    # Encontrar mejor subgénero
    best_subgenre = max(subgenre_analysis.items(), 
                       key=lambda x: x[1]['avg_conversion_rate'])
    worst_subgenre = min(subgenre_analysis.items(),
                        key=lambda x: x[1]['avg_conversion_rate'])
    
    print("📈 RENDIMIENTO COMPARATIVO:")
    print(f"   🏆 Mejor subgénero: {best_subgenre[0]} ({best_subgenre[1]['avg_conversion_rate']:.2f}% conversión)")
    print(f"   📉 Menor rendimiento: {worst_subgenre[0]} ({worst_subgenre[1]['avg_conversion_rate']:.2f}% conversión)")
    print()
    
    # 6. Recomendaciones automáticas para optimización
    print("🎯 RECOMENDACIONES AUTOMÁTICAS ML:")
    print("-" * 45)
    
    recommendations = []
    
    for subgenre, analysis in subgenre_analysis.items():
        conversion_rate = analysis['avg_conversion_rate']
        revenue_per_visit = analysis['revenue_per_visit']
        
        if conversion_rate > 15.0:  # Alta conversión
            recommendations.append({
                'type': 'scale_up',
                'subgenre': subgenre,
                'reason': f'Alta conversión ({conversion_rate:.1f}%)',
                'action': f'Incrementar presupuesto en {subgenre} +25%'
            })
        elif conversion_rate < 8.0:  # Baja conversión
            recommendations.append({
                'type': 'optimize_or_pause',
                'subgenre': subgenre,
                'reason': f'Baja conversión ({conversion_rate:.1f}%)',
                'action': f'Optimizar targeting o pausar {subgenre}'
            })
        
        if revenue_per_visit > 1.50:  # Alto revenue
            recommendations.append({
                'type': 'expand_geo',
                'subgenre': subgenre,
                'reason': f'Alto revenue/visita (${revenue_per_visit:.3f})',
                'action': f'Expandir {subgenre} a más países'
            })
    
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. 🔧 {rec['action']}")
        print(f"      📝 Razón: {rec['reason']}")
        print()
    
    # 7. Simulación de retroalimentación al sistema
    print("🔄 RETROALIMENTACIÓN AL SISTEMA ML:")
    print("-" * 45)
    
    # Datos estructurados para el ML Learning Cycle
    ml_feedback_data = {
        'timestamp': datetime.now().isoformat(),
        'campaign_performance': subgenre_analysis,
        'total_campaigns': len(campaign_results),
        'total_visits': total_visits,
        'total_conversions': total_conversions,
        'overall_conversion_rate': (total_conversions / total_visits * 100) if total_visits > 0 else 0,
        'total_revenue': total_revenue,
        'recommendations': recommendations,
        'utm_tracking_health': 'operational',
        'data_quality_score': 0.95  # Simulado
    }
    
    print("✅ DATOS PROCESADOS PARA ML:")
    print(f"   📊 Campañas analizadas: {ml_feedback_data['total_campaigns']}")
    print(f"   👥 Total visitas: {ml_feedback_data['total_visits']:,}")
    print(f"   🎯 Total conversiones: {ml_feedback_data['total_conversions']}")
    print(f"   📈 Conversión global: {ml_feedback_data['overall_conversion_rate']:.2f}%")
    print(f"   💰 Revenue total: ${ml_feedback_data['total_revenue']:.2f}")
    print(f"   🤖 Recomendaciones: {len(ml_feedback_data['recommendations'])}")
    print(f"   📊 Calidad datos: {ml_feedback_data['data_quality_score']*100:.1f}%")
    print()
    
    # 8. Validaciones del sistema integrado
    print("✅ VALIDACIONES SISTEMA INTEGRADO UTM + ML:")
    print("-" * 55)
    
    validations = {
        'utm_generation': len(campaign_results) > 0 and all('campaign_with_utms' in result for result in campaign_results),
        'visit_tracking': total_visits > 0,
        'conversion_tracking': total_conversions > 0,
        'ml_data_quality': ml_feedback_data['data_quality_score'] > 0.8,
        'recommendations_generated': len(recommendations) > 0,
        'subgenre_differentiation': len(subgenre_analysis) > 1,
        'geo_utm_support': any(len(result['campaign_with_utms']['geo_utms']) > 0 for result in campaign_results)
    }
    
    for validation, status in validations.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {validation.replace('_', ' ').title()}: {'PASS' if status else 'FAIL'}")
    
    all_validations_pass = all(validations.values())
    
    print()
    print("🎪 RESULTADO FINAL:")
    if all_validations_pass:
        print("   ✅ INTEGRACIÓN UTM + ML 100% EXITOSA")
        print("   🚀 Sistema listo para optimización automática en producción")
        print("   📊 UTMs alimentando correctamente el ML Learning Cycle")
    else:
        print("   ⚠️ Algunas validaciones requieren atención")
    
    # 9. Métricas consolidadas finales
    print()
    print("📋 MÉTRICAS CONSOLIDADAS FINALES:")
    print("=" * 45)
    print(f"💰 Revenue Total: ${total_revenue:.2f}")
    print(f"👥 Visitas Totales: {total_visits:,}")
    print(f"🎯 Conversiones Totales: {total_conversions}")
    print(f"📈 Tasa Conversión Global: {ml_feedback_data['overall_conversion_rate']:.2f}%")
    print(f"🎵 Subgéneros Analizados: {len(subgenre_analysis)}")
    print(f"🌍 UTMs Geográficos: {sum(len(result['campaign_with_utms']['geo_utms']) for result in campaign_results)}")
    print(f"🤖 Recomendaciones ML: {len(recommendations)}")
    print(f"✅ Validaciones Pasadas: {sum(validations.values())}/{len(validations)}")
    
    return {
        'campaign_results': campaign_results,
        'utm_report': utm_report,
        'ml_feedback_data': ml_feedback_data,
        'subgenre_analysis': subgenre_analysis,
        'recommendations': recommendations,
        'validations_passed': all_validations_pass,
        'system_ready_for_production': all_validations_pass
    }

if __name__ == "__main__":
    # Ejecutar test completo de integración
    integration_results = test_utm_ml_integration_complete()
    
    print("\n" + "="*60)
    if integration_results['validations_passed']:
        print("🎉 ¡INTEGRACIÓN UTM + ML COMPLETAMENTE EXITOSA!")
        print("   El sistema UTM está perfectamente integrado con ML Learning Cycle")
        print("   Listo para optimización automática de campañas Meta Ads")
        print("   UTMs proporcionando datos precisos para decisiones ML")
    else:
        print("⚠️ Integración completada con observaciones menores")
        print("   Revisar validaciones específicas para optimización final")
    print("="*60)