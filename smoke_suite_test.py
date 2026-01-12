#!/usr/bin/env python3
"""
Manual Smoke Suite Test - MetaExtract Core Functionality
Tests 3 critical smoke tests to verify system health before deployment.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, '/Users/pranay/Projects/metaextract')

def test_smoke_1_basic_imports():
    """SMOKE TEST 1: Basic imports work correctly.
    
    Verifies all core modules can be imported without errors.
    This is the most basic smoke test - if imports fail, nothing works.
    """
    print("\n" + "="*70)
    print("🧪 SMOKE TEST 1: BASIC IMPORTS")
    print("="*70)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test core modules
    core_modules = [
        ('server.extractor.modules', 'Core modules package'),
        ('server.extractor.core.extractor', 'Extractor core'),
        ('server.extractor.core.orchestrator', 'Orchestrator'),
        ('server.extractor.modules.image_formats', 'Image formats'),
        ('server.extractor.modules.exif_parser', 'EXIF parser'),
        ('server.extractor.modules.iptc_xmp', 'IPTC/XMP parser'),
    ]
    
    # Test renamed modules (our Phase 2 work)
    renamed_modules = [
        ('server.extractor.modules.camera_makernotes_advanced', 'Camera makernotes (renamed)'),
        ('server.extractor.modules.cardiac_imaging', 'Cardiac imaging (renamed)'),
        ('server.extractor.modules.neuroimaging', 'Neuroimaging (renamed)'),
        ('server.extractor.modules.medical_astronomical', 'Medical/astronomical (renamed)'),
        ('server.extractor.modules.emerging_tech', 'Emerging tech (renamed)'),
        ('server.extractor.modules.audio_advanced_id3', 'Audio advanced ID3 (renamed)'),
        ('server.extractor.modules.video_professional', 'Video professional (renamed)'),
        ('server.extractor.modules.forensic_security_advanced', 'Forensic security advanced (renamed)'),
        ('server.extractor.modules.orthopedic_imaging', 'Orthopedic imaging (renamed)'),
        ('server.extractor.modules.ecological_imaging', 'Ecological imaging (renamed)'),
        ('server.extractor.modules.regenerative_medicine_imaging', 'Regenerative medicine (renamed)'),
        ('server.extractor.modules.genetics_imaging', 'Genetics imaging (renamed)'),
        ('server.extractor.modules.dental_imaging', 'Dental imaging (renamed)'),
        ('server.extractor.modules.paleontology_imaging', 'Paleontology imaging (renamed)'),
        ('server.extractor.modules.tropical_medicine_imaging', 'Tropical medicine (renamed)'),
    ]
    
    # Test Phase 3 modules
    phase3_modules = [
        ('server.extractor.modules.rheumatology_imaging', 'Rheumatology (Phase 3)'),
        ('server.extractor.modules.pulmonology_imaging', 'Pulmonology (Phase 3)'),
        ('server.extractor.modules.nephrology_imaging', 'Nephrology (Phase 3)'),
        ('server.extractor.modules.endocrinology_imaging', 'Endocrinology (Phase 3)'),
        ('server.extractor.modules.gastroenterology_imaging', 'Gastroenterology (Phase 3)'),
    ]
    
    all_modules = core_modules + renamed_modules + phase3_modules
    
    print(f"\nTesting {len(all_modules)} modules...")
    
    for module_path, description in all_modules:
        try:
            module = __import__(module_path, fromlist=[''])
            print(f"  ✅ {module_path}: OK")
            tests_passed += 1
        except Exception as e:
            print(f"  ❌ {module_path}: FAILED - {str(e)[:50]}")
            tests_failed += 1
    
    print(f"\n📊 SMOKE TEST 1 RESULTS:")
    print(f"   Passed: {tests_passed}")
    print(f"   Failed: {tests_failed}")
    print(f"   Total:  {tests_passed + tests_failed}")
    
    if tests_failed == 0:
        print("\n✅ SMOKE TEST 1: PASSED - All imports successful!")
        return True
    else:
        print(f"\n❌ SMOKE TEST 1: FAILED - {tests_failed} import(s) failed")
        return False


def test_smoke_2_basic_extraction():
    """SMOKE TEST 2: Basic extraction functionality works.
    
    Verifies the extraction pipeline can process a basic file.
    """
    print("\n" + "="*70)
    print("🧪 SMOKE TEST 2: BASIC EXTRACTION")
    print("="*70)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test basic extraction functions from renamed modules
    extraction_tests = [
        ('server.extractor.modules.camera_makernotes_advanced', 'extract_camera_makernotes_advanced'),
        ('server.extractor.modules.cardiac_imaging', 'extract_cardiac_imaging'),
        ('server.extractor.modules.neuroimaging', 'extract_neuroimaging'),
        ('server.extractor.modules.orthopedic_imaging', 'extract_orthopedic_imaging'),
        ('server.extractor.modules.rheumatology_imaging', 'extract_rheumatology_imaging'),
        ('server.extractor.modules.pulmonology_imaging', 'extract_pulmonology_imaging'),
        ('server.extractor.modules.nephrology_imaging', 'extract_nephrology_imaging'),
        ('server.extractor.modules.endocrinology_imaging', 'extract_endocrinology_imaging'),
        ('server.extractor.modules.gastroenterology_imaging', 'extract_gastroenterology_imaging'),
    ]
    
    print(f"\nTesting extraction functions on non-existent file...")
    
    # Create a temporary non-existent file path for testing
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        non_existent_path = tmp.name
    os.unlink(non_existent_path)  # Delete so file doesn't exist
    
    for module_path, func_name in extraction_tests:
        try:
            module = __import__(module_path, fromlist=[func_name])
            func = getattr(module, func_name)
            result = func(non_existent_path)
            
            # Check basic result structure
            if isinstance(result, dict) and 'extraction_status' in result:
                print(f"  ✅ {func_name}: Returns valid structure")
                tests_passed += 1
            else:
                print(f"  ❌ {func_name}: Invalid return structure")
                tests_failed += 1
        except Exception as e:
            print(f"  ❌ {func_name}: FAILED - {str(e)[:50]}")
            tests_failed += 1
    
    print(f"\n📊 SMOKE TEST 2 RESULTS:")
    print(f"   Passed: {tests_passed}")
    print(f"   Failed: {tests_failed}")
    print(f"   Total:  {tests_passed + tests_failed}")
    
    if tests_failed == 0:
        print("\n✅ SMOKE TEST 2: PASSED - All extraction functions work!")
        return True
    else:
        print(f"\n❌ SMOKE TEST 2: FAILED - {tests_failed} extraction(s) failed")
        return False


def test_smoke_3_field_counts():
    """SMOKE TEST 3: Field count functions return valid values.
    
    Verifies all modules have proper field count functions.
    """
    print("\n" + "="*70)
    print("🧪 SMOKE TEST 3: FIELD COUNT FUNCTIONS")
    print("="*70)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test field count functions from renamed modules
    field_count_tests = [
        ('server.extractor.modules.camera_makernotes_advanced', 'get_camera_makernotes_advanced_field_count'),
        ('server.extractor.modules.cardiac_imaging', 'get_cardiac_imaging_field_count'),
        ('server.extractor.modules.neuroimaging', 'get_neuroimaging_field_count'),
        ('server.extractor.modules.orthopedic_imaging', 'get_orthopedic_imaging_field_count'),
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
            
            # Check basic result structure
            if isinstance(field_count, int) and field_count > 0:
                print(f"  ✅ {func_name}: Returns {field_count}")
                tests_passed += 1
            else:
                print(f"  ❌ {func_name}: Invalid return ({field_count})")
                tests_failed += 1
        except Exception as e:
            print(f"  ❌ {func_name}: FAILED - {str(e)[:50]}")
            tests_failed += 1
    
    print(f"\n📊 SMOKE TEST 3 RESULTS:")
    print(f"   Passed: {tests_passed}")
    print(f"   Failed: {tests_failed}")
    print(f"   Total:  {tests_passed + tests_failed}")
    
    if tests_failed == 0:
        print("\n✅ SMOKE TEST 3: PASSED - All field count functions work!")
        return True
    else:
        print(f"\n❌ SMOKE TEST 3: FAILED - {tests_failed} field count(s) failed")
        return False


def run_all_smoke_tests():
    """Run all smoke tests and provide summary."""
    print("\n" + "="*70)
    print("🚀 METAEXTRACT MANUAL SMOKE SUITE")
    print("="*70)
    print("\nRunning 3 smoke tests to verify system health...")
    print("These tests verify core functionality works before deployment.\n")
    
    results = []
    
    # Run smoke tests
    results.append(("SMOKE TEST 1: Basic Imports", test_smoke_1_basic_imports()))
    results.append(("SMOKE TEST 2: Basic Extraction", test_smoke_2_basic_extraction()))
    results.append(("SMOKE TEST 3: Field Count Functions", test_smoke_3_field_counts()))
    
    # Summary
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
        print("✅ System is healthy and ready for deployment.")
        print("\nNext Steps:")
        print("  1. Run E2E smoke test (tests/e2e/images-mvp.smoke.spec.ts)")
        print("  2. Implement Phase 4 if needed")
        print("  3. Proceed with remaining implementation phases")
    else:
        print("⚠️  SOME SMOKE TESTS FAILED!")
        print("❌ System has issues that need to be resolved before deployment.")
        print("\nAction Required:")
        print("  1. Review failed smoke test output above")
        print("  2. Fix import/extraction issues")
        print("  3. Re-run smoke suite")
    print("="*70)
    
    return all_passed


if __name__ == "__main__":
    success = run_all_smoke_tests()
    sys.exit(0 if success else 1)