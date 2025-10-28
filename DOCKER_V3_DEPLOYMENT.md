# 🚀 Docker V3 - Sistema Completo Deployment Guide

## 📋 Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Arquitectura](#arquitectura)
- [Servicios](#servicios)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Deployment](#deployment)
- [Monitoreo](#monitoreo)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Descripción General

**Docker V3** es el sistema COMPLETO que integra **TODAS** las capacidades:

### ✅ Componentes Integrados

| Origen | Componentes | Puerto(s) |
|--------|-------------|-----------|
| **Docker v1** (Orgánico) | ML Core (YOLOv8), Device Farm, GoLogin, PostgreSQL, Redis, Dashboard | 8000, 4723, 8501, 5432, 6379 |
| **Docker v2** (Paid Ads) | Meta Ads Manager, Pixel Tracker, YouTube Uploader, ML Predictor, Analytics | 9000-9005 |
| **NEW - n8n** | Workflow Orchestrator (3 workflows) | 5678 |
| **NEW - Ultralytics** | YOLOv8 Video Analysis (activado en ML Core) | - |
| **NEW - Unified v3** | Sistema Unificado Community Manager | 10000 |

### 🎬 Caso de Uso

**Community Manager de discográfica** quiere lanzar campaña viral completa:

1. **Organic Publishing** (Device Farm): 10 móviles publican en TikTok/Instagram
2. **Paid Amplification** (Meta Ads): Campañas Meta amplían alcance
3. **ML Optimization** (YOLOv8): Analiza videos, predice virality, optimiza captions
4. **Automation** (n8n): Orquesta 24/7, schedules óptimos, cross-engagement
5. **Unified Orchestration** (v3): Dashboard único controla TODO

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────────────┐
│                         🌐 NGINX (Port 80/443)                      │
│                      Reverse Proxy & SSL Termination                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼──────┐   ┌────────▼────────┐   ┌──────▼──────┐
│  Dashboard   │   │  Unified v3     │   │    n8n      │
│  (Streamlit) │   │  Orchestrator   │   │  Workflows  │
│  Port 8501   │   │  Port 10000     │   │  Port 5678  │
└───────┬──────┘   └────────┬────────┘   └──────┬──────┘
        │                   │                    │
        └─────────┬─────────┴────────────────────┘
                  │
     ┌────────────▼────────────┐
     │      Service Layer      │
     │  (Internal Network)     │
     └────────────┬────────────┘
                  │
    ┬─────────────┼─────────────┬─────────────┬─────────────┬
    │             │             │             │             │
┌───▼────┐  ┌────▼────┐  ┌─────▼─────┐  ┌───▼────┐  ┌────▼────┐
│ML Core │  │ Device  │  │  GoLogin  │  │  Meta  │  │ YouTube │
│YOLOv8  │  │  Farm   │  │ Automation│  │  Ads   │  │Uploader │
│Pt 8000 │  │ Pt 4723 │  │           │  │Pt 9000 │  │ Pt 9003 │
└───┬────┘  └────┬────┘  └─────┬─────┘  └───┬────┘  └────┬────┘
    │            │             │            │            │
    └────────────┴─────────────┴────────────┴────────────┘
                              │
                 ┌────────────┼────────────┐
                 │                         │
         ┌───────▼───────┐         ┌──────▼──────┐
         │  PostgreSQL   │         │    Redis    │
         │   Port 5432   │         │  Port 6379  │
         └───────────────┘         └─────────────┘
```

### 🔄 Data Flow

1. **Community Manager** → Dashboard (Streamlit)
2. **Dashboard** → Unified Orchestrator (lanza campañas)
3. **Unified Orchestrator** → n8n (triggers workflows)
4. **n8n Workflows**:
   - `main_orchestrator.json`: Coordina todo el sistema
   - `ml_decision_engine.json`: Decisiones ML (posting time, virality)
   - `device_farm_trigger.json`: Dispara publicación en móviles
5. **ML Core (YOLOv8)**: Analiza videos, detecta shadowbans, optimiza captions
6. **Device Farm**: Publica en TikTok/Instagram desde 10 móviles
7. **Meta Ads**: Amplifica alcance con paid ads
8. **YouTube**: Sube videos a YouTube Music
9. **Analytics**: PostgreSQL + Grafana

---

## 📦 Servicios

### Core Services (9 servicios)

| Servicio | Propósito | Puerto | Health Check |
|----------|-----------|--------|--------------|
| `ml-core` | ML Core con YOLOv8/Ultralytics | 8000 | `/health` |
| `device-farm` | 10 móviles ADB/Appium | 4723 | - |
| `gologin-automation` | 5 browser profiles | - | - |
| `meta-ads-manager` | Meta Ads campaigns | 9000 | `/health` |
| `pixel-tracker` | Facebook Pixel/CAPI | 9001 | - |
| `youtube-uploader` | YouTube API upload | 9003 | - |
| `n8n` | Workflow orchestrator | 5678 | `/healthz` |
| `unified-orchestrator` | Sistema v3 API | 10000 | `/health` |
| `dashboard` | Streamlit UI | 8501 | - |

### Infrastructure Services (5 servicios)

| Servicio | Propósito | Puerto | Volumes |
|----------|-----------|--------|---------|
| `postgres` | PostgreSQL 15 | 5432 | `postgres-data` |
| `redis` | Redis 7 cache | 6379 | `redis-data` |
| `nginx` | Reverse proxy | 80, 443 | `ssl/` |
| `grafana` | Monitoring dashboard | 3000 | `dashboards/` |

---

## 🔧 Instalación

### Prerequisites

- Docker 24.0+
- Docker Compose 2.0+
- 16GB RAM mínimo (32GB recomendado)
- 50GB espacio disco libre
- Ubuntu 20.04+ / Debian 11+ / macOS 12+

### 1. Clone Repository

```bash
git clone https://github.com/your-org/unified-viral-system.git
cd unified-viral-system
```

### 2. Create Environment File

```bash
cp .env.v3 .env
```

### 3. Configure Credentials

Edita `.env` y completa:

```bash
# Meta Ads (OBLIGATORIO)
META_ACCESS_TOKEN=EAABsb...
META_AD_ACCOUNT_ID=act_123456789
META_PIXEL_ID=123456789012345

# YouTube (OBLIGATORIO)
YOUTUBE_CLIENT_ID=xxx.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=GOCSPX-xxx

# GoLogin (OPCIONAL para browser automation)
GOLOGIN_API_KEY=xxx
GOLOGIN_PROFILE_IDS=profile1,profile2,profile3

# Telegram (OPCIONAL para notificaciones)
TELEGRAM_BOT_TOKEN=123456:ABC-DEF
TELEGRAM_CHAT_ID=123456789
```

### 4. Download YOLOv8 Models

```bash
# Descarga modelos pre-entrenados
mkdir -p data/models
cd data/models

# YOLOv8n (lightweight, screenshot detection)
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
mv yolov8n.pt yolov8n_screenshot.pt

# YOLOv8s (medium, video analysis)
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt
mv yolov8s.pt yolov8s_video.pt

# YOLOv8m (advanced, object detection)
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt
mv yolov8m.pt yolov8m_detection.pt
```

---

## 🚀 Deployment

### Quick Start

```bash
# Opción 1: Usar script CLI
./v3-docker.sh start

# Opción 2: Docker Compose directo
docker-compose -f docker-compose-v3.yml up -d
```

### Verify Deployment

```bash
./v3-docker.sh status
```

Output esperado:

```
NAME                    STATUS      PORTS
unified-ml-core         Up 30s      0.0.0.0:8000->8000/tcp
unified-device-farm     Up 30s      0.0.0.0:4723->4723/tcp
unified-n8n             Up 30s      0.0.0.0:5678->5678/tcp
unified-orchestrator    Up 30s      0.0.0.0:10000->10000/tcp
unified-dashboard       Up 30s      0.0.0.0:8501->8501/tcp
unified-postgres        Up 35s      0.0.0.0:5432->5432/tcp
unified-redis           Up 35s      0.0.0.0:6379->6379/tcp
...
```

### Health Checks

```bash
./v3-docker.sh health
```

Output esperado:

```
✅ ml-core: Healthy
✅ unified-orchestrator: Healthy
✅ meta-ads-manager: Healthy
✅ n8n: Healthy
```

---

## 🎛️ Configuración

### 1. n8n Workflows Setup

```bash
# Accede a n8n
./v3-docker.sh n8n

# O manualmente:
open http://localhost:5678
```

**Login:**
- Usuario: `admin`
- Password: `viral_admin_2025`

**Import Workflows:**

1. Click "Import from File"
2. Selecciona cada workflow:
   - `orchestration/n8n_workflows/main_orchestrator.json`
   - `orchestration/n8n_workflows/ml_decision_engine.json`
   - `orchestration/n8n_workflows/device_farm_trigger.json`
3. Activa cada workflow (toggle ON)

### 2. Ultralytics YOLOv8 Verification

```bash
# Test ML Core con YOLOv8
curl -X POST http://localhost:8000/analyze_screenshot \
  -H "Content-Type: application/json" \
  -d '{
    "screenshot_path": "/data/screenshots/test.jpg",
    "account_id": "test_account"
  }'
```

Response esperado:

```json
{
  "status": "success",
  "analysis": {
    "shadowban_detected": false,
    "anomalies": [],
    "confidence": 0.95,
    "model": "yolov8n_screenshot"
  }
}
```

### 3. Device Farm Configuration

```bash
# Lista dispositivos ADB conectados
docker exec unified-device-farm adb devices

# Conecta móviles vía USB o WiFi ADB
# USB: Conecta móviles físicos
# WiFi: adb connect 192.168.1.100:5555
```

### 4. Meta Ads Campaign Setup

```bash
# Test Meta Ads Manager
curl -X POST http://localhost:9000/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Campaign",
    "budget": 50.0,
    "objective": "REACH"
  }'
```

---

## 📊 Monitoreo

### 1. Grafana Dashboard

```bash
open http://localhost:3000
```

**Login:**
- Usuario: `admin`
- Password: `viral_monitor_2025`

**Dashboards disponibles:**
- Campaign Performance
- ML Predictions Accuracy
- Device Farm Status
- Meta Ads ROI
- System Health

### 2. PostgreSQL Database

```bash
./v3-docker.sh psql
```

**Queries útiles:**

```sql
-- Campañas recientes
SELECT * FROM campaigns ORDER BY created_at DESC LIMIT 10;

-- Métricas de performance
SELECT 
  account_id, 
  SUM(views) as total_views, 
  SUM(likes) as total_likes,
  AVG(engagement_rate) as avg_engagement
FROM metrics
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY account_id;

-- ML Predictions
SELECT * FROM ml_predictions 
WHERE prediction_type = 'virality' 
ORDER BY confidence DESC LIMIT 20;
```

### 3. Redis Cache

```bash
./v3-docker.sh redis-cli
```

**Commands:**

```bash
# Ver todas las keys
KEYS *

# Campañas activas
HGETALL campaign:active

# ML predictions cache
GET ml:virality:video_123
```

### 4. Logs en Tiempo Real

```bash
# Todos los servicios
./v3-docker.sh logs

# Servicio específico
./v3-docker.sh logs unified-orchestrator
./v3-docker.sh logs n8n
./v3-docker.sh logs ml-core
```

---

## 🔧 Troubleshooting

### Problema 1: ML Core no inicia

**Síntomas:**
```
unified-ml-core | ModuleNotFoundError: No module named 'ultralytics'
```

**Solución:**
```bash
# Rebuild ML Core con Ultralytics
docker-compose -f docker-compose-v3.yml build --no-cache ml-core
docker-compose -f docker-compose-v3.yml up -d ml-core
```

### Problema 2: n8n no importa workflows

**Síntomas:**
n8n muestra workflows vacíos

**Solución:**
```bash
# Verifica que workflows existen
ls orchestration/n8n_workflows/

# Re-mount volume
docker-compose -f docker-compose-v3.yml down
docker volume rm unified-v3_n8n-data
docker-compose -f docker-compose-v3.yml up -d n8n
```

### Problema 3: Device Farm no detecta móviles

**Síntomas:**
```
adb: no devices/emulators found
```

**Solución:**
```bash
# En host, verifica USB devices
lsusb

# Restart udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Restart Device Farm
docker-compose -f docker-compose-v3.yml restart device-farm
```

### Problema 4: Meta Ads API errores

**Síntomas:**
```
Error: Invalid OAuth 2.0 Access Token
```

**Solución:**
```bash
# Verifica token en .env
grep META_ACCESS_TOKEN .env

# Regenera token en Meta Business Suite
# https://business.facebook.com/settings/system-users

# Restart Meta Ads Manager
docker-compose -f docker-compose-v3.yml restart meta-ads-manager
```

### Problema 5: PostgreSQL connection refused

**Síntomas:**
```
psycopg2.OperationalError: could not connect to server
```

**Solución:**
```bash
# Verifica que postgres está corriendo
docker ps | grep postgres

# Verifica logs
docker logs unified-postgres

# Reset database
./v3-docker.sh clean
./v3-docker.sh start
```

---

## 🎯 Production Deployment

### 1. Environment Variables

**CRITICAL**: Cambia passwords en producción:

```bash
# .env (production)
POSTGRES_PASSWORD=<strong_password_here>
N8N_PASSWORD=<strong_password_here>
GRAFANA_PASSWORD=<strong_password_here>
```

### 2. SSL Configuration

```bash
# Genera certificados SSL (Let's Encrypt)
sudo apt-get install certbot
sudo certbot certonly --standalone -d your-domain.com

# Copia certificados a docker/nginx/ssl/
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/nginx/ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/nginx/ssl/

# Restart nginx
docker-compose -f docker-compose-v3.yml restart nginx
```

### 3. Firewall Rules

```bash
# UFW (Ubuntu)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 5432/tcp  # PostgreSQL (internal only)
sudo ufw deny 6379/tcp  # Redis (internal only)
sudo ufw enable
```

### 4. Backup Strategy

```bash
# Crea script de backup
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec unified-postgres pg_dump -U postgres community_manager | gzip > backup_$DATE.sql.gz
docker exec unified-redis redis-cli BGSAVE
EOF

chmod +x backup.sh

# Cron job (daily 3am)
crontab -e
# Añade: 0 3 * * * /path/to/backup.sh
```

---

## 📈 Scaling

### Horizontal Scaling

```bash
# Escala Device Farm a 3 instancias
./v3-docker.sh scale device-farm 3

# Escala Meta Ads Manager a 2 instancias
./v3-docker.sh scale meta-ads-manager 2
```

### Vertical Scaling

Edita `docker-compose-v3.yml`:

```yaml
services:
  ml-core:
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G
```

---

## 🎬 Complete Workflow Example

### Lanzamiento Campaña Viral Completa

```bash
# 1. Start Docker V3
./v3-docker.sh start

# 2. Accede Dashboard
./v3-docker.sh dashboard

# 3. En Dashboard:
#    - Tab "Lanzar Campaña"
#    - Nombre: "Nuevo Single 2025"
#    - Target TikTok: 1M views
#    - Budget Meta Ads: $500
#    - Click "Lanzar Campaña Viral"

# 4. n8n Orchestrator automáticamente:
#    - Analiza video con YOLOv8 (virality score)
#    - Optimiza captions con ML NLP
#    - Calcula posting time óptimo
#    - Programa Device Farm (10 móviles → TikTok/IG)
#    - Lanza Meta Ads campaigns
#    - Sube video a YouTube Music
#    - Activa Pixel tracking

# 5. Monitoreo 24/7:
#    - Grafana: http://localhost:3000
#    - Dashboard: http://localhost:8501
#    - n8n logs: ./v3-docker.sh logs n8n

# 6. Analytics en tiempo real:
#    - Views, Likes, Shares
#    - ROI Meta Ads
#    - Shadowban detection
#    - Virality predictions
```

---

## 📚 Referencias

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [n8n Documentation](https://docs.n8n.io/)
- [Ultralytics YOLOv8](https://docs.ultralytics.com/)
- [Meta Marketing API](https://developers.facebook.com/docs/marketing-apis)
- [Appium Documentation](https://appium.io/docs/)

---

## 🤝 Support

**Issues?**
- GitHub Issues: https://github.com/your-org/unified-viral-system/issues
- Email: support@your-domain.com
- Telegram: @support_bot

---

**Docker V3 - Sistema Completo Para ROMPER la Discográfica y las RRSS** 🚀🔥
