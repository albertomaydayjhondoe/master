# 🚀 Platform Publishing System

## 📋 Resumen Ejecutivo
- **Propósito**: Sistema unificado de publicación cross-platform con optimización automática por plataforma
- **Estado**: 🟡 Durmiente - Publishers mock con simulación de publicación
- **Complejidad**: Alto
- **Dependencias**: `requests`, `pillow`, `moviepy`, `schedule`

## 🚀 Inicio Rápido

### 1. Publicación Simple (Dummy Mode)
```python
from platform_publishing.core.publisher import UnifiedPublisher

# Crear publisher en modo dummy
publisher = UnifiedPublisher(dummy_mode=True)

# Publicar en una plataforma
result = await publisher.publish_content(
    platforms=["tiktok"],
    content_path="/path/to/video.mp4",
    title="Mi video viral 🔥",
    description="Contenido increíble #viral #fyp",
    tags=["viral", "trending", "fyp"]
)

print(f"Published: {result['success']}")
print(f"Post ID: {result['post_id']}")
print(f"Platform: {result['platform']}")
```

### 2. Publicación Cross-Platform
```python
import asyncio

async def multi_platform_publish():
    # Contenido optimizado para múltiples plataformas
    content_config = {
        "video_path": "/content/original_video.mp4",
        "title": "Contenido Viral Increíble",
        "base_description": "Mira este contenido increíble que está trendendoando",
        "hashtags": ["viral", "trending", "amazing", "mustwatch"]
    }
    
    # Publicar en todas las plataformas con optimización automática
    results = await publisher.publish_multi_platform(
        platforms=["tiktok", "instagram", "youtube"],
        content_config=content_config,
        optimize_per_platform=True
    )
    
    for platform, result in results.items():
        print(f"{platform}: {'✅' if result['success'] else '❌'}")
        if result['success']:
            print(f"  Post ID: {result['post_id']}")
            print(f"  URL: {result['url']}")

asyncio.run(multi_platform_publish())
```

### 3. Programar Publicaciones
```python
from datetime import datetime, timedelta

# Programar publicación para horario óptimo
optimal_time = await publisher.get_optimal_posting_time("tiktok")
print(f"Optimal time for TikTok: {optimal_time}")

# Crear publicación programada
scheduled_post = await publisher.schedule_post(
    platforms=["tiktok", "instagram"],
    content_path="/content/viral_video.mp4",
    title="Contenido Programado",
    description="Este contenido se publicará automáticamente",
    scheduled_time=datetime.now() + timedelta(hours=2),
    auto_optimize=True
)

print(f"Scheduled post ID: {scheduled_post['schedule_id']}")
print(f"Will publish at: {scheduled_post['scheduled_time']}")
```

## ⚙️ Configuración Detallada

### Instalación de Dependencias
```bash
# Procesamiento de medios
pip install pillow
pip install moviepy
pip install opencv-python

# APIs y requests
pip install requests
pip install aiohttp
pip install httpx

# Programación y scheduling
pip install schedule  
pip install croniter
pip install APScheduler
```

### Variables de Entorno
```bash
# En .env
PUBLISHING_MODE=dummy              # dummy/production
MAX_CONCURRENT_UPLOADS=3           # Uploads simultáneos
CONTENT_STORAGE_PATH=/content/     # Almacenamiento de contenido
AUTO_OPTIMIZE_CONTENT=true         # Optimización automática
RETRY_FAILED_UPLOADS=true          # Reintentar uploads fallidos
MAX_RETRY_ATTEMPTS=3               # Máximo reintentos

# APIs de plataformas (para producción)
TIKTOK_API_KEY=your_tiktok_key
INSTAGRAM_API_TOKEN=your_instagram_token
YOUTUBE_API_KEY=your_youtube_key
TWITTER_API_KEY=your_twitter_key
```

### Configuración de Plataformas
```yaml
# config/platform_publishing/platforms.yaml
platforms:
  tiktok:
    enabled: true
    api_endpoint: "https://open-api.tiktok.com"
    max_video_size: 287309824  # 274MB
    max_video_duration: 180    # 3 minutos
    supported_formats: ["mp4", "mov", "avi"]
    optimal_resolution: "1080x1920"  # Vertical
    optimal_aspect_ratio: "9:16"
    hashtag_limit: 5
    
  instagram:
    enabled: true  
    api_endpoint: "https://graph.instagram.com"
    max_video_size: 104857600  # 100MB
    max_video_duration: 60     # 1 minuto para Reels
    supported_formats: ["mp4", "mov"]
    optimal_resolution: "1080x1920"
    optimal_aspect_ratio: "9:16"
    hashtag_limit: 30
    
  youtube:
    enabled: true
    api_endpoint: "https://www.googleapis.com/youtube/v3"
    max_video_size: 137438953472  # 128GB
    max_video_duration: 43200     # 12 horas
    supported_formats: ["mp4", "mov", "avi", "wmv", "flv"]
    optimal_resolution: "1920x1080"  # Horizontal
    optimal_aspect_ratio: "16:9"
    hashtag_limit: 15

optimization:
  auto_resize: true
  auto_crop: true
  auto_compress: true
  maintain_quality: true
  generate_thumbnails: true
```

## 📚 API Reference

### Core Classes

#### `UnifiedPublisher`
Publisher principal que maneja todas las plataformas.

```python
# Crear publisher
publisher = UnifiedPublisher(
    dummy_mode=True,
    auto_optimize=True,
    concurrent_uploads=3
)

# Verificar configuración
print(f"Publisher ready: {publisher.is_initialized}")
print(f"Platforms available: {publisher.get_available_platforms()}")
print(f"Auto optimization: {publisher.auto_optimize}")
```

#### `ContentOptimizer`
Optimizador de contenido para cada plataforma.

```python
from platform_publishing.optimization.content_optimizer import ContentOptimizer

optimizer = ContentOptimizer()

# Optimizar video para TikTok
optimized_content = await optimizer.optimize_for_platform(
    content_path="/original/video.mp4",
    platform="tiktok",
    target_quality="high"
)

print(f"Optimized video: {optimized_content['output_path']}")
print(f"Original size: {optimized_content['original_size']} MB")
print(f"Optimized size: {optimized_content['optimized_size']} MB")
print(f"Compression ratio: {optimized_content['compression_ratio']:.2f}")
```

### Publishing Methods

#### `publish_content(platforms, content_path, **kwargs) -> Dict`
Publica contenido en plataformas especificadas.

```python
# Publicación básica
result = await publisher.publish_content(
    platforms=["tiktok"],
    content_path="/videos/awesome_content.mp4",
    title="Contenido Increíble 🔥",
    description="Este video va a ser viral #fyp #trending",
    tags=["viral", "fyp", "trending"]
)

# Publicación con configuración avanzada
advanced_result = await publisher.publish_content(
    platforms=["instagram", "youtube"],
    content_path="/videos/long_video.mp4",
    title="Tutorial Completo",
    description="Tutorial paso a paso sobre...",
    tags=["tutorial", "howto", "educational"],
    
    # Configuraciones específicas
    thumbnail_path="/thumbnails/custom_thumb.jpg",
    visibility="public",
    comments_enabled=True,
    monetization=True,
    
    # Optimización
    auto_optimize=True,
    custom_optimization={
        "instagram": {"max_duration": 60, "aspect_ratio": "9:16"},
        "youtube": {"quality": "1080p", "aspect_ratio": "16:9"}
    }
)
```

#### `publish_multi_platform(platforms, content_config, **kwargs) -> Dict`
Publicación optimizada para múltiples plataformas.

```python
# Configuración de contenido
content_config = {
    "video_path": "/content/master_video.mp4",
    "title": "Contenido Multi-Plataforma",
    "base_description": "Descripción base que se adaptará por plataforma",
    "hashtags": ["viral", "content", "amazing"],
    "thumbnail_path": "/thumbnails/thumb.jpg"
}

# Publicar con optimización automática
results = await publisher.publish_multi_platform(
    platforms=["tiktok", "instagram", "youtube"],
    content_config=content_config,
    optimize_per_platform=True,
    
    # Configuraciones por plataforma
    platform_configs={
        "tiktok": {
            "description_template": "{base_description} 🎵 #TikTok {hashtags}",
            "max_hashtags": 5
        },
        "instagram": {
            "description_template": "{base_description} 📸 {hashtags}",
            "add_story": True
        },
        "youtube": {
            "description_template": "{base_description}\n\n🔔 Suscríbete para más contenido\n\nHashtags: {hashtags}",
            "category": "Entertainment"
        }
    }
)

# Procesar resultados
successful_platforms = [p for p, r in results.items() if r['success']]
failed_platforms = [p for p, r in results.items() if not r['success']]

print(f"✅ Successful: {', '.join(successful_platforms)}")
print(f"❌ Failed: {', '.join(failed_platforms)}")
```

#### `schedule_post(platforms, content_path, scheduled_time, **kwargs) -> Dict`
Programa publicación para momento específico.

```python
from datetime import datetime, timedelta

# Programar para mañana a las 8 PM
tomorrow_8pm = datetime.now().replace(hour=20, minute=0, second=0) + timedelta(days=1)

scheduled_post = await publisher.schedule_post(
    platforms=["tiktok", "instagram"],
    content_path="/content/scheduled_video.mp4",
    title="Contenido Programado",
    description="Este contenido se publicará automáticamente",
    scheduled_time=tomorrow_8pm,
    
    # Configuración del scheduler
    auto_optimize=True,
    retry_on_failure=True,
    notification_enabled=True
)

print(f"Post scheduled with ID: {scheduled_post['schedule_id']}")

# Verificar publicaciones programadas
pending_posts = await publisher.get_scheduled_posts()
for post in pending_posts:
    print(f"Scheduled: {post['title']} - {post['scheduled_time']}")

# Cancelar publicación programada
await publisher.cancel_scheduled_post(scheduled_post['schedule_id'])
```

### Content Optimization

#### `optimize_for_platform(content_path, platform, **kwargs) -> Dict`
Optimiza contenido específicamente para una plataforma.

```python
# Optimización para TikTok
tiktok_optimized = await optimizer.optimize_for_platform(
    content_path="/original/horizontal_video.mp4",
    platform="tiktok",
    
    # Configuraciones de optimización
    target_resolution="1080x1920",  # Vertical para TikTok
    target_duration=60,             # Máximo 60 segundos
    crop_mode="smart",              # Crop inteligente
    audio_enhancement=True,         # Mejorar audio
    add_captions=True              # Añadir subtítulos automáticos
)

print(f"TikTok optimization:")
print(f"  Resolution: {tiktok_optimized['resolution']}")
print(f"  Duration: {tiktok_optimized['duration']}s")
print(f"  File size: {tiktok_optimized['file_size']} MB")

# Optimización para YouTube
youtube_optimized = await optimizer.optimize_for_platform(
    content_path="/original/short_vertical_video.mp4", 
    platform="youtube",
    
    # Configuraciones para YouTube
    target_resolution="1920x1080",  # Horizontal para YouTube
    target_duration=300,            # Extender a 5 minutos si es necesario
    add_intro=True,                # Añadir intro de canal
    add_outro=True,               # Añadir outro con suscripción
    thumbnail_generation=True      # Generar thumbnail automático
)
```

#### `batch_optimize(content_list, target_platforms) -> List[Dict]`
Optimización en lote para múltiples contenidos.

```python
# Lista de contenidos para optimizar
content_batch = [
    {"path": "/videos/video1.mp4", "title": "Video 1"},
    {"path": "/videos/video2.mp4", "title": "Video 2"}, 
    {"path": "/videos/video3.mp4", "title": "Video 3"}
]

# Optimizar todos para TikTok e Instagram
optimization_results = await optimizer.batch_optimize(
    content_list=content_batch,
    target_platforms=["tiktok", "instagram"],
    
    # Configuraciones globales
    maintain_aspect_ratios=True,
    parallel_processing=True,
    max_workers=3
)

for result in optimization_results:
    print(f"Content: {result['original_path']}")
    print(f"  TikTok: {result['optimized']['tiktok']['status']}")
    print(f"  Instagram: {result['optimized']['instagram']['status']}")
```

### Analytics & Insights

#### `get_publishing_analytics(platform, time_range) -> Dict`
Obtiene analytics de publicaciones.

```python
# Analytics de TikTok última semana
tiktok_analytics = await publisher.get_publishing_analytics(
    platform="tiktok",
    time_range="7d"
)

print(f"TikTok Analytics (7 days):")
print(f"  Posts published: {tiktok_analytics['posts_count']}")
print(f"  Total views: {tiktok_analytics['total_views']:,}")
print(f"  Average engagement: {tiktok_analytics['avg_engagement']:.2f}%")
print(f"  Best performing time: {tiktok_analytics['best_time']}")

# Analytics comparativo entre plataformas
comparative_analytics = await publisher.get_comparative_analytics(
    platforms=["tiktok", "instagram", "youtube"],
    metrics=["views", "engagement", "reach"],
    time_range="30d"
)

for platform, metrics in comparative_analytics.items():
    print(f"\n{platform.upper()}:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:,}")
```

#### `get_optimal_posting_times(platform) -> List[Dict]`
Obtiene horarios óptimos de publicación.

```python
# Obtener mejores horarios para TikTok
optimal_times = await publisher.get_optimal_posting_times("tiktok")

print("Optimal posting times for TikTok:")
for time_slot in optimal_times:
    print(f"  {time_slot['day']}: {time_slot['hour']}:00 (Score: {time_slot['score']:.2f})")

# Programar próxima publicación en horario óptimo
next_optimal = await publisher.get_next_optimal_time("instagram")
print(f"Next optimal time for Instagram: {next_optimal}")

await publisher.schedule_post(
    platforms=["instagram"],
    content_path="/content/optimal_time_post.mp4",
    title="Publicación en Horario Óptimo",
    scheduled_time=next_optimal,
    auto_optimize=True
)
```

## 🔧 Troubleshooting

### Problemas de Publicación

#### 1. **Upload fallido**
```python
# Verificar estado de upload
upload_status = await publisher.check_upload_status("post_id_123")
print(f"Upload status: {upload_status['status']}")

if upload_status['status'] == 'failed':
    print(f"Error: {upload_status['error_message']}")
    
    # Reintentar upload
    retry_result = await publisher.retry_upload(
        "post_id_123",
        max_attempts=3,
        backoff_factor=2.0
    )
    
    print(f"Retry result: {retry_result['success']}")

# Debug de upload
debug_info = await publisher.get_upload_debug_info("post_id_123")
print("Upload Debug Info:")
import pprint
pprint.pprint(debug_info)
```

#### 2. **Formato de video no soportado**
```python
# Verificar compatibilidad de archivo
compatibility = await publisher.check_file_compatibility(
    "/path/to/video.avi",
    platforms=["tiktok", "instagram"]
)

for platform, status in compatibility.items():
    print(f"{platform}: {status['compatible']}")
    if not status['compatible']:
        print(f"  Issues: {', '.join(status['issues'])}")
        print(f"  Suggestions: {', '.join(status['suggestions'])}")

# Convertir automáticamente
if not compatibility['tiktok']['compatible']:
    converted_video = await optimizer.convert_to_compatible_format(
        "/path/to/video.avi",
        target_platform="tiktok"
    )
    print(f"Converted video: {converted_video['output_path']}")
```

#### 3. **API rate limits**
```python
# Verificar límites de API
rate_limits = await publisher.get_rate_limits()

for platform, limits in rate_limits.items():
    print(f"{platform}:")
    print(f"  Requests remaining: {limits['remaining']}")
    print(f"  Reset time: {limits['reset_time']}")
    
    if limits['remaining'] < 10:
        print(f"  ⚠️  Low rate limit for {platform}")

# Implementar backoff automático
await publisher.enable_smart_rate_limiting(
    backoff_strategy="exponential",
    respect_limits=True
)
```

### Problemas de Optimización

#### 4. **Optimización muy lenta**
```python
# Verificar recursos de sistema
system_resources = await optimizer.check_system_resources()
print(f"CPU usage: {system_resources['cpu_percent']}%")
print(f"Memory usage: {system_resources['memory_percent']}%") 
print(f"Disk space: {system_resources['disk_free']} GB")

# Ajustar configuración para performance
await optimizer.configure_performance_mode(
    mode="balanced",  # fast/balanced/quality
    parallel_processing=True,
    use_gpu=True if system_resources['gpu_available'] else False
)

# Procesar en lotes más pequeños
batch_size = 2 if system_resources['memory_percent'] > 80 else 5
await optimizer.set_batch_size(batch_size)
```

#### 5. **Calidad de video degradada**
```python
# Verificar configuraciones de calidad
quality_settings = await optimizer.get_quality_settings()
print("Current quality settings:")
pprint.pprint(quality_settings)

# Ajustar para mantener calidad
await optimizer.configure_quality_settings({
    "video_codec": "h264_nvenc",  # Usar GPU encoding si disponible
    "crf": 18,                    # Constant Rate Factor (menor = mejor calidad)
    "preset": "medium",           # slow/medium/fast
    "maintain_bitrate": True,     # Mantener bitrate original
    "two_pass_encoding": True     # Encoding en dos pasadas
})

# Test de calidad
quality_test = await optimizer.run_quality_test(
    "/test/sample_video.mp4",
    platforms=["tiktok", "instagram", "youtube"]
)

for platform, results in quality_test.items():
    print(f"{platform}: Quality score {results['quality_score']:.2f}/10")
```

## 🔗 Integraciones

### Con ML Integration
```python
# Usar ML para optimizar contenido
async def ml_optimized_publishing():
    from ml_integration.ultralytics_bridge import create_ml_bridge
    
    ml_bridge = create_ml_bridge()
    
    # Analizar contenido para optimización
    content_analysis = await ml_bridge.analyze_content("/videos/content.mp4")
    
    # Obtener recomendaciones de publicación
    publishing_recommendations = await ml_bridge.get_publishing_recommendations(
        content_analysis
    )
    
    # Aplicar optimizaciones basadas en ML
    optimized_config = {
        "platforms": publishing_recommendations["recommended_platforms"],
        "optimal_times": publishing_recommendations["optimal_posting_times"],
        "hashtags": publishing_recommendations["recommended_hashtags"],
        "title_suggestions": publishing_recommendations["title_variations"]
    }
    
    # Publicar con configuración optimizada por ML
    results = await publisher.publish_multi_platform(
        platforms=optimized_config["platforms"],
        content_config={
            "video_path": "/videos/content.mp4",
            "title": optimized_config["title_suggestions"][0],
            "hashtags": optimized_config["hashtags"]
        },
        scheduled_times=optimized_config["optimal_times"]
    )
    
    return results

# Predicción de performance
async def predict_content_performance(content_path):
    ml_bridge = create_ml_bridge()
    
    # Analizar contenido
    analysis = await ml_bridge.analyze_content(content_path)
    
    # Predecir performance por plataforma
    performance_predictions = {}
    
    for platform in ["tiktok", "instagram", "youtube"]:
        prediction = await ml_bridge.predict_platform_performance(
            analysis, platform
        )
        
        performance_predictions[platform] = {
            "viral_probability": prediction["viral_probability"],
            "expected_views": prediction["expected_views"],
            "engagement_rate": prediction["engagement_rate"],
            "recommendation": prediction["recommendation"]
        }
    
    # Decidir plataformas de publicación basado en predicciones
    recommended_platforms = [
        platform for platform, pred in performance_predictions.items()
        if pred["viral_probability"] > 0.6
    ]
    
    return performance_predictions, recommended_platforms
```

### Con Analytics Dashboard
```python
# Integrar métricas de publicación con dashboard
async def update_publishing_metrics():
    from analytics_dashboard.collectors.metrics_collector import MetricsCollector
    
    collector = MetricsCollector()
    
    # Recopilar métricas de todas las plataformas
    publishing_metrics = {}
    
    for platform in ["tiktok", "instagram", "youtube"]:
        platform_analytics = await publisher.get_publishing_analytics(
            platform=platform,
            time_range="24h"
        )
        
        publishing_metrics[f"{platform}_posts"] = platform_analytics["posts_count"]
        publishing_metrics[f"{platform}_views"] = platform_analytics["total_views"]
        publishing_metrics[f"{platform}_engagement"] = platform_analytics["avg_engagement"]
    
    # Métricas generales del sistema
    system_metrics = await publisher.get_system_metrics()
    
    publishing_metrics.update({
        "total_posts_today": system_metrics["total_posts_24h"],
        "success_rate": system_metrics["upload_success_rate"],
        "avg_processing_time": system_metrics["avg_processing_time"],
        "scheduled_posts_pending": len(await publisher.get_scheduled_posts())
    })
    
    # Enviar métricas al collector
    await collector.update_metrics("platform_publishing", publishing_metrics)
    
    return publishing_metrics

# Dashboard de estado de publicaciones
def render_publishing_dashboard():
    import streamlit as st
    import plotly.express as px
    
    # Obtener datos recientes
    metrics = await update_publishing_metrics()
    
    st.title("📤 Publishing Dashboard")
    
    # KPIs principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Posts Today", metrics["total_posts_today"])
    with col2:
        st.metric("Success Rate", f"{metrics['success_rate']:.1f}%")
    with col3:
        st.metric("Avg Processing Time", f"{metrics['avg_processing_time']:.1f}s")
    with col4:
        st.metric("Scheduled Posts", metrics["scheduled_posts_pending"])
    
    # Gráfico de performance por plataforma
    platform_data = {
        "Platform": ["TikTok", "Instagram", "YouTube"],
        "Posts": [
            metrics["tiktok_posts"],
            metrics["instagram_posts"], 
            metrics["youtube_posts"]
        ],
        "Views": [
            metrics["tiktok_views"],
            metrics["instagram_views"],
            metrics["youtube_views"]
        ]
    }
    
    fig = px.bar(platform_data, x="Platform", y="Posts", title="Posts by Platform")
    st.plotly_chart(fig)
```

### Con Identity Management
```python
# Asignar cuentas específicas para publicación
async def publish_with_identity_rotation():
    from identity_management.core.identity_manager import IdentityManager
    
    identity_manager = IdentityManager()
    
    # Obtener cuentas disponibles para cada plataforma
    accounts = {}
    for platform in ["tiktok", "instagram", "youtube"]:
        account = await identity_manager.get_available_account(platform)
        if account:
            accounts[platform] = account
    
    # Publicar usando cuentas específicas
    results = {}
    for platform, account in accounts.items():
        try:
            result = await publisher.publish_with_account(
                platform=platform,
                account_credentials={
                    "username": account.username,
                    "access_token": account.access_token
                },
                content_path="/content/video.mp4",
                title="Contenido con identidad específica",
                description="Publicado con cuenta rotada"
            )
            
            results[platform] = result
            
            # Log uso de cuenta
            await identity_manager.log_account_usage(
                account.id,
                action="content_publish",
                success=result["success"]
            )
            
        except Exception as e:
            results[platform] = {"success": False, "error": str(e)}
            
            # Marcar cuenta como problemática si falla
            await identity_manager.flag_account_issue(
                account.id,
                issue_type="publish_failure",
                details=str(e)
            )
    
    return results

# Rotación automática después de X publicaciones
async def auto_rotate_publishing_accounts():
    rotation_thresholds = {
        "tiktok": 5,      # Rotar después de 5 posts
        "instagram": 8,   # Rotar después de 8 posts  
        "youtube": 3      # Rotar después de 3 posts
    }
    
    for platform, threshold in rotation_thresholds.items():
        account_usage = await identity_manager.get_account_usage_stats(platform)
        
        for account_id, stats in account_usage.items():
            if stats["posts_today"] >= threshold:
                # Tiempo de rotar esta cuenta
                await identity_manager.mark_account_for_rotation(
                    account_id,
                    reason="post_threshold_reached",
                    cooldown_hours=6
                )
                
                print(f"Account {account_id} marked for rotation ({stats['posts_today']} posts)")
```

## 📈 Métricas y Monitoring

### KPIs Publishing System
- **Upload Success Rate**: % uploads exitosos (target: >95%)
- **Processing Speed**: Tiempo promedio de procesamiento (target: <60s)
- **Cross-Platform Reach**: Alcance total combinado (target: maximizar)
- **Engagement Rate**: Engagement promedio por plataforma (target: >5%)

### Publishing Analytics
```python
# Analytics completos del sistema de publicación
async def generate_publishing_analytics():
    analytics = {
        "overview": {
            "total_posts_30d": await publisher.count_posts(days=30),
            "successful_uploads": await publisher.count_successful_uploads(days=30),
            "failed_uploads": await publisher.count_failed_uploads(days=30),
            "platforms_active": len(await publisher.get_active_platforms())
        },
        
        "performance": {
            "avg_processing_time": await publisher.get_avg_processing_time(),
            "upload_success_rate": await publisher.get_upload_success_rate(),
            "optimization_efficiency": await publisher.get_optimization_efficiency(),
            "cross_platform_reach": await publisher.get_cross_platform_reach()
        },
        
        "content": {
            "video_formats_processed": await publisher.get_format_statistics(),
            "optimization_results": await publisher.get_optimization_statistics(),
            "popular_hashtags": await publisher.get_popular_hashtags(),
            "best_performing_content": await publisher.get_top_performing_content()
        },
        
        "scheduling": {
            "scheduled_posts_pending": len(await publisher.get_scheduled_posts()),
            "optimal_times_usage": await publisher.get_optimal_times_usage(),
            "scheduling_accuracy": await publisher.get_scheduling_accuracy()
        }
    }
    
    return analytics

# Reportes automáticos de publicación
async def daily_publishing_report():
    analytics = await generate_publishing_analytics()
    
    report = f"""
📤 Daily Publishing Report - {datetime.now().strftime('%Y-%m-%d')}

📊 Overview:
  • Posts Published: {analytics['overview']['total_posts_30d']} (30d)
  • Success Rate: {analytics['performance']['upload_success_rate']:.1f}%
  • Active Platforms: {analytics['overview']['platforms_active']}

⚡ Performance:
  • Avg Processing Time: {analytics['performance']['avg_processing_time']:.1f}s
  • Optimization Efficiency: {analytics['performance']['optimization_efficiency']:.1f}%
  • Cross-Platform Reach: {analytics['performance']['cross_platform_reach']:,}

📅 Scheduling:
  • Pending Posts: {analytics['scheduling']['scheduled_posts_pending']}
  • Optimal Times Usage: {analytics['scheduling']['optimal_times_usage']:.1f}%
  • Scheduling Accuracy: {analytics['scheduling']['scheduling_accuracy']:.1f}%
    """
    
    # Enviar reporte via monitoring
    from social_extensions.telegram.monitoring import get_monitor
    monitor = get_monitor()
    await monitor.send_daily_report("platform_publishing", report)
    
    return report
```

### Alertas de Publishing
```python
# Sistema de alertas para publicación
class PublishingAlertSystem:
    def __init__(self, publisher, monitor):
        self.publisher = publisher
        self.monitor = monitor
    
    async def check_publishing_alerts(self):
        alerts = []
        
        # Alerta: Tasa de fallos alta
        success_rate = await self.publisher.get_upload_success_rate(hours=6)
        if success_rate < 80:
            alerts.append({
                "type": "low_success_rate",
                "severity": "high",
                "message": f"Upload success rate only {success_rate:.1f}% in last 6h",
                "action": "check_api_status_and_content_quality"
            })
        
        # Alerta: Processing muy lento
        avg_processing = await self.publisher.get_avg_processing_time(hours=2)
        if avg_processing > 180:  # Más de 3 minutos
            alerts.append({
                "type": "slow_processing",
                "severity": "medium",
                "message": f"Average processing time {avg_processing:.1f}s",
                "action": "check_system_resources"
            })
        
        # Alerta: Muchas publicaciones programadas fallaron
        failed_scheduled = await self.publisher.count_failed_scheduled_posts(hours=24)
        if failed_scheduled > 5:
            alerts.append({
                "type": "scheduling_failures",
                "severity": "high",
                "message": f"{failed_scheduled} scheduled posts failed in 24h",
                "action": "review_scheduling_system"
            })
        
        # Enviar alertas
        for alert in alerts:
            await self.monitor.send_alert(alert)
        
        return alerts
```

## 💡 Buenas Prácticas

### 1. Optimización de Contenido
```python
# Pipeline de optimización inteligente
class SmartOptimizationPipeline:
    def __init__(self):
        self.optimization_rules = {
            "tiktok": {
                "max_duration": 60,
                "aspect_ratio": "9:16", 
                "resolution": "1080x1920",
                "audio_required": True,
                "captions_recommended": True
            },
            "instagram": {
                "max_duration": 90,
                "aspect_ratio": "9:16",
                "resolution": "1080x1920", 
                "story_version": True,
                "hashtag_optimization": True
            },
            "youtube": {
                "min_duration": 60,
                "aspect_ratio": "16:9",
                "resolution": "1920x1080",
                "thumbnail_required": True,
                "seo_optimization": True
            }
        }
    
    async def smart_optimize(self, content_path, target_platforms):
        """Optimización inteligente basada en contenido y plataformas"""
        
        # Analizar contenido original
        content_info = await self.analyze_original_content(content_path)
        
        optimized_versions = {}
        
        for platform in target_platforms:
            rules = self.optimization_rules[platform]
            
            # Decidir optimizaciones necesarias
            optimizations_needed = []
            
            if content_info["duration"] > rules["max_duration"]:
                optimizations_needed.append("trim_video")
            
            if content_info["aspect_ratio"] != rules["aspect_ratio"]:
                optimizations_needed.append("change_aspect_ratio")
            
            if content_info["resolution"] != rules["resolution"]:
                optimizations_needed.append("resize_video")
            
            # Aplicar optimizaciones
            optimized_path = await self.apply_optimizations(
                content_path,
                optimizations_needed,
                platform_rules=rules
            )
            
            optimized_versions[platform] = {
                "path": optimized_path,
                "optimizations": optimizations_needed,
                "quality_score": await self.calculate_quality_score(optimized_path)
            }
        
        return optimized_versions

# Gestión inteligente de colas de publicación
class PublishingQueueManager:
    def __init__(self):
        self.priority_queue = []
        self.scheduled_queue = []
        self.retry_queue = []
    
    async def add_to_queue(self, post_request, priority="normal"):
        """Añadir publicación a cola con prioridad"""
        
        post_request["priority"] = priority
        post_request["added_at"] = datetime.now()
        post_request["retry_count"] = 0
        
        if priority == "high":
            self.priority_queue.insert(0, post_request)
        else:
            self.priority_queue.append(post_request)
    
    async def process_queue(self):
        """Procesar cola de publicaciones"""
        
        while self.priority_queue or self.scheduled_queue or self.retry_queue:
            # Procesar por orden de prioridad
            current_request = None
            
            # 1. Prioridad alta primero
            if self.priority_queue:
                current_request = self.priority_queue.pop(0)
            
            # 2. Publicaciones programadas que llegaron a su hora
            elif self.scheduled_queue:
                now = datetime.now()
                due_posts = [p for p in self.scheduled_queue 
                           if p["scheduled_time"] <= now]
                if due_posts:
                    current_request = due_posts[0]
                    self.scheduled_queue.remove(current_request)
            
            # 3. Reintentos
            elif self.retry_queue:
                current_request = self.retry_queue.pop(0)
            
            if current_request:
                try:
                    await self.process_single_request(current_request)
                    
                except Exception as e:
                    # Manejar fallos
                    await self.handle_failed_request(current_request, e)
            
            await asyncio.sleep(1)  # Pequeño delay entre procesamiento
    
    async def handle_failed_request(self, request, error):
        """Manejar publicaciones fallidas"""
        request["retry_count"] += 1
        request["last_error"] = str(error)
        
        max_retries = 3
        
        if request["retry_count"] < max_retries:
            # Añadir a cola de reintentos con backoff
            backoff_delay = 2 ** request["retry_count"]  # Exponential backoff
            request["retry_after"] = datetime.now() + timedelta(seconds=backoff_delay)
            
            self.retry_queue.append(request)
        else:
            # Máximo reintentos alcanzado, marcar como fallido permanentemente
            await self.mark_as_failed(request)
```

### 2. Gestión de APIs y Rate Limits
```python
# Rate limiter inteligente
class SmartRateLimiter:
    def __init__(self):
        self.rate_limits = {
            "tiktok": {"requests_per_hour": 1000, "uploads_per_day": 50},
            "instagram": {"requests_per_hour": 200, "uploads_per_day": 25},
            "youtube": {"requests_per_day": 10000, "uploads_per_day": 100}
        }
        self.usage_tracking = {}
    
    async def can_make_request(self, platform, request_type="general"):
        """Verificar si se puede hacer request sin exceder límites"""
        
        current_usage = self.usage_tracking.get(platform, {})
        limits = self.rate_limits[platform]
        
        # Verificar límites por hora
        hourly_requests = current_usage.get("hourly_requests", 0)
        if hourly_requests >= limits.get("requests_per_hour", float('inf')):
            return False, "hourly_limit_exceeded"
        
        # Verificar límites diarios
        if request_type == "upload":
            daily_uploads = current_usage.get("daily_uploads", 0)
            if daily_uploads >= limits.get("uploads_per_day", float('inf')):
                return False, "daily_upload_limit_exceeded"
        
        return True, "ok"
    
    async def track_request(self, platform, request_type="general"):
        """Registrar request realizado"""
        if platform not in self.usage_tracking:
            self.usage_tracking[platform] = {
                "hourly_requests": 0,
                "daily_uploads": 0,
                "last_reset": datetime.now()
            }
        
        # Resetear contadores si ha pasado el tiempo
        await self.reset_counters_if_needed(platform)
        
        # Incrementar contadores
        self.usage_tracking[platform]["hourly_requests"] += 1
        
        if request_type == "upload":
            self.usage_tracking[platform]["daily_uploads"] += 1
    
    async def get_wait_time(self, platform, request_type="general"):
        """Calcular tiempo de espera hasta poder hacer request"""
        can_request, reason = await self.can_make_request(platform, request_type)
        
        if can_request:
            return 0
        
        if "hourly" in reason:
            # Esperar hasta la próxima hora
            now = datetime.now()
            next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            return (next_hour - now).total_seconds()
        
        elif "daily" in reason:
            # Esperar hasta el próximo día
            now = datetime.now()
            next_day = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            return (next_day - now).total_seconds()
        
        return 3600  # Default: esperar 1 hora

# Context manager para manejo de APIs
from contextlib import asynccontextmanager

@asynccontextmanager
async def api_request_context(platform, request_type="general"):
    """Context manager para requests con rate limiting automático"""
    
    rate_limiter = SmartRateLimiter()
    
    # Verificar si podemos hacer el request
    can_request, reason = await rate_limiter.can_make_request(platform, request_type)
    
    if not can_request:
        wait_time = await rate_limiter.get_wait_time(platform, request_type)
        if wait_time > 0:
            print(f"Rate limit hit for {platform}, waiting {wait_time:.0f} seconds...")
            await asyncio.sleep(wait_time)
    
    # Registrar el request
    await rate_limiter.track_request(platform, request_type)
    
    try:
        yield
    except Exception as e:
        # Log error para análisis
        print(f"API request failed for {platform}: {e}")
        raise

# Uso del context manager
async with api_request_context("tiktok", "upload") as ctx:
    result = await publisher.upload_to_tiktok(video_path)
```

### 3. Monitoreo de Calidad
```python
# Sistema de QA automático
class ContentQualityAssurance:
    def __init__(self):
        self.quality_checks = [
            self.check_video_resolution,
            self.check_audio_quality,
            self.check_duration_compliance,
            self.check_content_guidelines,
            self.check_file_integrity
        ]
    
    async def run_quality_check(self, content_path, target_platform):
        """Ejecutar checks de calidad completos"""
        
        qa_results = {
            "overall_score": 0.0,
            "checks_passed": 0,
            "total_checks": len(self.quality_checks),
            "issues": [],
            "recommendations": []
        }
        
        for check_function in self.quality_checks:
            try:
                check_result = await check_function(content_path, target_platform)
                
                if check_result["passed"]:
                    qa_results["checks_passed"] += 1
                else:
                    qa_results["issues"].append(check_result["issue"])
                    qa_results["recommendations"].extend(check_result["recommendations"])
                
            except Exception as e:
                qa_results["issues"].append(f"QA check failed: {str(e)}")
        
        # Calcular score general
        qa_results["overall_score"] = qa_results["checks_passed"] / qa_results["total_checks"]
        
        return qa_results
    
    async def check_video_resolution(self, content_path, platform):
        """Verificar resolución de video"""
        import cv2
        
        cap = cv2.VideoCapture(content_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        platform_requirements = {
            "tiktok": {"min_width": 720, "min_height": 1280, "aspect_ratio": "9:16"},
            "instagram": {"min_width": 720, "min_height": 1280, "aspect_ratio": "9:16"},
            "youtube": {"min_width": 1280, "min_height": 720, "aspect_ratio": "16:9"}
        }
        
        requirements = platform_requirements.get(platform, {})
        
        issues = []
        recommendations = []
        
        if width < requirements.get("min_width", 0):
            issues.append(f"Width {width}px below minimum {requirements['min_width']}px")
            recommendations.append("Increase video resolution")
        
        if height < requirements.get("min_height", 0):
            issues.append(f"Height {height}px below minimum {requirements['min_height']}px")
            recommendations.append("Increase video resolution")
        
        # Verificar aspect ratio
        current_ratio = width / height
        target_ratios = {"9:16": 9/16, "16:9": 16/9}
        expected_ratio = target_ratios.get(requirements.get("aspect_ratio", ""), current_ratio)
        
        if abs(current_ratio - expected_ratio) > 0.1:
            issues.append(f"Aspect ratio {current_ratio:.2f} doesn't match {requirements.get('aspect_ratio', 'N/A')}")
            recommendations.append("Adjust video aspect ratio")
        
        return {
            "passed": len(issues) == 0,
            "issue": f"Resolution issues: {', '.join(issues)}" if issues else None,
            "recommendations": recommendations
        }
    
    async def auto_fix_issues(self, content_path, qa_results, target_platform):
        """Auto-fix de problemas detectados en QA"""
        
        if qa_results["overall_score"] >= 0.8:
            return content_path  # Ya está bien
        
        fixes_applied = []
        current_path = content_path
        
        for issue in qa_results["issues"]:
            if "resolution" in issue.lower():
                # Auto-fix resolución
                fixed_path = await self.auto_fix_resolution(current_path, target_platform)
                if fixed_path != current_path:
                    fixes_applied.append("resolution_fixed")
                    current_path = fixed_path
            
            elif "aspect ratio" in issue.lower():
                # Auto-fix aspect ratio
                fixed_path = await self.auto_fix_aspect_ratio(current_path, target_platform)
                if fixed_path != current_path:
                    fixes_applied.append("aspect_ratio_fixed")
                    current_path = fixed_path
            
            elif "duration" in issue.lower():
                # Auto-fix duración
                fixed_path = await self.auto_fix_duration(current_path, target_platform)
                if fixed_path != current_path:
                    fixes_applied.append("duration_fixed")
                    current_path = fixed_path
        
        return current_path, fixes_applied
```

## 🚀 Activación del Sistema

### Checklist para Salir de Modo Dormant

- [ ] 🔑 Configurar APIs de plataformas (TikTok, Instagram, YouTube, etc.)
- [ ] 📁 Configurar almacenamiento de contenido y backups
- [ ] ⚙️ Instalar dependencias de procesamiento de medios
- [ ] 🎥 Configurar optimizadores de video/audio
- [ ] 📊 Implementar analytics y tracking de performance
- [ ] 🔄 Configurar scheduling y colas de publicación
- [ ] 📈 Conectar con sistemas de monitoring y alertas
- [ ] 🧪 Ejecutar tests de publicación en cada plataforma

### Comando de Activación
```python
# Activar platform publishing
publisher = UnifiedPublisher(
    dummy_mode=False,
    auto_optimize=True,
    concurrent_uploads=3
)

# Health check completo
health = await publisher.system_health_check()
print(f"Publishing System Ready: {health['ready']}")
print(f"Platforms configured: {health['platforms_count']}")
print(f"Optimization enabled: {health['optimization_status']}")
```

---

## 📞 Soporte

- **Publishing Issues**: Problemas de upload y APIs de plataformas
- **Content Optimization**: Optimización de videos y formatos
- **Scheduling**: Configuración de horarios y programación
- **Performance**: Optimización de velocidad y calidad de procesamiento