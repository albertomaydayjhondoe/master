#!/usr/bin/env python3
"""
Guía Completa de Railway Deployment - Método Alternativo
Para deployment sin Railway CLI
"""

def create_web_deployment_guide():
    """Crear guía de deployment via web (sin CLI)"""
    
    guide_content = """
# 🚀 DEPLOYMENT RAILWAY - MÉTODO WEB (SIN CLI)

## OPCIÓN ALTERNATIVA - DEPLOYMENT VIA WEB INTERFACE

Ya que el Railway CLI presenta problemas, aquí está la guía completa para deployment via web:

## 📋 PASO 1: PREPARAR REPOSITORIO GITHUB

### 1.1 Subir código a GitHub
```bash
git add .
git commit -m "Stakas MVP Viral System - Railway Ready"
git push origin main
```

### 1.2 Verificar archivos clave en el repositorio:
- ✅ `railway_main.py` (aplicación principal)
- ✅ `Dockerfile.railway` (Docker configuration)
- ✅ `railway.json` (Railway configuration)  
- ✅ `requirements.txt` + `requirements-railway.txt`
- ✅ `RAILWAY_READY.md` (documentación)

## 📋 PASO 2: CREAR PROYECTO EN RAILWAY

### 2.1 Ir a Railway.app
1. Abrir [railway.app](https://railway.app)
2. Crear cuenta o hacer login
3. Click "New Project"

### 2.2 Conectar GitHub Repository
1. Seleccionar "Deploy from GitHub repo"
2. Autorizar Railway en GitHub
3. Seleccionar tu repositorio `master`
4. Branch: `completo`

### 2.3 Configurar Build
Railway detectará automáticamente:
- ✅ `Dockerfile.railway`
- ✅ `railway.json`

## 📋 PASO 3: CONFIGURAR VARIABLES DE ENTORNO

En Railway Dashboard → Settings → Variables:

### Variables Básicas (OBLIGATORIAS):
```
ENVIRONMENT=production
PORT=8080
STREAMLIT_SERVER_PORT=8080
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
YOUTUBE_CHANNEL_ID=UCgohgqLVu1QPdfa64Vkrgeg
CHANNEL_NAME=Stakas MVP
DUMMY_MODE=false
LOG_LEVEL=INFO
AUTO_RESTART=true
ENABLE_MONITORING=true
```

### Variables APIs (Configurar cuando tengas las credenciales):
```
META_ACCESS_TOKEN=tu_token_aqui
META_APP_ID=tu_app_id_aqui
META_APP_SECRET=tu_app_secret_aqui
YOUTUBE_API_KEY=tu_youtube_api_key_aqui
TIKTOK_CLIENT_KEY=tu_tiktok_key_aqui
INSTAGRAM_ACCESS_TOKEN=tu_instagram_token_aqui
TWITTER_API_KEY=tu_twitter_key_aqui
OPENAI_API_KEY=tu_openai_key_aqui
```

## 📋 PASO 4: DEPLOYMENT

### 4.1 Iniciar Deployment
1. En Railway Dashboard
2. Click "Deploy"
3. Railway construirá automáticamente usando `Dockerfile.railway`

### 4.2 Monitorear Build
- Ver logs en tiempo real
- Verificar que no hay errores
- Build típico: 3-5 minutos

### 4.3 Obtener URL
- Railway asignará URL automáticamente
- Formato: `https://[proyecto-id].railway.app`
- Guardar esta URL para acceso

## 📋 PASO 5: VERIFICACIÓN POST-DEPLOYMENT

### 5.1 Health Checks
- Ir a: `https://[tu-url].railway.app/health`
- Debe mostrar: `{"status": "healthy"}`

### 5.2 Dashboard Principal
- Ir a: `https://[tu-url].railway.app`
- Debe cargar dashboard Stakas MVP

### 5.3 API Status
- Ir a: `https://[tu-url].railway.app/api/status`
- Debe mostrar info del canal

## 🔧 CONFIGURACIÓN ADICIONAL

### Custom Domain (Opcional)
1. En Railway: Settings → Domains
2. Agregar dominio personalizado
3. Configurar DNS records

### Database (Si necesario)
1. Railway → Add Service → Database
2. Seleccionar PostgreSQL o Redis
3. Variables se crean automáticamente

### Alerts y Monitoring
1. Configurar webhook Discord/Slack:
```
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

## 🚨 TROUBLESHOOTING

### Build Fails
1. Verificar `Dockerfile.railway` syntax
2. Revisar `requirements.txt`
3. Comprobar logs de build

### App No Responde
1. Verificar variables de entorno
2. Ver logs: Railway Dashboard → View Logs
3. Verificar puerto 8080

### Performance Issues
1. Railway Dashboard → Metrics
2. Ver CPU/Memory usage
3. Ajustar configuración si necesario

## ⚡ COMANDOS ÚTILES (VIA WEB)

### Ver Logs
- Railway Dashboard → View Logs
- Filtrar por severidad
- Download logs para análisis

### Redeploy
- Railway Dashboard → Deploy
- O push cambios a GitHub (auto-deploy)

### Variables
- Settings → Variables
- Add/Edit/Delete variables
- Restart automático tras cambios

## 📊 MÉTRICAS Y MONITORING

### CPU/Memory
- Railway Dashboard → Metrics
- Gráficos en tiempo real
- Alertas automáticas si >90%

### Logs Structured
- Logs automáticos en Railway
- Retention: 7 días (plan gratuito)
- Upgrade para más retention

## 🎯 RESULTADO FINAL

Una vez completado tendrás:

✅ **Aplicación 24/7 online**
- URL: `https://[tu-proyecto].railway.app`

✅ **Dashboard Completo**
- Monitoreo Stakas MVP
- Control Meta Ads  
- Analytics en tiempo real

✅ **Health Monitoring**
- Auto-restart en fallos
- Alertas automáticas
- Performance optimization

✅ **Sistema Automatizado**
- 6 subsistemas activos
- ML optimization continua
- Cross-platform sync

## 💰 ACTIVACIÓN META ADS

Una vez online:
1. Configurar credenciales Meta Ads en variables
2. Activar campaña €500/mes
3. Sistema detecta automáticamente
4. Todos los subsistemas se activan
5. ROI 60-180% proyectado

## 📱 ACCESO PERMANENTE

- **Dashboard**: `https://[tu-url].railway.app`
- **Health**: `https://[tu-url].railway.app/health`
- **API**: `https://[tu-url].railway.app/api/status`
- **Railway Console**: [railway.app/dashboard](https://railway.app/dashboard)

---

# 🎉 ¡SISTEMA LISTO PARA OPERAR 24/7!

Tu **Stakas MVP Viral System** estará completamente operativo y monitoreando el canal automáticamente.

**¡Solo faltan las credenciales de APIs para activar Meta Ads y comenzar el crecimiento viral!**
"""
    
    return guide_content

def main():
    """Crear todas las guías necesarias"""
    
    print("🚀 CREANDO GUÍA COMPLETA DE RAILWAY DEPLOYMENT")
    print("=" * 60)
    
    # Crear guía web
    web_guide = create_web_deployment_guide()
    
    with open('RAILWAY_WEB_DEPLOYMENT.md', 'w', encoding='utf-8') as f:
        f.write(web_guide)
    
    print("✅ Guía creada: RAILWAY_WEB_DEPLOYMENT.md")
    
    # Crear checklist rápido
    checklist = """
# ✅ CHECKLIST RÁPIDO - RAILWAY DEPLOYMENT

## Pre-Deployment
- [ ] Código subido a GitHub
- [ ] Cuenta Railway creada
- [ ] Repositorio público/accesible

## Deployment
- [ ] Proyecto creado en Railway
- [ ] GitHub repo conectado
- [ ] Variables básicas configuradas
- [ ] Build completado exitosamente
- [ ] URL asignada y accesible

## Post-Deployment  
- [ ] Health check funciona: `/health`
- [ ] Dashboard carga: `/`
- [ ] API responde: `/api/status`
- [ ] Logs sin errores críticos

## APIs (Cuando estén listas)
- [ ] Meta Ads credentials configuradas
- [ ] YouTube API key añadida  
- [ ] TikTok API configurada
- [ ] Instagram tokens activos
- [ ] Twitter API funcionando

## Activación Final
- [ ] Meta Ads campaign €500/mes activada
- [ ] Sistema detecta automáticamente
- [ ] 6 subsistemas operativos
- [ ] Monitoreo 24/7 activo
- [ ] Crecimiento viral iniciado

## ✅ ESTADO: LISTO PARA RAILWAY
Sistema preparado para deployment inmediato via web interface.
"""
    
    with open('RAILWAY_CHECKLIST.md', 'w', encoding='utf-8') as f:
        f.write(checklist)
    
    print("✅ Checklist creado: RAILWAY_CHECKLIST.md")
    
    # Resumen de archivos
    files_summary = """
# 📁 ARCHIVOS RAILWAY - RESUMEN COMPLETO

## Configuración Core
- `railway.json` - Configuración Railway
- `Dockerfile.railway` - Container optimizado  
- `railway_main.py` - App web principal
- `production_optimizer.py` - Monitoring 24/7

## Deployment
- `railway_deployment_scripts.py` - Scripts automáticos
- `RAILWAY_WEB_DEPLOYMENT.md` - Guía web deployment
- `RAILWAY_DEPLOYMENT_GUIDE.md` - Guía CLI original
- `RAILWAY_CHECKLIST.md` - Checklist rápido
- `RAILWAY_READY.md` - Resumen completo

## Configuración
- `railway.env.template` - Variables de entorno
- `requirements-railway.txt` - Dependencias adicionales

## 🎯 MÉTODO RECOMENDADO
Usar `RAILWAY_WEB_DEPLOYMENT.md` para deployment via web interface.
"""
    
    with open('RAILWAY_FILES_SUMMARY.md', 'w', encoding='utf-8') as f:
        f.write(files_summary)
    
    print("✅ Resumen creado: RAILWAY_FILES_SUMMARY.md")
    
    print("\n" + "=" * 60)
    print("🎉 ¡TODAS LAS GUÍAS RAILWAY CREADAS!")
    print("=" * 60)
    
    print("\n📋 ARCHIVOS DISPONIBLES:")
    print("  📄 RAILWAY_WEB_DEPLOYMENT.md - Guía principal (SIN CLI)")
    print("  📄 RAILWAY_DEPLOYMENT_GUIDE.md - Guía CLI original") 
    print("  ✅ RAILWAY_CHECKLIST.md - Checklist rápido")
    print("  📋 RAILWAY_READY.md - Documentación completa")
    print("  📁 RAILWAY_FILES_SUMMARY.md - Resumen archivos")
    
    print("\n🚀 PRÓXIMO PASO:")
    print("  1. Leer RAILWAY_WEB_DEPLOYMENT.md")
    print("  2. Subir código a GitHub")  
    print("  3. Crear proyecto en railway.app")
    print("  4. Conectar repositorio GitHub")
    print("  5. Configurar variables básicas")
    print("  6. ¡Deploy automático!")
    
    print("\n🎯 RESULTADO:")
    print("  ✅ Sistema Stakas MVP online 24/7")
    print("  ✅ Dashboard web completo")
    print("  ✅ Monitoreo automático")
    print("  ✅ Listo para Meta Ads €500/mes")

if __name__ == "__main__":
    main()