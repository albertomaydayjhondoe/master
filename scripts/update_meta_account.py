#!/usr/bin/env python3
"""
Script para actualizar la configuración de Meta Ads con la nueva cuenta
asampayo00@gmail.com en lugar de flousoloflou@gmail.com
"""

import os
import sys
import requests
from datetime import datetime

def load_env_file():
    """Carga las variables de entorno del archivo .env"""
    # Buscar en múltiples ubicaciones
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'),  # raíz del proyecto
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'secrets', '.env'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'production', '.env')
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
            break  # Usar el primer archivo encontrado
    
    return env_vars

def verify_current_token():
    """Verifica el token actual de Meta Ads"""
    print("🔍 Verificando token actual de Meta Ads...")
    
    env_vars = load_env_file()
    token = env_vars.get('META_ACCESS_TOKEN')
    
    if not token:
        print("❌ No se encontró META_ACCESS_TOKEN en .env")
        return False
    
    try:
        # Verificar información del usuario
        response = requests.get(
            f"https://graph.facebook.com/v18.0/me",
            params={'access_token': token}
        )
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Token válido")
            print(f"   Usuario: {user_info.get('name', 'N/A')}")
            print(f"   ID: {user_info.get('id', 'N/A')}")
            
            # Verificar email si está disponible
            email_response = requests.get(
                f"https://graph.facebook.com/v18.0/me",
                params={
                    'access_token': token,
                    'fields': 'email,name,id'
                }
            )
            
            if email_response.status_code == 200:
                email_info = email_response.json()
                email = email_info.get('email', 'No disponible')
                print(f"   Email: {email}")
                
                if 'asampayo00@gmail.com' in email:
                    print("✅ El token ya está asociado a asampayo00@gmail.com")
                    return True
                else:
                    print(f"⚠️  El token está asociado a {email}")
                    print("   Necesitas generar un nuevo token con asampayo00@gmail.com")
                    return False
            
            return True
            
        else:
            print(f"❌ Token inválido: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando token: {e}")
        return False

def check_account_access():
    """Verifica acceso a la cuenta de ads específica"""
    print("\n🔍 Verificando acceso a cuenta de ads...")
    
    env_vars = load_env_file()
    token = env_vars.get('META_ACCESS_TOKEN')
    account_id = env_vars.get('META_ADS_ACCOUNT_ID', '9703931559732773')
    
    if not token:
        return False
    
    try:
        # Verificar acceso directo a la cuenta
        response = requests.get(
            f"https://graph.facebook.com/v18.0/act_{account_id}",
            params={
                'access_token': token,
                'fields': 'name,account_status,currency'
            }
        )
        
        if response.status_code == 200:
            account_info = response.json()
            print(f"✅ Acceso a cuenta {account_id}")
            print(f"   Nombre: {account_info.get('name', 'N/A')}")
            print(f"   Estado: {account_info.get('account_status', 'N/A')}")
            print(f"   Moneda: {account_info.get('currency', 'N/A')}")
            return True
        elif response.status_code == 403:
            print(f"❌ Sin permisos para cuenta {account_id}")
            print("   El propietario debe agregar asampayo00@gmail.com como administrador")
            return False
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando cuenta: {e}")
        return False

def show_setup_instructions():
    """Muestra instrucciones para el setup completo"""
    print("\n" + "="*60)
    print("📋 INSTRUCCIONES PARA CONFIGURAR NUEVA CUENTA")
    print("="*60)
    
    print("\n1. 🔑 GENERAR NUEVO TOKEN:")
    print("   - Ve a: https://developers.facebook.com/tools/explorer/")
    print("   - Asegúrate de estar logueado con asampayo00@gmail.com")
    print("   - Selecciona tu App de Meta Ads")
    print("   - Permisos necesarios:")
    print("     • ads_management")
    print("     • ads_read")  
    print("     • business_management")
    print("   - Genera el token y cópialo")
    
    print("\n2. 📝 ACTUALIZAR CONFIGURACIÓN:")
    print("   - Reemplaza META_ACCESS_TOKEN en config/secrets/.env")
    print("   - El token debe empezar con 'EAA...'")
    
    print("\n3. 👥 PERMISOS DE CUENTA:")
    print("   - El propietario de la cuenta 9703931559732773 debe:")
    print("   - Ir a: https://business.facebook.com/settings/ad-accounts")
    print("   - Agregar: asampayo00@gmail.com")
    print("   - Rol: Administrador")
    
    print("\n4. ✅ VERIFICAR:")
    print("   - Ejecuta este script nuevamente")
    print("   - Debe mostrar acceso completo a la cuenta")
    
    print("\n" + "="*60)

def main():
    """Función principal"""
    print("🔄 ACTUALIZACIÓN DE CUENTA META ADS")
    print("="*50)
    print("Cambiando de flousoloflou@gmail.com → asampayo00@gmail.com")
    print()
    
    # Verificar token actual
    token_valid = verify_current_token()
    
    # Verificar acceso a cuenta
    account_access = check_account_access()
    
    print("\n📊 RESUMEN:")
    print(f"   Token válido: {'✅' if token_valid else '❌'}")
    print(f"   Acceso a cuenta: {'✅' if account_access else '❌'}")
    
    if token_valid and account_access:
        print("\n🎉 ¡CONFIGURACIÓN COMPLETA!")
        print("   El sistema está listo con asampayo00@gmail.com")
    else:
        show_setup_instructions()
        
        # Verificar si necesitamos ejecutar el script de permisos
        if token_valid and not account_access:
            print(f"\n💡 TIP: Ejecuta también:")
            print(f"   python scripts\\verify_meta_permissions.py")

if __name__ == "__main__":
    main()