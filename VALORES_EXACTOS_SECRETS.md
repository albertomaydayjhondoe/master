# 🔐 VALORES EXACTOS PARA GITHUB SECRETS

## 📍 URL para configurar:
https://github.com/albertomaydayjhondoe/master/settings/secrets/actions

## 🔑 Secrets a configurar (COPIAR EXACTAMENTE):

### 1. DOCKERHUB_USERNAME
```
Name: DOCKERHUB_USERNAME
Value: agora90
```

### 2. DOCKERHUB_TOKEN  
```
Name: DOCKERHUB_TOKEN
Value: dckr_pat_W1iWIosKBkESIHmkZ3piRLyGNWk
```

### 3. RAILWAY_TOKEN
```
Name: RAILWAY_TOKEN
Value: [NECESITAS OBTENER ESTE DE RAILWAY.APP]
```

**Para obtener Railway Token:**
1. Ve a https://railway.app
2. Login with GitHub
3. Account Settings → Tokens
4. Create Token → Name: "GitHub Actions Deploy"
5. Copia el token generado

### 4. DISCORD_WEBHOOK_URL (OPCIONAL)
```
Name: DISCORD_WEBHOOK_URL  
Value: [opcional - solo si quieres notificaciones Discord]
```

## 🚀 Pasos para configurar:

1. **Ve a GitHub Secrets**: https://github.com/albertomaydayjhondoe/master/settings/secrets/actions

2. **Click "New repository secret"** para cada uno:
   - Pega el **Name** exacto
   - Pega el **Value** exacto
   - Click "Add secret"

3. **Obtén Railway Token**:
   - Ve a railway.app 
   - Login with GitHub
   - Crea token como se indica arriba

4. **Verificar configuración**:
   - Una vez configurados los 3 secrets principales
   - Ve a GitHub Actions para ver el deployment

## ⚡ Deployment Automático

Una vez configurados los secrets:
- ✅ GitHub Actions se ejecutará automáticamente
- ✅ Docker build: `agora90/stakas-mvp:latest` 
- ✅ Railway deployment automático
- ✅ URL pública disponible en ~10 minutos

## 📊 Monitoreo:
- **GitHub Actions**: https://github.com/albertomaydayjhondoe/master/actions
- **Railway Dashboard**: https://railway.app/dashboard

¡El sistema Stakas MVP estará corriendo 24/7 para viral content! 🎵🚀