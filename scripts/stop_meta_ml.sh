#!/bin/bash

# 🧠 Meta ML System - Stop Script
# Detiene todos los servicios del sistema Meta ML

echo "🛑 DETENIENDO SISTEMA META ML..."
echo "=================================="

# Función para detener servicio
stop_service() {
    local service_name=$1
    local pid_file="logs/${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🛑 Deteniendo $service_name (PID: $pid)..."
            kill "$pid"
            
            # Esperar a que termine
            local count=0
            while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
                sleep 1
                ((count++))
            done
            
            if kill -0 "$pid" 2>/dev/null; then
                echo "⚠️ Force killing $service_name..."
                kill -9 "$pid"
            fi
            
            rm -f "$pid_file"
            echo "✅ $service_name detenido"
        else
            echo "⚠️ $service_name no estaba corriendo"
            rm -f "$pid_file"
        fi
    else
        echo "⚠️ No se encontró PID file para $service_name"
    fi
}

# Detener servicios
stop_service "meta-ml-api"
stop_service "meta-ml-dashboard"

# Limpiar procesos huérfanos
echo ""
echo "🧹 Limpiando procesos..."

# Matar procesos Python relacionados con Meta ML
pkill -f "sistema_meta_ml" 2>/dev/null || true
pkill -f "dashboard_meta_ml" 2>/dev/null || true
pkill -f "uvicorn.*8006" 2>/dev/null || true
pkill -f "streamlit.*8501" 2>/dev/null || true

# Verificar que los puertos estén libres
echo ""
echo "🔍 Verificando puertos..."

if lsof -ti:8006 > /dev/null 2>&1; then
    echo "⚠️ Puerto 8006 aún ocupado"
    lsof -ti:8006 | xargs kill -9 2>/dev/null || true
else
    echo "✅ Puerto 8006 libre"
fi

if lsof -ti:8501 > /dev/null 2>&1; then
    echo "⚠️ Puerto 8501 aún ocupado"
    lsof -ti:8501 | xargs kill -9 2>/dev/null || true
else
    echo "✅ Puerto 8501 libre"
fi

echo ""
echo "✅ SISTEMA META ML DETENIDO COMPLETAMENTE"
echo "=================================="
echo ""
echo "Para reiniciar:"
echo "  ./scripts/start_meta_ml.sh"