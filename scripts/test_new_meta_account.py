#!/usr/bin/env python3
"""
Test de conexión con la nueva cuenta de Meta Ads: 9703931559732773
Verifica permisos, información de la cuenta y capacidades disponibles.
"""
import os
import sys
import requests
import json
from pathlib import Path

# Cargar variables de entorno
sys.path.append(str(Path(__file__).parent.parent))
from config.app_settings import get_env

def test_new_meta_ads_account():
    """Probar conexión con la nueva cuenta Meta Ads."""
    print("🎯 Testing Nueva Cuenta Meta Ads: 9703931559732773")
    print("=" * 60)
    
    # Obtener credenciales
    access_token = get_env("META_ACCESS_TOKEN")
    account_id = "9703931559732773"  # Nueva cuenta
    
    if not access_token:
        print("❌ META_ACCESS_TOKEN no encontrado en .env")
        return False
    
    print(f"✅ Token encontrado: {access_token[:20]}...")
    print(f"🆔 Cuenta ID: {account_id}")
    
    # Test 1: Información de la cuenta
    print(f"\n🔍 Test 1: Información de la cuenta...")
    try:
        url = f"https://graph.facebook.com/v18.0/act_{account_id}"
        params = {
            "fields": "name,account_status,currency,timezone_name,amount_spent,balance,business",
            "access_token": access_token
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Cuenta encontrada: {data.get('name', 'Sin nombre')}")
            print(f"  📊 Estado: {data.get('account_status', 'Desconocido')}")
            print(f"  💰 Moneda: {data.get('currency', 'N/A')}")
            print(f"  🌍 Zona horaria: {data.get('timezone_name', 'N/A')}")
            print(f"  💸 Gastado: {data.get('amount_spent', 0)} {data.get('currency', '')}")
            print(f"  🏦 Balance: {data.get('balance', 0)} {data.get('currency', '')}")
            
            # Verificar si la cuenta está activa
            if data.get('account_status') == 1:
                print("  🟢 Estado: ACTIVA")
            else:
                print(f"  🟡 Estado: {data.get('account_status')} (revisar)")
                
        else:
            print(f"  ❌ Error obteniendo info de cuenta: {response.status_code}")
            print(f"  📝 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error en test 1: {e}")
        return False
    
    # Test 2: Permisos del token
    print(f"\n🔐 Test 2: Verificando permisos del token...")
    try:
        url = "https://graph.facebook.com/v18.0/me"
        params = {
            "fields": "name,permissions",
            "access_token": access_token
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  👤 Usuario: {data.get('name', 'Desconocido')}")
            
            # Verificar permisos específicos
            permissions = data.get('permissions', {}).get('data', [])
            required_perms = ['ads_management', 'ads_read', 'business_management']
            
            print("  📋 Permisos verificados:")
            for perm in required_perms:
                found = any(p.get('permission') == perm and p.get('status') == 'granted' 
                           for p in permissions)
                status = "✅" if found else "❌"
                print(f"    {status} {perm}")
                
        else:
            print(f"  ❌ Error verificando permisos: {response.status_code}")
            print(f"  📝 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"  ❌ Error en test 2: {e}")
    
    # Test 3: Campañas existentes
    print(f"\n📢 Test 3: Verificando campañas existentes...")
    try:
        url = f"https://graph.facebook.com/v18.0/act_{account_id}/campaigns"
        params = {
            "fields": "name,status,objective,created_time",
            "limit": 10,
            "access_token": access_token
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            campaigns = data.get('data', [])
            
            print(f"  📊 Campañas encontradas: {len(campaigns)}")
            
            if campaigns:
                print("  🎯 Últimas campañas:")
                for camp in campaigns[:5]:
                    status_icon = "🟢" if camp.get('status') == 'ACTIVE' else "⭕"
                    print(f"    {status_icon} {camp.get('name', 'Sin nombre')} - {camp.get('objective', 'N/A')}")
            else:
                print("  ℹ️ No se encontraron campañas (cuenta nueva)")
                
        else:
            print(f"  ❌ Error obteniendo campañas: {response.status_code}")
            print(f"  📝 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"  ❌ Error en test 3: {e}")
    
    # Test 4: Capacidades de la cuenta
    print(f"\n⚡ Test 4: Verificando capacidades de la cuenta...")
    try:
        url = f"https://graph.facebook.com/v18.0/act_{account_id}"
        params = {
            "fields": "capabilities,spend_cap,daily_spend_limit",
            "access_token": access_token
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            capabilities = data.get('capabilities', [])
            print(f"  🛠️ Capacidades disponibles: {len(capabilities)}")
            
            important_caps = ['CAN_CREATE_BRAND_AWARENESS', 'CAN_CREATE_REACH', 'CAN_CREATE_TRAFFIC', 'CAN_CREATE_CONVERSIONS']
            for cap in important_caps:
                has_cap = cap in capabilities
                status = "✅" if has_cap else "❌"
                print(f"    {status} {cap}")
            
            # Límites de gasto
            spend_cap = data.get('spend_cap')
            daily_limit = data.get('daily_spend_limit')
            
            if spend_cap:
                print(f"  💳 Límite total de gasto: {spend_cap}")
            if daily_limit:
                print(f"  📅 Límite diario de gasto: {daily_limit}")
                
        else:
            print(f"  ❌ Error obteniendo capacidades: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Error en test 4: {e}")
    
    # Test 5: Test de creación de campaña (DRY RUN)
    print(f"\n🧪 Test 5: Simulando creación de campaña...")
    try:
        # Solo verificar que podemos acceder al endpoint
        url = f"https://graph.facebook.com/v18.0/act_{account_id}/campaigns"
        params = {
            "access_token": access_token
        }
        
        # Solo hacer GET para verificar acceso
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            print("  ✅ Acceso al endpoint de campañas confirmado")
            print("  🎯 Sistema listo para crear campañas automáticas")
        else:
            print(f"  ❌ Sin acceso al endpoint de campañas: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Error en test 5: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Test de nueva cuenta Meta Ads completado!")
    print("💡 Próximos pasos:")
    print("   1. Verificar que todos los tests pasaron")
    print("   2. Configurar presupuesto inicial en Facebook Ads Manager")
    print("   3. Activar campañas automáticas del sistema Stakas")
    
    return True

if __name__ == "__main__":
    success = test_new_meta_ads_account()
    sys.exit(0 if success else 1)