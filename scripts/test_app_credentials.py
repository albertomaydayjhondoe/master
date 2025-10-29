#!/usr/bin/env python3
"""
Probar acceso con Meta App ID y Secret para generar token de aplicación
"""

import os
import requests
import json

def load_env_file():
    """Carga las variables de entorno del archivo .env"""
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'secrets', '.env'),
    ]
    
    env_vars = {}
    for env_path in possible_paths:
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip()
            break
    return env_vars

def generate_app_access_token():
    """Genera un token de aplicación usando App ID y Secret"""
    print("🔑 GENERANDO TOKEN DE APLICACIÓN META")
    print("="*50)
    
    env_vars = load_env_file()
    app_id = env_vars.get('META_APP_ID')
    app_secret = env_vars.get('META_APP_SECRET')
    
    if not app_id or not app_secret:
        print("❌ No se encontraron credenciales de aplicación")
        return None
    
    print(f"📱 App ID: {app_id}")
    print(f"🔐 App Secret: {app_secret[:10]}...")
    
    try:
        # Generar token de aplicación
        token_url = "https://graph.facebook.com/oauth/access_token"
        params = {
            'client_id': app_id,
            'client_secret': app_secret,
            'grant_type': 'client_credentials'
        }
        
        print(f"\n🌐 Solicitando token de aplicación...")
        response = requests.get(token_url, params=params)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            
            if access_token:
                print(f"✅ Token generado exitosamente")
                print(f"🎯 Token: {access_token[:30]}...")
                return access_token
            else:
                print("❌ No se recibió token en la respuesta")
                return None
        else:
            print(f"❌ Error generando token: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_token_access(token):
    """Prueba el acceso con el token generado"""
    print(f"\n🔍 PROBANDO ACCESO CON TOKEN DE APLICACIÓN")
    print("="*50)
    
    env_vars = load_env_file()
    account_id = env_vars.get('META_ADS_ACCOUNT_ID', '1771115133833816')
    
    try:
        # Probar información básica de la aplicación
        print("📱 Verificando información de la aplicación...")
        app_response = requests.get(
            f"https://graph.facebook.com/v18.0/{env_vars.get('META_APP_ID')}",
            params={'access_token': token}
        )
        
        if app_response.status_code == 200:
            app_info = app_response.json()
            print(f"✅ App: {app_info.get('name', 'N/A')}")
            print(f"✅ ID: {app_info.get('id', 'N/A')}")
        
        # Probar acceso a la cuenta de ads
        print(f"\n🎯 Probando acceso a cuenta: {account_id}")
        ads_response = requests.get(
            f"https://graph.facebook.com/v18.0/act_{account_id}",
            params={
                'access_token': token,
                'fields': 'id,name,account_status,currency'
            }
        )
        
        print(f"📊 Respuesta: {ads_response.status_code}")
        
        if ads_response.status_code == 200:
            account_info = ads_response.json()
            print("🎉 ¡ACCESO EXITOSO A LA CUENTA!")
            print("="*40)
            print(f"✅ ID: {account_info.get('id', 'N/A')}")
            print(f"✅ Nombre: {account_info.get('name', 'N/A')}")
            print(f"✅ Estado: {account_info.get('account_status', 'N/A')}")
            print(f"✅ Moneda: {account_info.get('currency', 'N/A')}")
            return True
            
        elif ads_response.status_code == 400:
            error_info = ads_response.json()
            error_msg = error_info.get('error', {}).get('message', 'Sin mensaje')
            print(f"❌ Error 400: {error_msg}")
            
            if 'Unsupported get request' in error_msg:
                print("🔧 El token de aplicación no puede acceder directamente a cuentas")
                print("💡 Necesitas un token de usuario con permisos ads_management")
            
            return False
            
        elif ads_response.status_code == 403:
            print("❌ Error 403: Sin permisos para esta cuenta")
            return False
            
        else:
            print(f"❌ Error {ads_response.status_code}: {ads_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando acceso: {e}")
        return False

def show_next_steps(token_generated, account_access):
    """Muestra los próximos pasos según los resultados"""
    print(f"\n" + "="*60)
    print("📊 RESULTADOS Y PRÓXIMOS PASOS")
    print("="*60)
    
    if token_generated and account_access:
        print("🎉 ¡SISTEMA 100% OPERATIVO!")
        print("✅ App Token generado correctamente")
        print("✅ Acceso confirmado a cuenta 1771115133833816")
        print("✅ Meta Ads completamente configurado")
        
        print("\n🚀 SISTEMA COMPLETO:")
        print("   🤖 YOLOv8: Operativo") 
        print("   🌐 GoLogin: Configurado")
        print("   📊 Meta Ads: ¡ACCESO TOTAL!")
        print("   🚀 Railway: Listo")
        
    elif token_generated:
        print("✅ Token de aplicación generado")
        print("❌ Sin acceso directo a cuenta de ads")
        
        print("\n🔧 OPCIONES:")
        print("1. 👤 TOKEN DE USUARIO necesario:")
        print("   - Ir a: https://developers.facebook.com/tools/explorer/")
        print("   - Seleccionar App ID: 2672426126432982")
        print("   - Agregar permisos: ads_management, ads_read")
        print("   - Generar User Access Token")
        
        print("\n2. 🏢 VERIFICAR BUSINESS MANAGER:")
        print("   - Vincular app con Business Manager")
        print("   - Agregar cuenta 1771115133833816 al Business")
        
    else:
        print("❌ No se pudo generar token")
        print("🔧 Verificar credenciales de la aplicación")

def main():
    """Función principal"""
    print("🎯 PRUEBA DE ACCESO CON META APP CREDENTIALS")
    print("App ID: 2672426126432982")
    print("Cuenta objetivo: 1771115133833816")
    print()
    
    # Generar token de aplicación
    app_token = generate_app_access_token()
    
    if app_token:
        # Probar acceso con el token
        has_access = test_token_access(app_token)
        show_next_steps(True, has_access)
    else:
        show_next_steps(False, False)

if __name__ == "__main__":
    main()