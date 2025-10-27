"""
Device Farm v5 - Enhanced Ultralytics Integration
Advanced YOLO integration specifically for Device Farm automation
"""
import asyncio
import os
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import tempfile
import json
from datetime import datetime, timezone
from loguru import logger
import torch
from PIL import Image
import numpy as np

# Import Device Farm v5 components
from ..config_manager import get_config
from ..core.adb_manager import get_adb_manager

# Import existing ML v4 components if available
try:
    from ml_core.models.yolo_prod import YoloScreenshotDetector as MLv4YoloDetector
    from ml_core.models.factory import get_yolo_screenshot_detector
    ML_V4_AVAILABLE = True
except ImportError:
    ML_V4_AVAILABLE = False
    logger.warning("ML v4 YOLO components not available, using Device Farm v5 implementation")

# Ultralytics import
try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False
    logger.warning("Ultralytics not available. Install with: pip install ultralytics")


class DeviceFarmYoloDetector:
    """Enhanced YOLO detector specifically for Device Farm v5 automation"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or get_config().raw_config.get('ml_models', {})
        
        # Model configuration
        self.model_config = self.config.get('yolo_screenshot', {})
        self.model_path = self.model_config.get('model_path', 'yolov8n.pt')
        self.device = self.model_config.get('device', 'cuda' if torch.cuda.is_available() else 'cpu')
        self.confidence_threshold = self.model_config.get('confidence_threshold', 0.7)
        
        # Initialize model
        self.model = None
        self._initialize_model()
        
        # TikTok UI element classes
        self.tiktok_classes = {
            0: 'like_button',
            1: 'comment_button', 
            2: 'share_button',
            3: 'follow_button',
            4: 'profile_avatar',
            5: 'video_player',
            6: 'text_overlay',
            7: 'music_info',
            8: 'search_bar',
            9: 'discover_tab',
            10: 'home_tab',
            11: 'notification_icon',
            12: 'menu_button',
            13: 'live_badge',
            14: 'verified_badge',
            15: 'duet_button'
        }
        
        # Device Farm specific detection contexts
        self.automation_contexts = {
            'engagement': ['like_button', 'comment_button', 'share_button', 'follow_button'],
            'navigation': ['home_tab', 'discover_tab', 'profile_avatar', 'search_bar'],
            'content_analysis': ['video_player', 'text_overlay', 'music_info'],
            'account_health': ['notification_icon', 'verified_badge', 'live_badge'],
            'interaction_safety': ['menu_button', 'duet_button']
        }
        
        logger.info(f"DeviceFarmYoloDetector initialized with device: {self.device}")
    
    def _initialize_model(self):
        """Initialize YOLO model with fallback options"""
        try:
            if ULTRALYTICS_AVAILABLE:
                # Try to load from ML v4 first
                if ML_V4_AVAILABLE and os.path.exists(self.model_path):
                    logger.info(f"Loading ML v4 production model: {self.model_path}")
                    self.model = YOLO(self.model_path)
                else:
                    # Use pretrained YOLO model
                    logger.info("Loading pretrained YOLOv8 model")
                    self.model = YOLO('yolov8n.pt')  # Will download if not present
                
                self.model.to(self.device)
                
            else:
                logger.error("Ultralytics not available. Please install: pip install ultralytics")
                
        except Exception as e:
            logger.error(f"Failed to initialize YOLO model: {e}")
            self.model = None
    
    async def analyze_device_screenshot(self, device_serial: str, save_analysis: bool = True) -> Dict[str, Any]:
        """
        Take screenshot from device and analyze with YOLO
        
        Args:
            device_serial: Android device serial number
            save_analysis: Whether to save analysis results
            
        Returns:
            Analysis results with detections and automation recommendations
        """
        try:
            # Take screenshot using ADB manager
            adb_manager = await get_adb_manager()
            screenshot_path = await adb_manager.take_screenshot(device_serial)
            
            if not screenshot_path or not os.path.exists(screenshot_path):
                raise Exception(f"Failed to capture screenshot for device {device_serial}")
            
            # Analyze screenshot
            analysis_result = await self.analyze_image(screenshot_path)
            
            # Add device context
            analysis_result['device_serial'] = device_serial
            analysis_result['screenshot_path'] = screenshot_path
            analysis_result['timestamp'] = datetime.now(timezone.utc).isoformat()
            
            # Generate automation recommendations
            recommendations = self._generate_automation_recommendations(analysis_result['detections'])
            analysis_result['automation_recommendations'] = recommendations
            
            # Save analysis if requested
            if save_analysis:
                await self._save_analysis_results(device_serial, analysis_result)
            
            logger.info(f"Screenshot analysis completed for device {device_serial}: {len(analysis_result['detections'])} detections")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Screenshot analysis failed for device {device_serial}: {e}")
            raise
    
    async def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze image with YOLO model
        
        Args:
            image_path: Path to image file
            
        Returns:
            Analysis results with detections and metadata
        """
        if not self.model:
            raise Exception("YOLO model not initialized")
        
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            
            # Run inference
            results = self.model(image, device=self.device, verbose=False)
            
            # Process detections
            detections = []
            for result in results:
                if result.boxes is not None:
                    boxes = result.boxes
                    
                    for i, box in enumerate(boxes):
                        # Extract box data
                        coords = box.xyxy[0].cpu().numpy()
                        confidence = float(box.conf[0].cpu().numpy())
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Filter by confidence threshold
                        if confidence >= self.confidence_threshold:
                            detection = {
                                'id': i,
                                'class_id': class_id,
                                'class_name': self.tiktok_classes.get(class_id, f'unknown_{class_id}'),
                                'confidence': round(confidence, 3),
                                'bbox': {
                                    'x1': int(coords[0]),
                                    'y1': int(coords[1]), 
                                    'x2': int(coords[2]),
                                    'y2': int(coords[3]),
                                    'width': int(coords[2] - coords[0]),
                                    'height': int(coords[3] - coords[1]),
                                    'center_x': int((coords[0] + coords[2]) / 2),
                                    'center_y': int((coords[1] + coords[3]) / 2)
                                }
                            }
                            detections.append(detection)
            
            # Calculate image metadata
            img_array = np.array(image)
            image_info = {
                'width': image.width,
                'height': image.height,
                'channels': len(img_array.shape),
                'format': image.format,
                'mode': image.mode
            }
            
            analysis_result = {
                'image_info': image_info,
                'detections': detections,
                'detection_count': len(detections),
                'model_info': {
                    'model_path': str(self.model_path),
                    'device': self.device,
                    'confidence_threshold': self.confidence_threshold
                },
                'processing_time': datetime.now(timezone.utc).isoformat()
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            raise
    
    def _generate_automation_recommendations(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate automation recommendations based on detected elements"""
        recommendations = {
            'safe_actions': [],
            'risky_actions': [],
            'clickable_elements': [],
            'app_state': 'unknown',
            'automation_confidence': 0.0
        }
        
        detected_classes = [d['class_name'] for d in detections]
        
        # Determine app state
        if 'video_player' in detected_classes:
            if 'home_tab' in detected_classes:
                recommendations['app_state'] = 'tiktok_main_feed'
            elif 'profile_avatar' in detected_classes:
                recommendations['app_state'] = 'tiktok_profile_view'
            else:
                recommendations['app_state'] = 'tiktok_video_view'
        elif 'search_bar' in detected_classes:
            recommendations['app_state'] = 'tiktok_search'
        elif 'discover_tab' in detected_classes:
            recommendations['app_state'] = 'tiktok_discover'
        
        # Analyze engagement opportunities
        for detection in detections:
            class_name = detection['class_name']
            confidence = detection['confidence']
            
            element_info = {
                'class_name': class_name,
                'coordinates': detection['bbox'],
                'confidence': confidence
            }
            
            # Safe actions (low risk)
            if class_name in ['like_button', 'video_player'] and confidence > 0.8:
                recommendations['safe_actions'].append({
                    'action': 'tap',
                    'element': element_info,
                    'risk_level': 'low'
                })
            
            # Risky actions (high risk)
            elif class_name in ['comment_button', 'follow_button', 'share_button'] and confidence > 0.9:
                recommendations['risky_actions'].append({
                    'action': 'tap',
                    'element': element_info,
                    'risk_level': 'high'
                })
            
            # All clickable elements
            if class_name in self.automation_contexts['engagement'] + self.automation_contexts['navigation']:
                recommendations['clickable_elements'].append(element_info)
        
        # Calculate automation confidence
        high_conf_detections = [d for d in detections if d['confidence'] > 0.8]
        if len(detections) > 0:
            recommendations['automation_confidence'] = len(high_conf_detections) / len(detections)
        
        return recommendations
    
    async def batch_analyze_devices(self, device_serials: List[str]) -> Dict[str, Dict[str, Any]]:
        """Analyze screenshots from multiple devices concurrently"""
        tasks = []
        
        for device_serial in device_serials:
            task = self.analyze_device_screenshot(device_serial)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        batch_results = {}
        for i, result in enumerate(results):
            device_serial = device_serials[i]
            
            if isinstance(result, Exception):
                logger.error(f"Analysis failed for device {device_serial}: {result}")
                batch_results[device_serial] = {
                    'success': False,
                    'error': str(result)
                }
            else:
                batch_results[device_serial] = {
                    'success': True,
                    'analysis': result
                }
        
        return batch_results
    
    async def detect_anomalies(self, device_serial: str, historical_data: Optional[List] = None) -> Dict[str, Any]:
        """Detect anomalies in current screenshot compared to historical patterns"""
        try:
            # Get current analysis
            current_analysis = await self.analyze_device_screenshot(device_serial, save_analysis=False)
            
            anomalies = {
                'anomaly_detected': False,
                'anomaly_score': 0.0,
                'anomaly_types': [],
                'recommendations': []
            }
            
            # Basic anomaly detection rules
            detections = current_analysis['detections']
            
            # Check for shadowban indicators
            if len(detections) == 0:
                anomalies['anomaly_detected'] = True
                anomalies['anomaly_score'] = 0.8
                anomalies['anomaly_types'].append('no_ui_elements')
                anomalies['recommendations'].append('Check if app is properly loaded')
            
            # Check for unusual UI layout
            expected_elements = ['video_player', 'like_button', 'home_tab']
            found_elements = [d['class_name'] for d in detections]
            missing_critical = [e for e in expected_elements if e not in found_elements]
            
            if len(missing_critical) > 1:
                anomalies['anomaly_detected'] = True
                anomalies['anomaly_score'] = max(anomalies['anomaly_score'], 0.6)
                anomalies['anomaly_types'].append('missing_critical_elements')
                anomalies['recommendations'].append(f'Missing elements: {missing_critical}')
            
            # Check for low confidence detections
            low_conf_ratio = len([d for d in detections if d['confidence'] < 0.6]) / max(len(detections), 1)
            if low_conf_ratio > 0.5:
                anomalies['anomaly_detected'] = True
                anomalies['anomaly_score'] = max(anomalies['anomaly_score'], 0.4)
                anomalies['anomaly_types'].append('low_confidence_detections')
                anomalies['recommendations'].append('UI elements unclear or app state changed')
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection failed for device {device_serial}: {e}")
            return {
                'anomaly_detected': True,
                'anomaly_score': 1.0,
                'anomaly_types': ['detection_failed'],
                'error': str(e)
            }
    
    async def _save_analysis_results(self, device_serial: str, analysis_result: Dict[str, Any]):
        """Save analysis results for historical tracking"""
        try:
            # Create analysis directory
            config = get_config()
            analysis_dir = Path(config.raw_config.get('data_dir', './data')) / 'analysis' / device_serial
            analysis_dir.mkdir(parents=True, exist_ok=True)
            
            # Save with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            analysis_file = analysis_dir / f'analysis_{timestamp}.json'
            
            with open(analysis_file, 'w') as f:
                json.dump(analysis_result, f, indent=2)
            
            logger.debug(f"Analysis results saved to {analysis_file}")
            
        except Exception as e:
            logger.error(f"Failed to save analysis results: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.model:
            return {'error': 'Model not initialized'}
        
        return {
            'model_path': str(self.model_path),
            'device': self.device,
            'confidence_threshold': self.confidence_threshold,
            'supported_classes': list(self.tiktok_classes.values()),
            'automation_contexts': list(self.automation_contexts.keys()),
            'ultralytics_available': ULTRALYTICS_AVAILABLE,
            'ml_v4_integration': ML_V4_AVAILABLE
        }


# Global detector instance
_yolo_detector: Optional[DeviceFarmYoloDetector] = None


async def get_device_farm_yolo_detector() -> DeviceFarmYoloDetector:
    """Get global YOLO detector instance for Device Farm v5"""
    global _yolo_detector
    if _yolo_detector is None:
        _yolo_detector = DeviceFarmYoloDetector()
    return _yolo_detector


# Task handlers for YOLO integration with Device Farm task queue
async def yolo_screenshot_task_handler(device_serial: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Task handler for YOLO screenshot analysis"""
    detector = await get_device_farm_yolo_detector()
    
    analysis_result = await detector.analyze_device_screenshot(
        device_serial=device_serial,
        save_analysis=parameters.get('save_analysis', True)
    )
    
    return {
        'task_type': 'yolo_screenshot_analysis',
        'device_serial': device_serial,
        'analysis_result': analysis_result,
        'success': True,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }


async def yolo_anomaly_detection_task_handler(device_serial: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Task handler for YOLO-based anomaly detection"""
    detector = await get_device_farm_yolo_detector()
    
    anomaly_result = await detector.detect_anomalies(
        device_serial=device_serial,
        historical_data=parameters.get('historical_data')
    )
    
    return {
        'task_type': 'yolo_anomaly_detection',
        'device_serial': device_serial,
        'anomaly_result': anomaly_result,
        'success': True,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }


async def yolo_batch_analysis_task_handler(device_serial: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Task handler for batch YOLO analysis across multiple devices"""
    detector = await get_device_farm_yolo_detector()
    
    device_list = parameters.get('device_serials', [device_serial])
    batch_results = await detector.batch_analyze_devices(device_list)
    
    return {
        'task_type': 'yolo_batch_analysis',
        'batch_results': batch_results,
        'devices_analyzed': len(device_list),
        'success': True,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }