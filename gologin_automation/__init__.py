"""
GoLogin Automation System

Sistema completo de automatización de navegadores con anonimato avanzado.
Proporciona perfiles anónimos, anti-detección, patrones humanos y gestión inteligente de sesiones.

Componentes principales:
- AnonymityContext: Gestión de perfiles anónimos
- APIClient: Cliente para API de GoLogin  
- BrowserAutomation: Automatización con Playwright/Selenium
- Config: Sistema de configuración avanzado
"""

from .anonymity_context import (
    GoLoginAnonymityContext,
    AnonymityProfile, 
    AnonymityStats,
    anonymous_context,
    create_anonymous_session
)

from .api_client import (
    GoLoginAPIClient,
    GoLoginProfile,
    BrowserSession,
    create_gologin_client
)

from .config import (
    GoLoginConfig,
    ConfigManager,
    get_gologin_config,
    ProxyConfig,
    FingerPrintConfig,
    BrowserPreferences,
    SecurityConfig,
    HumanBehaviorConfig
)

# Importaciones condicionales basadas en disponibilidad
try:
    from .browser.browser_automation import (
        GoLoginBrowserAutomation,
        AntiDetectionMixin,
        HumanPattern,
        BrowserConfig,
        create_anonymous_browser
    )
    BROWSER_AUTOMATION_AVAILABLE = True
except ImportError:
    BROWSER_AUTOMATION_AVAILABLE = False

try:
    from .browser.selenium_wrapper import (
        GoLoginSeleniumDriver,
        SeleniumWrapper,
        create_gologin_selenium_driver
    )
    SELENIUM_WRAPPER_AVAILABLE = True
except ImportError:
    SELENIUM_WRAPPER_AVAILABLE = False

# Información del paquete
__version__ = "1.0.0"
__author__ = "GoLogin Automation Team"
__description__ = "Sistema de automatización web anónima de próxima generación"

# Configuración de logging
import logging
import os

def setup_logging(level: str = None):
    """Configurar logging para el sistema GoLogin."""
    level = level or os.getenv("GOLOGIN_LOG_LEVEL", "INFO")
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configurar loggers específicos
    logging.getLogger('gologin_automation').setLevel(level.upper())
    
    # Reducir verbosidad de librerías externas
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)

# Configurar logging automáticamente
setup_logging()

# Logger principal
logger = logging.getLogger(__name__)
logger.info(f"GoLogin Automation System v{__version__} inicializado")

# Información de disponibilidad de componentes
if not BROWSER_AUTOMATION_AVAILABLE:
    logger.warning("Browser Automation no disponible - instala playwright/selenium")

if not SELENIUM_WRAPPER_AVAILABLE:
    logger.warning("Selenium Wrapper no disponible - instala selenium")

# Exports principales
__all__ = [
    # Core components
    'GoLoginAnonymityContext',
    'AnonymityProfile',
    'AnonymityStats', 
    'anonymous_context',
    'create_anonymous_session',
    
    # API Client
    'GoLoginAPIClient',
    'GoLoginProfile',
    'BrowserSession',
    'create_gologin_client',
    
    # Configuration
    'GoLoginConfig',
    'ConfigManager',
    'get_gologin_config',
    'ProxyConfig',
    'FingerPrintConfig',
    'BrowserPreferences',
    'SecurityConfig',
    'HumanBehaviorConfig',
    
    # Browser automation (conditional)
    'GoLoginBrowserAutomation',
    'AntiDetectionMixin', 
    'HumanPattern',
    'BrowserConfig',
    'create_anonymous_browser',
    
    # Selenium wrapper (conditional)
    'GoLoginSeleniumDriver',
    'SeleniumWrapper',
    'create_gologin_selenium_driver',
    
    # Utilities
    'setup_logging',
    '__version__'
]

# Funciones de conveniencia principales
async def quick_anonymous_session(country: str = None, 
                                engine: str = "playwright",
                                headless: bool = False):
    """
    Crear sesión anónima rápida.
    
    Args:
        country: País preferido
        engine: Motor de automatización ("playwright", "selenium") 
        headless: Modo sin cabeza
        
    Returns:
        Contexto de automatización listo para usar
    """
    if BROWSER_AUTOMATION_AVAILABLE and engine == "playwright":
        return await create_anonymous_browser(
            country=country,
            engine="playwright"
        )
    elif SELENIUM_WRAPPER_AVAILABLE and engine == "selenium":
        # Crear contexto de anonimato y driver selenium
        ctx = GoLoginAnonymityContext()
        await ctx.initialize()
        
        profile = await ctx.get_anonymous_context(country_preference=country)
        
        driver = create_gologin_selenium_driver(
            profile_id=profile.profile_id,
            headless=headless,
            auto_start=True
        )
        
        return driver
    else:
        raise ImportError(f"Motor {engine} no disponible")

def get_system_info():
    """Obtener información del sistema GoLogin."""
    return {
        "version": __version__,
        "browser_automation_available": BROWSER_AUTOMATION_AVAILABLE,
        "selenium_wrapper_available": SELENIUM_WRAPPER_AVAILABLE,
        "dummy_mode": os.getenv("DUMMY_MODE", "true").lower() == "true",
        "components": {
            "anonymity_context": True,
            "api_client": True, 
            "config_system": True,
            "browser_automation": BROWSER_AUTOMATION_AVAILABLE,
            "selenium_wrapper": SELENIUM_WRAPPER_AVAILABLE
        }
    }

# Validación inicial del sistema
def _validate_system():
    """Validar configuración básica del sistema."""
    try:
        # Test configuración básica
        config = get_gologin_config()
        errors = config.validate()
        
        if errors and not config.dummy_mode:
            logger.warning(f"Errores de configuración: {errors}")
        
        # Test creación de perfil básico
        profile = AnonymityProfile(
            profile_id="validation_test",
            name="Validation Test",
            country="US",
            city="New York", 
            timezone="America/New_York",
            user_agent="Mozilla/5.0 (Validation)",
            screen_resolution="1920x1080",
            language="en-US",
            proxy_type="http",
            proxy_host="validation.test",
            proxy_port=8080
        )
        
        assert profile.can_use()
        logger.info("✅ Validación del sistema completada")
        
    except Exception as e:
        logger.error(f"❌ Error en validación del sistema: {e}")

# Ejecutar validación automática
_validate_system()
