#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════
# setup-credentials.sh - Interactive Credential Configuration
# ═══════════════════════════════════════════════════════════════════════════
#
# Configura credenciales para Docker V3 de forma interactiva
#
# Usage:
#   ./setup-credentials.sh
#
# ═══════════════════════════════════════════════════════════════════════════

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
banner() {
    echo -e "${BLUE}"
    echo "═══════════════════════════════════════════════════════════════"
    echo "  🔐 CONFIGURACIÓN DE CREDENCIALES - Docker V3"
    echo "  Sistema Completo Viral: Ultralytics + n8n + Meta Ads"
    echo "═══════════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if .env exists
check_env() {
    if [ -f .env ]; then
        log_warning ".env ya existe"
        read -p "¿Deseas sobrescribirlo? (yes/no): " overwrite
        if [ "$overwrite" != "yes" ]; then
            log_info "Saliendo sin cambios"
            exit 0
        fi
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
        log_success "Backup creado: .env.backup.*"
    fi
}

# Create .env from template
create_env() {
    if [ -f .env.v3 ]; then
        cp .env.v3 .env
        log_success ".env creado desde .env.v3"
    else
        log_error ".env.v3 no existe"
        exit 1
    fi
}

# Interactive credential input
configure_credentials() {
    echo ""
    log_info "════════════════════════════════════════════════════"
    log_info "  CONFIGURACIÓN INTERACTIVA DE CREDENCIALES"
    log_info "════════════════════════════════════════════════════"
    echo ""
    
    # Meta Ads
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}1. META ADS (Facebook/Instagram)${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Obtén tus credenciales en: https://business.facebook.com/settings/system-users"
    echo ""
    read -p "Meta Access Token (EAABsb...): " meta_token
    read -p "Meta Ad Account ID (act_123456789): " meta_account
    read -p "Meta Pixel ID (123456789012345): " meta_pixel
    
    if [ -n "$meta_token" ]; then
        sed -i "s|META_ACCESS_TOKEN=.*|META_ACCESS_TOKEN=$meta_token|g" .env
        log_success "Meta Access Token configurado"
    fi
    
    if [ -n "$meta_account" ]; then
        sed -i "s|META_AD_ACCOUNT_ID=.*|META_AD_ACCOUNT_ID=$meta_account|g" .env
        log_success "Meta Ad Account ID configurado"
    fi
    
    if [ -n "$meta_pixel" ]; then
        sed -i "s|META_PIXEL_ID=.*|META_PIXEL_ID=$meta_pixel|g" .env
        log_success "Meta Pixel ID configurado"
    fi
    
    # YouTube
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}2. YOUTUBE API${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Obtén tus credenciales en: https://console.cloud.google.com/apis/credentials"
    echo ""
    read -p "YouTube Client ID (xxx.apps.googleusercontent.com): " youtube_id
    read -p "YouTube Client Secret (GOCSPX-xxx): " youtube_secret
    read -p "YouTube Channel ID (UC_xxx): " youtube_channel
    
    if [ -n "$youtube_id" ]; then
        sed -i "s|YOUTUBE_CLIENT_ID=.*|YOUTUBE_CLIENT_ID=$youtube_id|g" .env
        log_success "YouTube Client ID configurado"
    fi
    
    if [ -n "$youtube_secret" ]; then
        sed -i "s|YOUTUBE_CLIENT_SECRET=.*|YOUTUBE_CLIENT_SECRET=$youtube_secret|g" .env
        log_success "YouTube Client Secret configurado"
    fi
    
    if [ -n "$youtube_channel" ]; then
        sed -i "s|YOUTUBE_CHANNEL_ID=.*|YOUTUBE_CHANNEL_ID=$youtube_channel|g" .env
        log_success "YouTube Channel ID configurado"
    fi
    
    # YouTube Artista Genérico (para Landing Pages Meta Ads)
    echo ""
    log_info "Credenciales del Artista Genérico (Landing Pages)"
    echo ""
    read -p "Nombre del Artista: " artist_name
    read -p "YouTube Channel del Artista (URL completa): " artist_channel_url
    read -p "Instagram Handle (@username): " artist_instagram
    read -p "TikTok Handle (@username): " artist_tiktok
    
    if [ -n "$artist_name" ]; then
        sed -i "s|ARTIST_NAME=.*|ARTIST_NAME=$artist_name|g" .env
        log_success "Nombre del artista configurado"
    fi
    
    if [ -n "$artist_channel_url" ]; then
        sed -i "s|ARTIST_YOUTUBE_CHANNEL=.*|ARTIST_YOUTUBE_CHANNEL=$artist_channel_url|g" .env
        log_success "YouTube Channel del artista configurado"
    fi
    
    if [ -n "$artist_instagram" ]; then
        sed -i "s|ARTIST_INSTAGRAM=.*|ARTIST_INSTAGRAM=$artist_instagram|g" .env
        log_success "Instagram del artista configurado"
    fi
    
    if [ -n "$artist_tiktok" ]; then
        sed -i "s|ARTIST_TIKTOK=.*|ARTIST_TIKTOK=$artist_tiktok|g" .env
        log_success "TikTok del artista configurado"
    fi
    
    # Runway ML
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}3. RUNWAY ML (Generación de Videos AI)${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    read -p "¿Configurar Runway ML? (y/n): " configure_runway
    
    if [ "$configure_runway" = "y" ]; then
        echo "Obtén tu API Key en: https://app.runwayml.com/settings/api"
        read -p "Runway API Key: " runway_key
        
        if [ -n "$runway_key" ]; then
            sed -i "s|RUNWAY_API_KEY=.*|RUNWAY_API_KEY=$runway_key|g" .env
            log_success "Runway API Key configurado"
        fi
    else
        log_info "Runway ML omitido (opcional)"
    fi
    
    # GoLogin (Optional)
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}4. GOLOGIN (Opcional - Browser Automation)${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    read -p "¿Configurar GoLogin? (y/n): " configure_gologin
    
    if [ "$configure_gologin" = "y" ]; then
        echo "Obtén tu API Key en: https://app.gologin.com/personalArea/TokenApi"
        read -p "GoLogin API Key: " gologin_key
        read -p "GoLogin Profile IDs (separados por coma): " gologin_profiles
        
        if [ -n "$gologin_key" ]; then
            sed -i "s|GOLOGIN_API_KEY=.*|GOLOGIN_API_KEY=$gologin_key|g" .env
            log_success "GoLogin API Key configurado"
        fi
        
        if [ -n "$gologin_profiles" ]; then
            sed -i "s|GOLOGIN_PROFILE_IDS=.*|GOLOGIN_PROFILE_IDS=$gologin_profiles|g" .env
            log_success "GoLogin Profiles configurados"
        fi
    else
        log_info "GoLogin omitido (opcional)"
    fi
    
    # n8n Webhooks
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}5. N8N WEBHOOKS (Automation Workflows)${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    log_info "n8n se configurará automáticamente en http://localhost:5678"
    log_info "Usuario por defecto: admin / viral_admin_2025"
    echo ""
    read -p "¿Deseas configurar webhook personalizado? (y/n): " configure_n8n_webhook
    
    if [ "$configure_n8n_webhook" = "y" ]; then
        read -p "Webhook URL personalizado (ej: https://n8n.tu-dominio.com): " n8n_webhook
        
        if [ -n "$n8n_webhook" ]; then
            sed -i "s|WEBHOOK_URL=.*|WEBHOOK_URL=$n8n_webhook|g" .env
            log_success "n8n Webhook URL configurado"
        fi
    else
        log_info "n8n usará URL local por defecto"
    fi
    
    # Telegram Bot (Optional)
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}6. TELEGRAM BOT (Opcional - Notificaciones)${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    read -p "¿Configurar Telegram Bot? (y/n): " configure_telegram
    
    if [ "$configure_telegram" = "y" ]; then
        echo "Crea un bot con @BotFather en Telegram"
        read -p "Telegram Bot Token (123456:ABC-DEF): " telegram_token
        read -p "Telegram Chat ID (123456789): " telegram_chat
        
        if [ -n "$telegram_token" ]; then
            sed -i "s|TELEGRAM_BOT_TOKEN=.*|TELEGRAM_BOT_TOKEN=$telegram_token|g" .env
            log_success "Telegram Bot Token configurado"
        fi
        
        if [ -n "$telegram_chat" ]; then
            sed -i "s|TELEGRAM_CHAT_ID=.*|TELEGRAM_CHAT_ID=$telegram_chat|g" .env
            log_success "Telegram Chat ID configurado"
        fi
    else
        log_info "Telegram Bot omitido (opcional)"
    fi
    
    # Database & Services (Keep defaults)
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}7. PASSWORDS (Seguridad)${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    log_warning "IMPORTANTE: Cambia estos passwords en PRODUCCIÓN"
    echo ""
    read -p "PostgreSQL Password [postgres123]: " postgres_pass
    read -p "n8n Password [viral_admin_2025]: " n8n_pass
    read -p "Grafana Password [viral_monitor_2025]: " grafana_pass
    
    postgres_pass=${postgres_pass:-postgres123}
    n8n_pass=${n8n_pass:-viral_admin_2025}
    grafana_pass=${grafana_pass:-viral_monitor_2025}
    
    sed -i "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$postgres_pass|g" .env
    sed -i "s|N8N_PASSWORD=.*|N8N_PASSWORD=$n8n_pass|g" .env
    sed -i "s|GRAFANA_PASSWORD=.*|GRAFANA_PASSWORD=$grafana_pass|g" .env
    
    log_success "Passwords configurados"
}

# Summary
show_summary() {
    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✅ CONFIGURACIÓN COMPLETADA${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
    echo ""
    log_success ".env configurado correctamente"
    echo ""
    echo "Credenciales configuradas:"
    echo ""
    
    # Check which credentials are set
    if grep -q "META_ACCESS_TOKEN=.*[^=]$" .env 2>/dev/null && ! grep -q "META_ACCESS_TOKEN=your_meta_access_token_here" .env; then
        echo "  ✅ Meta Ads"
    else
        echo "  ⚠️  Meta Ads (no configurado - OBLIGATORIO)"
    fi
    
    if grep -q "YOUTUBE_CLIENT_ID=.*[^=]$" .env 2>/dev/null && ! grep -q "YOUTUBE_CLIENT_ID=your_youtube_client_id_here" .env; then
        echo "  ✅ YouTube API"
    else
        echo "  ⚠️  YouTube API (no configurado - OBLIGATORIO)"
    fi
    
    if grep -q "GOLOGIN_API_KEY=.*[^=]$" .env 2>/dev/null && ! grep -q "GOLOGIN_API_KEY=your_gologin_api_key_here" .env; then
        echo "  ✅ GoLogin (opcional)"
    else
        echo "  ⏭️  GoLogin (no configurado - opcional)"
    fi
    
    if grep -q "TELEGRAM_BOT_TOKEN=.*[^=]$" .env 2>/dev/null && ! grep -q "TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here" .env; then
        echo "  ✅ Telegram Bot (opcional)"
    else
        echo "  ⏭️  Telegram Bot (no configurado - opcional)"
    fi
    
    echo "  ✅ PostgreSQL, n8n, Grafana passwords"
    echo ""
    echo -e "${CYAN}Próximos pasos:${NC}"
    echo ""
    echo "  1. Descarga modelos YOLOv8:"
    echo "     ${YELLOW}./download-models.sh${NC}"
    echo ""
    echo "  2. Inicia Docker V3:"
    echo "     ${YELLOW}./v3-docker.sh start${NC}"
    echo ""
    echo "  3. Verifica salud:"
    echo "     ${YELLOW}./v3-docker.sh health${NC}"
    echo ""
    echo "  4. Abre dashboard:"
    echo "     ${YELLOW}./v3-docker.sh dashboard${NC}"
    echo ""
}

# Main
main() {
    banner
    check_env
    create_env
    configure_credentials
    show_summary
}

main
