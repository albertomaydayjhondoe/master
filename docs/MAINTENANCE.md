# Guía de Mantenimiento

Esta guía proporciona información para mantener el sistema TikTok Viral ML de forma segura y eficiente.

## Mantenimiento Regular

### Diario

- [ ] **Revisar logs de errores**
  ```bash
  docker compose logs --tail=100 ml-api
  docker compose logs --tail=100 n8n
  ```

- [ ] **Verificar estado de dispositivos**
  ```bash
  adb devices
  # Verificar que todos los dispositivos estén conectados
  ```

- [ ] **Revisar métricas en Grafana**
  - Engagement rates
  - Detecciones de anomalías
  - Uso de recursos (CPU/GPU/RAM)

- [ ] **Check de alertas**
  - Revisar canal Discord para alertas
  - Verificar que no haya shadowbans detectados

### Semanal

- [ ] **Backup de base de datos**
  ```bash
  docker exec postgres pg_dump -U tiktok_ml tiktok_viral_db > backup_$(date +%Y%m%d).sql
  ```

- [ ] **Revisar performance de modelos ML**
  - Accuracy de detecciones
  - False positive rate
  - Processing time

- [ ] **Limpiar logs antiguos**
  ```bash
  find logs/ -name "*.log" -mtime +7 -delete
  ```

- [ ] **Actualizar dependencias de seguridad**
  ```bash
  pip list --outdated
  # Revisar y actualizar paquetes con vulnerabilidades conocidas
  ```

### Mensual

- [ ] **Reentrenar modelos ML** (si hay datos nuevos)
  ```bash
  python -m ml_core.training.train_yolo
  ```

- [ ] **Rotar API keys**
  - Generar nuevas keys
  - Actualizar en servicios
  - Deprecar keys antiguas

- [ ] **Auditoría de seguridad**
  - Revisar logs de acceso
  - Verificar que no haya accesos no autorizados
  - Check de configuración de firewall

- [ ] **Optimización de base de datos**
  ```sql
  VACUUM ANALYZE;
  REINDEX DATABASE tiktok_viral_db;
  ```

- [ ] **Review de cuentas**
  - Verificar estado de cuentas TikTok
  - Identificar cuentas con bajo rendimiento
  - Revisar métricas de engagement

### Trimestral

- [ ] **Actualización mayor de dependencias**
  - Actualizar Python y librerías principales
  - Probar en entorno staging antes de producción

- [ ] **Revisión de arquitectura**
  - Evaluar si se necesitan más dispositivos
  - Revisar capacidad de GPU
  - Optimizar workflows de n8n

- [ ] **Backup completo del sistema**
  - Base de datos
  - Modelos ML entrenados
  - Configuraciones
  - Workflows de n8n

- [ ] **Auditoría de compliance**
  - Verificar cumplimiento de ToS de TikTok
  - Revisar políticas de privacidad
  - Documentar cambios regulatorios

## Monitoreo

### Métricas Clave

#### Sistema
- **CPU Usage**: < 80% promedio
- **GPU Usage**: < 90% promedio
- **RAM Usage**: < 85% del total
- **Disk Space**: > 20% libre
- **Network Latency**: < 100ms promedio

#### Aplicación
- **API Response Time**: < 500ms (p95)
- **Model Inference Time**: < 200ms (p95)
- **Error Rate**: < 1%
- **Request Success Rate**: > 99%

#### Negocio
- **Engagement Rate**: Monitorear tendencia
- **Shadowban Rate**: < 5%
- **Account Growth**: Según objetivos
- **Content Performance**: Analizar patterns

### Alertas Configuradas

#### Críticas (Acción inmediata)
- Sistema caído o inaccesible
- GPU/CUDA errors
- Shadowban detectado
- Base de datos inaccesible
- Dispositivos desconectados (> 3)

#### Advertencias (Revisar en 24h)
- Alto uso de recursos (> 85%)
- Tasa de error elevada (> 5%)
- Bajo engagement rate
- Anomalías en patrones de uso
- Latencia elevada (> 1s)

#### Informativas
- Actualización de modelo completada
- Backup exitoso
- Rotación de credenciales
- Mantenimiento programado

## Resolución de Problemas

### Problema: Alta tasa de shadowbans

**Síntomas**: Múltiples cuentas detectadas con shadowban

**Causas posibles**:
- Patrones de comportamiento demasiado agresivos
- Modelos ML necesitan reentrenamiento
- Proxies bloqueados

**Solución**:
1. Pausar automatización en cuentas afectadas
2. Revisar y ajustar parámetros de rate limiting
3. Actualizar training data con patrones más humanos
4. Rotar proxies
5. Esperar período de cooldown (24-48h)

### Problema: GPU out of memory

**Síntomas**: CUDA errors, crashes del servicio ML

**Causas posibles**:
- Batch size demasiado grande
- Memory leak
- Múltiples inferencias simultáneas

**Solución**:
1. Reducir batch size en config
2. Reiniciar servicio ML
3. Implementar queue para inferencias
4. Considerar upgrade de GPU
5. Optimizar modelo (quantization, pruning)

### Problema: Dispositivos desconectados

**Síntomas**: ADB no detecta dispositivos

**Causas posibles**:
- Cables USB defectuosos
- Dispositivos en modo sleep
- Driver issues
- ADB server crashed

**Solución**:
1. Reiniciar servidor ADB: `adb kill-server && adb start-server`
2. Verificar conexiones físicas
3. Reboot dispositivos problemáticos
4. Verificar permisos USB
5. Actualizar drivers si es necesario

### Problema: n8n workflows no ejecutan

**Síntomas**: Workflows stuck o no se disparan

**Causas posibles**:
- API keys inválidas
- Servicios externos caídos
- Configuración incorrecta
- Rate limits alcanzados

**Solución**:
1. Revisar logs de n8n: `docker compose logs n8n`
2. Verificar credenciales en n8n UI
3. Test manual de endpoints
4. Revisar rate limits
5. Reiniciar workflow o n8n completo

## Backup y Recuperación

### Estrategia de Backup

#### Base de Datos (Diario)
```bash
#!/bin/bash
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)

docker exec postgres pg_dump -U tiktok_ml tiktok_viral_db | gzip > \
  "$BACKUP_DIR/tiktok_viral_db_$DATE.sql.gz"

# Mantener solo últimos 30 días
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete
```

#### Modelos ML (Después de cada reentrenamiento)
```bash
#!/bin/bash
MODEL_DIR="/app/data/models/production"
BACKUP_DIR="/backups/models"
DATE=$(date +%Y%m%d)

tar -czf "$BACKUP_DIR/models_$DATE.tar.gz" "$MODEL_DIR"
```

#### Configuraciones (Semanal)
```bash
#!/bin/bash
CONFIG_DIRS="config/ orchestration/ monitoring/"
BACKUP_DIR="/backups/config"
DATE=$(date +%Y%m%d)

tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" $CONFIG_DIRS
```

### Procedimiento de Recuperación

#### Recuperar Base de Datos
```bash
# Detener servicios que usan la DB
docker compose stop ml-api n8n

# Restaurar backup
gunzip < backup_20251023.sql.gz | \
  docker exec -i postgres psql -U tiktok_ml tiktok_viral_db

# Reiniciar servicios
docker compose start ml-api n8n
```

#### Recuperar Modelos
```bash
cd /app/data/models/
tar -xzf /backups/models/models_20251023.tar.gz
# Reiniciar servicio ML
docker compose restart ml-api
```

## Actualizaciones

### Actualizar Código

```bash
# 1. Backup actual
git branch backup-$(date +%Y%m%d)

# 2. Pull últimos cambios
git pull origin main

# 3. Actualizar dependencias
pip install -r requirements.txt --upgrade

# 4. Ejecutar migraciones (si aplica)
# alembic upgrade head

# 5. Test en staging
DUMMY_MODE=false pytest tests/integration/

# 6. Desplegar
docker compose up -d --build

# 7. Verificar
curl http://localhost:8000/health
```

### Actualizar Modelos ML

```bash
# 1. Backup modelo actual
cp data/models/production/tiktok_ui_detector.pt \
   data/models/checkpoints/tiktok_ui_detector_backup_$(date +%Y%m%d).pt

# 2. Entrenar nuevo modelo
python -m ml_core.training.train_yolo

# 3. Validar en staging
python -m ml_core.training.validate_model

# 4. Si OK, modelo ya está en production/
# 5. Reiniciar servicio
docker compose restart ml-api

# 6. Monitorear métricas por 24h
# Si hay problemas, revertir a backup
```

## Optimizaciones

### Performance

1. **Caching de inferencias ML**
   - Implementar Redis para cachear resultados frecuentes
   - Reducir carga en GPU

2. **Batch processing**
   - Agrupar múltiples inferencias
   - Mejor utilización de GPU

3. **Database indexes**
   - Añadir índices a columnas frecuentemente consultadas
   - Optimizar queries lentas

4. **Image preprocessing**
   - Resize imágenes antes de guardar
   - Usar formatos eficientes (WebP)

### Costos

1. **Proxies**
   - Evaluar diferentes proveedores
   - Negociar planes por volumen
   - Rotar IPs eficientemente

2. **Cloud resources**
   - Right-size instancias
   - Usar spot instances cuando sea posible
   - Apagar servicios no-críticos fuera de horas

3. **Storage**
   - Comprimir logs antiguos
   - Limpiar datos no necesarios
   - Usar object storage para archivos grandes

## Escalabilidad

### Escalar Horizontalmente

#### Añadir más dispositivos:
1. Configurar nuevo dispositivo con ADB
2. Añadir entrada en `config/devices/device_profiles.json`
3. Reiniciar device farm manager
4. Verificar detección: `adb devices`

#### Añadir más instancias ML API:
1. Desplegar nuevo container con mismo código
2. Configurar load balancer (nginx/HAProxy)
3. Shared storage para modelos
4. Actualizar n8n endpoints

### Escalar Verticalmente

#### Upgrade GPU:
1. Apagar servicios ML
2. Instalar nueva GPU
3. Actualizar drivers CUDA
4. Verificar: `nvidia-smi`
5. Ajustar batch sizes si es necesario
6. Reiniciar servicios

## Seguridad Continua

### Checklist Mensual

- [ ] Revisar logs de acceso a API
- [ ] Verificar integridad de credenciales
- [ ] Auditar usuarios/roles (si aplica)
- [ ] Escanear vulnerabilidades: `pip audit`
- [ ] Actualizar certificados SSL/TLS
- [ ] Revisar configuración de firewall
- [ ] Check de backups (restaurar uno para probar)
- [ ] Documentar incidentes del mes

### Respuesta a Incidentes

#### Si se detecta acceso no autorizado:
1. **Contener**: Desactivar credenciales comprometidas
2. **Investigar**: Revisar logs para identificar alcance
3. **Erradicar**: Cambiar todas las credenciales relacionadas
4. **Recuperar**: Restaurar a estado conocido bueno
5. **Documentar**: Registrar incidente y lecciones aprendidas

## Contactos de Emergencia

- **Administrador de Sistema**: [email/teléfono]
- **DevOps Lead**: [email/teléfono]
- **ML Engineer**: [email/teléfono]
- **Proveedor GoLogin**: [soporte@gologin.com]
- **Proveedor Proxies**: [según proveedor]

## Recursos Útiles

- [Documentación oficial de Ultralytics YOLO](https://docs.ultralytics.com/)
- [n8n Documentation](https://docs.n8n.io/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [ADB Documentation](https://developer.android.com/studio/command-line/adb)

---

**Última actualización**: 2025-10-23  
**Próxima revisión**: 2026-01-23
