"""
GoLogin Browser Automation Module

Módulo de automatización de navegadores con funcionalidades avanzadas de anonimato,
anti-detección y comportamiento humano.
"""

try:
    from .browser_automation import (
        GoLoginBrowserAutomation,
        AntiDetectionMixin,
        HumanPattern,
        BrowserConfig,
        create_anonymous_browser
    )
    BROWSER_AUTOMATION_AVAILABLE = True
except ImportError as e:
    BROWSER_AUTOMATION_AVAILABLE = False
    import logging
    logging.getLogger(__name__).warning(f"Browser automation no disponible: {e}")

try:
    from .selenium_wrapper import (
        GoLoginSeleniumDriver,
        SeleniumWrapper,
        create_gologin_selenium_driver
    )
    SELENIUM_WRAPPER_AVAILABLE = True
except ImportError as e:
    SELENIUM_WRAPPER_AVAILABLE = False
    import logging
    logging.getLogger(__name__).warning(f"Selenium wrapper no disponible: {e}")

__all__ = [
    'BROWSER_AUTOMATION_AVAILABLE',
    'SELENIUM_WRAPPER_AVAILABLE'
]

# Exports condicionales
if BROWSER_AUTOMATION_AVAILABLE:
    __all__.extend([
        'GoLoginBrowserAutomation',
        'AntiDetectionMixin',
        'HumanPattern', 
        'BrowserConfig',
        'create_anonymous_browser'
    ])

if SELENIUM_WRAPPER_AVAILABLE:
    __all__.extend([
        'GoLoginSeleniumDriver',
        'SeleniumWrapper',
        'create_gologin_selenium_driver'
    ])