#!/usr/bin/env python3
"""
Scripts de Deployment Automatizado para Railway
Stakas MVP Viral System - Deployment y Actualización
"""

import subprocess
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

class RailwayDeployment:
    """Manejo de deployment en Railway"""
    
    def __init__(self):
        self.project_name = "stakas-mvp-viral-system"
        self.railway_cli_installed = self._check_railway_cli()
        
    def _check_railway_cli(self):
        """Verificar si Railway CLI está instalado"""
        try:
            result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def install_railway_cli(self):
        """Instalar Railway CLI"""
        print("📦 Instalando Railway CLI...")
        
        try:
            # Para Windows
            if os.name == 'nt':
                subprocess.run(['powershell', '-Command', 
                              'iwr https://railway.app/install.ps1 | iex'], check=True)
            else:
                # Para Unix/Linux/Mac
                subprocess.run([, '-c', 
                              'curl -fsSL https://railway.app/install.sh | sh'], check=True)
            
            print("✅ Railway CLI instalado correctamente")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando Railway CLI: {e}")
            return False
    
    def login_railway(self):
        """Login en Railway"""
        print("🔐 Iniciando sesión en Railway...")
        
        try:
            subprocess.run(['railway', 'login'], check=True)
            print("✅ Login exitoso")
            return True
        except subprocess.CalledProcessError:
            print("❌ Error en login")
            return False
    
    def create_project(self):
        """Crear nuevo proyecto en Railway"""
        print(f"🚀 Creando proyecto {self.project_name}...")
        
        try:
            subprocess.run(['railway', 'create', self.project_name], check=True)
            print("✅ Proyecto creado exitosamente")
            return True
        except subprocess.CalledProcessError:
            print("❌ Error creando proyecto")
            return False
    
    def link_project(self):
        """Vincular con proyecto existente"""
        print("🔗 Vinculando con proyecto existente...")
        
        try:
            subprocess.run(['railway', 'link'], check=True)
            print("✅ Proyecto vinculado")
            return True
        except subprocess.CalledProcessError:
            print("❌ Error vinculando proyecto")
            return False
    
    def set_environment_variables(self):
        """Configurar variables de entorno"""
        print("⚙️ Configurando variables de entorno...")
        
        # Variables básicas necesarias
        env_vars = {
            'ENVIRONMENT': 'production',
            'PORT': '8080',
            'STREAMLIT_SERVER_PORT': '8080',
            'STREAMLIT_SERVER_ADDRESS': '0.0.0.0',
            'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false',
            'YOUTUBE_CHANNEL_ID': 'UCgohgqLVu1QPdfa64Vkrgeg',
            'CHANNEL_NAME': 'Stakas MVP',
            'DUMMY_MODE': 'false',
            'LOG_LEVEL': 'INFO',
            'AUTO_RESTART': 'true',
            'ENABLE_MONITORING': 'true'
        }
        
        try:
            for key, value in env_vars.items():
                subprocess.run(['railway', 'variables', 'set', f'{key}={value}'], check=True)
                print(f"  ✅ {key} configurada")
            
            print("✅ Variables de entorno configuradas")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error configurando variables: {e}")
            return False
    
    def deploy(self):
        """Realizar deployment"""
        print("🚀 Iniciando deployment...")
        
        try:
            # Verificar archivos necesarios
            required_files = [
                'railway_main.py',
                'Dockerfile.railway', 
                'railway.json',
                'requirements.txt'
            ]
            
            for file in required_files:
                if not Path(file).exists():
                    print(f"❌ Archivo requerido no encontrado: {file}")
                    return False
            
            # Deploy
            result = subprocess.run(['railway', 'up'], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Deployment exitoso!")
                
                # Extraer URL del deployment
                output = result.stdout
                if 'https://' in output:
                    url_start = output.find('https://')
                    url_end = output.find('\n', url_start)
                    if url_end == -1:
                        url_end = len(output)
                    url = output[url_start:url_end].strip()
                    print(f"🌐 URL de la aplicación: {url}")
                    
                    # Guardar URL para referencia
                    with open('railway_deployment_url.txt', 'w') as f:
                        f.write(url)
                
                return True
            else:
                print(f"❌ Error en deployment: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error durante deployment: {e}")
            return False
    
    def check_status(self):
        """Verificar estado del deployment"""
        print("📊 Verificando estado del deployment...")
        
        try:
            result = subprocess.run(['railway', 'status'], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Estado del proyecto:")
                print(result.stdout)
                return True
            else:
                print(f"❌ Error verificando estado: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            return False
    
    def view_logs(self):
        """Ver logs del deployment"""
        print("📋 Mostrando logs del deployment...")
        
        try:
            subprocess.run(['railway', 'logs'], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error accediendo a logs: {e}")
            return False
    
    def full_deployment_process(self):
        """Proceso completo de deployment"""
        print("="*60)
        print("🎵 STAKAS MVP VIRAL SYSTEM - RAILWAY DEPLOYMENT")
        print("="*60)
        
        steps = [
            ("Verificar Railway CLI", self._verify_or_install_cli),
            ("Login en Railway", self.login_railway),
            ("Crear/Vincular Proyecto", self._create_or_link_project),
            ("Configurar Variables", self.set_environment_variables),
            ("Realizar Deployment", self.deploy),
            ("Verificar Estado", self.check_status)
        ]
        
        for step_name, step_func in steps:
            print(f"\n🔄 {step_name}...")
            
            if not step_func():
                print(f"❌ Falló: {step_name}")
                return False
            
            print(f"✅ Completado: {step_name}")
        
        print("\n" + "="*60)
        print("🎉 ¡DEPLOYMENT COMPLETADO EXITOSAMENTE!")
        print("="*60)
        
        # Mostrar información final
        self._show_final_info()
        
        return True
    
    def _verify_or_install_cli(self):
        """Verificar o instalar Railway CLI"""
        if self.railway_cli_installed:
            print("✅ Railway CLI ya está instalado")
            return True
        else:
            print("📦 Railway CLI no encontrado, instalando...")
            return self.install_railway_cli()
    
    def _create_or_link_project(self):
        """Crear o vincular proyecto"""
        # Intentar vincular primero
        print("🔗 Intentando vincular con proyecto existente...")
        
        result = subprocess.run(['railway', 'link', '--help'], capture_output=True)
        if result.returncode == 0:
            # CLI disponible, intentar vincular
            link_result = subprocess.run(['railway', 'status'], capture_output=True)
            
            if link_result.returncode != 0:
                # No vinculado, crear nuevo
                print("📝 No hay proyecto vinculado, creando nuevo...")
                return self.create_project()
            else:
                print("✅ Proyecto ya vinculado")
                return True
        
        return False
    
    def _show_final_info(self):
        """Mostrar información final del deployment"""
        
        print("\n📊 INFORMACIÓN DEL DEPLOYMENT:")
        print("-" * 40)
        
        # Leer URL si existe
        url_file = Path('railway_deployment_url.txt')
        if url_file.exists():
            url = url_file.read_text().strip()
            print(f"🌐 URL Principal: {url}")
            print(f"🩺 Health Check: {url}/health")
            print(f"📊 API Status: {url}/api/status")
        
        print("\n🎯 CARACTERÍSTICAS ACTIVADAS:")
        print("  ✅ Dashboard unificado Streamlit")
        print("  ✅ Health checks automáticos")
        print("  ✅ Monitoreo 24/7")
        print("  ✅ Logging avanzado")
        print("  ✅ Auto-restart en fallos")
        print("  ✅ Optimización de rendimiento")
        
        print("\n📱 CANAL CONFIGURADO:")
        print("  📺 Stakas MVP (UCgohgqLVu1QPdfa64Vkrgeg)")
        print("  🎵 Género: Drill/Rap Español")
        print("  💰 Meta Ads Budget: €500/mes")
        print("  🎯 ROI Proyectado: 60-180%")
        
        print("\n🚀 PRÓXIMOS PASOS:")
        print("  1. Configurar APIs (Meta, YouTube, TikTok, etc.)")
        print("  2. Activar Meta Ads campaign")
        print("  3. Monitorear via dashboard web")
        print("  4. Verificar alertas y notificaciones")
        
        print("\n📋 COMANDOS ÚTILES:")
        print("  📊 Ver logs: railway logs")
        print("  📈 Ver estado: railway status")
        print("  🔄 Redeploy: railway up")
        print("  ⚙️ Variables: railway variables")

def create_deployment_guide():
    """Crear guía de deployment"""
    
    guide_content = """
# 🚀 Guía de Deployment Railway - Stakas MVP Viral System

## Prerequisitos

1. **Cuenta Railway**: Crear cuenta en [railway.app](https://railway.app)
2. **Git**: Tener el código en un repositorio Git
3. **APIs**: Configurar credenciales de APIs necesarias

## Deployment Automático

### Opción 1: Script Automático
```bash
python railway_deployment_scripts.py
```

### Opción 2: Manual

1. **Instalar Railway CLI**:
   ```bash
   # Windows (PowerShell)
   iwr https://railway.app/install.ps1 | iex
   
   # Mac/Linux
   curl -fsSL https://railway.app/install.sh | sh
   ```

2. **Login**:
   ```bash
   railway login
   ```

3. **Crear Proyecto**:
   ```bash
   railway create stakas-mvp-viral-system
   ```

4. **Configurar Variables de Entorno**:
   ```bash
   railway variables set ENVIRONMENT=production
   railway variables set PORT=8080
   railway variables set YOUTUBE_CHANNEL_ID=UCgohgqLVu1QPdfa64Vkrgeg
   # ... (ver railway.env.template para lista completa)
   ```

5. **Deploy**:
   ```bash
   railway up
   ```

## Configuración de APIs

### Meta Ads API
1. Crear app en [developers.facebook.com](https://developers.facebook.com)
2. Obtener: `META_ACCESS_TOKEN`, `META_APP_ID`, `META_APP_SECRET`
3. Configurar en Railway variables

### YouTube API
1. Crear proyecto en [Google Cloud Console](https://console.cloud.google.com)
2. Habilitar YouTube Data API v3
3. Obtener API key y OAuth credentials

### TikTok API
1. Registrarse en [TikTok for Developers](https://developers.tiktok.com)
2. Crear app y obtener client credentials

## Monitoreo

- **Dashboard Principal**: `https://[tu-app].railway.app`
- **Health Check**: `https://[tu-app].railway.app/health`
- **Logs**: `railway logs`
- **Status**: `railway status`

## Troubleshooting

### Build Fails
- Verificar `Dockerfile.railway`
- Revisar `requirements.txt`
- Comprobar `railway.json`

### Variables de Entorno
- Usar `railway variables` para verificar
- Verificar sintaxis de variables

### Performance Issues
- Monitorear logs con `railway logs`
- Verificar métricas de CPU/memoria
- Ajustar configuración de workers

## Comandos Útiles

```bash
# Ver todas las variables
railway variables

# Abrir dashboard de Railway
railway open

# Ver deployments
railway deployments

# Conectar a shell
railway shell

# Backup de variables
railway variables list > variables_backup.txt
```
"""
    
    with open('RAILWAY_DEPLOYMENT_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("📋 Guía de deployment creada: RAILWAY_DEPLOYMENT_GUIDE.md")

def main():
    """Función principal"""
    
    print("🎵 STAKAS MVP VIRAL SYSTEM - RAILWAY DEPLOYMENT TOOL")
    print("=" * 60)
    
    # Crear guía de deployment
    create_deployment_guide()
    
    # Menú interactivo
    while True:
        print("\n📋 OPCIONES DISPONIBLES:")
        print("1. 🚀 Deployment Completo Automático")
        print("2. 📦 Solo Instalar Railway CLI")
        print("3. 🔐 Solo Login Railway")
        print("4. ⚙️  Solo Configurar Variables")
        print("5. 🚢 Solo Deploy")
        print("6. 📊 Ver Estado del Proyecto")
        print("7. 📋 Ver Logs")
        print("8. 📄 Crear Guía de Deployment")
        print("9. ❌ Salir")
        
        choice = input("\n🎯 Selecciona una opción (1-9): ").strip()
        
        deployment = RailwayDeployment()
        
        if choice == '1':
            deployment.full_deployment_process()
        elif choice == '2':
            deployment.install_railway_cli()
        elif choice == '3':
            deployment.login_railway()
        elif choice == '4':
            deployment.set_environment_variables()
        elif choice == '5':
            deployment.deploy()
        elif choice == '6':
            deployment.check_status()
        elif choice == '7':
            deployment.view_logs()
        elif choice == '8':
            create_deployment_guide()
        elif choice == '9':
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida")
        
        input("\n⏸️  Presiona Enter para continuar...")

if __name__ == "__main__":
    main()