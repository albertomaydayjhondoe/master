"""Configuration for YOLO models including paths and hyperparameters.

This module loads model configuration from YAML files and provides it to
the factories when instantiating model classes.
"""
import os
from pathlib import Path
import yaml
from typing import Dict, Any


def get_model_config() -> Dict[str, Any]:
    """Load model configuration from YAML.
    
    The configuration file is expected at config/ml/model_config.yaml
    and should contain paths to model weights and training data.
    
    Returns:
        Dict containing model configuration
    """
    config_path = Path(__file__).parent / "model_config.yaml"
    
    if not config_path.exists():
        return {
            "yolo_screenshot": {
                "model_path": None,  # Will use dummy in dev
                "device": "cpu",
                "conf_threshold": 0.25,
                "iou_threshold": 0.45
            }
        }
        
    with open(config_path) as f:
        return yaml.safe_load(f)