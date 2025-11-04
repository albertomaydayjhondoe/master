#!/usr/bin/env python3
"""
🎬 Generador Simple de YouTube Refresh Token
Sin servidor local - solo intercambio de código
"""

import requests
import json

CLIENT_ID = "524783623513-rksdl9ncl9c6un9omiqpk4rug8b2dcku.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"

SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]

def generate_auth_url():
    """Generar URL de autorización"""
    scope_string = ' '.join(SCOPES)
    
    url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"response_type=code&"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"scope={scope_string}&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    return url

def exchange_code_for_token(auth_code):
    """Intercambiar código por tokens"""
    
    token_url = "https://oauth2.googleapis.com/token"
    
    data = {
        'code': auth_code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None

def main():
    print("🎬 Generador Simple de YouTube Refresh Token")
    print("=" * 50)
    print()
    
    # Paso 1: Mostrar URL
    auth_url = generate_auth_url()
    print("📋 PASO 1: Abre esta URL en tu navegador:")
    print()
    print(auth_url)
    print()
    print("Autoriza la aplicación y copia el código que te dan.")
    print()
    
    # Paso 2: Pedir código
    auth_code = input("📝 Pega el código aquí: ").strip()
    
    if not auth_code:
        print("❌ No ingresaste ningún código")
        return
    
    print()
    print("🔄 Intercambiando código por tokens...")
    print()
    
    # Paso 3: Intercambiar código
    tokens = exchange_code_for_token(auth_code)
    
    if tokens and 'refresh_token' in tokens:
        print("✅ ¡Tokens generados exitosamente!")
        print("=" * 50)
        print()
        print("📋 REFRESH TOKEN:")
        print(tokens['refresh_token'])
        print()
        print("📋 ACCESS TOKEN (temporal):")
        print(tokens['access_token'])
        print()
        
        # Guardar
        output = {
            "refresh_token": tokens['refresh_token'],
            "access_token": tokens['access_token'],
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
        
        with open('youtube_tokens.json', 'w') as f:
            json.dump(output, f, indent=2)
        
        print("💾 Tokens guardados en: youtube_tokens.json")
        print()
        print("🚀 Copia este REFRESH TOKEN a tu .env:")
        print(f"YOUTUBE_REFRESH_TOKEN={tokens['refresh_token']}")
        
    else:
        print("❌ Error al obtener tokens")
        if tokens:
            print(json.dumps(tokens, indent=2))

if __name__ == "__main__":
    main()
