#!/bin/bash

# 🎵 DISCOGRÁFICA ML SYSTEM - SETUP COMPLETO
# ==========================================

echo "🎵 CONFIGURANDO DISCOGRÁFICA ML SYSTEM"
echo "======================================"
echo ""

# Verificar directorio
if [[ ! -f "production_controller.py" ]]; then
    echo "❌ Error: Ejecutar desde el directorio raíz del proyecto"
    exit 1
fi

# Configurar variables de entorno para discográfica
export PROJECT_NAME="discografica-ml-system"
export SYSTEM_MODE="production"
export DUMMY_MODE="false"

echo "📋 CONFIGURACIÓN DEL SISTEMA:"
echo "- Proyecto: $PROJECT_NAME"
echo "- Modo: $SYSTEM_MODE"
echo "- Dummy Mode: $DUMMY_MODE"
echo ""

# 1. Configurar tokens interactivamente
echo "🔑 PASO 1: Configuración de Tokens"
echo "=================================="
if [[ -x "./setup_production_tokens.sh" ]]; then
    ./setup_production_tokens.sh
else
    echo "⚠️  setup_production_tokens.sh no encontrado o no ejecutable"
fi

echo ""

# 2. Validar configuración
echo "✅ PASO 2: Validación del Sistema"
echo "================================="
if [[ -x "./validate_tokens.sh" ]]; then
    ./validate_tokens.sh
else
    echo "⚠️  validate_tokens.sh no encontrado"
fi

echo ""

# 3. Instalar dependencias
echo "📦 PASO 3: Instalación de Dependencias"
echo "======================================"
if [[ -f "requirements.txt" ]]; then
    pip install -r requirements.txt
    echo "✅ Dependencias base instaladas"
fi

if [[ -f "requirements-ml.txt" ]]; then
    pip install -r requirements-ml.txt
    echo "✅ Dependencias ML instaladas"
fi

echo ""

# 4. Configurar base de datos
echo "🗄️  PASO 4: Configuración de Base de Datos"
echo "=========================================="
if [[ -f "database/init_db.py" ]]; then
    python database/init_db.py
    echo "✅ Base de datos inicializada"
fi

echo ""

# 5. Verificar modelos ML
echo "🧠 PASO 5: Verificación de Modelos ML"
echo "====================================="
if [[ -d "data/models" ]]; then
    echo "✅ Directorio de modelos encontrado"
    ls -la data/models/ | head -5
else
    echo "⚠️  Creando directorio de modelos..."
    mkdir -p data/models/production
    mkdir -p data/models/checkpoints
fi

echo ""

# 6. Lanzar sistema
echo "🚀 PASO 6: Lanzamiento del Sistema"
echo "=================================="
echo "Iniciando dashboards..."

# Lanzar Production Controller en background
if [[ -f "production_controller.py" ]]; then
    echo "🎮 Iniciando Production Controller (puerto 7860)..."
    nohup python production_controller.py > logs/production_controller.log 2>&1 &
    PROD_PID=$!
    echo "✅ Production Controller iniciado (PID: $PROD_PID)"
fi

# Esperar un momento
sleep 3

# Lanzar Analytics Engine en background
if [[ -f "analytics_engine.py" ]]; then
    echo "📊 Iniciando Analytics Engine (puerto 8501)..."
    nohup python analytics_engine.py > logs/analytics_engine.log 2>&1 &
    ANALYTICS_PID=$!
    echo "✅ Analytics Engine iniciado (PID: $ANALYTICS_PID)"
fi

echo ""

# 7. Información final
echo "🎵 DISCOGRÁFICA ML SYSTEM - ACTIVO 🚀"
echo "===================================="
echo ""
echo "📊 DASHBOARDS DISPONIBLES:"
echo "- 🎮 Production Controller: http://localhost:7860"
echo "- 📈 Analytics Engine: http://localhost:8501"
echo ""
echo "📋 PROCESOS ACTIVOS:"
[[ ! -z "$PROD_PID" ]] && echo "- Production Controller (PID: $PROD_PID)"
[[ ! -z "$ANALYTICS_PID" ]] && echo "- Analytics Engine (PID: $ANALYTICS_PID)"
echo ""
echo "📝 LOGS:"
echo "- Production: logs/production_controller.log"
echo "- Analytics: logs/analytics_engine.log"
echo ""
echo "🔄 PARA DETENER EL SISTEMA:"
echo "pkill -f 'python production_controller.py'"
echo "pkill -f 'python analytics_engine.py'"
echo ""
echo "🎵 ¡SISTEMA LISTO PARA CAMPAÑAS VIRALES! 🔥"
echo ""
echo "📱 PRÓXIMOS PASOS:"
echo "1. Abrir http://localhost:7860 (Production Controller)"
echo "2. Configurar tu primera campaña"
echo "3. ¡Presionar el BOTÓN ROJO para viralidad automática!"
echo ""
echo "🎤 ¡A HACER MÚSICA VIRAL! 🚀🎵"