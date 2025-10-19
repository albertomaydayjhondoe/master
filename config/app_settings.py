"""Runtime settings for toggling dummy vs production implementations.

Use the environment variable `DUMMY_MODE` to control behavior. When
`DUMMY_MODE=true` (default in this repo), the system uses lightweight
dummy stubs. To switch to production implementations, set
`DUMMY_MODE=false` and provide real implementations for the factories.
"""
import os


def is_dummy_mode() -> bool:
    v = os.getenv("DUMMY_MODE", "true").lower()
    return v in ("1", "true", "yes", "on")


def get_env(name: str, default: str = None) -> str:
    return os.getenv(name, default)
