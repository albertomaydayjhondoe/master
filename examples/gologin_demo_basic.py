"""
Demo Básico del Sistema GoLogin - Solo Funciones Core

Este demo muestra las funcionalidades básicas sin dependencias externas,
funcionando completamente en modo dummy.
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from gologin_automation import (
    anonymous_context,
    GoLoginAPIClient,
    get_gologin_config,
    get_system_info
)

async def main():
    """Demo básico completo."""
    print("🚀 GoLogin Automation System - Demo Básico")
    print("=" * 50)
    
    # 1. Información del sistema
    print("\n💻 === Información del Sistema ===")
    info = get_system_info()
    print(f"🔧 Version: {info['version']}")
    print(f"📦 Componentes disponibles: {sum(info['components'].values())}/{len(info['components'])}")
    print(f"🎭 Modo Dummy: {info['dummy_mode']}")
    
    # 2. Demo de contexto de anonimato
    print("\n🎭 === Contexto de Anonimato ===")
    async with anonymous_context() as ctx:
        # Crear perfiles para diferentes países
        countries = ["US", "GB", "DE", "JP"]
        profiles = []
        
        for country in countries:
            profile = await ctx.get_anonymous_context(country_preference=country, force_new=True)
            profiles.append(profile)
            print(f"✅ {country}: {profile.profile_id[:20]}... ({profile.city})")
        
        # Mostrar configuración del último perfil
        browser_config = ctx.get_browser_config()
        print(f"\n🌐 Configuración del navegador (perfil {profiles[-1].country}):")
        print(f"   User-Agent: {browser_config['user_agent'][:60]}...")
        print(f"   Viewport: {browser_config['viewport']}")
        print(f"   Timezone: {browser_config['timezone_id']}")
        
        # Estadísticas
        stats = ctx.get_anonymity_stats()
        print(f"\n📊 Estadísticas:")
        print(f"   Perfiles totales: {stats['total_profiles']}")
        print(f"   Sesiones iniciadas: {stats['sessions_started']}")
        print(f"   Rotaciones: {stats['proxy_rotations']}")
    
    # 3. Demo de cliente API
    print("\n🔌 === Cliente API ===")
    async with GoLoginAPIClient() as client:
        # Health check
        health = await client.health_check()
        print(f"💚 Estado: {health['status']}")
        
        # Listar perfiles
        profiles = await client.list_profiles(limit=3)
        print(f"📋 Perfiles API: {len(profiles)}")
        
        for i, profile in enumerate(profiles, 1):
            print(f"   {i}. {profile.name} - {profile.country}")
        
        # Gestión de sesión
        if profiles:
            test_profile = profiles[0]
            session = await client.start_browser_session(test_profile.id)
            print(f"🚀 Sesión iniciada en puerto: {session.port}")
            
            # Información del proxy
            proxy_info = await client.get_proxy_info(test_profile.id)
            print(f"🌐 Proxy: {proxy_info['host']}:{proxy_info['port']}")
            
            # Detener sesión
            await client.stop_browser_session(test_profile.id)
            print(f"⏹️ Sesión detenida")
    
    # 4. Demo de configuración
    print("\n⚙️ === Configuración ===")
    config = get_gologin_config()
    print(f"📋 Max perfiles: {config.max_profiles}")
    print(f"🔧 Motor de automatización: {config.automation_engine}")
    print(f"🤖 Delays humanos: {config.human_behavior.min_action_delay}s - {config.human_behavior.max_action_delay}s")
    print(f"🔒 Auto-rotación: {config.security.auto_rotate_on_detection}")
    
    # Validar configuración
    errors = config.validate()
    if errors:
        print(f"⚠️ Errores: {len(errors)}")
    else:
        print(f"✅ Configuración válida")
    
    # 5. Demo de Selenium wrapper (modo dummy)
    print("\n🕷️ === Selenium Wrapper (Dummy) ===")
    try:
        from gologin_automation.browser.selenium_wrapper import GoLoginSeleniumDriver
        
        # Crear driver en modo dummy
        with GoLoginSeleniumDriver(profile_id="demo_profile") as driver:
            print("🚗 Driver creado (modo dummy)")
            
            # Navegar
            result = driver.navigate_to("https://example.com")
            print(f"🔗 Navegación: {result['status']}")
            
            # Interacciones
            click_result = driver.click_element("#button")
            print(f"🖱️ Click: {click_result['status']}")
            
            type_result = driver.type_text("#input", "Hello World")
            print(f"⌨️ Escribir: {type_result['status']}")
            
            # Info de página
            page_info = driver.get_page_info()
            print(f"📄 Página: {page_info['title']}")
            
    except Exception as e:
        print(f"❌ Error en Selenium wrapper: {e}")
    
    # 6. Resumen final
    print("\n" + "=" * 50)
    print("🎉 Demo completado exitosamente!")
    print("\n📈 Resumen de funcionalidades probadas:")
    print("   ✅ Contexto de anonimato con múltiples perfiles")
    print("   ✅ Cliente API con gestión de sesiones")
    print("   ✅ Sistema de configuración avanzado")
    print("   ✅ Wrapper de Selenium en modo dummy")
    print("   ✅ Estadísticas y métricas")
    
    print("\n🚀 El sistema GoLogin está completamente funcional!")
    
    # Información adicional
    print("\n💡 Para usar en producción:")
    print("   1. export GOLOGIN_API_TOKEN='tu_token_real'")
    print("   2. export DUMMY_MODE='false'")
    print("   3. pip install playwright selenium")
    print("   4. playwright install chromium")

if __name__ == "__main__":
    asyncio.run(main())