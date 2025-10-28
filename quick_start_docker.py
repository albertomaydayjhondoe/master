#!/usr/bin/env python3
"""
🚀 Quick Start Script para Stakas MVP Docker
Build, test y deploy rápido del sistema viral
"""

import subprocess
import sys
import time
from pathlib import Path

def run_command(cmd, description, check=True):
    """Ejecutar comando con output en tiempo real"""
    print(f"\n🔄 {description}...")
    print(f"💻 Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=check, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - OK")
            return True
        else:
            print(f"❌ {description} - FAILED (code: {result.returncode})")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - ERROR: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ {description} - Comando no encontrado")
        return False

def quick_build():
    """Build rápido de Docker image"""
    print("🏗️  QUICK BUILD - Stakas MVP Docker Image")
    
    build_cmd = [
        "docker", "build", 
        "-t", "stakas-mvp:latest",
        "--build-arg", "CHANNEL_ID=UCgohgqLVu1QPdfa64Vkrgeg",
        "--build-arg", "ENVIRONMENT=development",
        "."
    ]
    
    return run_command(build_cmd, "Building Docker image")

def quick_test():
    """Test rápido del contenedor"""
    print("\n🧪 QUICK TEST - Testing Docker Container")
    
    # Stop previous test container
    subprocess.run(["docker", "stop", "stakas-test"], capture_output=True)
    subprocess.run(["docker", "rm", "stakas-test"], capture_output=True)
    
    # Run test container
    test_cmd = [
        "docker", "run", "-d",
        "--name", "stakas-test",
        "-p", "8080:8080",
        "-e", "DUMMY_MODE=true",
        "-e", "CHANNEL_ID=UCgohgqLVu1QPdfa64Vkrgeg",
        "stakas-mvp:latest"
    ]
    
    if not run_command(test_cmd, "Starting test container"):
        return False
    
    print("⏳ Waiting for app to start...")
    time.sleep(20)
    
    # Test health
    health_cmd = ["docker", "exec", "stakas-test", "curl", "-f", "http://localhost:8080/health"]
    success = run_command(health_cmd, "Health check", check=False)
    
    if success:
        print("🎉 SUCCESS! App running at http://localhost:8080")
        print("🔍 Check logs with: docker logs stakas-test")
    else:
        # Show logs on failure
        print("\n📋 Container logs:")
        subprocess.run(["docker", "logs", "--tail", "20", "stakas-test"])
    
    return success

def quick_compose():
    """Test con docker-compose"""
    print("\n🐳 QUICK COMPOSE - Testing with Docker Compose")
    
    # Use development compose file
    compose_cmd = [
        "docker-compose", "-f", "docker-compose.dev.yml",
        "up", "-d", "--build"
    ]
    
    return run_command(compose_cmd, "Starting with Docker Compose")

def quick_deploy():
    """Quick deploy a Railway"""
    print("\n🚀 QUICK DEPLOY - Railway Deployment")
    
    # Run the deployment script
    deploy_cmd = ["python", "railway_deploy.py"]
    return run_command(deploy_cmd, "Running Railway deployment", check=False)

def cleanup():
    """Limpiar recursos"""
    print("\n🧹 CLEANUP - Removing test containers")
    
    cleanup_cmds = [
        ["docker", "stop", "stakas-test"],
        ["docker", "rm", "stakas-test"],
        ["docker-compose", "-f", "docker-compose.dev.yml", "down"]
    ]
    
    for cmd in cleanup_cmds:
        run_command(cmd, f"Cleanup: {' '.join(cmd)}", check=False)

def main():
    """Menú interactivo principal"""
    print("=" * 60)
    print("🎵 STAKAS MVP - QUICK START DOCKER")
    print("📺 Canal: UCgohgqLVu1QPdfa64Vkrgeg")
    print("💰 Meta Ads Budget: €500/month")
    print("=" * 60)
    
    while True:
        print("\n🎛️  QUICK START OPTIONS:")
        print("1. 🏗️  Quick Build (Docker image)")
        print("2. 🧪 Quick Test (Single container)")
        print("3. 🐳 Quick Compose (Full stack)")
        print("4. 🚀 Quick Deploy (Railway)")
        print("5. 🧹 Cleanup (Remove containers)")
        print("6. 🎯 All-in-One (Build + Test + Info)")
        print("7. ❌ Exit")
        
        choice = input("\n👉 Choose option (1-7): ").strip()
        
        if choice == "1":
            quick_build()
            
        elif choice == "2":
            if quick_test():
                input("\n⏸️  Press Enter to stop test container...")
                subprocess.run(["docker", "stop", "stakas-test"], capture_output=True)
                
        elif choice == "3":
            if quick_compose():
                print("🎉 Stack running! Services:")
                print("   📱 App: http://localhost:8080")
                print("   🗄️  Database: localhost:5432")
                print("   📊 Redis: localhost:6379")
                input("\n⏸️  Press Enter to stop stack...")
                subprocess.run(["docker-compose", "-f", "docker-compose.dev.yml", "down"])
                
        elif choice == "4":
            quick_deploy()
            
        elif choice == "5":
            cleanup()
            
        elif choice == "6":
            print("🎯 ALL-IN-ONE QUICK START")
            if quick_build() and quick_test():
                print("\n🎉 SUCCESS! System ready for viral content!")
                print("📊 System Info:")
                print(f"   🎵 Canal: Stakas MVP (UCgohgqLVu1QPdfa64Vkrgeg)")
                print(f"   💰 Budget: €500/month Meta Ads")
                print(f"   🎯 Target: Drill/Rap Español audience")
                print(f"   📍 Location: España + LATAM")
                print(f"   ⏰ Peak time: 21:00 Spain timezone")
                
                action = input("\n🚀 Deploy to Railway now? (y/N): ")
                if action.lower() == 'y':
                    quick_deploy()
            
        elif choice == "7":
            cleanup()
            print("👋 ¡Stakas MVP listo para viral! 🎵🚀")
            break
            
        else:
            print("❌ Invalid option. Use 1-7")

if __name__ == "__main__":
    main()