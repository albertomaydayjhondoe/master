"""
🔑 OPCIÓN 1: OBTENER SERVICE ROLE KEY - PASOS DETALLADOS
Guía paso a paso para conseguir permisos completos en Supabase
"""

def detailed_service_role_steps():
    """Pasos detallados para obtener Service Role Key"""
    
    print("🔑 OPCIÓN 1: SERVICE ROLE KEY - PASOS DETALLADOS")
    print("=" * 60)
    print("⏱️  Tiempo estimado: 2-3 minutos")
    print("🎯 Objetivo: Obtener clave con permisos ADMIN para crear schema")
    print()
    
    print("📋 PASOS EXACTOS:")
    print("=" * 40)
    print()
    
    print("🌐 PASO 1: ABRIR SUPABASE DASHBOARD")
    print("   👉 Ve a: https://ilsikngctkrmqnbutpuz.supabase.co")
    print("   🔐 Login con tu cuenta (si no estás ya logueado)")
    print("   ✅ Confirma que estás en el proyecto correcto")
    print()
    
    print("⚙️ PASO 2: ACCEDER A CONFIGURACIÓN")
    print("   📍 En el sidebar izquierdo, ve hasta abajo")
    print("   🔧 Click en 'Settings' (icono de engranaje)")
    print("   📊 En el menú de Settings, click 'API'")
    print("   ✅ Verás la página 'Project API keys'")
    print()
    
    print("🔍 PASO 3: IDENTIFICAR LAS CLAVES")
    print("   👀 Verás dos secciones:")
    print("      🔓 'anon public' - Ya la tenemos")
    print("      🔐 'service_role' - La que necesitamos")
    print("   📝 La service_role estará oculta con asteriscos")
    print()
    
    print("👁️ PASO 4: REVELAR SERVICE ROLE KEY")
    print("   🖱️  En la sección 'service_role':")
    print("   👁️  Click en el botón 'Reveal' o el icono del ojo")
    print("   📋 Se mostrará la clave completa (muy larga)")
    print("   ⚠️  IMPORTANTE: Comienza con 'eyJ' como la anon key")
    print("   📱 Copia TODA la clave (Ctrl+A, Ctrl+C)")
    print()
    
    print("📝 PASO 5: ACTUALIZAR CONFIGURACIÓN LOCAL")
    print("   📂 Abre: config/production/.env")
    print("   🔍 Busca la línea: SUPABASE_SERVICE_KEY=...")
    print("   🔄 Reemplaza el valor con la nueva clave")
    print("   💾 Guarda el archivo")
    print()
    
    print("✅ PASO 6: VERIFICAR ACTUALIZACIÓN")
    print("   🖥️  Ejecuta en terminal:")
    print("      python scripts/test_supabase_connection.py")
    print("   ✅ Debe mostrar 'Cliente Supabase creado'")
    print()
    
    print("🚀 PASO 7: CREAR SCHEMA AUTOMÁTICO")
    print("   🖥️  Ejecuta:")
    print("      python scripts/execute_supabase_schema.py")
    print("   ✅ Esta vez debe funcionar completamente")
    print("   📊 Creará las 7 tablas automáticamente")
    print()
    
    print("🔍 PASO 8: VALIDAR CREACIÓN")
    print("   🖥️  Ejecuta:")
    print("      python scripts/validate_supabase_schema.py")
    print("   ✅ Debe mostrar '7/7 tablas válidas'")
    print("   🎉 ¡PASO 1 COMPLETADO!")
    print()
    
    print("⚠️ NOTAS IMPORTANTES:")
    print("=" * 30)
    print("🔒 Service Role Key tiene permisos TOTALES")
    print("🔐 No la compartas nunca públicamente")  
    print("💾 Mantenla solo en archivos .env locales")
    print("🚫 NO la subas a GitHub/repositorios públicos")
    print("✅ Es segura para uso en servidor/local")
    print()
    
    print("🆘 SI TIENES PROBLEMAS:")
    print("=" * 25)
    print("❌ No encuentras Settings:")
    print("   → Scroll down en sidebar izquierdo")
    print("❌ No ves 'Reveal' button:")
    print("   → Verifica que eres admin del proyecto")
    print("❌ Clave no funciona:")
    print("   → Copia de nuevo, incluye TODO el token")
    print("❌ Error de permisos:")
    print("   → Verifica que pegaste en SUPABASE_SERVICE_KEY")
    print()
    
    return True

def generate_update_script():
    """Genera script para actualizar la service key fácilmente"""
    
    update_script = '''
"""
🔄 ACTUALIZADOR DE SERVICE KEY
Script para actualizar service_role key en .env
"""

import os
from pathlib import Path

def update_service_key():
    """Actualiza service key en config/production/.env"""
    
    print("🔑 ACTUALIZADOR DE SUPABASE SERVICE KEY")
    print("=" * 45)
    
    # Solicitar nueva clave
    print("📋 Pega tu Service Role Key de Supabase:")
    print("   (La clave larga que empieza con 'eyJ...')")
    new_key = input("🔐 Service Key: ").strip()
    
    if not new_key.startswith('eyJ'):
        print("❌ Error: La clave debe empezar con 'eyJ'")
        return False
        
    # Actualizar archivo .env
    env_file = Path("config/production/.env")
    
    if not env_file.exists():
        print("❌ Error: No se encuentra config/production/.env")
        return False
        
    # Leer contenido
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar y reemplazar
    lines = content.split('\\n')
    updated = False
    
    for i, line in enumerate(lines):
        if line.startswith('SUPABASE_SERVICE_KEY='):
            lines[i] = f'SUPABASE_SERVICE_KEY={new_key}'
            updated = True
            break
    
    if not updated:
        # Agregar si no existe
        lines.append(f'SUPABASE_SERVICE_KEY={new_key}')
    
    # Guardar archivo
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write('\\n'.join(lines))
    
    print("✅ Service Key actualizada correctamente")
    print("📂 Archivo: config/production/.env")
    print()
    print("🎯 PRÓXIMO PASO:")
    print("   python scripts/execute_supabase_schema.py")
    
    return True

if __name__ == "__main__":
    update_service_key()
'''
    
    with open('scripts/update_service_key.py', 'w', encoding='utf-8') as f:
        f.write(update_script)
    
    print("🔄 SCRIPT HELPER CREADO:")
    print("   📂 scripts/update_service_key.py")
    print("   🎯 Te ayudará a actualizar la clave fácilmente")
    print()

def main():
    """Función principal"""
    detailed_service_role_steps()
    generate_update_script()
    
    print("🎯 RESUMEN OPCIÓN 1:")
    print("=" * 20)
    print("1. Ve a Supabase → Settings → API")
    print("2. Reveal service_role key")  
    print("3. Copia la clave completa")
    print("4. Actualiza config/production/.env")
    print("5. Ejecuta: python scripts/execute_supabase_schema.py")
    print("6. Valida: python scripts/validate_supabase_schema.py")
    print()
    print("⏱️  Total: 2-3 minutos")
    print("🎉 Resultado: Sistema 100% funcional")

if __name__ == "__main__":
    main()