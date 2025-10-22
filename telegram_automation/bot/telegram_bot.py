"""
Telegram Bot for Like4Like Automation
Handles conversations and manages YouTube video exchanges
"""
import os
import logging
import asyncio
import json
import re
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Safe imports with dummy mode support
DUMMY_MODE = os.getenv('DUMMY_MODE', 'true').lower() == 'true'
logger = logging.getLogger(__name__)

if DUMMY_MODE:
    logger.info("Using dummy Telethon implementations")
    
    # Dummy Telethon implementations
    class TelegramClient:
        def __init__(self, session_name, api_id, api_hash):
            self.session_name = session_name
            self.api_id = api_id  
            self.api_hash = api_hash
            self.is_connected = False
            logger.debug("Dummy Telegram Client: %s", session_name)
        
        async def start(self, phone=None, password=None):
            self.is_connected = True
            logger.debug("Dummy client started")
        
        async def disconnect(self):
            self.is_connected = False
            logger.debug("Dummy client disconnected")
        
        async def get_me(self):
            return User(id=123456789, first_name="Dummy", last_name="User")
        
        async def get_dialogs(self):
            return [Chat(id=i, title=f"Chat {i}") for i in range(1, 6)]
        
        async def send_message(self, entity, message):
            logger.debug("Send message to %s: %s", entity, message[:50])
            return type('Message', (), {'id': 1, 'text': message})()
        
        def on(self, event):
            def decorator(func):
                logger.debug("Event handler: %s", func.__name__)
                return func
            return decorator
        
        async def run_until_disconnected(self):
            logger.debug("Running until disconnected...")
            while self.is_connected:
                await asyncio.sleep(1)
    
    class events:
        class NewMessage:
            def __init__(self, **kwargs):
                self.kwargs = kwargs
            
            def __call__(self, func):
                return func
        
        @staticmethod
        def NewMessage(**kwargs):
            return events.NewMessage(**kwargs)
    
    class User:
        def __init__(self, id, first_name, last_name="", username=""):
            self.id = id
            self.first_name = first_name
            self.last_name = last_name
            self.username = username
    
    class Chat:
        def __init__(self, id, title):
            self.id = id
            self.title = title
    
    class Channel:
        def __init__(self, id, title, username=""):
            self.id = id
            self.title = title
            self.username = username
    
    class FloodWaitError(Exception):
        def __init__(self, seconds):
            self.seconds = seconds
            super().__init__(f"Flood wait: {seconds}s")
    
    class PeerFloodError(Exception):
        pass

else:
    # Production imports
    logger.info("Using real Telethon implementations")
    # Note: These will only work if telethon is installed
    # In production: pip install telethon==1.33.1

try:
    from telegram_automation.database.models import DatabaseConnection, Exchange, ExchangeStatus, Contact, ContactStatus, ConversationContext, ConversationState
    EXTERNAL_DB_AVAILABLE = True
except ImportError:
    EXTERNAL_DB_AVAILABLE = False

__all__ = ['TelegramClient', 'start', 'disconnect', 'get_me', 'get_dialogs', 'send_message', 'on', 'decorator', 'run_until_disconnected', 'events', 'NewMessage', 'NewMessage', 'User', 'Chat', 'Channel', 'FloodWaitError', 'PeerFloodError', 'DatabaseConnection', 'create_exchange', 'get_exchange_by_id', 'update_exchange', 'create_contact', 'get_contact_by_telegram_id', 'get_contact_by_user_id', 'update_contact', 'create_conversation_context', 'create_conversation_state', 'get_conversation_state', 'execute_query', 'execute_command', 'get_active_promotion_video', 'Exchange', 'ExchangeStatus', 'Contact', 'ContactStatus', 'Status', 'ConversationContext', 'ConversationState', 'State', 'calculate_reliability_score', 'TelegramBot', 'start', 'stop', 'process_message', 'MessageClassifier', 'classify_message', 'TelegramLike4LikeBot', 'start', 'load_monitored_groups', 'load_current_video', 'handle_new_message', 'process_like4like_message', 'send_initial_dm', 'craft_initial_message', 'generate_initial_terms', 'handle_private_message', 'process_conversation_response', 'check_dm_limit', 'reset_daily_limits', 'check_timeouts', 'handle_conversation_timeout', 'handle_exchange_timeout', 'log_message']

if not EXTERNAL_DB_AVAILABLE:
    logger.info("Using dummy database models")
    
    class DatabaseConnection:
        def __init__(self, database_url: str = None):
            self.database_url = database_url or "sqlite:///dummy.db"
            logger.debug("Dummy database connection: %s", self.database_url)
        
        async def create_exchange(self, exchange_data): 
            logger.debug("Create exchange: %s", exchange_data)
            return 1
        async def get_exchange_by_id(self, exchange_id): 
            return None
        async def update_exchange(self, exchange): 
            logger.debug("Update exchange: %s", exchange)
        async def create_contact(self, contact_data):
            logger.debug("Create contact: %s", contact_data)
            return 1
        async def get_contact_by_telegram_id(self, telegram_id):
            return None
        async def get_contact_by_user_id(self, user_id, platform):
            return None
        async def update_contact(self, contact):
            logger.debug("Update contact: %s", contact)
        async def create_conversation_context(self, context_data):
            logger.debug("Create conversation: %s", context_data)
            return 1
        async def create_conversation_state(self, context_data):
            logger.debug("Create conversation state: %s", context_data)
            return 1
        async def get_conversation_state(self, contact_id):
            return None
        async def execute_query(self, query, *args):
            logger.debug("Execute query: %s", query[:50])
            return []
        async def execute_command(self, query, *args):
            logger.debug("Execute command: %s", query[:50])
        async def get_active_promotion_video(self):
            return None
    
    class Exchange:
        def __init__(self):
            self.id = 1
            self.exchange_uuid = "dummy-uuid"
            self.status = "pending"
    
    class ExchangeStatus:
        PENDING = "pending"
        CONFIRMED = "confirmed"
        COMPLETED = "completed"
    
    class Contact:
        def __init__(self, **kwargs):
            self.id = kwargs.get('id', 1)
            self.telegram_id = kwargs.get('telegram_id', 123456)
            self.user_id = kwargs.get('user_id', 123456)  # Add user_id
            self.username = kwargs.get('username', 'dummyuser')
            self.first_name = kwargs.get('first_name', 'Dummy')
            self.last_name = kwargs.get('last_name', 'User')
            self.status = kwargs.get('status', 'discovered')
            self.reliability_score = kwargs.get('reliability_score', 50)
            self.created_at = datetime.now()
            # Add missing attributes
            self.first_contact_at = None
            self.last_contact_at = None
    
    class ContactStatus:
        class Status:
            def __init__(self, value):
                self.value = value
        
        DISCOVERED = Status('discovered')
        CONTACTED = Status('contacted')
        RESPONDED = Status('responded')
        ACTIVE_SAVED = Status('active_saved')
        UNRESPONSIVE = Status('unresponsive')
    
    class ConversationContext:
        def __init__(self, **kwargs):
            self.id = kwargs.get('id', 1)
            self.contact_id = kwargs.get('contact_id', 1)
            self.current_state = kwargs.get('current_state', 'waiting')
            self.their_video_url = kwargs.get('their_video_url', '')
            self.extracted_terms = kwargs.get('extracted_terms', {})
            self.created_at = datetime.now()
            # Add missing attributes
            self.initiated_by = kwargs.get('initiated_by', 'us')
    
    class ConversationState:
        class State:
            def __init__(self, value):
                self.value = value
        
        WAITING_RESPONSE = State('waiting_response')
        NEGOTIATING = State('negotiating')
        CONFIRMED = State('confirmed')
    
# Dummy function for reliability calculation
def calculate_reliability_score(contact_data):
    """Calculate reliability score for dummy mode"""
    logger.debug("Calculate reliability score")
    return random.randint(60, 90)
class TelegramBot:
    """Main Telegram Bot class for Like4Like automation"""
    
    def __init__(self, api_id: int, api_hash: str, bot_token: str, database_url: str = "sqlite:///dummy.db"):
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        self.database_url = database_url or "sqlite:///dummy.db"
        
        # Initialize client
        if DUMMY_MODE:
            self.client = TelegramClient('dummy_session', api_id, api_hash)
            logger.info("Dummy Telegram bot initialized")
        else:
            logger.info("Production Telegram bot initialized")
            # In production, use real TelegramClient
        
        self.db = DatabaseConnection(self.database_url)
        self.is_running = False
    
    async def start(self):
        """Start the bot"""
        logger.info("Starting Telegram bot...")
        self.is_running = True
        
        if DUMMY_MODE:
            await self.client.start()
            logger.info("Dummy bot started")
        else:
            logger.info("Production bot would start here")
    
    async def stop(self):
        """Stop the bot"""
        logger.info("Stopping Telegram bot...")
        self.is_running = False
        
        if DUMMY_MODE:
            await self.client.disconnect()
            logger.info("Dummy bot stopped")
    
    async def process_message(self, message):
        """Process incoming message"""
        logger.debug("Processing message: %s", message)
        # Message processing logic would go here

logger = logging.getLogger(__name__)


class MessageClassifier:
    """
    Classifies messages to determine if they're like4like requests
    Simple rule-based classifier (can be replaced with ML later)
    """
    
    # Like4Like keywords (positive indicators)
    LIKE4LIKE_KEYWORDS = [
        'like4like', 'l4l', 'sub4sub', 's4s', 'subscribe',
        'support', 'music', 'artist', 'song', 'video',
        'youtube', 'channel', 'check out', 'new music',
        'playlist', 'stream', 'listen', 'watch',
        'help me', 'support me', 'promote', 'share'
    ]
    
    # Exclusion keywords (negative indicators)
    EXCLUSION_KEYWORDS = [
        'selling', 'buy', 'purchase', 'money', 'paid',
        'service', 'bot', 'spam', 'fake', 'scam',
        'gambling', 'casino', 'crypto', 'trading'
    ]
    
    # YouTube URL patterns
    YOUTUBE_PATTERNS = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)',
        r'youtube\.com/channel/([a-zA-Z0-9_-]+)',
        r'youtube\.com/@([a-zA-Z0-9_.-]+)'
    ]
    
    def classify_message(self, message_text: str) -> Dict[str, Any]:
        """
        Classify message and extract relevant info
        
        Returns:
            {
                'is_like4like': bool,
                'confidence': float,
                'youtube_urls': List[str],
                'extracted_terms': Dict[str, int],
                'reasons': List[str]
            }
        """
        if not message_text:
            return {
                'is_like4like': False,
                'confidence': 0.0,
                'youtube_urls': [],
                'extracted_terms': {},
                'reasons': ['Empty message']
            }
        
        text_lower = message_text.lower()
        reasons = []
        confidence = 0.0
        
        # Extract YouTube URLs
        youtube_urls = []
        for pattern in self.YOUTUBE_PATTERNS:
            matches = re.findall(pattern, message_text)
            for match in matches:
                if 'youtube.com/watch' in message_text or 'youtu.be' in message_text:
                    youtube_urls.append(f"https://youtube.com/watch?v={match}")
                elif 'youtube.com/playlist' in message_text:
                    youtube_urls.append(f"https://youtube.com/playlist?list={match}")
                elif 'youtube.com/channel' in message_text:
                    youtube_urls.append(f"https://youtube.com/channel/{match}")
                elif 'youtube.com/@' in message_text:
                    youtube_urls.append(f"https://youtube.com/@{match}")
        
        # Check for YouTube URLs (strong positive indicator)
        if youtube_urls:
            confidence += 0.4
            reasons.append('Contains YouTube URLs')
        
        # Check for like4like keywords
        keyword_matches = []
        for keyword in self.LIKE4LIKE_KEYWORDS:
            if keyword in text_lower:
                keyword_matches.append(keyword)
                if keyword in ['like4like', 'l4l', 'sub4sub', 's4s']:
                    confidence += 0.3  # Strong indicators
                elif keyword in ['subscribe', 'support', 'check out']:
                    confidence += 0.2  # Medium indicators
                else:
                    confidence += 0.1  # Weak indicators
        
        if keyword_matches:
            reasons.append(f'Contains keywords: {", ".join(keyword_matches)}')
        
        # Check for exclusion keywords (negative indicators)
        exclusion_matches = []
        for keyword in self.EXCLUSION_KEYWORDS:
            if keyword in text_lower:
                exclusion_matches.append(keyword)
                confidence -= 0.3
        
        if exclusion_matches:
            reasons.append(f'Contains exclusion keywords: {", ".join(exclusion_matches)}')
        
        # Extract potential terms (numbers that might indicate exchange terms)
        extracted_terms = {}
        
        # Look for patterns like "5 likes", "10 subs", "2 minutes watch"
        patterns = {
            'likes': r'(\d+)\s*(?:like|👍|❤️)',
            'subs': r'(\d+)\s*(?:sub|subscribe|subscription)',
            'comments': r'(\d+)\s*(?:comment|💬)',
            'watch_seconds': r'(\d+)\s*(?:second|minute|min|watch)',
        }
        
        for term, pattern in patterns.items():
            matches = re.findall(pattern, text_lower)
            if matches:
                # Take the first/largest number found
                numbers = [int(m) for m in matches]
                extracted_terms[term] = max(numbers)
                if term == 'watch_seconds' and extracted_terms[term] < 10:
                    # Probably minutes, convert to seconds
                    extracted_terms[term] *= 60
        
        # Adjust confidence based on message structure
        if len(text_lower.split()) > 5:  # Longer messages are more likely to be genuine
            confidence += 0.1
        
        if any(char in text_lower for char in ['?', 'help', 'please']):
            confidence += 0.1
            reasons.append('Contains request language')
        
        # Cap confidence between 0 and 1
        confidence = max(0.0, min(1.0, confidence))
        
        # Determine if it's like4like
        is_like4like = confidence >= 0.3 and youtube_urls  # Need both confidence and YouTube URL
        
        return {
            'is_like4like': is_like4like,
            'confidence': confidence,
            'youtube_urls': youtube_urls,
            'extracted_terms': extracted_terms,
            'reasons': reasons
        }


class TelegramLike4LikeBot:
    """
    Main Telegram bot for Like4Like automation
    """
    
    def __init__(self, api_id: int, api_hash: str, session_name: str, db: DatabaseConnection):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.db = db
        
        # Initialize client
        self.client = TelegramClient(session_name, api_id, api_hash)
        
        # Initialize classifier
        self.classifier = MessageClassifier()
        
        # Rate limiting
        self.dm_count_today = 0
        self.dm_count_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.max_dm_per_day = 50  # Configurable limit
        
        # Groups to monitor (loaded from database)
        self.monitored_groups: Dict[int, Dict[str, Any]] = {}
        
        # Currently promoted video
        self.current_video: Optional[Dict[str, Any]] = None
        
        logger.info(f"🤖 Bot initialized with session: {session_name}")
    
    async def start(self):
        """Start the bot"""
        await self.client.start()
        
        # Load configuration from database
        await self.load_monitored_groups()
        await self.load_current_video()
        
        # Register event handlers
        self.client.add_event_handler(self.handle_new_message, events.NewMessage)
        self.client.add_event_handler(self.handle_private_message, events.NewMessage(incoming=True, func=lambda e: e.is_private))
        
        logger.info("✅ Bot started and listening for messages")
        
        # Start background tasks
        asyncio.create_task(self.reset_daily_limits())
        asyncio.create_task(self.check_timeouts())
        
        me = await self.client.get_me()
        logger.info(f"📱 Logged in as: {me.first_name} (@{me.username})")
    
    async def load_monitored_groups(self):
        """Load monitored groups from database"""
        query = "SELECT * FROM monitored_groups WHERE is_active = true"
        groups = await self.db.execute_query(query)
        
        self.monitored_groups = {}
        for group in groups:
            self.monitored_groups[group['group_id']] = group
        
        logger.info(f"📁 Loaded {len(self.monitored_groups)} monitored groups")
    
    async def load_current_video(self):
        """Load current video being promoted"""
        self.current_video = await self.db.get_active_promotion_video()
        
        if self.current_video:
            logger.info(f"🎵 Current promotion video: {self.current_video['title']}")
        else:
            logger.warning("⚠️  No video set for promotion")
    
    async def handle_new_message(self, event):
        """Handle new messages in monitored groups"""
        try:
            # Check if message is from monitored group
            chat_id = event.chat_id
            if chat_id not in self.monitored_groups:
                return
            
            group_info = self.monitored_groups[chat_id]
            
            # Get message details
            message = event.message
            sender = await event.get_sender()
            
            # Skip our own messages
            if sender.id == (await self.client.get_me()).id:
                return
            
            # Skip bot messages
            if getattr(sender, 'bot', False):
                return
            
            message_text = message.text or ""
            
            logger.debug(f"📨 New message in {group_info['group_name']}: {message_text[:100]}...")
            
            # Classify message
            classification = self.classifier.classify_message(message_text)
            
            # Log message for analysis
            await self.log_message(
                platform="telegram",
                group_id=chat_id,
                group_name=group_info['group_name'],
                user_id=sender.id,
                username=getattr(sender, 'username', None),
                message_id=message.id,
                message_text=message_text,
                classification=classification
            )
            
            # If it's a like4like message, process it
            if classification['is_like4like']:
                await self.process_like4like_message(event, sender, classification)
                
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")
    
    async def process_like4like_message(self, event, sender, classification):
        """Process a detected like4like message"""
        try:
            logger.info(f"🎯 Detected like4like message from @{getattr(sender, 'username', 'unknown')} (confidence: {classification['confidence']:.2f})")
            
            # Check if we already know this contact
            existing_contact = await self.db.get_contact_by_user_id(sender.id, "telegram")
            
            if existing_contact:
                # Update last seen
                existing_contact.last_contact_at = datetime.now()
                await self.db.update_contact(existing_contact)
                
                # If they're already active and reliable, don't spam them
                if existing_contact.status == ContactStatus.ACTIVE_SAVED.value and existing_contact.reliability_score >= 70:
                    logger.info(f"   ℹ️  Contact {existing_contact.username} is already active and reliable, skipping")
                    return
                
                # If we recently contacted them, skip
                if existing_contact.last_contact_at and existing_contact.last_contact_at > datetime.now() - timedelta(days=3):
                    logger.info(f"   ℹ️  Recently contacted {existing_contact.username}, skipping")
                    return
            
            # Check daily DM limit
            if not await self.check_dm_limit():
                logger.warning("⚠️  Daily DM limit reached, skipping")
                return
            
            # Create or update contact
            if not existing_contact:
                contact = Contact(
                    user_id=sender.id,
                    username=getattr(sender, 'username', None),
                    display_name=f"{getattr(sender, 'first_name', '')} {getattr(sender, 'last_name', '')}".strip(),
                    platform="telegram",
                    discovered_at=datetime.now(),
                    discovered_in_group=self.monitored_groups[event.chat_id]['group_name'],
                    discovered_in_group_id=event.chat_id,
                    original_message=event.message.text,
                    original_video_url=classification['youtube_urls'][0] if classification['youtube_urls'] else None,
                    status=ContactStatus.DISCOVERED.value
                )
                
                contact = await self.db.create_contact(contact)
            else:
                contact = existing_contact
            
            # Send initial DM
            await self.send_initial_dm(contact, classification)
            
        except Exception as e:
            logger.error(f"❌ Error processing like4like message: {e}")
    
    async def send_initial_dm(self, contact: Contact, classification: Dict[str, Any]):
        """Send initial DM to a contact"""
        try:
            if not self.current_video:
                logger.error("❌ No video set for promotion, can't send DM")
                return
            
            # Craft personalized message
            their_video_url = classification['youtube_urls'][0] if classification['youtube_urls'] else None
            extracted_terms = classification.get('extracted_terms', {})
            
            # Generate message
            message = await self.craft_initial_message(contact, their_video_url, extracted_terms)
            
            # Send DM
            await self.client.send_message(contact.user_id, message)
            
            # Update contact status
            contact.status = ContactStatus.CONTACTED.value
            contact.first_contact_at = datetime.now()
            contact.last_contact_at = datetime.now()
            await self.db.update_contact(contact)
            
            # Create exchange record
            exchange = Exchange(
                contact_id=contact.id,
                initiated_by="us",
                our_video_url=self.current_video['video_url'],
                their_video_url=their_video_url,
                terms=self.generate_initial_terms(extracted_terms),
                status=ExchangeStatus.INITIATED.value
            )
            
            exchange = await self.db.create_exchange(exchange)
            
            # Create conversation state
            conversation_context = ConversationContext(
                contact_id=contact.id,
                exchange_id=exchange.id,
                current_state=ConversationState.WAITING_RESPONSE.value,
                context={
                    'initial_message_sent': True,
                    'their_video_url': their_video_url,
                    'proposed_terms': exchange.terms
                },
                state_expires_at=datetime.now() + timedelta(hours=24)
            )
            
            await self.db.create_conversation_state(conversation_context)
            
            # Increment DM counter
            self.dm_count_today += 1
            
            logger.info(f"📤 Sent initial DM to @{contact.username}")
            
        except FloodWaitError as e:
            logger.warning(f"⏳ Rate limited, waiting {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
        except PeerFloodError:
            logger.warning("⚠️  Peer flood error, backing off from DMs")
        except Exception as e:
            logger.error(f"❌ Failed to send DM: {e}")
    
    async def craft_initial_message(self, contact: Contact, their_video_url: Optional[str], extracted_terms: Dict[str, Any]) -> str:
        """Craft personalized initial message"""
        
        # Greeting variations
        greetings = [
            f"Hey @{contact.username}!",
            f"Hi {contact.display_name or '@' + (contact.username or 'there')}!",
            f"Hello @{contact.username}!",
        ]
        
        greeting = random.choice(greetings)
        
        # Main message variations
        if their_video_url:
            messages = [
                f"I saw your video and it looks great! I'm also a music artist and I'd love to do a like4like exchange with you.",
                f"Your music sounds awesome! I'm also promoting my music and would love to support each other.",
                f"Nice video! I'm a musician too and I think we could help each other grow our channels.",
            ]
        else:
            messages = [
                f"I saw you're looking for music promotion support! I'm also an artist and would love to exchange likes/subs.",
                f"Hey! I'm also promoting my music and looking for like4like exchanges. Want to support each other?",
                f"I'm a music artist too and I think we could help each other grow our channels!",
            ]
        
        main_message = random.choice(messages)
        
        # Our video promotion
        video_promotion = f"\nHere's my latest track: {self.current_video['video_url']}"
        
        # Proposed terms
        if extracted_terms:
            terms_text = f"\nI can do {extracted_terms.get('likes', 5)} likes"
            if extracted_terms.get('subs'):
                terms_text += f", {extracted_terms.get('subs', 1)} sub"
            if extracted_terms.get('comments'):
                terms_text += f", and {extracted_terms.get('comments', 1)} comment"
            terms_text += " on your video if you can do the same for mine!"
        else:
            # Default terms
            terms_text = f"\nI can do 5 likes, 1 sub, and 1 comment on your video if you can do the same for mine!"
        
        # Closing
        closings = [
            "\nLet me know if you're interested! 🎵",
            "\nSound good? 🚀",
            "\nWhat do you think? 💯",
        ]
        
        closing = random.choice(closings)
        
        # Combine message
        full_message = greeting + "\n\n" + main_message + video_promotion + terms_text + closing
        
        return full_message
    
    def generate_initial_terms(self, extracted_terms: Dict[str, Any]) -> Dict[str, int]:
        """Generate initial terms for exchange"""
        # Default terms
        terms = {
            'likes': 5,
            'subs': 1,
            'comments': 1,
            'watch_seconds': 60
        }
        
        # Adjust based on what they mentioned
        if extracted_terms:
            for key in ['likes', 'subs', 'comments', 'watch_seconds']:
                if key in extracted_terms:
                    terms[key] = min(extracted_terms[key], terms[key] * 2)  # Cap at 2x our default
        
        return terms
    
    async def handle_private_message(self, event):
        """Handle private messages (responses to our DMs)"""
        try:
            sender = await event.get_sender()
            message_text = event.message.text or ""
            
            logger.info(f"💬 Received DM from @{getattr(sender, 'username', 'unknown')}: {message_text[:100]}...")
            
            # Get contact
            contact = await self.db.get_contact_by_user_id(sender.id, "telegram")
            if not contact:
                logger.warning(f"   ⚠️  No contact record found for user {sender.id}")
                return
            
            # Update last response time
            contact.last_response_at = datetime.now()
            
            # Calculate response time if we have first contact time
            if contact.first_contact_at:
                response_time_minutes = int((datetime.now() - contact.first_contact_at).total_seconds() / 60)
                contact.response_time_avg = response_time_minutes
            
            # Update status to responded if not already
            if contact.status == ContactStatus.CONTACTED.value:
                contact.status = ContactStatus.RESPONDED.value
            
            await self.db.update_contact(contact)
            
            # Get conversation state
            conversation_state = await self.db.get_conversation_state(contact.id)
            if not conversation_state:
                logger.warning(f"   ⚠️  No conversation state found for contact {contact.id}")
                return
            
            # Process response based on current state
            await self.process_conversation_response(contact, conversation_state, message_text)
            
        except Exception as e:
            logger.error(f"❌ Error handling private message: {e}")
    
    async def process_conversation_response(self, contact: Contact, conversation_state: ConversationContext, message_text: str):
        """Process response in conversation state machine"""
        # This will be implemented in the next file (conversation_handler.py)
        # For now, just log
        logger.info(f"🔄 Processing response in state {conversation_state.current_state}: {message_text[:50]}...")
    
    async def check_dm_limit(self) -> bool:
        """Check if we can send more DMs today"""
        now = datetime.now()
        
        # Reset counter if it's a new day
        if now.date() > self.dm_count_reset_time.date():
            self.dm_count_today = 0
            self.dm_count_reset_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        return self.dm_count_today < self.max_dm_per_day
    
    async def reset_daily_limits(self):
        """Background task to reset daily limits"""
        while True:
            now = datetime.now()
            next_reset = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            sleep_seconds = (next_reset - now).total_seconds()
            
            await asyncio.sleep(sleep_seconds)
            
            self.dm_count_today = 0
            self.dm_count_reset_time = next_reset
            logger.info("🔄 Daily DM limit reset")
    
    async def check_timeouts(self):
        """Background task to check for timed out conversations/exchanges"""
        while True:
            try:
                # Check every 10 minutes
                await asyncio.sleep(600)
                
                # Check conversation state timeouts
                query = """
                SELECT * FROM conversation_states 
                WHERE state_expires_at IS NOT NULL 
                  AND state_expires_at < NOW()
                """
                
                expired_states = await self.db.execute_query(query)
                
                for state_data in expired_states:
                    await self.handle_conversation_timeout(state_data)
                
                # Check exchange timeouts
                query = """
                SELECT * FROM exchanges 
                WHERE timeout_at IS NOT NULL 
                  AND timeout_at < NOW()
                  AND status NOT IN ('completed', 'failed', 'no_response')
                """
                
                expired_exchanges = await self.db.execute_query(query)
                
                for exchange_data in expired_exchanges:
                    await self.handle_exchange_timeout(exchange_data)
                    
            except Exception as e:
                logger.error(f"❌ Error checking timeouts: {e}")
    
    async def handle_conversation_timeout(self, state_data: Dict[str, Any]):
        """Handle conversation state timeout"""
        logger.info(f"⏰ Conversation timeout for contact {state_data['contact_id']}")
        
        # Mark conversation as timed out
        await self.db.delete_conversation_state(state_data['contact_id'])
        
        # Update contact status
        contact = await self.db.get_contact_by_id(state_data['contact_id'])
        if contact and contact.status == ContactStatus.CONTACTED.value:
            contact.status = ContactStatus.UNRESPONSIVE.value
            await self.db.update_contact(contact)
    
    async def handle_exchange_timeout(self, exchange_data: Dict[str, Any]):
        """Handle exchange timeout"""
        logger.info(f"⏰ Exchange timeout for exchange {exchange_data['exchange_uuid']}")
        
        # Update exchange status
        query = "UPDATE exchanges SET status = $1 WHERE id = $2"
        await self.db.execute_command(query, ExchangeStatus.NO_RESPONSE.value, exchange_data['id'])
        
        # Update contact reliability
        contact = await self.db.get_contact_by_id(exchange_data['contact_id'])
        if contact:
            contact.failed_exchanges += 1
            contact.reliability_score = calculate_reliability_score(
                contact.successful_exchanges,
                contact.total_exchanges + 1,
                contact.failed_exchanges
            )
            await self.db.update_contact(contact)
    
    async def log_message(self, platform: str, group_id: int, group_name: str,
                         user_id: int, username: Optional[str], message_id: int,
                         message_text: str, classification: Dict[str, Any]):
        """Log message for analysis"""
        query = """
        INSERT INTO message_log (
            platform, group_id, group_name, user_id, username, message_id,
            message_text, video_urls, is_like4like, classification_confidence,
            extracted_terms, message_timestamp
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        """
        
        await self.db.execute_command(
            query,
            platform, group_id, group_name, user_id, username, message_id,
            message_text, classification['youtube_urls'], classification['is_like4like'],
            classification['confidence'], classification['extracted_terms'],
            datetime.now()
        )