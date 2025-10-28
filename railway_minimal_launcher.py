#!/usr/bin/env python3
"""
🚀 RAILWAY MINIMAL LAUNCHER - STAKAS VIRAL SYSTEM
Launcher minimalista garantizado para funcionar en Railway
"""

import os
import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class MinimalHandler(BaseHTTPRequestHandler):
    """Handler HTTP minimalista"""
    
    def do_GET(self):
        if self.path == '/health':
            # Health check endpoint
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            health = {
                'status': 'healthy',
                'service': 'stakas-viral-system',
                'channel': 'UCgohgqLVu1QPdfa64Vkrgeg',
                'timestamp': int(time.time())
            }
            self.wfile.write(json.dumps(health).encode())
        else:
            # Main page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = f"""<!DOCTYPE html>
<html>
<head>
    <title>🚀 Stakas Viral System</title>
    <meta charset="UTF-8">
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            text-align: center; 
            padding: 50px;
            margin: 0;
        }}
        .container {{ 
            max-width: 800px; 
            margin: 0 auto; 
            background: rgba(255,255,255,0.1);
            padding: 40px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }}
        h1 {{ font-size: 3em; margin: 20px 0; }}
        .status {{ color: #4CAF50; font-size: 1.5em; margin: 20px 0; }}
        .info {{ margin: 10px 0; font-size: 1.1em; }}
        .footer {{ margin-top: 40px; opacity: 0.8; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Stakas Viral System</h1>
        <div class="status">✅ Sistema Activo en Railway</div>
        
        <div class="info">🎯 Canal: UCgohgqLVu1QPdfa64Vkrgeg</div>
        <div class="info">🎵 Género: Drill Rap Español</div>
        <div class="info">📈 Objetivo: 0 → 10K suscriptores</div>
        <div class="info">💰 Presupuesto Meta Ads: €500/mes</div>
        
        <div class="footer">
            <h3>🚀 Servicios del Sistema:</h3>
            <p>Meta Ads Campaigns • ML Analysis • Device Farm • GoLogin • n8n Workflows</p>
            <p>Puerto: {os.getenv('PORT', 8501)} | Entorno: {os.getenv('ENVIRONMENT', 'production')}</p>
        </div>
    </div>
</body>
</html>"""
            
            self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Disable default logging"""
        return

def main():
    """Función principal ultra-simple"""
    port = int(os.getenv('PORT', 8501))
    host = '0.0.0.0'
    
    print(f"🚀 Iniciando Stakas Viral System en {host}:{port}")
    print(f"📊 Canal objetivo: UCgohgqLVu1QPdfa64Vkrgeg")
    print(f"💰 Presupuesto Meta Ads: €500/mes")
    
    try:
        server = HTTPServer((host, port), MinimalHandler)
        print(f"✅ Servidor iniciado correctamente en http://{host}:{port}")
        print(f"🔗 Health check: http://{host}:{port}/health")
        
        # Mantener servidor activo
        server.serve_forever()
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())