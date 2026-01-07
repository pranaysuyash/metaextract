#!/usr/bin/env python3
"""
Verification script for MetaExtract routing fixes
"""

import requests
import json

def test_routing_fix():
    """Test that the routing fixes are working correctly"""
    
    print("🔧 Verifying MetaExtract Routing Fixes")
    print("=" * 50)
    
    # Test cases
    tests = [
        {
            "name": "Valid API endpoint",
            "url": "http://localhost:3000/api/auth/me",
            "expected_type": "json",
            "expected_status": 200
        },
        {
            "name": "Invalid API endpoint", 
            "url": "http://localhost:3000/api/invalid/route",
            "expected_type": "json",
            "expected_status": 404
        },
        {
            "name": "Dev users endpoint (should 404)",
            "url": "http://localhost:3000/api/auth/dev/users", 
            "expected_type": "json",
            "expected_status": 404
        },
        {
            "name": "Client route (should serve HTML)",
            "url": "http://localhost:5173/",
            "expected_type": "html",
            "expected_status": 200
        },
        {
            "name": "Client 404 route",
            "url": "http://localhost:5173/nonexistent",
            "expected_type": "html", 
            "expected_status": 200
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        print(f"\n📍 Testing: {test['name']}")
        print(f"URL: {test['url']}")
        
        try:
            response = requests.get(test['url'], timeout=5)
            content_type = response.headers.get('content-type', '')
            
            # Check status code
            status_ok = response.status_code == test['expected_status']
            
            # Check content type
            if test['expected_type'] == 'json':
                type_ok = 'application/json' in content_type
            else:
                type_ok = 'text/html' in content_type
            
            # Overall test result
            test_passed = status_ok and type_ok
            
            if test_passed:
                print(f"✅ PASSED - Status: {response.status_code}")
                passed += 1
            else:
                print(f"❌ FAILED - Status: {response.status_code}")
                print(f"   Expected: {test['expected_status']} {test['expected_type']}")
                print(f"   Got: {response.status_code} {content_type}")
                failed += 1
                
        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 50)
    print("📊 Fix Verification Results")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 All routing fixes verified successfully!")
        return True
    else:
        print(f"\n⚠️  {failed} issues need attention")
        return False

def test_api_404_format():
    """Test that API 404 responses are properly formatted"""
    
    print("\n🔍 Testing API 404 Response Format")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:3000/api/nonexistent/endpoint")
        
        if response.status_code == 404 and 'application/json' in response.headers.get('content-type', ''):
            data = response.json()
            
            required_fields = ['error', 'message', 'availableEndpoints']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ API 404 response properly formatted")
                print(f"   Error: {data['error']}")
                print(f"   Available endpoints: {len(data['availableEndpoints'])} listed")
                return True
            else:
                print(f"❌ Missing fields in 404 response: {missing_fields}")
                return False
        else:
            print("❌ API 404 response not in JSON format")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API 404: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting MetaExtract Routing Fix Verification")
    print("=" * 60)
    
    routing_ok = test_routing_fix()
    format_ok = test_api_404_format()
    
    print("\n" + "=" * 60)
    print("🏁 Final Verification Summary")
    
    if routing_ok and format_ok:
        print("🎉 SUCCESS: All routing fixes are working correctly!")
        print("\n✅ The following issues have been resolved:")
        print("   • API routes no longer return HTML")
        print("   • Invalid API endpoints return proper JSON 404")
        print("   • Client routes continue to serve HTML correctly")
        print("   • Routing conflict has been eliminated")
        exit(0)
    else:
        print("❌ FAILURE: Some issues remain")
        exit(1)