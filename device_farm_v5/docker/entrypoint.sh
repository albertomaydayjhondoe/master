#!/bin/bash
# Device Farm v5 - Docker Entrypoint Script
# Handles initialization of services and USB device access

set -e

echo "🚀 Starting Device Farm v5..."

# Check for required environment variables
if [ -z "$GOLOGIN_API_TOKEN" ]; then
    echo "⚠️  Warning: GOLOGIN_API_TOKEN not set"
fi

# Ensure required directories exist
mkdir -p /app/data /app/logs /app/screenshots

# Initialize database
echo "📊 Initializing database..."
python3 -c "
from src.core.models import get_db_manager
try:
    db_manager = get_db_manager()
    print('✅ Database initialized successfully')
except Exception as e:
    print(f'❌ Database initialization failed: {e}')
    exit(1)
"

# Check ADB connectivity
echo "📱 Checking ADB connectivity..."
adb devices -l || echo "⚠️  No devices detected (this is normal if no devices are connected)"

# Check Appium installation
echo "🤖 Checking Appium installation..."
appium --version || echo "⚠️  Appium not found"

# Start services based on mode
if [ "$1" = "dashboard-only" ]; then
    echo "🎛️  Starting dashboard only..."
    exec python3 -m src.dashboard.app
elif [ "$1" = "worker-only" ]; then
    echo "⚙️  Starting worker only..."
    exec python3 -m src.core.worker
elif [ "$1" = "dev" ]; then
    echo "🔧 Starting in development mode..."
    export DEBUG=true
    exec python3 -m src.main
else
    echo "🚀 Starting full system..."
    exec python3 -m src.main
fi