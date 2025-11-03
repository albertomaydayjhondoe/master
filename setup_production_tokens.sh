#!/bin/bash
# 🎵 CONFIGURADOR DE TOKENS DE PRODUCCIÓN - DISCOGRÁFICA ML
# =========================================================
# Script interactivo para configurar todos los tokens necesarios

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Archivo de configuración
ENV_FILE=".env.production"

echo -e "${PURPLE}🎵 CONFIGURADOR DE TOKENS - DISCOGRÁFICA ML${NC}"
echo -e "${PURPLE}===========================================${NC}"
echo ""
echo -e "${BLUE}Este script te ayudará a configurar todos los tokens necesarios${NC}"
echo -e "${BLUE}para activar el modo producción completo del sistema.${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANTE: Ten listos todos los tokens antes de continuar${NC}"
echo ""

# Función para leer token con validación
read_token() {
    local token_name="$1"
    local description="$2"
    local validation_pattern="$3"
    local help_url="$4"
    
    echo -e "${GREEN}📝 Configurando: ${token_name}${NC}"
    echo -e "${BLUE}   ${description}${NC}"
    if [ ! -z "$help_url" ]; then
        echo -e "${YELLOW}   📖 Obtener en: ${help_url}${NC}"
    fi
    echo ""
    
    while true; do
        read -p "   Ingresa ${token_name}: " token_value
        
        if [ -z "$token_value" ]; then
            echo -e "${RED}   ❌ Token no puede estar vacío${NC}"
            continue
        fi
        
        if [ ! -z "$validation_pattern" ] && [[ ! $token_value =~ $validation_pattern ]]; then
            echo -e "${RED}   ❌ Formato de token inválido${NC}"
            echo -e "${YELLOW}   Expected pattern: ${validation_pattern}${NC}"
            continue
        fi
        
        echo -e "${GREEN}   ✅ Token configurado${NC}"
        echo ""
        echo "$token_name=$token_value" >> "$ENV_FILE"
        break
    done
}

# Función para mostrar ayuda detallada
show_help() {
    echo -e "${PURPLE}🔍 GUÍA DETALLADA DE TOKENS${NC}"
    echo -e "${PURPLE}===========================${NC}"
    echo ""
    
    echo -e "${GREEN}1. META ADS API TOKENS${NC}"
    echo -e "${BLUE}   Pasos para obtener:${NC}"
    echo -e "   • Ve a https://developers.facebook.com/"
    echo -e "   • Crea una nueva App (tipo Business)"
    echo -e "   • Ve a Settings > Basic → copia App ID y App Secret"
    echo -e "   • Ve a Tools > Graph API Explorer"
    echo -e "   • Selecciona tu app y genera User Access Token"
    echo -e "   • Usa Access Token Debugger para convertir a Long-lived"
    echo ""
    
    echo -e "${GREEN}2. YOUTUBE DATA API${NC}"
    echo -e "${BLUE}   Pasos para obtener:${NC}"
    echo -e "   • Ve a https://console.cloud.google.com/"
    echo -e "   • Crea proyecto nuevo o selecciona existente"
    echo -e "   • Habilita YouTube Data API v3"
    echo -e "   • Ve a Credentials > Create Credentials > OAuth 2.0"
    echo -e "   • Descarga JSON y usa OAuth2 flow para obtener tokens"
    echo ""
    
    echo -e "${GREEN}3. TELEGRAM BOT API${NC}"
    echo -e "${BLUE}   Pasos para obtener:${NC}"
    echo -e "   • Bot Token: Habla con @BotFather en Telegram"
    echo -e "   • API ID/Hash: Ve a https://my.telegram.org/"
    echo -e "   • Login con tu número y crea nueva aplicación"
    echo ""
    
    echo -e "${GREEN}4. LONGCAT-VIDEO${NC}"
    echo -e "${BLUE}   Generación automática de videos:${NC}"
    echo -e "   • Modelo open-source de 13.6B parámetros"
    echo -e "   • GPU recomendada pero no requerida"
    echo -e "   • Text-to-Video, Image-to-Video, Video Continuation"
    echo -e "   • Integrado automáticamente en campañas"
    echo ""
    
    echo -e "${GREEN}5. GOLOGIN (OPCIONAL)${NC}"
    echo -e "${BLUE}   Para automatización avanzada:${NC}"
    echo -e "   • Registrate en https://gologin.com/"
    echo -e "   • Ve a Settings > API → copia API Token"
    echo ""
}

# Preguntar si quiere ayuda
echo -e "${YELLOW}❓ ¿Necesitas ayuda para obtener los tokens? (y/N)${NC}"
read -p "   " show_help_choice
if [[ $show_help_choice =~ ^[Yy]$ ]]; then
    show_help
    echo ""
    echo -e "${BLUE}Presiona Enter para continuar con la configuración...${NC}"
    read
fi

# Crear archivo de configuración
echo -e "${BLUE}📁 Creando archivo de configuración: ${ENV_FILE}${NC}"
echo ""

# Header del archivo
cat > "$ENV_FILE" << EOF
# 🎵 DISCOGRÁFICA ML - CONFIGURACIÓN DE PRODUCCIÓN
# Generated: $(date)
# Sistema completamente configurado para producción

# Modo de operación
DUMMY_MODE=false
ML_PRODUCTION_MODE=true
TRAP_ARTIST_MODE=true

EOF

echo -e "${GREEN}✅ Archivo base creado${NC}"
echo ""

# 1. META ADS TOKENS
echo -e "${PURPLE}🎯 1. META ADS API CONFIGURATION${NC}"
echo -e "${PURPLE}================================${NC}"
read_token "META_ACCESS_TOKEN" "Long-lived User Access Token de Meta Business" "^EAAG.*" "https://developers.facebook.com/"
read_token "META_APP_ID" "Application ID de tu app Meta" "^[0-9]{15,20}$" ""
read_token "META_APP_SECRET" "Application Secret de tu app Meta" "^[a-f0-9]{32}$" ""

# 2. YOUTUBE TOKENS
echo -e "${PURPLE}📺 2. YOUTUBE DATA API CONFIGURATION${NC}"
echo -e "${PURPLE}====================================${NC}"
read_token "YOUTUBE_CLIENT_ID" "OAuth 2.0 Client ID" ".*\.apps\.googleusercontent\.com" "https://console.cloud.google.com/"
read_token "YOUTUBE_CLIENT_SECRET" "OAuth 2.0 Client Secret" "^GOCSPX-.*" ""
read_token "YOUTUBE_REFRESH_TOKEN" "OAuth 2.0 Refresh Token" "^1//.*" ""

# 3. TELEGRAM TOKENS
echo -e "${PURPLE}💬 3. TELEGRAM BOT API CONFIGURATION${NC}"
echo -e "${PURPLE}====================================${NC}"
read_token "TELEGRAM_BOT_TOKEN" "Bot Token de @BotFather" "^[0-9]{8,10}:[a-zA-Z0-9_-]{35}$" "@BotFather en Telegram"
read_token "TELEGRAM_API_ID" "API ID de my.telegram.org" "^[0-9]{7,8}$" "https://my.telegram.org/"
read_token "TELEGRAM_API_HASH" "API Hash de my.telegram.org" "^[a-f0-9]{32}$" ""

# 4. N8N CONFIGURATION
echo -e "${PURPLE}🔄 4. N8N WORKFLOWS CONFIGURATION${NC}"
echo -e "${PURPLE}=================================${NC}"
echo -e "${BLUE}Configurando N8N para workflows automáticos...${NC}"
echo ""

echo "# N8N Configuration" >> "$ENV_FILE"
echo "N8N_WEBHOOK_URL=http://localhost:5678" >> "$ENV_FILE"
echo "N8N_API_BASE_URL=http://localhost:5678/api/v1" >> "$ENV_FILE"

echo -e "${YELLOW}❓ ¿Tienes N8N API Key? (opcional) (y/N)${NC}"
read -p "   " has_n8n_key
if [[ $has_n8n_key =~ ^[Yy]$ ]]; then
    read_token "N8N_API_KEY" "N8N API Key (opcional)" "" ""
else
    echo "# N8N_API_KEY=tu_api_key_opcional" >> "$ENV_FILE"
fi

# 5. LONGCAT-VIDEO CONFIGURATION
echo -e "${PURPLE}🎬 5. LONGCAT-VIDEO CONFIGURATION${NC}"
echo -e "${PURPLE}=================================${NC}"
echo -e "${GREEN}Configurando generación de video automática...${NC}"
echo ""

echo "" >> "$ENV_FILE"
echo "# LongCat-Video Configuration" >> "$ENV_FILE"
echo "LONGCAT_VIDEO_ENABLED=true" >> "$ENV_FILE"
echo "LONGCAT_VIDEO_DEVICE=cuda" >> "$ENV_FILE"
echo "LONGCAT_VIDEO_RESOLUTION=720p" >> "$ENV_FILE"
echo "LONGCAT_VIDEO_OUTPUT_DIR=data/generated_videos" >> "$ENV_FILE"
echo "LONGCAT_VIDEO_MAX_CONCURRENT=3" >> "$ENV_FILE"

echo -e "${YELLOW}❓ ¿Tienes GPU NVIDIA para acelerar generación? (y/N)${NC}"
read -p "   " has_gpu
if [[ $has_gpu =~ ^[Yy]$ ]]; then
    echo "LONGCAT_VIDEO_DEVICE=cuda" >> "$ENV_FILE"
    echo -e "${GREEN}   ✅ GPU habilitada para generación rápida${NC}"
else
    echo "LONGCAT_VIDEO_DEVICE=cpu" >> "$ENV_FILE"
    echo -e "${YELLOW}   ⚠️  CPU mode - generación más lenta pero funcional${NC}"
fi

# 6. CONFIGURACIONES ADICIONALES
echo -e "${PURPLE}⚙️  6. CONFIGURACIONES ADICIONALES${NC}"
echo -e "${PURPLE}==================================${NC}"

echo "" >> "$ENV_FILE"
echo "# Configuraciones del sistema" >> "$ENV_FILE"
echo "GRADIO_SERVER_PORT=7860" >> "$ENV_FILE"
echo "STREAMLIT_SERVER_PORT=8501" >> "$ENV_FILE"
echo "ML_API_PORT=8000" >> "$ENV_FILE"
echo "" >> "$ENV_FILE"
echo "# Meta Ads Configuration" >> "$ENV_FILE"
echo "META_API_VERSION=v18.0" >> "$ENV_FILE"
echo "META_DAILY_BUDGET_LIMIT=100" >> "$ENV_FILE"
echo "META_AUTO_CAMPAIGN_CREATION=true" >> "$ENV_FILE"
echo "" >> "$ENV_FILE"

# GOLOGIN (OPCIONAL)
echo -e "${YELLOW}❓ ¿Quieres configurar GoLogin para automatización avanzada? (y/N)${NC}"
read -p "   " setup_gologin
if [[ $setup_gologin =~ ^[Yy]$ ]]; then
    echo -e "${PURPLE}🎭 GOLOGIN CONFIGURATION${NC}"
    echo -e "${PURPLE}=======================${NC}"
    read_token "GOLOGIN_API_TOKEN" "GoLogin API Token" "" "https://gologin.com/"
    echo "GOLOGIN_MAX_PROFILES=10" >> "$ENV_FILE"
    echo "GOLOGIN_ROTATION_ENABLED=true" >> "$ENV_FILE"
else
    echo "# GoLogin Configuration (opcional)" >> "$ENV_FILE"
    echo "# GOLOGIN_API_TOKEN=tu_gologin_token" >> "$ENV_FILE"
fi

# FINALIZACIÓN
echo ""
echo -e "${GREEN}🎉 CONFIGURACIÓN COMPLETADA${NC}"
echo -e "${GREEN}===========================${NC}"
echo ""
echo -e "${BLUE}📁 Archivo creado: ${ENV_FILE}${NC}"
echo -e "${BLUE}📊 Tokens configurados: $(grep -c "=" "$ENV_FILE" | grep -v "#")${NC}"
echo ""

# Verificar archivo
echo -e "${YELLOW}🔍 Verificando configuración...${NC}"
echo ""

if [ -f "$ENV_FILE" ]; then
    echo -e "${GREEN}✅ Archivo de configuración creado exitosamente${NC}"
    
    # Contar tokens configurados
    meta_tokens=$(grep -c "^META_.*=" "$ENV_FILE" || echo "0")
    youtube_tokens=$(grep -c "^YOUTUBE_.*=" "$ENV_FILE" || echo "0")
    telegram_tokens=$(grep -c "^TELEGRAM_.*=" "$ENV_FILE" || echo "0")
    
    echo -e "${BLUE}   📊 Meta Ads tokens: ${meta_tokens}/3${NC}"
    echo -e "${BLUE}   📺 YouTube tokens: ${youtube_tokens}/3${NC}"
    echo -e "${BLUE}   💬 Telegram tokens: ${telegram_tokens}/3${NC}"
    echo ""
    
    # Backup del archivo actual
    if [ -f ".env" ]; then
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
        echo -e "${YELLOW}📦 Backup creado: .env.backup.$(date +%Y%m%d_%H%M%S)${NC}"
    fi
    
    # Copiar configuración a .env principal
    cp "$ENV_FILE" ".env"
    echo -e "${GREEN}✅ Configuración activada en .env${NC}"
    echo ""
    
    # Instrucciones finales
    echo -e "${PURPLE}🚀 PRÓXIMOS PASOS${NC}"
    echo -e "${PURPLE}================${NC}"
    echo -e "${GREEN}1. Ejecutar sistema en modo producción:${NC}"
    echo -e "   ${BLUE}./start_trap_production.py${NC}"
    echo ""
    echo -e "${GREEN}2. Acceder a dashboards:${NC}"
    echo -e "   ${BLUE}🔴 Control: http://localhost:7860${NC}"
    echo -e "   ${BLUE}📊 Analytics: http://localhost:8501${NC}"
    echo ""
    echo -e "${GREEN}3. Verificar logs:${NC}"
    echo -e "   ${BLUE}tail -f logs/production_controller.log${NC}"
    echo -e "   ${BLUE}tail -f logs/analytics_engine.log${NC}"
    echo ""
    
    echo -e "${GREEN}🎵 ¡SISTEMA LISTO PARA CAMPAÑAS VIRALES! 🔥${NC}"
    
else
    echo -e "${RED}❌ Error creando archivo de configuración${NC}"
    exit 1
fi