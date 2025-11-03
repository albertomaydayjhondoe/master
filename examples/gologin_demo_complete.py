"""
Ejemplo Completo del Sistema GoLogin Automation

Este ejemplo demuestra todas las funcionalidades del sistema de anonimato GoLogin,
incluyendo gestión de perfiles, automatización del navegador, y patrones humanos.
"""

import asyncio
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from gologin_automation import (
    anonymous_context,
    GoLoginAPIClient,
    get_gologin_config,
    get_system_info,
    setup_logging
)

# Configurar logging detallado
setup_logging("INFO")

async def demo_anonymity_context():
    """Demostrar el contexto de anonimato."""
    print("\n🎭 === Demo: Contexto de Anonimato ===")
    
    async with anonymous_context() as ctx:
        print(f"💼 Contexto inicializado con {len(ctx.profiles)} perfiles")
        
        # Obtener perfil anónimo para Estados Unidos
        profile_us = await ctx.get_anonymous_context(country_preference="US")
        print(f"🇺🇸 Perfil US: {profile_us.profile_id} ({profile_us.city})")
        print(f"   User-Agent: {profile_us.user_agent[:50]}...")
        print(f"   Resolución: {profile_us.screen_resolution}")
        print(f"   Proxy: {profile_us.proxy_host}:{profile_us.proxy_port}")
        
        # Obtener configuración del navegador
        browser_config = ctx.get_browser_config()
        print(f"🌐 Configuración del navegador:")
        print(f"   Viewport: {browser_config['viewport']}")
        print(f"   Locale: {browser_config['locale']}")
        print(f"   Timezone: {browser_config['timezone_id']}")
        
        # Rotar a perfil diferente
        print("\n🔄 Rotando perfil...")
        profile_new = await ctx.rotate_profile()
        print(f"🆕 Nuevo perfil: {profile_new.profile_id} ({profile_new.country})")
        
        # Estadísticas
        stats = ctx.get_anonymity_stats()
        print(f"📊 Estadísticas:")
        print(f"   Perfiles creados: {stats['profiles_created']}")
        print(f"   Sesiones iniciadas: {stats['sessions_started']}")
        print(f"   Rotaciones: {stats['proxy_rotations']}")

async def demo_api_client():
    """Demostrar el cliente API."""
    print("\n🔌 === Demo: Cliente API ===")
    
    async with GoLoginAPIClient() as client:
        # Health check
        health = await client.health_check()
        print(f"💚 Health Status: {health['status']}")
        print(f"   Dummy Mode: {health['dummy_mode']}")
        print(f"   Sesiones activas: {health['active_sessions']}")
        
        # Listar perfiles
        profiles = await client.list_profiles(limit=5)
        print(f"📋 Perfiles disponibles: {len(profiles)}")
        
        for i, profile in enumerate(profiles[:3], 1):
            print(f"   {i}. {profile.name} ({profile.country}) - {profile.status}")
        
        # Gestión de sesiones con el primer perfil
        if profiles:
            test_profile = profiles[0]
            print(f"\n🚀 Iniciando sesión para: {test_profile.name}")
            
            # Iniciar sesión del navegador
            session = await client.start_browser_session(test_profile.id)
            print(f"   ✅ Sesión iniciada en puerto: {session.port}")
            print(f"   Session ID: {session.session_id}")
            
            # Información del proxy
            proxy_info = await client.get_proxy_info(test_profile.id)
            print(f"   🌐 Proxy: {proxy_info['type']}://{proxy_info['host']}:{proxy_info['port']}")
            
            # Listar sesiones activas
            active_sessions = await client.list_active_sessions()
            print(f"   📊 Total sesiones activas: {len(active_sessions)}")
            
            # Detener sesión
            stopped = await client.stop_browser_session(test_profile.id)
            print(f"   ⏹️ Sesión detenida: {stopped}")

async def demo_browser_automation():
    """Demostrar automatización del navegador."""
    print("\n🤖 === Demo: Automatización del Navegador ===")
    
    try:
        from gologin_automation.browser import GoLoginBrowserAutomation
        
        async with GoLoginBrowserAutomation(automation_engine="playwright") as browser:
            # Inicializar contexto de anonimato
            from gologin_automation import GoLoginAnonymityContext
            browser.anonymity_context = GoLoginAnonymityContext()
            
            # Iniciar sesión anónima
            session_info = await browser.start_anonymous_session(country_preference="GB")
            print(f"🔐 Sesión anónima iniciada:")
            print(f"   Perfil: {session_info['profile_id']}")
            print(f"   País: {session_info['country']}")
            print(f"   Motor: {session_info['engine']}")
            
            # Navegar a página de prueba
            print(f"\n🔗 Navegando a página de prueba...")
            success = await browser.navigate_to("https://httpbin.org/user-agent")
            print(f"   Navegación exitosa: {success}")
            
            # Obtener información de la página
            page_info = await browser.get_page_info()
            print(f"   URL actual: {page_info['url']}")
            print(f"   Título: {page_info['title']}")
            
            # Simular scroll humano
            print(f"\n📜 Simulando comportamiento humano...")
            await browser.scroll_page("down", amount=2, human_like=True)
            print(f"   Scroll completado")
            
            # Tomar captura de pantalla
            screenshot = await browser.take_screenshot()
            if screenshot:
                print(f"   📸 Captura guardada: {screenshot}")
            
            # Información de la sesión
            session_status = browser.get_session_info()
            print(f"📊 Estado de la sesión:")
            print(f"   Activa: {session_status['active']}")
            print(f"   País: {session_status['country']}")
            print(f"   Navegador listo: {session_status['browser_ready']}")
            
    except ImportError:
        print("⚠️ Browser automation no disponible (requiere playwright)")
        print("   Instala con: pip install playwright && playwright install chromium")

async def demo_selenium_wrapper():
    """Demostrar wrapper de Selenium."""
    print("\n🕷️ === Demo: Selenium Wrapper ===")
    
    try:
        from gologin_automation.browser import GoLoginSeleniumDriver
        
        # Crear driver (en modo dummy)
        with GoLoginSeleniumDriver(
            profile_id="demo_profile",
            session_port=3001,
            headless=False
        ) as driver:
            print(f"🚗 Driver Selenium inicializado")
            
            # Navegar
            result = driver.navigate_to("https://httpbin.org/user-agent")
            print(f"   Navegación: {result['status']}")
            if result['status'] == 'success':
                print(f"   URL final: {result.get('final_url', 'N/A')}")
                print(f"   Título: {result.get('title', 'N/A')}")
            
            # Obtener información de la página
            page_info = driver.get_page_info()
            print(f"📄 Info de página:")
            print(f"   URL: {page_info['url']}")
            print(f"   Título: {page_info['title']}")
            print(f"   Ready: {page_info['ready']}")
            
            # Simular interacciones
            print(f"\n🖱️ Simulando interacciones...")
            
            # Scroll
            scroll_result = driver.scroll_page("down", amount=3)
            print(f"   Scroll: {scroll_result['status']}")
            
            # Esperar elemento (dummy)
            element_found = driver.wait_for_element("body", timeout=5)
            print(f"   Elemento encontrado: {element_found}")
            
            # Captura de pantalla
            screenshot = driver.take_screenshot()
            if screenshot:
                print(f"   📸 Captura: {screenshot}")
                
    except ImportError:
        print("⚠️ Selenium wrapper usando modo dummy")
        
        # Usar wrapper básico
        from gologin_automation.browser.selenium_wrapper import SeleniumWrapper
        
        wrapper = SeleniumWrapper("demo_profile", 3001)
        
        # Navegar
        result = wrapper.navigate_to("https://example.com")
        print(f"🌐 Navegación dummy: {result['status']}")
        
        # Click
        click_result = wrapper.click_element("#demo-button")
        print(f"🖱️ Click dummy: {click_result['status']}")
        
        wrapper.close()

def demo_configuration():
    """Demostrar sistema de configuración."""
    print("\n⚙️ === Demo: Sistema de Configuración ===")
    
    # Obtener configuración actual
    config = get_gologin_config()
    print(f"📋 Configuración actual:")
    print(f"   Dummy Mode: {config.dummy_mode}")
    print(f"   Debug Mode: {config.debug_mode}")
    print(f"   Max Profiles: {config.max_profiles}")
    print(f"   Automation Engine: {config.automation_engine}")
    
    # Configuración del proxy
    print(f"🌐 Configuración de Proxy:")
    print(f"   Habilitado: {config.proxy.enabled}")
    print(f"   Tipo: {config.proxy.type}")
    print(f"   Rotación: {config.proxy.rotation_interval}s")
    
    # Configuración de comportamiento humano
    print(f"🤖 Comportamiento Humano:")
    print(f"   Delay mín/máx: {config.human_behavior.min_action_delay}s - {config.human_behavior.max_action_delay}s")
    print(f"   Velocidad escritura: {config.human_behavior.typing_speed_min}s - {config.human_behavior.typing_speed_max}s")
    
    # Configuración de seguridad
    print(f"🔒 Configuración de Seguridad:")
    print(f"   Max uso por perfil: {config.security.max_profile_usage}")
    print(f"   Auto-rotación: {config.security.auto_rotate_on_detection}")
    print(f"   Sensibilidad: {config.security.detection_sensitivity}")
    
    # Argumentos del navegador
    browser_args = config.get_browser_args()
    print(f"🌐 Argumentos del navegador ({len(browser_args)}):")
    for arg in browser_args[:5]:  # Mostrar solo los primeros 5
        print(f"   {arg}")
    if len(browser_args) > 5:
        print(f"   ... y {len(browser_args) - 5} más")
    
    # Validación
    errors = config.validate()
    if errors:
        print(f"⚠️ Errores de validación: {errors}")
    else:
        print(f"✅ Configuración válida")

async def demo_multiple_profiles():
    """Demostrar gestión de múltiples perfiles."""
    print("\n👥 === Demo: Múltiples Perfiles ===")
    
    async with anonymous_context() as ctx:
        print("🔄 Creando perfiles para diferentes países...")
        
        countries = ["US", "GB", "DE", "FR", "JP"]
        profiles = []
        
        for country in countries:
            profile = await ctx.create_profile(country=country)
            profiles.append(profile)
            print(f"   ✅ {country}: {profile.profile_id} ({profile.city})")
        
        print(f"\n📊 Resumen de perfiles:")
        print(f"   Total creados: {len(profiles)}")
        
        # Agrupar por país
        by_country = {}
        for p in ctx.profiles.values():
            by_country[p.country] = by_country.get(p.country, 0) + 1
        
        for country, count in sorted(by_country.items()):
            print(f"   {country}: {count} perfil(es)")
        
        # Estadísticas finales
        final_stats = ctx.get_anonymity_stats()
        print(f"\n📈 Estadísticas finales:")
        print(f"   Perfiles totales: {final_stats['total_profiles']}")
        print(f"   Perfiles activos: {final_stats['profiles_active']}")
        print(f"   Sesiones iniciadas: {final_stats['sessions_started']}")

def demo_system_info():
    """Mostrar información del sistema."""
    print("\n💻 === Información del Sistema ===")
    
    info = get_system_info()
    print(f"🔧 GoLogin Automation System v{info['version']}")
    print(f"   Modo Dummy: {info['dummy_mode']}")
    
    print(f"\n📦 Componentes disponibles:")
    for component, available in info['components'].items():
        status = "✅" if available else "❌"
        print(f"   {status} {component.replace('_', ' ').title()}")
    
    print(f"\n🌍 Variables de entorno:")
    env_vars = [
        "DUMMY_MODE", "GOLOGIN_API_TOKEN", "DEBUG", 
        "GOLOGIN_ENV", "GOLOGIN_LOG_LEVEL"
    ]
    
    for var in env_vars:
        value = os.getenv(var, "No definida")
        if "TOKEN" in var and value != "No definida":
            value = f"{value[:8]}..." if len(value) > 8 else value
        print(f"   {var}: {value}")

async def main():
    """Función principal del demo."""
    print("🚀 GoLogin Automation System - Demo Completo")
    print("=" * 50)
    
    # Información del sistema
    demo_system_info()
    
    # Demos de componentes
    await demo_anonymity_context()
    await demo_api_client()
    await demo_browser_automation()
    await demo_selenium_wrapper()
    demo_configuration()
    await demo_multiple_profiles()
    
    print("\n" + "=" * 50)
    print("🎉 Demo completado exitosamente!")
    print("\n💡 Próximos pasos:")
    print("   1. Configura tu token API: export GOLOGIN_API_TOKEN='tu_token'")
    print("   2. Desactiva dummy mode: export DUMMY_MODE='false'")
    print("   3. Instala dependencias opcionales: pip install playwright selenium")
    print("   4. Revisa la documentación en gologin_automation/README.md")

if __name__ == "__main__":
    asyncio.run(main())