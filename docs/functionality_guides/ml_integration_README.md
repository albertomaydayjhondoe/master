# 🧠 Machine Learning Integration

## 📋 Resumen Ejecutivo
- **Propósito**: Bridge entre sistema social media y Ultralytics YOLO para análisis de contenido ML
- **Estado**: 🟡 Durmiente - Listo para activación
- **Complejidad**: Avanzado
- **Dependencias**: `ultralytics`, `opencv-python`, `torch`

## 🚀 Inicio Rápido

### 1. Instalación (Modo Dormant)
```python
from ml_integration.ultralytics_bridge import create_ml_bridge

# Crear bridge en modo dummy (seguro)
ml_bridge = create_ml_bridge(dummy_mode=True)
print(f"ML Bridge Status: {ml_bridge.dummy_mode}")
```

### 2. Verificar Disponibilidad
```python
from ml_integration.ultralytics_bridge import ML_INTEGRATION_STATUS

print("ML Integration Status:")
for key, value in ML_INTEGRATION_STATUS.items():
    print(f"  {key}: {value}")
```

### 3. Análisis Básico (Dummy Mode)
```python
import asyncio

async def analyze_content():
    # Analizar contenido (dummy data)
    result = await ml_bridge.analyze_content("/path/to/video.mp4")
    
    print(f"Objects detected: {len(result.detected_objects)}")
    print(f"Engagement prediction: {result.engagement_prediction:.2f}")
    print(f"Viral probability: {result.viral_probability:.2f}")
    print(f"Quality score: {result.quality_score:.2f}")

asyncio.run(analyze_content())
```

## ⚙️ Configuración Detallada

### Instalación Completa (Para Activación)
```bash
# Dependencias ML
pip install ultralytics
pip install opencv-python
pip install torch torchvision

# Verificar instalación
python -c "from ultralytics import YOLO; print('✅ Ultralytics OK')"
python -c "import cv2; print('✅ OpenCV OK')"
```

### Variables de Entorno
```bash
# En .env para activación
ML_MODE=production                 # production/dummy  
YOLO_MODEL_PATH=/models/yolov8n.pt # Ruta del modelo
GPU_ACCELERATION=true             # Usar GPU si disponible
ML_CONFIDENCE_THRESHOLD=0.5       # Threshold de confianza
ML_MAX_DETECTIONS=100            # Max detecciones por imagen
```

### Configuración Avanzada
```python
# Configurar ML bridge para producción
ml_config = {
    "model_path": "/path/to/yolov8n.pt",
    "confidence_threshold": 0.5,
    "iou_threshold": 0.45,
    "max_detections": 100,
    "target_objects": [
        "person", "car", "phone", "laptop", "bottle", 
        "chair", "book", "clock", "tv", "bicycle"
    ],
    "engagement_factors": {
        "face_present": 1.3,      # Boost si hay caras
        "motion_detected": 1.2,   # Boost si hay movimiento  
        "bright_colors": 1.1,     # Boost colores vibrantes
        "text_overlay": 0.9,      # Penalizar texto encima
        "multiple_people": 1.4    # Boost múltiples personas
    }
}

ml_bridge.config.update(ml_config)
```

## 📚 API Reference

### Core Classes

#### `UltralyticsMLBridge`
Puente principal entre sistema y ML.

```python
# Crear instancia
bridge = UltralyticsMLBridge(dummy_mode=False)  # Modo producción

# Verificar inicialización
print(f"Initialized: {bridge.is_initialized}")
print(f"Model loaded: {bridge.model is not None}")
```

#### `MLAnalysisResult`
Resultado del análisis ML.

```python
@dataclass
class MLAnalysisResult:
    timestamp: datetime              # Cuando se hizo el análisis
    file_path: str                  # Archivo analizado
    detected_objects: List[Dict]    # Objetos detectados
    confidence_scores: List[float]  # Scores de confianza
    scene_analysis: Dict[str, Any]  # Análisis de escena
    engagement_prediction: float    # Predicción engagement (0-1)
    viral_probability: float        # Probabilidad viral (0-1)  
    quality_score: float           # Score de calidad (0-1)
```

### Methods Principales

#### `analyze_content(file_path: str) -> MLAnalysisResult`
Analiza video/imagen para optimización.

```python
# Análisis completo
result = await ml_bridge.analyze_content("/videos/content.mp4")

# Acceder a resultados
print("Detected Objects:")
for obj in result.detected_objects:
    print(f"  {obj['class']}: {obj['confidence']:.2f}")

print(f"\nScene Analysis:")
for key, value in result.scene_analysis.items():
    print(f"  {key}: {value}")
```

#### `predict_viral_potential(analysis_result) -> Dict`
Predice potencial viral basado en análisis.

```python
# Obtener predicción viral
viral_prediction = ml_bridge.predict_viral_potential(result)

print(f"Viral Score: {viral_prediction['viral_score']:.2f}")
print(f"Recommendation: {viral_prediction['recommendation']}")

# Factores que contribuyen
for factor, score in viral_prediction['factors'].items():
    print(f"  {factor}: {score:.2f}")
```

#### `get_trending_elements() -> List[Dict]`
Obtiene elementos visuales trending actuales.

```python
# Elementos en tendencia
trending = ml_bridge.get_trending_elements()

for element in trending:
    print(f"{element['element']}: {element['trend_score']:.2f}")
    print(f"  Category: {element['category']}")
    print(f"  Tip: {element['recommendation']}")
```

#### `optimize_for_platform(content_path, platform) -> Dict`
Optimiza análisis para plataforma específica.

```python
# Optimización por plataforma
platforms = ["tiktok", "instagram", "youtube"]

for platform in platforms:
    optimization = ml_bridge.optimize_for_platform(
        "/content/video.mp4", 
        platform
    )
    
    print(f"\n{platform.upper()} Optimization:")
    print(f"  Score: {optimization['score']:.2f}")
    for rec in optimization['recommendations']:
        print(f"  - {rec}")
```

### Estructuras de Datos

#### Objetos Detectados
```python
detected_object = {
    "class": "person",           # Clase del objeto
    "confidence": 0.85,          # Confianza (0-1)
    "bbox": [100, 100, 200, 300] # Bounding box [x1,y1,x2,y2]
}
```

#### Análisis de Escena  
```python
scene_analysis = {
    "brightness": 0.7,           # Brillo promedio (0-1)
    "contrast": 0.6,             # Contraste (0-1)  
    "motion_intensity": 0.4,     # Intensidad movimiento (0-1)
    "color_diversity": 0.8,      # Diversidad colores (0-1)
    "face_count": 2,             # Número de caras detectadas
    "text_detected": True        # Si hay texto en imagen
}
```

## 🔧 Troubleshooting

### Problemas de Instalación

#### 1. **Error: "No module named 'ultralytics'"**
```bash
# Instalar Ultralytics
pip install ultralytics

# Si hay problemas con PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

#### 2. **Error: "OpenCV not found"**
```bash
# Instalar OpenCV
pip install opencv-python

# Para funcionalidad completa
pip install opencv-contrib-python
```

#### 3. **GPU no detectada**
```bash
# Verificar GPU
python -c "import torch; print(torch.cuda.is_available())"

# Instalar versión GPU de PyTorch  
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Problemas de Modelo

#### 4. **Error: "Model file not found"**
```python
# Verificar path del modelo
import os
model_path = "/path/to/yolov8n.pt"
print(f"Model exists: {os.path.exists(model_path)}")

# Descargar modelo automáticamente
from ultralytics import YOLO
model = YOLO("yolov8n.pt")  # Se descarga automáticamente
```

#### 5. **Memoria insuficiente**
```python
# Reducir tamaño de imagen
ml_bridge.config["max_image_size"] = 640  # Reducir de 1280

# Procesar en lotes más pequeños
ml_bridge.config["batch_size"] = 1
```

### Debug Mode

```python
# Activar logs detallados
import logging
logging.getLogger("ultralytics").setLevel(logging.DEBUG)

# Verificar configuración
print("ML Bridge Config:")
import pprint
pprint.pprint(ml_bridge.config)

# Test básico
test_result = await ml_bridge.analyze_content("/test/image.jpg")
print(f"Test analysis successful: {test_result is not None}")
```

## 🔗 Integraciones

### Con TikTok Flow System
```python
# Integration con apply branch (cuando se active)
from tiktok_flow_system import TikTokFlowSystem

# ML analysis alimenta al sistema viral
async def content_pipeline(video_path):
    # Análisis ML
    ml_result = await ml_bridge.analyze_content(video_path)
    
    # Si el contenido es prometedor
    if ml_result.viral_probability > 0.6:
        # Enviar al sistema TikTok para amplificación
        # tiktok_system.queue_for_publishing(video_path, ml_result)
        pass
```

### Con Sistema de Monitoring
```python
from social_extensions.telegram.monitoring import ActivityMetric

# Registrar análisis ML como actividad
async def log_ml_analysis(file_path, result):
    activity = ActivityMetric(
        timestamp=datetime.now(),
        type="ml_analysis",
        group_id=None,
        success=result is not None,
        duration_ms=result.processing_time if result else None,
        metadata={
            "file_path": file_path,
            "viral_probability": result.viral_probability if result else 0,
            "objects_detected": len(result.detected_objects) if result else 0
        }
    )
    
    await monitor.log_activity(activity)
```

### Con Content Optimization
```python
# Pipeline de optimización automática
async def optimize_content_pipeline(video_path):
    # 1. Análisis ML
    analysis = await ml_bridge.analyze_content(video_path)
    
    # 2. Obtener recomendaciones
    viral_pred = ml_bridge.predict_viral_potential(analysis)
    
    # 3. Optimizar por plataforma
    optimizations = {}
    for platform in ["tiktok", "instagram", "youtube"]:
        optimizations[platform] = ml_bridge.optimize_for_platform(
            video_path, platform
        )
    
    # 4. Generar reporte
    return {
        "analysis": analysis,
        "viral_prediction": viral_pred,
        "platform_optimizations": optimizations,
        "recommendation": "publish" if viral_pred["viral_score"] > 0.7 else "optimize"
    }
```

## 📈 Métricas y Monitoring

### KPIs ML
- **Analysis Speed**: Tiempo promedio de análisis (target: <30s/video)
- **Prediction Accuracy**: Precisión de predicciones virales (target: >70%)  
- **Model Confidence**: Confianza promedio de detecciones (target: >0.8)
- **Processing Throughput**: Videos procesados por hora (target: >20/h)

### Dashboards ML
1. **Model Performance**: Accuracy, speed, confidence metrics
2. **Content Analysis**: Trends en objetos detectados, escenas populares
3. **Viral Predictions**: Histórico de predicciones vs resultados reales
4. **Platform Optimization**: Efectividad por plataforma

### Monitoring Automático
```python
# Métricas automáticas
async def track_ml_metrics():
    # Speed tracking
    start_time = time.time()
    result = await ml_bridge.analyze_content(video_path)
    analysis_time = time.time() - start_time
    
    # Log metrics
    await monitor.log_activity(ActivityMetric(
        timestamp=datetime.now(),
        type="ml_performance",
        success=True,
        duration_ms=analysis_time * 1000,
        metadata={
            "confidence_avg": statistics.mean(result.confidence_scores),
            "objects_detected": len(result.detected_objects),
            "viral_probability": result.viral_probability
        }
    ))
```

## 💡 Buenas Prácticas

### 1. Gestión de Recursos
```python
# Limitar memoria GPU
import torch
torch.cuda.set_per_process_memory_fraction(0.7)

# Cleanup después de análisis
def cleanup_gpu():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
```

### 2. Batch Processing
```python
# Procesar múltiples archivos eficientemente
async def batch_analyze(file_paths):
    results = []
    for batch in chunks(file_paths, batch_size=4):
        batch_results = await asyncio.gather(*[
            ml_bridge.analyze_content(path) for path in batch
        ])
        results.extend(batch_results)
        cleanup_gpu()  # Limpiar entre batches
    
    return results
```

### 3. Cache de Resultados
```python
import hashlib
import pickle

# Cache análisis para evitar re-procesamiento
def cache_analysis_result(file_path, result):
    file_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
    cache_path = f"/cache/{file_hash}.pkl"
    
    with open(cache_path, 'wb') as f:
        pickle.dump(result, f)

def get_cached_analysis(file_path):
    file_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
    cache_path = f"/cache/{file_hash}.pkl"
    
    if os.path.exists(cache_path):
        with open(cache_path, 'rb') as f:
            return pickle.load(f)
    return None
```

## 🚀 Activación del Sistema

### Checklist para Salir de Modo Dormant

- [ ] ✅ Instalar dependencias (`ultralytics`, `opencv-python`, `torch`)
- [ ] 📁 Descargar modelos YOLO requeridos  
- [ ] ⚙️ Configurar variables de entorno
- [ ] 🧪 Ejecutar tests de integración
- [ ] 📊 Configurar monitoring ML
- [ ] 🔧 Ajustar thresholds para producción

### Comando de Activación
```python
# Activar sistema ML
ml_bridge = create_ml_bridge(dummy_mode=False)

# Verificar que todo funciona
health_check = await ml_bridge.system_health_check()
print(f"ML System Ready: {health_check['ready']}")
```

---

## 📞 Soporte

- **ML Issues**: Reportar problemas específicos de ML
- **Model Updates**: Solicitar nuevos modelos o mejoras
- **Performance**: Optimizaciones de velocidad/precisión
- **Integration**: Ayuda con integraciones complejas