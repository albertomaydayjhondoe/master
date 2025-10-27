"""
Device Farm v5 - Task Queue System
Manages and distributes automation tasks across devices
"""
import asyncio
import json
import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from loguru import logger
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base

from ..config_manager import get_config
from ..core.models import Base, get_db_session


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class TaskDefinition:
    """Task definition structure"""
    task_id: str
    task_type: str
    priority: TaskPriority
    device_requirements: Dict[str, Any]  # OS version, capabilities, etc.
    parameters: Dict[str, Any]
    timeout_seconds: int
    max_retries: int
    created_at: datetime
    scheduled_for: Optional[datetime] = None
    callback_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['priority'] = self.priority.value
        data['created_at'] = self.created_at.isoformat()
        if self.scheduled_for:
            data['scheduled_for'] = self.scheduled_for.isoformat()
        return data


@dataclass
class TaskExecution:
    """Task execution tracking"""
    task_id: str
    device_serial: str
    status: TaskStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        if self.started_at:
            data['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        return data


class Task(Base):
    """Database model for tasks"""
    __tablename__ = 'tasks'
    
    id = Column(String, primary_key=True)
    task_type = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    device_serial = Column(String, nullable=True)
    parameters = Column(Text, nullable=False)  # JSON
    device_requirements = Column(Text, nullable=True)  # JSON
    timeout_seconds = Column(Integer, default=300)
    max_retries = Column(Integer, default=3)
    retry_count = Column(Integer, default=0)
    result = Column(Text, nullable=True)  # JSON
    error_message = Column(Text, nullable=True)
    callback_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    scheduled_for = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class TaskQueue:
    """Manages task queuing and distribution"""
    
    def __init__(self):
        self.config = get_config()
        
        # In-memory queues by priority
        self._queues: Dict[TaskPriority, asyncio.Queue] = {
            priority: asyncio.Queue() for priority in TaskPriority
        }
        
        # Active executions
        self._active_executions: Dict[str, TaskExecution] = {}
        
        # Device availability tracking
        self._device_availability: Dict[str, bool] = {}
        
        # Task handlers registry
        self._task_handlers: Dict[str, Callable] = {}
        
        # Background tasks
        self._queue_processor_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        logger.info("TaskQueue initialized")
    
    async def initialize(self) -> bool:
        """Initialize task queue system"""
        try:
            # Load pending tasks from database
            await self._load_pending_tasks()
            
            # Start background processors
            self._queue_processor_task = asyncio.create_task(self._queue_processor())
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_tasks())
            
            logger.info("TaskQueue initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize TaskQueue: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown task queue system"""
        logger.info("Shutting down TaskQueue...")
        
        # Cancel background tasks
        if self._queue_processor_task:
            self._queue_processor_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        # Cancel active executions
        for execution in self._active_executions.values():
            if execution.status == TaskStatus.RUNNING:
                await self._cancel_task_execution(execution.task_id)
        
        logger.info("TaskQueue shutdown complete")
    
    def register_task_handler(self, task_type: str, handler: Callable):
        """Register a task handler function"""
        self._task_handlers[task_type] = handler
        logger.info(f"Registered handler for task type: {task_type}")
    
    async def submit_task(self, task_def: TaskDefinition) -> str:
        """Submit a new task to the queue"""
        try:
            # Save to database
            await self._save_task_to_db(task_def)
            
            # Add to appropriate priority queue
            await self._queues[task_def.priority].put(task_def)
            
            logger.info(f"Submitted task {task_def.task_id} with priority {task_def.priority.name}")
            return task_def.task_id
            
        except Exception as e:
            logger.error(f"Failed to submit task {task_def.task_id}: {e}")
            raise
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task"""
        try:
            # Check if task is running
            if task_id in self._active_executions:
                execution = self._active_executions[task_id]
                if execution.status == TaskStatus.RUNNING:
                    await self._cancel_task_execution(task_id)
                
                execution.status = TaskStatus.CANCELLED
                execution.completed_at = datetime.now(timezone.utc)
                
                # Update database
                await self._update_task_status(task_id, TaskStatus.CANCELLED)
                
                logger.info(f"Cancelled running task {task_id}")
                return True
            
            # Update database status for pending tasks
            session = get_db_session()
            task = session.query(Task).filter(Task.id == task_id).first()
            if task and task.status in ['pending', 'assigned']:
                task.status = TaskStatus.CANCELLED.value
                task.completed_at = datetime.now(timezone.utc)
                session.commit()
                session.close()
                
                logger.info(f"Cancelled pending task {task_id}")
                return True
            
            session.close()
            logger.warning(f"Task {task_id} not found or cannot be cancelled")
            return False
            
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return False
    
    async def get_task_status(self, task_id: str) -> Optional[TaskExecution]:
        """Get current task status"""
        # Check active executions first
        if task_id in self._active_executions:
            return self._active_executions[task_id]
        
        # Check database
        try:
            session = get_db_session()
            task = session.query(Task).filter(Task.id == task_id).first()
            session.close()
            
            if task:
                execution = TaskExecution(
                    task_id=task.id,
                    device_serial=task.device_serial or "",
                    status=TaskStatus(task.status),
                    started_at=task.started_at,
                    completed_at=task.completed_at,
                    result=json.loads(task.result) if task.result else None,
                    error_message=task.error_message,
                    retry_count=task.retry_count
                )
                return execution
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get task status for {task_id}: {e}")
            return None
    
    async def update_device_availability(self, device_serial: str, available: bool):
        """Update device availability status"""
        self._device_availability[device_serial] = available
        logger.debug(f"Device {device_serial} availability: {available}")
    
    async def get_queue_statistics(self) -> Dict[str, Any]:
        """Get queue statistics"""
        stats = {
            'queued_tasks': {},
            'active_tasks': len(self._active_executions),
            'available_devices': sum(1 for available in self._device_availability.values() if available),
            'total_devices': len(self._device_availability),
            'registered_handlers': list(self._task_handlers.keys())
        }
        
        for priority in TaskPriority:
            stats['queued_tasks'][priority.name] = self._queues[priority].qsize()
        
        return stats
    
    async def _load_pending_tasks(self):
        """Load pending tasks from database into queues"""
        try:
            session = get_db_session()
            
            # Get pending and assigned tasks
            pending_tasks = session.query(Task).filter(
                Task.status.in_(['pending', 'assigned'])
            ).order_by(Task.priority.desc(), Task.created_at.asc()).all()
            
            for task in pending_tasks:
                try:
                    task_def = TaskDefinition(
                        task_id=task.id,
                        task_type=task.task_type,
                        priority=TaskPriority(task.priority),
                        device_requirements=json.loads(task.device_requirements or '{}'),
                        parameters=json.loads(task.parameters),
                        timeout_seconds=task.timeout_seconds,
                        max_retries=task.max_retries,
                        created_at=task.created_at,
                        scheduled_for=task.scheduled_for,
                        callback_url=task.callback_url
                    )
                    
                    # Check if task is scheduled for future
                    if task_def.scheduled_for and task_def.scheduled_for > datetime.now(timezone.utc):
                        continue  # Skip future tasks for now
                    
                    await self._queues[task_def.priority].put(task_def)
                    
                except Exception as e:
                    logger.error(f"Failed to load task {task.id}: {e}")
            
            session.close()
            logger.info(f"Loaded {len(pending_tasks)} pending tasks from database")
            
        except Exception as e:
            logger.error(f"Failed to load pending tasks: {e}")
    
    async def _queue_processor(self):
        """Background task processor"""
        logger.info("Queue processor started")
        
        while True:
            try:
                # Process queues by priority (highest first)
                task_processed = False
                
                for priority in sorted(TaskPriority, key=lambda p: p.value, reverse=True):
                    if not self._queues[priority].empty():
                        # Check if we have available devices
                        available_devices = [
                            serial for serial, available in self._device_availability.items() 
                            if available
                        ]
                        
                        if available_devices:
                            try:
                                task_def = self._queues[priority].get_nowait()
                                await self._assign_and_execute_task(task_def, available_devices)
                                task_processed = True
                            except asyncio.QueueEmpty:
                                continue
                        else:
                            logger.debug("No available devices for task execution")
                            break
                
                # Sleep if no tasks processed
                if not task_processed:
                    await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in queue processor: {e}")
                await asyncio.sleep(5)
    
    async def _assign_and_execute_task(self, task_def: TaskDefinition, available_devices: List[str]):
        """Assign task to suitable device and execute"""
        try:
            # Find suitable device
            suitable_device = await self._find_suitable_device(task_def, available_devices)
            
            if not suitable_device:
                logger.warning(f"No suitable device found for task {task_def.task_id}, requeueing")
                # Requeue task
                await self._queues[task_def.priority].put(task_def)
                return
            
            # Mark device as busy
            self._device_availability[suitable_device] = False
            
            # Create execution tracking
            execution = TaskExecution(
                task_id=task_def.task_id,
                device_serial=suitable_device,
                status=TaskStatus.ASSIGNED,
                started_at=datetime.now(timezone.utc)
            )
            
            self._active_executions[task_def.task_id] = execution
            
            # Update database
            await self._update_task_assignment(task_def.task_id, suitable_device)
            
            # Execute task
            asyncio.create_task(self._execute_task(task_def, execution))
            
            logger.info(f"Assigned task {task_def.task_id} to device {suitable_device}")
            
        except Exception as e:
            logger.error(f"Failed to assign task {task_def.task_id}: {e}")
    
    async def _find_suitable_device(self, task_def: TaskDefinition, available_devices: List[str]) -> Optional[str]:
        """Find suitable device for task execution"""
        # For now, simple round-robin selection
        # In production, this could check device capabilities, requirements, etc.
        
        if not available_devices:
            return None
        
        # Check device requirements
        requirements = task_def.device_requirements
        
        for device_serial in available_devices:
            # Simple check - in production, this would check actual device capabilities
            if self._device_meets_requirements(device_serial, requirements):
                return device_serial
        
        # Fallback to first available device
        return available_devices[0]
    
    def _device_meets_requirements(self, device_serial: str, requirements: Dict[str, Any]) -> bool:
        """Check if device meets task requirements"""
        # Placeholder implementation
        # In production, this would check:
        # - Android version
        # - Installed apps
        # - Screen resolution
        # - Available storage
        # - etc.
        
        return True  # For now, assume all devices are suitable
    
    async def _execute_task(self, task_def: TaskDefinition, execution: TaskExecution):
        """Execute task on assigned device"""
        try:
            execution.status = TaskStatus.RUNNING
            execution.started_at = datetime.now(timezone.utc)
            
            # Update database
            await self._update_task_status(task_def.task_id, TaskStatus.RUNNING)
            
            logger.info(f"Executing task {task_def.task_id} on device {execution.device_serial}")
            
            # Get task handler
            handler = self._task_handlers.get(task_def.task_type)
            if not handler:
                raise Exception(f"No handler registered for task type: {task_def.task_type}")
            
            # Execute with timeout
            try:
                result = await asyncio.wait_for(
                    handler(execution.device_serial, task_def.parameters),
                    timeout=task_def.timeout_seconds
                )
                
                # Task completed successfully
                execution.status = TaskStatus.COMPLETED
                execution.completed_at = datetime.now(timezone.utc)
                execution.result = result
                
                await self._update_task_completion(task_def.task_id, TaskStatus.COMPLETED, result)
                
                logger.info(f"Task {task_def.task_id} completed successfully")
                
            except asyncio.TimeoutError:
                execution.status = TaskStatus.TIMEOUT
                execution.completed_at = datetime.now(timezone.utc)
                execution.error_message = f"Task timed out after {task_def.timeout_seconds} seconds"
                
                await self._update_task_completion(task_def.task_id, TaskStatus.TIMEOUT, None, execution.error_message)
                
                logger.error(f"Task {task_def.task_id} timed out")
                
        except Exception as e:
            execution.status = TaskStatus.FAILED
            execution.completed_at = datetime.now(timezone.utc)
            execution.error_message = str(e)
            execution.retry_count += 1
            
            logger.error(f"Task {task_def.task_id} failed: {e}")
            
            # Check if we should retry
            if execution.retry_count < task_def.max_retries:
                logger.info(f"Retrying task {task_def.task_id} (attempt {execution.retry_count + 1}/{task_def.max_retries})")
                
                # Requeue task for retry
                await self._queues[task_def.priority].put(task_def)
                await self._update_task_status(task_def.task_id, TaskStatus.PENDING)
            else:
                await self._update_task_completion(task_def.task_id, TaskStatus.FAILED, None, execution.error_message)
        
        finally:
            # Mark device as available again
            self._device_availability[execution.device_serial] = True
            
            # Remove from active executions
            if task_def.task_id in self._active_executions:
                del self._active_executions[task_def.task_id]
    
    async def _cancel_task_execution(self, task_id: str):
        """Cancel running task execution"""
        # This would send cancellation signal to the task handler
        # Implementation depends on how tasks are structured
        logger.info(f"Cancelling task execution: {task_id}")
    
    async def _save_task_to_db(self, task_def: TaskDefinition):
        """Save task definition to database"""
        try:
            session = get_db_session()
            
            task = Task(
                id=task_def.task_id,
                task_type=task_def.task_type,
                priority=task_def.priority.value,
                status=TaskStatus.PENDING.value,
                parameters=json.dumps(task_def.parameters),
                device_requirements=json.dumps(task_def.device_requirements),
                timeout_seconds=task_def.timeout_seconds,
                max_retries=task_def.max_retries,
                callback_url=task_def.callback_url,
                created_at=task_def.created_at,
                scheduled_for=task_def.scheduled_for
            )
            
            session.add(task)
            session.commit()
            session.close()
            
        except Exception as e:
            logger.error(f"Failed to save task to database: {e}")
            session.rollback()
            session.close()
            raise
    
    async def _update_task_status(self, task_id: str, status: TaskStatus):
        """Update task status in database"""
        try:
            session = get_db_session()
            
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = status.value
                if status == TaskStatus.RUNNING:
                    task.started_at = datetime.now(timezone.utc)
                session.commit()
            
            session.close()
            
        except Exception as e:
            logger.error(f"Failed to update task status: {e}")
            session.rollback()
            session.close()
    
    async def _update_task_assignment(self, task_id: str, device_serial: str):
        """Update task device assignment"""
        try:
            session = get_db_session()
            
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                task.device_serial = device_serial
                task.status = TaskStatus.ASSIGNED.value
                session.commit()
            
            session.close()
            
        except Exception as e:
            logger.error(f"Failed to update task assignment: {e}")
            session.rollback()
            session.close()
    
    async def _update_task_completion(self, task_id: str, status: TaskStatus, result: Optional[Dict], error_message: Optional[str] = None):
        """Update task completion in database"""
        try:
            session = get_db_session()
            
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = status.value
                task.completed_at = datetime.now(timezone.utc)
                if result:
                    task.result = json.dumps(result)
                if error_message:
                    task.error_message = error_message
                session.commit()
            
            session.close()
            
        except Exception as e:
            logger.error(f"Failed to update task completion: {e}")
            session.rollback()
            session.close()
    
    async def _cleanup_expired_tasks(self):
        """Cleanup old completed tasks"""
        logger.info("Cleanup task started")
        
        while True:
            try:
                # Run cleanup every hour
                await asyncio.sleep(3600)
                
                # Remove tasks older than 7 days
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
                
                session = get_db_session()
                deleted_count = session.query(Task).filter(
                    Task.completed_at < cutoff_date,
                    Task.status.in_(['completed', 'failed', 'cancelled'])
                ).delete()
                
                session.commit()
                session.close()
                
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} expired tasks")
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")


# Global task queue instance
_task_queue: Optional[TaskQueue] = None


async def get_task_queue() -> TaskQueue:
    """Get global task queue instance"""
    global _task_queue
    if _task_queue is None:
        _task_queue = TaskQueue()
        await _task_queue.initialize()
    return _task_queue


def create_task_definition(
    task_type: str,
    parameters: Dict[str, Any],
    priority: TaskPriority = TaskPriority.NORMAL,
    device_requirements: Optional[Dict[str, Any]] = None,
    timeout_seconds: int = 300,
    max_retries: int = 3,
    scheduled_for: Optional[datetime] = None,
    callback_url: Optional[str] = None
) -> TaskDefinition:
    """Helper function to create task definition"""
    
    return TaskDefinition(
        task_id=str(uuid.uuid4()),
        task_type=task_type,
        priority=priority,
        device_requirements=device_requirements or {},
        parameters=parameters,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        created_at=datetime.now(timezone.utc),
        scheduled_for=scheduled_for,
        callback_url=callback_url
    )