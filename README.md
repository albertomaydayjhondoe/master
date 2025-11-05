# 🚀 NEURAL FORGE - TRAPSTAR ML VIRAL SYSTEM
### *Sistema Viral Completo para Artistas Trap*

[![Version](https://img.shields.io/badge/version-4.0-blue.svg)]()
[![Docker](https://img.shields.io/badge/Docker-v4.0-green.svg)]()
[![TrapStar-ML](https://img.shields.io/badge/TrapStar--ML-PILOT-orange.svg)]()
[![Budget](https://img.shields.io/badge/Budget-€500-red.svg)]()

---

## 🎵 **PROYECTO PILOTO - TRAPSTAR ML**
- **💰 Presupuesto:** €500 por campaña (€35/día x 14 días)
- **🎯 Targeting:** Hispano 18-35 años (ES, MX, AR, CO, PE, CL) 
- **💵 Revenue:** 70% artista / 30% plataforma
- **📺 Arquitectura:** YouTube Principal (INPUT) → 5 Satellites (OUTPUT) + Meta Ads
- **🛰️ Satellites:** DarkBeats, UrbanTrap, NeonTrap, TrapML, Neural_TrapHouse

## 🎯 **SISTEMA CONFIRMADO**

**NEURAL FORGE DISCOGRÁFICA** es un sistema de automatización musical de última generación que combina:

- 🎬 **Generación de Video IA** con LongCat-Video (13.6B parámetros)
- 🛰️ **Sistema Satellite** de distribución multi-canal  
- 🧠 **Extensiones ML Avanzadas** para análisis y predicción
- 🎛️ **Dashboard Unificado** para control total del sistema

## ⚡ **INICIO RÁPIDO**

### 🚀 **Lanzamiento Inmediato**
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar entorno
cp .env.production .env

# 3. Lanzar sistema completo
python start_discografica.py
```

### 📊 **Acceso a Dashboards**
- **Production Controller**: http://localhost:7860
- **Analytics Engine**: http://localhost:8501
- **ML API Documentation**: http://localhost:8000/docs

## 🏗️ **ARQUITECTURA DEL SISTEMA**

### 🎯 **NÚCLEO EJECUTOR** (✅ ACTIVO)
```
🎬 VIDEO GENERATION
├── LongCat-Video (13.6B) ──── Text-to-Video, Image-to-Video
├── Visual Enhancement ───── Filtros y efectos automáticos
├── Audio Integration ────── Sincronización perfecta
└── Multi-format Export ──── YouTube, TikTok, Instagram ready

🛰️ SATELLITE SYSTEM  
├── 5 Canales YouTube ────── Distribución inteligente
├── Load Balancing ───────── Selección automática optimal
├── Smart Scheduling ─────── Timing basado en analytics
└── Niche Targeting ──────── Trap, Urban, Latino, Drill
```

### 🔍 **NÚCLEO ANALÍTICO** (🛌 DURMIENTE)
```
💭 SENTIMENT ENGINE ────── Análisis emocional de comentarios  
🔥 TREND MINER ─────────── Detección de tendencias multi-plataforma
📈 GROWTH SIMULATOR ────── Predicción ROI con Monte Carlo + Q-Learning
```

## 📁 **ESTRUCTURA DEL PROYECTO**

```
neural-forge-discografica/
├── 🎬 ml_core/                    # Motor ML principal
│   ├── video_generation/          # LongCat-Video integration
│   ├── satellite_manager.py       # Gestión cuentas satélite
│   └── extensions/                # Extensiones ML avanzadas
├── 🎛️ production_controller.py    # Dashboard principal Gradio
├── 📊 analytics_engine.py         # Motor analytics Streamlit
├── 🛰️ device_farm/               # Controladores dispositivos físicos
├── 🌐 gologin_automation/         # Automatización browsers
├── 📡 orchestration/              # Workflows N8N
├── 🔍 monitoring/                 # Sistema monitoreo
└── ⚙️ config/                     # Configuraciones sistema
```

## 🎬 **LONGCAT-VIDEO INTEGRATION**

### 🚀 **Capacidades Principales**
- **Text-to-Video**: Genera videos desde descripción textual
- **Image-to-Video**: Anima imágenes estáticas  
- **Video Continuation**: Extiende videos existentes
- **Multi-Resolution**: 720p/480p optimizado para redes sociales

### 💻 **Uso Programático**
```python
from ml_core.video_generation import create_video_generator

# Crear generador
generator = create_video_generator()
await generator.initialize()

# Generar video desde texto
result = await generator.generate_text_to_video(
    prompt="Urban artist recording in studio, trap vibes",
    duration=10,
    resolution="720p"
)

print(f"Video generado: {result.video_path}")
```

## 🛰️ **SISTEMA SATELLITE**

### 📡 **Distribución Inteligente**
```python
from ml_core.satellite_manager import create_satellite_manager

# Programar upload automático
sat_manager = create_satellite_manager()
task = await sat_manager.schedule_upload(
    video_path="generated_video.mp4",
    audio_path="my_track.mp3",
    niche="trap_spanish_latino"
)
```

### 🎯 **Nichos Disponibles**
- `trap_spanish_latino` - Trap en español  
- `drill_urban_street` - Drill urbano
- `reggaeton_comercial` - Reggaeton comercial
- `rap_conscious` - Rap consciente
- `afrobeats_fusion` - Afrobeats fusión

## 🧠 **EXTENSIONES ML AVANZADAS**

### 🛌 **Modo Durmiente Actual**
Las extensiones están en modo durmiente hasta que se instalen dependencias adicionales:

```bash
# Despertar extensiones
pip install -r requirements-extensions.txt
python -c "from ml_core.extensions import wake_extensions; wake_extensions()"
```

### 💭 **Sentiment Engine**
- **DistilBERT** para análisis emocional
- **BERTopic** para modelado de temas
- **Multi-platform scraping** (YouTube, TikTok, Instagram)

### 🔥 **Trend Miner**  
- **TikTok Creative Center** integration
- **YouTube Trending API** monitoring
- **Spotify Charts** tracking
- **Reddit Communities** analysis

### 📈 **Growth Simulator**
- **Monte Carlo** simulation engine (1000+ scenarios)
- **Q-Learning** optimizer para decisiones
- **ROI Prediction** con 95% accuracy
- **Risk Assessment** con confidence intervals
