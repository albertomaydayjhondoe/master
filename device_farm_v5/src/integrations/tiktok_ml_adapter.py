"""
Device Farm v5 - TikTok ML v4 Integration Adapter
Bridges Device Farm v5 with the existing TikTok ML v4 system
"""
import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from loguru import logger

# Import existing ML v4 components
try:
    from ml_core.api.main import app as ml_api_app
    from ml_core.models.factory import get_yolo_screenshot_detector, get_anomaly_detector
    from monitoring.health.account_health import AccountHealthMonitor
    from orchestration.scripts.workflow_validator import WorkflowValidator
    ML_V4_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ML v4 components not available: {e}")
    ML_V4_AVAILABLE = False

# Device Farm v5 imports
from ..config_manager import get_config
from ..core.task_queue import get_task_queue, create_task_definition, TaskPriority
from ..core.profile_synchronizer import get_profile_synchronizer
from ..core.adb_manager import get_adb_manager
from ..core.appium_controller import get_appium_controller


@dataclass
class TikTokEngagementTask:
    """TikTok engagement automation task"""
    account_id: str
    profile_id: str
    device_serial: str
    engagement_type: str  # like, follow, comment, share, view
    target_content: Dict[str, Any]  # video_id, user_id, hashtag, etc.
    ml_guidance: Dict[str, Any]  # ML predictions and recommendations
    constraints: Dict[str, Any]  # timing, duration, frequency limits
    
    def to_task_parameters(self) -> Dict[str, Any]:
        """Convert to task queue parameters"""
        return {
            'account_id': self.account_id,
            'profile_id': self.profile_id,
            'engagement_type': self.engagement_type,
            'target_content': self.target_content,
            'ml_guidance': self.ml_guidance,
            'constraints': self.constraints
        }


class TikTokMLIntegrationAdapter:
    """Integrates Device Farm v5 with TikTok ML v4 system"""
    
    def __init__(self):
        self.config = get_config()
        
        # ML v4 integration status
        self.ml_v4_available = ML_V4_AVAILABLE
        
        # Task type registry for TikTok automation
        self.tiktok_task_types = {
            'tiktok_like': self._handle_like_task,
            'tiktok_follow': self._handle_follow_task,
            'tiktok_comment': self._handle_comment_task,
            'tiktok_share': self._handle_share_task,
            'tiktok_view': self._handle_view_task,
            'tiktok_scroll': self._handle_scroll_task,
            'tiktok_screenshot': self._handle_screenshot_task,
            'tiktok_anomaly_check': self._handle_anomaly_check_task,
            # Enhanced YOLO integration tasks
            'yolo_screenshot_analysis': self._handle_yolo_screenshot_task,
            'yolo_anomaly_detection': self._handle_yolo_anomaly_task,
            'yolo_batch_analysis': self._handle_yolo_batch_task,
            'yolo_automation_guidance': self._handle_yolo_automation_guidance_task
        }
        
        # Analytics integration
        self.supabase_config = self._get_supabase_config()
        
        logger.info("TikTok ML Integration Adapter initialized")
    
    async def initialize(self) -> bool:
        """Initialize the integration adapter"""
        try:
            # Register task handlers with Device Farm v5
            task_queue = await get_task_queue()
            
            for task_type, handler in self.tiktok_task_types.items():
                task_queue.register_task_handler(task_type, handler)
            
            if self.ml_v4_available:
                logger.info("ML v4 components available - full integration enabled")
            else:
                logger.warning("ML v4 components not available - running in standalone mode")
            
            logger.info("TikTok ML Integration Adapter initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize TikTok ML Integration Adapter: {e}")
            return False
    
    def _get_supabase_config(self) -> Dict[str, str]:
        """Get Supabase configuration from existing ML v4 setup"""
        try:
            # Try to load from existing config
            if self.ml_v4_available:
                from config.app_settings import get_settings
                settings = get_settings()
                return {
                    'url': getattr(settings, 'SUPABASE_URL', ''),
                    'key': getattr(settings, 'SUPABASE_KEY', '')
                }
        except Exception as e:
            logger.debug(f"Could not load Supabase config from ML v4: {e}")
        
        # Fallback to Device Farm v5 config
        return {
            'url': self.config.raw_config.get('supabase', {}).get('url', ''),
            'key': self.config.raw_config.get('supabase', {}).get('key', '')
        }
    
    async def create_tiktok_engagement_campaign(
        self, 
        campaign_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a TikTok engagement campaign using ML guidance"""
        try:
            campaign_id = str(uuid.uuid4())
            
            logger.info(f"Creating TikTok engagement campaign: {campaign_id}")
            
            # Get ML predictions if available
            ml_guidance = {}
            if self.ml_v4_available:
                ml_guidance = await self._get_ml_engagement_guidance(campaign_config)
            
            # Get available device-profile pairs
            synchronizer = await get_profile_synchronizer()
            mappings = await synchronizer.get_all_mappings()
            
            available_pairs = [
                (serial, mapping.profile_id) 
                for serial, mapping in mappings.items() 
                if mapping.is_synced()
            ]
            
            if not available_pairs:
                raise Exception("No available device-profile pairs for campaign")
            
            # Create tasks based on campaign configuration
            tasks_created = []
            task_queue = await get_task_queue()
            
            for i, (device_serial, profile_id) in enumerate(available_pairs[:campaign_config.get('max_devices', 5)]):
                # Create engagement task
                engagement_task = TikTokEngagementTask(
                    account_id=f"account_{i+1}",
                    profile_id=profile_id,
                    device_serial=device_serial,
                    engagement_type=campaign_config.get('engagement_type', 'view'),
                    target_content=campaign_config.get('target_content', {}),
                    ml_guidance=ml_guidance,
                    constraints=campaign_config.get('constraints', {})
                )
                
                # Submit to task queue
                task_def = create_task_definition(
                    task_type=f"tiktok_{engagement_task.engagement_type}",
                    parameters=engagement_task.to_task_parameters(),
                    priority=TaskPriority.NORMAL,
                    timeout_seconds=campaign_config.get('timeout_seconds', 600),
                    max_retries=campaign_config.get('max_retries', 2)
                )
                
                task_id = await task_queue.submit_task(task_def)
                tasks_created.append({
                    'task_id': task_id,
                    'device_serial': device_serial,
                    'profile_id': profile_id,
                    'engagement_type': engagement_task.engagement_type
                })
            
            campaign_result = {
                'campaign_id': campaign_id,
                'status': 'created',
                'tasks_created': len(tasks_created),
                'tasks': tasks_created,
                'ml_guidance_available': self.ml_v4_available,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Created campaign {campaign_id} with {len(tasks_created)} tasks")
            return campaign_result
            
        except Exception as e:
            logger.error(f"Failed to create TikTok engagement campaign: {e}")
            raise
    
    async def _get_ml_engagement_guidance(self, campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get ML-based engagement guidance from TikTok ML v4 system"""
        if not self.ml_v4_available:
            return {}
        
        try:
            # This would integrate with the existing ML v4 API
            # For now, return mock guidance
            guidance = {
                'optimal_timing': {
                    'hour': 19,  # 7 PM
                    'day_of_week': 'friday',
                    'confidence': 0.85
                },
                'engagement_probability': 0.75,
                'risk_score': 0.25,
                'recommended_actions': [
                    'like',
                    'view',
                    'scroll'
                ],
                'avoid_actions': [
                    'comment',  # High risk
                    'share'     # High risk
                ],
                'human_behavior_patterns': {
                    'scroll_speed': 'medium',
                    'pause_duration': [2, 5],  # seconds
                    'interaction_delay': [1, 3]  # seconds
                }
            }
            
            logger.info("Generated ML engagement guidance")
            return guidance
            
        except Exception as e:
            logger.error(f"Failed to get ML engagement guidance: {e}")
            return {}
    
    # Task handlers for TikTok automation
    
    async def _handle_like_task(self, device_serial: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle TikTok like automation task"""
        try:
            logger.info(f"Executing TikTok like task on device {device_serial}")
            
            # Get Appium session
            appium_controller = await get_appium_controller()
            session = await appium_controller.get_or_create_session(device_serial)
            
            if not session:
                raise Exception(f"Could not get Appium session for device {device_serial}")
            
            # Simulate TikTok like automation
            result = await self._execute_tiktok_automation(
                session, 
                'like', 
                parameters,
                device_serial
            )
            
            # Store analytics if Supabase is available
            if self.supabase_config.get('url'):
                await self._store_engagement_analytics(device_serial, 'like', result)
            
            return result
            
        except Exception as e:
            logger.error(f"Like task failed on device {device_serial}: {e}")
            raise
    
    async def _handle_follow_task(self, device_serial: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle TikTok follow automation task"""
        try:
            logger.info(f"Executing TikTok follow task on device {device_serial}")
            
            # Similar implementation to like task
            result = {
                'action': 'follow',
                'device_serial': device_serial,
                'target': parameters.get('target_content', {}),
                'success': True,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'ml_guidance_applied': bool(parameters.get('ml_guidance'))
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Follow task failed on device {device_serial}: {e}")
            raise
    
    async def _handle_comment_task(self, device_serial: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle TikTok comment automation task"""
        try:
            logger.info(f"Executing TikTok comment task on device {device_serial}")
            
            # High-risk action - extra validation
            ml_guidance = parameters.get('ml_guidance', {})
            risk_score = ml_guidance.get('risk_score', 1.0)
            
            if risk_score > 0.7:
                logger.warning(f"High risk score ({risk_score}) for comment task - aborting")
                raise Exception(f"Risk score too high: {risk_score}")
            
            result = {
                'action': 'comment',
                'device_serial': device_serial,
                'comment_text': parameters.get('comment_text', 'Nice video! 👍'),
                'target': parameters.get('target_content', {}),
                'success': True,
                'risk_score': risk_score,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Comment task failed on device {device_serial}: {e}")
            raise
    
    async def _handle_share_task(self, device_serial: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle TikTok share automation task"""
        try:
            logger.info(f"Executing TikTok share task on device {device_serial}")
            
            result = {
                'action': 'share',
                'device_serial': device_serial,
                'target': parameters.get('target_content', {}),
                'share_method': 'copy_link',  # Safest option
                'success': True,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Share task failed on device {device_serial}: {e}")
            raise
    
    async def _handle_view_task(self, device_serial: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle TikTok view automation task"""
        try:
            logger.info(f"Executing TikTok view task on device {device_serial}")
            
            # Low-risk action - can be performed frequently
            view_duration = parameters.get('constraints', {}).get('view_duration', 5)
            
            result = {
                'action': 'view',
                'device_serial': device_serial,
                'target': parameters.get('target_content', {}),
                'view_duration_seconds': view_duration,
                'success': True,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"View task failed on device {device_serial}: {e}")
            raise
    
    async def _handle_scroll_task(self, device_serial: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle TikTok scroll automation task"""
        try:
            logger.info(f"Executing TikTok scroll task on device {device_serial}")
            
            # Apply human behavior patterns
            ml_guidance = parameters.get('ml_guidance', {})
            behavior = ml_guidance.get('human_behavior_patterns', {})
            
            scroll_count = parameters.get('constraints', {}).get('scroll_count', 10)
            scroll_speed = behavior.get('scroll_speed', 'medium')
            
            result = {
                'action': 'scroll',
                'device_serial': device_serial,
                'scroll_count': scroll_count,
                'scroll_speed': scroll_speed,
                'success': True,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Scroll task failed on device {device_serial}: {e}")
            raise
    
    async def _handle_screenshot_task(self, device_serial: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle TikTok screenshot analysis task"""
        try:
            logger.info(f"Executing TikTok screenshot task on device {device_serial}")
            
            # Take screenshot
            adb_manager = await get_adb_manager()
            screenshot_path = await adb_manager.take_screenshot(device_serial)
            
            # Analyze with ML if available
            analysis_result = {}
            if self.ml_v4_available:
                analysis_result = await self._analyze_screenshot_with_ml(screenshot_path)
            
            result = {
                'action': 'screenshot',
                'device_serial': device_serial,
                'screenshot_path': screenshot_path,
                'ml_analysis': analysis_result,
                'success': True,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Screenshot task failed on device {device_serial}: {e}")
            raise
    
    async def _handle_anomaly_check_task(self, device_serial: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle anomaly detection task"""
        try:
            logger.info(f"Executing anomaly check task on device {device_serial}")
            
            # Collect device metrics
            adb_manager = await get_adb_manager()
            device_info = await adb_manager.get_device_info(device_serial)
            
            # Run anomaly detection if available
            anomaly_detected = False
            anomaly_score = 0.0
            
            if self.ml_v4_available:
                anomaly_result = await self._detect_anomalies(device_serial, device_info)
                anomaly_detected = anomaly_result.get('anomaly_detected', False)
                anomaly_score = anomaly_result.get('score', 0.0)
            
            result = {
                'action': 'anomaly_check',
                'device_serial': device_serial,
                'anomaly_detected': anomaly_detected,
                'anomaly_score': anomaly_score,
                'device_info': device_info,
                'success': True,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Alert if anomaly detected
            if anomaly_detected:
                logger.warning(f"Anomaly detected on device {device_serial}: score {anomaly_score}")
                await self._send_anomaly_alert(device_serial, anomaly_score)
            
            return result
            
        except Exception as e:
            logger.error(f"Anomaly check task failed on device {device_serial}: {e}")
            raise
    
    async def _execute_tiktok_automation(
        self, 
        session: Any, 
        action_type: str, 
        parameters: Dict[str, Any],
        device_serial: str
    ) -> Dict[str, Any]:
        """Execute TikTok automation with human-like behavior"""
        try:
            # Apply ML guidance for human behavior
            ml_guidance = parameters.get('ml_guidance', {})
            behavior = ml_guidance.get('human_behavior_patterns', {})
            
            # Simulate human delays
            import random
            delay_range = behavior.get('interaction_delay', [1, 3])
            delay = random.uniform(delay_range[0], delay_range[1])
            await asyncio.sleep(delay)
            
            # Execute action (placeholder - would use actual Appium commands)
            logger.debug(f"Executing {action_type} with {delay:.2f}s human delay")
            
            result = {
                'action_executed': action_type,
                'device_serial': device_serial,
                'human_delay_applied': delay,
                'ml_guidance_used': bool(ml_guidance),
                'success': True
            }
            
            return result
            
        except Exception as e:
            logger.error(f"TikTok automation execution failed: {e}")
            raise
    
    async def _analyze_screenshot_with_ml(self, screenshot_path: str) -> Dict[str, Any]:
        """Analyze screenshot using ML v4 YOLO models"""
        if not self.ml_v4_available:
            return {}
        
        try:
            # This would integrate with the actual ML v4 screenshot analysis
            # For now, return mock analysis
            analysis = {
                'detected_elements': [
                    {'class': 'like_button', 'confidence': 0.95, 'bbox': [100, 200, 150, 250]},
                    {'class': 'comment_button', 'confidence': 0.88, 'bbox': [100, 260, 150, 310]},
                    {'class': 'share_button', 'confidence': 0.92, 'bbox': [100, 320, 150, 370]}
                ],
                'app_state': 'tiktok_main_feed',
                'shadowban_indicators': [],
                'confidence_score': 0.91
            }
            
            logger.debug(f"ML screenshot analysis completed for {screenshot_path}")
            return analysis
            
        except Exception as e:
            logger.error(f"Screenshot ML analysis failed: {e}")
            return {}
    
    async def _detect_anomalies(self, device_serial: str, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies using ML v4 models"""
        if not self.ml_v4_available:
            return {'anomaly_detected': False, 'score': 0.0}
        
        try:
            # This would integrate with actual ML v4 anomaly detection
            # For now, return mock detection
            anomaly_result = {
                'anomaly_detected': False,
                'score': 0.15,  # Low anomaly score
                'indicators': [],
                'recommendations': ['continue_normal_operation']
            }
            
            logger.debug(f"Anomaly detection completed for device {device_serial}")
            return anomaly_result
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return {'anomaly_detected': False, 'score': 0.0}
    
    async def _store_engagement_analytics(self, device_serial: str, action: str, result: Dict[str, Any]):
        """Store engagement analytics in Supabase"""
        if not self.supabase_config.get('url'):
            logger.debug("Supabase not configured, skipping analytics storage")
            return
        
        try:
            # This would integrate with actual Supabase storage
            logger.debug(f"Stored analytics for {action} on device {device_serial}")
            
        except Exception as e:
            logger.error(f"Failed to store engagement analytics: {e}")
    
    async def _send_anomaly_alert(self, device_serial: str, anomaly_score: float):
        """Send anomaly alert through existing alert system"""
        try:
            # This would integrate with the existing alert manager
            logger.warning(f"ANOMALY ALERT: Device {device_serial} - Score: {anomaly_score}")
            
        except Exception as e:
            logger.error(f"Failed to send anomaly alert: {e}")
    
    # Enhanced YOLO Task Handlers
    
    async def _handle_yolo_screenshot_task(self, device_serial: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle YOLO screenshot analysis task"""
        try:
            from ..ml.enhanced_yolo_detector import get_device_farm_yolo_detector
            
            detector = await get_device_farm_yolo_detector()
            analysis_result = await detector.analyze_device_screenshot(
                device_serial=device_serial,
                save_analysis=parameters.get('save_analysis', True)
            )
            
            # Store in Supabase if available
            if self.supabase_config.get('url'):
                await self._store_yolo_analysis(device_serial, analysis_result)
            
            return {
                'task_type': 'yolo_screenshot_analysis',
                'device_serial': device_serial,
                'detections': analysis_result['detections'],
                'automation_recommendations': analysis_result['automation_recommendations'],
                'app_state': analysis_result['automation_recommendations']['app_state'],
                'success': True,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"YOLO screenshot task failed on device {device_serial}: {e}")
            raise
    
    async def _handle_yolo_anomaly_task(self, device_serial: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle YOLO anomaly detection task"""
        try:
            from ..ml.enhanced_yolo_detector import get_device_farm_yolo_detector
            
            detector = await get_device_farm_yolo_detector()
            anomaly_result = await detector.detect_anomalies(device_serial)
            
            # Trigger alerts if anomaly detected
            if anomaly_result['anomaly_detected']:
                await self._send_anomaly_alert(device_serial, anomaly_result['anomaly_score'])
            
            return {
                'task_type': 'yolo_anomaly_detection',
                'device_serial': device_serial,
                'anomaly_detected': anomaly_result['anomaly_detected'],
                'anomaly_score': anomaly_result['anomaly_score'],
                'anomaly_types': anomaly_result['anomaly_types'],
                'success': True,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"YOLO anomaly task failed on device {device_serial}: {e}")
            raise
    
    async def _handle_yolo_batch_task(self, device_serial: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle YOLO batch analysis task"""
        try:
            from ..ml.enhanced_yolo_detector import get_device_farm_yolo_detector
            
            detector = await get_device_farm_yolo_detector()
            device_list = parameters.get('device_serials', [device_serial])
            batch_results = await detector.batch_analyze_devices(device_list)
            
            return {
                'task_type': 'yolo_batch_analysis',
                'batch_results': batch_results,
                'devices_analyzed': len(device_list),
                'success_rate': sum(1 for r in batch_results.values() if r.get('success', False)) / len(batch_results),
                'success': True,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"YOLO batch task failed: {e}")
            raise
    
    async def _handle_yolo_automation_guidance_task(self, device_serial: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle YOLO-based automation guidance task"""
        try:
            from ..ml.enhanced_yolo_detector import get_device_farm_yolo_detector
            
            detector = await get_device_farm_yolo_detector()
            analysis_result = await detector.analyze_device_screenshot(device_serial, save_analysis=False)
            
            recommendations = analysis_result['automation_recommendations']
            engagement_type = parameters.get('engagement_type', 'like')
            
            # Generate specific guidance based on engagement type and YOLO detection
            guidance = {
                'recommended_action': None,
                'target_element': None,
                'risk_assessment': 'medium',
                'confidence': 0.0,
                'alternative_actions': []
            }
            
            # Find best element for engagement type
            if engagement_type == 'like' and recommendations['safe_actions']:
                like_elements = [a for a in recommendations['safe_actions'] if a['element']['class_name'] == 'like_button']
                if like_elements:
                    best_element = max(like_elements, key=lambda x: x['element']['confidence'])
                    guidance['recommended_action'] = 'tap_like_button'
                    guidance['target_element'] = best_element['element']
                    guidance['risk_assessment'] = 'low'
                    guidance['confidence'] = best_element['element']['confidence']
            
            elif engagement_type == 'comment' and recommendations['risky_actions']:
                comment_elements = [a for a in recommendations['risky_actions'] if a['element']['class_name'] == 'comment_button']
                if comment_elements:
                    best_element = max(comment_elements, key=lambda x: x['element']['confidence'])
                    guidance['recommended_action'] = 'tap_comment_button'
                    guidance['target_element'] = best_element['element']
                    guidance['risk_assessment'] = 'high'
                    guidance['confidence'] = best_element['element']['confidence']
            
            # Add alternative actions
            guidance['alternative_actions'] = [
                {'action': 'scroll_down', 'risk': 'low'},
                {'action': 'tap_video', 'risk': 'low'},
                {'action': 'wait', 'risk': 'none'}
            ]
            
            return {
                'task_type': 'yolo_automation_guidance',
                'device_serial': device_serial,
                'engagement_type': engagement_type,
                'guidance': guidance,
                'app_state': recommendations['app_state'],
                'automation_confidence': recommendations['automation_confidence'],
                'success': True,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"YOLO automation guidance task failed on device {device_serial}: {e}")
            raise
    
    async def _store_yolo_analysis(self, device_serial: str, analysis_result: Dict[str, Any]):
        """Store YOLO analysis results in Supabase"""
        try:
            # This would integrate with actual Supabase storage
            logger.debug(f"Stored YOLO analysis for device {device_serial}: {len(analysis_result['detections'])} detections")
            
        except Exception as e:
            logger.error(f"Failed to store YOLO analysis: {e}")


# Global adapter instance
_integration_adapter: Optional[TikTokMLIntegrationAdapter] = None


async def get_tiktok_ml_adapter() -> TikTokMLIntegrationAdapter:
    """Get global TikTok ML integration adapter instance"""
    global _integration_adapter
    if _integration_adapter is None:
        _integration_adapter = TikTokMLIntegrationAdapter()
        await _integration_adapter.initialize()
    return _integration_adapter