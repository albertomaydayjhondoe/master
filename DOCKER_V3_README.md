# 🚀 Docker V3 - Sistema Completo Para ROMPER Discográfica + RRSS

> **Sistema Unificado**: Ultralytics YOLOv8 + n8n Workflows + Meta Ads + Device Farm + Todo Docker v1 + v2

---

## 🎯 ¿Qué es Docker V3?

El **arma definitiva** para Community Managers de discográficas. Combina:

| Componente | Funcionalidad | Estado |
|------------|---------------|--------|
| **Ultralytics YOLOv8** | Análisis de videos (virality prediction, shadowban detection) | ✅ Integrado |
| **n8n Workflows** | Automatización 24/7 (3 workflows pre-configurados) | ✅ Integrado |
| **ML Core** | 6 métodos ML (posting time, captions, affinity, thumbnails) | ✅ Integrado |
| **Device Farm** | 10 móviles ADB/Appium (TikTok, Instagram) | ✅ Integrado |
| **GoLogin** | 5 browser profiles automation | ✅ Integrado |
| **Meta Ads** | Campañas Facebook/Instagram automáticas | ✅ Integrado |
| **Pixel Tracker** | Facebook Pixel/CAPI tracking | ✅ Integrado |
| **YouTube** | Uploads automáticos a YouTube Music | ✅ Integrado |
| **Sistema Unificado v3** | Orquestador central | ✅ Integrado |
| **Dashboard** | Streamlit UI | ✅ Integrado |
| **Grafana** | Monitoring 24/7 | ✅ Integrado |

---

## ⚡ Quick Start (5 minutos)

### 1. Clonar repositorio

```bash
git clone https://github.com/your-org/unified-viral-system.git
cd unified-viral-system
```

### 2. Configurar credenciales

```bash
# Copia template
cp .env.v3 .env

# Edita con tus credenciales
nano .env

# OBLIGATORIO:
# - META_ACCESS_TOKEN
# - META_AD_ACCOUNT_ID
# - YOUTUBE_CLIENT_ID
```

### 3. Descargar modelos YOLOv8

```bash
mkdir -p data/models && cd data/models

# YOLOv8n (lightweight)
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
mv yolov8n.pt yolov8n_screenshot.pt

# YOLOv8s (medium)
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt
mv yolov8s.pt yolov8s_video.pt

cd ../..
```

### 4. Iniciar Docker V3

```bash
# Con script CLI
./v3-docker.sh start

# O directo con docker-compose
docker-compose -f docker-compose-v3.yml up -d
```

### 5. Verificar salud

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

## 🌐 Access Points

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Dashboard** | http://localhost:8501 | - |
| **Unified Orchestrator API** | http://localhost:10000 | - |
| **n8n Workflows** | http://localhost:5678 | admin / viral_admin_2025 |
| **ML Core API** | http://localhost:8000/docs | - |
| **Meta Ads Manager** | http://localhost:9000 | - |
| **Grafana Monitoring** | http://localhost:3000 | admin / viral_monitor_2025 |

---

## 🎬 Ejemplo: Lanzar Campaña Viral

### Opción 1: Dashboard (Recomendado)

```bash
# Abre dashboard
./v3-docker.sh dashboard

# En el navegador:
# 1. Tab "Lanzar Campaña"
# 2. Nombre: "Nuevo Single 2025"
# 3. Target: 1M views TikTok
# 4. Budget: $500
# 5. Click "Lanzar Campaña Viral"
```

### Opción 2: CLI (Python)

```bash
python unified_system_v3.py \
  --mode launch \
  --video "path/to/video.mp4" \
  --campaign-name "Nuevo Single 2025" \
  --target-views 1000000 \
  --paid-budget 500.0
```

### Opción 3: API (cURL)

```bash
curl -X POST http://localhost:10000/campaigns/launch \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nuevo Single 2025",
    "video_path": "/data/videos/single2025.mp4",
    "target_platform": "tiktok",
    "target_views": 1000000,
    "paid_budget": 500.0
  }'
```

---

## 🔄 ¿Qué hace el sistema automáticamente?

Cuando lanzas una campaña, **n8n Orchestrator** activa:

1. **ML Analysis** (YOLOv8):
   - Analiza video con Ultralytics
   - Predice virality score (0-100)
   - Detecta posibles shadowbans
   - Optimiza captions con NLP

2. **Posting Time Optimization** (LSTM):
   - Calcula hora óptima para publicar
   - Basado en engagement histórico
   - Considera timezone target audience

3. **Device Farm Publishing** (10 móviles):
   - Publica en TikTok desde 10 cuentas
   - Publica en Instagram Reels
   - Aplicando human-like patterns

4. **Meta Ads Amplification**:
   - Crea campaña en Facebook Ads
   - Targeting: similar audiences
   - Budget optimization automático

5. **YouTube Upload**:
   - Sube video a YouTube Music
   - Title/description optimizado
   - Tags automáticos

6. **Pixel Tracking**:
   - Instala Facebook Pixel
   - Eventos CAPI: ViewContent, AddToCart
   - Retargeting automático

7. **Cross-Engagement** (GoLogin):
   - 5 browsers simulan users reales
   - Likes, comments, shares
   - Algoritmo ML de human behavior

8. **24/7 Monitoring**:
   - Grafana dashboards
   - Shadowban detection
   - ROI tracking
   - Alertas Telegram

---

## 📊 Monitoreo

### Grafana Dashboards

```bash
# Abre Grafana
open http://localhost:3000

# Login: admin / viral_monitor_2025
```

**Dashboards disponibles:**
- Campaign Performance
- ML Predictions Accuracy
- Device Farm Status
- Meta Ads ROI
- System Health

### PostgreSQL Queries

```bash
# Conecta a DB
./v3-docker.sh psql

# Ver campañas recientes
SELECT * FROM campaigns ORDER BY created_at DESC LIMIT 10;

# Ver métricas
SELECT 
  account_id, 
  SUM(views) as total_views,
  SUM(likes) as total_likes,
  AVG(engagement_rate) as avg_engagement
FROM metrics
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY account_id;
```

### Logs en Tiempo Real

```bash
# Todos los servicios
./v3-docker.sh logs

# Servicio específico
./v3-docker.sh logs unified-orchestrator
./v3-docker.sh logs n8n
./v3-docker.sh logs ml-core
```

---

## 🛠️ Comandos Útiles

```bash
# Iniciar todo
./v3-docker.sh start

# Ver estado
./v3-docker.sh status

# Ver salud
./v3-docker.sh health

# Logs
./v3-docker.sh logs [service]

# Escalar Device Farm a 3 instancias
./v3-docker.sh scale device-farm 3

# Abrir n8n
./v3-docker.sh n8n

# Abrir Dashboard
./v3-docker.sh dashboard

# PostgreSQL CLI
./v3-docker.sh psql

# Redis CLI
./v3-docker.sh redis-cli

# Detener todo
./v3-docker.sh stop

# Reset completo (DESTRUYE DATOS)
./v3-docker.sh reset
```

---

## 🔧 Troubleshooting

### Problema: ML Core no inicia

```bash
# Rebuild
docker-compose -f docker-compose-v3.yml build --no-cache ml-core
docker-compose -f docker-compose-v3.yml up -d ml-core
```

### Problema: n8n no muestra workflows

```bash
# Verifica que workflows existen
ls orchestration/n8n_workflows/

# Restart n8n
docker-compose -f docker-compose-v3.yml restart n8n
```

### Problema: Device Farm no detecta móviles

```bash
# En host
lsusb
sudo udevadm control --reload-rules

# Restart Device Farm
docker-compose -f docker-compose-v3.yml restart device-farm
```

### Problema: Meta Ads API error

```bash
# Verifica token en .env
grep META_ACCESS_TOKEN .env

# Regenera token: https://business.facebook.com/settings/system-users
```

---

## 📚 Documentación Completa

- **[DOCKER_V3_DEPLOYMENT.md](DOCKER_V3_DEPLOYMENT.md)**: Guía completa deployment
- **[ML_INTEGRATION_V3.md](ML_INTEGRATION_V3.md)**: Integración ML Core
- **[UNIFIED_V3_GUIDE.md](UNIFIED_V3_GUIDE.md)**: Sistema Unificado v3
- **[DOCKER_V2_COMPLETE_GUIDE.md](DOCKER_V2_COMPLETE_GUIDE.md)**: Docker v2 (Meta Ads)

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    🌐 NGINX (80/443)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌─────▼─────┐  ┌──────▼──────┐
│  Dashboard   │  │ Unified   │  │    n8n      │
│  (8501)      │  │ Orch(10k) │  │  (5678)     │
└───────┬──────┘  └─────┬─────┘  └──────┬──────┘
        │               │                │
        └───────────────┼────────────────┘
                        │
     ┌──────────────────┼──────────────────┐
     │                  │                  │
┌────▼────┐  ┌─────────▼────────┐  ┌──────▼──────┐
│ML Core  │  │   Device Farm    │  │  Meta Ads   │
│YOLOv8   │  │   (10 móviles)   │  │  Manager    │
│(8000)   │  │   (4723)         │  │  (9000)     │
└────┬────┘  └─────────┬────────┘  └──────┬──────┘
     │                 │                  │
     └─────────────────┼──────────────────┘
                       │
          ┌────────────┼────────────┐
          │                         │
    ┌─────▼─────┐          ┌───────▼────┐
    │PostgreSQL │          │   Redis    │
    │  (5432)   │          │  (6379)    │
    └───────────┘          └────────────┘
```

---

## 📈 Scaling

### Horizontal Scaling

```bash
# Escala Device Farm
./v3-docker.sh scale device-farm 5

# Escala Meta Ads Manager
./v3-docker.sh scale meta-ads-manager 3
```

### Vertical Scaling

Edita `docker-compose-v3.yml`:

```yaml
services:
  ml-core:
    deploy:
      resources:
        limits:
          cpus: '8.0'
          memory: 16G
```

---

## 🔐 Producción

### SSL Configuration

```bash
# Genera certificados (Let's Encrypt)
sudo certbot certonly --standalone -d your-domain.com

# Copia a Docker
cp /etc/letsencrypt/live/your-domain.com/*.pem docker/nginx/ssl/

# Restart nginx
docker-compose -f docker-compose-v3.yml restart nginx
```

### Firewall

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 5432/tcp
sudo ufw deny 6379/tcp
sudo ufw enable
```

### Backups

```bash
# Crea script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec unified-postgres pg_dump -U postgres community_manager | gzip > backup_$DATE.sql.gz
EOF

chmod +x backup.sh

# Cron (daily 3am)
crontab -e
# Añade: 0 3 * * * /path/to/backup.sh
```

---

## ✅ Checklist Pre-Launch

- [ ] `.env` configurado con credenciales reales
- [ ] YOLOv8 models descargados (`data/models/`)
- [ ] PostgreSQL inicializado (`./v3-docker.sh start`)
- [ ] n8n workflows importados (http://localhost:5678)
- [ ] Device Farm móviles conectados (`adb devices`)
- [ ] Meta Ads token válido (test con `/campaigns`)
- [ ] YouTube OAuth configurado
- [ ] Grafana dashboards cargados
- [ ] Health checks pasando (`./v3-docker.sh health`)
- [ ] SSL configurado (producción)
- [ ] Backups automáticos (producción)

---

## 🎯 Objetivo Final

**ROMPER la discográfica y las RRSS** con:

- ✅ **1M+ views** por campaña (organic + paid)
- ✅ **ROI 5x** en Meta Ads
- ✅ **Zero shadowbans** (ML detection)
- ✅ **24/7 automation** (n8n workflows)
- ✅ **ML-optimized** content (YOLOv8)

---

## 🤝 Support

- **GitHub Issues**: https://github.com/your-org/unified-viral-system/issues
- **Email**: support@your-domain.com
- **Telegram**: @support_bot

---

**¡A ROMPERLA! 🚀🔥**
