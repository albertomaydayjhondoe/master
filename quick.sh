#!/bin/bash

# 🎯 TikTok Viral ML System - Acceso Rápido Local
# ===============================================
# Un comando para acceder rápidamente al sistema

# Colores
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
WHITE='\033[1;37m'
NC='\033[0m'

echo -e "${CYAN}🎯 TikTok Viral ML System - Acceso Rápido${NC}"
echo -e "${CYAN}=========================================${NC}"
echo ""

# Función para mostrar URLs
show_urls() {
    echo -e "${WHITE}🌐 ACCESO AL SISTEMA:${NC}"
    echo -e "${GREEN}   📊 Dashboard:    http://localhost:8501${NC}"
    echo -e "${GREEN}   🤖 ML API:       http://localhost:8000${NC}"
    if [ -n "$CODESPACE_NAME" ]; then
        echo -e "${GREEN}   📱 Codespace:    https://$CODESPACE_NAME-8501.app.github.dev${NC}"
    fi
    echo ""
}

# Verificar si está corriendo
if ./run_local.sh status > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Sistema está corriendo${NC}"
    show_urls
    
    echo -e "${CYAN}🔧 COMANDOS DISPONIBLES:${NC}"
    echo "   ./quick.sh start     # Iniciar sistema"
    echo "   ./quick.sh stop      # Detener sistema"  
    echo "   ./quick.sh restart   # Reiniciar sistema"
    echo "   ./quick.sh validate  # Validar sistema"
    echo "   ./quick.sh logs      # Ver logs"
    echo ""
    
    # Abrir browser si se especifica
    if [ "$1" = "open" ] || [ "$1" = "browser" ]; then
        echo -e "${YELLOW}🌐 Abriendo navegador...${NC}"
        if command -v xdg-open >/dev/null 2>&1; then
            xdg-open "http://localhost:8501" 2>/dev/null &
        elif command -v open >/dev/null 2>&1; then
            open "http://localhost:8501" 2>/dev/null &
        else
            echo -e "${YELLOW}⚠️  No se pudo abrir navegador automáticamente${NC}"
            echo -e "${CYAN}   Accede manualmente a: http://localhost:8501${NC}"
        fi
    fi
    
else
    echo -e "${YELLOW}⚠️  Sistema no está corriendo${NC}"
    echo -e "${CYAN}🚀 ¿Quieres iniciarlo? (y/n)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        ./run_local.sh start
        show_urls
    fi
fi

# Comandos específicos
case "$1" in
    "start")
        ./run_local.sh start
        ;;
    "stop")
        ./run_local.sh stop
        ;;
    "restart")
        ./run_local.sh restart
        ;;
    "validate")
        python validate_multibranch.py --dummy-mode
        ;;
    "logs")
        echo -e "${CYAN}📝 Streamlit Logs:${NC}"
        tail -20 /tmp/streamlit_dashboard.log 2>/dev/null || echo "No logs disponibles"
        echo ""
        echo -e "${CYAN}📝 ML API Logs:${NC}"
        tail -20 /tmp/ml_api.log 2>/dev/null || echo "No logs disponibles"
        ;;
esac