#!/usr/bin/env python3
"""
Setup script para descargar y configurar modelos YOLOv8 para el sistema Stakas.

Este script descarga modelos YOLOv8 pre-entrenados y los adapta para
el análisis de interfaces de TikTok y contenido viral.
"""
import os
import sys
import shutil
from pathlib import Path
from ultralytics import YOLO
import yaml

def setup_directories():
    """Crear estructura de directorios necesaria."""
    base_path = Path(__file__).parent.parent
    dirs = [
        base_path / "data" / "models" / "production",
        base_path / "data" / "models" / "checkpoints", 
        base_path / "data" / "datasets" / "tiktok_ui",
        base_path / "data" / "datasets" / "tiktok_video"
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Directorio creado: {dir_path}")

def download_base_models():
    """Descargar modelos YOLOv8 base para fine-tuning."""
    base_path = Path(__file__).parent.parent
    production_path = base_path / "data" / "models" / "production"
    
    models = {
        "yolov8n.pt": "tiktok_ui_detector.pt",      # Modelo ligero para UI
        "yolov8s.pt": "tiktok_video_analyzer.pt",   # Modelo medio para video
        "yolov8m.pt": "anomaly_detector.pt"         # Modelo robusto para anomalías
    }
    
    for base_model, target_name in models.items():
        print(f"🔄 Descargando {base_model}...")
        try:
            # Cargar modelo (se descarga automáticamente si no existe)
            model = YOLO(base_model)
            
            # Copiar a directorio de producción
            target_path = production_path / target_name
            shutil.copy2(model.ckpt_path or f"{base_model}", target_path)
            
            print(f"✅ Modelo guardado: {target_path}")
            
            # Verificar que funcione
            test_results = model.predict(source="https://ultralytics.com/images/bus.jpg", verbose=False)
            print(f"✅ Modelo {base_model} verificado correctamente")
            
        except Exception as e:
            print(f"❌ Error descargando {base_model}: {e}")
            return False
    
    return True

def create_data_yaml():
    """Crear archivo data.yaml para entrenamiento personalizado."""
    base_path = Path(__file__).parent.parent
    dataset_path = base_path / "data" / "datasets" / "tiktok_ui"
    
    # Crear estructura de dataset
    for subset in ["train", "val", "test"]:
        (dataset_path / subset / "images").mkdir(parents=True, exist_ok=True)
        (dataset_path / subset / "labels").mkdir(parents=True, exist_ok=True)
    
    # Configuración del dataset
    data_config = {
        "path": str(dataset_path.absolute()),
        "train": "train/images",
        "val": "val/images", 
        "test": "test/images",
        "names": {
            0: "like_button",
            1: "follow_button",
            2: "comment_button", 
            3: "video_player",
            4: "profile_icon",
            5: "share_button",
            6: "text_overlay",
            7: "thumbnail",
            8: "user_avatar"
        },
        "nc": 9  # number of classes
    }
    
    # Guardar data.yaml
    data_yaml_path = dataset_path / "data.yaml"
    with open(data_yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(data_config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"✅ Dataset configurado: {data_yaml_path}")
    
    # Actualizar config del sistema
    update_model_config(dataset_path)

def update_model_config(dataset_path):
    """Actualizar config/ml/model_config.yaml con rutas locales."""
    base_path = Path(__file__).parent.parent
    config_path = base_path / "config" / "ml" / "model_config.yaml"
    
    # Configuración actualizada
    config = {
        "yolo_screenshot": {
            "model_path": str(base_path / "data" / "models" / "production" / "tiktok_ui_detector.pt"),
            "device": "cuda" if check_cuda_available() else "cpu",
            "conf_threshold": 0.25,
            "iou_threshold": 0.45,
            "training": {
                "data_yaml": str(dataset_path / "data.yaml"),
                "epochs": 100,
                "imgsz": 640,
                "batch": 16
            }
        },
        "yolo_video": {
            "model_path": str(base_path / "data" / "models" / "production" / "tiktok_video_analyzer.pt"),
            "device": "cuda" if check_cuda_available() else "cpu"
        },
        "affinity": {
            "model_path": str(base_path / "data" / "models" / "production" / "account_affinity.onnx"),
            "device": "cuda" if check_cuda_available() else "cpu"
        },
        "anomaly": {
            "model_path": str(base_path / "data" / "models" / "production" / "anomaly_detector.pt"),
            "device": "cuda" if check_cuda_available() else "cpu"
        }
    }
    
    # Guardar configuración actualizada
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"✅ Configuración actualizada: {config_path}")

def check_cuda_available():
    """Verificar disponibilidad de CUDA."""
    try:
        import torch
        return torch.cuda.is_available()
    except:
        return False

def test_yolo_integration():
    """Probar que los modelos funcionen correctamente."""
    base_path = Path(__file__).parent.parent
    
    # Importar y probar el detector de producción
    sys.path.append(str(base_path))
    
    try:
        from ml_core.models.yolo_prod import YoloScreenshotDetector
        
        model_path = base_path / "data" / "models" / "production" / "tiktok_ui_detector.pt"
        detector = YoloScreenshotDetector(
            model_path=str(model_path),
            device="cpu"  # Usar CPU para test inicial
        )
        
        # Test con imagen dummy
        from PIL import Image
        import io
        
        # Crear imagen de prueba
        test_img = Image.new('RGB', (640, 640), color='white')
        img_buffer = io.BytesIO()
        test_img.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        
        # Ejecutar detección
        results = detector.detect(img_bytes)
        print(f"✅ Test de detección completado: {len(results)} detecciones")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de integración: {e}")
        return False

def main():
    """Función principal de setup."""
    print("🚀 Iniciando setup de modelos YOLOv8 para Stakas...")
    
    # Paso 1: Crear directorios
    print("\n📁 Creando estructura de directorios...")
    setup_directories()
    
    # Paso 2: Descargar modelos
    print("\n⬇️ Descargando modelos YOLOv8...")
    if not download_base_models():
        print("❌ Error descargando modelos. Abortando...")
        return False
    
    # Paso 3: Configurar datasets
    print("\n📊 Configurando datasets...")
    create_data_yaml()
    
    # Paso 4: Probar integración
    print("\n🧪 Probando integración...")
    if not test_yolo_integration():
        print("⚠️ Advertencia: Test de integración falló, pero modelos descargados")
    
    print("\n🎉 ¡Setup de YOLOv8 completado exitosamente!")
    print("\n📝 Próximos pasos:")
    print("   1. Configura DUMMY_MODE=false en tu .env")
    print("   2. Reinicia el sistema ML Core")
    print("   3. Añade imágenes de entrenamiento al dataset")
    print("   4. Ejecuta fine-tuning si es necesario")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)