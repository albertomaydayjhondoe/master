"""
🔑 SOLUCIÓN: OBTENER SERVICE ROLE KEY DE SUPABASE
Pasos para conseguir la clave con permisos completos
"""

def get_service_role_instructions():
    """Instrucciones para obtener Service Role Key"""
    
    print("🔑 CÓMO OBTENER SERVICE ROLE KEY")
    print("=" * 50)
    print()
    
    print("📍 PASO A PASO:")
    print("1️⃣ Ve a tu proyecto Supabase:")
    print("   🌐 https://ilsikngctkrmqnbutpuz.supabase.co")
    print()
    
    print("2️⃣ En el dashboard, ve a:")
    print("   ⚙️  Settings (icono engranaje abajo izquierda)")
    print("   📋 API")
    print()
    
    print("3️⃣ En la página API verás:")
    print("   🔓 anon public (ya la tenemos)")
    print("   🔐 service_role (la que necesitamos)")
    print()
    
    print("4️⃣ Copia la service_role key:")
    print("   👁️  Click 'Reveal' en service_role")
    print("   📋 Copia la clave completa (empieza con eyJ...)")
    print("   ⚠️  IMPORTANTE: Esta clave tiene permisos ADMIN")
    print()
    
    print("5️⃣ Actualiza tu configuración:")
    print("   📝 Pega la clave en config/production/.env")
    print("   🔄 Reemplaza SUPABASE_SERVICE_KEY")
    print()
    
    print("🎯 DESPUÉS DE OBTENER LA CLAVE:")
    print("✅ Podremos crear el schema automáticamente")
    print("✅ Sistema funcionará al 100%")
    print()

if __name__ == "__main__":
    get_service_role_instructions()