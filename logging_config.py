"""
Centralized Logging Configuration
Provides consistent logging setup across all project modules
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

def setup_project_logging(
    name: str = "universal_automation",
    level: str = "INFO",
    log_dir: Optional[str] = None
) -> logging.Logger:
    """
    Setup standardized logging for the project
    
    Args:
        name: Logger name
        level: Logging level
        log_dir: Directory for log files
    
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_path / f"{name}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Create default project logger
project_logger = setup_project_logging(log_dir="logs")
