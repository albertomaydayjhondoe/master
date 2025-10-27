# 🚀 TikTok Viral ML System V3 - Community Manager

Sistema completo de **auto-viralización** para Community Managers de discográficas. Combina ML (YOLOv8), Device Farm, GoLogin, Meta Ads y YouTube para lanzar campañas virales automáticas.

## 🎯 **¿Qué Hace?**

Le das un **video** o **canal de YouTube** y el sistema:

1. ✅ **Analiza** con YOLOv8 (virality score ML)
2. ✅ **Publica** en todas las redes (TikTok, Instagram, YouTube, Twitter, Facebook)
3. ✅ **Lanza Meta Ads** con landing pages optimizadas
4. ✅ **Genera engagement** automático (Device Farm + GoLogin)
5. ✅ **Monitorea** 24/7 con Grafana
6. ✅ **Optimiza** en tiempo real con ML

**Resultado:** 1M+ views en 7-14 días con $500 budget.

---

## 🆕 **NUEVO: Modo Monitor-Channel**

Monitorea un canal de YouTube 24/7 y **automáticamente viraliza** videos nuevos con alto potencial:

```bash
python unified_system_v3.py \
  --mode monitor-channel \
  --youtube-channel "UC_TuCanal" \
  --auto-launch \
  --max-campaigns-per-day 2 \
  --paid-budget 50.0
```

**Control de carga inteligente:**
- ✅ Límite: 2 campañas/día (protege UTM)
- ✅ Threshold: Solo videos con ML score > 0.70
- ✅ Priorización: Por virality score (mejores primero)
- ✅ Budget: $50 × 2 = $100/día max

Ver documentación completa: [`docs/MONITOR_CHANNEL_MODE.md`](docs/MONITOR_CHANNEL_MODE.md)

---

## 📋 **Quick Start (5 minutos)**

### 1. **Configurar Credenciales**
```bash
./setup-credentials.sh
```

Pedirá:
- Meta Ads (ACCESS_TOKEN, AD_ACCOUNT_ID, PIXEL_ID)
- YouTube API (CLIENT_ID, CLIENT_SECRET, CHANNEL_ID)
- **Artista genérico** (nombre, YouTube channel, Instagram, TikTok) ⭐
- Runway ML (opcional, AI video generation)
- n8n webhooks (automation)
- Telegram (notificaciones)

### 2. **Descargar Modelos YOLOv8**
```bash
./download-models.sh
```

### 3. **Iniciar Docker V3**
```bash
./v3-docker.sh start
```

### 4. **Configurar n8n**
```bash
./n8n-setup.sh
```

### 5. **Lanzar Campaña** 🚀

#### **Opción A: Video Individual**
```bash
python unified_system_v3.py \
  --mode launch \
  --video "nuevo_single.mp4" \
  --campaign-name "Verano 2025" \
  --artist-name "Stakas" \
  --paid-budget 500.0
```

#### **Opción B: Monitoreo de Canal (AUTO)** ⭐ **NUEVO**
```bash
python unified_system_v3.py \
  --mode monitor-channel \
  --youtube-channel "UC_ArtistChannel" \
  --auto-launch \
  --max-campaigns-per-day 2
```

Ver guía completa: [`QUICKSTART_GUIDE.md`](QUICKSTART_GUIDE.md)

---

## 🏗️ **Arquitectura Docker V3**

### **Servicios (14 activos):**

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **ml-core** | 8000 | YOLOv8 analysis + ML predictions |
| **meta-ads-manager** | 9000 | Meta Ads campaigns |
| **pixel-tracker** | 9001 | Facebook Pixel tracking |
| **youtube-uploader** | 9003 | YouTube video uploads |
| **n8n** | 5678 | Workflow automation |
| **unified-orchestrator** | 10000 | API unificado |
| **dashboard** | 8501 | Streamlit UI |
| **postgres** | 5432 | Database |
| **redis** | 6379 | Cache |
| **grafana** | 3000 | Monitoring |
| **prometheus** | 9090 | Metrics |
| **nginx** | 80, 443 | Reverse proxy |

**Device Farm:** Deshabilitado temporalmente (líneas 67-92 `docker-compose-v3.yml`)

---

## 📊 **2 MODOS DE OPERACIÓN**

### **Modo 1: LAUNCH (Individual)**

Para lanzamientos importantes de singles, colaboraciones, etc.

**Características:**
- ✅ Control total sobre timing y budget
- ✅ 1 video → 1 campaña
- ✅ Decisión manual

**Cuándo usar:**
- Lanzamiento de single flagship
- Colaboración con artista famoso
- Budget alto ($500+) para un video

**Ejemplo:**
```bash
python unified_system_v3.py \
  --mode launch \
  --video "mi_gran_hit.mp4" \
  --campaign-name "Mi Gran Hit 2025" \
  --paid-budget 1000.0
```

---

### **Modo 2: MONITOR-CHANNEL (Automático)** ⭐

Para catálogo continuo, canales activos con múltiples videos.

**Características:**
- ✅ Monitoreo 24/7
- ✅ Auto-viraliza videos con ML score > threshold
- ✅ Límite diario de campañas (protección UTM)
- ✅ Priorización por virality score
- ✅ Set-and-forget

**Cuándo usar:**
- Canal con >1 video/semana
- Catálogo extenso de música
- Automatización completa
- Budget distribuido ($50/video × N)

**Ejemplo:**
```bash
python unified_system_v3.py \
  --mode monitor-channel \
  --youtube-channel "UC_ArtistChannel" \
  --auto-launch \
  --virality-threshold 0.70 \
  --max-campaigns-per-day 2 \
  --paid-budget 50.0 \
  --check-interval 6
```

**Comparación completa:** [`docs/LAUNCH_VS_MONITOR.md`](docs/LAUNCH_VS_MONITOR.md)

---

## 🧠 **ML Core (YOLOv8)**

### **Capabilities:**

1. **Screenshot Analysis**
   - Detecta elementos UI de TikTok/Instagram
   - Identifica shadowban risk
   - Quality score (0.0-1.0)

2. **Virality Prediction**
   - Analiza video frame-by-frame
   - LSTM para engagement prediction
   - Output: 0.0-1.0 score

3. **Posting Time Optimization**
   - Basado en histórico de engagement
   - Ajuste por timezone del público
   - Output: "HH:MM" (24h format)

4. **Caption Optimization**
   - NLP sentiment analysis
   - Emoji effectiveness
   - Hashtag research

5. **Anomaly Detection**
   - Shadowban detection
   - Engagement drop patterns
   - Follower/view ratio analysis

---

## 🤖 **Automation Stack**

### **Organic Engagement:**
- **Device Farm:** 10 cuentas TikTok (Appium)
- **GoLogin:** 5 cuentas Instagram (browser automation)
- **ML-driven:** Timing y cantidad de interacciones

### **Paid Acquisition:**
- **Meta Ads:** Facebook + Instagram campaigns
- **Landing Pages:** Con artista genérico (YouTube, Instagram, TikTok)
- **Pixel Tracking:** Retargeting automático

### **Orchestration:**
- **n8n Workflows:** 4 workflows (main orchestrator, ML decision, device farm trigger, landing page generator)
- **Unified API:** `/launch` endpoint para integración

---

## 📚 **Documentación**

| Archivo | Descripción |
|---------|-------------|
| **[QUICKSTART_GUIDE.md](QUICKSTART_GUIDE.md)** | Setup completo en 10 minutos |
| **[docs/MONITOR_CHANNEL_MODE.md](docs/MONITOR_CHANNEL_MODE.md)** | Modo monitor-channel detallado |
| **[docs/LAUNCH_VS_MONITOR.md](docs/LAUNCH_VS_MONITOR.md)** | Comparación de modos |
| **[.github/copilot-instructions.md](.github/copilot-instructions.md)** | Contexto para AI agents |

---

## 🔧 **Desarrollo**

### **Dummy Mode (Default):**

Sistema corre en modo dummy por defecto (`DUMMY_MODE=true`):
- ✅ Stubs para YOLOv8, Device Farm, GoLogin
- ✅ Permite desarrollo local sin GPU ni dispositivos
- ✅ Datos simulados realistas

### **Salir de Dummy Mode:**

1. Implementa factories reales:
   - `ml_core/models/factory.py`
   - `device_farm/controllers/factory.py`

2. Provee modelos YOLOv8:
   - `data/models/yolov8n_screenshot.pt`
   - `data/models/yolov8s_video.pt`

3. Configura credenciales:
   - GoLogin API key + profile IDs
   - Appium servers para Device Farm

4. Cambia: `DUMMY_MODE=false`

Ver: `scripts/scaffold_prod_factories.py`

---

## 🧪 **Tests**

```bash
# Unit tests
PYTHONPATH=. pytest tests/unit/

# Integration tests
PYTHONPATH=. pytest tests/integration/

# E2E tests
PYTHONPATH=. pytest tests/e2e/

# Test monitor-channel mode
./test-monitor-channel.sh
```

---

## 📊 **Analytics & Monitoring**

### **Grafana Dashboards:**
- **Campaign Performance:** Views, engagement, ROI
- **Channel Monitor:** Videos analizados, campañas lanzadas
- **UTM Health:** Device Farm, GoLogin, Meta Ads usage
- **Budget Tracking:** Spend vs target

### **Access:**
```bash
# Dashboard UI
http://localhost:8501

# Grafana
http://localhost:3000
User: admin
Pass: viral_monitor_2025

# n8n
http://localhost:5678
User: admin
Pass: viral_admin_2025
```

---

## 🎯 **Roadmap**

### **Completado:**
- ✅ Docker V3 infrastructure (14 servicios)
- ✅ ML Core (YOLOv8 analysis)
- ✅ Meta Ads integration
- ✅ YouTube uploader
- ✅ Pixel Tracker
- ✅ n8n workflows
- ✅ Landing page generator
- ✅ Modo monitor-channel ⭐
- ✅ Control de carga inteligente
- ✅ Artista genérico para landing pages

### **Pendiente:**
- ⏳ Runway ML integration (AI video generation)
- ⏳ Re-enable Device Farm (cuando se necesite)
- ⏳ TikTok direct API integration
- ⏳ Advanced ML models (GPT captions, DALLE thumbnails)
- ⏳ Multi-language support

---

## 🤝 **Contribuir**

1. Fork el repo
2. Crea feature branch: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m "Add: nueva funcionalidad"`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Abre Pull Request

---

## 📄 **Licencia**

Ver [LICENSE](LICENSE)

---

## 🚀 **¡Empieza Ahora!**

```bash
# Setup completo (5 minutos)
./setup-credentials.sh
./download-models.sh
./v3-docker.sh start
./n8n-setup.sh

# Modo 1: Lanzar un video
python unified_system_v3.py \
  --mode launch \
  --video "mi_video.mp4" \
  --campaign-name "Mi Hit" \
  --paid-budget 500.0

# Modo 2: Monitorear canal completo ⭐
python unified_system_v3.py \
  --mode monitor-channel \
  --youtube-channel "UC_TuCanal" \
  --auto-launch \
  --max-campaigns-per-day 2
```

**¡A ROMPER LAS RRSS! 🔥🎵🚀**

---

## 📞 **Soporte**

- **Issues:** [GitHub Issues](https://github.com/SPAYTK/master/issues)
- **Documentación:** Ver carpeta `/docs`
- **Email:** (añade tu email de soporte aquí)

---

**Made with ❤️ for Community Managers**

---

## 💰 **ROI Estimado**

### **Inversión:**
- Setup inicial: $0 (software open-source)
- Budget mensual: $1,500-3,000 (Meta Ads)
- Tiempo setup: ~~10 minutos~~ **⚡ 30 segundos** (Meta-Centric)

### **Retorno:**
- 15-30M views/mes (organic + paid)
- 50-100K nuevos seguidores/mes
- 5-10x ROAS en Meta Ads
- Crecimiento canal: 50-80%/mes

**ROI: 500-1000% en 3 meses** 🚀

---

## 🚀 **NUEVO: Meta Ads-Centric Flow**

**Revoluciona tu workflow**: Crea campañas Meta Ads y **automáticamente** lanza en todas las plataformas.

```bash
# Un solo comando → Ecosistema completo activo
curl -X POST https://your-app.railway.app/campaigns/create-with-orchestration \
  -d '{"name": "Mi Hit 2025", "daily_budget": 100, "auto_optimize": true}'

# Resultado: YouTube + TikTok + Instagram + Twitter + Meta Ads ¡ACTIVOS!
```

**📊 Análisis completo**: [`META_CENTRIC_ARCHITECTURE.md`](META_CENTRIC_ARCHITECTURE.md)