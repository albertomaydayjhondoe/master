#!/bin/bash

# 🎯 TikTok Viral ML System - Auto Start Local
# ============================================
# Script que inicia automáticamente todo el sistema en local

# Configuración por defecto
export DUMMY_MODE=true
export STREAMLIT_PORT=8501
export ML_API_PORT=8000

# Colores
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}🎯 TikTok Viral ML System - Auto Start${NC}"
echo -e "${CYAN}=====================================${NC}"
echo ""

# Verificar dependencias y instalar si es necesario
echo -e "${CYAN}📦 Verificando dependencias...${NC}"
if ! python -c "import streamlit" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Instalando Streamlit...${NC}"
    pip install -q streamlit pandas plotly psutil requests httpx numpy pydantic
fi

# Hacer scripts ejecutables
chmod +x *.sh *.py 2>/dev/null

# Iniciar con el ejecutor local
echo -e "${GREEN}🚀 Iniciando sistema completo...${NC}"
exec ./run_local.sh start
