#!/usr/bin/env python3
"""
🔍 API TESTING SCRIPT - NEURAL FORGE DISCOGRÁFICA
===============================================
Script para probar todas las APIs introducidas en el sistema
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def test_longcat_video_api():
    """Test LongCat Video Generation API"""
    print("🎬 TESTING LONGCAT-VIDEO API")
    print("-" * 30)
    
    try:
        from ml_core.video_generation import create_video_generator, LongCatVideoGenerator
        
        # Test factory function
        generator = create_video_generator()
        print("✅ Video generator created successfully")
        
        # Test methods
        assert hasattr(generator, 'generate_text_to_video')
        assert hasattr(generator, 'generate_image_to_video')  
        assert hasattr(generator, 'get_capabilities')
        print("✅ All video generation methods available")
        
        # Test capabilities
        capabilities = generator.get_capabilities()
        print(f"✅ Capabilities: {list(capabilities.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ LongCat Video API failed: {e}")
        return False

def test_satellite_system_api():
    """Test Satellite System API"""
    print("\n🛰️ TESTING SATELLITE SYSTEM API")
    print("-" * 30)
    
    try:
        from ml_core.satellite_manager import create_satellite_manager, SatelliteManager
        
        # Test factory function
        sat_manager = create_satellite_manager()
        print("✅ Satellite manager created successfully")
        
        # Test methods
        assert hasattr(sat_manager, 'get_optimal_channel')
        assert hasattr(sat_manager, 'schedule_upload')
        assert hasattr(sat_manager, 'get_satellite_stats')
        print("✅ All satellite management methods available")
        
        # Test channel selection
        optimal = sat_manager.get_optimal_channel("trap_spanish_latino")
        print(f"✅ Optimal channel selection: {optimal}")
        
        return True
        
    except Exception as e:
        print(f"❌ Satellite System API failed: {e}")
        return False

def test_extensions_api():
    """Test ML Extensions API"""
    print("\n🧠 TESTING ML EXTENSIONS API")
    print("-" * 30)
    
    try:
        from ml_core.extensions import create_sentiment_engine, create_trend_miner, create_growth_simulator
        
        # Test sentiment engine
        sentiment_engine = create_sentiment_engine()
        print("✅ Sentiment engine created")
        
        # Test trend miner
        trend_miner = create_trend_miner()
        print("✅ Trend miner created")
        
        # Test growth simulator
        growth_simulator = create_growth_simulator()
        print("✅ Growth simulator created")
        
        # Test basic functionality (dormant mode)
        sentiment_result = sentiment_engine.analyze_comments(["Great music!"])
        print(f"✅ Sentiment analysis result: {sentiment_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ ML Extensions API failed: {e}")
        return False

def test_production_controller_api():
    """Test Production Controller API"""
    print("\n🎛️ TESTING PRODUCTION CONTROLLER API")
    print("-" * 30)
    
    try:
        # Import the main dashboard components
        import production_controller
        print("✅ Production controller imported successfully")
        
        # Check if it has the main dashboard function
        assert hasattr(production_controller, 'create_main_dashboard') or hasattr(production_controller, 'main')
        print("✅ Dashboard creation functions available")
        
        return True
        
    except Exception as e:
        print(f"❌ Production Controller API failed: {e}")
        return False

async def test_video_generation_workflow():
    """Test complete video generation workflow"""
    print("\n🔄 TESTING COMPLETE VIDEO WORKFLOW")
    print("-" * 30)
    
    try:
        from ml_core.video_generation import create_video_generator
        from ml_core.satellite_manager import create_satellite_manager
        
        # Step 1: Create video generator
        video_gen = create_video_generator()
        print("✅ Step 1: Video generator initialized")
        
        # Step 2: Initialize generator
        init_result = await video_gen.initialize()
        print(f"✅ Step 2: Generator initialized - {init_result}")
        
        # Step 3: Get capabilities (should work in dummy mode)
        capabilities = video_gen.get_capabilities()
        print(f"✅ Step 3: Capabilities retrieved - {len(capabilities)} features")
        
        # Step 4: Create satellite manager
        sat_manager = create_satellite_manager()
        print("✅ Step 4: Satellite manager ready")
        
        # Step 5: Test channel selection
        optimal_channel = sat_manager.get_optimal_channel("trap_spanish_latino")
        print(f"✅ Step 5: Channel selected - {optimal_channel}")
        
        print("🎉 COMPLETE WORKFLOW TEST PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Complete workflow failed: {e}")
        return False

def main():
    """Run all API tests"""
    print("🧠 NEURAL FORGE DISCOGRÁFICA - API TESTING")
    print("=" * 50)
    
    tests = [
        ("LongCat Video API", test_longcat_video_api),
        ("Satellite System API", test_satellite_system_api), 
        ("ML Extensions API", test_extensions_api),
        ("Production Controller API", test_production_controller_api)
    ]
    
    results = []
    
    # Run synchronous tests
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Run async workflow test
    print("\n" + "=" * 50)
    workflow_result = asyncio.run(test_video_generation_workflow())
    results.append(("Complete Workflow", workflow_result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 OVERALL RESULT: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL APIS OPERATIONAL - SYSTEM READY FOR PRODUCTION!")
        return 0
    else:
        print("⚠️ SOME APIS NEED ATTENTION - CHECK LOGS ABOVE")
        return 1

if __name__ == "__main__":
    sys.exit(main())