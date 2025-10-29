#!/usr/bin/env python3
"""
Verificar qué cuentas Meta Ads están disponibles con el token actual.
Esto te ayudará a ver qué cuentas puedes usar inmediatamente.
"""
import os
import sys
import requests
import json
from pathlib import Path

# Cargar variables de entorno
sys.path.append(str(Path(__file__).parent.parent))
from config.app_settings import get_env

def check_available_accounts():
    """Verificar cuentas disponibles con token actual."""
    print("📊 VERIFICANDO CUENTAS META ADS DISPONIBLES")
    print("=" * 60)
    
    access_token = get_env("META_ACCESS_TOKEN")
    
    if not access_token:
        print("❌ META_ACCESS_TOKEN no encontrado en .env")
        return False
    
    print(f"✅ Token encontrado: {access_token[:20]}...")
    
    # Test 1: Usuario actual
    print(f"\n👤 Test 1: Información del usuario...")
    try:
        url = "https://graph.facebook.com/v18.0/me"
        params = {
            "fields": "name,id",
            "access_token": access_token
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Usuario: {data.get('name', 'Desconocido')}")
            print(f"  🆔 ID: {data.get('id', 'N/A')}")
        else:
            print(f"  ❌ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error obteniendo usuario: {e}")
        return False
    
    # Test 2: Cuentas de anuncios disponibles
    print(f"\n📢 Test 2: Cuentas de anuncios disponibles...")
    try:
        url = "https://graph.facebook.com/v18.0/me/adaccounts"
        params = {
            "fields": "id,name,account_status,currency,timezone_name,amount_spent,balance",
            "access_token": access_token
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            accounts = data.get('data', [])
            
            print(f"  📊 Total de cuentas encontradas: {len(accounts)}")
            
            if accounts:
                print("\n  📋 Detalles de cuentas:")
                for i, account in enumerate(accounts, 1):
                    account_id = account.get('id', '').replace('act_', '')
                    name = account.get('name', 'Sin nombre')
                    status = account.get('account_status', 'Desconocido')
                    currency = account.get('currency', 'N/A')
                    balance = account.get('balance', 0)
                    
                    status_icon = "🟢" if status == 1 else "🔴" if status == 2 else "🟡"
                    
                    print(f"\n    {i}. {status_icon} {name}")
                    print(f"       🆔 ID: {account_id}")
                    print(f"       💰 Moneda: {currency}")
                    print(f"       🏦 Balance: {balance} {currency}")
                    print(f"       📊 Estado: {status}")
                    
                    # Verificar si es la cuenta que queremos usar
                    if account_id == "9703931559732773":
                        print(f"       🎯 ¡ESTA ES LA CUENTA QUE QUERÍAS USAR!")
                    
                # Sugerir mejor cuenta para usar
                print(f"\n  💡 Recomendaciones:")
                active_accounts = [acc for acc in accounts if acc.get('account_status') == 1]
                
                if active_accounts:
                    best_account = active_accounts[0]
                    best_id = best_account.get('id', '').replace('act_', '')
                    print(f"    ✅ Cuenta recomendada para usar: {best_id}")
                    print(f"    📝 Para usarla, actualiza META_ADS_ACCOUNT_ID={best_id} en .env")
                else:
                    print(f"    ⚠️ No se encontraron cuentas activas")
                    
            else:
                print("  ℹ️ No se encontraron cuentas de anuncios")
                print("  💡 Necesitas crear una cuenta en https://business.facebook.com/")
                
        else:
            print(f"  ❌ Error obteniendo cuentas: {response.status_code}")
            print(f"  📝 Respuesta: {response.text}")
            
            if response.status_code == 400:
                print("  💡 Posible solución: El token necesita permisos 'ads_read'")
            elif response.status_code == 403:
                print("  💡 Posible solución: El token no tiene acceso a cuentas de anuncios")
                
    except Exception as e:
        print(f"  ❌ Error en test 2: {e}")
    
    # Test 3: Páginas de Facebook disponibles
    print(f"\n📄 Test 3: Páginas de Facebook disponibles...")
    try:
        url = "https://graph.facebook.com/v18.0/me/accounts"
        params = {
            "fields": "id,name,category",
            "access_token": access_token
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            pages = data.get('data', [])
            
            print(f"  📊 Páginas encontradas: {len(pages)}")
            
            if pages:
                print("  📋 Lista de páginas:")
                for page in pages[:5]:  # Solo primeras 5
                    print(f"    📄 {page.get('name', 'Sin nombre')} - {page.get('category', 'N/A')}")
            else:
                print("  ℹ️ No se encontraron páginas administradas")
                
        else:
            print(f"  ❌ Error obteniendo páginas: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Error en test 3: {e}")
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN:")
    print("1. Si encontraste cuentas activas disponibles:")
    print("   → Usa una de esas cuentas actualizando META_ADS_ACCOUNT_ID en .env")
    print("2. Si no encontraste la cuenta 9703931559732773:")
    print("   → Verifica que tengas acceso o crea una nueva cuenta")
    print("3. Si no tienes cuentas disponibles:")
    print("   → Ve a https://business.facebook.com/ y crea una cuenta nueva")
    print("\n💡 Para crear nueva cuenta Meta Ads:")
    print("   1. Ve a https://business.facebook.com/")
    print("   2. Configuración → Cuentas de anuncios → Agregar")
    print("   3. Crear nueva cuenta de anuncios")
    print("   4. Configura método de pago")
    print("   5. Usa el nuevo ID en tu .env")
    
    return True

if __name__ == "__main__":
    success = check_available_accounts()
    sys.exit(0 if success else 1)