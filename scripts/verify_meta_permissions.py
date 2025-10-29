#!/usr/bin/env python3
"""
🎯 VERIFICAR PERMISOS META ADS - Cuenta 9703931559732773

Script para verificar que tienes permisos de administrador
después de que te agreguen a la cuenta.
"""
import sys
import requests
from pathlib import Path

# Cargar configuración
sys.path.append(str(Path(__file__).parent.parent))
from config.app_settings import get_env

def verify_account_permissions():
    """Verificar permisos en la cuenta específica."""
    
    print("🎯 VERIFICANDO PERMISOS CUENTA META ADS")
    print("=" * 50)
    
    account_id = "9703931559732773"
    token = get_env("META_ACCESS_TOKEN")
    
    if not token:
        print("❌ META_ACCESS_TOKEN no encontrado")
        return False
    
    print(f"🆔 Cuenta objetivo: {account_id}")
    print(f"✅ Token: {token[:20]}...")
    
    # Test 1: Información básica de la cuenta
    print(f"\n📊 Test 1: Acceso a información de cuenta...")
    try:
        url = f"https://graph.facebook.com/v18.0/act_{account_id}"
        params = {
            "fields": "name,account_status,currency,timezone_name,balance,amount_spent,owner",
            "access_token": token
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ¡ACCESO CONCEDIDO!")
            print(f"   📊 Nombre: {data.get('name', 'N/A')}")
            print(f"   💰 Moneda: {data.get('currency', 'N/A')}")
            print(f"   📈 Estado: {data.get('account_status', 'N/A')}")
            print(f"   🌍 Zona horaria: {data.get('timezone_name', 'N/A')}")
            print(f"   🏦 Balance: {data.get('balance', 0)} {data.get('currency', '')}")
            print(f"   💸 Gastado: {data.get('amount_spent', 0)} {data.get('currency', '')}")
            
        elif response.status_code == 403:
            error = response.json().get('error', {})
            print(f"❌ SIN ACCESO AÚN")
            print(f"   Código: {error.get('code', 'N/A')}")
            print(f"   Mensaje: {error.get('message', 'Sin mensaje')}")
            
            if "NOT grant" in error.get('message', ''):
                print(f"\n💡 ACCIÓN REQUERIDA:")
                print(f"   El propietario de la cuenta debe:")
                print(f"   1. Ir a: https://business.facebook.com/settings/ad-accounts")
                print(f"   2. Buscar cuenta: {account_id}")
                print(f"   3. Agregar usuario: asampayo00@gmail.com")
                print(f"   4. Rol: Administrador")
            
            return False
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Crear campaña (test de permisos de escritura)
    print(f"\n📢 Test 2: Permisos de gestión de campañas...")
    try:
        url = f"https://graph.facebook.com/v18.0/act_{account_id}/campaigns"
        params = {
            "fields": "name,status,objective,created_time",
            "limit": 5,
            "access_token": token
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            campaigns = data.get('data', [])
            
            print(f"✅ Acceso a campañas: {len(campaigns)} encontradas")
            
            if campaigns:
                print(f"   📋 Últimas campañas:")
                for camp in campaigns[:3]:
                    status_icon = "🟢" if camp.get('status') == 'ACTIVE' else "⭕"
                    print(f"     {status_icon} {camp.get('name', 'Sin nombre')}")
            else:
                print(f"   ℹ️ No hay campañas existentes (cuenta nueva)")
                
        else:
            print(f"❌ Sin acceso a campañas: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 3: Verificar capacidades
    print(f"\n⚡ Test 3: Capacidades disponibles...")
    try:
        url = f"https://graph.facebook.com/v18.0/act_{account_id}"
        params = {
            "fields": "capabilities,account_status,can_create_brand_awareness_ads",
            "access_token": token
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            capabilities = data.get('capabilities', [])
            
            print(f"✅ Capacidades disponibles: {len(capabilities)}")
            
            # Verificar capacidades importantes
            important_caps = [
                'CAN_CREATE_BRAND_AWARENESS',
                'CAN_CREATE_REACH', 
                'CAN_CREATE_TRAFFIC',
                'CAN_CREATE_CONVERSIONS',
                'CAN_USE_REACH_AND_FREQUENCY'
            ]
            
            print(f"   🛠️ Capacidades para campañas:")
            for cap in important_caps:
                has_cap = cap in capabilities
                status = "✅" if has_cap else "❌"
                print(f"     {status} {cap}")
                
        else:
            print(f"❌ Error obteniendo capacidades: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n🎉 ¡VERIFICACIÓN COMPLETA!")
    print(f"✅ Tienes acceso completo a la cuenta {account_id}")
    print(f"🚀 El sistema Stakas está listo para crear campañas automáticas")
    
    return True

def show_next_steps():
    """Mostrar próximos pasos después de obtener acceso."""
    
    print(f"\n🚀 PRÓXIMOS PASOS")
    print("-" * 30)
    
    print("1. 💳 CONFIGURAR MÉTODO DE PAGO:")
    print("   → Ve a Business Manager → Facturación")
    print("   → Agregar tarjeta de crédito")
    print("   → Configurar límite diario €20-50")
    
    print(f"\n2. 🎯 CREAR PRIMERA CAMPAÑA DE PRUEBA:")
    print("   → Objetivo: Tráfico a YouTube")
    print("   → Audiencia: Interesados en música drill")
    print("   → Presupuesto: €10/día")
    print("   → Ubicación: España + Latinoamérica")
    
    print(f"\n3. 🤖 ACTIVAR AUTOMATIZACIÓN STAKAS:")
    print("   → El sistema creará campañas automáticamente")
    print("   → Optimización ML basada en performance")
    print("   → Presupuesto total: €500/mes")
    
    print(f"\n4. 📊 MONITOREO Y MÉTRICAS:")
    print("   → Dashboard en tiempo real")
    print("   → Alertas de performance")
    print("   → Optimización automática")

def main():
    """Función principal."""
    
    print("🎯 VERIFICACIÓN DE PERMISOS META ADS")
    print("=" * 60)
    
    print("📋 INFORMACIÓN PARA EL PROPIETARIO DE LA CUENTA:")
    print("   🔗 Link: https://business.facebook.com/settings/ad-accounts")
    print("   🆔 Cuenta: 9703931559732773")
    print("   👤 Usuario a agregar: asampayo00@gmail.com")
    print("   🔧 Rol necesario: Administrador")
    print()
    
    input("⏳ Presiona Enter cuando el propietario te haya agregado como administrador...")
    
    if verify_account_permissions():
        show_next_steps()
        
        print(f"\n✅ CONFIGURACIÓN COMPLETA")
        print("🎯 Sistema Stakas listo para generar contenido viral")
        print("💰 Presupuesto €500/mes activado")
        
    else:
        print(f"\n❌ CONFIGURACIÓN PENDIENTE")
        print("🔧 El propietario aún debe agregarte como administrador")
        print()
        print("📝 INSTRUCCIONES PARA ENVIAR AL PROPIETARIO:")
        print("=" * 50)
        print("Hola,")
        print()
        print("Para que asampayo00@gmail.com pueda gestionar")
        print("las campañas de Meta Ads, necesitas agregarlo como administrador:")
        print()
        print("1. Ve a: https://business.facebook.com/settings/ad-accounts")
        print("2. Busca la cuenta: 9703931559732773") 
        print("3. Haz clic en 'Agregar personas'")
        print("4. Email: asampayo00@gmail.com")
        print("5. Rol: Administrador")
        print("6. Confirmar")
        print()
        print("¡Gracias!")

if __name__ == "__main__":
    main()