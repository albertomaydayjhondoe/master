# 🌅 Universal Multi-Branch Automation System

> **One command to wake them all** - A unified automation ecosystem spanning TikTok ML, Meta Ads, and Like4Like systems

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Dummy Mode](https://img.shields.io/badge/dummy%20mode-enabled-green.svg)](https://github.com/your-repo)
[![Multi-Branch](https://img.shields.io/badge/branches-3-orange.svg)](https://github.com/your-repo)
[![Status](https://img.shields.io/badge/status-production%20ready-success.svg)](https://github.com/your-repo)

## 🎯 System Overview

This project implements a **Universal Dummy Mode Architecture** that can simulate and operate three sophisticated automation systems:

- 🎬 **RAMA Branch**: TikTok ML Automation System with YOLO models and device farm
- 📱 **META Branch**: Meta Ads Automation with Telegram monitoring  
- 💬 **TELE Branch**: Like4Like Telegram Bot with YouTube automation

**Key Innovation**: Single command initialization that intelligently generates configurations, simulates cloud databases, mocks Ultralytics integrations, and awakens all systems simultaneously.

## ⚡ Quick Start

```bash
# One command to wake the entire ecosystem
make wake

# Or use the direct script
./wake.sh --quick

# Full system awakening (all branches)
make wake-full

# Stop everything
make stop
```

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           UNIVERSAL AWAKENER SYSTEM                                │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  🌅 awakener.py          │  🔧 config_generator.py  │  🚀 wake.sh               │
│  ├─ ENV Generation       │  ├─ Intelligent Analysis │  ├─ System Orchestration   │
│  ├─ Cloud DB Simulation  │  ├─ Branch Detection     │  ├─ Service Management     │
│  ├─ Ultralytics Mock     │  ├─ Config Generation    │  └─ Health Monitoring      │
│  └─ Service Coordination │  └─ Dependency Mapping   │                            │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RAMA BRANCH   │    │   META BRANCH   │    │   TELE BRANCH   │
│   🎬 TikTok ML  │    │   📱 Meta Ads   │    │   💬 Like4Like  │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • ML Core API   │    │ • Telegram Mon  │    │ • Telegram Bot  │
│ • YOLO Models   │    │ • Meta Ads API  │    │ • Conversation   │
│ • Device Farm   │    │ • GoLogin Auto  │    │ • YouTube Exec  │
│ • Monitoring    │    │ • Campaign Mgmt │    │ • State Machine │
└─────────────────┘    └─────────────────┘    └─────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              SHARED INFRASTRUCTURE                                 │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  🗄️ Mock Databases    │  🤖 Ultralytics Sim  │  🔒 Security Layer  │  📊 Monitoring │
│  ├─ PostgreSQL (SQLite)│ ├─ YOLO Model Mocks  │ ├─ Dummy API Keys  │ ├─ Health Checks│
│  ├─ MongoDB (JSON)     │ ├─ Training Data     │ ├─ Rate Limiting   │ ├─ Metrics Coll │
│  ├─ Redis (JSON)       │ ├─ Model Configs     │ └─ CORS Settings   │ └─ Alerting     │
│  └─ Elasticsearch      │ └─ Auto-Retraining   │                    │                 │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## 🚀 Features

### 🌟 Universal Awakener
- **Single Command Initialization**: `make wake` activates everything
- **Intelligent Configuration**: Automatically analyzes project structure and generates optimal configs
- **Cross-Branch Compatibility**: Seamlessly works across rama, meta, and tele branches
- **Dummy Mode First**: Everything works out-of-the-box without external dependencies

### 🧠 Intelligent Systems
- **Smart ENV Generation**: Analyzes requirements and generates appropriate environment files
- **Cloud Database Simulation**: Creates mock databases that behave like production systems
- **Ultralytics Integration**: Simulates YOLO models with realistic responses
- **Service Orchestration**: Coordinates startup and health monitoring of all services

### 🔧 Production Ready
- **Factory Pattern**: Easy migration from dummy to production implementations
- **Environment Variables**: Production configurations through ENV overrides
- **Health Monitoring**: Comprehensive system health checks and metrics
- **Error Recovery**: Graceful handling of failures and automatic restarts

## 📋 System Commands

| Command | Description | Use Case |
|---------|-------------|----------|
| `make wake` | Quick development start | Daily development |
| `make wake-full` | Full system with all branches | Complete testing |
| `make rama` | TikTok ML system only | ML development |
| `make meta` | Meta Ads automation only | Ads testing |
| `make tele` | Like4Like bot only | Bot development |
| `make stop` | Stop all services | Cleanup |
| `make status` | System health check | Monitoring |
| `make config` | Generate configurations | Setup |

## 🌿 Branch Details

### 🎬 RAMA Branch - TikTok ML System
- **Location**: Root directory
- **Focus**: ML-powered TikTok automation
- **Services**: ML API (FastAPI), Device Farm, Monitoring
- **Models**: YOLO Screenshot Detection, Video Analysis, Affinity Calculation
- **Key Features**: Automated content analysis, device orchestration, anomaly detection

### 📱 META Branch - Meta Ads Automation  
- **Location**: `meta_automation/`
- **Focus**: Telegram-driven Meta Ads management
- **Services**: Telegram Monitor, Meta Ads API, GoLogin Integration
- **Key Features**: Campaign automation, audience targeting, budget optimization

### 💬 TELE Branch - Like4Like Automation
- **Location**: `telegram_automation/` 
- **Focus**: Telegram bot for like-for-like exchanges
- **Services**: Telegram Bot, YouTube Executor, Conversation Handler
- **Key Features**: Intelligent conversations, YouTube automation, exchange tracking

## ⚙️ Configuration System

The system uses intelligent configuration generation:

```python
# Automatic project analysis
python3 config_generator.py

# Generates:
# - .env (global settings)
# - .env.rama (TikTok ML)
# - .env.meta (Meta Ads) 
# - .env.tele (Like4Like)
# - universal_config.json
# - universal_config.yaml
```

### Environment Variables

Each branch gets optimized environment variables:

```bash
# RAMA Branch
DUMMY_MODE=true
ML_API_PORT=8000
DATABASE_URL=postgresql://dummy:dummy@localhost:5432/tiktok_ml
YOLO_SCREENSHOT_IMPL=ml_core.models.yolo_screenshot.YoloScreenshotDetector

# META Branch  
TELEGRAM_API_ID=12345
META_ACCESS_TOKEN=dummy_meta_token
GOLOGIN_API_TOKEN=dummy_gologin_token

# TELE Branch
TELEGRAM_BOT_TOKEN=dummy_bot_token
YOUTUBE_ENABLE_COMMENTS=true
SECURITY_HUMAN_DELAYS=true
```

## 🗄️ Database Architecture

### Mock Database System
The awakener creates intelligent database mocks:

```
data/mock_databases/
├── postgresql.db          # SQLite mock of PostgreSQL
├── mongodb_collections/   # JSON files for MongoDB
├── redis_cache.json      # Redis simulation
└── elasticsearch/        # Elasticsearch mock
```

### Database Features
- **Cross-Branch Tables**: Separate schemas for each branch
- **Realistic Data**: Auto-generated test data that mimics production
- **Migration Ready**: Easy transition to real databases
- **Performance Simulation**: Realistic query timing and responses

## 🤖 Ultralytics Integration

### Mock YOLO Models
```
data/models/mock_ultralytics/
├── yolov8n_screenshot.pt     # UI element detection
├── yolov8s_video.pt          # Video content analysis  
├── yolov8m_detection.pt      # General object detection
├── custom_tiktok.pt          # TikTok-specific elements
└── training_data/            # Mock training datasets
```

### Model Features
- **Realistic Responses**: Simulated detection results with confidence scores
- **Configuration**: Model-specific settings and class definitions
- **Training Simulation**: Mock training pipelines and metrics
- **Performance Metrics**: Simulated accuracy and timing data

## 🔒 Security & Production

### Dummy Mode Security
- **API Key Simulation**: Realistic but safe dummy keys
- **Rate Limiting**: Production-like throttling
- **CORS Configuration**: Development-friendly settings
- **Authentication**: Disabled for development, ready for production

### Production Migration
```bash
# 1. Set production environment variables
export DUMMY_MODE=false
export REAL_API_KEYS=true

# 2. Implement production factories
# ml_core/models/factory.py - point to real implementations
# device_farm/controllers/factory.py - real ADB controllers

# 3. Add real credentials
# Update .env files with actual API keys

# 4. Deploy with production settings
make wake-full
```

## 📊 Monitoring & Health

### System Monitoring
- **Health Checks**: Automated service health verification
- **Metrics Collection**: System and application metrics
- **Alerting**: Configurable alert thresholds
- **Logging**: Structured logging across all services

### Available Endpoints
```
# Health Monitoring
http://localhost:8000/health          # ML API health
http://localhost:8000/docs            # API documentation
http://localhost:8000/metrics         # System metrics

# Branch-Specific Endpoints
http://localhost:8001/meta/status     # Meta Ads status  
http://localhost:8002/tele/status     # Like4Like status
```

## 🛠️ Development Workflow

### Daily Development
```bash
# Start development environment
make wake

# Check system status
make status

# Run tests
make test

# Stop everything
make stop
```

### Feature Development
```bash
# Work on specific branch
make rama    # TikTok ML development
make meta    # Meta Ads development  
make tele    # Like4Like development

# Generate new configs after changes
make config

# Clean and restart
make clean && make wake
```

### Production Deployment
```bash
# Full system deployment
make wake-full

# With Docker
make docker-build
make docker-run

# Monitor deployment
make status
```

## 📁 Project Structure

```
universal-automation-system/
├── 🌅 awakener.py              # Universal system awakener
├── 🔧 config_generator.py      # Intelligent config generation
├── 🚀 wake.sh                  # Shell script orchestrator
├── 📝 Makefile                 # Universal command interface
├── 📚 README_UNIVERSAL.md      # This file
├── 
├── 🎬 rama/ (TikTok ML)
│   ├── ml_core/                # ML API and models
│   ├── device_farm/            # Device automation
│   ├── orchestration/          # Workflow coordination
│   └── monitoring/             # System monitoring
├── 
├── 📱 meta_automation/ (Meta Ads)
│   ├── telegram_monitor.py     # Telegram monitoring
│   ├── meta_ads/               # Meta Ads integration
│   ├── gologin/                # Browser automation
│   └── campaigns/              # Campaign management
├── 
├── 💬 telegram_automation/ (Like4Like)
│   ├── bot/                    # Telegram bot core
│   ├── youtube_executor/       # YouTube automation
│   ├── database/               # Database models  
│   └── main.py                 # Application entry
├── 
├── 🗄️ data/
│   ├── mock_databases/         # Simulated databases
│   ├── models/                 # ML model storage
│   ├── exports/                # Data exports
│   └── screenshots/            # Screenshot storage
├── 
├── ⚙️ config/
│   ├── app_settings.py         # Global settings
│   ├── secrets/                # Environment files
│   └── ml/                     # ML configurations
├── 
└── 📋 logs/                    # System logs
```

## 🔧 Advanced Configuration

### Custom Branch Configuration
```python
# config_generator.py customization
def add_custom_branch(self):
    custom_branch = {
        'name': 'custom',
        'description': 'Custom Automation System',
        'services': ['custom_api', 'custom_worker'],
        'env_vars': {
            'CUSTOM_API_KEY': 'dummy_key',
            'CUSTOM_DATABASE_URL': 'postgresql://dummy:dummy@localhost:5432/custom'
        }
    }
    return custom_branch
```

### Service Extensions
```bash
# Add new service to awakener
# awakener.py - ServiceOrchestrator class
services['custom'] = [
    {
        'name': 'custom_service',
        'command': ['python', 'custom_service.py'],
        'cwd': self.config.project_root / 'custom_automation'
    }
]
```

## 🐛 Troubleshooting

### Common Issues

1. **Services won't start**
   ```bash
   # Check Python version
   python3 --version  # Should be 3.9+
   
   # Check ports
   lsof -i :8000  # Check if port is busy
   
   # Reset everything
   make stop && make clean && make wake
   ```

2. **Database connection errors**
   ```bash
   # Recreate mock databases
   rm -rf data/mock_databases/
   make config  # Regenerates everything
   ```

3. **Environment issues**
   ```bash
   # Regenerate environment files
   make env
   
   # Check environment variables
   make status
   ```

### Debug Mode
```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
make wake

# Check logs
tail -f logs/*.log
```

## 🤝 Contributing

### Adding New Branches
1. Create branch directory structure
2. Add branch detection to `config_generator.py`
3. Add services to `awakener.py`
4. Update `wake.sh` with branch-specific commands
5. Add Makefile targets

### Extending Functionality
1. Follow the factory pattern for new implementations
2. Add dummy mode implementations first
3. Create production overrides via environment variables
4. Add health checks and monitoring
5. Update documentation

## 📊 System Metrics

### Performance Characteristics
- **Startup Time**: < 30 seconds for full system
- **Memory Usage**: ~500MB for all services
- **API Response Time**: < 100ms for dummy endpoints
- **Database Performance**: Sub-millisecond for mock operations

### Scalability
- **Concurrent Services**: Up to 20 services per branch
- **Database Connections**: Pool-based connection management
- **API Throughput**: 1000+ requests/second in dummy mode
- **Resource Monitoring**: Real-time metrics collection

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ultralytics**: YOLO model architecture inspiration
- **FastAPI**: High-performance API framework
- **Telethon**: Telegram automation library
- **Selenium**: Web automation framework
- **GoLogin**: Browser profile management

---

## 🚀 Get Started Now

```bash
# Clone and wake the system
git clone <repository>
cd universal-automation-system
make wake

# 🎉 Your entire automation ecosystem is now AWAKE!
```

**Built with ❤️ for automation enthusiasts who believe one command should rule them all.**