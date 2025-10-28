# 🚀 Stakas MVP - Docker Deployment Instructions

## 📋 Overview
Sistema completo dockerizado para el canal Stakas MVP (UCgohgqLVu1QPdfa64Vkrgeg) con deployment automático a Railway vía GitHub Actions.

## 🏗️ Architecture
- **Base Image**: Python 3.11-slim
- **Framework**: Streamlit para dashboard
- **Platform**: Railway hosting
- **CI/CD**: GitHub Actions
- **Registry**: Docker Hub

## ⚡ Quick Deployment

### 1. GitHub Secrets Setup
Configura estos secrets en GitHub (Settings > Secrets and Variables > Actions):

```
DOCKERHUB_USERNAME=tu_usuario_dockerhub
DOCKERHUB_TOKEN=tu_access_token_dockerhub
RAILWAY_TOKEN=tu_railway_token
DISCORD_WEBHOOK_URL=tu_discord_webhook (opcional)
```

### 2. Automatic Deployment
El sistema se despliega automáticamente en cada push a `main`:

```bash
git add .
git commit -m "feat: deploy stakas mvp system"
git push origin main
```

### 3. Manual Deployment
También puedes triggerar deployment manualmente:
- Ve a Actions tab en GitHub
- Selecciona "Build & Deploy Stakas MVP to Railway"  
- Click "Run workflow"
- Select branch y marque "Deploy to Railway"

## 🐳 Docker Configuration

### Image Details
- **Name**: `stakasmvp/viral-system:latest`
- **Platforms**: linux/amd64, linux/arm64
- **Size**: ~800MB optimizada
- **Port**: 8080
- **Health Check**: `/health` endpoint

### Environment Variables
```env
# Core
CHANNEL_ID=UCgohgqLVu1TPdfa64Vkrgeg
META_ADS_BUDGET=500
ENVIRONMENT=production
PORT=8080
DUMMY_MODE=false

# Optional
DISCORD_WEBHOOK_URL=tu_webhook
META_ACCESS_TOKEN=tu_token
YOUTUBE_API_KEY=tu_key
```

## 🚂 Railway Deployment

### Service Configuration
Railway detectará automáticamente:
- Dockerfile para build
- Puerto 8080
- Health checks en `/health`
- Variables de entorno desde railway.json

### Domain & SSL
Railway proporcionará automáticamente:
- Dominio público: `https://stakas-mvp-production.up.railway.app`
- Certificado SSL gratuito
- CDN global

## 📊 Monitoring

### Health Checks
- **Endpoint**: `/health`
- **Interval**: 30 segundos
- **Timeout**: 10 segundos
- **Retries**: 3

### Logs
```bash
# Ver logs en Railway dashboard o CLI
railway logs --follow
```

### Metrics
El sistema incluye endpoints para monitoreo:
- `/health` - Estado del sistema
- `/metrics` - Métricas Prometheus (si configurado)
- `/channel/stats` - Estadísticas del canal

## 🎯 Channel-Specific Config

### Stakas MVP Settings
```yaml
channel_id: UCgohgqLVu1QPdfa64Vkrgeg
channel_name: "Stakas MVP"
genre: drill_rap_espanol
target_audience:
  age_range: "16-28"
  locations: ["ES", "AR", "MX", "CO"]
  interests: ["drill", "rap", "musica_urbana"]
budget_monthly: 500  # EUR
peak_hours: ["19:00", "20:30", "21:00"]  # Europe/Madrid
```

## 🛠️ Troubleshooting

### Common Issues

**Build Failures:**
```bash
# Check GitHub Actions logs
# Verify Dockerfile syntax
# Ensure requirements.txt is complete
```

**Deploy Failures:**
```bash
# Verify RAILWAY_TOKEN is valid
# Check Railway service limits
# Verify Docker image was pushed to hub
```

**Runtime Errors:**
```bash
# Check Railway logs
# Verify environment variables
# Check port configuration (must be 8080)
```

### Debug Commands
```bash
# Test locally (si Docker funciona)
docker run -p 8080:8080 -e DUMMY_MODE=true stakasmvp/viral-system:latest

# Check health
curl http://localhost:8080/health

# View logs
docker logs container_name
```

## 📈 Performance

### Expected Resources
- **CPU**: 0.5-1 vCPU
- **Memory**: 512MB-1GB RAM
- **Storage**: 1GB (app + logs)
- **Bandwidth**: 5GB/month

### Scaling
Railway auto-escala basado en:
- CPU usage >80%
- Memory usage >85%  
- Response time >2s
- Request queue depth

## 🎉 Success Indicators

Deployment exitoso cuando:
1. ✅ GitHub Actions build pasa
2. ✅ Docker image se sube a Docker Hub  
3. ✅ Railway deployment completa
4. ✅ Health check responde 200 OK
5. ✅ Dashboard accesible públicamente

**URL Final**: El sistema estará disponible en la URL que proporcione Railway, típicamente:
`https://stakas-mvp-production-[random].up.railway.app`

## 🎵 Ready for Viral!

Una vez desplegado, el sistema estará 24/7 optimizando:
- 📺 Canal UCgohgqLVu1QPdfa64Vkrgeg  
- 💰 €500/month Meta Ads budget
- 🎯 Drill/Rap Español audience
- 📈 Viral content predictions
- 🤖 ML-driven optimizations