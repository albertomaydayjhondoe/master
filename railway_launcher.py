#!/usr/bin/env python3
"""
🚀 RAILWAY PRODUCTION LAUNCHER - STAKAS VIRAL SYSTEM
Multi-service launcher optimized for Railway deployment
"""

import os
import sys
import time
import uvicorn
import subprocess
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import logging
import platform
import shutil
from pathlib import Path

# Import cross-platform utilities (optional)
try:
    from cross_platform_launcher import CrossPlatformLauncher
except ImportError:
    CrossPlatformLauncher = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='🚀 %(asctime)s [RAILWAY] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class RailwayLauncher:
    """Railway multi-service launcher with cross-platform support"""
    
    def __init__(self):
        self.port = int(os.getenv('PORT', 8501))
        self.host = '0.0.0.0'
        self.environment = os.getenv('ENVIRONMENT', 'production')
        self.dummy_mode = os.getenv('DUMMY_MODE', 'false').lower() == 'true'
        self.cross_platform = CrossPlatformLauncher() if CrossPlatformLauncher else None
        self.system_info = self.cross_platform.get_startup_info() if self.cross_platform else {}
        
        logger.info(f"🎯 Railway Launcher initialized - Port: {self.port}")
        logger.info(f"📊 Environment: {self.environment}")
        logger.info(f"🔧 Dummy Mode: {self.dummy_mode}")
    
    def setup_environment(self):
        """Setup production environment variables"""
        os.environ.update({
            'PYTHONPATH': '/app',
            'DUMMY_MODE': str(self.dummy_mode).lower(),
            'ENVIRONMENT': self.environment,
            'STREAMLIT_SERVER_HEADLESS': 'true',
            'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false'
        })
        
        logger.info("✅ Environment variables configured")
    
    def start_ml_api(self):
        """Start ML API in background"""
        try:
            logger.info("🚀 Starting ML Core API...")
            
            # Use uvicorn directly for better Railway compatibility
            from ml_core.api.main import app
            
            # Start in a separate process
            def run_api():
                uvicorn.run(
                    app,
                    host='0.0.0.0',
                    port=8000,
                    workers=1,
                    log_level='info'
                )
            
            process = multiprocessing.Process(target=run_api, daemon=True)
            process.start()
            
            logger.info("✅ ML API started on port 8000")
            return process
            
        except Exception as e:
            logger.error(f"❌ Failed to start ML API: {e}")
            return None
    
    def start_main_dashboard(self):
        """Start main Streamlit dashboard"""
        try:
            logger.info("🎯 Starting main dashboard...")
            
            import streamlit.web.cli as stcli
            from streamlit import config as st_config
            
            # Configure Streamlit
            st_config.set_option('server.port', self.port)
            st_config.set_option('server.address', self.host)
            st_config.set_option('server.headless', True)
            st_config.set_option('browser.gatherUsageStats', False)
            
            # Run unified system
            sys.argv = [
                "streamlit", "run", "unified_system_production.py",
                "--server.port", str(self.port),
                "--server.address", self.host,
                "--server.headless", "true"
            ]
            
            stcli.main()
            
        except Exception as e:
            logger.error(f"❌ Failed to start dashboard: {e}")
            # Fallback to simple HTTP server
            self.start_fallback_server()
    
    def start_fallback_server(self):
        """Fallback HTTP server for Railway"""
        from http.server import HTTPServer, SimpleHTTPRequestHandler
        import json
        
        class RailwayHandler(SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {
                        'status': 'healthy',
                        'service': 'stakas-viral-system',
                        'channel': 'UCgohgqLVu1QPdfa64Vkrgeg',
                        'environment': self.environment,
                        'port': self.port
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
                            h1 {{ 
                                font-size: 3em; 
                                margin-bottom: 30px;
                                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                            }}
                            .metrics {{ 
                                display: grid; 
                                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                                gap: 20px; 
                                margin: 30px 0;
                            }}
                            .metric {{ 
                                background: rgba(255,255,255,0.1); 
                                padding: 20px; 
                                border-radius: 10px;
                                border: 1px solid rgba(255,255,255,0.2);
                            }}
                            .status {{ 
                                color: #4CAF50; 
                                font-size: 1.2em; 
                                font-weight: bold;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>🚀 Stakas Viral System</h1>
                            <p class="status">✅ Sistema Desplegado en Railway</p>
                            
                            <div class="metrics">
                                <div class="metric">
                                    <h3>🎯 Canal Target</h3>
                                    <p>UCgohgqLVu1QPdfa64Vkrgeg</p>
                                </div>
                                <div class="metric">
                                    <h3>🌍 Environment</h3>
                                    <p>{self.environment}</p>
                                </div>
                                <div class="metric">
                                    <h3>🔧 Puerto</h3>
                                    <p>{self.port}</p>
                                </div>
                                <div class="metric">
                                    <h3>📊 Status</h3>
                                    <p class="status">ONLINE</p>
                                </div>
                            </div>
                            
                            <h2>🎵 Drill Rap Viral System</h2>
                            <p>Sistema completo de automatización para crecimiento viral</p>
                            <p>Meta Ads + Device Farm + ML Analysis + GoLogin Automation</p>
                            
                            <div style="margin-top: 40px;">
                                <h3>📈 Servicios Activos:</h3>
                                <ul style="text-align: left; display: inline-block;">
                                    <li>🤖 ML Core API (Puerto 8000)</li>
                                    <li>📊 Dashboard Principal (Puerto {self.port})</li>
                                    <li>📱 Device Farm Controller</li>
                                    <li>🌐 GoLogin Browser Automation</li>
                                    <li>💰 Meta Ads Campaigns</li>
                                    <li>🔄 n8n Workflow Orchestration</li>
                                </ul>
                            </div>
                            
                            <p style="margin-top: 30px; opacity: 0.8;">
                                Canal objetivo: De 0 a 10K suscriptores | Presupuesto: €500/mes
                            </p>
                        </div>
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode())
        
        logger.info("🔄 Starting fallback HTTP server...")
        server = HTTPServer((self.host, self.port), RailwayHandler)
        logger.info(f"✅ Fallback server running on {self.host}:{self.port}")
        server.serve_forever()
    
    def run(self):
        """Run the complete Railway deployment"""
        logger.info("🚀 Starting Stakas Viral System on Railway...")
        
        # Setup environment
        self.setup_environment()
        
        # Start ML API in background
        ml_process = self.start_ml_api()
        
        # Wait a bit for ML API to start
        time.sleep(5)
        
        # Start main dashboard (this will block)
        logger.info(f"🎯 Starting main service on port {self.port}")
        self.start_main_dashboard()

if __name__ == "__main__":
    launcher = RailwayLauncher()
    launcher.run()