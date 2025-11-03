#!/usr/bin/env python3
"""
🎛️ Centralized Dashboard Launcher

Sistema de lanzamiento centralizado para dashboards de producción
- Production Controller (Gradio): Centro de comando y control
- Analytics Engine (Streamlit): Motor de analytics e insights
- Arquitectura limpia con modo dummy → producción

Autor: Sistema Centralizado de Dashboards
Fecha: 2025-11-03
"""

import subprocess
import sys
import os
import time
import signal
import psutil
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import threading
import webbrowser

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DashboardLauncher:
    """Launcher centralizado para dashboards de producción"""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.status_file = "data/dashboard_status.json"
        self.pid_file = "data/dashboard_pids.json"
        
        # Configuración de servicios
        self.services = {
            "production_controller": {
                "name": "Production Controller (Gradio)",
                "script": "production_controller.py",
                "port": 7860,
                "url": "http://localhost:7860",
                "description": "Centro de comando para campañas y control del sistema"
            },
            "analytics_engine": {
                "name": "Analytics Engine (Streamlit)",
                "script": "analytics_engine.py", 
                "port": 8501,
                "url": "http://localhost:8501",
                "description": "Motor de analytics, insights y recomendaciones ML"
            },
            "ml_api": {
                "name": "ML API (FastAPI)",
                "script": "ml_core/api/main.py",
                "port": 8000,
                "url": "http://localhost:8000",
                "description": "API de machine learning para procesamiento YOLO/COCO"
            }
        }
        
        # Crear directorios necesarios
        os.makedirs("data", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # Configurar handler para señales
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handler para señales de sistema"""
        logger.info("Received signal, shutting down gracefully...")
        self.stop_all_services()
        sys.exit(0)
    
    def _check_port_available(self, port: int) -> bool:
        """Verificar si un puerto está disponible"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', port)) != 0
        except Exception:
            return False
    
    def _wait_for_service(self, service_name: str, timeout: int = 30) -> bool:
        """Esperar a que un servicio esté disponible"""
        service = self.services[service_name]
        port = service["port"]
        
        for i in range(timeout):
            if not self._check_port_available(port):
                logger.info(f"✅ {service['name']} is ready on port {port}")
                return True
            time.sleep(1)
            
        logger.warning(f"⚠️ {service['name']} did not start within {timeout} seconds")
        return False
    
    def start_service(self, service_name: str) -> bool:
        """Iniciar un servicio específico"""
        if service_name not in self.services:
            logger.error(f"Unknown service: {service_name}")
            return False
        
        service = self.services[service_name]
        
        # Verificar si ya está corriendo
        if service_name in self.processes:
            if self.processes[service_name].poll() is None:
                logger.info(f"✅ {service['name']} is already running")
                return True
            else:
                # El proceso terminó, removerlo
                del self.processes[service_name]
        
        # Verificar puerto
        if not self._check_port_available(service["port"]):
            logger.warning(f"⚠️ Port {service['port']} is already in use")
            return False
        
        logger.info(f"🚀 Starting {service['name']}...")
        
        try:
            # Comando específico según el servicio
            if service_name == "production_controller":
                cmd = [sys.executable, service["script"]]
            elif service_name == "analytics_engine":
                cmd = [
                    sys.executable, "-m", "streamlit", "run", 
                    service["script"],
                    "--server.port", str(service["port"]),
                    "--server.address", "0.0.0.0",
                    "--server.headless", "true",
                    "--browser.gatherUsageStats", "false"
                ]
            elif service_name == "ml_api":
                cmd = [
                    sys.executable, "-m", "uvicorn",
                    "ml_core.api.main:app",
                    "--host", "0.0.0.0",
                    "--port", str(service["port"]),
                    "--reload"
                ]
            else:
                cmd = [sys.executable, service["script"]]
            
            # Iniciar proceso
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            self.processes[service_name] = process
            
            # Esperar a que el servicio esté listo
            if self._wait_for_service(service_name):
                logger.info(f"✅ {service['name']} started successfully")
                self._save_status()
                return True
            else:
                logger.error(f"❌ {service['name']} failed to start properly")
                self.stop_service(service_name)
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting {service['name']}: {e}")
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """Detener un servicio específico"""
        if service_name not in self.processes:
            logger.info(f"Service {service_name} is not running")
            return True
        
        service = self.services[service_name]
        process = self.processes[service_name]
        
        logger.info(f"🛑 Stopping {service['name']}...")
        
        try:
            # Intentar terminación graceful
            process.terminate()
            
            # Esperar hasta 10 segundos
            try:
                process.wait(timeout=10)
                logger.info(f"✅ {service['name']} stopped gracefully")
            except subprocess.TimeoutExpired:
                # Forzar terminación
                process.kill()
                process.wait()
                logger.info(f"✅ {service['name']} force stopped")
            
            del self.processes[service_name]
            self._save_status()
            return True
            
        except Exception as e:
            logger.error(f"❌ Error stopping {service['name']}: {e}")
            return False
    
    def start_all_services(self) -> bool:
        """Iniciar todos los servicios"""
        logger.info("🚀 Starting all dashboard services...")
        
        success_count = 0
        total_services = len(self.services)
        
        # Iniciar servicios en orden específico
        service_order = ["ml_api", "production_controller", "analytics_engine"]
        
        for service_name in service_order:
            if self.start_service(service_name):
                success_count += 1
                time.sleep(2)  # Delay entre servicios
            else:
                logger.error(f"❌ Failed to start {service_name}")
        
        if success_count == total_services:
            logger.info("✅ All services started successfully!")
            self._show_dashboard_urls()
            return True
        else:
            logger.warning(f"⚠️ Only {success_count}/{total_services} services started")
            return False
    
    def stop_all_services(self) -> bool:
        """Detener todos los servicios"""
        logger.info("🛑 Stopping all dashboard services...")
        
        success_count = 0
        for service_name in list(self.processes.keys()):
            if self.stop_service(service_name):
                success_count += 1
        
        logger.info(f"✅ Stopped {success_count} services")
        return len(self.processes) == 0
    
    def restart_service(self, service_name: str) -> bool:
        """Reiniciar un servicio específico"""
        logger.info(f"🔄 Restarting {self.services[service_name]['name']}...")
        
        self.stop_service(service_name)
        time.sleep(2)
        return self.start_service(service_name)
    
    def get_services_status(self) -> Dict[str, Dict]:
        """Obtener estado de todos los servicios"""
        status = {}
        
        for service_name, service_config in self.services.items():
            is_running = service_name in self.processes and self.processes[service_name].poll() is None
            port_available = self._check_port_available(service_config["port"])
            
            status[service_name] = {
                "name": service_config["name"],
                "running": is_running,
                "port": service_config["port"],
                "port_available": port_available,
                "url": service_config["url"],
                "description": service_config["description"],
                "pid": self.processes[service_name].pid if is_running else None
            }
        
        return status
    
    def _save_status(self):
        """Guardar estado actual"""
        status = self.get_services_status()
        
        with open(self.status_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "services": status
            }, f, indent=2)
        
        # Guardar PIDs
        pids = {name: proc.pid for name, proc in self.processes.items()}
        with open(self.pid_file, 'w') as f:
            json.dump(pids, f, indent=2)
    
    def _show_dashboard_urls(self):
        """Mostrar URLs de dashboards"""
        print("\n" + "="*60)
        print("🎯 DASHBOARDS DE PRODUCCIÓN ACTIVOS")
        print("="*60)
        
        for service_name, service_config in self.services.items():
            if service_name in self.processes and self.processes[service_name].poll() is None:
                print(f"✅ {service_config['name']}")
                print(f"   URL: {service_config['url']}")
                print(f"   Función: {service_config['description']}")
                print()
        
        print("="*60)
        print("📋 COMANDOS ÚTILES:")
        print("   Estado: python centralized_launcher.py status")
        print("   Parar: python centralized_launcher.py stop")
        print("   Reiniciar: python centralized_launcher.py restart")
        print("="*60)
    
    def open_dashboards_in_browser(self):
        """Abrir dashboards en el navegador"""
        logger.info("🌐 Opening dashboards in browser...")
        
        for service_name, service_config in self.services.items():
            if service_name in self.processes and self.processes[service_name].poll() is None:
                try:
                    webbrowser.open(service_config["url"])
                    time.sleep(1)  # Delay entre tabs
                except Exception as e:
                    logger.warning(f"Could not open {service_config['name']}: {e}")
    
    def monitor_services(self, interval: int = 30):
        """Monitorear servicios continuamente"""
        logger.info(f"👁️ Starting service monitoring (interval: {interval}s)")
        
        try:
            while True:
                status = self.get_services_status()
                
                # Verificar servicios caídos
                for service_name, service_status in status.items():
                    if not service_status["running"] and not service_status["port_available"]:
                        logger.warning(f"⚠️ Service {service_name} appears to be down, attempting restart...")
                        self.restart_service(service_name)
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")

def main():
    """Función principal"""
    launcher = DashboardLauncher()
    
    if len(sys.argv) < 2:
        command = "start"
    else:
        command = sys.argv[1].lower()
    
    if command == "start":
        print("🎯 Starting Production Dashboard System...")
        
        if launcher.start_all_services():
            print("\n✅ All services started successfully!")
            
            # Abrir navegador si no estamos en modo headless
            if "--no-browser" not in sys.argv:
                time.sleep(3)  # Esperar a que los servicios estén completamente listos
                launcher.open_dashboards_in_browser()
            
            # Mantener el script corriendo
            try:
                print("\n📡 Monitoring services... Press Ctrl+C to stop all services")
                launcher.monitor_services()
            except KeyboardInterrupt:
                print("\n🛑 Shutting down services...")
                launcher.stop_all_services()
        else:
            print("\n❌ Some services failed to start")
            sys.exit(1)
    
    elif command == "stop":
        print("🛑 Stopping all services...")
        launcher.stop_all_services()
        print("✅ All services stopped")
    
    elif command == "restart":
        print("🔄 Restarting all services...")
        launcher.stop_all_services()
        time.sleep(3)
        launcher.start_all_services()
    
    elif command == "status":
        print("📊 Service Status:")
        status = launcher.get_services_status()
        
        for service_name, service_status in status.items():
            status_icon = "✅" if service_status["running"] else "❌"
            print(f"{status_icon} {service_status['name']}")
            print(f"   Port: {service_status['port']}")
            print(f"   URL: {service_status['url']}")
            if service_status["pid"]:
                print(f"   PID: {service_status['pid']}")
            print()
    
    elif command == "logs":
        service_name = sys.argv[2] if len(sys.argv) > 2 else None
        
        if service_name and service_name in launcher.processes:
            process = launcher.processes[service_name]
            try:
                while True:
                    output = process.stdout.readline()
                    if output:
                        print(output.decode().strip())
                    time.sleep(0.1)
            except KeyboardInterrupt:
                pass
        else:
            print("Specify service name: production_controller, analytics_engine, or ml_api")
    
    elif command == "help":
        print("""
🎛️ Centralized Dashboard Launcher

Commands:
  start     - Start all dashboard services (default)
  stop      - Stop all services  
  restart   - Restart all services
  status    - Show status of all services
  logs      - Show logs for specific service
  help      - Show this help message

Options:
  --no-browser  - Don't open browser automatically

Examples:
  python centralized_launcher.py start
  python centralized_launcher.py status
  python centralized_launcher.py logs production_controller
        """)
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'python centralized_launcher.py help' for available commands")
        sys.exit(1)

if __name__ == "__main__":
    main()