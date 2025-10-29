#!/usr/bin/env python3
"""
🎯 META ADS - CONFIGURACIÓN COMPLETA Y SOLUCIÓN DE PERMISOS

Este script te guía paso a paso para configurar correctamente Meta Ads
con la cuenta 9703931559732773 y resolver todos los problemas de permisos.
"""
import os
import sys
import requests
import json
import webbrowser
from pathlib import Path

# Cargar configuración
sys.path.append(str(Path(__file__).parent.parent))
from config.app_settings import get_env

def main_menu():
    """Menú principal para configuración Meta Ads."""
    print("🎯 META ADS - CONFIGURACIÓN COMPLETA")
    print("=" * 60)
    print("👋 Hola! Te ayudo a configurar Meta Ads correctamente.")
    print()
    print("Opciones disponibles:")
    print("1. 🔍 Verificar token actual y cuentas disponibles")
    print("2. 🔧 Generar nuevo token con permisos correctos")
    print("3. 📱 Usar Facebook Graph API Explorer (fácil)")
    print("4. 🏢 Crear nueva cuenta Meta Ads")
    print("5. 🧪 Probar conexión con cuenta específica")
    print("6. 📋 Ver configuración actual")
    print("0. ❌ Salir")
    print()
    
    choice = input("Selecciona una opción (0-6): ").strip()
    return choice

def check_current_token():
    """Verificar el token actual y mostrar información detallada."""
    print("\n🔍 VERIFICANDO TOKEN ACTUAL")
    print("-" * 40)
    
    token = get_env("META_ACCESS_TOKEN")
    if not token:
        print("❌ No se encontró META_ACCESS_TOKEN en .env")
        return False
    
    print(f"✅ Token encontrado: {token[:20]}...")
    
    # Test 1: Información básica del usuario
    try:
        url = "https://graph.facebook.com/v18.0/me"
        params = {
            "fields": "name,id,email",
            "access_token": token
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"👤 Usuario: {data.get('name', 'Desconocido')}")
            print(f"🆔 ID: {data.get('id', 'N/A')}")
            print(f"📧 Email: {data.get('email', 'No disponible')}")
        else:
            print(f"❌ Error obteniendo info de usuario: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Permisos del token
    try:
        url = "https://graph.facebook.com/v18.0/me/permissions"
        params = {"access_token": token}
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            perms_data = response.json()
            permissions = perms_data.get('data', [])
            
            print(f"\n🔐 Permisos actuales ({len(permissions)} total):")
            
            # Permisos importantes para Meta Ads
            required_perms = [
                'ads_management',
                'ads_read', 
                'business_management',
                'pages_read_engagement',
                'pages_show_list'
            ]
            
            granted_perms = []
            for perm in permissions:
                if perm.get('status') == 'granted':
                    granted_perms.append(perm.get('permission'))
            
            for req_perm in required_perms:
                has_perm = req_perm in granted_perms
                status = "✅" if has_perm else "❌"
                print(f"   {status} {req_perm}")
            
            # Mostrar todos los permisos concedidos
            print(f"\n📋 Todos los permisos concedidos:")
            for perm in granted_perms[:10]:  # Solo primeros 10
                print(f"   ✅ {perm}")
            
            if len(granted_perms) > 10:
                print(f"   ... y {len(granted_perms) - 10} más")
        
    except Exception as e:
        print(f"❌ Error verificando permisos: {e}")
    
    # Test 3: Intentar acceder a cuentas de anuncios
    try:
        print(f"\n📢 Probando acceso a cuentas de anuncios...")
        url = "https://graph.facebook.com/v18.0/me/adaccounts"
        params = {
            "fields": "id,name,account_status",
            "access_token": token
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            accounts = data.get('data', [])
            print(f"✅ Se encontraron {len(accounts)} cuentas de anuncios")
            
            for acc in accounts:
                acc_id = acc.get('id', '').replace('act_', '')
                name = acc.get('name', 'Sin nombre')
                status = acc.get('account_status', 'Desconocido')
                print(f"   📊 {name} (ID: {acc_id}) - Estado: {status}")
                
                if acc_id == "9703931559732773":
                    print("   🎯 ¡Esta es la cuenta que quieres usar!")
        else:
            error_data = response.json()
            print(f"❌ Error: {error_data.get('error', {}).get('message', 'Error desconocido')}")
            
    except Exception as e:
        print(f"❌ Error probando cuentas: {e}")
    
    return True

def generate_new_token_guide():
    """Guía para generar un nuevo token con permisos correctos."""
    print("\n🔧 GENERAR NUEVO TOKEN CON PERMISOS")
    print("-" * 40)
    
    print("📋 Método 1: Facebook Graph API Explorer (RECOMENDADO)")
    print("1. Ve a: https://developers.facebook.com/tools/explorer/")
    print("2. Selecciona tu aplicación Facebook")
    print("3. En 'Permissions', agrega estos permisos:")
    
    perms = [
        "ads_management",
        "ads_read", 
        "business_management",
        "pages_read_engagement",
        "pages_show_list"
    ]
    
    for perm in perms:
        print(f"   ✅ {perm}")
    
    print("4. Haz clic en 'Generate Access Token'")
    print("5. Acepta todos los permisos")
    print("6. Copia el token generado")
    print("7. Actualiza META_ACCESS_TOKEN en tu .env")
    
    print(f"\n📋 Método 2: URL Manual de autorización")
    
    # Generar URL de autorización
    app_id = input("Ingresa tu Facebook App ID (o Enter para ejemplo): ").strip()
    if not app_id:
        app_id = "TU_APP_ID"
    
    permissions_str = ",".join(perms)
    auth_url = (
        f"https://www.facebook.com/v18.0/dialog/oauth?"
        f"client_id={app_id}&"
        f"redirect_uri=https://localhost:8000/callback&"
        f"scope={permissions_str}&"
        f"response_type=code"
    )
    
    print(f"\n🔗 URL de autorización:")
    print(f"{auth_url}")
    
    print(f"\n📝 Pasos:")
    print("1. Reemplaza TU_APP_ID con tu App ID real")
    print("2. Ve a la URL en tu navegador")
    print("3. Acepta todos los permisos")
    print("4. Copia el 'code' de la URL de respuesta")
    print("5. Intercambia el code por un access token")
    
    # Preguntar si quiere abrir Graph API Explorer
    open_explorer = input("\n🌐 ¿Abrir Graph API Explorer ahora? (y/n): ").strip().lower()
    if open_explorer == 'y':
        webbrowser.open("https://developers.facebook.com/tools/explorer/")
        print("✅ Abriendo Graph API Explorer...")

def use_graph_api_explorer():
    """Guía paso a paso para usar Graph API Explorer."""
    print("\n📱 USAR FACEBOOK GRAPH API EXPLORER")
    print("-" * 40)
    
    print("🎯 Esta es la forma MÁS FÁCIL de obtener un token con permisos:")
    
    print(f"\n📝 PASO A PASO:")
    print("1. 🌐 Ve a Graph API Explorer")
    print("2. 🔧 En la esquina superior derecha, selecciona tu App")
    print("3. 🔐 Haz clic en 'Get Token' → 'Get User Access Token'")
    print("4. ✅ Selecciona estos permisos:")
    
    perms = [
        "ads_management - Para crear y gestionar campañas",
        "ads_read - Para leer datos de campañas", 
        "business_management - Para gestionar Business Manager",
        "pages_read_engagement - Para leer engagement de páginas",
        "pages_show_list - Para listar páginas"
    ]
    
    for i, perm in enumerate(perms, 1):
        print(f"   {i}. {perm}")
    
    print("5. 🎯 Haz clic en 'Generate Access Token'")
    print("6. ✅ Acepta todos los permisos en Facebook")
    print("7. 📋 Copia el token que aparece")
    print("8. 🔧 Actualiza tu .env con el nuevo token")
    
    print(f"\n🧪 Para probar el token:")
    print("En Graph API Explorer, prueba estas queries:")
    print("   • GET /me (info de usuario)")
    print("   • GET /me/adaccounts (tus cuentas de anuncios)")  
    print("   • GET /act_9703931559732773 (info de tu cuenta específica)")
    
    # Abrir Graph API Explorer
    open_now = input("\n🚀 ¿Abrir Graph API Explorer ahora? (y/n): ").strip().lower()
    if open_now == 'y':
        webbrowser.open("https://developers.facebook.com/tools/explorer/")
        print("✅ Abriendo Graph API Explorer...")
        
        # Esperar a que configure el token
        input("\n⏳ Configura tu token en Graph API Explorer y presiona Enter cuando esté listo...")
        
        # Pedir el nuevo token
        new_token = input("📋 Pega aquí tu nuevo token (o Enter para omitir): ").strip()
        
        if new_token:
            # Probar el nuevo token
            test_new_token(new_token)

def test_new_token(token):
    """Probar un nuevo token."""
    print(f"\n🧪 PROBANDO NUEVO TOKEN")
    print("-" * 40)
    
    # Test básico
    try:
        url = "https://graph.facebook.com/v18.0/me"
        params = {
            "fields": "name,id",
            "access_token": token
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token válido - Usuario: {data.get('name')}")
        else:
            print(f"❌ Token inválido: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error probando token: {e}")
        return False
    
    # Test de cuentas de anuncios
    try:
        url = "https://graph.facebook.com/v18.0/me/adaccounts"
        params = {"access_token": token}
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            accounts = data.get('data', [])
            print(f"✅ Acceso a cuentas: {len(accounts)} encontradas")
            
            # Buscar cuenta específica
            target_found = False
            for acc in accounts:
                acc_id = acc.get('id', '').replace('act_', '')
                if acc_id == "9703931559732773":
                    target_found = True
                    print(f"🎯 ¡Cuenta objetivo encontrada! {acc.get('name')}")
                    break
            
            if not target_found:
                print("⚠️ Cuenta 9703931559732773 no encontrada en la lista")
        else:
            print(f"❌ Error accediendo cuentas: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Preguntar si actualizar .env
    update_env = input(f"\n💾 ¿Actualizar .env con este token? (y/n): ").strip().lower()
    if update_env == 'y':
        update_env_file(token)
    
    return True

def update_env_file(new_token):
    """Actualizar archivo .env con nuevo token."""
    env_path = Path(__file__).parent.parent / ".env"
    
    try:
        # Leer archivo actual
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar token
        import re
        pattern = r'META_ACCESS_TOKEN=.*'
        replacement = f'META_ACCESS_TOKEN={new_token}'
        
        if re.search(pattern, content):
            new_content = re.sub(pattern, replacement, content)
        else:
            # Agregar token si no existe
            new_content = content + f'\nMETA_ACCESS_TOKEN={new_token}\n'
        
        # Guardar archivo
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Token actualizado en .env")
        
        # Verificar inmediatamente
        print(f"\n🔄 Verificando nueva configuración...")
        os.environ['META_ACCESS_TOKEN'] = new_token  # Actualizar env actual
        
        # Test rápido
        try:
            url = "https://graph.facebook.com/v18.0/act_9703931559732773"
            params = {
                "fields": "name,account_status,currency",
                "access_token": new_token
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                print(f"🎯 ¡ÉXITO! Acceso a cuenta confirmado:")
                print(f"   📊 Nombre: {data.get('name', 'N/A')}")
                print(f"   💰 Moneda: {data.get('currency', 'N/A')}")
                print(f"   📈 Estado: {data.get('account_status', 'N/A')}")
            else:
                print(f"⚠️ Token guardado, pero aún no hay acceso a cuenta específica")
                print(f"   Respuesta: {response.text}")
                
        except Exception as e:
            print(f"⚠️ Token guardado, error verificando: {e}")
            
    except Exception as e:
        print(f"❌ Error actualizando .env: {e}")

def create_new_account():
    """Guía para crear nueva cuenta Meta Ads."""
    print("\n🏢 CREAR NUEVA CUENTA META ADS")
    print("-" * 40)
    
    print("📋 Si no tienes acceso a la cuenta 9703931559732773,")
    print("puedes crear una nueva cuenta fácilmente:")
    
    print(f"\n📝 PASOS:")
    print("1. 🌐 Ve a Facebook Business Manager")
    print("2. 🔧 Configuración → Cuentas de anuncios")
    print("3. ➕ Hacer clic en 'Agregar' → 'Crear nueva cuenta de anuncios'")
    print("4. 📝 Completar información:")
    print("   • Nombre: 'Stakas Music Promotion'")
    print("   • Zona horaria: Tu zona horaria")
    print("   • Moneda: EUR (Euro)")
    print("5. 💳 Configurar método de pago")
    print("6. 📋 Copiar el nuevo Account ID")
    print("7. 🔧 Actualizar META_ADS_ACCOUNT_ID en .env")
    
    print(f"\n💡 VENTAJAS de cuenta nueva:")
    print("   ✅ Control completo")
    print("   ✅ Sin restricciones de permisos")
    print("   ✅ Historial limpio")
    print("   ✅ Fácil configuración de presupuesto")
    
    # Abrir Business Manager
    open_bm = input("\n🚀 ¿Abrir Facebook Business Manager? (y/n): ").strip().lower()
    if open_bm == 'y':
        webbrowser.open("https://business.facebook.com/settings/ad-accounts")
        print("✅ Abriendo Business Manager...")

def test_specific_account():
    """Probar conexión con cuenta específica."""
    print("\n🧪 PROBAR CUENTA ESPECÍFICA")
    print("-" * 40)
    
    account_id = input("Ingresa Account ID a probar (o Enter para 9703931559732773): ").strip()
    if not account_id:
        account_id = "9703931559732773"
    
    token = get_env("META_ACCESS_TOKEN")
    if not token:
        print("❌ No se encontró META_ACCESS_TOKEN")
        return
    
    print(f"🎯 Probando cuenta: {account_id}")
    
    try:
        # Test 1: Información básica
        url = f"https://graph.facebook.com/v18.0/act_{account_id}"
        params = {
            "fields": "name,account_status,currency,timezone_name,amount_spent,balance",
            "access_token": token
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cuenta encontrada:")
            print(f"   📊 Nombre: {data.get('name', 'N/A')}")
            print(f"   📈 Estado: {data.get('account_status', 'N/A')}")
            print(f"   💰 Moneda: {data.get('currency', 'N/A')}")
            print(f"   🌍 Zona horaria: {data.get('timezone_name', 'N/A')}")
            print(f"   💸 Gastado: {data.get('amount_spent', 0)} {data.get('currency', '')}")
            
        elif response.status_code == 403:
            error = response.json().get('error', {})
            print(f"❌ Sin acceso a la cuenta:")
            print(f"   Código: {error.get('code', 'N/A')}")
            print(f"   Mensaje: {error.get('message', 'Sin mensaje')}")
            
            if "NOT grant ads_management" in error.get('message', ''):
                print(f"\n💡 SOLUCIÓN: El owner de la cuenta debe:")
                print(f"   1. Ir a Business Manager")
                print(f"   2. Configuración → Cuentas de anuncios")
                print(f"   3. Seleccionar la cuenta {account_id}")
                print(f"   4. Agregar tu usuario con permisos 'Administrar'")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
        # Test 2: Campañas
        print(f"\n📢 Probando acceso a campañas...")
        url = f"https://graph.facebook.com/v18.0/act_{account_id}/campaigns"
        params = {
            "fields": "name,status",
            "limit": 5,
            "access_token": token
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            campaigns = data.get('data', [])
            print(f"✅ Acceso a campañas: {len(campaigns)} encontradas")
        else:
            print(f"❌ Sin acceso a campañas: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error probando cuenta: {e}")

def show_current_config():
    """Mostrar configuración actual."""
    print("\n📋 CONFIGURACIÓN ACTUAL")
    print("-" * 40)
    
    # Leer .env
    env_path = Path(__file__).parent.parent / ".env"
    
    config_items = [
        "META_ACCESS_TOKEN",
        "META_ADS_ACCOUNT_ID", 
        "META_APP_ID",
        "META_APP_SECRET",
        "DUMMY_MODE",
        "ENVIRONMENT"
    ]
    
    for item in config_items:
        value = get_env(item)
        if value:
            if "TOKEN" in item or "SECRET" in item:
                display_value = f"{value[:20]}..." if len(value) > 20 else value
            else:
                display_value = value
            print(f"   ✅ {item}: {display_value}")
        else:
            print(f"   ❌ {item}: No configurado")
    
    print(f"\n📁 Archivo .env: {env_path}")
    print(f"   {'✅ Existe' if env_path.exists() else '❌ No encontrado'}")

def main():
    """Función principal."""
    while True:
        try:
            choice = main_menu()
            
            if choice == "1":
                check_current_token()
            elif choice == "2":
                generate_new_token_guide()
            elif choice == "3":
                use_graph_api_explorer()
            elif choice == "4":
                create_new_account()
            elif choice == "5":
                test_specific_account()
            elif choice == "6":
                show_current_config()
            elif choice == "0":
                print("\n👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida. Intenta de nuevo.")
            
            input("\nPresiona Enter para continuar...")
            print("\n" + "="*60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrumpido por usuario. ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            input("Presiona Enter para continuar...")

if __name__ == "__main__":
    main()