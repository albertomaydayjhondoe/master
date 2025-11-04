#!/usr/bin/env python3
"""
🎬 Generador de YouTube Refresh Token
Genera el refresh token para YouTube Data API v3
"""

import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Scopes necesarios para YouTube
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]

def generate_refresh_token():
    """Generar refresh token de YouTube"""
    
    # Credenciales del cliente
    client_config = {
        "installed": {
            "client_id": "524783623513-rksdl9ncl9c6un9omiqpk4rug8b2dcku.apps.googleusercontent.com",
            "client_secret": "9f60c6969b0997e3f5062d6e472fefc6",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080/", "urn:ietf:wg:oauth:2.0:oob"]
        }
    }
    
    print("🎬 Generando YouTube Refresh Token")
    print("=" * 50)
    print()
    print("Se abrirá tu navegador para autorizar la aplicación...")
    print("Acepta los permisos y copia el código de autorización.")
    print()
    
    # Crear flow de OAuth
    flow = InstalledAppFlow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )
    
    # Ejecutar flow local
    creds = flow.run_local_server(port=8080, prompt='consent')
    
    # Mostrar tokens
    print()
    print("✅ ¡Tokens generados exitosamente!")
    print("=" * 50)
    print()
    print("📋 REFRESH TOKEN:")
    print(creds.refresh_token)
    print()
    print("📋 ACCESS TOKEN (temporal):")
    print(creds.token)
    print()
    
    # Guardar en archivo
    tokens = {
        "refresh_token": creds.refresh_token,
        "access_token": creds.token,
        "client_id": client_config["installed"]["client_id"],
        "client_secret": client_config["installed"]["client_secret"]
    }
    
    with open('youtube_tokens.json', 'w') as f:
        json.dump(tokens, f, indent=2)
    
    print("💾 Tokens guardados en: youtube_tokens.json")
    print()
    print("🚀 Usa este REFRESH TOKEN en tu .env:")
    print(f"YOUTUBE_REFRESH_TOKEN={creds.refresh_token}")

if __name__ == "__main__":
    try:
        generate_refresh_token()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 Asegúrate de tener instalado: pip install google-auth-oauthlib")
