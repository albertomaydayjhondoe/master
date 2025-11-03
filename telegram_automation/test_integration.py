"""
Integration Test for Complete Telegram Bot System
Tests all modules working together in coordination.
"""

import asyncio
import pytest
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from main_bot import TelegramBot
from core.listener_module import TelegramListener, ViralContent, EngagementPattern
from core.executor_module import TaskExecutor, Task, TaskPriority
from core.priority_engine import PriorityEngine
from core.metrics_collector import MetricsCollector
from core.message_generator import MessageGenerator
from core.multi_account_manager import MultiAccountManager
from config.telegram_config import TelegramConfig

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestTelegramBotIntegration:
    """Integration tests for the complete Telegram bot system."""
    
    @pytest.fixture
    async def bot(self):
        """Create bot instance for testing."""
        bot = TelegramBot()
        yield bot
        await bot.stop()
    
    async def test_bot_initialization(self):
        """Test that the bot initializes all modules correctly."""
        bot = TelegramBot()
        
        # Check that all modules are initialized
        assert bot.listener is not None
        assert bot.executor is not None
        assert bot.priority_engine is not None
        assert bot.metrics_collector is not None
        assert bot.message_generator is not None
        assert bot.account_manager is not None
        
        await bot.stop()
    
    async def test_viral_content_processing_flow(self, bot):
        """Test the complete viral content processing flow."""
        logger.info("Testing viral content processing flow...")
        
        # Simulate viral content detection
        viral_content = ViralContent(
            content_id="test_viral_123",
            platform="tiktok",
            content_type="video",
            author="test_creator",
            author_followers=100000,
            engagement_rate=0.15,
            viral_score=0.85,
            detected_at=datetime.now()
        )
        
        # Add to listener's viral content queue
        await bot.listener._add_viral_content(viral_content)
        
        # Process the viral content
        await bot._process_viral_content()
        
        # Check that tasks were created
        active_tasks = await bot.executor.get_active_tasks()
        assert len(active_tasks) > 0
        
        # Verify task has correct properties
        viral_task = next((task for task in active_tasks if task.task_type == 'viral_engagement'), None)
        assert viral_task is not None
        assert viral_task.platform == "tiktok"
        assert viral_task.target_id == "test_viral_123"
        
        logger.info("✓ Viral content processing flow test passed")
    
    async def test_engagement_exchange_flow(self, bot):
        """Test the engagement exchange request flow."""
        logger.info("Testing engagement exchange flow...")
        
        # Simulate engagement pattern detection
        engagement_pattern = EngagementPattern(
            pattern_type="exchange_request",
            user_id=12345,
            platform="youtube",
            confidence=0.9,
            detected_at=datetime.now(),
            metadata={
                'content_url': 'https://youtube.com/watch?v=test123',
                'exchange_type': 'like',
                'target_engagement': 50
            }
        )
        
        # Process the exchange request
        await bot._process_exchange_request(engagement_pattern)
        
        # Check that tasks were created
        active_tasks = await bot.executor.get_active_tasks()
        exchange_tasks = [task for task in active_tasks if task.user_id == 12345]
        assert len(exchange_tasks) > 0
        
        logger.info("✓ Engagement exchange flow test passed")
    
    async def test_priority_calculation_integration(self, bot):
        """Test priority calculation with real data."""
        logger.info("Testing priority calculation integration...")
        
        # Test various content scenarios
        test_scenarios = [
            {
                'content_type': 'video',
                'engagement_rate': 0.12,
                'platform': 'tiktok',
                'author_followers': 50000,
                'expected_priority_range': (0.6, 0.9)
            },
            {
                'content_type': 'image',
                'engagement_rate': 0.08,
                'platform': 'instagram',
                'author_followers': 10000,
                'expected_priority_range': (0.3, 0.6)
            },
            {
                'content_type': 'video',
                'engagement_rate': 0.20,
                'platform': 'youtube',
                'author_followers': 1000000,
                'expected_priority_range': (0.8, 1.0)
            }
        ]
        
        for scenario in test_scenarios:
            priority_score = await bot.priority_engine.calculate_priority(scenario)
            
            min_expected, max_expected = scenario['expected_priority_range']
            assert min_expected <= priority_score <= max_expected, \
                f"Priority {priority_score} not in expected range {scenario['expected_priority_range']} for {scenario}"
        
        logger.info("✓ Priority calculation integration test passed")
    
    async def test_metrics_collection_flow(self, bot):
        """Test metrics collection and reporting."""
        logger.info("Testing metrics collection flow...")
        
        # Simulate user activity
        test_user_id = 54321
        
        # Record some engagement activities
        await bot.metrics_collector.record_engagement(
            user_id=test_user_id,
            platform="tiktok",
            action="like",
            success=True
        )
        
        await bot.metrics_collector.record_engagement(
            user_id=test_user_id,
            platform="youtube",
            action="subscribe",
            success=True
        )
        
        # Get user metrics
        user_metrics = await bot.metrics_collector.get_user_metrics(test_user_id)
        
        assert user_metrics['total_engagements'] >= 2
        assert 'tiktok' in user_metrics['platform_breakdown']
        assert 'youtube' in user_metrics['platform_breakdown']
        assert user_metrics['activity_score'] > 0
        
        logger.info("✓ Metrics collection flow test passed")
    
    async def test_message_generation_integration(self, bot):
        """Test message generation with different contexts."""
        logger.info("Testing message generation integration...")
        
        # Test different message types
        test_contexts = [
            {
                'type': 'exchange_confirmation',
                'context': {
                    'user_id': 12345,
                    'exchange_params': {'youtube': [{'type': 'like', 'target': 'video123'}]},
                    'estimated_completion': '15 minutes'
                }
            },
            {
                'type': 'viral_opportunity',
                'context': {
                    'user_id': 67890,
                    'opportunity': {
                        'platform': 'tiktok',
                        'content_id': 'viral456',
                        'potential_reward': 'High'
                    }
                }
            },
            {
                'type': 'daily_report',
                'context': {
                    'user_id': 11111,
                    'stats': {
                        'engagements_completed': 25,
                        'exchanges_successful': 20,
                        'points_earned': 150
                    }
                }
            }
        ]
        
        for test_case in test_contexts:
            message = await bot.message_generator.generate_message(
                test_case['type'],
                test_case['context']
            )
            
            assert message is not None
            assert len(message) > 0
            assert isinstance(message, str)
        
        logger.info("✓ Message generation integration test passed")
    
    async def test_account_health_monitoring(self, bot):
        """Test account health monitoring and management."""
        logger.info("Testing account health monitoring...")
        
        # Initialize account manager
        await bot.account_manager.initialize()
        
        # Check account health
        health_report = await bot.account_manager.check_all_accounts_health()
        
        assert isinstance(health_report, dict)
        
        # Test individual platform checks
        for platform in ['youtube', 'instagram', 'tiktok']:
            if platform in health_report:
                platform_health = health_report[platform]
                assert isinstance(platform_health, dict)
        
        logger.info("✓ Account health monitoring test passed")
    
    async def test_task_execution_flow(self, bot):
        """Test complete task execution flow."""
        logger.info("Testing task execution flow...")
        
        # Create test task
        test_task = Task(
            task_type='like',
            platform='tiktok',
            target_id='test_video_789',
            priority=TaskPriority.MEDIUM,
            user_id=99999,
            metadata={'test': True}
        )
        
        # Add task to executor
        await bot.executor.add_task(test_task)
        
        # Start executor
        await bot.executor.start()
        
        # Wait for task processing
        await asyncio.sleep(2)
        
        # Check task status
        task_status = await bot.executor.get_task_status(test_task.task_id)
        assert task_status is not None
        
        await bot.executor.stop()
        
        logger.info("✓ Task execution flow test passed")
    
    async def test_system_status_reporting(self, bot):
        """Test system status reporting."""
        logger.info("Testing system status reporting...")
        
        # Get system status
        status = await bot.get_system_status()
        
        # Verify status structure
        assert 'bot_status' in status
        assert 'modules' in status
        assert 'performance' in status
        assert 'active_tasks' in status
        assert 'managed_accounts' in status
        
        # Check module status
        modules = status['modules']
        expected_modules = ['listener', 'executor', 'priority_engine', 'metrics_collector', 'account_manager']
        
        for module in expected_modules:
            assert module in modules
        
        logger.info("✓ System status reporting test passed")
    
    async def test_end_to_end_workflow(self, bot):
        """Test complete end-to-end workflow."""
        logger.info("Testing end-to-end workflow...")
        
        # 1. Detect viral content
        viral_content = ViralContent(
            content_id="e2e_test_content",
            platform="youtube",
            content_type="video",
            author="e2e_creator",
            author_followers=75000,
            engagement_rate=0.18,
            viral_score=0.92,
            detected_at=datetime.now()
        )
        
        await bot.listener._add_viral_content(viral_content)
        
        # 2. Process viral content (creates high priority tasks)
        await bot._process_viral_content()
        
        # 3. Handle user engagement exchange request
        engagement_pattern = EngagementPattern(
            pattern_type="exchange_request",
            user_id=88888,
            platform="youtube",
            confidence=0.95,
            detected_at=datetime.now(),
            metadata={
                'content_url': 'https://youtube.com/watch?v=e2e_test',
                'exchange_type': 'subscribe',
                'target_engagement': 100
            }
        )
        
        await bot._process_exchange_request(engagement_pattern)
        
        # 4. Update priorities and metrics
        await bot._update_priorities_and_metrics()
        
        # 5. Check final state
        active_tasks = await bot.executor.get_active_tasks()
        assert len(active_tasks) >= 2  # At least viral + exchange tasks
        
        # Verify high priority viral task exists
        viral_tasks = [task for task in active_tasks if 'viral' in task.task_type]
        assert len(viral_tasks) > 0
        
        # Verify exchange tasks exist
        exchange_tasks = [task for task in active_tasks if task.user_id == 88888]
        assert len(exchange_tasks) > 0
        
        logger.info("✓ End-to-end workflow test passed")


async def run_integration_tests():
    """Run all integration tests."""
    logger.info("Starting Telegram Bot Integration Tests...")
    
    test_instance = TestTelegramBotIntegration()
    
    try:
        # Run tests
        await test_instance.test_bot_initialization()
        
        # Create bot for remaining tests
        bot = TelegramBot()
        
        await test_instance.test_viral_content_processing_flow(bot)
        await test_instance.test_engagement_exchange_flow(bot)
        await test_instance.test_priority_calculation_integration(bot)
        await test_instance.test_metrics_collection_flow(bot)
        await test_instance.test_message_generation_integration(bot)
        await test_instance.test_account_health_monitoring(bot)
        await test_instance.test_task_execution_flow(bot)
        await test_instance.test_system_status_reporting(bot)
        await test_instance.test_end_to_end_workflow(bot)
        
        await bot.stop()
        
        logger.info("🎉 All integration tests passed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(run_integration_tests())
    exit(0 if result else 1)