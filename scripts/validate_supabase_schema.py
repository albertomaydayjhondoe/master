
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
