#!/usr/bin/env python3
"""
Test Documentation System

Script simple para probar el sistema de documentación sin dependencias externas.
Verifica que todos los componentes funcionen correctamente en modo fallback.

Autor: Sistema de Documentación
Fecha: 2024
"""

import sys
import os
from pathlib import Path

# Añadir el directorio del proyecto al path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

def test_auto_updater():
    """Probar el sistema de auto-actualización"""
    
    print("\n🔄 Testing Auto-Update System...")
    
    try:
        # Import local
        from scripts.auto_update_docs import DocumentationAutoUpdater
        
        # Crear instancia
        updater = DocumentationAutoUpdater()
        
        # Test básico - verificar que inicializa correctamente
        print(f"✅ Auto-updater initialized")
        print(f"   📁 Repo path: {updater.repo_path}")
        print(f"   📄 Docs path: {updater.docs_path}")
        
        # Test de detección de cambios simulados
        import asyncio
        from datetime import datetime, timedelta
        
        # Ejecutar detección de cambios
        last_scan = datetime.now() - timedelta(hours=6)
        changes = asyncio.run(updater.detect_code_changes(since=last_scan))
        
        print(f"   📊 Changes detected: {len(changes)}")
        
        if changes:
            for change in changes[:3]:  # Mostrar primeros 3
                print(f"     • {change.file_path}: {len(change.function_changes)} functions, {len(change.class_changes)} classes")
        
        print("✅ Auto-updater system working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Auto-updater test failed: {e}")
        return False

def test_dashboard_cli():
    """Probar el dashboard en modo CLI"""
    
    print("\n📊 Testing Dashboard System...")
    
    try:
        # Import local
        from scripts.documentation_dashboard import DocumentationDashboard, CLIDashboard
        
        # Probar dashboard básico
        dashboard = DocumentationDashboard()
        
        print(f"✅ Dashboard initialized")
        print(f"   📁 Repo path: {dashboard.repo_path}")
        
        # Test de obtención de documentos
        docs = dashboard.get_all_documentation_files()
        print(f"   📄 Documentation files found: {len(docs)}")
        
        if docs:
            for doc in docs[:3]:  # Mostrar primeros 3
                print(f"     • {doc.name}: {doc.word_count} words, {doc.code_blocks} code blocks")
        
        # Test de búsqueda
        if docs:
            results = dashboard.search_documentation("ML integration")
            print(f"   🔍 Search results for 'ML integration': {len(results)}")
        
        # Test health metrics
        health = dashboard.calculate_health_metrics()
        print(f"   🏥 System health score: {health['overall_score']:.1f}/100")
        
        print("✅ Dashboard system working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

def test_simulation_data():
    """Probar el generador de datos simulados"""
    
    print("\n🎭 Testing Simulation Data Generator...")
    
    try:
        # Import local
        from scripts.generate_simulation_data import DocumentationDataSimulator
        
        # Crear instancia
        simulator = DocumentationDataSimulator()
        
        print(f"✅ Simulator initialized")
        print(f"   📁 Data path: {simulator.data_dir}")
        
        # Generar datos de prueba
        analytics = simulator.generate_usage_analytics(7)  # 7 días
        
        print(f"   📊 Analytics generated:")
        print(f"     • Total views: {analytics['overview']['total_views']}")
        print(f"     • Documents tracked: {len(analytics['popular_documents'])}")
        print(f"     • Daily trends: {len(analytics['trends'])} days")
        
        # Health metrics
        health = simulator.generate_system_health()
        print(f"   🏥 Health metrics:")
        print(f"     • Overall score: {health['overall_score']:.1f}/100")
        print(f"     • Issues found: {len(health['issues'])}")
        
        print("✅ Simulation system working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Simulation test failed: {e}")
        return False

def test_file_structure():
    """Verificar estructura de archivos"""
    
    print("\n📁 Testing File Structure...")
    
    required_files = [
        "scripts/auto_update_docs.py",
        "scripts/documentation_dashboard.py", 
        "scripts/generate_simulation_data.py",
        "scripts/setup_documentation_system.sh",
        "docs/functionality_guides/README_SYSTEM.md"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = repo_root / file_path
        if full_path.exists():
            size_kb = full_path.stat().st_size / 1024
            print(f"   ✅ {file_path} ({size_kb:.1f} KB)")
        else:
            print(f"   ❌ {file_path} (missing)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing {len(missing_files)} required files")
        return False
    else:
        print("✅ All required files present")
        return True

def test_imports():
    """Probar importaciones y dependencias"""
    
    print("\n🐍 Testing Python Imports...")
    
    # Core imports que siempre deben funcionar
    core_modules = [
        'os', 'sys', 'json', 'datetime', 'pathlib', 'typing', 
        'collections', 'dataclasses', 'asyncio', 're', 'ast'
    ]
    
    for module in core_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError as e:
            print(f"   ❌ {module}: {e}")
            return False
    
    # Optional imports
    optional_modules = [
        ('streamlit', 'Web dashboard functionality'),
        ('plotly', 'Interactive charts'),
        ('pandas', 'Data analysis'),
        ('git', 'Git integration')
    ]
    
    print("\n   Optional dependencies:")
    for module, description in optional_modules:
        try:
            __import__(module)
            print(f"   ✅ {module} - {description}")
        except ImportError:
            print(f"   ⚠️  {module} - {description} (fallback mode available)")
    
    print("✅ Import testing completed")
    return True

def run_interactive_demo():
    """Ejecutar demo interactivo"""
    
    print("\n🎮 Interactive Demo Mode")
    print("=" * 30)
    
    try:
        from scripts.documentation_dashboard import CLIDashboard
        
        # Crear CLI dashboard
        cli = CLIDashboard()
        
        print("Starting CLI Dashboard...")
        cli.run_cli()
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")

def main():
    """Función principal de testing"""
    
    print("🧪 Documentation System Test Suite")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Python Imports", test_imports),
        ("Auto-Update System", test_auto_updater),
        ("Dashboard System", test_dashboard_cli),
        ("Simulation Data", test_simulation_data)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📋 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:10} {test_name}")
        if success:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! System is ready to use.")
        
        # Ofrecer demo interactivo
        response = input("\n🎮 Run interactive demo? (y/N): ").strip().lower()
        if response == 'y':
            run_interactive_demo()
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return 0 if passed == len(results) else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n👋 Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)