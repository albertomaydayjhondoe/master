"""Dummy GoLogin API wrapper.

Simulates creation and management of browser profiles. Production code should
wrap the real GoLogin HTTP API.
"""
from typing import Dict, Any, List
import uuid
import time


class GoLoginClient:
    def __init__(self):
        # In-memory store of profiles
        self.profiles: Dict[str, Dict[str, Any]] = {}

    def create_profile(self, name: str, fingerprint: Dict[str, Any] = None) -> Dict[str, Any]:
        pid = str(uuid.uuid4())
        profile = {
            "id": pid,
            "name": name,
            "fingerprint": fingerprint or {"locale": "es-ES"},
            "created_at": time.time(),
            "status": "stopped",
        }
        self.profiles[pid] = profile
        return profile

    def list_profiles(self) -> List[Dict[str, Any]]:
        return list(self.profiles.values())

    def start_profile(self, profile_id: str) -> Dict[str, Any]:
        p = self.profiles.get(profile_id)
        if not p:
            raise KeyError("profile_not_found")
        p["status"] = "running"
        p["last_started"] = time.time()
        return p

    def stop_profile(self, profile_id: str) -> Dict[str, Any]:
        p = self.profiles.get(profile_id)
        if not p:
            raise KeyError("profile_not_found")
        p["status"] = "stopped"
        p["last_stopped"] = time.time()
        return p
