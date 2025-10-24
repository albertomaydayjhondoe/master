#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════
# v3-docker.sh - Docker V3 Management CLI
# ═══════════════════════════════════════════════════════════════════════════
#
# Sistema completo: Ultralytics + n8n + v1 + v2
#
# Usage:
#   ./v3-docker.sh [command]
#
# Commands:
#   start          - Inicia todos los servicios
#   stop           - Detiene todos los servicios
#   restart        - Reinicia todos los servicios
#   status         - Muestra el estado de los servicios
#   logs           - Muestra logs en tiempo real
#   build          - Reconstruye las imágenes
#   clean          - Limpia volúmenes y contenedores
#   reset          - Reset completo (DESTRUYE DATOS)
#   scale          - Escala servicios
#   health         - Verifica salud de servicios
#   n8n            - Abre n8n en navegador
#   dashboard      - Abre dashboard en navegador
#   psql           - Conecta a PostgreSQL
#   redis-cli      - Conecta a Redis
#
# ═══════════════════════════════════════════════════════════════════════════

set -e

COMPOSE_FILE="docker-compose-v3.yml"
PROJECT_NAME="unified-v3"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
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

banner() {
    echo -e "${BLUE}"
    echo "═══════════════════════════════════════════════════════════════"
    echo "  🚀 DOCKER V3 - Sistema Completo Viral"
    echo "  Ultralytics YOLOv8 + n8n Workflows + Meta Ads + Device Farm"
    echo "═══════════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

check_env() {
    if [ ! -f .env ]; then
        log_warning "No se encontró .env"
        if [ -f .env.v3 ]; then
            log_info "Copiando .env.v3 a .env..."
            cp .env.v3 .env
            log_success ".env creado desde .env.v3"
        else
            log_error ".env.v3 no existe. Crea uno basado en .env.example"
            exit 1
        fi
    fi
}

# Command functions
cmd_start() {
    banner
    log_info "Iniciando Docker V3..."
    check_env
    
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d
    
    log_success "Docker V3 iniciado correctamente"
    echo ""
    log_info "Access points:"
    echo "  Dashboard:            http://localhost:8501"
    echo "  Unified Orchestrator: http://localhost:10000"
    echo "  n8n Workflows:        http://localhost:5678"
    echo "  ML Core API:          http://localhost:8000"
    echo "  Meta Ads Manager:     http://localhost:9000"
    echo "  Grafana Monitoring:   http://localhost:3000"
}

cmd_stop() {
    log_info "Deteniendo Docker V3..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" stop
    log_success "Docker V3 detenido"
}

cmd_restart() {
    log_info "Reiniciando Docker V3..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" restart
    log_success "Docker V3 reiniciado"
}

cmd_status() {
    banner
    log_info "Estado de servicios:"
    echo ""
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps
}

cmd_logs() {
    SERVICE="${2:-}"
    if [ -z "$SERVICE" ]; then
        log_info "Mostrando logs de todos los servicios..."
        docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f
    else
        log_info "Mostrando logs de $SERVICE..."
        docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f "$SERVICE"
    fi
}

cmd_build() {
    log_info "Reconstruyendo imágenes Docker..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" build --no-cache
    log_success "Imágenes reconstruidas"
}

cmd_clean() {
    log_warning "Limpiando contenedores y volúmenes..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down -v
    log_success "Limpieza completada"
}

cmd_reset() {
    log_error "⚠️  RESET COMPLETO - DESTRUIRÁ TODOS LOS DATOS"
    read -p "¿Estás seguro? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        log_info "Deteniendo servicios..."
        docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down -v
        
        log_info "Eliminando volúmenes..."
        docker volume rm ${PROJECT_NAME}_postgres-data 2>/dev/null || true
        docker volume rm ${PROJECT_NAME}_redis-data 2>/dev/null || true
        docker volume rm ${PROJECT_NAME}_n8n-data 2>/dev/null || true
        docker volume rm ${PROJECT_NAME}_ml-models 2>/dev/null || true
        docker volume rm ${PROJECT_NAME}_video-data 2>/dev/null || true
        
        log_success "Reset completado"
    else
        log_info "Reset cancelado"
    fi
}

cmd_scale() {
    SERVICE="${2:-}"
    COUNT="${3:-2}"
    
    if [ -z "$SERVICE" ]; then
        log_error "Uso: ./v3-docker.sh scale <service> <count>"
        exit 1
    fi
    
    log_info "Escalando $SERVICE a $COUNT instancias..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d --scale "$SERVICE=$COUNT"
    log_success "$SERVICE escalado a $COUNT instancias"
}

cmd_health() {
    banner
    log_info "Verificando salud de servicios..."
    echo ""
    
    services=(
        "ml-core:8000:/health"
        "unified-orchestrator:10000:/health"
        "meta-ads-manager:9000:/health"
        "n8n:5678:/healthz"
    )
    
    for service_info in "${services[@]}"; do
        IFS=':' read -r service port path <<< "$service_info"
        url="http://localhost:$port$path"
        
        if curl -sf "$url" > /dev/null 2>&1; then
            log_success "$service: Healthy"
        else
            log_error "$service: Unhealthy (URL: $url)"
        fi
    done
}

cmd_n8n() {
    log_info "Abriendo n8n en navegador..."
    if command -v xdg-open &> /dev/null; then
        xdg-open "http://localhost:5678"
    elif command -v open &> /dev/null; then
        open "http://localhost:5678"
    else
        log_info "Abre manualmente: http://localhost:5678"
        log_info "Usuario: admin"
        log_info "Password: viral_admin_2025"
    fi
}

cmd_dashboard() {
    log_info "Abriendo dashboard en navegador..."
    if command -v xdg-open &> /dev/null; then
        xdg-open "http://localhost:8501"
    elif command -v open &> /dev/null; then
        open "http://localhost:8501"
    else
        log_info "Abre manualmente: http://localhost:8501"
    fi
}

cmd_psql() {
    log_info "Conectando a PostgreSQL..."
    docker exec -it unified-postgres psql -U postgres -d community_manager
}

cmd_redis_cli() {
    log_info "Conectando a Redis..."
    docker exec -it unified-redis redis-cli
}

cmd_help() {
    banner
    echo "Comandos disponibles:"
    echo ""
    echo "  start          - Inicia todos los servicios"
    echo "  stop           - Detiene todos los servicios"
    echo "  restart        - Reinicia todos los servicios"
    echo "  status         - Muestra el estado de los servicios"
    echo "  logs [service] - Muestra logs (opcional: de un servicio específico)"
    echo "  build          - Reconstruye las imágenes"
    echo "  clean          - Limpia volúmenes y contenedores"
    echo "  reset          - Reset completo (DESTRUYE DATOS)"
    echo "  scale <srv> <n>- Escala un servicio a N instancias"
    echo "  health         - Verifica salud de servicios"
    echo "  n8n            - Abre n8n en navegador"
    echo "  dashboard      - Abre dashboard en navegador"
    echo "  psql           - Conecta a PostgreSQL CLI"
    echo "  redis-cli      - Conecta a Redis CLI"
    echo "  help           - Muestra esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  ./v3-docker.sh start"
    echo "  ./v3-docker.sh logs unified-orchestrator"
    echo "  ./v3-docker.sh scale device-farm 3"
    echo "  ./v3-docker.sh health"
}

# Main command dispatcher
COMMAND="${1:-help}"

case "$COMMAND" in
    start)
        cmd_start "$@"
        ;;
    stop)
        cmd_stop "$@"
        ;;
    restart)
        cmd_restart "$@"
        ;;
    status)
        cmd_status "$@"
        ;;
    logs)
        cmd_logs "$@"
        ;;
    build)
        cmd_build "$@"
        ;;
    clean)
        cmd_clean "$@"
        ;;
    reset)
        cmd_reset "$@"
        ;;
    scale)
        cmd_scale "$@"
        ;;
    health)
        cmd_health "$@"
        ;;
    n8n)
        cmd_n8n "$@"
        ;;
    dashboard)
        cmd_dashboard "$@"
        ;;
    psql)
        cmd_psql "$@"
        ;;
    redis-cli)
        cmd_redis_cli "$@"
        ;;
    help|--help|-h)
        cmd_help
        ;;
    *)
        log_error "Comando desconocido: $COMMAND"
        echo ""
        cmd_help
        exit 1
        ;;
esac
