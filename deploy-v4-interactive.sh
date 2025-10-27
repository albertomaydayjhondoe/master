#!/bin/bash

# TikTok ML System v4 - Interactive Production Deployment Script (Bash)
# Complete deployment with user input and validation for Unix/Linux systems

set -e

# Colors for enhanced user experience
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_prompt() { echo -e "${MAGENTA}[INPUT]${NC} $1"; }

# Header function
show_header() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    printf "║ %-68s ║\n" "$1"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Input function with validation
read_input() {
    local prompt="$1"
    local default="$2"
    local required="$3"
    local secret="$4"
    local input=""
    
    while true; do
        if [[ -n "$default" ]]; then
            log_prompt "$prompt [$default]: "
        else
            if [[ "$required" == "true" ]]; then
                log_prompt "$prompt (REQUERIDO): "
            else
                log_prompt "$prompt: "
            fi
        fi
        
        if [[ "$secret" == "true" ]]; then
            read -s input
            echo ""
        else
            read input
        fi
        
        if [[ -z "$input" ]]; then
            input="$default"
        fi
        
        if [[ "$required" == "true" && -z "$input" ]]; then
            log_warning "Este campo es requerido. Por favor ingresa un valor."
        else
            break
        fi
    done
    
    echo "$input"
}

# Test prerequisites
test_prerequisites() {
    show_header "VERIFICACIÓN DE PREREQUISITOS"
    
    local all_good=true
    
    # Check Docker
    log_info "🔍 Verificando Docker..."
    if command -v docker &> /dev/null; then
        local docker_version=$(docker --version)
        log_success "✅ Docker encontrado: $docker_version"
    else
        log_error "❌ Docker no está instalado"
        all_good=false
    fi
    
    # Check Docker Compose
    log_info "🔍 Verificando Docker Compose..."
    if command -v docker-compose &> /dev/null; then
        local compose_version=$(docker-compose --version)
        log_success "✅ Docker Compose encontrado: $compose_version"
    else
        log_error "❌ Docker Compose no está instalado"
        all_good=false
    fi
    
    # Check Git
    log_info "🔍 Verificando Git..."
    if command -v git &> /dev/null; then
        local git_version=$(git --version)
        log_success "✅ Git encontrado: $git_version"
    else
        log_warning "⚠️  Git no encontrado (opcional para deployment)"
    fi
    
    # Check required files
    log_info "🔍 Verificando archivos requeridos..."
    local required_files=(
        "Dockerfile.v4"
        "docker-compose.v4.yml"
        "requirements.txt"
        "ml_core/api/main_v4.py"
        ".env.example"
    )
    
    for file in "${required_files[@]}"; do
        if [[ -f "$file" ]]; then
            log_success "✅ $file"
        else
            log_error "❌ $file - ARCHIVO FALTANTE"
            all_good=false
        fi
    done
    
    if [[ "$all_good" == "false" ]]; then
        log_error "❌ Prerequisitos faltantes. Por favor instala los componentes faltantes."
        return 1
    fi
    
    log_success "🎉 Todos los prerequisitos verificados correctamente!"
    return 0
}

# Get deployment configuration
get_deployment_config() {
    show_header "CONFIGURACIÓN DE DEPLOYMENT"
    
    log_info "📋 Selecciona el tipo de deployment:"
    echo -e "${WHITE}1. 🐳 Docker Local (Desarrollo/Testing)${NC}"
    echo -e "${WHITE}2. 🚀 Railway Cloud (Producción)${NC}"
    echo -e "${WHITE}3. ☁️  Docker Compose Completo (Producción Local)${NC}"
    
    local deploy_type=$(read_input "Tipo de deployment [1-3]" "1" "true")
    
    case "$deploy_type" in
        "1") DEPLOY_TYPE="docker-local" ;;
        "2") DEPLOY_TYPE="railway" ;;
        "3") DEPLOY_TYPE="docker-compose" ;;
        *) DEPLOY_TYPE="docker-local" ;;
    esac
    
    local prod_mode=$(read_input "🔧 Modo producción (true/false)" "true")
    if [[ "$prod_mode" == "true" ]]; then
        PRODUCTION_MODE=true
        log_warning "⚠️  MODO PRODUCCIÓN activado - Se requieren credenciales reales"
    else
        PRODUCTION_MODE=false
        log_info "🧪 MODO DESARROLLO activado - Se usarán valores dummy"
    fi
}

# Get API credentials
get_api_credentials() {
    show_header "CONFIGURACIÓN DE CREDENCIALES API"
    
    if [[ "$PRODUCTION_MODE" == "true" ]]; then
        log_warning "🔐 Configurando credenciales para PRODUCCIÓN"
        log_warning "⚠️  Todas las credenciales son requeridas en modo producción"
        echo ""
        
        # Core API
        API_SECRET_KEY=$(read_input "🔑 API Secret Key (min 32 caracteres)" "" "true" "true")
        JWT_SECRET=$(read_input "🔑 JWT Secret (min 32 caracteres)" "" "true" "true")
        
        # Supabase
        echo ""
        log_info "📊 SUPABASE CONFIGURATION (Requerido para métricas)"
        SUPABASE_URL=$(read_input "🔗 Supabase URL" "" "true")
        SUPABASE_ANON_KEY=$(read_input "🔑 Supabase Anon Key" "" "true" "true")
        SUPABASE_SERVICE_KEY=$(read_input "🔑 Supabase Service Key" "" "true" "true")
        
        # Meta Ads
        echo ""
        log_info "🎯 META ADS CONFIGURATION"
        local include_meta=$(read_input "¿Configurar Meta Ads? (y/n)" "y")
        if [[ "$include_meta" == "y" ]]; then
            META_APP_ID=$(read_input "📱 Meta App ID" "" "true")
            META_APP_SECRET=$(read_input "🔐 Meta App Secret" "" "true" "true")
            META_ACCESS_TOKEN=$(read_input "🎫 Meta Access Token (long-lived)" "" "true" "true")
            META_PIXEL_ID=$(read_input "📊 Meta Pixel ID" "")
        fi
        
        # YouTube
        echo ""
        log_info "🎥 YOUTUBE CONFIGURATION"
        local include_youtube=$(read_input "¿Configurar YouTube API? (y/n)" "y")
        if [[ "$include_youtube" == "y" ]]; then
            YOUTUBE_API_KEY=$(read_input "🔑 YouTube API Key" "" "true" "true")
            YOUTUBE_CHANNEL_IDS=$(read_input "📺 Channel IDs (separados por coma)" "")
        fi
        
        # Spotify
        echo ""
        log_info "🎵 SPOTIFY CONFIGURATION"
        local include_spotify=$(read_input "¿Configurar Spotify API? (y/n)" "y")
        if [[ "$include_spotify" == "y" ]]; then
            SPOTIFY_CLIENT_ID=$(read_input "🎼 Spotify Client ID" "" "true")
            SPOTIFY_CLIENT_SECRET=$(read_input "🔐 Spotify Client Secret" "" "true" "true")
            SPOTIFY_ARTIST_IDS=$(read_input "🎤 Artist IDs (separados por coma)" "")
            SPOTIFY_PLAYLIST_IDS=$(read_input "📋 Playlist IDs (separados por coma)" "")
        fi
        
        # Landing Pages
        echo ""
        log_info "🌐 LANDING PAGE CONFIGURATION"
        local include_landing=$(read_input "¿Configurar Landing Pages? (y/n)" "y")
        if [[ "$include_landing" == "y" ]]; then
            LANDING_PAGE_URLS=$(read_input "🌐 Landing Page URLs (separadas por coma)" "")
        fi
        
        # n8n
        echo ""
        log_info "🔄 N8N CONFIGURATION"
        local include_n8n=$(read_input "¿Configurar n8n? (y/n)" "y")
        if [[ "$include_n8n" == "y" ]]; then
            N8N_WEBHOOK_BASE_URL=$(read_input "🔗 n8n Webhook Base URL" "")
            N8N_API_KEY=$(read_input "🔑 n8n API Key" "" "false" "true")
        fi
        
    else
        log_info "🧪 Modo desarrollo - usando valores dummy"
        API_SECRET_KEY="dummy-secret-key-development-only-32chars"
        JWT_SECRET="dummy-jwt-secret-development-only-32chars"
        SUPABASE_URL="https://dummy-project.supabase.co"
        SUPABASE_ANON_KEY="dummy-anon-key"
        SUPABASE_SERVICE_KEY="dummy-service-key"
        META_APP_ID="dummy-meta-app-id"
        META_APP_SECRET="dummy-meta-secret"
        META_ACCESS_TOKEN="dummy-access-token"
        YOUTUBE_API_KEY="dummy-youtube-key"
        SPOTIFY_CLIENT_ID="dummy-spotify-client"
        SPOTIFY_CLIENT_SECRET="dummy-spotify-secret"
    fi
}

# Create environment file
create_environment_file() {
    show_header "CREACIÓN ARCHIVO .ENV"
    
    log_info "📝 Creando archivo .env con configuraciones..."
    
    # Backup existing .env if it exists
    if [[ -f ".env" ]]; then
        local backup=".env.backup.$(date +%Y%m%d-%H%M%S)"
        cp ".env" "$backup"
        log_warning "💾 Backup de .env existente guardado como: $backup"
    fi
    
    # Create new .env file
    cat > .env << EOF
# TikTok ML System v4 - Auto-Generated Configuration
# Generated on: $(date '+%Y-%m-%d %H:%M:%S')
# Mode: $(if [[ "$PRODUCTION_MODE" == "true" ]]; then echo "PRODUCTION"; else echo "DEVELOPMENT"; fi)

# === SYSTEM CONFIGURATION ===
PRODUCTION_MODE=$PRODUCTION_MODE
DEBUG=$(if [[ "$PRODUCTION_MODE" == "true" ]]; then echo "false"; else echo "true"; fi)
LOG_LEVEL=INFO

# === CORE API CONFIGURATION ===
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1
API_SECRET_KEY=$API_SECRET_KEY
JWT_SECRET=$JWT_SECRET

# === SUPABASE CONFIGURATION ===
SUPABASE_URL=$SUPABASE_URL
SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY
SUPABASE_SERVICE_KEY=$SUPABASE_SERVICE_KEY

# === META ADS CONFIGURATION ===
META_APP_ID=${META_APP_ID:-}
META_APP_SECRET=${META_APP_SECRET:-}
META_ACCESS_TOKEN=${META_ACCESS_TOKEN:-}
META_PIXEL_ID=${META_PIXEL_ID:-}

# === YOUTUBE API CONFIGURATION ===
YOUTUBE_API_KEY=${YOUTUBE_API_KEY:-}
YOUTUBE_CHANNEL_IDS=${YOUTUBE_CHANNEL_IDS:-}

# === SPOTIFY API CONFIGURATION ===
SPOTIFY_CLIENT_ID=${SPOTIFY_CLIENT_ID:-}
SPOTIFY_CLIENT_SECRET=${SPOTIFY_CLIENT_SECRET:-}
SPOTIFY_ARTIST_IDS=${SPOTIFY_ARTIST_IDS:-}
SPOTIFY_PLAYLIST_IDS=${SPOTIFY_PLAYLIST_IDS:-}

# === LANDING PAGE CONFIGURATION ===
LANDING_PAGE_URLS=${LANDING_PAGE_URLS:-}

# === ML CONFIGURATION ===
ULTRALYTICS_MODEL=yolov8n.pt
ML_MODEL_PATH=/app/data/models
MAX_UPLOAD_SIZE=52428800

# === N8N CONFIGURATION ===
N8N_WEBHOOK_BASE_URL=${N8N_WEBHOOK_BASE_URL:-}
N8N_API_KEY=${N8N_API_KEY:-}

# === DEPLOYMENT CONFIGURATION ===
PORT=8000
HEALTHCHECK_INTERVAL=30s
EOF
    
    # Set secure permissions
    chmod 600 .env
    log_success "✅ Archivo .env creado exitosamente"
    log_info "🔒 Permisos de .env configurados para seguridad (600)"
}

# Docker build
start_docker_build() {
    show_header "CONSTRUCCIÓN DE IMAGEN DOCKER"
    
    log_info "🔨 Construyendo imagen Docker v4..."
    
    local build_args=""
    if [[ "$DEPLOY_TYPE" == "railway" ]]; then
        build_args="--platform linux/amd64"
    fi
    
    log_info "Ejecutando: docker build $build_args -f Dockerfile.v4 -t tiktok-ml-v4:latest ."
    
    if docker build $build_args -f Dockerfile.v4 -t tiktok-ml-v4:latest .; then
        log_success "✅ Imagen Docker construida exitosamente"
        return 0
    else
        log_error "❌ Error construyendo imagen Docker"
        return 1
    fi
}

# Start deployment
start_deployment() {
    show_header "INICIO DE DEPLOYMENT"
    
    case "$DEPLOY_TYPE" in
        "docker-local")
            log_info "🐳 Iniciando deployment Docker local..."
            
            # Stop existing container
            docker stop tiktok-ml-v4 2>/dev/null || true
            docker rm tiktok-ml-v4 2>/dev/null || true
            
            # Run new container
            log_info "Ejecutando container Docker..."
            if docker run -d \
                --name tiktok-ml-v4 \
                -p 8000:8000 \
                --env-file .env \
                -v "$(pwd)/data:/app/data" \
                -v "$(pwd)/logs:/app/logs" \
                tiktok-ml-v4:latest; then
                log_success "✅ Container Docker iniciado exitosamente"
                return 0
            else
                log_error "❌ Error iniciando container Docker"
                return 1
            fi
            ;;
            
        "docker-compose")
            log_info "🐳 Iniciando deployment Docker Compose completo..."
            
            docker-compose -f docker-compose.v4.yml down 2>/dev/null || true
            if docker-compose -f docker-compose.v4.yml up -d; then
                log_success "✅ Stack Docker Compose iniciado exitosamente"
                return 0
            else
                log_error "❌ Error iniciando stack Docker Compose"
                return 1
            fi
            ;;
            
        "railway")
            log_info "🚀 Preparando deployment Railway..."
            
            # Check Railway CLI
            if ! command -v railway &> /dev/null; then
                log_warning "❌ Railway CLI no encontrado. Instalando..."
                if command -v npm &> /dev/null; then
                    npm install -g @railway/cli
                    log_success "✅ Railway CLI instalado"
                else
                    log_error "❌ npm no encontrado. Por favor instala Node.js y Railway CLI manualmente."
                    return 1
                fi
            else
                local railway_version=$(railway version)
                log_success "✅ Railway CLI encontrado: $railway_version"
            fi
            
            # Railway login check
            if ! railway whoami &>/dev/null; then
                log_info "🔑 Por favor inicia sesión en Railway..."
                railway login
            fi
            
            # Deploy to Railway
            log_info "🚀 Desplegando a Railway..."
            if railway up --detach; then
                log_success "✅ Deployment a Railway completado exitosamente"
                return 0
            else
                log_error "❌ Error en deployment Railway"
                return 1
            fi
            ;;
    esac
    
    return 1
}

# Wait for health check
wait_for_health_check() {
    show_header "VERIFICACIÓN DE SALUD DEL SISTEMA"
    
    local base_url
    case "$DEPLOY_TYPE" in
        "docker-local"|"docker-compose")
            base_url="http://localhost:8000"
            ;;
        "railway")
            log_info "🔗 Obteniendo URL de Railway..."
            # Try to get Railway URL
            local railway_url=$(railway status --json 2>/dev/null | jq -r '.deployments[0].url' 2>/dev/null)
            if [[ -n "$railway_url" && "$railway_url" != "null" ]]; then
                base_url="$railway_url"
                log_info "🌐 URL Railway: $base_url"
            else
                log_warning "⚠️  No se pudo obtener URL de Railway automáticamente"
                base_url=$(read_input "🌐 Ingresa la URL de Railway manualmente" "https://your-app.railway.app")
            fi
            ;;
    esac
    
    log_info "🩺 Verificando salud del sistema en: $base_url"
    
    local max_attempts=20
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        log_info "🔄 Intento $attempt/$max_attempts - Verificando health endpoint..."
        
        if curl -f "$base_url/health" --max-time 10 --silent >/dev/null 2>&1; then
            log_success "✅ Sistema saludable!"
            echo "$base_url"
            return 0
        fi
        
        log_info "⏳ Esperando que el sistema esté listo..."
        sleep 15
        ((attempt++))
    done
    
    log_error "❌ El sistema no respondió después de $max_attempts intentos"
    echo "$base_url"
    return 1
}

# Test endpoints
test_endpoints() {
    local base_url="$1"
    show_header "PRUEBAS DE ENDPOINTS"
    
    local endpoints=(
        "Health Check:/health"
        "Root Info:/"
        "API Docs:/docs"
        "OpenAPI Schema:/openapi.json"
    )
    
    for endpoint_info in "${endpoints[@]}"; do
        IFS=':' read -r name path <<< "$endpoint_info"
        log_info "🧪 Probando $name: $path"
        
        if curl -f "$base_url$path" --max-time 10 --silent >/dev/null 2>&1; then
            log_success "✅ $name - OK"
        else
            log_error "❌ $name - Failed"
        fi
    done
}

# Show deployment summary
show_deployment_summary() {
    local base_url="$1"
    show_header "RESUMEN DE DEPLOYMENT"
    
    log_success "🎉 DEPLOYMENT COMPLETADO!"
    echo ""
    
    # Configuration Summary
    log_info "📋 CONFIGURACIÓN:"
    echo -e "${WHITE}   • Tipo: $DEPLOY_TYPE${NC}"
    echo -e "${WHITE}   • Modo: $(if [[ "$PRODUCTION_MODE" == "true" ]]; then echo "PRODUCTION"; else echo "DEVELOPMENT"; fi)${NC}"
    echo -e "${WHITE}   • URL Base: $base_url${NC}"
    echo ""
    
    # Quick Access URLs
    log_info "🌐 ENLACES RÁPIDOS:"
    echo -e "${WHITE}   • 🏠 Página Principal: $base_url/${NC}"
    echo -e "${WHITE}   • 📖 Documentación API: $base_url/docs${NC}"
    echo -e "${WHITE}   • 🩺 Health Check: $base_url/health${NC}"
    
    if [[ "$DEPLOY_TYPE" == "docker-compose" ]]; then
        echo -e "${WHITE}   • 🔄 n8n Workflows: http://localhost:5678${NC}"
        echo -e "${WHITE}   • 📊 Traefik Dashboard: http://localhost:8080${NC}"
    fi
    echo ""
    
    # Management Commands
    log_info "🛠️  COMANDOS DE GESTIÓN:"
    case "$DEPLOY_TYPE" in
        "docker-local")
            echo -e "${WHITE}   • Ver logs: docker logs tiktok-ml-v4 -f${NC}"
            echo -e "${WHITE}   • Parar: docker stop tiktok-ml-v4${NC}"
            echo -e "${WHITE}   • Reiniciar: docker restart tiktok-ml-v4${NC}"
            ;;
        "docker-compose")
            echo -e "${WHITE}   • Ver logs: docker-compose -f docker-compose.v4.yml logs -f${NC}"
            echo -e "${WHITE}   • Parar: docker-compose -f docker-compose.v4.yml down${NC}"
            echo -e "${WHITE}   • Reiniciar: docker-compose -f docker-compose.v4.yml restart${NC}"
            ;;
        "railway")
            echo -e "${WHITE}   • Ver logs: railway logs${NC}"
            echo -e "${WHITE}   • Estado: railway status${NC}"
            echo -e "${WHITE}   • Redeploy: railway up --detach${NC}"
            ;;
    esac
    echo ""
    
    # Next Steps
    log_info "📋 PRÓXIMOS PASOS:"
    echo -e "${WHITE}   1. 🔧 Configurar workflows n8n (si aplica)${NC}"
    echo -e "${WHITE}   2. 🧪 Probar endpoints en /docs${NC}"
    echo -e "${WHITE}   3. 📊 Verificar métricas Supabase${NC}"
    echo -e "${WHITE}   4. 🎯 Configurar campañas Meta Ads${NC}"
    echo -e "${WHITE}   5. 🔒 Configurar SSL para producción${NC}"
    echo ""
    
    log_success "🚀 ¡TikTok ML System v4 desplegado exitosamente!"
}

# Main function
main() {
    clear
    
    # Logo and welcome
    echo -e "${CYAN}"
    cat << "EOF"
    ████████╗██╗██╗  ██╗████████╗ ██████╗ ██╗  ██╗    ███╗   ███╗██╗         
    ╚══██╔══╝██║██║ ██╔╝╚══██╔══╝██╔═══██╗██║ ██╔╝    ████╗ ████║██║         
       ██║   ██║█████╔╝    ██║   ██║   ██║█████╔╝     ██╔████╔██║██║         
       ██║   ██║██╔═██╗    ██║   ██║   ██║██╔═██╗     ██║╚██╔╝██║██║         
       ██║   ██║██║  ██╗   ██║   ╚██████╔╝██║  ██╗    ██║ ╚═╝ ██║███████╗    
       ╚═╝   ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝    ╚═╝     ╚═╝╚══════╝    
                                                                              
                        SISTEMA v4 - DEPLOYMENT INTERACTIVO
EOF
    echo -e "${NC}"
    
    log_info "🚀 Bienvenido al deployment interactivo del TikTok ML System v4"
    log_info "📋 Este script te guiará paso a paso para desplegar el sistema completo"
    echo ""
    
    # Execute deployment steps
    if ! test_prerequisites; then
        log_error "❌ No se pueden cumplir los prerequisitos. Deployment cancelado."
        exit 1
    fi
    
    get_deployment_config
    get_api_credentials
    create_environment_file
    
    if ! start_docker_build; then
        log_error "❌ Error en construcción Docker. Deployment cancelado."
        exit 1
    fi
    
    if ! start_deployment; then
        log_error "❌ Error en deployment. Proceso cancelado."
        exit 1
    fi
    
    local base_url
    base_url=$(wait_for_health_check)
    test_endpoints "$base_url"
    show_deployment_summary "$base_url"
    
    echo ""
    log_info "⏸️  Presiona Enter para continuar..."
    read
}

# Execute main function
main "$@"