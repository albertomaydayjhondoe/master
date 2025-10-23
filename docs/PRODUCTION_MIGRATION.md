# Guía de Migración a Producción

Esta guía detalla los pasos necesarios para migrar del modo dummy (desarrollo) al modo producción del TikTok Viral ML System.

## Estado Actual

El sistema está configurado en **modo dummy** por defecto:
- `DUMMY_MODE=true` (ver `config/app_settings.py`)
- Usa implementaciones mock para todos los servicios
- No requiere GPUs, dispositivos físicos ni credenciales
- Ideal para desarrollo y testing

## Requisitos de Producción

### Hardware

1. **Servidor ML**
   - GPU NVIDIA con CUDA support (recomendado: RTX 3090 o superior)
   - Mínimo 32GB RAM
   - 500GB+ almacenamiento SSD
   - Ubuntu 22.04 LTS o similar

2. **Device Farm**
   - 10 dispositivos Android físicos
   - Android 10+ con USB debugging habilitado
   - Hub USB de calidad con alimentación externa
   - Servidor con ADB y Appium configurado

3. **Red**
   - Conexión estable de alta velocidad
   - IPs dedicadas o proxies rotativos de calidad
   - Firewall configurado

### Software

1. **Python & Dependencies**
   ```bash
   Python 3.11+
   CUDA Toolkit 11.8+
   cuDNN 8.6+
   ```

2. **Servicios**
   - PostgreSQL 15+
   - n8n (workflow automation)
   - Grafana (monitoring)
   - Docker & Docker Compose

3. **Cuentas y Credenciales**
   - GoLogin API key y suscripción
   - Servicio de proxies (Bright Data, Oxylabs, etc.)
   - Cuentas TikTok para automatizar (con autorización)
   - Weights & Biases account (opcional, para training tracking)

## Pasos de Migración

### Fase 1: Preparación del Entorno

#### 1.1 Clonar y Configurar Repositorio

```bash
git clone <repository-url>
cd master
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

#### 1.2 Instalar Dependencias de Producción

```bash
# Instalar dependencias ML (requiere CUDA)
pip install -r requirements.txt
pip install -r requirements-ml.txt

# Verificar instalación de PyTorch con CUDA
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

#### 1.3 Configurar Variables de Entorno

```bash
# Copiar ejemplo y editar
cp docker/.env.example docker/.env
nano docker/.env  # O tu editor preferido
```

**Variables críticas a configurar:**

```bash
# Cambiar de dummy a producción
DUMMY_MODE=false

# PostgreSQL
POSTGRES_USER=tiktok_ml
POSTGRES_PASSWORD=<contraseña_segura_única>
POSTGRES_DB=tiktok_viral_db

# ML API
ML_API_KEY=<generar_api_key_segura>
MODEL_PATH=/app/data/models/production
DATASET_PATH=/app/data/datasets

# GoLogin
GOLOGIN_API_KEY=<tu_gologin_api_key>

# Proxies
PROXY_PROVIDER_API_KEY=<tu_proxy_api_key>
PROXY_PROVIDER=brightdata  # o tu proveedor

# Device Farm
ADB_SERVER_HOST=<ip_del_servidor_adb>
APPIUM_HOST=<ip_del_servidor_appium>
APPIUM_PORT=4723

# Monitoring
GRAFANA_ADMIN_PASSWORD=<contraseña_segura>
DISCORD_WEBHOOK_URL=<tu_webhook_discord>

# Training (opcional)
WANDB_API_KEY=<tu_wandb_key>
```

### Fase 2: Modelos de Machine Learning

#### 2.1 Preparar Datasets

```bash
# Crear estructura de directorios
mkdir -p data/datasets/tiktok_ui/{train,val,test}/{images,labels}
mkdir -p data/models/{production,checkpoints}
```

**Estructura esperada:**
```
data/datasets/tiktok_ui/
├── train/
│   ├── images/    # Screenshots etiquetadas
│   └── labels/    # Archivos .txt formato YOLO
├── val/
│   ├── images/
│   └── labels/
└── data.yaml      # Config YOLO (ya existe en config/ml/)
```

#### 2.2 Recopilar Screenshots para Training

Necesitarás screenshots etiquetadas de TikTok UI para entrenar el modelo:

1. **Captura de Screenshots** (100-500 imágenes mínimo)
   - Diferentes estados de la UI
   - Varios tipos de contenido
   - Diferentes resoluciones de pantalla
   - Modos día/noche

2. **Etiquetado** (usar LabelImg o Roboflow)
   - Botones: like, follow, comment, share
   - Elementos: video_player, profile_icon, avatar, overlay text
   - Formato: YOLO (class x_center y_center width height)

3. **Organización**
   - 70% train, 20% val, 10% test
   - Copiar imágenes y labels a directorios correspondientes

#### 2.3 Entrenar Modelo YOLO

```bash
# Opción 1: Script de entrenamiento incluido
python -m ml_core.training.train_yolo

# Opción 2: Ultralytics CLI directamente
yolo detect train \
  data=config/ml/data.yaml \
  model=yolov8n.pt \
  epochs=100 \
  imgsz=640 \
  batch=16 \
  device=0
```

**Monitorear entrenamiento:**
- Logs en consola
- TensorBoard: `tensorboard --logdir=runs/detect/train`
- Weights & Biases (si configurado)

**Validación:**
```bash
# Evaluar modelo en validation set
yolo detect val \
  model=data/models/production/tiktok_ui_detector.pt \
  data=config/ml/data.yaml
```

#### 2.4 Modelos Adicionales

**Anomaly Detector** (`anomaly_detector.pt`):
- Entrenar con datos de comportamiento normal vs. shadowban
- Script: `ml_core/training/train_anomaly.py` (crear si no existe)

**Account Affinity** (`account_affinity.onnx`):
- Modelo de clustering/recomendación
- Basado en métricas de engagement y contenido similar

**Video Analyzer** (`tiktok_video_analyzer.pt`):
- Análisis de contenido de video (opcional)
- Detección de trends, audio popular, efectos

### Fase 3: Implementar Factories de Producción

#### 3.1 ML Factory

Editar `ml_core/models/factory.py`:

```python
import os
from config.app_settings import get_settings

def get_yolo_screenshot_detector():
    settings = get_settings()
    
    if settings.DUMMY_MODE:
        from ml_core.models.yolo_screenshot import YoloScreenshotDetector
        return YoloScreenshotDetector()
    else:
        # PRODUCCIÓN: Implementar o importar clase real
        from ml_core.models.yolo_prod import YoloScreenshotDetector
        return YoloScreenshotDetector(
            model_path=settings.MODEL_PATH + "/tiktok_ui_detector.pt",
            device="cuda"
        )
```

Repetir para otros detectores (anomaly, affinity, video).

#### 3.2 Device Farm Factory

Editar `device_farm/controllers/factory.py`:

```python
def get_adb_controller():
    settings = get_settings()
    
    if settings.DUMMY_MODE:
        from device_farm.controllers.adb_controller import ADBController
        return ADBController()  # Dummy
    else:
        # PRODUCCIÓN: Implementar ADB real
        from device_farm.controllers.adb_prod import ADBControllerProduction
        return ADBControllerProduction(
            adb_host=os.getenv("ADB_SERVER_HOST"),
            appium_host=os.getenv("APPIUM_HOST"),
            appium_port=int(os.getenv("APPIUM_PORT", 4723))
        )
```

#### 3.3 GoLogin Factory

Crear/editar `gologin_automation/factory.py`:

```python
def get_gologin_client():
    settings = get_settings()
    
    if settings.DUMMY_MODE:
        from gologin_automation.api.gologin_client import GoLoginClient
        return GoLoginClient()  # Dummy
    else:
        from gologin_automation.api.gologin_prod import GoLoginClientProduction
        return GoLoginClientProduction(
            api_key=os.getenv("GOLOGIN_API_KEY")
        )
```

### Fase 4: Configurar Device Farm

#### 4.1 Preparar Dispositivos

```bash
# Conectar dispositivos vía USB
# Verificar detección
adb devices

# Deberías ver algo como:
# List of devices attached
# device1_serial    device
# device2_serial    device
# ...
```

#### 4.2 Instalar Appium

```bash
# Instalar Node.js y Appium
npm install -g appium
appium driver install uiautomator2

# Iniciar servidor
appium --address 0.0.0.0 --port 4723
```

#### 4.3 Configurar Perfiles de Dispositivo

Crear `config/devices/device_profiles.json`:

```json
{
  "devices": [
    {
      "id": "device_001",
      "serial": "XXXXXXXX",
      "model": "Samsung Galaxy S21",
      "android_version": "12",
      "appium_port": 4723,
      "system_port": 8200,
      "status": "active"
    }
  ]
}
```

### Fase 5: Configurar GoLogin

#### 5.1 Crear Perfiles de Navegador

```python
# Script de ejemplo: scripts/setup_gologin_profiles.py
from gologin_automation.api.gologin_client import GoLoginClient

client = GoLoginClient(api_key=os.getenv("GOLOGIN_API_KEY"))

# Crear 30 perfiles
for i in range(30):
    profile = client.create_profile(
        name=f"tiktok_profile_{i:02d}",
        os="win",
        navigator={
            "userAgent": "Mozilla/5.0...",
            "resolution": "1920x1080"
        },
        proxy={
            "mode": "http",
            "host": "proxy.example.com",
            "port": 8080,
            "username": "user",
            "password": "pass"
        }
    )
    print(f"Created profile: {profile['id']}")
```

### Fase 6: Configurar Orquestación (n8n)

#### 6.1 Desplegar n8n

```bash
docker compose -f docker/docker-compose.yml up -d n8n
```

Acceder a: `http://localhost:5678`

#### 6.2 Importar Workflows

1. Login a n8n UI
2. Settings → Import from File
3. Importar workflows desde `orchestration/n8n_workflows/`:
   - `main_orchestrator.json`
   - `ml_decision_engine.json`
   - `device_farm_trigger.json`
   - `gologin_trigger.json`

#### 6.3 Configurar Credenciales en n8n

- HTTP Request nodes: Añadir API key del ML service
- PostgreSQL nodes: Configurar conexión a base de datos
- Webhook nodes: Configurar URLs accesibles

### Fase 7: Base de Datos

#### 7.1 Inicializar PostgreSQL

```bash
docker compose -f docker/docker-compose.yml up -d postgres

# Crear tablas
# (Si existen migraciones Alembic o scripts SQL)
python scripts/init_database.py
```

#### 7.2 Schema Mínimo

```sql
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255),
    device_id VARCHAR(255),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(255) REFERENCES accounts(account_id),
    metric_type VARCHAR(100),
    value FLOAT,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ml_predictions (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(255) REFERENCES accounts(account_id),
    prediction_type VARCHAR(100),
    result JSONB,
    confidence FLOAT,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

### Fase 8: Monitoring

#### 8.1 Configurar Grafana

```bash
docker compose -f docker/docker-compose.yml up -d grafana
```

Acceder a: `http://localhost:3000` (admin/password del .env)

#### 8.2 Importar Dashboards

1. Add Data Source → PostgreSQL
2. Import dashboard desde `monitoring/dashboards/grafana/`

#### 8.3 Configurar Alertas

Editar `config/automation/alert_thresholds.json`:

```json
{
  "shadowban_confidence_threshold": 0.7,
  "rate_limit_actions_per_hour": 30,
  "anomaly_detection_threshold": 0.8,
  "device_health_check_interval": 300
}
```

### Fase 9: Testing en Producción

#### 9.1 Smoke Tests

```bash
# Test ML API
curl -X POST "http://localhost:8000/api/v1/analyze_screenshot" \
  -H "X-API-Key: ${ML_API_KEY}" \
  -F "file=@test_screenshot.png"

# Test health
curl http://localhost:8000/health
```

#### 9.2 Integration Tests

```bash
# Con DUMMY_MODE=false
DUMMY_MODE=false PYTHONPATH=. pytest tests/integration/ -v
```

#### 9.3 E2E Tests (cuidado - usa dispositivos reales)

```bash
# Ejecutar con precaución
DUMMY_MODE=false PYTHONPATH=. pytest tests/e2e/ -v --device device_001
```

### Fase 10: Despliegue y Monitoreo

#### 10.1 Arrancar Todos los Servicios

```bash
# Opción 1: Docker Compose (recomendado)
docker compose -f docker/docker-compose.yml up -d

# Opción 2: Manual
# Terminal 1: ML API
DUMMY_MODE=false uvicorn ml_core.api.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Device Farm Manager
DUMMY_MODE=false python -m device_farm.manager

# Terminal 3: n8n ya corriendo en Docker
# Terminal 4: Monitoring services ya en Docker
```

#### 10.2 Verificar Servicios

```bash
# Check running containers
docker ps

# Check logs
docker compose logs -f ml-api
docker compose logs -f n8n
docker compose logs -f postgres
```

#### 10.3 Monitoreo Continuo

- **Grafana**: Métricas de sistema y cuentas
- **n8n**: Estado de workflows
- **Discord**: Alertas vía webhook
- **Logs**: `tail -f logs/*.log`

## Troubleshooting

### Problema: CUDA not available

```bash
# Verificar instalación
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"

# Reinstalar PyTorch con CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Problema: ADB no detecta dispositivos

```bash
# Reiniciar servidor ADB
adb kill-server
adb start-server
adb devices

# Verificar permisos USB
sudo usermod -aG plugdev $USER
```

### Problema: GoLogin API errors

- Verificar API key válida
- Revisar límites de cuenta (número de perfiles)
- Check proxy configuration

### Problema: Modelo no carga

```bash
# Verificar ruta de modelo
ls -la data/models/production/

# Test carga manual
python -c "from ultralytics import YOLO; model = YOLO('data/models/production/tiktok_ui_detector.pt')"
```

## Rollback a Dummy Mode

Si algo falla, regresar a dummy mode:

```bash
# En .env
DUMMY_MODE=true

# Reiniciar servicios
docker compose restart
```

## Checklist de Migración

Pre-despliegue:
- [ ] Hardware preparado (GPU, devices)
- [ ] Dependencias instaladas
- [ ] Variables de entorno configuradas
- [ ] Modelos entrenados y ubicados correctamente
- [ ] Factories implementadas
- [ ] Base de datos inicializada
- [ ] n8n workflows importados
- [ ] Monitoring configurado

Post-despliegue:
- [ ] Smoke tests passed
- [ ] Integration tests passed
- [ ] Dispositivos detectados y funcionando
- [ ] GoLogin perfiles creados
- [ ] Métricas visibles en Grafana
- [ ] Alertas funcionando
- [ ] Documentación actualizada
- [ ] Equipo entrenado

## Soporte

Para ayuda con la migración:
- Consultar documentación en `/docs`
- Revisar logs en detalle
- Abrir issue en GitHub con logs y configuración (sin secretos)

---

**Última actualización**: 2025-10-23
