# 🚀 Docker v2.0 - Meta Ads to YouTube Marketing Funnel
## Complete Implementation Guide

---

## 📋 TABLE OF CONTENTS

1. [Architecture Overview](#architecture-overview)
2. [Services Description](#services-description)
3. [Setup Guide](#setup-guide)
4. [Configuration](#configuration)
5. [Deployment](#deployment)
6. [API Documentation](#api-documentation)
7. [Workflow Automation](#workflow-automation)
8. [Monitoring & Analytics](#monitoring--analytics)
9. [Cost Analysis](#cost-analysis)
10. [Troubleshooting](#troubleshooting)

---

## 🏗️ ARCHITECTURE OVERVIEW

### System Flow

```
┌────────────────────────────────────────────────────────────────┐
│                    DOCKER V2.0 ARCHITECTURE                     │
│          Meta Ads → Pixeles → Landing Pages → YouTube          │
└────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  1. META ADS MANAGER (Port 9000)                                │
│     - Create/manage campaigns                                   │
│     - Audience targeting                                        │
│     - Budget optimization                                       │
│     - A/B testing automation                                    │
│     └──▶ Drives traffic to Landing Pages                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. LANDING PAGE OPTIMIZER (Port 9002)                          │
│     - High-converting templates                                 │
│     - A/B testing                                               │
│     - ML personalization                                        │
│     - Speed optimization                                        │
│     └──▶ Tracks with Facebook Pixel                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. PIXEL TRACKER (Port 9001)                                   │
│     - PageView tracking                                         │
│     - Conversion events                                         │
│     - Custom events (Spotify click, YouTube click)              │
│     - Custom Audience building                                  │
│     └──▶ Sends data to Meta Conversion API                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. USER ACTIONS                                                │
│     - Click Spotify link → Track "SpotifyClick"                 │
│     - Click YouTube link → Track "YouTubeClick"                 │
│     - Watch video 75% → Track "VideoWatch75"                    │
│     - Submit email → Track "Lead"                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. YOUTUBE UPLOADER (Port 9003)                                │
│     - Automated video upload                                    │
│     - Metadata optimization (SEO)                               │
│     - Thumbnail generation                                      │
│     - Analytics tracking                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. ML PREDICTOR (Port 9004)                                    │
│     - Predict best ad creatives                                 │
│     - Optimize budget allocation                                │
│     - Predict conversion rates                                  │
│     - Audience interest prediction                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  7. ANALYTICS DASHBOARD (Port 9005)                             │
│     - Real-time metrics                                         │
│     - ROI tracking                                              │
│     - Campaign performance                                      │
│     - Alerts & notifications                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  8. AUTOMATION ORCHESTRATOR (Port 9006)                         │
│     - Workflow coordination                                     │
│     - Auto-pause low performers                                 │
│     - Auto-boost high performers                                │
│     - Budget scaling                                            │
└─────────────────────────────────────────────────────────────────┘

SUPPORTING SERVICES:
├─ PostgreSQL (Port 5433): Campaign data, metrics, conversions
├─ Redis (Port 6380): Caching, queues, real-time data
└─ Nginx (Ports 8080/8443): Reverse proxy, SSL, static files
```

---

## 🎯 SERVICES DESCRIPTION

### 1. Meta Ads Manager (`meta-ads-manager:9000`)

**Purpose:** Complete Meta Ads campaign management

**Features:**
- Create campaigns with automatic setup
- Manage ad sets with ML-powered targeting
- Create ad creatives
- Get real-time insights
- Automatic optimization (pause/boost/scale)

**Key Endpoints:**
```bash
POST /campaigns/create          # Create new campaign
POST /adsets/create             # Create ad set
POST /ads/create                # Create ad
GET  /campaigns/{id}/insights   # Get performance data
POST /campaigns/{id}/optimize   # Auto-optimize campaign
POST /quick-campaign            # One-click campaign setup
```

**Example Quick Campaign:**
```bash
curl -X POST http://localhost:9000/quick-campaign \
  -H "Content-Type: application/json" \
  -d '{
    "artist_name": "Stakas",
    "song_name": "Nueva Vida",
    "landing_url": "https://your-domain.com/stakas",
    "daily_budget": 50.0,
    "target_countries": ["US", "MX", "ES"]
  }'
```

---

### 2. Pixel Tracker (`pixel-tracker:9001`)

**Purpose:** Track conversions and build custom audiences

**Features:**
- Facebook Pixel implementation
- Conversion API integration
- Custom event tracking
- Privacy-compliant (SHA-256 hashing)

**Key Endpoints:**
```bash
POST /track/pageview      # Track page views
POST /track/viewcontent   # Track content views (song page)
POST /track/lead          # Track leads (email signup)
POST /track/custom        # Track custom events
GET  /pixel/snippet       # Get pixel JavaScript code
GET  /pixel/music-events  # Get music-specific tracking code
```

**Custom Events for Music:**
- `SpotifyClick`: User clicks Spotify link
- `YouTubeClick`: User clicks YouTube link
- `AppleMusicClick`: User clicks Apple Music link
- `VideoWatch75`: User watches video 75%
- `SocialFollow`: User follows social media

---

### 3. Landing Page Optimizer (`landing-optimizer:9002`)

**Purpose:** High-converting landing pages with A/B testing

**Features:**
- Pre-built music artist templates
- A/B testing automation
- ML-powered personalization
- Heatmap tracking
- Speed optimization (lazy loading, compression)

**Templates Available:**
- `music_artist_v1`: Single artist page
- `new_release_v1`: New song release
- `pre_save_v1`: Pre-save campaign
- `tour_dates_v1`: Concert tour promotion

**Admin Dashboard:** `http://localhost:9012`

---

### 4. YouTube Uploader (`youtube-uploader:9003`)

**Purpose:** Automated YouTube video management

**Features:**
- Automated video upload
- Metadata optimization (SEO-friendly)
- Automatic thumbnail generation
- Scheduled publishing
- Analytics tracking

**Key Endpoints:**
```bash
POST /optimize-metadata   # Generate optimized metadata
POST /upload              # Upload video
POST /quick-upload        # Upload with auto-optimization
GET  /analytics/{id}      # Get video analytics
POST /playlist/add        # Add video to playlist
```

**Example Quick Upload:**
```bash
curl -X POST http://localhost:9003/quick-upload \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/data/videos/nueva_vida_official.mp4",
    "artist_name": "Stakas",
    "song_name": "Nueva Vida",
    "genre": "Trap"
  }'
```

---

### 5. ML Predictor (`ml-predictor-v2:9004`)

**Purpose:** AI-powered campaign optimization

**Predictions:**
- Click-through rate (CTR)
- Conversion probability
- Video performance
- Optimal budget allocation
- Audience interest matching

---

### 6. Analytics Dashboard (`analytics-dashboard:9005`)

**Purpose:** Real-time monitoring and reporting

**Metrics Tracked:**
- Campaign spend vs revenue
- ROAS (Return on Ad Spend)
- Conversion rates
- Cost per acquisition (CPA)
- Video views and engagement
- Landing page performance

**Alerts:**
- High spend warnings
- Low performance alerts
- Conversion anomalies
- Budget exhaustion warnings

---

### 7. Automation Orchestrator (`automation-orchestrator:9006`)

**Purpose:** Workflow coordination and automation

**Automated Actions:**
- Pause campaigns with ROAS < 1.5x
- Increase budget for campaigns with ROAS > 3.0x
- Pause ads with CPC > $5
- Auto-create lookalike audiences
- Schedule content publishing

---

## 🚀 SETUP GUIDE

### Prerequisites

1. **Meta Developer Account**
   - Go to: https://developers.facebook.com/
   - Create app
   - Enable Marketing API
   - Get App ID, App Secret, Access Token

2. **Meta Business Manager**
   - Go to: https://business.facebook.com/
   - Create Ad Account
   - Create Facebook Page
   - Create Facebook Pixel
   - Get Account IDs

3. **YouTube Account**
   - Go to: https://console.cloud.google.com/
   - Create project
   - Enable YouTube Data API v3
   - Create OAuth 2.0 credentials
   - Get Client ID, Client Secret, Refresh Token

4. **Domain (Optional)**
   - For landing pages
   - SSL certificate recommended

---

### Installation Steps

#### Step 1: Clone Repository

```bash
git clone https://github.com/your-repo/master.git
cd master
```

#### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.v2 .env

# Edit with your credentials
nano .env
```

**Required Environment Variables:**

```bash
# Meta Ads
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
META_ACCESS_TOKEN=your_long_lived_token
META_AD_ACCOUNT_ID=act_123456789
META_PAGE_ID=your_page_id
META_PIXEL_ID=your_pixel_id
META_CONVERSION_API_TOKEN=your_conversion_token

# YouTube
YOUTUBE_CLIENT_ID=your_client_id.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=your_client_secret
YOUTUBE_REFRESH_TOKEN=your_refresh_token
YOUTUBE_CHANNEL_ID=your_channel_id

# Database
DB_PASSWORD=YourSecurePassword123
REDIS_PASSWORD=YourRedisPassword456

# Alerts
DISCORD_WEBHOOK=https://discord.com/api/webhooks/your-webhook
```

#### Step 3: Build Docker Images

```bash
# Build all services
docker-compose -f docker-compose-v2.yml build

# Or build individually
docker-compose -f docker-compose-v2.yml build meta-ads-manager
docker-compose -f docker-compose-v2.yml build pixel-tracker
docker-compose -f docker-compose-v2.yml build youtube-uploader
```

#### Step 4: Start Services

```bash
# Start all services
docker-compose -f docker-compose-v2.yml up -d

# Check status
docker-compose -f docker-compose-v2.yml ps

# View logs
docker-compose -f docker-compose-v2.yml logs -f
```

#### Step 5: Verify Health

```bash
# Check all services
curl http://localhost:9000/health  # Meta Ads Manager
curl http://localhost:9001/health  # Pixel Tracker
curl http://localhost:9002/health  # Landing Pages
curl http://localhost:9003/health  # YouTube Uploader
curl http://localhost:9004/health  # ML Predictor
curl http://localhost:9005/health  # Analytics Dashboard
curl http://localhost:9006/health  # Orchestrator
```

---

## 🔧 CONFIGURATION

### Meta Ads Targeting Configuration

**File:** `.env`

```bash
# Geographic Targeting
TARGET_COUNTRIES=US,MX,ES,AR,CL,CO
TARGET_LANGUAGES=en,es

# Demographic Targeting
TARGET_AGE_MIN=18
TARGET_AGE_MAX=35
TARGET_GENDERS=all  # all, male, female

# Interest Targeting (Music)
TARGET_INTERESTS=trap music,hip hop,reggaeton,Latin music,Spotify,SoundCloud

# Behavioral Targeting
TARGET_BEHAVIORS=music streaming,concert attendance,festival goers
```

### Campaign Budget Configuration

```bash
# Budget Settings
DAILY_BUDGET=50  # USD per day
CAMPAIGN_OBJECTIVE=CONVERSIONS
OPTIMIZATION_GOAL=LANDING_PAGE_VIEWS

# Optimization Thresholds
MIN_ROAS_THRESHOLD=1.5
MAX_CPC_THRESHOLD=5.0
MIN_CTR_THRESHOLD=0.5

# Auto-Scaling
BUDGET_INCREASE_TRIGGER_ROAS=3.0
BUDGET_INCREASE_PERCENTAGE=20
BUDGET_DECREASE_TRIGGER_ROAS=1.0
BUDGET_DECREASE_PERCENTAGE=30
```

---

## 📊 WORKFLOW AUTOMATION

### Complete Marketing Funnel (Automated)

```yaml
DAILY WORKFLOW:

08:00 AM - Campaign Check
  ├─ Orchestrator queries all active campaigns
  ├─ Gets insights from Meta Ads Manager
  ├─ ML Predictor analyzes performance
  └─ Actions:
      ├─ Pause campaigns with ROAS < 1.5x
      ├─ Increase budget for ROAS > 3.0x
      └─ Send daily report to Discord

10:00 AM - Content Upload
  ├─ YouTube Uploader checks /data/videos/
  ├─ Optimizes metadata
  ├─ Uploads videos
  ├─ Adds to playlists
  └─ Notifies analytics dashboard

12:00 PM - Mid-day Optimization
  ├─ Check landing page performance
  ├─ A/B test winner determination
  ├─ Update pixel tracking
  └─ Retarget high-intent users

03:00 PM - Budget Reallocation
  ├─ ML Predictor suggests budget changes
  ├─ Orchestrator implements changes
  └─ Update campaigns

06:00 PM - Evening Report
  ├─ Analytics Dashboard generates report
  ├─ Calculate day's ROI
  ├─ Send to Discord/Email
  └─ Plan tomorrow's strategy
```

---

## 💰 COST ANALYSIS

### Infrastructure Costs (Monthly)

```yaml
VPS Hosting (Hetzner CX51):
  - 8 vCPU, 16GB RAM, 240GB SSD
  - Cost: €19.99/month (~$22/month)

Meta Ads Spend:
  - Daily budget: $50
  - Monthly: $1,500

YouTube Data API:
  - Free quota: 10,000 units/day
  - Cost: $0 (unless exceeding quota)

Domain + SSL:
  - Domain: $12/year
  - SSL: Free (Let's Encrypt)

Total Infrastructure: ~$22/month
Total with Ads: ~$1,522/month
```

### ROI Projection

```
SCENARIO: $50/day ad spend

Conservative:
├─ Daily clicks: 200 (CTR: 3%)
├─ Landing page conversions: 10 (5% CR)
├─ Spotify streams per conversion: 50
├─ Daily streams: 500
├─ Monthly streams: 15,000
└─ Revenue (at $0.004/stream): $60/month
    ROI: -$1,490/month (loss)

Optimized:
├─ Daily clicks: 300 (CTR: 4.5%)
├─ Landing page conversions: 21 (7% CR)
├─ Spotify streams per conversion: 100
├─ Daily streams: 2,100
├─ Monthly streams: 63,000
└─ Revenue (at $0.004/stream): $252/month
    ROI: -$1,270/month (loss, but building audience)

WITH MERCHANDISE/TICKETS:
├─ Monthly organic audience: 63,000 streams
├─ Retargeting for merch: 5% conversion
├─ 3,150 potential buyers
├─ Merch revenue (10% buy $20 item): $6,300
└─ ROI: +$4,778/month (profit!)
```

**Key Insight:** Ads are for audience building, monetize through:
- Merchandise
- Concert tickets
- Brand deals
- YouTube ad revenue
- Streaming royalties (accumulative)

---

## 🔍 MONITORING & ALERTS

### Health Checks

```bash
# Automated health monitoring
while true; do
  curl -sf http://localhost:9000/health || echo "Meta Ads DOWN"
  curl -sf http://localhost:9001/health || echo "Pixel Tracker DOWN"
  curl -sf http://localhost:9003/health || echo "YouTube Uploader DOWN"
  sleep 60
done
```

### Alert Configuration

**Discord Webhook Alerts:**
- High spend warning (> 80% daily budget)
- Low ROAS alert (< 1.5x)
- Campaign paused notification
- Video upload success/failure
- Daily performance report

---

## 🛠️ TROUBLESHOOTING

### Common Issues

**1. Meta Ads API Errors**
```bash
# Check token validity
curl "https://graph.facebook.com/debug_token?input_token=YOUR_TOKEN&access_token=YOUR_TOKEN"

# Regenerate long-lived token
# https://developers.facebook.com/tools/explorer/
```

**2. YouTube Upload Fails**
```bash
# Refresh OAuth token
# Re-authenticate: https://console.cloud.google.com/
# Update YOUTUBE_REFRESH_TOKEN in .env
```

**3. Database Connection Errors**
```bash
# Check database is running
docker-compose -f docker-compose-v2.yml ps database-v2

# Test connection
docker exec -it marketing-database-v2 psql -U marketing_user -d marketing_funnel_v2
```

**4. High Memory Usage**
```bash
# Check container stats
docker stats

# Restart specific service
docker-compose -f docker-compose-v2.yml restart meta-ads-manager
```

---

## 📚 NEXT STEPS

1. **Configure Landing Pages**
   - Create templates in `v2/landing_pages/templates/`
   - Add your branding
   - Test A/B variants

2. **Set Up Pixel on Landing Pages**
   ```bash
   curl http://localhost:9001/pixel/snippet
   ```
   Copy snippet to landing page `<head>`

3. **Create First Campaign**
   ```bash
   curl -X POST http://localhost:9000/quick-campaign \
     -H "Content-Type: application/json" \
     -d '{
       "artist_name": "Your Artist Name",
       "song_name": "Your Song",
       "landing_url": "https://your-domain.com",
       "daily_budget": 50.0
     }'
   ```

4. **Upload First Video**
   ```bash
   curl -X POST http://localhost:9003/quick-upload \
     -H "Content-Type: application/json" \
     -d '{
       "video_path": "/data/videos/your_video.mp4",
       "artist_name": "Your Artist Name",
       "song_name": "Your Song",
       "genre": "Trap"
     }'
   ```

5. **Monitor Performance**
   - Open Analytics Dashboard: http://localhost:9005
   - Check daily reports in Discord

---

## 🎯 SUCCESS METRICS

### Week 1 Goals
- [ ] 10,000 landing page views
- [ ] 500 Spotify clicks
- [ ] 100 new followers (social media)
- [ ] ROAS > 1.0x

### Month 1 Goals
- [ ] 100,000 landing page views
- [ ] 5,000 Spotify streams
- [ ] 1,000 new followers
- [ ] ROAS > 1.5x
- [ ] Break-even on ad spend

### Month 3 Goals
- [ ] 300,000 landing page views
- [ ] 20,000 Spotify streams
- [ ] 5,000 new followers
- [ ] ROAS > 2.5x
- [ ] Profitable with merch/tickets

---

**Docker v2.0 is ready for production!** 🚀

For support: [Your Contact Information]
