#!/bin/bash

# Telegram Automation Dependency Installer
# Installs required packages for Like4Like automation

set -e

echo "🔧 Installing Telegram Automation Dependencies"
echo "=============================================="

# Check if we're in dummy mode
DUMMY_MODE=${DUMMY_MODE:-true}

if [ "$DUMMY_MODE" = "true" ]; then
    echo "🎭 DUMMY MODE: Installing minimal dependencies only"
    
    # Install only essential packages
    pip install -q python-dotenv pyyaml colorlog asyncio-mqtt
    
    echo "✅ Minimal dependencies installed for dummy mode"
    echo "ℹ️  To install full dependencies, set DUMMY_MODE=false and run again"
    
else
    echo "🚀 PRODUCTION MODE: Installing all dependencies"
    
    # Check if Chrome is installed (required for Selenium)
    if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null; then
        echo "⚠️  Chrome/Chromium not found. Installing..."
        
        # Install Chrome
        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
        apt-get update -qq
        apt-get install -y -qq google-chrome-stable
        
        echo "✅ Chrome installed"
    fi
    
    # Install ChromeDriver
    echo "📦 Installing ChromeDriver..."
    pip install -q webdriver-manager
    
    # Install all required packages
    echo "📦 Installing Python packages..."
    
    if [ -f "requirements-full.txt" ]; then
        pip install -q -r requirements-full.txt
    else
        # Fallback to individual packages
        pip install -q telethon selenium asyncpg aiohttp python-dotenv pyyaml colorlog
    fi
    
    # Verify installations
    echo "🔍 Verifying installations..."
    
    python3 -c "
import sys
packages = ['telethon', 'selenium', 'asyncpg', 'aiohttp']
missing = []
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg} - OK')
    except ImportError:
        missing.append(pkg)
        print(f'❌ {pkg} - MISSING')

if missing:
    print(f'⚠️  Missing packages: {missing}')
    sys.exit(1)
else:
    print('🎉 All packages verified successfully!')
    "
fi

echo ""
echo "🎯 Setup complete!"
echo "💡 Usage:"
echo "   DUMMY_MODE=true  python3 main.py  # Development mode"
echo "   DUMMY_MODE=false python3 main.py  # Production mode"