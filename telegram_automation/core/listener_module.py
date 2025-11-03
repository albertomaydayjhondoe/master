"""
Telegram Listener Module
Monitors Telegram groups and channels for engagement opportunities.
Detects viral content, trending hashtags, and user interactions.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Set, Any, Callable
from datetime import datetime, timedelta
import re
from dataclasses import dataclass

from telethon import TelegramClient, events
from telethon.tl.types import Message, User, Chat, Channel
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.telegram_config import TelegramConfig
from database.models import User, EngagementTask, ViralContentRecord

logger = logging.getLogger(__name__)

@dataclass
class ViralContent:
    """Represents potentially viral content detected in groups."""
    message_id: int
    chat_id: int
    content: str
    author_id: int
    timestamp: datetime
    engagement_score: float
    viral_indicators: List[str]
    platform_links: List[str]
    hashtags: List[str]
    mentions: List[str]

@dataclass
class EngagementPattern:
    """Represents user engagement patterns for analysis."""
    user_id: int
    chat_id: int
    message_count: int
    engagement_rate: float
    avg_response_time: timedelta
    activity_hours: List[int]
    platform_preferences: Dict[str, float]

class TelegramListener:
    """
    Listens to Telegram groups and channels to identify engagement opportunities.
    Monitors for viral content, trending topics, and user activity patterns.
    """
    
    def __init__(self, config: TelegramConfig):
        self.config = config
        self.client = None
        self.is_listening = False
        
        # Monitoring state
        self.monitored_chats: Set[int] = set()
        self.viral_thresholds = config.viral_detection_thresholds
        self.content_cache: Dict[int, List[ViralContent]] = {}
        self.user_patterns: Dict[int, EngagementPattern] = {}
        
        # Event handlers
        self.content_handlers: List[Callable] = []
        self.engagement_handlers: List[Callable] = []
        
        # Analytics
        self.message_stats = {
            'total_messages': 0,
            'viral_detected': 0,
            'opportunities_found': 0,
            'last_reset': datetime.now()
        }
    
    async def initialize(self):
        """Initialize the Telegram client and connect."""
        try:
            logger.info("Initializing Telegram listener...")
            
            self.client = TelegramClient(
                session=self.config.session_name,
                api_id=self.config.api_id,
                api_hash=self.config.api_hash
            )
            
            await self.client.start(phone=self.config.phone_number)
            
            # Register event handlers
            self._register_event_handlers()
            
            # Load monitored chats from config
            await self._load_monitored_chats()
            
            logger.info(f"Telegram listener initialized, monitoring {len(self.monitored_chats)} chats")
            
        except Exception as e:
            logger.error(f"Failed to initialize Telegram listener: {e}")
            raise
    
    def _register_event_handlers(self):
        """Register Telegram event handlers."""
        
        @self.client.on(events.NewMessage)
        async def handle_new_message(event):
            await self._process_new_message(event)
        
        @self.client.on(events.MessageEdited)
        async def handle_edited_message(event):
            await self._process_edited_message(event)
        
        @self.client.on(events.MessageDeleted)
        async def handle_deleted_message(event):
            await self._process_deleted_message(event)
        
        @self.client.on(events.UserUpdate)
        async def handle_user_update(event):
            await self._process_user_update(event)
    
    async def _load_monitored_chats(self):
        """Load the list of chats to monitor from configuration."""
        try:
            # Get dialogs (chats/channels the bot has access to)
            dialogs = await self.client.get_dialogs()
            
            for dialog in dialogs:
                chat = dialog.entity
                
                # Check if this chat should be monitored
                if await self._should_monitor_chat(chat):
                    self.monitored_chats.add(chat.id)
                    logger.info(f"Added chat to monitoring: {getattr(chat, 'title', chat.id)}")
            
            logger.info(f"Loaded {len(self.monitored_chats)} chats for monitoring")
            
        except Exception as e:
            logger.error(f"Failed to load monitored chats: {e}")
    
    async def _should_monitor_chat(self, chat) -> bool:
        """Determine if a chat should be monitored based on criteria."""
        # Check chat type
        if isinstance(chat, Channel):
            # Monitor channels with engagement keywords
            title = getattr(chat, 'title', '').lower()
            keywords = self.config.engagement_keywords
            
            return any(keyword in title for keyword in keywords)
        
        elif isinstance(chat, Chat):
            # Monitor groups with sufficient members
            return getattr(chat, 'participants_count', 0) >= self.config.min_group_size
        
        return False
    
    async def _process_new_message(self, event):
        """Process new messages for engagement opportunities."""
        try:
            message = event.message
            chat_id = event.chat_id
            
            # Only process messages from monitored chats
            if chat_id not in self.monitored_chats:
                return
            
            self.message_stats['total_messages'] += 1
            
            # Extract message content and metadata
            content_data = await self._extract_message_data(message)
            
            # Check for viral potential
            if await self._is_potentially_viral(content_data):
                viral_content = await self._create_viral_content(message, content_data)
                await self._handle_viral_content(viral_content)
            
            # Check for engagement opportunities
            opportunities = await self._detect_engagement_opportunities(message, content_data)
            for opportunity in opportunities:
                await self._handle_engagement_opportunity(opportunity)
            
            # Update user activity patterns
            await self._update_user_patterns(message.sender_id, chat_id, message)
            
        except Exception as e:
            logger.error(f"Error processing new message: {e}")
    
    async def _extract_message_data(self, message: Message) -> Dict[str, Any]:
        """Extract relevant data from a Telegram message."""
        content = message.text or message.caption or ""
        
        # Extract URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        
        # Extract platform-specific links
        platform_links = {
            'youtube': [url for url in urls if 'youtube.com' in url or 'youtu.be' in url],
            'instagram': [url for url in urls if 'instagram.com' in url],
            'tiktok': [url for url in urls if 'tiktok.com' in url]
        }
        
        # Extract hashtags and mentions
        hashtags = re.findall(r'#(\w+)', content)
        mentions = re.findall(r'@(\w+)', content)
        
        # Calculate engagement metrics
        views = getattr(message, 'views', 0)
        forwards = getattr(message, 'forwards', 0)
        replies = getattr(message, 'replies', None)
        reply_count = getattr(replies, 'replies', 0) if replies else 0
        
        return {
            'content': content,
            'urls': urls,
            'platform_links': platform_links,
            'hashtags': hashtags,
            'mentions': mentions,
            'views': views,
            'forwards': forwards,
            'replies': reply_count,
            'timestamp': message.date,
            'sender_id': message.sender_id,
            'chat_id': message.chat_id,
            'message_id': message.id
        }
    
    async def _is_potentially_viral(self, content_data: Dict[str, Any]) -> bool:
        """Determine if content has viral potential based on metrics and patterns."""
        
        # Check engagement thresholds
        if content_data['views'] >= self.viral_thresholds.get('min_views', 1000):
            return True
        
        if content_data['forwards'] >= self.viral_thresholds.get('min_forwards', 50):
            return True
        
        if content_data['replies'] >= self.viral_thresholds.get('min_replies', 20):
            return True
        
        # Check for viral keywords
        content = content_data['content'].lower()
        viral_keywords = self.config.viral_keywords
        
        if any(keyword in content for keyword in viral_keywords):
            return True
        
        # Check for trending hashtags
        hashtags = content_data['hashtags']
        if any(hashtag in self.config.trending_hashtags for hashtag in hashtags):
            return True
        
        # Check platform links (content with cross-platform potential)
        total_platform_links = sum(len(links) for links in content_data['platform_links'].values())
        if total_platform_links > 0:
            return True
        
        return False
    
    async def _create_viral_content(self, message: Message, content_data: Dict[str, Any]) -> ViralContent:
        """Create a ViralContent object from message data."""
        
        # Calculate engagement score
        engagement_score = await self._calculate_engagement_score(content_data)
        
        # Identify viral indicators
        viral_indicators = []
        
        if content_data['views'] >= self.viral_thresholds.get('min_views', 1000):
            viral_indicators.append('high_views')
        
        if content_data['forwards'] >= self.viral_thresholds.get('min_forwards', 50):
            viral_indicators.append('high_forwards')
        
        if content_data['replies'] >= self.viral_thresholds.get('min_replies', 20):
            viral_indicators.append('high_replies')
        
        # Check for viral patterns in content
        content = content_data['content'].lower()
        if any(keyword in content for keyword in self.config.viral_keywords):
            viral_indicators.append('viral_keywords')
        
        if len(content_data['hashtags']) >= 3:
            viral_indicators.append('multiple_hashtags')
        
        if any(len(links) > 0 for links in content_data['platform_links'].values()):
            viral_indicators.append('cross_platform')
        
        # Flatten platform links
        all_platform_links = []
        for platform, links in content_data['platform_links'].items():
            all_platform_links.extend(links)
        
        return ViralContent(
            message_id=message.id,
            chat_id=message.chat_id,
            content=content_data['content'],
            author_id=message.sender_id,
            timestamp=message.date,
            engagement_score=engagement_score,
            viral_indicators=viral_indicators,
            platform_links=all_platform_links,
            hashtags=content_data['hashtags'],
            mentions=content_data['mentions']
        )
    
    async def _calculate_engagement_score(self, content_data: Dict[str, Any]) -> float:
        """Calculate engagement score based on various metrics."""
        
        score = 0.0
        
        # Views contribution (normalized)
        views = content_data['views']
        score += min(views / 10000, 1.0) * 30  # Max 30 points from views
        
        # Forwards contribution
        forwards = content_data['forwards']
        score += min(forwards / 100, 1.0) * 25  # Max 25 points from forwards
        
        # Replies contribution
        replies = content_data['replies']
        score += min(replies / 50, 1.0) * 20  # Max 20 points from replies
        
        # Content quality indicators
        if len(content_data['hashtags']) >= 2:
            score += 5
        
        if len(content_data['mentions']) >= 1:
            score += 5
        
        if any(len(links) > 0 for links in content_data['platform_links'].values()):
            score += 10  # Cross-platform potential
        
        # Time factor (newer content gets slight boost)
        time_diff = datetime.now() - content_data['timestamp']
        if time_diff.total_seconds() < 3600:  # Within last hour
            score += 5
        
        return min(score, 100.0)  # Cap at 100
    
    async def _detect_engagement_opportunities(self, message: Message, content_data: Dict[str, Any]) -> List[EngagementOpportunity]:
        """Detect specific engagement opportunities in the message."""
        
        opportunities = []
        
        # Check for platform-specific content
        for platform, links in content_data['platform_links'].items():
            if links:
                for link in links:
                    opportunity = EngagementOpportunity(
                        chat_id=message.chat_id,
                        message_id=message.id,
                        platform=platform,
                        content_url=link,
                        opportunity_type='cross_promotion',
                        priority_score=await self._calculate_opportunity_priority(
                            platform, content_data
                        ),
                        detected_at=datetime.now(),
                        expires_at=datetime.now() + timedelta(hours=24)
                    )
                    opportunities.append(opportunity)
        
        # Check for engagement requests
        content = content_data['content'].lower()
        engagement_requests = [
            'like4like', 'sub4sub', 'follow4follow',
            'intercambio', 'engagement', 'apoyo mutuo'
        ]
        
        if any(request in content for request in engagement_requests):
            opportunity = EngagementOpportunity(
                chat_id=message.chat_id,
                message_id=message.id,
                platform='telegram',
                content_url=f"https://t.me/c/{message.chat_id}/{message.id}",
                opportunity_type='mutual_engagement',
                priority_score=await self._calculate_opportunity_priority(
                    'telegram', content_data
                ),
                detected_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=12)
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    async def _calculate_opportunity_priority(self, platform: str, content_data: Dict[str, Any]) -> float:
        """Calculate priority score for an engagement opportunity."""
        
        base_score = 50.0
        
        # Platform multipliers
        platform_multipliers = {
            'youtube': 1.5,
            'instagram': 1.3,
            'tiktok': 1.4,
            'telegram': 1.0
        }
        
        multiplier = platform_multipliers.get(platform, 1.0)
        score = base_score * multiplier
        
        # Engagement metrics boost
        if content_data['views'] > 500:
            score += 20
        
        if content_data['forwards'] > 10:
            score += 15
        
        if content_data['replies'] > 5:
            score += 10
        
        # Recency boost
        time_diff = datetime.now() - content_data['timestamp']
        if time_diff.total_seconds() < 1800:  # Within 30 minutes
            score += 25
        elif time_diff.total_seconds() < 3600:  # Within 1 hour
            score += 15
        
        return min(score, 100.0)
    
    async def _handle_viral_content(self, viral_content: ViralContent):
        """Handle detected viral content."""
        try:
            logger.info(f"Viral content detected: {viral_content.message_id} (score: {viral_content.engagement_score:.1f})")
            
            # Cache the viral content
            chat_id = viral_content.chat_id
            if chat_id not in self.content_cache:
                self.content_cache[chat_id] = []
            
            self.content_cache[chat_id].append(viral_content)
            
            # Keep only recent viral content (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.content_cache[chat_id] = [
                content for content in self.content_cache[chat_id]
                if content.timestamp > cutoff_time
            ]
            
            # Notify registered handlers
            for handler in self.content_handlers:
                try:
                    await handler(viral_content)
                except Exception as e:
                    logger.error(f"Error in content handler: {e}")
            
            self.message_stats['viral_detected'] += 1
            
        except Exception as e:
            logger.error(f"Error handling viral content: {e}")
    
    async def _handle_engagement_opportunity(self, opportunity: EngagementOpportunity):
        """Handle detected engagement opportunity."""
        try:
            logger.info(f"Engagement opportunity detected: {opportunity.opportunity_type} on {opportunity.platform}")
            
            # Notify registered handlers
            for handler in self.engagement_handlers:
                try:
                    await handler(opportunity)
                except Exception as e:
                    logger.error(f"Error in engagement handler: {e}")
            
            self.message_stats['opportunities_found'] += 1
            
        except Exception as e:
            logger.error(f"Error handling engagement opportunity: {e}")
    
    async def _update_user_patterns(self, user_id: int, chat_id: int, message: Message):
        """Update user engagement patterns for analysis."""
        try:
            if user_id not in self.user_patterns:
                self.user_patterns[user_id] = EngagementPattern(
                    user_id=user_id,
                    chat_id=chat_id,
                    message_count=0,
                    engagement_rate=0.0,
                    avg_response_time=timedelta(0),
                    activity_hours=[],
                    platform_preferences={}
                )
            
            pattern = self.user_patterns[user_id]
            pattern.message_count += 1
            
            # Update activity hours
            hour = message.date.hour
            if hour not in pattern.activity_hours:
                pattern.activity_hours.append(hour)
            
            # Update platform preferences based on links shared
            content_data = await self._extract_message_data(message)
            for platform, links in content_data['platform_links'].items():
                if links:
                    if platform not in pattern.platform_preferences:
                        pattern.platform_preferences[platform] = 0
                    pattern.platform_preferences[platform] += len(links)
            
        except Exception as e:
            logger.error(f"Error updating user patterns: {e}")
    
    async def _process_edited_message(self, event):
        """Process edited messages."""
        # Similar logic to new messages, but track edits
        pass
    
    async def _process_deleted_message(self, event):
        """Process deleted messages."""
        # Remove from cache if it was viral content
        pass
    
    async def _process_user_update(self, event):
        """Process user status updates."""
        # Track user activity patterns
        pass
    
    def register_content_handler(self, handler: Callable[[ViralContent], None]):
        """Register a handler for viral content detection."""
        self.content_handlers.append(handler)
    
    def register_engagement_handler(self, handler: Callable[[EngagementOpportunity], None]):
        """Register a handler for engagement opportunities."""
        self.engagement_handlers.append(handler)
    
    async def get_viral_content(self, chat_id: Optional[int] = None, hours: int = 24) -> List[ViralContent]:
        """Get viral content from the cache."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        if chat_id:
            return [
                content for content in self.content_cache.get(chat_id, [])
                if content.timestamp > cutoff_time
            ]
        else:
            all_content = []
            for chat_content in self.content_cache.values():
                all_content.extend([
                    content for content in chat_content
                    if content.timestamp > cutoff_time
                ])
            return sorted(all_content, key=lambda x: x.engagement_score, reverse=True)
    
    async def get_user_patterns(self, user_id: Optional[int] = None) -> Dict[int, EngagementPattern]:
        """Get user engagement patterns."""
        if user_id:
            return {user_id: self.user_patterns.get(user_id)}
        return self.user_patterns.copy()
    
    async def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        return {
            'monitored_chats': len(self.monitored_chats),
            'total_messages': self.message_stats['total_messages'],
            'viral_detected': self.message_stats['viral_detected'],
            'opportunities_found': self.message_stats['opportunities_found'],
            'cached_content': sum(len(content) for content in self.content_cache.values()),
            'tracked_users': len(self.user_patterns),
            'uptime': datetime.now() - self.message_stats['last_reset']
        }
    
    async def add_monitored_chat(self, chat_id: int):
        """Add a chat to the monitoring list."""
        self.monitored_chats.add(chat_id)
        logger.info(f"Added chat {chat_id} to monitoring")
    
    async def remove_monitored_chat(self, chat_id: int):
        """Remove a chat from the monitoring list."""
        self.monitored_chats.discard(chat_id)
        if chat_id in self.content_cache:
            del self.content_cache[chat_id]
        logger.info(f"Removed chat {chat_id} from monitoring")
    
    async def start(self):
        """Start the listener."""
        self.is_listening = True
        logger.info("Telegram listener started")
    
    async def stop(self):
        """Stop the listener."""
        self.is_listening = False
        if self.client:
            await self.client.disconnect()
        logger.info("Telegram listener stopped")