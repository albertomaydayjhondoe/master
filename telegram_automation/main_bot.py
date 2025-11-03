"""
Main Telegram Bot Orchestrator
Coordinates all modules and manages the overall bot functionality.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from core.listener_module import TelegramListener, ViralContent, EngagementPattern
from core.executor_module import TaskExecutor, Task, TaskPriority
from core.priority_engine import PriorityEngine
from core.metrics_collector import MetricsCollector
from core.message_generator import MessageGenerator
from core.multi_account_manager import MultiAccountManager
from config.telegram_config import TelegramConfig
from database.models import User, EngagementTask, Metrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramBot:
    """
    Main Telegram Bot orchestrator that coordinates all modules.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = TelegramConfig(config_path)
        
        # Initialize modules
        self.listener = TelegramListener(self.config.listener_config)
        self.executor = TaskExecutor(self.config.executor_config)
        self.priority_engine = PriorityEngine(self.config.priority_config)
        self.metrics_collector = MetricsCollector(self.config.metrics_config)
        self.message_generator = MessageGenerator(self.config.message_config)
        self.account_manager = MultiAccountManager(self.config.account_config)
        
        # Bot state
        self.is_running = False
        self.last_activity = datetime.now()
        self.engagement_exchange_pairs = []
        
        logger.info("Telegram Bot initialized")
    
    async def start(self):
        """Start the bot and all modules."""
        try:
            logger.info("Starting Telegram Bot...")
            
            # Initialize all modules
            await self.listener.start()
            await self.executor.start()
            await self.priority_engine.initialize()
            await self.metrics_collector.start()
            await self.account_manager.initialize()
            
            self.is_running = True
            logger.info("Telegram Bot started successfully")
            
            # Start main loop
            await self._main_loop()
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            await self.stop()
    
    async def stop(self):
        """Stop the bot and cleanup resources."""
        logger.info("Stopping Telegram Bot...")
        self.is_running = False
        
        # Stop all modules
        await self.listener.stop()
        await self.executor.stop()
        await self.metrics_collector.stop()
        await self.account_manager.cleanup()
        
        logger.info("Telegram Bot stopped")
    
    async def _main_loop(self):
        """Main bot operation loop."""
        while self.is_running:
            try:
                # Process viral content detection
                await self._process_viral_content()
                
                # Handle engagement exchange
                await self._handle_engagement_exchange()
                
                # Update priorities and metrics
                await self._update_priorities_and_metrics()
                
                # Manage account health
                await self._manage_account_health()
                
                # Generate automated responses
                await self._handle_automated_responses()
                
                # Wait before next cycle
                await asyncio.sleep(self.config.main_loop_interval)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(30)  # Wait longer on errors
    
    async def _process_viral_content(self):
        """Process detected viral content."""
        try:
            viral_content = await self.listener.get_recent_viral_content()
            
            for content in viral_content:
                # Calculate priority for this content
                priority_score = await self.priority_engine.calculate_priority({
                    'content_type': content.content_type,
                    'engagement_rate': content.engagement_rate,
                    'platform': content.platform,
                    'author_followers': content.author_followers,
                    'viral_score': content.viral_score
                })
                
                # Create engagement task if priority is high enough
                if priority_score > self.config.min_viral_priority:
                    task = Task(
                        task_type='viral_engagement',
                        platform=content.platform,
                        target_id=content.content_id,
                        priority=TaskPriority.HIGH if priority_score > 0.8 else TaskPriority.MEDIUM,
                        metadata={
                            'content': content.to_dict(),
                            'priority_score': priority_score
                        }
                    )
                    
                    await self.executor.add_task(task)
                    logger.info(f"Added viral engagement task for {content.platform}: {content.content_id}")
            
        except Exception as e:
            logger.error(f"Error processing viral content: {e}")
    
    async def _handle_engagement_exchange(self):
        """Handle user engagement exchange requests."""
        try:
            engagement_patterns = await self.listener.get_engagement_opportunities()
            
            for pattern in engagement_patterns:
                if pattern.pattern_type == 'exchange_request':
                    # Process engagement exchange
                    await self._process_exchange_request(pattern)
                elif pattern.pattern_type == 'viral_opportunity':
                    # Process viral opportunity
                    await self._process_viral_opportunity(pattern)
            
        except Exception as e:
            logger.error(f"Error handling engagement exchange: {e}")
    
    async def _process_exchange_request(self, pattern: EngagementPattern):
        """Process an engagement exchange request."""
        try:
            user_id = pattern.user_id
            
            # Get user preferences and history
            user_metrics = await self.metrics_collector.get_user_metrics(user_id)
            
            # Calculate optimal exchange parameters
            exchange_params = await self.priority_engine.calculate_exchange_parameters(
                user_metrics, pattern.metadata
            )
            
            # Create reciprocal tasks
            for platform, actions in exchange_params.items():
                for action in actions:
                    task = Task(
                        task_type=action['type'],
                        platform=platform,
                        target_id=action['target'],
                        priority=TaskPriority.MEDIUM,
                        user_id=user_id,
                        metadata=action.get('metadata', {})
                    )
                    
                    await self.executor.add_task(task)
            
            # Send confirmation message
            confirmation_msg = await self.message_generator.generate_message(
                'exchange_confirmation',
                {
                    'user_id': user_id,
                    'exchange_params': exchange_params,
                    'estimated_completion': exchange_params.get('completion_time', '30 minutes')
                }
            )
            
            await self.listener.send_message(user_id, confirmation_msg)
            
        except Exception as e:
            logger.error(f"Error processing exchange request: {e}")
    
    async def _process_viral_opportunity(self, pattern: EngagementPattern):
        """Process a viral opportunity pattern."""
        try:
            # Notify relevant users about the opportunity
            eligible_users = await self._get_eligible_users_for_viral(pattern)
            
            for user_id in eligible_users:
                # Generate personalized notification
                notification = await self.message_generator.generate_message(
                    'viral_opportunity',
                    {
                        'user_id': user_id,
                        'opportunity': pattern.to_dict(),
                        'potential_reward': pattern.metadata.get('potential_reward', 'High')
                    }
                )
                
                await self.listener.send_message(user_id, notification)
            
        except Exception as e:
            logger.error(f"Error processing viral opportunity: {e}")
    
    async def _get_eligible_users_for_viral(self, pattern: EngagementPattern) -> List[int]:
        """Get users eligible for a viral opportunity."""
        try:
            # Get active users with relevant preferences
            active_users = await self.metrics_collector.get_active_users(
                platform=pattern.platform,
                min_activity_score=0.3
            )
            
            eligible_users = []
            for user_id in active_users:
                user_metrics = await self.metrics_collector.get_user_metrics(user_id)
                
                # Check if user is interested in this type of content
                if self._is_user_interested(user_metrics, pattern):
                    eligible_users.append(user_id)
            
            return eligible_users[:10]  # Limit to top 10 users
            
        except Exception as e:
            logger.error(f"Error getting eligible users: {e}")
            return []
    
    def _is_user_interested(self, user_metrics: Dict[str, Any], pattern: EngagementPattern) -> bool:
        """Check if user would be interested in this pattern."""
        try:
            # Check platform preference
            if pattern.platform not in user_metrics.get('preferred_platforms', []):
                return False
            
            # Check content type preference
            user_interests = user_metrics.get('content_interests', [])
            pattern_tags = pattern.metadata.get('tags', [])
            
            if not any(tag in user_interests for tag in pattern_tags):
                return False
            
            # Check engagement level
            if user_metrics.get('activity_score', 0) < 0.3:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking user interest: {e}")
            return False
    
    async def _update_priorities_and_metrics(self):
        """Update priorities and collect metrics."""
        try:
            # Update task priorities based on current data
            await self.executor.update_task_priorities()
            
            # Collect and update metrics
            await self.metrics_collector.collect_metrics()
            
            # Update priority engine with new data
            recent_metrics = await self.metrics_collector.get_recent_metrics()
            await self.priority_engine.update_with_metrics(recent_metrics)
            
        except Exception as e:
            logger.error(f"Error updating priorities and metrics: {e}")
    
    async def _manage_account_health(self):
        """Manage account health and rotation."""
        try:
            # Check account health
            health_report = await self.account_manager.check_all_accounts_health()
            
            # Handle any issues
            for platform, accounts in health_report.items():
                for account_id, health_data in accounts.items():
                    if health_data['status'] == 'unhealthy':
                        await self.account_manager.handle_unhealthy_account(
                            platform, account_id, health_data
                        )
            
            # Rotate accounts if needed
            await self.account_manager.rotate_accounts_if_needed()
            
        except Exception as e:
            logger.error(f"Error managing account health: {e}")
    
    async def _handle_automated_responses(self):
        """Handle automated responses and notifications."""
        try:
            # Get pending messages
            pending_messages = await self.listener.get_pending_responses()
            
            for message_data in pending_messages:
                # Generate appropriate response
                response = await self.message_generator.generate_message(
                    message_data['type'],
                    message_data['context']
                )
                
                if response:
                    await self.listener.send_message(
                        message_data['user_id'],
                        response
                    )
            
        except Exception as e:
            logger.error(f"Error handling automated responses: {e}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            return {
                'bot_status': 'running' if self.is_running else 'stopped',
                'last_activity': self.last_activity,
                'modules': {
                    'listener': await self.listener.get_status(),
                    'executor': await self.executor.get_status(),
                    'priority_engine': await self.priority_engine.get_status(),
                    'metrics_collector': await self.metrics_collector.get_status(),
                    'account_manager': await self.account_manager.get_status()
                },
                'performance': await self.metrics_collector.get_system_performance(),
                'active_tasks': await self.executor.get_active_task_count(),
                'managed_accounts': await self.account_manager.get_account_count()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}


async def main():
    """Main entry point for the bot."""
    bot = TelegramBot()
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal...")
        await bot.stop()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())