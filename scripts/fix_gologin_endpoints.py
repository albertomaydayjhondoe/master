#!/usr/bin/env python3
"""
🔧 GOLOGIN API - CORRECCIÓN DE ENDPOINTS Y PRUEBA REAL

Este script identifica los endpoints correctos de GoLogin API v2
y prueba la creación real de perfiles.
"""
import os
import sys
import requests
import json
from pathlib import Path

# Cargar configuración
sys.path.append(str(Path(__file__).parent.parent))
from config.app_settings import get_env

def find_correct_endpoints():
    """Encontrar los endpoints correctos de GoLogin API."""
    
    print("🔧 IDENTIFICANDO ENDPOINTS CORRECTOS DE GOLOGIN")
    print("=" * 55)
    
    token = get_env("GOLOGIN_API_TOKEN")
    if not token:
        print("❌ GOLOGIN_API_TOKEN no encontrado")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    base_urls = [
        "https://api.gologin.com",
        "https://app.gologin.com/api"
    ]
    
    # Endpoints para probar
    test_endpoints = [
        ("GET", "/user", "Información de usuario"),
        ("GET", "/browser", "Listar perfiles (v1)"),
        ("GET", "/browser/v2", "Listar perfiles (v2)"),
        ("GET", "/folders", "Listar carpetas"),
        ("GET", "/tariffs", "Información de tarifas"),
        ("GET", "/proxies", "Proxies disponibles")
    ]
    
    working_endpoints = {}
    
    for base_url in base_urls:
        print(f"\n🌐 Probando base URL: {base_url}")
        print("-" * 40)
        
        for method, endpoint, description in test_endpoints:
            try:
                url = f"{base_url}{endpoint}"
                
                if method == "GET":
                    response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {description}: {url}")
                    
                    # Mostrar información relevante
                    if "user" in endpoint:
                        print(f"   👤 Usuario: {data.get('email', 'N/A')}")
                        print(f"   📊 Plan: {data.get('plan', {}).get('name', 'N/A')}")
                    elif "browser" in endpoint:
                        profiles_count = len(data) if isinstance(data, list) else len(data.get('data', []))
                        print(f"   🖥️ Perfiles encontrados: {profiles_count}")
                    elif "folders" in endpoint:
                        folders_count = len(data) if isinstance(data, list) else len(data.get('data', []))
                        print(f"   📁 Carpetas encontradas: {folders_count}")
                    
                    working_endpoints[f"{method}_{endpoint}"] = {
                        "url": url,
                        "description": description,
                        "status": "working"
                    }
                    
                elif response.status_code == 404:
                    print(f"❌ {description}: No encontrado")
                elif response.status_code == 403:
                    print(f"⚠️ {description}: Sin permisos")
                else:
                    print(f"⚠️ {description}: Status {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {description}: Error - {str(e)[:50]}...")
    
    # Resumen de endpoints funcionales
    print(f"\n📋 ENDPOINTS FUNCIONALES ENCONTRADOS")
    print("-" * 40)
    
    for key, info in working_endpoints.items():
        print(f"✅ {info['description']}")
        print(f"   🔗 {info['url']}")
    
    return working_endpoints

def test_profile_creation():
    """Probar creación real de perfil."""
    
    print(f"\n🧪 PROBANDO CREACIÓN DE PERFIL REAL")
    print("-" * 40)
    
    token = get_env("GOLOGIN_API_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Configuración de perfil de prueba
    test_profile = {
        "name": "Stakas_Test_Profile_" + str(int(time.time())),
        "os": "win",
        "navigator": {
            "language": "es-ES,es;q=0.9",
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "resolution": "1920x1080",
            "platform": "Win32"
        },
        "geolocation": {
            "mode": "prompt",
            "enabled": True,
            "latitude": 40.4168,
            "longitude": -3.7038
        },
        "timezone": {
            "id": "Europe/Madrid"
        },
        "webRTC": {
            "mode": "alerted",
            "enabled": True
        },
        "canvas": {
            "mode": "real"
        },
        "webGL": {
            "mode": "real"
        },
        "notes": "Perfil de prueba para sistema Stakas"
    }
    
    # URLs para probar creación
    creation_urls = [
        "https://api.gologin.com/browser",
        "https://api.gologin.com/browser/v2", 
        "https://app.gologin.com/api/browser",
        "https://app.gologin.com/api/browser/v2"
    ]
    
    import time
    
    for url in creation_urls:
        try:
            print(f"\n🔄 Probando creación en: {url}")
            
            response = requests.post(url, headers=headers, json=test_profile, timeout=15)
            
            if response.status_code in [200, 201]:
                result = response.json()
                profile_id = result.get('id', 'unknown')
                
                print(f"✅ ¡Perfil creado exitosamente!")
                print(f"   🆔 ID: {profile_id}")
                print(f"   📝 Nombre: {result.get('name', 'N/A')}")
                print(f"   📊 Estado: {result.get('status', 'N/A')}")
                
                # Intentar listar perfiles para confirmar
                list_url = url.replace("/browser/v2", "/browser").replace("/browser", "/browser")
                list_response = requests.get(list_url, headers=headers)
                
                if list_response.status_code == 200:
                    profiles = list_response.json()
                    profiles_data = profiles if isinstance(profiles, list) else profiles.get('data', [])
                    
                    # Buscar nuestro perfil
                    our_profile = next((p for p in profiles_data if p.get('id') == profile_id), None)
                    if our_profile:
                        print(f"✅ Perfil confirmado en la lista")
                        
                        # Opcional: eliminar perfil de prueba
                        delete_choice = input("🗑️ ¿Eliminar perfil de prueba? (y/n): ").strip().lower()
                        if delete_choice == 'y':
                            delete_url = f"{url}/{profile_id}"
                            delete_response = requests.delete(delete_url, headers=headers)
                            if delete_response.status_code in [200, 204]:
                                print("✅ Perfil de prueba eliminado")
                            else:
                                print("⚠️ No se pudo eliminar el perfil de prueba")
                
                return {
                    "success": True,
                    "creation_url": url,
                    "profile_id": profile_id
                }
                
            else:
                print(f"❌ Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Mensaje: {error_data.get('message', 'Sin mensaje')}")
                except:
                    print(f"   Respuesta: {response.text[:100]}...")
                    
        except Exception as e:
            print(f"❌ Error probando {url}: {str(e)[:50]}...")
    
    print(f"\n❌ No se pudo crear perfil en ningún endpoint")
    return {"success": False}

def update_gologin_client():
    """Actualizar cliente GoLogin con endpoints correctos."""
    
    print(f"\n🔧 ACTUALIZANDO CLIENTE GOLOGIN")
    print("-" * 40)
    
    # Aquí actualizaríamos el cliente con los endpoints correctos
    print("📝 Recomendaciones para actualizar el cliente:")
    print("1. Usar https://api.gologin.com como base URL")
    print("2. Endpoint de perfiles: /browser (no /browser/v2)")  
    print("3. Creación de perfiles: POST /browser")
    print("4. Inicio de perfil: GET /browser/{id}/web")
    print("5. Parada de perfil: DELETE /browser/{id}")
    
    # Generar código actualizado
    updated_code = '''
# URLs corregidas para GoLogin API
class GoLoginClient:
    def __init__(self):
        self.base_url = "https://api.gologin.com"
        
    async def create_profile(self, profile_data):
        """Crear perfil usando endpoint correcto."""
        url = f"{self.base_url}/browser"
        # ... rest of implementation
        
    async def list_profiles(self):
        """Listar perfiles usando endpoint correcto."""
        url = f"{self.base_url}/browser"
        # ... rest of implementation
        
    async def start_profile(self, profile_id):
        """Iniciar perfil usando endpoint correcto."""
        url = f"{self.base_url}/browser/{profile_id}/web"
        # ... rest of implementation
    '''
    
    print(f"\n📄 Código de ejemplo:")
    print(updated_code)

def main():
    """Función principal."""
    
    print("🔧 GOLOGIN API - CORRECCIÓN Y CONFIGURACIÓN")
    print("=" * 60)
    
    # Paso 1: Identificar endpoints correctos
    working_endpoints = find_correct_endpoints()
    
    if working_endpoints:
        print(f"\n🎯 Endpoints identificados correctamente")
        
        # Paso 2: Probar creación de perfil
        creation_result = test_profile_creation()
        
        if creation_result.get("success"):
            print(f"\n✅ ¡Creación de perfil exitosa!")
            print(f"🔗 URL funcional: {creation_result['creation_url']}")
            
            # Paso 3: Actualizar cliente
            update_gologin_client()
            
        else:
            print(f"\n⚠️ Creación de perfil falló, pero API está conectada")
            print("💡 Puede ser por límites del plan o configuración")
            
    else:
        print(f"\n❌ No se encontraron endpoints funcionales")
        print("🔧 Verifica:")
        print("   1. Token GoLogin válido")
        print("   2. Plan activo")
        print("   3. Conexión a internet")
    
    print("=" * 60)

if __name__ == "__main__":
    import time
    main()