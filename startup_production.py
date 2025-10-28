#!/usr/bin/env python3
"""🚀 Production Startup Script for Railway Deployment

Inicia el sistema completo de producción Meta Ads Centric con todas las funcionalidades:
- Sistema unificado de producción 
- Dashboard Streamlit
- APIs FastAPI
- Monitoreo continuo

Diseñado para Railway deployment con optimización de recursos.
"""
import os
import sys
import asyncio
import logging
import multiprocessing
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Configurar entorno de producción."""
    logger.info("🔧 Setting up production environment...")
    
    # Ensure production mode
    os.environ["DUMMY_MODE"] = "false" 
    os.environ["ENVIRONMENT"] = "production"
    os.environ["PYTHONPATH"] = str(Path(__file__).parent)
    
    # Railway specific
    port = os.environ.get("PORT", "8501")
    os.environ["STREAMLIT_SERVER_PORT"] = port
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    
    logger.info(f"✅ Environment configured - Port: {port}")

def start_streamlit_dashboard():
    """Iniciar dashboard Streamlit."""
    import subprocess
    
    logger.info("📊 Starting Streamlit dashboard...")
    
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        "scripts/viral_study_analysis_lightweight.py",
        "--server.port", os.environ.get("PORT", "8501"),
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
        "--server.fileWatcherType", "none"
    ]
    
    return subprocess.Popen(cmd)

def start_ml_api():
    """Iniciar ML API en proceso separado."""
    import subprocess
    
    logger.info("🧠 Starting ML Core API...")
    
    cmd = [
        sys.executable, "-m", "uvicorn",
        "ml_core.api.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--workers", "1"
    ]
    
    return subprocess.Popen(cmd)

async def start_unified_system():
    """Iniciar sistema unificado en background."""
    try:
        logger.info("🎯 Starting unified production system...")
        
        # Import and run unified system
        from unified_system_production import UnifiedProductionSystem
        
        system = UnifiedProductionSystem()
        initialized = await system.initialize_full_system()
        
        if initialized:
            logger.info("✅ Unified system initialized successfully")
            
            # Run monitoring in background
            asyncio.create_task(system.run_continuous_monitoring())
            return system
        else:
            logger.error("❌ Unified system initialization failed")
            return None
            
    except Exception as e:
        logger.error(f"❌ Unified system startup error: {str(e)}")
        return None

def main():
    """Función principal de startup."""
    logger.info("🚀 Starting Meta Ads Centric Production System")
    
    # Setup environment
    setup_environment()
    
    processes = []
    
    try:
        # Start ML API in background
        ml_process = start_ml_api()
        processes.append(ml_process)
        logger.info("✅ ML API started")
        
        # Start unified system
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        system = loop.run_until_complete(start_unified_system())
        if system:
            logger.info("✅ Unified system running")
        
        # Start Streamlit dashboard (main process)
        logger.info("📊 Starting main dashboard...")
        streamlit_process = start_streamlit_dashboard()
        processes.append(streamlit_process)
        
        # Keep main process alive
        logger.info("🎯 Meta Ads Centric System fully operational!")
        logger.info(f"🌐 Dashboard: http://0.0.0.0:{os.environ.get('PORT', '8501')}")
        logger.info("📊 All systems running in production mode")
        
        # Wait for main Streamlit process
        streamlit_process.wait()
        
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown signal received")
    except Exception as e:
        logger.error(f"❌ Startup error: {str(e)}")
    finally:
        # Cleanup processes
        for process in processes:
            if process.poll() is None:
                process.terminate()
                process.wait()
        
        logger.info("✅ All processes terminated")

if __name__ == "__main__":
    main()