#!/usr/bin/env python3
"""
Universal System Validator
Validates that the entire dummy mode ecosystem is functioning correctly
"""

import asyncio
import json
import logging
import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import aiohttp
import sqlite3
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SystemValidator:
    """Validates the entire universal dummy system"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.validation_results = {}
        self.errors = []
        self.warnings = []
    
    async def validate_entire_system(self) -> Dict[str, Any]:
        """Run comprehensive system validation"""
        logger.info("🔍 Starting Universal System Validation...")
        
        validation_tasks = [
            ("Project Structure", self.validate_project_structure()),
            ("Configuration Files", self.validate_configuration_files()),
            ("Environment Variables", self.validate_environment_variables()),
            ("Mock Databases", self.validate_mock_databases()),
            ("ML Models", self.validate_ml_models()),
            ("Scripts and Executables", self.validate_scripts()),
            ("Service Health", self.validate_service_health()),
            ("API Endpoints", self.validate_api_endpoints()),
            ("Branch Compatibility", self.validate_branch_compatibility()),
            ("Documentation", self.validate_documentation())
        ]
        
        for category, task in validation_tasks:
            try:
                logger.info(f"🔧 Validating {category}...")
                result = await task
                self.validation_results[category] = result
                
                if result.get('status') == 'pass':
                    logger.info(f"✅ {category}: PASSED")
                elif result.get('status') == 'warning':
                    logger.warning(f"⚠️ {category}: WARNINGS")
                    self.warnings.extend(result.get('warnings', []))
                else:
                    logger.error(f"❌ {category}: FAILED")
                    self.errors.extend(result.get('errors', []))
                    
            except Exception as e:
                logger.error(f"❌ {category}: ERROR - {e}")
                self.errors.append(f"{category}: {str(e)}")
                self.validation_results[category] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Generate final report
        report = self.generate_validation_report()
        await self.save_validation_report(report)
        
        return report
    
    async def validate_project_structure(self) -> Dict[str, Any]:
        """Validate project directory structure"""
        required_files = [
            'awakener.py',
            'wake.sh',
            'config_generator.py',
            'Makefile',
            'README_UNIVERSAL.md',
            '.env.universal'
        ]
        
        required_dirs = [
            'ml_core',
            'device_farm', 
            'config',
            'data',
            'logs'
        ]
        
        optional_dirs = [
            'meta_automation',
            'telegram_automation',
            'data/mock_databases',
            'data/models'
        ]
        
        missing_files = []
        missing_dirs = []
        warnings = []
        
        # Check required files
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        # Check required directories
        for dir_path in required_dirs:
            if not (self.project_root / dir_path).exists():
                missing_dirs.append(dir_path)
        
        # Check optional directories
        for dir_path in optional_dirs:
            if not (self.project_root / dir_path).exists():
                warnings.append(f"Optional directory missing: {dir_path}")
        
        # Check executability
        executable_files = ['awakener.py', 'wake.sh']
        for file_path in executable_files:
            full_path = self.project_root / file_path
            if full_path.exists() and not os.access(full_path, os.X_OK):
                warnings.append(f"File not executable: {file_path}")
        
        status = 'pass'
        if missing_files or missing_dirs:
            status = 'fail'
        elif warnings:
            status = 'warning'
        
        return {
            'status': status,
            'missing_files': missing_files,
            'missing_dirs': missing_dirs,
            'warnings': warnings,
            'total_files_checked': len(required_files),
            'total_dirs_checked': len(required_dirs) + len(optional_dirs)
        }
    
    async def validate_configuration_files(self) -> Dict[str, Any]:
        """Validate configuration files"""
        config_files = [
            '.env.universal',
            'universal_config.json',
            'universal_config.yaml'
        ]
        
        results = {}
        errors = []
        warnings = []
        
        for config_file in config_files:
            file_path = self.project_root / config_file
            
            if not file_path.exists():
                if config_file == '.env.universal':
                    errors.append(f"Critical config missing: {config_file}")
                else:
                    warnings.append(f"Config file missing (can be generated): {config_file}")
                continue
            
            # Validate file content
            try:
                if config_file.endswith('.json'):
                    with open(file_path) as f:
                        data = json.load(f)
                        results[config_file] = {
                            'valid_json': True,
                            'entries': len(data) if isinstance(data, dict) else 0
                        }
                elif config_file.endswith('.env') or config_file == '.env.universal':
                    with open(file_path) as f:
                        lines = f.readlines()
                        env_vars = [line for line in lines if '=' in line and not line.strip().startswith('#')]
                        results[config_file] = {
                            'total_lines': len(lines),
                            'env_variables': len(env_vars)
                        }
            except Exception as e:
                errors.append(f"Error reading {config_file}: {str(e)}")
        
        status = 'fail' if errors else ('warning' if warnings else 'pass')
        
        return {
            'status': status,
            'results': results,
            'errors': errors,
            'warnings': warnings
        }
    
    async def validate_environment_variables(self) -> Dict[str, Any]:
        """Validate environment variable configuration"""
        critical_env_vars = [
            'DUMMY_MODE',
            'PROJECT_ROOT',
            'LOG_LEVEL'
        ]
        
        branch_env_vars = {
            'rama': ['RAMA_ML_API_PORT', 'RAMA_DATABASE_URL'],
            'meta': ['META_TELEGRAM_API_ID', 'META_DATABASE_URL'],
            'tele': ['TELE_TELEGRAM_API_ID', 'TELE_DATABASE_URL']
        }
        
        missing_vars = []
        warnings = []
        
        # Load environment from .env.universal if exists
        env_file = self.project_root / '.env.universal'
        env_vars = {}
        
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        env_vars[key] = value
        
        # Check critical variables
        for var in critical_env_vars:
            if var not in env_vars and var not in os.environ:
                missing_vars.append(var)
        
        # Check branch variables
        for branch, vars_list in branch_env_vars.items():
            branch_missing = []
            for var in vars_list:
                if var not in env_vars and var not in os.environ:
                    branch_missing.append(var)
            
            if branch_missing:
                warnings.append(f"Branch {branch} missing variables: {branch_missing}")
        
        # Check dummy mode consistency
        dummy_mode = env_vars.get('DUMMY_MODE', os.environ.get('DUMMY_MODE', 'true'))
        if dummy_mode.lower() not in ['true', '1', 'yes', 'on']:
            warnings.append("DUMMY_MODE is not enabled - system may not work in production mode")
        
        status = 'fail' if missing_vars else ('warning' if warnings else 'pass')
        
        return {
            'status': status,
            'total_env_vars': len(env_vars),
            'missing_critical': missing_vars,
            'warnings': warnings,
            'dummy_mode_enabled': dummy_mode.lower() in ['true', '1', 'yes', 'on']
        }
    
    async def validate_mock_databases(self) -> Dict[str, Any]:
        """Validate mock database setup"""
        db_dir = self.project_root / 'data' / 'mock_databases'
        
        if not db_dir.exists():
            return {
                'status': 'fail',
                'error': 'Mock databases directory does not exist'
            }
        
        expected_dbs = [
            'postgresql.db',
            'mongodb_collections',
            'redis_cache.json'
        ]
        
        db_status = {}
        errors = []
        warnings = []
        
        for db_name in expected_dbs:
            db_path = db_dir / db_name
            
            if not db_path.exists():
                warnings.append(f"Mock database missing: {db_name}")
                continue
            
            try:
                if db_name.endswith('.db'):
                    # Validate SQLite database
                    conn = sqlite3.connect(str(db_path))
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    conn.close()
                    
                    db_status[db_name] = {
                        'type': 'sqlite',
                        'tables': len(tables),
                        'valid': True
                    }
                
                elif db_name.endswith('.json'):
                    # Validate JSON database
                    with open(db_path) as f:
                        data = json.load(f)
                        db_status[db_name] = {
                            'type': 'json',
                            'entries': len(data) if isinstance(data, dict) else 0,
                            'valid': True
                        }
                
                elif db_path.is_dir():
                    # Validate directory-based database
                    files = list(db_path.glob('*.json'))
                    db_status[db_name] = {
                        'type': 'directory',
                        'collections': len(files),
                        'valid': True
                    }
                    
            except Exception as e:
                errors.append(f"Error validating {db_name}: {str(e)}")
                db_status[db_name] = {
                    'valid': False,
                    'error': str(e)
                }
        
        status = 'fail' if errors else ('warning' if warnings else 'pass')
        
        return {
            'status': status,
            'databases': db_status,
            'errors': errors,
            'warnings': warnings
        }
    
    async def validate_ml_models(self) -> Dict[str, Any]:
        """Validate ML model setup"""
        models_dir = self.project_root / 'data' / 'models' / 'mock_ultralytics'
        
        if not models_dir.exists():
            return {
                'status': 'warning',
                'warning': 'ML models directory does not exist (will be created on first run)'
            }
        
        expected_models = [
            'yolov8n_screenshot.pt',
            'yolov8s_video.pt',
            'yolov8m_detection.pt',
            'custom_tiktok.pt'
        ]
        
        model_status = {}
        warnings = []
        
        for model_name in expected_models:
            model_path = models_dir / model_name
            config_path = models_dir / f"{model_name}.config.json"
            
            if model_path.exists():
                model_status[model_name] = {
                    'exists': True,
                    'size': model_path.stat().st_size,
                    'has_config': config_path.exists()
                }
                
                if not config_path.exists():
                    warnings.append(f"Model config missing for {model_name}")
            else:
                warnings.append(f"Mock model missing: {model_name}")
                model_status[model_name] = {'exists': False}
        
        # Check training data directory
        training_dir = models_dir / 'training_data'
        training_datasets = 0
        if training_dir.exists():
            training_datasets = len(list(training_dir.iterdir()))
        
        status = 'warning' if warnings else 'pass'
        
        return {
            'status': status,
            'models': model_status,
            'training_datasets': training_datasets,
            'warnings': warnings
        }
    
    async def validate_scripts(self) -> Dict[str, Any]:
        """Validate scripts and executables"""
        scripts = [
            ('awakener.py', True),
            ('wake.sh', True),
            ('config_generator.py', False),
            ('start.sh', False)
        ]
        
        script_status = {}
        errors = []
        warnings = []
        
        for script_name, must_be_executable in scripts:
            script_path = self.project_root / script_name
            
            if not script_path.exists():
                if script_name in ['awakener.py', 'wake.sh']:
                    errors.append(f"Critical script missing: {script_name}")
                else:
                    warnings.append(f"Optional script missing: {script_name}")
                continue
            
            is_executable = os.access(script_path, os.X_OK)
            
            script_status[script_name] = {
                'exists': True,
                'executable': is_executable,
                'size': script_path.stat().st_size
            }
            
            if must_be_executable and not is_executable:
                warnings.append(f"Script not executable: {script_name}")
        
        status = 'fail' if errors else ('warning' if warnings else 'pass')
        
        return {
            'status': status,
            'scripts': script_status,
            'errors': errors,
            'warnings': warnings
        }
    
    async def validate_service_health(self) -> Dict[str, Any]:
        """Validate that services can start and are healthy"""
        # This is a basic check - services might not be running
        service_ports = {
            'ml_api': 8000,
            'meta_automation': 8001,
            'telegram_automation': 8002
        }
        
        service_status = {}
        warnings = []
        
        for service_name, port in service_ports.items():
            try:
                # Check if port is available (not currently in use)
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    service_status[service_name] = {
                        'port': port,
                        'status': 'running'
                    }
                else:
                    service_status[service_name] = {
                        'port': port,
                        'status': 'available'
                    }
                    
            except Exception as e:
                warnings.append(f"Could not check service {service_name}: {str(e)}")
                service_status[service_name] = {
                    'port': port,
                    'status': 'unknown',
                    'error': str(e)
                }
        
        return {
            'status': 'pass',
            'services': service_status,
            'warnings': warnings
        }
    
    async def validate_api_endpoints(self) -> Dict[str, Any]:
        """Validate API endpoints (if services are running)"""
        endpoints = [
            'http://localhost:8000/health',
            'http://localhost:8000/',
            'http://localhost:8000/docs'
        ]
        
        endpoint_status = {}
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            for endpoint in endpoints:
                try:
                    async with session.get(endpoint) as response:
                        endpoint_status[endpoint] = {
                            'status_code': response.status,
                            'reachable': True,
                            'response_time': None  # Could measure this
                        }
                except aiohttp.ClientError as e:
                    endpoint_status[endpoint] = {
                        'reachable': False,
                        'error': str(e)
                    }
                except Exception as e:
                    endpoint_status[endpoint] = {
                        'reachable': False,
                        'error': f"Unexpected error: {str(e)}"
                    }
        
        reachable_count = sum(1 for status in endpoint_status.values() if status.get('reachable'))
        
        return {
            'status': 'pass',  # APIs might not be running, that's OK
            'endpoints': endpoint_status,
            'reachable_count': reachable_count,
            'total_endpoints': len(endpoints)
        }
    
    async def validate_branch_compatibility(self) -> Dict[str, Any]:
        """Validate that all branches are compatible"""
        branches = ['rama', 'meta', 'tele']
        
        branch_status = {}
        
        for branch in branches:
            branch_dir = None
            
            if branch == 'rama':
                branch_dir = self.project_root
                required_components = ['ml_core', 'device_farm']
            elif branch == 'meta':
                branch_dir = self.project_root / 'meta_automation'
                required_components = ['main.py', 'telegram_monitor.py']
            elif branch == 'tele':
                branch_dir = self.project_root / 'telegram_automation'
                required_components = ['main.py', 'bot', 'database']
            
            if branch_dir and branch_dir.exists():
                missing_components = []
                for component in required_components:
                    if not (branch_dir / component).exists():
                        missing_components.append(component)
                
                branch_status[branch] = {
                    'exists': True,
                    'missing_components': missing_components,
                    'complete': len(missing_components) == 0
                }
            else:
                branch_status[branch] = {
                    'exists': False
                }
        
        complete_branches = sum(1 for status in branch_status.values() if status.get('complete'))
        
        return {
            'status': 'pass',
            'branches': branch_status,
            'complete_branches': complete_branches,
            'total_branches': len(branches)
        }
    
    async def validate_documentation(self) -> Dict[str, Any]:
        """Validate documentation files"""
        doc_files = [
            'README.md',
            'README_UNIVERSAL.md',
            'CHANGELOG.md'
        ]
        
        doc_status = {}
        warnings = []
        
        for doc_file in doc_files:
            doc_path = self.project_root / doc_file
            
            if doc_path.exists():
                with open(doc_path) as f:
                    content = f.read()
                    doc_status[doc_file] = {
                        'exists': True,
                        'size': len(content),
                        'lines': len(content.split('\n'))
                    }
            else:
                if doc_file == 'README_UNIVERSAL.md':
                    warnings.append(f"Important documentation missing: {doc_file}")
                else:
                    warnings.append(f"Documentation missing: {doc_file}")
                doc_status[doc_file] = {'exists': False}
        
        status = 'warning' if warnings else 'pass'
        
        return {
            'status': status,
            'documentation': doc_status,
            'warnings': warnings
        }
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        total_categories = len(self.validation_results)
        passed_categories = sum(1 for result in self.validation_results.values() 
                               if result.get('status') == 'pass')
        warning_categories = sum(1 for result in self.validation_results.values() 
                                if result.get('status') == 'warning')
        failed_categories = sum(1 for result in self.validation_results.values() 
                               if result.get('status') in ['fail', 'error'])
        
        overall_status = 'pass'
        if failed_categories > 0:
            overall_status = 'fail'
        elif warning_categories > 0:
            overall_status = 'warning'
        
        report = {
            'validation_timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'overall_status': overall_status,
            'summary': {
                'total_categories': total_categories,
                'passed': passed_categories,
                'warnings': warning_categories,
                'failed': failed_categories,
                'success_rate': round((passed_categories / total_categories) * 100, 2) if total_categories > 0 else 0
            },
            'categories': self.validation_results,
            'errors': self.errors,
            'warnings': self.warnings,
            'recommendations': self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        if self.errors:
            recommendations.append("🔴 Critical issues found - system may not function properly")
            recommendations.append("Run 'make setup' to initialize missing components")
        
        if self.warnings:
            recommendations.append("🟡 Some optional components are missing")
            recommendations.append("Run 'make config' to generate missing configuration files")
        
        # Specific recommendations based on validation results
        project_structure = self.validation_results.get('Project Structure', {})
        if project_structure.get('missing_files'):
            recommendations.append("Run the system setup to create missing files")
        
        mock_databases = self.validation_results.get('Mock Databases', {})
        if mock_databases.get('status') != 'pass':
            recommendations.append("Run 'python3 awakener.py --mode basic' to create mock databases")
        
        ml_models = self.validation_results.get('ML Models', {})
        if ml_models.get('status') != 'pass':
            recommendations.append("Mock ML models will be created automatically on first run")
        
        if not self.errors and not self.warnings:
            recommendations.append("✅ System is ready! Use 'make wake' to start")
        
        return recommendations
    
    async def save_validation_report(self, report: Dict[str, Any]):
        """Save validation report to file"""
        reports_dir = self.project_root / 'logs'
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = reports_dir / f'system_validation_{timestamp}.json'
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📄 Validation report saved: {report_file}")
    
    def print_validation_summary(self, report: Dict[str, Any]):
        """Print a human-readable validation summary"""
        print("\n" + "="*80)
        print("🔍 UNIVERSAL SYSTEM VALIDATION REPORT")
        print("="*80)
        print(f"📅 Timestamp: {report['validation_timestamp']}")
        print(f"📁 Project Root: {report['project_root']}")
        print(f"🎯 Overall Status: {report['overall_status'].upper()}")
        print()
        
        summary = report['summary']
        print("📊 SUMMARY:")
        print(f"  Total Categories: {summary['total_categories']}")
        print(f"  ✅ Passed: {summary['passed']}")
        print(f"  ⚠️  Warnings: {summary['warnings']}")
        print(f"  ❌ Failed: {summary['failed']}")
        print(f"  📈 Success Rate: {summary['success_rate']}%")
        print()
        
        # Category details
        print("📋 CATEGORY RESULTS:")
        for category, result in report['categories'].items():
            status_icon = {
                'pass': '✅',
                'warning': '⚠️',
                'fail': '❌',
                'error': '🔥'
            }.get(result.get('status', 'unknown'), '❓')
            
            print(f"  {status_icon} {category}: {result.get('status', 'unknown').upper()}")
        
        print()
        
        # Errors and warnings
        if report['errors']:
            print("🔴 ERRORS:")
            for error in report['errors']:
                print(f"  • {error}")
            print()
        
        if report['warnings']:
            print("🟡 WARNINGS:")
            for warning in report['warnings']:
                print(f"  • {warning}")
            print()
        
        # Recommendations
        if report['recommendations']:
            print("💡 RECOMMENDATIONS:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
        
        print("\n" + "="*80)


async def main():
    """Main validation entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Universal System Validator')
    parser.add_argument('--project-root', help='Project root directory')
    parser.add_argument('--save-report', action='store_true', help='Save detailed report to file')
    parser.add_argument('--quiet', action='store_true', help='Only show summary')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Create validator
    validator = SystemValidator(project_root=args.project_root)
    
    try:
        # Run validation
        report = await validator.validate_entire_system()
        
        # Print summary
        validator.print_validation_summary(report)
        
        # Exit with appropriate code
        if report['overall_status'] == 'fail':
            sys.exit(1)
        elif report['overall_status'] == 'warning':
            sys.exit(2)
        else:
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"❌ Validation failed with error: {e}")
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())