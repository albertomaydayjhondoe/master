"""
Validador de integridad del sistema después de las correcciones.
Verifica que todos los componentes funcionen correctamente.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemValidator:
    """Validador de integridad del sistema."""
    
    def __init__(self, repo_path: str = "/workspaces/master"):
        self.repo_path = Path(repo_path)
        self.validation_results: Dict[str, bool] = {}
        self.errors_found: List[str] = []
    
    def validate_telegram_system(self) -> bool:
        """Validar el sistema de automatización de Telegram."""
        logger.info("🔍 Validando sistema de automatización de Telegram...")
        
        telegram_path = self.repo_path / "telegram_automation"
        
        # Verificar estructura de directorios
        required_dirs = [
            "core",
            "config", 
            "integrations",
            "database"
        ]
        
        for dir_name in required_dirs:
            dir_path = telegram_path / dir_name
            if not dir_path.exists():
                self.errors_found.append(f"Directorio faltante: {dir_path}")
                return False
        
        # Verificar archivos principales
        required_files = [
            "main_bot.py",
            "api_gateway.py",
            "requirements.txt",
            "Dockerfile",
            "Makefile",
            ".env.example"
        ]
        
        for file_name in required_files:
            file_path = telegram_path / file_name
            if not file_path.exists():
                self.errors_found.append(f"Archivo faltante: {file_path}")
                return False
        
        # Verificar módulos core
        core_modules = [
            "listener_module.py",
            "executor_module.py", 
            "priority_engine.py",
            "metrics_collector.py",
            "message_generator.py",
            "multi_account_manager.py"
        ]
        
        for module in core_modules:
            module_path = telegram_path / "core" / module
            if not module_path.exists():
                self.errors_found.append(f"Módulo core faltante: {module_path}")
                return False
        
        logger.info("✅ Sistema de Telegram validado correctamente")
        return True
    
    def validate_ml_system(self) -> bool:
        """Validar sistema ML."""
        logger.info("🔍 Validando sistema ML...")
        
        # Verificar YOLO COCO
        yolo_path = self.repo_path / "ml_core" / "models" / "yolo_coco_pretrained.py"
        if not yolo_path.exists():
            self.errors_found.append(f"Sistema YOLO faltante: {yolo_path}")
            return False
        
        # Verificar factory
        factory_path = self.repo_path / "ml_core" / "models" / "factory.py"
        if not factory_path.exists():
            self.errors_found.append(f"Factory ML faltante: {factory_path}")
            return False
        
        logger.info("✅ Sistema ML validado correctamente")
        return True
    
    def validate_gologin_system(self) -> bool:
        """Validar sistema GoLogin."""
        logger.info("🔍 Validando sistema GoLogin...")
        
        gologin_path = self.repo_path / "gologin_automation"
        if not gologin_path.exists():
            self.errors_found.append(f"Sistema GoLogin faltante: {gologin_path}")
            return False
        
        # Verificar componentes principales
        required_files = [
            "api_client.py",
            "anonymity_context.py",
            "config.py"
        ]
        
        for file_name in required_files:
            file_path = gologin_path / file_name
            if not file_path.exists():
                self.errors_found.append(f"Componente GoLogin faltante: {file_path}")
                return False
        
        logger.info("✅ Sistema GoLogin validado correctamente")
        return True
    
    def test_imports(self) -> bool:
        """Probar imports críticos."""
        logger.info("🔍 Probando imports críticos...")
        
        try:
            # Test Telegram imports
            sys.path.append(str(self.repo_path / "telegram_automation"))
            
            # Import dentro de try-catch para manejar errores específicos
            exec("from config.telegram_config import TelegramConfig")
            exec("from database.models import User, EngagementTask, Metrics")
            exec("from integrations.youtube_client import YouTubeClient")
            exec("from integrations.instagram_client import InstagramClient")
            exec("from integrations.tiktok_client import TikTokClient")
            
            logger.info("✅ Imports de Telegram OK")
            
            # Test ML imports  
            sys.path.append(str(self.repo_path))
            exec("from ml_core.models.yolo_coco_pretrained import YoloCOCOPretrainedDetector")
            exec("from ml_core.models.factory import get_yolo_coco_detector")
            
            logger.info("✅ Imports de ML OK")
            
            # Test GoLogin imports
            exec("from gologin_automation.api_client import GoLoginAPIClient")
            exec("from gologin_automation.anonymity_context import AnonymityProfile")
            
            logger.info("✅ Imports de GoLogin OK")
            
            return True
            
        except ImportError as e:
            self.errors_found.append(f"Error de import: {e}")
            return False
        except Exception as e:
            self.errors_found.append(f"Error en test de imports: {e}")
            return False
    
    def test_basic_functionality(self) -> bool:
        """Probar funcionalidad básica."""
        logger.info("🔍 Probando funcionalidad básica...")
        
        try:
            # Test configuración de Telegram
            sys.path.append(str(self.repo_path / "telegram_automation"))
            from config.telegram_config import TelegramConfig
            
            config = TelegramConfig()
            assert hasattr(config, 'telegram_config')
            assert hasattr(config, 'platform_configs')
            logger.info("✅ Configuración de Telegram OK")
            
            # Test clientes de plataforma
            from integrations.youtube_client import YouTubeClient
            youtube = YouTubeClient({'dummy_mode': True})
            assert youtube is not None
            logger.info("✅ Cliente de YouTube OK")
            
            # Test detector YOLO
            sys.path.append(str(self.repo_path))
            from ml_core.models.yolo_coco_pretrained import YoloCOCOPretrainedDetector
            detector = YoloCOCOPretrainedDetector()
            assert detector is not None
            logger.info("✅ Detector YOLO OK")
            
            return True
            
        except Exception as e:
            self.errors_found.append(f"Error en funcionalidad básica: {e}")
            return False
    
    def validate_documentation(self) -> bool:
        """Validar documentación."""
        logger.info("🔍 Validando documentación...")
        
        docs_to_check = [
            "README.md",
            "CONTRIBUTING.md", 
            "telegram_automation/README.md",
            "telegram_automation/CHANGELOG.md",
            "telegram_automation/SYSTEM_COMPLETE.md"
        ]
        
        for doc in docs_to_check:
            doc_path = self.repo_path / doc
            if not doc_path.exists():
                self.errors_found.append(f"Documentación faltante: {doc_path}")
                return False
        
        logger.info("✅ Documentación validada correctamente")
        return True
    
    def run_full_validation(self) -> bool:
        """Ejecutar validación completa."""
        logger.info("🚀 Iniciando validación completa del sistema...")
        logger.info("=" * 60)
        
        validations = [
            ("Sistema Telegram", self.validate_telegram_system),
            ("Sistema ML", self.validate_ml_system),
            ("Sistema GoLogin", self.validate_gologin_system),
            ("Imports críticos", self.test_imports),
            ("Funcionalidad básica", self.test_basic_functionality),
            ("Documentación", self.validate_documentation)
        ]
        
        passed = 0
        total = len(validations)
        
        for validation_name, validation_func in validations:
            try:
                logger.info(f"\n🔍 Validando: {validation_name}")
                result = validation_func()
                self.validation_results[validation_name] = result
                
                if result:
                    passed += 1
                    logger.info(f"✅ {validation_name} - PASÓ")
                else:
                    logger.error(f"❌ {validation_name} - FALLÓ")
                    
            except Exception as e:
                logger.error(f"❌ {validation_name} - ERROR: {e}")
                self.validation_results[validation_name] = False
        
        # Mostrar resumen
        logger.info(f"\n🎯 Resumen de validación:")
        logger.info(f"   ✅ Validaciones pasadas: {passed}/{total}")
        logger.info(f"   📊 Tasa de éxito: {(passed/total)*100:.1f}%")
        
        if self.errors_found:
            logger.info(f"\n⚠️ Errores encontrados:")
            for error in self.errors_found:
                logger.error(f"   - {error}")
        
        success = passed == total
        
        if success:
            logger.info("\n🎉 ¡Validación completa exitosa!")
            logger.info("El sistema está funcionalmente correcto según el propósito definido.")
        else:
            logger.error(f"\n💥 Validación incompleta: {total-passed} fallos encontrados")
        
        return success

def main() -> None:
    """Función principal."""
    print("🔍 Validador de integridad del sistema")
    print("Verificando funcionalidad después de correcciones")
    print("=" * 60)
    
    validator = SystemValidator()
    success = validator.run_full_validation()
    
    print(f"\n{'🎉 SISTEMA VÁLIDO' if success else '⚠️ SISTEMA REQUIERE ATENCIÓN'}")
    exit(0 if success else 1)

if __name__ == "__main__":
    main()