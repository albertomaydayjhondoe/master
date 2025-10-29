#!/usr/bin/env python3
"""
Guía para configurar correctamente el acceso a la cuenta Meta Ads: 9703931559732773

Este script te ayuda a obtener los tokens y permisos necesarios.
"""
import sys
import webbrowser
from pathlib import Path

def generate_facebook_auth_url():
    """Generar URL para autorización de Facebook."""
    
    print("🔐 CONFIGURACIÓN DE ACCESO META ADS")
    print("=" * 60)
    print("📋 Necesitas configurar permisos para la cuenta: 9703931559732773")
    print()
    
    # Paso 1: Información básica
    print("📝 PASO 1: Información de tu App de Facebook")
    print("-" * 40)
    print("Si no tienes una app, ve a: https://developers.facebook.com/apps/")
    print("1. Crea una nueva app (tipo: Business)")
    print("2. Agrega el producto 'Marketing API'")
    print("3. Anota tu App ID y App Secret")
    print()
    
    # Paso 2: URL de autorización
    print("📝 PASO 2: URL de Autorización")
    print("-" * 40)
    
    app_id = input("Ingresa tu Facebook App ID (o presiona Enter para usar ejemplo): ").strip()
    if not app_id:
        app_id = "TU_APP_ID"
    
    # Permisos necesarios
    permissions = [
        "ads_management",      # Crear y gestionar campañas
        "ads_read",           # Leer datos de campañas
        "business_management", # Gestión de business manager
        "pages_read_engagement", # Leer engagement de páginas
        "pages_show_list"     # Listar páginas
    ]
    
    permissions_str = ",".join(permissions)
    redirect_uri = "https://localhost:8000/callback"  # Puedes usar cualquier URL válida
    
    auth_url = (
        f"https://www.facebook.com/v18.0/dialog/oauth?"
        f"client_id={app_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={permissions_str}&"
        f"response_type=code"
    )
    
    print("🔗 URL de autorización generada:")
    print(f"   {auth_url}")
    print()
    print("📋 INSTRUCCIONES:")
    print("1. Reemplaza TU_APP_ID con tu App ID real")
    print("2. Ve a la URL en tu navegador") 
    print("3. Acepta los permisos solicitados")
    print("4. Copia el 'code' de la URL de respuesta")
    print()
    
    # Paso 3: Intercambio por token de acceso
    print("📝 PASO 3: Obtener Access Token")
    print("-" * 40)
    print("Una vez que tengas el 'code', ejecuta este comando:")
    print()
    
    app_secret = input("Ingresa tu Facebook App Secret (opcional): ").strip() or "TU_APP_SECRET"
    
    token_url = (
        f"https://graph.facebook.com/v18.0/oauth/access_token?"
        f"client_id={app_id}&"
        f"redirect_uri={redirect_uri}&"
        f"client_secret={app_secret}&"
        f"code=EL_CODE_QUE_OBTUVISTE"
    )
    
    print(f"🔗 URL para obtener token:")
    print(f"   {token_url}")
    print()
    print("📋 Reemplaza 'EL_CODE_QUE_OBTUVISTE' con el code real")
    print()
    
    # Paso 4: Verificar permisos de cuenta
    print("📝 PASO 4: Verificar Acceso a la Cuenta")
    print("-" * 40)
    print("🆔 Cuenta objetivo: 9703931559732773")
    print()
    print("Posibles problemas y soluciones:")
    print("❓ Si no tienes acceso a esta cuenta:")
    print("   1. Verifica que seas admin de la cuenta de anuncios")
    print("   2. Ve a Business Manager → Configuración → Cuentas de anuncios")
    print("   3. Agrega o solicita acceso a la cuenta 9703931559732773")
    print()
    print("❓ Si la cuenta no existe:")
    print("   1. Verifica el ID en tu Facebook Ads Manager")
    print("   2. Va a Configuración → Info de la cuenta de anuncios")
    print("   3. Copia el ID exacto (sin 'act_')")
    print()
    
    # Paso 5: Alternativa - usar tu propia cuenta
    print("📝 ALTERNATIVA: Usar Tu Cuenta Existente")
    print("-" * 40)
    print("Si prefieres usar una cuenta que ya controlas:")
    print("1. Ve a https://business.facebook.com/")
    print("2. Crea una nueva cuenta de anuncios")
    print("3. Configura método de pago")
    print("4. Usa el ID de esa cuenta nueva")
    print()
    
    # Generar script de test rápido
    print("📝 SCRIPT DE VERIFICACIÓN RÁPIDA")
    print("-" * 40)
    
    test_script = f'''
# Test rápido con curl (reemplaza TU_ACCESS_TOKEN)
curl "https://graph.facebook.com/v18.0/me/adaccounts?access_token=TU_ACCESS_TOKEN"

# Test con Python
import requests
token = "TU_ACCESS_TOKEN"
response = requests.get(f"https://graph.facebook.com/v18.0/me/adaccounts?access_token={{token}}")
print(response.json())
'''
    
    print("💾 Guarda este script para verificar tus cuentas disponibles:")
    print(test_script)
    
    # Opción de abrir navegador
    print("\n🌐 ¿Quieres abrir Facebook Developers ahora?")
    open_browser = input("Presiona 'y' para abrir en navegador, o cualquier tecla para continuar: ").strip().lower()
    
    if open_browser == 'y':
        webbrowser.open("https://developers.facebook.com/apps/")
        print("✅ Abriendo Facebook Developers...")
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE PASOS:")
    print("1. Crear/configurar app en Facebook Developers")
    print("2. Obtener autorización con permisos ads_management")
    print("3. Intercambiar code por access_token") 
    print("4. Verificar acceso a cuenta 9703931559732773")
    print("5. Actualizar .env con nuevo token")
    print("6. Ejecutar test_new_meta_account.py nuevamente")
    print()
    print("💡 Tip: También puedes usar Facebook Graph API Explorer")
    print("   https://developers.facebook.com/tools/explorer/")

if __name__ == "__main__":
    generate_facebook_auth_url()