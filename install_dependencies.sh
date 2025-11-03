#!/bin/bash

# ===================================================================
# INSTALADOR AUTOMÁTICO DE DEPENDENCIAS - TikTok Viral ML System
# ===================================================================
# Script inteligente que detecta la rama y usa el requirements.txt correcto
# Soporte para todas las ramas: MAIN, META, TELE + modo DUMMY

set -e  # Exit on error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function para logging con colores
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Banner
echo ""
log_header "🚀 TikTok Viral ML System - Instalador Automático de Dependencias"
log_header "================================================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "requirements.txt" ]; then
    log_error "No se encontró requirements.txt. Ejecuta este script desde el directorio raíz del proyecto."
    exit 1
fi

# Detectar rama actual
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
log_info "Rama actual detectada: $CURRENT_BRANCH"

# Verificar Python
python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1,2 || echo "not_found")
if [ "$python_version" = "not_found" ]; then
    log_error "Python 3 no encontrado. Instala Python 3.9-3.11"
    exit 1
else
    log_info "Python version: $python_version"
    
    # Verificar versión compatible
    if [[ "$python_version" < "3.9" ]] || [[ "$python_version" > "3.11" ]]; then
        log_warning "Python $python_version puede no ser compatible. Recomendado: 3.9-3.11"
    fi
fi

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    log_error "pip3 no encontrado. Instala pip."
    exit 1
fi

# Determinar requirements file basado en rama o flag
REQUIREMENTS_FILE=""
INSTALL_MODE=""

# Check for command line arguments
if [ "$1" = "--dummy" ] || [ "$1" = "-d" ]; then
    REQUIREMENTS_FILE="requirements-dummy.txt"
    INSTALL_MODE="DUMMY"
elif [ "$1" = "--dev" ]; then
    REQUIREMENTS_FILE="requirements-dev.txt" 
    INSTALL_MODE="DEVELOPMENT"
elif [ "$1" = "--rama" ] || [ "$1" = "-r" ]; then
    REQUIREMENTS_FILE="requirements-rama.txt"
    INSTALL_MODE="RAMA MAIN"
elif [ "$1" = "--meta" ] || [ "$1" = "-m" ]; then
    REQUIREMENTS_FILE="requirements-meta.txt"
    INSTALL_MODE="RAMA META"
elif [ "$1" = "--tele" ] || [ "$1" = "-t" ]; then
    REQUIREMENTS_FILE="requirements-tele.txt"
    INSTALL_MODE="RAMA TELE"
else
    # Auto-detect based on branch name
    case "$CURRENT_BRANCH" in
        "main"|"rama")
            REQUIREMENTS_FILE="requirements-rama.txt"
            INSTALL_MODE="RAMA MAIN (Auto-detected)"
            ;;
        "meta")
            REQUIREMENTS_FILE="requirements-meta.txt"
            INSTALL_MODE="RAMA META (Auto-detected)"
            ;;
        "tele"|"telegram")
            REQUIREMENTS_FILE="requirements-tele.txt"
            INSTALL_MODE="RAMA TELE (Auto-detected)"
            ;;
        *)
            log_warning "Rama '$CURRENT_BRANCH' no reconocida. Usando modo DUMMY por seguridad."
            REQUIREMENTS_FILE="requirements-dummy.txt"
            INSTALL_MODE="DUMMY (Fallback)"
            ;;
    esac
fi

# Verificar que el archivo requirements existe
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    log_error "Archivo $REQUIREMENTS_FILE no encontrado."
    exit 1
fi

log_info "Modo de instalación: $INSTALL_MODE"
log_info "Archivo requirements: $REQUIREMENTS_FILE"

# Mostrar información del modo seleccionado
echo ""
case "$REQUIREMENTS_FILE" in
    "requirements-rama.txt")
        log_header "📊 RAMA MAIN - TikTok ML + Device Farm + Módulo 7"
        echo "   ▶ Incluye: YOLOv8, Ultralytics, Device automation"
        echo "   ▶ Espacio requerido: ~10GB (modelos ML)"
        echo "   ▶ GPU recomendado para mejor performance"
        ;;
    "requirements-meta.txt")
        log_header "🌐 RAMA META - Meta Ads + GoLogin + Browser Automation"
        echo "   ▶ Incluye: Facebook Business API, Selenium, Playwright"
        echo "   ▶ Espacio requerido: ~2GB"
        echo "   ▶ Requiere configuración de proxies y GoLogin"
        ;;
    "requirements-tele.txt")
        log_header "💬 RAMA TELE - Telegram Like4Like + Social Networks"
        echo "   ▶ Incluye: Telegram APIs, Social automation"
        echo "   ▶ Espacio requerido: ~3GB"
        echo "   ▶ Requiere tokens de Telegram"
        ;;
    "requirements-dummy.txt")
        log_header "🧪 DUMMY MODE - Testing y Desarrollo"
        echo "   ▶ Sin dependencias pesadas"
        echo "   ▶ Espacio requerido: ~500MB"
        echo "   ▶ Perfecto para testing y CI/CD"
        ;;
    "requirements-dev.txt")
        log_header "🛠️ DEVELOPMENT MODE - Herramientas de desarrollo"
        echo "   ▶ Testing, linting, formateo"
        echo "   ▶ Jupyter, debugging tools"
        ;;
esac

echo ""
read -p "¿Continuar con la instalación? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Instalación cancelada."
    exit 0
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    log_info "Creando entorno virtual..."
    python3 -m venv venv
    log_success "Entorno virtual creado: venv/"
fi

# Activar entorno virtual
log_info "Activando entorno virtual..."
source venv/bin/activate

# Upgrade pip
log_info "Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias core primero
log_info "Instalando dependencias compartidas..."
pip install -r requirements.txt

# Instalar dependencias específicas
log_info "Instalando dependencias específicas: $REQUIREMENTS_FILE"
pip install -r "$REQUIREMENTS_FILE"

# Instalaciones especiales según el modo
if [ "$REQUIREMENTS_FILE" = "requirements-rama.txt" ]; then
    log_info "Descargando modelos YOLOv8..."
    python3 -c "
import ultralytics
from ultralytics import YOLO
print('Descargando YOLOv8n...')
model = YOLO('yolov8n.pt')
print('Descargando YOLOv8s...')  
model = YOLO('yolov8s.pt')
print('✅ Modelos YOLOv8 descargados')
"
fi

# Crear archivos de configuración si no existen
if [ ! -f ".env" ]; then
    log_info "Creando archivo .env desde template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        cat > .env << EOF
# Configuración básica - TikTok Viral ML System
DUMMY_MODE=true
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./data/app.db

# Configura estos valores según tu rama:
# RAMA META: Facebook, GoLogin tokens
# RAMA TELE: Telegram API credentials  
# RAMA MAIN: Device farm, YOLOv8 configs
EOF
    fi
    log_success "Archivo .env creado. Revisa y configura las variables necesarias."
fi

# Crear directorios necesarios
log_info "Creando directorios del proyecto..."
mkdir -p data/{models,video_clips,mock_databases}
mkdir -p logs
mkdir -p config/secrets

# Verificar instalación
log_info "Verificando instalación..."
python3 -c "
import fastapi
import uvicorn
import pandas as pd
import numpy as np
print('✅ Dependencias básicas verificadas')
"

if [ "$REQUIREMENTS_FILE" = "requirements-rama.txt" ]; then
    python3 -c "
import torch
import ultralytics
print(f'✅ PyTorch: {torch.__version__}')
print(f'✅ Ultralytics: {ultralytics.__version__}')
print(f'✅ CUDA disponible: {torch.cuda.is_available()}')
"
fi

echo ""
log_success "🎉 Instalación completada exitosamente!"
echo ""
log_info "📋 Próximos pasos:"
echo "   1. Revisa y configura el archivo .env"
echo "   2. Ejecuta el sistema: ./start.sh"
echo "   3. Accede a la API: http://localhost:8000"
echo ""

# Instrucciones específicas por rama
case "$REQUIREMENTS_FILE" in
    "requirements-rama.txt")
        log_info "🤖 Instrucciones adicionales RAMA MAIN:"
        echo "   • Conecta dispositivos Android (ADB)"
        echo "   • Configura CUDA si tienes GPU"
        echo "   • Coloca videos en data/video_clips/"
        ;;
    "requirements-meta.txt")
        log_info "🌐 Instrucciones adicionales RAMA META:"
        echo "   • Configura Facebook Business API tokens"
        echo "   • Instala y configura GoLogin profiles"
        echo "   • Configura proxies residenciales"
        ;;
    "requirements-tele.txt")
        log_info "💬 Instrucciones adicionales RAMA TELE:"
        echo "   • Obtén Telegram API credentials"
        echo "   • Configura grupos Like4Like"
        echo "   • Ajusta configuración de engagement"
        ;;
    "requirements-dummy.txt")
        log_info "🧪 DUMMY MODE activado:"
        echo "   • Todas las operaciones son simuladas"
        echo "   • No requiere APIs externas"
        echo "   • Perfecto para desarrollo y testing"
        ;;
esac

echo ""
log_info "💡 Para cambiar de rama: git checkout <rama> && ./install_dependencies.sh"
log_info "📚 Documentación completa: docs/setup/"
echo ""

# Mostrar comandos útiles
log_header "🔧 Comandos útiles:"
echo "   Activar entorno: source venv/bin/activate"
echo "   Ejecutar tests:  pytest tests/ -v"
echo "   Modo dummy:      ./install_dependencies.sh --dummy"
echo "   Logs del API:    tail -f logs/api.log"
echo ""

log_success "Sistema listo para usar! 🚀"