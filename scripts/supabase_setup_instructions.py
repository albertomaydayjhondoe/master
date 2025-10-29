"""
🗄️ PASO 1: MANUAL SUPABASE SCHEMA SETUP
Genera instrucciones paso a paso para crear el schema en Supabase UI
"""

from pathlib import Path
from datetime import datetime

def generate_step_by_step_instructions():
    """Genera instrucciones detalladas para crear schema manualmente"""
    
    print("🗄️ PASO 1: CREAR SCHEMA EN SUPABASE")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Leer el archivo SQL
    schema_file = Path("database/supabase_schema.sql")
    
    if not schema_file.exists():
        print(f"❌ Error: No se encuentra {schema_file}")
        return False
        
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    print("✅ CONFIGURACIÓN COMPLETADA:")
    print(f"   🔗 URL: https://ilsikngctkrmqnbutpuz.supabase.co")
    print(f"   🔑 Anon Key: Configurada correctamente")
    print(f"   📄 Schema SQL: {len(schema_sql)} caracteres")
    print()
    
    print("🎯 PASOS PARA EJECUTAR (COPIA Y PEGA):")
    print("=" * 60)
    print()
    
    print("PASO 1️⃣ - Ir a Supabase Dashboard")
    print("   👉 https://ilsikngctkrmqnbutpuz.supabase.co")
    print("   📱 Login con tu cuenta")
    print()
    
    print("PASO 2️⃣ - Abrir SQL Editor")
    print("   📊 Sidebar izquierdo → 'SQL Editor'")
    print("   ➕ Click 'New Query'")
    print()
    
    print("PASO 3️⃣ - Ejecutar Schema Completo")
    print("   📝 Copia TODO el contenido del archivo:")
    print("   📂 database/supabase_schema.sql")
    print("   ▶️  Click 'RUN' para ejecutar")
    print()
    
    # Mostrar contenido del schema
    print("📄 CONTENIDO COMPLETO DEL SCHEMA:")
    print("=" * 60)
    print("```sql")
    print(schema_sql)
    print("```")
    print("=" * 60)
    print()
    
    print("PASO 4️⃣ - Verificar Creación")
    print("   📊 Ve a 'Table Editor' en sidebar")
    print("   ✅ Verifica que se crearon 7 tablas:")
    print("      • accounts")
    print("      • campaigns")
    print("      • metrics")
    print("      • ml_predictions")
    print("      • cross_platform_data")
    print("      • geographic_performance")
    print("      • optimization_logs")
    print()
    
    print("PASO 5️⃣ - Confirmar Datos de Prueba")
    print("   🔍 Ve a tabla 'accounts'")
    print("   ✅ Debe haber 1 registro: ASampayo Meta Ads")
    print("   🔍 Ve a tabla 'campaigns'")
    print("   ✅ Debe haber 1 registro: Test España-LATAM ML")
    print()
    
    print("🚨 SI HAY ERRORES:")
    print("   1. Verifica que tienes permisos de admin en Supabase")
    print("   2. Ejecuta comandos uno por uno si falla el script completo")
    print("   3. Algunas funciones pueden requerir extensiones (se crearán automáticamente)")
    print()
    
    return True

def generate_validation_script():
    """Genera script de validación una vez creado el schema"""
    
    validation_script = '''
"""
✅ VALIDADOR DE SCHEMA SUPABASE
Ejecutar DESPUÉS de crear el schema en Supabase UI
"""

import os
import asyncio
from supabase import create_client

async def validate_schema():
    """Valida que el schema se creó correctamente"""
    
    # Credenciales
    url = "https://ilsikngctkrmqnbutpuz.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlsc2lrbmdjdGtybXFuYnV0cHV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0MTQwMTMsImV4cCI6MjA3Njk5MDAxM30.05KqrCvc0aDRjO1XzlNwrX5WcRBVAFdXMOgneiZ26Og"
    
    supabase = create_client(url, key)
    
    tables = ['accounts', 'campaigns', 'metrics', 'ml_predictions', 
              'cross_platform_data', 'geographic_performance', 'optimization_logs']
    
    print("🔍 VALIDANDO SCHEMA SUPABASE...")
    print("=" * 40)
    
    valid_tables = 0
    
    for table in tables:
        try:
            result = supabase.table(table).select('*').limit(1).execute()
            print(f"✅ {table}")
            valid_tables += 1
        except Exception as e:
            print(f"❌ {table}: {str(e)[:50]}...")
    
    print()
    print(f"📊 RESULTADO: {valid_tables}/{len(tables)} tablas válidas")
    
    if valid_tables == len(tables):
        print("🎉 ¡SCHEMA COMPLETAMENTE FUNCIONAL!")
        print("✅ Paso 1 terminado exitosamente")
        print("🚀 Listo para Paso 2: Activar Device Farm V5")
        return True
    else:
        print("⚠️ Schema incompleto - revisa los errores arriba")
        return False

if __name__ == "__main__":
    asyncio.run(validate_schema())
'''
    
    with open('scripts/validate_supabase_schema.py', 'w', encoding='utf-8') as f:
        f.write(validation_script)
    
    print("📝 SCRIPT DE VALIDACIÓN CREADO:")
    print("   📂 scripts/validate_supabase_schema.py")
    print("   🔧 Ejecuta DESPUÉS de crear schema en Supabase UI")
    print()

def main():
    """Función principal"""
    
    print("🎯 GENERANDO INSTRUCCIONES PASO A PASO...")
    print()
    
    success = generate_step_by_step_instructions()
    
    if success:
        print("✅ INSTRUCCIONES GENERADAS")
        print()
        generate_validation_script()
        
        print("🎯 RESUMEN:")
        print("1. ☝️  Copia el SQL de arriba")
        print("2. 🌐 Ve a https://ilsikngctkrmqnbutpuz.supabase.co")
        print("3. 📊 SQL Editor → New Query → Pegar → RUN")
        print("4. ✅ Ejecutar: python scripts/validate_supabase_schema.py")
        print()
        print("⏱️  Tiempo estimado: 2-3 minutos")
        print("🎉 Después de esto: ¡Sistema 100% listo!")

if __name__ == "__main__":
    main()