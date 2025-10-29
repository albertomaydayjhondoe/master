#!/usr/bin/env python3
"""
🔍 META ADS ACCOUNT FINDER
Encuentra tus cuentas de Meta Ads disponibles con el token actual
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import requests

def load_production_env():
    """Cargar entorno de producción"""
    prod_env = Path("config/production/.env")
    if prod_env.exists():
        load_dotenv(prod_env)
        return True
    return False

def find_ad_accounts():
    """Buscar cuentas de ads disponibles"""
    
    if not load_production_env():
        return
    
    access_token = os.getenv('META_ACCESS_TOKEN')
    
    try:
        print("🔍 Buscando cuentas de Meta Ads disponibles...")
        
        # Obtener cuentas de ads del usuario
        url = "https://graph.facebook.com/v18.0/me/adaccounts"
        params = {
            "access_token": access_token,
            "fields": "id,name,account_status,balance,currency,timezone_name"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            accounts = data.get('data', [])
            
            if accounts:
                print(f"✅ Encontradas {len(accounts)} cuenta(s) de Meta Ads:")
                print("-" * 80)
                
                for i, account in enumerate(accounts, 1):
                    print(f"🏦 Cuenta #{i}:")
                    print(f"   ID: {account.get('id', 'N/A')}")
                    print(f"   Nombre: {account.get('name', 'N/A')}")
                    print(f"   Status: {account.get('account_status', 'N/A')}")
                    print(f"   Balance: {account.get('balance', 'N/A')} {account.get('currency', '')}")
                    print(f"   Timezone: {account.get('timezone_name', 'N/A')}")
                    print("-" * 40)
                
                # Mostrar el primer ID para usar
                first_id = accounts[0].get('id')
                print(f"💡 Usar este ID en .env:")
                print(f"META_ADS_ACCOUNT_ID={first_id}")
                
            else:
                print("❌ No se encontraron cuentas de Meta Ads")
                print("💡 Necesitas crear una cuenta de Meta Ads primero en business.facebook.com")
        else:
            print(f"❌ Error buscando cuentas - Status: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🎯 META ADS ACCOUNT FINDER")
    print("=" * 50)
    find_ad_accounts()