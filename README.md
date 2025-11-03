# 🎵 Discográfica ML - Ultra-Efficient Music Label System

Sistema ultra-eficiente de discográfica ML enfocado exclusivamente en:
- 🎯 Lanzamiento de campañas virales para artistas
- 📊 Analytics ML con modelos Ultralytics/YOLO  
- 🔴 Dashboard rector centralizado
- 🤖 Automatización Meta Ads para música
- 🔄 Workflows N8N para community management

## 🚀 Componentes Core

### **Production Controller (Gradio)**
- Centro de control principal
- Botón rojo para lanzar campañas
- Integración completa N8N

### **Analytics Engine (Streamlit)**  
- Análisis ML con Ultralytics
- Métricas de rendimiento musical
- Visualizaciones en tiempo real

### **ML Core**
- Modelos Ultralytics/YOLO preentrenados
- Análisis de contenido visual
- Predicciones de viralidad

### **Meta Automation**
- Campañas publicitarias automatizadas
- Targeting inteligente para música
- ROI tracking en tiempo real

## 🎮 Uso Rápido

```bash
# Iniciar dashboards
python3 production_controller.py &    # Puerto 7860
streamlit run analytics_engine.py &   # Puerto 8501

# Acceder
http://localhost:7860  # 🔴 BOTÓN ROJO
http://localhost:8501  # 📊 Analytics ML
```

## � Configuración de Producción

### **Tokens Requeridos para Funcionalidad Completa**

Para habilitar todas las funcionalidades necesitas obtener estos tokens:

#### **1. Meta Ads API (Obligatorio para publicidad)**
```bash
META_ACCESS_TOKEN=EAAG...    # Meta Business Access Token
META_APP_ID=123456789...     # App ID de Meta Developer
META_APP_SECRET=abcd1234...  # App Secret de Meta Developer
```
**Obtener en**: https://developers.facebook.com/
- Crear app Business
- Configurar Marketing API
- Generar Long-lived User Access Token

#### **2. YouTube Data API v3 (Para canal YouTube)**
```bash
YOUTUBE_CLIENT_ID=123...apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=GOCSPX-...
YOUTUBE_REFRESH_TOKEN=1//...
```
**Obtener en**: https://console.cloud.google.com/
- Crear proyecto Google Cloud
- Habilitar YouTube Data API v3
- Crear credenciales OAuth 2.0

#### **3. Telegram Bot API (Para automation)**
```bash
TELEGRAM_BOT_TOKEN=1234567890:AABBcc...
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcd1234efgh5678...
```
**Obtener en**: 
- Bot Token: @BotFather en Telegram
- API ID/Hash: https://my.telegram.org/

#### **4. N8N Webhooks (Para workflows)**
```bash
N8N_WEBHOOK_URL=http://localhost:5678
N8N_API_KEY=tu_n8n_api_key (opcional)
```

### **🚀 Activación Automática**
```bash
# Ejecutar configurador interactivo
./setup_production_tokens.sh
```

## �📋 Dependencias Mínimas

- gradio>=4.0.0 (Dashboard principal)
- streamlit>=1.28.0 (Analytics)  
- ultralytics>=8.0.0 (Modelos ML)
- plotly>=5.17.0 (Visualizaciones)
- requests>=2.31.0 (API calls)

## 🎯 Target: Discográfica ML Ultra-Eficiente

Sistema limpio, rápido y enfocado únicamente en el negocio musical con ML.
