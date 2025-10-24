# 🔍 Monitoring System

## 📋 Resumen Ejecutivo
- **Propósito**: Sistema avanzado de monitoreo y alertas para Telegram y plataformas sociales
- **Estado**: 🟢 Activo y funcional
- **Complejidad**: Básico → Intermedio
- **Dependencias**: `statistics`, `asyncio`, `logging`

## 🚀 Inicio Rápido

### 1. Instalación
```python
from social_extensions.telegram.monitoring import TelegramMonitor, ActivityMetric

# Crear monitor
monitor = TelegramMonitor()
```

### 2. Configuración Básica
```python
# Configurar thresholds de alertas
monitor.alert_thresholds.update({
    "message_failure_rate": 0.15,  # 15% max failure rate
    "response_time": 5.0,           # 5s max response time
    "high_failure_rate": 0.25       # 25% spike threshold
})
```

### 3. Primer Ejemplo
```python
import asyncio
from datetime import datetime

async def basic_monitoring():
    # Log una actividad
    activity = ActivityMetric(
        timestamp=datetime.now(),
        type="message_sent",
        group_id=12345,
        success=True,
        duration_ms=1200.5,
        metadata={"engagement": 0.08}
    )
    
    await monitor.log_activity(activity)
    
    # Obtener salud del sistema
    health = await monitor.get_system_health()
    print(f"System Status: {health['status']}")
    print(f"Success Rate: {health['success_rate']:.1%}")

# Ejecutar
asyncio.run(basic_monitoring())
```

## ⚙️ Configuración Detallada

### Variables de Entorno
```bash
# En .env
DUMMY_MODE=true                    # Modo desarrollo
MONITORING_LOG_LEVEL=INFO         # Nivel de logging
ALERT_COOLDOWN_MINUTES=60         # Cooldown entre alertas
```

### Configuración de Thresholds
```python
# Configuración avanzada de alertas
monitor.alert_thresholds = {
    "message_failure_rate": 0.15,     # Tasa de fallo de mensajes
    "response_time": 5.0,              # Tiempo de respuesta (segundos)
    "rate_limit_hits": 10,             # Hits de rate limit
    "low_engagement": 0.05,            # Engagement mínimo
    "high_failure_rate": 0.25,         # Tasa alta de fallos
    "error_spike": 5,                  # Pico de errores (10 min)
    "flood_wait_frequent": 3,          # Flood waits por hora
    "engagement_drop": 0.7             # Caída de engagement (70%)
}
```

### Configuración de Logs
```python
import logging

# Setup logging personalizado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring.log'),
        logging.StreamHandler()
    ]
)
```

## 📚 API Reference

### Core Methods

#### `log_activity(activity: ActivityMetric)`
Registra una actividad para monitoreo.

```python
activity = ActivityMetric(
    timestamp=datetime.now(),
    type="message_sent|flood_wait|api_call",
    group_id=12345,                    # Optional
    success=True,
    duration_ms=1500.0,               # Optional
    metadata={"key": "value"}         # Datos adicionales
)

await monitor.log_activity(activity)
```

#### `get_system_health() -> Dict[str, Any]`
Obtiene el estado de salud del sistema.

```python
health = await monitor.get_system_health()
# Returns:
{
    "status": "healthy|degraded|critical",
    "success_rate": 0.985,
    "response_time_ms": 1200,
    "active_alerts": 2,
    "critical_alerts": 0,
    "activities_24h": 450,
    "monitoring_enabled": True,
    "last_updated": "2025-10-24T10:30:00Z"
}
```

#### `get_alerts(severity=None, hours=24, resolved=False)`
Obtiene alertas filtradas.

```python
# Alertas críticas no resueltas
critical_alerts = await monitor.get_alerts(
    severity="critical", 
    resolved=False
)

# Todas las alertas de las últimas 6 horas
recent_alerts = await monitor.get_alerts(hours=6)
```

#### `resolve_alert(alert_id: str) -> bool`
Resuelve una alerta específica.

```python
success = await monitor.resolve_alert("high_failure_rate_system_20251024_103000")
print(f"Alert resolved: {success}")
```

### Tipos de Alertas

| Tipo | Severidad | Trigger | Descripción |
|------|-----------|---------|-------------|
| `high_response_time` | Warning | >3000ms | Respuesta lenta detectada |
| `frequent_flood_waits` | Warning | >3/hora | Demasiados flood waits |
| `engagement_drop` | Warning | <70% promedio | Caída significativa de engagement |
| `high_failure_rate` | Critical/Warning | >25%/50% | Alta tasa de fallos |
| `message_delivery_failed` | Medium | Entrega fallida | Mensaje no entregado |
| `connection_lost` | Critical | Sin conexión | Pérdida de conectividad |

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. **Error: "statistics module not found"**
```bash
# Solución: statistics es built-in en Python 3.4+
python --version  # Verificar versión
pip install --upgrade python  # Si es necesario
```

#### 2. **Alertas no se generan**
```python
# Verificar configuración
print(monitor.alert_thresholds)
print(f"Monitoring enabled: {monitor.monitoring_enabled}")

# Verificar logs
monitor.logger.setLevel(logging.DEBUG)
```

#### 3. **Modo dummy no funciona**
```python
# Verificar configuración dummy
from config.app_settings import is_dummy_mode
print(f"Dummy mode: {is_dummy_mode()}")

# Forzar modo dummy
monitor.dummy_mode = True
```

#### 4. **Memory leak con activity_log**
```python
# El deque tiene maxlen=10000 por defecto
print(f"Activity log size: {len(monitor.activity_log)}")

# Ajustar si es necesario
monitor.activity_log = deque(maxlen=5000)  # Reducir tamaño
```

### Logs Relevantes

```bash
# Logs importantes a revistar
grep "CRITICAL ALERT" monitoring.log
grep "WARNING ALERT" monitoring.log  
grep "Activity pattern" monitoring.log
grep "Alert created" monitoring.log
```

### Debug Mode

```python
# Activar debug completo
monitor.logger.setLevel(logging.DEBUG)

# Ver configuración actual
import pprint
pprint.pprint({
    "thresholds": monitor.alert_thresholds,
    "active_alerts": len(monitor.active_alerts),
    "activities": len(monitor.activity_log),
    "groups_monitored": len(monitor.group_metrics)
})
```

## 🔗 Integraciones

### Con YouTube Executor
```python
from telegram_automation.youtube_executor.youtube_executor import YouTubeExecutor

# Integración automática de métricas
executor = YouTubeExecutor()
# El executor ya registra actividades en el monitor
```

### Con Telegram Bot
```python
from telegram_automation.bot.telegram_bot import TelegramBot

# El bot registra automáticamente:
# - Envíos de mensajes
# - Respuestas recibidas  
# - Errores de API
# - Flood waits
```

### Con Sistema de Alertas Externo
```python
# Personalizar notificaciones
async def custom_alert_handler(alert):
    if alert.severity == "critical":
        # Enviar a Slack, email, etc.
        await send_slack_notification(alert.message)
        
# Reemplazar el handler por defecto
monitor._send_alert_notification = custom_alert_handler
```

## 📈 Métricas y Monitoring

### KPIs Principales
- **Success Rate**: % de actividades exitosas (target: >95%)
- **Response Time**: Tiempo promedio de respuesta (target: <2s)
- **Alert Volume**: Número de alertas por hora (target: <5/h)
- **Resolution Time**: Tiempo promedio de resolución (target: <30min)

### Dashboards Disponibles
1. **System Health**: Estado general del sistema
2. **Activity Timeline**: Línea de tiempo de actividades  
3. **Alert Analytics**: Análisis de alertas por tipo/severidad
4. **Performance Metrics**: Métricas de rendimiento por grupo

### Alertas Configuradas
- **Slack**: Alertas críticas y warnings
- **Email**: Resumen diario y alertas críticas
- **Log Files**: Todas las alertas para auditoría
- **Dashboard**: Visualización en tiempo real

## 💡 Buenas Prácticas

### 1. Configuración de Production
```python
# Para producción
monitor.alert_thresholds["message_failure_rate"] = 0.05  # Más estricto
monitor.alert_thresholds["response_time"] = 3.0           # Más estricto

# Logging a archivo
logging.basicConfig(filename='/var/log/monitoring.log')
```

### 2. Monitoreo Proactivo
```python
# Scheduled health checks
import schedule

def scheduled_health_check():
    health = await monitor.get_system_health()
    if health["success_rate"] < 0.95:
        # Tomar acción preventiva
        pass

schedule.every(15).minutes.do(scheduled_health_check)
```

### 3. Cleanup de Datos
```python
# Limpiar alertas antiguas (ejecutar weekly)
async def cleanup_old_alerts():
    cutoff = datetime.now() - timedelta(days=7)
    monitor.alert_history = [
        alert for alert in monitor.alert_history 
        if alert.timestamp > cutoff
    ]
```

---

## 📞 Soporte

- **Issues**: Reportar en GitHub Issues
- **Docs**: [Documentation Portal](../README_SYSTEM.md)
- **Contact**: Ver CONTRIBUTING.md