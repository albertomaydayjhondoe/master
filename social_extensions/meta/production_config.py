"""
Meta Ads Production Configuration
Configuration templates and initialization for production Meta Ads deployment
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class MetaProductionConfig:
    """Production configuration for Meta Ads integration"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / "config" / "meta"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
    def create_production_config_template(self) -> Dict[str, Any]:
        """Create template configuration for production Meta Ads setup"""
        
        template = {
            "meta_ads": {
                "api_config": {
                    "app_id": "${META_APP_ID}",
                    "app_secret": "${META_APP_SECRET}",
                    "access_token": "${META_ACCESS_TOKEN}",
                    "ad_account_id": "${META_AD_ACCOUNT_ID}",
                    "page_id": "${META_PAGE_ID}",
                    "pixel_id": "${META_PIXEL_ID}",
                    "webhook_verify_token": "${META_WEBHOOK_VERIFY_TOKEN}",
                    "api_version": "v18.0"
                },
                "rate_limits": {
                    "calls_per_hour": 200,
                    "calls_per_day": 4800,
                    "burst_limit": 20,
                    "respect_rate_limits": True
                },
                "retry_config": {
                    "max_retries": 3,
                    "initial_delay": 1.0,
                    "max_delay": 30.0,
                    "exponential_backoff": True
                },
                "monitoring": {
                    "enable_performance_tracking": True,
                    "log_api_calls": True,
                    "alert_on_errors": True,
                    "error_threshold": 0.1
                }
            },
            "action_generation": {
                "meta": {
                    "min_roas_threshold": 2.0,
                    "max_cpa_threshold": 50.0,
                    "budget_scale_factor": 1.2,
                    "confidence_threshold": 0.6,
                    "max_daily_actions": 10,
                    "auto_optimization": True,
                    "optimization_frequency_hours": 6
                },
                "ml_config": {
                    "model_type": "ensemble",
                    "features": [
                        "roas", "cpa", "ctr", "spend_velocity",
                        "audience_overlap", "creative_fatigue"
                    ],
                    "prediction_window_hours": 24,
                    "retraining_frequency_days": 7,
                    "minimum_data_points": 100
                }
            },
            "campaign_defaults": {
                "budget_limits": {
                    "min_daily_budget": 10.0,
                    "max_daily_budget": 1000.0,
                    "min_lifetime_budget": 50.0,
                    "max_lifetime_budget": 10000.0
                },
                "targeting_constraints": {
                    "min_audience_size": 1000,
                    "max_audience_size": 50000000,
                    "age_min": 18,
                    "age_max": 65
                },
                "performance_thresholds": {
                    "min_roas": 1.5,
                    "max_cpa": 100.0,
                    "min_ctr": 0.5,
                    "frequency_cap": 3.0
                }
            },
            "security": {
                "encrypt_tokens": True,
                "token_rotation_days": 60,
                "audit_logging": True,
                "ip_whitelist": [],
                "require_https": True
            }
        }
        
        return template
    
    def save_config_template(self) -> str:
        """Save configuration template to file"""
        
        template = self.create_production_config_template()
        config_file = self.config_dir / "meta_production_template.json"
        
        with open(config_file, 'w') as f:
            json.dump(template, f, indent=2)
        
        logger.info(f"📄 Meta Ads production template saved to: {config_file}")
        return str(config_file)
    
    def create_environment_template(self) -> str:
        """Create environment variables template"""
        
        env_template = """
# Meta Ads Production Environment Variables
# Copy to .env and fill in your actual values

# ============================================
# Meta Business API Configuration
# ============================================

# Facebook App ID (from Facebook Developers)
META_APP_ID=your_facebook_app_id_here

# Facebook App Secret (keep secure!)
META_APP_SECRET=your_facebook_app_secret_here

# Long-lived User Access Token (refresh regularly)
META_ACCESS_TOKEN=your_long_lived_access_token_here

# Ad Account ID (without 'act_' prefix)
META_AD_ACCOUNT_ID=1234567890

# Facebook Page ID
META_PAGE_ID=0987654321

# Meta Pixel ID
META_PIXEL_ID=your_pixel_id_here

# Webhook Verify Token (create a random secure string)
META_WEBHOOK_VERIFY_TOKEN=your_secure_webhook_token_here

# ============================================
# Production Settings
# ============================================

# Set to 'false' to enable production mode
DUMMY_MODE=false

# Enable Meta Ads module
ENABLE_META_ADS=true

# Database URL for production
DATABASE_URL=postgresql://user:password@localhost/meta_ads_db

# Redis URL for caching (optional)
REDIS_URL=redis://localhost:6379

# ============================================
# Security & Monitoring
# ============================================

# API Security
API_SECRET_KEY=your_api_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here

# Monitoring (optional)
GRAFANA_URL=http://localhost:3000
PROMETHEUS_URL=http://localhost:9090

# Alerts (optional)
SLACK_WEBHOOK_URL=your_slack_webhook_url
EMAIL_ALERTS_TO=admin@yourcompany.com

# ============================================
# Performance Tuning
# ============================================

# Worker Configuration
MAX_WORKERS=4
WORKER_TIMEOUT=300

# Rate Limiting
META_API_RATE_LIMIT=200
META_API_BURST_LIMIT=20

# Caching
ENABLE_CACHING=true
CACHE_TTL_SECONDS=3600
"""
        
        env_file = self.config_dir / "meta_production.env.template"
        
        with open(env_file, 'w') as f:
            f.write(env_template.strip())
        
        logger.info(f"📄 Meta Ads environment template saved to: {env_file}")
        return str(env_file)
    
    def load_production_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """Load production configuration with environment variable substitution"""
        
        if config_file is None:
            config_file = self.config_dir / "meta_production.json"
        
        if not Path(config_file).exists():
            logger.warning(f"⚠️ Production config not found: {config_file}")
            logger.info("🔄 Creating template configuration...")
            self.save_config_template()
            self.create_environment_template()
            return self.create_production_config_template()
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Substitute environment variables
        config = self._substitute_env_vars(config)
        
        # Validate required variables
        validation_errors = self._validate_config(config)
        if validation_errors:
            logger.error(f"❌ Configuration validation failed: {validation_errors}")
            raise ValueError(f"Invalid configuration: {validation_errors}")
        
        return config
    
    def _substitute_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively substitute environment variables in config"""
        
        if isinstance(config, dict):
            result = {}
            for key, value in config.items():
                result[key] = self._substitute_env_vars(value)
            return result
        
        elif isinstance(config, list):
            return [self._substitute_env_vars(item) for item in config]
        
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            env_var = config[2:-1]  # Remove ${ and }
            return os.getenv(env_var, config)  # Return original if env var not found
        
        else:
            return config
    
    def _validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate production configuration"""
        
        errors = []
        
        # Required Meta API fields
        meta_config = config.get("meta_ads", {}).get("api_config", {})
        
        required_fields = [
            "app_id", "app_secret", "access_token", 
            "ad_account_id", "page_id", "pixel_id"
        ]
        
        for field in required_fields:
            value = meta_config.get(field, "")
            if not value or value.startswith("${"):
                errors.append(f"Missing or unsubstituted Meta API field: {field}")
        
        # Validate numeric ranges
        action_config = config.get("action_generation", {}).get("meta", {})
        
        min_roas = action_config.get("min_roas_threshold", 0)
        if min_roas <= 0:
            errors.append("min_roas_threshold must be > 0")
        
        max_cpa = action_config.get("max_cpa_threshold", 0)
        if max_cpa <= 0:
            errors.append("max_cpa_threshold must be > 0")
        
        # Validate budget limits
        budget_limits = config.get("campaign_defaults", {}).get("budget_limits", {})
        
        min_daily = budget_limits.get("min_daily_budget", 0)
        max_daily = budget_limits.get("max_daily_budget", 0)
        
        if min_daily >= max_daily:
            errors.append("min_daily_budget must be < max_daily_budget")
        
        return errors
    
    def create_production_setup_script(self) -> str:
        """Create setup script for production deployment"""
        
        script = """#!

# Meta Ads Production Setup Script
# This script helps set up the Meta Ads integration for production use

set -e

echo "🚀 Meta Ads Production Setup"
echo "============================"

# Check if running in production environment
if [ "$DUMMY_MODE" = "true" ]; then
    echo "⚠️  Warning: DUMMY_MODE is enabled. Set DUMMY_MODE=false for production."
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

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

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Test Meta API connectivity
echo "🔌 Testing Meta API connectivity..."

python3 -c "
import os
try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    
    app_id = os.getenv('META_APP_ID')
    app_secret = os.getenv('META_APP_SECRET')
    access_token = os.getenv('META_ACCESS_TOKEN')
    ad_account_id = os.getenv('META_AD_ACCOUNT_ID')
    
    FacebookAdsApi.init(app_id, app_secret, access_token)
    account = AdAccount(f'act_{ad_account_id}')
    
    # Test basic API call
    account_info = account.api_get(fields=['name', 'account_status'])
    print(f'✅ Connected to account: {account_info[\"name\"]} (Status: {account_info[\"account_status\"]})')
    
except Exception as e:
    print(f'❌ API connection failed: {e}')
    print('💡 Check your Meta API credentials')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Meta API connectivity test failed"
    exit 1
fi

# Create database tables (if using database)
if [ ! -z "$DATABASE_URL" ]; then
    echo "🗃️  Setting up database..."
    # Add database setup commands here
    echo "✅ Database setup completed"
fi

# Create log directories
echo "📝 Creating log directories..."
mkdir -p logs/meta_ads
chmod 755 logs/meta_ads
echo "✅ Log directories created"

# Set up systemd service (optional)
if command -v systemctl &> /dev/null; then
    echo "🔧 Setting up systemd service..."
    
    cat > /tmp/meta-ads-api.service << EOF
[Unit]
Description=Meta Ads ML API Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin:/usr/bin:/bin
ExecStart=$(pwd)/venv/bin/python -m ml_core.api_gateway
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    echo "📋 Systemd service file created at /tmp/meta-ads-api.service"
    echo "💡 Run 'sudo cp /tmp/meta-ads-api.service /etc/systemd/system/' to install"
    echo "💡 Then run 'sudo systemctl enable meta-ads-api && sudo systemctl start meta-ads-api'"
fi

echo ""
echo "🎉 Meta Ads production setup completed!"
echo ""
echo "Next steps:"
echo "1. Review the generated configuration files"
echo "2. Set up monitoring and alerting"
echo "3. Configure rate limiting and security"
echo "4. Test with a small campaign first"
echo "5. Start the API service"
echo ""
echo "🚀 Ready to launch Meta Ads automation!"
"""
        
        script_file = self.config_dir / "setup_production.sh"
        
        with open(script_file, 'w') as f:
            f.write(script.strip())
        
        # Make executable
        os.chmod(script_file, 0o755)
        
        logger.info(f"📄 Production setup script saved to: {script_file}")
        return str(script_file)

# Factory function
def create_meta_production_config() -> MetaProductionConfig:
    """Create Meta Ads production configuration manager"""
    return MetaProductionConfig()

# Initialize production configuration
def initialize_meta_production(config_file: Optional[str] = None) -> Dict[str, Any]:
    """Initialize Meta Ads for production deployment"""
    
    try:
        config_manager = create_meta_production_config()
        
        # Load production configuration
        production_config = config_manager.load_production_config(config_file)
        
        # Extract Meta-specific configuration
        meta_config = production_config.get("meta_ads", {}).get("api_config", {})
        action_config = production_config.get("action_generation", {})
        
        # Initialize Meta endpoints with production config
        from . import initialize_meta_endpoints
        
        success = initialize_meta_endpoints(meta_config, action_config)
        
        if success:
            logger.info("✅ Meta Ads production initialization completed")
            return {
                "status": "success",
                "config": production_config,
                "meta_initialized": True
            }
        else:
            logger.error("❌ Meta Ads endpoint initialization failed")
            return {
                "status": "error",
                "error": "Endpoint initialization failed",
                "meta_initialized": False
            }
    
    except Exception as e:
        logger.error(f"❌ Meta Ads production initialization failed: {e}")
        return {
            "status": "error", 
            "error": str(e),
            "meta_initialized": False
        }

if __name__ == "__main__":
    # Create all production configuration files
    config_manager = create_meta_production_config()
    
    print("📁 Creating Meta Ads production configuration files...")
    
    config_file = config_manager.save_config_template()
    env_file = config_manager.create_environment_template()
    setup_script = config_manager.create_production_setup_script()
    
    print(f"""
🎯 Meta Ads Production Setup Files Created:

📄 Configuration Template: {config_file}
🔧 Environment Template: {env_file}  
🚀 Setup Script: {setup_script}

Next steps:
1. Copy the environment template to .env and fill in your Meta API credentials
2. Review and customize the configuration template
3. Run the setup script: bash {setup_script}
4. Start the API with production configuration

💡 For production deployment, ensure DUMMY_MODE=false in your environment
""")