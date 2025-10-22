#!/bin/bash

# 🤖 Telegram Like4Like Bot Setup Script
# Configura todo el entorno para el sistema de intercambio automático

echo "🚀 Iniciando setup del sistema Telegram Like4Like..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. Verificar Python y pip
log_info "Verificando Python y pip..."
if ! command -v python3 &> /dev/null; then
    log_error "Python3 no encontrado. Por favor instala Python 3.8+"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    log_error "pip3 no encontrado. Por favor instala pip"
    exit 1
fi

log_success "Python y pip verificados"

# 2. Crear directorios necesarios
log_info "Creando estructura de directorios..."
mkdir -p data/models
mkdir -p data/training/screenshots
mkdir -p data/logs
mkdir -p config/telegram
mkdir -p sessions

log_success "Directorios creados"

# 3. Instalar dependencias básicas
log_info "Instalando dependencias básicas..."
pip3 install -r requirements.txt

# 4. Instalar dependencias específicas para Telegram Like4Like
log_info "Instalando dependencias específicas..."

# Telegram
pip3 install telethon cryptg

# Computer Vision y ML
pip3 install ultralytics opencv-python torch torchvision

# Utilities
pip3 install python-dotenv requests Pillow

log_success "Dependencias instaladas"

# 5. Configurar variables de entorno
log_info "Configurando variables de entorno..."

if [ ! -f .env ]; then
    cat > .env << EOF
# Telegram API Configuration
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here

# Phone Numbers (comma separated)
PHONE_NUMBERS=+1234567890,+0987654321

# YouTube API (optional)
YOUTUBE_API_KEY=your_youtube_api_key

# ML Configuration
ULTRALYTICS_MODEL_PATH=data/models/youtube_interaction_detector.pt
CONFIDENCE_THRESHOLD=0.7

# Logging
LOG_LEVEL=INFO
GITHUB_INTEGRATION=true

# Safety Settings
DUMMY_MODE=true
WARMUP_DAYS=7
MAX_INTERACTIONS_PER_HOUR=50
EOF

    log_success "Archivo .env creado"
    log_warning "IMPORTANTE: Edita el archivo .env con tus credenciales reales"
else
    log_info "Archivo .env ya existe, no se sobrescribe"
fi

# 6. Descargar modelo base YOLO
log_info "Descargando modelo base YOLO..."
python3 -c "
from ultralytics import YOLO
import os

# Crear directorio si no existe
os.makedirs('data/models', exist_ok=True)

# Descargar modelo base
model = YOLO('yolov8n.pt')
model.save('data/models/yolo_base.pt')

print('✅ Modelo base descargado')
"

if [ $? -eq 0 ]; then
    log_success "Modelo YOLO descargado"
else
    log_warning "Error descargando modelo YOLO - se usará descarga automática"
fi

# 7. Crear script de inicialización
log_info "Creando script de inicio..."

cat > start_like4like_bot.py << 'EOF'
#!/usr/bin/env python3
"""
Script de inicio para el bot Telegram Like4Like
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar path del proyecto
sys.path.append('/workspaces/master')

def main():
    """Función principal"""
    print("🤖 Iniciando Telegram Like4Like Bot...")
    
    # Verificar configuración
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH') 
    phone_numbers = os.getenv('PHONE_NUMBERS', '').split(',')
    
    if not api_id or api_id == 'your_api_id_here':
        print("❌ Error: Configura TELEGRAM_API_ID en el archivo .env")
        return
    
    if not api_hash or api_hash == 'your_api_hash_here':
        print("❌ Error: Configura TELEGRAM_API_HASH en el archivo .env")
        return
    
    if not phone_numbers or phone_numbers == ['']:
        print("❌ Error: Configura PHONE_NUMBERS en el archivo .env")
        return
    
    # Importar y ejecutar bot
    try:
        from telegram_like4like_bot import create_like4like_bot
        
        async def run_bot():
            bot = create_like4like_bot(api_id, api_hash, phone_numbers)
            await bot.start_bot()
        
        # Ejecutar bot
        asyncio.run(run_bot())
        
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido por el usuario")
    except Exception as e:
        print(f"❌ Error ejecutando bot: {e}")

if __name__ == "__main__":
    main()
EOF

chmod +x start_like4like_bot.py
log_success "Script de inicio creado"

# 8. Crear script de entrenamiento ML
log_info "Creando script de entrenamiento ML..."

cat > train_youtube_detector.py << 'EOF'
#!/usr/bin/env python3
"""
Script para entrenar el detector de interacciones de YouTube
"""

import os
import json
from ultralytics import YOLO
from pathlib import Path

def create_training_dataset():
    """Crear dataset de entrenamiento para detección de interacciones YouTube"""
    
    print("📊 Creando dataset de entrenamiento...")
    
    # Crear estructura YOLO
    dataset_path = Path("data/training/youtube_dataset")
    dataset_path.mkdir(parents=True, exist_ok=True)
    
    (dataset_path / "images" / "train").mkdir(parents=True, exist_ok=True)
    (dataset_path / "images" / "val").mkdir(parents=True, exist_ok=True)
    (dataset_path / "labels" / "train").mkdir(parents=True, exist_ok=True) 
    (dataset_path / "labels" / "val").mkdir(parents=True, exist_ok=True)
    
    # Crear archivo YAML de configuración
    yaml_config = f"""
path: {dataset_path.absolute()}
train: images/train
val: images/val

nc: 7  # number of classes
names: ['like_button', 'subscribe_button', 'comment_section', 'video_title', 'like_active', 'subscribed_active', 'comment_posted']
"""
    
    with open(dataset_path / "dataset.yaml", "w") as f:
        f.write(yaml_config)
    
    print(f"✅ Dataset estructura creada en: {dataset_path}")
    return dataset_path

def train_model():
    """Entrenar modelo personalizado"""
    
    print("🤖 Iniciando entrenamiento del modelo...")
    
    # Crear dataset
    dataset_path = create_training_dataset()
    
    # Cargar modelo base
    model = YOLO('yolov8n.pt')
    
    # Entrenar (usar pocos epochs para demo)
    results = model.train(
        data=dataset_path / "dataset.yaml",
        epochs=10,  # Aumentar para entrenamiento real
        imgsz=640,
        save=True,
        project="data/models",
        name="youtube_detector"
    )
    
    # Guardar modelo entrenado
    model_path = "data/models/youtube_interaction_detector.pt"
    model.save(model_path)
    
    print(f"✅ Modelo entrenado guardado en: {model_path}")
    return model_path

if __name__ == "__main__":
    train_model()
EOF

chmod +x train_youtube_detector.py
log_success "Script de entrenamiento creado"

# 9. Crear documentación de uso
log_info "Creando documentación de uso..."

cat > QUICK_START.md << 'EOF'
# 🚀 Quick Start - Telegram Like4Like Bot

## 1. Configuración Inicial

### Editar credenciales en `.env`:
```bash
nano .env
```

Configura:
- `TELEGRAM_API_ID`: Tu API ID de Telegram
- `TELEGRAM_API_HASH`: Tu API Hash de Telegram  
- `PHONE_NUMBERS`: Tus números de teléfono (separados por coma)

### Obtener credenciales Telegram:
1. Ve a https://my.telegram.org/
2. Inicia sesión con tu número
3. Crea una nueva aplicación
4. Copia API ID y API Hash

## 2. Entrenamiento del Modelo (Opcional)

```bash
# Entrenar detector personalizado
python3 train_youtube_detector.py
```

## 3. Ejecutar el Bot

```bash
# Modo dummy (seguro para pruebas)
python3 start_like4like_bot.py

# Modo producción (editar DUMMY_MODE=false en .env)
python3 start_like4like_bot.py
```

## 4. Monitoreo

- Logs en: `data/logs/like4like_log_YYYYMMDD.json`
- Screenshots en: `data/training/screenshots/`
- Métricas en tiempo real en la terminal

## 5. Escalabilidad

1. **Días 1-2**: Máximo 10 interacciones/hora
2. **Días 3-5**: Hasta 30 interacciones/hora  
3. **Días 6+**: Hasta 50 interacciones/hora

## 6. Seguridad

- ✅ Warm-up automático activado
- ✅ Rate limiting inteligente
- ✅ Detección de patrones humanos
- ✅ Monitoreo continuo de salud de cuentas

¡Listo para generar intercambios automáticos! 🎯
EOF

log_success "Documentación creada"

# 10. Verificación final
log_info "Verificando instalación..."

# Verificar imports críticos
python3 -c "
try:
    import telethon
    import ultralytics
    import cv2
    import torch
    print('✅ Todas las dependencias críticas importadas correctamente')
except ImportError as e:
    print(f'❌ Error importando: {e}')
"

# Resumen final
echo ""
echo "🎉 ===== SETUP COMPLETADO ====="
echo ""
log_success "Sistema Telegram Like4Like configurado exitosamente"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "1. Edita el archivo .env con tus credenciales de Telegram"
echo "2. Ejecuta: python3 start_like4like_bot.py"
echo "3. El bot iniciará en modo dummy (seguro)"
echo "4. Revisa QUICK_START.md para más detalles"
echo ""
log_warning "IMPORTANTE: Configura las credenciales antes de ejecutar"
echo ""
echo "🚀 ¡Tu sistema está listo para dominar YouTube!"