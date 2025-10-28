"""
🧠 Script de Setup Meta ML - Configuración completa del sistema
Configura todo el sistema Meta ML con datos de YouTube, Spotify y distribución España-LATAM
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Agregar ruta raíz
sys.path.append(str(Path(__file__).parent.parent))

from ml_core.sistema_meta_ml import meta_ml_system
from v2.meta_ads_400.meta_ml_integration import meta_ml_integrator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_meta_ml_system():
    """Setup completo del sistema Meta ML"""
    
    print("🧠 META ML SYSTEM SETUP")
    print("=" * 50)
    
    try:
        # 1. Verificar configuración
        logger.info("📋 Step 1: Verificando configuración...")
        
        # Crear directorio de modelos
        models_dir = Path("models/meta_ml")
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear directorio de datos
        data_dir = Path("data/meta_ml")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        print("✅ Directorios creados")
        
        # 2. Datos dummy para entrenamiento inicial
        logger.info("📊 Step 2: Generando datos de entrenamiento dummy...")
        
        meta_ads_data = generate_dummy_meta_ads_data()
        youtube_data = generate_dummy_youtube_data()
        spotify_data = generate_dummy_spotify_data()
        
        print(f"✅ Generados: {len(meta_ads_data)} Meta Ads + {len(youtube_data)} YouTube + {len(spotify_data)} Spotify")
        
        # 3. Procesar datos multi-plataforma
        logger.info("🔄 Step 3: Procesando datos multi-plataforma...")
        
        processed_data = await meta_ml_system.process_data_sources(
            meta_ads_data, youtube_data, spotify_data
        )
        
        print(f"✅ Procesados: {processed_data['total_high_quality_users']} usuarios cross-platform")
        
        # 4. Entrenar modelos iniciales
        logger.info("🤖 Step 4: Entrenando modelos ML...")
        
        if len(processed_data["features_dataframe"]) >= 10:
            training_result = await meta_ml_system.train_models(processed_data["features_dataframe"])
            print(f"✅ Modelos entrenados: ROI Score {training_result.get('roi_score', 'N/A'):.3f}")
        else:
            print("⚠️ Pocos datos para entrenar, usando modelos dummy")
        
        # 5. Test de predicción
        logger.info("🎯 Step 5: Probando sistema de predicción...")
        
        test_campaign = {
            "campaign_id": "test_reggaeton_2025",
            "artist": "Test Artist",
            "song": "Test Song",
            "daily_budget": 400.0,
            "target_countries": ["ES", "MX", "CO"]
        }
        
        prediction = await meta_ml_system.predict_optimization(test_campaign)
        
        print(f"✅ Predicción generada: ROI esperado {prediction.expected_roi:.2f}x")
        print(f"   - España: {prediction.spain_percentage}%")
        print(f"   - LATAM: {len(prediction.latam_distribution)} países")
        print(f"   - Optimizaciones: {len(prediction.target_segments)} segmentos")
        
        # 6. Test de integración
        logger.info("🔗 Step 6: Probando integración completa...")
        
        youtube_analytics = {
            "channel": "test_channel",
            "viewers": generate_youtube_viewers_data()
        }
        
        spotify_analytics = {
            "artist": "Test Artist",
            "listeners": generate_spotify_listeners_data()
        }
        
        integration_result = await meta_ml_integrator.integrate_ml_with_campaign(
            test_campaign, youtube_analytics, spotify_analytics
        )
        
        if integration_result["success"]:
            optimizations = integration_result["ml_integration"]["optimizations_applied"]
            print(f"✅ Integración exitosa: {len(optimizations)} optimizaciones aplicadas")
        else:
            print(f"⚠️ Integración parcial: {integration_result.get('error', 'Unknown error')}")
        
        # 7. Guardar configuración
        logger.info("💾 Step 7: Guardando configuración...")
        
        config = {
            "setup_date": "2025-10-27",
            "version": "1.0.0",
            "models_trained": True,
            "data_quality_threshold": 0.7,
            "geographic_distribution": {
                "spain_minimum": 35.0,
                "latam_variable": 65.0,
                "exploration_budget": 20.0
            },
            "ml_thresholds": {
                "high_performance": 130.0,
                "low_performance": 70.0,
                "auto_approval_threshold": 50.0
            },
            "api_endpoints": {
                "ml_system": "http://localhost:8006",
                "dashboard": "http://localhost:8501"
            }
        }
        
        config_path = Path("config/meta_ml_config.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuración guardada: {config_path}")
        
        # 8. Summary
        print("\n" + "=" * 50)
        print("🎉 META ML SYSTEM SETUP COMPLETO")
        print("=" * 50)
        print(f"📊 Dashboard ML: streamlit run dashboard_meta_ml.py --server.port 8501")
        print(f"🤖 API ML: python -m uvicorn ml_core.sistema_meta_ml:app --port 8006")
        print(f"📋 Configuración: {config_path}")
        print("\n🎯 READY FOR €400 META ADS CAMPAIGNS!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en setup: {str(e)}")
        return False

def generate_dummy_meta_ads_data():
    """Generar datos dummy de Meta Ads"""
    from ml_core.sistema_meta_ml import MetaAdsPerformance
    from datetime import datetime, timedelta
    import random
    
    data = []
    countries = ["ES", "MX", "CO", "AR", "CL"]
    age_ranges = ["18-24", "25-34", "35-44"]
    
    for i in range(50):
        country = random.choice(countries)
        performance_multiplier = 1.0
        
        # España: performance más estable
        if country == "ES":
            performance_multiplier = random.uniform(0.8, 1.2)
        # México/Colombia: alto performance
        elif country in ["MX", "CO"]:
            performance_multiplier = random.uniform(1.1, 1.6)
        # Argentina: bajo performance
        elif country == "AR":
            performance_multiplier = random.uniform(0.6, 1.0)
        # Chile: muy alto performance (exploración)
        elif country == "CL":
            performance_multiplier = random.uniform(1.3, 1.8)
        
        data.append(MetaAdsPerformance(
            campaign_id=f"campaign_{i//10}",
            creative_id=f"creative_{i%5}",
            utm_source="meta_ads",
            ctr=0.03 + random.uniform(-0.01, 0.02) * performance_multiplier,
            retention_rate=0.65 + random.uniform(-0.15, 0.25) * performance_multiplier,
            conversions=int(random.uniform(3, 15) * performance_multiplier),
            cost_per_conversion=random.uniform(3.0, 8.0) / performance_multiplier,
            engagement_rate=0.06 + random.uniform(-0.02, 0.04) * performance_multiplier,
            country=country,
            region="ES" if country == "ES" else "LATAM",
            age_range=random.choice(age_ranges),
            gender=random.choice(["male", "female", "mixed"]),
            device_type=random.choice(["mobile", "desktop"]),
            landing_page_time=int(random.uniform(20, 90) * performance_multiplier),
            landing_page_conversions=int(random.uniform(1, 8) * performance_multiplier),
            timestamp=datetime.now() - timedelta(days=random.randint(0, 30))
        ))
    
    return data

def generate_dummy_youtube_data():
    """Generar datos dummy de YouTube (filtrados)"""
    from ml_core.sistema_meta_ml import YouTubeData
    from datetime import datetime, timedelta
    import random
    
    data = []
    countries = ["ES", "MX", "CO", "AR", "CL"]
    
    for i in range(80):
        # Solo usuarios con retención >40% y orgánicos
        retention = random.uniform(0.41, 0.95)  # >40% filtro
        is_organic = random.choice([True, True, True, False])  # 75% orgánicos
        is_recurring = random.choice([True, False])
        
        if retention > 0.4 and is_organic:  # Aplicar filtros
            data.append(YouTubeData(
                video_id=f"video_{i//20}",
                user_id=f"yt_user_{i}",
                retention_rate=retention,
                is_organic=is_organic,
                is_recurring=is_recurring,
                age=random.randint(16, 45),
                country=random.choice(countries),
                device=random.choice(["mobile", "desktop", "tablet"]),
                gender=random.choice(["male", "female"]) if random.random() > 0.1 else None,
                watch_time=int(random.uniform(30, 180)),
                engagement_actions=random.sample(["like", "comment", "share", "subscribe"], 
                                              random.randint(0, 3)),
                timestamp=datetime.now() - timedelta(days=random.randint(0, 14))
            ))
    
    return data

def generate_dummy_spotify_data():
    """Generar datos dummy de Spotify (filtrados)"""
    from ml_core.sistema_meta_ml import SpotifyData
    from datetime import datetime, timedelta
    import random
    
    data = []
    countries = ["ES", "MX", "CO", "AR", "CL"]
    
    for i in range(60):
        # Solo oyentes orgánicos que guardan o repiten
        is_organic = random.choice([True, True, True, False])  # 75% orgánicos
        saved_track = random.choice([True, False])
        repeat_listens = random.randint(0, 8)
        
        if is_organic and (saved_track or repeat_listens > 1):  # Aplicar filtros
            data.append(SpotifyData(
                track_id=f"track_{i//15}",
                user_id=f"sp_user_{i}",
                is_organic_listener=is_organic,
                has_saved_track=saved_track,
                repeat_listens=repeat_listens,
                age=random.randint(16, 40),
                country=random.choice(countries),
                gender=random.choice(["male", "female"]) if random.random() > 0.1 else None,
                listening_time=int(random.uniform(60, 240)),
                playlist_additions=random.randint(0, 3),
                timestamp=datetime.now() - timedelta(days=random.randint(0, 7))
            ))
    
    return data

def generate_youtube_viewers_data():
    """Generar datos de viewers YouTube para integración"""
    import random
    
    viewers = []
    countries = ["ES", "MX", "CO", "AR", "CL"]
    
    for i in range(100):
        viewers.append({
            "user_id": f"yt_viewer_{i}",
            "country": random.choice(countries),
            "age": random.randint(18, 40),
            "retention_rate": random.uniform(0.42, 0.88),  # Filtrados >40%
            "traffic_source": "organic" if random.random() > 0.25 else "paid",
            "is_recurring": random.choice([True, False]),
            "watch_time": random.randint(30, 180),
            "actions": random.sample(["like", "comment", "share"], random.randint(0, 2))
        })
    
    return viewers

def generate_spotify_listeners_data():
    """Generar datos de listeners Spotify para integración"""
    import random
    
    listeners = []
    countries = ["ES", "MX", "CO", "AR", "CL"]
    
    for i in range(80):
        listeners.append({
            "user_id": f"sp_listener_{i}",
            "country": random.choice(countries),
            "age": random.randint(16, 35),
            "playlist_source": "organic" if random.random() > 0.2 else "external_paid",
            "saved_track": random.choice([True, False]),
            "repeat_listens": random.randint(0, 6),
            "listening_time": random.randint(90, 240)
        })
    
    return listeners

if __name__ == "__main__":
    asyncio.run(setup_meta_ml_system())