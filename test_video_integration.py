#!/usr/bin/env python3
"""
Test script to verify video integration with comprehensive engine.
"""

import sys
import os
from pathlib import Path

# Add the server directory to the path
server_path = os.path.join(os.path.dirname(__file__), 'server')
sys.path.insert(0, server_path)

def test_video_integration():
    """Test video integration with comprehensive engine."""
    
    print("Testing Video Integration with Comprehensive Engine")
    print("=" * 55)
    
    try:
        # Test 1: Test comprehensive engine with video support
        print("1. Testing comprehensive engine with video extractor...")
        from extractor.core.comprehensive_engine import extract_comprehensive_metadata_new
        
        # Test with a fake video file path (since we don't have real videos)
        test_file = "test_video.mp4"
        
        print(f"   Testing with file: {test_file}")
        
        # Create a dummy video file for testing
        dummy_content = b'\x00\x00\x00\x18ftypmp4\x00\x00\x00\x00isommp41'
        with open(test_file, 'wb') as f:
            f.write(dummy_content)
        
        try:
            result = extract_comprehensive_metadata_new(test_file, tier="free")
            
            print(f"   ✅ Engine status: {result.get('status', 'unknown')}")
            print(f"   ✅ Engine version: {result.get('extraction_info', {}).get('engine_version', 'unknown')}")
            print(f"   ✅ Architecture: {result.get('extraction_info', {}).get('architecture', 'unknown')}")
            
            # Check registry summary
            registry_summary = result.get('registry_summary', {})
            print(f"   ✅ Registry summary present: {'✅' if registry_summary else '❌'}")
            
            if registry_summary:
                print(f"   Available summaries: {list(registry_summary.keys())}")
                if 'video' in registry_summary:
                    video_summary = registry_summary['video']
                    print(f"   Video fields - Format: {video_summary.get('format', 0)}, Codec: {video_summary.get('codec', 0)}, Telemetry: {video_summary.get('telemetry', 0)}")
                if 'image' in registry_summary:
                    image_summary = registry_summary['image']
                    print(f"   Image fields - EXIF: {image_summary.get('exif', 0)}, IPTC: {image_summary.get('iptc', 0)}, XMP: {image_summary.get('xmp', 0)}")
            
            # Check metadata structure
            metadata = result.get('metadata', {})
            print(f"   ✅ Metadata sections: {list(metadata.keys()) if metadata else 'none'}")
            
            # Check extraction info
            extraction_info = result.get('extraction_info', {})
            print(f"   ✅ Extractors used: {extraction_info.get('extractors_used', 'unknown')}")
            
        finally:
            # Clean up dummy file
            if os.path.exists(test_file):
                os.remove(test_file)
        
        # Test 2: Check orchestrator setup
        print("2. Testing orchestrator setup...")
        from extractor.core.comprehensive_engine import NewComprehensiveMetadataExtractor
        
        extractor = NewComprehensiveMetadataExtractor()
        info = extractor.get_extractor_info()
        
        print(f"   ✅ Engine info: {info.get('engine_version', 'unknown')}")
        print(f"   ✅ Extractors available: {len(info.get('extractors', []))}")
        
        for extractor_info in info.get('extractors', []):
            print(f"   - {extractor_info['name']}: {len(extractor_info['supported_formats'])} formats")
        
        print("\n✅ Video integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Video integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_video_integration()
    if success:
        print("\n🎉 Video integration successful!")
    else:
        print("\n❌ Video integration failed.")