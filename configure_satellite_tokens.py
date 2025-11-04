#!/usr/bin/env python3
"""
🛰️ Generador de Tokens para Cuentas Satélite
Genera refresh tokens para cada canal satélite de YouTube
"""

import json
import requests
from pathlib import Path

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
    """Intercambiar código por refresh token"""
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

def update_satellite_config(satellite_id, refresh_token, channel_id=None):
    """Actualizar configuración del satélite con el token"""
    config_path = Path("config/satellite_accounts_config.json")
    
    with open(config_path) as f:
        config = json.load(f)
    
    # Buscar y actualizar satélite
    for sat in config['satellite_accounts']['satellites']:
        if sat['id'] == satellite_id:
            sat['youtube_credentials']['refresh_token'] = refresh_token
            if channel_id:
                sat['channel_id'] = channel_id
            break
    
    # Guardar configuración actualizada
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuración actualizada para {satellite_id}")

def main():
    print("🛰️ GENERADOR DE TOKENS PARA CUENTAS SATÉLITE")
    print("=" * 50)
    print()
    
    # Cargar configuración de satélites
    config_path = Path("config/satellite_accounts_config.json")
    with open(config_path) as f:
        config = json.load(f)
    
    satellites = config['satellite_accounts']['satellites']
    
    print(f"📋 Satélites configurados: {len(satellites)}")
    print()
    
    # Mostrar satélites
    for idx, sat in enumerate(satellites, 1):
        status = "✅" if sat['youtube_credentials']['refresh_token'] != "PENDING_OAUTH" else "⏳"
        print(f"{idx}. {status} {sat['name']} ({sat['id']})")
    
    print()
    print("=" * 50)
    print()
    
    # Seleccionar satélite
    choice = input("Selecciona número de satélite a configurar (1-5, o 0 para todos): ").strip()
    
    if choice == "0":
        # Configurar todos
        selected_satellites = satellites
    else:
        try:
            idx = int(choice) - 1
            selected_satellites = [satellites[idx]]
        except (ValueError, IndexError):
            print("❌ Selección inválida")
            return
    
    # Generar URL de autorización
    auth_url = generate_auth_url()
    
    print()
    print("📋 INSTRUCCIONES:")
    print("1. Abre esta URL en tu navegador")
    print("2. Inicia sesión con la cuenta de YouTube del satélite")
    print("3. Autoriza la aplicación")
    print("4. Copia el código que te den")
    print()
    print("🔗 URL:")
    print(auth_url)
    print()
    
    # Procesar cada satélite seleccionado
    for sat in selected_satellites:
        print("=" * 50)
        print(f"🛰️ Configurando: {sat['name']}")
        print("=" * 50)
        print()
        
        # Verificar si ya tiene token
        if sat['youtube_credentials']['refresh_token'] != "PENDING_OAUTH":
            overwrite = input(f"⚠️ {sat['name']} ya tiene token. ¿Sobrescribir? (y/N): ").strip().lower()
            if overwrite != 'y':
                print("⏭️ Saltando...")
                continue
        
        # Pedir código de autorización
        auth_code = input(f"📝 Pega el código para {sat['name']}: ").strip()
        
        if not auth_code:
            print("❌ No se ingresó código, saltando...")
            continue
        
        print()
        print("🔄 Intercambiando código por token...")
        
        # Obtener refresh token
        tokens = exchange_code_for_token(auth_code)
        
        if tokens and 'refresh_token' in tokens:
            refresh_token = tokens['refresh_token']
            
            print()
            print("✅ Refresh Token obtenido:")
            print(refresh_token)
            print()
            
            # Opcional: pedir channel ID si no lo tiene
            channel_id = None
            if sat['channel_id'] == "PENDING_CREATION":
                channel_id = input("📺 Ingresa el Channel ID (opcional, Enter para saltar): ").strip()
            
            # Actualizar configuración
            update_satellite_config(sat['id'], refresh_token, channel_id)
            
            print()
            print(f"🎉 {sat['name']} configurado exitosamente!")
            print()
            
        else:
            print("❌ Error obteniendo token")
            if tokens:
                print(json.dumps(tokens, indent=2))
    
    print()
    print("=" * 50)
    print("🎉 CONFIGURACIÓN COMPLETA")
    print("=" * 50)
    print()
    print("📊 Resumen:")
    
    # Mostrar resumen final
    with open(config_path) as f:
        updated_config = json.load(f)
    
    configured = 0
    for sat in updated_config['satellite_accounts']['satellites']:
        if sat['youtube_credentials']['refresh_token'] != "PENDING_OAUTH":
            configured += 1
            print(f"✅ {sat['name']}")
        else:
            print(f"⏳ {sat['name']} - Pendiente")
    
    print()
    print(f"Total configurado: {configured}/{len(satellites)}")
    print()
    
    if configured == len(satellites):
        print("🚀 ¡Todos los satélites están listos para operar!")
    else:
        print("⚠️ Ejecuta este script nuevamente para configurar los satélites pendientes")

if __name__ == "__main__":
    main()
