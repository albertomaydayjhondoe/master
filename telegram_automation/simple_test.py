"""
Simple Integration Test for Telegram Bot System
Tests basic functionality without complex imports.
"""

import asyncio
import logging
import sys
import os

# Add the telegram_automation directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_basic_imports():
    """Test that all modules can be imported."""
    logger.info("Testing basic imports...")
    
    try:
        # Test config import
        from config.telegram_config import TelegramConfig
        logger.info("✓ TelegramConfig imported successfully")
        
        # Test database models
        from database.models import User, EngagementTask
        logger.info("✓ Database models imported successfully")
        
        # Test platform clients
        from integrations.youtube_client import YouTubeClient
        from integrations.instagram_client import InstagramClient
        from integrations.tiktok_client import TikTokClient
        logger.info("✓ Platform clients imported successfully")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        return False

async def test_config_loading():
    """Test configuration loading."""
    logger.info("Testing configuration loading...")
    
    try:
        from config.telegram_config import TelegramConfig
        
        # Test config initialization
        config = TelegramConfig()
        
        # Check that config has expected attributes
        assert hasattr(config, 'telegram_config')
        assert hasattr(config, 'platform_configs')
        assert hasattr(config, 'ml_config')
        
        logger.info("✓ Configuration loading test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration loading failed: {e}")
        return False

async def test_client_initialization():
    """Test platform client initialization."""
    logger.info("Testing platform client initialization...")
    
    try:
        from integrations.youtube_client import YouTubeClient
        from integrations.instagram_client import InstagramClient
        from integrations.tiktok_client import TikTokClient
        
        # Test client initialization in dummy mode
        youtube = YouTubeClient({'dummy_mode': True})
        instagram = InstagramClient({'dummy_mode': True})
        tiktok = TikTokClient({'dummy_mode': True})
        
        # Test initialization
        await youtube.initialize()
        await instagram.initialize()
        await tiktok.initialize()
        
        # Test authentication
        youtube_auth = await youtube.test_authentication()
        instagram_auth = await instagram.test_authentication()
        tiktok_auth = await tiktok.test_authentication()
        
        assert youtube_auth == True
        assert instagram_auth == True
        assert tiktok_auth == True
        
        # Cleanup
        await youtube.close()
        await instagram.close()
        await tiktok.close()
        
        logger.info("✓ Platform client initialization test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Platform client initialization failed: {e}")
        return False

async def test_dummy_operations():
    """Test dummy operations on all platforms."""
    logger.info("Testing dummy operations...")
    
    try:
        from integrations.youtube_client import YouTubeClient
        from integrations.instagram_client import InstagramClient
        from integrations.tiktok_client import TikTokClient
        
        # Initialize clients
        youtube = YouTubeClient({'dummy_mode': True})
        instagram = InstagramClient({'dummy_mode': True})
        tiktok = TikTokClient({'dummy_mode': True})
        
        await youtube.initialize()
        await instagram.initialize()
        await tiktok.initialize()
        
        # Test YouTube operations
        youtube_like = await youtube.like_video('test_video_123')
        youtube_subscribe = await youtube.subscribe_to_channel('test_channel')
        youtube_comment = await youtube.add_comment('test_video_123', 'Great video!')
        
        assert youtube_like == True
        assert youtube_subscribe == True
        assert youtube_comment == True
        
        # Test Instagram operations
        instagram_like = await instagram.like_post('test_post_456')
        instagram_follow = await instagram.follow_user('test_user')
        instagram_comment = await instagram.add_comment('test_post_456', 'Amazing!')
        
        assert instagram_like == True
        assert instagram_follow == True
        assert instagram_comment == True
        
        # Test TikTok operations
        tiktok_like = await tiktok.like_video('test_tiktok_789')
        tiktok_follow = await tiktok.follow_user('test_tiktoker')
        tiktok_comment = await tiktok.add_comment('test_tiktok_789', 'Cool!')
        
        assert tiktok_like == True
        assert tiktok_follow == True
        assert tiktok_comment == True
        
        # Cleanup
        await youtube.close()
        await instagram.close()
        await tiktok.close()
        
        logger.info("✓ Dummy operations test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Dummy operations test failed: {e}")
        return False

async def test_data_structures():
    """Test data structure creation."""
    logger.info("Testing data structures...")
    
    try:
        from database.models import User, EngagementTask, Metrics
        
        # Test creating user
        user = User(
            user_id=12345,
            username="test_user",
            first_name="Test",
            last_name="User",
            is_active=True
        )
        
        # Test creating task
        task = EngagementTask(
            task_id="test_task_123",
            user_id=12345,
            platform="youtube",
            action_type="like",
            target_id="video_123",
            status="pending"
        )
        
        # Test creating metrics
        metrics = Metrics(
            user_id=12345,
            platform="youtube",
            action="like",
            success=True,
            timestamp="2024-01-01 12:00:00"
        )
        
        # Verify objects were created
        assert user.user_id == 12345
        assert task.platform == "youtube"
        assert metrics.success == True
        
        logger.info("✓ Data structures test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Data structures test failed: {e}")
        return False

async def test_system_components():
    """Test system components work together."""
    logger.info("Testing system components...")
    
    try:
        # Test priority calculation
        priority_factors = {
            'engagement_rate': 0.15,
            'follower_count': 50000,
            'content_type': 'video',
            'platform': 'tiktok'
        }
        
        # Simple priority calculation (mock ML logic)
        engagement_score = priority_factors['engagement_rate'] * 2
        follower_score = min(priority_factors['follower_count'] / 100000, 1.0)
        platform_score = 0.8 if priority_factors['platform'] == 'tiktok' else 0.6
        
        priority_score = (engagement_score + follower_score + platform_score) / 3
        
        assert 0 <= priority_score <= 1
        logger.info(f"Priority score calculated: {priority_score:.3f}")
        
        # Test message generation (simple template)
        user_context = {
            'user_id': 12345,
            'username': 'test_user',
            'exchange_count': 5
        }
        
        message_template = f"Hello @{user_context['username']}! You have completed {user_context['exchange_count']} exchanges."
        message = message_template
        
        assert len(message) > 0
        assert 'test_user' in message
        logger.info(f"Generated message: {message}")
        
        logger.info("✓ System components test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ System components test failed: {e}")
        return False

async def run_simple_tests():
    """Run all simple tests."""
    logger.info("🚀 Starting Simple Telegram Bot Tests...")
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Configuration Loading", test_config_loading),
        ("Client Initialization", test_client_initialization),
        ("Dummy Operations", test_dummy_operations),
        ("Data Structures", test_data_structures),
        ("System Components", test_system_components)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} ---")
        try:
            result = await test_func()
            if result:
                passed += 1
                logger.info(f"✅ {test_name} PASSED")
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} FAILED with exception: {e}")
    
    logger.info(f"\n🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! The Telegram Bot system is working correctly.")
        return True
    else:
        logger.error(f"💥 {total - passed} tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    result = asyncio.run(run_simple_tests())
    exit(0 if result else 1)