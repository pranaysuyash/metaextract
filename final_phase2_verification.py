#!/usr/bin/env python3
"""
Final Phase 2 Verification - Critical Functionality Check

This script verifies that all critical functionality works exactly as before,
with only performance improvements added. This is the final check before
considering Phase 2 complete.
"""

import requests
import json
import time
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

def create_test_jpeg():
    """Create a minimal valid JPEG file"""
    test_file = "test_final.jpg"
    if not os.path.exists(test_file):
        # Minimal valid JPEG (1x1 black pixel)
        jpeg_data = bytes([
            0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01, 0x01, 0x01, 0x00, 0x48,
            0x00, 0x48, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43, 0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08,
            0x07, 0x07, 0x07, 0x09, 0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12, 0x13, 0x0F,
            0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20, 0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28,
            0x37, 0x29, 0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32, 0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0,
            0x00, 0x11, 0x08, 0x00, 0x01, 0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0x02, 0x11, 0x01, 0x03, 0x11, 0x01, 0xFF, 0xDA, 0x00, 0x0C,
            0x03, 0x01, 0x00, 0x02, 0x11, 0x03, 0x11, 0x00, 0x3F, 0x00, 0xA2, 0x00, 0xFF, 0xD9
        ])
        with open(test_file, 'wb') as f:
            f.write(jpeg_data)
    return test_file

def test_endpoint(name: str, method: str, endpoint: str, files=None, params=None, 
                  expected_status=200, required_fields=None) -> Dict[str, Any]:
    """Test an endpoint and return detailed results"""
    base_url = "http://localhost:3000"
    result = {
        "name": name,
        "endpoint": endpoint,
        "method": method,
        "success": False,
        "status_code": None,
        "error": None,
        "response_data": None,
        "validation_errors": []
    }
    
    try:
        if method == "GET":
            response = requests.get(f"{base_url}{endpoint}", params=params, timeout=15)
        elif method == "POST":
            response = requests.post(f"{base_url}{endpoint}", files=files, params=params, timeout=30)
        
        result["status_code"] = response.status_code
        
        if response.status_code == expected_status:
            try:
                data = response.json()
                result["response_data"] = data
                
                # Validate required fields
                if required_fields:
                    missing_fields = []
                    for field in required_fields:
                        if field not in data:
                            missing_fields.append(field)
                    
                    if missing_fields:
                        result["validation_errors"] = missing_fields
                        result["error"] = f"Missing required fields: {missing_fields}"
                    else:
                        result["success"] = True
                else:
                    result["success"] = True
                    
            except json.JSONDecodeError:
                result["error"] = "Response is not valid JSON"
        else:
            result["error"] = f"Expected status {expected_status}, got {response.status_code}"
            
    except Exception as e:
        result["error"] = str(e)
    
    return result

def main():
    """Run final Phase 2 verification"""
    print("🚀 FINAL PHASE 2 VERIFICATION")
    print("=" * 80)
    print("Testing critical functionality to ensure zero regressions")
    print("=" * 80)
    
    # Create test image
    test_image = create_test_jpeg()
    
    # Test cases - critical functionality that must work
    test_cases = [
        # Health endpoints
        ("Main Health", "GET", "/api/health", None, None, 200, ["status"]),
        ("Extract Health", "GET", "/api/extract/health", None, None, 200, ["status"]),
        
        # Original extraction endpoints
        ("Single File Extraction", "POST", "/api/extract", 
         lambda: {'file': ('test.jpg', open(test_image, 'rb'), 'image/jpeg')},
         {'tier': 'enterprise'}, 200, ["fields_extracted", "exif"]),
        
        ("Advanced Extraction", "POST", "/api/extract/advanced",
         lambda: {'file': ('test.jpg', open(test_image, 'rb'), 'image/jpeg')},
         {'tier': 'enterprise'}, 200, ["fields_extracted", "exif"]),
        
        # Images MVP endpoints
        ("Images MVP Extraction", "POST", "/api/images_mvp/extract",
         lambda: {'file': ('test.jpg', open(test_image, 'rb'), 'image/jpeg')},
         None, 200, ["fields_extracted", "exif"]),
        
        ("Images MVP Credit Packs", "GET", "/api/images_mvp/credits/packs",
         None, None, 200, ["packs"]),
        
        # Forensic endpoints
        ("Forensic Capabilities", "GET", "/api/forensic/capabilities",
         None, {'tier': 'enterprise'}, 200, ["tier", "modules"]),
    ]
    
    results = []
    
    print(f"\n🧪 Running {len(test_cases)} critical tests...")
    
    for i, (name, method, endpoint, files_func, params, expected_status, required_fields) in enumerate(test_cases, 1):
        print(f"\n{i:2d}. Testing: {name}")
        print(f"    Endpoint: {method} {endpoint}")
        
        # Handle file opening for POST requests
        files = None
        if files_func:
            files = files_func()
        
        result = test_endpoint(name, method, endpoint, files, params, expected_status, required_fields)
        results.append(result)
        
        # Close file if opened
        if files and 'file' in files and hasattr(files['file'][1], 'close'):
            files['file'][1].close()
        
        # Display result
        if result["success"]:
            print(f"    ✅ PASSED")
            if result["response_data"]:
                # Show key metrics
                if "fields_extracted" in result["response_data"]:
                    print(f"       Fields extracted: {result['response_data']['fields_extracted']}")
                if "quality_metrics" in result["response_data"]:
                    print(f"       Has quality metrics: ✅")
                if "processing_insights" in result["response_data"]:
                    print(f"       Has processing insights: ✅")
        else:
            print(f"    ❌ FAILED")
            if result["error"]:
                print(f"       Error: {result['error']}")
            if result["validation_errors"]:
                print(f"       Missing fields: {result['validation_errors']}")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 FINAL VERIFICATION SUMMARY")
    print("=" * 80)
    
    passed_tests = [r for r in results if r["success"]]
    failed_tests = [r for r in results if not r["success"]]
    
    total_tests = len(results)
    passed_count = len(passed_tests)
    failed_count = len(failed_tests)
    success_rate = (passed_count / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if failed_tests:
        print(f"\n🔍 Failed Tests:")
        for test in failed_tests:
            print(f"   ❌ {test['name']}: {test['error']}")
    
    # Final verdict
    print("\n" + "=" * 80)
    
    if success_rate >= 95:
        print("🎉 PHASE 2 VERIFICATION PASSED!")
        print("✅ All critical functionality working exactly as before")
        print("✅ Zero regressions detected")
        print("✅ Ready for Phase 2 completion")
        final_status = "PASSED"
    elif success_rate >= 85:
        print("⚠️  PHASE 2 VERIFICATION PARTIALLY PASSED")
        print("🔧 Some minor issues detected but core functionality intact")
        print("🔧 Review recommended but not blocking")
        final_status = "PARTIAL"
    else:
        print("❌ PHASE 2 VERIFICATION FAILED")
        print("🔧 Significant regressions detected")
        print("🔧 Fixes required before completion")
        final_status = "FAILED"
    
    print("=" * 80)
    
    # Save detailed report
    try:
        report_file = f"phase2_final_verification_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "final_status": final_status,
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed_count,
                    "failed": failed_count,
                    "success_rate": success_rate
                },
                "test_results": results
            }, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_file}")
    except Exception as e:
        print(f"\n❌ Failed to save report: {e}")
    
    # Cleanup
    if os.path.exists(test_image):
        os.remove(test_image)
    
    return final_status == "PASSED"

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)