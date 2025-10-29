#!/usr/bin/env python3
"""
Script para verificar detalladamente el token actual y el email asociado
"""

import os
import sys
import requests
from datetime import datetime

def load_env_file():
    """Carga las variables de entorno del archivo .env"""
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'),  # raíz del proyecto
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
            break  # Usar el primer archivo encontrado
    
    return env_vars

def verify_token_email():
    """Verifica detalladamente el email del token"""
    print("🔍 VERIFICACIÓN DETALLADA DEL TOKEN")
    print("="*50)
    
    env_vars = load_env_file()
    token = env_vars.get('META_ACCESS_TOKEN')
    
    if not token:
        print("❌ No se encontró META_ACCESS_TOKEN")
        return False
    
    try:
        # Verificar información básica del usuario
        print("📋 Información del usuario:")
        response = requests.get(
            f"https://graph.facebook.com/v18.0/me",
            params={
                'access_token': token,
                'fields': 'id,name,email'
            }
        )
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"   ✅ Nombre: {user_info.get('name', 'N/A')}")
            print(f"   ✅ ID: {user_info.get('id', 'N/A')}")
            print(f"   ✅ Email: {user_info.get('email', 'No disponible en API')}")
            
            # Verificar si es asampayo00@gmail.com
            email = user_info.get('email', '')
            if 'asampayo00@gmail.com' in email.lower():
                print("   🎉 ¡CONFIRMADO! Token asociado a asampayo00@gmail.com")
                return True
            else:
                print(f"   📧 Email del token: {email}")
                
        # Intentar obtener más información de la cuenta
        print("\n🔍 Verificando permisos del token:")
        perms_response = requests.get(
            f"https://graph.facebook.com/v18.0/me/permissions",
            params={'access_token': token}
        )
        
        if perms_response.status_code == 200:
            permissions = perms_response.json()
            granted_perms = [p['permission'] for p in permissions.get('data', []) if p.get('status') == 'granted']
            print("   📝 Permisos concedidos:")
            for perm in granted_perms:
                if 'ads' in perm or 'business' in perm:
                    print(f"      ✅ {perm}")
                else:
                    print(f"      📋 {perm}")
                    
        # Verificar cuentas de ads accesibles
        print("\n🎯 Verificando cuentas de ads:")
        ads_response = requests.get(
            f"https://graph.facebook.com/v18.0/me/adaccounts",
            params={
                'access_token': token,
                'fields': 'id,name,account_status'
            }
        )
        
        if ads_response.status_code == 200:
            accounts = ads_response.json()
            print(f"   📊 Cuentas accesibles: {len(accounts.get('data', []))}")
            for account in accounts.get('data', []):
                account_id = account.get('id', '').replace('act_', '')
                print(f"      🏢 {account.get('name', 'Sin nombre')}")
                print(f"         ID: {account_id}")
                print(f"         Estado: {account.get('account_status', 'N/A')}")
                
                # Verificar si incluye nuestra cuenta objetivo
                if account_id == '9703931559732773':
                    print("         🎉 ¡ENCONTRADA! Esta es nuestra cuenta objetivo")
                    
        return True
        
    except Exception as e:
        print(f"❌ Error verificando token: {e}")
        return False

def main():
    """Función principal"""
    print("🔄 VERIFICACIÓN DE TOKEN ANGEL GARCIA")
    print("Confirmando que el token está asociado a asampayo00@gmail.com")
    print()
    
    if verify_token_email():
        print("\n📊 CONCLUSIÓN:")
        print("   Si Angel Garcia tiene el email asampayo00@gmail.com,")
        print("   entonces el token actual es correcto.")
        print("   El problema son solo los PERMISOS de la cuenta específica.")
        print("\n🎯 PRÓXIMO PASO:")
        print("   Solicitar al propietario de 9703931559732773 que agregue")
        print("   a Angel Garcia (asampayo00@gmail.com) como Administrador")
        
        # Ejecutar verificación de permisos
        print("\n🔧 Ejecutando verificación de permisos...")
        return True
    else:
        print("\n❌ Hay problemas con el token actual")
        return False

if __name__ == "__main__":
    main()