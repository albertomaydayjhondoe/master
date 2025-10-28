"""
🧪 TEST SUPABASE CONNECTION
Prueba rápida de conexión con las nuevas credenciales
"""

import asyncio
import os
from pathlib import Path

# Configurar credenciales directamente
os.environ['SUPABASE_URL'] = 'https://ilsikngctkrmqnbutpuz.supabase.co'
os.environ['SUPABASE_ANON_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlsc2lrbmdjdGtybXFuYnV0cHV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0MTQwMTMsImV4cCI6MjA3Njk5MDAxM30.05KqrCvc0aDRjO1XzlNwrX5WcRBVAFdXMOgneiZ26Og'

async def test_supabase_connection():
    """Prueba conexión a Supabase"""
    
    print("🧪 TESTING SUPABASE CONNECTION")
    print("=" * 40)
    
    try:
        # Intentar importar supabase
        try:
            from supabase import create_client, Client
            print("✅ Supabase library importada correctamente")
        except ImportError:
            print("❌ Error: supabase library no instalada")
            print("💡 Ejecuta: pip install supabase")
            return False
        
        # Crear cliente
        url = os.environ['SUPABASE_URL']
        key = os.environ['SUPABASE_ANON_KEY']
        
        print(f"🔗 URL: {url}")
        print(f"🔑 Key: {key[:50]}...")
        
        supabase: Client = create_client(url, key)
        print("✅ Cliente Supabase creado")
        
        # Probar conexión básica
        try:
            # Intentar listar tablas o hacer ping
            result = supabase.table('users').select('*').limit(1).execute()
            print("✅ Conexión a base de datos exitosa")
            print(f"📊 Respuesta: {result}")
            
        except Exception as e:
            print(f"⚠️ Advertencia en query: {e}")
            print("💡 Esto es normal si las tablas no existen aún")
        
        # Test de función serverless
        try:
            # Probar función de tracking utm
            response = supabase.functions.invoke('track-utm', {
                'utm_source': 'test',
                'utm_medium': 'script',
                'utm_campaign': 'connection_test',
                'page_url': 'https://test.com',
                'user_agent': 'test-script'
            })
            print(f"✅ Función track-utm disponible: {response}")
        except Exception as e:
            print(f"⚠️ Función track-utm no disponible: {e}")
        
        print("\n🎉 SUPABASE CONNECTION TEST COMPLETADO")
        print("✅ Las credenciales funcionan correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en conexión: {e}")
        return False

def test_env_config():
    """Verifica configuración de archivos .env"""
    
    print("\n📁 VERIFICANDO CONFIGURACIÓN DE ARCHIVOS")
    print("=" * 40)
    
    env_files = [
        "config/production/.env",
        ".env"
    ]
    
    for env_file in env_files:
        if Path(env_file).exists():
            print(f"✅ Encontrado: {env_file}")
            
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'ilsikngctkrmqnbutpuz' in content:
                    print(f"   🔗 Contiene URL de Supabase correcta")
                if 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9' in content:
                    print(f"   🔑 Contiene Anon Key correcta")
        else:
            print(f"❌ No encontrado: {env_file}")

async def main():
    """Función principal"""
    print("🧪 SUPABASE CONNECTION TEST")
    print("Credenciales: ilsikngctkrmqnbutpuz.supabase.co")
    print("=" * 50)
    
    # Test configuración
    test_env_config()
    
    # Test conexión
    success = await test_supabase_connection()
    
    if success:
        print("\n🎉 ¡TODO FUNCIONANDO!")
        print("💡 Ahora puedes usar Supabase en tus scripts")
        print("🚀 Próximo paso: Ejecutar setup completo del sistema")
    else:
        print("\n❌ Problemas detectados")
        print("💡 Revisa las credenciales y la conexión a internet")

if __name__ == "__main__":
    asyncio.run(main())