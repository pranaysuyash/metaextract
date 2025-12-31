#!/usr/bin/env python3
"""
Quick test script for newly implemented extraction functions
"""

import sys
import os
from pathlib import Path

# Add modules to path
sys.path.insert(0, '/Users/pranay/Projects/metaextract/server/extractor/modules')

def test_extraction_imports():
    """Test that new extraction functions can be imported"""
    print("Testing extraction function imports...")

    try:
        from makernotes_complete import extract_makernotes_metadata
        print("✅ makernotes_complete.extract_makernotes_metadata imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import makernotes extraction: {e}")

    try:
        from id3_frames_complete import extract_id3_frames_metadata
        print("✅ id3_frames_complete.extract_id3_frames_metadata imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ID3 extraction: {e}")

def test_function_signatures():
    """Test that extraction functions have correct signatures"""
    print("\nTesting function signatures...")

    try:
        from makernotes_complete import extract_makernotes_metadata
        import inspect

        sig = inspect.signature(extract_makernotes_metadata)
        params = list(sig.parameters.keys())
        print(f"✅ extract_makernotes_metadata parameters: {params}")

        if 'filepath' in params:
            print("✅ Correct parameter name 'filepath' found")
        else:
            print(f"❌ Expected 'filepath' parameter, got: {params}")

    except Exception as e:
        print(f"❌ Error checking makernotes signature: {e}")

    try:
        from id3_frames_complete import extract_id3_frames_metadata
        import inspect

        sig = inspect.signature(extract_id3_frames_metadata)
        params = list(sig.parameters.keys())
        print(f"✅ extract_id3_frames_metadata parameters: {params}")

        if 'filepath' in params:
            print("✅ Correct parameter name 'filepath' found")
        else:
            print(f"❌ Expected 'filepath' parameter, got: {params}")

    except Exception as e:
        print(f"❌ Error checking ID3 signature: {e}")

def test_basic_functionality():
    """Test basic functionality with None input (error handling)"""
    print("\nTesting basic functionality with error handling...")

    try:
        from makernotes_complete import extract_makernotes_metadata

        # Test with None to check error handling
        result = extract_makernotes_metadata(None)
        print(f"✅ extract_makernotes_metadata handles None input")
        print(f"   Result keys: {list(result.keys())[:5]}...")

        if 'fields_extracted' in result:
            print(f"✅ Returns expected structure with fields_extracted")
        else:
            print(f"❌ Missing expected keys in result")

    except Exception as e:
        print(f"⚠️  makernotes extraction raised exception (expected): {str(e)[:100]}")

    try:
        from id3_frames_complete import extract_id3_frames_metadata

        # Test with None to check error handling
        result = extract_id3_frames_metadata(None)
        print(f"✅ extract_id3_frames_metadata handles None input")
        print(f"   Result keys: {list(result.keys())[:5]}...")

        if 'fields_extracted' in result:
            print(f"✅ Returns expected structure with fields_extracted")
        else:
            print(f"❌ Missing expected keys in result")

    except Exception as e:
        print(f"⚠️  ID3 extraction raised exception (expected): {str(e)[:100]}")

def test_field_counts():
    """Test that field count functions work"""
    print("\nTesting field count functions...")

    try:
        from makernotes_complete import get_makernote_field_count
        count = get_makernote_field_count()
        print(f"✅ get_makernote_field_count returns: {count:,} fields")
    except Exception as e:
        print(f"❌ Error getting makernote field count: {e}")

    try:
        from id3_frames_complete import get_id3_frames_field_count
        count = get_id3_frames_field_count()
        print(f"✅ get_id3_frames_field_count returns: {count:,} fields")
    except Exception as e:
        print(f"❌ Error getting ID3 field count: {e}")

def main():
    print("="*60)
    print("NEW EXTRACTION FUNCTIONS TEST")
    print("="*60)

    test_extraction_imports()
    test_function_signatures()
    test_basic_functionality()
    test_field_counts()

    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()