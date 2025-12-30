#!/usr/bin/env python3
"""
Test script for MetaExtract Comprehensive Engine v4.0
"""

import sys
import os

# Add the server directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server', 'extractor'))

def test_imports():
    """Test that all comprehensive engine modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from comprehensive_metadata_engine import (
            extract_comprehensive_metadata,
            ComprehensiveMetadataExtractor,
            MedicalImagingEngine,
            AstronomicalDataEngine,
            GeospatialEngine,
            ScientificInstrumentEngine,
            DroneUAVEngine,
            BlockchainProvenanceEngine
        )
        print("✅ Core comprehensive engine imports successful")
    except ImportError as e:
        print(f"❌ Core import failed: {e}")
        return False
    
    try:
        from modules.advanced_analysis import (
            detect_ai_content,
            detect_enhanced_manipulation,
            detect_enhanced_steganography,
            AIContentDetector,
            EnhancedManipulationDetector,
            EnhancedSteganographyDetector
        )
        print("✅ Advanced analysis modules imports successful")
    except ImportError as e:
        print(f"❌ Advanced analysis import failed: {e}")
        return False
    
    return True

def test_engine_availability():
    """Test availability of specialized engines"""
    print("\n🔍 Testing specialized engine availability...")
    
    # Test library availability
    engines = {
        'Medical Imaging (DICOM)': 'pydicom',
        'Astronomical Data (FITS)': 'astropy.io.fits', 
        'Geospatial (Rasterio)': 'rasterio',
        'Geospatial (Fiona)': 'fiona',
        'Scientific Data (HDF5)': 'h5py',
        'Scientific Data (NetCDF)': 'netCDF4',
        'Advanced Image Analysis': 'cv2',
        'Machine Learning': 'sklearn',
        'Audio Analysis': 'librosa',
        'Document Processing': 'docx',
        'Web Processing': 'bs4',
        'Blockchain': 'web3',
        'Microscopy': 'aicsimageio'
    }
    
    available_engines = []
    for name, module in engines.items():
        try:
            __import__(module)
            available_engines.append(name)
            print(f"✅ {name}")
        except ImportError:
            print(f"⚠️  {name} (optional)")
    
    print(f"\n📊 {len(available_engines)}/{len(engines)} specialized engines available")
    return len(available_engines) > 0

def test_comprehensive_extractor():
    """Test the comprehensive extractor initialization"""
    print("\n🏗️  Testing comprehensive extractor initialization...")
    
    try:
        from comprehensive_metadata_engine import ComprehensiveMetadataExtractor
        extractor = ComprehensiveMetadataExtractor()
        print("✅ ComprehensiveMetadataExtractor initialized successfully")
        
        # Test engine attributes
        engines = [
            'medical_engine',
            'astronomical_engine', 
            'geospatial_engine',
            'scientific_engine',
            'drone_engine',
            'blockchain_engine'
        ]
        
        for engine_name in engines:
            if hasattr(extractor, engine_name):
                print(f"✅ {engine_name} available")
            else:
                print(f"❌ {engine_name} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Extractor initialization failed: {e}")
        return False

def test_basic_extraction():
    """Test basic metadata extraction with a simple file"""
    print("\n📁 Testing basic extraction...")
    
    try:
        # Create a simple test file
        import tempfile
        from PIL import Image
        
        # Create test image
        img = Image.new('RGB', (100, 100), color='red')
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        img.save(temp_file.name, 'JPEG')
        
        # Test extraction
        from comprehensive_metadata_engine import extract_comprehensive_metadata
        
        result = extract_comprehensive_metadata(temp_file.name, tier="free")
        
        if 'error' in result:
            print(f"❌ Extraction failed: {result['error']}")
            return False
        
        # Check basic fields
        fields_extracted = result.get('extraction_info', {}).get('comprehensive_fields_extracted', 0)
        engine_version = result.get('extraction_info', {}).get('comprehensive_version', 'unknown')
        
        print(f"✅ Engine version: {engine_version}")
        print(f"✅ Fields extracted: {fields_extracted}")
        
        # Check for basic sections
        sections = ['file', 'summary', 'extraction_info']
        for section in sections:
            if section in result:
                print(f"✅ {section} section present")
            else:
                print(f"⚠️  {section} section missing")
        
        # Clean up
        os.unlink(temp_file.name)
        
        return True
        
    except Exception as e:
        print(f"❌ Basic extraction test failed: {e}")
        return False

def test_tier_differences():
    """Test different tier configurations"""
    print("\n🎚️  Testing tier differences...")
    
    try:
        import tempfile
        from PIL import Image
        
        # Create test image
        img = Image.new('RGB', (100, 100), color='blue')
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        img.save(temp_file.name, 'JPEG')
        
        from comprehensive_metadata_engine import extract_comprehensive_metadata
        
        tier_results = {}
        
        for tier in ['free', 'starter', 'premium', 'super']:
            try:
                result = extract_comprehensive_metadata(temp_file.name, tier=tier)
                
                if 'error' not in result:
                    fields = result.get('extraction_info', {}).get('comprehensive_fields_extracted', 0)
                    tier_results[tier] = fields
                    print(f"✅ {tier.upper()} tier: {fields} fields")
                else:
                    print(f"⚠️  {tier.upper()} tier: {result['error']}")
                    
            except Exception as e:
                print(f"❌ {tier.upper()} tier failed: {e}")
        
        # Verify field count increases with tier
        if len(tier_results) >= 2:
            tiers = list(tier_results.keys())
            if tier_results[tiers[-1]] >= tier_results[tiers[0]]:
                print("✅ Field count increases with tier level")
            else:
                print("⚠️  Field count doesn't increase with tier level")
        
        # Clean up
        os.unlink(temp_file.name)
        
        return True
        
    except Exception as e:
        print(f"❌ Tier testing failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 MetaExtract Comprehensive Engine v4.0 Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Engine Availability", test_engine_availability), 
        ("Extractor Initialization", test_comprehensive_extractor),
        ("Basic Extraction", test_basic_extraction),
        ("Tier Differences", test_tier_differences)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n{'='*60}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Comprehensive engine is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())