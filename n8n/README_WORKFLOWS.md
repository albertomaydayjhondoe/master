# 🚀 N8N Workflow Orchestration - Stakas MVP

Workflows de automatización para el canal **UCgohgqLVu1QPdfa64Vkrgeg** (Stakas MVP) con presupuesto de €500/mes en Meta Ads.

## 📋 Workflows Disponibles

### 1. 📊 **Stakas Channel Monitor** (`stakas_channel_monitor.json`)
**Propósito**: Monitoreo automático cada 2 horas del canal de YouTube con optimización ML.

**Funcionalidades**:
- ✅ Analytics del canal UCgohgqLVu1QPdfa64Vkrgeg cada 2 horas
- ✅ Análisis de videos recientes y detección de patrones virales 
- ✅ Métricas de rendimiento y progreso hacia 10K suscriptores
- ✅ Auto-optimización de Meta Ads basada en performance
- ✅ Almacenamiento en PostgreSQL de métricas históricas
- ✅ Notificaciones Discord con resúmenes de analytics

**Trigger**: Cron job cada 2 horas
**APIs**: YouTube Data API v3, Meta Graph API, PostgreSQL, Discord Webhook

### 2. 🎬 **Viral Content Generator** (`viral_content_generator.json`)
**Propósito**: Generación de contenido viral optimizado para drill/rap español.

**Funcionalidades**:
- ✅ Generador de ideas de contenido viral (freestyle, behind scenes, reactions)
- ✅ Optimización automática de Meta Ads con targeting ES+LATAM
- ✅ Scripts de video generados por IA con guidelines específicas
- ✅ Boost automático para contenido con +80% potencial viral
- ✅ Integración con GitHub Actions para pipeline de viral boost
- ✅ Logging completo en PostgreSQL

**Trigger**: Webhook `/webhook/viral-content`
**APIs**: Meta Graph API, GitHub Actions API, PostgreSQL, Discord Webhook

### 3. 🔧 **Stakas Launch Orchestrator** (`stakas_launch_orchestrator.json`)
**Propósito**: Orquestador principal del sistema completo.

**Funcionalidades**:
- ✅ Triggers de GitHub Actions para deployment automático
- ✅ Coordinación entre todos los workflows
- ✅ Monitoreo de health checks del sistema
- ✅ Deployment en Railway con configuración automática

## 🔧 Configuración Requerida

### Credentials Necesarias en n8n:

#### 1. **YouTube API Key** (`youtube_api_key`)
```json
{
  "key": "AIzaSyC..."
}
```

#### 2. **Meta Ads API** (`meta_ads_api`) 
```json
{
  "access_token": "EAAGm0PX...",
  "account_id": "act_123456789"
}
```

#### 3. **Stakas PostgreSQL** (`stakas_postgres_db`)
```json
{
  "host": "postgres",
  "port": 5432,
  "database": "stakas_n8n",
  "user": "stakas_user", 
  "password": "StakasN8N2024!"
}
```

#### 4. **GitHub Token** (`github_token`)
```json
{
  "token": "ghp_xxxxxxxxxxxx"
}
```

#### 5. **Stakas Discord Webhook** (`stakas_discord_webhook`)
```json
{
  "webhookUrl": "https://discord.com/api/webhooks/..."
}
```

## 🚀 Deployment

### 1. Levantar n8n con PostgreSQL y Redis:
```bash
docker-compose -f docker-compose.n8n.yml up -d
```

### 2. Acceder a n8n:
```
http://localhost:5678
```
**Usuario**: `stakas_admin`  
**Password**: `StakasN8N2024!`

### 3. Importar workflows:
1. Ir a **Workflows** → **Import from File**
2. Importar cada archivo `.json` de la carpeta `n8n/workflows/`
3. Configurar credentials en **Settings** → **Credentials**

### 4. Activar workflows:
- ✅ **Stakas Channel Monitor**: Se ejecuta automáticamente cada 2 horas
- ✅ **Viral Content Generator**: Webhook disponible en `/webhook/viral-content`
- ✅ **Launch Orchestrator**: Webhook disponible en `/webhook/stakas-launch`

## 📊 Métricas y Monitoreo

### Dashboard de Analytics:
- **Subscribers**: Progreso hacia meta de 10K
- **Views per Video**: Promedio y tendencias
- **Viral Score**: Potencial viral de contenido reciente
- **Meta Ads Performance**: ROI y métricas de campañas

### Notificaciones Discord:
- 📊 Analytics updates cada 2 horas
- 🎬 Nuevas ideas de contenido viral generadas
- 🚀 Boost campaigns activadas para contenido +80% viral
- ⚠️ Alertas de performance y optimizaciones

### Base de Datos:
```sql
-- Tablas creadas automáticamente
CREATE TABLE channel_analytics (
  id SERIAL PRIMARY KEY,
  channel_id VARCHAR(50),
  subscribers INTEGER,
  total_views BIGINT,
  video_count INTEGER,
  avg_views_per_video INTEGER,
  recommendations_count INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE viral_content_log (
  id SERIAL PRIMARY KEY,
  channel_id VARCHAR(50),
  content_type VARCHAR(100),
  title TEXT,
  viral_potential INTEGER,
  meta_budget INTEGER,
  hashtags TEXT[],
  created_at TIMESTAMP DEFAULT NOW(),
  campaign_status VARCHAR(50)
);
```

## 🎯 Estrategia Meta Ads

### Presupuesto €500/mes distribuido:
- **España**: €150 (30%) - Targeting drill español + Real Madrid/Barcelona
- **LATAM**: €200 (40%) - México, Argentina, Colombia + Latin Trap
- **Lookalike**: €150 (30%) - 2% lookalike de video viewers 75%

### Objetivos de Campaña:
- **Primary**: VIDEO_VIEWS (ThruPlay 75%)
- **CPM Esperado**: €2-4
- **Reach Estimado**: 50K-75K usuarios únicos/semana
- **Conversión a Subs**: 2-3% de viewers

## 🔗 Webhooks Disponibles

### Para activar workflows externamente:

#### Generar Contenido Viral:
```bash
curl -X POST http://localhost:5678/webhook/viral-content \
  -H "Content-Type: application/json" \
  -d '{"trigger": "manual", "content_type": "freestyle"}'
```

#### Launch del Sistema:
```bash
curl -X POST http://localhost:5678/webhook/stakas-launch \
  -H "Content-Type: application/json" \
  -d '{"action": "full_deploy", "environment": "production"}'
```

---

## 🎵 Especialización Drill/Rap Español

### Keywords Virales Detectados:
- `vida en el barrio`, `struggle real`, `dinero fácil`, `loyalty squad`
- `trap life`, `drill español`, `calle respect`, `hustle mode`

### Hashtags de Alto Engagement:
- `#DrillEspañol`, `#TrapSpain`, `#BarrioLife`, `#RealRap`
- `#SpanishDrill`, `#StreetMusic`, `#RapEspañol`

### Horarios Peak España:
- **Weekdays**: 19:00, 20:30, 22:00
- **Weekends**: 15:00, 17:30, 20:00, 21:30

**🎯 Meta**: Canal UCgohgqLVu1QPdfa64Vkrgeg de 0 a 10K subs con contenido drill auténtico y €500/mes en Meta Ads optimizados por ML.**