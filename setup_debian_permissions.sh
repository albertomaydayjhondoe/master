#!/bin/bash
# 🔧 DEBIAN PERMISSIONS SETUP - STAKAS VIRAL SYSTEM
# Script para establecer permisos correctos en Debian/Railway

echo "🔧 Configurando permisos para Debian..."

# Establecer permisos para archivos Python principales
chmod +x railway_launcher.py
chmod +x universal_startup.py  
chmod +x unified_system_production.py
chmod +x cross_platform_launcher.py
chmod +x fix_cross_platform.py

# ML Core API
chmod +x ml_core/api/main.py

# Scripts del sistema
find scripts/ -name "*.py" -type f -exec chmod +x {} \;

# Dashboards
chmod +x scripts/dashboard_metricas_ultimo_mes.py
chmod +x scripts/dashboard_utms_completo.py

# Device Farm
find device_farm/ -name "*.py" -type f -exec chmod +x {} \;

# GoLogin Automation
find gologin_automation/ -name "*.py" -type f -exec chmod +x {} \;

# Monitoring
find monitoring/ -name "*.py" -type f -exec chmod +x {} \;

# Orchestration
find orchestration/ -name "*.py" -type f -exec chmod +x {} \;

# Meta Ads System
chmod +x meta_ads_centric_system.py

# Todos los archivos .sh
find . -name "*.sh" -type f -exec chmod +x {} \;

echo "✅ Permisos configurados correctamente para Debian"
echo "🚀 Sistema listo para ejecutarse en Railway"