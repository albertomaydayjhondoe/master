#!/usr/bin/env python3
"""
Production Control CLI - Command Line Interface

Interfaz de línea de comandos para el control de producción.
Permite activar/desactivar módulos desde terminal.

🔴 RED BUTTON SYSTEM CLI 🔴

Uso:
    python production_control_cli.py status
    python production_control_cli.py activate telegram_bot production
    python production_control_cli.py deactivate telegram_bot
    python production_control_cli.py emergency-stop
    python production_control_cli.py safe-mode
    python production_control_cli.py check-deps

Autor: Sistema de Control de Producción
Fecha: 2024
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import subprocess

# Añadir el directorio raíz al path para imports
sys.path.insert(0, '/workspaces/master')

from config.dependency_manager import DependencyManager, check_dependencies

class ProductionControlCLI:
    """CLI para control de producción"""
    
    def __init__(self):
        self.config_file = Path("/workspaces/master/config/production_control.json")
        self.logs_dir = Path("/workspaces/master/logs/production_control")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Colores para output
        self.RED = '\033[91m'
        self.GREEN = '\033[92m'
        self.YELLOW = '\033[93m'
        self.BLUE = '\033[94m'
        self.PURPLE = '\033[95m'
        self.CYAN = '\033[96m'
        self.WHITE = '\033[97m'
        self.RESET = '\033[0m'
        self.BOLD = '\033[1m'
    
    def load_config(self) -> Dict:
        """Cargar configuración actual"""
        
        if not self.config_file.exists():
            return {}
        
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def save_config(self, config: Dict):
        """Guardar configuración"""
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def log_action(self, action: str, module: str, details: str):
        """Registrar acción"""
        
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {action}: {module} - {details}"
        
        # Log a archivo
        log_file = self.logs_dir / f"cli_actions_{datetime.now().strftime('%Y%m%d')}.log"
        
        with open(log_file, 'a') as f:
            f.write(log_entry + '\n')
        
        # También mostrar en consola si es verbose
        if hasattr(self, 'verbose') and self.verbose:
            print(f"{self.BLUE}[LOG]{self.RESET} {log_entry}")
    
    def print_header(self, title: str):
        """Imprimir header con estilo"""
        
        border = "=" * (len(title) + 4)
        print(f"\n{self.RED}{self.BOLD}{border}{self.RESET}")
        print(f"{self.RED}{self.BOLD}  {title}  {self.RESET}")
        print(f"{self.RED}{self.BOLD}{border}{self.RESET}\n")
    
    def print_status(self, message: str, status: str = "info"):
        """Imprimir mensaje con estado"""
        
        if status == "success":
            icon = "✅"
            color = self.GREEN
        elif status == "warning":
            icon = "⚠️ "
            color = self.YELLOW
        elif status == "error":
            icon = "❌"
            color = self.RED
        elif status == "info":
            icon = "ℹ️ "
            color = self.BLUE
        else:
            icon = "🔵"
            color = self.WHITE
        
        print(f"{color}{icon} {message}{self.RESET}")
    
    def show_system_status(self):
        """Mostrar estado general del sistema"""
        
        self.print_header("🔴 PRODUCTION CONTROL SYSTEM STATUS")
        
        # Cargar configuración
        config = self.load_config()
        
        if not config:
            self.print_status("No configuration found - system in default state", "warning")
            return
        
        # Mostrar estado de módulos
        print(f"{self.BOLD}Module Status:{self.RESET}")
        
        modules = [
            "telegram_bot", "ml_ultralytics", "device_farm", "meta_ads",
            "gologin_proxy", "youtube_automation", "analytics_dashboard", "cloud_processing"
        ]
        
        module_names = {
            "telegram_bot": "Telegram Bot System",
            "ml_ultralytics": "ML Ultralytics Integration", 
            "device_farm": "Android Device Farm",
            "meta_ads": "Meta Ads Integration",
            "gologin_proxy": "GoLogin Proxy System",
            "youtube_automation": "YouTube Automation",
            "analytics_dashboard": "Analytics Dashboard",
            "cloud_processing": "Cloud ML Processing"
        }
        
        production_count = 0
        testing_count = 0
        dummy_count = 0
        error_count = 0
        
        for module_id in modules:
            module_data = config.get(module_id, {})
            status = module_data.get('status', 'dummy')
            name = module_names.get(module_id, module_id)
            
            # Contar por estado
            if status == 'production':
                production_count += 1
                status_display = f"{self.GREEN}🟢 PRODUCTION{self.RESET}"
            elif status == 'testing':
                testing_count += 1
                status_display = f"{self.YELLOW}🟡 TESTING{self.RESET}"
            elif status == 'error':
                error_count += 1
                status_display = f"{self.RED}🔴 ERROR{self.RESET}"
            else:  # dummy
                dummy_count += 1
                status_display = f"{self.WHITE}⚪ DUMMY{self.RESET}"
            
            # Información adicional
            errors = module_data.get('error_count', 0)
            health = module_data.get('health_score', 100.0)
            
            error_info = f" | Errors: {errors}" if errors > 0 else ""
            health_info = f" | Health: {health:.1f}%" if health < 100 else ""
            
            print(f"  {name:<25} {status_display}{error_info}{health_info}")
        
        # Resumen
        print(f"\n{self.BOLD}System Summary:{self.RESET}")
        print(f"  Production: {self.GREEN}{production_count}{self.RESET}")
        print(f"  Testing:    {self.YELLOW}{testing_count}{self.RESET}")
        print(f"  Dummy:      {self.WHITE}{dummy_count}{self.RESET}")
        print(f"  Errors:     {self.RED}{error_count}{self.RESET}")
        
        # Calcular salud general
        total_health = 0
        health_count = 0
        for module_data in config.values():
            if isinstance(module_data, dict) and 'health_score' in module_data:
                total_health += module_data['health_score']
                health_count += 1
        
        if health_count > 0:
            system_health = total_health / health_count
            
            if system_health >= 90:
                health_color = self.GREEN
                health_status = "EXCELLENT"
            elif system_health >= 70:
                health_color = self.YELLOW
                health_status = "GOOD"
            elif system_health >= 50:
                health_color = self.YELLOW
                health_status = "WARNING"
            else:
                health_color = self.RED
                health_status = "CRITICAL"
            
            print(f"  System Health: {health_color}{system_health:.1f}% ({health_status}){self.RESET}")
    
    def activate_module(self, module_id: str, mode: str = "testing"):
        """Activar módulo en el modo especificado"""
        
        valid_modules = [
            "telegram_bot", "ml_ultralytics", "device_farm", "meta_ads",
            "gologin_proxy", "youtube_automation", "analytics_dashboard", "cloud_processing"
        ]
        
        if module_id not in valid_modules:
            self.print_status(f"Invalid module: {module_id}", "error")
            self.print_status(f"Valid modules: {', '.join(valid_modules)}", "info")
            return False
        
        valid_modes = ["testing", "production"]
        if mode not in valid_modes:
            self.print_status(f"Invalid mode: {mode}", "error")
            self.print_status(f"Valid modes: {', '.join(valid_modes)}", "info")
            return False
        
        # Verificar dependencias si es producción
        if mode == "production":
            if not self._verify_module_dependencies(module_id):
                self.print_status(f"Cannot activate {module_id} in production: dependencies not met", "error")
                return False
            
            # Confirmación adicional para producción
            if not self._confirm_production_activation(module_id):
                self.print_status("Production activation cancelled by user", "warning")
                return False
        
        # Cargar configuración actual
        config = self.load_config()
        
        # Actualizar módulo
        if module_id not in config:
            config[module_id] = {}
        
        old_status = config[module_id].get('status', 'dummy')
        config[module_id]['status'] = mode
        config[module_id]['last_activated'] = datetime.now().isoformat()
        config[module_id]['activation_count'] = config[module_id].get('activation_count', 0) + 1
        
        # Actualizar variable de entorno
        self._update_module_environment(module_id, mode)
        
        # Guardar configuración
        self.save_config(config)
        
        # Log
        self.log_action("ACTIVATE", module_id, f"{old_status} -> {mode}")
        
        if mode == "production":
            self.print_status(f"🚀 {module_id} activated in PRODUCTION mode", "success")
        else:
            self.print_status(f"🟡 {module_id} activated in TESTING mode", "success")
        
        return True
    
    def deactivate_module(self, module_id: str):
        """Desactivar módulo (volver a dummy)"""
        
        config = self.load_config()
        
        if module_id not in config:
            self.print_status(f"Module {module_id} not found in configuration", "warning")
            return True  # Ya está en dummy por defecto
        
        old_status = config[module_id].get('status', 'dummy')
        config[module_id]['status'] = 'dummy'
        
        # Actualizar variable de entorno
        self._update_module_environment(module_id, 'dummy')
        
        # Guardar configuración
        self.save_config(config)
        
        # Log
        self.log_action("DEACTIVATE", module_id, f"{old_status} -> dummy")
        
        self.print_status(f"⚪ {module_id} deactivated - returned to dummy mode", "success")
        return True
    
    def emergency_stop(self):
        """Parada de emergencia total"""
        
        self.print_header("🚨 EMERGENCY STOP PROTOCOL")
        
        # Confirmación
        print(f"{self.RED}{self.BOLD}WARNING: This will immediately stop ALL production modules!{self.RESET}")
        confirm = input(f"{self.YELLOW}Type 'EMERGENCY STOP' to confirm: {self.RESET}")
        
        if confirm != "EMERGENCY STOP":
            self.print_status("Emergency stop cancelled", "info")
            return False
        
        config = self.load_config()
        stopped_modules = []
        
        # Parar todos los módulos que estén en producción
        for module_id, module_data in config.items():
            if isinstance(module_data, dict) and module_data.get('status') == 'production':
                module_data['status'] = 'dummy'
                self._update_module_environment(module_id, 'dummy')
                stopped_modules.append(module_id)
        
        # Set global dummy mode
        os.environ['DUMMY_MODE'] = 'true'
        self._update_env_file("DUMMY_MODE", "true")
        
        # Guardar configuración
        self.save_config(config)
        
        # Log
        self.log_action("EMERGENCY_STOP", "ALL", f"Stopped modules: {', '.join(stopped_modules)}")
        
        self.print_status(f"🚨 EMERGENCY STOP EXECUTED", "error")
        self.print_status(f"Stopped {len(stopped_modules)} production modules", "info")
        
        for module in stopped_modules:
            self.print_status(f"  - {module}", "info")
        
        return True
    
    def activate_safe_mode(self):
        """Activar modo seguro (todo a dummy)"""
        
        self.print_header("🛡️ SAFE MODE ACTIVATION")
        
        config = self.load_config()
        
        # Poner todos los módulos en dummy
        modules_changed = []
        for module_id in config:
            if isinstance(config[module_id], dict):
                old_status = config[module_id].get('status', 'dummy')
                if old_status != 'dummy':
                    config[module_id]['status'] = 'dummy'
                    config[module_id]['error_count'] = 0
                    self._update_module_environment(module_id, 'dummy')
                    modules_changed.append(module_id)
        
        # Set global dummy mode
        os.environ['DUMMY_MODE'] = 'true'
        self._update_env_file("DUMMY_MODE", "true")
        
        # Guardar configuración
        self.save_config(config)
        
        # Log
        self.log_action("SAFE_MODE", "ALL", f"Changed modules: {', '.join(modules_changed)}")
        
        self.print_status("🛡️ Safe mode activated", "success")
        self.print_status("All modules set to dummy mode", "info")
        self.print_status("All error counts reset", "info")
        
        return True
    
    def check_dependencies(self):
        """Verificar estado de dependencias"""
        
        self.print_header("📦 DEPENDENCY STATUS CHECK")
        
        print("Checking system dependencies...")
        
        deps_status = check_dependencies()
        
        print(f"\n{self.BOLD}Critical Dependencies:{self.RESET}")
        
        critical_ok = 0
        critical_total = 0
        
        for dep_name, status in deps_status.items():
            if status.critical:
                critical_total += 1
                
                if status.available:
                    critical_ok += 1
                    self.print_status(f"{dep_name} v{status.version}", "success")
                elif status.fallback_available:
                    self.print_status(f"{dep_name} (fallback mode)", "warning")
                else:
                    self.print_status(f"{dep_name} - {status.error_message}", "error")
        
        print(f"\n{self.BOLD}Optional Dependencies:{self.RESET}")
        
        optional_ok = 0
        optional_total = 0
        
        for dep_name, status in deps_status.items():
            if not status.critical:
                optional_total += 1
                
                if status.available:
                    optional_ok += 1
                    self.print_status(f"{dep_name} v{status.version}", "success")
                elif status.fallback_available:
                    self.print_status(f"{dep_name} (fallback available)", "info")
                else:
                    self.print_status(f"{dep_name} - not installed", "warning")
        
        # Resumen
        print(f"\n{self.BOLD}Summary:{self.RESET}")
        print(f"  Critical: {critical_ok}/{critical_total} available")
        print(f"  Optional: {optional_ok}/{optional_total} available")
        
        if critical_ok == critical_total:
            self.print_status("✅ All critical dependencies satisfied", "success")
        else:
            self.print_status(f"❌ Missing {critical_total - critical_ok} critical dependencies", "error")
        
        return critical_ok == critical_total
    
    def _verify_module_dependencies(self, module_id: str) -> bool:
        """Verificar dependencias específicas de un módulo"""
        
        module_deps = {
            "telegram_bot": ["telethon"],
            "ml_ultralytics": ["ultralytics", "torch"],
            "device_farm": ["selenium"],
            "meta_ads": ["facebook-business"],
            "gologin_proxy": ["selenium"],
            "youtube_automation": ["selenium", "google-api-python-client"],
            "analytics_dashboard": ["streamlit", "plotly"],
            "cloud_processing": ["boto3"]
        }
        
        required_deps = module_deps.get(module_id, [])
        deps_status = check_dependencies()
        
        for dep in required_deps:
            status = deps_status.get(dep)
            if not status or not status.available:
                return False
        
        return True
    
    def _confirm_production_activation(self, module_id: str) -> bool:
        """Confirmar activación de producción"""
        
        print(f"\n{self.RED}{self.BOLD}⚠️  PRODUCTION ACTIVATION WARNING ⚠️{self.RESET}")
        print(f"{self.RED}You are about to activate '{module_id}' in PRODUCTION mode.{self.RESET}")
        print(f"{self.RED}This will switch from simulation to REAL operations.{self.RESET}")
        print(f"{self.RED}This may affect real accounts, charge money, or use live APIs.{self.RESET}")
        
        confirm = input(f"\n{self.YELLOW}Type 'ACTIVATE PRODUCTION' to confirm: {self.RESET}")
        
        return confirm == "ACTIVATE PRODUCTION"
    
    def _update_module_environment(self, module_id: str, status: str):
        """Actualizar variables de entorno del módulo"""
        
        env_vars = {
            "telegram_bot": "TELEGRAM_BOT_MODE",
            "ml_ultralytics": "ULTRALYTICS_MODE",
            "device_farm": "DEVICE_FARM_MODE", 
            "meta_ads": "META_ADS_MODE",
            "gologin_proxy": "GOLOGIN_MODE",
            "youtube_automation": "YOUTUBE_MODE",
            "analytics_dashboard": "ANALYTICS_MODE",
            "cloud_processing": "CLOUD_PROCESSING_MODE"
        }
        
        env_var = env_vars.get(module_id)
        if env_var:
            os.environ[env_var] = status
            self._update_env_file(env_var, status)
    
    def _update_env_file(self, var_name: str, value: str):
        """Actualizar archivo .env"""
        
        env_file = Path("/workspaces/master/.env")
        lines = []
        var_updated = False
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                lines = f.readlines()
        
        # Actualizar o añadir variable
        for i, line in enumerate(lines):
            if line.startswith(f"{var_name}="):
                lines[i] = f"{var_name}={value}\n"
                var_updated = True
                break
        
        if not var_updated:
            lines.append(f"{var_name}={value}\n")
        
        # Escribir archivo
        with open(env_file, 'w') as f:
            f.writelines(lines)

def main():
    """Función principal del CLI"""
    
    parser = argparse.ArgumentParser(
        description="Production Control CLI - Red Button System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                           Show system status
  %(prog)s activate telegram_bot testing   Activate module in testing mode
  %(prog)s activate ml_ultralytics production  Activate in production (dangerous!)
  %(prog)s deactivate telegram_bot         Deactivate module (return to dummy)
  %(prog)s emergency-stop                  Emergency stop all production modules
  %(prog)s safe-mode                       Activate safe mode (all dummy)
  %(prog)s check-deps                      Check dependency status
        """
    )
    
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    # Activate command
    activate_parser = subparsers.add_parser('activate', help='Activate module')
    activate_parser.add_argument('module', help='Module ID to activate')
    activate_parser.add_argument('mode', nargs='?', default='testing',
                                choices=['testing', 'production'],
                                help='Activation mode (default: testing)')
    
    # Deactivate command
    deactivate_parser = subparsers.add_parser('deactivate', help='Deactivate module')
    deactivate_parser.add_argument('module', help='Module ID to deactivate')
    
    # Emergency commands
    subparsers.add_parser('emergency-stop', help='Emergency stop all production')
    subparsers.add_parser('safe-mode', help='Activate safe mode')
    
    # Dependency check
    subparsers.add_parser('check-deps', help='Check dependencies status')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create CLI instance
    cli = ProductionControlCLI()
    cli.verbose = args.verbose
    
    # Execute command
    try:
        if args.command == 'status':
            cli.show_system_status()
        
        elif args.command == 'activate':
            success = cli.activate_module(args.module, args.mode)
            sys.exit(0 if success else 1)
        
        elif args.command == 'deactivate':
            success = cli.deactivate_module(args.module)
            sys.exit(0 if success else 1)
        
        elif args.command == 'emergency-stop':
            success = cli.emergency_stop()
            sys.exit(0 if success else 1)
        
        elif args.command == 'safe-mode':
            success = cli.activate_safe_mode()
            sys.exit(0 if success else 1)
        
        elif args.command == 'check-deps':
            success = cli.check_dependencies()
            sys.exit(0 if success else 1)
        
        else:
            parser.print_help()
            sys.exit(1)
    
    except KeyboardInterrupt:
        cli.print_status("\n🚨 Operation interrupted by user", "warning")
        sys.exit(130)
    
    except Exception as e:
        cli.print_status(f"❌ Error: {e}", "error")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()