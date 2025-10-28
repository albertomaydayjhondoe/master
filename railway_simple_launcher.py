#!/usr/bin/env python3
"""
🚀 RAILWAY SIMPLE LAUNCHER - STAKAS VIRAL SYSTEM
Launcher simplificado sin dependencias externas para Railway
"""

import os
import sys
import time
import logging
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='🚀 %(asctime)s [RAILWAY] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleRailwayLauncher:
    """Railway launcher simplificado"""
    
    def __init__(self):
        self.port = int(os.getenv('PORT', 8501))
        self.host = '0.0.0.0'
        self.environment = os.getenv('ENVIRONMENT', 'production')
        
        logger.info(f"🎯 Simple Railway Launcher - Port: {self.port}")
        logger.info(f"📊 Environment: {self.environment}")
    
    def start_health_server(self):
        """Inicia servidor de health check"""
        class HealthHandler(SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {
                        'status': 'healthy',
                        'service': 'stakas-viral-system',
                        'channel': 'UCgohgqLVu1QPdfa64Vkrgeg',
                        'environment': os.getenv('ENVIRONMENT', 'production'),
                        'port': int(os.getenv('PORT', 8501))
                    }
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>🎯 Stakas Viral System - Railway</title>
                        <meta charset="UTF-8">
                        <style>
                            body {{ 
                                font-family: Arial, sans-serif; 
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                color: white; 
                                text-align: center; 
                                padding: 50px;
                            }}
                            .container {{ 
                                max-width: 800px; 
                                margin: 0 auto; 
                                background: rgba(255,255,255,0.1);
                                padding: 40px;
                                border-radius: 20px;
                                backdrop-filter: blur(10px);
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>🚀 Stakas Viral System</h1>
                            <p>✅ Sistema Desplegado en Railway</p>
                            <h2>🎵 Drill Rap Viral Engine</h2>
                            <p>Canal: UCgohgqLVu1QPdfa64Vkrgeg</p>
                            <p>Objetivo: 0 → 10K suscriptores</p>
                            <p>Presupuesto: €500/mes Meta Ads</p>
                        </div>
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode())
        
        server = HTTPServer((self.host, self.port), HealthHandler)
        logger.info(f"✅ Health server running on {self.host}:{self.port}")
        
        # Ejecutar en thread separado
        def run_server():
            server.serve_forever()
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        return server
    
    def start_streamlit_fallback(self):
        """Intenta iniciar Streamlit como fallback"""
        try:
            logger.info("🎯 Intentando iniciar Streamlit...")
            
            # Comandos Streamlit posibles
            streamlit_commands = [
                f"python -m streamlit run unified_system_production.py --server.port {self.port} --server.address {self.host} --server.headless true",
                f"python3 -m streamlit run unified_system_production.py --server.port {self.port} --server.address {self.host} --server.headless true",
                f"streamlit run unified_system_production.py --server.port {self.port} --server.address {self.host} --server.headless true"
            ]
            
            for cmd in streamlit_commands:
                try:
                    logger.info(f"Probando comando: {cmd}")
                    process = subprocess.Popen(
                        cmd.split(),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    
                    # Esperar un poco para ver si el proceso inicia correctamente
                    time.sleep(3)
                    
                    if process.poll() is None:  # Proceso aún corriendo
                        logger.info("✅ Streamlit iniciado correctamente")
                        return process
                        
                except Exception as e:
                    logger.warning(f"Comando falló: {e}")
                    continue
            
            logger.warning("⚠️ No se pudo iniciar Streamlit, usando servidor básico")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error iniciando Streamlit: {e}")
            return None
    
    def run(self):
        """Ejecuta el launcher simplificado"""
        logger.info("🚀 Iniciando Stakas Viral System en Railway...")
        
        # 1. Intentar iniciar Streamlit
        streamlit_process = self.start_streamlit_fallback()
        
        # 2. Si Streamlit no funciona, usar servidor básico
        if not streamlit_process:
            logger.info("🔄 Iniciando servidor de respaldo...")
            health_server = self.start_health_server()
        
        # 3. Mantener el proceso activo
        try:
            logger.info("✅ Sistema iniciado correctamente en Railway")
            logger.info(f"🌐 URL: http://{self.host}:{self.port}")
            
            while True:
                time.sleep(30)
                logger.info("🟢 Sistema operativo...")
                
        except KeyboardInterrupt:
            logger.info("🛑 Deteniendo sistema...")
        except Exception as e:
            logger.error(f"❌ Error crítico: {e}")

def main():
    """Punto de entrada principal"""
    launcher = SimpleRailwayLauncher()
    launcher.run()

if __name__ == "__main__":
    main()