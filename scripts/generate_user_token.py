#!/usr/bin/env python3
"""
Generador de User Token para Meta Ads con permisos correctos
App ID: 2672426126432982 | Account: 1771115133833816
"""

import webbrowser
import urllib.parse
import requests
import sys
sys.path.append('c:\\Users\\ADM\\Documents\\GitHub\\master')

from config.app_settings import get_env

def generate_user_token_url():
    """Genera URL para obtener User Token con permisos de ads"""
    print("🔑 GENERANDO USER TOKEN PARA META ADS")
    print("="*60)
    
    app_id = "2672426126432982"
    
    # Permisos necesarios para Meta Ads
    permissions = [
        "ads_management",  # CRÍTICO: Gestión de anuncios
        "ads_read",        # CRÍTICO: Lectura de anuncios  
        "business_management", # Gestión de Business Manager
        "email",           # Información básica
        "public_profile"   # Perfil público
    ]
    
    # URL de autorización para User Token
    auth_url = "https://www.facebook.com/v18.0/dialog/oauth?" + urllib.parse.urlencode({
        'client_id': app_id,
        'redirect_uri': 'https://developers.facebook.com/tools/explorer/callback',
        'scope': ','.join(permissions),
        'response_type': 'code',
        'state': 'user_token_generation'
    })
    
    print(f"📱 App ID: {app_id}")
    print(f"🎯 Account objetivo: 1771115133833816") 
    print(f"🔑 Permisos requeridos:")
    for perm in permissions:
        print(f"   • {perm}")
    
    print(f"\n🌐 URL de autorización:")
    print(auth_url)
    
    return auth_url

def show_step_by_step_instructions():
    """Muestra instrucciones paso a paso"""
    print(f"\n📋 INSTRUCCIONES PASO A PASO:")
    print("="*60)
    
    print("🎯 OPCIÓN 1 - GRAPH API EXPLORER (MÁS FÁCIL):")
    print("1. Ve a: https://developers.facebook.com/tools/explorer/")
    print("2. Selecciona App: 'Alberto' (2672426126432982)")
    print("3. Haz clic 'Add a Permission' y agrega:")
    print("   ✓ ads_management")
    print("   ✓ ads_read")
    print("   ✓ business_management")
    print("4. Haz clic 'Generate Access Token'")
    print("5. Autoriza la app si aparece popup")
    print("6. Copia el token que empieza con 'EAAa...'")
    print("7. Pégalo aquí para probarlo")
    
    print(f"\n🎯 OPCIÓN 2 - URL DIRECTA:")
    print("1. Abre la URL que generé arriba")
    print("2. Autoriza la aplicación")
    print("3. Copia el 'code' del callback")
    print("4. Intercambiarlo por access_token")
    
    print(f"\n💡 IMPORTANTE:")
    print("• El token debe empezar con 'EAAa'")
    print("• Debe ser un USER TOKEN, no App Token")
    print("• Debe tener permisos ads_management/ads_read")

def test_user_token_input():
    """Permite probar un token ingresado por el usuario"""
    print(f"\n🧪 PRUEBA DE TOKEN DE USUARIO")
    print("="*50)
    
    token = input("🔑 Pega aquí tu User Token (EAAa...): ").strip()
    
    if not token:
        print("❌ No se proporcionó token")
        return False
    
    if not token.startswith('EAAa'):
        print("⚠️ ADVERTENCIA: El token no parece ser un User Token")
        print("   Los User Tokens suelen empezar con 'EAAa'")
        print("   ¿Continuar de todas formas? (y/n)")
        if input().lower() != 'y':
            return False
    
    # Probar token
    return test_token_with_ads_access(token)

def test_token_with_ads_access(access_token):
    """Prueba token específicamente para acceso a ads"""
    print(f"\n🚀 PROBANDO TOKEN PARA ACCESO A ADS")
    print("="*50)
    
    account_id = "1771115133833816"
    
    # Test 1: Usuario del token
    try:
        response = requests.get(
            "https://graph.facebook.com/v18.0/me",
            params={'access_token': access_token}
        )
        
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Token válido - Usuario: {user.get('name', 'N/A')}")
        else:
            print(f"❌ Token inválido: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error validando token: {e}")
        return False
    
    # Test 2: Permisos del token
    try:
        response = requests.get(
            "https://graph.facebook.com/v18.0/me/permissions",
            params={'access_token': access_token}
        )
        
        if response.status_code == 200:
            permissions = response.json()
            granted = [p['permission'] for p in permissions.get('data', []) if p.get('status') == 'granted']
            
            ads_perms = ['ads_management', 'ads_read', 'business_management']
            has_ads = [perm for perm in ads_perms if perm in granted]
            
            print(f"🔑 Permisos encontrados: {len(granted)}")
            print(f"✅ Permisos de ads: {has_ads}")
            
            if not has_ads:
                print("❌ ERROR: Token no tiene permisos de ads")
                print("   Necesitas ads_management y/o ads_read")
                return False
        else:
            print(f"❌ Error verificando permisos: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error verificando permisos: {e}")
        return False
    
    # Test 3: Acceso a cuenta específica
    try:
        response = requests.get(
            f"https://graph.facebook.com/v18.0/act_{account_id}",
            params={'access_token': access_token}
        )
        
        if response.status_code == 200:
            account = response.json()
            print(f"🎯 ¡ÉXITO! Acceso a cuenta {account_id}")
            print(f"   Nombre: {account.get('name', 'N/A')}")
            print(f"   Moneda: {account.get('currency', 'N/A')}")
            
            # Actualizar .env con token válido
            update_env_with_valid_token(access_token)
            return True
        else:
            error = response.json()
            print(f"❌ No se puede acceder a cuenta {account_id}")
            print(f"   Error: {error.get('error', {}).get('message', 'Desconocido')}")
            return False
    except Exception as e:
        print(f"❌ Error accediendo a cuenta: {e}")
        return False

def update_env_with_valid_token(valid_token):
    """Actualiza .env con token válido"""
    print(f"\n⚙️ ACTUALIZANDO .ENV CON TOKEN VÁLIDO")
    print("="*50)
    
    env_file = 'c:\\Users\\ADM\\Documents\\GitHub\\master\\.env'
    
    # Leer archivo actual
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazar token
    old_token_line = None
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if line.startswith('META_ACCESS_TOKEN='):
            old_token_line = line
            lines[i] = f'META_ACCESS_TOKEN={valid_token}'
            break
    
    # Escribir archivo actualizado
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ .env actualizado exitosamente")
    print(f"   Anterior: {old_token_line}")
    print(f"   Nuevo: META_ACCESS_TOKEN={valid_token[:30]}...")
    
    print(f"\n🎉 ¡SISTEMA META ADS 100% CONFIGURADO!")
    print("✅ Token válido con permisos de ads")
    print("✅ Acceso confirmado a cuenta 1771115133833816")
    print("✅ Configuración guardada en .env")

def main():
    """Función principal"""
    print("🎯 GENERADOR DE USER TOKEN PARA META ADS")
    print("App: Alberto (2672426126432982)")
    print("Account: 1771115133833816")
    print()
    
    # Generar URL de autorización
    auth_url = generate_user_token_url()
    
    # Mostrar instrucciones
    show_step_by_step_instructions()
    
    print(f"\n" + "="*60)
    print("💬 PRÓXIMOS PASOS:")
    print("1. Genera tu User Token usando Graph API Explorer")
    print("2. Pégalo aquí para probarlo y configurarlo automáticamente")
    print("3. ¡Sistema completo al 100%!")
    print("="*60)
    
    # Permitir probar token
    while True:
        choice = input("\n¿Tienes tu User Token listo? (y/n/url): ").lower().strip()
        
        if choice == 'y':
            if test_user_token_input():
                print("\n🎊 ¡CONFIGURACIÓN COMPLETADA CON ÉXITO!")
                break
            else:
                print("\n⚠️ Token no válido. Inténtalo de nuevo.")
                
        elif choice == 'n':
            print("👍 Ve a generar tu token y vuelve cuando lo tengas")
            break
            
        elif choice == 'url':
            print(f"\n🌐 Abriendo Graph API Explorer...")
            webbrowser.open('https://developers.facebook.com/tools/explorer/')
            
        else:
            print("Responde 'y' (sí), 'n' (no) o 'url' (abrir explorador)")

if __name__ == "__main__":
    main()