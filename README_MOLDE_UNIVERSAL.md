# 🎵 DISCOGRÁFICA ML SYSTEM - UNIVERSAL TEMPLATE

## 🎯 **MOLDE BASE PARA REPLICACIÓN DE CAMPAÑAS MUSICALES**

Este repositorio es el **molde universal** para crear campañas musicales automatizadas con inteligencia artificial. Cada campaña específica se replica a partir de este template base.

---

## 🏗️ **ARQUITECTURA DEL MOLDE**

### 📊 **DASHBOARDS UNIVERSALES**
- **🎮 Production Controller** (Puerto 7860)
  - Interfaz Gradio para lanzar campañas
  - Botón rojo para activación viral
  - Control multi-plataforma unificado

- **📈 Analytics Engine** (Puerto 8501)  
  - Motor Streamlit con ML integrado
  - Análisis Ultralytics/YOLO en tiempo real
  - Métricas de performance por género

### 🔄 **ORQUESTACIÓN N8N**
- **Workflows Flexibles** que se adaptan por género:
  - `main_orchestrator.json` - Coordinador principal
  - `ml_decision_engine.json` - Engine de decisiones ML
  - Workflows específicos por plataforma
  - Auto-configuración según género musical

### 🤖 **INTELIGENCIA ARTIFICIAL INTEGRADA**
- **YOLO v8** para análisis visual de contenido
- **ML Engine** para predicción de viralidad  
- **Pattern Recognition** para detección de trends
- **Automated Content Generation** para posts
- **A/B Testing** automático con ML

---

## 🎼 **GÉNEROS SOPORTADOS**

El molde incluye configuraciones optimizadas para:

| Género | Descripción | Target Audience | Platforms Weight |
|--------|-------------|-----------------|------------------|
| **🎤 Trap** | Música urbana con beats pesados | 16-35 años | TikTok 40% |
| **🎵 Reggaeton** | Música latina con ritmo pegajoso | 18-40 años | Instagram 35% |
| **🎶 Pop** | Música popular mainstream | 13-45 años | YouTube 25% |
| **🎸 Rock** | Música rock con instrumentos en vivo | 16-50 años | YouTube 35% |
| **💕 Bachata** | Música romántica latina | 20-50 años | Instagram 40% |
| **🎧 Electronic/EDM** | Música electrónica para festivales | 16-35 años | TikTok 35% |
| **💃 Salsa** | Música latina bailable tradicional | 25-60 años | Facebook 15% |
| **🎷 Jazz** | Música sofisticada con improvisación | 25-65 años | YouTube 40% |

---

## 🚀 **INTEGRACIONES COMPLETAS**

### 📱 **META ADS AUTOMATION**
- **Sistema Completo**: `social_extensions/meta/meta_automator.py`
- **Campaign Creation** automática con A/B testing
- **Budget Optimization** basada en ML
- **Audience Targeting** por género musical
- **Performance Tracking** en tiempo real

### 🎬 **YOUTUBE CHANNEL AUTOMATION**  
- **Cliente Completo**: `telegram_automation/integrations/youtube_client.py`
- **OAuth2 Flow** preparado para producción
- **Video Upload** automático con metadata ML
- **Engagement Automation** (likes, comments, subscriptions)
- **Analytics Integration** con YouTube Data API v3

### 🤖 **TELEGRAM BOT ECOSYSTEM**
- **Multi-Bot System** para engagement masivo
- **Like4Like Automation** con detección inteligente
- **Community Management** automatizado
- **Cross-Platform Coordination** via webhooks

### 🌐 **GOLOGIN PROFILES**
- **Multi-Profile Management** para escalado
- **Proxy Integration** para evitar detección
- **Browser Automation** con patrones humanos
- **Account Health Monitoring**

---

## 🔧 **CONFIGURACIÓN POR CAMPAÑA**

### 🎯 **SETUP AUTOMÁTICO**
```bash
# 1. Configurar tokens interactivamente
./setup_production_tokens.sh

# 2. Generar configuración de artista
python config_artist_generator.py

# 3. Validar sistema completo
./validate_tokens.sh

# 4. Lanzar molde personalizado
./start_discografica_ml.sh
```

### 🎨 **PERSONALIZACIÓN POR GÉNERO**
El molde se auto-configura según el género seleccionado:
- **Hashtags optimizados** por estilo musical
- **Horarios de posting** ideales por audiencia
- **Distribución de presupuesto** por plataforma
- **Templates de contenido** especializados
- **Targeting de audiencia** específico

---

## 📊 **COMPONENTES DEL MOLDE**

### 🏠 **CORE SYSTEM**
```
├── production_controller.py      # Dashboard principal Gradio
├── analytics_engine.py           # Motor analytics Streamlit  
├── config_artist_generator.py    # Configurador interactivo
├── start_discografica_ml.sh      # Launcher completo
├── setup_production_tokens.sh    # Configurador tokens
└── validate_tokens.sh            # Validador sistema
```

### 🗂️ **CONFIGURACIONES**
```
config/
├── genres/
│   └── genre_config.yaml         # Configuraciones por género
├── meta/
│   └── meta_production.env       # Variables Meta Ads
├── ml/
│   └── model_config.yaml         # Configuración ML/YOLO
└── accounts/
    └── *.json                    # Configuraciones artistas
```

### 🤖 **AUTOMATION ENGINES**
```
├── ml_core/                      # Motor ML con FastAPI
├── device_farm/                  # Control dispositivos físicos
├── gologin_automation/           # Gestión perfiles browser
├── telegram_automation/          # Bots Telegram ecosystem
├── social_extensions/            # Meta Ads + ML integration
└── orchestration/               # N8N workflows
```

---

## 🎯 **PATRÓN DE REPLICACIÓN**

### 📋 **FLUJO DE CREACIÓN DE CAMPAÑA**
1. **Prompt de Campaña** → Usuario especifica género, artista, objetivos
2. **Replicación del Molde** → Sistema crea nuevo repo basado en template
3. **Auto-Configuración** → Molde se adapta a la campaña específica
4. **Lanzamiento** → Campaña lista para ejecutar con botón rojo

### 🚀 **CASOS DE USO**
```bash
# Ejemplos de replicación:
discografica-ml-system → campaña-trap-artista-x
discografica-ml-system → campaña-reggaeton-navidad-2024  
discografica-ml-system → campaña-pop-verano-festival
discografica-ml-system → campaña-rock-tour-europa
```

---

## 🔑 **TOKENS UNIVERSALES REQUERIDOS**

### 📱 **Meta Business API**
```bash
META_ACCESS_TOKEN=          # Long-lived User Access Token
META_APP_ID=                # Facebook App ID  
META_APP_SECRET=            # Facebook App Secret
META_AD_ACCOUNT_ID=         # Ad Account ID (sin 'act_')
META_PAGE_ID=               # Facebook Page ID
```

### 🎬 **YouTube Data API v3**
```bash
YOUTUBE_CLIENT_ID=          # OAuth2 Client ID
YOUTUBE_CLIENT_SECRET=      # OAuth2 Client Secret  
YOUTUBE_API_KEY=            # YouTube Data API Key
YOUTUBE_REFRESH_TOKEN=      # OAuth2 Refresh Token
```

### 🤖 **Telegram Bot API**
```bash
TELEGRAM_BOT_TOKEN=         # Bot Token de @BotFather
TELEGRAM_API_ID=            # API ID de my.telegram.org
TELEGRAM_API_HASH=          # API Hash de my.telegram.org
```

### 🌐 **GoLogin API (Opcional)**
```bash
GOLOGIN_API_TOKEN=          # GoLogin API Token
GOLOGIN_PROFILE_COUNT=10    # Cantidad de perfiles
```

---

## 📈 **MÉTRICAS Y ANALYTICS**

### 🎯 **KPIs TRACKED**
- **Reach Orgánico** por plataforma y género
- **Engagement Rate** promedio por tipo de contenido
- **Conversion Rate** de fans a streams/ventas
- **ROI** de campañas pagadas vs orgánicas  
- **Viral Coefficient** de contenido por género
- **Cost Per Acquisition** por plataforma

### 📊 **DASHBOARDS INTEGRADOS**
- **Vista Ejecutiva** de performance global
- **Análisis por Artista** individual
- **Comparativas** entre géneros musicales
- **Predicciones ML** de viralidad
- **Alertas Automáticas** de oportunidades

---

## 🛠️ **STACK TECNOLÓGICO**

### 🧠 **Machine Learning Stack**
- **Ultralytics YOLO v8** - Análisis visual avanzado
- **FastAPI** - API de ML para predicciones
- **Scikit-learn** - Modelos predictivos
- **TensorFlow** - Deep learning para patterns

### 🖥️ **Interface Stack**  
- **Gradio** - Production Controller dashboard
- **Streamlit** - Analytics Engine dashboard
- **N8N** - Workflow automation visual

### 🔗 **Integration Stack**
- **Meta Graph API** - Facebook/Instagram automation
- **YouTube Data API v3** - YouTube automation completo
- **Telegram Bot API** - Community management
- **GoLogin API** - Multi-profile management

### 🗄️ **Data Stack**
- **SQLite** - Base de datos local para desarrollo
- **PostgreSQL** - Base de datos producción
- **Redis** - Caché y sesiones
- **InfluxDB** - Métricas time-series

---

## 🚀 **INICIO RÁPIDO UNIVERSAL**

### 1️⃣ **Clonación del Molde**
```bash
git clone https://github.com/albertomaydayjhondoe/discografica-ml-system.git
cd discografica-ml-system
```

### 2️⃣ **Configuración Automática**
```bash
# Setup completo interactivo
./setup_production_tokens.sh

# Configurar artista/género
python config_artist_generator.py
```

### 3️⃣ **Validación y Lanzamiento**
```bash
# Validar configuración
./validate_tokens.sh

# Lanzar sistema completo
./start_discografica_ml.sh
```

### 4️⃣ **Acceso a Dashboards**
- 🎮 **Production Controller**: http://localhost:7860
- 📊 **Analytics Engine**: http://localhost:8501
- 🔄 **N8N Workflows**: http://localhost:5678

---

## 💡 **CARACTERÍSTICAS ÚNICAS DEL MOLDE**

### ✨ **AUTO-ADAPTACIÓN**
- Configuración automática según género seleccionado
- Templates dinámicos por estilo musical
- Optimización ML por audiencia target

### 🚀 **ESCALABILIDAD**
- Multi-artista simultáneo
- Multi-género en paralelo  
- Auto-scaling de recursos según demanda

### 🧠 **INTELIGENCIA**
- Predicciones ML de viralidad
- A/B testing automático
- Optimización continua basada en performance

### 🔄 **AUTOMATIZACIÓN**
- Community management 24/7
- Cross-platform posting coordinado
- Engagement orgánico inteligente

---

## 🎵 **LISTO PARA REPLICAR**

Este molde base está **100% preparado** para ser replicado en campañas específicas. 

**Próximo paso**: Introducir prompt de campaña trap para primera replicación.

---

## 📞 **SOPORTE Y DOCUMENTACIÓN**

### 📚 **Documentación Técnica**
- `TOKENS_PREPARATION_GUIDE.md` - Guía configuración tokens
- `DEVELOPMENT_GUIDE.md` - Guía para desarrolladores  
- `API_INTEGRATION.md` - Documentación APIs
- `ML_MODELS_GUIDE.md` - Guía modelos ML

### 🔧 **Scripts de Utilidad**
- `setup_production_tokens.sh` - Configuración automática
- `validate_tokens.sh` - Validación completa
- `config_artist_generator.py` - Configurador artistas
- `start_discografica_ml.sh` - Launcher universal

---

**🎵 MOLDE UNIVERSAL LISTO PARA CAMPAÑAS VIRALES 🚀**

*Template desarrollado para la automatización musical con IA*

**#DiscograficaML #MusicAutomation #ViralCampaigns #MLMusic**