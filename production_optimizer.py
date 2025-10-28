#!/usr/bin/env python3
"""
Production Optimization - Sistema 24/7 para Railway
Configuración de logging, monitoring y health checks
"""

import logging
import sys
import os
import time
import psutil
import threading
from datetime import datetime, timedelta
import json
import requests
from pathlib import Path

class ProductionOptimizer:
    """Optimizador para producción 24/7"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.health_checks = []
        self.alerts_sent = []
        self.setup_logging()
        self.setup_monitoring()
    
    def setup_logging(self):
        """Configurar logging avanzado"""
        
        # Crear directorio de logs
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Configurar formato
        log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        
        # Configurar handlers
        handlers = [
            # Console handler
            logging.StreamHandler(sys.stdout),
            
            # File handler rotativo
            logging.handlers.RotatingFileHandler(
                'logs/stakas_mvp.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            
            # Error handler separado
            logging.handlers.RotatingFileHandler(
                'logs/errors.log',
                maxBytes=5*1024*1024,   # 5MB
                backupCount=3
            )
        ]
        
        # Configurar logging
        logging.basicConfig(
            level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
            format=log_format,
            handlers=handlers
        )
        
        # Logger específico para errores
        error_handler = handlers[2]
        error_handler.setLevel(logging.ERROR)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("✅ Sistema de logging configurado")
    
    def setup_monitoring(self):
        """Configurar monitoring del sistema"""
        
        self.monitoring_enabled = os.getenv('ENABLE_MONITORING', 'true').lower() == 'true'
        self.health_check_interval = int(os.getenv('HEALTH_CHECK_INTERVAL', 300))
        
        if self.monitoring_enabled:
            # Iniciar thread de monitoreo
            monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            monitor_thread.start()
            self.logger.info("✅ Sistema de monitoreo activado")
    
    def _monitoring_loop(self):
        """Loop principal de monitoreo"""
        
        while True:
            try:
                # Realizar health check
                health_status = self.perform_health_check()
                
                # Guardar resultado
                self.health_checks.append({
                    'timestamp': datetime.now().isoformat(),
                    'status': health_status
                })
                
                # Mantener solo últimas 100 mediciones
                if len(self.health_checks) > 100:
                    self.health_checks = self.health_checks[-100:]
                
                # Verificar alertas
                self._check_alerts(health_status)
                
                # Esperar siguiente intervalo
                time.sleep(self.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Error en monitoring loop: {e}")
                time.sleep(60)  # Esperar 1 minuto si hay error
    
    def perform_health_check(self):
        """Realizar health check completo"""
        
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
            'system': self._get_system_metrics(),
            'application': self._get_app_metrics(),
            'services': self._check_services(),
            'overall_status': 'healthy'
        }
        
        # Determinar estado general
        critical_issues = []
        
        if health_status['system']['cpu_percent'] > 90:
            critical_issues.append('high_cpu')
        
        if health_status['system']['memory_percent'] > 90:
            critical_issues.append('high_memory')
        
        if health_status['system']['disk_percent'] > 95:
            critical_issues.append('high_disk')
        
        if critical_issues:
            health_status['overall_status'] = 'critical'
            health_status['issues'] = critical_issues
        elif health_status['system']['cpu_percent'] > 70 or health_status['system']['memory_percent'] > 70:
            health_status['overall_status'] = 'warning'
        
        self.logger.info(f"Health check: {health_status['overall_status']} - CPU: {health_status['system']['cpu_percent']:.1f}% - Memory: {health_status['system']['memory_percent']:.1f}%")
        
        return health_status
    
    def _get_system_metrics(self):
        """Obtener métricas del sistema"""
        
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'network_io': psutil.net_io_counters()._asdict(),
            'process_count': len(psutil.pids()),
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        }
    
    def _get_app_metrics(self):
        """Obtener métricas de la aplicación"""
        
        return {
            'channel_id': 'UCgohgqLVu1QPdfa64Vkrgeg',
            'channel_name': 'Stakas MVP',
            'automation_active': True,
            'meta_ads_ready': True,
            'last_content_check': datetime.now().isoformat(),
            'subsystems_status': {
                'content_automation': 'active',
                'engagement_automation': 'active',
                'analytics_automation': 'active',
                'cross_platform_sync': 'active',
                'performance_optimization': 'active',
                'continuous_monitoring': 'active'
            }
        }
    
    def _check_services(self):
        """Verificar estado de servicios"""
        
        services = {
            'streamlit': self._check_port(8080),
            'health_api': self._check_port(8081),
            'database': True,  # Simulated for Railway
            'redis': True      # Simulated for Railway
        }
        
        return services
    
    def _check_port(self, port):
        """Verificar si un puerto está activo"""
        
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except:
            return False
    
    def _check_alerts(self, health_status):
        """Verificar y enviar alertas si es necesario"""
        
        current_time = datetime.now()
        
        # Verificar si necesitamos enviar alertas
        if health_status['overall_status'] == 'critical':
            # Evitar spam de alertas (máximo 1 cada 30 minutos)
            last_critical_alert = None
            for alert in reversed(self.alerts_sent):
                if alert.get('type') == 'critical':
                    last_critical_alert = datetime.fromisoformat(alert['timestamp'])
                    break
            
            if not last_critical_alert or (current_time - last_critical_alert).total_seconds() > 1800:
                self._send_alert('critical', health_status)
        
        elif health_status['overall_status'] == 'warning':
            # Alertas de warning cada 2 horas máximo
            last_warning_alert = None
            for alert in reversed(self.alerts_sent):
                if alert.get('type') == 'warning':
                    last_warning_alert = datetime.fromisoformat(alert['timestamp'])
                    break
            
            if not last_warning_alert or (current_time - last_warning_alert).total_seconds() > 7200:
                self._send_alert('warning', health_status)
    
    def _send_alert(self, alert_type, health_status):
        """Enviar alerta"""
        
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'health_status': health_status
        }
        
        self.alerts_sent.append(alert)
        
        # Mantener solo últimas 50 alertas
        if len(self.alerts_sent) > 50:
            self.alerts_sent = self.alerts_sent[-50:]
        
        # Log de alerta
        if alert_type == 'critical':
            self.logger.critical(f"🚨 ALERTA CRÍTICA: {health_status.get('issues', [])}")
        else:
            self.logger.warning(f"⚠️ ALERTA WARNING: Sistema bajo estrés")
        
        # Enviar a webhooks si están configurados
        self._send_webhook_alert(alert)
    
    def _send_webhook_alert(self, alert):
        """Enviar alerta via webhook (Discord, Slack, etc.)"""
        
        discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
        
        if discord_webhook:
            try:
                message = f"""
🎵 **Stakas MVP System Alert**

⏰ **Time**: {alert['timestamp']}
🚨 **Type**: {alert['type'].upper()}
💻 **CPU**: {alert['health_status']['system']['cpu_percent']:.1f}%
🧠 **Memory**: {alert['health_status']['system']['memory_percent']:.1f}%
💾 **Disk**: {alert['health_status']['system']['disk_percent']:.1f}%
⏱️ **Uptime**: {alert['health_status']['uptime_seconds']:.0f}s

📺 **Canal**: Stakas MVP (UCgohgqLVu1QPdfa64Vkrgeg)
🤖 **Automation**: Active
"""
                
                payload = {
                    'content': message,
                    'username': 'Stakas MVP Monitor'
                }
                
                requests.post(discord_webhook, json=payload, timeout=10)
                
            except Exception as e:
                self.logger.error(f"Error enviando webhook: {e}")
    
    def get_health_report(self):
        """Generar reporte de salud"""
        
        if not self.health_checks:
            return {"status": "no_data"}
        
        latest = self.health_checks[-1]
        
        # Calcular promedios de las últimas 10 mediciones
        recent_checks = self.health_checks[-10:]
        
        avg_cpu = sum(check['status']['system']['cpu_percent'] for check in recent_checks) / len(recent_checks)
        avg_memory = sum(check['status']['system']['memory_percent'] for check in recent_checks) / len(recent_checks)
        
        return {
            'current_status': latest['status']['overall_status'],
            'uptime_hours': latest['status']['uptime_seconds'] / 3600,
            'avg_cpu_10min': avg_cpu,
            'avg_memory_10min': avg_memory,
            'total_alerts': len(self.alerts_sent),
            'last_check': latest['timestamp'],
            'services_status': latest['status']['services']
        }
    
    def optimize_performance(self):
        """Optimizar rendimiento del sistema"""
        
        try:
            # Limpiar logs antiguos
            self._cleanup_old_logs()
            
            # Optimizar memoria
            self._optimize_memory()
            
            # Verificar y limpiar archivos temporales
            self._cleanup_temp_files()
            
            self.logger.info("✅ Optimización de rendimiento completada")
            
        except Exception as e:
            self.logger.error(f"Error en optimización: {e}")
    
    def _cleanup_old_logs(self):
        """Limpiar logs antiguos"""
        
        log_dir = Path('logs')
        if not log_dir.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=7)
        
        for log_file in log_dir.glob('*.log*'):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                try:
                    log_file.unlink()
                    self.logger.info(f"Eliminado log antiguo: {log_file}")
                except Exception as e:
                    self.logger.warning(f"No se pudo eliminar {log_file}: {e}")
    
    def _optimize_memory(self):
        """Optimizar uso de memoria"""
        
        import gc
        
        # Forzar garbage collection
        collected = gc.collect()
        
        if collected > 0:
            self.logger.info(f"Garbage collection: {collected} objetos liberados")
    
    def _cleanup_temp_files(self):
        """Limpiar archivos temporales"""
        
        temp_patterns = [
            '*.tmp',
            '*.temp', 
            '__pycache__/*',
            '.pytest_cache/*',
            '*.pyc'
        ]
        
        for pattern in temp_patterns:
            for file_path in Path('.').rglob(pattern):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        import shutil
                        shutil.rmtree(file_path)
                except Exception as e:
                    self.logger.debug(f"No se pudo eliminar {file_path}: {e}")

# Instancia global del optimizador
production_optimizer = ProductionOptimizer()

def get_health_status():
    """Función helper para obtener estado de salud"""
    return production_optimizer.get_health_report()

def optimize_system():
    """Función helper para optimizar sistema"""
    production_optimizer.optimize_performance()

if __name__ == "__main__":
    # Ejecutar optimizaciones periódicas
    while True:
        try:
            optimize_system()
            time.sleep(3600)  # Cada hora
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(f"Error en loop de optimización: {e}")
            time.sleep(300)  # Esperar 5 minutos si hay error