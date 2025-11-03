#!/usr/bin/env python3
"""
🔧 N8N Workflow Manager - Gestión Completa de Workflows

Herramienta de línea de comandos para gestión completa de workflows N8N
- Instalación y configuración automática de N8N
- Importación de workflows del sistema
- Verificación de estados y salud
- Troubleshooting y monitoreo

Autor: Sistema de Integración N8N
Fecha: 2025-11-03
"""

import os
import sys
import json
import subprocess
import requests
import time
import argparse
from pathlib import Path
import logging
from typing import Dict, List, Any
import shutil
import yaml

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class N8NWorkflowManager:
    """Gestor completo de workflows N8N"""
    
    def __init__(self, n8n_url: str = "http://localhost:5678"):
        self.n8n_url = n8n_url
        self.base_dir = Path("/workspaces/master")
        self.workflows_dir = self.base_dir / "orchestration" / "n8n_workflows"
        self.config_dir = self.base_dir / "config"
        
        # Definir workflows del sistema
        self.system_workflows = {
            "main_orchestrator": {
                "file": "main_orchestrator.json",
                "description": "Orquestador principal del sistema",
                "webhooks": ["/webhook/main-orchestrator"],
                "priority": "HIGH"
            },
            "ml_decision_engine": {
                "file": "ml_decision_engine.json", 
                "description": "Motor de decisiones ML",
                "webhooks": ["/webhook/ml-decision"],
                "priority": "HIGH"
            },
            "device_farm_trigger": {
                "file": "device_farm_trigger.json",
                "description": "Trigger para device farm",
                "webhooks": ["/webhook/device-farm"],
                "priority": "MEDIUM"
            },
            "viral_content_generator": {
                "file": "viral_content_generator.json",
                "description": "Generador de contenido viral",
                "webhooks": ["/webhook/viral-content"],
                "priority": "MEDIUM"
            },
            "meta_ads_orchestrator": {
                "file": "meta_ads_orchestrator.json",
                "description": "Orquestador de Meta Ads",
                "webhooks": ["/webhook/meta-ads"],
                "priority": "HIGH"
            },
            "community_management_auto": {
                "file": "community_management_auto.json",
                "description": "Community management automatizado",
                "webhooks": ["/webhook/community-management"],
                "priority": "CRITICAL"
            }
        }
    
    def check_n8n_installation(self) -> bool:
        """Verificar si N8N está instalado"""
        try:
            result = subprocess.run(['n8n', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f"✅ N8N found: {version}")
                return True
            else:
                logger.warning("⚠️ N8N command not found")
                return False
        except FileNotFoundError:
            logger.warning("⚠️ N8N not installed")
            return False
    
    def install_n8n(self) -> bool:
        """Instalar N8N globalmente"""
        try:
            logger.info("📦 Installing N8N...")
            
            # Verificar si npm está disponible
            npm_check = subprocess.run(['npm', '--version'], capture_output=True)
            if npm_check.returncode != 0:
                logger.error("❌ npm not found. Please install Node.js first")
                return False
            
            # Instalar N8N
            install_cmd = ['npm', 'install', '-g', 'n8n']
            result = subprocess.run(install_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ N8N installed successfully")
                return True
            else:
                logger.error(f"❌ N8N installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error installing N8N: {e}")
            return False
    
    def start_n8n(self, background: bool = True) -> bool:
        """Iniciar N8N server"""
        try:
            if self.is_n8n_running():
                logger.info("✅ N8N is already running")
                return True
            
            logger.info("🚀 Starting N8N server...")
            
            # Configurar variables de entorno
            env = os.environ.copy()
            env.update({
                'N8N_BASIC_AUTH_ACTIVE': 'false',
                'N8N_HOST': '0.0.0.0',
                'N8N_PORT': '5678',
                'N8N_PROTOCOL': 'http',
                'WEBHOOK_URL': 'http://localhost:5678',
                'GENERIC_TIMEZONE': 'America/Mexico_City'
            })
            
            if background:
                # Ejecutar en background
                subprocess.Popen(['n8n', 'start'], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # Esperar a que inicie
                for i in range(30):  # 30 segundos timeout
                    time.sleep(1)
                    if self.is_n8n_running():
                        logger.info("✅ N8N started successfully")
                        return True
                
                logger.error("❌ N8N failed to start in time")
                return False
            else:
                # Ejecutar en foreground
                subprocess.run(['n8n', 'start'], env=env)
                return True
                
        except Exception as e:
            logger.error(f"❌ Error starting N8N: {e}")
            return False
    
    def is_n8n_running(self) -> bool:
        """Verificar si N8N está ejecutándose"""
        try:
            response = requests.get(f"{self.n8n_url}/healthz", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def stop_n8n(self) -> bool:
        """Detener N8N server"""
        try:
            # Buscar proceso N8N
            result = subprocess.run(['pkill', '-f', 'n8n'], capture_output=True)
            
            if result.returncode == 0:
                logger.info("✅ N8N stopped")
                return True
            else:
                logger.warning("⚠️ No N8N process found")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error stopping N8N: {e}")
            return False
    
    def create_workflow_templates(self):
        """Crear templates de workflows del sistema"""
        logger.info("📝 Creating workflow templates...")
        
        # Crear directorio si no existe
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        
        for workflow_name, config in self.system_workflows.items():
            workflow_file = self.workflows_dir / config["file"]
            
            if not workflow_file.exists():
                # Template básico de workflow
                template = {
                    "name": workflow_name,
                    "nodes": [
                        {
                            "name": "Webhook",
                            "type": "n8n-nodes-base.webhook",
                            "typeVersion": 1,
                            "position": [250, 300],
                            "webhookId": workflow_name.replace("_", "-"),
                            "parameters": {
                                "httpMethod": "POST",
                                "path": config["webhooks"][0].replace("/webhook/", ""),
                                "responseMode": "responseNode",
                                "options": {}
                            }
                        },
                        {
                            "name": "Process Data",
                            "type": "n8n-nodes-base.function",
                            "typeVersion": 1,
                            "position": [450, 300],
                            "parameters": {
                                "functionCode": f"""
// {config['description']}
// Prioridad: {config['priority']}

const inputData = $json;
console.log('Received data:', inputData);

// Procesamiento específico del workflow
const processedData = {{
    workflow: '{workflow_name}',
    timestamp: new Date().toISOString(),
    input: inputData,
    status: 'processing',
    priority: '{config['priority']}'
}};

return processedData;
"""
                            }
                        },
                        {
                            "name": "Response",
                            "type": "n8n-nodes-base.respondToWebhook",
                            "typeVersion": 1,
                            "position": [650, 300],
                            "parameters": {
                                "respondWith": "json",
                                "responseBody": "={{ {{ \\"success\\": true, \\"workflow\\": \\"{workflow_name}\\", \\"timestamp\\": $json.timestamp }} }}"
                            }
                        }
                    ],
                    "connections": {
                        "Webhook": {
                            "main": [
                                [
                                    {
                                        "node": "Process Data",
                                        "type": "main",
                                        "index": 0
                                    }
                                ]
                            ]
                        },
                        "Process Data": {
                            "main": [
                                [
                                    {
                                        "node": "Response", 
                                        "type": "main",
                                        "index": 0
                                    }
                                ]
                            ]
                        }
                    },
                    "active": True,
                    "settings": {},
                    "id": workflow_name
                }
                
                # Guardar template
                with open(workflow_file, 'w') as f:
                    json.dump(template, f, indent=2)
                
                logger.info(f"✅ Created workflow template: {workflow_file}")
            else:
                logger.info(f"📋 Workflow template exists: {workflow_file}")
    
    def import_workflows(self) -> bool:
        """Importar workflows al servidor N8N"""
        if not self.is_n8n_running():
            logger.error("❌ N8N is not running. Start N8N first.")
            return False
        
        logger.info("📥 Importing workflows to N8N...")
        
        success_count = 0
        total_count = len(self.system_workflows)
        
        for workflow_name, config in self.system_workflows.items():
            workflow_file = self.workflows_dir / config["file"]
            
            if workflow_file.exists():
                try:
                    with open(workflow_file, 'r') as f:
                        workflow_data = json.load(f)
                    
                    # Importar workflow via API
                    response = requests.post(
                        f"{self.n8n_url}/api/v1/workflows",
                        json=workflow_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if response.status_code in [200, 201]:
                        logger.info(f"✅ Imported workflow: {workflow_name}")
                        success_count += 1
                    else:
                        logger.warning(f"⚠️ Failed to import {workflow_name}: {response.status_code}")
                        
                except Exception as e:
                    logger.error(f"❌ Error importing {workflow_name}: {e}")
            else:
                logger.warning(f"⚠️ Workflow file not found: {workflow_file}")
        
        logger.info(f"📊 Import complete: {success_count}/{total_count} workflows")
        return success_count > 0
    
    def list_workflows(self) -> List[Dict]:
        """Listar workflows activos en N8N"""
        if not self.is_n8n_running():
            logger.error("❌ N8N is not running")
            return []
        
        try:
            response = requests.get(f"{self.n8n_url}/api/v1/workflows")
            
            if response.status_code == 200:
                workflows = response.json()
                logger.info(f"📋 Found {len(workflows)} workflows")
                
                for workflow in workflows:
                    status = "✅ Active" if workflow.get('active') else "❌ Inactive"
                    logger.info(f"  - {workflow.get('name', 'Unknown')}: {status}")
                
                return workflows
            else:
                logger.error(f"❌ Failed to list workflows: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error listing workflows: {e}")
            return []
    
    def activate_all_workflows(self) -> bool:
        """Activar todos los workflows del sistema"""
        if not self.is_n8n_running():
            logger.error("❌ N8N is not running")
            return False
        
        try:
            workflows = self.list_workflows()
            activated = 0
            
            for workflow in workflows:
                workflow_id = workflow.get('id')
                if workflow_id and not workflow.get('active'):
                    
                    response = requests.patch(
                        f"{self.n8n_url}/api/v1/workflows/{workflow_id}",
                        json={"active": True}
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"✅ Activated: {workflow.get('name', workflow_id)}")
                        activated += 1
                    else:
                        logger.warning(f"⚠️ Failed to activate: {workflow.get('name', workflow_id)}")
            
            logger.info(f"🔥 Activated {activated} workflows")
            return activated > 0
            
        except Exception as e:
            logger.error(f"❌ Error activating workflows: {e}")
            return False
    
    def test_webhooks(self) -> bool:
        """Probar todos los webhooks del sistema"""
        logger.info("🧪 Testing system webhooks...")
        
        test_payload = {
            "test": True,
            "timestamp": time.time(),
            "source": "n8n_workflow_manager"
        }
        
        success_count = 0
        total_count = 0
        
        for workflow_name, config in self.system_workflows.items():
            for webhook_path in config["webhooks"]:
                total_count += 1
                webhook_url = f"{self.n8n_url}{webhook_path}"
                
                try:
                    response = requests.post(webhook_url, json=test_payload, timeout=10)
                    
                    if response.status_code in [200, 201]:
                        logger.info(f"✅ Webhook OK: {webhook_path}")
                        success_count += 1
                    else:
                        logger.warning(f"⚠️ Webhook failed: {webhook_path} ({response.status_code})")
                        
                except Exception as e:
                    logger.error(f"❌ Webhook error: {webhook_path} - {e}")
        
        logger.info(f"🎯 Webhook test results: {success_count}/{total_count} passed")
        return success_count == total_count
    
    def health_check(self) -> Dict[str, Any]:
        """Verificación completa de salud del sistema"""
        logger.info("🏥 Performing complete health check...")
        
        health_status = {
            "timestamp": time.time(),
            "n8n_installed": self.check_n8n_installation(),
            "n8n_running": self.is_n8n_running(),
            "workflows_count": 0,
            "active_workflows": 0,
            "webhook_tests": 0,
            "overall_status": "UNKNOWN"
        }
        
        if health_status["n8n_running"]:
            workflows = self.list_workflows()
            health_status["workflows_count"] = len(workflows)
            health_status["active_workflows"] = len([w for w in workflows if w.get('active')])
            
            # Test webhooks if running
            if self.test_webhooks():
                health_status["webhook_tests"] = len([w for config in self.system_workflows.values() for w in config["webhooks"]])
        
        # Determinar estado general
        if (health_status["n8n_installed"] and 
            health_status["n8n_running"] and 
            health_status["active_workflows"] > 0):
            health_status["overall_status"] = "HEALTHY"
        elif health_status["n8n_running"]:
            health_status["overall_status"] = "PARTIAL"
        else:
            health_status["overall_status"] = "DOWN"
        
        # Log resumen
        status_emoji = {"HEALTHY": "✅", "PARTIAL": "⚠️", "DOWN": "❌"}
        logger.info(f"{status_emoji.get(health_status['overall_status'])} Health Status: {health_status['overall_status']}")
        
        return health_status

def main():
    """CLI principal del N8N Workflow Manager"""
    parser = argparse.ArgumentParser(description="N8N Workflow Manager - Gestión completa de workflows")
    
    parser.add_argument('action', choices=[
        'install', 'start', 'stop', 'status', 'create-templates', 
        'import', 'list', 'activate', 'test', 'health', 'setup'
    ], help='Acción a ejecutar')
    
    parser.add_argument('--url', default='http://localhost:5678', help='URL del servidor N8N')
    parser.add_argument('--background', action='store_true', help='Ejecutar N8N en background')
    parser.add_argument('--force', action='store_true', help='Forzar operación')
    
    args = parser.parse_args()
    
    # Inicializar manager
    manager = N8NWorkflowManager(args.url)
    
    if args.action == 'install':
        success = manager.install_n8n()
        sys.exit(0 if success else 1)
        
    elif args.action == 'start':
        success = manager.start_n8n(args.background)
        sys.exit(0 if success else 1)
        
    elif args.action == 'stop':
        success = manager.stop_n8n()
        sys.exit(0 if success else 1)
        
    elif args.action == 'status':
        running = manager.is_n8n_running()
        print(f"N8N Status: {'✅ Running' if running else '❌ Not running'}")
        sys.exit(0 if running else 1)
        
    elif args.action == 'create-templates':
        manager.create_workflow_templates()
        
    elif args.action == 'import':
        success = manager.import_workflows()
        sys.exit(0 if success else 1)
        
    elif args.action == 'list':
        manager.list_workflows()
        
    elif args.action == 'activate':
        success = manager.activate_all_workflows()
        sys.exit(0 if success else 1)
        
    elif args.action == 'test':
        success = manager.test_webhooks()
        sys.exit(0 if success else 1)
        
    elif args.action == 'health':
        health = manager.health_check()
        print(json.dumps(health, indent=2))
        sys.exit(0 if health["overall_status"] == "HEALTHY" else 1)
        
    elif args.action == 'setup':
        # Setup completo
        logger.info("🚀 Performing complete N8N setup...")
        
        steps = [
            ("Installing N8N", lambda: manager.install_n8n()),
            ("Creating workflow templates", lambda: manager.create_workflow_templates() or True),
            ("Starting N8N", lambda: manager.start_n8n(True)),
            ("Importing workflows", lambda: manager.import_workflows()),
            ("Activating workflows", lambda: manager.activate_all_workflows()),
            ("Testing webhooks", lambda: manager.test_webhooks())
        ]
        
        for step_name, step_func in steps:
            logger.info(f"▶️ {step_name}...")
            try:
                success = step_func()
                if success:
                    logger.info(f"✅ {step_name} completed")
                else:
                    logger.error(f"❌ {step_name} failed")
                    if not args.force:
                        sys.exit(1)
            except Exception as e:
                logger.error(f"❌ {step_name} error: {e}")
                if not args.force:
                    sys.exit(1)
        
        # Verificación final
        health = manager.health_check()
        if health["overall_status"] == "HEALTHY":
            logger.info("🎉 N8N setup completed successfully!")
            sys.exit(0)
        else:
            logger.error("⚠️ Setup completed with issues")
            sys.exit(1)

if __name__ == "__main__":
    main()