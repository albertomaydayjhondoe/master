# 🎬 Configuración de Credentials N8N - Stakas MVP

Este documento detalla la configuración completa de credentials necesarias para los workflows de n8n del canal **UCgohgqLVu1QPdfa64Vkrgeg**.

## 📋 Credentials Requeridas

### 1. 🎥 **YouTube Data API v3** 
**ID**: `youtube_api_key`  
**Type**: `Google API`

#### Configuración:
```json
{
  "name": "YouTube API Key - Stakas MVP",
  "type": "googleApi",
  "data": {
    "apiKey": "AIzaSyC_TU_API_KEY_AQUI"
  }
}
```

#### Cómo obtener:
1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear/seleccionar proyecto
3. Habilitar **YouTube Data API v3**
4. Crear **API Key** en Credentials
5. Restringir a YouTube Data API v3

---

### 2. 📱 **Meta Ads API** 
**ID**: `meta_ads_api`  
**Type**: `HTTP Header Auth`

#### Configuración:
```json
{
  "name": "Meta Ads API - Stakas MVP",
  "type": "httpHeaderAuth",
  "data": {
    "name": "Authorization",
    "value": "Bearer EAAGm0PX_TU_ACCESS_TOKEN_AQUI"
  }
}
```

#### Variables adicionales requeridas:
- **Account ID**: `act_123456789` (en los workflows como `{{ $credentials.meta_ads.account_id }}`)

#### Cómo obtener:
1. Ir a [Meta Developers](https://developers.facebook.com/)
2. Crear App → Business → Ads Management
3. Generar **Access Token** con permisos: `ads_management`, `ads_read`
4. Obtener **Account ID** de Business Manager

---

### 3. 🐘 **PostgreSQL Database**
**ID**: `stakas_postgres_db`  
**Type**: `Postgres`

#### Configuración:
```json
{
  "name": "Stakas PostgreSQL Database",
  "type": "postgres", 
  "data": {
    "host": "postgres",
    "port": 5432,
    "database": "stakas_n8n",
    "user": "stakas_user",
    "password": "StakasN8N2024!",
    "ssl": false
  }
}
```

#### Tablas auto-creadas:
```sql
-- Analytics del canal
CREATE TABLE IF NOT EXISTS channel_analytics (
  id SERIAL PRIMARY KEY,
  channel_id VARCHAR(50) NOT NULL,
  subscribers INTEGER DEFAULT 0,
  total_views BIGINT DEFAULT 0,
  video_count INTEGER DEFAULT 0,
  avg_views_per_video INTEGER DEFAULT 0,
  recommendations_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Log de contenido viral 
CREATE TABLE IF NOT EXISTS viral_content_log (
  id SERIAL PRIMARY KEY,
  channel_id VARCHAR(50) NOT NULL,
  content_type VARCHAR(100),
  title TEXT,
  viral_potential INTEGER DEFAULT 0,
  meta_budget INTEGER DEFAULT 0,
  hashtags TEXT[],
  campaign_status VARCHAR(50) DEFAULT 'created',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Métricas de Meta Ads
CREATE TABLE IF NOT EXISTS meta_ads_metrics (
  id SERIAL PRIMARY KEY,
  campaign_id VARCHAR(100),
  campaign_name TEXT,
  spend DECIMAL(10,2) DEFAULT 0,
  impressions INTEGER DEFAULT 0,
  clicks INTEGER DEFAULT 0,
  video_views INTEGER DEFAULT 0,
  cpm DECIMAL(10,2) DEFAULT 0,
  date_start DATE,
  date_stop DATE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 4. 🐙 **GitHub Token**
**ID**: `github_token`  
**Type**: `HTTP Header Auth`

#### Configuración:
```json
{
  "name": "GitHub Personal Access Token",
  "type": "httpHeaderAuth",
  "data": {
    "name": "Authorization", 
    "value": "Bearer ghp_TU_GITHUB_TOKEN_AQUI"
  }
}
```

#### Permisos requeridos:
- ✅ `repo` (Full repository access)
- ✅ `workflow` (Update GitHub Action workflows)
- ✅ `actions:write` (Trigger workflow runs)

#### Cómo obtener:
1. GitHub → Settings → Developer settings
2. Personal access tokens → Tokens (classic)
3. Generate new token con permisos arriba
4. Copiar token (se muestra solo una vez)

---

### 5. 💬 **Discord Webhook**
**ID**: `stakas_discord_webhook`  
**Type**: `Discord Webhook`

#### Configuración:
```json
{
  "name": "Stakas MVP Discord Notifications",
  "type": "discordWebhookApi",
  "data": {
    "webhookUrl": "https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN"
  }
}
```

#### Cómo obtener:
1. Discord Server → Server Settings → Integrations
2. Create Webhook → Choose channel
3. Copy Webhook URL
4. Test con: `curl -X POST "WEBHOOK_URL" -H "Content-Type: application/json" -d '{"content":"Test desde n8n"}'`

---

## 🔧 Configuración en n8n

### Paso 1: Acceder a Credentials
1. Abrir n8n: `http://localhost:5678`
2. Login: `stakas_admin` / `StakasN8N2024!`
3. Ir a **Settings** → **Credentials**

### Paso 2: Crear cada Credential
Para cada credential arriba:

1. Click **Add Credential**
2. Seleccionar el **Type** correspondiente
3. Completar los datos según la configuración
4. **Save** y **Test connection** (si está disponible)

### Paso 3: Verificar en Workflows
Los workflows referencian las credentials por ID:
- `{{ $credentials.youtube_api_key.apiKey }}`
- `{{ $credentials.meta_ads_api.account_id }}`
- `{{ $credentials.stakas_postgres_db.host }}`
- etc.

---

## 🧪 Testing de Credentials

### Test YouTube API:
```bash
curl "https://www.googleapis.com/youtube/v3/channels?part=statistics&id=UCgohgqLVu1QPdfa64Vkrgeg&key=TU_API_KEY"
```

### Test Meta Ads API:
```bash
curl "https://graph.facebook.com/v18.0/me/adaccounts" \
  -H "Authorization: Bearer TU_ACCESS_TOKEN"
```

### Test PostgreSQL:
```bash
# Desde container n8n
psql -h postgres -U stakas_user -d stakas_n8n
```

### Test Discord Webhook:
```bash
curl -X POST "TU_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content": "🚀 Test desde Stakas MVP n8n workflows!"}'
```

### Test GitHub API:
```bash
curl -H "Authorization: Bearer TU_GITHUB_TOKEN" \
  "https://api.github.com/user"
```

---

## ⚠️ Seguridad y Mejores Prácticas

### 🔒 Tokens y Keys:
- **NUNCA** commitear tokens/keys en Git
- Usar **environment variables** para desarrollo local
- Rotar tokens periódicamente (cada 3-6 meses)
- Restringir permisos al mínimo necesario

### 🌐 Network Security:
- PostgreSQL solo accesible desde containers de n8n
- Webhooks con URLs secretas/tokens
- Rate limiting en APIs externas

### 📝 Logging:
- **NO** logear tokens completos
- Logs de errores sin credenciales sensibles
- Monitoring de uso de APIs para detectar anomalías

### 🔄 Backup:
- Backup regular de base de datos PostgreSQL
- Export periódico de workflows n8n
- Documentar recovery procedures

---

## 🚨 Troubleshooting Común

### ❌ **YouTube API Error 403**:
- Verificar que API está habilitada en Google Cloud
- Comprobar cuotas/límites diarios
- Validar restricciones de API Key

### ❌ **Meta Ads Error 190**:
- Access token expirado → regenerar token
- Verificar permisos de la App
- Comprobar Account ID correcto

### ❌ **PostgreSQL Connection Failed**:
- Verificar que containers están en misma network
- Comprobar credenciales de BD
- Validar que PostgreSQL está running

### ❌ **Discord Webhook 401**:
- Verificar URL completa del webhook
- Comprobar que canal existe
- Test con Postman/curl primero

### ❌ **GitHub Actions 401**:
- Token con permisos insuficientes
- Verificar scope de `repo` y `workflow`
- Comprobar que repo es correcto

---

**🎯 Una vez configuradas todas las credentials, los workflows de Stakas MVP estarán listos para automatizar completamente el canal UCgohgqLVu1QPdfa64Vkrgeg con €500/mes en Meta Ads optimizados por ML.**