# Meta Ads Integration System

Complete Facebook/Instagram advertising automation with ML optimization, ready for production deployment.

## 🎯 System Overview

The Meta Ads integration provides:

- **Campaign Automation**: Full campaign lifecycle management with Meta Marketing API
- **ML Optimization**: Real-time performance optimization using machine learning
- **Monitoring & Alerts**: Comprehensive monitoring with automated alerts
- **Production Ready**: Complete production deployment configuration

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Meta Automator │────│ Action Generator│────│    Monitor      │
│                 │    │                 │    │                 │
│ • Campaign Mgmt │    │ • ML Insights   │    │ • Alerts        │
│ • API Calls     │    │ • Optimization  │    │ • Health Score  │
│ • Pixel Events  │    │ • Auto Actions  │    │ • Reporting     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   API Gateway   │
                    │                 │
                    │ • REST Endpoints│
                    │ • Authentication│
                    │ • Rate Limiting │
                    └─────────────────┘
```

## 📦 Components

### 1. MetaAdsAutomator (`meta_automator.py`)
- **Campaign Management**: Create, modify, and manage Meta Ads campaigns
- **Conversions API**: Track and send conversion events 
- **Rate Limiting**: Respect Meta API limits
- **Error Handling**: Robust error handling and retries

### 2. MetaActionGenerator (`meta_action_generator.py`)
- **ML Insights**: Generate optimization insights from performance data
- **Action Generation**: Convert insights to executable actions
- **Performance Analysis**: Analyze ROAS, CPA, CTR trends
- **Smart Optimization**: Budget scaling, audience expansion, creative refresh

### 3. MetaAdsMonitor (`monitoring.py`)
- **Real-time Monitoring**: Continuous campaign performance tracking
- **Alert System**: Automated alerts for performance issues
- **Health Scoring**: Comprehensive campaign health assessment
- **Reporting**: Daily and weekly performance reports

### 4. API Endpoints (`api_endpoints.py`)
- **Campaign Management**: REST API for campaign operations
- **Optimization**: ML-powered optimization endpoints
- **Monitoring**: Health and metrics endpoints
- **Webhooks**: Meta Conversions API webhook handling

### 5. Production Config (`production_config.py`)
- **Environment Setup**: Production configuration templates
- **Security**: Secure credential management
- **Validation**: Configuration validation and setup scripts

## 🚀 Quick Start

### 1. Development Mode (Default)

The system starts in dummy mode by default for safe development:

```bash
# Install dependencies
pip install -r requirements.txt

# Run example
python social_extensions/meta/example_usage.py

# Start API server
python -m ml_core.api_gateway
```

### 2. Production Setup

#### Step 1: Install Meta Business SDK
```bash
pip install facebook-business>=18.0.0
```

#### Step 2: Configure Environment Variables
```bash
# Copy environment template
cp config/meta/meta_production.env.template .env

# Edit .env with your Meta API credentials
META_APP_ID=your_facebook_app_id
META_APP_SECRET=your_facebook_app_secret
META_ACCESS_TOKEN=your_long_lived_access_token
META_AD_ACCOUNT_ID=1234567890
META_PAGE_ID=0987654321
META_PIXEL_ID=your_pixel_id

# Enable production mode
DUMMY_MODE=false
```

#### Step 3: Run Setup Script
```bash
bash config/meta/setup_production.sh
```

#### Step 4: Start Production API
```bash
python -m ml_core.api_gateway
```

## 🔧 API Usage

### Create Campaign

```python
import httpx

# Campaign data
campaign_data = {
    "campaign_name": "My Product Campaign",
    "objective": "CONVERSIONS",
    "budget_total": 1000.0,
    "start_date": "2024-01-15T00:00:00Z",
    "end_date": "2024-01-22T23:59:59Z",
    "targeting": {
        "countries": ["US", "CA"],
        "age_min": 25,
        "age_max": 45,
        "interests": ["Technology", "Online Shopping"]
    },
    "creatives": [{
        "name": "Main Creative",
        "type": "single_image",
        "title": "Amazing Product!",
        "body": "Get 50% off today only.",
        "call_to_action": "SHOP_NOW",
        "link_url": "https://example.com/product",
        "image_url": "https://example.com/image.jpg"
    }]
}

# Create campaign
response = httpx.post(
    "http://localhost:8000/api/v1/meta/campaigns/create",
    json=campaign_data
)

campaign_result = response.json()
campaign_id = campaign_result["data"]["campaign_id"]
```

### Get Campaign Metrics

```python
# Get 24-hour metrics
response = httpx.get(
    f"http://localhost:8000/api/v1/meta/campaigns/{campaign_id}/metrics?hours=24"
)

metrics = response.json()
print(f"ROAS: {metrics['data']['summary']['overall_roas']:.2f}")
print(f"CPA: ${metrics['data']['summary']['overall_cpa']:.2f}")
```

### Optimize Campaign

```python
# Run ML optimization
optimization_data = {
    "campaign_id": campaign_id,
    "optimization_type": "auto",
    "target_roas": 3.0,
    "max_cpa": 30.0,
    "force_execute": True
}

response = httpx.post(
    f"http://localhost:8000/api/v1/meta/campaigns/{campaign_id}/optimize",
    json=optimization_data
)

result = response.json()
print(f"Applied {result['data']['actions_executed']} optimizations")
```

### Check Account Health

```python
# Get account health
response = httpx.get(
    f"http://localhost:8000/api/v1/meta/accounts/{account_id}/health"
)

health = response.json()
print(f"Health: {health['data']['overall_health']}")
print(f"ROAS: {health['data']['avg_roas_24h']:.2f}")
```

## 🎯 ML Optimization Features

### Automatic Budget Scaling
- **High Performers**: Automatically increase budget for campaigns exceeding ROAS targets
- **Poor Performers**: Reduce budget or pause underperforming campaigns
- **Smart Scaling**: ML-driven scaling factors based on performance confidence

### Audience Optimization
- **Lookalike Expansion**: Create and test lookalike audiences from converters
- **Interest Refinement**: Add/remove interests based on performance data
- **Demographic Optimization**: Adjust age and gender targeting based on conversion data

### Creative Management
- **Fatigue Detection**: Identify and refresh fatigued creatives
- **Performance Ranking**: Rank creatives by conversion performance
- **A/B Testing**: Automated creative testing and winner selection

### Bidding Optimization
- **Bid Cap Adjustment**: Dynamically adjust bid caps based on CPA performance
- **Strategy Switching**: Switch between bidding strategies based on campaign goals
- **Time-based Optimization**: Adjust bids based on performance by time of day

## 📊 Monitoring & Alerts

### Performance Alerts
- **ROAS Alerts**: Alert when ROAS falls below threshold
- **CPA Alerts**: Alert when cost per acquisition exceeds limit
- **Budget Alerts**: Alert on budget overspend or underspend
- **Conversion Alerts**: Alert when conversions stop or drop significantly

### Health Scoring
- **Overall Score**: 0-100 comprehensive health score
- **Component Scores**: Performance, budget efficiency, engagement, technical
- **Trend Analysis**: Historical performance trend assessment
- **Actionable Insights**: Specific recommendations for improvement

### Reporting
- **Daily Reports**: Daily performance summary emails
- **Weekly Reports**: Comprehensive weekly analysis
- **Custom Reports**: On-demand reporting via API
- **Dashboard Integration**: Grafana dashboard templates included

## 🔐 Security & Compliance

### Data Protection
- **PII Hashing**: Automatic hashing of personal data for Conversions API
- **Token Encryption**: Encrypted storage of access tokens
- **Audit Logging**: Complete audit trail of all actions

### Rate Limiting
- **API Limits**: Respect Meta's rate limits automatically
- **Burst Protection**: Handle traffic spikes gracefully
- **Priority Queuing**: Prioritize critical operations

### Access Control
- **API Authentication**: Secure API endpoints with JWT tokens
- **Role-based Access**: Different permission levels for different users
- **IP Whitelisting**: Restrict API access to specific IPs

## 🛠️ Advanced Configuration

### ML Model Tuning
```python
# Custom ML configuration
ml_config = {
    "meta_ml_config": {
        "model_type": "ensemble",
        "features": ["roas", "cpa", "ctr", "spend_velocity"],
        "prediction_window_hours": 24,
        "retraining_frequency_days": 7,
        "minimum_data_points": 100
    }
}
```

### Alert Customization
```python
# Custom alert thresholds
alert_config = {
    "alert_thresholds": {
        "min_roas": 2.0,
        "max_cpa": 50.0,
        "min_ctr": 0.5,
        "budget_burn_rate_warning": 80.0
    }
}
```

### Campaign Defaults
```python
# Default campaign settings
campaign_defaults = {
    "budget_limits": {
        "min_daily_budget": 10.0,
        "max_daily_budget": 1000.0
    },
    "targeting_constraints": {
        "min_audience_size": 1000,
        "max_audience_size": 50000000
    }
}
```

## 🐛 Troubleshooting

### Common Issues

#### 1. API Connection Errors
```bash
# Check credentials
echo $META_ACCESS_TOKEN | cut -c1-10
```

#### 2. Import Errors
```bash
# Install missing dependencies
pip install facebook-business requests numpy pandas
```

#### 3. Rate Limiting
```bash
# Check rate limit status in logs
grep "rate_limit" logs/meta_ads.log
```

#### 4. Conversion Tracking Issues
```bash
# Verify pixel configuration
curl -X GET "https://graph.facebook.com/v18.0/$META_PIXEL_ID" \
  -H "Authorization: Bearer $META_ACCESS_TOKEN"
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python -m ml_core.api_gateway
```

### Health Checks
```bash
# System health
curl http://localhost:8000/system/health

# Meta-specific health  
curl http://localhost:8000/api/v1/meta/accounts/$META_AD_ACCOUNT_ID/health
```

## 📈 Performance Optimization

### Database Optimization
- Use PostgreSQL for production
- Index campaign_id and timestamp columns
- Regular cleanup of old metrics data

### Caching
- Redis for API response caching
- Cache campaign configurations
- Cache ML model predictions

### Scaling
- Horizontal scaling with load balancer
- Separate ML processing workers
- Queue-based action execution

## 🤝 Contributing

### Development Setup
```bash
# Clone and setup
git clone <repository>
cd meta-ads-integration
pip install -r requirements.txt

# Run tests
pytest tests/

# Run linting
flake8 social_extensions/meta/
```

### Adding New Features
1. Create feature branch
2. Add tests for new functionality
3. Update documentation
4. Submit pull request

## 📚 Additional Resources

- [Meta Marketing API Documentation](https://developers.facebook.com/docs/marketing-api)
- [Meta Business SDK Python](https://github.com/facebook/facebook-python-business-sdk)
- [Conversions API Guide](https://developers.facebook.com/docs/marketing-api/conversions-api)
- [Meta Pixel Documentation](https://developers.facebook.com/docs/facebook-pixel)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Ready to scale your Meta Ads with AI? 🚀**

The system is production-ready and includes everything needed to deploy intelligent Meta Ads automation at scale.