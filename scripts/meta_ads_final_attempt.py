#!/usr/bin/env python3
"""
Último intento Meta Ads - Enfoque directo y simplificado
"""

import os
import requests

def show_current_situation():
    """Muestra la situación actual"""
    print("🎯 ÚLTIMO INTENTO META ADS - ENFOQUE DIRECTO")
    print("="*60)
    print("📊 Situación actual:")
    print("   ✅ App ID: 2672426126432982 (App 'Alberto')")
    print("   ❌ App Secret: No válido para este App ID")
    print("   🎯 Cuenta objetivo: 1771115133833816")
    print("   🔧 Necesidad: Token con permisos ads_management")
    print()

def show_direct_approaches():
    """Muestra enfoques directos para conseguir el token"""
    print("🔧 ENFOQUES DIRECTOS PARA CONSEGUIR TOKEN:")
    print("="*60)
    
    print("\n1️⃣ OPCIÓN MÁS SIMPLE - TOKEN DE USUARIO:")
    print("   📋 Pasos:")
    print("   • Ve a: https://developers.facebook.com/tools/explorer/")
    print("   • Selecciona App: Alberto (2672426126432982)")
    print("   • Add Permission: ads_management")
    print("   • Add Permission: ads_read")
    print("   • Generate Access Token")
    print("   • Copia el token y pégalo aquí")
    
    print("\n2️⃣ OPCIÓN ALTERNATIVA - NUEVA APP:")
    print("   📋 Pasos:")
    print("   • Ve a: https://developers.facebook.com/apps/")
    print("   • Create App > Business")
    print("   • Agrega Meta Marketing API")
    print("   • Genera token con permisos")
    
    print("\n3️⃣ OPCIÓN MANUAL - USAR CUENTA DIFERENTE:")
    print("   📋 Pasos:")
    print("   • Usa una cuenta que tenga acceso directo a 1771115133833816")
    print("   • Crea app desde esa cuenta")
    print("   • Genera token directamente")

def test_any_token(token):
    """Prueba cualquier token que el usuario proporcione"""
    print(f"\n🔍 PROBANDO TOKEN PROPORCIONADO")
    print("="*50)
    print(f"Token: {token[:20]}...")
    
    try:
        # Probar información básica
        me_response = requests.get(
            "https://graph.facebook.com/v18.0/me",
            params={'access_token': token}
        )
        
        if me_response.status_code == 200:
            user_info = me_response.json()
            print(f"✅ Usuario: {user_info.get('name', 'N/A')}")
            print(f"✅ ID: {user_info.get('id', 'N/A')}")
        else:
            print(f"❌ Token inválido: {me_response.status_code}")
            return False
        
        # Probar permisos
        perms_response = requests.get(
            "https://graph.facebook.com/v18.0/me/permissions",
            params={'access_token': token}
        )
        
        if perms_response.status_code == 200:
            permissions = perms_response.json()
            granted = [p['permission'] for p in permissions.get('data', []) if p.get('status') == 'granted']
            
            print(f"\n🔑 Permisos concedidos:")
            for perm in granted:
                print(f"   {'✅' if 'ads' in perm else '📋'} {perm}")
            
            has_ads_perms = any('ads' in p for p in granted)
            
            if has_ads_perms:
                print(f"\n✅ Token tiene permisos de ads!")
                return test_account_access(token)
            else:
                print(f"\n❌ Token SIN permisos de ads")
                return False
        else:
            print(f"❌ Error verificando permisos: {perms_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_account_access(token):
    """Prueba acceso a la cuenta específica"""
    print(f"\n🎯 PROBANDO ACCESO A CUENTA 1771115133833816")
    print("="*50)
    
    try:
        # Probar acceso directo
        response = requests.get(
            f"https://graph.facebook.com/v18.0/act_1771115133833816",
            params={
                'access_token': token,
                'fields': 'id,name,account_status,currency'
            }
        )
        
        if response.status_code == 200:
            account_info = response.json()
            print(f"🎉 ¡ACCESO EXITOSO!")
            print(f"✅ Nombre: {account_info.get('name', 'N/A')}")
            print(f"✅ Estado: {account_info.get('account_status', 'N/A')}")
            print(f"✅ Moneda: {account_info.get('currency', 'N/A')}")
            
            # Actualizar .env
            update_token_in_env(token)
            return True
            
        elif response.status_code == 403:
            print(f"❌ Sin permisos para esta cuenta específica")
            
            # Probar listar todas las cuentas accesibles
            print(f"\n🔍 Listando cuentas accesibles...")
            list_response = requests.get(
                "https://graph.facebook.com/v18.0/me/adaccounts",
                params={'access_token': token, 'fields': 'id,name'}
            )
            
            if list_response.status_code == 200:
                accounts = list_response.json()
                print(f"📊 Cuentas disponibles: {len(accounts.get('data', []))}")
                for account in accounts.get('data', []):
                    account_id = account.get('id', '').replace('act_', '')
                    print(f"   🏢 {account.get('name', 'Sin nombre')} (ID: {account_id})")
                    
                if accounts.get('data'):
                    print(f"\n💡 Puedes usar cualquiera de estas cuentas")
                    return False
            
            return False
            
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def update_token_in_env(token):
    """Actualiza el token en .env"""
    print(f"\n📝 ACTUALIZANDO TOKEN EN .ENV")
    
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('META_ACCESS_TOKEN='):
                lines[i] = f'META_ACCESS_TOKEN={token}'
                break
        
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ Token actualizado correctamente")
        
    except Exception as e:
        print(f"❌ Error actualizando .env: {e}")

def main():
    """Función principal"""
    show_current_situation()
    show_direct_approaches()
    
    print(f"\n" + "="*60)
    print("💬 INSTRUCCIONES SIMPLES:")
    print("1. 🌐 Abre: https://developers.facebook.com/tools/explorer/")
    print("2. 📱 Selecciona App: Alberto (2672426126432982)")
    print("3. 🔑 Add Permission: ads_management y ads_read")
    print("4. 🎯 Generate Access Token")
    print("5. 📋 Copia el token COMPLETO aquí")
    print("="*60)
    
    # Esperar input del usuario
    print(f"\n⏳ Cuando tengas el token, pégalo y presiona Enter:")
    print(f"   (O escribe 'skip' para continuar sin Meta Ads)")

if __name__ == "__main__":
    main()