
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
    lines = content.split('\n')
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
        f.write('\n'.join(lines))
    
    print("✅ Service Key actualizada correctamente")
    print("📂 Archivo: config/production/.env")
    print()
    print("🎯 PRÓXIMO PASO:")
    print("   python scripts/execute_supabase_schema.py")
    
    return True

if __name__ == "__main__":
    update_service_key()
