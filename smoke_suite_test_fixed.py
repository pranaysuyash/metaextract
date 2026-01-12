#!/usr/bin/env python3
"""
Manual Smoke Suite Test - MetaExtract Core Functionality  
Tests 3 critical smoke tests to verify system health before deployment.
Updated to use actual function names from renamed modules.
"""

import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, '/Users/pranay/Projects/metaextract')

def test_smoke_1_basic_imports():
    """SMOKE TEST 1: Basic imports work correctly."""
    print("\n" + "="*70)
    print("🧪 SMOKE TEST 1: BASIC IMPORTS")
    print("="*70)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test renamed modules (our Phase 2 work) - all 17 files
    renamed_modules = [
        ('server.extractor.modules.camera_makernotes_advanced', 'Camera makernotes'),
        ('server.extractor.modules.cardiac_imaging', 'Cardiac imaging'),
        ('server.extractor.modules.neuroimaging', 'Neuroimaging'),
        ('server.extractor.modules.medical_astronomical', 'Medical/astronomical'),
        ('server.extractor.modules.emerging_tech', 'Emerging tech'),
        ('server.extractor.modules.audio_advanced_id3', 'Audio advanced ID3'),
        ('server.extractor.modules.video_professional', 'Video professional'),
        ('server.extractor.modules.forensic_security_advanced', 'Forensic security advanced'),
        ('server.extractor.modules.orthopedic_imaging', 'Orthopedic imaging'),
        ('server.extractor.modules.ecological_imaging', 'Ecological imaging'),
        ('server.extractor.modules.regenerative_medicine_imaging', 'Regenerative medicine'),
        ('server.extractor.modules.genetics_imaging', 'Genetics imaging'),
        ('server.extractor.modules.dental_imaging', 'Dental imaging'),
        ('server.extractor.modules.paleontology_imaging', 'Paleontology imaging'),
        ('server.extractor.modules.tropical_medicine_imaging', 'Tropical medicine'),
    ]
    
    # Test Phase 3 modules
    phase3_modules = [
        ('server.extractor.modules.rheumatology_imaging', 'Rheumatology'),
        ('server.extractor.modules.pulmonology_imaging', 'Pulmonology'),
        ('server.extractor.modules.nephrology_imaging', 'Nephrology'),
        ('server.extractor.modules.endocrinology_imaging', 'Endocrinology'),
        ('server.extractor.modules.gastroenterology_imaging', 'Gastroenterology'),
    ]
    
    all_modules = renamed_modules + phase3_modules
    
    print(f"\nTesting {len(all_modules)} renamed modules...")
    
    for module_path, description in all_modules:
        try:
            module = __import__(module_path, fromlist=[''])
            print(f"  ✅ {description}: OK")
            tests_passed += 1
        except Exception as e:
            print(f"  ❌ {description}: FAILED - {str(e)[:50]}")
            tests_failed += 1
    
    print(f"\n📊 SMOKE TEST 1 RESULTS:")
    print(f"   Passed: {tests_passed}/{len(all_modules)}")
    print(f"   Failed: {tests_failed}")
    
    return tests_failed == 0


def test_smoke_2_basic_extraction():
    """SMOKE TEST 2: Basic extraction functionality works."""
    print("\n" + "="*70)
    print("🧪 SMOKE TEST 2: BASIC EXTRACTION")
    print("="*70)
    
    tests_passed = 0
    tests_failed = 0
    
    # Create a temporary non-existent file path for testing
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        non_existent_path = tmp.name
    os.unlink(non_existent_path)
    
    # Map modules to their actual function names
    extraction_tests = [
        ('server.extractor.modules.camera_makernotes_advanced', 'extract_camera_makernotes_advanced'),
        ('server.extractor.modules.cardiac_imaging', 'extract_scientific_dicom_fits_ultimate_advanced_extension_ii'),
        ('server.extractor.modules.neuroimaging', 'extract_scientific_dicom_fits_ultimate_advanced_extension_iii'),
        ('server.extractor.modules.orthopedic_imaging', 'extract_scientific_dicom_fits_ultimate_advanced_extension_xvii'),
        ('server.extractor.modules.rheumatology_imaging', 'extract_rheumatology_imaging'),
        ('server.extractor.modules.pulmonology_imaging', 'extract_pulmonology_imaging'),
        ('server.extractor.modules.nephrology_imaging', 'extract_nephrology_imaging'),
        ('server.extractor.modules.endocrinology_imaging', 'extract_endocrinology_imaging'),
        ('server.extractor.modules.gastroenterology_imaging', 'extract_gastroenterology_imaging'),
    ]
    
    print(f"\nTesting extraction functions...")
    
    for module_path, func_name in extraction_tests:
        try:
            module = __import__(module_path, fromlist=[func_name])
            func = getattr(module, func_name)
            result = func(non_existent_path)
            
            if isinstance(result, dict) and 'extraction_status' in result:
                print(f"  ✅ {func_name}: OK")
                tests_passed += 1
            else:
                print(f"  ❌ {func_name}: Invalid structure")
                tests_failed += 1
        except Exception as e:
            print(f"  ❌ {func_name}: {str(e)[:40]}")
            tests_failed += 1
    
    print(f"\n📊 SMOKE TEST 2 RESULTS:")
    print(f"   Passed: {tests_passed}/{len(extraction_tests)}")
    print(f"   Failed: {tests_failed}")
    
    return tests_failed == 0


def test_smoke_3_field_counts():
    """SMOKE TEST 3: Field count functions."""
    print("\n" + "="*70)
    print("🧪 SMOKE TEST 3: FIELD COUNT FUNCTIONS")
    print("="*70)
    
    tests_passed = 0
    tests_failed = 0
    
    # Map modules to their actual field count function names
    field_count_tests = [
        ('server.extractor.modules.camera_makernotes_advanced', 'get_camera_makernotes_advanced_field_count'),
        ('server.extractor.modules.cardiac_imaging', 'get_scientific_dicom_fits_ultimate_advanced_extension_ii_field_count'),
        ('server.extractor.modules.neuroimaging', 'get_scientific_dicom_fits_ultimate_advanced_extension_iii_field_count'),
        ('server.extractor.modules.orthopedic_imaging', 'get_scientific_dicom_fits_ultimate_advanced_extension_xvii_field_count'),
        ('server.extractor.modules.rheumatology_imaging', 'get_rheumatology_imaging_field_count'),
        ('server.extractor.modules.pulmonology_imaging', 'get_pulmonology_imaging_field_count'),
        ('server.extractor.modules.nephrology_imaging', 'get_nephrology_imaging_field_count'),
        ('server.extractor.modules.endocrinology_imaging', 'get_endocrinology_imaging_field_count'),
        ('server.extractor.modules.gastroenterology_imaging', 'get_gastroenterology_imaging_field_count'),
    ]
    
    print(f"\nTesting field count functions...")
    
    for module_path, func_name in field_count_tests:
        try:
            module = __import__(module_path, fromlist=[func_name])
            func = getattr(module, func_name)
            field_count = func()
            
            if isinstance(field_count, int) and field_count > 0:
                print(f"  ✅ {func_name}: {field_count}")
                tests_passed += 1
            else:
                print(f"  ❌ {func_name}: Invalid ({field_count})")
                tests_failed += 1
        except Exception as e:
            print(f"  ❌ {func_name}: {str(e)[:40]}")
            tests_failed += 1
    
    print(f"\n📊 SMOKE TEST 3 RESULTS:")
    print(f"   Passed: {tests_passed}/{len(field_count_tests)}")
    print(f"   Failed: {tests_failed}")
    
    return tests_failed == 0


def run_all_smoke_tests():
    """Run all smoke tests and provide summary."""
    print("\n" + "="*70)
    print("🚀 METAEXTRACT MANUAL SMOKE SUITE")
    print("="*70)
    print("\nTesting renamed modules and Phase 3 modules...")
    
    results = []
    
    results.append(("SMOKE TEST 1: Basic Imports", test_smoke_1_basic_imports()))
    results.append(("SMOKE TEST 2: Basic Extraction", test_smoke_2_basic_extraction()))
    results.append(("SMOKE TEST 3: Field Count Functions", test_smoke_3_field_counts()))
    
    print("\n" + "="*70)
    print("📊 FINAL SMOKE SUITE SUMMARY")
    print("="*70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL SMOKE TESTS PASSED!")
        print("✅ Renamed modules and Phase 3 modules are healthy!")
    else:
        print("⚠️  SOME SMOKE TESTS FAILED!")
        print("❌ Review failures above and fix issues.")
    print("="*70)
    
    return all_passed


if __name__ == "__main__":
    success = run_all_smoke_tests()
    sys.exit(0 if success else 1)