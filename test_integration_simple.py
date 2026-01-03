#!/usr/bin/env python3
"""
Simple test script to verify the integration.
"""

import sys
import os
from pathlib import Path

# Add the server directory to the path
server_path = os.path.join(os.path.dirname(__file__), 'server')
sys.path.insert(0, server_path)

def test_basic_imports():
    """Test basic imports work."""
    
    print("Testing Basic Integration")
    print("=" * 30)
    
    try:
        # Test 1: Import new comprehensive engine
        print("1. Testing new comprehensive engine import...")
        from extractor.core.comprehensive_engine import extract_comprehensive_metadata_new
        print("   ✅ New comprehensive engine imported successfully")
        
        # Test 2: Test the engine with a file
        print("2. Testing engine with sample file...")
        test_file = "test_ultra_comprehensive.jpg"
        
        if os.path.exists(test_file):
            result = extract_comprehensive_metadata_new(test_file, tier="free")
            print(f"   ✅ Engine executed successfully")
            print(f"   ✅ Status: {result.get('status', 'unknown')}")
            
            # Check if registry summary is present
            has_registry_summary = 'registry_summary' in result
            print(f"   ✅ Registry summary present: {has_registry_summary}")
            
            if has_registry_summary:
                print(f"   ✅ Registry summary: {result['registry_summary']}")
            
            # Check metadata structure
            metadata = result.get('metadata', {})
            if metadata:
                sections = list(metadata.keys())
                print(f"   ✅ Metadata sections: {sections}")
                
                # Count fields for tier logic
                field_count = sum(len(section) for section in metadata.values() if isinstance(section, dict))
                print(f"   ✅ Total fields: {field_count}")
            
        else:
            print("   ⚠️  Test file not found, skipping engine test")
        
        # Test 3: Check image extractor directly
        print("3. Testing image extractor...")
        from extractor.extractors.image_extractor import ImageExtractor
        from extractor.core.base_engine import ExtractionContext
        
        extractor = ImageExtractor()
        print(f"   ✅ Image extractor created: {extractor.name}")
        print(f"   ✅ Supported formats: {len(extractor.supported_formats)} formats")
        
        if os.path.exists(test_file):
            context = ExtractionContext(
                filepath=test_file,
                file_size=os.path.getsize(test_file),
                file_extension=Path(test_file).suffix.lower(),
                mime_type="image/jpeg",
                tier="free",
                processing_options={},
                execution_stats={}
            )
            
            result = extractor.extract(context)
            print(f"   ✅ Image extraction status: {result.status}")
            print(f"   ✅ Processing time: {result.processing_time_ms}ms")
            
        print("\n✅ Basic integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_imports()
    if success:
        print("\n🎉 Basic integration successful!")
    else:
        print("\n❌ Basic integration failed.")