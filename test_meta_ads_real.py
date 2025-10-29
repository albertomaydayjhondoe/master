#!/usr/bin/env python3
"""
🔍 META ADS PRODUCTION TESTER - VERIFICACIÓN REAL
Test específico para verificar si Meta Ads funciona con credenciales reales
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import requests

def load_production_env():
    """Cargar específicamente el entorno de producción"""
    prod_env = Path("config/production/.env")
    if prod_env.exists():
        load_dotenv(prod_env)
        print(f"✅ Cargado entorno de producción desde {prod_env}")
        return True
    else:
        print(f"❌ No se encontró {prod_env}")
        return False

def test_meta_ads_connection():
    """Test real de conexión a Meta Ads API"""
    
    # Cargar entorno de producción
    if not load_production_env():
        return False
    
    # Obtener credenciales
    access_token = os.getenv('META_ACCESS_TOKEN')
    account_id = os.getenv('META_ADS_ACCOUNT_ID') 
    
    print(f"🔑 Access Token: {'✅ Configurado' if access_token and access_token != 'your-access-token' else '❌ No configurado'}")
    print(f"🏦 Account ID: {account_id if account_id else '❌ No configurado'}")
    
    if not access_token or access_token.startswith('your-'):
        print("❌ Meta Ads no tiene credenciales reales")
        return False
    
    # Test real de la API
    try:
        print("\n🚀 Probando conexión real a Meta Ads API...")
        
        # Test 1: Validar token
        token_url = f"https://graph.facebook.com/v18.0/me"
        params = {"access_token": access_token}
        
        response = requests.get(token_url, params=params, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Token válido - Usuario: {user_data.get('name', 'N/A')}")
        else:
            print(f"❌ Token inválido - Status: {response.status_code}")
            print(f"Error: {response.text}")
            return False
        
        # Test 2: Verificar cuenta de ads
        if account_id:
            account_url = f"https://graph.facebook.com/v18.0/{account_id}"
            response = requests.get(account_url, params=params, timeout=10)
            
            if response.status_code == 200:
                account_data = response.json()
                print(f"✅ Cuenta de ads válida - Nombre: {account_data.get('name', 'N/A')}")
                print(f"📊 Balance: {account_data.get('balance', 'N/A')}")
                return True
            else:
                print(f"❌ Cuenta de ads inválida - Status: {response.status_code}")
                print(f"Error: {response.text}")
                return False
        
    except Exception as e:
        print(f"❌ Error conectando a Meta Ads: {e}")
        return False

def main():
    """Función principal"""
    print("🎯 META ADS REAL CONNECTION TEST - STAKAS MVP")
    print("=" * 60)
    
    success = test_meta_ads_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ¡META ADS ESTÁ FUNCIONANDO CON CREDENCIALES REALES!")
        print("💰 Listo para campañas de €500/mes")
        print("🎯 Canal: UCgohgqLVu1QPdfa64Vkrgeg")
    else:
        print("❌ Meta Ads no está configurado correctamente")
        print("🔧 Revisar credenciales en config/production/.env")

if __name__ == "__main__":
    main()