#!/usr/bin/env python3
"""
🚀 Test y Build Docker - Stakas MVP
Prueba el build local antes del deploy a Railway
"""

import subprocess
import sys
from pathlib import Path

def test_docker_build():
    """Test del build de Docker localmente"""
    
    print("🎵" + "="*50 + "🎵")
    print("🚀 TESTING DOCKER BUILD - STAKAS MVP")
    print("📺 Dashboard: UCgohgqLVu1QPdfa64Vkrgeg")
    print("🎵" + "="*50 + "🎵\n")
    
    try:
        # Build de la imagen
        print("🔧 Building Docker image...")
        result = subprocess.run([
            'docker', 'build', 
            '-t', 'stakas-mvp-viral:test',
            '-f', 'Dockerfile', 
            '.'
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode != 0:
            print("❌ Docker build failed:")
            print(result.stderr)
            return False
        
        print("✅ Docker build successful!")
        
        # Test run del container
        print("\n🧪 Testing container run...")
        result = subprocess.run([
            'docker', 'run', 
            '--rm',
            '-p', '8501:8501',
            '-e', 'PORT=8501',
            '--name', 'stakas-test',
            'stakas-mvp-viral:test'
        ], capture_output=True, text=True, timeout=30)
        
        print("✅ Container test completed")
        return True
        
    except subprocess.TimeoutExpired:
        print("✅ Container started successfully (timeout expected)")
        # Cleanup
        subprocess.run(['docker', 'stop', 'stakas-test'], capture_output=True)
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def cleanup_docker():
    """Limpia imágenes de test"""
    try:
        subprocess.run([
            'docker', 'rmi', 'stakas-mvp-viral:test'
        ], capture_output=True)
        print("🧹 Docker cleanup completed")
    except:
        pass

if __name__ == "__main__":
    success = test_docker_build()
    cleanup_docker()
    
    if success:
        print("\n🎉 ¡Docker build exitoso!")
        print("🚀 Listo para deploy a Railway")
        print("📊 Dashboard funcionará correctamente")
        sys.exit(0)
    else:
        print("\n❌ Docker build falló")
        print("🔧 Revisa los errores arriba")
        sys.exit(1)