#!/usr/bin/env python3
"""
🚀 Stakas MVP - Viral Dashboard Launcher
Production-ready launcher for Railway deployment
"""
import os
import sys
import uvicorn
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Launch the Stakas MVP viral dashboard"""
    
    # Get port from environment (Railway sets this)
    port = int(os.getenv('PORT', 8501))
    
    # Launch Streamlit dashboard
    os.system(f"""
        streamlit run scripts/viral_study_analysis.py \
            --server.port={port} \
            --server.address=0.0.0.0 \
            --server.headless=true \
            --server.runOnSave=true \
            --browser.serverAddress=0.0.0.0 \
            --browser.gatherUsageStats=false
    """)

if __name__ == "__main__":
    print("🎬 Starting Stakas MVP Viral Dashboard...")
    print(f"📺 Target Channel: UCgohgqLVu1QPdfa64Vkrgeg")
    print(f"🎯 Goal: 0→10K subscribers via viral content")
    print(f"🚀 Port: {os.getenv('PORT', 8501)}")
    main()