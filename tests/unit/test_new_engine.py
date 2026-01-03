#!/usr/bin/env python3
"""
Test script for the new refactored comprehensive engine.
"""

import sys
import os
import json
from pathlib import Path

# Add the server directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from extractor.core.comprehensive_engine import extract_comprehensive_metadata_new, NewComprehensiveMetadataExtractor

def test_new_engine():
    """Test the new refactored comprehensive engine."""
    
    print("Testing New Comprehensive Metadata Engine")
    print("=" * 50)
    
    # Test with the sample image
    test_file = "test_ultra_comprehensive.jpg"
    
    if not os.path.exists(test_file):
        print(f"Test file {test_file} not found")
        return
    
    print(f"Testing with file: {test_file}")
    
    # Test the new engine
    try:
        extractor = NewComprehensiveMetadataExtractor()
        print(f"Extractor info: {extractor.get_extractor_info()}")
        
        result = extractor.extract_comprehensive_metadata(test_file, tier="free")
        
        print(f"Extraction status: {result.get('status', 'unknown')}")
        print(f"Engine version: {result.get('extraction_info', {}).get('engine_version', 'unknown')}")
        print(f"Architecture: {result.get('extraction_info', {}).get('architecture', 'unknown')}")
        print(f"Processing time: {result.get('extraction_info', {}).get('processing_time_ms', 'unknown')}ms")
        
        if 'metadata' in result and result['metadata']:
            print(f"Extracted metadata sections: {list(result['metadata'].keys())}")
            
            # Show some details
            metadata = result['metadata']
            if 'file_info' in metadata:
                print(f"File info: {metadata['file_info']}")
            if 'exif' in metadata:
                exif_sample = dict(list(metadata['exif'].items())[:3])
                print(f"Sample EXIF data: {exif_sample}")
            if 'gps' in metadata:
                print(f"GPS data: {metadata['gps']}")
        
        # Test compatibility function
        print("\nTesting compatibility function...")
        compat_result = extract_comprehensive_metadata_new(test_file, tier="free")
        print(f"Compatibility function status: {compat_result.get('status', 'unknown')}")
        
        # Compare with old engine (if available)
        print("\nComparing with old engine...")
        try:
            from extractor.comprehensive_metadata_engine import extract_comprehensive_metadata as old_extract
            old_result = old_extract(test_file, tier="free")
            
            print(f"Old engine status: {old_result.get('status', 'unknown')}")
            print(f"Old engine processing time: {old_result.get('extraction_info', {}).get('processing_ms', 'unknown')}ms")
            
            # Compare metadata keys
            old_keys = set(old_result.get('metadata', {}).keys())
            new_keys = set(result.get('metadata', {}).keys())
            
            print(f"Old engine metadata keys: {len(old_keys)}")
            print(f"New engine metadata keys: {len(new_keys)}")
            print(f"Common keys: {len(old_keys & new_keys)}")
            print(f"Keys only in old: {old_keys - new_keys}")
            print(f"Keys only in new: {new_keys - old_keys}")
            
        except Exception as e:
            print(f"Could not compare with old engine: {e}")
        
    except Exception as e:
        print(f"New engine test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_engine()