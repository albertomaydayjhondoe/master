#!/bin/bash
# 🚀 Railway Environment Variables Setup
# Generated automatically for TikTok Viral ML System V3

echo "🚀 Setting up Railway environment variables..."

# Core system variables
railway variables set DUMMY_MODE="false"
railway variables set RAILWAY_ENVIRONMENT="production"
railway variables set PYTHONPATH="."
railway variables set PORT="$PORT"
railway variables set DATABASE_URL="${RAILWAY_DATABASE_URL}"
railway variables set POSTGRES_PASSWORD="railway_postgres_2025"
railway variables set REDIS_URL="${RAILWAY_REDIS_URL}"
railway variables set N8N_USER="admin"
railway variables set N8N_PASSWORD="viral_admin_2025"
railway variables set N8N_ENCRYPTION_KEY="railway_n8n_key_2025"
railway variables set GRAFANA_USER="admin"
railway variables set GRAFANA_PASSWORD="viral_monitor_2025"
railway variables set TELEGRAM_BOT_TOKEN="OPTIONAL - For notifications"
railway variables set TELEGRAM_CHAT_ID="OPTIONAL - For notifications"
railway variables set GOLOGIN_API_KEY="OPTIONAL - For browser automation"
railway variables set GOLOGIN_PROFILE_IDS="OPTIONAL - Comma separated profile IDs"
railway variables set ML_CORE_URL="https://ml-core.railway.app"
railway variables set META_ADS_URL="https://meta-ads.railway.app"
railway variables set YOUTUBE_URL="https://youtube.railway.app"
railway variables set N8N_URL="https://n8n.railway.app"

echo "✅ Basic variables configured!"
echo "⚠️  Configure these REQUIRED variables manually:"
echo "   1. Meta Ads credentials (META_ACCESS_TOKEN, META_AD_ACCOUNT_ID, META_PIXEL_ID)"
echo "   2. YouTube API credentials (YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_CHANNEL_ID)"  
echo "   3. Optional: Telegram notifications (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)"
echo "   4. Optional: GoLogin automation (GOLOGIN_API_KEY, GOLOGIN_PROFILE_IDS)"

echo "🌐 After setting required variables, deploy with:"
echo "   railway up"
