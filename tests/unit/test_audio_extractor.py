#!/usr/bin/env python3
"""
Test script for the new audio extractor.
"""

import sys
import os
from pathlib import Path

# Add the server directory to the path
server_path = os.path.join(os.path.dirname(__file__), 'server')
sys.path.insert(0, server_path)

def test_audio_extractor():
    """Test the audio extractor."""
    
    print("Testing Audio Extractor")
    print("=" * 25)
    
    try:
        # Test 1: Import audio extractor
        print("1. Testing audio extractor import...")
        from extractor.extractors.audio_extractor import AudioExtractor
        from extractor.core.base_engine import ExtractionContext
        
        extractor = AudioExtractor()
        print(f"   ✅ Audio extractor created: {extractor.name}")
        print(f"   ✅ Supported formats: {len(extractor.supported_formats)} formats")
        print(f"   ✅ First few formats: {extractor.supported_formats[:8]}")
        
        # Test 2: Test with non-existent file (should handle gracefully)
        print("2. Testing with non-existent file...")
        context = ExtractionContext(
            filepath="nonexistent.mp3",
            file_size=1024,
            file_extension=".mp3",
            mime_type="audio/mpeg",
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
        
        # Test 4: Test mutagen availability
        print("4. Testing mutagen availability...")
        try:
            import mutagen
            print("   ✅ Mutagen is available")
        except ImportError:
            print("   ⚠️  Mutagen not available")
        
        print("\n✅ Audio extractor tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Audio extractor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_audio_extractor()
    if success:
        print("\n🎉 Audio extractor ready!")
    else:
        print("\n❌ Audio extractor needs fixes.")