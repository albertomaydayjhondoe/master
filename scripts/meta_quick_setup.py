#!/usr/bin/env python3
"""
🚀 SOLUCIÓN RÁPIDA META ADS - Crear cuenta propia

Script para crear y configurar tu propia cuenta Meta Ads 
en menos de 10 minutos. Control total y sin problemas de permisos.
"""
import webbrowser
import sys
from pathlib import Path

def quick_setup_guide():
    """Guía rápida para crear cuenta Meta Ads propia."""
    
    print("🚀 CREAR TU PROPIA CUENTA META ADS")
    print("=" * 50)
    print("⏱️ Tiempo estimado: 5-10 minutos")
    print("💰 Presupuesto sugerido inicial: €50-100")
    print()
    
    print("📋 PASO A PASO:")
    print()
    
    print("1. 🌐 ABRIR BUSINESS MANAGER")
    print("   → Ir a https://business.facebook.com")
    print("   → Iniciar sesión con tu cuenta Facebook")
    print()
    
    print("2. ➕ CREAR CUENTA DE ANUNCIOS") 
    print("   → Configuración (menú izquierdo)")
    print("   → Cuentas de anuncios")
    print("   → Agregar → Crear nueva cuenta de anuncios")
    print()
    
    print("3. 📝 CONFIGURAR INFORMACIÓN")
    print("   → Nombre: 'Stakas Music Viral'")
    print("   → País/región: Tu país")
    print("   → Zona horaria: Tu zona horaria")
    print("   → Moneda: EUR (Euro)")
    print()
    
    print("4. 💳 AGREGAR MÉTODO DE PAGO")
    print("   → Tarjeta de crédito/débito")
    print("   → PayPal")
    print("   → Transferencia bancaria")
    print()
    
    print("5. 🆔 COPIAR ACCOUNT ID")
    print("   → En Configuración → Cuentas de anuncios")
    print("   → Ver el ID de tu cuenta nueva")
    print("   → Copiar SOLO los números (sin 'act_')")
    print()
    
    print("6. 🔧 ACTUALIZAR CONFIGURACIÓN")
    print("   → Actualizar META_ADS_ACCOUNT_ID en .env")
    print("   → Probar conexión")
    print()
    
    # Preguntar si continuar
    choice = input("🚀 ¿Empezar ahora? (y/n): ").strip().lower()
    
    if choice == 'y':
        print("\n✅ Abriendo Business Manager...")
        webbrowser.open("https://business.facebook.com/settings/ad-accounts")
        
        print("\n⏳ Completa la creación de cuenta y regresa aquí...")
        new_account_id = input("📋 Pega aquí tu nuevo Account ID: ").strip()
        
        if new_account_id:
            update_account_id(new_account_id)
        
    else:
        print("\n📚 Alternativas:")
        print("A. Pedir acceso a la cuenta 9703931559732773")
        print("B. Usar Graph API Explorer para verificar cuentas disponibles")
        print("C. Configurar una cuenta de prueba temporal")

def update_account_id(new_id):
    """Actualizar Account ID en .env."""
    
    print(f"\n🔧 Actualizando configuración con ID: {new_id}")
    
    env_path = Path(__file__).parent.parent / ".env"
    
    try:
        # Leer archivo
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar Account ID
        import re
        pattern = r'META_ADS_ACCOUNT_ID=.*'
        replacement = f'META_ADS_ACCOUNT_ID={new_id}'
        
        if re.search(pattern, content):
            new_content = re.sub(pattern, replacement, content)
        else:
            new_content = content + f'\nMETA_ADS_ACCOUNT_ID={new_id}\n'
        
        # Guardar
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Account ID actualizado en .env")
        
        # Test inmediato
        test_new_account(new_id)
        
    except Exception as e:
        print(f"❌ Error actualizando .env: {e}")

def test_new_account(account_id):
    """Probar nueva cuenta inmediatamente."""
    
    print(f"\n🧪 Probando nueva cuenta: {account_id}")
    
    # Importar configuración
    sys.path.append(str(Path(__file__).parent.parent))
    from config.app_settings import get_env
    import requests
    
    token = get_env("META_ACCESS_TOKEN")
    
    try:
        url = f"https://graph.facebook.com/v18.0/act_{account_id}"
        params = {
            "fields": "name,account_status,currency,balance",
            "access_token": token
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"🎉 ¡ÉXITO! Cuenta configurada correctamente:")
            print(f"   📊 Nombre: {data.get('name', 'N/A')}")
            print(f"   💰 Moneda: {data.get('currency', 'N/A')}")
            print(f"   📈 Estado: {data.get('account_status', 'N/A')}")
            print(f"   🏦 Balance: {data.get('balance', 0)} {data.get('currency', '')}")
            
            print(f"\n🎯 Sistema Stakas listo para:")
            print("   ✅ Crear campañas automáticamente")
            print("   ✅ Promocionar contenido viral")
            print("   ✅ Gestionar presupuesto €500/mes")
            
            # Próximos pasos
            print(f"\n🚀 PRÓXIMOS PASOS:")
            print("1. Agregar presupuesto inicial (€50-100)")
            print("2. Crear primera campaña de prueba")
            print("3. Configurar pixel de conversión")
            print("4. Iniciar automatización Stakas")
            
        else:
            print(f"❌ Error verificando cuenta: {response.text}")
            print(f"\n💡 Posibles causas:")
            print("   • La cuenta aún se está creando (espera 5 minutos)")
            print("   • ID incorrecto (verifica que sea solo números)")
            print("   • Necesitas agregar método de pago primero")
            
    except Exception as e:
        print(f"❌ Error probando cuenta: {e}")

def show_account_alternatives():
    """Mostrar alternativas si no quiere crear cuenta nueva."""
    
    print("\n📚 ALTERNATIVAS A CREAR CUENTA NUEVA")
    print("=" * 50)
    
    print("🔑 OPCIÓN A: Solicitar acceso a 9703931559732773")
    print("   1. Contactar al propietario de la cuenta")
    print("   2. Pedir que te agregue como administrador")
    print("   3. Usar Graph API Explorer para verificar acceso")
    print()
    
    print("🧪 OPCIÓN B: Cuenta de prueba temporal")
    print("   1. Crear cuenta de prueba con presupuesto bajo")
    print("   2. Probar sistema Stakas")
    print("   3. Migrar a cuenta definitiva después")
    print()
    
    print("🔍 OPCIÓN C: Verificar cuentas existentes")
    print("   1. Usar Graph API Explorer")
    print("   2. Revisar qué cuentas ya tienes acceso")
    print("   3. Usar una cuenta existente")
    print()
    
    choice = input("¿Qué opción prefieres? (A/B/C): ").strip().upper()
    
    if choice == 'A':
        print("\n📞 Para solicitar acceso:")
        print("1. Contacta al propietario de 9703931559732773")
        print("1. Comparte tu Instagram Business ID: 17841470265116861")
        print("2. Comparte tu Facebook User ID: asampayo00@gmail.com")
        print("3. Crea una aplicación en: https://developers.facebook.com/apps/")
        print("4. Solicita permisos: ads_management, business_management")
        print("3. Pide permisos de 'Administrador'")
        
    elif choice == 'B':
        quick_setup_guide()  # Crear cuenta temporal
        
    elif choice == 'C':
        print("\n🔍 Verificando cuentas disponibles...")
        webbrowser.open("https://developers.facebook.com/tools/explorer/")
        print("✅ Abriendo Graph API Explorer")
        print("📝 Ejecuta: GET /me/adaccounts para ver tus cuentas")

def main():
    """Función principal."""
    print("🎯 SOLUCIÓN META ADS - CONFIGURACIÓN RÁPIDA")
    print("=" * 55)
    
    print("📊 SITUACIÓN ACTUAL:")
    print("   ✅ Token válido (asampayo00@gmail.com)")
    print("   ❌ Sin acceso a cuenta 9703931559732773") 
    print("   🔧 Necesita solución rápida")
    print()
    
    print("💡 RECOMENDACIÓN: Crear tu propia cuenta")
    print("   ⚡ Más rápido (5-10 minutos)")
    print("   🔒 Control total")
    print("   💰 Presupuesto propio")
    print("   🚀 Listo para producción")
    print()
    
    choice = input("¿Crear cuenta nueva? (y/n/help): ").strip().lower()
    
    if choice == 'y':
        quick_setup_guide()
    elif choice == 'help':
        show_account_alternatives()
    else:
        print("\n📚 Otras opciones disponibles:")
        print("   python scripts/meta_ads_setup_complete.py")
        print("   → Configurador completo con todas las opciones")

if __name__ == "__main__":
    main()