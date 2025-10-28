"""
Universal Project Configuration
Intelligently configures all branches and services based on project analysis
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class BranchConfig:
    """Configuration for each project branch"""
    name: str
    description: str
    main_directory: Optional[str]
    services: List[str]
    dependencies: List[str]
    env_vars: Dict[str, str]
    startup_commands: List[str]
    health_checks: List[str]
    database_requirements: List[str]
    ml_requirements: List[str]


@dataclass
class UniversalConfig:
    """Master configuration for the entire project"""
    project_name: str
    project_root: Path
    dummy_mode: bool
    active_branches: List[str]
    global_settings: Dict[str, Any]
    branch_configs: Dict[str, BranchConfig]
    cloud_endpoints: Dict[str, str]
    monitoring_config: Dict[str, Any]
    security_config: Dict[str, Any]


class IntelligentConfigGenerator:
    """Generates intelligent configuration by analyzing project structure"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.analysis_cache = {}
    
    def analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze the entire project structure"""
        if 'structure' in self.analysis_cache:
            return self.analysis_cache['structure']
        
        analysis = {
            'branches': self._detect_branches(),
            'services': self._detect_services(),
            'databases': self._detect_databases(),
            'ml_components': self._detect_ml_components(),
            'automation_systems': self._detect_automation_systems(),
            'configuration_files': self._detect_configuration_files()
        }
        
        self.analysis_cache['structure'] = analysis
        return analysis
    
    def _detect_branches(self) -> Dict[str, Dict]:
        """Detect project branches and their characteristics"""
        branches = {}
        
        # Main branch (rama) - TikTok ML System
        if (self.project_root / 'ml_core').exists():
            branches['rama'] = {
                'type': 'ml_system',
                'main_dir': str(self.project_root),
                'components': ['ml_core', 'device_farm', 'orchestration', 'monitoring'],
                'focus': 'TikTok automation with ML',
                'services': ['ml_api', 'device_farm', 'monitoring'],
                'databases': ['postgresql', 'redis'],
                'ml_models': ['yolo_screenshot', 'yolo_video', 'affinity', 'anomaly']
            }
        
        # Meta branch - Meta Ads Automation
        meta_dir = self.project_root / 'meta_automation'
        if meta_dir.exists():
            branches['meta'] = {
                'type': 'ads_automation',
                'main_dir': str(meta_dir),
                'components': ['telegram_monitor', 'meta_ads', 'gologin_integration'],
                'focus': 'Meta Ads automation via Telegram',
                'services': ['telegram_monitor', 'meta_ads_api', 'gologin_manager'],
                'databases': ['postgresql'],
                'integrations': ['telegram', 'meta_ads', 'gologin']
            }
        
        # Tele branch - Like4Like Telegram
        tele_dir = self.project_root / 'telegram_automation'
        if tele_dir.exists():
            branches['tele'] = {
                'type': 'telegram_automation',
                'main_dir': str(tele_dir),
                'components': ['telegram_bot', 'conversation_handler', 'youtube_executor'],
                'focus': 'Like4Like Telegram automation',
                'services': ['telegram_bot', 'youtube_executor'],
                'databases': ['postgresql'],
                'integrations': ['telegram', 'youtube', 'gologin']
            }
        
        return branches
    
    def _detect_services(self) -> Dict[str, Dict]:
        """Detect available services across all branches"""
        services = {}
        
        # ML API Service
        if (self.project_root / 'ml_core' / 'api' / 'main.py').exists():
            services['ml_api'] = {
                'type': 'fastapi',
                'port': 8000,
                'startup_command': ['uvicorn', 'ml_core.api.main:app', '--host', '0.0.0.0', '--port', '8000'],
                'health_check': 'http://localhost:8000/health',
                'branch': 'rama'
            }
        
        # Device Farm Service
        if (self.project_root / 'device_farm').exists():
            services['device_farm'] = {
                'type': 'python_service',
                'startup_command': ['python', '-m', 'device_farm.controllers.device_manager'],
                'branch': 'rama'
            }
        
        # Meta Automation Service
        meta_main = self.project_root / 'meta_automation' / 'main.py'
        if meta_main.exists():
            services['meta_automation'] = {
                'type': 'python_service',
                'startup_command': ['python', 'main.py'],
                'working_directory': str(self.project_root / 'meta_automation'),
                'branch': 'meta'
            }
        
        # Telegram Automation Service
        tele_main = self.project_root / 'telegram_automation' / 'main.py'
        if tele_main.exists():
            services['telegram_automation'] = {
                'type': 'python_service',
                'startup_command': ['python', 'main.py'],
                'working_directory': str(self.project_root / 'telegram_automation'),
                'branch': 'tele'
            }
        
        return services
    
    def _detect_databases(self) -> Dict[str, Dict]:
        """Detect database requirements"""
        databases = {}
        
        # Look for database schemas
        schema_files = list(self.project_root.rglob('schema.sql'))
        for schema_file in schema_files:
            db_name = schema_file.parent.parent.name
            databases[db_name] = {
                'type': 'postgresql',
                'schema_file': str(schema_file),
                'connection_string': f'postgresql://dummy:dummy@localhost:5432/{db_name}'
            }
        
        # Look for SQLite databases
        sqlite_files = list(self.project_root.rglob('*.db'))
        for db_file in sqlite_files:
            databases[db_file.stem] = {
                'type': 'sqlite',
                'file_path': str(db_file)
            }
        
        # Standard databases for branches
        if not databases:
            databases = {
                'tiktok_ml': {'type': 'postgresql', 'connection_string': 'postgresql://dummy:dummy@localhost:5432/tiktok_ml'},
                'meta_ads': {'type': 'postgresql', 'connection_string': 'postgresql://dummy:dummy@localhost:5432/meta_ads'},
                'like4like_bot': {'type': 'postgresql', 'connection_string': 'postgresql://dummy:dummy@localhost:5432/like4like_bot'},
                'redis_cache': {'type': 'redis', 'connection_string': 'redis://localhost:6379/0'}
            }
        
        return databases
    
    def _detect_ml_components(self) -> Dict[str, Dict]:
        """Detect ML model components"""
        ml_components = {}
        
        # Look for YOLO models
        model_files = list(self.project_root.rglob('*.pt'))
        for model_file in model_files:
            model_name = model_file.stem
            ml_components[model_name] = {
                'type': 'yolo',
                'file_path': str(model_file),
                'framework': 'ultralytics'
            }
        
        # Look for model configuration
        config_files = list(self.project_root.rglob('model_config.yaml'))
        if config_files:
            ml_components['config'] = {
                'type': 'configuration',
                'file_path': str(config_files[0])
            }
        
        # Default ML components for dummy mode
        if not ml_components:
            ml_components = {
                'yolo_screenshot': {'type': 'yolo', 'dummy': True, 'classes': ['button', 'text', 'image']},
                'yolo_video': {'type': 'yolo', 'dummy': True, 'classes': ['person', 'face', 'object']},
                'affinity_model': {'type': 'ml_model', 'dummy': True, 'purpose': 'engagement_scoring'},
                'anomaly_detector': {'type': 'ml_model', 'dummy': True, 'purpose': 'behavior_analysis'}
            }
        
        return ml_components
    
    def _detect_automation_systems(self) -> Dict[str, Dict]:
        """Detect automation systems and integrations"""
        automations = {}
        
        # Telegram automation
        if (self.project_root / 'meta_automation').exists() or (self.project_root / 'telegram_automation').exists():
            automations['telegram'] = {
                'type': 'telegram_integration',
                'library': 'telethon',
                'required_credentials': ['api_id', 'api_hash', 'phone']
            }
        
        # GoLogin automation
        gologin_files = list(self.project_root.rglob('*gologin*'))
        if gologin_files:
            automations['gologin'] = {
                'type': 'browser_automation',
                'service': 'gologin',
                'required_credentials': ['api_token']
            }
        
        # Selenium automation
        selenium_files = list(self.project_root.rglob('*selenium*'))
        if selenium_files:
            automations['selenium'] = {
                'type': 'web_automation',
                'framework': 'selenium',
                'browsers': ['chrome', 'firefox']
            }
        
        # Meta Ads integration
        meta_files = list(self.project_root.rglob('*meta*'))
        if meta_files:
            automations['meta_ads'] = {
                'type': 'ads_platform',
                'platform': 'meta',
                'required_credentials': ['access_token', 'app_id', 'app_secret']
            }
        
        return automations
    
    def _detect_configuration_files(self) -> Dict[str, str]:
        """Detect existing configuration files"""
        config_files = {}
        
        # Look for various config file types
        patterns = ['*.yaml', '*.yml', '*.json', '*.env*', '*.conf', '*.ini']
        for pattern in patterns:
            for config_file in self.project_root.rglob(pattern):
                if 'node_modules' not in str(config_file) and '.git' not in str(config_file):
                    config_files[config_file.name] = str(config_file)
        
        return config_files
    
    def generate_universal_config(self) -> UniversalConfig:
        """Generate comprehensive configuration for all branches"""
        analysis = self.analyze_project_structure()
        
        # Generate branch configurations
        branch_configs = {}
        for branch_name, branch_info in analysis['branches'].items():
            branch_configs[branch_name] = self._generate_branch_config(branch_name, branch_info, analysis)
        
        # Generate global configuration
        config = UniversalConfig(
            project_name="Universal Multi-Branch Automation System",
            project_root=self.project_root,
            dummy_mode=True,
            active_branches=list(analysis['branches'].keys()),
            global_settings=self._generate_global_settings(analysis),
            branch_configs=branch_configs,
            cloud_endpoints=self._generate_cloud_endpoints(analysis),
            monitoring_config=self._generate_monitoring_config(analysis),
            security_config=self._generate_security_config(analysis)
        )
        
        return config
    
    def _generate_branch_config(self, branch_name: str, branch_info: Dict, analysis: Dict) -> BranchConfig:
        """Generate configuration for a specific branch"""
        
        # Base configuration templates
        base_configs = {
            'rama': {
                'description': 'TikTok ML Automation System',
                'services': ['ml_api', 'device_farm', 'monitoring'],
                'dependencies': ['fastapi', 'uvicorn', 'ultralytics', 'selenium'],
                'startup_commands': [
                    'uvicorn ml_core.api.main:app --host 0.0.0.0 --port 8000 --reload'
                ],
                'health_checks': ['http://localhost:8000/health'],
                'database_requirements': ['postgresql', 'redis'],
                'ml_requirements': ['yolo_screenshot', 'yolo_video', 'affinity_model']
            },
            'meta': {
                'description': 'Meta Ads Automation System',
                'services': ['telegram_monitor', 'meta_ads', 'gologin_manager'],
                'dependencies': ['telethon', 'facebook-business', 'selenium'],
                'startup_commands': [
                    'python main.py'
                ],
                'health_checks': [],
                'database_requirements': ['postgresql'],
                'ml_requirements': []
            },
            'tele': {
                'description': 'Like4Like Telegram Automation',
                'services': ['telegram_bot', 'youtube_executor'],
                'dependencies': ['telethon', 'selenium', 'asyncpg'],
                'startup_commands': [
                    'python main.py'
                ],
                'health_checks': [],
                'database_requirements': ['postgresql'],
                'ml_requirements': []
            }
        }
        
        base_config = base_configs.get(branch_name, {})
        
        # Generate environment variables
        env_vars = self._generate_branch_env_vars(branch_name, branch_info, analysis)
        
        return BranchConfig(
            name=branch_name,
            description=base_config.get('description', f'{branch_name.title()} Branch'),
            main_directory=branch_info.get('main_dir'),
            services=base_config.get('services', []),
            dependencies=base_config.get('dependencies', []),
            env_vars=env_vars,
            startup_commands=base_config.get('startup_commands', []),
            health_checks=base_config.get('health_checks', []),
            database_requirements=base_config.get('database_requirements', []),
            ml_requirements=base_config.get('ml_requirements', [])
        )
    
    def _generate_branch_env_vars(self, branch_name: str, branch_info: Dict, analysis: Dict) -> Dict[str, str]:
        """Generate environment variables for a branch"""
        
        # Common environment variables
        common_env = {
            'DUMMY_MODE': 'true',
            'LOG_LEVEL': 'INFO',
            'PROJECT_ROOT': str(self.project_root),
            'BRANCH_NAME': branch_name
        }
        
        # Branch-specific environment variables
        branch_env_templates = {
            'rama': {
                'ML_API_PORT': '8000',
                'ML_API_HOST': '0.0.0.0',
                'DATABASE_URL': 'postgresql://dummy:dummy@localhost:5432/tiktok_ml',
                'REDIS_URL': 'redis://localhost:6379/0',
                'YOLO_SCREENSHOT_IMPL': 'ml_core.models.yolo_screenshot.YoloScreenshotDetector',
                'YOLO_VIDEO_IMPL': 'ml_core.models.yolo_video.YoloVideoDetector',
                'ADB_CONTROLLER_IMPL': 'device_farm.controllers.adb_controller.ADBController',
                'DEVICE_FARM_SIZE': '10',
                'MONITORING_ENABLED': 'true'
            },
            'meta': {
                'TELEGRAM_API_ID': '12345',
                'TELEGRAM_API_HASH': 'dummy_hash',
                'TELEGRAM_PHONE': '+1234567890',
                'META_ACCESS_TOKEN': 'dummy_meta_token',
                'META_APP_ID': 'dummy_app_id',
                'META_APP_SECRET': 'dummy_app_secret',
                'GOLOGIN_API_TOKEN': 'dummy_gologin_token',
                'DATABASE_URL': 'postgresql://dummy:dummy@localhost:5432/meta_ads',
                'DAILY_BUDGET_LIMIT': '100',
                'AUTO_CAMPAIGN_CREATION': 'true'
            },
            'tele': {
                'TELEGRAM_API_ID': '12345',
                'TELEGRAM_API_HASH': 'dummy_hash',
                'TELEGRAM_PHONE': '+1234567890',
                'TELEGRAM_BOT_TOKEN': 'dummy_bot_token',
                'DATABASE_URL': 'postgresql://dummy:dummy@localhost:5432/like4like_bot',
                'GOLOGIN_API_TOKEN': 'dummy_gologin_token',
                'GOLOGIN_MAX_PROFILES': '5',
                'YOUTUBE_MIN_WATCH_TIME': '30',
                'YOUTUBE_MAX_WATCH_TIME': '300',
                'YOUTUBE_MAX_ACTIONS_PER_DAY': '50',
                'YOUTUBE_ENABLE_COMMENTS': 'true',
                'SECURITY_HUMAN_DELAYS': 'true'
            }
        }
        
        branch_specific = branch_env_templates.get(branch_name, {})
        
        # Merge common and branch-specific
        return {**common_env, **branch_specific}
    
    def _generate_global_settings(self, analysis: Dict) -> Dict[str, Any]:
        """Generate global project settings"""
        return {
            'dummy_mode': True,
            'auto_wake_services': True,
            'generate_test_data': True,
            'simulation_level': 'full',
            'health_check_interval': 300,
            'metrics_collection_enabled': True,
            'cors_enabled': True,
            'api_docs_enabled': True,
            'debug_mode': True,
            'hot_reload': True
        }
    
    def _generate_cloud_endpoints(self, analysis: Dict) -> Dict[str, str]:
        """Generate cloud service endpoint configurations"""
        return {
            'postgresql': 'postgresql://dummy:dummy@localhost:5432',
            'mongodb': 'mongodb://dummy:dummy@localhost:27017',
            'redis': 'redis://localhost:6379',
            'elasticsearch': 'http://localhost:9200',
            'prometheus': 'http://localhost:9090',
            'grafana': 'http://localhost:3000',
            'webhook_notifications': 'http://localhost:3001/webhooks'
        }
    
    def _generate_monitoring_config(self, analysis: Dict) -> Dict[str, Any]:
        """Generate monitoring configuration"""
        return {
            'enabled': True,
            'health_checks': {
                'interval': 300,
                'timeout': 30,
                'retries': 3
            },
            'metrics': {
                'collection_interval': 60,
                'retention_days': 30,
                'enable_system_metrics': True,
                'enable_application_metrics': True
            },
            'alerting': {
                'enabled': True,
                'channels': ['console', 'file'],
                'thresholds': {
                    'cpu_usage': 80,
                    'memory_usage': 85,
                    'disk_usage': 90,
                    'error_rate': 5
                }
            }
        }
    
    def _generate_security_config(self, analysis: Dict) -> Dict[str, Any]:
        """Generate security configuration"""
        return {
            'dummy_api_keys': {
                'ml_api': 'dummy_development_key',
                'meta_ads': 'dummy_meta_key',
                'gologin': 'dummy_gologin_key'
            },
            'rate_limiting': {
                'enabled': True,
                'requests_per_minute': 60,
                'burst_limit': 10
            },
            'cors': {
                'enabled': True,
                'allowed_origins': ['*'],
                'allowed_methods': ['*'],
                'allowed_headers': ['*']
            },
            'authentication': {
                'enabled': False,  # Disabled in dummy mode
                'require_api_key': False
            }
        }
    
    def save_configuration(self, config: UniversalConfig, output_path: str = None):
        """Save configuration to files"""
        if output_path is None:
            output_path = self.project_root / "universal_config.json"
        
        # Convert dataclass to dict
        config_dict = asdict(config)
        
        # Convert Path objects to strings for JSON serialization
        config_dict['project_root'] = str(config.project_root)
        
        # Save main configuration
        with open(output_path, 'w') as f:
            json.dump(config_dict, f, indent=2, default=str)
        
        # Save YAML version for human readability
        yaml_path = str(output_path).replace('.json', '.yaml')
        with open(yaml_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        
        return output_path, yaml_path


# Main function for standalone usage
def main():
    """Generate universal configuration"""
    generator = IntelligentConfigGenerator()
    
    print("🔍 Analyzing project structure...")
    analysis = generator.analyze_project_structure()
    
    print(f"📊 Found {len(analysis['branches'])} branches:")
    for branch_name, branch_info in analysis['branches'].items():
        print(f"  • {branch_name}: {branch_info['focus']}")
    
    print("⚙️ Generating universal configuration...")
    config = generator.generate_universal_config()
    
    print("💾 Saving configuration files...")
    json_path, yaml_path = generator.save_configuration(config)
    
    print(f"✅ Configuration generated:")
    print(f"  • JSON: {json_path}")
    print(f"  • YAML: {yaml_path}")
    
    print("\n🚀 Ready to wake the system with:")
    print("  python scripts/cross_platform_runner.py --mode full")


if __name__ == "__main__":
    main()