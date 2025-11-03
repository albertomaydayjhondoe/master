🎵 INSTRUCCIONES COMPLETAS - MODO PRODUCCIÓN TRAP
================================================

## 🎯 **OBJETIVO**
Convertir sistema de DUMMY → PRODUCCIÓN completa para artista trap

## 🚀 **EJECUCIÓN AUTOMÁTICA (RECOMENDADO)**

### **Un Solo Comando:**
```bash
./activate_trap_production.sh
```

Este script automático:
1. ✅ Cambia DUMMY_MODE → false
2. ✅ Habilita Ultralytics en código  
3. ✅ Instala dependencias ML
4. ✅ Descarga modelos YOLO
5. ✅ Configura perfil trap
6. ✅ Crea launcher producción

## 🛠️ **EJECUCIÓN MANUAL (PASO A PASO)**

### **1. Cambiar Variables de Entorno**
```bash
export DUMMY_MODE=false
export ML_PRODUCTION_MODE=true
export TRAP_ARTIST_MODE=true
```

### **2. Crear archivo .env**
```bash
cat > .env << EOF
DUMMY_MODE=false
ML_PRODUCTION_MODE=true
TRAP_ARTIST_MODE=true
ARTIST_GENRE=trap
CAMPAIGN_TYPE=viral_trap
EOF
```

### **3. Habilitar Ultralytics en Código**
```bash
# Backup
cp ml_core/models/yolo_coco_pretrained.py ml_core/models/yolo_coco_pretrained.py.backup

# Rehabilitar imports
sed -i 's/# from ultralytics import YOLO  # Disabled/from ultralytics import YOLO/' ml_core/models/yolo_coco_pretrained.py
sed -i 's/ULTRALYTICS_AVAILABLE = False/ULTRALYTICS_AVAILABLE = True/' ml_core/models/yolo_coco_pretrained.py
```

### **4. Instalar Dependencias ML**
```bash
pip install --upgrade ultralytics torch torchvision opencv-python
```

### **5. Descargar Modelos YOLO**
```bash
python3 -c "
from ultralytics import YOLO
model_n = YOLO('yolov8n.pt')  # Descarga automática
model_s = YOLO('yolov8s.pt')  # Descarga automática
print('✅ Modelos descargados')
"
```

### **6. Iniciar Sistema Producción**
```bash
./start_trap_production.py
```

## 🎯 **VERIFICACIÓN POST-ACTIVACIÓN**

### **Comprobar Estado:**
```bash
# Variables
echo "DUMMY_MODE: $DUMMY_MODE"
echo "ML_PRODUCTION_MODE: $ML_PRODUCTION_MODE"

# Servicios
curl http://localhost:7860  # Gradio
curl http://localhost:8501  # Streamlit
curl http://localhost:8000/health  # ML API
```

### **Test ML Funcional:**
```bash
python3 -c "
import os
os.environ['DUMMY_MODE'] = 'false'
from ml_core.models.factory import get_yolo_coco_detector
detector = get_yolo_coco_detector()
print('✅ ML YOLO operativo en producción')
"
```

## 🔥 **FUNCIONALIDADES TRAP ACTIVADAS**

### **1. ML Intelligence Real:**
- ✅ YOLO object detection
- ✅ Screenshot analysis  
- ✅ Video content analysis
- ✅ Viral prediction models

### **2. Campañas Trap Específicas:**
- ✅ Beat detection para trap
- ✅ Audience targeting 16-25 años
- ✅ Hashtag optimization
- ✅ Peak hours scheduling

### **3. Dashboards Operativos:**
- 🔴 **Gradio (7860)**: Botón rojo campañas
- 📊 **Streamlit (8501)**: Analytics ML real
- 🤖 **ML API (8000)**: Endpoints YOLO

## 📊 **URLS POST-ACTIVACIÓN**

| Servicio | URL | Función |
|----------|-----|---------|
| **Control Dashboard** | http://localhost:7860 | Lanzar campañas trap |
| **Analytics Engine** | http://localhost:8501 | Métricas ML reales |
| **ML API** | http://localhost:8000 | YOLO endpoints |
| **N8N Workflows** | http://localhost:5678 | Automatización |

## ⚡ **COMANDOS RÁPIDOS**

```bash
# ACTIVAR TODO
./activate_trap_production.sh

# INICIAR SERVICIOS  
./start_trap_production.py

# VERIFICAR ESTADO
curl -s http://localhost:8000/health | jq

# LANZAR CAMPAÑA TRAP
curl -X POST http://localhost:7860/api/launch_campaign \
  -d '{"artist":"TrapStar","genre":"trap","viral_mode":true}'
```

## 🎵 **¡SISTEMA TRAP LISTO PARA VIRAL!**

Después de ejecutar estos comandos tendrás:
- ✅ **ML Real** con YOLO funcional
- ✅ **Campañas trap** optimizadas  
- ✅ **Dashboards operativos**
- ✅ **Análisis viral** en tiempo real

**¡Tu artista trap está listo para dominar TikTok!** 🔥🎵