#!/usr/bin/env python3
"""
Production Control Launcher

Launcher para el sistema de control de producción.
Detecta automáticamente si puede usar Streamlit o CLI.

🔴 RED BUTTON SYSTEM LAUNCHER 🔴

Uso:
    python red_button_control.py              # Auto-detect mode
    python red_button_control.py --web        # Force web dashboard
    python red_button_control.py --cli        # Force CLI mode
    python red_button_control.py status       # Quick status via CLI
    python red_button_control.py emergency    # Emergency controls

Autor: Sistema de Control de Producción  
Fecha: 2024
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, '/workspaces/master')

def check_streamlit_available():
    """Verificar si Streamlit está disponible"""
    
    try:
        import streamlit
        return True
    except ImportError:
        return False

def check_display_available():
    """Verificar si hay display disponible para web"""
    
    return os.getenv('DISPLAY') is not None or os.getenv('BROWSER') is not None

def run_web_dashboard():
    """Ejecutar dashboard web con Streamlit"""
    
    print("🔴 Starting Production Control Dashboard (Web Mode)...")
    print("🌐 Opening in browser at http://localhost:8501")
    print("⚡ Press Ctrl+C to stop\n")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run',
            '/workspaces/master/scripts/production_control_dashboard.py',
            '--server.port', '8501',
            '--server.address', '0.0.0.0',
            '--theme.base', 'dark',
            '--theme.primaryColor', '#ff0000'
        ])
    except KeyboardInterrupt:
        print("\n🔴 Dashboard stopped by user")

def run_cli_mode(args=None):
    """Ejecutar modo CLI"""
    
    cli_script = '/workspaces/master/scripts/production_control_cli.py'
    
    if args and len(args) > 0:
        # Pasar argumentos al CLI
        cmd = [sys.executable, cli_script] + args
    else:
        # Modo interactivo
        cmd = [sys.executable, cli_script, 'status']
    
    subprocess.run(cmd)

def run_interactive_cli():
    """Ejecutar CLI interactivo"""
    
    print("🔴 Production Control System - Interactive CLI Mode")
    print("=" * 50)
    
    while True:
        print("\nAvailable commands:")
        print("  1. Show system status")
        print("  2. Activate module")
        print("  3. Deactivate module")
        print("  4. Check dependencies")
        print("  5. Emergency stop")
        print("  6. Safe mode")
        print("  7. Exit")
        
        try:
            choice = input("\nEnter choice (1-7): ").strip()
            
            if choice == '1':
                run_cli_mode(['status'])
            
            elif choice == '2':
                modules = [
                    "telegram_bot", "ml_ultralytics", "device_farm", "meta_ads",
                    "gologin_proxy", "youtube_automation", "analytics_dashboard", "cloud_processing"
                ]
                
                print("\nAvailable modules:")
                for i, module in enumerate(modules, 1):
                    print(f"  {i}. {module}")
                
                try:
                    module_choice = int(input("\nSelect module (1-8): ")) - 1
                    if 0 <= module_choice < len(modules):
                        module = modules[module_choice]
                        
                        mode = input("Mode (testing/production) [testing]: ").strip().lower()
                        if not mode:
                            mode = "testing"
                        
                        if mode in ['testing', 'production']:
                            run_cli_mode(['activate', module, mode])
                        else:
                            print("❌ Invalid mode. Use 'testing' or 'production'")
                    else:
                        print("❌ Invalid module selection")
                except ValueError:
                    print("❌ Invalid input. Please enter a number.")
            
            elif choice == '3':
                modules = [
                    "telegram_bot", "ml_ultralytics", "device_farm", "meta_ads",
                    "gologin_proxy", "youtube_automation", "analytics_dashboard", "cloud_processing"
                ]
                
                print("\nAvailable modules:")
                for i, module in enumerate(modules, 1):
                    print(f"  {i}. {module}")
                
                try:
                    module_choice = int(input("\nSelect module to deactivate (1-8): ")) - 1
                    if 0 <= module_choice < len(modules):
                        module = modules[module_choice]
                        run_cli_mode(['deactivate', module])
                    else:
                        print("❌ Invalid module selection")
                except ValueError:
                    print("❌ Invalid input. Please enter a number.")
            
            elif choice == '4':
                run_cli_mode(['check-deps'])
            
            elif choice == '5':
                print("\n🚨 WARNING: This will stop ALL production modules!")
                confirm = input("Type 'yes' to confirm emergency stop: ")
                if confirm.lower() == 'yes':
                    run_cli_mode(['emergency-stop'])
            
            elif choice == '6':
                run_cli_mode(['safe-mode'])
            
            elif choice == '7':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1-7.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Goodbye!")
            break

def show_quick_status():
    """Mostrar estado rápido del sistema"""
    
    print("🔴 Production Control System - Quick Status")
    print("=" * 45)
    
    run_cli_mode(['status'])

def emergency_controls():
    """Controles de emergencia rápidos"""
    
    print("🚨 EMERGENCY CONTROLS")
    print("=" * 20)
    print("1. Emergency Stop (stop all production)")
    print("2. Safe Mode (all modules to dummy)")
    print("3. Check system status")
    print("4. Cancel")
    
    try:
        choice = input("\nSelect emergency action (1-4): ").strip()
        
        if choice == '1':
            print("\n🚨 EMERGENCY STOP PROTOCOL")
            confirm = input("Type 'EMERGENCY' to confirm: ")
            if confirm == 'EMERGENCY':
                run_cli_mode(['emergency-stop'])
        
        elif choice == '2':
            run_cli_mode(['safe-mode'])
        
        elif choice == '3':
            run_cli_mode(['status'])
        
        elif choice == '4':
            print("Emergency controls cancelled")
        
        else:
            print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n🚨 Emergency controls interrupted")

def main():
    """Función principal del launcher"""
    
    parser = argparse.ArgumentParser(
        description="Production Control System Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🔴 RED BUTTON SYSTEM 🔴

This launcher provides multiple ways to access the production control system:

1. Web Dashboard (preferred):
   - Full graphical interface with real-time status
   - Individual module control with safety confirmations  
   - Dependency management and system monitoring
   - Emergency controls with visual feedback

2. Command Line Interface:
   - Quick status checks and module control
   - Scriptable for automation
   - Emergency controls for headless systems

The launcher automatically detects the best available mode.

Examples:
  %(prog)s                    # Auto-detect best interface
  %(prog)s --web              # Force web dashboard  
  %(prog)s --cli              # Force CLI mode
  %(prog)s status             # Quick status check
  %(prog)s emergency          # Emergency controls menu
        """
    )
    
    parser.add_argument('--web', action='store_true',
                       help='Force web dashboard mode')
    parser.add_argument('--cli', action='store_true', 
                       help='Force CLI mode')
    parser.add_argument('--interactive', action='store_true',
                       help='Interactive CLI menu')
    
    # Special quick commands
    parser.add_argument('quick_command', nargs='?', 
                       choices=['status', 'emergency'],
                       help='Quick command to execute')
    
    args = parser.parse_args()
    
    # Handle quick commands first
    if args.quick_command == 'status':
        show_quick_status()
        return
    
    if args.quick_command == 'emergency':
        emergency_controls()
        return
    
    # Check capabilities
    streamlit_available = check_streamlit_available()
    display_available = check_display_available()
    
    print("🔴 Production Control System Launcher")
    print("=" * 40)
    print(f"Streamlit available: {'✅' if streamlit_available else '❌'}")
    print(f"Display available: {'✅' if display_available else '❌'}")
    print()
    
    # Decide mode
    if args.web:
        if streamlit_available:
            run_web_dashboard()
        else:
            print("❌ Streamlit not available. Install with: pip install streamlit")
            print("🔄 Falling back to CLI mode...")
            time.sleep(2)
            
            if args.interactive:
                run_interactive_cli()
            else:
                run_cli_mode()
    
    elif args.cli:
        if args.interactive:
            run_interactive_cli()
        else:
            run_cli_mode()
    
    elif args.interactive:
        run_interactive_cli()
    
    else:
        # Auto-detect best mode
        if streamlit_available and display_available:
            print("🌐 Auto-selecting web dashboard mode")
            print("💡 Use --cli flag to force CLI mode")
            print()
            run_web_dashboard()
        
        elif streamlit_available:
            print("🌐 Streamlit available but no display detected")
            print("🔄 Starting web server anyway (access via browser)")
            print()
            run_web_dashboard()
        
        else:
            print("🖥️  Auto-selecting CLI mode")
            print("💡 Install Streamlit for web dashboard: pip install streamlit")
            print()
            run_interactive_cli()

if __name__ == "__main__":
    main()