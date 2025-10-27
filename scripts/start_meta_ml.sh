#!/bin/bash

# 🧠 Meta ML System - Start Script
# Lanza el sistema completo de Meta ML para optimización España-LATAM

echo "🧠 INICIANDO SISTEMA META ML..."
echo "=================================="

# Verificar Python
if ! command -v python &> /dev/null; then
    echo "❌ Python no encontrado. Instala Python 3.11+"
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv_meta_ml" ]; then
    echo "📦 Creando entorno virtual Meta ML..."
    python -m venv venv_meta_ml
fi

# Activar entorno virtual
echo "⚡ Activando entorno virtual..."
source venv_meta_ml/bin/activate

# Instalar dependencias
echo "📥 Instalando dependencias ML..."
pip install -q -r requirements.txt
pip install -q -r requirements-ml.txt

# Dependencias específicas Meta ML
pip install -q scikit-learn>=1.3.0 pandas>=2.0.0 numpy>=1.24.0 joblib>=1.3.0
pip install -q plotly>=5.15.0 streamlit>=1.25.0 asyncpg>=0.28.0

# Setup inicial del sistema
echo "🔧 Configurando sistema Meta ML..."
python scripts/setup_meta_ml.py

if [ $? -eq 0 ]; then
    echo "✅ Setup Meta ML completado"
else
    echo "❌ Error en setup Meta ML"
    exit 1
fi

# Función para lanzar servicios en background
launch_service() {
    local service_name=$1
    local command=$2
    local port=$3
    
    echo "🚀 Lanzando $service_name en puerto $port..."
    nohup $command > logs/${service_name}.log 2>&1 &
    echo $! > logs/${service_name}.pid
    
    # Verificar que el servicio esté corriendo
    sleep 3
    if kill -0 $(cat logs/${service_name}.pid) 2>/dev/null; then
        echo "✅ $service_name iniciado correctamente"
    else
        echo "❌ Error iniciando $service_name"
    fi
}

# Crear directorio de logs
mkdir -p logs

# 1. Lanzar API Meta ML
echo ""
echo "🤖 LANZANDO API META ML..."
launch_service "meta-ml-api" "python -m uvicorn ml_core.sistema_meta_ml:app --host 0.0.0.0 --port 8006" 8006

# 2. Lanzar Dashboard Meta ML
echo ""
echo "📊 LANZANDO DASHBOARD META ML..."
launch_service "meta-ml-dashboard" "streamlit run dashboard_meta_ml.py --server.port 8501 --server.headless true" 8501

# 3. Verificar servicios
echo ""
echo "🔍 VERIFICANDO SERVICIOS..."

sleep 5

# Health check API
if curl -s -f http://localhost:8006/health > /dev/null; then
    echo "✅ API Meta ML: http://localhost:8006 - ACTIVO"
else
    echo "❌ API Meta ML: ERROR"
fi

# Health check Dashboard
if curl -s -f http://localhost:8501 > /dev/null; then
    echo "✅ Dashboard Meta ML: http://localhost:8501 - ACTIVO"
else
    echo "❌ Dashboard Meta ML: ERROR"
fi

echo ""
echo "🎉 SISTEMA META ML INICIADO"
echo "=================================="
echo "🤖 API ML: http://localhost:8006"
echo "📊 Dashboard: http://localhost:8501" 
echo "📋 Logs: ./logs/"
echo ""
echo "🎯 READY FOR €400 META ADS CAMPAIGNS!"
echo ""
echo "Para detener:"
echo "  ./stop_meta_ml.sh"
echo ""
echo "Para monitorear:"
echo "  tail -f logs/meta-ml-api.log"
echo "  tail -f logs/meta-ml-dashboard.log"