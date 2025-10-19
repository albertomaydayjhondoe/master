"""Dummy ADB controller for simulating Android device interactions.

This module provides a lightweight in-memory simulation of connected devices
and actions. Replace with real ADB/Appium integration in production.
"""
from typing import List, Dict, Any
import random
import time


class ADBController:
    def __init__(self):
        # Simulate 10 connected devices by default
        self.devices = {f"device_{i}": {"id": f"device_{i}", "status": "idle"} for i in range(1, 11)}

    def list_devices(self) -> List[Dict[str, Any]]:
        return list(self.devices.values())

    def get_device(self, device_id: str) -> Dict[str, Any]:
        return self.devices.get(device_id)

    def simulate_action(self, device_id: str, action: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        # Simulate latency and a probabilistic success
        time.sleep(random.uniform(0.01, 0.1))
        device = self.devices.get(device_id)
        if device is None:
            return {"success": False, "error": "device_not_found"}

        # Randomly fail small percentage to simulate unreliable network
        if random.random() < 0.02:
            return {"success": False, "error": "transient_error"}

        device["status"] = "active"
        # Return a simulated outcome
        return {
            "success": True,
            "device_id": device_id,
            "action": action,
            "params": params or {},
            "timestamp": time.time(),
        }

    def disconnect_device(self, device_id: str) -> bool:
        if device_id in self.devices:
            self.devices[device_id]["status"] = "disconnected"
            return True
        return False
