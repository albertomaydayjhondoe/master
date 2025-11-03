#!/bin/bash

# 🎯 TikTok Viral ML System - Ejecutor Local Completo
# ===================================================
# Script para hacer el sistema plenamente ejecutable y operativo en local

set -e  # Exit on any error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_colored() {
    echo -e "${1}${2}${NC}"
}

# Header
print_colored $PURPLE "🎯 TikTok Viral ML System - Ejecutor Local Completo"
print_colored $PURPLE "===================================================="
echo ""

# Función para verificar comando
check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        print_colored $GREEN "✅ $1 está disponible"
        return 0
    else
        print_colored $RED "❌ $1 no está disponible"
        return 1
    fi
}

# Función para verificar Python package
check_python_package() {
    if python -c "import $1" 2>/dev/null; then
        print_colored $GREEN "✅ $1 (Python) está disponible"
        return 0
    else
        print_colored $YELLOW "⚠️  $1 (Python) no está disponible"
        return 1
    fi
}

# Función para crear PID file
create_pid_file() {
    local service_name=$1
    local pid=$2
    echo $pid > "/tmp/tiktok_${service_name}.pid"
    print_colored $GREEN "📝 PID file creado para $service_name: $pid"
}

# Función para verificar si servicio está corriendo
is_service_running() {
    local service_name=$1
    local pid_file="/tmp/tiktok_${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            print_colored $GREEN "✅ $service_name está corriendo (PID: $pid)"
            return 0
        else
            rm -f "$pid_file"
            print_colored $YELLOW "⚠️  $service_name no está corriendo (PID file obsoleto eliminado)"
            return 1
        fi
    else
        print_colored $YELLOW "⚠️  $service_name no está corriendo"
        return 1
    fi
}

# Función para detener servicio
stop_service() {
    local service_name=$1
    local pid_file="/tmp/tiktok_${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null
            rm -f "$pid_file"
            print_colored $GREEN "🛑 $service_name detenido (PID: $pid)"
        else
            rm -f "$pid_file"
            print_colored $YELLOW "⚠️  $service_name ya estaba detenido"
        fi
    else
        print_colored $YELLOW "⚠️  $service_name no estaba corriendo"
    fi
}

# Función para instalar dependencias
install_dependencies() {
    print_colored $CYAN "📦 Verificando e instalando dependencias..."
    
    # Core dependencies
    if ! check_python_package "streamlit"; then
        print_colored $YELLOW "📥 Instalando Streamlit y dependencias..."
        pip install -r requirements-streamlit.txt || {
            print_colored $RED "❌ Error instalando dependencias de Streamlit"
            exit 1
        }
    fi
    
    # Verificar dependencias básicas
    if ! check_python_package "fastapi"; then
        print_colored $YELLOW "📥 Instalando dependencias básicas..."
        pip install fastapi uvicorn httpx aiohttp requests pandas numpy || {
            print_colored $RED "❌ Error instalando dependencias básicas"
            exit 1
        }
    fi
    
    print_colored $GREEN "✅ Todas las dependencias están disponibles"
}

# Función para verificar estructura
verify_structure() {
    print_colored $CYAN "📁 Verificando estructura del proyecto..."
    
    local required_files=(
        "streamlit_dashboard.py"
        "validate_multibranch.py"
        "validate_helper.sh"
        "requirements-streamlit.txt"
        "launch_dashboard.sh"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            print_colored $GREEN "✅ $file"
        else
            print_colored $RED "❌ $file faltante"
            return 1
        fi
    done
    
    print_colored $GREEN "✅ Estructura del proyecto verificada"
}

# Función para hacer archivos ejecutables
make_executable() {
    print_colored $CYAN "🔧 Haciendo archivos ejecutables..."
    
    local scripts=(
        "streamlit_dashboard.py"
        "validate_multibranch.py"
        "validate_helper.sh"
        "launch_dashboard.sh"
        "install_dependencies.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [ -f "$script" ]; then
            chmod +x "$script"
            print_colored $GREEN "✅ $script es ejecutable"
        fi
    done
}

# Función para iniciar Streamlit Dashboard
start_streamlit() {
    local port=${1:-8501}
    local mode=${2:-dummy}
    
    print_colored $CYAN "🚀 Iniciando Streamlit Dashboard..."
    
    # Configurar modo dummy si se especifica
    if [ "$mode" = "dummy" ]; then
        export DUMMY_MODE=true
        print_colored $CYAN "🎭 Modo dummy activado"
    else
        unset DUMMY_MODE
        print_colored $CYAN "🔧 Modo producción activado"
    fi
    
    # Verificar si el puerto está en uso
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_colored $YELLOW "⚠️  Puerto $port ya está en uso. Intentando detener..."
        pkill -f "streamlit.*$port" 2>/dev/null || true
        sleep 2
    fi
    
    # Iniciar Streamlit en background
    nohup streamlit run streamlit_dashboard.py \
        --server.port $port \
        --server.headless true \
        --server.runOnSave false \
        --browser.gatherUsageStats false \
        > /tmp/streamlit_dashboard.log 2>&1 &
    
    local streamlit_pid=$!
    create_pid_file "streamlit" $streamlit_pid
    
    # Esperar a que inicie
    print_colored $YELLOW "⏳ Esperando a que Streamlit inicie..."
    sleep 5
    
    # Verificar que esté corriendo
    if kill -0 $streamlit_pid 2>/dev/null; then
        print_colored $GREEN "✅ Streamlit Dashboard iniciado correctamente"
        print_colored $WHITE "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        print_colored $GREEN "🌐 URL Local:    http://localhost:$port"
        print_colored $GREEN "🌍 URL Red:      http://$(hostname -I | awk '{print $1}'):$port"
        if [ -n "$CODESPACE_NAME" ]; then
            print_colored $GREEN "📱 Codespace:    https://$CODESPACE_NAME-$port.app.github.dev"
        fi
        print_colored $WHITE "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        return 0
    else
        print_colored $RED "❌ Error iniciando Streamlit Dashboard"
        print_colored $YELLOW "📝 Log:"
        tail -20 /tmp/streamlit_dashboard.log 2>/dev/null || echo "No hay logs disponibles"
        return 1
    fi
}

# Función para iniciar ML API (opcional)
start_ml_api() {
    print_colored $CYAN "🤖 Iniciando ML API..."
    
    # Verificar si existe el archivo principal de la API
    if [ -f "ml_core/api/main.py" ]; then
        # Verificar si el puerto 8000 está libre
        if ! lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
            # Iniciar API en background
            nohup python -m uvicorn ml_core.api.main:app \
                --host 0.0.0.0 \
                --port 8000 \
                --reload \
                > /tmp/ml_api.log 2>&1 &
            
            local api_pid=$!
            create_pid_file "ml_api" $api_pid
            
            sleep 3
            if kill -0 $api_pid 2>/dev/null; then
                print_colored $GREEN "✅ ML API iniciada en http://localhost:8000"
            else
                print_colored $YELLOW "⚠️  ML API no pudo iniciarse (modo dummy, opcional)"
            fi
        else
            print_colored $YELLOW "⚠️  Puerto 8000 ya está en uso"
        fi
    else
        print_colored $YELLOW "⚠️  ML API no disponible (modo dummy, opcional)"
    fi
}

# Función de status
show_status() {
    print_colored $CYAN "📊 Estado de los Servicios:"
    echo ""
    
    is_service_running "streamlit" && echo "" || echo ""
    is_service_running "ml_api" && echo "" || echo ""
    
    # Mostrar puertos en uso
    print_colored $CYAN "🌐 Puertos en uso:"
    netstat -tlnp 2>/dev/null | grep -E ':(8501|8000|5678)' || echo "   No hay puertos activos"
    echo ""
}

# Función para detener todos los servicios
stop_all() {
    print_colored $CYAN "🛑 Deteniendo todos los servicios..."
    
    stop_service "streamlit"
    stop_service "ml_api"
    
    # Limpiar procesos residuales
    pkill -f "streamlit" 2>/dev/null || true
    pkill -f "uvicorn.*ml_core" 2>/dev/null || true
    
    print_colored $GREEN "✅ Todos los servicios detenidos"
}

# Función de ayuda
show_help() {
    print_colored $WHITE "🔧 USO:"
    echo "  $0 start [puerto] [modo]    # Iniciar sistema completo"
    echo "  $0 stop                     # Detener todos los servicios"
    echo "  $0 status                   # Ver estado de servicios"
    echo "  $0 restart                  # Reiniciar sistema completo"
    echo "  $0 install                  # Instalar dependencias"
    echo "  $0 validate                 # Validar sistema"
    echo ""
    print_colored $WHITE "🎯 EJEMPLOS:"
    echo "  $0 start                    # Iniciar en puerto 8501, modo dummy"
    echo "  $0 start 8502               # Iniciar en puerto 8502, modo dummy"
    echo "  $0 start 8501 prod          # Iniciar en modo producción"
    echo "  $0 restart                  # Reiniciar completamente"
}

# Función principal
main() {
    local command=${1:-start}
    local port=${2:-8501}
    local mode=${3:-dummy}
    
    case $command in
        "start")
            print_colored $GREEN "🚀 Iniciando TikTok Viral ML System..."
            verify_structure || exit 1
            install_dependencies || exit 1
            make_executable
            start_streamlit $port $mode || exit 1
            start_ml_api
            echo ""
            print_colored $GREEN "🎉 Sistema iniciado correctamente!"
            print_colored $CYAN "💡 Usa '$0 status' para ver el estado"
            print_colored $CYAN "💡 Usa '$0 stop' para detener"
            ;;
        "stop")
            stop_all
            ;;
        "status")
            show_status
            ;;
        "restart")
            print_colored $CYAN "🔄 Reiniciando sistema..."
            stop_all
            sleep 2
            main start $port $mode
            ;;
        "install")
            install_dependencies
            ;;
        "validate")
            print_colored $CYAN "🔍 Validando sistema..."
            if [ -f "validate_multibranch.py" ]; then
                python validate_multibranch.py --dummy-mode
            else
                print_colored $RED "❌ Validador no encontrado"
            fi
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            print_colored $RED "❌ Comando no reconocido: $command"
            show_help
            exit 1
            ;;
    esac
}

# Trap para cleanup al salir
trap 'echo ""; print_colored $YELLOW "⏹️  Script interrumpido"' INT TERM

# Ejecutar función principal
main "$@"