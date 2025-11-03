"""
GoLogin Browser Automation - Sistema de automatización de navegador

Este módulo proporciona automatización inteligente del navegador con GoLogin,
incluyendo patrones humanos, evasión de detección, y gestión avanzada de sesiones.
"""

import asyncio
import logging
import random
import time
import json
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path
import os

# Importaciones para automatización web
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import (
        TimeoutException, NoSuchElementException, 
        WebDriverException, StaleElementReferenceException
    )
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Importaciones internas
from ..api_client import GoLoginAPIClient, BrowserSession
from ..anonymity_context import GoLoginAnonymityContext, AnonymityProfile

logger = logging.getLogger(__name__)

@dataclass
class HumanPattern:
    """Patrón de comportamiento humano."""
    min_delay: float = 0.5
    max_delay: float = 2.0
    typing_speed: float = 0.1  # segundos por carácter
    mouse_movement_steps: int = 5
    scroll_pause: float = 0.3
    page_load_timeout: float = 30.0
    element_wait_timeout: float = 10.0
    
    # Patrones específicos
    reading_pause_min: float = 1.0
    reading_pause_max: float = 5.0
    interaction_delay_min: float = 0.2
    interaction_delay_max: float = 1.0

@dataclass
class BrowserConfig:
    """Configuración del navegador."""
    headless: bool = False
    window_size: tuple = (1920, 1080)
    user_data_dir: Optional[str] = None
    disable_images: bool = False
    disable_javascript: bool = False
    disable_plugins: bool = False
    disable_extensions: bool = False
    proxy_config: Optional[Dict[str, Any]] = None
    
    # GoLogin específico
    profile_id: Optional[str] = None
    session_port: Optional[int] = None
    debugger_address: Optional[str] = None

class AntiDetectionMixin:
    """Mixin para funcionalidades anti-detección."""
    
    def __init__(self):
        self.detection_checks = [
            self._check_webdriver_property,
            self._check_chrome_property,
            self._check_permissions_property,
            self._check_plugins_property,
            self._check_languages_property
        ]
    
    async def apply_stealth_measures(self, driver_or_page):
        """Aplicar medidas de sigilo."""
        if hasattr(driver_or_page, 'execute_script'):
            # Selenium
            await self._apply_selenium_stealth(driver_or_page)
        else:
            # Playwright
            await self._apply_playwright_stealth(driver_or_page)
    
    async def _apply_selenium_stealth(self, driver):
        """Aplicar sigilo para Selenium."""
        stealth_scripts = [
            # Ocultar webdriver property
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});",
            
            # Modificar chrome property  
            """
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            """,
            
            # Modificar permissions
            """
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            """,
            
            # Modificar plugins
            "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});",
            
            # Modificar languages
            "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});"
        ]
        
        for script in stealth_scripts:
            try:
                driver.execute_script(script)
            except Exception as e:
                logger.warning(f"Error aplicando script stealth: {e}")
    
    async def _apply_playwright_stealth(self, page):
        """Aplicar sigilo para Playwright."""
        # Playwright tiene mejor sigilo nativo, pero añadimos extras
        await page.add_init_script("""
            // Eliminar rastros de automatización
            delete navigator.__proto__.webdriver;
            
            // Modificar propiedades del navigator
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Simular comportamiento humano en eventos
            ['mousedown', 'mouseup', 'click'].forEach(eventType => {
                document.addEventListener(eventType, event => {
                    event.isTrusted = true;
                }, true);
            });
        """)
    
    def _check_webdriver_property(self, driver_or_page) -> bool:
        """Verificar si webdriver property está oculta."""
        try:
            if hasattr(driver_or_page, 'execute_script'):
                result = driver_or_page.execute_script("return navigator.webdriver")
                return result is None
            else:
                # Playwright check
                return True  # Playwright maneja esto mejor
        except:
            return False
    
    def _check_chrome_property(self, driver_or_page) -> bool:
        """Verificar chrome property."""
        try:
            if hasattr(driver_or_page, 'execute_script'):
                result = driver_or_page.execute_script("return window.chrome !== undefined")
                return result
            else:
                return True
        except:
            return False
    
    def _check_permissions_property(self, driver_or_page) -> bool:
        """Verificar permissions property."""
        return True  # Implementación básica
    
    def _check_plugins_property(self, driver_or_page) -> bool:
        """Verificar plugins property."""
        return True  # Implementación básica
    
    def _check_languages_property(self, driver_or_page) -> bool:
        """Verificar languages property."""
        return True  # Implementación básica

class GoLoginBrowserAutomation(AntiDetectionMixin):
    """
    Sistema de automatización de navegador con GoLogin.
    
    Características:
    - Integración completa con GoLogin API
    - Patrones de comportamiento humano
    - Anti-detección avanzada
    - Soporte para Selenium y Playwright
    - Gestión automática de sesiones
    - Monitoreo de anomalías
    """
    
    def __init__(self, 
                 api_client: GoLoginAPIClient = None,
                 anonymity_context: GoLoginAnonymityContext = None,
                 automation_engine: str = "playwright",  # "selenium" o "playwright"
                 human_patterns: HumanPattern = None):
        """
        Inicializar automatización del navegador.
        
        Args:
            api_client: Cliente API de GoLogin
            anonymity_context: Contexto de anonimato
            automation_engine: Motor de automatización
            human_patterns: Patrones de comportamiento humano
        """
        super().__init__()
        
        self.api_client = api_client
        self.anonymity_context = anonymity_context
        self.automation_engine = automation_engine
        self.human_patterns = human_patterns or HumanPattern()
        
        # Estado interno
        self.browser = None
        self.context = None
        self.page = None
        self.driver = None
        self.active_session: Optional[BrowserSession] = None
        self.active_profile: Optional[AnonymityProfile] = None
        
        # Configuración
        self.dummy_mode = os.getenv("DUMMY_MODE", "true").lower() == "true"
        
        # Validar disponibilidad del motor
        if automation_engine == "selenium" and not SELENIUM_AVAILABLE:
            raise ImportError("Selenium no está disponible. Instala: pip install selenium")
        elif automation_engine == "playwright" and not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright no está disponible. Instala: pip install playwright")
        
        logger.info(f"GoLogin Browser Automation inicializado (engine: {automation_engine})")
    
    async def __aenter__(self):
        """Context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.cleanup()
    
    async def initialize(self):
        """Inicializar sistema de automatización."""
        logger.info("🚀 Inicializando automatización del navegador...")
        
        # Inicializar componentes si no están listos
        if self.api_client and not self.api_client.session:
            await self.api_client.initialize()
        
        if self.anonymity_context:
            await self.anonymity_context.initialize()
        
        logger.info("✅ Automatización del navegador lista")
    
    async def cleanup(self):
        """Limpiar recursos."""
        logger.info("🧹 Limpiando automatización del navegador...")
        
        # Cerrar navegador/driver
        await self._close_browser()
        
        # Detener sesión GoLogin
        if self.active_session and self.api_client:
            try:
                await self.api_client.stop_browser_session(self.active_session.profile_id)
            except Exception as e:
                logger.warning(f"Error deteniendo sesión GoLogin: {e}")
        
        logger.info("✅ Automatización cerrada")
    
    async def start_anonymous_session(self, 
                                    country_preference: str = None,
                                    force_new_profile: bool = False) -> Dict[str, Any]:
        """
        Iniciar sesión anónima completa.
        
        Args:
            country_preference: País preferido
            force_new_profile: Forzar nuevo perfil
            
        Returns:
            Información de la sesión iniciada
        """
        logger.info("🔒 Iniciando sesión anónima...")
        
        # Obtener contexto de anonimato
        if not self.anonymity_context:
            raise ValueError("Contexto de anonimato requerido")
        
        self.active_profile = await self.anonymity_context.get_anonymous_context(
            force_new=force_new_profile,
            country_preference=country_preference
        )
        
        # Iniciar sesión GoLogin
        if self.api_client and not self.dummy_mode:
            self.active_session = await self.api_client.start_browser_session(
                self.active_profile.profile_id
            )
        else:
            # Sesión dummy
            self.active_session = BrowserSession(
                profile_id=self.active_profile.profile_id,
                session_id="dummy_session",
                port=3001
            )
        
        # Configurar navegador
        browser_config = self._create_browser_config()
        
        # Iniciar navegador
        await self._start_browser(browser_config)
        
        session_info = {
            "profile_id": self.active_profile.profile_id,
            "session_id": self.active_session.session_id,
            "country": self.active_profile.country,
            "city": self.active_profile.city,
            "user_agent": self.active_profile.user_agent,
            "proxy_enabled": bool(self.active_profile.proxy_host != "dummy"),
            "engine": self.automation_engine,
            "ready": True
        }
        
        logger.info(f"✅ Sesión anónima iniciada: {self.active_profile.profile_id} ({self.active_profile.country})")
        
        return session_info
    
    def _create_browser_config(self) -> BrowserConfig:
        """Crear configuración del navegador."""
        if not self.active_profile or not self.active_session:
            raise ValueError("Perfil y sesión requeridos")
        
        # Parsear resolución
        resolution = self.active_profile.screen_resolution.split('x')
        window_size = (int(resolution[0]), int(resolution[1]))
        
        # Configuración de proxy
        proxy_config = None
        if self.active_profile.proxy_host != "dummy":
            proxy_config = {
                "server": f"{self.active_profile.proxy_type}://{self.active_profile.proxy_host}:{self.active_profile.proxy_port}",
                "username": self.active_profile.proxy_username,
                "password": self.active_profile.proxy_password
            }
        
        return BrowserConfig(
            headless=False,  # GoLogin requiere modo visible
            window_size=window_size,
            proxy_config=proxy_config,
            profile_id=self.active_profile.profile_id,
            session_port=self.active_session.port,
            debugger_address=f"127.0.0.1:{self.active_session.port}" if not self.dummy_mode else None
        )
    
    async def _start_browser(self, config: BrowserConfig):
        """Iniciar navegador según el motor configurado."""
        if self.automation_engine == "playwright":
            await self._start_playwright_browser(config)
        else:
            await self._start_selenium_browser(config)
        
        # Aplicar medidas anti-detección
        if self.automation_engine == "playwright" and self.page:
            await self.apply_stealth_measures(self.page)
        elif self.automation_engine == "selenium" and self.driver:
            await self.apply_stealth_measures(self.driver)
    
    async def _start_playwright_browser(self, config: BrowserConfig):
        """Iniciar navegador con Playwright."""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright no disponible")
        
        playwright = await async_playwright().start()
        
        launch_options = {
            "headless": config.headless,
            "args": [
                f"--window-size={config.window_size[0]},{config.window_size[1]}",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        }
        
        # Conectar a sesión GoLogin existente o lanzar nuevo
        if config.debugger_address and not self.dummy_mode:
            launch_options["args"].append(f"--remote-debugging-port={config.session_port}")
            try:
                self.browser = await playwright.chromium.connect_over_cdp(
                    f"http://{config.debugger_address}"
                )
            except Exception as e:
                logger.warning(f"Error conectando a GoLogin, usando navegador local: {e}")
                self.browser = await playwright.chromium.launch(**launch_options)
        else:
            self.browser = await playwright.chromium.launch(**launch_options)
        
        # Crear contexto
        context_options = {
            "viewport": {"width": config.window_size[0], "height": config.window_size[1]},
            "user_agent": self.active_profile.user_agent if self.active_profile else None,
            "locale": self.active_profile.language if self.active_profile else "en-US"
        }
        
        if config.proxy_config:
            context_options["proxy"] = config.proxy_config
        
        self.context = await self.browser.new_context(**context_options)
        
        # Crear página
        self.page = await self.context.new_page()
        
        logger.info(f"🌐 Navegador Playwright iniciado (puerto: {config.session_port})")
    
    async def _start_selenium_browser(self, config: BrowserConfig):
        """Iniciar navegador con Selenium."""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium no disponible")
        
        options = webdriver.ChromeOptions()
        
        # Configuración básica
        if config.headless:
            options.add_argument("--headless")
        
        options.add_argument(f"--window-size={config.window_size[0]},{config.window_size[1]}")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        # User agent
        if self.active_profile:
            options.add_argument(f"--user-agent={self.active_profile.user_agent}")
        
        # Proxy
        if config.proxy_config:
            proxy_url = config.proxy_config["server"]
            options.add_argument(f"--proxy-server={proxy_url}")
        
        # Conectar a GoLogin o usar local
        if config.debugger_address and not self.dummy_mode:
            options.add_experimental_option("debuggerAddress", config.debugger_address)
        
        # Crear driver
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_size(config.window_size[0], config.window_size[1])
        
        logger.info(f"🌐 Navegador Selenium iniciado")
    
    async def _close_browser(self):
        """Cerrar navegador."""
        try:
            if self.automation_engine == "playwright":
                if self.page:
                    await self.page.close()
                if self.context:
                    await self.context.close()
                if self.browser:
                    await self.browser.close()
            else:
                if self.driver:
                    self.driver.quit()
            
            logger.info("🚪 Navegador cerrado")
            
        except Exception as e:
            logger.warning(f"Error cerrando navegador: {e}")
        finally:
            self.page = None
            self.context = None
            self.browser = None
            self.driver = None
    
    # Métodos de automatización con patrones humanos
    
    async def navigate_to(self, url: str, wait_for_load: bool = True) -> bool:
        """
        Navegar a URL con comportamiento humano.
        
        Args:
            url: URL destino
            wait_for_load: Esperar carga completa
            
        Returns:
            True si navegación exitosa
        """
        logger.info(f"🔗 Navegando a: {url}")
        
        try:
            if self.automation_engine == "playwright" and self.page:
                await self.page.goto(url, wait_until="domcontentloaded")
                
                if wait_for_load:
                    await self.page.wait_for_load_state("networkidle")
                
            elif self.automation_engine == "selenium" and self.driver:
                self.driver.get(url)
                
                if wait_for_load:
                    WebDriverWait(self.driver, self.human_patterns.page_load_timeout).until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                    )
            
            # Pausa humana después de carga
            await self._human_delay("reading_pause")
            
            logger.info(f"✅ Navegación exitosa a: {url}")
            return True
            
        except Exception as e:
            logger.error(f"Error navegando a {url}: {e}")
            return False
    
    async def click_element(self, 
                          selector: str, 
                          method: str = "css",
                          human_like: bool = True) -> bool:
        """
        Hacer clic en elemento con comportamiento humano.
        
        Args:
            selector: Selector del elemento
            method: Método de selección ("css", "xpath", "text")
            human_like: Aplicar comportamiento humano
            
        Returns:
            True si clic exitoso
        """
        try:
            if human_like:
                await self._human_delay("interaction_delay")
            
            if self.automation_engine == "playwright" and self.page:
                if method == "css":
                    await self.page.click(selector)
                elif method == "xpath":
                    await self.page.click(f"xpath={selector}")
                elif method == "text":
                    await self.page.click(f"text={selector}")
                
            elif self.automation_engine == "selenium" and self.driver:
                if method == "css":
                    element = WebDriverWait(self.driver, self.human_patterns.element_wait_timeout).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                elif method == "xpath":
                    element = WebDriverWait(self.driver, self.human_patterns.element_wait_timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                else:
                    raise ValueError(f"Método no soportado para Selenium: {method}")
                
                if human_like:
                    # Movimiento humano del mouse
                    actions = ActionChains(self.driver)
                    actions.move_to_element(element).pause(random.uniform(0.1, 0.3)).click().perform()
                else:
                    element.click()
            
            if human_like:
                await self._human_delay("interaction_delay")
            
            logger.debug(f"✅ Clic en elemento: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Error haciendo clic en {selector}: {e}")
            return False
    
    async def type_text(self, 
                       selector: str, 
                       text: str, 
                       clear_first: bool = True,
                       human_like: bool = True) -> bool:
        """
        Escribir texto con comportamiento humano.
        
        Args:
            selector: Selector del campo
            text: Texto a escribir
            clear_first: Limpiar campo primero
            human_like: Aplicar comportamiento humano
            
        Returns:
            True si escritura exitosa
        """
        try:
            if self.automation_engine == "playwright" and self.page:
                if clear_first:
                    await self.page.fill(selector, "")
                
                if human_like:
                    # Escritura carácter por carácter
                    for char in text:
                        await self.page.type(selector, char)
                        await asyncio.sleep(random.uniform(0.05, self.human_patterns.typing_speed))
                else:
                    await self.page.type(selector, text)
                
            elif self.automation_engine == "selenium" and self.driver:
                element = WebDriverWait(self.driver, self.human_patterns.element_wait_timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                
                if clear_first:
                    element.clear()
                
                if human_like:
                    # Escritura carácter por carácter
                    for char in text:
                        element.send_keys(char)
                        await asyncio.sleep(random.uniform(0.05, self.human_patterns.typing_speed))
                else:
                    element.send_keys(text)
            
            logger.debug(f"✅ Texto escrito en {selector}: {text[:20]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error escribiendo en {selector}: {e}")
            return False
    
    async def scroll_page(self, 
                         direction: str = "down", 
                         amount: int = 3,
                         human_like: bool = True) -> bool:
        """
        Hacer scroll con comportamiento humano.
        
        Args:
            direction: Dirección ("up", "down")
            amount: Cantidad de scrolls
            human_like: Aplicar comportamiento humano
            
        Returns:
            True si scroll exitoso
        """
        try:
            scroll_distance = 300 if direction == "down" else -300
            
            for i in range(amount):
                if self.automation_engine == "playwright" and self.page:
                    await self.page.mouse.wheel(0, scroll_distance)
                elif self.automation_engine == "selenium" and self.driver:
                    self.driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
                
                if human_like:
                    await asyncio.sleep(random.uniform(
                        self.human_patterns.scroll_pause * 0.5, 
                        self.human_patterns.scroll_pause * 1.5
                    ))
            
            logger.debug(f"✅ Scroll {direction} completado ({amount} veces)")
            return True
            
        except Exception as e:
            logger.error(f"Error haciendo scroll: {e}")
            return False
    
    async def wait_for_element(self, 
                             selector: str, 
                             timeout: float = None,
                             visible: bool = True) -> bool:
        """
        Esperar por elemento.
        
        Args:
            selector: Selector del elemento
            timeout: Timeout personalizado
            visible: Esperar que sea visible
            
        Returns:
            True si elemento encontrado
        """
        timeout = timeout or self.human_patterns.element_wait_timeout
        
        try:
            if self.automation_engine == "playwright" and self.page:
                if visible:
                    await self.page.wait_for_selector(selector, timeout=timeout * 1000)
                else:
                    await self.page.wait_for_selector(selector, state="attached", timeout=timeout * 1000)
                
            elif self.automation_engine == "selenium" and self.driver:
                if visible:
                    WebDriverWait(self.driver, timeout).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
                    )
                else:
                    WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
            
            logger.debug(f"✅ Elemento encontrado: {selector}")
            return True
            
        except Exception as e:
            logger.warning(f"Elemento no encontrado en {timeout}s: {selector}")
            return False
    
    async def get_page_info(self) -> Dict[str, Any]:
        """Obtener información de la página actual."""
        try:
            if self.automation_engine == "playwright" and self.page:
                return {
                    "url": self.page.url,
                    "title": await self.page.title(),
                    "viewport": self.page.viewport_size
                }
            elif self.automation_engine == "selenium" and self.driver:
                return {
                    "url": self.driver.current_url,
                    "title": self.driver.title,
                    "window_size": self.driver.get_window_size()
                }
        except Exception as e:
            logger.error(f"Error obteniendo info de página: {e}")
            return {}
    
    async def take_screenshot(self, filename: str = None) -> Optional[str]:
        """Tomar captura de pantalla."""
        try:
            if not filename:
                filename = f"screenshot_{int(time.time())}.png"
            
            filepath = Path("logs") / "screenshots" / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            if self.automation_engine == "playwright" and self.page:
                await self.page.screenshot(path=str(filepath))
            elif self.automation_engine == "selenium" and self.driver:
                self.driver.save_screenshot(str(filepath))
            
            logger.info(f"📸 Captura guardada: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error tomando captura: {e}")
            return None
    
    # Métodos de utilidad para comportamiento humano
    
    async def _human_delay(self, delay_type: str = "default"):
        """Aplicar retraso humano."""
        delays = {
            "default": (self.human_patterns.min_delay, self.human_patterns.max_delay),
            "interaction_delay": (self.human_patterns.interaction_delay_min, self.human_patterns.interaction_delay_max),
            "reading_pause": (self.human_patterns.reading_pause_min, self.human_patterns.reading_pause_max)
        }
        
        min_delay, max_delay = delays.get(delay_type, delays["default"])
        delay = random.uniform(min_delay, max_delay)
        
        await asyncio.sleep(delay)
    
    def get_session_info(self) -> Dict[str, Any]:
        """Obtener información de la sesión actual."""
        return {
            "active": bool(self.active_session),
            "profile_id": self.active_profile.profile_id if self.active_profile else None,
            "country": self.active_profile.country if self.active_profile else None,
            "session_port": self.active_session.port if self.active_session else None,
            "engine": self.automation_engine,
            "browser_ready": bool(self.page or self.driver),
            "dummy_mode": self.dummy_mode
        }


# Funciones de conveniencia

async def create_anonymous_browser(country: str = None, 
                                 engine: str = "playwright",
                                 api_token: str = None) -> GoLoginBrowserAutomation:
    """Crear navegador anónimo completo."""
    from .api_client import GoLoginAPIClient
    from .anonymity_context import GoLoginAnonymityContext
    
    # Crear componentes
    api_client = GoLoginAPIClient(api_token=api_token)
    anonymity_context = GoLoginAnonymityContext(api_token=api_token)
    
    # Crear automatización
    automation = GoLoginBrowserAutomation(
        api_client=api_client,
        anonymity_context=anonymity_context,
        automation_engine=engine
    )
    
    # Inicializar
    await automation.initialize()
    
    # Iniciar sesión anónima
    await automation.start_anonymous_session(country_preference=country)
    
    return automation


if __name__ == "__main__":
    # Test de automatización
    async def test_browser_automation():
        async with GoLoginBrowserAutomation(automation_engine="playwright") as browser:
            # Crear contexto dummy para testing
            from .anonymity_context import GoLoginAnonymityContext
            
            anonymity_context = GoLoginAnonymityContext()
            browser.anonymity_context = anonymity_context
            
            # Iniciar sesión
            session_info = await browser.start_anonymous_session()
            print(f"Sesión iniciada: {session_info}")
            
            # Navegar
            success = await browser.navigate_to("https://httpbin.org/user-agent")
            print(f"Navegación exitosa: {success}")
            
            # Info de página
            page_info = await browser.get_page_info()
            print(f"Página: {page_info}")
    
    if PLAYWRIGHT_AVAILABLE:
        asyncio.run(test_browser_automation())
    else:
        print("Playwright no disponible para testing")