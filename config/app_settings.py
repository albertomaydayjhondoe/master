"""Runtime settings for toggling dummy vs production implementations.

Use the environment variable `DUMMY_MODE` to control behavior. When
`DUMMY_MODE=true` (default in this repo), the system uses lightweight
dummy stubs. To switch to production implementations, set
`DUMMY_MODE=false` and provide real implementations for the factories.
"""
import os
from pathlib import Path

# Auto-load .env file if exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment from: {env_path}")
except ImportError:
    pass  # dotenv not installed


def is_dummy_mode() -> bool:
    v = os.getenv("DUMMY_MODE", "true").lower()
    return v in ("1", "true", "yes", "on")


def get_env(name: str, default: str = None) -> str:
    return os.getenv(name, default)
