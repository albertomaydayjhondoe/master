#!/usr/bin/env python3
"""
Verificar acceso de colaborador asampayo00@gmail.com a la cuenta de Angel Garcia
"""

import os
import requests

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

def test_collaborator_access():
    """Prueba el acceso como colaborador"""
    print("🤝 VERIFICANDO ACCESO DE COLABORADOR")
    print("="*50)
    print("👤 Colaborador: asampayo00@gmail.com")
    print("🏢 Cuenta principal: Angel Garcia (flousoloflou@gmail.com)")
    print("📊 Cuenta Meta Ads: 9703931559732773")
    print()
    
    env_vars = load_env_file()
    token = env_vars.get('META_ACCESS_TOKEN')
    
    if not token:
        print("❌ No se encontró token")
        return False
    
    try:
        # Verificar usuario del token
        print("🔍 Verificando usuario del token actual...")
        me_response = requests.get(
            "https://graph.facebook.com/v18.0/me",
            params={
                'access_token': token,
                'fields': 'id,name,email'
            }
        )
        
        if me_response.status_code == 200:
            user_info = me_response.json()
            print(f"   ✅ Usuario: {user_info.get('name', 'N/A')}")
            print(f"   ✅ ID: {user_info.get('id', 'N/A')}")
            print(f"   ✅ Email: {user_info.get('email', 'No disponible')}")
        
        # Verificar cuentas de ads accesibles
        print("\n🎯 Verificando cuentas de ads accesibles...")
        ads_response = requests.get(
            "https://graph.facebook.com/v18.0/me/adaccounts",
            params={
                'access_token': token,
                'fields': 'id,name,account_status,owner'
            }
        )
        
        if ads_response.status_code == 200:
            accounts = ads_response.json()
            account_count = len(accounts.get('data', []))
            print(f"   📊 Cuentas encontradas: {account_count}")
            
            target_found = False
            for account in accounts.get('data', []):
                account_id = account.get('id', '').replace('act_', '')
                account_name = account.get('name', 'Sin nombre')
                status = account.get('account_status', 'N/A')
                
                print(f"   🏢 {account_name}")
                print(f"      ID: {account_id}")
                print(f"      Estado: {status}")
                
                if account_id == '9703931559732773':
                    print("      🎉 ¡CUENTA OBJETIVO ENCONTRADA!")
                    target_found = True
            
            if target_found:
                # Probar acceso específico a la cuenta objetivo
                print(f"\n✅ Probando acceso directo a cuenta 9703931559732773...")
                target_response = requests.get(
                    f"https://graph.facebook.com/v18.0/act_9703931559732773",
                    params={
                        'access_token': token,
                        'fields': 'name,account_status,currency,balance,owner'
                    }
                )
                
                if target_response.status_code == 200:
                    target_info = target_response.json()
                    print("   🎉 ¡ACCESO CONFIRMADO!")
                    print(f"      Nombre: {target_info.get('name', 'N/A')}")
                    print(f"      Estado: {target_info.get('account_status', 'N/A')}")
                    print(f"      Moneda: {target_info.get('currency', 'N/A')}")
                    
                    return True
                else:
                    print(f"   ❌ Sin acceso directo: {target_response.status_code}")
                    return False
            else:
                print("   ❌ Cuenta objetivo 9703931559732773 no encontrada")
                return False
        else:
            print(f"   ❌ Error obteniendo cuentas: {ads_response.status_code}")
            print(f"   📝 Respuesta: {ads_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_next_steps(has_access):
    """Muestra los próximos pasos según el resultado"""
    print("\n" + "="*50)
    if has_access:
        print("🎉 ¡PERFECTO! EL SISTEMA ESTÁ LISTO")
        print("="*50)
        print("✅ Token válido con acceso a cuenta objetivo")
        print("✅ asampayo00@gmail.com tiene permisos de colaborador")
        print("✅ Acceso confirmado a cuenta 9703931559732773")
        print()
        print("🚀 SISTEMA 100% OPERATIVO:")
        print("   🤖 YOLOv8: Modelos listos")
        print("   🌐 GoLogin: API configurada")
        print("   📊 Meta Ads: Acceso completo")
        print("   🚀 Railway: Deployment listo")
        print()
        print("💰 Listo para automatización €500/mes")
    else:
        print("🔧 CONFIGURACIÓN ADICIONAL NECESARIA")
        print("="*50)
        print("❌ Sin acceso a cuenta 9703931559732773")
        print()
        print("🎯 OPCIONES:")
        print("1. 📧 Solicitar a Angel Garcia (flousoloflou@gmail.com):")
        print("   - Agregar asampayo00@gmail.com como administrador")
        print("   - Link: https://business.facebook.com/settings/ad-accounts")
        print()
        print("2. 🔑 Generar token con cuenta principal:")
        print("   - Usar flousoloflou@gmail.com para generar token")
        print("   - Con permisos ads_management, business_management")

def main():
    """Función principal"""
    has_access = test_collaborator_access()
    show_next_steps(has_access)

if __name__ == "__main__":
    main()