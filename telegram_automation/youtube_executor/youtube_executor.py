"""
YouTube Automation Executor with GoLogin Integration
Executes YouTube actions (subscribe, like, comment, watch) using GoLogin profiles
"""
import asyncio
import logging
import random
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from contextlib import asynccontextmanager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

from database.models import DatabaseConnection, Exchange, ExchangeStatus

logger = logging.getLogger(__name__)


class GoLoginAPI:
    """
    GoLogin API client for managing browser profiles
    """
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.gologin.com"
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    def get_available_profiles(self) -> List[str]:
        """Get list of available GoLogin profiles"""
        # TODO: Implement actual API call to GoLogin
        # For now, return dummy profiles
        return [
            "gol_profile_001",
            "gol_profile_002", 
            "gol_profile_003",
            "gol_profile_004",
            "gol_profile_005"
        ]
    
    def start_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Start GoLogin profile and return connection info"""
        try:
            # TODO: Implement actual GoLogin profile start
            # For now, simulate profile start
            
            if profile_id in self.active_sessions:
                logger.warning(f"Profile {profile_id} already active")
                return self.active_sessions[profile_id]
            
            # Simulate profile startup
            port = random.randint(9000, 9999)
            session_info = {
                'profile_id': profile_id,
                'port': port,
                'status': 'active',
                'started_at': datetime.now(),
                'ws_endpoint': f'ws://127.0.0.1:{port}'
            }
            
            self.active_sessions[profile_id] = session_info
            
            logger.info(f"✅ Started GoLogin profile {profile_id} on port {port}")
            return session_info
            
        except Exception as e:
            logger.error(f"❌ Failed to start GoLogin profile {profile_id}: {e}")
            return None
    
    def stop_profile(self, profile_id: str) -> bool:
        """Stop GoLogin profile"""
        try:
            if profile_id not in self.active_sessions:
                logger.warning(f"Profile {profile_id} not active")
                return True
            
            # TODO: Implement actual GoLogin profile stop
            # For now, just remove from active sessions
            
            del self.active_sessions[profile_id]
            logger.info(f"🔒 Stopped GoLogin profile {profile_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop GoLogin profile {profile_id}: {e}")
            return False
    
    def get_profile_health(self, profile_id: str) -> Dict[str, Any]:
        """Check profile health status"""
        # TODO: Implement health check
        return {
            'profile_id': profile_id,
            'is_healthy': True,
            'last_used': datetime.now(),
            'ban_risk': 'low'
        }


class YouTubeExecutor:
    """
    Executes YouTube actions using GoLogin profiles
    """
    
    def __init__(self, gologin_api: GoLoginAPI, db: DatabaseConnection):
        self.gologin_api = gologin_api
        self.db = db
        self.driver: Optional[webdriver.Chrome] = None
        self.current_profile_id: Optional[str] = None
        
        # Comment templates for different music genres
        self.comment_templates = {
            'generic': [
                "Great music! 🎵",
                "This is fire! 🔥",
                "Love this track! 💯",
                "Amazing work! Keep it up! 🚀",
                "This is awesome! 👏",
                "Great vibe! 🎶",
                "Incredible! 🙌",
                "This hits different! 💥"
            ],
            'hip_hop': [
                "This beat is crazy! 🔥",
                "Bars are insane! 💯",
                "Flow is perfect! 🎤",
                "This goes hard! 💪",
                "Beat drop is sick! 🎵"
            ],
            'pop': [
                "Such a catchy melody! 🎵",
                "This is so good! ✨",
                "Can't stop listening! 🔄",
                "Perfect vocals! 🎤",
                "This is a hit! 🌟"
            ],
            'electronic': [
                "The drop is insane! 🎧",
                "Perfect for the club! 🕺",
                "Love the synths! ⚡",
                "This is euphoric! 🌈",
                "Great production! 🎛️"
            ]
        }
    
    @asynccontextmanager
    async def session(self, profile_id: Optional[str] = None):
        """Context manager for YouTube session"""
        selected_profile = profile_id or self.select_best_profile()
        
        try:
            await self.start_session(selected_profile)
            yield self
        finally:
            await self.stop_session()
    
    async def start_session(self, profile_id: str):
        """Start YouTube session with GoLogin profile"""
        try:
            logger.info(f"🔓 Starting YouTube session with profile: {profile_id}")
            
            # Start GoLogin profile
            session_info = self.gologin_api.start_profile(profile_id)
            if not session_info:
                raise Exception(f"Failed to start GoLogin profile {profile_id}")
            
            # Wait a bit for profile to fully start
            await asyncio.sleep(3)
            
            # Setup Chrome options to connect to GoLogin
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{session_info['port']}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-images")  # Faster loading
            
            # Initialize WebDriver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            self.current_profile_id = profile_id
            
            # Navigate to YouTube to warm up the session
            self.driver.get("https://www.youtube.com")
            await asyncio.sleep(2)
            
            logger.info(f"✅ YouTube session started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start YouTube session: {e}")
            await self.stop_session()
            raise
    
    async def stop_session(self):
        """Stop YouTube session"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
            
            if self.current_profile_id:
                self.gologin_api.stop_profile(self.current_profile_id)
                self.current_profile_id = None
            
            logger.info("🔒 YouTube session stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping session: {e}")
    
    def select_best_profile(self) -> str:
        """Select best available GoLogin profile"""
        available_profiles = self.gologin_api.get_available_profiles()
        
        # TODO: Implement intelligent profile selection based on:
        # - Last usage time
        # - Success rate
        # - Ban status
        # - Rate limiting
        
        # For now, just return random available profile
        return random.choice(available_profiles)
    
    async def execute_exchange_terms(self, exchange: Exchange) -> Dict[str, bool]:
        """
        Execute all terms for an exchange
        
        Returns:
            Dict with results of each action
        """
        logger.info(f"🎬 Executing exchange terms for {exchange.exchange_uuid}")
        
        if not exchange.their_video_url or not exchange.terms:
            logger.error("❌ Missing video URL or terms")
            return {}
        
        results = {}
        
        try:
            # Update exchange status
            exchange.our_execution_started_at = datetime.now()
            exchange.status = ExchangeStatus.MY_TURN_DONE.value
            await self.db.update_exchange(exchange)
            
            # Navigate to their video
            await self.navigate_to_video(exchange.their_video_url)
            await asyncio.sleep(random.uniform(2, 4))
            
            # Execute each term
            terms = exchange.terms
            
            # Watch video (do this first to make other actions more natural)
            if terms.get('watch_seconds', 0) > 0:
                results['watch'] = await self.watch_video(terms['watch_seconds'])
                await asyncio.sleep(random.uniform(1, 3))
            
            # Like video
            if terms.get('likes', 0) > 0:
                results['like'] = await self.like_video()
                await asyncio.sleep(random.uniform(2, 4))
            
            # Subscribe to channel
            if terms.get('subs', 0) > 0:
                results['subscribe'] = await self.subscribe_to_channel()
                await asyncio.sleep(random.uniform(2, 5))
            
            # Comment on video
            if terms.get('comments', 0) > 0:
                comment_text = self.generate_comment()
                results['comment'] = await self.comment_on_video(comment_text)
                await asyncio.sleep(random.uniform(1, 3))
            
            # Update exchange with results
            exchange.our_execution_completed_at = datetime.now()
            exchange.our_execution_results = results
            
            await self.db.update_exchange(exchange)
            
            # Log success
            successful_actions = [action for action, success in results.items() if success]
            logger.info(f"✅ Exchange execution completed. Successful actions: {successful_actions}")
            
            # Update profile usage stats
            await self.update_profile_stats(self.current_profile_id, results)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error executing exchange terms: {e}")
            
            # Mark as failed
            exchange.our_execution_completed_at = datetime.now()
            exchange.our_execution_results = results  # Partial results
            await self.db.update_exchange(exchange)
            
            return results
    
    async def navigate_to_video(self, video_url: str):
        """Navigate to YouTube video"""
        try:
            logger.info(f"🎥 Navigating to video: {video_url}")
            
            self.driver.get(video_url)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 15)
            wait.until(EC.presence_of_element_located((By.ID, "movie_player")))
            
            # Close any popups or overlays
            await self.close_popups()
            
            logger.info("✅ Successfully navigated to video")
            
        except TimeoutException:
            logger.error("❌ Timeout waiting for video page to load")
            raise
        except Exception as e:
            logger.error(f"❌ Error navigating to video: {e}")
            raise
    
    async def close_popups(self):
        """Close YouTube popups and overlays"""
        try:
            # Common popup selectors
            popup_selectors = [
                "button[aria-label='Close']",
                "button[aria-label='No thanks']",
                "button[aria-label='Not now']",
                ".ytp-ad-skip-button",
                ".ytp-ad-overlay-close-button"
            ]
            
            for selector in popup_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            await asyncio.sleep(0.5)
                except:
                    continue
                    
        except Exception as e:
            logger.debug(f"Error closing popups: {e}")
    
    async def watch_video(self, duration_seconds: int) -> bool:
        """Watch video for specified duration"""
        try:
            logger.info(f"⏱️ Watching video for {duration_seconds} seconds")
            
            # Find video player
            video_player = self.driver.find_element(By.CSS_SELECTOR, "video.html5-main-video")
            
            # Check if video is playing
            is_playing = self.driver.execute_script(
                "return !document.querySelector('video.html5-main-video').paused"
            )
            
            if not is_playing:
                # Click play button
                play_button = self.driver.find_element(By.CSS_SELECTOR, ".ytp-large-play-button")
                if play_button.is_displayed():
                    play_button.click()
                    await asyncio.sleep(1)
            
            # Watch for specified duration with human-like behavior
            start_time = time.time()
            watch_duration = min(duration_seconds, 300)  # Cap at 5 minutes
            
            while time.time() - start_time < watch_duration:
                # Simulate human behavior during watching
                remaining_time = watch_duration - (time.time() - start_time)
                
                if remaining_time > 10:
                    # Occasionally scroll or move mouse
                    if random.random() < 0.1:  # 10% chance
                        scroll_amount = random.randint(-100, 100)
                        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                    
                    # Wait random interval
                    await asyncio.sleep(random.uniform(8, 12))
                else:
                    # Final wait
                    await asyncio.sleep(remaining_time)
                    break
            
            logger.info(f"✅ Watched video for {watch_duration} seconds")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error watching video: {e}")
            return False
    
    async def like_video(self) -> bool:
        """Like the video"""
        try:
            logger.info("👍 Liking video")
            
            # Wait for like button to be available
            wait = WebDriverWait(self.driver, 10)
            
            # Try different like button selectors (YouTube changes these frequently)
            like_selectors = [
                "button[aria-label*='like this video']",
                "button[aria-pressed='false'][aria-label*='like']",
                "#segmented-like-button > ytd-toggle-button-renderer > yt-button-shape > button",
                "ytd-toggle-button-renderer:first-child button"
            ]
            
            like_button = None
            for selector in like_selectors:
                try:
                    like_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except TimeoutException:
                    continue
            
            if not like_button:
                logger.error("❌ Could not find like button")
                return False
            
            # Check if already liked
            aria_pressed = like_button.get_attribute('aria-pressed')
            if aria_pressed == 'true':
                logger.info("ℹ️ Video already liked")
                return True
            
            # Click like button
            like_button.click()
            await asyncio.sleep(random.uniform(1, 2))
            
            logger.info("✅ Successfully liked video")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error liking video: {e}")
            return False
    
    async def subscribe_to_channel(self) -> bool:
        """Subscribe to the channel"""
        try:
            logger.info("📺 Subscribing to channel")
            
            # Wait for subscribe button
            wait = WebDriverWait(self.driver, 10)
            
            # Try different subscribe button selectors
            subscribe_selectors = [
                "button[aria-label*='Subscribe']",
                "#subscribe-button button",
                "ytd-subscribe-button-renderer button",
                ".ytd-subscribe-button-renderer button"
            ]
            
            subscribe_button = None
            for selector in subscribe_selectors:
                try:
                    subscribe_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except TimeoutException:
                    continue
            
            if not subscribe_button:
                logger.error("❌ Could not find subscribe button")
                return False
            
            # Check if already subscribed
            button_text = subscribe_button.text.lower()
            if 'subscribed' in button_text or 'suscrito' in button_text:
                logger.info("ℹ️ Already subscribed to channel")
                return True
            
            # Click subscribe button
            subscribe_button.click()
            await asyncio.sleep(random.uniform(2, 3))
            
            # Handle subscription confirmation popup if it appears
            try:
                confirm_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Subscribe']")
                if confirm_button.is_displayed():
                    confirm_button.click()
                    await asyncio.sleep(1)
            except:
                pass
            
            logger.info("✅ Successfully subscribed to channel")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error subscribing to channel: {e}")
            return False
    
    async def comment_on_video(self, comment_text: str) -> bool:
        """Comment on the video"""
        try:
            logger.info(f"💬 Commenting on video: '{comment_text}'")
            
            # Scroll down to load comments section
            self.driver.execute_script("window.scrollTo(0, 800);")
            await asyncio.sleep(2)
            
            # Wait for comments section
            wait = WebDriverWait(self.driver, 10)
            
            # Try to find comment box
            comment_selectors = [
                "#placeholder-area",
                "div#placeholder",
                "#comments #placeholder-area"
            ]
            
            comment_box = None
            for selector in comment_selectors:
                try:
                    comment_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except TimeoutException:
                    continue
            
            if not comment_box:
                logger.error("❌ Could not find comment box")
                return False
            
            # Click on comment box to focus
            comment_box.click()
            await asyncio.sleep(1)
            
            # Find the actual text input
            text_input_selectors = [
                "#contenteditable-root",
                "div[contenteditable='true']",
                "#textbox"
            ]
            
            text_input = None
            for selector in text_input_selectors:
                try:
                    text_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if text_input.is_displayed():
                        break
                except:
                    continue
            
            if not text_input:
                logger.error("❌ Could not find comment text input")
                return False
            
            # Type comment with human-like timing
            text_input.clear()
            for char in comment_text:
                text_input.send_keys(char)
                await asyncio.sleep(random.uniform(0.05, 0.15))
            
            await asyncio.sleep(random.uniform(1, 2))
            
            # Find and click submit button
            submit_selectors = [
                "#submit-button button",
                "button[aria-label*='Comment']",
                "#submit-button"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if submit_button.is_enabled():
                        break
                except:
                    continue
            
            if not submit_button:
                logger.error("❌ Could not find comment submit button")
                return False
            
            submit_button.click()
            await asyncio.sleep(2)
            
            logger.info("✅ Successfully commented on video")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error commenting on video: {e}")
            return False
    
    def generate_comment(self, genre: str = 'generic') -> str:
        """Generate appropriate comment for the video"""
        templates = self.comment_templates.get(genre.lower(), self.comment_templates['generic'])
        return random.choice(templates)
    
    async def update_profile_stats(self, profile_id: str, results: Dict[str, bool]):
        """Update GoLogin profile usage statistics"""
        try:
            successful_actions = sum(1 for success in results.values() if success)
            total_actions = len(results)
            
            query = """
            UPDATE gologin_profiles SET
                last_used_at = NOW(),
                total_uses = total_uses + 1,
                successful_uses = successful_uses + $2,
                daily_actions = CASE 
                    WHEN daily_actions_date = CURRENT_DATE THEN daily_actions + $3
                    ELSE $3
                END,
                daily_actions_date = CURRENT_DATE
            WHERE profile_id = $1
            """
            
            await self.db.execute_command(query, profile_id, successful_actions, total_actions)
            
        except Exception as e:
            logger.error(f"❌ Error updating profile stats: {e}")
    
    async def get_channel_url_from_video(self, video_url: str) -> Optional[str]:
        """Extract channel URL from video page"""
        try:
            # Wait for channel link
            wait = WebDriverWait(self.driver, 10)
            channel_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-channel-name a")))
            
            return channel_link.get_attribute('href')
            
        except Exception as e:
            logger.error(f"❌ Error getting channel URL: {e}")
            return None


class YouTubeExecutorService:
    """
    Service for managing YouTube execution tasks
    """
    
    def __init__(self, db: DatabaseConnection, gologin_api_token: str):
        self.db = db
        self.gologin_api = GoLoginAPI(gologin_api_token)
        self.executor = YouTubeExecutor(self.gologin_api, db)
        
        # Task queue for execution requests
        self.execution_queue: asyncio.Queue = asyncio.Queue()
        self.is_running = False
    
    async def start(self):
        """Start the YouTube executor service"""
        self.is_running = True
        
        # Start background task to process execution queue
        asyncio.create_task(self.process_execution_queue())
        
        logger.info("🚀 YouTube Executor Service started")
    
    async def stop(self):
        """Stop the YouTube executor service"""
        self.is_running = False
        logger.info("🔒 YouTube Executor Service stopped")
    
    async def queue_exchange_execution(self, exchange_id: int):
        """Queue an exchange for execution"""
        await self.execution_queue.put(exchange_id)
        logger.info(f"📥 Queued exchange {exchange_id} for execution")
    
    async def process_execution_queue(self):
        """Process queued exchange executions"""
        while self.is_running:
            try:
                # Wait for next execution request
                exchange_id = await asyncio.wait_for(self.execution_queue.get(), timeout=10)
                
                # Get exchange details
                exchange = await self.db.get_exchange_by_id(exchange_id)
                if not exchange:
                    logger.error(f"❌ Exchange {exchange_id} not found")
                    continue
                
                # Execute the exchange
                await self.execute_exchange(exchange)
                
                # Rate limiting - wait between executions
                await asyncio.sleep(random.uniform(30, 60))
                
            except asyncio.TimeoutError:
                # No new tasks, continue waiting
                continue
            except Exception as e:
                logger.error(f"❌ Error processing execution queue: {e}")
                await asyncio.sleep(10)
    
    async def execute_exchange(self, exchange: Exchange):
        """Execute a single exchange"""
        try:
            logger.info(f"🎬 Starting execution for exchange {exchange.exchange_uuid}")
            
            # Select and start session
            async with self.executor.session() as session:
                results = await session.execute_exchange_terms(exchange)
                
                # Check if execution was successful
                if any(results.values()):
                    logger.info(f"✅ Exchange {exchange.exchange_uuid} executed successfully")
                    
                    # Notify the conversation handler that execution is complete
                    await self.notify_execution_complete(exchange)
                else:
                    logger.warning(f"⚠️ Exchange {exchange.exchange_uuid} execution failed")
                    
                    # Mark exchange as failed
                    exchange.status = ExchangeStatus.FAILED.value
                    await self.db.update_exchange(exchange)
            
        except Exception as e:
            logger.error(f"❌ Error executing exchange {exchange.exchange_uuid}: {e}")
            
            # Mark exchange as failed
            exchange.status = ExchangeStatus.FAILED.value
            exchange.our_execution_completed_at = datetime.now()
            exchange.our_execution_results = {'error': str(e)}
            await self.db.update_exchange(exchange)
    
    async def notify_execution_complete(self, exchange: Exchange):
        """Notify that execution is complete (to be called by conversation handler)"""
        # This will be integrated with the conversation handler
        # to send notifications to contacts
        pass