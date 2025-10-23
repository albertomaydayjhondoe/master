"""
Main Like4Like Telegram Bot Application
Orchestrates all components of the Like4Like automation system
"""
import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import Optional

from database.models import DatabaseConnection
from bot.telegram_bot import TelegramLike4LikeBot
from bot.conversation_handler import ConversationHandler
from youtube_executor.youtube_executor import YouTubeExecutorService
from youtube_executor.config import load_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/like4like_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class Like4LikeApplication:
    """
    Main application class that coordinates all system components
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.db: Optional[DatabaseConnection] = None
        self.telegram_bot: Optional[TelegramLike4LikeBot] = None
        self.conversation_handler: Optional[ConversationHandler] = None
        self.youtube_service: Optional[YouTubeExecutorService] = None
        
        self.is_running = False
        self.shutdown_event = asyncio.Event()
    
    async def initialize(self):
        """Initialize all system components"""
        try:
            logger.info("🚀 Initializing Like4Like application...")
            
            # Initialize database connection
            self.db = DatabaseConnection(
                host=self.config.get('database', {}).get('host', 'localhost'),
                port=self.config.get('database', {}).get('port', 5432),
                database=self.config.get('database', {}).get('name', 'like4like_bot'),
                user=self.config.get('database', {}).get('user', 'postgres'),
                password=self.config.get('database', {}).get('password', 'postgres')
            )
            
            await self.db.connect()
            logger.info("✅ Database connected")
            
            # Initialize YouTube executor service
            gologin_token = self.config.get('gologin', {}).get('api_token', 'dummy_token')
            self.youtube_service = YouTubeExecutorService(self.db, gologin_token)
            
            # Initialize conversation handler
            self.conversation_handler = ConversationHandler(self.db, self.youtube_service)
            
            # Initialize Telegram bot
            api_id = self.config.get('telegram', {}).get('api_id')
            api_hash = self.config.get('telegram', {}).get('api_hash')
            bot_token = self.config.get('telegram', {}).get('bot_token')
            phone = self.config.get('telegram', {}).get('phone')
            
            if not all([api_id, api_hash]):
                raise ValueError("Missing Telegram API credentials")
            
            self.telegram_bot = TelegramLike4LikeBot(
                api_id=api_id,
                api_hash=api_hash,
                bot_token=bot_token,
                phone=phone,
                db=self.db,
                conversation_handler=self.conversation_handler
            )
            
            logger.info("✅ All components initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize application: {e}")
            raise
    
    async def start(self):
        """Start all system components"""
        try:
            logger.info("🔥 Starting Like4Like application...")
            
            # Start YouTube executor service
            await self.youtube_service.start()
            
            # Start Telegram bot
            await self.telegram_bot.start()
            
            self.is_running = True
            logger.info("✅ Like4Like application started successfully")
            
            # Setup system monitoring tasks
            asyncio.create_task(self.health_monitor())
            asyncio.create_task(self.metrics_collector())
            
        except Exception as e:
            logger.error(f"❌ Failed to start application: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop all system components gracefully"""
        try:
            logger.info("🔄 Stopping Like4Like application...")
            
            self.is_running = False
            self.shutdown_event.set()
            
            # Stop components in reverse order
            if self.telegram_bot:
                await self.telegram_bot.stop()
                logger.info("✅ Telegram bot stopped")
            
            if self.youtube_service:
                await self.youtube_service.stop()
                logger.info("✅ YouTube service stopped")
            
            if self.db:
                await self.db.close()
                logger.info("✅ Database connection closed")
            
            logger.info("✅ Like4Like application stopped gracefully")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")
    
    async def run(self):
        """Run the application until shutdown signal"""
        try:
            await self.start()
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
        except KeyboardInterrupt:
            logger.info("🛑 Received keyboard interrupt")
        except Exception as e:
            logger.error(f"❌ Application error: {e}")
        finally:
            await self.stop()
    
    async def health_monitor(self):
        """Monitor system health and component status"""
        while self.is_running:
            try:
                # Check database health
                db_healthy = await self.check_database_health()
                
                # Check Telegram bot health
                bot_healthy = await self.check_telegram_health()
                
                # Check YouTube service health
                youtube_healthy = await self.check_youtube_health()
                
                # Log health status
                health_status = {
                    'database': db_healthy,
                    'telegram_bot': bot_healthy,
                    'youtube_service': youtube_healthy,
                    'timestamp': datetime.now().isoformat()
                }
                
                if not all(health_status.values()):
                    logger.warning(f"⚠️ Health check failed: {health_status}")
                else:
                    logger.debug(f"✅ Health check passed: {health_status}")
                
                # Save health metrics to database
                await self.save_health_metrics(health_status)
                
                # Wait before next check
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in health monitor: {e}")
                await asyncio.sleep(60)
    
    async def check_database_health(self) -> bool:
        """Check database connection health"""
        try:
            if not self.db:
                return False
            
            # Simple query to test connection
            result = await self.db.execute_query("SELECT 1")
            return result is not None
            
        except Exception as e:
            logger.error(f"❌ Database health check failed: {e}")
            return False
    
    async def check_telegram_health(self) -> bool:
        """Check Telegram bot health"""
        try:
            if not self.telegram_bot:
                return False
            
            return self.telegram_bot.is_connected()
            
        except Exception as e:
            logger.error(f"❌ Telegram health check failed: {e}")
            return False
    
    async def check_youtube_health(self) -> bool:
        """Check YouTube service health"""
        try:
            if not self.youtube_service:
                return False
            
            return self.youtube_service.is_running
            
        except Exception as e:
            logger.error(f"❌ YouTube health check failed: {e}")
            return False
    
    async def save_health_metrics(self, health_status: dict):
        """Save health metrics to database"""
        try:
            query = """
            INSERT INTO system_health (
                database_healthy, telegram_healthy, youtube_healthy, checked_at
            ) VALUES ($1, $2, $3, NOW())
            """
            
            await self.db.execute_command(
                query,
                health_status['database'],
                health_status['telegram_bot'],
                health_status['youtube_service']
            )
            
        except Exception as e:
            logger.error(f"❌ Error saving health metrics: {e}")
    
    async def metrics_collector(self):
        """Collect and aggregate system metrics"""
        while self.is_running:
            try:
                # Collect metrics from different components
                metrics = {
                    'timestamp': datetime.now(),
                    'active_conversations': await self.get_active_conversations_count(),
                    'pending_exchanges': await self.get_pending_exchanges_count(),
                    'completed_exchanges_today': await self.get_completed_exchanges_today(),
                    'youtube_executions_today': await self.get_youtube_executions_today(),
                    'memory_usage': await self.get_memory_usage(),
                    'cpu_usage': await self.get_cpu_usage()
                }
                
                # Save metrics
                await self.save_metrics(metrics)
                
                # Log summary
                logger.info(f"📊 Metrics: {metrics['active_conversations']} conversations, "
                          f"{metrics['pending_exchanges']} pending exchanges, "
                          f"{metrics['completed_exchanges_today']} completed today")
                
                # Wait before next collection
                await asyncio.sleep(3600)  # 1 hour
                
            except Exception as e:
                logger.error(f"❌ Error collecting metrics: {e}")
                await asyncio.sleep(300)
    
    async def get_active_conversations_count(self) -> int:
        """Get count of active conversations"""
        try:
            query = "SELECT COUNT(*) FROM conversation_states WHERE status != 'ENDED'"
            result = await self.db.execute_query(query)
            return result[0]['count'] if result else 0
        except:
            return 0
    
    async def get_pending_exchanges_count(self) -> int:
        """Get count of pending exchanges"""
        try:
            query = "SELECT COUNT(*) FROM exchanges WHERE status IN ('CONFIRMED', 'THEIR_TURN_DONE')"
            result = await self.db.execute_query(query)
            return result[0]['count'] if result else 0
        except:
            return 0
    
    async def get_completed_exchanges_today(self) -> int:
        """Get count of exchanges completed today"""
        try:
            query = """
            SELECT COUNT(*) FROM exchanges 
            WHERE status = 'COMPLETED' 
            AND DATE(created_at) = CURRENT_DATE
            """
            result = await self.db.execute_query(query)
            return result[0]['count'] if result else 0
        except:
            return 0
    
    async def get_youtube_executions_today(self) -> int:
        """Get count of YouTube executions today"""
        try:
            query = """
            SELECT COUNT(*) FROM exchanges 
            WHERE our_execution_completed_at IS NOT NULL
            AND DATE(our_execution_completed_at) = CURRENT_DATE
            """
            result = await self.db.execute_query(query)
            return result[0]['count'] if result else 0
        except:
            return 0
    
    async def get_memory_usage(self) -> float:
        """Get memory usage percentage"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except:
            return 0.0
    
    async def get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except:
            return 0.0
    
    async def save_metrics(self, metrics: dict):
        """Save metrics to database"""
        try:
            query = """
            INSERT INTO system_metrics (
                active_conversations, pending_exchanges, completed_exchanges_today,
                youtube_executions_today, memory_usage, cpu_usage, collected_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            """
            
            await self.db.execute_command(
                query,
                metrics['active_conversations'],
                metrics['pending_exchanges'],
                metrics['completed_exchanges_today'],
                metrics['youtube_executions_today'],
                metrics['memory_usage'],
                metrics['cpu_usage'],
                metrics['timestamp']
            )
            
        except Exception as e:
            logger.error(f"❌ Error saving metrics: {e}")


def setup_signal_handlers(app: Like4LikeApplication):
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"🛑 Received signal {signum}")
        asyncio.create_task(app.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """Main application entry point"""
    try:
        # Load configuration
        config = load_config()
        
        # Add additional config from environment or config files
        config.update({
            'database': {
                'host': 'localhost',
                'port': 5432,
                'name': 'like4like_bot',
                'user': 'postgres',
                'password': 'postgres'
            },
            'telegram': {
                'api_id': 12345,  # Replace with actual values
                'api_hash': 'your_api_hash',
                'bot_token': 'your_bot_token',  # Optional
                'phone': '+1234567890'
            }
        })
        
        # Create and initialize application
        app = Like4LikeApplication(config)
        
        # Setup signal handlers
        setup_signal_handlers(app)
        
        # Initialize and run
        await app.initialize()
        await app.run()
        
    except Exception as e:
        logger.error(f"❌ Application failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    import os
    os.makedirs('logs', exist_ok=True)
    
    # Run the application
    asyncio.run(main())