#!/usr/bin/env python3
"""
Simple Frontend Test - Essential functionality only
"""

import requests
import json
from pathlib import Path

def test_basic_functionality():
    """Test core functionality that should work"""
    base_url = "http://localhost:3000"
    
    print("🧪 Simple Frontend Test")
    print("=" * 40)
    
    # 1. Health Check
    print("1. Testing server health...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Server: {data['service']} v{data['version']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # 2. Frontend Access
    print("2. Testing frontend access...")
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("   ✅ Frontend accessible")
        else:
            print(f"   ❌ Frontend not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Frontend error: {e}")
        return False
    
    # 3. File Upload
    print("3. Testing file upload...")
    try:
        test_file = Path("test.jpg")
        if not test_file.exists():
            print("   ❌ Test file not found")
            return False
        
        with open(test_file, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(f"{base_url}/api/extract?tier=free", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Upload successful: {data.get('fields_extracted', 0)} fields")
        else:
            print(f"   ❌ Upload failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Upload error: {e}")
        return False
    
    # 4. Tier Testing
    print("4. Testing different tiers...")
    tiers = ["free", "professional", "forensic", "enterprise"]
    for tier in tiers:
        try:
            with open("test.jpg", 'rb') as f:
                files = {'file': ('test.jpg', f, 'image/jpeg')}
                response = requests.post(f"{base_url}/api/extract?tier={tier}", files=files)
            
            if response.status_code == 200:
                data = response.json()
                fields = data.get('fields_extracted', 0)
                print(f"   ✅ {tier}: {fields} fields")
            else:
                print(f"   ⚠️  {tier}: restricted")
        except Exception as e:
            print(f"   ❌ {tier}: error")
    
    # 5. Advanced Features
    print("5. Testing advanced features...")
    try:
        response = requests.get(f"{base_url}/api/forensic/capabilities?tier=enterprise")
        if response.status_code == 200:
            data = response.json()
            modules = len(data.get('modules', []))
            print(f"   ✅ Forensic modules: {modules}")
        else:
            print(f"   ⚠️  Forensic capabilities: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Advanced features error: {e}")
    
    print("\n✅ Basic functionality test complete!")
    return True

if __name__ == "__main__":
    success = test_basic_functionality()
    exit(0 if success else 1)