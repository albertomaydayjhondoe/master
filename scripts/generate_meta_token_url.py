#!/usr/bin/env python3
"""
Generar URL para obtener token de usuario con App ID 2672426126432982
"""

import urllib.parse

def generate_facebook_auth_url():
    """Genera URL de autorización de Facebook para obtener token"""
    print("🔑 GENERANDO URL DE AUTORIZACIÓN FACEBOOK")
    print("="*60)
    
    app_id = "2672426126432982"
    redirect_uri = "https://developers.facebook.com/tools/explorer/callback"
    
    # Permisos necesarios para Meta Ads
    permissions = [
        "ads_management",
        "ads_read", 
        "business_management",
        "email",
        "public_profile"
    ]
    
    # Construir URL de autorización
    base_url = "https://www.facebook.com/v18.0/dialog/oauth"
    params = {
        'client_id': app_id,
        'redirect_uri': redirect_uri,
        'scope': ','.join(permissions),
        'response_type': 'code',
        'state': 'meta_ads_auth'
    }
    
    # Codificar parámetros
    query_string = urllib.parse.urlencode(params)
    auth_url = f"{base_url}?{query_string}"
    
    print(f"📱 App ID: {app_id}")
    print(f"🔑 Permisos: {', '.join(permissions)}")
    print(f"\n🌐 URL de autorización:")
    print(f"{auth_url}")
    
    return auth_url

def show_manual_steps():
    """Muestra pasos manuales para obtener token"""
    print(f"\n📋 PASOS MANUALES ALTERNATIVOS:")
    print("="*60)
    
    print("1️⃣ MÉTODO GRAPH API EXPLORER:")
    print("   • Ve a: https://developers.facebook.com/tools/explorer/")
    print("   • Selecciona tu app en el dropdown")
    print("   • Haz clic 'Add a Permission'")
    print("   • Busca y agrega: ads_management")
    print("   • Busca y agrega: ads_read") 
    print("   • Haz clic 'Generate Access Token'")
    print("   • Copia el token y pégalo aquí")
    
    print(f"\n2️⃣ MÉTODO DIRECTO CON URL:")
    print("   • Abre la URL generada arriba")
    print("   • Autoriza la aplicación")
    print("   • Copia el code del callback")
    print("   • Intercambia code por access_token")
    
    print(f"\n3️⃣ MÉTODO SIMPLIFICADO:")
    print("   • Si tienes cualquier token de Facebook (aunque sea básico)")
    print("   • Pégalo aquí y lo probaremos")
    print("   • Podemos verificar qué permisos tiene")

def test_app_id_directly():
    """Prueba información pública del App ID"""
    print(f"\n🔍 VERIFICANDO APP ID 2672426126432982")
    print("="*50)
    
    import requests
    
    try:
        # Usar token de aplicación básico para verificar app
        app_token = f"2672426126432982|access_token"
        
        response = requests.get(
            f"https://graph.facebook.com/v18.0/2672426126432982",
            params={'access_token': app_token}
        )
        
        print(f"📊 Respuesta: {response.status_code}")
        
        if response.status_code == 200:
            app_info = response.json()
            print(f"✅ App encontrada: {app_info.get('name', 'N/A')}")
            print(f"✅ ID confirmado: {app_info.get('id', 'N/A')}")
        else:
            print(f"❌ Error verificando app: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def show_simple_token_test():
    """Muestra cómo probar cualquier token que el usuario tenga"""
    print(f"\n🧪 PRUEBA DE TOKEN SIMPLE")
    print("="*50)
    print("Si tienes CUALQUIER token de Facebook:")
    print("1. Pégalo aquí (puede ser de cualquier app)")
    print("2. Lo probaré para ver qué permisos tiene")
    print("3. Verificaré si puede acceder a cuentas de ads")
    print("4. Si funciona, lo configuramos inmediatamente")
    
    print(f"\n💡 TOKENS VÁLIDOS:")
    print("   • Token de Graph API Explorer")
    print("   • Token de cualquier app de Facebook")
    print("   • Token temporal de testing")
    print("   • Incluso tokens básicos sin permisos")

def main():
    """Función principal"""
    print("🎯 CONFIGURACIÓN META ADS - APP ID: 2672426126432982")
    print()
    
    # Generar URL de autorización
    auth_url = generate_facebook_auth_url()
    
    # Mostrar pasos manuales
    show_manual_steps()
    
    # Verificar App ID
    test_app_id_directly()
    
    # Mostrar prueba simple
    show_simple_token_test()
    
    print(f"\n" + "="*60)
    print("💬 PRÓXIMO PASO:")
    print("Proporciona cualquier token de Facebook y lo probaremos")
    print("O escribe 'url' para abrir la URL de autorización")
    print("="*60)

if __name__ == "__main__":
    main()