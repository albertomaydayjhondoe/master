#!/usr/bin/env bash
set -euo pipefail

# Start the FastAPI app in dummy mode
export DUMMY_MODE=${DUMMY_MODE:-true}
export UVICORN_WORKERS=${UVICORN_WORKERS:-1}

echo "Starting ML API (dummy_mode=${DUMMY_MODE}) on port ${PORT:-8080}..."
exec uvicorn ml_core.api.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers ${UVICORN_WORKERS}
