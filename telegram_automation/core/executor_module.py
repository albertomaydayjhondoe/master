"""
Task Executor Module
Executes engagement tasks across different platforms.
Manages task queues, priorities, and cross-platform coordination.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import uuid
from concurrent.futures import ThreadPoolExecutor
import random

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.telegram_config import TelegramConfig
from database.models import ExchangeTask, TaskExecution, PlatformAccount
from integrations.youtube_client import YouTubeClient
from integrations.instagram_client import InstagramClient
from integrations.tiktok_client import TikTokClient

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

@dataclass
class ExecutionResult:
    """Result of task execution."""
    success: bool
    task_id: str
    platform: str
    action_type: str
    execution_time: timedelta
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    retry_count: int = 0

@dataclass
class TaskMetrics:
    """Metrics for task execution."""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_execution_time: timedelta = timedelta(0)
    success_rate: float = 0.0
    platform_stats: Dict[str, Dict[str, int]] = field(default_factory=dict)

class TaskExecutor:
    """
    Executes engagement tasks across different social media platforms.
    Manages task queues, scheduling, and cross-platform coordination.
    """
    
    def __init__(self, config: TelegramConfig):
        self.config = config
        self.is_running = False
        
        # Task management
        self.task_queue: List[ExchangeTask] = []
        self.active_tasks: Dict[str, ExchangeTask] = {}
        self.completed_tasks: Dict[str, ExecutionResult] = {}
        
        # Platform clients
        self.youtube_client = YouTubeClient(config.youtube_config) if hasattr(config, 'youtube_config') else None
        self.instagram_client = InstagramClient(config.instagram_config) if hasattr(config, 'instagram_config') else None
        self.tiktok_client = TikTokClient(config.tiktok_config) if hasattr(config, 'tiktok_config') else None
        
        # Execution control
        self.max_concurrent_tasks = config.max_concurrent_tasks or 5
        self.execution_semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        self.executor_pool = ThreadPoolExecutor(max_workers=self.max_concurrent_tasks)
        
        # Metrics and monitoring
        self.metrics = TaskMetrics()
        self.execution_callbacks: List[Callable] = []
        
        # Rate limiting
        self.platform_rate_limits = {
            'youtube': {'requests_per_hour': 100, 'current_count': 0, 'reset_time': datetime.now()},
            'instagram': {'requests_per_hour': 200, 'current_count': 0, 'reset_time': datetime.now()},
            'tiktok': {'requests_per_hour': 150, 'current_count': 0, 'reset_time': datetime.now()}
        }
    
    async def initialize(self):
        """Initialize the task executor and platform clients."""
        try:
            logger.info("Initializing task executor...")
            
            # Initialize platform clients
            initialization_tasks = []
            
            if self.youtube_client:
                initialization_tasks.append(self.youtube_client.initialize())
            
            if self.instagram_client:
                initialization_tasks.append(self.instagram_client.initialize())
            
            if self.tiktok_client:
                initialization_tasks.append(self.tiktok_client.initialize())
            
            if initialization_tasks:
                await asyncio.gather(*initialization_tasks, return_exceptions=True)
            
            # Load pending tasks from database
            await self._load_pending_tasks()
            
            logger.info("Task executor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize task executor: {e}")
            raise
    
    async def _load_pending_tasks(self):
        """Load pending tasks from database."""
        try:
            # This would typically load from database
            # For now, initialize empty queue
            self.task_queue = []
            logger.info("Loaded pending tasks from database")
            
        except Exception as e:
            logger.error(f"Failed to load pending tasks: {e}")
    
    async def create_exchange_task(self, user_id: int, session_data: Dict[str, Any]) -> str:
        """Create a new engagement exchange task."""
        try:
            task_id = str(uuid.uuid4())
            
            # Determine task priority based on user metrics and content
            priority = await self._calculate_task_priority(user_id, session_data)
            
            # Create task object
            task = ExchangeTask(
                task_id=task_id,
                user_id=user_id,
                platform=session_data['platform'],
                account_info=session_data['account_info'],
                content_url=session_data['content_url'],
                exchange_type=session_data.get('exchange_type', 'standard'),
                priority=priority,
                status=TaskStatus.PENDING,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=24),
                retry_count=0,
                max_retries=3
            )
            
            # Add to queue
            await self._add_task_to_queue(task)
            
            logger.info(f"Created exchange task {task_id} for user {user_id} on {session_data['platform']}")
            
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to create exchange task: {e}")
            raise
    
    async def _calculate_task_priority(self, user_id: int, session_data: Dict[str, Any]) -> TaskPriority:
        """Calculate task priority based on various factors."""
        
        priority_score = 0
        
        # Platform priority
        platform_scores = {
            'youtube': 3,
            'instagram': 2,
            'tiktok': 2,
            'telegram': 1
        }
        priority_score += platform_scores.get(session_data['platform'], 1)
        
        # User engagement history (would be loaded from database)
        # For now, use random factor
        user_factor = random.uniform(0.5, 2.0)
        priority_score *= user_factor
        
        # Content type analysis
        content_url = session_data.get('content_url', '')
        if 'shorts' in content_url or 'reel' in content_url:
            priority_score += 1  # Short-form content gets boost
        
        # Time-based priority
        hour = datetime.now().hour
        if 18 <= hour <= 22:  # Peak engagement hours
            priority_score += 1
        
        # Convert to priority enum
        if priority_score >= 6:
            return TaskPriority.CRITICAL
        elif priority_score >= 5:
            return TaskPriority.URGENT
        elif priority_score >= 3:
            return TaskPriority.HIGH
        elif priority_score >= 2:
            return TaskPriority.NORMAL
        else:
            return TaskPriority.LOW
    
    async def _add_task_to_queue(self, task: ExchangeTask):
        """Add task to the execution queue with proper ordering."""
        
        # Insert task in priority order
        inserted = False
        for i, queued_task in enumerate(self.task_queue):
            if task.priority.value > queued_task.priority.value:
                self.task_queue.insert(i, task)
                inserted = True
                break
        
        if not inserted:
            self.task_queue.append(task)
        
        logger.info(f"Added task {task.task_id} to queue (priority: {task.priority.name}, position: {self.task_queue.index(task) + 1})")
    
    async def execute_next_task(self) -> Optional[ExecutionResult]:
        """Execute the next task in the queue."""
        
        if not self.task_queue:
            return None
        
        # Check rate limits
        available_task = None
        for task in self.task_queue:
            if await self._check_rate_limit(task.platform):
                available_task = task
                break
        
        if not available_task:
            logger.debug("No tasks available due to rate limits")
            return None
        
        # Remove task from queue and add to active tasks
        self.task_queue.remove(available_task)
        self.active_tasks[available_task.task_id] = available_task
        
        # Execute task
        result = await self._execute_task(available_task)
        
        # Remove from active tasks
        del self.active_tasks[available_task.task_id]
        
        # Store result
        self.completed_tasks[available_task.task_id] = result
        
        # Update metrics
        await self._update_metrics(result)
        
        # Notify callbacks
        for callback in self.execution_callbacks:
            try:
                await callback(result)
            except Exception as e:
                logger.error(f"Error in execution callback: {e}")
        
        return result
    
    async def _check_rate_limit(self, platform: str) -> bool:
        """Check if platform is within rate limits."""
        
        if platform not in self.platform_rate_limits:
            return True
        
        rate_limit = self.platform_rate_limits[platform]
        now = datetime.now()
        
        # Reset counter if hour has passed
        if now - rate_limit['reset_time'] >= timedelta(hours=1):
            rate_limit['current_count'] = 0
            rate_limit['reset_time'] = now
        
        # Check if within limit
        return rate_limit['current_count'] < rate_limit['requests_per_hour']
    
    async def _execute_task(self, task: ExchangeTask) -> ExecutionResult:
        """Execute a single task."""
        
        async with self.execution_semaphore:
            start_time = datetime.now()
            
            try:
                logger.info(f"Executing task {task.task_id} on {task.platform}")
                
                # Update task status
                task.status = TaskStatus.IN_PROGRESS
                
                # Route to appropriate platform executor
                if task.platform == 'youtube':
                    result = await self._execute_youtube_task(task)
                elif task.platform == 'instagram':
                    result = await self._execute_instagram_task(task)
                elif task.platform == 'tiktok':
                    result = await self._execute_tiktok_task(task)
                else:
                    raise ValueError(f"Unsupported platform: {task.platform}")
                
                # Update rate limit counter
                if task.platform in self.platform_rate_limits:
                    self.platform_rate_limits[task.platform]['current_count'] += 1
                
                execution_time = datetime.now() - start_time
                
                if result['success']:
                    task.status = TaskStatus.COMPLETED
                    logger.info(f"Task {task.task_id} completed successfully in {execution_time}")
                else:
                    task.status = TaskStatus.FAILED
                    logger.warning(f"Task {task.task_id} failed: {result.get('error', 'Unknown error')}")
                
                return ExecutionResult(
                    success=result['success'],
                    task_id=task.task_id,
                    platform=task.platform,
                    action_type=result.get('action_type', 'engagement'),
                    execution_time=execution_time,
                    details=result.get('details', {}),
                    error_message=result.get('error'),
                    retry_count=task.retry_count
                )
                
            except Exception as e:
                execution_time = datetime.now() - start_time
                task.status = TaskStatus.FAILED
                task.retry_count += 1
                
                logger.error(f"Task {task.task_id} execution failed: {e}")
                
                # Retry logic
                if task.retry_count < task.max_retries:
                    # Add back to queue with delay
                    await asyncio.sleep(60 * task.retry_count)  # Exponential backoff
                    task.status = TaskStatus.PENDING
                    await self._add_task_to_queue(task)
                    logger.info(f"Task {task.task_id} re-queued for retry ({task.retry_count}/{task.max_retries})")
                
                return ExecutionResult(
                    success=False,
                    task_id=task.task_id,
                    platform=task.platform,
                    action_type='engagement',
                    execution_time=execution_time,
                    error_message=str(e),
                    retry_count=task.retry_count
                )
    
    async def _execute_youtube_task(self, task: ExchangeTask) -> Dict[str, Any]:
        """Execute YouTube-specific engagement task."""
        try:
            if not self.youtube_client:
                return {'success': False, 'error': 'YouTube client not initialized'}
            
            # Parse content URL to extract video ID
            video_id = await self._extract_youtube_video_id(task.content_url)
            if not video_id:
                return {'success': False, 'error': 'Invalid YouTube URL'}
            
            # Perform engagement actions
            actions_performed = []
            
            # Like the video
            like_result = await self.youtube_client.like_video(video_id)
            if like_result:
                actions_performed.append('like')
            
            # Subscribe to channel (if not already subscribed)
            channel_id = await self.youtube_client.get_video_channel_id(video_id)
            if channel_id:
                subscribe_result = await self.youtube_client.subscribe_to_channel(channel_id)
                if subscribe_result:
                    actions_performed.append('subscribe')
            
            # Add comment (if enabled and has comment templates)
            if self.config.enable_comments:
                comment_result = await self.youtube_client.add_comment(
                    video_id, 
                    await self._generate_engagement_comment(task.platform)
                )
                if comment_result:
                    actions_performed.append('comment')
            
            return {
                'success': len(actions_performed) > 0,
                'action_type': 'youtube_engagement',
                'details': {
                    'video_id': video_id,
                    'actions_performed': actions_performed,
                    'total_actions': len(actions_performed)
                }
            }
            
        except Exception as e:
            logger.error(f"YouTube task execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_instagram_task(self, task: ExchangeTask) -> Dict[str, Any]:
        """Execute Instagram-specific engagement task."""
        try:
            if not self.instagram_client:
                return {'success': False, 'error': 'Instagram client not initialized'}
            
            # Parse content URL to extract post ID
            post_id = await self._extract_instagram_post_id(task.content_url)
            if not post_id:
                return {'success': False, 'error': 'Invalid Instagram URL'}
            
            actions_performed = []
            
            # Like the post
            like_result = await self.instagram_client.like_post(post_id)
            if like_result:
                actions_performed.append('like')
            
            # Follow account
            account_username = await self.instagram_client.get_post_author(post_id)
            if account_username:
                follow_result = await self.instagram_client.follow_user(account_username)
                if follow_result:
                    actions_performed.append('follow')
            
            # Add comment
            if self.config.enable_comments:
                comment_result = await self.instagram_client.add_comment(
                    post_id,
                    await self._generate_engagement_comment(task.platform)
                )
                if comment_result:
                    actions_performed.append('comment')
            
            return {
                'success': len(actions_performed) > 0,
                'action_type': 'instagram_engagement',
                'details': {
                    'post_id': post_id,
                    'actions_performed': actions_performed,
                    'total_actions': len(actions_performed)
                }
            }
            
        except Exception as e:
            logger.error(f"Instagram task execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_tiktok_task(self, task: ExchangeTask) -> Dict[str, Any]:
        """Execute TikTok-specific engagement task."""
        try:
            if not self.tiktok_client:
                return {'success': False, 'error': 'TikTok client not initialized'}
            
            # Parse content URL to extract video ID
            video_id = await self._extract_tiktok_video_id(task.content_url)
            if not video_id:
                return {'success': False, 'error': 'Invalid TikTok URL'}
            
            actions_performed = []
            
            # Like the video
            like_result = await self.tiktok_client.like_video(video_id)
            if like_result:
                actions_performed.append('like')
            
            # Follow user
            username = await self.tiktok_client.get_video_author(video_id)
            if username:
                follow_result = await self.tiktok_client.follow_user(username)
                if follow_result:
                    actions_performed.append('follow')
            
            # Add comment
            if self.config.enable_comments:
                comment_result = await self.tiktok_client.add_comment(
                    video_id,
                    await self._generate_engagement_comment(task.platform)
                )
                if comment_result:
                    actions_performed.append('comment')
            
            return {
                'success': len(actions_performed) > 0,
                'action_type': 'tiktok_engagement',
                'details': {
                    'video_id': video_id,
                    'actions_performed': actions_performed,
                    'total_actions': len(actions_performed)
                }
            }
            
        except Exception as e:
            logger.error(f"TikTok task execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _extract_youtube_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL."""
        import re
        
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)',
            r'youtube\.com\/embed\/([a-zA-Z0-9_-]+)',
            r'youtube\.com\/v\/([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    async def _extract_instagram_post_id(self, url: str) -> Optional[str]:
        """Extract Instagram post ID from URL."""
        import re
        
        pattern = r'instagram\.com\/p\/([a-zA-Z0-9_-]+)'
        match = re.search(pattern, url)
        
        return match.group(1) if match else None
    
    async def _extract_tiktok_video_id(self, url: str) -> Optional[str]:
        """Extract TikTok video ID from URL."""
        import re
        
        pattern = r'tiktok\.com\/@[\w\.-]+\/video\/(\d+)'
        match = re.search(pattern, url)
        
        return match.group(1) if match else None
    
    async def _generate_engagement_comment(self, platform: str) -> str:
        """Generate an appropriate engagement comment for the platform."""
        
        comments = {
            'youtube': [
                "¡Excelente contenido! 👍",
                "Me encanta este video 🔥",
                "¡Sigue así! 💪",
                "Genial, nuevo suscriptor aquí 🚀",
                "¡Increíble trabajo! ⭐"
            ],
            'instagram': [
                "¡Increíble! 😍",
                "Me encanta ❤️",
                "¡Qué genial! 🔥",
                "¡Hermoso! ✨",
                "¡Amazing! 👏"
            ],
            'tiktok': [
                "🔥🔥🔥",
                "Me encanta! ❤️",
                "¡Genial! 👏",
                "🚀✨",
                "¡Increíble! 😍"
            ]
        }
        
        platform_comments = comments.get(platform, comments['youtube'])
        return random.choice(platform_comments)
    
    async def _update_metrics(self, result: ExecutionResult):
        """Update execution metrics."""
        
        self.metrics.total_tasks += 1
        
        if result.success:
            self.metrics.completed_tasks += 1
        else:
            self.metrics.failed_tasks += 1
        
        # Update success rate
        self.metrics.success_rate = (
            self.metrics.completed_tasks / self.metrics.total_tasks * 100
            if self.metrics.total_tasks > 0 else 0
        )
        
        # Update average execution time
        if self.metrics.completed_tasks > 0:
            total_time = (
                self.metrics.average_execution_time * (self.metrics.completed_tasks - 1) +
                result.execution_time
            )
            self.metrics.average_execution_time = total_time / self.metrics.completed_tasks
        else:
            self.metrics.average_execution_time = result.execution_time
        
        # Update platform stats
        platform = result.platform
        if platform not in self.metrics.platform_stats:
            self.metrics.platform_stats[platform] = {
                'total': 0, 'completed': 0, 'failed': 0
            }
        
        self.metrics.platform_stats[platform]['total'] += 1
        if result.success:
            self.metrics.platform_stats[platform]['completed'] += 1
        else:
            self.metrics.platform_stats[platform]['failed'] += 1
    
    async def get_active_tasks_count(self) -> int:
        """Get number of currently active tasks."""
        return len(self.active_tasks)
    
    async def get_queue_length(self) -> int:
        """Get current queue length."""
        return len(self.task_queue)
    
    async def get_user_queue_info(self, user_id: int) -> Dict[str, Any]:
        """Get queue information for a specific user."""
        user_tasks = [task for task in self.task_queue if task.user_id == user_id]
        user_active = [task for task in self.active_tasks.values() if task.user_id == user_id]
        
        return {
            'queued_tasks': len(user_tasks),
            'active_tasks': len(user_active),
            'queue_position': next(
                (i + 1 for i, task in enumerate(self.task_queue) if task.user_id == user_id),
                None
            ),
            'estimated_wait_time': await self._estimate_wait_time(user_tasks[0] if user_tasks else None)
        }
    
    async def estimate_completion_time(self, priority_score: float) -> str:
        """Estimate task completion time based on priority and queue."""
        
        # Calculate position in queue based on priority
        higher_priority_tasks = sum(
            1 for task in self.task_queue 
            if task.priority.value > priority_score
        )
        
        # Estimate based on average execution time and queue position
        avg_time_minutes = self.metrics.average_execution_time.total_seconds() / 60
        estimated_minutes = (higher_priority_tasks + 1) * avg_time_minutes
        
        if estimated_minutes < 60:
            return f"{int(estimated_minutes)} minutos"
        else:
            hours = int(estimated_minutes // 60)
            minutes = int(estimated_minutes % 60)
            return f"{hours}h {minutes}m"
    
    async def _estimate_wait_time(self, task: Optional[ExchangeTask]) -> Optional[str]:
        """Estimate wait time for a specific task."""
        if not task:
            return None
        
        position = self.task_queue.index(task) + 1
        avg_time_minutes = self.metrics.average_execution_time.total_seconds() / 60
        estimated_minutes = position * avg_time_minutes
        
        if estimated_minutes < 60:
            return f"{int(estimated_minutes)} minutos"
        else:
            hours = int(estimated_minutes // 60)
            minutes = int(estimated_minutes % 60)
            return f"{hours}h {minutes}m"
    
    def register_execution_callback(self, callback: Callable[[ExecutionResult], None]):
        """Register a callback for task execution results."""
        self.execution_callbacks.append(callback)
    
    async def cancel_task(self, task_id: str, user_id: int) -> bool:
        """Cancel a task if it belongs to the user and is not in progress."""
        
        # Check if task is in queue
        for task in self.task_queue:
            if task.task_id == task_id and task.user_id == user_id:
                self.task_queue.remove(task)
                task.status = TaskStatus.CANCELLED
                logger.info(f"Task {task_id} cancelled by user {user_id}")
                return True
        
        # Cannot cancel active tasks
        if task_id in self.active_tasks:
            logger.warning(f"Cannot cancel active task {task_id}")
            return False
        
        return False
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        
        # Check active tasks
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                'task_id': task_id,
                'status': task.status.value,
                'progress': 'in_progress',
                'created_at': task.created_at.isoformat(),
                'platform': task.platform
            }
        
        # Check queue
        for task in self.task_queue:
            if task.task_id == task_id:
                position = self.task_queue.index(task) + 1
                return {
                    'task_id': task_id,
                    'status': task.status.value,
                    'queue_position': position,
                    'estimated_wait': await self._estimate_wait_time(task),
                    'created_at': task.created_at.isoformat(),
                    'platform': task.platform
                }
        
        # Check completed tasks
        if task_id in self.completed_tasks:
            result = self.completed_tasks[task_id]
            return {
                'task_id': task_id,
                'status': 'completed' if result.success else 'failed',
                'execution_time': str(result.execution_time),
                'platform': result.platform,
                'success': result.success,
                'error': result.error_message
            }
        
        return None
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get execution metrics."""
        return {
            'total_tasks': self.metrics.total_tasks,
            'completed_tasks': self.metrics.completed_tasks,
            'failed_tasks': self.metrics.failed_tasks,
            'success_rate': round(self.metrics.success_rate, 2),
            'average_execution_time': str(self.metrics.average_execution_time),
            'platform_stats': self.metrics.platform_stats,
            'current_queue_length': len(self.task_queue),
            'active_tasks': len(self.active_tasks)
        }
    
    async def start(self):
        """Start the task executor."""
        self.is_running = True
        
        # Start background task processing
        asyncio.create_task(self._process_queue())
        
        logger.info("Task executor started")
    
    async def stop(self):
        """Stop the task executor."""
        self.is_running = False
        
        # Wait for active tasks to complete
        while self.active_tasks:
            await asyncio.sleep(1)
        
        # Shutdown executor pool
        self.executor_pool.shutdown(wait=True)
        
        logger.info("Task executor stopped")
    
    async def _process_queue(self):
        """Background task to continuously process the queue."""
        while self.is_running:
            try:
                if self.task_queue and len(self.active_tasks) < self.max_concurrent_tasks:
                    await self.execute_next_task()
                else:
                    await asyncio.sleep(5)  # Wait before checking again
                    
            except Exception as e:
                logger.error(f"Error in queue processing: {e}")
                await asyncio.sleep(10)  # Wait longer on error