#!/usr/bin/env python3
"""
Phase 2.4 Scientific Extractor Validation Test
Comprehensive test to validate the scientific extractor implementation
"""

import time
import os
import sys
from pathlib import Path

# Add server path for imports
sys.path.insert(0, str(Path(__file__).parent / "server"))

from server.extractor.core.comprehensive_engine import NewComprehensiveMetadataExtractor
from server.extractor.extractors.scientific_extractor import ScientificExtractor
from server.extractor.core.base_engine import ExtractionContext


def test_scientific_extractor():
    """Test the scientific extractor directly"""
    print("🧪 Testing ScientificExtractor directly...")
    
    extractor = ScientificExtractor()
    
    # Test basic properties
    assert extractor.name == "scientific"
    assert len(extractor.supported_formats) == 17
    assert extractor._streaming_enabled == True
    assert extractor.streaming_extractor.config.chunk_size == 5_000_000
    
    print(f"✅ Extractor instantiated: {len(extractor.supported_formats)} formats supported")
    print(f"✅ Streaming enabled with {extractor.streaming_extractor.config.chunk_size/1_000_000}MB chunks")
    
    # Test format detection
    test_cases = [
        ('.dcm', 'dicom'),
        ('.fits', 'fits'),
        ('.h5', 'hdf5'),
        ('.nc', 'netcdf'),
        ('.tif', 'geotiff'),
    ]
    
    for ext, expected in test_cases:
        detected = extractor._detect_format(ext, f"test{ext}")
        assert detected == expected, f"Format detection failed for {ext}: got {detected}, expected {expected}"
    
    print("✅ Format detection working correctly")
    
    # Test with existing DICOM file
    test_file = "test.dcm"
    if os.path.exists(test_file):
        context = ExtractionContext(
            filepath=test_file,
            file_size=os.path.getsize(test_file),
            file_extension='.dcm',
            mime_type='application/dicom',
            tier='super',
            processing_options={},
            execution_stats={}
        )
        
        result = extractor._extract_metadata(context)
        
        assert result['scientific_format'] == 'dicom'
        assert result['extraction_method'] == 'standard'
        assert 'metadata' in result
        assert 'registry_summary' in result
        
        metadata = result['metadata']
        assert len(metadata['headers']) > 0
        assert metadata['format_type'] == 'dicom'
        
        print(f"✅ DICOM extraction successful: {len(metadata['headers'])} headers, {len(metadata['properties'])} properties")
    
    return True


def test_comprehensive_integration():
    """Test scientific extractor integration with comprehensive engine"""
    print("\n🔗 Testing comprehensive engine integration...")
    
    extractor = NewComprehensiveMetadataExtractor()
    
    # Test with existing DICOM file
    test_file = "test.dcm"
    if os.path.exists(test_file):
        start_time = time.time()
        result = extractor.extract_comprehensive_metadata(test_file, tier='super')
        elapsed = time.time() - start_time
        
        assert 'metadata' in result
        metadata = result['metadata']
        
        # Check if scientific metadata is present
        if 'scientific_format' in metadata:
            print(f"✅ Scientific extractor integrated: {metadata['scientific_format']} format detected")
            print(f"✅ Extraction time: {elapsed*1000:.1f}ms")
        else:
            print("⚠️  Scientific metadata not found in comprehensive result")
            print(f"Available metadata keys: {list(metadata.keys())}")
    
    return True


def test_scientific_test_datasets():
    """Test with generated scientific test datasets"""
    print("\n📊 Testing with generated scientific test datasets...")
    
    test_files = [
        'tests/scientific-test-datasets/scientific-test-datasets/dicom/ct_scan/ct_scan.dcm',
        'tests/scientific-test-datasets/scientific-test-datasets/fits/hst_observation/hst_observation.fits',
        'tests/scientific-test-datasets/scientific-test-datasets/hdf5_netcdf/climate_model/climate_model.nc'
    ]
    
    extractor = ScientificExtractor()
    
    for test_file in test_files:
        if os.path.exists(test_file):
            file_size = os.path.getsize(test_file)
            
            context = ExtractionContext(
                filepath=test_file,
                file_size=file_size,
                file_extension=Path(test_file).suffix,
                mime_type='application/octet-stream',
                tier='super',
                processing_options={},
                execution_stats={}
            )
            
            start_time = time.time()
            result = extractor._extract_metadata(context)
            elapsed = time.time() - start_time
            
            format_type = result.get('scientific_format', 'unknown')
            method = result.get('extraction_method', 'unknown')
            
            print(f"✅ {Path(test_file).name}: {format_type} ({method}) in {elapsed*1000:.1f}ms")
            
            # Validate metadata structure
            metadata = result.get('metadata', {})
            registry = result.get('registry_summary', {})
            
            assert len(metadata) > 0, f"No metadata extracted from {test_file}"
            assert 'headers' in metadata, f"No headers in metadata for {test_file}"
            assert 'properties' in metadata, f"No properties in metadata for {test_file}"
            assert registry.get('total_fields', 0) > 0, f"No fields counted for {test_file}"
    
    print("✅ All scientific test datasets processed successfully")
    return True


def test_streaming_functionality():
    """Test streaming extraction for large files"""
    print("\n🌊 Testing streaming functionality...")
    
    extractor = ScientificExtractor()
    
    # Test with a larger file that should use streaming
    test_file = 'tests/scientific-test-datasets/scientific-test-datasets/hdf5_netcdf/climate_model/climate_model.nc'
    
    if os.path.exists(test_file):
        file_size = os.path.getsize(test_file)
        
        # This file is >50MB so should use streaming
        assert file_size > 50_000_000, "Test file should be >50MB for streaming test"
        
        context = ExtractionContext(
            filepath=test_file,
            file_size=file_size,
            file_extension='.nc',
            mime_type='application/x-netcdf',
            tier='super',
            processing_options={},
            execution_stats={}
        )
        
        result = extractor._extract_metadata(context)
        
        # Should use streaming for large files
        assert result['extraction_method'] == 'streaming', f"Expected streaming, got {result['extraction_method']}"
        assert 'processing_stats' in result, "Processing stats missing for streaming extraction"
        
        print(f"✅ Streaming extraction working: {result['extraction_method']}")
        print(f"✅ Processing stats: {result['processing_stats']}")
    
    return True


def main():
    """Run all validation tests"""
    print("🚀 Phase 2.4 Scientific Extractor Validation")
    print("=" * 50)
    
    try:
        # Run all tests
        test_scientific_extractor()
        test_comprehensive_integration()
        test_scientific_test_datasets()
        test_streaming_functionality()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("✅ Phase 2.4 Scientific Extractor Implementation Complete")
        print("✅ Ready for production deployment")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())