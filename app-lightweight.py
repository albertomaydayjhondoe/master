#!/usr/bin/env python3
"""
🚀 Stakas MVP - Ultra Lightweight Launcher
Bandwidth optimized version for Railway deployment
"""
import os
import sys
from pathlib import Path

def main():
    """Launch ultra-lightweight Stakas MVP dashboard"""
    
    # Get port from Railway environment
    port = int(os.getenv('PORT', 8501))
    
    # Minimal environment setup
    os.environ.update({
        'STREAMLIT_SERVER_HEADLESS': 'true',
        'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false',
        'STREAMLIT_SERVER_ENABLE_CORS': 'false',
        'STREAMLIT_SERVER_MAX_UPLOAD_SIZE': '5',  # 5MB max
        'STREAMLIT_THEME_BASE': 'dark',
        'STREAMLIT_SERVER_RUN_ON_SAVE': 'false',  # Disable file watching
        'STREAMLIT_SERVER_FILE_WATCHER_TYPE': 'none',  # No file watching
        'STREAMLIT_BROWSER_SERVER_ADDRESS': '0.0.0.0'
    })
    
    # Launch with minimal resources
    import streamlit.web.cli as stcli
    sys.argv = [
        'streamlit',
        'run', 
        'scripts/viral_study_analysis_lightweight.py',
        f'--server.port={port}',
        '--server.address=0.0.0.0',
        '--server.headless=true',
        '--server.enableCORS=false',
        '--browser.gatherUsageStats=false',
        '--server.maxUploadSize=5',
        '--server.runOnSave=false',
        '--server.fileWatcherType=none'
    ]
    
    print(f"🎬 Stakas MVP Lightweight Starting...")
    print(f"📺 Channel: UCgohgqLVu1QPdfa64Vkrgeg")
    print(f"🚀 Port: {port}")
    print(f"⚡ Bandwidth: OPTIMIZED")
    
    stcli.main()

if __name__ == "__main__":
    main()