#!/usr/bin/env python3
"""
🎬 Generador Simple de YouTube Refresh Token
Intercambia código de autorización por refresh token
"""

import requests
import json

# Credenciales
CLIENT_ID = "524783623513-rksdl9ncl9c6un9omiqpk4rug8b2dcku.apps.googleusercontent.com"
CLIENT_SECRET = "9f60c6969b0997e3f5062d6e472fefc6"

print("🎬 Generador Simple de YouTube Refresh Token")
print("=" * 50)
print()
print("Paso 1: Abre esta URL en tu navegador:")
print()
print("https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=524783623513-rksdl9ncl9c6un9omiqpk4rug8b2dcku.apps.googleusercontent.com&redirect_uri=urn:ietf:wg:oauth:2.0:oob&scope=https://www.googleapis.com/auth/youtube.upload%20https://www.googleapis.com/auth/youtube&access_type=offline&prompt=consent")
print()
print("Paso 2: Autoriza la aplicación")
print("Paso 3: Copia el código que te dan")
print()

# Pedir código
code = input("📋 Pega aquí el código de autorización: ").strip()

if not code:
    print("❌ No se ingresó ningún código")
    exit(1)

print()
print("🔄 Intercambiando código por tokens...")

# Intercambiar código por tokens
token_url = "https://oauth2.googleapis.com/token"
data = {
    "code": code,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
    "grant_type": "authorization_code"
}

try:
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    
    tokens = response.json()
    
    print()
    print("✅ ¡Tokens generados exitosamente!")
    print("=" * 50)
    print()
    print("📋 REFRESH TOKEN:")
    print(tokens.get('refresh_token'))
    print()
    print("📋 ACCESS TOKEN (temporal):")
    print(tokens.get('access_token'))
    print()
    
    # Guardar tokens
    output = {
        "refresh_token": tokens.get('refresh_token'),
        "access_token": tokens.get('access_token'),
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "token_type": tokens.get('token_type'),
        "expires_in": tokens.get('expires_in')
    }
    
    with open('youtube_tokens.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("💾 Tokens guardados en: youtube_tokens.json")
    print()
    print("🚀 Copia este REFRESH TOKEN para tu .env:")
    print()
    print(f"YOUTUBE_REFRESH_TOKEN={tokens.get('refresh_token')}")
    print()
    
except requests.exceptions.HTTPError as e:
    print(f"❌ Error HTTP: {e}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
