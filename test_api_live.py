#!/usr/bin/env python3
"""
Live API testing script for advanced analysis endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:3000"

def test_health_check():
    """Test basic server health"""
    print("🏥 Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ Server is healthy")
            return True
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Health check error: {e}")
        return False

def test_forensic_capabilities():
    """Test forensic capabilities endpoint"""
    print("\n🔍 Testing forensic capabilities...")
    try:
        response = requests.get(f"{BASE_URL}/api/forensic/capabilities?tier=professional", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("  ✅ Capabilities endpoint working")
            print(f"  📊 Tier: {data.get('tier')}")
            print(f"  🔬 Advanced analysis: {data.get('advanced_analysis_available')}")
            
            # Check modules
            modules = data.get('modules', {})
            for module_name, module_info in modules.items():
                status = "✅" if module_info.get('available') else "❌"
                print(f"  {status} {module_name}: {module_info.get('available')}")
            
            return True
        else:
            print(f"  ❌ Capabilities failed: {response.status_code}")
            print(f"  📄 Response: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Capabilities error: {e}")
        return False

def test_basic_extraction():
    """Test basic metadata extraction"""
    print("\n📁 Testing basic extraction...")
    try:
        # Use the test.jpg file
        with open('test.jpg', 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(
                f"{BASE_URL}/api/extract?tier=professional", 
                files=files, 
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            print("  ✅ Basic extraction working")
            print(f"  📊 Fields extracted: {data.get('fields_extracted', 0)}")
            print(f"  📄 Filename: {data.get('filename')}")
            print(f"  🎚️ Tier: {data.get('tier')}")
            return True
        else:
            print(f"  ❌ Extraction failed: {response.status_code}")
            print(f"  📄 Response: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Extraction error: {e}")
        return False

def test_advanced_analysis():
    """Test advanced analysis endpoint"""
    print("\n🔬 Testing advanced analysis...")
    try:
        # Use the test.jpg file
        with open('test.jpg', 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(
                f"{BASE_URL}/api/extract/advanced?tier=professional", 
                files=files, 
                timeout=60
            )
        
        if response.status_code == 200:
            data = response.json()
            print("  ✅ Advanced analysis working")
            print(f"  📊 Fields extracted: {data.get('fields_extracted', 0)}")
            
            # Check for advanced analysis results
            advanced = data.get('advanced_analysis', {})
            if advanced:
                print(f"  🎯 Forensic score: {advanced.get('forensic_score', 'N/A')}")
                print(f"  🔍 Authenticity: {advanced.get('authenticity_assessment', 'N/A')}")
                print(f"  ⏱️ Processing time: {advanced.get('processing_time_ms', 0)}ms")
                modules = advanced.get('modules_run', [])
                print(f"  🧪 Modules run: {', '.join(modules) if modules else 'None'}")
            
            # Check for specific analysis results
            if data.get('steganography_analysis'):
                print("  ✅ Steganography analysis present")
            if data.get('manipulation_detection'):
                print("  ✅ Manipulation detection present")
            if data.get('ai_detection'):
                print("  ✅ AI detection present")
            
            return True
        else:
            print(f"  ❌ Advanced analysis failed: {response.status_code}")
            print(f"  📄 Response: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Advanced analysis error: {e}")
        return False

def main():
    print("🚀 Live API Testing Suite")
    print("=" * 50)
    
    tests = [
        test_health_check,
        test_forensic_capabilities,
        test_basic_extraction,
        test_advanced_analysis
    ]
    
    passed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            time.sleep(1)  # Brief pause between tests
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"✅ {passed}/{len(tests)} API tests passed")
    
    if passed == len(tests):
        print("🎉 All API endpoints working! Ready for frontend testing.")
        print("\n📋 Next Steps:")
        print("  1. Open http://localhost:3000 in your browser")
        print("  2. Upload a test file")
        print("  3. Click the 'Advanced' tab")
        print("  4. Test the advanced analysis features")
        print("  5. Try batch comparison and timeline features")
    else:
        print("⚠️  Some API endpoints need attention")
        print("💡 Check server logs for detailed error information")

if __name__ == "__main__":
    main()