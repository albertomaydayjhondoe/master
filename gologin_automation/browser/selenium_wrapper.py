"""
GoLogin Selenium Wrapper - Wrapper especializado para Selenium con GoLogin

Este módulo proporciona una interfaz específica para Selenium que se integra
perfectamente con el sistema de anonimato GoLogin.
"""

import asyncio
import logging
import time
import random
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
import os

# Selenium imports con manejo de errores
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import Select
    from selenium.common.exceptions import (
        TimeoutException, NoSuchElementException, WebDriverException,
        StaleElementReferenceException, ElementClickInterceptedException,
        ElementNotInteractableException
    )
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

logger = logging.getLogger(__name__)

class SeleniumWrapper:
    """
    Wrapper simplificado para compatibilidad con código existente.
    """
    def __init__(self, profile_id: str, port: int = 3001):
        self.profile_id = profile_id
        self.port = port
        self.session_active = True
        
    def navigate_to(self, url: str) -> Dict[str, Any]:
        """Simulate navigating to a URL."""
        time.sleep(random.uniform(0.5, 2.0))  # Human-like delay
        return {
            "status": "success",
            "url": url,
            "profile_id": self.profile_id,
            "port": self.port,
            "timestamp": time.time()
        }
    
    def click_element(self, selector: str) -> Dict[str, Any]:
        """Simulate clicking an element."""
        time.sleep(random.uniform(0.2, 0.8))
        return {
            "status": "success",
            "action": "click",
            "selector": selector,
            "profile_id": self.profile_id
        }
    
    def close(self):
        """Close the browser session."""
        self.session_active = False

class GoLoginSeleniumDriver:
    """
    Driver Selenium especializado para GoLogin.
    
    Proporciona funcionalidades específicas para trabajar con perfiles GoLogin,
    incluyendo configuración automática, comportamiento humano y anti-detección.
    """
    
    def __init__(self, 
                 profile_id: str = None,
                 session_port: int = None,
                 headless: bool = False,
                 browser_type: str = "chrome"):
        """
        Inicializar driver GoLogin.
        
        Args:
            profile_id: ID del perfil GoLogin
            session_port: Puerto de la sesión
            headless: Modo sin cabeza
            browser_type: Tipo de navegador ("chrome", "firefox")
        """
        if not SELENIUM_AVAILABLE:
            # Fallback a wrapper dummy
            logger.warning("Selenium no disponible, usando wrapper dummy")
            self._use_dummy = True
            self.dummy_wrapper = SeleniumWrapper(profile_id or "dummy", session_port or 3001)
            return
        
        self._use_dummy = False
        self.profile_id = profile_id
        self.session_port = session_port
        self.headless = headless
        self.browser_type = browser_type.lower()
        
        # Estado interno
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.actions: Optional[ActionChains] = None
        
        # Configuración
        self.dummy_mode = os.getenv("DUMMY_MODE", "true").lower() == "true"
        
        logger.info(f"GoLogin Selenium Driver inicializado ({browser_type})")
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.quit()
    
    def start(self) -> bool:
        """Iniciar driver del navegador."""
        if self._use_dummy:
            return True
            
        try:
            logger.info("🚀 Iniciando driver Selenium...")
            
            if self.browser_type == "chrome":
                self._start_chrome()
            elif self.browser_type == "firefox":
                self._start_firefox()
            else:
                raise ValueError(f"Tipo de navegador no soportado: {self.browser_type}")
            
            # Configurar herramientas adicionales
            self.wait = WebDriverWait(self.driver, 10)
            self.actions = ActionChains(self.driver)
            
            # Aplicar configuraciones post-inicio
            self._apply_stealth_measures()
            
            logger.info("✅ Driver Selenium iniciado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error iniciando driver Selenium: {e}")
            return False
    
    def _start_chrome(self):
        """Iniciar Chrome driver."""
        options = ChromeOptions()
        
        # Configuración básica anti-detección
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        if self.headless:
            options.add_argument("--headless")
        
        # Conectar a sesión GoLogin existente si disponible
        if self.session_port and not self.dummy_mode:
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.session_port}")
        
        try:
            self.driver = webdriver.Chrome(options=options)
        except Exception as e:
            logger.warning(f"Error conectando a GoLogin, usando driver local: {e}")
            # Usar driver local
            options._experimental_options.pop("debuggerAddress", None)
            self.driver = webdriver.Chrome(options=options)
    
    def _start_firefox(self):
        """Iniciar Firefox driver."""
        options = FirefoxOptions()
        
        if self.headless:
            options.add_argument("--headless")
        
        profile = webdriver.FirefoxProfile()
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference("useAutomationExtension", False)
        
        self.driver = webdriver.Firefox(options=options, firefox_profile=profile)
    
    def _apply_stealth_measures(self):
        """Aplicar medidas anti-detección."""
        if not self.driver:
            return
            
        stealth_scripts = [
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});",
            """
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            """,
            "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});"
        ]
        
        for script in stealth_scripts:
            try:
                self.driver.execute_script(script)
            except Exception as e:
                logger.warning(f"Error aplicando script stealth: {e}")
        
        # Maximizar ventana
        try:
            self.driver.maximize_window()
        except:
            pass
    
    def quit(self):
        """Cerrar driver."""
        if self._use_dummy:
            if hasattr(self, 'dummy_wrapper'):
                self.dummy_wrapper.close()
            return
            
        if self.driver:
            try:
                self.driver.quit()
                logger.info("🚪 Driver Selenium cerrado")
            except Exception as e:
                logger.warning(f"Error cerrando driver: {e}")
            finally:
                self.driver = None
                self.wait = None
                self.actions = None
    
    # Métodos de navegación
    
    def navigate_to(self, url: str, wait_for_load: bool = True) -> Dict[str, Any]:
        """Navegar a URL."""
        if self._use_dummy:
            return self.dummy_wrapper.navigate_to(url)
            
        try:
            logger.info(f"🔗 Navegando a: {url}")
            
            self.driver.get(url)
            
            if wait_for_load and self.wait:
                self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            
            # Pausa humana
            time.sleep(random.uniform(1.0, 3.0))
            
            return {
                "status": "success",
                "url": url,
                "final_url": self.driver.current_url,
                "title": self.driver.title
            }
            
        except Exception as e:
            logger.error(f"Error navegando a {url}: {e}")
            return {"status": "error", "error": str(e)}
    
    def click_element(self, selector: str, by: By = By.CSS_SELECTOR) -> Dict[str, Any]:
        """Hacer clic en elemento."""
        if self._use_dummy:
            return self.dummy_wrapper.click_element(selector)
            
        try:
            # Retraso humano
            time.sleep(random.uniform(0.2, 0.8))
            
            element = self.wait.until(EC.element_to_be_clickable((by, selector)))
            
            # Movimiento humano del mouse
            self.actions.move_to_element(element).pause(random.uniform(0.1, 0.3)).click().perform()
            
            logger.debug(f"✅ Clic en: {selector}")
            return {
                "status": "success",
                "action": "click",
                "selector": selector
            }
            
        except Exception as e:
            logger.error(f"Error haciendo clic en {selector}: {e}")
            return {"status": "error", "error": str(e)}
    
    def type_text(self, selector: str, text: str, by: By = By.CSS_SELECTOR, 
                  clear_first: bool = True) -> Dict[str, Any]:
        """Escribir texto."""
        if self._use_dummy:
            time.sleep(len(text) * 0.1)  # Simular velocidad de escritura
            return {
                "status": "success",
                "action": "type",
                "selector": selector,
                "text": text[:20] + "..." if len(text) > 20 else text
            }
            
        try:
            element = self.wait.until(EC.presence_of_element_located((by, selector)))
            
            if clear_first:
                element.clear()
            
            # Escritura carácter por carácter para simular comportamiento humano
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            return {
                "status": "success",
                "action": "type",
                "selector": selector,
                "text": text[:20] + "..." if len(text) > 20 else text
            }
            
        except Exception as e:
            logger.error(f"Error escribiendo en {selector}: {e}")
            return {"status": "error", "error": str(e)}
    
    def scroll_page(self, direction: str = "down", amount: int = 3) -> Dict[str, Any]:
        """Hacer scroll."""
        if self._use_dummy:
            time.sleep(amount * 0.5)
            return {
                "status": "success",
                "action": "scroll",
                "direction": direction,
                "amount": amount
            }
            
        try:
            scroll_distance = 300 if direction == "down" else -300
            
            for i in range(amount):
                self.driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
                time.sleep(random.uniform(0.3, 1.0))
            
            return {
                "status": "success",
                "action": "scroll",
                "direction": direction,
                "amount": amount
            }
            
        except Exception as e:
            logger.error(f"Error haciendo scroll: {e}")
            return {"status": "error", "error": str(e)}
    
    def wait_for_element(self, selector: str, by: By = By.CSS_SELECTOR, 
                        timeout: int = 10) -> bool:
        """Esperar por elemento."""
        if self._use_dummy:
            time.sleep(random.uniform(0.5, 2.0))
            return True
            
        try:
            temp_wait = WebDriverWait(self.driver, timeout)
            temp_wait.until(EC.presence_of_element_located((by, selector)))
            return True
        except TimeoutException:
            logger.warning(f"Elemento no encontrado en {timeout}s: {selector}")
            return False
    
    def take_screenshot(self, filename: str = None) -> Optional[str]:
        """Tomar captura de pantalla."""
        if self._use_dummy:
            return f"dummy_screenshot_{int(time.time())}.png"
            
        try:
            if not filename:
                filename = f"selenium_screenshot_{int(time.time())}.png"
            
            filepath = Path("logs/screenshots") / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            self.driver.save_screenshot(str(filepath))
            
            logger.info(f"📸 Captura guardada: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error tomando captura: {e}")
            return None
    
    def get_page_info(self) -> Dict[str, Any]:
        """Obtener información de la página."""
        if self._use_dummy:
            return {
                "url": "https://example.com",
                "title": "Example Page",
                "ready": True
            }
            
        try:
            return {
                "url": self.driver.current_url,
                "title": self.driver.title,
                "ready": self.driver.execute_script("return document.readyState") == "complete"
            }
        except Exception as e:
            logger.error(f"Error obteniendo info de página: {e}")
            return {}
    
    def close(self):
        """Alias para quit para retrocompatibilidad."""
        self.quit()


# Función de conveniencia
def create_gologin_selenium_driver(profile_id: str = None,
                                 session_port: int = None,
                                 headless: bool = False,
                                 auto_start: bool = True) -> GoLoginSeleniumDriver:
    """Crear driver GoLogin Selenium."""
    driver = GoLoginSeleniumDriver(
        profile_id=profile_id,
        session_port=session_port,
        headless=headless
    )
    
    if auto_start:
        driver.start()
    
    return driver
