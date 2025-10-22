"""
Database models and connection management for Telegram automation
Handles PostgreSQL operations for exchanges, contacts, and conversation tracking
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
import json
import uuid


__all__ = ['DummyConnection', 'execute', 'fetch', 'fetchrow', 'close', 'connect', 'asyncpg', 'ContactStatus', 'ExchangeStatus', 'ConversationState', 'Contact', 'Exchange', 'ConversationContext', 'DatabaseConnection', 'connect', 'disconnect', 'execute_query', 'execute_command', 'fetchone', 'create_contact', 'get_contact_by_user_id', 'get_contact_by_id', 'update_contact', 'get_contacts_ready_for_relaunch', 'count_contacts', 'create_exchange', 'get_exchange_by_id', 'update_exchange', 'get_active_exchanges', 'count_exchanges', 'create_conversation_state', 'get_conversation_state', 'update_conversation_state', 'delete_conversation_state', 'record_analytics', 'get_performance_summary', 'add_my_video', 'get_active_promotion_video', 'get_my_video_by_id', 'calculate_reliability_score', 'initialize_database']


# Safe imports with dummy mode support
DUMMY_MODE = os.getenv('DUMMY_MODE', 'true').lower() == 'true'

if DUMMY_MODE:
    print("🎭 Using dummy asyncpg implementation")
    
    class DummyConnection:
        async def execute(self, query, *args):
            print(f"🎭 SQL Execute: {query[:50]}...")
            return "SELECT 1"
        
        async def fetch(self, query, *args):
            print(f"🎭 SQL Fetch: {query[:50]}...")
            return []
        
        async def fetchrow(self, query, *args):
            print(f"🎭 SQL Fetchrow: {query[:50]}...")
            return None
        
        async def close(self):
            print("🎭 Close database connection")
    
    async def connect(*args, **kwargs):
        print("🎭 Connect to dummy database")
        return DummyConnection()
    
    # Create asyncpg-like module
    class asyncpg:
        connect = staticmethod(connect)
        Connection = DummyConnection

else:
    print("🚀 Production mode - asyncpg should be installed")
    # Note: In production, install with: pip install asyncpg==0.29.0

logger = logging.getLogger(__name__)


class ContactStatus(Enum):
    DISCOVERED = "discovered"
    CONTACTED = "contacted"
    RESPONDED = "responded"
    ACTIVE_SAVED = "active_saved"
    UNRESPONSIVE = "unresponsive"
    BLOCKED = "blocked"


class ExchangeStatus(Enum):
    INITIATED = "initiated"
    NEGOTIATING = "negotiating"
    AGREED = "agreed"
    MY_TURN_DONE = "my_turn_done"
    THEIR_TURN_DONE = "their_turn_done"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_RESPONSE = "no_response"
    PARTNER_DID_NOT_COMPLETE = "partner_did_not_complete"


class ConversationState(Enum):
    WAITING_RESPONSE = "waiting_response"
    NEGOTIATING_TERMS = "negotiating_terms"
    WAITING_EXECUTION = "waiting_execution"
    VERIFYING_COMPLETION = "verifying_completion"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Contact:
    """Represents a contact from Telegram/Discord/WhatsApp"""
    id: Optional[int] = None
    user_id: Optional[int] = None
    username: Optional[str] = None
    display_name: Optional[str] = None
    platform: str = "telegram"
    
    # Discovery info
    discovered_at: Optional[datetime] = None
    discovered_in_group: Optional[str] = None
    discovered_in_group_id: Optional[int] = None
    original_message: Optional[str] = None
    original_video_url: Optional[str] = None
    
    # Status and reliability
    status: str = ContactStatus.DISCOVERED.value
    reliability_score: int = 50
    total_exchanges: int = 0
    successful_exchanges: int = 0
    failed_exchanges: int = 0
    
    # Communication tracking
    first_contact_at: Optional[datetime] = None
    last_contact_at: Optional[datetime] = None
    last_response_at: Optional[datetime] = None
    last_exchange_at: Optional[datetime] = None
    
    # Preferences
    preferred_terms: Optional[Dict[str, Any]] = None
    response_time_avg: Optional[int] = None
    active_hours_pattern: Optional[Dict[str, Any]] = None
    
    # Notes and tags
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Exchange:
    """Represents a like4like exchange"""
    id: Optional[int] = None
    exchange_uuid: Optional[str] = None
    contact_id: Optional[int] = None
    initiated_by: str = "us"
    
    # Exchange content
    our_video_url: Optional[str] = None
    their_video_url: Optional[str] = None
    
    # Terms
    terms: Optional[Dict[str, Any]] = None
    
    # Status
    status: str = ExchangeStatus.INITIATED.value
    
    # Execution tracking
    our_execution_started_at: Optional[datetime] = None
    our_execution_completed_at: Optional[datetime] = None
    our_execution_results: Optional[Dict[str, Any]] = None
    their_execution_verified_at: Optional[datetime] = None
    their_execution_results: Optional[Dict[str, Any]] = None
    
    # Conversation
    conversation_history: Optional[List[Dict[str, Any]]] = None
    
    # Timing
    initiated_at: Optional[datetime] = None
    agreed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout_at: Optional[datetime] = None
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class ConversationContext:
    """Context for ongoing conversation with a contact"""
    id: Optional[int] = None
    contact_id: Optional[int] = None
    exchange_id: Optional[int] = None
    
    # State machine
    current_state: str = ConversationState.WAITING_RESPONSE.value
    previous_state: Optional[str] = None
    
    # Context data
    context: Optional[Dict[str, Any]] = None
    
    # Timing
    state_entered_at: Optional[datetime] = None
    state_expires_at: Optional[datetime] = None
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DatabaseConnection:
    """AsyncPG database connection manager"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Initialize connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20,
                command_timeout=30
            )
            logger.info("✅ Database connection pool created")
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            raise
    
    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("🔒 Database connection pool closed")
    
    async def execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dicts"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def execute_command(self, query: str, *args) -> str:
        """Execute INSERT/UPDATE/DELETE and return status"""
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetchone(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Execute query and return single result"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
    
    # ==================== CONTACT METHODS ====================
    
    async def create_contact(self, contact: Contact) -> Contact:
        """Create new contact"""
        query = """
        INSERT INTO contacts (
            user_id, username, display_name, platform,
            discovered_in_group, discovered_in_group_id, 
            original_message, original_video_url, status
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING id, created_at, updated_at
        """
        
        result = await self.fetchone(
            query,
            contact.user_id, contact.username, contact.display_name, contact.platform,
            contact.discovered_in_group, contact.discovered_in_group_id,
            contact.original_message, contact.original_video_url, contact.status
        )
        
        contact.id = result['id']
        contact.created_at = result['created_at']
        contact.updated_at = result['updated_at']
        
        logger.info(f"✅ Created contact: {contact.username} (ID: {contact.id})")
        return contact
    
    async def get_contact_by_user_id(self, user_id: int, platform: str = "telegram") -> Optional[Contact]:
        """Get contact by user ID and platform"""
        query = "SELECT * FROM contacts WHERE user_id = $1 AND platform = $2"
        result = await self.fetchone(query, user_id, platform)
        
        if result:
            return Contact(**result)
        return None
    
    async def get_contact_by_id(self, contact_id: int) -> Optional[Contact]:
        """Get contact by ID"""
        query = "SELECT * FROM contacts WHERE id = $1"
        result = await self.fetchone(query, contact_id)
        
        if result:
            return Contact(**result)
        return None
    
    async def update_contact(self, contact: Contact) -> Contact:
        """Update existing contact"""
        query = """
        UPDATE contacts SET
            username = $2, display_name = $3, status = $4,
            reliability_score = $5, total_exchanges = $6,
            successful_exchanges = $7, failed_exchanges = $8,
            first_contact_at = $9, last_contact_at = $10,
            last_response_at = $11, last_exchange_at = $12,
            preferred_terms = $13, response_time_avg = $14,
            notes = $15, tags = $16
        WHERE id = $1
        RETURNING updated_at
        """
        
        result = await self.fetchone(
            query,
            contact.id, contact.username, contact.display_name, contact.status,
            contact.reliability_score, contact.total_exchanges,
            contact.successful_exchanges, contact.failed_exchanges,
            contact.first_contact_at, contact.last_contact_at,
            contact.last_response_at, contact.last_exchange_at,
            json.dumps(contact.preferred_terms) if contact.preferred_terms else None,
            contact.response_time_avg, contact.notes, contact.tags
        )
        
        contact.updated_at = result['updated_at']
        return contact
    
    async def get_contacts_ready_for_relaunch(self, limit: int = 100) -> List[Contact]:
        """Get contacts ready for relaunch notifications"""
        query = """
        SELECT * FROM contacts_ready_for_relaunch
        LIMIT $1
        """
        
        results = await self.execute_query(query, limit)
        return [Contact(**row) for row in results]
    
    async def count_contacts(self, status: Optional[str] = None) -> int:
        """Count contacts, optionally filtered by status"""
        if status:
            query = "SELECT COUNT(*) as count FROM contacts WHERE status = $1"
            result = await self.fetchone(query, status)
        else:
            query = "SELECT COUNT(*) as count FROM contacts"
            result = await self.fetchone(query)
        
        return result['count']
    
    # ==================== EXCHANGE METHODS ====================
    
    async def create_exchange(self, exchange: Exchange) -> Exchange:
        """Create new exchange"""
        query = """
        INSERT INTO exchanges (
            contact_id, initiated_by, our_video_url, their_video_url,
            terms, status, timeout_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id, exchange_uuid, created_at, updated_at
        """
        
        # Set timeout (24 hours from now)
        timeout_at = datetime.now() + timedelta(hours=24)
        
        result = await self.fetchone(
            query,
            exchange.contact_id, exchange.initiated_by,
            exchange.our_video_url, exchange.their_video_url,
            json.dumps(exchange.terms) if exchange.terms else None,
            exchange.status, timeout_at
        )
        
        exchange.id = result['id']
        exchange.exchange_uuid = result['exchange_uuid']
        exchange.created_at = result['created_at']
        exchange.updated_at = result['updated_at']
        exchange.timeout_at = timeout_at
        
        logger.info(f"✅ Created exchange: {exchange.exchange_uuid}")
        return exchange
    
    async def get_exchange_by_id(self, exchange_id: int) -> Optional[Exchange]:
        """Get exchange by ID"""
        query = "SELECT * FROM exchanges WHERE id = $1"
        result = await self.fetchone(query, exchange_id)
        
        if result:
            # Parse JSON fields
            result['terms'] = json.loads(result['terms']) if result['terms'] else None
            result['our_execution_results'] = json.loads(result['our_execution_results']) if result['our_execution_results'] else None
            result['their_execution_results'] = json.loads(result['their_execution_results']) if result['their_execution_results'] else None
            result['conversation_history'] = json.loads(result['conversation_history']) if result['conversation_history'] else None
            
            return Exchange(**result)
        return None
    
    async def update_exchange(self, exchange: Exchange) -> Exchange:
        """Update existing exchange"""
        query = """
        UPDATE exchanges SET
            status = $2, our_execution_started_at = $3,
            our_execution_completed_at = $4, our_execution_results = $5,
            their_execution_verified_at = $6, their_execution_results = $7,
            conversation_history = $8, agreed_at = $9, completed_at = $10
        WHERE id = $1
        RETURNING updated_at
        """
        
        result = await self.fetchone(
            query,
            exchange.id, exchange.status,
            exchange.our_execution_started_at, exchange.our_execution_completed_at,
            json.dumps(exchange.our_execution_results) if exchange.our_execution_results else None,
            exchange.their_execution_verified_at,
            json.dumps(exchange.their_execution_results) if exchange.their_execution_results else None,
            json.dumps(exchange.conversation_history) if exchange.conversation_history else None,
            exchange.agreed_at, exchange.completed_at
        )
        
        exchange.updated_at = result['updated_at']
        return exchange
    
    async def get_active_exchanges(self) -> List[Exchange]:
        """Get all active exchanges (not completed/failed)"""
        query = """
        SELECT * FROM exchanges 
        WHERE status NOT IN ('completed', 'failed', 'no_response', 'partner_did_not_complete')
        ORDER BY created_at DESC
        """
        
        results = await self.execute_query(query)
        exchanges = []
        
        for row in results:
            # Parse JSON fields
            row['terms'] = json.loads(row['terms']) if row['terms'] else None
            row['our_execution_results'] = json.loads(row['our_execution_results']) if row['our_execution_results'] else None
            row['their_execution_results'] = json.loads(row['their_execution_results']) if row['their_execution_results'] else None
            row['conversation_history'] = json.loads(row['conversation_history']) if row['conversation_history'] else None
            
            exchanges.append(Exchange(**row))
        
        return exchanges
    
    async def count_exchanges(self, status: Optional[str] = None) -> int:
        """Count exchanges, optionally filtered by status"""
        if status:
            query = "SELECT COUNT(*) as count FROM exchanges WHERE status = $1"
            result = await self.fetchone(query, status)
        else:
            query = "SELECT COUNT(*) as count FROM exchanges"
            result = await self.fetchone(query)
        
        return result['count']
    
    # ==================== CONVERSATION STATE METHODS ====================
    
    async def create_conversation_state(self, context: ConversationContext) -> ConversationContext:
        """Create or update conversation state"""
        # First, try to update existing state for this contact
        query = """
        INSERT INTO conversation_states (
            contact_id, exchange_id, current_state, context, state_expires_at
        ) VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (contact_id) DO UPDATE SET
            exchange_id = EXCLUDED.exchange_id,
            previous_state = conversation_states.current_state,
            current_state = EXCLUDED.current_state,
            context = EXCLUDED.context,
            state_entered_at = NOW(),
            state_expires_at = EXCLUDED.state_expires_at,
            updated_at = NOW()
        RETURNING id, created_at, updated_at
        """
        
        result = await self.fetchone(
            query,
            context.contact_id, context.exchange_id, context.current_state,
            json.dumps(context.context) if context.context else None,
            context.state_expires_at
        )
        
        context.id = result['id']
        context.created_at = result['created_at']
        context.updated_at = result['updated_at']
        
        return context
    
    async def get_conversation_state(self, contact_id: int) -> Optional[ConversationContext]:
        """Get conversation state for contact"""
        query = "SELECT * FROM conversation_states WHERE contact_id = $1"
        result = await self.fetchone(query, contact_id)
        
        if result:
            result['context'] = json.loads(result['context']) if result['context'] else None
            return ConversationContext(**result)
        return None
    
    async def update_conversation_state(self, context: ConversationContext) -> ConversationContext:
        """Update conversation state"""
        query = """
        UPDATE conversation_states SET
            exchange_id = $2, previous_state = current_state,
            current_state = $3, context = $4,
            state_entered_at = NOW(), state_expires_at = $5
        WHERE contact_id = $1
        RETURNING updated_at
        """
        
        result = await self.fetchone(
            query,
            context.contact_id, context.exchange_id, context.current_state,
            json.dumps(context.context) if context.context else None,
            context.state_expires_at
        )
        
        context.updated_at = result['updated_at']
        return context
    
    async def delete_conversation_state(self, contact_id: int):
        """Delete conversation state (conversation ended)"""
        query = "DELETE FROM conversation_states WHERE contact_id = $1"
        await self.execute_command(query, contact_id)
    
    # ==================== ANALYTICS METHODS ====================
    
    async def record_analytics(self, date: datetime, metrics: Dict[str, Any]):
        """Record daily analytics"""
        query = """
        INSERT INTO bot_analytics (
            date, new_contacts_found, messages_processed,
            exchanges_initiated, exchanges_completed, exchanges_failed,
            dm_sent, dm_responses_received, average_response_time_minutes,
            youtube_actions_attempted, youtube_actions_successful
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        ON CONFLICT (date) DO UPDATE SET
            new_contacts_found = EXCLUDED.new_contacts_found,
            messages_processed = EXCLUDED.messages_processed,
            exchanges_initiated = EXCLUDED.exchanges_initiated,
            exchanges_completed = EXCLUDED.exchanges_completed,
            exchanges_failed = EXCLUDED.exchanges_failed,
            dm_sent = EXCLUDED.dm_sent,
            dm_responses_received = EXCLUDED.dm_responses_received,
            average_response_time_minutes = EXCLUDED.average_response_time_minutes,
            youtube_actions_attempted = EXCLUDED.youtube_actions_attempted,
            youtube_actions_successful = EXCLUDED.youtube_actions_successful,
            updated_at = NOW()
        """
        
        await self.execute_command(
            query, date.date(),
            metrics.get('new_contacts_found', 0),
            metrics.get('messages_processed', 0),
            metrics.get('exchanges_initiated', 0),
            metrics.get('exchanges_completed', 0),
            metrics.get('exchanges_failed', 0),
            metrics.get('dm_sent', 0),
            metrics.get('dm_responses_received', 0),
            metrics.get('average_response_time_minutes'),
            metrics.get('youtube_actions_attempted', 0),
            metrics.get('youtube_actions_successful', 0)
        )
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get bot performance summary"""
        query = "SELECT * FROM bot_performance_summary"
        result = await self.fetchone(query)
        return result if result else {}
    
    # ==================== MY VIDEOS METHODS ====================
    
    async def add_my_video(self, video_id: str, video_url: str, title: str = None) -> Dict[str, Any]:
        """Add our video for promotion"""
        query = """
        INSERT INTO my_videos (video_id, video_url, title)
        VALUES ($1, $2, $3)
        ON CONFLICT (video_id) DO UPDATE SET
            title = EXCLUDED.title,
            promotion_active = true,
            updated_at = NOW()
        RETURNING *
        """
        
        result = await self.fetchone(query, video_id, video_url, title)
        logger.info(f"✅ Added video for promotion: {title} ({video_id})")
        return result
    
    async def get_active_promotion_video(self) -> Optional[Dict[str, Any]]:
        """Get current video being promoted"""
        query = """
        SELECT * FROM my_videos 
        WHERE promotion_active = true 
        ORDER BY promotion_started_at DESC 
        LIMIT 1
        """
        
        return await self.fetchone(query)
    
    async def get_my_video_by_id(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get our video by ID"""
        query = "SELECT * FROM my_videos WHERE video_id = $1"
        return await self.fetchone(query, video_id)


# ==================== UTILITY FUNCTIONS ====================

def calculate_reliability_score(successful: int, total: int, failed: int) -> int:
    """Calculate reliability score for a contact"""
    base_score = 50
    success_bonus = min(successful * 5, 40)
    failure_penalty = min(failed * 10, 50)
    
    # Success rate bonus
    if total > 0:
        success_rate = successful / total
        if success_rate > 0.8:
            success_bonus += 20
        elif success_rate > 0.6:
            success_bonus += 10
    
    final_score = base_score + success_bonus - failure_penalty
    return max(0, min(100, final_score))


async def initialize_database(database_url: str) -> DatabaseConnection:
    """Initialize database connection"""
    db = DatabaseConnection(database_url)
    await db.connect()
    return db