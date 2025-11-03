#!/usr/bin/env python3
"""
🎯 TikTok Viral ML System - Validador Multi-Ramas con Modo Dummy
================================================================

Validador inteligente que puede:
- ✅ Validar todas las ramas automáticamente
- 🎭 Modo dummy para testing sin dependencias pesadas
- 🔄 Switch automático entre configuraciones
- 📊 Comparación entre ramas
- 🚀 Recomendaciones específicas por rama

Uso:
    python validate_multibranch.py                    # Valida rama actual
    python validate_multibranch.py --all-branches     # Valida todas las ramas
    python validate_multibranch.py --dummy-mode       # Fuerza modo dummy
    python validate_multibranch.py --compare          # Compara todas las ramas
    python validate_multibranch.py --fix              # Auto-instala dependencias faltantes
"""

import os
import sys
import json
import subprocess
import importlib.util
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import argparse

# Configuración de colores
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_colored(text: str, color: str = Colors.ENDC) -> None:
    """Imprime texto con color"""
    print(f"{color}{text}{Colors.ENDC}")

def get_git_branch() -> str:
    """Obtiene la rama actual de Git"""
    try:
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True, cwd=Path.cwd())
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"

def check_dummy_mode() -> bool:
    """Verifica si el modo dummy está activo"""
    return os.getenv('DUMMY_MODE', 'false').lower() == 'true'

def get_python_info() -> Dict[str, Any]:
    """Obtiene información de Python"""
    return {
        'version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'major_minor': f"{sys.version_info.major}.{sys.version_info.minor}",
        'executable': sys.executable,
        'is_compatible': 3.9 <= sys.version_info.major + sys.version_info.minor/10 <= 3.11
    }

def check_system_dependencies() -> Dict[str, bool]:
    """Verifica dependencias del sistema"""
    deps = {}
    
    # Git
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
        deps['git'] = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        deps['git'] = False
    
    # FFmpeg (solo en modo producción)
    if not check_dummy_mode():
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            deps['ffmpeg'] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            deps['ffmpeg'] = False
    else:
        deps['ffmpeg'] = True  # No requerido en dummy mode
    
    # Node.js (opcional para n8n)
    try:
        subprocess.run(['node', '--version'], capture_output=True, check=True)
        deps['nodejs'] = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        deps['nodejs'] = False
    
    return deps

def check_python_package(package_name: str, optional: bool = False) -> Tuple[bool, str]:
    """Verifica si un paquete de Python está instalado"""
    try:
        importlib.import_module(package_name)
        return True, "✅"
    except ImportError:
        if optional and check_dummy_mode():
            return True, "🎭"  # OK en modo dummy
        return False, "❌"

def get_branch_requirements() -> Dict[str, Dict[str, List[str]]]:
    """Define requirements por rama con modo dummy"""
    
    # Core dependencies (siempre requeridas)
    core_deps = [
        'fastapi', 'uvicorn', 'pydantic', 'httpx', 'aiohttp', 'requests', 
        'numpy', 'pandas'
    ]
    
    # Dependencies que se relajan en modo dummy
    core_heavy = ['sqlalchemy', 'pillow'] if not check_dummy_mode() else []
    
    # Modulo 7 dependencies (relajadas en dummy)
    modulo7_audio = ['librosa', 'soundfile', 'torch_audio']
    modulo7_video = ['moviepy', 'imageio', 'cv2']
    modulo7_ml = ['transformers', 'sentence_transformers']
    
    return {
        'main': {
            'core': core_deps + core_heavy,
            'ml': ['torch', 'ultralytics', 'yolov8'] if not check_dummy_mode() else [],
            'device': ['appium-python-client', 'adb-shell'] if not check_dummy_mode() else [],
            'modulo7': modulo7_audio + modulo7_video + modulo7_ml if not check_dummy_mode() else []
        },
        'meta': {
            'core': core_deps + core_heavy,
            'meta': ['facebook-business'] if not check_dummy_mode() else [],
            'browser': ['selenium', 'playwright'] if not check_dummy_mode() else [],
            'gologin': ['gologin'] if not check_dummy_mode() else [],
            'modulo7': modulo7_video + modulo7_ml if not check_dummy_mode() else []
        },
        'tele': {
            'core': core_deps + core_heavy,
            'telegram': ['telethon'] + (['telegram', 'pyrogram'] if not check_dummy_mode() else []),
            'social': ['instagrapi', 'tweepy'] if not check_dummy_mode() else [],
            'modulo7': modulo7_audio + modulo7_video + modulo7_ml if not check_dummy_mode() else []
        },
        'dummy': {
            'core': core_deps,  # Solo lo esencial
            'testing': ['pytest', 'pytest-asyncio', 'pytest-mock'],
            'mock': []  # Todo simulado
        }
    }

def validate_branch_dependencies(branch: str, requirements: Dict[str, List[str]]) -> Dict[str, Any]:
    """Valida las dependencias de una rama específica"""
    results = {}
    total_checks = 0
    successful_checks = 0
    
    for category, deps in requirements.items():
        category_results = {}
        category_success = 0
        
        for dep in deps:
            is_available, status = check_python_package(dep, optional=check_dummy_mode())
            category_results[dep] = {
                'available': is_available,
                'status': status,
                'required': not check_dummy_mode()
            }
            
            total_checks += 1
            if is_available:
                successful_checks += 1
                category_success += 1
        
        results[category] = {
            'dependencies': category_results,
            'success_rate': (category_success / len(deps) * 100) if deps else 100,
            'total': len(deps),
            'successful': category_success
        }
    
    return {
        'branch': branch,
        'categories': results,
        'overall_success_rate': (successful_checks / total_checks * 100) if total_checks > 0 else 100,
        'total_checks': total_checks,
        'successful_checks': successful_checks,
        'dummy_mode': check_dummy_mode()
    }

def check_file_structure() -> Dict[str, Any]:
    """Verifica la estructura de archivos requerida"""
    required_files = [
        'requirements.txt',
        'requirements-rama.txt',
        'requirements-meta.txt', 
        'requirements-tele.txt',
        'requirements-dummy.txt',
        'install_dependencies.sh',
        'validate_dependencies.py',
        'DEPENDENCIES_GUIDE.md'
    ]
    
    required_dirs = [
        'data', 'logs', 'config', 'ml_core', 'device_farm', 
        'gologin_automation', 'social_extensions', 'orchestration'
    ]
    
    files_status = {}
    dirs_status = {}
    
    for file in required_files:
        files_status[file] = Path(file).exists()
    
    for dir in required_dirs:
        dirs_status[dir] = Path(dir).exists()
    
    return {
        'files': files_status,
        'directories': dirs_status,
        'files_success': sum(files_status.values()),
        'dirs_success': sum(dirs_status.values()),
        'total_files': len(required_files),
        'total_dirs': len(required_dirs)
    }

def generate_branch_report(branch: str, force_dummy: bool = False) -> Dict[str, Any]:
    """Genera reporte completo para una rama"""
    
    # Set dummy mode if forced
    original_dummy = os.getenv('DUMMY_MODE')
    if force_dummy:
        os.environ['DUMMY_MODE'] = 'true'
    
    try:
        requirements = get_branch_requirements()
        branch_reqs = requirements.get(branch, requirements.get('dummy', {}))
        
        # Validaciones
        python_info = get_python_info()
        system_deps = check_system_dependencies()
        file_structure = check_file_structure()
        dependencies = validate_branch_dependencies(branch, branch_reqs)
        
        # Cálculo de score general
        scores = {
            'python': 100 if python_info['is_compatible'] else 70,
            'system': (sum(system_deps.values()) / len(system_deps)) * 100,
            'files': ((file_structure['files_success'] + file_structure['dirs_success']) / 
                     (file_structure['total_files'] + file_structure['total_dirs'])) * 100,
            'dependencies': dependencies['overall_success_rate']
        }
        
        overall_score = sum(scores.values()) / len(scores)
        
        return {
            'branch': branch,
            'timestamp': datetime.now().isoformat(),
            'dummy_mode': check_dummy_mode(),
            'python': python_info,
            'system': system_deps,
            'file_structure': file_structure,
            'dependencies': dependencies,
            'scores': scores,
            'overall_score': overall_score,
            'status': 'READY' if overall_score >= 85 else 'PARTIAL' if overall_score >= 60 else 'INCOMPLETE'
        }
    
    finally:
        # Restore original dummy mode
        if original_dummy is None:
            os.environ.pop('DUMMY_MODE', None)
        else:
            os.environ['DUMMY_MODE'] = original_dummy

def print_branch_report(report: Dict[str, Any], detailed: bool = True):
    """Imprime reporte de una rama"""
    
    branch = report['branch']
    score = report['overall_score']
    status = report['status']
    dummy_mode = report['dummy_mode']
    
    # Header
    print_colored(f"\n🎯 VALIDACIÓN RAMA: {branch.upper()}", Colors.HEADER + Colors.BOLD)
    print_colored("=" * 60, Colors.HEADER)
    
    if dummy_mode:
        print_colored("🎭 MODO DUMMY ACTIVO - Testing sin dependencias pesadas", Colors.OKCYAN)
    
    # Score general
    color = Colors.OKGREEN if score >= 85 else Colors.WARNING if score >= 60 else Colors.FAIL
    print_colored(f"📊 Score General: {score:.1f}% - {status}", color + Colors.BOLD)
    
    if not detailed:
        return
    
    # Python info
    python = report['python']
    python_color = Colors.OKGREEN if python['is_compatible'] else Colors.WARNING
    print_colored(f"\n🐍 PYTHON", Colors.OKBLUE + Colors.BOLD)
    print_colored(f"   Versión: {python['version']} {Colors.OKGREEN + '✅' if python['is_compatible'] else Colors.WARNING + '⚠️'}", python_color)
    
    # System dependencies
    print_colored(f"\n🔧 SISTEMA", Colors.OKBLUE + Colors.BOLD)
    for dep, available in report['system'].items():
        status_icon = "✅" if available else "❌"
        color = Colors.OKGREEN if available else Colors.FAIL
        print_colored(f"   {dep}: {status_icon}", color)
    
    # File structure
    structure = report['file_structure']
    structure_score = ((structure['files_success'] + structure['dirs_success']) / 
                      (structure['total_files'] + structure['total_dirs'])) * 100
    print_colored(f"\n📁 ESTRUCTURA: {structure_score:.0f}%", Colors.OKBLUE + Colors.BOLD)
    
    # Dependencies by category
    deps = report['dependencies']['categories']
    print_colored(f"\n📦 DEPENDENCIAS", Colors.OKBLUE + Colors.BOLD)
    
    for category, data in deps.items():
        success_rate = data['success_rate']
        successful = data['successful']
        total = data['total']
        
        color = Colors.OKGREEN if success_rate >= 85 else Colors.WARNING if success_rate >= 60 else Colors.FAIL
        print_colored(f"   {category.upper()}: {successful}/{total} ({success_rate:.0f}%)", color)
        
        # Top missing dependencies
        missing = [dep for dep, info in data['dependencies'].items() if not info['available']]
        if missing and not dummy_mode:
            print_colored(f"      Faltantes: {', '.join(missing[:3])}", Colors.FAIL)
    
    # Recommendations
    print_colored(f"\n💡 RECOMENDACIONES", Colors.OKCYAN + Colors.BOLD)
    
    if score >= 85:
        print_colored("   ✅ Sistema listo para usar", Colors.OKGREEN)
    elif score >= 60:
        print_colored("   ⚠️  Sistema parcialmente funcional", Colors.WARNING)
        if not dummy_mode:
            print_colored(f"   🔧 Ejecuta: ./install_dependencies.sh --{branch}", Colors.OKCYAN)
    else:
        print_colored("   ❌ Sistema incompleto", Colors.FAIL)
        if dummy_mode:
            print_colored("   🎭 Considera usar modo producción para funcionalidad completa", Colors.OKCYAN)
        else:
            print_colored(f"   🔧 Ejecuta: ./install_dependencies.sh --{branch}", Colors.OKCYAN)

def compare_branches(branches: List[str], force_dummy: bool = False) -> Dict[str, Any]:
    """Compara múltiples ramas"""
    reports = {}
    
    print_colored(f"\n🔄 COMPARANDO {len(branches)} RAMAS...", Colors.HEADER + Colors.BOLD)
    if force_dummy:
        print_colored("🎭 Comparación en modo dummy", Colors.OKCYAN)
    
    for branch in branches:
        print_colored(f"   Analizando {branch}...", Colors.OKBLUE)
        reports[branch] = generate_branch_report(branch, force_dummy)
    
    # Tabla comparativa
    print_colored(f"\n📊 TABLA COMPARATIVA", Colors.HEADER + Colors.BOLD)
    print_colored("=" * 80, Colors.HEADER)
    
    # Header
    header = f"{'RAMA':<10} {'SCORE':<8} {'STATUS':<12} {'DEPS':<8} {'FILES':<8} {'SISTEMA':<8}"
    print_colored(header, Colors.BOLD)
    print_colored("-" * 80, Colors.HEADER)
    
    # Rows
    for branch, report in reports.items():
        score = report['overall_score']
        status = report['status']
        deps_score = report['dependencies']['overall_success_rate']
        files_score = ((report['file_structure']['files_success'] + report['file_structure']['dirs_success']) / 
                      (report['file_structure']['total_files'] + report['file_structure']['total_dirs'])) * 100
        system_score = (sum(report['system'].values()) / len(report['system'])) * 100
        
        color = Colors.OKGREEN if score >= 85 else Colors.WARNING if score >= 60 else Colors.FAIL
        
        row = f"{branch:<10} {score:>6.1f}% {status:<12} {deps_score:>6.1f}% {files_score:>6.1f}% {system_score:>6.1f}%"
        print_colored(row, color)
    
    # Summary
    best_branch = max(reports.keys(), key=lambda k: reports[k]['overall_score'])
    worst_branch = min(reports.keys(), key=lambda k: reports[k]['overall_score'])
    avg_score = sum(r['overall_score'] for r in reports.values()) / len(reports)
    
    print_colored(f"\n📈 RESUMEN COMPARATIVO", Colors.OKCYAN + Colors.BOLD)
    print_colored(f"   🏆 Mejor rama: {best_branch} ({reports[best_branch]['overall_score']:.1f}%)", Colors.OKGREEN)
    print_colored(f"   🔧 Rama a mejorar: {worst_branch} ({reports[worst_branch]['overall_score']:.1f}%)", Colors.FAIL)
    print_colored(f"   📊 Score promedio: {avg_score:.1f}%", Colors.OKBLUE)
    
    return reports

def auto_fix_dependencies(branch: str):
    """Intenta instalar automáticamente las dependencias faltantes"""
    print_colored(f"\n🔧 AUTO-REPARACIÓN RAMA: {branch.upper()}", Colors.HEADER + Colors.BOLD)
    
    # Check if install script exists
    install_script = Path('./install_dependencies.sh')
    if not install_script.exists():
        print_colored("❌ Script de instalación no encontrado", Colors.FAIL)
        return False
    
    # Make script executable
    try:
        subprocess.run(['chmod', '+x', str(install_script)], check=True)
        print_colored("✅ Script de instalación preparado", Colors.OKGREEN)
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ Error preparando script: {e}", Colors.FAIL)
        return False
    
    # Execute installation
    try:
        print_colored(f"🚀 Instalando dependencias para rama {branch}...", Colors.OKCYAN)
        result = subprocess.run([str(install_script), f'--{branch}'], 
                               capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print_colored("✅ Instalación completada exitosamente", Colors.OKGREEN)
            print_colored("🔄 Ejecutando validación post-instalación...", Colors.OKCYAN)
            
            # Re-validate
            report = generate_branch_report(branch)
            print_branch_report(report, detailed=False)
            
            return True
        else:
            print_colored(f"❌ Error en instalación: {result.stderr}", Colors.FAIL)
            return False
            
    except subprocess.TimeoutExpired:
        print_colored("❌ Timeout en instalación (>5 min)", Colors.FAIL)
        return False
    except Exception as e:
        print_colored(f"❌ Error ejecutando instalación: {e}", Colors.FAIL)
        return False

def save_report(reports: Dict[str, Any], filename: str = None):
    """Guarda reporte en JSON"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"validation_report_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(reports, f, indent=2, ensure_ascii=False, default=str)
    
    print_colored(f"💾 Reporte guardado en: {filename}", Colors.OKCYAN)

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Validador Multi-Ramas TikTok ML System')
    parser.add_argument('--all-branches', action='store_true', 
                       help='Valida todas las ramas disponibles')
    parser.add_argument('--compare', action='store_true',
                       help='Compara todas las ramas')
    parser.add_argument('--dummy-mode', action='store_true',
                       help='Fuerza modo dummy para todas las validaciones')
    parser.add_argument('--fix', action='store_true',
                       help='Intenta auto-instalar dependencias faltantes')
    parser.add_argument('--branch', type=str,
                       help='Valida rama específica (main, meta, tele)')
    parser.add_argument('--save', type=str,
                       help='Guarda reporte en archivo JSON')
    parser.add_argument('--quiet', action='store_true',
                       help='Modo silencioso - solo resultados finales')
    
    args = parser.parse_args()
    
    # Header
    if not args.quiet:
        print_colored("🎯 TikTok Viral ML System - Validador Multi-Ramas", Colors.HEADER + Colors.BOLD)
        print_colored("=" * 70, Colors.HEADER)
        print_colored(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.OKBLUE)
    
    # Force dummy mode if requested
    if args.dummy_mode:
        os.environ['DUMMY_MODE'] = 'true'
        if not args.quiet:
            print_colored("🎭 Modo dummy forzado globalmente", Colors.OKCYAN)
    
    # Available branches
    available_branches = ['main', 'meta', 'tele', 'dummy']
    current_branch = get_git_branch()
    
    if not args.quiet:
        print_colored(f"🌿 Rama actual: {current_branch}", Colors.OKBLUE)
        print_colored(f"🎭 Modo dummy: {'Activo' if check_dummy_mode() else 'Inactivo'}", Colors.OKCYAN)
    
    reports = {}
    
    try:
        if args.compare or args.all_branches:
            # Compare all branches
            branches_to_check = available_branches if args.all_branches else ['main', 'meta', 'tele']
            reports = compare_branches(branches_to_check, args.dummy_mode)
            
        elif args.branch:
            # Specific branch
            if args.branch not in available_branches:
                print_colored(f"❌ Rama '{args.branch}' no reconocida. Disponibles: {available_branches}", Colors.FAIL)
                return 1
            
            report = generate_branch_report(args.branch, args.dummy_mode)
            reports[args.branch] = report
            
            if not args.quiet:
                print_branch_report(report)
            
        else:
            # Current branch
            branch_to_check = current_branch if current_branch in available_branches else 'dummy'
            report = generate_branch_report(branch_to_check, args.dummy_mode)
            reports[branch_to_check] = report
            
            if not args.quiet:
                print_branch_report(report)
        
        # Auto-fix if requested
        if args.fix:
            for branch in reports.keys():
                if reports[branch]['overall_score'] < 85:
                    auto_fix_dependencies(branch)
        
        # Save report if requested
        if args.save:
            save_report(reports, args.save)
        
        # Final summary
        if not args.quiet:
            avg_score = sum(r['overall_score'] for r in reports.values()) / len(reports)
            ready_count = sum(1 for r in reports.values() if r['status'] == 'READY')
            total_count = len(reports)
            
            print_colored(f"\n🎯 RESUMEN FINAL", Colors.HEADER + Colors.BOLD)
            print_colored("=" * 50, Colors.HEADER)
            print_colored(f"📊 Score promedio: {avg_score:.1f}%", Colors.OKBLUE)
            print_colored(f"✅ Ramas listas: {ready_count}/{total_count}", Colors.OKGREEN)
            
            if ready_count == total_count:
                print_colored("🎉 ¡Todas las ramas están listas!", Colors.OKGREEN + Colors.BOLD)
                return 0
            elif avg_score >= 60:
                print_colored("⚠️  Sistema parcialmente funcional", Colors.WARNING + Colors.BOLD)
                return 1
            else:
                print_colored("❌ Sistema requiere configuración", Colors.FAIL + Colors.BOLD)
                return 2
        
        return 0
    
    except KeyboardInterrupt:
        print_colored("\n⏹️  Validación interrumpida por usuario", Colors.WARNING)
        return 130
    
    except Exception as e:
        print_colored(f"\n❌ Error inesperado: {e}", Colors.FAIL)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)