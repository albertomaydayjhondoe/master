# Like4Like Telegram Bot

A sophisticated automation system for managing like-for-like exchanges on Telegram, with automatic YouTube interactions via GoLogin profiles.

## 🚀 Features

- **Telegram Group Monitoring**: Automatically monitors Telegram groups for like4like requests
- **Intelligent Conversation Handling**: State-machine based conversation flow with natural response classification
- **YouTube Automation**: Automated video interactions (like, subscribe, comment, watch) using GoLogin browser profiles
- **Database-Driven**: Comprehensive PostgreSQL database with contact management, exchange tracking, and analytics
- **Rate Limiting & Security**: Built-in rate limiting, human-like behavior simulation, and ban detection
- **Health Monitoring**: System-wide health monitoring and metrics collection
- **Reliability Scoring**: Contact reliability tracking based on exchange completion rates

## 📋 System Requirements

- Python 3.9+
- PostgreSQL 13+
- Google Chrome/Chromium
- GoLogin account and API token
- Telegram API credentials

## 🛠️ Installation

### Automated Setup

Run the setup script to automatically configure the environment:

```bash
./setup.sh
```

This will:
- Check system requirements
- Create Python virtual environment
- Install dependencies
- Setup PostgreSQL database
- Create configuration templates
- Setup systemd service (optional)

### Manual Setup

1. **Clone and setup environment:**
   ```bash
   git clone <repository>
   cd telegram_automation
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Setup PostgreSQL:**
   ```bash
   sudo -u postgres createdb like4like_bot
   sudo -u postgres psql -c "CREATE USER like4like_user WITH PASSWORD 'like4like_pass';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE like4like_bot TO like4like_user;"
   PGPASSWORD=like4like_pass psql -h localhost -U like4like_user -d like4like_bot -f database/schema.sql
   ```

3. **Configure credentials:**
   ```bash
   cp config/secrets/.env.example config/secrets/.env
   # Edit .env with your actual credentials
   ```

## ⚙️ Configuration

Edit `config/secrets/.env` with your credentials:

```env
# Telegram API Configuration
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890

# GoLogin Configuration
GOLOGIN_API_TOKEN=your_gologin_token

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=like4like_bot
DB_USER=like4like_user
DB_PASSWORD=like4like_pass
```

### Getting Telegram API Credentials

1. Visit https://my.telegram.org
2. Log in with your phone number
3. Go to "API Development Tools"
4. Create a new application
5. Copy `api_id` and `api_hash`

### GoLogin Setup

1. Sign up at https://gologin.com
2. Get your API token from the dashboard
3. Create browser profiles for YouTube automation

## 🚦 Usage

### Running the Bot

```bash
# Activate virtual environment
source venv/bin/activate

# Run the bot
python main.py
```

### Using Systemd Service

```bash
# Start the service
sudo systemctl start like4like-bot

# Enable auto-start on boot
sudo systemctl enable like4like-bot

# Check status
sudo systemctl status like4like-bot

# View logs
sudo journalctl -u like4like-bot -f
```

### Manual Testing

```bash
# Test database connection
python -c "
import asyncio
from database.models import DatabaseConnection
async def test():
    db = DatabaseConnection('localhost', 5432, 'like4like_bot', 'like4like_user', 'like4like_pass')
    await db.connect()
    print('✅ Database connected')
    await db.close()
asyncio.run(test())
"

# Test YouTube executor
python -c "
from youtube_executor.config import load_config
config = load_config()
print('✅ Configuration loaded:', config)
"
```

## 📊 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Telegram Bot   │    │ Conversation    │    │  YouTube        │
│                 │◄──►│ Handler         │◄──►│  Executor       │
│ - Group Monitor │    │                 │    │                 │
│ - DM Handler    │    │ - State Machine │    │ - GoLogin API   │
│ - Rate Limiting │    │ - Response AI   │    │ - Selenium      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   Database      │
                    │                 │
                    │ - Contacts      │
                    │ - Exchanges     │
                    │ - Analytics     │
                    │ - Health Logs   │
                    └─────────────────┘
```

## 📦 Components

### 1. Telegram Bot (`bot/telegram_bot.py`)
- Monitors specified Telegram groups for like4like requests
- Handles direct messages and conversation initiation
- Message classification and filtering
- Rate limiting and spam protection

### 2. Conversation Handler (`bot/conversation_handler.py`)
- State machine for managing conversation flow
- Response classification using pattern matching
- Term negotiation and agreement tracking
- Integration with YouTube executor

### 3. YouTube Executor (`youtube_executor/youtube_executor.py`)
- GoLogin profile management
- Selenium-based YouTube automation
- Human-like behavior simulation
- Action execution and result tracking

### 4. Database Models (`database/models.py`)
- PostgreSQL integration with AsyncPG
- Comprehensive data models for all entities
- Connection pooling and query optimization

## 📈 Monitoring & Analytics

The system includes comprehensive monitoring:

- **Health Monitoring**: Component health checks every 5 minutes
- **Metrics Collection**: System metrics collected hourly
- **Reliability Scoring**: Contact reliability based on exchange completion
- **Performance Analytics**: Execution success rates and timing analysis

### Database Analytics Views

```sql
-- View active conversations
SELECT * FROM active_conversations_view;

-- View exchange success rates
SELECT * FROM exchange_success_rates_view;

-- View contact reliability
SELECT * FROM contact_reliability_view;
```

## 🔒 Security Features

- **Rate Limiting**: Prevents excessive API usage
- **Human Behavior Simulation**: Random delays and mouse movements
- **Profile Rotation**: Automatic GoLogin profile rotation
- **Ban Detection**: Monitors for account restrictions
- **Error Handling**: Comprehensive error handling and recovery

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check PostgreSQL service
   sudo systemctl status postgresql
   
   # Test connection
   psql -h localhost -U like4like_user -d like4like_bot
   ```

2. **Telegram API Errors**
   ```bash
   # Check API credentials in .env file
   # Ensure phone number format is correct: +1234567890
   ```

3. **Chrome/Selenium Issues**
   ```bash
   # Install Chrome
   wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
   sudo apt-get update && sudo apt-get install google-chrome-stable
   ```

4. **GoLogin Profile Issues**
   ```bash
   # Check GoLogin API token
   # Ensure profiles are created and active
   ```

### Logging

- Application logs: `logs/like4like_bot.log`
- System logs: `sudo journalctl -u like4like-bot`
- Database logs: PostgreSQL log files

## 🔧 Development

### Project Structure

```
telegram_automation/
├── bot/
│   ├── telegram_bot.py         # Main Telegram bot
│   ├── conversation_handler.py # Conversation state machine
│   └── __init__.py
├── database/
│   ├── schema.sql             # Database schema
│   ├── models.py              # Database models
│   └── __init__.py
├── youtube_executor/
│   ├── youtube_executor.py    # YouTube automation
│   ├── config.py             # Configuration
│   └── __init__.py
├── config/
│   └── secrets/
│       └── .env              # Environment variables
├── logs/                     # Log files
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
├── setup.sh                  # Setup script
└── README.md                 # This file
```

### Testing

```bash
# Run tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_conversation_handler.py -v

# Run with coverage
python -m pytest --cov=telegram_automation tests/
```

### Adding New Features

1. **Database Changes**: Update `database/schema.sql` and `database/models.py`
2. **Conversation Flow**: Modify state machine in `conversation_handler.py`
3. **YouTube Actions**: Extend `youtube_executor.py` with new automation
4. **Configuration**: Add new settings to `config.py`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## ⚠️ Disclaimer

This software is for educational purposes only. Users are responsible for complying with Telegram's Terms of Service, YouTube's Terms of Service, and all applicable laws and regulations. The authors are not responsible for any misuse of this software.

## 📧 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the logs for error details

---

**Built with ❤️ for automation enthusiasts**