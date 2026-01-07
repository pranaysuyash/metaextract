#!/usr/bin/env python3
"""
Test script to verify MetaExtract routing issues.
This script tests various endpoints to identify broken routes and responses.
"""

import requests
import json
import sys
from typing import Dict, Any

# Base URLs
CLIENT_URL = "http://localhost:5173"
API_URL = "http://localhost:3000"

def check_endpoint(url: str, expected_type: str = "json", method: str = "GET", data: Dict = None) -> Dict[str, Any]:
    """Test an endpoint and return results"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        
        result = {
            "url": url,
            "status_code": response.status_code,
            "content_type": response.headers.get("content-type", "unknown"),
            "response_size": len(response.content),
            "success": False,
            "error": None
        }
        
        # Check if response is HTML when expecting JSON
        if expected_type == "json" and "text/html" in result["content_type"]:
            result["error"] = "Expected JSON but received HTML"
            result["response_preview"] = response.text[:200] + "..." if len(response.text) > 200 else response.text
        elif expected_type == "json":
            try:
                json_data = response.json()
                result["json_response"] = json_data
                result["success"] = True
            except json.JSONDecodeError as e:
                result["error"] = f"Invalid JSON response: {str(e)}"
                result["response_preview"] = response.text[:200] + "..." if len(response.text) > 200 else response.text
        else:
            result["success"] = True
            
    except requests.exceptions.RequestException as e:
        result = {
            "url": url,
            "status_code": None,
            "error": str(e),
            "success": False
        }
    
    return result

def run_tests():
    """Run comprehensive routing tests"""
    print("🧪 MetaExtract Routing Test Suite")
    print("=" * 50)
    
    tests = [
        # API Endpoints
        ("API Health Check", f"{API_URL}/api/extract/health", "json"),
        ("Auth Status", f"{API_URL}/api/auth/me", "json"),
        ("Dev Users (Broken)", f"{API_URL}/api/auth/dev/users", "json"),
        ("Invalid API Route", f"{API_URL}/api/invalid/route", "json"),
        
        # Client Routes
        ("Home Page", f"{CLIENT_URL}/", "html"),
        ("Results Page", f"{CLIENT_URL}/results", "html"),
        ("Dashboard (Protected)", f"{CLIENT_URL}/dashboard", "html"),
        ("Invalid Client Route", f"{CLIENT_URL}/invalid-route", "html"),
        
        # Images MVP Routes
        ("Images MVP Landing", f"{CLIENT_URL}/images_mvp", "html"),
        ("Images MVP Results", f"{CLIENT_URL}/images_mvp/results", "html"),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for test_name, url, expected_type in tests:
        print(f"\n📍 Testing: {test_name}")
        print(f"URL: {url}")
        
        result = check_endpoint(url, expected_type)
        results.append(result)
        
        if result["success"]:
            print("✅ PASSED")
            if "status_code" in result:
                print(f"   Status: {result['status_code']}")
            passed += 1
        else:
            print("❌ FAILED")
            if "error" in result:
                print(f"   Error: {result['error']}")
            if "status_code" in result:
                print(f"   Status: {result['status_code']}")
            if "response_preview" in result:
                print(f"   Preview: {result['response_preview']}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    # Detailed Analysis
    print("\n🔍 Detailed Analysis")
    print("-" * 30)
    
    html_responses = [r for r in results if "text/html" in r.get("content_type", "")]
    json_responses = [r for r in results if "application/json" in r.get("content_type", "")]
    
    print(f"HTML Responses: {len(html_responses)}")
    print(f"JSON Responses: {len(json_responses)}")
    
    # Identify routing issues
    api_html_issues = [r for r in results if r["url"].startswith(API_URL) and "text/html" in r.get("content_type", "")]
    if api_html_issues:
        print(f"\n⚠️  CRITICAL: Found {len(api_html_issues)} API endpoints returning HTML:")
        for issue in api_html_issues:
            print(f"   - {issue['url']}")
    
    return results

if __name__ == "__main__":
    try:
        results = run_tests()
        
        # Save detailed results
        with open("routing_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to routing_test_results.json")
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite failed: {str(e)}")
        sys.exit(1)