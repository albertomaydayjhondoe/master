# 🤖 Device Farm v5 - Android Automation System

**Automated testing and engagement system for Android devices with Gologin integration**

---

## 🚀 **OVERVIEW**

Device Farm v5 is a comprehensive automation system designed to manage **10 physical Android devices** simultaneously, integrating with **Gologin API** for browser profile management and **Appium** for mobile automation. Perfect for social media engagement, testing, and large-scale mobile automation workflows.

### **✨ Key Features**

- 📱 **Multi-Device Support**: Control up to 10 physical Android devices via ADB
- 🔗 **Gologin Integration**: Automatic profile management with proxy configuration
- 🤖 **Appium Automation**: WebDriver sessions with fingerprint injection
- 🎛️ **Web Dashboard**: Real-time monitoring and manual device control
- 📊 **Task Queue System**: Priority-based task distribution with Redis
- 🐳 **Dockerized**: Complete containerized deployment
- 💾 **Database Persistence**: SQLite with automatic backups
- 🔒 **Security**: API authentication, encrypted credentials storage

---

## 🏗️ **ARCHITECTURE**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Web Dashboard  │    │   Task Queue     │    │  Gologin API    │
│   (Flask)       │    │   (Redis)        │    │  (Profiles)     │
└─────────┬───────┘    └─────────┬────────┘    └─────────┬───────┘
          │                      │                       │
          └──────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────┴──────────────┐
                    │     Main Controller        │
                    │   (Device Farm v5)         │
                    └─────────────┬──────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
┌───────▼────────┐    ┌─────────▼──────────┐    ┌────────▼────────┐
│ ADB Manager    │    │ Appium Controller  │    │ Profile Sync    │
│ (USB Devices)  │    │ (WebDriver)        │    │ (Gologin→Device)│
└───────┬────────┘    └─────────┬──────────┘    └────────┬────────┘
        │                       │                        │
┌───────▼────────┐    ┌─────────▼──────────┐    ┌────────▼────────┐
│   Device 1     │    │   Device 2         │    │   Device N      │
│  (Android)     │    │  (Android)         │    │  (Android)      │
└────────────────┘    └────────────────────┘    └─────────────────┘
```

---

## ⚡ **QUICK START**

### **1. Prerequisites**
```bash
# Required software
- Docker & Docker Compose
- USB debugging enabled on Android devices
- Gologin API account (optional for profiles)
```

### **2. One-Command Deployment**
```powershell
# Windows (PowerShell)
.\deploy-device-farm-v5.ps1

# Linux/Mac
./deploy-device-farm-v5.sh
```

### **3. Access Dashboard**
- **Dashboard**: http://localhost:5000
- **API Docs**: http://localhost:8000/docs
- **Default Login**: admin / admin123

---

## 📋 **DETAILED SETUP**

### **🔧 Development Setup**

```bash
# 1. Clone and navigate
git clone <repository>
cd device_farm_v5

# 2. Create environment file
cp config/.env.example .env
# Edit .env with your Gologin API token

# 3. Development deployment
docker-compose -f docker-compose.dev.yml up -d

# 4. Access services
# Dashboard: http://localhost:5000
# API: http://localhost:8000
```

### **🚀 Production Setup**

```bash
# 1. Production deployment
docker-compose up -d

# 2. With monitoring (optional)
docker-compose --profile monitoring up -d

# 3. With Nginx proxy (optional)  
docker-compose --profile nginx up -d
```

### **📱 Device Connection**

1. **Enable USB Debugging** on each Android device
2. **Connect devices** via USB to host machine
3. **Authorize devices** when prompted
4. **Verify detection**:
   ```bash
   adb devices -l
   ```

---

## 🎛️ **WEB DASHBOARD**

### **Main Features**
- **📊 Real-time Device Status**: Online/offline devices, battery levels
- **🎮 Manual Control**: Start/stop automation, reboot devices
- **📈 Analytics**: Task completion rates, success metrics
- **🔧 Configuration**: Proxy settings, profile assignments
- **📋 Task Management**: Create, monitor, and manage automation tasks
- **📱 Device Logs**: Real-time logging per device

### **Dashboard Sections**
```
├── 🏠 Overview - System status and quick stats
├── 📱 Devices - Individual device management
├── 🔗 Profiles - Gologin profile configuration
├── 📋 Tasks - Task queue and execution monitoring
├── 📊 Analytics - Performance metrics and reports
├── ⚙️ Settings - System configuration
└── 📋 Logs - Real-time system and device logs
```

---

## 🔗 **GOLOGIN INTEGRATION**

### **Profile Management**
```python
# Automatic profile sync from Gologin API
- Browser fingerprints (User-Agent, screen resolution)
- Proxy configurations (HTTP/SOCKS5)
- Timezone and language settings
- Hardware fingerprinting data
```

### **Device-Profile Mapping**
- **Automatic Assignment**: Profiles distributed across devices
- **Manual Override**: Assign specific profiles to devices
- **Rotation Support**: Automatic profile rotation on detection
- **Proxy Synchronization**: Device proxy matches Gologin profile

---

## 🤖 **APPIUM AUTOMATION**

### **Supported Applications**
- **🌐 Chrome Browser**: Web automation with fingerprint injection
- **📸 Instagram**: Native app automation
- **🎵 TikTok**: Video engagement automation
- **🐦 Twitter/X**: Social media interactions
- **📱 Custom Apps**: Configurable package support

### **Automation Features**
- **JavaScript Injection**: Fingerprint spoofing in web contexts
- **Screenshot Capture**: Automatic visual logging
- **Element Detection**: UI Automator 2 integration
- **Session Management**: Multiple concurrent sessions per device
- **Retry Logic**: Automatic error recovery

---

## 📊 **TASK QUEUE SYSTEM**

### **Task Types**
```yaml
web_navigation:
  - url: "https://example.com"
  - actions: ["scroll", "click", "wait"]
  - duration: 30

app_interaction:
  - package: "com.instagram.android"
  - actions: ["like", "follow", "comment"]
  - target_count: 10

screenshot_monitoring:
  - interval: 60
  - analysis: true
  - anomaly_detection: true
```

### **Queue Management**
- **Priority Levels**: 1 (highest) to 10 (lowest)
- **Device Assignment**: Automatic load balancing
- **Retry Logic**: Configurable retry attempts
- **Timeout Handling**: Task-level timeout settings
- **Real-time Monitoring**: Live task execution tracking

---

## 🛠️ **CONFIGURATION**

### **Environment Variables**
```bash
# === GOLOGIN API ===
GOLOGIN_API_TOKEN=your_token_here

# === SYSTEM ===
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
EXPECTED_DEVICES=10

# === SECURITY ===
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=secure_password
API_SECRET_KEY=your_api_key
JWT_SECRET_KEY=your_jwt_key

# === REDIS ===
REDIS_PASSWORD=secure_redis_password
```

### **Advanced Configuration**
Edit `config/config.yaml` for detailed system settings:
- Device detection intervals
- Appium server configurations
- Database connection settings
- Monitoring and alerting options

---

## 📈 **MONITORING & ALERTS**

### **Built-in Monitoring**
- **Device Health**: Connectivity, battery, performance
- **Task Metrics**: Success/failure rates, execution times
- **System Resources**: CPU, memory, disk usage
- **API Performance**: Response times, error rates

### **Optional Monitoring Stack**
```bash
# Deploy with Prometheus + Grafana
docker-compose --profile monitoring up -d

# Access:
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin123)
```

### **Alert Configuration**
- **Webhooks**: Custom webhook notifications
- **Telegram Bot**: Real-time mobile alerts
- **Email**: SMTP alert notifications
- **Dashboard Alerts**: Visual notifications

---

## 🔒 **SECURITY**

### **Authentication**
- **API Key Authentication**: Secure API access
- **JWT Tokens**: Session management
- **Dashboard Login**: Username/password protection

### **Data Protection**
- **Environment Variables**: Sensitive data externalized
- **Database Encryption**: Optional SQLite encryption
- **Secure Proxy**: Encrypted proxy communications
- **USB Security**: Device authorization required

### **Network Security**
- **Internal Network**: Docker network isolation
- **Port Control**: Minimal exposed ports
- **Reverse Proxy**: Optional Nginx SSL termination

---

## 🧪 **TESTING**

### **Run Tests**
```bash
# Unit tests
python -m pytest tests/unit/

# Integration tests  
python -m pytest tests/integration/

# Full test suite
python -m pytest tests/

# With coverage
python -m pytest --cov=src tests/
```

### **Test Categories**
- **Unit Tests**: Individual component testing
- **Integration Tests**: Multi-component workflows
- **Device Tests**: Physical device interactions
- **API Tests**: REST API endpoint validation

---

## 🐛 **TROUBLESHOOTING**

### **Common Issues**

**🔧 Devices Not Detected**
```bash
# Check ADB connection
adb devices -l

# Restart ADB server
adb kill-server
adb start-server

# Check Docker container access
docker exec -it device-farm-v5 adb devices
```

**🔗 Gologin API Issues**
```bash
# Test API connection
curl -H "Authorization: Bearer YOUR_TOKEN" https://api.gologin.com/profile

# Check logs
docker logs device-farm-v5 | grep -i gologin
```

**🤖 Appium Server Issues**
```bash
# Check Appium installation
docker exec -it device-farm-v5 appium --version

# Manual server start
docker exec -it device-farm-v5 appium --port 4723
```

**💾 Database Issues**
```bash
# Check database file
ls -la data/device_farm_v5.db

# Reset database
docker exec -it device-farm-v5 python -c "from src.core.models import get_db_manager; get_db_manager().create_tables()"
```

---

## 🔄 **MAINTENANCE**

### **Regular Tasks**
```bash
# Update system
docker-compose pull
docker-compose up -d

# Backup database
cp data/device_farm_v5.db backups/backup_$(date +%Y%m%d).db

# Clean logs
docker exec -it device-farm-v5 find logs/ -name "*.log" -mtime +7 -delete

# Check system health
curl http://localhost:5000/health
```

### **Performance Optimization**
- **Device Limits**: Monitor CPU/memory usage per device
- **Task Batching**: Group similar tasks for efficiency
- **Profile Rotation**: Implement intelligent profile switching
- **Cache Management**: Regular cache cleanup for optimal performance

---

## 📚 **API REFERENCE**

### **Core Endpoints**
```bash
# Health check
GET /health

# Device management
GET /devices
POST /devices/{serial}/reboot
PUT /devices/{serial}/proxy

# Profile management
GET /profiles
POST /profiles/sync
PUT /profiles/{id}/assign/{device_serial}

# Task management
GET /tasks
POST /tasks
DELETE /tasks/{id}

# Automation
POST /automation/navigate/{session_id}
POST /automation/screenshot/{session_id}
POST /automation/script/{session_id}
```

### **WebSocket Events**
```javascript
// Real-time updates
ws://localhost:5000/ws

// Event types
device_status_change
task_completed
profile_assigned
system_alert
```

---

## 👥 **CONTRIBUTING**

### **Development Workflow**
1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** Pull Request

### **Code Standards**
- **Python 3.11+** compatibility
- **Type hints** for all functions
- **Docstrings** for public methods
- **pytest** for testing
- **Black** for code formatting

---

## 📄 **LICENSE**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 **SUPPORT**

- **📧 Issues**: Create GitHub issue for bugs
- **💬 Discussions**: Use GitHub Discussions for questions
- **📖 Wiki**: Check project wiki for detailed guides
- **🔍 Search**: Search existing issues before creating new ones

---

## 🏆 **ACKNOWLEDGMENTS**

- **Appium Team** - Mobile automation framework
- **Gologin** - Browser profile management
- **Docker** - Containerization platform
- **Flask** - Web framework for dashboard
- **SQLAlchemy** - Database ORM

---

**🤖 Device Farm v5 - Professional Android Device Automation**

*Built with ❤️ for scalable mobile automation*