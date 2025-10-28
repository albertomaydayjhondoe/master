"""
🔧 CONFIGURADOR SUPABASE DIRECTO
Actualiza .env con credenciales de Supabase
"""

import os
from pathlib import Path

def update_supabase_config():
    """Actualiza configuración de Supabase en .env"""
    
    print("🔧 CONFIGURADOR SUPABASE - Sistema Meta ML")
    print("=" * 50)
    print("✅ CONFIGURACIÓN AUTOMÁTICA CON CREDENCIALES PROPORCIONADAS")
    print()
    
    # Credenciales ya proporcionadas
    supabase_url = "https://ilsikngctkrmqnbutpuz.supabase.co"
    supabase_anon = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlsc2lrbmdjdGtybXFuYnV0cHV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0MTQwMTMsImV4cCI6MjA3Njk5MDAxM30.05KqrCvc0aDRjO1XzlNwrX5WcRBVAFdXMOgneiZ26Og"
    
    # Solicitar service key si no se proporcionó
    supabase_service = input("�️ SUPABASE_SERVICE_KEY (opcional, press Enter para usar anon): ").strip()
    if not supabase_service:
        supabase_service = supabase_anon  # Usar anon key como fallback
        
    # Generar DATABASE_URL
    project_id = "ilsikngctkrmqnbutpuz"
    db_password = input("🔐 Password de la DB PostgreSQL (opcional): ").strip()
    if not db_password:
        db_password = "[password]"  # Placeholder
    database_url = f"postgresql://postgres:{db_password}@db.{project_id}.supabase.co:5432/postgres"
    
    # Archivo .env
    env_file = Path("config/production/.env")
    
    if not env_file.exists():
        print("❌ Error: No se encuentra config/production/.env")
        return False
        
    # Leer contenido actual
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Actualizar variables de Supabase
    updates = {
        'SUPABASE_URL': supabase_url,
        'SUPABASE_ANON_KEY': supabase_anon,
        'SUPABASE_SERVICE_KEY': supabase_service,
        'DATABASE_URL': database_url
    }
    
    # Reemplazar valores
    for key, value in updates.items():
        # Buscar línea existente
        lines = content.split('\n')
        updated = False
        
        for i, line in enumerate(lines):
            if line.startswith(f'{key}='):
                lines[i] = f'{key}={value}'
                updated = True
                break
                
        if updated:
            content = '\n'.join(lines)
            print(f"✅ {key}: Actualizado")
        else:
            # Agregar al final si no existe
            content += f'\n{key}={value}'
            print(f"➕ {key}: Agregado")
    
    # Guardar archivo actualizado
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print()
        print("🎉 CONFIGURACIÓN COMPLETADA")
        print("=" * 50)
        print("✅ Supabase configurado correctamente")
        print("✅ Variables actualizadas en config/production/.env")
        print()
        print("🎯 PRÓXIMOS PASOS:")
        print("1. Ve a Database → SQL Editor en Supabase")
        print("2. Ejecuta el schema: database/supabase_schema.sql")
        print("3. Verifica con: python scripts/check_api_status_dynamic.py")
        print()
        print("🚀 ¡Tu sistema estará 100% completo!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error guardando configuración: {e}")
        return False

if __name__ == "__main__":
    update_supabase_config()