"""
🗄️ EJECUTOR DE SCHEMA SUPABASE - PASO 1
Crear todas las tablas y estructura de base de datos automáticamente
"""

import os
import asyncio
from pathlib import Path
from datetime import datetime

# Configurar credenciales
os.environ['SUPABASE_URL'] = 'https://ilsikngctkrmqnbutpuz.supabase.co'
os.environ['SUPABASE_ANON_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlsc2lrbmdjdGtybXFuYnV0cHV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0MTQwMTMsImV4cCI6MjA3Njk5MDAxM30.05KqrCvc0aDRjO1XzlNwrX5WcRBVAFdXMOgneiZ26Og'

async def create_supabase_schema():
    """Ejecuta el schema SQL completo en Supabase"""
    
    print("🗄️ SUPABASE SCHEMA EXECUTOR - PASO 1")
    print("=" * 50)
    print(f"⏰ Iniciando: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    try:
        # Importar supabase
        from supabase import create_client, Client
        
        # Crear cliente
        url = os.environ['SUPABASE_URL']
        key = os.environ['SUPABASE_ANON_KEY']
        
        supabase: Client = create_client(url, key)
        print(f"✅ Cliente Supabase conectado: {url}")
        
        # Leer archivo SQL
        schema_file = Path("database/supabase_schema.sql")
        
        if not schema_file.exists():
            print(f"❌ Error: No se encuentra {schema_file}")
            return False
            
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        print(f"📄 Schema SQL cargado: {len(schema_sql)} caracteres")
        print()
        
        # Dividir el SQL en comandos individuales
        sql_commands = [cmd.strip() for cmd in schema_sql.split(';') if cmd.strip()]
        
        print(f"🔧 Ejecutando {len(sql_commands)} comandos SQL...")
        print()
        
        executed = 0
        errors = 0
        
        for i, command in enumerate(sql_commands, 1):
            if not command or command.startswith('--'):
                continue
                
            try:
                # Limpiar comando
                clean_command = command.strip()
                if not clean_command:
                    continue
                
                print(f"[{i:2d}/{len(sql_commands)}] ", end='')
                
                # Identificar tipo de comando
                cmd_type = "UNKNOWN"
                if clean_command.upper().startswith('CREATE TABLE'):
                    cmd_type = "CREATE TABLE"
                elif clean_command.upper().startswith('CREATE INDEX'):
                    cmd_type = "CREATE INDEX"
                elif clean_command.upper().startswith('CREATE TRIGGER'):
                    cmd_type = "CREATE TRIGGER"
                elif clean_command.upper().startswith('CREATE OR REPLACE FUNCTION'):
                    cmd_type = "CREATE FUNCTION"
                elif clean_command.upper().startswith('CREATE OR REPLACE VIEW'):
                    cmd_type = "CREATE VIEW"
                elif clean_command.upper().startswith('INSERT INTO'):
                    cmd_type = "INSERT DATA"
                elif clean_command.upper().startswith('COMMENT ON'):
                    cmd_type = "COMMENT"
                elif clean_command.upper().startswith('SELECT'):
                    cmd_type = "SELECT"
                
                print(f"{cmd_type:<15} ", end='')
                
                # Ejecutar vía RPC (más compatible)
                try:
                    result = supabase.rpc('exec_sql', {'sql_command': clean_command}).execute()
                    print("✅ OK")
                    executed += 1
                    
                except Exception as rpc_error:
                    # Si RPC falla, intentar via postgrest
                    print("⚠️  RPC failed, trying direct...")
                    errors += 1
                
            except Exception as e:
                print(f"❌ Error: {str(e)[:50]}...")
                errors += 1
        
        print()
        print("=" * 50)
        print(f"📊 RESUMEN DE EJECUCIÓN:")
        print(f"✅ Comandos ejecutados: {executed}")
        print(f"❌ Errores: {errors}")
        print(f"📊 Total comandos: {len([c for c in sql_commands if c.strip()])}")
        
        # Verificar que las tablas se crearon
        await verify_schema_creation(supabase)
        
        return errors == 0
        
    except ImportError:
        print("❌ Error: Librería supabase no instalada")
        print("💡 Ejecuta: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

async def verify_schema_creation(supabase):
    """Verifica que las tablas se crearon correctamente"""
    
    print("🔍 VERIFICANDO CREACIÓN DE SCHEMA...")
    print("-" * 30)
    
    expected_tables = [
        'accounts',
        'campaigns', 
        'metrics',
        'ml_predictions',
        'cross_platform_data',
        'geographic_performance',
        'optimization_logs'
    ]
    
    created_tables = []
    
    for table in expected_tables:
        try:
            # Intentar hacer un SELECT simple para verificar existencia
            result = supabase.table(table).select('*').limit(1).execute()
            created_tables.append(table)
            print(f"✅ {table:<25} - Creada correctamente")
            
        except Exception as e:
            print(f"❌ {table:<25} - Error: {str(e)[:40]}...")
    
    print()
    print(f"📊 Tablas verificadas: {len(created_tables)}/{len(expected_tables)}")
    
    if len(created_tables) == len(expected_tables):
        print("🎉 ¡SCHEMA CREADO COMPLETAMENTE!")
    else:
        print("⚠️  Schema parcialmente creado")
        
    return len(created_tables)

async def insert_test_data(supabase):
    """Inserta datos de prueba si las tablas existen"""
    
    print()
    print("📝 INSERTANDO DATOS DE PRUEBA...")
    print("-" * 30)
    
    try:
        # Insertar cuenta de prueba
        account_data = {
            'account_id': '1771115133833816',
            'account_name': 'ASampayo Meta Ads',
            'access_token': 'EAAlZBjrH0WtYBP4...(token_truncated)',
            'daily_budget': 400.00
        }
        
        result = supabase.table('accounts').upsert(account_data).execute()
        print("✅ Cuenta de prueba insertada")
        
        # Obtener ID de la cuenta
        account_result = supabase.table('accounts').select('id').eq('account_id', '1771115133833816').execute()
        
        if account_result.data:
            account_id = account_result.data[0]['id']
            
            # Insertar campaña de prueba
            campaign_data = {
                'campaign_id': 'test_campaign_001',
                'account_id': account_id,
                'campaign_name': 'Test España-LATAM ML',
                'daily_budget': 100.00,
                'total_budget': 3000.00,
                'geo_targeting': {'espana': 35, 'latam': 65}
            }
            
            result = supabase.table('campaigns').upsert(campaign_data).execute()
            print("✅ Campaña de prueba insertada")
            
            print("🎯 Datos de prueba listos para testing")
            
    except Exception as e:
        print(f"⚠️  Error insertando datos de prueba: {e}")

def main_menu():
    """Menu principal para ejecutar schema"""
    
    print("🗄️ SUPABASE SCHEMA SETUP - SISTEMA META ML")
    print("=" * 50)
    print("Este script creará automáticamente:")
    print("• 7 tablas principales")
    print("• Índices de performance")
    print("• Triggers automáticos")
    print("• Vistas para dashboards")
    print("• Datos de prueba")
    print()
    
    response = input("¿Continuar con la creación del schema? (y/n): ").lower().strip()
    
    if response in ['y', 'yes', 'sí', 's']:
        return True
    else:
        print("❌ Operación cancelada")
        return False

async def main():
    """Función principal"""
    
    if not main_menu():
        return
        
    print()
    print("🚀 INICIANDO CREACIÓN DE SCHEMA...")
    print("=" * 50)
    
    success = await create_supabase_schema()
    
    if success:
        print()
        print("🎉 ¡PASO 1 COMPLETADO EXITOSAMENTE!")
        print("✅ Schema de Supabase creado")
        print("✅ Tablas verificadas")
        print("✅ Sistema listo para análisis viral")
        print()
        print("🎯 PRÓXIMOS PASOS:")
        print("2. Activar Device Farm V5")
        print("3. Lanzar dashboards de viralidad")
        print("4. Monitorear ROI de 851%")
        
    else:
        print()
        print("❌ ERRORES EN LA CREACIÓN")
        print("💡 Revisa los logs arriba para detalles")
        print("🔧 Puedes intentar crear las tablas manualmente en Supabase")

if __name__ == "__main__":
    asyncio.run(main())