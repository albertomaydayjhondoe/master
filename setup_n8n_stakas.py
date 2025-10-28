#!/usr/bin/env python3
"""
🚀 Script de Setup Automático - n8n Stakas MVP
Configura automáticamente el entorno n8n para UCgohgqLVu1QPdfa64Vkrgeg
"""

import os
import sys
import json
import time
import requests
import webbrowser
from pathlib import Path
from typing import Dict, Any

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m' 
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}🚀 {text}{Colors.ENDC}")

def print_success(text: str):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

class N8nStakasSetup:
    def __init__(self):
        self.n8n_url = "http://localhost:5678"
        self.n8n_user = "stakas_admin"
        self.n8n_password = "StakasN8N2024!"
        self.session = requests.Session()
        self.credentials = {}
        
    def check_n8n_running(self) -> bool:
        """Verifica si n8n está corriendo"""
        try:
            response = requests.get(f"{self.n8n_url}/healthz", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_n8n_if_needed(self):
        """Inicia n8n si no está corriendo"""
        print_header("Verificando n8n...")
        
        if self.check_n8n_running():
            print_success("n8n ya está corriendo en http://localhost:5678")
            return
            
        print_info("n8n no está corriendo. Iniciando...")
        
        # Intentar iniciar con docker-compose
        import subprocess
        try:
            result = subprocess.run([
                "docker-compose", "-f", "docker-compose.n8n.yml", "up", "-d"
            ], capture_output=True, text=True, cwd=Path.cwd())
            
            if result.returncode == 0:
                print_success("n8n iniciado con docker-compose")
                
                # Esperar a que n8n esté listo
                print_info("Esperando a que n8n esté listo...")
                for i in range(30):
                    if self.check_n8n_running():
                        print_success(f"n8n listo después de {i*2} segundos")
                        break
                    time.sleep(2)
                else:
                    print_error("n8n no respondió después de 60 segundos")
                    return False
            else:
                print_error(f"Error iniciando n8n: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print_error("docker-compose no encontrado. Instala Docker Desktop.")
            return False
            
        return True

    def login_n8n(self) -> bool:
        """Login en n8n y obtener cookies de sesión"""
        try:
            # Intentar login
            login_data = {
                "email": self.n8n_user,
                "password": self.n8n_password
            }
            
            response = self.session.post(
                f"{self.n8n_url}/rest/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print_success("Login exitoso en n8n")
                return True
            else:
                print_error(f"Error de login: {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"Error conectando a n8n: {e}")
            return False

    def collect_credentials(self) -> Dict[str, Any]:
        """Recolecta credentials del usuario"""
        print_header("Configuración de Credentials")
        
        credentials = {}
        
        # YouTube API Key
        print_info("📺 YouTube Data API v3")
        youtube_key = input("Ingresa tu YouTube API Key: ").strip()
        if youtube_key:
            credentials['youtube_api'] = {
                'type': 'googleApi',
                'name': 'YouTube API Key - Stakas MVP',
                'data': {'apiKey': youtube_key}
            }
            print_success("YouTube API Key configurada")
        
        # Meta Ads API
        print_info("\n📱 Meta Ads API")
        meta_token = input("Ingresa tu Meta Access Token: ").strip()
        meta_account_id = input("Ingresa tu Meta Account ID (act_xxxxxxx): ").strip()
        if meta_token and meta_account_id:
            credentials['meta_ads'] = {
                'type': 'httpHeaderAuth',
                'name': 'Meta Ads API - Stakas MVP',
                'data': {
                    'name': 'Authorization',
                    'value': f'Bearer {meta_token}',
                    'account_id': meta_account_id
                }
            }
            print_success("Meta Ads API configurada")
        
        # GitHub Token
        print_info("\n🐙 GitHub Personal Access Token")
        github_token = input("Ingresa tu GitHub Token: ").strip()
        if github_token:
            credentials['github'] = {
                'type': 'httpHeaderAuth',
                'name': 'GitHub Token - Stakas MVP',
                'data': {
                    'name': 'Authorization',
                    'value': f'Bearer {github_token}'
                }
            }
            print_success("GitHub Token configurado")
        
        # Discord Webhook
        print_info("\n💬 Discord Webhook URL")
        discord_webhook = input("Ingresa tu Discord Webhook URL: ").strip()
        if discord_webhook:
            credentials['discord'] = {
                'type': 'discordWebhookApi',
                'name': 'Stakas Discord Webhook',
                'data': {'webhookUrl': discord_webhook}
            }
            print_success("Discord Webhook configurado")
        
        # PostgreSQL (automático)
        credentials['postgres'] = {
            'type': 'postgres',
            'name': 'Stakas PostgreSQL Database',
            'data': {
                'host': 'postgres',
                'port': 5432,
                'database': 'stakas_n8n',
                'user': 'stakas_user',
                'password': 'StakasN8N2024!',
                'ssl': False
            }
        }
        print_success("PostgreSQL Database configurada (automática)")
        
        return credentials

    def create_credential_in_n8n(self, cred_id: str, cred_data: Dict[str, Any]) -> bool:
        """Crea una credential en n8n via API"""
        try:
            response = self.session.post(
                f"{self.n8n_url}/rest/credentials",
                json={
                    'name': cred_data['name'],
                    'type': cred_data['type'],
                    'data': cred_data['data']
                },
                timeout=10
            )
            
            if response.status_code == 201:
                return True
            else:
                print_error(f"Error creando credential {cred_id}: {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"Error en API para {cred_id}: {e}")
            return False

    def setup_credentials(self, credentials: Dict[str, Any]):
        """Configura todas las credentials en n8n"""
        print_header("Creando Credentials en n8n")
        
        for cred_id, cred_data in credentials.items():
            print_info(f"Creando credential: {cred_data['name']}")
            
            if self.create_credential_in_n8n(cred_id, cred_data):
                print_success(f"✅ {cred_data['name']} creada")
            else:
                print_warning(f"⚠️  Error creando {cred_data['name']} - crear manualmente")

    def import_workflows(self):
        """Importa workflows desde archivos JSON"""
        print_header("Importando Workflows")
        
        workflows_dir = Path("n8n/workflows")
        if not workflows_dir.exists():
            print_error("Directorio n8n/workflows no encontrado")
            return
        
        workflow_files = list(workflows_dir.glob("*.json"))
        if not workflow_files:
            print_error("No se encontraron archivos de workflow")
            return
        
        for workflow_file in workflow_files:
            print_info(f"Importando {workflow_file.name}...")
            
            try:
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)
                
                response = self.session.post(
                    f"{self.n8n_url}/rest/workflows",
                    json=workflow_data,
                    timeout=15
                )
                
                if response.status_code == 201:
                    print_success(f"✅ {workflow_file.name} importado")
                else:
                    print_warning(f"⚠️  Error importando {workflow_file.name}: {response.status_code}")
                    
            except Exception as e:
                print_error(f"Error procesando {workflow_file.name}: {e}")

    def test_integrations(self):
        """Prueba las integraciones configuradas"""
        print_header("Probando Integraciones")
        
        # Test YouTube API
        if 'youtube_api' in self.credentials:
            print_info("Probando YouTube API...")
            try:
                api_key = self.credentials['youtube_api']['data']['apiKey']
                url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id=UCgohgqLVu1QPdfa64Vkrgeg&key={api_key}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'items' in data and len(data['items']) > 0:
                        stats = data['items'][0]['statistics']
                        print_success(f"YouTube API OK - Subs: {stats.get('subscriberCount', 'N/A')}")
                    else:
                        print_warning("YouTube API responde pero sin datos del canal")
                else:
                    print_error(f"YouTube API Error: {response.status_code}")
            except Exception as e:
                print_error(f"Error probando YouTube API: {e}")
        
        # Test Discord Webhook
        if 'discord' in self.credentials:
            print_info("Probando Discord Webhook...")
            try:
                webhook_url = self.credentials['discord']['data']['webhookUrl']
                test_message = {
                    "content": "🚀 **Test desde n8n Setup**\n✅ Stakas MVP workflows configurados correctamente!\n🎯 Canal: UCgohgqLVu1QPdfa64Vkrgeg"
                }
                response = requests.post(webhook_url, json=test_message, timeout=10)
                
                if response.status_code == 204:
                    print_success("Discord Webhook OK - mensaje enviado")
                else:
                    print_error(f"Discord Webhook Error: {response.status_code}")
            except Exception as e:
                print_error(f"Error probando Discord Webhook: {e}")

    def open_n8n_dashboard(self):
        """Abre el dashboard de n8n en el browser"""
        print_header("Abriendo n8n Dashboard")
        
        try:
            webbrowser.open(f"{self.n8n_url}")
            print_success("Dashboard abierto en el browser")
            print_info("Credenciales de acceso:")
            print_info(f"  Usuario: {self.n8n_user}")
            print_info(f"  Password: {self.n8n_password}")
        except Exception as e:
            print_error(f"Error abriendo browser: {e}")
            print_info(f"Accede manualmente a: {self.n8n_url}")

    def run_setup(self):
        """Ejecuta el setup completo"""
        print_header("Setup Automático n8n - Stakas MVP")
        print_info("Canal: UCgohgqLVu1QPdfa64Vkrgeg")
        print_info("Presupuesto Meta Ads: €500/mes")
        
        # 1. Verificar/iniciar n8n
        if not self.start_n8n_if_needed():
            print_error("No se pudo iniciar n8n. Saliendo...")
            return False
        
        # 2. Login en n8n
        if not self.login_n8n():
            print_error("No se pudo hacer login en n8n. Saliendo...")
            return False
        
        # 3. Recolectar credentials
        self.credentials = self.collect_credentials()
        
        # 4. Crear credentials en n8n
        if self.credentials:
            self.setup_credentials(self.credentials)
        
        # 5. Importar workflows
        self.import_workflows()
        
        # 6. Probar integraciones
        self.test_integrations()
        
        # 7. Abrir dashboard
        self.open_n8n_dashboard()
        
        print_header("🎉 Setup Completado!")
        print_success("n8n configurado para Stakas MVP")
        print_info("Próximos pasos:")
        print_info("  1. Verificar credentials en n8n dashboard")
        print_info("  2. Activar workflows importados")
        print_info("  3. Probar webhooks de generación de contenido")
        print_info("  4. Monitorear analytics del canal cada 2 horas")
        
        return True

def main():
    """Función principal"""
    setup = N8nStakasSetup()
    
    try:
        success = setup.run_setup()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print_warning("\nSetup cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()