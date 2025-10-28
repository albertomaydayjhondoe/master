"""
Device Farm v5 - Appium Controller
Manages Appium servers and WebDriver sessions for mobile automation
"""
import asyncio
import subprocess
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from loguru import logger
import psutil

# Appium imports (will be available after pip install)
try:
    from appium import webdriver
    from appium.webdriver.common.appiumby import AppiumBy
    from appium.options.android import UiAutomator2Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import WebDriverException, TimeoutException
    APPIUM_AVAILABLE = True
except ImportError:
    logger.warning("Appium not installed, using mock implementation")
    APPIUM_AVAILABLE = False

from ..config_manager import get_config
from ..core.models import get_db_session, Device


@dataclass
class AppiumServerConfig:
    """Appium server configuration"""
    port: int
    device_serial: str
    bootstrap_port: int
    chromedriver_port: int
    system_port: int
    
    def get_server_url(self) -> str:
        """Get Appium server URL"""
        return f"http://127.0.0.1:{self.port}"
    
    def get_capabilities(self, app_package: Optional[str] = None) -> Dict[str, Any]:
        """Get Appium capabilities for this configuration"""
        caps = {
            'platformName': 'Android',
            'automationName': 'UiAutomator2',
            'deviceName': self.device_serial,
            'udid': self.device_serial,
            'systemPort': self.system_port,
            'chromedriverPort': self.chromedriver_port,
            'noReset': True,
            'fullReset': False,
            'newCommandTimeout': 300,
            'uiautomator2ServerLaunchTimeout': 60000,
            'uiautomator2ServerInstallTimeout': 60000,
            'adbExecTimeout': 30000,
            'androidDeviceReadyTimeout': 30,
            'androidInstallTimeout': 90000,
            'appWaitDuration': 30000,
            'deviceReadyTimeout': 30
        }
        
        if app_package:
            caps.update({
                'appPackage': app_package,
                'appActivity': self._get_main_activity(app_package)
            })
        
        return caps
    
    def _get_main_activity(self, package: str) -> str:
        """Get main activity for common packages"""
        activities = {
            'com.android.chrome': 'com.google.android.apps.chrome.Main',
            'com.instagram.android': 'com.instagram.mainactivity.MainActivity',
            'com.zhiliaoapp.musically': 'com.ss.android.ugc.aweme.splash.SplashActivity',
            'com.twitter.android': 'com.twitter.android.StartActivity'
        }
        return activities.get(package, f'{package}.MainActivity')


@dataclass
class WebDriverSession:
    """Active WebDriver session"""
    session_id: str
    device_serial: str
    driver: Any  # WebDriver instance
    app_package: Optional[str]
    created_at: datetime
    last_activity: datetime
    
    def is_active(self) -> bool:
        """Check if session is still active"""
        try:
            if not self.driver:
                return False
            # Simple check to see if driver is responsive
            self.driver.current_activity
            return True
        except:
            return False
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now(timezone.utc)


class AppiumServerManager:
    """Manages individual Appium server instance"""
    
    def __init__(self, config: AppiumServerConfig):
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.start_time: Optional[datetime] = None
        
    async def start(self) -> bool:
        """Start Appium server"""
        try:
            if self.is_running:
                logger.debug(f"Appium server already running on port {self.config.port}")
                return True
            
            # Check if port is available
            if not await self._is_port_available(self.config.port):
                logger.error(f"Port {self.config.port} is already in use")
                return False
            
            # Build Appium command
            cmd = [
                'appium',
                '--port', str(self.config.port),
                '--bootstrap-port', str(self.config.bootstrap_port),
                '--chromedriver-port', str(self.config.chromedriver_port),
                '--session-override',
                '--log-level', 'info',
                '--log-timestamp',
                '--local-timezone'
            ]
            
            logger.info(f"Starting Appium server for device {self.config.device_serial} on port {self.config.port}")
            
            # Start server process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to be ready
            if await self._wait_for_server():
                self.is_running = True
                self.start_time = datetime.now(timezone.utc)
                logger.info(f"Appium server started successfully on port {self.config.port}")
                return True
            else:
                logger.error(f"Appium server failed to start on port {self.config.port}")
                await self.stop()
                return False
                
        except Exception as e:
            logger.error(f"Error starting Appium server on port {self.config.port}: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop Appium server"""
        try:
            if not self.is_running:
                return True
            
            if self.process:
                logger.info(f"Stopping Appium server on port {self.config.port}")
                self.process.terminate()
                
                # Wait for graceful shutdown
                try:
                    await asyncio.wait_for(asyncio.to_thread(self.process.wait), timeout=10)
                except asyncio.TimeoutError:
                    logger.warning(f"Appium server on port {self.config.port} did not stop gracefully, killing")
                    self.process.kill()
                    await asyncio.to_thread(self.process.wait)
                
                self.process = None
            
            self.is_running = False
            self.start_time = None
            logger.info(f"Appium server stopped on port {self.config.port}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping Appium server on port {self.config.port}: {e}")
            return False
    
    async def _is_port_available(self, port: int) -> bool:
        """Check if port is available"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                return False
        return True
    
    async def _wait_for_server(self, timeout: int = 30) -> bool:
        """Wait for Appium server to be ready"""
        import aiohttp
        
        server_url = f"{self.config.get_server_url()}/status"
        
        async with aiohttp.ClientSession() as session:
            for _ in range(timeout):
                try:
                    async with session.get(server_url, timeout=aiohttp.ClientTimeout(total=2)) as response:
                        if response.status == 200:
                            return True
                except:
                    pass
                
                await asyncio.sleep(1)
        
        return False
    
    def get_uptime(self) -> Optional[float]:
        """Get server uptime in seconds"""
        if self.start_time:
            return (datetime.now(timezone.utc) - self.start_time).total_seconds()
        return None


class AppiumController:
    """Main controller for Appium servers and WebDriver sessions"""
    
    def __init__(self):
        self.config = get_config()
        
        # Server management
        self._servers: Dict[str, AppiumServerManager] = {}  # device_serial -> server
        self._sessions: Dict[str, WebDriverSession] = {}    # session_id -> session
        self._port_allocator = iter(range(
            self.config.appium.base_port,
            self.config.appium.base_port + self.config.appium.port_range
        ))
        
        logger.info("Appium Controller initialized")
    
    async def initialize_device_server(self, device_serial: str) -> bool:
        """Initialize Appium server for a device"""
        try:
            if device_serial in self._servers:
                server = self._servers[device_serial]
                if server.is_running:
                    logger.debug(f"Server already running for device {device_serial}")
                    return True
                else:
                    # Restart existing server
                    return await server.start()
            
            # Allocate ports for new server
            try:
                main_port = next(self._port_allocator)
                bootstrap_port = next(self._port_allocator)
                chromedriver_port = next(self._port_allocator)
                system_port = next(self._port_allocator)
            except StopIteration:
                logger.error("No more ports available for Appium servers")
                return False
            
            # Create server configuration
            server_config = AppiumServerConfig(
                port=main_port,
                device_serial=device_serial,
                bootstrap_port=bootstrap_port,
                chromedriver_port=chromedriver_port,
                system_port=system_port
            )
            
            # Create and start server
            server = AppiumServerManager(server_config)
            if await server.start():
                self._servers[device_serial] = server
                logger.info(f"Appium server initialized for device {device_serial}")
                return True
            else:
                logger.error(f"Failed to start Appium server for device {device_serial}")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing server for device {device_serial}: {e}")
            return False
    
    async def create_session(self, device_serial: str, app_package: Optional[str] = None, 
                           fingerprint_script: Optional[str] = None) -> Optional[str]:
        """Create new WebDriver session"""
        try:
            if not APPIUM_AVAILABLE:
                logger.error("Appium not available, cannot create session")
                return None
            
            # Ensure server is running
            if not await self.initialize_device_server(device_serial):
                logger.error(f"Cannot create session - server not available for {device_serial}")
                return None
            
            server = self._servers[device_serial]
            server_url = server.config.get_server_url()
            
            # Get capabilities
            options = UiAutomator2Options()
            capabilities = server.config.get_capabilities(app_package)
            
            for key, value in capabilities.items():
                options.set_capability(key, value)
            
            logger.info(f"Creating WebDriver session for device {device_serial}")
            
            # Create WebDriver instance
            driver = webdriver.Remote(server_url, options=options)
            
            # Inject fingerprint if provided
            if fingerprint_script and app_package == 'com.android.chrome':
                try:
                    await self._inject_fingerprint(driver, fingerprint_script)
                except Exception as e:
                    logger.warning(f"Failed to inject fingerprint: {e}")
            
            # Create session record
            session_id = f"session_{device_serial}_{int(time.time())}"
            session = WebDriverSession(
                session_id=session_id,
                device_serial=device_serial,
                driver=driver,
                app_package=app_package,
                created_at=datetime.now(timezone.utc),
                last_activity=datetime.now(timezone.utc)
            )
            
            self._sessions[session_id] = session
            
            logger.info(f"WebDriver session created: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session for device {device_serial}: {e}")
            return None
    
    async def _inject_fingerprint(self, driver: Any, fingerprint_script: str):
        """Inject fingerprint script into Chrome"""
        try:
            # Switch to web context if needed
            contexts = driver.contexts
            for context in contexts:
                if 'WEBVIEW' in context or 'CHROME' in context:
                    driver.switch_to.context(context)
                    break
            
            # Execute fingerprint injection script
            driver.execute_script(fingerprint_script)
            logger.debug("Fingerprint injected successfully")
            
        except Exception as e:
            logger.error(f"Error injecting fingerprint: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[WebDriverSession]:
        """Get active session by ID"""
        session = self._sessions.get(session_id)
        if session and session.is_active():
            session.update_activity()
            return session
        elif session:
            # Session exists but is not active, clean it up
            await self.close_session(session_id)
        return None
    
    async def close_session(self, session_id: str) -> bool:
        """Close WebDriver session"""
        try:
            session = self._sessions.get(session_id)
            if not session:
                logger.debug(f"Session {session_id} not found")
                return True
            
            logger.info(f"Closing session {session_id}")
            
            # Quit WebDriver
            if session.driver:
                try:
                    session.driver.quit()
                except:
                    pass  # Ignore errors when quitting
            
            # Remove from sessions
            del self._sessions[session_id]
            
            logger.info(f"Session {session_id} closed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error closing session {session_id}: {e}")
            return False
    
    async def navigate_to_url(self, session_id: str, url: str) -> bool:
        """Navigate session to URL"""
        try:
            session = await self.get_session(session_id)
            if not session:
                logger.error(f"Session {session_id} not found or inactive")
                return False
            
            logger.info(f"Navigating session {session_id} to {url}")
            session.driver.get(url)
            
            # Wait for page load
            WebDriverWait(session.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            logger.info(f"Navigation completed for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Navigation failed for session {session_id}: {e}")
            return False
    
    async def take_screenshot(self, session_id: str, save_path: Optional[str] = None) -> Optional[str]:
        """Take screenshot of current session"""
        try:
            session = await self.get_session(session_id)
            if not session:
                logger.error(f"Session {session_id} not found or inactive")
                return None
            
            if not save_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = f"screenshots/{session.device_serial}_{timestamp}.png"
            
            # Ensure directory exists
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Take screenshot
            session.driver.save_screenshot(save_path)
            
            logger.debug(f"Screenshot saved: {save_path}")
            return save_path
            
        except Exception as e:
            logger.error(f"Screenshot failed for session {session_id}: {e}")
            return None
    
    async def execute_script(self, session_id: str, script: str) -> Any:
        """Execute JavaScript in session"""
        try:
            session = await self.get_session(session_id)
            if not session:
                logger.error(f"Session {session_id} not found or inactive")
                return None
            
            result = session.driver.execute_script(script)
            logger.debug(f"Script executed in session {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Script execution failed for session {session_id}: {e}")
            return None
    
    async def click_element(self, session_id: str, locator: Tuple[str, str], timeout: int = 10) -> bool:
        """Click element in session"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return False
            
            # Wait for element and click
            element = WebDriverWait(session.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            element.click()
            
            logger.debug(f"Clicked element {locator} in session {session_id}")
            return True
            
        except TimeoutException:
            logger.warning(f"Element {locator} not found in session {session_id}")
            return False
        except Exception as e:
            logger.error(f"Click failed for session {session_id}: {e}")
            return False
    
    async def cleanup_inactive_sessions(self):
        """Clean up inactive sessions"""
        inactive_sessions = []
        
        for session_id, session in self._sessions.items():
            if not session.is_active():
                inactive_sessions.append(session_id)
        
        for session_id in inactive_sessions:
            await self.close_session(session_id)
        
        if inactive_sessions:
            logger.info(f"Cleaned up {len(inactive_sessions)} inactive sessions")
    
    async def shutdown_device_server(self, device_serial: str) -> bool:
        """Shutdown Appium server for device"""
        try:
            # Close all sessions for this device
            device_sessions = [
                sid for sid, session in self._sessions.items()
                if session.device_serial == device_serial
            ]
            
            for session_id in device_sessions:
                await self.close_session(session_id)
            
            # Stop server
            if device_serial in self._servers:
                server = self._servers[device_serial]
                await server.stop()
                del self._servers[device_serial]
                logger.info(f"Shut down server for device {device_serial}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error shutting down server for device {device_serial}: {e}")
            return False
    
    async def get_controller_statistics(self) -> Dict[str, Any]:
        """Get controller statistics"""
        active_servers = sum(1 for s in self._servers.values() if s.is_running)
        active_sessions = sum(1 for s in self._sessions.values() if s.is_active())
        
        return {
            'total_servers': len(self._servers),
            'active_servers': active_servers,
            'total_sessions': len(self._sessions),
            'active_sessions': active_sessions,
            'appium_available': APPIUM_AVAILABLE
        }
    
    async def shutdown(self):
        """Shutdown all servers and sessions"""
        try:
            logger.info("Shutting down Appium Controller...")
            
            # Close all sessions
            for session_id in list(self._sessions.keys()):
                await self.close_session(session_id)
            
            # Stop all servers
            for device_serial in list(self._servers.keys()):
                await self.shutdown_device_server(device_serial)
            
            logger.info("Appium Controller shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during Appium Controller shutdown: {e}")


# Global Appium controller instance
_appium_controller: Optional[AppiumController] = None


async def get_appium_controller() -> AppiumController:
    """Get global Appium controller instance"""
    global _appium_controller
    if _appium_controller is None:
        _appium_controller = AppiumController()
    return _appium_controller