# 🔐 Configuración Manual de GitHub Secrets

## 📍 URL Directo para Configurar Secrets
https://github.com/albertomaydayjhondoe/master/settings/secrets/actions

## 🔑 Secrets a Configurar

### 1. DOCKERHUB_USERNAME
- **Name**: `DOCKERHUB_USERNAME`
- **Value**: `agora90`

### 2. DOCKERHUB_TOKEN
- **Name**: `DOCKERHUB_TOKEN`
- **Value**: [Obtén tu token siguiendo estos pasos]

**Cómo obtener Docker Hub Token:**
1. Ve a https://hub.docker.com/
2. Login con tu cuenta `agora90`
3. Click en tu perfil (esquina superior derecha) → Account Settings
4. En el sidebar izquierdo → Security
5. Click "New Access Token"
6. **Token Description**: `GitHub Actions Stakas MVP`
7. **Access permissions**: Read, Write, Delete
8. Click "Generate"
9. **COPIA EL TOKEN** (solo se muestra una vez)

### 3. RAILWAY_TOKEN
- **Name**: `RAILWAY_TOKEN`
- **Value**: [Obtén tu token siguiendo estos pasos]

**Cómo obtener Railway Token:**
1. Ve a https://railway.app
2. Login (usa "Login with GitHub" para facilitar)
3. Click en tu perfil → Account Settings
4. Scroll down a la sección "Tokens"
5. Click "Create Token"
6. **Description**: `GitHub Actions Deploy`
7. Click "Create"
8. **COPIA EL TOKEN**

### 4. DISCORD_WEBHOOK_URL (OPCIONAL)
- **Name**: `DISCORD_WEBHOOK_URL`
- **Value**: [Solo si quieres notificaciones Discord]

**Cómo crear Discord Webhook:**
1. Ve a tu servidor Discord
2. Settings del servidor → Integrations
3. Webhooks → New Webhook
4. **Name**: `Stakas MVP Deployments`
5. **Channel**: #general (o el que prefieras)
6. Copy Webhook URL

## 📋 Pasos en GitHub

1. **Abrir Secrets Page**:
   ```
   https://github.com/albertomaydayjhondoe/master/settings/secrets/actions
   ```

2. **Para cada secret**:
   - Click "New repository secret"
   - Pega exactamente el **Name** y **Value**
   - Click "Add secret"

3. **Orden recomendado**:
   ```
   1. DOCKERHUB_USERNAME = agora90
   2. DOCKERHUB_TOKEN = [tu_token_dockerhub]
   3. RAILWAY_TOKEN = [tu_token_railway]
   4. DISCORD_WEBHOOK_URL = [opcional]
   ```

## 🚀 Después de Configurar Secrets

### Opción A: Deployment Automático
El sistema ya se desplegará automáticamente porque hicimos push a `main`.

### Opción B: Trigger Manual
1. Ve a: https://github.com/albertomaydayjhondoe/master/actions
2. Click en workflow "Build & Deploy Stakas MVP to Railway"
3. Click "Run workflow"
4. Select "main" branch
5. Marca "Deploy to Railway": true
6. Click "Run workflow"

## 📊 Monitoreo del Deployment

### GitHub Actions
- URL: https://github.com/albertomaydayjhondoe/master/actions
- El workflow tardará ~5-10 minutos
- Verás progress en tiempo real

### Fases del Deployment:
1. **🏗️ Build**: Construir imagen Docker
2. **🔒 Security**: Escanear vulnerabilidades  
3. **📦 Push**: Subir a Docker Hub como `agora90/stakas-mvp:latest`
4. **🚂 Deploy**: Desplegar en Railway
5. **✅ Success**: URL pública disponible

## 🎯 Resultado Final

Una vez completado tendrás:
- **Docker Image**: `agora90/stakas-mvp:latest` en Docker Hub
- **Railway App**: URL pública automática
- **Monitoreo**: Health checks cada 30s
- **Auto-deploy**: En cada push a main

## 🎵 Stakas MVP Configuración

```yaml
Canal: UCgohgqLVu1QPdfa64Vkrgeg
Artista: Stakas MVP
Género: Drill/Rap Español
Budget: €500/month Meta Ads
Target: España + LATAM, 16-28 años
Platform: Railway 24/7
```

## ⚠️ Troubleshooting

**Si el workflow falla:**
- Verifica que los tokens sean válidos
- Revisa que Railway esté conectado con GitHub
- Check logs en GitHub Actions

**Si Railway no despliega:**
- Crea proyecto Railway manualmente desde GitHub repo
- Conecta el repositorio `albertomaydayjhondoe/master`
- Railway detectará Dockerfile automáticamente

¡Una vez configurados los secrets, el sistema estará 100% automatizado! 🚀