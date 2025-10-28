#!/usr/bin/env python3
"""
🚀 UNIVERSAL STARTUP SCRIPT - STAKAS VIRAL SYSTEM
Script de inicio que funciona en Windows, Linux y macOS
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from cross_platform_launcher import CrossPlatformLauncher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='🚀 %(asctime)s [STARTUP] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class UniversalStartup:
    """Sistema de inicio universal multiplataforma"""
    
    def __init__(self):
        self.launcher = CrossPlatformLauncher()
        self.project_root = Path(__file__).parent
        self.system_info = self.launcher.get_startup_info()
        
    def display_system_info(self):
        """Muestra información del sistema"""
        logger.info("🎯 Stakas Viral System - Universal Startup")
        logger.info("=" * 60)
        logger.info(f"💻 Sistema: {self.system_info['platform']}")
        logger.info(f"🐍 Python: {self.system_info['python_version']}")
        logger.info(f"📂 Directorio: {self.system_info['cwd']}")
        logger.info(f"🔧 Shell: {self.system_info['shell']}")
        logger.info("=" * 60)
    
    def check_environment(self):
        """Verifica el entorno y dependencias"""
        logger.info("🔍 Verificando entorno del sistema...")
        
        # Verificar dependencias básicas
        if not self.launcher.check_dependencies():
            logger.error("❌ Faltan dependencias críticas")
            sys.exit(1)
        
        # Verificar archivos importantes
        critical_files = [
            'requirements.txt',
            'unified_system_production.py',
            'ml_core/api/main.py'
        ]
        
        missing_files = []
        for file in critical_files:
            if not (self.project_root / file).exists():
                missing_files.append(file)
        
        if missing_files:
            logger.warning(f"⚠️  Archivos faltantes: {', '.join(missing_files)}")
        else:
            logger.info("✅ Todos los archivos críticos están presentes")
        
        return len(missing_files) == 0
    
    def install_dependencies(self):
        """Instala dependencias necesarias"""
        logger.info("📦 Instalando dependencias...")
        
        requirements_files = [
            'requirements.txt',
            'requirements-ml.txt'
        ]
        
        for req_file in requirements_files:
            req_path = self.project_root / req_file
            if req_path.exists():
                try:
                    self.launcher.install_requirements(str(req_path))
                    logger.info(f"✅ Instalado: {req_file}")
                except Exception as e:
                    logger.error(f"❌ Error instalando {req_file}: {e}")
            else:
                logger.warning(f"⚠️  No encontrado: {req_file}")
    
    def start_services(self):
        """Inicia todos los servicios del sistema"""
        logger.info("🚀 Iniciando servicios del sistema...")
        
        services = [
            {
                'name': 'ML Core API',
                'type': 'fastapi',
                'module': 'ml_core.api.main:app',
                'port': 8000,
                'priority': 1
            },
            {
                'name': 'Dashboard Principal',
                'type': 'streamlit',
                'script': 'unified_system_production.py',
                'port': 8501,
                'priority': 2
            },
            {
                'name': 'Dashboard Métricas',
                'type': 'streamlit',
                'script': 'scripts/dashboard_metricas_ultimo_mes.py',
                'port': 8502,
                'priority': 3
            },
            {
                'name': 'Dashboard UTMs',
                'type': 'streamlit',
                'script': 'scripts/dashboard_utms_completo.py',
                'port': 8503,
                'priority': 3
            }
        ]
        
        # Ordenar por prioridad
        services.sort(key=lambda x: x['priority'])
        
        for service in services:
            try:
                if service['type'] == 'fastapi':
                    self.launcher.start_fastapi(service['module'], service['port'])
                    logger.info(f"✅ {service['name']} iniciado en puerto {service['port']}")
                
                elif service['type'] == 'streamlit':
                    script_path = self.project_root / service['script']
                    if script_path.exists():
                        self.launcher.start_streamlit(str(script_path), service['port'])
                        logger.info(f"✅ {service['name']} iniciado en puerto {service['port']}")
                    else:
                        logger.warning(f"⚠️  Script no encontrado: {service['script']}")
                
                # Esperar un poco entre servicios
                import time
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Error iniciando {service['name']}: {e}")
    
    def get_access_urls(self):
        """Genera URLs de acceso según el entorno"""
        base_host = 'localhost'
        
        # En Railway, usar la variable PORT
        railway_port = os.getenv('PORT')
        if railway_port:
            base_host = '0.0.0.0'
        
        urls = {
            'ML API': f'http://{base_host}:8000',
            'Dashboard Principal': f'http://{base_host}:8501',
            'Dashboard Métricas': f'http://{base_host}:8502',
            'Dashboard UTMs': f'http://{base_host}:8503'
        }
        
        return urls
    
    def display_access_info(self):
        """Muestra información de acceso"""
        urls = self.get_access_urls()
        
        logger.info("🌐 URLs de Acceso:")
        logger.info("=" * 40)
        for service, url in urls.items():
            logger.info(f"📊 {service}: {url}")
        logger.info("=" * 40)
        
        # Información adicional
        logger.info("🎯 Canal Objetivo: UCgohgqLVu1QPdfa64Vkrgeg")
        logger.info("💰 Presupuesto Meta Ads: €500/mes")
        logger.info("📈 Objetivo: 0 → 10K suscriptores")
    
    async def run(self):
        """Ejecuta el sistema completo"""
        try:
            # 1. Mostrar información del sistema
            self.display_system_info()
            
            # 2. Verificar entorno
            if not self.check_environment():
                logger.error("❌ El entorno no está configurado correctamente")
                return False
            
            # 3. Instalar dependencias si es necesario
            if '--install-deps' in sys.argv:
                self.install_dependencies()
            
            # 4. Iniciar servicios
            self.start_services()
            
            # 5. Mostrar información de acceso
            import time
            time.sleep(5)  # Esperar que los servicios se inicien
            self.display_access_info()
            
            # 6. Mantener el proceso activo
            logger.info("✅ Sistema iniciado correctamente")
            logger.info("🔄 Manteniendo servicios activos...")
            
            # En Railway, solo necesitamos mantener el proceso principal
            if os.getenv('PORT'):
                # Modo Railway - ejecutar el launcher específico
                from railway_launcher import RailwayLauncher
                railway = RailwayLauncher()
                railway.run()
            else:
                # Modo local - mantener activo indefinidamente
                while True:
                    await asyncio.sleep(30)
                    logger.info("🟢 Sistema operativo...")
            
            return True
            
        except KeyboardInterrupt:
            logger.info("🛑 Deteniendo sistema...")
            return True
        except Exception as e:
            logger.error(f"❌ Error crítico: {e}")
            return False

def main():
    """Punto de entrada principal"""
    startup = UniversalStartup()
    
    if os.name == 'nt':  # Windows
        # En Windows, usar asyncio.set_event_loop_policy
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Ejecutar el sistema
    success = asyncio.run(startup.run())
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()