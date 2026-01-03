#!/usr/bin/env python3
"""
Test script to verify all tier restrictions are bypassed in development mode.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:3000"

def test_endpoint(method, endpoint, files=None, expected_success=True):
    """Test an API endpoint and return success status."""
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", files=files)
        
        data = response.json()
        
        if expected_success:
            success = "error" not in data
            status = "✅ PASS" if success else "❌ FAIL"
        else:
            success = "error" in data
            status = "✅ PASS" if success else "❌ FAIL"
            
        print(f"{status} {method} {endpoint}")
        if not success and expected_success:
            print(f"   Error: {data.get('error', 'Unknown error')}")
        elif success and not expected_success:
            print(f"   Expected error but got success")
            
        return success
        
    except Exception as e:
        print(f"❌ FAIL {method} {endpoint} - Exception: {e}")
        return False

def main():
    print("🧪 Testing Tier Bypass in Development Mode")
    print("=" * 50)
    
    # Test files
    with open('test.jpg', 'rb') as f1, open('sample_with_meta.jpg', 'rb') as f2:
        test_files = {
            'file': ('test.jpg', f1, 'image/jpeg')
        }
        
        multi_files = [
            ('files', ('test.jpg', f1, 'image/jpeg')),
            ('files', ('sample_with_meta.jpg', f2, 'image/jpeg'))
        ]
    
        tests = [
            # Basic endpoints (should work)
            ("GET", "/api/health", None, True),
            ("GET", "/api/tiers", None, True),
            
            # Forensic capabilities (should show all features available)
            ("GET", "/api/forensic/capabilities?tier=free", None, True),
            
            # Basic extraction (should work)
            ("POST", "/api/extract?tier=free", test_files, True),
            
            # Advanced analysis (should work with tier bypass)
            ("POST", "/api/extract/advanced?tier=free", test_files, True),
            
            # Batch comparison (should work with tier bypass)
            ("POST", "/api/compare/batch?tier=free", multi_files, True),
            
            # Timeline reconstruction (should work with tier bypass)
            ("POST", "/api/timeline/reconstruct?tier=free", multi_files, True),
            
            # Forensic report (should work with tier bypass, may have other errors)
            ("POST", "/api/forensic/report?tier=free", multi_files, True),
        ]
        
        passed = 0
        total = len(tests)
        
        for method, endpoint, files, expected_success in tests:
            if test_endpoint(method, endpoint, files, expected_success):
                passed += 1
    
    # Close file handles
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tier bypasses working correctly!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())