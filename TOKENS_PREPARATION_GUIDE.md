🔑 GUÍA COMPLETA DE CONFIGURACIÓN - TOKENS DE PRODUCCIÓN
======================================================

## 🎯 **INFORMACIÓN NECESARIA PARA ESTAR PREPARADO**

Antes de ejecutar el configurador, ten lista la siguiente información:

### **1. 🎯 META ADS API (OBLIGATORIO)**

#### **Qué necesitas:**
- App ID de Meta Business
- App Secret de Meta Business  
- Long-lived User Access Token

#### **Cómo obtenerlos:**
1. **Crear Meta App**:
   - Ve a: https://developers.facebook.com/
   - Click "Create App" → "Business"
   - Completa información básica

2. **Obtener App ID y Secret**:
   - Ve a Settings → Basic
   - Copia "App ID" y "App Secret"

3. **Generar Access Token**:
   - Ve a Tools → Graph API Explorer
   - Selecciona tu app
   - Genera User Access Token
   - Permisos necesarios: `ads_management`, `ads_read`, `business_management`

4. **Convertir a Long-lived**:
   - Ve a Tools → Access Token Debugger
   - Pega tu token y click "Debug"
   - Click "Extend Access Token"

#### **Formatos esperados:**
```bash
META_ACCESS_TOKEN=EAAG...     # Empieza con EAAG
META_APP_ID=123456789012345   # 15-20 dígitos
META_APP_SECRET=abcd1234...   # 32 caracteres hexadecimales
```

### **2. 📺 YOUTUBE DATA API v3**

#### **Qué necesitas:**
- Client ID OAuth 2.0
- Client Secret OAuth 2.0
- Refresh Token

#### **Cómo obtenerlos:**
1. **Google Cloud Console**:
   - Ve a: https://console.cloud.google.com/
   - Crea proyecto o selecciona existente

2. **Habilitar API**:
   - Ve a APIs & Services → Library
   - Busca "YouTube Data API v3"
   - Click "Enable"

3. **Crear Credenciales**:
   - Ve a APIs & Services → Credentials
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Tipo: "Desktop application"
   - Descarga JSON

4. **Obtener Refresh Token**:
   - Usa OAuth 2.0 Playground: https://developers.google.com/oauthplayground/
   - Autoriza scopes: `https://www.googleapis.com/auth/youtube`
   - Intercambia authorization code por tokens

#### **Formatos esperados:**
```bash
YOUTUBE_CLIENT_ID=123...apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=GOCSPX-...
YOUTUBE_REFRESH_TOKEN=1//...
```

### **3. 💬 TELEGRAM BOT API**

#### **Qué necesitas:**
- Bot Token
- API ID
- API Hash

#### **Cómo obtenerlos:**
1. **Bot Token**:
   - Habla con @BotFather en Telegram
   - Comando: `/newbot`
   - Sigue instrucciones
   - Copia token generado

2. **API ID y Hash**:
   - Ve a: https://my.telegram.org/
   - Login con tu número de teléfono
   - Ve a "API development tools"
   - Crea nueva aplicación
   - Copia API ID y API Hash

#### **Formatos esperados:**
```bash
TELEGRAM_BOT_TOKEN=1234567890:AABBcc...  # Número:Token
TELEGRAM_API_ID=12345678                 # 7-8 dígitos
TELEGRAM_API_HASH=abcd1234...            # 32 caracteres hex
```

### **4. 🎭 GOLOGIN (OPCIONAL)**

#### **Para qué sirve:**
- Automatización avanzada con perfiles de navegador
- Bypass de detección anti-bot
- Múltiples identidades virtuales

#### **Cómo obtenerlo:**
1. Registrate en: https://gologin.com/
2. Ve a Settings → API
3. Copia API Token

### **5. 🔄 N8N WORKFLOWS**

#### **Configuración automática:**
- Se configura automáticamente para localhost
- API Key es opcional (para N8N en la nube)

## 🚀 **EJECUCIÓN DEL CONFIGURADOR**

### **Paso 1: Preparar información**
Ten listos TODOS los tokens arriba mencionados

### **Paso 2: Ejecutar configurador**
```bash
./setup_production_tokens.sh
```

### **Paso 3: Validar configuración**
```bash
./validate_tokens.sh
```

### **Paso 4: Iniciar sistema**
```bash
./start_trap_production.py
```

## 📋 **CHECKLIST PRE-CONFIGURACIÓN**

### **✅ Meta Ads**
- [ ] App creada en Meta Developer
- [ ] App ID obtenido
- [ ] App Secret obtenido  
- [ ] Long-lived Access Token generado
- [ ] Permisos ads_management configurados

### **✅ YouTube**
- [ ] Proyecto Google Cloud creado
- [ ] YouTube Data API v3 habilitada
- [ ] Credenciales OAuth 2.0 creadas
- [ ] Client ID y Secret obtenidos
- [ ] Refresh Token generado

### **✅ Telegram**
- [ ] Bot creado con @BotFather
- [ ] Bot Token obtenido
- [ ] App registrada en my.telegram.org
- [ ] API ID y Hash obtenidos

### **✅ Sistema**
- [ ] Ultralytics instalado (`pip install ultralytics`)
- [ ] Dependencias principales instaladas
- [ ] Puertos 7860, 8501, 8000 disponibles

## ⚠️ **ADVERTENCIAS IMPORTANTES**

### **🔒 Seguridad**
- **NUNCA** compartas tokens en repositorios públicos
- Usa `.env` files que están en `.gitignore`
- Rota tokens regularmente
- Usa tokens con permisos mínimos necesarios

### **💰 Costos**
- **Meta Ads**: Cobrará por campañas reales
- **YouTube**: API gratuita hasta 10,000 requests/día
- **Telegram**: Completamente gratuito
- **GoLogin**: Servicio de pago

### **🚫 Limitaciones**
- **Meta**: Rate limits estrictos
- **YouTube**: Quotas diarias
- **Telegram**: Anti-spam automático

## 🎵 **¡LISTO PARA VIRAL!**

Una vez configurado, tendrás acceso completo a:
- 🔴 **Dashboard de control** (puerto 7860)
- 📊 **Analytics ML** (puerto 8501)
- 🤖 **Campañas automáticas** Meta Ads
- 📺 **Upload automático** YouTube
- 💬 **Community management** Telegram

¡Tu sistema estará listo para crear contenido trap viral! 🎵🔥