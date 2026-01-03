#!/usr/bin/env python3
"""
Test script for the new video extractor.
"""

import sys
import os
from pathlib import Path

# Add the server directory to the path
server_path = os.path.join(os.path.dirname(__file__), 'server')
sys.path.insert(0, server_path)

def test_video_extractor():
    """Test the video extractor."""
    
    print("Testing Video Extractor")
    print("=" * 25)
    
    try:
        # Test 1: Import video extractor
        print("1. Testing video extractor import...")
        from extractor.extractors.video_extractor import VideoExtractor
        from extractor.core.base_engine import ExtractionContext
        
        extractor = VideoExtractor()
        print(f"   ✅ Video extractor created: {extractor.name}")
        print(f"   ✅ Supported formats: {len(extractor.supported_formats)} formats")
        print(f"   ✅ First few formats: {extractor.supported_formats[:5]}")
        
        # Test 2: Test with non-existent file (should handle gracefully)
        print("2. Testing with non-existent file...")
        context = ExtractionContext(
            filepath="nonexistent.mp4",
            file_size=1024,
            file_extension=".mp4",
            mime_type="video/mp4",
            tier="free",
            processing_options={},
            execution_stats={}
        )
        
        result = extractor.extract(context)
        print(f"   ✅ Extraction status: {result.status}")
        print(f"   ✅ Processing time: {result.processing_time_ms}ms")
        
        if result.metadata:
            print(f"   ✅ Metadata sections: {list(result.metadata.keys())}")
        
        # Test 3: Test extractor info
        print("3. Testing extractor info...")
        info = extractor.get_extraction_info()
        print(f"   ✅ Extractor info: {info}")
        
        # Test 4: Test ffprobe availability
        print("4. Testing ffprobe availability...")
        try:
            result = subprocess.run(['ffprobe', '-version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("   ✅ ffprobe is available")
            else:
                print("   ⚠️  ffprobe test failed")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("   ⚠️  ffprobe not available")
        
        print("\n✅ Video extractor tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Video extractor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import subprocess
    success = test_video_extractor()
    if success:
        print("\n🎉 Video extractor ready!")
    else:
        print("\n❌ Video extractor needs fixes.")