"""
Telegram Groups Automator - Complete Implementation
Handles group management, posting, monitoring and engagement
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import os
from dataclasses import dataclass

# Import configuration
from ...config.app_settings import is_dummy_mode

# Telegram dependencies
try:
    from telethon import TelegramClient, events, functions, types
    from telethon.errors import (
        SessionPasswordNeededError, FloodWaitError, 
        ChannelPrivateError, UserBannedInChannelError,
        ChatWriteForbiddenError, SlowModeWaitError
    )
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("🎭 Using dummy Telegram implementations")

@dataclass
class TelegramGroup:
    """Telegram group configuration"""
    id: int
    username: str
    title: str
    members_count: int
    is_active: bool = True
    post_frequency: str = "daily"  # hourly, daily, weekly
    content_type: List[str] = None  # text, photo, video, document
    engagement_rate: float = 0.0
    last_post_time: Optional[datetime] = None

@dataclass 
class TelegramMessage:
    """Telegram message structure"""
    text: str
    media: Optional[str] = None
    media_type: str = "photo"  # photo, video, document
    buttons: Optional[List[Dict]] = None
    parse_mode: str = "HTML"
    disable_web_page_preview: bool = False

class TelegramAutomator:
    """Complete Telegram Groups Automation System"""
    
    def __init__(self):
        self.dummy_mode = is_dummy_mode()
        self.logger = logging.getLogger(__name__)
        
        if not self.dummy_mode and TELEGRAM_AVAILABLE:
            # Production mode - real Telegram API
            self.api_id = os.getenv('TELEGRAM_API_ID')
            self.api_hash = os.getenv('TELEGRAM_API_HASH')
            self.phone = os.getenv('TELEGRAM_PHONE')
            self.session_name = os.getenv('TELEGRAM_SESSION_NAME', 'telegram_session')
            
            if not all([self.api_id, self.api_hash, self.phone]):
                raise ValueError("Missing Telegram credentials in environment variables")
            
            self.client = TelegramClient(
                self.session_name, 
                int(self.api_id), 
                self.api_hash
            )
            self.groups: Dict[int, TelegramGroup] = {}
            self.message_queue = []
            
        else:
            # Dummy mode for development
            self.client = None
            self.groups = {
                -1001234567890: TelegramGroup(
                    id=-1001234567890,
                    username="test_group",
                    title="Test Marketing Group",
                    members_count=1500,
                    content_type=["text", "photo"],
                    engagement_rate=0.15
                ),
                -1001234567891: TelegramGroup(
                    id=-1001234567891,
                    username="crypto_signals",
                    title="Crypto Trading Signals",
                    members_count=8500,
                    content_type=["text", "photo", "document"],
                    engagement_rate=0.22
                )
            }
            self.message_queue = []
            
        self.is_connected = False
        
    async def connect(self) -> bool:
        """Connect to Telegram"""
        if self.dummy_mode:
            self.logger.info("🎭 Dummy mode: Simulating Telegram connection")
            self.is_connected = True
            return True
            
        try:
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                await self.client.send_code_request(self.phone)
                code = input("Enter the code you received: ")
                
                try:
                    await self.client.sign_in(self.phone, code)
                except SessionPasswordNeededError:
                    password = input("Enter your 2FA password: ")
                    await self.client.sign_in(password=password)
            
            self.is_connected = True
            self.logger.info("✅ Connected to Telegram successfully")
            
            # Load groups
            await self._load_groups()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to Telegram: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Telegram"""
        if self.dummy_mode:
            self.logger.info("🎭 Dummy mode: Simulating disconnect")
            return
            
        if self.client and self.client.is_connected():
            await self.client.disconnect()
            self.is_connected = False
            self.logger.info("📴 Disconnected from Telegram")
    
    async def _load_groups(self):
        """Load user's groups and channels"""
        if self.dummy_mode:
            return
            
        try:
            dialogs = await self.client.get_dialogs()
            
            for dialog in dialogs:
                entity = dialog.entity
                
                if isinstance(entity, (types.Chat, types.Channel)):
                    # Check if we can post to this group
                    try:
                        permissions = await self.client.get_permissions(entity)
                        if permissions.send_messages:
                            
                            group = TelegramGroup(
                                id=entity.id,
                                username=getattr(entity, 'username', None) or str(entity.id),
                                title=entity.title,
                                members_count=getattr(entity, 'participants_count', 0)
                            )
                            
                            self.groups[entity.id] = group
                            
                    except Exception as e:
                        self.logger.warning(f"Cannot access group {entity.title}: {e}")
                        
            self.logger.info(f"📊 Loaded {len(self.groups)} accessible groups")
            
        except Exception as e:
            self.logger.error(f"Failed to load groups: {e}")
    
    async def get_groups(self) -> List[TelegramGroup]:
        """Get list of available groups"""
        return list(self.groups.values())
    
    async def get_group_info(self, group_id: int) -> Optional[TelegramGroup]:
        """Get detailed group information"""
        if self.dummy_mode:
            return self.groups.get(group_id)
            
        try:
            entity = await self.client.get_entity(group_id)
            full_info = await self.client(functions.channels.GetFullChannelRequest(entity))
            
            group = TelegramGroup(
                id=entity.id,
                username=getattr(entity, 'username', None) or str(entity.id),
                title=entity.title,
                members_count=full_info.full_chat.participants_count,
                engagement_rate=await self._calculate_engagement_rate(group_id)
            )
            
            self.groups[group_id] = group
            return group
            
        except Exception as e:
            self.logger.error(f"Failed to get group info for {group_id}: {e}")
            return None
    
    async def send_message(self, group_id: int, message: TelegramMessage) -> Dict[str, Any]:
        """Send message to Telegram group"""
        if not self.is_connected:
            await self.connect()
        
        if self.dummy_mode:
            self.logger.info(f"🎭 Dummy mode: Would send message to group {group_id}")
            return {
                "success": True,
                "message_id": 12345,
                "group_id": group_id,
                "text": message.text[:50] + "..." if len(message.text) > 50 else message.text,
                "timestamp": datetime.now().isoformat(),
                "engagement": {
                    "views": 150,
                    "reactions": 12,
                    "replies": 3
                }
            }
        
        try:
            # Prepare message kwargs
            kwargs = {
                "message": message.text,
                "parse_mode": message.parse_mode
            }
            
            # Add media if present
            if message.media:
                kwargs["file"] = message.media
            
            # Add buttons if present
            if message.buttons:
                from telethon.tl.types import KeyboardButtonUrl
                buttons = []
                for button_row in message.buttons:
                    row = []
                    for button in button_row:
                        if isinstance(button, dict) and 'text' in button and 'url' in button:
                            row.append(KeyboardButtonUrl(button['text'], button['url']))
                    if row:
                        buttons.append(row)
                kwargs["buttons"] = buttons
            
            # Send message
            sent_message = await self.client.send_message(group_id, **kwargs)
            
            # Update group last post time
            if group_id in self.groups:
                self.groups[group_id].last_post_time = datetime.now()
            
            result = {
                "success": True,
                "message_id": sent_message.id,
                "group_id": group_id,
                "text": message.text,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ Message sent to group {group_id}: {sent_message.id}")
            return result
            
        except FloodWaitError as e:
            wait_time = e.seconds
            self.logger.warning(f"⏰ Flood wait: {wait_time} seconds for group {group_id}")
            return {
                "success": False,
                "error": "flood_wait",
                "wait_time": wait_time,
                "group_id": group_id
            }
            
        except SlowModeWaitError as e:
            wait_time = e.seconds
            self.logger.warning(f"🐌 Slow mode wait: {wait_time} seconds for group {group_id}")
            return {
                "success": False,
                "error": "slow_mode_wait",
                "wait_time": wait_time,
                "group_id": group_id
            }
            
        except (ChatWriteForbiddenError, UserBannedInChannelError):
            self.logger.error(f"🚫 No permission to write in group {group_id}")
            return {
                "success": False,
                "error": "no_permission",
                "group_id": group_id
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send message to group {group_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "group_id": group_id
            }
    
    async def schedule_message(self, group_id: int, message: TelegramMessage, 
                             send_time: datetime) -> Dict[str, Any]:
        """Schedule message for later sending"""
        scheduled_message = {
            "group_id": group_id,
            "message": message,
            "send_time": send_time,
            "status": "scheduled"
        }
        
        self.message_queue.append(scheduled_message)
        
        self.logger.info(f"📅 Message scheduled for group {group_id} at {send_time}")
        
        return {
            "success": True,
            "scheduled_id": len(self.message_queue),
            "send_time": send_time.isoformat(),
            "group_id": group_id
        }
    
    async def process_message_queue(self):
        """Process scheduled messages"""
        now = datetime.now()
        
        for scheduled_msg in self.message_queue[:]:
            if (scheduled_msg["status"] == "scheduled" and 
                scheduled_msg["send_time"] <= now):
                
                result = await self.send_message(
                    scheduled_msg["group_id"],
                    scheduled_msg["message"]
                )
                
                if result["success"]:
                    scheduled_msg["status"] = "sent"
                    scheduled_msg["result"] = result
                else:
                    scheduled_msg["status"] = "failed"
                    scheduled_msg["error"] = result.get("error")
    
    async def get_group_analytics(self, group_id: int, days: int = 7) -> Dict[str, Any]:
        """Get group analytics and performance metrics"""
        if self.dummy_mode:
            return {
                "group_id": group_id,
                "period_days": days,
                "total_messages": 45,
                "avg_views": 320,
                "avg_reactions": 18,
                "engagement_rate": 0.156,
                "peak_hours": [10, 14, 19, 21],
                "top_content_types": ["photo", "text"],
                "member_growth": 12,
                "active_members": 890
            }
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get messages from the period
            messages = []
            async for message in self.client.iter_messages(
                group_id, 
                offset_date=start_date,
                reverse=True
            ):
                if message.date > end_date:
                    break
                messages.append(message)
            
            # Calculate analytics
            total_messages = len(messages)
            total_views = sum(getattr(msg, 'views', 0) for msg in messages)
            total_reactions = sum(len(getattr(msg, 'reactions', [])) for msg in messages)
            
            analytics = {
                "group_id": group_id,
                "period_days": days,
                "total_messages": total_messages,
                "avg_views": total_views / total_messages if total_messages > 0 else 0,
                "avg_reactions": total_reactions / total_messages if total_messages > 0 else 0,
                "engagement_rate": await self._calculate_engagement_rate(group_id),
                "peak_hours": await self._get_peak_hours(messages),
                "top_content_types": await self._get_top_content_types(messages),
                "member_growth": await self._get_member_growth(group_id, days)
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to get analytics for group {group_id}: {e}")
            return {"error": str(e)}
    
    async def _calculate_engagement_rate(self, group_id: int) -> float:
        """Calculate engagement rate for a group"""
        if self.dummy_mode:
            return 0.15 + (hash(str(group_id)) % 20) / 100
        
        # Implementation for real engagement calculation
        try:
            # Get recent messages and calculate engagement
            messages = []
            async for message in self.client.iter_messages(group_id, limit=50):
                messages.append(message)
            
            if not messages:
                return 0.0
            
            total_views = sum(getattr(msg, 'views', 0) for msg in messages)
            total_reactions = sum(len(getattr(msg, 'reactions', [])) for msg in messages)
            
            group_info = self.groups.get(group_id)
            members_count = group_info.members_count if group_info else 1000
            
            engagement = (total_reactions / total_views) if total_views > 0 else 0
            return min(engagement, 1.0)
            
        except Exception:
            return 0.0
    
    async def _get_peak_hours(self, messages: List) -> List[int]:
        """Analyze peak activity hours"""
        hour_counts = {}
        
        for message in messages:
            hour = message.date.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Return top 4 hours
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        return [hour for hour, _ in sorted_hours[:4]]
    
    async def _get_top_content_types(self, messages: List) -> List[str]:
        """Analyze top performing content types"""
        type_counts = {}
        
        for message in messages:
            if message.photo:
                content_type = "photo"
            elif message.video:
                content_type = "video"
            elif message.document:
                content_type = "document"
            else:
                content_type = "text"
            
            type_counts[content_type] = type_counts.get(content_type, 0) + 1
        
        # Return sorted by popularity
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        return [content_type for content_type, _ in sorted_types]
    
    async def _get_member_growth(self, group_id: int, days: int) -> int:
        """Get member growth over period"""
        if self.dummy_mode:
            return 5 + (hash(str(group_id)) % 20)
        
        # For real implementation, you'd need to store historical data
        # or use Telegram's admin log if you're an admin
        return 0
    
    async def bulk_send_message(self, group_ids: List[int], message: TelegramMessage, 
                               delay_between: int = 5) -> Dict[str, Any]:
        """Send message to multiple groups with delay"""
        results = {}
        
        for group_id in group_ids:
            result = await self.send_message(group_id, message)
            results[group_id] = result
            
            # Delay between sends to avoid rate limiting
            if delay_between > 0:
                await asyncio.sleep(delay_between)
        
        success_count = sum(1 for r in results.values() if r.get("success"))
        
        return {
            "total_groups": len(group_ids),
            "successful_sends": success_count,
            "failed_sends": len(group_ids) - success_count,
            "results": results
        }
    
    async def monitor_mentions(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Monitor groups for specific keywords/mentions"""
        if self.dummy_mode:
            return [
                {
                    "group_id": -1001234567890,
                    "group_name": "Test Marketing Group",
                    "message_id": 12345,
                    "text": f"Check out this amazing {keywords[0] if keywords else 'product'}!",
                    "author": "user123",
                    "timestamp": datetime.now().isoformat(),
                    "keyword_matched": keywords[0] if keywords else "product"
                }
            ]
        
        mentions = []
        
        try:
            for group_id in self.groups.keys():
                async for message in self.client.iter_messages(group_id, limit=20):
                    if message.text:
                        for keyword in keywords:
                            if keyword.lower() in message.text.lower():
                                mentions.append({
                                    "group_id": group_id,
                                    "group_name": self.groups[group_id].title,
                                    "message_id": message.id,
                                    "text": message.text[:200],
                                    "author": getattr(message.sender, 'username', 'Unknown'),
                                    "timestamp": message.date.isoformat(),
                                    "keyword_matched": keyword
                                })
                                break
        
        except Exception as e:
            self.logger.error(f"Failed to monitor mentions: {e}")
        
        return mentions

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path

from config.app_settings import is_dummy_mode

# Conditional imports for production vs dummy mode
if not is_dummy_mode():
    try:
        from telethon import TelegramClient, events
        from telethon.tl.types import Channel, Chat, User, Message
        from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
        from telethon.tl.functions.messages import SendMessageRequest, GetHistoryRequest
        from telethon.errors import FloodWaitError, SessionPasswordNeededError
        TELEGRAM_AVAILABLE = True
    except ImportError:
        TELEGRAM_AVAILABLE = False
else:
    TELEGRAM_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class TelegramGroupInfo:
    """Information about a Telegram group"""
    id: int
    title: str
    username: Optional[str]
    members_count: int
    description: Optional[str]
    is_channel: bool
    is_group: bool
    is_supergroup: bool
    invite_link: Optional[str]

@dataclass
class TelegramMessage:
    """Telegram message data"""
    id: int
    text: str
    date: datetime
    sender_id: Optional[int]
    group_id: int
    reply_to: Optional[int] = None
    views: Optional[int] = None
    forwards: Optional[int] = None

@dataclass
class TelegramPostMetrics:
    """Metrics for a Telegram post"""
    message_id: int
    group_id: int
    views: int
    forwards: int
    replies: int
    reactions: Dict[str, int]
    engagement_rate: float
    timestamp: datetime

class TelegramAutomator:
    """Main Telegram automation class for group management and posting"""
    
    def __init__(
        self,
        api_id: Optional[str] = None,
        api_hash: Optional[str] = None,
        phone: Optional[str] = None,
        session_name: str = "telegram_session"
    ):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.session_name = session_name
        self.client = None
        self.is_connected = False
        
        # Configuration
        self.max_groups = 100
        self.posting_delay = 300  # 5 minutes between posts
        self.max_posts_per_hour = 12
        
        # Tracking
        self.managed_groups: Dict[int, TelegramGroupInfo] = {}
        self.post_history: List[TelegramMessage] = []
        self.metrics_cache: Dict[int, TelegramPostMetrics] = {}
        
        if is_dummy_mode():
            logger.info("🤖 Telegram Automator initialized in dummy mode")
        else:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Telegram client"""
        if not TELEGRAM_AVAILABLE:
            logger.warning("Telethon not available - using dummy mode")
            return
            
        if not all([self.api_id, self.api_hash]):
            logger.error("API ID and API Hash are required for Telegram client")
            return
            
        try:
            self.client = TelegramClient(
                self.session_name,
                int(self.api_id),
                self.api_hash
            )
        except Exception as e:
            logger.error(f"Failed to initialize Telegram client: {e}")
    
    async def connect(self) -> bool:
        """Connect to Telegram"""
        if is_dummy_mode():
            logger.info("🤖 Dummy Telegram connection established")
            self.is_connected = True
            return True
            
        if not self.client:
            logger.error("Telegram client not initialized")
            return False
            
        try:
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                if self.phone:
                    await self.client.send_code_request(self.phone)
                    logger.info("SMS code sent. Please enter it when prompted.")
                    return False
                else:
                    logger.error("Phone number required for authorization")
                    return False
            
            self.is_connected = True
            logger.info("✅ Connected to Telegram successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Telegram: {e}")
            return False
    
    async def authorize(self, code: str, password: Optional[str] = None) -> bool:
        """Complete Telegram authorization"""
        if is_dummy_mode():
            return True
            
        if not self.client or not self.phone:
            return False
            
        try:
            await self.client.sign_in(self.phone, code)
            self.is_connected = True
            logger.info("✅ Telegram authorization successful")
            return True
            
        except SessionPasswordNeededError:
            if password:
                await self.client.sign_in(password=password)
                self.is_connected = True
                logger.info("✅ Telegram authorization with 2FA successful")
                return True
            else:
                logger.error("2FA password required")
                return False
                
        except Exception as e:
            logger.error(f"Authorization failed: {e}")
            return False
    
    async def get_groups(self, limit: int = 50) -> List[TelegramGroupInfo]:
        """Get list of user's groups and channels"""
        if is_dummy_mode():
            return self._get_dummy_groups(limit)
            
        if not self.is_connected:
            await self.connect()
            
        groups = []
        try:
            async for dialog in self.client.iter_dialogs(limit=limit):
                entity = dialog.entity
                
                if isinstance(entity, (Channel, Chat)):
                    group_info = TelegramGroupInfo(
                        id=entity.id,
                        title=entity.title,
                        username=getattr(entity, 'username', None),
                        members_count=getattr(entity, 'participants_count', 0),
                        description=getattr(entity, 'about', None),
                        is_channel=isinstance(entity, Channel) and entity.broadcast,
                        is_group=isinstance(entity, Chat),
                        is_supergroup=isinstance(entity, Channel) and entity.megagroup,
                        invite_link=None
                    )
                    groups.append(group_info)
                    self.managed_groups[entity.id] = group_info
                    
        except Exception as e:
            logger.error(f"Failed to get groups: {e}")
            
        return groups
    
    async def join_group(self, group_username_or_link: str) -> bool:
        """Join a Telegram group or channel"""
        if is_dummy_mode():
            logger.info(f"🤖 Dummy joined group: {group_username_or_link}")
            return True
            
        if not self.is_connected:
            return False
            
        try:
            # Handle different input formats
            if group_username_or_link.startswith('@'):
                username = group_username_or_link[1:]
            elif 't.me/' in group_username_or_link:
                username = group_username_or_link.split('/')[-1]
            else:
                username = group_username_or_link
                
            entity = await self.client.get_entity(username)
            await self.client(JoinChannelRequest(entity))
            
            logger.info(f"✅ Successfully joined: {entity.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to join group {group_username_or_link}: {e}")
            return False
    
    async def leave_group(self, group_id: int) -> bool:
        """Leave a Telegram group or channel"""
        if is_dummy_mode():
            logger.info(f"🤖 Dummy left group: {group_id}")
            return True
            
        if not self.is_connected:
            return False
            
        try:
            entity = await self.client.get_entity(group_id)
            await self.client(LeaveChannelRequest(entity))
            
            # Remove from managed groups
            if group_id in self.managed_groups:
                del self.managed_groups[group_id]
                
            logger.info(f"✅ Successfully left group: {group_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to leave group {group_id}: {e}")
            return False
    
    async def send_message(
        self,
        group_id: int,
        text: str,
        reply_to: Optional[int] = None,
        parse_mode: str = 'markdown'
    ) -> Optional[TelegramMessage]:
        """Send a message to a Telegram group"""
        if is_dummy_mode():
            return self._create_dummy_message(group_id, text)
            
        if not self.is_connected:
            return None
            
        try:
            entity = await self.client.get_entity(group_id)
            
            message = await self.client.send_message(
                entity,
                text,
                reply_to=reply_to,
                parse_mode=parse_mode
            )
            
            telegram_msg = TelegramMessage(
                id=message.id,
                text=text,
                date=message.date,
                sender_id=message.sender_id,
                group_id=group_id,
                reply_to=reply_to
            )
            
            self.post_history.append(telegram_msg)
            logger.info(f"✅ Message sent to group {group_id}: {text[:50]}...")
            return telegram_msg
            
        except FloodWaitError as e:
            logger.warning(f"Rate limit hit. Wait {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
            return None
            
        except Exception as e:
            logger.error(f"Failed to send message to {group_id}: {e}")
            return None
    
    async def get_group_messages(
        self,
        group_id: int,
        limit: int = 100,
        offset_date: Optional[datetime] = None
    ) -> List[TelegramMessage]:
        """Get recent messages from a group"""
        if is_dummy_mode():
            return self._get_dummy_messages(group_id, limit)
            
        if not self.is_connected:
            return []
            
        messages = []
        try:
            entity = await self.client.get_entity(group_id)
            
            async for message in self.client.iter_messages(
                entity,
                limit=limit,
                offset_date=offset_date
            ):
                if message.text:
                    telegram_msg = TelegramMessage(
                        id=message.id,
                        text=message.text,
                        date=message.date,
                        sender_id=message.sender_id,
                        group_id=group_id,
                        views=getattr(message, 'views', None),
                        forwards=getattr(message, 'forwards', None)
                    )
                    messages.append(telegram_msg)
                    
        except Exception as e:
            logger.error(f"Failed to get messages from {group_id}: {e}")
            
        return messages
    
    async def get_post_metrics(self, group_id: int, message_id: int) -> Optional[TelegramPostMetrics]:
        """Get metrics for a specific post"""
        if is_dummy_mode():
            return self._create_dummy_metrics(group_id, message_id)
            
        if not self.is_connected:
            return None
            
        try:
            entity = await self.client.get_entity(group_id)
            message = await self.client.get_messages(entity, ids=message_id)
            
            if message:
                msg = message[0]
                metrics = TelegramPostMetrics(
                    message_id=message_id,
                    group_id=group_id,
                    views=getattr(msg, 'views', 0),
                    forwards=getattr(msg, 'forwards', 0),
                    replies=0,  # Would need to count replies separately
                    reactions={},  # Would need to get reactions
                    engagement_rate=0.0,  # Calculate based on group size
                    timestamp=datetime.now()
                )
                
                self.metrics_cache[message_id] = metrics
                return metrics
                
        except Exception as e:
            logger.error(f"Failed to get metrics for {group_id}/{message_id}: {e}")
            
        return None
    
    async def schedule_post(
        self,
        group_id: int,
        text: str,
        schedule_time: datetime
    ) -> bool:
        """Schedule a post for future sending"""
        if is_dummy_mode():
            logger.info(f"🤖 Post scheduled for {schedule_time}: {text[:50]}...")
            return True
            
        # For now, we'll use a simple delay-based approach
        # In production, you'd want to use a proper task queue
        delay = (schedule_time - datetime.now()).total_seconds()
        
        if delay > 0:
            await asyncio.sleep(delay)
            
        return await self.send_message(group_id, text) is not None
    
    async def bulk_post(
        self,
        group_ids: List[int],
        text: str,
        delay_between_posts: int = 60
    ) -> Dict[int, bool]:
        """Send the same message to multiple groups"""
        results = {}
        
        for i, group_id in enumerate(group_ids):
            if i > 0:  # Add delay between posts except for the first one
                await asyncio.sleep(delay_between_posts)
                
            result = await self.send_message(group_id, text)
            results[group_id] = result is not None
            
        return results
    
    async def auto_reply(
        self,
        group_id: int,
        keywords: List[str],
        reply_text: str,
        enabled: bool = True
    ):
        """Set up automatic replies for specific keywords"""
        if is_dummy_mode():
            logger.info(f"🤖 Auto-reply configured for group {group_id}")
            return
            
        if not self.is_connected:
            return
            
        @self.client.on(events.NewMessage(chats=group_id))
        async def handler(event):
            if not enabled:
                return
                
            message_text = event.message.text.lower()
            
            for keyword in keywords:
                if keyword.lower() in message_text:
                    await self.send_message(
                        group_id,
                        reply_text,
                        reply_to=event.message.id
                    )
                    break
    
    def get_engagement_analytics(
        self,
        group_id: Optional[int] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get engagement analytics for groups"""
        if is_dummy_mode():
            return self._get_dummy_analytics(group_id, days)
            
        # Analyze post history and metrics
        start_date = datetime.now() - timedelta(days=days)
        
        relevant_posts = [
            post for post in self.post_history
            if post.date >= start_date and (group_id is None or post.group_id == group_id)
        ]
        
        if not relevant_posts:
            return {"total_posts": 0, "avg_engagement": 0}
            
        total_posts = len(relevant_posts)
        total_views = sum(
            self.metrics_cache.get(post.id, TelegramPostMetrics(
                0, 0, 0, 0, 0, {}, 0.0, datetime.now()
            )).views
            for post in relevant_posts
        )
        
        return {
            "total_posts": total_posts,
            "total_views": total_views,
            "avg_views_per_post": total_views / total_posts if total_posts > 0 else 0,
            "groups_posted": len(set(post.group_id for post in relevant_posts)),
            "posting_frequency": total_posts / days
        }
    
    # Dummy mode methods
    def _get_dummy_groups(self, limit: int) -> List[TelegramGroupInfo]:
        """Generate dummy groups for testing"""
        groups = []
        for i in range(min(limit, 10)):
            group = TelegramGroupInfo(
                id=1000 + i,
                title=f"Test Group {i+1}",
                username=f"testgroup{i+1}",
                members_count=1000 + i * 500,
                description=f"Description for test group {i+1}",
                is_channel=i % 3 == 0,
                is_group=i % 3 == 1,
                is_supergroup=i % 3 == 2,
                invite_link=f"https://t.me/testgroup{i+1}"
            )
            groups.append(group)
            self.managed_groups[group.id] = group
        return groups
    
    def _create_dummy_message(self, group_id: int, text: str) -> TelegramMessage:
        """Create a dummy message for testing"""
        message_id = len(self.post_history) + 1
        message = TelegramMessage(
            id=message_id,
            text=text,
            date=datetime.now(),
            sender_id=12345,
            group_id=group_id
        )
        self.post_history.append(message)
        return message
    
    def _get_dummy_messages(self, group_id: int, limit: int) -> List[TelegramMessage]:
        """Generate dummy messages for testing"""
        messages = []
        for i in range(limit):
            message = TelegramMessage(
                id=i + 1,
                text=f"Dummy message {i+1} in group {group_id}",
                date=datetime.now() - timedelta(hours=i),
                sender_id=12345 + i,
                group_id=group_id,
                views=100 + i * 10,
                forwards=i * 2
            )
            messages.append(message)
        return messages
    
    def _create_dummy_metrics(self, group_id: int, message_id: int) -> TelegramPostMetrics:
        """Create dummy metrics for testing"""
        return TelegramPostMetrics(
            message_id=message_id,
            group_id=group_id,
            views=150,
            forwards=5,
            replies=3,
            reactions={"👍": 10, "❤️": 5, "😂": 2},
            engagement_rate=0.15,
            timestamp=datetime.now()
        )
    
    def _get_dummy_analytics(self, group_id: Optional[int], days: int) -> Dict[str, Any]:
        """Generate dummy analytics for testing"""
        return {
            "total_posts": days * 2,
            "total_views": days * 300,
            "avg_views_per_post": 150,
            "groups_posted": 5 if group_id is None else 1,
            "posting_frequency": 2.0,
            "engagement_rate": 0.12,
            "top_performing_post": "Dummy high-engagement post",
            "peak_hours": [9, 14, 19, 21]
        }
    
    async def disconnect(self):
        """Disconnect from Telegram"""
        if is_dummy_mode():
            logger.info("🤖 Dummy Telegram disconnected")
            return
            
        if self.client and self.is_connected:
            await self.client.disconnect()
            self.is_connected = False
            logger.info("Disconnected from Telegram")

# Factory function for dependency injection
def create_telegram_automator(**kwargs) -> TelegramAutomator:
    """Create TelegramAutomator instance with dependency injection"""
    return TelegramAutomator(**kwargs)