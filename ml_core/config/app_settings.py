"""ML Core Configuration"""

import os
from typing import Dict, Any

def is_dummy_mode() -> bool:
    """Check if running in dummy mode"""
    return os.getenv('DUMMY_MODE', 'true').lower() == 'true'

def get_ml_config() -> Dict[str, Any]:
    """Get ML configuration"""
    return {
        'dummy_mode': is_dummy_mode(),
        'model_path': os.getenv('ML_MODEL_PATH', 'data/models/'),
        'batch_size': int(os.getenv('ML_BATCH_SIZE', '32')),
        'confidence_threshold': float(os.getenv('ML_CONFIDENCE_THRESHOLD', '0.7'))
    }