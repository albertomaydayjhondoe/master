
# 🚀 Guía de Deployment Railway - Stakas MVP Viral System

## Prerequisitos

1. **Cuenta Railway**: Crear cuenta en [railway.app](https://railway.app)
2. **Git**: Tener el código en un repositorio Git
3. **APIs**: Configurar credenciales de APIs necesarias

## Deployment Automático

### Opción 1: Script Automático
```bash
python railway_deployment_scripts.py
```

### Opción 2: Manual

1. **Instalar Railway CLI**:
   ```bash
   # Windows (PowerShell)
   iwr https://railway.app/install.ps1 | iex
   
   # Mac/Linux
   curl -fsSL https://railway.app/install.sh | sh
   ```

2. **Login**:
   ```bash
   railway login
   ```

3. **Crear Proyecto**:
   ```bash
   railway create stakas-mvp-viral-system
   ```

4. **Configurar Variables de Entorno**:
   ```bash
   railway variables set ENVIRONMENT=production
   railway variables set PORT=8080
   railway variables set YOUTUBE_CHANNEL_ID=UCgohgqLVu1QPdfa64Vkrgeg
   # ... (ver railway.env.template para lista completa)
   ```

5. **Deploy**:
   ```bash
   railway up
   ```

## Configuración de APIs

### Meta Ads API
1. Crear app en [developers.facebook.com](https://developers.facebook.com)
2. Obtener: `META_ACCESS_TOKEN`, `META_APP_ID`, `META_APP_SECRET`
3. Configurar en Railway variables

### YouTube API
1. Crear proyecto en [Google Cloud Console](https://console.cloud.google.com)
2. Habilitar YouTube Data API v3
3. Obtener API key y OAuth credentials

### TikTok API
1. Registrarse en [TikTok for Developers](https://developers.tiktok.com)
2. Crear app y obtener client credentials

## Monitoreo

- **Dashboard Principal**: `https://[tu-app].railway.app`
- **Health Check**: `https://[tu-app].railway.app/health`
- **Logs**: `railway logs`
- **Status**: `railway status`

## Troubleshooting

### Build Fails
- Verificar `Dockerfile.railway`
- Revisar `requirements.txt`
- Comprobar `railway.json`

### Variables de Entorno
- Usar `railway variables` para verificar
- Verificar sintaxis de variables

### Performance Issues
- Monitorear logs con `railway logs`
- Verificar métricas de CPU/memoria
- Ajustar configuración de workers

## Comandos Útiles

```bash
# Ver todas las variables
railway variables

# Abrir dashboard de Railway
railway open

# Ver deployments
railway deployments

# Conectar a shell
railway shell

# Backup de variables
railway variables list > variables_backup.txt
```
