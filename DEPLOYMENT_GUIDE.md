# 🚀 TikTok ML System v4 - Scripts de Deployment

Este directorio contiene los scripts interactivos para el deployment completo del TikTok ML System v4.

## 📋 Scripts Disponibles

### 1. 🎯 **Deployment Interactivo Completo**

#### Windows PowerShell:
```powershell
.\deploy-v4-interactive.ps1
```

#### Linux/Mac Bash:
```bash
chmod +x deploy-v4-interactive.sh
./deploy-v4-interactive.sh
```

**Características:**
- ✅ Verificación automática de prerequisitos
- 🔧 Configuración guiada paso a paso
- 🔐 Input seguro de credenciales (con masking)
- 🐳 Múltiples opciones de deployment (Docker local, Railway, Docker Compose)
- 🩺 Health checks automáticos
- 🧪 Testing de endpoints
- 📊 Resumen completo de deployment

### 2. ⚡ **Quick Launch** (Desarrollo Rápido)

```powershell
# Desarrollo local básico
.\quick-launch-v4.ps1

# Con modo producción
.\quick-launch-v4.ps1 -Production

# En puerto específico
.\quick-launch-v4.ps1 -Port 9000

# Sin rebuild (si imagen ya existe)
.\quick-launch-v4.ps1 -SkipBuild
```

**Características:**
- 🏃 Deployment en segundos
- 🧪 Configuración mínima automática
- 🔄 Ideal para desarrollo iterativo
- 📝 .env automático con valores dummy

## 🎛️ Opciones de Deployment

### 1. 🐳 **Docker Local**
- **Uso**: Desarrollo y testing
- **Puertos**: 8000 (API)
- **Recursos**: Minimal
- **Configuración**: Automática

### 2. ☁️ **Docker Compose Completo**  
- **Uso**: Producción local con servicios completos
- **Puertos**: 8000 (API), 5678 (n8n), 8080 (Traefik)
- **Servicios**: API + n8n + Traefik + Volúmenes persistentes
- **SSL**: Configuración Traefik automática

### 3. 🚀 **Railway Cloud**
- **Uso**: Producción en la nube
- **Escalabilidad**: Automática
- **SSL**: Incluido
- **Configuración**: Variables de entorno en Railway

## 📋 Prerequisitos

### Sistema Base:
- ✅ **Docker** (v20+)
- ✅ **Docker Compose** (v2+)
- 🔧 **Git** (opcional)
- 💻 **PowerShell 5.1+** o **Bash 4+**

### Para Railway:
- 🌐 **Node.js** (para Railway CLI)
- 🔑 **Cuenta Railway** (railway.app)

### Para Producción:
- 🔐 **Credenciales Supabase** (requerido)
- 🎯 **Meta Ads API** (opcional)
- 🎥 **YouTube Data API** (opcional)
- 🎵 **Spotify Web API** (opcional)
- 🔄 **n8n Instance** (opcional)

## 🔧 Configuración Paso a Paso

### 1. **Preparación Inicial**
```bash
# Clonar repositorio (si no lo tienes)
git clone <repository-url>
cd master

# Verificar archivos necesarios
ls Dockerfile.v4 docker-compose.v4.yml requirements.txt
```

### 2. **Credenciales de Producción**

#### Supabase (Requerido):
1. Crear proyecto en [supabase.com](https://supabase.com)
2. Obtener URL del proyecto
3. Ir a Settings > API > Obtener keys

#### Meta Ads API (Opcional):
1. Crear app en [developers.facebook.com](https://developers.facebook.com)
2. Habilitar Marketing API
3. Generar long-lived access token
4. Configurar Meta Pixel

#### YouTube API (Opcional):
1. Proyecto en [Google Cloud Console](https://console.cloud.google.com)
2. Habilitar YouTube Data API v3
3. Crear API Key
4. Obtener Channel IDs

#### Spotify API (Opcional):
1. App en [Spotify Developer Dashboard](https://developer.spotify.com)
2. Obtener Client ID y Secret
3. Encontrar Artist IDs y Playlist IDs

### 3. **Ejecutar Deployment**

#### Desarrollo Rápido:
```powershell
# Deployment inmediato con configuración dummy
.\quick-launch-v4.ps1
```

#### Producción Completa:
```powershell
# Script interactivo completo
.\deploy-v4-interactive.ps1
```

## 🌐 URLs de Acceso Post-Deployment

### Docker Local:
- 🏠 **API Principal**: http://localhost:8000
- 📖 **Documentación**: http://localhost:8000/docs
- 🩺 **Health Check**: http://localhost:8000/health

### Docker Compose:
- 🏠 **API Principal**: http://localhost:8000
- 📖 **Documentación**: http://localhost:8000/docs
- 🔄 **n8n Workflows**: http://localhost:5678
- 📊 **Traefik Dashboard**: http://localhost:8080

### Railway:
- 🌐 **URL Dinámica**: https://tu-app.railway.app
- 📖 **Documentación**: https://tu-app.railway.app/docs

## 🛠️ Comandos de Gestión

### Docker Local:
```bash
# Ver logs en tiempo real
docker logs tiktok-ml-v4-quick -f

# Reiniciar servicio
docker restart tiktok-ml-v4-quick

# Parar servicio
docker stop tiktok-ml-v4-quick

# Estado del contenedor
docker ps | grep tiktok-ml
```

### Docker Compose:
```bash
# Ver logs todos los servicios
docker-compose -f docker-compose.v4.yml logs -f

# Reiniciar stack completo
docker-compose -f docker-compose.v4.yml restart

# Parar stack
docker-compose -f docker-compose.v4.yml down

# Estado de servicios
docker-compose -f docker-compose.v4.yml ps
```

### Railway:
```bash
# Ver logs
railway logs

# Estado del deployment
railway status

# Redeploy
railway up --detach

# Variables de entorno
railway variables
```

## 🚨 Troubleshooting

### Error: Docker no encontrado
```bash
# Windows: Instalar Docker Desktop
# Linux: sudo apt install docker.io docker-compose
# Mac: brew install docker docker-compose
```

### Error: Puerto ocupado
```powershell
# Cambiar puerto en quick launch
.\quick-launch-v4.ps1 -Port 9000
```

### Error: Credenciales inválidas
```bash
# Verificar .env generado
cat .env | grep -E "(SUPABASE|META|YOUTUBE|SPOTIFY)"

# Re-ejecutar script con nuevas credenciales
.\deploy-v4-interactive.ps1
```

### Error: Health check falla
```bash
# Verificar logs del contenedor
docker logs tiktok-ml-v4-quick --tail 50

# Verificar que el puerto esté libre
netstat -an | findstr 8000  # Windows
ss -tulpn | grep 8000       # Linux
```

### Error: Railway CLI
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Verificar conexión
railway whoami
```

## 📊 Monitoring y Logs

### Métricas del Sistema:
- 🩺 **Health Endpoint**: `/health`
- 📈 **Metrics**: Prometheus compatible
- 📊 **Analytics**: Supabase dashboard
- 🔍 **Logs**: Structured JSON logging

### Alertas Automáticas:
- 🚨 API response time > 5s
- 💾 Memory usage > 80%
- 🔄 Health check failures
- 🌐 External API failures

## 🔐 Seguridad

### Variables Sensibles:
- 🔑 API keys masked en logs
- 🔐 .env con permisos restrictivos
- 🛡️ Contenedores non-root
- 🌐 CORS configurado

### Mejores Prácticas:
- 🔄 Rotar API keys regularmente
- 🔒 Usar HTTPS en producción
- 📊 Monitorear logs de seguridad
- 🚫 No commitear .env al repo

## 🎯 Próximos Pasos

Después de un deployment exitoso:

1. **🔧 Configurar n8n workflows** (si se desplegó)
2. **🧪 Probar endpoints** en `/docs`
3. **📊 Verificar Supabase** dashboard
4. **🎯 Configurar Meta Ads** campaigns
5. **🔒 Configurar SSL** para producción
6. **📈 Setup monitoring** y alertas
7. **🔄 Configurar CI/CD** para updates

---

## 💡 Tips Adicionales

### Desarrollo Local:
- Usa `quick-launch-v4.ps1` para iteración rápida
- El modo desarrollo usa valores dummy seguros
- Hot-reload disponible montando código como volumen

### Producción:
- Usa el script interactivo completo para primera vez
- Guarda backup de .env generado
- Configura monitoring desde el primer día
- Planifica estrategia de updates

### Performance:
- Railway escala automáticamente
- Docker local limitar RAM si es necesario
- Usar Redis cache en Docker Compose para mejor rendimiento

¡Happy Deploying! 🚀