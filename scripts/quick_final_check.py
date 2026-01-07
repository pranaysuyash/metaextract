#!/usr/bin/env python3
"""
Quick Final Verification - Core Functionality Check
"""

import requests
import json
import time
import os
from pathlib import Path

def test_core_endpoints():
    """Test core endpoints quickly"""
    base_url = "http://localhost:3000"
    
    print("🚀 Quick Core Functionality Check")
    print("=" * 50)
    
    # Test 1: Health endpoints
    print("\n🏥 Testing Health Endpoints...")
    health_checks = [
        ("/api/health", "Main Health"),
        ("/api/extract/health", "Extract Health"),
    ]
    
    for endpoint, name in health_checks:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}")
            else:
                print(f"❌ {name} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {name} - Error: {e}")
    
    # Test 2: Core extraction endpoints
    print("\n🔍 Testing Core Extraction...")
    
    # Create a simple test image
    try:
        # Create minimal JPEG
        test_jpg = "test_quick.jpg"
        if not os.path.exists(test_jpg):
            with open(test_jpg, 'wb') as f:
                # Minimal JPEG header
                f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c\x20\x24\x2e\x27\x20\x22\x2c\x23\x1c\x1c\x28\x37\x29\x2c\x30\x31\x34\x34\x34\x1f\x27\x39\x3d\x38\x32\x3c\x2e\x33\x34\x32\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xa2\x00\xff\xd9')
        
        # Test single extraction
        with open(test_jpg, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(f"{base_url}/api/extract", 
                                   files=files, 
                                   params={'tier': 'enterprise'},
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if "fields_extracted" in data or "exif" in data:
                    print("✅ Single File Extraction")
                else:
                    print("❌ Single File Extraction - No metadata returned")
            else:
                print(f"❌ Single File Extraction - Status: {response.status_code}")
        
        # Test Images MVP extraction
        with open(test_jpg, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(f"{base_url}/api/images_mvp/extract", 
                                   files=files, 
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if "fields_extracted" in data or "exif" in data:
                    print("✅ Images MVP Extraction")
                    print(f"   Fields extracted: {data.get('fields_extracted', 0)}")
                    print(f"   Has quality metrics: {'quality_metrics' in data}")
                    print(f"   Has processing insights: {'processing_insights' in data}")
                else:
                    print("❌ Images MVP Extraction - No metadata returned")
            else:
                print(f"❌ Images MVP Extraction - Status: {response.status_code}")
        
        # Test credit system
        response = requests.get(f"{base_url}/api/images_mvp/credits/packs")
        if response.status_code == 200:
            print("✅ Credit System")
        else:
            print(f"❌ Credit System - Status: {response.status_code}")
        
        # Cleanup
        if os.path.exists(test_jpg):
            os.remove(test_jpg)
            
    except Exception as e:
        print(f"❌ Core extraction test failed: {e}")
    
    # Test 3: Error handling
    print("\n⚠️  Testing Error Handling...")
    try:
        # Test invalid file
        files = {'file': ('test.txt', b'invalid', 'text/plain')}
        response = requests.post(f"{base_url}/api/extract", 
                               files=files, 
                               params={'tier': 'enterprise'})
        
        if response.status_code in [400, 403]:
            print("✅ Invalid File Type Handling")
        else:
            print(f"❌ Invalid File Type Handling - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Core functionality verification complete")
    print("Check the detailed logs above for any issues")

if __name__ == "__main__":
    test_core_endpoints()