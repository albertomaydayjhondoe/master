# 🚀 GUÍA RÁPIDA - Setup Completo Docker V3

## 📋 PASO A PASO (10 minutos)

### 1️⃣ **Configurar Credenciales** (5 minutos)

```bash
./setup-credentials.sh
```

El script te pedirá **interactivamente**:

#### 🔴 **OBLIGATORIAS** (Meta Ads + YouTube)
- **Meta Access Token** (https://business.facebook.com/settings/system-users)
- **Meta Ad Account ID** (act_123456789)
- **Meta Pixel ID** (123456789012345)
- **YouTube Client ID** (xxx.apps.googleusercontent.com)
- **YouTube Client Secret** (GOCSPX-xxx)
- **YouTube Channel ID** (UC_xxx)

#### 🎤 **ARTISTA GENÉRICO** (Landing Pages)
- **Nombre del Artista**: Ej: "DJ Producer X"
- **YouTube Channel**: https://www.youtube.com/@artist_channel
- **Instagram**: @artist_instagram
- **TikTok**: @artist_tiktok

#### 🟡 **OPCIONALES**
- **Runway ML API Key** (generación videos AI)
- **GoLogin API Key** (browser automation)
- **Telegram Bot** (notificaciones)
- **n8n Webhook personalizado**

---

### 2️⃣ **Descargar Modelos YOLOv8** (2 minutos)

```bash
./download-models.sh
```

Descarga automáticamente:
- `yolov8n_screenshot.pt` (6.2 MB)
- `yolov8s_video.pt` (21.5 MB)
- `yolov8m_detection.pt` (49.7 MB)

---

### 3️⃣ **Iniciar Docker V3** (1 minuto)

```bash
./v3-docker.sh start
```

Inicia **14 servicios**:
- ✅ ML Core (YOLOv8)
- ✅ Meta Ads Manager
- ✅ Pixel Tracker
- ✅ YouTube Uploader
- ✅ n8n Orchestrator
- ✅ Unified Orchestrator
- ✅ Dashboard
- ✅ PostgreSQL, Redis, Nginx, Grafana

---

### 4️⃣ **Verificar Salud** (30 segundos)

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

### 5️⃣ **Configurar n8n Workflows** (3 minutos)

```bash
./n8n-setup.sh
```

#### Manual:
1. Abre: http://localhost:5678
2. Login: `admin` / `viral_admin_2025`
3. Import workflows:
   - `orchestration/n8n_workflows/main_orchestrator.json`
   - `orchestration/n8n_workflows/ml_decision_engine.json`
   - `orchestration/n8n_workflows/device_farm_trigger.json`
   - `orchestration/n8n_workflows/landing_page_generator.json` ⭐ **NUEVO**

4. Activa cada workflow (toggle ON)

---

### 6️⃣ **Abrir Dashboard** (inmediato)

```bash
./v3-docker.sh dashboard
```

O manualmente: http://localhost:8501

---

### 7️⃣ **Lanzar Primera Campaña** 🚀

#### **Modo 1: Video Individual**

##### Desde Dashboard:
1. Tab: **"Lanzar Campaña"**
2. Completa:
   - **Nombre**: "Nuevo Single 2025"
   - **Video**: Upload o path
   - **Target**: 1M views TikTok
   - **Budget**: $500
3. Click: **"Lanzar Campaña Viral"**

##### Desde CLI:
```bash
python unified_system_v3.py \
  --mode launch \
  --video "path/to/video.mp4" \
  --campaign-name "Nuevo Single 2025" \
  --artist-name "Stakas" \
  --target-views 1000000 \
  --paid-budget 50.0
```

---

#### **Modo 2: Monitoreo de Canal (AUTO-VIRALIZE)** ⭐ **NUEVO**

##### Desde Dashboard:
1. Tab: **"Monitorear Canal"**
2. Pega URL del canal: `https://www.youtube.com/@artist_channel`
3. Configura:
   - **Auto-launch**: ON
   - **Virality threshold**: 0.70
   - **Max campañas/día**: 2
   - **Budget por video**: $50
4. Click: **"Iniciar Monitoreo 24/7"**

##### Desde CLI:
```bash
python unified_system_v3.py \
  --mode monitor-channel \
  --youtube-channel "UC_ABC123XYZ" \
  --auto-launch \
  --virality-threshold 0.70 \
  --max-campaigns-per-day 2 \
  --paid-budget 50.0 \
  --check-interval 6
```

**¿Qué hace?**
- ✅ Monitorea canal 24/7
- ✅ Detecta videos nuevos cada 6 horas
- ✅ Analiza con YOLOv8 (virality score)
- ✅ Auto-lanza campañas para videos con score > 0.70
- ✅ **Límite: 2 campañas/día** (protección UTM)
- ✅ Prioriza videos con mayor potencial

**Ver documentación completa:** `docs/MONITOR_CHANNEL_MODE.md`

---

## 🎯 ¿QUÉ PASA CUANDO LANZAS CAMPAÑA?

### **Automatización Completa:**

1. ✅ **n8n Main Orchestrator** dispara workflow
2. ✅ **ML Core (YOLOv8)** analiza video
   - Virality score: 89/100
   - Shadowban detection: OK
   - Optimal posting time: 20:00 viernes
3. ✅ **Landing Page Generator** (n8n workflow)
   - Genera HTML con datos del artista genérico
   - Incluye YouTube channel embed
   - Instagram/TikTok links
   - Meta Pixel integrado
4. ✅ **Meta Ads Manager** lanza campaña
   - Budget: $500
   - Landing page URL configurada
   - Targeting: similares + lookalikes
5. ✅ **Pixel Tracker** activa eventos
   - PageView, ViewContent, AddToCart
   - Retargeting automático
6. ✅ **YouTube Uploader** sube video
   - YouTube Music
   - Title/description optimizados
7. ✅ **Grafana** monitorea 24/7
   - Views, likes, engagement
   - ROI Meta Ads
   - Alertas shadowban

---

## 🌐 ACCESS POINTS

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Dashboard** | http://localhost:8501 | - |
| **Unified API** | http://localhost:10000 | - |
| **n8n Workflows** | http://localhost:5678 | admin / viral_admin_2025 |
| **ML Core API** | http://localhost:8000/docs | - |
| **Meta Ads** | http://localhost:9000 | - |
| **Grafana** | http://localhost:3000 | admin / viral_monitor_2025 |

---

## 📊 VARIABLES DE ENTORNO (.env)

### Credenciales Artista Genérico (Landing Pages)
```bash
ARTIST_NAME=DJ Producer X
ARTIST_YOUTUBE_CHANNEL=https://www.youtube.com/@djproducerx
ARTIST_INSTAGRAM=@djproducerx
ARTIST_TIKTOK=@djproducerx
```

Estas variables se usan en:
- **Landing Pages Meta Ads**: Información del artista
- **n8n Workflows**: Datos automáticos en workflows
- **Dashboard**: Perfil del artista en UI

---

## 🛠️ COMANDOS ÚTILES

```bash
# Ver estado
./v3-docker.sh status

# Ver logs
./v3-docker.sh logs unified-orchestrator
./v3-docker.sh logs n8n

# Reiniciar servicio
docker-compose -f docker-compose-v3.yml restart meta-ads-manager

# PostgreSQL
./v3-docker.sh psql

# Redis
./v3-docker.sh redis-cli

# Detener todo
./v3-docker.sh stop
```

---

## ⚠️ ANTES DE PRODUCCIÓN

### 🔴 CRÍTICO:
1. **Cambia passwords** en `.env`:
   ```bash
   POSTGRES_PASSWORD=<strong_random_password>
   N8N_PASSWORD=<strong_random_password>
   GRAFANA_PASSWORD=<strong_random_password>
   ```

2. **Configura SSL/TLS**:
   ```bash
   sudo certbot certonly --standalone -d tu-dominio.com
   cp /etc/letsencrypt/live/tu-dominio.com/*.pem docker/nginx/ssl/
   docker-compose -f docker-compose-v3.yml restart nginx
   ```

3. **Firewall**:
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw deny 5432/tcp
   sudo ufw deny 6379/tcp
   ```

---

## 🎉 ¡LISTO!

Sistema **COMPLETO** y **FUNCIONAL** para:
- ✅ **1M+ views/campaña** (organic + paid)
- ✅ **ROI 5x+** en Meta Ads
- ✅ **Zero shadowbans** (ML detection)
- ✅ **24/7 automation** (n8n workflows)
- ✅ **Landing pages** con artista genérico
- ✅ **Runway ML** (opcional, video generation)

**¡A ROMPER LAS RRSS! 🚀🔥🎵**
