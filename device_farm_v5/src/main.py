"""
Device Farm v5 - Main Application Entry Point
Orchestrates all system components for Android device automation
"""
import asyncio
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from loguru import logger

# Import core components
from src.config_manager import get_config, validate_configuration
from src.core.models import get_db_manager
from src.core.adb_manager import get_adb_manager
from src.core.appium_controller import get_appium_controller
from src.core.profile_synchronizer import get_profile_synchronizer
from src.core.task_queue import get_task_queue
from src.integrations.gologin_manager import get_gologin_manager
from src.integrations.tiktok_ml_adapter import get_tiktok_ml_adapter


class DeviceFarmSystem:
    """Main system orchestrator for Device Farm v5"""
    
    def __init__(self):
        self.config = get_config()
        self.running = False
        self.components = {}
        
        # Setup logging
        self._setup_logging()
        
        logger.info("Device Farm v5 System initializing...")
    
    def _setup_logging(self):
        """Configure logging system"""
        log_level = self.config.log_level
        log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
        
        # Remove default handler
        logger.remove()
        
        # Console logging
        logger.add(
            sys.stdout,
            level=log_level,
            format=log_format,
            colorize=True
        )
        
        # File logging
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logger.add(
            log_dir / "device_farm_v5.log",
            level=log_level,
            format=log_format,
            rotation="100 MB",
            retention="7 days",
            compression="gz"
        )
        
        logger.info("Logging system configured")
    
    async def initialize(self) -> bool:
        """Initialize all system components"""
        try:
            logger.info("🚀 Initializing Device Farm v5 System...")
            
            # Validate configuration
            if not validate_configuration():
                logger.error("❌ Configuration validation failed")
                return False
            
            logger.info("✅ Configuration validated")
            
            # Initialize database
            logger.info("📊 Initializing database...")
            db_manager = get_db_manager()
            if not db_manager.health_check():
                logger.error("❌ Database health check failed")
                return False
            
            self.components['database'] = db_manager
            logger.info("✅ Database initialized")
            
            # Initialize ADB manager
            logger.info("📱 Initializing ADB manager...")
            adb_manager = await get_adb_manager()
            self.components['adb'] = adb_manager
            logger.info("✅ ADB manager initialized")
            
            # Initialize Appium controller
            logger.info("🤖 Initializing Appium controller...")
            appium_controller = await get_appium_controller()
            self.components['appium'] = appium_controller
            logger.info("✅ Appium controller initialized")
            
            # Initialize Gologin manager
            logger.info("🔗 Initializing Gologin manager...")
            gologin_manager = await get_gologin_manager()
            self.components['gologin'] = gologin_manager
            logger.info("✅ Gologin manager initialized")
            
            # Initialize Profile Synchronizer
            logger.info("🔄 Initializing Profile Synchronizer...")
            profile_synchronizer = await get_profile_synchronizer()
            self.components['profile_sync'] = profile_synchronizer
            logger.info("✅ Profile Synchronizer initialized")
            
            # Initialize Task Queue
            logger.info("📋 Initializing Task Queue...")
            task_queue = await get_task_queue()
            self.components['task_queue'] = task_queue
            logger.info("✅ Task Queue initialized")
            
            # Initialize TikTok ML Integration Adapter
            logger.info("🤖 Initializing TikTok ML Integration...")
            tiktok_adapter = await get_tiktok_ml_adapter()
            self.components['tiktok_ml'] = tiktok_adapter
            logger.info("✅ TikTok ML Integration initialized")
            
            # Perform initial system checks
            await self._perform_system_checks()
            
            logger.info("🎉 Device Farm v5 System initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ System initialization failed: {e}")
            return False
    
    async def _perform_system_checks(self):
        """Perform initial system health checks"""
        logger.info("🔍 Performing system health checks...")
        
        # Check device connectivity
        adb_manager = self.components.get('adb')
        if adb_manager:
            devices = await adb_manager.scan_devices()
            logger.info(f"📱 Detected {len(devices)} Android devices")
            
            for device in devices:
                logger.info(f"   • {device.serial} - {device.model} (Android {device.android_version})")
        
        # Check Gologin connectivity
        gologin_manager = self.components.get('gologin')
        if gologin_manager:
            try:
                profiles = await gologin_manager.get_profiles()
                logger.info(f"🔗 Found {len(profiles)} Gologin profiles")
            except Exception as e:
                logger.warning(f"⚠️  Gologin API issue: {e}")
        
        # Check Appium status
        appium_controller = self.components.get('appium')
        if appium_controller:
            stats = await appium_controller.get_controller_statistics()
            logger.info(f"🤖 Appium controller status: {stats}")
    
    async def start_services(self):
        """Start all system services"""
        try:
            logger.info("🚀 Starting Device Farm v5 services...")
            
            # Start background tasks
            tasks = []
            
            # Health monitoring task
            tasks.append(asyncio.create_task(self._health_monitor()))
            
            # Device scanning task
            tasks.append(asyncio.create_task(self._device_scanner()))
            
            # Session cleanup task
            tasks.append(asyncio.create_task(self._session_cleaner()))
            
            # Start dashboard (if enabled)
            if self.config.raw_config.get('dashboard', {}).get('enabled', True):
                tasks.append(asyncio.create_task(self._start_dashboard()))
            
            self.running = True
            logger.info("✅ All services started successfully")
            
            # Wait for tasks
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ Error starting services: {e}")
            raise
    
    async def _health_monitor(self):
        """Monitor system health"""
        logger.info("💚 Health monitor started")
        
        while self.running:
            try:
                # Check component health
                db_healthy = self.components.get('database', {}).health_check() if 'database' in self.components else False
                
                # Log health status
                if not db_healthy:
                    logger.warning("⚠️  Database health check failed")
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Health monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _device_scanner(self):
        """Periodically scan for devices"""
        logger.info("📱 Device scanner started")
        
        while self.running:
            try:
                adb_manager = self.components.get('adb')
                if adb_manager:
                    await adb_manager.scan_devices()
                
                # Wait before next scan
                await asyncio.sleep(30)  # Scan every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Device scanner error: {e}")
                await asyncio.sleep(30)
    
    async def _session_cleaner(self):
        """Clean up inactive sessions"""
        logger.info("🧹 Session cleaner started")
        
        while self.running:
            try:
                appium_controller = self.components.get('appium')
                if appium_controller:
                    await appium_controller.cleanup_inactive_sessions()
                
                # Wait before next cleanup
                await asyncio.sleep(300)  # Clean every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Session cleaner error: {e}")
                await asyncio.sleep(300)
    
    async def _start_dashboard(self):
        """Start web dashboard"""
        try:
            logger.info("🎛️  Starting web dashboard...")
            
            # Import dashboard here to avoid circular imports
            from src.dashboard.app import create_dashboard_app
            
            app = create_dashboard_app()
            
            # Run dashboard (this will block)
            import uvicorn
            
            config = uvicorn.Config(
                app,
                host=self.config.dashboard.host,
                port=self.config.dashboard.port,
                log_level="info"
            )
            
            server = uvicorn.Server(config)
            await server.serve()
            
        except Exception as e:
            logger.error(f"❌ Dashboard error: {e}")
    
    async def shutdown(self):
        """Graceful shutdown of all components"""
        logger.info("🛑 Shutting down Device Farm v5 System...")
        
        self.running = False
        
        try:
            # Shutdown Appium controller
            appium_controller = self.components.get('appium')
            if appium_controller:
                await appium_controller.shutdown()
                logger.info("✅ Appium controller shut down")
            
            # Close Gologin manager
            gologin_manager = self.components.get('gologin')
            if gologin_manager:
                await gologin_manager.close()
                logger.info("✅ Gologin manager closed")
            
            logger.info("✅ Device Farm v5 System shut down gracefully")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")


# Global system instance
device_farm_system: Optional[DeviceFarmSystem] = None


def get_system() -> DeviceFarmSystem:
    """Get global system instance"""
    global device_farm_system
    if device_farm_system is None:
        device_farm_system = DeviceFarmSystem()
    return device_farm_system


async def main():
    """Main application entry point"""
    system = get_system()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating shutdown...")
        asyncio.create_task(system.shutdown())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize system
        if not await system.initialize():
            logger.error("❌ System initialization failed")
            sys.exit(1)
        
        # Start services
        await system.start_services()
        
    except KeyboardInterrupt:
        logger.info("🛑 Received interrupt signal")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
    finally:
        await system.shutdown()


if __name__ == "__main__":
    # Run the main application
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)