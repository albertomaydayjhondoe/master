"""
Device Farm v5 - Web Dashboard
Flask-based web interface for monitoring and controlling the device farm
"""
import asyncio
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import threading
from typing import Dict, Any, List

from ..config_manager import get_config
from ..core.adb_manager import get_adb_manager
from ..integrations.gologin_manager import get_gologin_manager
from ..core.appium_controller import get_appium_controller
from ..core.profile_synchronizer import get_profile_synchronizer
from ..core.task_queue import get_task_queue, create_task_definition, TaskPriority
from ..core.models import get_db_session, Device, GologinProfile, Task

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'device-farm-v5-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global references
config = None
loop = None


def run_async(coro):
    """Run async function in the main event loop"""
    global loop
    if loop and loop.is_running():
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        return future.result(timeout=30)
    else:
        return asyncio.run(coro)


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/devices')
def devices_page():
    """Devices management page"""
    return render_template('devices.html')


@app.route('/tasks')
def tasks_page():
    """Tasks management page"""
    return render_template('tasks.html')


@app.route('/profiles')
def profiles_page():
    """Gologin profiles page"""
    return render_template('profiles.html')


# API Routes

@app.route('/api/status')
def api_status():
    """Get system status"""
    try:
        # Get device stats
        adb_manager = run_async(get_adb_manager())
        devices = run_async(adb_manager.scan_devices())
        
        online_devices = sum(1 for d in devices if d.status == 'online')
        
        # Get task queue stats
        task_queue = run_async(get_task_queue())
        queue_stats = run_async(task_queue.get_queue_statistics())
        
        # Get profile synchronizer stats
        synchronizer = run_async(get_profile_synchronizer())
        sync_stats = run_async(synchronizer.get_synchronizer_statistics())
        
        return jsonify({
            'status': 'running',
            'devices': {
                'total': len(devices),
                'online': online_devices,
                'offline': len(devices) - online_devices
            },
            'tasks': {
                'active': queue_stats['active_tasks'],
                'queued': sum(queue_stats['queued_tasks'].values())
            },
            'profiles': {
                'synced': sync_stats['synced_mappings'],
                'total': sync_stats['total_mappings']
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/devices')
def api_devices():
    """Get devices list"""
    try:
        session = get_db_session()
        devices = session.query(Device).all()
        
        device_list = []
        for device in devices:
            device_data = {
                'serial': device.serial,
                'status': device.status,
                'model': device.model,
                'android_version': device.android_version,
                'assigned_profile': device.assigned_profile,
                'proxy_host': device.proxy_host,
                'proxy_port': device.proxy_port,
                'last_seen': device.last_seen.isoformat() if device.last_seen else None,
                'created_at': device.created_at.isoformat() if device.created_at else None
            }
            device_list.append(device_data)
        
        session.close()
        
        return jsonify({'devices': device_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/devices/scan', methods=['POST'])
def api_scan_devices():
    """Trigger device scan"""
    try:
        adb_manager = run_async(get_adb_manager())
        devices = run_async(adb_manager.scan_devices())
        
        return jsonify({
            'message': f'Scanned {len(devices)} devices',
            'devices': [{'serial': d.serial, 'status': d.status} for d in devices]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/devices/<device_serial>/assign_profile', methods=['POST'])
def api_assign_profile(device_serial):
    """Assign profile to device"""
    try:
        data = request.get_json() or {}
        profile_id = data.get('profile_id')
        
        synchronizer = run_async(get_profile_synchronizer())
        success = run_async(synchronizer.assign_profile_to_device(device_serial, profile_id))
        
        if success:
            return jsonify({'message': f'Profile assigned to device {device_serial}'})
        else:
            return jsonify({'error': 'Failed to assign profile'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/devices/<device_serial>/unassign_profile', methods=['POST'])
def api_unassign_profile(device_serial):
    """Unassign profile from device"""
    try:
        synchronizer = run_async(get_profile_synchronizer())
        success = run_async(synchronizer.unassign_profile_from_device(device_serial))
        
        if success:
            return jsonify({'message': f'Profile unassigned from device {device_serial}'})
        else:
            return jsonify({'error': 'Failed to unassign profile'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/profiles')
def api_profiles():
    """Get Gologin profiles"""
    try:
        session = get_db_session()
        profiles = session.query(GologinProfile).all()
        
        profile_list = []
        for profile in profiles:
            profile_data = {
                'id': profile.id,
                'gologin_id': profile.gologin_id,
                'name': profile.name,
                'status': profile.status,
                'proxy_host': profile.proxy_host,
                'proxy_port': profile.proxy_port,
                'last_used': profile.last_used.isoformat() if profile.last_used else None,
                'created_at': profile.created_at.isoformat() if profile.created_at else None
            }
            profile_list.append(profile_data)
        
        session.close()
        
        return jsonify({'profiles': profile_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/profiles/sync', methods=['POST'])
def api_sync_profiles():
    """Sync profiles from Gologin"""
    try:
        gologin_manager = run_async(get_gologin_manager())
        profiles = run_async(gologin_manager.get_available_profiles())
        
        return jsonify({
            'message': f'Synced {len(profiles)} profiles',
            'profiles': [p.to_dict() for p in profiles]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks')
def api_tasks():
    """Get tasks list"""
    try:
        session = get_db_session()
        
        # Get recent tasks (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        tasks = session.query(Task).filter(
            Task.created_at > cutoff_time
        ).order_by(Task.created_at.desc()).limit(100).all()
        
        task_list = []
        for task in tasks:
            task_data = {
                'id': task.id,
                'task_type': task.task_type,
                'priority': task.priority,
                'status': task.status,
                'device_serial': task.device_serial,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'started_at': task.started_at.isoformat() if task.started_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'retry_count': task.retry_count,
                'error_message': task.error_message
            }
            task_list.append(task_data)
        
        session.close()
        
        return jsonify({'tasks': task_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks', methods=['POST'])
def api_create_task():
    """Create new task"""
    try:
        data = request.get_json()
        
        task_def = create_task_definition(
            task_type=data['task_type'],
            parameters=data.get('parameters', {}),
            priority=TaskPriority(data.get('priority', TaskPriority.NORMAL.value)),
            device_requirements=data.get('device_requirements', {}),
            timeout_seconds=data.get('timeout_seconds', 300),
            max_retries=data.get('max_retries', 3)
        )
        
        task_queue = run_async(get_task_queue())
        task_id = run_async(task_queue.submit_task(task_def))
        
        return jsonify({
            'message': 'Task created successfully',
            'task_id': task_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks/<task_id>/cancel', methods=['POST'])
def api_cancel_task(task_id):
    """Cancel task"""
    try:
        task_queue = run_async(get_task_queue())
        success = run_async(task_queue.cancel_task(task_id))
        
        if success:
            return jsonify({'message': f'Task {task_id} cancelled'})
        else:
            return jsonify({'error': 'Failed to cancel task'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sync/all', methods=['POST'])
def api_sync_all():
    """Sync all devices with profiles"""
    try:
        synchronizer = run_async(get_profile_synchronizer())
        results = run_async(synchronizer.sync_all_devices())
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        return jsonify({
            'message': f'Sync completed: {successful}/{total} devices synced successfully',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# YOLO Analysis API Endpoints

@app.route('/api/yolo/analyze/<device_serial>', methods=['POST'])
def api_yolo_analyze_device(device_serial):
    """Analyze device screenshot with YOLO"""
    try:
        from ..ml.enhanced_yolo_detector import get_device_farm_yolo_detector
        
        detector = run_async(get_device_farm_yolo_detector())
        analysis_result = run_async(detector.analyze_device_screenshot(device_serial))
        
        return jsonify({
            'message': f'YOLO analysis completed for device {device_serial}',
            'analysis': {
                'detections': analysis_result['detections'],
                'detection_count': analysis_result['detection_count'],
                'app_state': analysis_result['automation_recommendations']['app_state'],
                'automation_confidence': analysis_result['automation_recommendations']['automation_confidence'],
                'safe_actions': len(analysis_result['automation_recommendations']['safe_actions']),
                'risky_actions': len(analysis_result['automation_recommendations']['risky_actions'])
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/yolo/anomaly/<device_serial>', methods=['POST'])
def api_yolo_anomaly_check(device_serial):
    """Check for anomalies using YOLO"""
    try:
        from ..ml.enhanced_yolo_detector import get_device_farm_yolo_detector
        
        detector = run_async(get_device_farm_yolo_detector())
        anomaly_result = run_async(detector.detect_anomalies(device_serial))
        
        return jsonify({
            'message': f'Anomaly check completed for device {device_serial}',
            'anomaly_detected': anomaly_result['anomaly_detected'],
            'anomaly_score': anomaly_result['anomaly_score'],
            'anomaly_types': anomaly_result.get('anomaly_types', []),
            'recommendations': anomaly_result.get('recommendations', [])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/yolo/batch_analyze', methods=['POST'])
def api_yolo_batch_analyze():
    """Batch analyze multiple devices with YOLO"""
    try:
        data = request.get_json()
        device_serials = data.get('device_serials', [])
        
        if not device_serials:
            return jsonify({'error': 'No device serials provided'}), 400
        
        from ..ml.enhanced_yolo_detector import get_device_farm_yolo_detector
        
        detector = run_async(get_device_farm_yolo_detector())
        batch_results = run_async(detector.batch_analyze_devices(device_serials))
        
        successful = sum(1 for r in batch_results.values() if r.get('success', False))
        
        return jsonify({
            'message': f'Batch analysis completed: {successful}/{len(device_serials)} successful',
            'results': batch_results,
            'success_rate': successful / len(device_serials) if device_serials else 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/yolo/model_info')
def api_yolo_model_info():
    """Get YOLO model information"""
    try:
        from ..ml.enhanced_yolo_detector import get_device_farm_yolo_detector
        
        detector = run_async(get_device_farm_yolo_detector())
        model_info = detector.get_model_info()
        
        return jsonify(model_info)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/yolo/create_task', methods=['POST'])
def api_yolo_create_task():
    """Create YOLO analysis task"""
    try:
        data = request.get_json()
        
        task_type = data.get('task_type', 'yolo_screenshot_analysis')
        device_serial = data.get('device_serial')
        parameters = data.get('parameters', {})
        
        if not device_serial:
            return jsonify({'error': 'Device serial required'}), 400
        
        from ..core.task_queue import get_task_queue, create_task_definition, TaskPriority
        
        task_def = create_task_definition(
            task_type=task_type,
            parameters={
                'device_serial': device_serial,
                **parameters
            },
            priority=TaskPriority.HIGH,  # YOLO tasks have high priority
            timeout_seconds=data.get('timeout_seconds', 120)
        )
        
        task_queue = run_async(get_task_queue())
        task_id = run_async(task_queue.submit_task(task_def))
        
        return jsonify({
            'message': f'YOLO task created successfully',
            'task_id': task_id,
            'task_type': task_type,
            'device_serial': device_serial
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# WebSocket events

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connected', {'data': 'Connected to Device Farm v5 Dashboard'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


@socketio.on('request_status')
def handle_status_request():
    """Handle status request via WebSocket"""
    try:
        # Get system status (same as API)
        status_data = api_status().get_json()
        emit('status_update', status_data)
    except Exception as e:
        emit('error', {'message': str(e)})


def start_dashboard(host='127.0.0.1', port=5000, debug=False):
    """Start the Flask dashboard"""
    global config, loop
    
    config = get_config()
    
    # Get the current event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    print(f"Starting Device Farm v5 Dashboard on http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug)


if __name__ == '__main__':
    start_dashboard(debug=True)