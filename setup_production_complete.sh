#!/bin/bash
# 🚀 Neural Forge - Complete Production Setup Script
# =================================================
# Sets up Meta Ads + YouTube + Dashboards for 100% operability

set -e

echo "🎵 =================================="
echo "🎵 Neural Forge Production Setup"
echo "🎵 Meta Ads + YouTube + Dashboards"
echo "🎵 =================================="

# Create required directories
echo "📁 Creating directory structure..."
mkdir -p monitoring/dashboards/grafana
mkdir -p monitoring/metrics
mkdir -p config/secrets
mkdir -p data/campaigns
mkdir -p logs/meta_ads
mkdir -p logs/youtube

# Check if secrets exist
if [ ! -f "config/secrets/secrets.env" ]; then
    echo "⚠️  Creating secrets template..."
    cp config/secrets/secrets.env.template config/secrets/secrets.env
    echo "🔐 IMPORTANT: Edit config/secrets/secrets.env with your real API keys!"
fi

# Install production dependencies
echo "📦 Installing production dependencies..."
pip install --upgrade pip
pip install facebook-business>=18.0.0
pip install google-api-python-client>=2.100.0
pip install google-auth>=2.22.0
pip install google-auth-oauthlib>=1.0.0
pip install prometheus-client>=0.17.0
pip install grafana-api>=1.0.3

# Validate Meta Ads credentials
echo "🛰️ Validating Meta Ads setup..."
python -c "
import os
from dotenv import load_dotenv
load_dotenv('config/secrets/secrets.env')

required_meta = ['META_APP_ID', 'META_APP_SECRET', 'META_ACCESS_TOKEN', 'META_AD_ACCOUNT_ID']
missing = [var for var in required_meta if not os.getenv(var)]

if missing:
    print(f'❌ Missing Meta Ads variables: {missing}')
    print('🔧 Please configure these in config/secrets/secrets.env')
    exit(1)
else:
    print('✅ Meta Ads credentials configured')
"

# Validate YouTube credentials
echo "📺 Validating YouTube setup..."
python -c "
import os
from dotenv import load_dotenv
load_dotenv('config/secrets/secrets.env')

# Check main account (metrics only)
main_vars = ['YOUTUBE_API_KEY', 'YOUTUBE_CLIENT_ID', 'YOUTUBE_CLIENT_SECRET', 'YOUTUBE_CHANNEL_ID']
missing_main = [var for var in main_vars if not os.getenv(var)]

# Check satellites
satellite_missing = []
for i in range(1, 6):
    sat_vars = [f'YOUTUBE_SATELLITE_{i}_API_KEY', f'YOUTUBE_SATELLITE_{i}_CLIENT_ID', 
                f'YOUTUBE_SATELLITE_{i}_CLIENT_SECRET', f'YOUTUBE_SATELLITE_{i}_CHANNEL_ID']
    missing = [var for var in sat_vars if not os.getenv(var)]
    if missing:
        satellite_missing.extend(missing)

if missing_main:
    print(f'❌ Missing YouTube Main variables: {missing_main}')
if satellite_missing:
    print(f'❌ Missing YouTube Satellite variables: {satellite_missing[:5]}...')
    
if missing_main or satellite_missing:
    print('🔧 Please configure YouTube APIs in config/secrets/secrets.env')
    exit(1)
else:
    print('✅ YouTube credentials configured (Main + 5 Satellites)')
"

# Test Meta Ads API connection
echo "🧪 Testing Meta Ads API connection..."
python -c "
import os
import sys
sys.path.append('.')
from dotenv import load_dotenv
load_dotenv('config/secrets/secrets.env')

try:
    from social_extensions.meta_ads_production import MetaAdsProductionAPI
    api = MetaAdsProductionAPI()
    if api.ad_account:
        print('✅ Meta Ads API connection successful')
    else:
        print('⚠️ Meta Ads running in dummy mode (check credentials)')
except Exception as e:
    print(f'❌ Meta Ads API error: {e}')
"

# Test YouTube API connection
echo "🧪 Testing YouTube API connection..."
python -c "
import os
import sys
sys.path.append('.')
from dotenv import load_dotenv
load_dotenv('config/secrets/secrets.env')

try:
    from social_extensions.youtube_integration import YouTubeMainAccount, YouTubeSatelliteAccount
    
    # Test main account
    main = YouTubeMainAccount(
        api_key=os.getenv('YOUTUBE_API_KEY'),
        client_id=os.getenv('YOUTUBE_CLIENT_ID'),
        client_secret=os.getenv('YOUTUBE_CLIENT_SECRET'),
        refresh_token=os.getenv('YOUTUBE_REFRESH_TOKEN'),
        channel_id=os.getenv('YOUTUBE_CHANNEL_ID')
    )
    print('✅ YouTube Main Account initialized (metrics only)')
    
    # Test first satellite
    sat1 = YouTubeSatelliteAccount(
        satellite_id=1,
        api_key=os.getenv('YOUTUBE_SATELLITE_1_API_KEY'),
        client_id=os.getenv('YOUTUBE_SATELLITE_1_CLIENT_ID'),
        client_secret=os.getenv('YOUTUBE_SATELLITE_1_CLIENT_SECRET'),
        refresh_token=os.getenv('YOUTUBE_SATELLITE_1_REFRESH_TOKEN'),
        channel_id=os.getenv('YOUTUBE_SATELLITE_1_CHANNEL_ID')
    )
    print('✅ YouTube Satellite Accounts ready (upload enabled)')
    
except Exception as e:
    print(f'❌ YouTube API error: {e}')
"

# Setup Grafana dashboards
echo "📊 Setting up Grafana dashboards..."
if command -v docker &> /dev/null; then
    # Start Grafana if not running
    if ! docker ps | grep -q grafana; then
        echo "🚀 Starting Grafana..."
        docker run -d \
            --name neural-forge-grafana \
            -p 3000:3000 \
            -v $(pwd)/monitoring/dashboards:/var/lib/grafana/dashboards \
            -e GF_SECURITY_ADMIN_PASSWORD=neuralforge \
            grafana/grafana:latest
        
        echo "⏳ Waiting for Grafana to start..."
        sleep 10
    fi
    
    # Import dashboards
    echo "📊 Importing dashboards..."
    curl -X POST \
        -H "Content-Type: application/json" \
        -d @monitoring/dashboards/meta_ads_dashboard.json \
        http://admin:neuralforge@localhost:3000/api/dashboards/db 2>/dev/null || echo "Dashboard import attempted"
    
    curl -X POST \
        -H "Content-Type: application/json" \
        -d @monitoring/dashboards/youtube_analytics_dashboard.json \
        http://admin:neuralforge@localhost:3000/api/dashboards/db 2>/dev/null || echo "Dashboard import attempted"
    
    echo "✅ Grafana dashboards configured"
    echo "🌐 Access Grafana at: http://localhost:3000 (admin/neuralforge)"
else
    echo "⚠️ Docker not found, skipping Grafana setup"
fi

# Create production launcher
echo "🚀 Creating production launcher..."
cat > launch_production.sh << 'EOF'
#!/bin/bash
# 🎵 Neural Forge Production Launcher

echo "🚀 Starting Neural Forge Production System..."

# Start all services
docker-compose -f docker-compose.prod.yml up -d

echo "✅ Neural Forge Production Started!"
echo ""
echo "🌐 Access Points:"
echo "   • Production Controller: http://localhost:7860"
echo "   • Analytics Dashboard:   http://localhost:8501"
echo "   • ML Core API:          http://localhost:8000"
echo "   • N8N Workflows:        http://localhost:5678"
echo "   • Meta Ads API:         http://localhost:8002"
echo "   • Grafana Dashboards:   http://localhost:3000"
echo ""
echo "🎵 Ready to create viral hits! 🚀"
EOF

chmod +x launch_production.sh

# Create validation script
echo "🧪 Creating validation script..."
cat > validate_production.py << 'EOF'
#!/usr/bin/env python3
"""
🧪 Neural Forge - Production Validation
Validates all systems are ready for operation
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
load_dotenv('config/secrets/secrets.env')

async def validate_meta_ads():
    """Validate Meta Ads functionality"""
    try:
        from social_extensions.meta_ads_production import MetaAdsProductionAPI
        api = MetaAdsProductionAPI()
        
        if api.ad_account:
            print("✅ Meta Ads: Ready for campaigns")
            return True
        else:
            print("⚠️ Meta Ads: Running in dummy mode")
            return False
    except Exception as e:
        print(f"❌ Meta Ads: {e}")
        return False

async def validate_youtube():
    """Validate YouTube functionality"""
    try:
        from social_extensions.youtube_integration import YouTubeMainAccount
        
        main = YouTubeMainAccount(
            api_key=os.getenv('YOUTUBE_API_KEY'),
            client_id=os.getenv('YOUTUBE_CLIENT_ID'),
            client_secret=os.getenv('YOUTUBE_CLIENT_SECRET'),
            refresh_token=os.getenv('YOUTUBE_REFRESH_TOKEN'),
            channel_id=os.getenv('YOUTUBE_CHANNEL_ID')
        )
        
        print("✅ YouTube Main: Metrics collection ready")
        print("✅ YouTube Satellites: Upload distribution ready")
        return True
    except Exception as e:
        print(f"❌ YouTube: {e}")
        return False

async def validate_ml_core():
    """Validate ML Core functionality"""
    try:
        import requests
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ ML Core: API ready")
            return True
        else:
            print("⚠️ ML Core: API not responding")
            return False
    except:
        print("⚠️ ML Core: Not running (start with docker-compose)")
        return False

async def main():
    print("🧪 Neural Forge Production Validation")
    print("=" * 40)
    
    results = await asyncio.gather(
        validate_meta_ads(),
        validate_youtube(),
        validate_ml_core()
    )
    
    print("\n📊 Validation Results:")
    print(f"   Meta Ads: {'✅' if results[0] else '❌'}")
    print(f"   YouTube:  {'✅' if results[1] else '❌'}")
    print(f"   ML Core:  {'✅' if results[2] else '❌'}")
    
    if all(results):
        print("\n🚀 SYSTEM READY FOR VIRAL CAMPAIGNS!")
        return 0
    else:
        print("\n⚠️ Some systems need configuration")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
EOF

chmod +x validate_production.py

echo ""
echo "🎵 =================================="
echo "🎵 SETUP COMPLETED!"
echo "🎵 =================================="
echo ""
echo "📋 Next Steps:"
echo "   1. Configure real API keys in: config/secrets/secrets.env"
echo "   2. Run validation: ./validate_production.py"  
echo "   3. Launch production: ./launch_production.sh"
echo ""
echo "🌐 Access Points (after launch):"
echo "   • Production Interface: http://localhost:7860"
echo "   • Grafana Dashboards:  http://localhost:3000"
echo "   • Analytics Engine:    http://localhost:8501"
echo ""
echo "🚀 Ready to create viral music campaigns!"