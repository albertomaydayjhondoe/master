"""
Meta Ads Musical Intelligence - Ejemplo de Uso Completo
Demostración del sistema inteligente de campañas musicales contextuales
"""

import asyncio
import json
from datetime import datetime, timedelta

# Imports del sistema musical
from .musical_context_system import (
    MusicalGenre, create_trap_pixel, create_reggaeton_pixel, create_corrido_pixel,
    CampaignContext, musical_context_db
)
from .musical_intelligence_engine import musical_intelligence, quick_campaign_analysis
from .musical_ml_models import musical_ml_ensemble

async def demo_sistema_musical_completo():
    """
    🔥 DEMO COMPLETA: Sistema Inteligente de Meta Ads Musical
    
    Simula el workflow completo desde crear pixels hasta optimización automática
    """
    
    print("🎵 === META ADS MUSICAL INTELLIGENCE DEMO ===")
    print("Sistema que entiende géneros musicales y optimiza automáticamente\n")
    
    # ===== 1. CREAR PIXELS MUSICALES =====
    print("🎯 1. CREANDO PIXELS MUSICALES CON CONTEXTO...")
    
    # Pixel de Trap - Audiencia masculina joven
    trap_pixel = create_trap_pixel(
        pixel_id="TrapPixel01",
        name="Urban Trap España 2024", 
        theme="street_life"
    )
    musical_context_db.add_pixel(trap_pixel)
    print(f"   ✅ Pixel Trap creado: {trap_pixel.name}")
    
    # Pixel de Reggaetón - Audiencia femenina mixta  
    reggaeton_pixel = create_reggaeton_pixel(
        pixel_id="ReggaetonPixel01",
        name="Latin Party Hits",
        theme="party_vibes"
    )
    musical_context_db.add_pixel(reggaeton_pixel)
    print(f"   ✅ Pixel Reggaetón creado: {reggaeton_pixel.name}")
    
    # Pixel de Corrido - Audiencia masculina adulta
    corrido_pixel = create_corrido_pixel(
        pixel_id="CorridoPixel01", 
        name="Corridos Tumbados México",
        theme="narco_story"
    )
    musical_context_db.add_pixel(corrido_pixel)
    print(f"   ✅ Pixel Corrido creado: {corrido_pixel.name}")
    
    # ===== 2. CREAR CAMPAÑAS CON DIFERENTES CONTEXTOS =====
    print(f"\n🚀 2. LANZANDO CAMPAÑAS CON CONTEXTOS ESPECÍFICOS...")
    
    campaigns = []
    
    # Campaña Trap - España, audiencia masculina 18-28
    trap_campaign = CampaignContext(
        campaign_id="TRAP_ESP_001",
        pixel_profile=trap_pixel,
        budget=600.0,
        target_countries=["spain"],
        target_age_range=(18, 28),
        target_gender="male"
    )
    musical_context_db.add_campaign(trap_campaign)
    campaigns.append(trap_campaign)
    print(f"   🎯 Campaña Trap España: €{trap_campaign.budget} | {trap_campaign.target_age_range}")
    
    # Campaña Reggaetón - Colombia, audiencia femenina 16-30  
    reggaeton_campaign = CampaignContext(
        campaign_id="REGGAETON_COL_001",
        pixel_profile=reggaeton_pixel,
        budget=800.0,
        target_countries=["colombia"],
        target_age_range=(16, 30), 
        target_gender="female"
    )
    musical_context_db.add_campaign(reggaeton_campaign)
    campaigns.append(reggaeton_campaign)
    print(f"   💃 Campaña Reggaetón Colombia: €{reggaeton_campaign.budget} | {reggaeton_campaign.target_age_range}")
    
    # Campaña Corrido - México, audiencia masculina 25-45
    corrido_campaign = CampaignContext(
        campaign_id="CORRIDO_MEX_001", 
        pixel_profile=corrido_pixel,
        budget=500.0,
        target_countries=["mexico"],
        target_age_range=(25, 45),
        target_gender="male"
    )
    musical_context_db.add_campaign(corrido_campaign)
    campaigns.append(corrido_campaign)
    print(f"   🤠 Campaña Corrido México: €{corrido_campaign.budget} | {corrido_campaign.target_age_range}")
    
    # ===== 3. PREDICCIONES INICIALES POR ML ESPECIALIZADO =====
    print(f"\n🧠 3. GENERANDO PREDICCIONES ML ESPECIALIZADAS POR GÉNERO...")
    
    for campaign in campaigns:
        prediction = musical_ml_ensemble.predict_campaign_performance(campaign)
        genre = campaign.pixel_profile.musical_context.genre.value
        
        print(f"\n   📊 {genre.upper()} - {campaign.campaign_id}:")
        print(f"      CTR Predicho: {prediction.predicted_ctr:.3f} ({prediction.predicted_ctr/0.02:.1f}x baseline)")
        print(f"      CPV Predicho: €{prediction.predicted_cpv:.3f}")
        print(f"      Confianza: {prediction.confidence:.1%}")
        print(f"      Probabilidad Viral: {prediction.prob_viral_potential:.1%}")
        print(f"      Probabilidad Escalar: {prediction.prob_scale_worthy:.1%}")
        print(f"      🎯 Insights: {prediction.genre_specific_insights[0] if prediction.genre_specific_insights else 'N/A'}")
    
    # ===== 4. SIMULAR PERFORMANCE REAL (DESPUÉS DE 24H) =====
    print(f"\n📈 4. SIMULANDO PERFORMANCE REAL DESPUÉS DE 24 HORAS...")
    
    # Simular métricas realistas por género
    performance_data = {
        "TRAP_ESP_001": {
            "current_ctr": 0.018,  # Trap típico
            "current_cpv": 0.032,
            "current_watch_time": 11.8,
            "impressions": 28500,
            "clicks": 513,
            "conversions": 12
        },
        "REGGAETON_COL_001": {
            "current_ctr": 0.031,  # Reggaetón alto performance
            "current_cpv": 0.019,
            "current_watch_time": 17.2,
            "impressions": 41200,
            "clicks": 1277,
            "conversions": 28
        },
        "CORRIDO_MEX_001": {
            "current_ctr": 0.024,  # Corrido sólido
            "current_cpv": 0.025,
            "current_watch_time": 14.1,
            "impressions": 22100,
            "clicks": 530,
            "conversions": 15
        }
    }
    
    # Actualizar campañas con métricas reales
    for campaign in campaigns:
        perf = performance_data[campaign.campaign_id]
        campaign.current_ctr = perf["current_ctr"]
        campaign.current_cpv = perf["current_cpv"] 
        campaign.current_watch_time = perf["current_watch_time"]
        campaign.impressions = perf["impressions"]
        campaign.clicks = perf["clicks"]
        campaign.conversions = perf["conversions"]
        
        print(f"\n   📊 {campaign.campaign_id} - Performance Real:")
        print(f"      CTR: {campaign.current_ctr:.3f} | CPV: €{campaign.current_cpv:.3f}")
        print(f"      Impresiones: {campaign.impressions:,} | Clicks: {campaign.clicks:,}")
        print(f"      Conversiones: {campaign.conversions} | Watch Time: {campaign.current_watch_time:.1f}s")
    
    # ===== 5. ANÁLISIS INTELIGENTE AUTOMÁTICO =====
    print(f"\n🎯 5. ANÁLISIS DE INTELIGENCIA AUTOMÁTICO...")
    
    for campaign in campaigns:
        insights = await musical_intelligence.analyze_campaign_intelligence(campaign.campaign_id)
        genre = campaign.pixel_profile.musical_context.genre.value
        
        print(f"\n   🧠 INTELIGENCIA - {genre.upper()} ({campaign.campaign_id}):")
        print(f"      📈 Nota de Performance: {_calculate_performance_grade(insights)}")
        print(f"      📊 Percentil en Género: {insights.genre_percentile:.1%}")
        print(f"      🎯 Posición de Mercado: {insights.market_position.upper()}")
        print(f"      🚀 Acción Recomendada: {insights.optimization_decision.decision_type.upper()}")
        print(f"      💪 Confianza: {insights.optimization_decision.confidence:.1%}")
        
        if insights.optimization_decision.reasoning:
            print(f"      📝 Razón: {insights.optimization_decision.reasoning[0]}")
        
        # Detectar oportunidades especiales
        if insights.viral_potential:
            print(f"      🔥 ¡POTENCIAL VIRAL DETECTADO! Confianza: {insights.viral_potential['confidence']:.1%}")
        
        if insights.scaling_opportunity:
            print(f"      📈 Oportunidad de Escalar: {insights.scaling_opportunity['recommended_multiplier']:.1f}x")
    
    # ===== 6. DECISIONES AUTOMÁTICAS DE OPTIMIZACIÓN =====
    print(f"\n⚡ 6. EJECUTANDO OPTIMIZACIONES AUTOMÁTICAS...")
    
    optimization_results = []
    
    for campaign in campaigns:
        insights = await musical_intelligence.analyze_campaign_intelligence(campaign.campaign_id)
        decision = insights.optimization_decision
        
        # Ejecutar la optimización
        result = await musical_intelligence.execute_optimization_decision(decision)
        optimization_results.append(result)
        
        print(f"\n   ⚙️ {campaign.campaign_id}:")
        print(f"      🎯 Acción: {decision.decision_type.upper()}")
        print(f"      💰 Multiplicador Budget: {decision.budget_multiplier or 'N/A'}")
        print(f"      📅 Ejecutado: {result['executed_at']}")
        print(f"      ✅ Estado: {'ÉXITO' if result['success'] else 'ERROR'}")
        
        if decision.expected_improvement:
            for metric, improvement in decision.expected_improvement.items():
                print(f"      📈 {metric}: {improvement}")
    
    # ===== 7. RESUMEN COMPARATIVO POR GÉNERO =====
    print(f"\n📊 7. RESUMEN COMPARATIVO DE GÉNEROS...")
    
    genre_performance = {}
    
    for genre in [MusicalGenre.TRAP, MusicalGenre.REGGAETON, MusicalGenre.CORRIDO]:
        summary = musical_intelligence.get_genre_intelligence_summary(genre)
        
        if "error" not in summary:
            genre_performance[genre.value] = {
                "campaigns": summary["total_campaigns"],
                "avg_ctr": summary["performance_metrics"]["avg_ctr"],
                "high_performer_rate": summary["performance_metrics"]["high_performer_rate"]
            }
    
    print(f"\n   🏆 RANKING DE GÉNEROS POR PERFORMANCE:")
    sorted_genres = sorted(
        genre_performance.items(), 
        key=lambda x: x[1]["avg_ctr"], 
        reverse=True
    )
    
    for i, (genre, data) in enumerate(sorted_genres, 1):
        print(f"      {i}. {genre.upper()}")
        print(f"         CTR Promedio: {data['avg_ctr']:.3f}")
        print(f"         Tasa Alto Rendimiento: {data['high_performer_rate']:.1%}")
        print(f"         Campañas Totales: {data['campaigns']}")
    
    # ===== 8. DASHBOARD EJECUTIVO =====
    print(f"\n📋 8. DASHBOARD EJECUTIVO - RESUMEN FINAL...")
    
    total_budget = sum(c.budget for c in campaigns)
    total_conversions = sum(c.conversions for c in campaigns)
    avg_ctr = sum(c.current_ctr for c in campaigns) / len(campaigns)
    
    high_performing = len([c for c in campaigns if c.current_ctr > 0.025])
    viral_candidates = len([c for c in campaigns if c.current_ctr > 0.030])
    
    print(f"\n   💰 INVERSIÓN TOTAL: €{total_budget:,.0f}")
    print(f"   🎯 CONVERSIONES TOTALES: {total_conversions}")
    print(f"   📊 CTR PROMEDIO: {avg_ctr:.3f}")
    print(f"   🚀 CAMPAÑAS ALTO RENDIMIENTO: {high_performing}/{len(campaigns)}")
    print(f"   🔥 CANDIDATAS VIRALES: {viral_candidates}/{len(campaigns)}")
    
    # ROI estimado por género
    print(f"\n   💎 ROI ESTIMADO POR GÉNERO:")
    for campaign in campaigns:
        genre = campaign.pixel_profile.musical_context.genre.value
        revenue_estimate = campaign.conversions * 25  # €25 por conversión
        roi = (revenue_estimate / campaign.budget - 1) * 100
        print(f"      {genre.upper()}: {roi:+.1f}% ROI (€{revenue_estimate} revenue)")
    
    print(f"\n🎉 === DEMO COMPLETADA ===")
    print("Sistema Musical Intelligence funcionando al 100%!")
    print("Listo para campañas reales de trap, reggaetón, corridos y más! 🚀")
    
    return {
        "demo_completed": True,
        "campaigns_created": len(campaigns),
        "total_budget": total_budget,
        "optimization_results": optimization_results,
        "performance_summary": {
            "avg_ctr": avg_ctr,
            "total_conversions": total_conversions,
            "high_performing_campaigns": high_performing,
            "viral_candidates": viral_candidates
        }
    }

# Helper function
def _calculate_performance_grade(insights) -> str:
    """Calcular nota de performance A-F"""
    from .musical_intelligence_engine import _calculate_performance_grade as calc_grade
    return calc_grade(insights)

# Función de test rápido
async def test_sistema_basico():
    """Test básico del sistema sin demo completa"""
    
    print("🧪 Test Básico del Sistema Musical...")
    
    # Crear pixel de prueba
    test_pixel = create_trap_pixel("TEST_TRAP", "Test Trap Pixel")
    musical_context_db.add_pixel(test_pixel)
    
    # Crear campaña de prueba
    test_campaign = CampaignContext(
        campaign_id="TEST_001",
        pixel_profile=test_pixel,
        budget=500.0,
        target_countries=["spain"],
        target_age_range=(20, 30)
    )
    musical_context_db.add_campaign(test_campaign)
    
    # Test de predicción
    prediction = musical_ml_ensemble.predict_campaign_performance(test_campaign)
    
    print(f"✅ Pixel creado: {test_pixel.pixel_id}")
    print(f"✅ Campaña creada: {test_campaign.campaign_id}")
    print(f"✅ Predicción ML: CTR {prediction.predicted_ctr:.3f}, confianza {prediction.confidence:.1%}")
    
    return {"test_passed": True, "prediction": prediction}

# Casos de uso específicos
async def caso_uso_trap_viralizado():
    """Caso específico: campaña de trap que se viraliza"""
    
    print("🔥 CASO DE USO: Trap Viral España")
    
    # Crear pixel viral
    viral_pixel = create_trap_pixel("TRAP_VIRAL", "Trap Viral España 2024", "viral_street")
    musical_context_db.add_pixel(viral_pixel)
    
    # Campaña con presupuesto inicial moderado
    viral_campaign = CampaignContext(
        campaign_id="TRAP_VIRAL_001",
        pixel_profile=viral_pixel,
        budget=400.0,
        target_countries=["spain"],
        target_age_range=(16, 28),
        target_gender="male"
    )
    musical_context_db.add_campaign(viral_campaign)
    
    # Simular que se viraliza (CTR altísimo)
    viral_campaign.current_ctr = 0.045  # CTR viral
    viral_campaign.current_cpv = 0.012  # CPV excelente
    viral_campaign.impressions = 125000
    viral_campaign.clicks = 5625
    viral_campaign.conversions = 89
    
    # Análisis de la viralización
    insights = await musical_intelligence.analyze_campaign_intelligence("TRAP_VIRAL_001")
    
    print(f"📈 CTR: {viral_campaign.current_ctr:.3f} (¡VIRAL!)")
    print(f"🎯 Decisión: {insights.optimization_decision.decision_type}")
    print(f"🚀 Multiplicador recomendado: {insights.optimization_decision.budget_multiplier}x")
    print(f"🔥 Potencial viral: {insights.ml_prediction.prob_viral_potential:.1%}")
    
    return insights

if __name__ == "__main__":
    # Ejecutar demo completa
    asyncio.run(demo_sistema_musical_completo())