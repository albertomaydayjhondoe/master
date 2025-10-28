# 🚀 Docker Deployment Guide - Stakas ML Channel (UCgohgqLVu1QPdfa64Vkrgeg)

## 📋 Resumen del Sistema

Sistema de análisis ML para el canal Stakas MVP con presupuesto de €500/mes en Meta Ads, desplegado en Railway usando Docker con mejores prácticas de seguridad y CI/CD.

## 🏗️ Arquitectura Docker

### Multi-Stage Build
- **Base Stage**: Python 3.11-slim con dependencias del sistema
- **Dependencies Stage**: Instalación optimizada de paquetes Python
- **Security Stage**: Configuración de usuario no-root y permisos
- **Production Stage**: Imagen final optimizada para producción

### Características de Seguridad
- ✅ Usuario no-root (`stakas:1001`)
- ✅ Imagen base minimal (Python slim)
- ✅ Timezone configurado (Europe/Madrid) 
- ✅ Health checks integrados
- ✅ Secrets management via variables de entorno
- ✅ Scanning de vulnerabilidades con Trivy

## 🔧 Configuración de Deployment

### 1. Pre-requisitos

**Docker Hub Account:**
```bash
# Crear cuenta en https://hub.docker.com
# Generar Access Token en Security > Access Tokens
```

**GitHub Secrets (Settings > Secrets and variables > Actions):**
```
DOCKERHUB_USERNAME=tu_usuario_dockerhub
DOCKERHUB_TOKEN=tu_access_token
RAILWAY_TOKEN=tu_railway_token
DISCORD_WEBHOOK=tu_webhook_discord (opcional)
```

### 2. Build Local (Desarrollo)

```bash
# Build para testing local
docker build --target development -t stakas-ml:dev .

# Run con docker-compose
docker-compose -f docker-compose.production.yml up -d

# Testing del contenedor
docker run -p 8080:8080 -e DUMMY_MODE=true stakas-ml:dev
```

### 3. Build Manager Interactivo

```bash
python docker_build_manager.py
```

**Opciones disponibles:**
1. **Build Local** - Construir imagen localmente
2. **Test Image** - Probar imagen construida
3. **Push to Registry** - Subir a Docker Hub
4. **Railway Config** - Generar configuración Railway
5. **Full Pipeline** - Proceso completo automatizado

### 4. CI/CD Automatizado

**Trigger del Pipeline:**
```bash
git add .
git commit -m "feat: docker deployment ready"
git push origin main
```

**Pipeline GitHub Actions:**
1. 🔍 **build-and-test** - Build y test básico
2. 🛡️ **security-scan** - Scan con Trivy
3. 📦 **docker-build** - Build multi-platform (amd64/arm64)
4. 🔒 **docker-security** - Security scan de imagen final
5. 🚀 **deploy-railway** - Deploy automático a Railway
6. 📢 **notify** - Notificación Discord del resultado

## 🌐 Railway Configuration

### Variables de Entorno Requeridas

```env
# Core Configuration
ENVIRONMENT=production
DUMMY_MODE=false
CHANNEL_ID=UCgohgqLVu1QPdfa64Vkrgeg
PORT=8080
TZ=Europe/Madrid
PYTHONPATH=/app

# Meta Ads Configuration
META_ADS_BUDGET=500
META_ACCESS_TOKEN=tu_meta_token
META_APP_ID=tu_meta_app_id
META_APP_SECRET=tu_meta_secret

# Database Configuration (Railway auto-provisioned)
DATABASE_URL=${DATABASE_URL}
REDIS_URL=${REDIS_URL}

# Optional: Monitoring
DISCORD_WEBHOOK_URL=tu_webhook_url
```

### Servicios Railway Requeridos

1. **Main App** (Dockerfile deployment)
   - Plan: $5/month
   - Source: Docker Hub image
   - Port: 8080

2. **Redis** (Add-on)
   - Plan: $5/month  
   - Version: Redis 7

3. **PostgreSQL** (Add-on)
   - Plan: $5/month
   - Version: PostgreSQL 15

## 📊 Monitorización y Health Checks

### Health Check Endpoints

```bash
# Application health
curl https://tu-app.railway.app/health

# Metrics endpoint
curl https://tu-app.railway.app/metrics

# Channel status
curl https://tu-app.railway.app/channel/status
```

### Logs y Debugging

```bash
# Railway CLI logs (si instalado)
railway logs --follow

# Docker logs local
docker logs stakas-ml-api

# Container inspection
docker exec -it stakas-ml-api /bin/bash
```

## 🚀 Deployment Steps

### Opción A: Full Automated (Recomendado)

1. **Configurar GitHub Secrets**
   ```
   DOCKERHUB_USERNAME, DOCKERHUB_TOKEN, RAILWAY_TOKEN
   ```

2. **Push código a GitHub**
   ```bash
   git push origin main
   ```

3. **Monitorear GitHub Actions**
   - Ver progreso en Actions tab
   - Verificar build exitoso
   - Confirmar deployment a Railway

### Opción B: Manual Docker Build

1. **Build y Push**
   ```bash
   python docker_build_manager.py
   # Seleccionar opción 5: Full Pipeline
   ```

2. **Configurar Railway**
   - Crear nuevo proyecto en Railway
   - Conectar Docker Hub image
   - Añadir variables de entorno
   - Deploy

### Opción C: Local Testing Extensivo

```bash
# 1. Build local
docker build -t stakas-ml:test .

# 2. Test con compose
docker-compose -f docker-compose.production.yml up -d

# 3. Verificar endpoints
curl http://localhost:8080/health
curl http://localhost:8080/channel/UCgohgqLVu1QPdfa64Vkrgeg/stats

# 4. Push cuando esté listo
docker tag stakas-ml:test tu_usuario/stakas-ml:latest
docker push tu_usuario/stakas-ml:latest
```

## 🔒 Security Best Practices Implementadas

### Docker Security
- ✅ Non-root user execution
- ✅ Minimal base image (Python slim)
- ✅ Multi-stage builds para imagen final pequeña
- ✅ No secrets en Dockerfile
- ✅ Health checks para monitoring
- ✅ Read-only root filesystem cuando sea posible

### CI/CD Security
- ✅ Trivy vulnerability scanning
- ✅ Multi-platform builds
- ✅ Signed container images
- ✅ Secrets management via GitHub
- ✅ Automated security updates

### Runtime Security
- ✅ Environment variable injection
- ✅ Resource limits configurados
- ✅ Network segmentation con Railway
- ✅ Encrypted connections (HTTPS)
- ✅ Regular security scans

## 🎯 Channel-Specific Configuration

### Stakas MVP (UCgohgqLVu1QPdfa64Vkrgeg)
- **Género**: Drill/Rap Español
- **Videos**: 15 activos
- **Engagement**: Alto en demografía urbana 18-25
- **Budget**: €500/month Meta Ads
- **Target**: Madrid, Barcelona, Valencia
- **Horarios**: 20:00-23:00 peak engagement

### ML Model Configuration
```yaml
channel_config:
  id: "UCgohgqLVu1QPdfa64Vkrgeg"
  name: "Stakas MVP"
  genre: "drill_rap_espanol"
  target_demographics:
    - age_range: "18-25"
    - locations: ["Madrid", "Barcelona", "Valencia"]
    - interests: ["rap", "drill", "musica_urbana"]
  
ml_models:
  engagement_predictor: "yolo_engagement_v2.pt"
  content_analyzer: "content_analysis_v1.pt"
  posting_optimizer: "posting_time_v1.pt"
```

## 📈 Expected Performance

### Resource Usage
- **CPU**: 0.5-1.0 vCPU under normal load
- **Memory**: 512MB-1GB RAM  
- **Storage**: 2GB (models + logs)
- **Network**: 10GB/month outbound

### Scaling Triggers
- **CPU >80%** para >5min → Scale up
- **Memory >85%** → Scale up  
- **Response time >2s** → Scale up
- **Error rate >5%** → Alert + investigate

## 🏁 Resultado Final

Una vez desplegado tendrás:

1. **📱 App Web**: `https://tu-proyecto.railway.app`
2. **🤖 ML API**: Endpoints para análisis en tiempo real
3. **📊 Dashboard**: Métricas del canal Stakas MVP
4. **🔄 CI/CD**: Deploy automático en cada push
5. **📈 Analytics**: Tracking de €500 Meta Ads budget
6. **🛡️ Security**: Scanning y monitoreo continuo

**¡Sistema listo para generar contenido viral 24/7!** 🚀