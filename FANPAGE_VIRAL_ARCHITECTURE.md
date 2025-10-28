# 🎯 Fanpage Viral Architecture - Docker Cloud Ready

## Análisis de Preparación: Docker en Cloud para Estrategia Híbrida

### ✅ ESTADO ACTUAL: Base Sólida (60% Lista)

#### **LO QUE YA ESTÁ PREPARADO:**

```yaml
INFRAESTRUCTURA EXISTENTE:
  ✅ ML Core Service (8000):
     - YOLOv8 video quality predictor
     - Engagement optimizer
     - Posting time prediction
     - Content affinity matrix
  
  ✅ Database Stack:
     - PostgreSQL para métricas y logs
     - Redis para caching y queues
  
  ✅ Device Farm (comentado, listo para activar):
     - ADB controller para móviles
     - Multi-device management
  
  ✅ Meta Ads Service (8002):
     - Campaign management
     - Audience targeting
  
  ✅ Monitoring:
     - Health checks
     - Auto-restart
     - Nginx reverse proxy

WORKFLOWS BÁSICOS:
  ✅ n8n main_orchestrator.json (cron scheduling)
  ✅ n8n ml_decision_engine.json (ML predictions)
  ✅ n8n device_farm_trigger.json (device coordination)
```

---

### ❌ LO QUE FALTA PARA ESTRATEGIA COMPLETA:

```yaml
CONTENT GENERATION PIPELINE:
  ❌ Runway Gen-4 API Integration Service
  ❌ FFmpeg Video Processing Pipeline
  ❌ Automated Content Editor
  ❌ Multi-platform Upload Manager

ACQUISITION & ENGAGEMENT:
  ❌ TikTok/Instagram Scraper Service
  ❌ Bot Engine (likes, comments, shares)
  ❌ Follower Growth Tracker
  ❌ CAC (Cost per Acquisition) Calculator

n8n WORKFLOWS AVANZADOS:
  ❌ Daily Content Generation Workflow
  ❌ Intelligent Engagement Executor
  ❌ Acquisition Tracking Workflow
  ❌ Viral Detection & Boost System
  ❌ Cross-Engagement Matrix Builder

FANPAGE INFRASTRUCTURE:
  ❌ GoLogin Web Automation (parcialmente implementado)
  ❌ Multi-account Publishing Coordinator
  ❌ Shadowban Detection System
  ❌ Account Health Monitor
```

---

## 🏗️ ARQUITECTURA EXTENDIDA PROPUESTA

### Docker Compose Completo con Todos los Servicios

```yaml
# docker-compose-fanpage-full.yml
version: '3.8'

services:
  # ============================================
  # EXISTING SERVICES (Ya funcionando)
  # ============================================
  
  ml-core:
    # [Ya configurado en docker-compose.yml]
    # Maneja: YOLOv8, ML predictions, quality filtering
  
  dashboard:
    # [Ya configurado]
    # Red Button Control Interface
  
  database:
    # [Ya configurado]
    # PostgreSQL para todas las métricas
  
  redis:
    # [Ya configurado]
    # Caching + Queue management

  # ============================================
  # NEW SERVICES (Para Fanpage Automation)
  # ============================================

  # n8n Orchestrator - Cerebro de todo
  n8n:
    image: n8nio/n8n:latest
    container_name: tiktok-n8n
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER:-admin}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD:-change_this}
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://n8n:5678/
      - GENERIC_TIMEZONE=America/Mexico_City
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=database
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=${DB_USER:-tiktok_user}
      - DB_POSTGRESDB_PASSWORD=${DB_PASSWORD:-change_this_password}
    volumes:
      - n8n-data:/home/node/.n8n
      - ./orchestration/n8n_workflows:/home/node/.n8n/workflows:ro
      - ./data:/data  # Access to generated videos
    ports:
      - "5678:5678"
    networks:
      - tiktok-network
    restart: unless-stopped
    depends_on:
      - database
      - redis
      - ml-core
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:5678/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Content Generator - Runway Gen-4 Integration
  content-generator:
    build:
      context: .
      dockerfile: docker/Dockerfile.content-generator
    container_name: tiktok-content-gen
    environment:
      - RUNWAY_API_KEY=${RUNWAY_API_KEY}
      - RUNWAY_API_URL=https://api.runwayml.com/v1
      - OUTPUT_DIR=/data/generated_videos
      - DUMMY_MODE=${DUMMY_MODE:-true}
    volumes:
      - ./data:/data
      - ./logs:/app/logs
    ports:
      - "8003:8003"
    networks:
      - tiktok-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Video Processor - FFmpeg Pipeline
  video-processor:
    build:
      context: .
      dockerfile: docker/Dockerfile.video-processor
    container_name: tiktok-video-processor
    environment:
      - INPUT_DIR=/data/generated_videos
      - OUTPUT_DIR=/data/processed_videos
      - EFFECTS_PRESET=trap  # trap, reggaeton, afrobeat
      - DUMMY_MODE=${DUMMY_MODE:-true}
    volumes:
      - ./data:/data
      - ./scripts/video_processing:/app/scripts
      - ./logs:/app/logs
    ports:
      - "8004:8004"
    networks:
      - tiktok-network
    restart: unless-stopped

  # Social Scraper - TikTok/IG Metrics
  social-scraper:
    build:
      context: .
      dockerfile: docker/Dockerfile.scraper
    container_name: tiktok-scraper
    environment:
      - SCRAPE_INTERVAL=300  # 5 minutos
      - PLATFORMS=tiktok,instagram
      - PROXY_ENABLED=true
      - PROXY_LIST=${PROXY_LIST}
      - DUMMY_MODE=${DUMMY_MODE:-true}
    volumes:
      - ./data:/data
      - ./config/accounts:/app/accounts
      - ./logs:/app/logs
    ports:
      - "8005:8005"
    networks:
      - tiktok-network
    restart: unless-stopped
    depends_on:
      - database
      - redis

  # Bot Engine - Automated Engagement
  bot-engine:
    build:
      context: .
      dockerfile: docker/Dockerfile.bot-engine
    container_name: tiktok-bot-engine
    environment:
      - MAX_CONCURRENT_ACTIONS=10
      - HUMANIZATION_ENABLED=true
      - AFFINITY_MATRIX_ENABLED=true
      - DUMMY_MODE=${DUMMY_MODE:-true}
    volumes:
      - ./device_farm:/app/device_farm
      - ./gologin_automation:/app/gologin
      - ./data:/data
      - ./logs:/app/logs
    ports:
      - "8006:8006"
    networks:
      - tiktok-network
    restart: unless-stopped
    depends_on:
      - ml-core
      - redis
      - database

  # GoLogin Service - Web Browser Automation
  gologin-service:
    build:
      context: .
      dockerfile: docker/Dockerfile.gologin
    container_name: tiktok-gologin
    environment:
      - GOLOGIN_API_TOKEN=${GOLOGIN_API_TOKEN}
      - PROFILES_DIR=/data/gologin_profiles
      - MAX_PROFILES=30
      - DUMMY_MODE=${DUMMY_MODE:-true}
    volumes:
      - ./gologin_automation:/app/gologin
      - ./data:/data
      - ./logs:/app/logs
    ports:
      - "8007:8007"
    networks:
      - tiktok-network
    restart: unless-stopped
    depends_on:
      - redis

  # Publishing Coordinator - Multi-platform Upload
  publishing-coordinator:
    build:
      context: .
      dockerfile: docker/Dockerfile.publisher
    container_name: tiktok-publisher
    environment:
      - PLATFORMS=tiktok,instagram,youtube_shorts
      - MAX_CONCURRENT_UPLOADS=5
      - RETRY_FAILED=true
      - DUMMY_MODE=${DUMMY_MODE:-true}
    volumes:
      - ./data:/data
      - ./config/accounts:/app/accounts
      - ./logs:/app/logs
    ports:
      - "8008:8008"
    networks:
      - tiktok-network
    restart: unless-stopped
    depends_on:
      - gologin-service
      - bot-engine
      - ml-core

  # Acquisition Tracker - Follower Growth & CAC
  acquisition-tracker:
    build:
      context: .
      dockerfile: docker/Dockerfile.acquisition
    container_name: tiktok-acquisition
    environment:
      - TRACKING_INTERVAL=3600  # 1 hora
      - CAC_CALCULATION=daily
      - GOOGLE_SHEETS_ENABLED=true
      - GOOGLE_SHEETS_ID=${GOOGLE_SHEETS_ID}
      - DUMMY_MODE=${DUMMY_MODE:-true}
    volumes:
      - ./data:/data
      - ./logs:/app/logs
    ports:
      - "8009:8009"
    networks:
      - tiktok-network
    restart: unless-stopped
    depends_on:
      - social-scraper
      - database

networks:
  tiktok-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

volumes:
  postgres-data:
  redis-data:
  n8n-data:
```

---

## 📂 ESTRUCTURA DE SERVICIOS FALTANTES

### 1. Content Generator Service

```python
# services/content_generator/main.py
"""
Runway Gen-4 API Integration
Genera videos basados en prompts ML-optimizados
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import asyncio
from typing import List, Optional

app = FastAPI(title="Content Generator Service")

class VideoGenerationRequest(BaseModel):
    prompt: str
    duration: int = 2  # segundos
    aspect_ratio: str = "9:16"
    style: Optional[str] = "trap_aesthetic"

class VideoGenerationResponse(BaseModel):
    video_id: str
    video_url: str
    status: str
    quality_score: float

@app.post("/generate", response_model=VideoGenerationResponse)
async def generate_video(request: VideoGenerationRequest):
    """
    Genera video usando Runway Gen-4
    
    DUMMY_MODE: Retorna video de muestra
    PRODUCTION: Llama a Runway API
    """
    if os.getenv("DUMMY_MODE", "true") == "true":
        return VideoGenerationResponse(
            video_id=f"dummy_{uuid.uuid4().hex[:8]}",
            video_url=f"/data/samples/trap_video_{random.randint(1,5)}.mp4",
            status="completed",
            quality_score=0.85
        )
    
    # PRODUCTION: Real Runway API call
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.runwayml.com/v1/generate",
            headers={"Authorization": f"Bearer {os.getenv('RUNWAY_API_KEY')}"},
            json={
                "prompt": request.prompt,
                "duration": request.duration,
                "aspect_ratio": request.aspect_ratio,
                "model": "gen-4"
            },
            timeout=120.0
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Runway API error")
        
        data = response.json()
        
        return VideoGenerationResponse(
            video_id=data["id"],
            video_url=data["video_url"],
            status=data["status"],
            quality_score=0.0  # Se calculará después con ML
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "content-generator"}
```

### 2. Video Processor Service

```python
# services/video_processor/main.py
"""
FFmpeg Pipeline para efectos trap/reggaeton
"""

from fastapi import FastAPI, BackgroundTasks
import subprocess
import os

app = FastAPI(title="Video Processor Service")

class VideoProcessingRequest(BaseModel):
    input_path: str
    output_path: str
    effects_preset: str = "trap"

@app.post("/process")
async def process_video(request: VideoProcessingRequest, background_tasks: BackgroundTasks):
    """
    Aplica efectos con FFmpeg
    
    Efectos trap:
    - Filtro de color azul/morado neón
    - Glitch effects
    - Bass boost
    - Transiciones rápidas
    """
    
    if os.getenv("DUMMY_MODE", "true") == "true":
        # Simular procesamiento
        await asyncio.sleep(2)
        return {"status": "completed", "output": request.output_path}
    
    # PRODUCTION: FFmpeg command
    ffmpeg_cmd = build_ffmpeg_command(request)
    
    background_tasks.add_task(execute_ffmpeg, ffmpeg_cmd)
    
    return {"status": "processing", "output": request.output_path}

def build_ffmpeg_command(request: VideoProcessingRequest) -> List[str]:
    """
    Construye comando FFmpeg según preset
    """
    if request.effects_preset == "trap":
        return [
            "ffmpeg", "-i", request.input_path,
            "-vf", "colorbalance=rs=0.1:gs=-0.1:bs=0.3,eq=brightness=0.05:contrast=1.2",
            "-af", "bass=g=8,treble=g=4",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            request.output_path
        ]
    # Otros presets...
```

### 3. Social Scraper Service

```python
# services/social_scraper/main.py
"""
Scraper de métricas de TikTok/Instagram
"""

from fastapi import FastAPI
from playwright.async_api import async_playwright
import json

app = FastAPI(title="Social Scraper Service")

class MetricsScrapeRequest(BaseModel):
    platform: str
    video_url: str
    account_id: str

@app.post("/scrape_metrics")
async def scrape_metrics(request: MetricsScrapeRequest):
    """
    Extrae views, likes, comments, shares
    
    DUMMY_MODE: Retorna datos simulados
    PRODUCTION: Usa Playwright + proxies
    """
    
    if os.getenv("DUMMY_MODE", "true") == "true":
        return {
            "video_id": request.video_url,
            "views": random.randint(1000, 100000),
            "likes": random.randint(100, 10000),
            "comments": random.randint(10, 1000),
            "shares": random.randint(5, 500),
            "scraped_at": datetime.now().isoformat()
        }
    
    # PRODUCTION: Real scraping con Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            proxy={"server": get_proxy()}
        )
        page = await browser.new_page()
        await page.goto(request.video_url)
        
        metrics = await extract_metrics(page, request.platform)
        
        await browser.close()
        
        return metrics
```

### 4. Bot Engine Service

```python
# services/bot_engine/main.py
"""
Coordina acciones de engagement automatizado
"""

from fastapi import FastAPI
import httpx

app = FastAPI(title="Bot Engine Service")

class EngagementRequest(BaseModel):
    video_id: str
    target_likes: int
    target_comments: int
    accounts_pool: List[str]
    humanization: bool = True

@app.post("/execute_engagement")
async def execute_engagement(request: EngagementRequest):
    """
    Distribuye engagement entre cuentas
    
    1. Consulta ML para affinity matrix
    2. Selecciona mejores cuentas
    3. Distribuye acciones con delays humanizados
    4. Ejecuta via GoLogin + Device Farm
    """
    
    # Consultar ML para strategy
    async with httpx.AsyncClient() as client:
        ml_response = await client.post(
            "http://ml-core:8000/engagement_strategy",
            json={
                "video_id": request.video_id,
                "target_likes": request.target_likes,
                "available_accounts": request.accounts_pool
            }
        )
        
        strategy = ml_response.json()
    
    # Ejecutar acciones
    results = await distribute_engagement(strategy)
    
    return {
        "status": "completed",
        "likes_given": results["likes"],
        "comments_posted": results["comments"],
        "accounts_used": len(results["accounts"])
    }
```

---

## 🔄 n8n WORKFLOWS COMPLETOS

### Workflow 1: Daily Viral Content Pipeline

```json
{
  "name": "Daily Viral Content Pipeline",
  "nodes": [
    {
      "id": "trigger",
      "type": "schedule",
      "name": "Every 6 Hours",
      "parameters": {"cron": "0 */6 * * *"}
    },
    {
      "id": "ml_prompts",
      "type": "httpRequest",
      "name": "ML: Get Optimal Prompts",
      "parameters": {
        "url": "http://ml-core:8000/get_optimal_prompts",
        "method": "POST",
        "body": {"num_prompts": 5, "genre": "trap"}
      }
    },
    {
      "id": "generate",
      "type": "httpRequest",
      "name": "Generate Videos",
      "parameters": {
        "url": "http://content-generator:8003/generate",
        "method": "POST",
        "body": {"prompt": "={{$json.prompt}}"}
      }
    },
    {
      "id": "wait",
      "type": "wait",
      "name": "Wait Generation",
      "parameters": {"amount": 30, "unit": "seconds"}
    },
    {
      "id": "process",
      "type": "httpRequest",
      "name": "Process with FFmpeg",
      "parameters": {
        "url": "http://video-processor:8004/process",
        "method": "POST",
        "body": {
          "input_path": "={{$json.video_url}}",
          "effects_preset": "trap"
        }
      }
    },
    {
      "id": "quality_check",
      "type": "httpRequest",
      "name": "ML: Quality Filter",
      "parameters": {
        "url": "http://ml-core:8000/analyze_video_quality",
        "method": "POST",
        "body": {"video_path": "={{$json.output_path}}"}
      }
    },
    {
      "id": "if_quality",
      "type": "if",
      "name": "Quality > 75?",
      "parameters": {
        "conditions": {
          "number": [{"value1": "={{$json.quality_score}}", "operation": "larger", "value2": 75}]
        }
      }
    },
    {
      "id": "predict_accounts",
      "type": "httpRequest",
      "name": "ML: Best Accounts",
      "parameters": {
        "url": "http://ml-core:8000/predict_best_accounts",
        "method": "POST",
        "body": {"video_features": "={{$json.features}}"}
      }
    },
    {
      "id": "publish",
      "type": "httpRequest",
      "name": "Publish Multi-platform",
      "parameters": {
        "url": "http://publishing-coordinator:8008/publish",
        "method": "POST",
        "body": {
          "video_path": "={{$json.output_path}}",
          "accounts": "={{$json.selected_accounts}}",
          "platforms": ["tiktok", "instagram"]
        }
      }
    },
    {
      "id": "save_db",
      "type": "postgres",
      "name": "Save to Database",
      "parameters": {
        "operation": "insert",
        "table": "published_videos",
        "columns": "video_id, quality_score, accounts, published_at"
      }
    },
    {
      "id": "notify",
      "type": "discord",
      "name": "Notify Discord",
      "parameters": {
        "webhook": "={{$credentials.discordWebhook}}",
        "content": "✅ Published video (Score: ={{$json.quality_score}})"
      }
    }
  ],
  "connections": {
    "trigger": {"main": [[{"node": "ml_prompts"}]]},
    "ml_prompts": {"main": [[{"node": "generate"}]]},
    "generate": {"main": [[{"node": "wait"}]]},
    "wait": {"main": [[{"node": "process"}]]},
    "process": {"main": [[{"node": "quality_check"}]]},
    "quality_check": {"main": [[{"node": "if_quality"}]]},
    "if_quality": {
      "main": [
        [{"node": "predict_accounts"}],
        [{"node": "notify_rejected"}]
      ]
    },
    "predict_accounts": {"main": [[{"node": "publish"}]]},
    "publish": {"main": [[{"node": "save_db"}]]},
    "save_db": {"main": [[{"node": "notify"}]]}
  }
}
```

### Workflow 2: Intelligent Engagement Executor

```json
{
  "name": "Intelligent Engagement Executor",
  "nodes": [
    {
      "id": "trigger",
      "type": "schedule",
      "name": "Every 30 Minutes",
      "parameters": {"cron": "*/30 * * * *"}
    },
    {
      "id": "query_videos",
      "type": "postgres",
      "name": "Get Recent Videos",
      "parameters": {
        "query": "SELECT * FROM published_videos WHERE published_at > NOW() - INTERVAL '24 hours' AND status = 'active'"
      }
    },
    {
      "id": "scrape_metrics",
      "type": "httpRequest",
      "name": "Scrape Current Metrics",
      "parameters": {
        "url": "http://social-scraper:8005/scrape_metrics",
        "method": "POST",
        "body": {"video_id": "={{$json.video_id}}"}
      }
    },
    {
      "id": "ml_strategy",
      "type": "httpRequest",
      "name": "ML: Calculate Strategy",
      "parameters": {
        "url": "http://ml-core:8000/engagement_strategy",
        "method": "POST",
        "body": {
          "video_id": "={{$json.video_id}}",
          "current_metrics": "={{$json.metrics}}"
        }
      }
    },
    {
      "id": "if_boost",
      "type": "if",
      "name": "Should Boost?",
      "parameters": {
        "conditions": {
          "boolean": [{"value1": "={{$json.should_boost}}", "value2": true}]
        }
      }
    },
    {
      "id": "execute_bot",
      "type": "httpRequest",
      "name": "Execute Bot Actions",
      "parameters": {
        "url": "http://bot-engine:8006/execute_engagement",
        "method": "POST",
        "body": {
          "video_id": "={{$json.video_id}}",
          "target_likes": "={{$json.recommended_likes}}",
          "accounts_pool": "={{$json.affinity_accounts}}"
        }
      }
    },
    {
      "id": "update_db",
      "type": "postgres",
      "name": "Update Database",
      "parameters": {
        "operation": "update",
        "table": "published_videos",
        "where": "video_id = ={{$json.video_id}}",
        "set": {
          "last_boost_at": "NOW()",
          "total_bot_likes": "total_bot_likes + ={{$json.likes_given}}"
        }
      }
    }
  ]
}
```

### Workflow 3: Acquisition Tracker

```json
{
  "name": "Daily Acquisition Tracker",
  "nodes": [
    {
      "id": "trigger",
      "type": "schedule",
      "name": "Daily at 3 AM",
      "parameters": {"cron": "0 3 * * *"}
    },
    {
      "id": "query_accounts",
      "type": "postgres",
      "name": "Get All Accounts",
      "parameters": {
        "query": "SELECT * FROM fanpage_accounts WHERE status = 'active'"
      }
    },
    {
      "id": "scrape_followers",
      "type": "httpRequest",
      "name": "Scrape Followers",
      "parameters": {
        "url": "http://social-scraper:8005/get_followers",
        "method": "POST",
        "body": {"account_id": "={{$json.account_id}}"}
      }
    },
    {
      "id": "calculate_growth",
      "type": "code",
      "name": "Calculate Growth",
      "parameters": {
        "code": `
const prev = $input.first().json.followers_yesterday;
const curr = $input.first().json.followers_today;
const growth = curr - prev;
return {
  account_id: $input.first().json.account_id,
  growth: growth,
  growth_rate: (growth / prev * 100).toFixed(2)
};
        `
      }
    },
    {
      "id": "save_growth",
      "type": "postgres",
      "name": "Save Growth Metrics",
      "parameters": {
        "operation": "insert",
        "table": "follower_growth",
        "columns": "account_id, date, growth, growth_rate"
      }
    },
    {
      "id": "calculate_cac",
      "type": "code",
      "name": "Calculate CAC",
      "parameters": {
        "code": `
const budget = 150;
const totalGrowth = $input.all().reduce((sum, item) => sum + item.json.growth, 0);
const cac = (budget / totalGrowth).toFixed(2);
return {
  total_growth: totalGrowth,
  cost_per_acquisition: cac,
  month: new Date().toISOString().slice(0, 7)
};
        `
      }
    },
    {
      "id": "update_sheets",
      "type": "googleSheets",
      "name": "Update Dashboard",
      "parameters": {
        "operation": "append",
        "sheetId": "={{$credentials.spreadsheetId}}",
        "range": "Acquisition!A:E"
      }
    },
    {
      "id": "notify",
      "type": "discord",
      "name": "Daily Report",
      "parameters": {
        "content": "📈 Growth: ={{$json.total_growth}} | CAC: $={{$json.cost_per_acquisition}}"
      }
    }
  ]
}
```

---

## 🚀 PLAN DE IMPLEMENTACIÓN

### Fase 1: Core Services (1 semana)

```bash
# Día 1-2: Content Generation
docker build -f docker/Dockerfile.content-generator -t tiktok-content-gen .
docker build -f docker/Dockerfile.video-processor -t tiktok-video-proc .

# Día 3-4: Scraping & Engagement
docker build -f docker/Dockerfile.scraper -t tiktok-scraper .
docker build -f docker/Dockerfile.bot-engine -t tiktok-bot .

# Día 5: Integration Testing
docker-compose -f docker-compose-fanpage-full.yml up -d
./test_content_pipeline.sh

# Día 6-7: n8n Workflows
# Importar workflows a n8n
# Testear end-to-end pipeline
```

### Fase 2: Optimization (1 semana)

```bash
# Día 1-3: ML Model Training
# Entrenar con data real de primeros videos
# Afinar quality predictor

# Día 4-5: Bot Humanization
# Afinar delays y patrones
# Implementar affinity matrix real

# Día 6-7: Monitoring & Alerts
# Configurar Grafana dashboards
# Configurar alertas de shadowban
```

### Fase 3: Scaling (Ongoing)

```bash
# Agregar más cuentas gradualmente
# 10 → 20 → 30 → 60 cuentas

# Expandir a más plataformas
# TikTok → Instagram → YouTube Shorts

# Optimizar costs
# Migrar a VPS más grande si necesario
```

---

## 💰 COSTOS PROYECTADOS

### Infraestructura Cloud

```yaml
OPCIÓN A: DigitalOcean Droplet
  - 4 vCPU, 8GB RAM, 160GB SSD: $48/mes
  - Backup automático: $9.60/mes
  - Total: ~$58/mes

OPCIÓN B: AWS (con savings plan)
  - t3.large: ~$50/mes
  - EBS 100GB: ~$10/mes
  - Total: ~$60/mes

OPCIÓN C: Hetzner (más barato)
  - CX31 (2 vCPU, 8GB): ~$10/mes EUR = $11/mes
  - Total: ~$11/mes 🔥 MEJOR PRECIO
```

### APIs y Tools

```yaml
Runway Gen-4:
  - $0.05 per second
  - 5 videos x 2s x 4 daily batches = 40s/día
  - 40s x 30 días x $0.05 = $60/mes

GoLogin:
  - Plan Professional: $49/mes (100 profiles)
  
Proxies:
  - SmartProxy: $75/mes (5GB rotating)
  
Google Sheets API:
  - Gratis

Discord Webhooks:
  - Gratis

TOTAL APIs: ~$184/mes
```

### Total Mensual

```
VPS: $11-60/mes
APIs: $184/mes
TOTAL: $195-244/mes

ROI Esperado:
- 3,560 followers/mes × $0.30 CAC = Break-even
- Streams orgánicos → +$194/mes (Spotify)
- Profit desde mes 2-3
```

---

## ✅ RESPUESTA FINAL

### ¿Está el Docker en Cloud preparado?

**RESPUESTA: 60% Preparado, 40% por Implementar**

#### **LO QUE YA FUNCIONA (Listo para 24/7):**
✅ ML Core con YOLOv8 y predictores
✅ Database + Redis stack
✅ Health monitoring y auto-restart
✅ Meta Ads integration
✅ Device Farm base (activable)
✅ Dashboard de control

#### **LO QUE NECESITAS AGREGAR:**
❌ Content Generator (Runway API)
❌ Video Processor (FFmpeg)
❌ Social Scraper (métricas)
❌ Bot Engine (engagement)
❌ n8n workflows completos
❌ Publishing Coordinator
❌ Acquisition Tracker

#### **TIEMPO ESTIMADO IMPLEMENTACIÓN:**
- **Core funcional:** 1 semana
- **Optimización:** 1 semana
- **Production-ready:** 2-3 semanas

#### **RECOMENDACIÓN:**

1. **Inmediato:** Usa Docker actual para testear ML + Meta Ads
2. **Semana 1:** Implementa Content Pipeline (Generator + Processor)
3. **Semana 2:** Agrega Scraper + Bot Engine + n8n workflows
4. **Semana 3:** Scaling y optimization

**Deploy en VPS Hetzner ($11/mes) + APIs ($184/mes) = $195/mes total**

¿Quieres que implemente los servicios faltantes o prefieres empezar con un MVP reducido?
