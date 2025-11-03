#!/bin/bash

# 🎯 TikTok Viral ML System - Launcher Streamlit Dashboard
# ========================================================

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
print_colored $PURPLE "🎯 TikTok Viral ML System - Dashboard Universal"
print_colored $PURPLE "=============================================="
echo ""

# Verificar dependencias
print_colored $CYAN "🔍 Verificando dependencias de Streamlit..."

if ! python -c "import streamlit" 2>/dev/null; then
    print_colored $YELLOW "⚠️  Streamlit no encontrado. Instalando..."
    pip install -r requirements-streamlit.txt || {
        print_colored $RED "❌ Error instalando dependencias de Streamlit"
        exit 1
    }
    print_colored $GREEN "✅ Streamlit instalado correctamente"
else
    print_colored $GREEN "✅ Streamlit ya está instalado"
fi

# Verificar que el validador multiramas existe
if [ ! -f "validate_multibranch.py" ]; then
    print_colored $RED "❌ Error: validate_multibranch.py no encontrado"
    print_colored $YELLOW "   Asegúrate de ejecutar este script desde el directorio raíz del proyecto"
    exit 1
fi

# Verificar puerto
PORT=${1:-8501}
print_colored $BLUE "🌐 Puerto configurado: $PORT"

# Información del sistema
print_colored $WHITE "📋 Información del Sistema:"
echo "   🐍 Python: $(python --version)"
echo "   🌿 Rama Git: $(git branch --show-current 2>/dev/null || echo 'unknown')"
echo "   🎭 Modo Dummy: ${DUMMY_MODE:-false}"
echo "   💾 Directorio: $(pwd)"
echo ""

# Opciones de lanzamiento
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    print_colored $WHITE "🔧 USO:"
    echo "  ./launch_dashboard.sh [puerto]     # Lanzar en puerto específico (default: 8501)"
    echo "  ./launch_dashboard.sh --dev        # Modo desarrollo con auto-reload"
    echo "  ./launch_dashboard.sh --dummy      # Forzar modo dummy"
    echo "  ./launch_dashboard.sh --prod       # Forzar modo producción"
    echo "  ./launch_dashboard.sh --help       # Mostrar esta ayuda"
    echo ""
    print_colored $CYAN "🎯 EJEMPLOS:"
    echo "  ./launch_dashboard.sh              # Puerto 8501 por defecto"
    echo "  ./launch_dashboard.sh 8502         # Puerto 8502"
    echo "  ./launch_dashboard.sh --dummy      # Modo dummy forzado"
    exit 0
fi

# Configurar modo según argumentos
if [ "$1" = "--dummy" ]; then
    export DUMMY_MODE=true
    print_colored $CYAN "🎭 Modo dummy forzado"
    PORT=8501
elif [ "$1" = "--prod" ]; then
    unset DUMMY_MODE
    print_colored $CYAN "🔧 Modo producción forzado"
    PORT=8501
elif [ "$1" = "--dev" ]; then
    print_colored $CYAN "🔄 Modo desarrollo activado"
    PORT=8501
fi

# Mostrar información de acceso
print_colored $GREEN "🚀 Iniciando Dashboard Universal..."
print_colored $WHITE "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_colored $GREEN "🌐 URL Local:    http://localhost:$PORT"
print_colored $GREEN "🌍 URL Red:      http://$(hostname -I | awk '{print $1}'):$PORT"
print_colored $GREEN "📱 Codespace:    https://$CODESPACE_NAME-$PORT.app.github.dev"
print_colored $WHITE "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_colored $YELLOW "💡 FUNCIONALIDADES DEL DASHBOARD:"
echo "   🔍 Validación multi-ramas en tiempo real"
echo "   📦 Instalación automática de dependencias"
echo "   🎭 Toggle modo dummy/producción"
echo "   ⚡ Control de servicios integrado"
echo "   📈 Monitoreo y métricas avanzadas"
echo "   📝 Visualización de logs del sistema"
echo ""
print_colored $CYAN "⏹️  Presiona Ctrl+C para detener el dashboard"
echo ""

# Configurar argumentos de Streamlit
STREAMLIT_ARGS="--server.port $PORT --server.headless true"

# Modo desarrollo con auto-reload
if [ "$1" = "--dev" ]; then
    STREAMLIT_ARGS="$STREAMLIT_ARGS --server.runOnSave true --server.allowRunOnSave true"
fi

# Lanzar Streamlit
exec streamlit run streamlit_dashboard.py $STREAMLIT_ARGS