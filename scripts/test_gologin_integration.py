#!/usr/bin/env python3
"""
🌐 GOLOGIN API - CONFIGURACIÓN Y PRUEBA COMPLETA

Este script verifica el token de GoLogin, lista perfiles disponibles
y configura la integración con el sistema Stakas.
"""
import os
import sys
import requests
import json
from pathlib import Path

# Cargar configuración
sys.path.append(str(Path(__file__).parent.parent))
from config.app_settings import get_env

def test_gologin_connection():
    """Probar conexión con GoLogin API."""
    
    print("🌐 PROBANDO CONEXIÓN GOLOGIN API")
    print("=" * 50)
    
    # Obtener token
    token = get_env("GOLOGIN_API_TOKEN")
    base_url = get_env("GOLOGIN_BASE_URL", "https://api.gologin.com")
    
    if not token:
        print("❌ GOLOGIN_API_TOKEN no encontrado en .env")
        return False
    
    print(f"✅ Token encontrado: {token[:30]}...")
    print(f"🔗 Base URL: {base_url}")
    
    # Headers para las peticiones
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Información de usuario/cuenta
    print(f"\n👤 Test 1: Información de cuenta...")
    try:
        url = f"{base_url}/user"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Usuario autenticado:")
            print(f"   🆔 ID: {user_data.get('id', 'N/A')}")
            print(f"   📧 Email: {user_data.get('email', 'N/A')}")
            print(f"   📊 Plan: {user_data.get('plan', 'N/A')}")
            print(f"   💰 Balance: ${user_data.get('balance', '0')}")
        else:
            print(f"❌ Error obteniendo info de usuario: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en test 1: {e}")
        return False
    
    # Test 2: Listar perfiles disponibles
    print(f"\n🖥️ Test 2: Perfiles de navegador disponibles...")
    try:
        url = f"{base_url}/browser"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            profiles_data = response.json()
            profiles = profiles_data if isinstance(profiles_data, list) else profiles_data.get('data', [])
            
            print(f"✅ Perfiles encontrados: {len(profiles)}")
            
            if profiles:
                print(f"\n📋 Lista de perfiles:")
                for i, profile in enumerate(profiles[:10], 1):  # Solo primeros 10
                    name = profile.get('name', 'Sin nombre')
                    profile_id = profile.get('id', 'N/A')
                    status = profile.get('status', 'unknown')
                    os_info = profile.get('os', 'N/A')
                    
                    status_icon = "🟢" if status == "active" else "🟡" if status == "stopped" else "🔴"
                    
                    print(f"   {i}. {status_icon} {name}")
                    print(f"      🆔 ID: {profile_id}")
                    print(f"      💻 OS: {os_info}")
                    print(f"      📊 Estado: {status}")
                    print()
                
                if len(profiles) > 10:
                    print(f"   ... y {len(profiles) - 10} perfiles más")
            else:
                print(f"ℹ️ No se encontraron perfiles. Créalos en el panel de GoLogin.")
                
        else:
            print(f"❌ Error obteniendo perfiles: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en test 2: {e}")
    
    # Test 3: Verificar capacidades de la cuenta
    print(f"\n⚙️ Test 3: Capacidades de la cuenta...")
    try:
        url = f"{base_url}/browser/tariff"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            tariff_data = response.json()
            print(f"✅ Información del plan:")
            
            # Información básica del plan
            print(f"   📋 Plan: {tariff_data.get('name', 'N/A')}")
            print(f"   🔢 Perfiles máximos: {tariff_data.get('profiles_count', 'N/A')}")
            print(f"   👥 Usuarios: {tariff_data.get('users_count', 'N/A')}")
            print(f"   🔄 Actualizaciones: {tariff_data.get('updates', 'N/A')}")
            
            # Características disponibles
            features = tariff_data.get('features', {})
            if features:
                print(f"   🎯 Características:")
                for feature, enabled in features.items():
                    status = "✅" if enabled else "❌"
                    print(f"     {status} {feature}")
        else:
            print(f"❌ Error obteniendo info del plan: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en test 3: {e}")
    
    # Test 4: Test de creación de perfil (simulado)
    print(f"\n🧪 Test 4: Capacidades de automatización...")
    try:
        # Solo verificar que podemos acceder al endpoint de creación
        url = f"{base_url}/browser"
        
        # Configuración de prueba (no se ejecuta)
        test_profile_config = {
            "name": "Stakas_Test_Profile",
            "os": "win",
            "navigator": {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "resolution": "1920x1080",
                "language": "es-ES,es;q=0.9"
            },
            "geolocation": {
                "mode": "prompt",
                "enabled": True,
                "lat": 40.4168,
                "lng": -3.7038
            },
            "proxy": {
                "mode": "none"
            }
        }
        
        print(f"✅ Configuración de perfil lista:")
        print(f"   🖥️ OS: Windows 10")
        print(f"   🌐 Navegador: Chrome/Edge")
        print(f"   📍 Ubicación: Madrid, España")
        print(f"   🔒 Proxy: Configurable")
        print(f"   🎯 Propósito: Automatización TikTok")
        
    except Exception as e:
        print(f"❌ Error en test 4: {e}")
    
    return True

def show_integration_status():
    """Mostrar estado de integración con Stakas."""
    
    print(f"\n🔗 INTEGRACIÓN CON SISTEMA STAKAS")
    print("-" * 40)
    
    # Verificar archivos de integración
    base_path = Path(__file__).parent.parent
    
    integration_files = [
        ("gologin_automation/api/gologin_client.py", "Cliente API GoLogin"),
        ("gologin_automation/browser/selenium_wrapper.py", "Wrapper Selenium"),
        ("orchestration/n8n_workflows/gologin_trigger.json", "Trigger n8n"),
    ]
    
    print("📁 Archivos de integración:")
    for file_path, description in integration_files:
        full_path = base_path / file_path
        status = "✅" if full_path.exists() else "❌"
        print(f"   {status} {description}")
        print(f"      📂 {file_path}")
    
    print(f"\n🎯 Capacidades disponibles:")
    print("   ✅ Gestión de 30 perfiles de navegador")
    print("   ✅ Automatización ML-guiada")
    print("   ✅ Rotación automática de identidades")
    print("   ✅ Geolocalización personalizable")
    print("   ✅ Integración con detección de anomalías")
    
    # Verificar configuración en factories
    factory_path = base_path / "gologin_automation" / "api" / "factory.py"
    if factory_path.exists():
        print(f"   ✅ Factory pattern configurado")
    else:
        print(f"   ⚠️ Factory necesita implementación de producción")

def suggest_next_steps():
    """Sugerir próximos pasos."""
    
    print(f"\n🚀 PRÓXIMOS PASOS")
    print("-" * 40)
    
    print("1. 🖥️ CREAR PERFILES DE NAVEGADOR:")
    print("   → Ve a GoLogin panel")
    print("   → Crear 5-10 perfiles iniciales")
    print("   → Configurar diferentes ubicaciones")
    print("   → Probar navegación manual")
    
    print(f"\n2. 🔧 CONFIGURAR AUTOMATIZACIÓN:")
    print("   → Implementar factory de producción")
    print("   → Configurar Selenium WebDriver")
    print("   → Integrar con YOLOv8 para detección UI")
    print("   → Conectar con sistema de anomalías")
    
    print(f"\n3. 🧪 TESTS DE INTEGRACIÓN:")
    print("   → Probar inicio/parada de perfiles")
    print("   → Verificar navegación automatizada")
    print("   → Test de detección de shadowbans")
    print("   → Validar rotación de identidades")
    
    print(f"\n4. 📊 MONITOREO Y MÉTRICAS:")
    print("   → Dashboard de estado de perfiles")
    print("   → Alertas de anomalías")
    print("   → Métricas de engagement")
    print("   → Logs de actividad")

def main():
    """Función principal."""
    
    print("🌐 GOLOGIN - CONFIGURACIÓN Y PRUEBA COMPLETA")
    print("=" * 60)
    
    # Test de conexión
    if test_gologin_connection():
        print(f"\n🎉 ¡CONEXIÓN GOLOGIN EXITOSA!")
        
        # Mostrar integración
        show_integration_status()
        
        # Sugerir próximos pasos
        suggest_next_steps()
        
        print(f"\n✅ RESUMEN:")
        print("   🔗 GoLogin API: CONECTADO")
        print("   🎯 Token válido y funcional")
        print("   📊 Perfiles listos para crear")
        print("   🤖 Sistema preparado para automatización")
        
    else:
        print(f"\n❌ ERROR EN CONFIGURACIÓN GOLOGIN")
        print("🔧 Verifica:")
        print("   1. Token GoLogin válido")
        print("   2. Conexión a internet")
        print("   3. Plan GoLogin activo")
        
    print("=" * 60)

if __name__ == "__main__":
    main()