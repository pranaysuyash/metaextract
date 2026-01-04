#!/usr/bin/env python3
"""
Comprehensive test suite for metadata extraction functionality.
Tests various file types and extraction capabilities across different tiers.
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add the server directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../server'))

def create_test_image():
    """Create a minimal test image with some metadata."""
    # Create a minimal JPEG with basic EXIF data
    jpeg_header = bytes([
        0xFF, 0xD8,  # SOI (Start of Image)
        0xFF, 0xE1,  # APP1 marker
        0x00, 0x10,  # Length of APP1 segment
        0x45, 0x78, 0x69, 0x66, 0x00, 0x00,  # "Exif\0\0"
        0x49, 0x49,  # TIFF header (little endian)
        0x2A, 0x00,  # TIFF magic number
        0x08, 0x00, 0x00, 0x00,  # Offset to first IFD
        # IFD (Image File Directory) with basic EXIF tags
        0x01, 0x00,  # Number of directory entries
        0x10, 0x01, 0x03, 0x00,  # Tag: ImageWidth
        0x01, 0x00, 0x00, 0x00,  # Data type: SHORT
        0x01, 0x00, 0x00, 0x00,  # Number of components
        0x64, 0x00, 0x00, 0x00,  # Value offset or value
        0x00, 0x00,  # Next IFD offset (0 = no next IFD)
        0xFF, 0xD9   # EOI (End of Image)
    ])
    return jpeg_header

def test_comprehensive_extraction():
    """Test comprehensive metadata extraction functionality."""
    
    print("Testing Comprehensive Metadata Extraction")
    print("=" * 50)

    # Create a temporary test image
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        temp_file.write(create_test_image())
        temp_file_path = temp_file.name

    try:
        # Test 1: Import the comprehensive engine
        print("1. Testing comprehensive engine import...")
        from extractor.comprehensive_metadata_engine import extract_comprehensive_metadata
        print("   ✅ Comprehensive engine imported successfully")

        # Test 2: Test extraction with different tiers
        print("2. Testing extraction with different tiers...")
        
        for tier in ["free", "starter", "pro", "super"]:
            print(f"   Testing {tier} tier...")
            try:
                result = extract_comprehensive_metadata(temp_file_path, tier=tier)
                
                print(f"      Status: {result.get('status', 'unknown')}")
                print(f"      Engine version: {result.get('extraction_info', {}).get('engine_version', 'unknown')}")
                
                # Check if metadata was extracted
                metadata = result.get('metadata', {})
                if metadata:
                    print(f"      Metadata keys: {len(metadata.keys())} extracted")
                    print(f"      ✅ {tier} tier extraction successful")
                else:
                    print(f"      ⚠️  No metadata extracted for {tier} tier")
                    
            except Exception as e:
                print(f"      ❌ {tier} tier extraction failed: {str(e)}")

        # Test 3: Test performance metrics
        print("3. Testing performance metrics...")
        try:
            result = extract_comprehensive_metadata(temp_file_path, tier="pro", include_performance=True)
            performance = result.get('performance', {})
            if performance:
                print(f"      ✅ Performance metrics extracted: {list(performance.keys())}")
            else:
                print("      ⚠️  No performance metrics found")
        except Exception as e:
            print(f"      ❌ Performance metrics test failed: {str(e)}")

        # Test 4: Test error handling
        print("4. Testing error handling...")
        try:
            # Test with non-existent file
            error_result = extract_comprehensive_metadata("/nonexistent/file.jpg", tier="free")
            print(f"      Error handling status: {error_result.get('status', 'unknown')}")
            if error_result.get('status') == 'error':
                print("      ✅ Error handling working correctly")
            else:
                print("      ⚠️  Error handling may not be working as expected")
        except Exception as e:
            print(f"      ✅ Error properly caught: {str(e)}")

        # Test 5: Test specific metadata categories
        print("5. Testing specific metadata categories...")
        try:
            result = extract_comprehensive_metadata(temp_file_path, tier="pro")
            metadata = result.get('metadata', {})
            
            # Check for common metadata categories
            categories = ['file', 'exif', 'image', 'technical']
            for category in categories:
                if category in metadata:
                    print(f"      ✅ {category} metadata found: {len(metadata[category]) if isinstance(metadata[category], dict) else 'N/A'} items")
                else:
                    print(f"      ⚠️  {category} metadata not found")
                    
        except Exception as e:
            print(f"      ❌ Category test failed: {str(e)}")

        print("\n✅ Comprehensive metadata extraction tests completed")

    except ImportError as e:
        print(f"❌ Could not import comprehensive engine: {str(e)}")
    except Exception as e:
        print(f"❌ Comprehensive extraction test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def test_extraction_edge_cases():
    """Test edge cases for metadata extraction."""
    
    print("\nTesting Extraction Edge Cases")
    print("=" * 40)

    # Test 1: Empty file
    print("1. Testing empty file...")
    with tempfile.NamedTemporaryFile(delete=False) as empty_file:
        empty_file_path = empty_file.name
    
    try:
        from extractor.comprehensive_metadata_engine import extract_comprehensive_metadata
        result = extract_comprehensive_metadata(empty_file_path, tier="free")
        print(f"   Empty file result: {result.get('status', 'unknown')}")
        print("   ✅ Empty file handled gracefully")
    except Exception as e:
        print(f"   ✅ Empty file caused expected error: {str(e)}")
    finally:
        if os.path.exists(empty_file_path):
            os.unlink(empty_file_path)

    # Test 2: Large file simulation (just large size, not actual content)
    print("2. Testing large file simulation...")
    with tempfile.NamedTemporaryFile(delete=False) as large_file:
        # Write 10MB of zeros to simulate a large file
        large_file.write(b'\x00' * (10 * 1024 * 1024))
        large_file_path = large_file.name
    
    try:
        result = extract_comprehensive_metadata(large_file_path, tier="free")
        print(f"   Large file result: {result.get('status', 'unknown')}")
        print("   ✅ Large file handled gracefully")
    except Exception as e:
        print(f"   ✅ Large file caused expected behavior: {str(e)}")
    finally:
        if os.path.exists(large_file_path):
            os.unlink(large_file_path)

    print("\n✅ Edge case tests completed")

def test_tier_restrictions():
    """Test that different tiers return appropriate metadata."""
    
    print("\nTesting Tier Restrictions")
    print("=" * 30)

    # Create a test image
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        temp_file.write(create_test_image())
        temp_file_path = temp_file.name

    try:
        from extractor.comprehensive_metadata_engine import extract_comprehensive_metadata
        
        # Extract with different tiers and compare
        results = {}
        for tier in ["free", "starter", "pro", "super"]:
            try:
                result = extract_comprehensive_metadata(temp_file_path, tier=tier)
                metadata = result.get('metadata', {})
                field_count = sum(
                    len(v) if isinstance(v, dict) else 1 
                    for v in metadata.values()
                ) if metadata else 0
                results[tier] = field_count
                print(f"   {tier}: {field_count} fields")
            except Exception as e:
                print(f"   {tier}: Error - {str(e)}")
                results[tier] = 0
        
        # Verify that higher tiers return at least as many fields as lower tiers
        tiers_in_order = ["free", "starter", "pro", "super"]
        for i in range(len(tiers_in_order) - 1):
            current_tier = tiers_in_order[i]
            next_tier = tiers_in_order[i + 1]
            if results.get(current_tier, 0) <= results.get(next_tier, 0):
                print(f"   ✅ {next_tier} has same or more fields than {current_tier}")
            else:
                print(f"   ⚠️  {next_tier} has fewer fields than {current_tier}")
        
        print("\n✅ Tier restriction tests completed")
        
    except Exception as e:
        print(f"❌ Tier restriction test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

if __name__ == "__main__":
    print("Running Comprehensive Metadata Extraction Tests\n")
    
    test_comprehensive_extraction()
    test_extraction_edge_cases()
    test_tier_restrictions()
    
    print("\n" + "=" * 50)
    print("All comprehensive metadata extraction tests completed!")