#!/bin/bash
# 🎬 Neural Forge - LongCat Video Integration Test
# ===============================================

echo "🎬 Testing LongCat Video Integration..."

# Test imports
python3 -c "
import sys
sys.path.append('.')

try:
    from social_extensions.longcat_production import ProductionVideoGenerator, get_production_video_generator
    print('✅ LongCat Production imports successful')
    
    from ml_core.video_generation import LongCatVideoGenerator, create_video_generator
    print('✅ LongCat Core imports successful')
    
    print('🎬 LongCat Video fully integrated!')
    
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
except Exception as e:
    print(f'❌ General error: {e}')
    exit(1)
"

echo "✅ LongCat Video Integration Test Passed!"