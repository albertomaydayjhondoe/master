# 🔄 FLUJO DE DATOS I/O - SISTEMA TIKTOK ML v4

## 📊 **ARQUITECTURA COMPLETA DEL SISTEMA**

```mermaid
graph TD
    %% External Data Sources
    YT[🎥 YouTube API<br/>Videos, Analytics, Comments]
    SP[🎵 Spotify API<br/>Tracks, Playlists, Stats]
    META[🎯 Meta Ads API<br/>Campaigns, Performance]
    LP[🌐 Landing Pages<br/>Conversions, Traffic]
    N8N[🔄 n8n Workflows<br/>Automation, Triggers]

    %% Core System  
    API[🚀 FastAPI v4<br/>localhost:8000<br/>Main Controller]
    
    %% ML Processing
    YOLO[🤖 Ultralytics YOLOv8<br/>Image Detection<br/>Screenshot Analysis]
    
    %% Database
    SUPA[(🗄️ Supabase<br/>PostgreSQL<br/>Metrics Storage)]
    
    %% Internal Data Flow
    API --> |Process Images| YOLO
    YOLO --> |Detection Results| API
    
    %% External Integrations INPUT
    YT --> |Channel Data| API
    SP --> |Artist Metrics| API  
    META --> |Ad Performance| API
    LP --> |User Analytics| API
    N8N --> |Webhook Triggers| API
    
    %% Database Operations
    API --> |Store Metrics| SUPA
    SUPA --> |Retrieve Analytics| API
    
    %% Output Endpoints
    API --> |Analytics Dashboard| DASH[📊 Analytics UI<br/>Real-time Charts]
    API --> |JSON Responses| CLI[💻 API Clients<br/>External Apps]
    API --> |Webhook Events| EXT[🔗 External Systems<br/>n8n, Zapier]
    
    %% Styling
    classDef input fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef processing fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef storage fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef output fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
    class YT,SP,META,LP,N8N input
    class API,YOLO processing  
    class SUPA storage
    class DASH,CLI,EXT output
```

---

## 🔍 **DETALLE DE FLUJOS DE DATOS**

### **📥 INPUT STREAMS (Datos de Entrada)**

#### **1. 🎥 YouTube Data API → FastAPI**
```
ENDPOINT: /webhooks/youtube-metrics
METHOD: POST
DATA FLOW:
├── Channel Analytics (views, subscribers, engagement)
├── Video Performance (watch time, clicks, comments)  
├── Search Rankings (keyword positions)
└── Revenue Metrics (monetization data)
    ↓
    PROCESSING: Normalize data + Store in Supabase
    ↓  
    OUTPUT: Analytics dashboard + Webhook notifications
```

#### **2. 🎵 Spotify Web API → FastAPI**
```
ENDPOINT: /webhooks/spotify-metrics  
METHOD: POST
DATA FLOW:
├── Track Statistics (streams, saves, shares)
├── Playlist Performance (placements, discovery)
├── Artist Analytics (followers, listener demographics)
└── Market Data (chart positions, territories)
    ↓
    PROCESSING: Calculate engagement rates + Trend analysis
    ↓
    OUTPUT: Streaming dashboard + Growth predictions
```

#### **3. 🎯 Meta Ads API → FastAPI**
```
ENDPOINT: /meta-ads/report/{account_id}
METHOD: GET
DATA FLOW:  
├── Campaign Performance (reach, impressions, CTR)
├── Audience Insights (demographics, behaviors)
├── Conversion Tracking (purchases, sign-ups)
└── Budget & Spend Analysis (ROAS, CPC, CPM)
    ↓
    PROCESSING: ROI calculations + Optimization suggestions
    ↓
    OUTPUT: Ad performance dashboard + Budget alerts
```

#### **4. 🌐 Landing Pages → FastAPI**
```
ENDPOINT: /webhooks/landing-page-metrics
METHOD: POST  
DATA FLOW:
├── Traffic Analytics (visitors, sessions, bounce rate)
├── Conversion Funnels (sign-ups, purchases, downloads)
├── Source Attribution (organic, paid, social, direct)
└── User Behavior (time on page, scroll depth)
    ↓
    PROCESSING: Conversion rate optimization + A/B test results
    ↓
    OUTPUT: Conversion dashboard + Performance alerts
```

#### **5. 🔄 n8n Workflows → FastAPI**
```
ENDPOINT: Multiple webhook endpoints
METHOD: POST
DATA FLOW:
├── Automation Triggers (scheduled events, data updates)
├── Cross-platform Synchronization (sync campaigns)
├── Alert System (performance thresholds, anomalies)  
└── Workflow Results (task completion, error handling)
    ↓
    PROCESSING: Workflow orchestration + Event routing
    ↓
    OUTPUT: Automation dashboard + Task notifications
```

---

### **🔬 PROCESSING LAYER (ML & Analytics)**

#### **🤖 Ultralytics YOLOv8 Integration**
```
ENDPOINT: /ml/ultralytics/detect
METHOD: POST  
INPUT: Screenshot images, video frames
PROCESSING:
├── Object Detection (UI elements, buttons, text)
├── Scene Classification (app screens, content types)
├── Anomaly Detection (shadowbans, unusual patterns)
└── Performance Metrics (detection confidence, speed)
    ↓
    ML OUTPUT: Detection results + Confidence scores
    ↓
    STORAGE: Results stored in Supabase for analysis
```

---

### **🗄️ STORAGE LAYER (Supabase PostgreSQL)**

#### **Database Schema & Tables**
```sql
-- Core Analytics Tables
📊 youtube_metrics
├── channel_id, video_id, timestamp
├── views, likes, comments, subscribers  
├── watch_time, engagement_rate
└── revenue, rpm, cpm

📊 spotify_metrics  
├── artist_id, track_id, timestamp
├── streams, saves, playlist_adds
├── listener_count, follower_growth
└── chart_position, market_data

📊 meta_ads_metrics
├── account_id, campaign_id, timestamp  
├── impressions, clicks, conversions
├── spend, cpc, cpm, roas
└── audience_data, targeting_info

📊 landing_page_metrics
├── page_url, session_id, timestamp
├── visitors, conversions, bounce_rate  
├── traffic_source, device_type
└── funnel_step, conversion_value

📊 ml_detections
├── image_id, detection_type, timestamp
├── confidence_score, bounding_box
├── classification, anomaly_flag
└── processing_time, model_version
```

---

### **📤 OUTPUT STREAMS (Datos de Salida)**

#### **1. 📊 Analytics Dashboard Endpoints**
```
GET /analytics/comprehensive
├── Unified view of all platform metrics
├── Real-time performance indicators  
├── Cross-platform correlation analysis
└── ROI and conversion tracking

GET /analytics/youtube
├── Channel performance deep-dive
├── Video engagement analytics
├── Revenue optimization insights  
└── Growth trend predictions

GET /analytics/spotify
├── Streaming performance metrics
├── Playlist placement tracking
├── Fan engagement analysis
└── Market penetration data

GET /analytics/meta-ads  
├── Campaign performance overview
├── Audience insights & targeting
├── Budget optimization recommendations
└── A/B test results & insights
```

#### **2. 🔗 Webhook Outputs (Para n8n/Automatización)**
```
Webhook Triggers Enviados:
├── Performance Alerts (when metrics exceed thresholds)
├── Conversion Events (new sign-ups, purchases)  
├── Anomaly Detected (unusual patterns, shadowbans)
├── Campaign Updates (budget changes, performance shifts)
└── ML Results (detection completed, confidence scores)
```

#### **3. 💻 API Client Integration**
```
JSON Response Format:
{
  "status": "success",
  "timestamp": "2025-10-27T10:30:00Z",
  "data": {
    "metrics": {...},
    "insights": {...}, 
    "recommendations": {...}
  },
  "meta": {
    "processing_time": "1.2s",
    "cache_status": "fresh",
    "api_version": "v4"
  }
}
```

---

## 🚀 **FLUJO DE DATOS EN TIEMPO REAL**

### **Secuencia Típica de Procesamiento:**
```
1. 📥 INGEST: External APIs → FastAPI webhooks
2. 🔍 VALIDATE: Data validation + authentication  
3. 🤖 PROCESS: ML analysis + metric calculations
4. 💾 STORE: Normalized data → Supabase tables
5. 📊 ANALYZE: Cross-platform correlation + insights
6. 🔔 NOTIFY: Alerts + webhook triggers → n8n
7. 📤 SERVE: Real-time dashboard + API responses
```

### **Performance Characteristics:**
- **⚡ Latency**: < 500ms para endpoints simples
- **🔄 Throughput**: 1000+ requests/min por endpoint
- **💾 Storage**: Metrics agregados por hora/día/semana
- **🤖 ML Processing**: 2-5s para análisis YOLOv8
- **📊 Dashboard**: Actualización cada 30s

---

## 🔧 **CONFIGURACIÓN DE INTEGRACIÓN**

### **Environment Variables Críticas:**
```bash
# === CORE API ===
API_HOST=0.0.0.0
API_PORT=8000  
API_SECRET_KEY=your-secret-key

# === SUPABASE (Storage) ===
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# === EXTERNAL APIS ===  
YOUTUBE_API_KEY=your-youtube-key
SPOTIFY_CLIENT_ID=your-spotify-id
SPOTIFY_CLIENT_SECRET=your-spotify-secret
META_ACCESS_TOKEN=your-meta-token

# === AUTOMATION ===
N8N_WEBHOOK_BASE_URL=your-n8n-url
N8N_API_KEY=your-n8n-key
```

### **Modos de Operación:**
- **🔐 SUPABASE_ONLY=true**: Solo base de datos, sin APIs externas
- **🎯 DUMMY_MODE=false**: Producción con todas las integraciones
- **📊 PRODUCTION_MODE=true**: Optimizaciones para producción
- **🐛 DEBUG=false**: Logging optimizado para producción

---

**🎯 Este es el flujo completo I/O del sistema v4 que tenemos implementado.**