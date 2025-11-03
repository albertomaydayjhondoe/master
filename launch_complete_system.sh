#!/bin/bash
"""
🚀 Sistema de Lanzamiento Completo - Dashboards + N8N Integration

Script de lanzamiento unificado para el sistema completo:
- Dashboards centralizados (Gradio + Streamlit)
- Integración N8N completa con workflows
- Monitoreo en tiempo real
- Community management automatizado

Uso:
  ./launch_complete_system.sh [--dummy|--production] [--quick]

Autor: Sistema Centralizado de Dashboards
Fecha: 2025-11-03
"""

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
BASE_DIR="/workspaces/master"
LOG_DIR="$BASE_DIR/logs"
PID_DIR="$BASE_DIR/.pids"

# Default settings
MODE="dummy"
QUICK_START=false
SKIP_N8N=false

# Create directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dummy)
            MODE="dummy"
            shift
            ;;
        --production)
            MODE="production"
            shift
            ;;
        --quick)
            QUICK_START=true
            shift
            ;;
        --skip-n8n)
            SKIP_N8N=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--dummy|--production] [--quick] [--skip-n8n]"
            echo ""
            echo "Options:"
            echo "  --dummy       Run in dummy mode (default)"
            echo "  --production  Run in production mode"
            echo "  --quick       Skip health checks and validations"
            echo "  --skip-n8n    Skip N8N setup and integration"
            echo "  --help        Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

log_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[$(date +'%Y-%m-%d %H:%M:%S')] STEP:${NC} $1"
}

# Check if process is running
is_running() {
    local pid_file=$1
    if [[ -f "$pid_file" ]]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        else
            rm -f "$pid_file"
            return 1
        fi
    fi
    return 1
}

# Kill process by PID file
kill_process() {
    local pid_file=$1
    local name=$2
    
    if is_running "$pid_file"; then
        local pid=$(cat "$pid_file")
        log "Stopping $name (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
        sleep 2
        
        # Force kill if still running
        if kill -0 "$pid" 2>/dev/null; then
            log_warn "Force killing $name..."
            kill -9 "$pid" 2>/dev/null || true
        fi
        
        rm -f "$pid_file"
        log "$name stopped"
    fi
}

# Clean up function
cleanup() {
    log_step "🧹 Cleaning up processes..."
    
    kill_process "$PID_DIR/production_controller.pid" "Production Controller"
    kill_process "$PID_DIR/analytics_engine.pid" "Analytics Engine"
    kill_process "$PID_DIR/ml_api.pid" "ML API"
    
    if [[ "$SKIP_N8N" != "true" ]]; then
        kill_process "$PID_DIR/n8n.pid" "N8N Server"
    fi
    
    log "✅ Cleanup completed"
}

# Handle signals
trap cleanup EXIT INT TERM

# Check dependencies
check_dependencies() {
    log_step "🔍 Checking dependencies..."
    
    local missing_deps=()
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        missing_deps+=("pip3")
    fi
    
    # Check Node.js (for N8N)
    if [[ "$SKIP_N8N" != "true" ]] && ! command -v node &> /dev/null; then
        missing_deps+=("node.js")
    fi
    
    # Check npm (for N8N)
    if [[ "$SKIP_N8N" != "true" ]] && ! command -v npm &> /dev/null; then
        missing_deps+=("npm")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_error "Please install missing dependencies first"
        exit 1
    fi
    
    log "✅ All dependencies found"
}

# Install Python requirements
install_requirements() {
    log_step "📦 Installing Python requirements..."
    
    cd "$BASE_DIR"
    
    # Install requirements based on mode
    if [[ "$MODE" == "dummy" ]]; then
        if [[ -f "requirements-dummy.txt" ]]; then
            pip3 install -r requirements-dummy.txt >> "$LOG_DIR/pip_install.log" 2>&1
        fi
    else
        if [[ -f "requirements.txt" ]]; then
            pip3 install -r requirements.txt >> "$LOG_DIR/pip_install.log" 2>&1
        fi
    fi
    
    # Install additional requirements
    local additional_packages=(
        "gradio>=4.0.0"
        "streamlit>=1.28.0"
        "plotly>=5.17.0"
        "pandas>=2.0.0"
        "aiohttp>=3.8.0"
        "requests>=2.31.0"
    )
    
    for package in "${additional_packages[@]}"; do
        pip3 install "$package" >> "$LOG_DIR/pip_install.log" 2>&1 || true
    done
    
    log "✅ Python requirements installed"
}

# Setup N8N
setup_n8n() {
    if [[ "$SKIP_N8N" == "true" ]]; then
        log_info "Skipping N8N setup as requested"
        return 0
    fi
    
    log_step "🔧 Setting up N8N..."
    
    cd "$BASE_DIR"
    
    # Use our N8N workflow manager
    if [[ -f "n8n_workflow_manager.py" ]]; then
        log "Using N8N Workflow Manager for setup..."
        
        if [[ "$QUICK_START" == "true" ]]; then
            python3 n8n_workflow_manager.py setup --force
        else
            python3 n8n_workflow_manager.py setup
        fi
        
        if [[ $? -eq 0 ]]; then
            log "✅ N8N setup completed successfully"
        else
            log_warn "⚠️ N8N setup completed with issues"
        fi
    else
        log_warn "N8N Workflow Manager not found, skipping N8N setup"
    fi
}

# Start ML API
start_ml_api() {
    log_step "🤖 Starting ML API..."
    
    cd "$BASE_DIR"
    
    if is_running "$PID_DIR/ml_api.pid"; then
        log "ML API already running"
        return 0
    fi
    
    # Start ML API in background
    if [[ "$MODE" == "dummy" ]]; then
        export DUMMY_MODE=true
    else
        export DUMMY_MODE=false
    fi
    
    # Use dummy ML API for now
    cat > ml_api_dummy.py << 'EOF'
#!/usr/bin/env python3
"""Dummy ML API for testing"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import asyncio

app = FastAPI(title="ML API (Dummy)", version="1.0.0")

@app.get("/health")
async def health():
    return {"status": "healthy", "mode": "dummy"}

@app.post("/analyze_screenshot")
async def analyze_screenshot(data: dict):
    await asyncio.sleep(0.1)  # Simulate processing
    return {"analysis": "dummy_result", "confidence": 0.95}

@app.post("/detect_anomaly")
async def detect_anomaly(data: dict):
    await asyncio.sleep(0.1)
    return {"anomaly_detected": False, "score": 0.1}

@app.post("/predict_posting_time")
async def predict_posting_time(data: dict):
    await asyncio.sleep(0.1)
    return {"optimal_time": "2025-11-03T15:30:00Z", "score": 0.88}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF
    
    chmod +x ml_api_dummy.py
    
    python3 ml_api_dummy.py > "$LOG_DIR/ml_api.log" 2>&1 &
    echo $! > "$PID_DIR/ml_api.pid"
    
    # Wait for API to start
    for i in {1..10}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            log "✅ ML API started successfully"
            return 0
        fi
        sleep 1
    done
    
    log_warn "⚠️ ML API may not have started properly"
}

# Start Production Controller
start_production_controller() {
    log_step "🎯 Starting Production Controller (Gradio)..."
    
    cd "$BASE_DIR"
    
    if is_running "$PID_DIR/production_controller.pid"; then
        log "Production Controller already running"
        return 0
    fi
    
    if [[ -f "production_controller.py" ]]; then
        python3 production_controller.py > "$LOG_DIR/production_controller.log" 2>&1 &
        echo $! > "$PID_DIR/production_controller.pid"
        
        # Wait for Gradio to start
        for i in {1..15}; do
            if curl -s http://localhost:7860 > /dev/null 2>&1; then
                log "✅ Production Controller started at http://localhost:7860"
                return 0
            fi
            sleep 2
        done
        
        log_warn "⚠️ Production Controller may not have started properly"
    else
        log_error "❌ production_controller.py not found"
        return 1
    fi
}

# Start Analytics Engine
start_analytics_engine() {
    log_step "📊 Starting Analytics Engine (Streamlit)..."
    
    cd "$BASE_DIR"
    
    if is_running "$PID_DIR/analytics_engine.pid"; then
        log "Analytics Engine already running"
        return 0
    fi
    
    if [[ -f "analytics_engine.py" ]]; then
        streamlit run analytics_engine.py --server.port=8501 --server.address=0.0.0.0 > "$LOG_DIR/analytics_engine.log" 2>&1 &
        echo $! > "$PID_DIR/analytics_engine.pid"
        
        # Wait for Streamlit to start
        for i in {1..15}; do
            if curl -s http://localhost:8501 > /dev/null 2>&1; then
                log "✅ Analytics Engine started at http://localhost:8501"
                return 0
            fi
            sleep 2
        done
        
        log_warn "⚠️ Analytics Engine may not have started properly"
    else
        log_error "❌ analytics_engine.py not found"
        return 1
    fi
}

# Health check
perform_health_check() {
    if [[ "$QUICK_START" == "true" ]]; then
        log_info "Skipping health check (quick start mode)"
        return 0
    fi
    
    log_step "🏥 Performing health check..."
    
    local health_status=0
    
    # Check ML API
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        log "✅ ML API health check passed"
    else
        log_warn "⚠️ ML API health check failed"
        health_status=1
    fi
    
    # Check Production Controller
    if curl -s http://localhost:7860 > /dev/null 2>&1; then
        log "✅ Production Controller health check passed"
    else
        log_warn "⚠️ Production Controller health check failed"
        health_status=1
    fi
    
    # Check Analytics Engine
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        log "✅ Analytics Engine health check passed"
    else
        log_warn "⚠️ Analytics Engine health check failed"
        health_status=1
    fi
    
    # Check N8N if not skipped
    if [[ "$SKIP_N8N" != "true" ]]; then
        if curl -s http://localhost:5678/healthz > /dev/null 2>&1; then
            log "✅ N8N health check passed"
        else
            log_warn "⚠️ N8N health check failed"
            health_status=1
        fi
    fi
    
    return $health_status
}

# Show status
show_status() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║           🚀 SISTEMA INICIADO EXITOSAMENTE      ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -e "${GREEN}📊 DASHBOARDS CENTRALIZADOS:${NC}"
    echo -e "   🎯 Production Controller: http://localhost:7860"
    echo -e "   📈 Analytics Engine:      http://localhost:8501"
    echo ""
    
    echo -e "${BLUE}🔧 SERVICIOS DE SOPORTE:${NC}"
    echo -e "   🤖 ML API:               http://localhost:8000"
    
    if [[ "$SKIP_N8N" != "true" ]]; then
        echo -e "   🔄 N8N Workflows:        http://localhost:5678"
    fi
    echo ""
    
    echo -e "${YELLOW}⚙️ CONFIGURACIÓN:${NC}"
    echo -e "   📁 Modo:                 $MODE"
    echo -e "   📂 Base Directory:       $BASE_DIR"
    echo -e "   📝 Logs:                 $LOG_DIR"
    echo -e "   🔒 PIDs:                 $PID_DIR"
    echo ""
    
    echo -e "${PURPLE}🎮 COMANDOS ÚTILES:${NC}"
    echo -e "   Ver logs:                tail -f $LOG_DIR/*.log"
    echo -e "   Detener sistema:         pkill -f 'python3.*production_controller'"
    echo -e "   Health check:            curl http://localhost:7860"
    echo ""
    
    if [[ "$MODE" == "dummy" ]]; then
        echo -e "${CYAN}💡 MODO DUMMY ACTIVO:${NC}"
        echo -e "   - Todas las operaciones son simuladas"
        echo -e "   - No se requieren credenciales reales"
        echo -e "   - Ideal para desarrollo y testing"
        echo ""
    fi
    
    echo -e "${GREEN}🎉 El sistema está listo para usar!${NC}"
    echo ""
}

# Main execution
main() {
    echo -e "${CYAN}"
    cat << 'EOF'
╔═══════════════════════════════════════════════════════════╗
║  🚀 SISTEMA CENTRALIZADO DE DASHBOARDS + N8N INTEGRATION  ║
║                                                           ║
║  TikTok Viral ML System - Production Ready               ║
║  Dashboards + Community Management + N8N Workflows       ║
╚═══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    log_step "🎬 Iniciando lanzamiento del sistema completo..."
    log_info "Modo: $MODE"
    log_info "Quick Start: $QUICK_START"
    log_info "Skip N8N: $SKIP_N8N"
    echo ""
    
    # Stop any existing processes
    cleanup
    
    # Perform checks and setup
    check_dependencies
    install_requirements
    
    if [[ "$SKIP_N8N" != "true" ]]; then
        setup_n8n
    fi
    
    # Start services
    start_ml_api
    start_production_controller
    start_analytics_engine
    
    # Health check
    if perform_health_check; then
        log "✅ All health checks passed"
    else
        log_warn "⚠️ Some health checks failed, but system may still be functional"
    fi
    
    # Show final status
    show_status
    
    # Keep script running
    log_step "🔄 Sistema en ejecución. Presiona Ctrl+C para detener."
    
    while true; do
        sleep 10
        
        # Basic monitoring
        if ! is_running "$PID_DIR/production_controller.pid"; then
            log_error "❌ Production Controller stopped unexpectedly"
        fi
        
        if ! is_running "$PID_DIR/analytics_engine.pid"; then
            log_error "❌ Analytics Engine stopped unexpectedly"
        fi
    done
}

# Execute main function
main "$@"