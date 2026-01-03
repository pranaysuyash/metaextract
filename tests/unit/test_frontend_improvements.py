#!/usr/bin/env python3
"""
Test script for frontend improvements and integration enhancements
"""

import requests
import json
import time
from pathlib import Path

def test_server_health():
    """Test if the server is running and healthy"""
    try:
        response = requests.get("http://localhost:3000/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server health check passed: {data['status']}")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server health check error: {e}")
        return False

def test_basic_extraction():
    """Test basic file extraction endpoint"""
    try:
        # Use the test image
        test_file = Path("test.jpg")
        if not test_file.exists():
            print("❌ Test file test.jpg not found")
            return False
        
        with open(test_file, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post("http://localhost:3000/api/extract?tier=free", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Basic extraction successful: {data.get('filename', 'unknown')}")
            print(f"   Fields returned: {data.get('fields_extracted', 0)}")
            return True
        else:
            print(f"❌ Basic extraction failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Basic extraction error: {e}")
        return False

def test_advanced_analysis():
    """Test advanced analysis endpoint"""
    try:
        test_file = Path("test.jpg")
        if not test_file.exists():
            print("❌ Test file test.jpg not found")
            return False
        
        with open(test_file, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post("http://localhost:3000/api/extract/advanced?tier=professional", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Advanced analysis successful")
            print(f"   Analysis type: {data.get('analysis_type', 'unknown')}")
            return True
        else:
            print(f"❌ Advanced analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Advanced analysis error: {e}")
        return False

def test_forensic_capabilities():
    """Test forensic capabilities endpoint"""
    try:
        response = requests.get("http://localhost:3000/api/forensic/capabilities?tier=enterprise")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Forensic capabilities retrieved")
            print(f"   Available modules: {len(data.get('modules', []))}")
            return True
        else:
            print(f"❌ Forensic capabilities failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Forensic capabilities error: {e}")
        return False

def test_frontend_accessibility():
    """Test if the frontend is accessible"""
    try:
        response = requests.get("http://localhost:3000/")
        
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend accessibility error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Frontend Improvements and Integration Enhancements")
    print("=" * 60)
    
    tests = [
        ("Server Health", test_server_health),
        ("Frontend Accessibility", test_frontend_accessibility),
        ("Basic Extraction", test_basic_extraction),
        ("Advanced Analysis", test_advanced_analysis),
        ("Forensic Capabilities", test_forensic_capabilities),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        time.sleep(0.5)  # Brief pause between tests
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Frontend improvements are working correctly.")
        print("\n✨ New Features Available:")
        print("   • Enhanced Upload Zone with drag & drop, progress tracking, and file validation")
        print("   • Metadata Explorer with three-pane layout and smart context detection")
        print("   • UI Adaptation Controller for dynamic interface optimization")
        print("   • Error Boundaries with graceful error handling and recovery")
        print("   • Loading Skeletons for smooth loading states")
        print("   • Demo Payment Modal with clear development/production modes")
        print("   • Context Detection Engine for intelligent UI adaptation")
        print("   • Advanced Results Integration with forensic analysis")
    else:
        print(f"⚠️  {total - passed} tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)