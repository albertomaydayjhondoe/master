"""
Device Farm v5 - Database Models
SQLAlchemy models for persistence layer
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger


Base = declarative_base()


class Device(Base):
    """Android device model"""
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    serial = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100))
    status = Column(String(20), default="offline")  # offline, online, busy, error
    assigned_profile = Column(String(50))
    
    # Device information
    model = Column(String(100))
    android_version = Column(String(20))
    screen_resolution = Column(String(20))
    
    # Connection info
    appium_port = Column(Integer)
    proxy_host = Column(String(100))
    proxy_port = Column(Integer)
    
    # Timestamps
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Statistics
    total_tasks_completed = Column(Integer, default=0)
    total_tasks_failed = Column(Integer, default=0)
    uptime_hours = Column(Float, default=0.0)
    
    def __repr__(self):
        return f"<Device(serial='{self.serial}', status='{self.status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert device to dictionary"""
        return {
            'id': self.id,
            'serial': self.serial,
            'name': self.name,
            'status': self.status,
            'assigned_profile': self.assigned_profile,
            'model': self.model,
            'android_version': self.android_version,
            'screen_resolution': self.screen_resolution,
            'appium_port': self.appium_port,
            'proxy_host': self.proxy_host,
            'proxy_port': self.proxy_port,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'total_tasks_completed': self.total_tasks_completed,
            'total_tasks_failed': self.total_tasks_failed,
            'uptime_hours': self.uptime_hours
        }


class GologinProfile(Base):
    """Gologin profile model"""
    __tablename__ = "gologin_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    gologin_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100))
    status = Column(String(20), default="available")  # available, in_use, disabled
    
    # Proxy configuration
    proxy_config = Column(JSON)  # Store full proxy config as JSON
    proxy_host = Column(String(100))
    proxy_port = Column(Integer)
    proxy_type = Column(String(20))  # http, socks5
    
    # Fingerprint data
    fingerprint = Column(JSON)  # Store fingerprint data as JSON
    user_agent = Column(Text)
    screen_width = Column(Integer)
    screen_height = Column(Integer)
    timezone = Column(String(50))
    language = Column(String(10))
    
    # Usage statistics
    last_used = Column(DateTime)
    total_usage_minutes = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<GologinProfile(gologin_id='{self.gologin_id}', status='{self.status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        return {
            'id': self.id,
            'gologin_id': self.gologin_id,
            'name': self.name,
            'status': self.status,
            'proxy_config': self.proxy_config,
            'proxy_host': self.proxy_host,
            'proxy_port': self.proxy_port,
            'proxy_type': self.proxy_type,
            'fingerprint': self.fingerprint,
            'user_agent': self.user_agent,
            'screen_width': self.screen_width,
            'screen_height': self.screen_height,
            'timezone': self.timezone,
            'language': self.language,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'total_usage_minutes': self.total_usage_minutes,
            'success_rate': self.success_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Task(Base):
    """Task model for device automation"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String(50), nullable=False)  # web_navigation, app_interaction, etc.
    priority = Column(Integer, default=5)  # 1 (highest) to 10 (lowest)
    status = Column(String(20), default="pending")  # pending, running, completed, failed, cancelled
    
    # Task configuration
    url = Column(String(500))
    app_package = Column(String(100))
    actions = Column(JSON)  # List of actions to perform
    expected_duration = Column(Integer)  # Expected duration in seconds
    
    # Assignment and execution
    assigned_device_id = Column(Integer)
    assigned_device_serial = Column(String(50))
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Results and metrics
    result = Column(JSON)  # Task execution result
    success = Column(Boolean, default=False)
    error_message = Column(Text)
    execution_time = Column(Float)  # Actual execution time in seconds
    screenshots = Column(JSON)  # List of screenshot paths
    
    # Retry management
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<Task(id={self.id}, type='{self.task_type}', status='{self.status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'task_type': self.task_type,
            'priority': self.priority,
            'status': self.status,
            'url': self.url,
            'app_package': self.app_package,
            'actions': self.actions,
            'expected_duration': self.expected_duration,
            'assigned_device_id': self.assigned_device_id,
            'assigned_device_serial': self.assigned_device_serial,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'result': self.result,
            'success': self.success,
            'error_message': self.error_message,
            'execution_time': self.execution_time,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DeviceLog(Base):
    """Device activity log"""
    __tablename__ = "device_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, nullable=False)
    device_serial = Column(String(50), index=True)
    level = Column(String(10), nullable=False)  # INFO, WARNING, ERROR, DEBUG
    message = Column(Text, nullable=False)
    
    # Context information
    task_id = Column(Integer)
    component = Column(String(50))  # adb, appium, gologin, etc.
    
    # Additional metadata
    metadata = Column(JSON)
    
    # Timestamp
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    def __repr__(self):
        return f"<DeviceLog(device_serial='{self.device_serial}', level='{self.level}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log to dictionary"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_serial': self.device_serial,
            'level': self.level,
            'message': self.message,
            'task_id': self.task_id,
            'component': self.component,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class SystemMetrics(Base):
    """System performance metrics"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # System metrics
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    disk_usage = Column(Float)
    
    # Device farm metrics
    total_devices = Column(Integer)
    online_devices = Column(Integer)
    busy_devices = Column(Integer)
    
    # Task metrics
    pending_tasks = Column(Integer)
    running_tasks = Column(Integer)
    completed_tasks_hour = Column(Integer)
    failed_tasks_hour = Column(Integer)
    
    # Gologin metrics
    active_profiles = Column(Integer)
    profile_success_rate = Column(Float)
    
    # Timestamp
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            'id': self.id,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'disk_usage': self.disk_usage,
            'total_devices': self.total_devices,
            'online_devices': self.online_devices,
            'busy_devices': self.busy_devices,
            'pending_tasks': self.pending_tasks,
            'running_tasks': self.running_tasks,
            'completed_tasks_hour': self.completed_tasks_hour,
            'failed_tasks_hour': self.failed_tasks_hour,
            'active_profiles': self.active_profiles,
            'profile_success_rate': self.profile_success_rate,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
            
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            session = self.get_session()
            session.execute("SELECT 1")
            session.close()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global _db_manager
    if _db_manager is None:
        from .config_manager import get_config
        config = get_config()
        _db_manager = DatabaseManager(config.database_url)
        _db_manager.create_tables()
    return _db_manager


def get_db_session() -> Session:
    """Get database session"""
    return get_db_manager().get_session()