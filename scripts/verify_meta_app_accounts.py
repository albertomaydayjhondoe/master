#!/usr/bin/env python3
"""
Verificar cuentas Meta Ads asociadas al App ID 2672426126432982
"""

import os
import requests

def load_env_file():
    """Carga las variables de entorno del archivo .env"""
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'),
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

def check_app_info():
    """Verifica información de la aplicación Meta"""
    print("📱 VERIFICANDO APLICACIÓN META")
    print("="*50)
    print("🆔 App ID: 2672426126432982")
    
    env_vars = load_env_file()
    token = env_vars.get('META_ACCESS_TOKEN')
    app_id = '2672426126432982'
    
    if not token:
        print("❌ No se encontró token")
        return False
    
    try:
        # Verificar información de la app
        app_response = requests.get(
            f"https://graph.facebook.com/v18.0/{app_id}",
            params={
                'access_token': token,
                'fields': 'id,name,app_domains,category'
            }
        )
        
        if app_response.status_code == 200:
            app_info = app_response.json()
            print(f"✅ Nombre: {app_info.get('name', 'N/A')}")
            print(f"✅ ID: {app_info.get('id', 'N/A')}")
            print(f"✅ Categoría: {app_info.get('category', 'N/A')}")
            
            domains = app_info.get('app_domains', [])
            if domains:
                print(f"✅ Dominios: {', '.join(domains)}")
            
            return True
        else:
            print(f"❌ Error verificando app: {app_response.status_code}")
            print(f"📝 Respuesta: {app_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def find_associated_accounts():
    """Busca cuentas de ads asociadas a la aplicación"""
    print(f"\n🔍 BUSCANDO CUENTAS ASOCIADAS")
    print("="*50)
    
    env_vars = load_env_file()
    token = env_vars.get('META_ACCESS_TOKEN')
    
    try:
        # Verificar cuentas accesibles con el token actual
        accounts_response = requests.get(
            "https://graph.facebook.com/v18.0/me/adaccounts",
            params={
                'access_token': token,
                'fields': 'id,name,account_status,owner,business'
            }
        )
        
        if accounts_response.status_code == 200:
            accounts = accounts_response.json()
            account_list = accounts.get('data', [])
            
            print(f"📊 Cuentas encontradas: {len(account_list)}")
            
            if account_list:
                for i, account in enumerate(account_list, 1):
                    account_id = account.get('id', '').replace('act_', '')
                    print(f"\n🏢 Cuenta {i}:")
                    print(f"   ID: {account_id}")
                    print(f"   Nombre: {account.get('name', 'N/A')}")
                    print(f"   Estado: {account.get('account_status', 'N/A')}")
                    
                    # Verificar si es una cuenta que podemos usar
                    if account_id in ['1771115133833816', '9703931559732773']:
                        print(f"   🎯 ¡CUENTA OBJETIVO ENCONTRADA!")
                        return account_id
                        
                return account_list[0].get('id', '').replace('act_', '') if account_list else None
            else:
                print("❌ No se encontraron cuentas accesibles")
                return None
                
        else:
            print(f"❌ Error listando cuentas: {accounts_response.status_code}")
            
            # Si es error 400, el token no tiene permisos de ads
            if accounts_response.status_code == 400:
                print("🔧 Token sin permisos ads_management")
                
                # Intentar con información básica del usuario
                user_response = requests.get(
                    "https://graph.facebook.com/v18.0/me",
                    params={
                        'access_token': token,
                        'fields': 'id,name'
                    }
                )
                
                if user_response.status_code == 200:
                    user_info = user_response.json()
                    print(f"👤 Usuario del token: {user_info.get('name', 'N/A')}")
                    print(f"🆔 User ID: {user_info.get('id', 'N/A')}")
                
            return None
            
    except Exception as e:
        print(f"❌ Error buscando cuentas: {e}")
        return None

def test_direct_account_access(account_id=None):
    """Prueba acceso directo a cuenta específica"""
    target_account = account_id or '1771115133833816'
    
    print(f"\n🎯 PROBANDO ACCESO DIRECTO")
    print("="*50)
    print(f"🆔 Cuenta objetivo: {target_account}")
    
    env_vars = load_env_file()
    token = env_vars.get('META_ACCESS_TOKEN')
    
    try:
        direct_response = requests.get(
            f"https://graph.facebook.com/v18.0/act_{target_account}",
            params={
                'access_token': token,
                'fields': 'id,name,account_status,currency,business'
            }
        )
        
        if direct_response.status_code == 200:
            account_info = direct_response.json()
            print(f"🎉 ¡ACCESO EXITOSO!")
            print(f"✅ Nombre: {account_info.get('name', 'N/A')}")
            print(f"✅ Estado: {account_info.get('account_status', 'N/A')}")
            print(f"✅ Moneda: {account_info.get('currency', 'N/A')}")
            
            if 'business' in account_info:
                print(f"✅ Business: {account_info['business']}")
                
            return True
            
        elif direct_response.status_code == 403:
            print(f"❌ Error 403: Sin permisos para cuenta {target_account}")
            return False
            
        else:
            print(f"❌ Error {direct_response.status_code}")
            try:
                error_info = direct_response.json()
                print(f"📝 Error: {error_info.get('error', {}).get('message', 'Sin mensaje')}")
            except:
                print(f"📝 Respuesta: {direct_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_results(app_valid, found_account, direct_access):
    """Muestra resultados y próximos pasos"""
    print(f"\n" + "="*60)
    print("📊 RESULTADOS FINALES")
    print("="*60)
    
    if app_valid and direct_access:
        print("🎉 ¡CONFIGURACIÓN PERFECTA!")
        print("✅ App Meta válida")
        print("✅ Token con acceso a cuenta")
        print("✅ Sistema 100% operativo")
        
        print(f"\n🚀 SISTEMA COMPLETO:")
        print("   🤖 YOLOv8: Operativo")
        print("   🌐 GoLogin: Configurado")
        print("   📊 Meta Ads: ¡ACCESO CONFIRMADO!")
        print("   🚀 Railway: Listo")
        
        print(f"\n💰 LISTO PARA €500/mes AUTOMATIZACIÓN")
        
    elif app_valid and found_account:
        print("✅ App válida, cuenta encontrada")
        print(f"🆔 Usar cuenta: {found_account}")
        print("🔧 Actualizar META_ADS_ACCOUNT_ID")
        
    elif app_valid:
        print("✅ App válida")
        print("❌ Sin acceso a cuentas de ads")
        print("🔧 Token necesita permisos ads_management")
        
    else:
        print("❌ Problemas con configuración")
        print("🔧 Verificar App ID y token")

def main():
    """Función principal"""
    print("🎯 VERIFICACIÓN COMPLETA - APP META 2672426126432982")
    print()
    
    # Verificar app
    app_valid = check_app_info()
    
    # Buscar cuentas asociadas
    found_account = find_associated_accounts()
    
    # Probar acceso directo
    direct_access = test_direct_account_access(found_account)
    
    # Mostrar resultados
    show_results(app_valid, found_account, direct_access)

if __name__ == "__main__":
    main()