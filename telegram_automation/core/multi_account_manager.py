"""
Multi-Account Manager Module
Manages multiple social media accounts for automated engagement.
Handles account rotation, health monitoring, and authentication.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import random
from concurrent.futures import ThreadPoolExecutor

from ..config.telegram_config import TelegramConfig
from ..database.models import AccountCredentials, AccountMetrics, AccountHealth
from ..integrations.youtube_client import YouTubeClient
from ..integrations.instagram_client import InstagramClient
from ..integrations.tiktok_client import TikTokClient

logger = logging.getLogger(__name__)

class AccountStatus(Enum):
    """Account status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    AUTHENTICATING = "authenticating"
    MAINTENANCE = "maintenance"

class PlatformType(Enum):
    """Supported platform types."""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"

@dataclass
class AccountInfo:
    """Account information container."""
    account_id: str
    platform: PlatformType
    username: str
    user_id: int  # Telegram user who owns this account
    status: AccountStatus = AccountStatus.INACTIVE
    
    # Authentication details
    credentials: Optional[Dict[str, Any]] = None
    last_auth: Optional[datetime] = None
    auth_expires: Optional[datetime] = None
    
    # Usage metrics
    daily_actions: int = 0
    monthly_actions: int = 0
    total_actions: int = 0
    success_rate: float = 0.0
    
    # Health monitoring
    last_health_check: Optional[datetime] = None
    health_score: float = 100.0
    consecutive_failures: int = 0
    
    # Rate limiting
    rate_limit_reset: Optional[datetime] = None
    remaining_requests: int = 100
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class AccountPool:
    """Pool of accounts for a specific platform."""
    platform: PlatformType
    accounts: List[AccountInfo] = field(default_factory=list)
    active_accounts: int = 0
    rotation_index: int = 0
    last_rotation: datetime = field(default_factory=datetime.now)

class MultiAccountManager:
    """
    Manages multiple social media accounts for automated engagement.
    Handles account rotation, health monitoring, and load balancing.
    """
    
    def __init__(self, config: TelegramConfig):
        self.config = config
        self.is_running = False
        
        # Account pools by platform
        self.account_pools: Dict[PlatformType, AccountPool] = {
            PlatformType.YOUTUBE: AccountPool(PlatformType.YOUTUBE),
            PlatformType.INSTAGRAM: AccountPool(PlatformType.INSTAGRAM),
            PlatformType.TIKTOK: AccountPool(PlatformType.TIKTOK)
        }
        
        # User account mapping
        self.user_accounts: Dict[int, List[AccountInfo]] = {}
        
        # Platform clients
        self.platform_clients: Dict[PlatformType, Dict[str, Any]] = {
            PlatformType.YOUTUBE: {},
            PlatformType.INSTAGRAM: {},
            PlatformType.TIKTOK: {}
        }
        
        # Health monitoring
        self.health_check_interval = timedelta(minutes=30)
        self.last_global_health_check = datetime.now()
        
        # Security and encryption
        self.encryption_key = config.account_encryption_key if hasattr(config, 'account_encryption_key') else 'default_key'
        
        # Performance metrics
        self.account_metrics = {
            'total_accounts': 0,
            'active_accounts': 0,
            'healthy_accounts': 0,
            'daily_actions_performed': 0,
            'success_rate_average': 0.0
        }
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
    
    async def initialize(self):
        """Initialize the multi-account manager."""
        try:
            logger.info("Initializing multi-account manager...")
            
            # Load accounts from database
            await self._load_accounts_from_database()
            
            # Initialize platform clients
            await self._initialize_platform_clients()
            
            # Start health monitoring
            await self._start_health_monitoring()
            
            # Start background tasks
            self._start_background_tasks()
            
            logger.info(f"Multi-account manager initialized with {self.account_metrics['total_accounts']} accounts")
            
        except Exception as e:
            logger.error(f"Failed to initialize multi-account manager: {e}")
            raise
    
    async def _load_accounts_from_database(self):
        """Load account configurations from database."""
        try:
            # This would typically load from encrypted database
            # For now, initialize with empty pools
            
            for platform_type in PlatformType:
                self.account_pools[platform_type] = AccountPool(platform_type)
            
            await self._update_account_metrics()
            logger.info("Loaded accounts from database")
            
        except Exception as e:
            logger.error(f"Failed to load accounts: {e}")
    
    async def _initialize_platform_clients(self):
        """Initialize clients for each platform and account."""
        try:
            for platform_type, pool in self.account_pools.items():
                for account in pool.accounts:
                    await self._create_platform_client(account)
            
            logger.info("Platform clients initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize platform clients: {e}")
    
    async def _create_platform_client(self, account: AccountInfo) -> bool:
        """Create a platform-specific client for an account."""
        try:
            client = None
            
            if account.platform == PlatformType.YOUTUBE:
                client = YouTubeClient(account.credentials)
            elif account.platform == PlatformType.INSTAGRAM:
                client = InstagramClient(account.credentials)
            elif account.platform == PlatformType.TIKTOK:
                client = TikTokClient(account.credentials)
            
            if client:
                await client.initialize()
                self.platform_clients[account.platform][account.account_id] = client
                account.status = AccountStatus.ACTIVE
                return True
            
        except Exception as e:
            logger.error(f"Failed to create client for account {account.account_id}: {e}")
            account.status = AccountStatus.ERROR
            account.consecutive_failures += 1
        
        return False
    
    async def add_user_account(self, user_id: int, platform: str, username: str, 
                             credentials: Dict[str, Any]) -> Tuple[bool, str]:
        """Add a new account for a user."""
        try:
            platform_type = PlatformType(platform.lower())
            
            # Generate unique account ID
            account_id = self._generate_account_id(user_id, platform, username)
            
            # Check if account already exists
            if await self._account_exists(account_id):
                return False, "Account already exists"
            
            # Encrypt credentials
            encrypted_credentials = await self._encrypt_credentials(credentials)
            
            # Create account info
            account = AccountInfo(
                account_id=account_id,
                platform=platform_type,
                username=username,
                user_id=user_id,
                credentials=encrypted_credentials,
                status=AccountStatus.AUTHENTICATING
            )
            
            # Test authentication
            auth_success = await self._test_account_authentication(account)
            
            if not auth_success:
                return False, "Authentication failed"
            
            # Add to pools
            self.account_pools[platform_type].accounts.append(account)
            
            # Add to user mapping
            if user_id not in self.user_accounts:
                self.user_accounts[user_id] = []
            self.user_accounts[user_id].append(account)
            
            # Create platform client
            await self._create_platform_client(account)
            
            # Update metrics
            await self._update_account_metrics()
            
            # Save to database
            await self._save_account_to_database(account)
            
            logger.info(f"Added account {account_id} for user {user_id}")
            return True, "Account added successfully"
            
        except ValueError:
            return False, f"Unsupported platform: {platform}"
        except Exception as e:
            logger.error(f"Failed to add account: {e}")
            return False, f"Error adding account: {str(e)}"
    
    def _generate_account_id(self, user_id: int, platform: str, username: str) -> str:
        """Generate unique account ID."""
        data = f"{user_id}:{platform}:{username}:{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    async def _account_exists(self, account_id: str) -> bool:
        """Check if account ID already exists."""
        for pool in self.account_pools.values():
            for account in pool.accounts:
                if account.account_id == account_id:
                    return True
        return False
    
    async def _encrypt_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt account credentials for secure storage."""
        # In production, use proper encryption like Fernet
        # For now, return as-is (would implement proper encryption)
        return credentials
    
    async def _decrypt_credentials(self, encrypted_credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt account credentials."""
        # In production, decrypt using proper method
        return encrypted_credentials
    
    async def _test_account_authentication(self, account: AccountInfo) -> bool:
        """Test if account credentials are valid."""
        try:
            # Create temporary client to test auth
            decrypted_creds = await self._decrypt_credentials(account.credentials)
            
            if account.platform == PlatformType.YOUTUBE:
                test_client = YouTubeClient(decrypted_creds)
            elif account.platform == PlatformType.INSTAGRAM:
                test_client = InstagramClient(decrypted_creds)
            elif account.platform == PlatformType.TIKTOK:
                test_client = TikTokClient(decrypted_creds)
            else:
                return False
            
            # Test authentication
            auth_result = await test_client.test_authentication()
            
            if auth_result:
                account.status = AccountStatus.ACTIVE
                account.last_auth = datetime.now()
                account.auth_expires = datetime.now() + timedelta(days=30)  # Platform-specific
                account.health_score = 100.0
                account.consecutive_failures = 0
                return True
            
        except Exception as e:
            logger.error(f"Authentication test failed for {account.account_id}: {e}")
            account.status = AccountStatus.ERROR
            account.consecutive_failures += 1
        
        return False
    
    async def get_available_account(self, platform: str, exclude_accounts: Optional[List[str]] = None) -> Optional[AccountInfo]:
        """Get an available account for a platform with load balancing."""
        try:
            platform_type = PlatformType(platform.lower())
            pool = self.account_pools[platform_type]
            
            if not pool.accounts:
                return None
            
            exclude_accounts = exclude_accounts or []
            
            # Filter available accounts
            available_accounts = [
                account for account in pool.accounts
                if (account.status == AccountStatus.ACTIVE and
                    account.account_id not in exclude_accounts and
                    account.remaining_requests > 0 and
                    (account.rate_limit_reset is None or account.rate_limit_reset < datetime.now()))
            ]
            
            if not available_accounts:
                return None
            
            # Select account using round-robin with health weighting
            best_account = await self._select_optimal_account(available_accounts)
            
            # Update rotation index
            pool.rotation_index = (pool.rotation_index + 1) % len(available_accounts)
            pool.last_rotation = datetime.now()
            
            return best_account
            
        except ValueError:
            logger.error(f"Invalid platform: {platform}")
            return None
        except Exception as e:
            logger.error(f"Error getting available account: {e}")
            return None
    
    async def _select_optimal_account(self, available_accounts: List[AccountInfo]) -> AccountInfo:
        """Select optimal account based on health, usage, and rotation."""
        
        # Calculate scores for each account
        scored_accounts = []
        
        for account in available_accounts:
            score = 0.0
            
            # Health score (0-100)
            score += account.health_score * 0.4
            
            # Usage balance (prefer less used accounts)
            max_daily = max(acc.daily_actions for acc in available_accounts) or 1
            usage_factor = 1.0 - (account.daily_actions / max_daily)
            score += usage_factor * 30
            
            # Success rate
            score += account.success_rate * 0.2
            
            # Rate limit availability
            rate_limit_factor = account.remaining_requests / 100
            score += rate_limit_factor * 10
            
            scored_accounts.append((account, score))
        
        # Sort by score and add some randomness
        scored_accounts.sort(key=lambda x: x[1], reverse=True)
        
        # Select from top 3 to add randomness
        top_accounts = scored_accounts[:3]
        selected_account = random.choice(top_accounts)[0]
        
        return selected_account
    
    async def update_account_usage(self, account_id: str, success: bool, actions_count: int = 1):
        """Update account usage statistics after task execution."""
        
        account = await self._find_account_by_id(account_id)
        if not account:
            return
        
        # Update action counts
        account.daily_actions += actions_count
        account.monthly_actions += actions_count
        account.total_actions += actions_count
        
        # Update success rate
        if success:
            account.success_rate = (account.success_rate * 0.9) + (1.0 * 0.1)  # Moving average
            account.consecutive_failures = 0
            account.health_score = min(account.health_score + 1, 100.0)
        else:
            account.success_rate = (account.success_rate * 0.9) + (0.0 * 0.1)
            account.consecutive_failures += 1
            account.health_score = max(account.health_score - 5, 0.0)
        
        # Update rate limiting
        account.remaining_requests = max(account.remaining_requests - actions_count, 0)
        
        # Check for suspension or rate limiting
        if account.consecutive_failures >= 5:
            account.status = AccountStatus.SUSPENDED
            logger.warning(f"Account {account_id} suspended due to consecutive failures")
        elif account.remaining_requests <= 0:
            account.status = AccountStatus.RATE_LIMITED
            account.rate_limit_reset = datetime.now() + timedelta(hours=1)
        
        account.updated_at = datetime.now()
        
        # Update global metrics
        await self._update_account_metrics()
    
    async def _find_account_by_id(self, account_id: str) -> Optional[AccountInfo]:
        """Find account by ID across all pools."""
        for pool in self.account_pools.values():
            for account in pool.accounts:
                if account.account_id == account_id:
                    return account
        return None
    
    async def get_user_accounts(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all accounts for a specific user."""
        
        user_accounts = self.user_accounts.get(user_id, [])
        
        return [
            {
                'account_id': account.account_id,
                'platform': account.platform.value,
                'username': account.username,
                'status': account.status.value,
                'health_score': account.health_score,
                'daily_actions': account.daily_actions,
                'success_rate': round(account.success_rate * 100, 1),
                'created_at': account.created_at.isoformat()
            }
            for account in user_accounts
        ]
    
    async def remove_user_account(self, user_id: int, account_id: str) -> Tuple[bool, str]:
        """Remove an account for a user."""
        try:
            account = await self._find_account_by_id(account_id)
            
            if not account:
                return False, "Account not found"
            
            if account.user_id != user_id:
                return False, "Account does not belong to user"
            
            # Remove from pools
            for pool in self.account_pools.values():
                pool.accounts = [acc for acc in pool.accounts if acc.account_id != account_id]
            
            # Remove from user mapping
            if user_id in self.user_accounts:
                self.user_accounts[user_id] = [
                    acc for acc in self.user_accounts[user_id] 
                    if acc.account_id != account_id
                ]
            
            # Remove platform client
            if account.platform in self.platform_clients:
                self.platform_clients[account.platform].pop(account_id, None)
            
            # Remove from database
            await self._remove_account_from_database(account_id)
            
            # Update metrics
            await self._update_account_metrics()
            
            logger.info(f"Removed account {account_id} for user {user_id}")
            return True, "Account removed successfully"
            
        except Exception as e:
            logger.error(f"Failed to remove account: {e}")
            return False, f"Error removing account: {str(e)}"
    
    async def _start_health_monitoring(self):
        """Start health monitoring for all accounts."""
        
        async def health_monitor():
            while self.is_running:
                try:
                    await self._perform_health_checks()
                    await asyncio.sleep(self.health_check_interval.total_seconds())
                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")
                    await asyncio.sleep(60)
        
        task = asyncio.create_task(health_monitor())
        self.background_tasks.append(task)
    
    async def _perform_health_checks(self):
        """Perform health checks on all accounts."""
        
        logger.info("Performing account health checks...")
        
        total_checked = 0
        healthy_count = 0
        
        for pool in self.account_pools.values():
            for account in pool.accounts:
                try:
                    # Check authentication status
                    if account.auth_expires and account.auth_expires < datetime.now():
                        await self._refresh_account_authentication(account)
                    
                    # Reset rate limits if expired
                    if (account.rate_limit_reset and 
                        account.rate_limit_reset < datetime.now() and
                        account.status == AccountStatus.RATE_LIMITED):
                        
                        account.status = AccountStatus.ACTIVE
                        account.remaining_requests = 100  # Reset to platform default
                        account.rate_limit_reset = None
                    
                    # Update health score based on recent performance
                    await self._update_account_health_score(account)
                    
                    # Check if account should be reactivated
                    if (account.status == AccountStatus.SUSPENDED and 
                        account.consecutive_failures < 3):
                        account.status = AccountStatus.ACTIVE
                        logger.info(f"Reactivated account {account.account_id}")
                    
                    account.last_health_check = datetime.now()
                    total_checked += 1
                    
                    if account.health_score > 70:
                        healthy_count += 1
                    
                except Exception as e:
                    logger.error(f"Health check failed for account {account.account_id}: {e}")
                    account.health_score = max(account.health_score - 10, 0)
        
        # Update global metrics
        self.account_metrics['healthy_accounts'] = healthy_count
        self.last_global_health_check = datetime.now()
        
        logger.info(f"Health check completed: {healthy_count}/{total_checked} accounts healthy")
    
    async def _refresh_account_authentication(self, account: AccountInfo):
        """Refresh account authentication."""
        try:
            logger.info(f"Refreshing authentication for account {account.account_id}")
            
            # Test current authentication
            auth_success = await self._test_account_authentication(account)
            
            if auth_success:
                account.last_auth = datetime.now()
                account.auth_expires = datetime.now() + timedelta(days=30)
                account.status = AccountStatus.ACTIVE
            else:
                account.status = AccountStatus.ERROR
                logger.warning(f"Authentication refresh failed for account {account.account_id}")
                
        except Exception as e:
            logger.error(f"Failed to refresh authentication for {account.account_id}: {e}")
            account.status = AccountStatus.ERROR
    
    async def _update_account_health_score(self, account: AccountInfo):
        """Update account health score based on various factors."""
        
        # Base score from success rate
        base_score = account.success_rate * 70
        
        # Recent activity bonus
        if account.daily_actions > 0:
            base_score += 10
        
        # Consecutive failures penalty
        failure_penalty = account.consecutive_failures * 5
        base_score -= failure_penalty
        
        # Authentication status
        if account.status == AccountStatus.ACTIVE:
            base_score += 10
        elif account.status in [AccountStatus.SUSPENDED, AccountStatus.ERROR]:
            base_score -= 20
        
        # Rate limit status
        if account.status == AccountStatus.RATE_LIMITED:
            base_score -= 10
        
        # Clamp between 0 and 100
        account.health_score = max(0, min(100, base_score))
    
    def _start_background_tasks(self):
        """Start background maintenance tasks."""
        
        # Daily reset task
        async def daily_reset():
            while self.is_running:
                try:
                    # Wait until midnight
                    now = datetime.now()
                    tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                    wait_seconds = (tomorrow - now).total_seconds()
                    await asyncio.sleep(wait_seconds)
                    
                    # Reset daily counters
                    for pool in self.account_pools.values():
                        for account in pool.accounts:
                            account.daily_actions = 0
                    
                    logger.info("Daily account counters reset")
                    
                except Exception as e:
                    logger.error(f"Daily reset error: {e}")
                    await asyncio.sleep(3600)  # Retry in 1 hour
        
        # Metrics update task
        async def metrics_updater():
            while self.is_running:
                try:
                    await self._update_account_metrics()
                    await asyncio.sleep(300)  # Update every 5 minutes
                except Exception as e:
                    logger.error(f"Metrics update error: {e}")
                    await asyncio.sleep(300)
        
        self.background_tasks.extend([
            asyncio.create_task(daily_reset()),
            asyncio.create_task(metrics_updater())
        ])
    
    async def _update_account_metrics(self):
        """Update global account metrics."""
        
        total_accounts = 0
        active_accounts = 0
        healthy_accounts = 0
        total_success_rate = 0.0
        daily_actions = 0
        
        for pool in self.account_pools.values():
            for account in pool.accounts:
                total_accounts += 1
                
                if account.status == AccountStatus.ACTIVE:
                    active_accounts += 1
                
                if account.health_score > 70:
                    healthy_accounts += 1
                
                total_success_rate += account.success_rate
                daily_actions += account.daily_actions
        
        self.account_metrics = {
            'total_accounts': total_accounts,
            'active_accounts': active_accounts,
            'healthy_accounts': healthy_accounts,
            'daily_actions_performed': daily_actions,
            'success_rate_average': (total_success_rate / max(total_accounts, 1)) * 100
        }
    
    async def get_account_statistics(self) -> Dict[str, Any]:
        """Get comprehensive account statistics."""
        
        platform_stats = {}
        
        for platform_type, pool in self.account_pools.items():
            platform_name = platform_type.value
            
            active_count = sum(1 for acc in pool.accounts if acc.status == AccountStatus.ACTIVE)
            avg_health = sum(acc.health_score for acc in pool.accounts) / max(len(pool.accounts), 1)
            total_actions = sum(acc.daily_actions for acc in pool.accounts)
            
            platform_stats[platform_name] = {
                'total_accounts': len(pool.accounts),
                'active_accounts': active_count,
                'average_health': round(avg_health, 1),
                'daily_actions': total_actions
            }
        
        return {
            'global_metrics': self.account_metrics,
            'platform_breakdown': platform_stats,
            'last_health_check': self.last_global_health_check.isoformat(),
            'health_status': 'good' if self.account_metrics['healthy_accounts'] > 0 else 'poor'
        }
    
    async def _save_account_to_database(self, account: AccountInfo):
        """Save account to database."""
        # This would implement database storage
        pass
    
    async def _remove_account_from_database(self, account_id: str):
        """Remove account from database."""
        # This would implement database removal
        pass
    
    async def start(self):
        """Start the multi-account manager."""
        self.is_running = True
        
        logger.info("Multi-account manager started")
    
    async def stop(self):
        """Stop the multi-account manager."""
        self.is_running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Close platform clients
        for platform_clients in self.platform_clients.values():
            for client in platform_clients.values():
                try:
                    await client.close()
                except:
                    pass
        
        logger.info("Multi-account manager stopped")