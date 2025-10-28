# 🚀 Docker v2.0 - Meta Ads to YouTube Marketing Funnel

Complete automated marketing system for music artists: Meta Ads → Facebook Pixel → Landing Pages → YouTube

---

## ✨ What's New in v2.0

Docker v2.0 is a **complete reimplementation** focused on the marketing funnel:

- ✅ **Meta Ads Manager**: Full campaign automation with ML optimization
- ✅ **Facebook Pixel Tracker**: Conversion tracking & custom audiences
- ✅ **Landing Page Optimizer**: High-converting pages with A/B testing
- ✅ **YouTube Uploader**: Automated video publishing with SEO optimization
- ✅ **ML Predictor**: AI-powered campaign optimization
- ✅ **Analytics Dashboard**: Real-time metrics and ROI tracking
- ✅ **Automation Orchestrator**: Smart workflow coordination

---

## 🎯 Quick Start (5 minutes)

```bash
# 1. Configure credentials
cp .env.v2 .env
nano .env  # Add your Meta Ads + YouTube credentials

# 2. Build and start
./docker-v2-manage.sh build
./docker-v2-manage.sh start

# 3. Check health
./docker-v2-manage.sh health

# 4. Create first campaign
./docker-v2-manage.sh campaign

# 5. Upload first video
./docker-v2-manage.sh upload
```

---

## 📊 Architecture

```
Meta Ads (9000) → Landing Pages (9002) → Pixel Tracker (9001)
                         ↓
                   User Actions
                         ↓
              YouTube (9003) + Analytics (9005)
                         ↓
               ML Optimization (9004)
                         ↓
           Auto-Scale & Optimize (9006)
```

**Services:**
- **Port 9000**: Meta Ads Manager
- **Port 9001**: Pixel Tracker
- **Port 9002**: Landing Pages
- **Port 9003**: YouTube Uploader
- **Port 9004**: ML Predictor
- **Port 9005**: Analytics Dashboard
- **Port 9006**: Automation Orchestrator

---

## 🔧 Management Commands

```bash
./docker-v2-manage.sh build      # Build images
./docker-v2-manage.sh start      # Start all services
./docker-v2-manage.sh stop       # Stop services
./docker-v2-manage.sh health     # Check service health
./docker-v2-manage.sh logs       # View logs
./docker-v2-manage.sh urls       # Show all URLs
./docker-v2-manage.sh docs       # Show API docs
./docker-v2-manage.sh campaign   # Create Meta Ads campaign
./docker-v2-manage.sh upload     # Upload YouTube video
./docker-v2-manage.sh backup     # Create backup
```

---

## 📖 Documentation

- **Complete Guide**: [DOCKER_V2_COMPLETE_GUIDE.md](DOCKER_V2_COMPLETE_GUIDE.md)
  - Architecture details
  - Setup instructions
  - API documentation
  - Workflow automation
  - Cost analysis
  - Troubleshooting

---

## 🎨 Example: Complete Marketing Campaign

### 1. Create Meta Ads Campaign

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

### 2. Track Conversions with Pixel

```html
<!-- Add to landing page -->
<script>
fbq('trackCustom', 'SpotifyClick', {
  content_name: 'Nueva Vida',
  content_category: 'Trap',
  value: 1.00
});
</script>
```

### 3. Upload Video to YouTube

```bash
curl -X POST http://localhost:9003/quick-upload \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/data/videos/nueva_vida.mp4",
    "artist_name": "Stakas",
    "song_name": "Nueva Vida",
    "genre": "Trap"
  }'
```

### 4. Monitor Performance

```bash
# Open analytics dashboard
open http://localhost:9005

# Or check via API
curl http://localhost:9000/campaigns/{campaign_id}/insights
```

---

## 💰 Cost Analysis

**Infrastructure**: ~$22/month (VPS)  
**Meta Ads**: $50/day = $1,500/month  
**Total**: ~$1,522/month

**ROI with Merchandising**:
- 63,000 monthly streams
- 3,150 retargeting audience
- 315 merch sales ($20 avg)
- **Revenue**: $6,300/month
- **Profit**: +$4,778/month

---

## 🔐 Required Credentials

### Meta Ads
1. Go to https://developers.facebook.com/
2. Create app → Enable Marketing API
3. Get: `META_APP_ID`, `META_APP_SECRET`, `META_ACCESS_TOKEN`
4. Get Ad Account ID from https://business.facebook.com/
5. Create Facebook Pixel → Get `META_PIXEL_ID`

### YouTube
1. Go to https://console.cloud.google.com/
2. Create project → Enable YouTube Data API v3
3. Create OAuth 2.0 credentials
4. Get: `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`
5. Generate refresh token

See [DOCKER_V2_COMPLETE_GUIDE.md](DOCKER_V2_COMPLETE_GUIDE.md) for detailed instructions.

---

## 🚀 Deployment

### Local Development
```bash
DUMMY_MODE=true ./docker-v2-manage.sh start
```

### Production (VPS)
```bash
# 1. SSH into VPS
ssh root@your-vps-ip

# 2. Clone repo
git clone https://github.com/your-repo/master.git
cd master

# 3. Configure
cp .env.v2 .env
nano .env  # Add production credentials
sed -i 's/DUMMY_MODE=true/DUMMY_MODE=false/' .env

# 4. Deploy
./docker-v2-manage.sh build
./docker-v2-manage.sh start

# 5. Verify
./docker-v2-manage.sh health
```

---

## 📊 Monitoring

### Health Checks
```bash
# Check all services
./docker-v2-manage.sh health

# View logs
./docker-v2-manage.sh logs meta-ads-manager
```

### Alerts
Configure Discord webhook in `.env`:
```bash
DISCORD_WEBHOOK=https://discord.com/api/webhooks/your-webhook
```

Alerts for:
- High ad spend (> 80% budget)
- Low ROAS (< 1.5x)
- Campaign paused
- Video upload success/failure
- Daily performance report

---

## 🆚 v1 vs v2 Comparison

| Feature | v1 (Fanpage Viral) | v2 (Meta Ads Funnel) |
|---------|-------------------|---------------------|
| **Focus** | Organic viral growth | Paid acquisition + conversion |
| **Primary Goal** | TikTok/IG virality | Landing page conversions |
| **Cost** | ~$195/month | ~$1,522/month |
| **Timeline** | 2-3 weeks setup | 5 minutes setup |
| **Scale** | Limited by accounts | Limited by budget |
| **ROI** | Break-even month 2-3 | Requires merch/tickets |
| **Best For** | Long-term audience | Fast growth + monetization |

**Recommendation**: Use both!
- v2 for paid acquisition (fast growth)
- v1 for organic engagement (cost-effective)

---

## 🤝 Support

- **Documentation**: [DOCKER_V2_COMPLETE_GUIDE.md](DOCKER_V2_COMPLETE_GUIDE.md)
- **Issues**: Create GitHub issue
- **Questions**: Discord community

---

## 📝 License

MIT License - See LICENSE file

---

## 🎯 Next Steps

1. **Configure credentials** in `.env`
2. **Build and start** services
3. **Create first campaign** with `./docker-v2-manage.sh campaign`
4. **Upload first video** with `./docker-v2-manage.sh upload`
5. **Monitor performance** on http://localhost:9005
6. **Scale budget** as ROI improves

**Ready to grow your music career? Let's go! 🚀🎵**
