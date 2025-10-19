from typing import Dict, Any, List
from .adb_controller import ADBController
import threading
import time


class DeviceManager:
    def __init__(self):
        self.adb = ADBController()
        self._lock = threading.Lock()

    def list(self) -> List[Dict[str, Any]]:
        return self.adb.list_devices()

    def perform_action(self, device_id: str, action: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        with self._lock:
            # In real system, we'd schedule actions; in dummy mode we directly call simulate
            return self.adb.simulate_action(device_id, action, params)

    def broadcast(self, action: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        results = {}
        for dev in self.list():
            results[dev["id"]] = self.perform_action(dev["id"], action, params)
        return results

    def health_check(self) -> Dict[str, Any]:
        devices = self.list()
        healthy = [d for d in devices if d.get("status") != "disconnected"]
        return {"total": len(devices), "healthy": len(healthy), "timestamp": time.time()}
