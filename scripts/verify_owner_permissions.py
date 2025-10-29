#!/usr/bin/env python3
"""
Verificar permisos exactos del token actual y generar instrucciones para token con permisos owner
"""

import os
import requests

def load_env_file():
    """Carga las variables de entorno del archivo .env"""
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'secrets', '.env'),
    ]
    
    env_vars = {}
    for env_path in possible_paths:
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip()
            break
    return env_vars

def verify_current_permissions():
    """Verifica los permisos exactos del token actual"""
    print("🔍 VERIFICACIÓN DE PERMISOS DEL TOKEN OWNER")
    print("="*60)
    
    env_vars = load_env_file()
    token = env_vars.get('META_ACCESS_TOKEN')
    
    if not token:
        print("❌ No se encontró token")
        return False
    
    try:
        # Verificar usuario
        print("👤 Usuario del token:")
        me_response = requests.get(
            "https://graph.facebook.com/v18.0/me",
            params={
                'access_token': token,
                'fields': 'id,name,email'
            }
        )
        
        if me_response.status_code == 200:
            user_info = me_response.json()
            print(f"   ✅ Nombre: {user_info.get('name', 'N/A')}")
            print(f"   ✅ ID: {user_info.get('id', 'N/A')}")
            print(f"   ✅ Email: {user_info.get('email', 'No disponible')}")
        
        # Verificar permisos específicos
        print("\n🔑 Permisos del token:")
        perms_response = requests.get(
            f"https://graph.facebook.com/v18.0/me/permissions",
            params={'access_token': token}
        )
        
        if perms_response.status_code == 200:
            permissions = perms_response.json()
            granted_perms = []
            declined_perms = []
            
            for perm in permissions.get('data', []):
                if perm.get('status') == 'granted':
                    granted_perms.append(perm['permission'])
                else:
                    declined_perms.append(perm['permission'])
            
            print("   ✅ Permisos CONCEDIDOS:")
            for perm in granted_perms:
                print(f"      🟢 {perm}")
            
            if declined_perms:
                print("   ❌ Permisos DENEGADOS:")
                for perm in declined_perms:
                    print(f"      🔴 {perm}")
            
            # Verificar permisos críticos para ads
            critical_perms = ['ads_management', 'ads_read', 'business_management']
            missing_perms = [p for p in critical_perms if p not in granted_perms]
            
            if missing_perms:
                print(f"\n🚨 PERMISOS FALTANTES PARA ADS:")
                for perm in missing_perms:
                    print(f"      ❌ {perm}")
                return False
            else:
                print(f"\n✅ TODOS LOS PERMISOS DE ADS PRESENTES")
                return True
        
    except Exception as e:
        print(f"❌ Error verificando permisos: {e}")
        return False

def show_owner_instructions():
    """Muestra instrucciones específicas para el owner"""
    print("\n" + "="*60)
    print("🎯 INSTRUCCIONES PARA TOKEN DE OWNER")
    print("="*60)
    
    print("\n📋 SITUACIÓN:")
    print("   👤 Angel Garcia es OWNER de cuenta 9703931559732773")
    print("   🔑 Necesita token con permisos completos de ads")
    print("   ✅ Como owner, puede generar token sin restricciones")
    
    print("\n🔧 PASOS PARA GENERAR TOKEN CORRECTO:")
    print("   1. 🌐 Ir a: https://developers.facebook.com/tools/explorer/")
    print("   2. 👤 Loguearse como Angel Garcia")
    print("   3. 📱 Seleccionar aplicación de Meta Ads")
    print("   4. 🔑 Agregar permisos:")
    print("      ✅ ads_management")
    print("      ✅ ads_read")
    print("      ✅ business_management")
    print("   5. 🎯 Generar Access Token")
    print("   6. 📋 Copiar token completo")
    
    print("\n💡 VENTAJA DEL OWNER:")
    print("   🏆 Acceso total a todas las funciones")
    print("   🚀 Sin restricciones de permisos")
    print("   💰 Control completo para €500/mes automation")

def main():
    """Función principal"""
    has_correct_permissions = verify_current_permissions()
    
    if has_correct_permissions:
        print("\n🎉 ¡TOKEN PERFECTO!")
        print("   El token actual ya tiene todos los permisos necesarios")
        print("   Probando acceso directo a cuenta...")
        
        # Probar acceso directo
        env_vars = load_env_file()
        token = env_vars.get('META_ACCESS_TOKEN')
        
        try:
            response = requests.get(
                f"https://graph.facebook.com/v18.0/act_9703931559732773",
                params={
                    'access_token': token,
                    'fields': 'name,account_status,currency'
                }
            )
            
            if response.status_code == 200:
                account_info = response.json()
                print(f"   ✅ Acceso confirmado a cuenta")
                print(f"   ✅ Nombre: {account_info.get('name', 'N/A')}")
                print(f"   ✅ Estado: {account_info.get('account_status', 'N/A')}")
                print("\n🚀 SISTEMA 100% LISTO PARA PRODUCCIÓN!")
            else:
                print(f"   ❌ Sin acceso directo: {response.status_code}")
                show_owner_instructions()
        except Exception as e:
            print(f"   ❌ Error probando acceso: {e}")
            show_owner_instructions()
    else:
        show_owner_instructions()

if __name__ == "__main__":
    main()