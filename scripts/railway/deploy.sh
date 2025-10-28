#!/bin/bash
# Railway Meta Ads-Centric Deployment Script

set -e

echo "Starting Meta Ads-Centric Railway deployment..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
echo "Checking Railway authentication..."
railway login

# Create new project if it doesn't exist
echo "Setting up Railway project..."
railway project new meta-ads-centric --template blank

# Link to project
railway link

# Set environment variables
echo "Setting environment variables..."

# Core variables (you need to provide these)
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set DUMMY_MODE=false

# Database
echo "Setting up database..."
railway add --database postgresql
railway variables set DATABASE_URL='${{DATABASE_URL}}'

# Redis for caching  
echo "Setting up Redis..."
railway add --database redis
railway variables set REDIS_URL='${{REDIS_URL}}'

# Meta Ads (REQUIRED - you need to set these)
echo "Meta Ads configuration (REQUIRED)..."
echo "Please set these manually in Railway dashboard:"
echo "- META_ACCESS_TOKEN"
echo "- META_APP_ID" 
echo "- META_APP_SECRET"
echo "- META_ACCOUNT_ID"
echo "- META_PIXEL_ID"

# YouTube (REQUIRED)
echo "YouTube configuration (REQUIRED)..."
echo "Please set these manually in Railway dashboard:"
echo "- YOUTUBE_API_KEY"
echo "- YOUTUBE_CLIENT_ID"
echo "- YOUTUBE_CLIENT_SECRET"

# TikTok (OPTIONAL)
echo "TikTok configuration (OPTIONAL)..."
echo "Set these if you have TikTok API access:"
echo "- TIKTOK_CLIENT_KEY"
echo "- TIKTOK_CLIENT_SECRET" 
echo "- TIKTOK_ACCESS_TOKEN"

# Instagram (OPTIONAL)
echo "Instagram configuration (OPTIONAL)..."
echo "Set these if you have Instagram API access:"
echo "- INSTAGRAM_ACCESS_TOKEN"
echo "- INSTAGRAM_BUSINESS_ACCOUNT_ID"

# Twitter (OPTIONAL) 
echo "Twitter configuration (OPTIONAL)..."
echo "Set these if you have Twitter API access:"
echo "- TWITTER_API_KEY"
echo "- TWITTER_API_SECRET"
echo "- TWITTER_ACCESS_TOKEN" 
echo "- TWITTER_ACCESS_TOKEN_SECRET"

# OpenAI (RECOMMENDED)
echo "OpenAI configuration (RECOMMENDED)..."
echo "Set this for enhanced ML capabilities:"
echo "- OPENAI_API_KEY"

# Security
railway variables set JWT_SECRET_KEY=$(openssl rand -base64 32)
railway variables set API_SECRET_KEY=$(openssl rand -base64 32)
railway variables set META_WEBHOOK_VERIFY_TOKEN=$(openssl rand -base64 16)

# Service URLs (automatic)
railway variables set ML_CORE_URL=http://ml-core:8000
railway variables set META_ADS_URL=http://meta-ads-manager:9000
railway variables set YOUTUBE_UPLOADER_URL=http://youtube-uploader:8001
railway variables set UNIFIED_ORCHESTRATOR_URL=http://unified-orchestrator:10000
railway variables set WEBHOOK_BASE_URL='${{RAILWAY_STATIC_URL}}'

# Deploy
echo "Deploying to Railway..."
railway up

echo "Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Set your API keys in Railway dashboard"
echo "2. Configure Meta Ads webhooks to point to your Railway URL"
echo "3. Test with a sample campaign"
echo ""
echo "Railway URL: $(railway status --json | jq -r '.deployments[0].url')"
echo ""
echo "Your Meta Ads-Centric system is ready!"
