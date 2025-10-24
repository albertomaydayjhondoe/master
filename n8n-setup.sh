#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════
# n8n-setup.sh - Setup n8n Workflows and Configuration
# ═══════════════════════════════════════════════════════════════════════════

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

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
    echo "  🔄 N8N WORKFLOW SETUP - Docker V3"
    echo "  Automatización 24/7 con 3 workflows pre-configurados"
    echo "═══════════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

# Check if n8n is running
check_n8n() {
    log_info "Verificando si n8n está corriendo..."
    
    if curl -sf http://localhost:5678/healthz > /dev/null 2>&1; then
        log_success "n8n está corriendo en http://localhost:5678"
        return 0
    else
        log_error "n8n no está corriendo"
        log_info "Inicia Docker V3 primero: ./v3-docker.sh start"
        exit 1
    fi
}

# Import workflows
import_workflows() {
    log_info "Importando workflows n8n..."
    echo ""
    
    WORKFLOW_DIR="orchestration/n8n_workflows"
    
    if [ ! -d "$WORKFLOW_DIR" ]; then
        log_error "Directorio de workflows no encontrado: $WORKFLOW_DIR"
        exit 1
    fi
    
    # Count workflows
    WORKFLOW_COUNT=$(ls -1 "$WORKFLOW_DIR"/*.json 2>/dev/null | wc -l)
    
    if [ "$WORKFLOW_COUNT" -eq 0 ]; then
        log_warning "No se encontraron workflows en $WORKFLOW_DIR"
        exit 1
    fi
    
    log_info "Encontrados $WORKFLOW_COUNT workflows:"
    echo ""
    
    for workflow in "$WORKFLOW_DIR"/*.json; do
        filename=$(basename "$workflow")
        echo "  📄 $filename"
    done
    
    echo ""
    log_info "Para importar workflows:"
    echo ""
    echo "  1. Abre n8n: http://localhost:5678"
    echo "  2. Login: admin / viral_admin_2025"
    echo "  3. Click en '+ Add workflow'"
    echo "  4. Click en '...' → 'Import from file'"
    echo "  5. Selecciona cada archivo:"
    
    for workflow in "$WORKFLOW_DIR"/*.json; do
        echo "     - $workflow"
    done
    
    echo ""
    log_success "Workflows listos para importar"
}

# Configure webhooks
configure_webhooks() {
    echo ""
    log_info "═════════════════════════════════════════════════════"
    log_info "  CONFIGURACIÓN DE WEBHOOKS"
    log_info "═════════════════════════════════════════════════════"
    echo ""
    
    # Check .env for webhook URL
    if [ -f .env ]; then
        WEBHOOK_URL=$(grep WEBHOOK_URL .env | cut -d '=' -f2)
        log_info "Webhook URL actual: $WEBHOOK_URL"
    else
        log_warning ".env no encontrado"
        WEBHOOK_URL="http://n8n:5678/"
    fi
    
    echo ""
    log_info "Webhooks disponibles (después de importar workflows):"
    echo ""
    echo "  1. Main Orchestrator:"
    echo "     ${WEBHOOK_URL}webhook/main-orchestrator"
    echo ""
    echo "  2. ML Decision Engine:"
    echo "     ${WEBHOOK_URL}webhook/ml-decision"
    echo ""
    echo "  3. Device Farm Trigger:"
    echo "     ${WEBHOOK_URL}webhook/device-farm"
    echo ""
    
    log_info "Configura estos webhooks en unified_system_v3.py"
}

# Test webhook
test_webhook() {
    echo ""
    log_info "═════════════════════════════════════════════════════"
    log_info "  TEST DE WEBHOOK"
    log_info "═════════════════════════════════════════════════════"
    echo ""
    
    read -p "¿Deseas probar un webhook? (y/n): " test_webhook
    
    if [ "$test_webhook" = "y" ]; then
        log_info "Testing webhook de health check..."
        
        response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5678/healthz)
        
        if [ "$response" -eq 200 ]; then
            log_success "Webhook test exitoso (HTTP 200)"
        else
            log_warning "Webhook test falló (HTTP $response)"
        fi
    fi
}

# Show credentials
show_credentials() {
    echo ""
    log_info "═════════════════════════════════════════════════════"
    log_info "  CREDENCIALES N8N"
    log_info "═════════════════════════════════════════════════════"
    echo ""
    echo "  URL:      http://localhost:5678"
    echo "  Usuario:  admin"
    echo "  Password: viral_admin_2025"
    echo ""
    log_warning "IMPORTANTE: Cambia la password en producción"
    echo ""
}

# Show workflow list
show_workflows() {
    echo ""
    log_info "═════════════════════════════════════════════════════"
    log_info "  WORKFLOWS DISPONIBLES"
    log_info "═════════════════════════════════════════════════════"
    echo ""
    echo "  1. main_orchestrator.json"
    echo "     → Coordina TODO el sistema"
    echo "     → Triggers: Campaign launch, scheduled tasks"
    echo "     → Calls: ML Core, Meta Ads, YouTube, Pixel Tracker"
    echo ""
    echo "  2. ml_decision_engine.json"
    echo "     → Decisiones basadas en ML"
    echo "     → Virality predictions, posting time optimization"
    echo "     → Shadowban detection, content scoring"
    echo ""
    echo "  3. device_farm_trigger.json"
    echo "     → Dispara publicación en móviles"
    echo "     → Coordina 10 dispositivos ADB"
    echo "     → Human-like patterns, engagement automation"
    echo ""
}

# Main
main() {
    banner
    check_n8n
    show_credentials
    show_workflows
    import_workflows
    configure_webhooks
    test_webhook
    
    echo ""
    log_success "═════════════════════════════════════════════════════"
    log_success "  ✅ N8N SETUP COMPLETADO"
    log_success "═════════════════════════════════════════════════════"
    echo ""
    log_info "Próximos pasos:"
    echo ""
    echo "  1. Abre n8n: http://localhost:5678"
    echo "  2. Importa workflows desde orchestration/n8n_workflows/"
    echo "  3. Activa cada workflow (toggle ON)"
    echo "  4. Configura credenciales en cada nodo"
    echo "  5. Ejecuta primera campaña desde dashboard"
    echo ""
}

main
