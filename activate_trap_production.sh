#!/bin/bash
# 🎵 ACTIVAR MODO PRODUCCIÓN - ARTISTA TRAP
# =========================================
# Script para convertir sistema de dummy → producción completa

echo "🎯 ACTIVANDO MODO PRODUCCIÓN PARA ARTISTA TRAP"
echo "=============================================="
echo ""

# 1. CAMBIAR MODO DUMMY → PRODUCCIÓN
echo "📝 1. Configurando variables de entorno..."
export DUMMY_MODE=false
export ML_PRODUCTION_MODE=true
export TRAP_ARTIST_MODE=true

# Crear archivo .env para persistencia
cat > .env << EOF
# 🎵 Discográfica ML - Modo Producción Trap
DUMMY_MODE=false
ML_PRODUCTION_MODE=true
TRAP_ARTIST_MODE=true
ARTIST_GENRE=trap
CAMPAIGN_TYPE=viral_trap
N8N_WEBHOOK_URL=http://localhost:5678
META_ADS_API_TOKEN=your_meta_token_here
GRADIO_SERVER_PORT=7860
STREAMLIT_SERVER_PORT=8501
EOF

echo "✅ Variables configuradas en .env"

# 2. HABILITAR ULTRALYTICS EN CÓDIGO
echo "📝 2. Habilitando Ultralytics YOLO..."

# Backup del archivo original
cp ml_core/models/yolo_coco_pretrained.py ml_core/models/yolo_coco_pretrained.py.backup

# Rehabilitar imports
sed -i 's/# from ultralytics import YOLO  # Disabled/from ultralytics import YOLO/' ml_core/models/yolo_coco_pretrained.py
sed -i 's/YOLO = None/# YOLO = None/' ml_core/models/yolo_coco_pretrained.py
sed -i 's/ULTRALYTICS_AVAILABLE = False  # Disabled for compatibility/ULTRALYTICS_AVAILABLE = True/' ml_core/models/yolo_coco_pretrained.py
sed -i 's/ULTRALYTICS_AVAILABLE = False/ULTRALYTICS_AVAILABLE = True/' ml_core/models/yolo_coco_pretrained.py

echo "✅ Ultralytics habilitado en código"

# 3. INSTALAR DEPENDENCIAS COMPLETAS
echo "📝 3. Instalando dependencias ML..."
pip install --upgrade ultralytics torch torchvision
pip install --upgrade opencv-python
pip install --upgrade scipy scikit-learn

echo "✅ Dependencias ML instaladas"

# 4. DESCARGAR MODELOS YOLO PREENTRENADOS
echo "📝 4. Descargando modelos YOLO..."
python3 -c "
import os
os.environ['DUMMY_MODE'] = 'false'
try:
    from ultralytics import YOLO
    print('⬇️  Descargando YOLOv8n...')
    model_n = YOLO('yolov8n.pt')
    print('⬇️  Descargando YOLOv8s...')  
    model_s = YOLO('yolov8s.pt')
    print('✅ Modelos YOLO descargados exitosamente')
except Exception as e:
    print(f'⚠️  Error descargando modelos: {e}')
"

# 5. CONFIGURAR PERFILES TRAP
echo "📝 5. Configurando perfiles para artista trap..."

# Crear configuración específica trap
mkdir -p config/trap_profiles
cat > config/trap_profiles/trap_artist_config.json << EOF
{
  "artist_profile": {
    "name": "TrapStar_Artist",
    "genre": "trap",
    "style": "aggressive_beats",
    "target_audience": "16-25",
    "preferred_platforms": ["tiktok", "instagram", "youtube"],
    "posting_schedule": {
      "peak_hours": ["19:00", "21:00", "23:00"],
      "frequency": "daily",
      "content_types": ["video_clips", "stories", "reels"]
    }
  },
  "campaign_settings": {
    "viral_triggers": ["trending_sounds", "challenges", "hashtag_waves"],
    "engagement_targets": {
      "views": 100000,
      "likes": 10000,
      "shares": 2000,
      "comments": 500
    },
    "budget_allocation": {
      "meta_ads": 70,
      "influencer_partnerships": 20,
      "organic_boost": 10
    }
  },
  "ml_preferences": {
    "content_analysis": "aggressive_beats_detection",
    "viral_prediction": "trap_specific_model",
    "audience_targeting": "trap_demographics"
  }
}
EOF

echo "✅ Perfil trap configurado"

# 6. CREAR SCRIPT DE INICIO PRODUCCIÓN
cat > start_trap_production.py << 'EOF'
#!/usr/bin/env python3
"""
🎵 LAUNCHER PRODUCCIÓN - ARTISTA TRAP
====================================
Inicia sistema completo en modo producción para campañas trap
"""

import os
import subprocess
import sys
import time
import requests
from pathlib import Path

def setup_production_env():
    """Configurar entorno de producción"""
    os.environ['DUMMY_MODE'] = 'false'
    os.environ['ML_PRODUCTION_MODE'] = 'true'
    os.environ['TRAP_ARTIST_MODE'] = 'true'
    print("✅ Entorno producción configurado")

def verify_ml_models():
    """Verificar que modelos ML están disponibles"""
    try:
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')
        print("✅ Modelos YOLO verificados")
        return True
    except Exception as e:
        print(f"❌ Error modelos ML: {e}")
        return False

def start_services():
    """Iniciar servicios del sistema"""
    print("🚀 Iniciando servicios producción...")
    
    # ML API
    subprocess.Popen([sys.executable, "-m", "ml_core.api.main"], 
                     cwd=Path.cwd())
    time.sleep(3)
    
    # Production Controller (Gradio)
    subprocess.Popen([sys.executable, "production_controller.py"], 
                     cwd=Path.cwd())
    time.sleep(2)
    
    # Analytics Engine (Streamlit)  
    subprocess.Popen(["streamlit", "run", "analytics_engine.py", 
                      "--server.port=8501"], cwd=Path.cwd())
    time.sleep(2)
    
    print("✅ Servicios iniciados")

def verify_services():
    """Verificar que servicios están corriendo"""
    services = [
        ("ML API", "http://localhost:8000/health"),
        ("Gradio Dashboard", "http://localhost:7860"),
        ("Streamlit Analytics", "http://localhost:8501")
    ]
    
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: OPERATIVO")
            else:
                print(f"⚠️  {name}: Respuesta {response.status_code}")
        except:
            print(f"❌ {name}: NO DISPONIBLE")

if __name__ == "__main__":
    print("🎵 INICIANDO SISTEMA TRAP EN PRODUCCIÓN")
    print("=====================================")
    
    setup_production_env()
    
    if not verify_ml_models():
        print("❌ Modelos ML no disponibles. Ejecuta el script de activación primero.")
        sys.exit(1)
    
    start_services()
    time.sleep(5)
    verify_services()
    
    print("")
    print("🎯 SISTEMA TRAP PRODUCTIVO INICIADO")
    print("===================================")
    print("📊 Gradio Dashboard: http://localhost:7860")
    print("📈 Streamlit Analytics: http://localhost:8501") 
    print("🤖 ML API: http://localhost:8000")
    print("")
    print("🔥 ¡LISTO PARA CAMPAÑAS VIRALES TRAP! 🎵")
EOF

chmod +x start_trap_production.py
echo "✅ Script de inicio producción creado"

# 7. MENSAJE FINAL
echo ""
echo "🎯 CONVERSIÓN A PRODUCCIÓN COMPLETADA"
echo "===================================="
echo ""
echo "📝 CAMBIOS REALIZADOS:"
echo "✅ DUMMY_MODE → false"
echo "✅ Ultralytics habilitado"
echo "✅ Modelos YOLO descargados"
echo "✅ Perfil trap configurado"
echo "✅ Script producción creado"
echo ""
echo "🚀 PARA INICIAR SISTEMA TRAP:"
echo "./start_trap_production.py"
echo ""
echo "🔗 DASHBOARDS DISPONIBLES:"
echo "📊 Control: http://localhost:7860"
echo "📈 Analytics: http://localhost:8501"
echo ""
echo "🎵 ¡SISTEMA LISTO PARA TRAP VIRAL! 🔥"