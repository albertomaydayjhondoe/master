"""Training script for YOLOv8 TikTok UI detector.

This script handles model training using labeled screenshots. To use:

1. Prepare dataset following data.yaml structure
2. Run training:
   python -m ml_core.training.train_yolo
3. Trained weights will be saved to /app/data/models/production/

Requirements:
- ultralytics
- torch
- pyyaml
"""
from pathlib import Path
import shutil
import logging
from datetime import datetime

from ml_core.models.yolo_prod import YoloScreenshotDetector
from config.ml import get_model_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run YOLOv8 training on TikTok UI dataset."""
    # Load config
    config = get_model_config()
    yolo_config = config["yolo_screenshot"]
    
    # Paths
    output_dir = Path("/app/data/models/production")
    checkpoint_dir = Path("/app/data/models/checkpoints")
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize model
    try:
        detector = YoloScreenshotDetector(
            model_path="yolov8n.pt",  # Start from COCO pretrained
            device=yolo_config["device"]
        )
        
        # Train model
        logger.info("Starting training...")
        detector.train(
            data_yaml=yolo_config["training"]["data_yaml"],
            epochs=yolo_config["training"]["epochs"],
            imgsz=yolo_config["training"]["imgsz"],
            batch=yolo_config["training"]["batch"]
        )
        
        # Save checkpoint
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_path = checkpoint_dir / f"tiktok_ui_detector_{timestamp}.pt"
        shutil.copy(detector.model_path, checkpoint_path)
        logger.info(f"Saved checkpoint to {checkpoint_path}")
        
        # Copy best model to production
        prod_path = output_dir / "tiktok_ui_detector.pt"
        shutil.copy(detector.model_path, prod_path)
        logger.info(f"Saved production model to {prod_path}")
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()