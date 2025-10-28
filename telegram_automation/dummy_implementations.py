"""
Dummy implementations for external dependencies in development mode
Allows the project to run without installing heavy dependencies like Selenium, Telethon, etc.
"""
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
import asyncio
import random

logger = logging.getLogger(__name__)

# =============================================================================
# SELENIUM DUMMY IMPLEMENTATIONS
# =============================================================================

class DummyWebDriver:
    """Dummy WebDriver for development mode"""
    
    def __init__(self, *args, **kwargs):
        self.current_url = "https://www.youtube.com"
        self.page_source = "<html><body>Dummy YouTube page</body></html>"
        logger.info("🎭 Dummy WebDriver initialized")
    
    def get(self, url: str):
        self.current_url = url
        logger.info(f"🎭 Dummy navigation to: {url}")
        return None
    
    def find_element(self, by, value):
        return DummyWebElement()
    
    def find_elements(self, by, value):
        return [DummyWebElement() for _ in range(random.randint(0, 3))]
    
    def execute_script(self, script: str, *args):
        if "paused" in script:
            return False  # Video is playing
        logger.info(f"🎭 Dummy script execution: {script[:50]}...")
        return True
    
    def quit(self):
        logger.info("🎭 Dummy WebDriver quit")
    
    def set_page_load_timeout(self, timeout):
        pass
    
    def implicitly_wait(self, timeout):
        pass

class DummyWebElement:
    """Dummy WebElement for development mode"""
    
    def __init__(self):
        self.text = "Dummy Element"
        self._displayed = True
        self._enabled = True
    
    def click(self):
        logger.info(f"🎭 Dummy click on element: {self.text}")
    
    def send_keys(self, keys):
        logger.info(f"🎭 Dummy send keys: {keys}")
    
    def clear(self):
        logger.info("🎭 Dummy clear element")
    
    def is_displayed(self):
        return self._displayed
    
    def is_enabled(self):
        return self._enabled
    
    def get_attribute(self, name):
        if name == "aria-pressed":
            return "false"
        elif name == "href":
            return "https://www.youtube.com/channel/dummy"
        return f"dummy_{name}"

class DummyBy:
    """Dummy By locators"""
    ID = "id"
    CSS_SELECTOR = "css selector"
    XPATH = "xpath"
    CLASS_NAME = "class name"
    TAG_NAME = "tag name"

class DummyWebDriverWait:
    """Dummy WebDriverWait"""
    
    def __init__(self, driver, timeout):
        self.driver = driver
        self.timeout = timeout
    
    def until(self, condition):
        return DummyWebElement()

class DummyExpectedConditions:
    """Dummy Expected Conditions"""
    
    @staticmethod
    def presence_of_element_located(locator):
        return lambda driver: DummyWebElement()
    
    @staticmethod
    def element_to_be_clickable(locator):
        return lambda driver: DummyWebElement()

class DummyKeys:
    """Dummy Keys"""
    ENTER = "\n"
    SPACE = " "
    TAB = "\t"

class DummyOptions:
    """Dummy Chrome Options"""
    
    def __init__(self):
        self.arguments = []
        self.experimental_options = {}
    
    def add_argument(self, argument):
        self.arguments.append(argument)
    
    def add_experimental_option(self, name, value):
        self.experimental_options[name] = value

class DummyTimeoutException(Exception):
    """Dummy TimeoutException"""
    pass

class DummyWebDriverException(Exception):
    """Dummy WebDriverException"""
    pass

# =============================================================================
# TELETHON DUMMY IMPLEMENTATIONS
# =============================================================================

class DummyTelegramClient:
    """Dummy Telegram Client for development mode"""
    
    def __init__(self, session_name, api_id, api_hash):
        self.session_name = session_name
        self.api_id = api_id
        self.api_hash = api_hash
        self.is_connected = False
        logger.info("🎭 Dummy Telegram Client initialized")
    
    async def start(self, phone=None, password=None):
        self.is_connected = True
        logger.info("🎭 Dummy Telegram Client started")
    
    async def disconnect(self):
        self.is_connected = False
        logger.info("🎭 Dummy Telegram Client disconnected")
    
    async def get_me(self):
        return DummyUser()
    
    async def get_dialogs(self):
        return [DummyChat() for _ in range(5)]
    
    async def send_message(self, entity, message):
        logger.info(f"🎭 Dummy message sent to {entity}: {message[:50]}...")
        return DummyMessage()
    
    def on(self, event):
        """Decorator for event handlers"""
        def decorator(func):
            logger.info(f"🎭 Dummy event handler registered: {func.__name__}")
            return func
        return decorator
    
    async def run_until_disconnected(self):
        logger.info("🎭 Dummy client running until disconnected")
        while self.is_connected:
            await asyncio.sleep(1)

class DummyUser:
    """Dummy Telegram User"""
    
    def __init__(self):
        self.id = 123456789
        self.first_name = "Dummy"
        self.last_name = "User"
        self.username = "dummyuser"
        self.phone = "+1234567890"

class DummyChat:
    """Dummy Telegram Chat"""
    
    def __init__(self):
        self.id = random.randint(100000, 999999)
        self.title = f"Dummy Chat {self.id}"
        self.name = self.title

class DummyChannel:
    """Dummy Telegram Channel"""
    
    def __init__(self):
        self.id = random.randint(1000000, 9999999)
        self.title = f"Dummy Channel {self.id}"
        self.username = f"dummychannel{self.id}"

class DummyMessage:
    """Dummy Telegram Message"""
    
    def __init__(self):
        self.id = random.randint(1, 1000000)
        self.text = "Dummy message"
        self.date = datetime.now()
        self.sender_id = 123456789

class DummyFloodWaitError(Exception):
    """Dummy FloodWaitError"""
    
    def __init__(self, seconds):
        self.seconds = seconds
        super().__init__(f"Flood wait for {seconds} seconds")

class DummyPeerFloodError(Exception):
    """Dummy PeerFloodError"""
    pass

class DummyEvents:
    """Dummy Telethon Events"""
    
    class NewMessage:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
        
        def __call__(self, func):
            return func

    @staticmethod  
    def NewMessage(**kwargs):
        return DummyEvents.NewMessage(**kwargs)

# =============================================================================
# DATABASE DUMMY IMPLEMENTATIONS  
# =============================================================================

class DummyAsyncpgConnection:
    """Dummy asyncpg connection"""
    
    async def execute(self, query, *args):
        logger.info(f"🎭 Dummy SQL execute: {query[:50]}...")
        return "SELECT 1"
    
    async def fetch(self, query, *args):
        logger.info(f"🎭 Dummy SQL fetch: {query[:50]}...")
        return []
    
    async def fetchrow(self, query, *args):
        logger.info(f"🎭 Dummy SQL fetchrow: {query[:50]}...")
        return None
    
    async def close(self):
        logger.info("🎭 Dummy database connection closed")

async def dummy_asyncpg_connect(*args, **kwargs):
    """Dummy asyncpg connect function"""
    logger.info("🎭 Dummy database connection established")
    return DummyAsyncpgConnection()

# =============================================================================
# HTTP CLIENT DUMMY IMPLEMENTATIONS
# =============================================================================

class DummyResponse:
    """Dummy HTTP Response"""
    
    def __init__(self, status=200, json_data=None, text="OK"):
        self.status = status
        self.status_code = status
        self._json_data = json_data or {}
        self._text = text
    
    async def json(self):
        return self._json_data
    
    async def text(self):
        return self._text
    
    def json(self):  # Sync version for requests
        return self._json_data
    
    @property
    def text(self):  # Property for requests
        return self._text

class DummyClientSession:
    """Dummy aiohttp ClientSession"""
    
    async def get(self, url, **kwargs):
        logger.info(f"🎭 Dummy GET request to: {url}")
        return DummyResponse()
    
    async def post(self, url, **kwargs):
        logger.info(f"🎭 Dummy POST request to: {url}")
        return DummyResponse()
    
    async def close(self):
        logger.info("🎭 Dummy HTTP session closed")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

# =============================================================================
# FACTORY FUNCTIONS FOR DUMMY MODE
# =============================================================================

def get_dummy_implementations():
    """Return dictionary of dummy implementations for imports"""
    return {
        # Selenium
        'selenium.webdriver': type('DummyWebDriverModule', (), {
            'Chrome': DummyWebDriver,
            'Firefox': DummyWebDriver,
            'Safari': DummyWebDriver,
        }),
        'selenium.webdriver.common.by': type('DummyByModule', (), {'By': DummyBy}),
        'selenium.webdriver.support.ui': type('DummyUIModule', (), {'WebDriverWait': DummyWebDriverWait}),
        'selenium.webdriver.support': type('DummySupportModule', (), {'expected_conditions': DummyExpectedConditions}),
        'selenium.webdriver.common.keys': type('DummyKeysModule', (), {'Keys': DummyKeys}),
        'selenium.webdriver.chrome.options': type('DummyOptionsModule', (), {'Options': DummyOptions}),
        'selenium.common.exceptions': type('DummyExceptionsModule', (), {
            'TimeoutException': DummyTimeoutException,
            'WebDriverException': DummyWebDriverException,
        }),
        
        # Telethon
        'telethon': type('DummyTelethonModule', (), {
            'TelegramClient': DummyTelegramClient,
            'events': DummyEvents,
        }),
        'telethon.tl.types': type('DummyTypesModule', (), {
            'User': DummyUser,
            'Chat': DummyChat, 
            'Channel': DummyChannel,
        }),
        'telethon.errors': type('DummyErrorsModule', (), {
            'FloodWaitError': DummyFloodWaitError,
            'PeerFloodError': DummyPeerFloodError,
        }),
        
        # Database
        'asyncpg': type('DummyAsyncpgModule', (), {
            'connect': dummy_asyncpg_connect,
        }),
        
        # HTTP
        'aiohttp': type('DummyAiohttpModule', (), {
            'ClientSession': DummyClientSession,
        }),
    }