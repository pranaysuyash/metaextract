#!/usr/bin/env python3
"""
Test Original Extraction Endpoints to Ensure Zero Regressions
"""

import requests
import json
import time
import os
from pathlib import Path

def create_test_image():
    """Create a minimal valid JPEG for testing"""
    test_file = "test_original.jpg"
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

def check_endpoint(endpoint, method="GET", files=None, data=None, params=None, expected_status=200, name=""):
    """Test an endpoint and return result"""
    base_url = "http://localhost:3000"
    
    try:
        if method == "GET":
            response = requests.get(f"{base_url}{endpoint}", params=params, timeout=15)
        elif method == "POST":
            response = requests.post(f"{base_url}{endpoint}", files=files, data=data, params=params, timeout=30)
        
        success = response.status_code == expected_status
        
        if success:
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - Expected {expected_status}, got {response.status_code}")
            
        return success, response
    except Exception as e:
        print(f"❌ {name} - Error: {e}")
        return False, None

def main():
    """Test all original endpoints"""
    print("🧪 Testing Original Extraction Endpoints")
    print("=" * 60)
    
    # Create test image
    test_image = create_test_image()
    
    results = []
    
    # Test 1: Health endpoints
    print("\n🏥 Health Endpoints:")
    
    success, response = check_endpoint("/api/health", name="Main Health")
    results.append(("Main Health", success))
    
    success, response = check_endpoint("/api/extract/health", name="Extract Health")
    results.append(("Extract Health", success))
    
    success, response = check_endpoint("/api/extract/health/image", name="Image Health")
    results.append(("Image Health", success))
    
    # Test 2: Original extraction endpoints
    print("\n🔍 Original Extraction Endpoints:")
    
    # Single file extraction
    with open(test_image, 'rb') as f:
        files = {'file': ('test.jpg', f, 'image/jpeg')}
        success, response = check_endpoint("/api/extract", method="POST", files=files, 
                                        params={'tier': 'enterprise'}, name="Single Extract")
        results.append(("Single Extract", success))
        
        if success:
            data = response.json()
            print(f"   Fields extracted: {data.get('fields_extracted', 0)}")
    
    # Advanced extraction
    with open(test_image, 'rb') as f:
        files = {'file': ('test.jpg', f, 'image/jpeg')}
        success, response = check_endpoint("/api/extract/advanced", method="POST", files=files,
                                        params={'tier': 'enterprise'}, name="Advanced Extract")
        results.append(("Advanced Extract", success))
        
        if success:
            data = response.json()
            print(f"   Has advanced analysis: {'advanced_analysis' in data}")
    
    # Test 3: Timeline reconstruction
    print("\n📅 Timeline Reconstruction:")
    
    files = []
    for i in range(2):
        with open(test_image, 'rb') as f:
            files.append(('files', (f'test_{i}.jpg', f, 'image/jpeg')))
    
    success, response = check_endpoint("/api/timeline/reconstruct", method="POST", files=files,
                                    params={'tier': 'enterprise'}, name="Timeline")
    results.append(("Timeline", success))
    
    if success:
        data = response.json()
        print(f"   Files analyzed: {data.get('files_analyzed', 0)}")
        print(f"   Events found: {len(data.get('events', []))}")
    
    # Test 4: Images MVP endpoints
    print("\n🖼️  Images MVP Endpoints:")
    
    # Images MVP extraction
    with open(test_image, 'rb') as f:
        files = {'file': ('test.jpg', f, 'image/jpeg')}
        success, response = check_endpoint("/api/images_mvp/extract", method="POST", files=files,
                                        name="Images MVP Extract")
        results.append(("Images MVP Extract", success))
        
        if success:
            data = response.json()
            print(f"   Fields extracted: {data.get('fields_extracted', 0)}")
            print(f"   Has quality metrics: {'quality_metrics' in data}")
            print(f"   Has processing insights: {'processing_insights' in data}")
    
    # Credit packs
    success, response = check_endpoint("/api/images_mvp/credits/packs", name="Credit Packs")
    results.append(("Credit Packs", success))
    
    if success:
        data = response.json()
        print(f"   Available packs: {len(data.get('packs', {}))}")
    
    # Test 5: Forensic capabilities
    print("\n🔍 Forensic Capabilities:")
    
    success, response = check_endpoint("/api/forensic/capabilities", params={'tier': 'enterprise'}, 
                                    name="Forensic Capabilities")
    results.append(("Forensic Capabilities", success))
    
    if success:
        data = response.json()
        print(f"   Tier: {data.get('tier', 'unknown')}")
        print(f"   Advanced analysis: {data.get('advanced_analysis_available', False)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"📈 Success Rate: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 ALL ORIGINAL ENDPOINTS WORKING!")
        print("✅ Zero regressions detected")
    else:
        print("\n⚠️  SOME ISSUES DETECTED")
        print("🔧 Check failed tests above")
    
    # Cleanup
    if os.path.exists(test_image):
        os.remove(test_image)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)