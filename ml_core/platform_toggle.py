"""
Platform Toggle System
Independent platform activation/deactivation with dummy/production modes
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import os
from abc import ABC, abstractmethod

# Import platform configurations
try:
    from config import app_settings
except ImportError:
    import sys
    sys.path.append('/workspaces/master')
    from config import app_settings

# Import social extensions
try:
    from social_extensions import SocialPlatform, create_social_orchestrator
except ImportError:
    import sys
    sys.path.append('/workspaces/master')
    from social_extensions import SocialPlatform, create_social_orchestrator

class PlatformMode(Enum):
    DISABLED = "disabled"        # Platform completely disabled
    DUMMY = "dummy"             # Dummy mode for testing
    TESTING = "testing"         # Limited testing mode
    PRODUCTION = "production"   # Full production mode

class PlatformCapability(Enum):
    DATA_ACQUISITION = "data_acquisition"
    CONTENT_CREATION = "content_creation"
    ENGAGEMENT = "engagement"
    ANALYTICS = "analytics"
    AUTOMATION = "automation"
    MONITORING = "monitoring"

class PlatformStatus(Enum):
    INACTIVE = "inactive"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class PlatformConfiguration:
    platform_id: str
    platform_name: str
    mode: PlatformMode
    status: PlatformStatus
    enabled_capabilities: Set[PlatformCapability]
    configuration: Dict[str, Any]
    credentials: Dict[str, str]
    rate_limits: Dict[str, int]
    last_activated: Optional[datetime]
    last_error: Optional[str]
    performance_metrics: Dict[str, float]

@dataclass
class CapabilityConfig:
    capability: PlatformCapability
    enabled: bool
    configuration: Dict[str, Any]
    rate_limit: int
    last_used: Optional[datetime]
    usage_count: int = 0
    error_count: int = 0

class PlatformController(ABC):
    """Abstract base class for platform controllers"""
    
    def __init__(self, platform_id: str, config: PlatformConfiguration):
        self.platform_id = platform_id
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.Controller.{platform_id}")
        self.capabilities = {}
        self.is_initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the platform controller"""
        pass
    
    @abstractmethod
    async def activate(self) -> bool:
        """Activate the platform"""
        pass
    
    @abstractmethod
    async def deactivate(self) -> bool:
        """Deactivate the platform"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        pass
    
    async def enable_capability(self, capability: PlatformCapability) -> bool:
        """Enable a specific capability"""
        try:
            if capability not in self.config.enabled_capabilities:
                self.config.enabled_capabilities.add(capability)
                await self._setup_capability(capability)
                self.logger.info(f"✅ Enabled capability {capability.value} for {self.platform_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"❌ Failed to enable capability {capability.value}: {e}")
            return False
    
    async def disable_capability(self, capability: PlatformCapability) -> bool:
        """Disable a specific capability"""
        try:
            if capability in self.config.enabled_capabilities:
                self.config.enabled_capabilities.remove(capability)
                await self._teardown_capability(capability)
                self.logger.info(f"❌ Disabled capability {capability.value} for {self.platform_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"❌ Failed to disable capability {capability.value}: {e}")
            return False
    
    @abstractmethod
    async def _setup_capability(self, capability: PlatformCapability):
        """Setup specific capability"""
        pass
    
    @abstractmethod
    async def _teardown_capability(self, capability: PlatformCapability):
        """Teardown specific capability"""
        pass

class InstagramController(PlatformController):
    """Instagram platform controller"""
    
    def __init__(self, config: PlatformConfiguration):
        super().__init__("instagram", config)
        self.api_client = None
        self.automation_engine = None
    
    async def initialize(self) -> bool:
        """Initialize Instagram controller"""
        try:
            self.logger.info(f"🔄 Initializing Instagram controller in {self.config.mode.value} mode")
            
            if self.config.mode == PlatformMode.DUMMY:
                self.api_client = DummyInstagramClient()
                self.automation_engine = DummyInstagramAutomation()
            elif self.config.mode == PlatformMode.PRODUCTION:
                # Initialize real Instagram components
                self.api_client = await self._create_real_instagram_client()
                self.automation_engine = await self._create_real_instagram_automation()
            
            # Setup enabled capabilities
            for capability in self.config.enabled_capabilities:
                await self._setup_capability(capability)
            
            self.is_initialized = True
            self.config.status = PlatformStatus.ACTIVE
            self.config.last_activated = datetime.now()
            
            self.logger.info("✅ Instagram controller initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Instagram controller: {e}")
            self.config.status = PlatformStatus.ERROR
            self.config.last_error = str(e)
            return False
    
    async def activate(self) -> bool:
        """Activate Instagram platform"""
        if not self.is_initialized:
            await self.initialize()
        
        if self.is_initialized:
            self.config.status = PlatformStatus.ACTIVE
            self.logger.info("🟢 Instagram platform activated")
            return True
        return False
    
    async def deactivate(self) -> bool:
        """Deactivate Instagram platform"""
        self.config.status = PlatformStatus.INACTIVE
        self.logger.info("🔴 Instagram platform deactivated")
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform Instagram health check"""
        health = {
            'platform': 'instagram',
            'status': self.config.status.value,
            'mode': self.config.mode.value,
            'capabilities': list(self.config.enabled_capabilities),
            'last_check': datetime.now().isoformat(),
            'api_status': 'unknown',
            'automation_status': 'unknown',
            'rate_limit_status': {}
        }
        
        try:
            if self.api_client:
                api_health = await self.api_client.health_check()
                health['api_status'] = api_health.get('status', 'unknown')
            
            if self.automation_engine:
                automation_health = await self.automation_engine.health_check()
                health['automation_status'] = automation_health.get('status', 'unknown')
            
            # Check rate limits
            for capability, limit in self.config.rate_limits.items():
                usage = await self._get_capability_usage(capability)
                health['rate_limit_status'][capability] = {
                    'limit': limit,
                    'used': usage,
                    'remaining': max(0, limit - usage)
                }
        
        except Exception as e:
            health['error'] = str(e)
            self.logger.error(f"❌ Instagram health check failed: {e}")
        
        return health
    
    async def _setup_capability(self, capability: PlatformCapability):
        """Setup Instagram capability"""
        if capability == PlatformCapability.DATA_ACQUISITION:
            await self._setup_data_acquisition()
        elif capability == PlatformCapability.CONTENT_CREATION:
            await self._setup_content_creation()
        elif capability == PlatformCapability.ENGAGEMENT:
            await self._setup_engagement()
        elif capability == PlatformCapability.ANALYTICS:
            await self._setup_analytics()
        elif capability == PlatformCapability.AUTOMATION:
            await self._setup_automation()
        elif capability == PlatformCapability.MONITORING:
            await self._setup_monitoring()
    
    async def _teardown_capability(self, capability: PlatformCapability):
        """Teardown Instagram capability"""
        self.logger.info(f"🔄 Tearing down Instagram capability: {capability.value}")
    
    async def _setup_data_acquisition(self):
        """Setup Instagram data acquisition"""
        self.logger.info("📊 Setting up Instagram data acquisition")
    
    async def _setup_content_creation(self):
        """Setup Instagram content creation"""
        self.logger.info("📝 Setting up Instagram content creation")
    
    async def _setup_engagement(self):
        """Setup Instagram engagement"""
        self.logger.info("❤️ Setting up Instagram engagement")
    
    async def _setup_analytics(self):
        """Setup Instagram analytics"""
        self.logger.info("📈 Setting up Instagram analytics")
    
    async def _setup_automation(self):
        """Setup Instagram automation"""
        self.logger.info("🤖 Setting up Instagram automation")
    
    async def _setup_monitoring(self):
        """Setup Instagram monitoring"""
        self.logger.info("👁️ Setting up Instagram monitoring")
    
    async def _create_real_instagram_client(self):
        """Create real Instagram API client"""
        # This would create actual Instagram API client
        self.logger.info("🔗 Creating real Instagram API client")
        return None  # Placeholder
    
    async def _create_real_instagram_automation(self):
        """Create real Instagram automation engine"""
        # This would create actual Instagram automation
        self.logger.info("🤖 Creating real Instagram automation engine")
        return None  # Placeholder
    
    async def _get_capability_usage(self, capability: str) -> int:
        """Get current capability usage"""
        # This would check actual usage from database/cache
        return 0

class TwitterController(PlatformController):
    """Twitter platform controller"""
    
    def __init__(self, config: PlatformConfiguration):
        super().__init__("twitter", config)
        self.api_client = None
        self.automation_engine = None
    
    async def initialize(self) -> bool:
        """Initialize Twitter controller"""
        try:
            self.logger.info(f"🔄 Initializing Twitter controller in {self.config.mode.value} mode")
            
            if self.config.mode == PlatformMode.DUMMY:
                self.api_client = DummyTwitterClient()
                self.automation_engine = DummyTwitterAutomation()
            elif self.config.mode == PlatformMode.PRODUCTION:
                self.api_client = await self._create_real_twitter_client()
                self.automation_engine = await self._create_real_twitter_automation()
            
            # Setup enabled capabilities
            for capability in self.config.enabled_capabilities:
                await self._setup_capability(capability)
            
            self.is_initialized = True
            self.config.status = PlatformStatus.ACTIVE
            self.config.last_activated = datetime.now()
            
            self.logger.info("✅ Twitter controller initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Twitter controller: {e}")
            self.config.status = PlatformStatus.ERROR
            self.config.last_error = str(e)
            return False
    
    async def activate(self) -> bool:
        """Activate Twitter platform"""
        if not self.is_initialized:
            await self.initialize()
        
        if self.is_initialized:
            self.config.status = PlatformStatus.ACTIVE
            self.logger.info("🟢 Twitter platform activated")
            return True
        return False
    
    async def deactivate(self) -> bool:
        """Deactivate Twitter platform"""
        self.config.status = PlatformStatus.INACTIVE
        self.logger.info("🔴 Twitter platform deactivated")
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform Twitter health check"""
        health = {
            'platform': 'twitter',
            'status': self.config.status.value,
            'mode': self.config.mode.value,
            'capabilities': list(self.config.enabled_capabilities),
            'last_check': datetime.now().isoformat(),
            'api_status': 'unknown',
            'automation_status': 'unknown'
        }
        
        try:
            if self.api_client:
                api_health = await self.api_client.health_check()
                health['api_status'] = api_health.get('status', 'unknown')
            
            if self.automation_engine:
                automation_health = await self.automation_engine.health_check()
                health['automation_status'] = automation_health.get('status', 'unknown')
        
        except Exception as e:
            health['error'] = str(e)
            self.logger.error(f"❌ Twitter health check failed: {e}")
        
        return health
    
    async def _setup_capability(self, capability: PlatformCapability):
        """Setup Twitter capability"""
        self.logger.info(f"🔄 Setting up Twitter capability: {capability.value}")
    
    async def _teardown_capability(self, capability: PlatformCapability):
        """Teardown Twitter capability"""
        self.logger.info(f"🔄 Tearing down Twitter capability: {capability.value}")
    
    async def _create_real_twitter_client(self):
        """Create real Twitter API client"""
        self.logger.info("🔗 Creating real Twitter API client")
        return None  # Placeholder
    
    async def _create_real_twitter_automation(self):
        """Create real Twitter automation engine"""
        self.logger.info("🤖 Creating real Twitter automation engine")
        return None  # Placeholder

class LinkedInController(PlatformController):
    """LinkedIn platform controller"""
    
    def __init__(self, config: PlatformConfiguration):
        super().__init__("linkedin", config)
        self.api_client = None
        self.automation_engine = None
    
    async def initialize(self) -> bool:
        """Initialize LinkedIn controller"""
        try:
            self.logger.info(f"🔄 Initializing LinkedIn controller in {self.config.mode.value} mode")
            
            if self.config.mode == PlatformMode.DUMMY:
                self.api_client = DummyLinkedInClient()
                self.automation_engine = DummyLinkedInAutomation()
            elif self.config.mode == PlatformMode.PRODUCTION:
                self.api_client = await self._create_real_linkedin_client()
                self.automation_engine = await self._create_real_linkedin_automation()
            
            # Setup enabled capabilities
            for capability in self.config.enabled_capabilities:
                await self._setup_capability(capability)
            
            self.is_initialized = True
            self.config.status = PlatformStatus.ACTIVE
            self.config.last_activated = datetime.now()
            
            self.logger.info("✅ LinkedIn controller initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize LinkedIn controller: {e}")
            self.config.status = PlatformStatus.ERROR
            self.config.last_error = str(e)
            return False
    
    async def activate(self) -> bool:
        """Activate LinkedIn platform"""
        if not self.is_initialized:
            await self.initialize()
        
        if self.is_initialized:
            self.config.status = PlatformStatus.ACTIVE
            self.logger.info("🟢 LinkedIn platform activated")
            return True
        return False
    
    async def deactivate(self) -> bool:
        """Deactivate LinkedIn platform"""
        self.config.status = PlatformStatus.INACTIVE
        self.logger.info("🔴 LinkedIn platform deactivated")
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform LinkedIn health check"""
        health = {
            'platform': 'linkedin',
            'status': self.config.status.value,
            'mode': self.config.mode.value,
            'capabilities': list(self.config.enabled_capabilities),
            'last_check': datetime.now().isoformat(),
            'api_status': 'unknown',
            'automation_status': 'unknown'
        }
        
        try:
            if self.api_client:
                api_health = await self.api_client.health_check()
                health['api_status'] = api_health.get('status', 'unknown')
            
            if self.automation_engine:
                automation_health = await self.automation_engine.health_check()
                health['automation_status'] = automation_health.get('status', 'unknown')
        
        except Exception as e:
            health['error'] = str(e)
            self.logger.error(f"❌ LinkedIn health check failed: {e}")
        
        return health
    
    async def _setup_capability(self, capability: PlatformCapability):
        """Setup LinkedIn capability"""
        self.logger.info(f"🔄 Setting up LinkedIn capability: {capability.value}")
    
    async def _teardown_capability(self, capability: PlatformCapability):
        """Teardown LinkedIn capability"""
        self.logger.info(f"🔄 Tearing down LinkedIn capability: {capability.value}")
    
    async def _create_real_linkedin_client(self):
        """Create real LinkedIn API client"""
        self.logger.info("🔗 Creating real LinkedIn API client")
        return None  # Placeholder
    
    async def _create_real_linkedin_automation(self):
        """Create real LinkedIn automation engine"""
        self.logger.info("🤖 Creating real LinkedIn automation engine")
        return None  # Placeholder

class WhatsAppController(PlatformController):
    """WhatsApp platform controller"""
    
    def __init__(self, config: PlatformConfiguration):
        super().__init__("whatsapp", config)
        self.api_client = None
        self.automation_engine = None
    
    async def initialize(self) -> bool:
        """Initialize WhatsApp controller"""
        try:
            self.logger.info(f"🔄 Initializing WhatsApp controller in {self.config.mode.value} mode")
            
            if self.config.mode == PlatformMode.DUMMY:
                self.api_client = DummyWhatsAppClient()
                self.automation_engine = DummyWhatsAppAutomation()
            elif self.config.mode == PlatformMode.PRODUCTION:
                self.api_client = await self._create_real_whatsapp_client()
                self.automation_engine = await self._create_real_whatsapp_automation()
            
            # Setup enabled capabilities
            for capability in self.config.enabled_capabilities:
                await self._setup_capability(capability)
            
            self.is_initialized = True
            self.config.status = PlatformStatus.ACTIVE
            self.config.last_activated = datetime.now()
            
            self.logger.info("✅ WhatsApp controller initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize WhatsApp controller: {e}")
            self.config.status = PlatformStatus.ERROR
            self.config.last_error = str(e)
            return False
    
    async def activate(self) -> bool:
        """Activate WhatsApp platform"""
        if not self.is_initialized:
            await self.initialize()
        
        if self.is_initialized:
            self.config.status = PlatformStatus.ACTIVE
            self.logger.info("🟢 WhatsApp platform activated")
            return True
        return False
    
    async def deactivate(self) -> bool:
        """Deactivate WhatsApp platform"""
        self.config.status = PlatformStatus.INACTIVE
        self.logger.info("🔴 WhatsApp platform deactivated")
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform WhatsApp health check"""
        health = {
            'platform': 'whatsapp',
            'status': self.config.status.value,
            'mode': self.config.mode.value,
            'capabilities': list(self.config.enabled_capabilities),
            'last_check': datetime.now().isoformat(),
            'api_status': 'unknown',
            'automation_status': 'unknown'
        }
        
        try:
            if self.api_client:
                api_health = await self.api_client.health_check()
                health['api_status'] = api_health.get('status', 'unknown')
            
            if self.automation_engine:
                automation_health = await self.automation_engine.health_check()
                health['automation_status'] = automation_health.get('status', 'unknown')
        
        except Exception as e:
            health['error'] = str(e)
            self.logger.error(f"❌ WhatsApp health check failed: {e}")
        
        return health
    
    async def _setup_capability(self, capability: PlatformCapability):
        """Setup WhatsApp capability"""
        self.logger.info(f"🔄 Setting up WhatsApp capability: {capability.value}")
    
    async def _teardown_capability(self, capability: PlatformCapability):
        """Teardown WhatsApp capability"""
        self.logger.info(f"🔄 Tearing down WhatsApp capability: {capability.value}")
    
    async def _create_real_whatsapp_client(self):
        """Create real WhatsApp API client"""
        self.logger.info("🔗 Creating real WhatsApp API client")
        return None  # Placeholder
    
    async def _create_real_whatsapp_automation(self):
        """Create real WhatsApp automation engine"""
        self.logger.info("🤖 Creating real WhatsApp automation engine")
        return None  # Placeholder

# Dummy implementations for testing
class DummyInstagramClient:
    async def health_check(self):
        return {'status': 'healthy', 'dummy': True}

class DummyInstagramAutomation:
    async def health_check(self):
        return {'status': 'healthy', 'dummy': True}

class DummyTwitterClient:
    async def health_check(self):
        return {'status': 'healthy', 'dummy': True}

class DummyTwitterAutomation:
    async def health_check(self):
        return {'status': 'healthy', 'dummy': True}

class DummyLinkedInClient:
    async def health_check(self):
        return {'status': 'healthy', 'dummy': True}

class DummyLinkedInAutomation:
    async def health_check(self):
        return {'status': 'healthy', 'dummy': True}

class DummyWhatsAppClient:
    async def health_check(self):
        return {'status': 'healthy', 'dummy': True}

class DummyWhatsAppAutomation:
    async def health_check(self):
        return {'status': 'healthy', 'dummy': True}

class UniversalPlatformToggleSystem:
    """
    Universal Platform Toggle System that manages independent platform activation/deactivation
    """
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "/workspaces/master/config/platform_toggle_config.json"
        self.logger = self._setup_logging()
        
        # Platform controllers
        self.platform_controllers: Dict[str, PlatformController] = {}
        
        # Platform configurations
        self.platform_configs: Dict[str, PlatformConfiguration] = {}
        
        # System state
        self.is_initialized = False
        self.monitoring_active = False
        self.monitoring_task = None
        
        # Global settings
        self.global_mode = PlatformMode.DUMMY  # Default to dummy mode
        self.auto_recovery = True
        self.health_check_interval = 300  # 5 minutes
        
        self.logger.info("⚙️ Universal Platform Toggle System initialized")
    
    async def initialize(self):
        """Initialize the platform toggle system"""
        self.logger.info("🚀 Initializing Universal Platform Toggle System...")
        
        try:
            # Load platform configurations
            await self._load_platform_configurations()
            
            # Initialize platform controllers
            await self._initialize_platform_controllers()
            
            # Start monitoring
            await self._start_monitoring()
            
            self.is_initialized = True
            self.logger.info("✅ Universal Platform Toggle System ready!")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize platform toggle system: {e}")
            raise
    
    async def set_global_mode(self, mode: PlatformMode):
        """Set global mode for all platforms"""
        self.logger.info(f"🌐 Setting global mode to {mode.value}")
        
        self.global_mode = mode
        
        # Update all platform configurations
        for platform_id, config in self.platform_configs.items():
            old_mode = config.mode
            config.mode = mode
            
            if old_mode != mode:
                self.logger.info(f"🔄 Switching {platform_id} from {old_mode.value} to {mode.value}")
                
                # Reinitialize controller with new mode
                if platform_id in self.platform_controllers:
                    await self.platform_controllers[platform_id].deactivate()
                    del self.platform_controllers[platform_id]
                
                # Create new controller with updated config
                controller = await self._create_platform_controller(platform_id, config)
                if controller:
                    self.platform_controllers[platform_id] = controller
        
        # Save updated configurations
        await self._save_platform_configurations()
    
    async def activate_platform(self, platform_id: str) -> bool:
        """Activate a specific platform"""
        if platform_id not in self.platform_controllers:
            self.logger.error(f"❌ Platform {platform_id} not found")
            return False
        
        try:
            controller = self.platform_controllers[platform_id]
            success = await controller.activate()
            
            if success:
                self.logger.info(f"✅ Platform {platform_id} activated successfully")
            else:
                self.logger.error(f"❌ Failed to activate platform {platform_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error activating platform {platform_id}: {e}")
            return False
    
    async def deactivate_platform(self, platform_id: str) -> bool:
        """Deactivate a specific platform"""
        if platform_id not in self.platform_controllers:
            self.logger.error(f"❌ Platform {platform_id} not found")
            return False
        
        try:
            controller = self.platform_controllers[platform_id]
            success = await controller.deactivate()
            
            if success:
                self.logger.info(f"✅ Platform {platform_id} deactivated successfully")
            else:
                self.logger.error(f"❌ Failed to deactivate platform {platform_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error deactivating platform {platform_id}: {e}")
            return False
    
    async def set_platform_mode(self, platform_id: str, mode: PlatformMode) -> bool:
        """Set mode for a specific platform"""
        if platform_id not in self.platform_configs:
            self.logger.error(f"❌ Platform {platform_id} not found")
            return False
        
        try:
            config = self.platform_configs[platform_id]
            old_mode = config.mode
            config.mode = mode
            
            self.logger.info(f"🔄 Setting {platform_id} mode from {old_mode.value} to {mode.value}")
            
            # Reinitialize controller with new mode
            if platform_id in self.platform_controllers:
                await self.platform_controllers[platform_id].deactivate()
                del self.platform_controllers[platform_id]
            
            # Create new controller with updated config
            controller = await self._create_platform_controller(platform_id, config)
            if controller:
                self.platform_controllers[platform_id] = controller
                await self._save_platform_configurations()
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error setting platform {platform_id} mode: {e}")
            return False
    
    async def enable_platform_capability(self, platform_id: str, capability: PlatformCapability) -> bool:
        """Enable a capability for a specific platform"""
        if platform_id not in self.platform_controllers:
            self.logger.error(f"❌ Platform {platform_id} not found")
            return False
        
        try:
            controller = self.platform_controllers[platform_id]
            success = await controller.enable_capability(capability)
            
            if success:
                await self._save_platform_configurations()
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error enabling capability {capability.value} for {platform_id}: {e}")
            return False
    
    async def disable_platform_capability(self, platform_id: str, capability: PlatformCapability) -> bool:
        """Disable a capability for a specific platform"""
        if platform_id not in self.platform_controllers:
            self.logger.error(f"❌ Platform {platform_id} not found")
            return False
        
        try:
            controller = self.platform_controllers[platform_id]
            success = await controller.disable_capability(capability)
            
            if success:
                await self._save_platform_configurations()
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error disabling capability {capability.value} for {platform_id}: {e}")
            return False
    
    async def get_platform_status(self, platform_id: str = None) -> Dict[str, Any]:
        """Get status of specific platform or all platforms"""
        if platform_id:
            if platform_id not in self.platform_controllers:
                return {"error": f"Platform {platform_id} not found"}
            
            controller = self.platform_controllers[platform_id]
            config = self.platform_configs[platform_id]
            
            health = await controller.health_check()
            
            return {
                "platform_id": platform_id,
                "mode": config.mode.value,
                "status": config.status.value,
                "enabled_capabilities": [cap.value for cap in config.enabled_capabilities],
                "last_activated": config.last_activated.isoformat() if config.last_activated else None,
                "last_error": config.last_error,
                "health": health
            }
        else:
            # Return status for all platforms
            all_status = {}
            
            for pid in self.platform_controllers.keys():
                all_status[pid] = await self.get_platform_status(pid)
            
            return {
                "global_mode": self.global_mode.value,
                "monitoring_active": self.monitoring_active,
                "platforms": all_status,
                "system_health": await self._get_system_health()
            }
    
    async def perform_health_check(self, platform_id: str = None) -> Dict[str, Any]:
        """Perform health check on specific platform or all platforms"""
        if platform_id:
            if platform_id not in self.platform_controllers:
                return {"error": f"Platform {platform_id} not found"}
            
            controller = self.platform_controllers[platform_id]
            return await controller.health_check()
        else:
            health_results = {}
            
            for pid, controller in self.platform_controllers.items():
                try:
                    health_results[pid] = await controller.health_check()
                except Exception as e:
                    health_results[pid] = {"error": str(e)}
            
            return health_results
    
    async def get_available_platforms(self) -> List[str]:
        """Get list of available platforms"""
        return list(self.platform_controllers.keys())
    
    async def get_platform_capabilities(self, platform_id: str) -> List[str]:
        """Get available capabilities for a platform"""
        if platform_id not in self.platform_configs:
            return []
        
        config = self.platform_configs[platform_id]
        return [cap.value for cap in config.enabled_capabilities]
    
    # Private methods
    
    async def _load_platform_configurations(self):
        """Load platform configurations from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                
                for platform_id, config_dict in config_data.get('platforms', {}).items():
                    # Convert to PlatformConfiguration object
                    config = PlatformConfiguration(
                        platform_id=config_dict['platform_id'],
                        platform_name=config_dict['platform_name'],
                        mode=PlatformMode(config_dict['mode']),
                        status=PlatformStatus(config_dict['status']),
                        enabled_capabilities={PlatformCapability(cap) for cap in config_dict['enabled_capabilities']},
                        configuration=config_dict['configuration'],
                        credentials=config_dict['credentials'],
                        rate_limits=config_dict['rate_limits'],
                        last_activated=datetime.fromisoformat(config_dict['last_activated']) if config_dict.get('last_activated') else None,
                        last_error=config_dict.get('last_error'),
                        performance_metrics=config_dict.get('performance_metrics', {})
                    )
                    
                    self.platform_configs[platform_id] = config
                
                # Load global settings
                self.global_mode = PlatformMode(config_data.get('global_mode', 'dummy'))
                self.auto_recovery = config_data.get('auto_recovery', True)
                self.health_check_interval = config_data.get('health_check_interval', 300)
                
                self.logger.info(f"📖 Loaded configuration for {len(self.platform_configs)} platforms")
            
            else:
                # Create default configurations
                await self._create_default_configurations()
                await self._save_platform_configurations()
        
        except Exception as e:
            self.logger.error(f"❌ Error loading platform configurations: {e}")
            await self._create_default_configurations()
    
    async def _create_default_configurations(self):
        """Create default platform configurations"""
        default_platforms = {
            'instagram': {
                'platform_name': 'Instagram',
                'enabled_capabilities': [PlatformCapability.DATA_ACQUISITION, PlatformCapability.ENGAGEMENT],
                'rate_limits': {'api_calls': 1000, 'posts': 10, 'follows': 50}
            },
            'twitter': {
                'platform_name': 'Twitter',
                'enabled_capabilities': [PlatformCapability.DATA_ACQUISITION, PlatformCapability.CONTENT_CREATION],
                'rate_limits': {'api_calls': 1500, 'tweets': 20, 'follows': 100}
            },
            'linkedin': {
                'platform_name': 'LinkedIn',
                'enabled_capabilities': [PlatformCapability.DATA_ACQUISITION, PlatformCapability.ENGAGEMENT],
                'rate_limits': {'api_calls': 500, 'posts': 5, 'connections': 20}
            },
            'whatsapp': {
                'platform_name': 'WhatsApp Business',
                'enabled_capabilities': [PlatformCapability.DATA_ACQUISITION, PlatformCapability.AUTOMATION],
                'rate_limits': {'messages': 1000, 'broadcasts': 10}
            }
        }
        
        for platform_id, defaults in default_platforms.items():
            config = PlatformConfiguration(
                platform_id=platform_id,
                platform_name=defaults['platform_name'],
                mode=self.global_mode,
                status=PlatformStatus.INACTIVE,
                enabled_capabilities=set(defaults['enabled_capabilities']),
                configuration={},
                credentials={},
                rate_limits=defaults['rate_limits'],
                last_activated=None,
                last_error=None,
                performance_metrics={}
            )
            
            self.platform_configs[platform_id] = config
        
        self.logger.info(f"📝 Created default configurations for {len(self.platform_configs)} platforms")
    
    async def _save_platform_configurations(self):
        """Save platform configurations to file"""
        try:
            # Ensure config directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            config_data = {
                'global_mode': self.global_mode.value,
                'auto_recovery': self.auto_recovery,
                'health_check_interval': self.health_check_interval,
                'platforms': {}
            }
            
            for platform_id, config in self.platform_configs.items():
                config_data['platforms'][platform_id] = {
                    'platform_id': config.platform_id,
                    'platform_name': config.platform_name,
                    'mode': config.mode.value,
                    'status': config.status.value,
                    'enabled_capabilities': [cap.value for cap in config.enabled_capabilities],
                    'configuration': config.configuration,
                    'credentials': config.credentials,
                    'rate_limits': config.rate_limits,
                    'last_activated': config.last_activated.isoformat() if config.last_activated else None,
                    'last_error': config.last_error,
                    'performance_metrics': config.performance_metrics
                }
            
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            self.logger.info(f"💾 Saved platform configurations to {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Error saving platform configurations: {e}")
    
    async def _initialize_platform_controllers(self):
        """Initialize platform controllers"""
        for platform_id, config in self.platform_configs.items():
            try:
                controller = await self._create_platform_controller(platform_id, config)
                if controller:
                    self.platform_controllers[platform_id] = controller
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize controller for {platform_id}: {e}")
    
    async def _create_platform_controller(self, platform_id: str, config: PlatformConfiguration) -> Optional[PlatformController]:
        """Create platform controller based on platform type"""
        try:
            if platform_id == 'instagram':
                controller = InstagramController(config)
            elif platform_id == 'twitter':
                controller = TwitterController(config)
            elif platform_id == 'linkedin':
                controller = LinkedInController(config)
            elif platform_id == 'whatsapp':
                controller = WhatsAppController(config)
            else:
                self.logger.error(f"❌ Unknown platform type: {platform_id}")
                return None
            
            # Initialize the controller
            await controller.initialize()
            
            return controller
            
        except Exception as e:
            self.logger.error(f"❌ Error creating controller for {platform_id}: {e}")
            return None
    
    async def _start_monitoring(self):
        """Start platform monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("👁️ Started platform monitoring")
    
    async def _stop_monitoring(self):
        """Stop platform monitoring"""
        self.monitoring_active = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("👁️ Stopped platform monitoring")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Perform health checks
                for platform_id, controller in self.platform_controllers.items():
                    try:
                        health = await controller.health_check()
                        
                        # Check for errors and handle auto-recovery
                        if health.get('error') and self.auto_recovery:
                            await self._handle_platform_error(platform_id, health['error'])
                    
                    except Exception as e:
                        self.logger.error(f"❌ Health check failed for {platform_id}: {e}")
                        
                        if self.auto_recovery:
                            await self._handle_platform_error(platform_id, str(e))
                
                # Wait for next check
                await asyncio.sleep(self.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def _handle_platform_error(self, platform_id: str, error_message: str):
        """Handle platform error with auto-recovery"""
        self.logger.warning(f"⚠️ Handling error for {platform_id}: {error_message}")
        
        config = self.platform_configs[platform_id]
        config.last_error = error_message
        config.status = PlatformStatus.ERROR
        
        # Attempt recovery
        try:
            controller = self.platform_controllers[platform_id]
            
            # Deactivate and reactivate
            await controller.deactivate()
            await asyncio.sleep(30)  # Wait before retry
            
            success = await controller.activate()
            
            if success:
                config.status = PlatformStatus.ACTIVE
                config.last_error = None
                self.logger.info(f"✅ Successfully recovered {platform_id}")
            else:
                self.logger.error(f"❌ Failed to recover {platform_id}")
        
        except Exception as e:
            self.logger.error(f"❌ Recovery failed for {platform_id}: {e}")
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        total_platforms = len(self.platform_controllers)
        active_platforms = sum(1 for config in self.platform_configs.values() if config.status == PlatformStatus.ACTIVE)
        error_platforms = sum(1 for config in self.platform_configs.values() if config.status == PlatformStatus.ERROR)
        
        return {
            'total_platforms': total_platforms,
            'active_platforms': active_platforms,
            'error_platforms': error_platforms,
            'health_percentage': (active_platforms / total_platforms * 100) if total_platforms > 0 else 0,
            'monitoring_active': self.monitoring_active,
            'global_mode': self.global_mode.value
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for platform toggle system"""
        logger = logging.getLogger(f"{__name__}.PlatformToggleSystem")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

# Factory function
def create_platform_toggle_system(config_path: str = None) -> UniversalPlatformToggleSystem:
    """Create and return a configured platform toggle system"""
    return UniversalPlatformToggleSystem(config_path)