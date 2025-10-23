#!/bin/bash

# Meta Ads Production Setup Script
echo "🚀 Meta Ads Production Setup"
echo "============================"

# Check required environment variables
echo "🔍 Checking environment variables..."

required_vars=("META_APP_ID" "META_APP_SECRET" "META_ACCESS_TOKEN" "META_AD_ACCOUNT_ID" "META_PAGE_ID" "META_PIXEL_ID")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing required environment variable: $var"
        echo "💡 Please set this in your .env file"
        exit 1
    else
        echo "✅ $var is set"
    fi
done

# Install production dependencies
echo "📦 Installing Meta Ads dependencies..."
pip install facebook-business>=18.0.0 requests>=2.31.0

echo "✅ Setup completed!"