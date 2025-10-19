# Guía de Integración API

Esta guía explica cómo integrar el sistema TikTok Viral ML en otros servicios y aplicaciones.

## Cliente Python

Se proporciona un cliente Python oficial con soporte tanto síncrono como asíncrono:

```python
from examples.ml_client import MLClient
import asyncio

async def main():
    async with MLClient("http://localhost:8000", "your_api_key") as client:
        # Analizar screenshot
        with open("screenshot.png", "rb") as f:
            result = await client.analyze_screenshot(f.read())
            print(result)

asyncio.run(main())
```

## Endpoints REST API

La API expone los siguientes endpoints:

### Análisis de Screenshot
```http
POST /api/v1/analyze_screenshot
Content-Type: multipart/form-data
X-API-Key: your_api_key

file=@screenshot.png
```

Respuesta:
```json
{
  "detected_elements": [
    {
      "type": "like_button",
      "confidence": 0.95,
      "coordinates": {"x": 100, "y": 200}
    }
  ],
  "processing_time": 0.45,
  "screen_state": "normal",
  "recommendation": "safe_to_interact"
}
```

### Detección de Anomalías
```http
POST /api/v1/detect_anomaly
Content-Type: application/json
X-API-Key: your_api_key

{
  "account_id": "acc_123",
  "recent_actions": ["like", "follow", "comment"],
  "context": {"device_id": "dev_1", "session_duration": 3600}
}
```

Respuesta:
```json
{
  "anomaly_detected": true,
  "anomaly_type": "rate_limit_warning",
  "confidence": 0.85,
  "recommendation": "pause",
  "cooldown_period": 1800
}
```

### Predicción de Mejor Momento
```http
POST /api/v1/predict_posting_time
Content-Type: application/json
X-API-Key: your_api_key

{
  "account_id": "acc_123",
  "timezone": "Europe/Madrid",
  "historical_data": {
    "avg_views": 5000,
    "peak_hours": [9, 18, 20]
  }
}
```

Respuesta:
```json
{
  "best_times": [
    {
      "hour": 9,
      "score": 0.85,
      "estimated_reach": 8000,
      "confidence": 0.9
    }
  ],
  "recommended_next_post": {
    "timestamp": "2025-10-19T09:00:00Z",
    "confidence": 0.85,
    "estimated_views": 10000
  },
  "account_momentum": 0.75,
  "daily_post_limit": 3
}
```

### Cálculo de Afinidad
```http
POST /api/v1/calculate_affinity
Content-Type: application/json
X-API-Key: your_api_key

{
  "account_ids": ["acc_1", "acc_2", "acc_3"],
  "context": {
    "content_type": "dance",
    "engagement_threshold": 0.5
  }
}
```

Respuesta:
```json
{
  "affinity_scores": {
    "acc_1": 0.85,
    "acc_2": 0.65,
    "acc_3": 0.45
  },
  "engagement_recommendations": [
    {
      "account_id": "acc_1",
      "recommended_actions": ["like", "follow"],
      "engagement_score": 0.85
    }
  ],
  "cluster_info": {
    "cluster_id": 3,
    "cluster_size": 20,
    "cluster_theme": "dance"
  }
}
```

## Autenticación

Todas las peticiones requieren un API key en el header `X-API-Key`.

En modo dummy, usar: `dummy_development_key`

En producción: Solicitar key al administrador del sistema.

## Gestión de Errores

La API usa códigos HTTP estándar:

- 200: OK
- 400: Petición inválida 
- 403: API key inválida
- 429: Rate limit alcanzado
- 500: Error interno

Los errores incluyen detalles en el body:

```json
{
  "error": "invalid_request",
  "message": "Missing required field: account_id",
  "details": {
    "field": "account_id",
    "code": "missing_field"
  }
}
```

## Rate Limiting

- Modo dummy: Sin límites
- Producción: Consultar con administrador

## Migración a Producción

1. Obtener API key de producción
2. Actualizar URL base a endpoint de producción
3. Activar retry con backoff exponencial
4. Implementar métricas y monitorización
5. Respetar rate limits

## Ejemplo cURL

```bash
# Analizar screenshot
curl -X POST "http://localhost:8000/api/v1/analyze_screenshot" \
  -H "X-API-Key: dummy_development_key" \
  -F "file=@screenshot.png"

# Detectar anomalías  
curl -X POST "http://localhost:8000/api/v1/detect_anomaly" \
  -H "X-API-Key: dummy_development_key" \
  -H "Content-Type: application/json" \
  -d '{"account_id": "acc_123"}'
```

## Webhooks (Próximamente)

Se añadirá soporte para notificaciones via webhook.

## Soporte

Contactar a los mantenedores para dudas o incidencias:
- GitHub Issues
- Email: support@example.com