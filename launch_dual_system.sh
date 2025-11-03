#!/bin/bash
"""
Lanzador del Sistema Dual: Gradio (Triggers) + Streamlit (COCO/YOLO)
"""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de logging
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

# Directorio del proyecto
PROJECT_DIR="/workspaces/master"
cd "$PROJECT_DIR" || exit 1

# Archivos PID
GRADIO_PID_FILE="$PROJECT_DIR/.gradio.pid"
STREAMLIT_PID_FILE="$PROJECT_DIR/.streamlit_coco.pid"
ML_API_PID_FILE="$PROJECT_DIR/.ml_api.pid"

# Función para verificar si un proceso está corriendo
is_process_running() {
    local pid_file=$1
    if [[ -f "$pid_file" ]]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$pid_file"
            return 1
        fi
    fi
    return 1
}

# Función para detener un proceso
stop_process() {
    local name=$1
    local pid_file=$2
    
    if is_process_running "$pid_file"; then
        local pid=$(cat "$pid_file")
        log_warning "Deteniendo $name (PID: $pid)..."
        kill "$pid" 2>/dev/null
        sleep 2
        
        if ps -p "$pid" > /dev/null 2>&1; then
            log_warning "Forzando terminación de $name..."
            kill -9 "$pid" 2>/dev/null
        fi
        
        rm -f "$pid_file"
        log_success "$name detenido"
    else
        log_info "$name no está corriendo"
    fi
}

# Función para iniciar Gradio Trigger Manager
start_gradio() {
    log_info "Iniciando Gradio Trigger Manager..."
    
    if is_process_running "$GRADIO_PID_FILE"; then
        log_warning "Gradio ya está corriendo"
        return
    fi
    
    # Asegurar que el directorio de datos existe
    mkdir -p "$PROJECT_DIR/data"
    
    # Iniciar Gradio en background
    python3 "$PROJECT_DIR/gradio_trigger_manager.py" > "$PROJECT_DIR/logs/gradio.log" 2>&1 &
    local gradio_pid=$!
    
    # Guardar PID
    echo "$gradio_pid" > "$GRADIO_PID_FILE"
    
    # Esperar a que inicie
    sleep 3
    
    if is_process_running "$GRADIO_PID_FILE"; then
        log_success "Gradio Trigger Manager iniciado (PID: $gradio_pid)"
        log_info "🌐 Gradio URL: http://localhost:7860"
    else
        log_error "Error iniciando Gradio Trigger Manager"
        rm -f "$GRADIO_PID_FILE"
    fi
}

# Función para iniciar Streamlit COCO Analytics
start_streamlit() {
    log_info "Iniciando Streamlit COCO Analytics..."
    
    if is_process_running "$STREAMLIT_PID_FILE"; then
        log_warning "Streamlit COCO ya está corriendo"
        return
    fi
    
    # Asegurar que el directorio de datos existe
    mkdir -p "$PROJECT_DIR/data"
    
    # Iniciar Streamlit en background
    streamlit run "$PROJECT_DIR/streamlit_coco_analytics.py" --server.port 8501 --server.address 0.0.0.0 > "$PROJECT_DIR/logs/streamlit_coco.log" 2>&1 &
    local streamlit_pid=$!
    
    # Guardar PID
    echo "$streamlit_pid" > "$STREAMLIT_PID_FILE"
    
    # Esperar a que inicie
    sleep 5
    
    if is_process_running "$STREAMLIT_PID_FILE"; then
        log_success "Streamlit COCO Analytics iniciado (PID: $streamlit_pid)"
        log_info "🌐 Streamlit URL: http://localhost:8501"
    else
        log_error "Error iniciando Streamlit COCO Analytics"
        rm -f "$STREAMLIT_PID_FILE"
    fi
}

# Función para iniciar ML API
start_ml_api() {
    log_info "Iniciando ML API..."
    
    if is_process_running "$ML_API_PID_FILE"; then
        log_warning "ML API ya está corriendo"
        return
    fi
    
    # Verificar que existe el archivo de la API
    if [[ ! -f "$PROJECT_DIR/ml_core/api/main.py" ]]; then
        log_error "No se encuentra ml_core/api/main.py"
        return
    fi
    
    # Iniciar ML API desde el directorio raíz
    cd "$PROJECT_DIR"
    export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"
    uvicorn ml_core.api.main:app --host 0.0.0.0 --port 8000 > "$PROJECT_DIR/logs/ml_api.log" 2>&1 &
    local api_pid=$!
    
    # Guardar PID
    echo "$api_pid" > "$ML_API_PID_FILE"
    
    # Esperar a que inicie
    sleep 3
    
    if is_process_running "$ML_API_PID_FILE"; then
        log_success "ML API iniciada (PID: $api_pid)"
        log_info "🌐 API URL: http://localhost:8000"
    else
        log_error "Error iniciando ML API"
        rm -f "$ML_API_PID_FILE"
    fi
}

# Función para mostrar estado
show_status() {
    echo
    log_info "Estado de los Servicios:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Gradio Status
    if is_process_running "$GRADIO_PID_FILE"; then
        local gradio_pid=$(cat "$GRADIO_PID_FILE")
        log_success "🎯 Gradio Trigger Manager (PID: $gradio_pid) - http://localhost:7860"
    else
        log_error "🎯 Gradio Trigger Manager - Detenido"
    fi
    
    # Streamlit Status  
    if is_process_running "$STREAMLIT_PID_FILE"; then
        local streamlit_pid=$(cat "$STREAMLIT_PID_FILE")
        log_success "📊 Streamlit COCO Analytics (PID: $streamlit_pid) - http://localhost:8501"
    else
        log_error "📊 Streamlit COCO Analytics - Detenido"
    fi
    
    # ML API Status
    if is_process_running "$ML_API_PID_FILE"; then
        local api_pid=$(cat "$ML_API_PID_FILE")
        log_success "🤖 ML API (PID: $api_pid) - http://localhost:8000"
    else
        log_error "🤖 ML API - Detenida"
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Verificar puertos
    log_info "Puertos en uso:"
    netstat -tlnp 2>/dev/null | grep -E ":(7860|8501|8000)" | while read line; do
        echo "  $line"
    done
    echo
}

# Función principal
main() {
    echo "🎯 TikTok Viral ML System - Lanzador Dual"
    echo "=========================================="
    
    # Crear directorio de logs si no existe
    mkdir -p "$PROJECT_DIR/logs"
    
    case "${1:-start}" in
        "start")
            log_info "Iniciando todos los servicios..."
            start_ml_api
            start_gradio
            start_streamlit
            show_status
            ;;
            
        "stop")
            log_info "Deteniendo todos los servicios..."
            stop_process "Gradio Trigger Manager" "$GRADIO_PID_FILE"
            stop_process "Streamlit COCO Analytics" "$STREAMLIT_PID_FILE"
            stop_process "ML API" "$ML_API_PID_FILE"
            log_success "Todos los servicios detenidos"
            ;;
            
        "restart")
            log_info "Reiniciando todos los servicios..."
            stop_process "Gradio Trigger Manager" "$GRADIO_PID_FILE"
            stop_process "Streamlit COCO Analytics" "$STREAMLIT_PID_FILE"
            stop_process "ML API" "$ML_API_PID_FILE"
            sleep 2
            start_ml_api
            start_gradio
            start_streamlit
            show_status
            ;;
            
        "status")
            show_status
            ;;
            
        "gradio")
            start_gradio
            ;;
            
        "streamlit")
            start_streamlit
            ;;
            
        "api")
            start_ml_api
            ;;
            
        "logs")
            service="${2:-all}"
            case "$service" in
                "gradio")
                    tail -f "$PROJECT_DIR/logs/gradio.log"
                    ;;
                "streamlit")
                    tail -f "$PROJECT_DIR/logs/streamlit_coco.log"
                    ;;
                "api")
                    tail -f "$PROJECT_DIR/logs/ml_api.log"
                    ;;
                "all"|*)
                    log_info "Mostrando logs combinados (Ctrl+C para salir):"
                    tail -f "$PROJECT_DIR/logs"/*.log 2>/dev/null
                    ;;
            esac
            ;;
            
        "help"|"-h"|"--help")
            echo
            echo "Uso: $0 [comando]"
            echo
            echo "Comandos:"
            echo "  start     - Iniciar todos los servicios (por defecto)"
            echo "  stop      - Detener todos los servicios"
            echo "  restart   - Reiniciar todos los servicios"
            echo "  status    - Mostrar estado de los servicios"
            echo "  gradio    - Iniciar solo Gradio Trigger Manager"
            echo "  streamlit - Iniciar solo Streamlit COCO Analytics"
            echo "  api       - Iniciar solo ML API"
            echo "  logs [service] - Mostrar logs (gradio|streamlit|api|all)"
            echo "  help      - Mostrar esta ayuda"
            echo
            echo "URLs de acceso:"
            echo "  🎯 Gradio Trigger Manager:  http://localhost:7860"
            echo "  📊 Streamlit COCO Analytics: http://localhost:8501"
            echo "  🤖 ML API:                   http://localhost:8000"
            echo
            ;;
            
        *)
            log_error "Comando desconocido: $1"
            log_info "Usa '$0 help' para ver los comandos disponibles"
            exit 1
            ;;
    esac
}

# Ejecutar función principal con todos los argumentos
main "$@"