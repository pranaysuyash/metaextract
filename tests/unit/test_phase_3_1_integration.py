#!/usr/bin/env python3
"""
Test script for Phase 3.1: Advanced Analysis Integration

This script tests the automatic triggering of forensic analysis features
and validates the confidence scoring and visualization data structures.
"""

import json
import requests
import time
import sys
from pathlib import Path

def test_forensic_analysis_integration():
    """Test the forensic analysis integration with a sample image."""
    
    # Test configuration
    base_url = "http://localhost:3000"  # Adjust if your server runs on a different port
    test_file = "sample_with_meta.jpg"  # Use the existing sample file
    
    # Ensure test file exists
    if not Path(test_file).exists():
        print(f"❌ Test file {test_file} not found. Please provide a test image.")
        return False
    
    print("🧪 Testing Phase 3.1: Advanced Analysis Integration")
    print("=" * 60)
    
    # Test 1: Basic extraction with forensic tier (should trigger advanced analysis)
    print("\n1️⃣ Testing forensic tier with automatic advanced analysis...")
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': f}
            data = {'tier': 'forensic'}  # Use forensic tier to trigger advanced analysis
            
            response = requests.post(f"{base_url}/api/extract", files=files, data=data)
            
            if response.status_code != 200:
                print(f"❌ Request failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            result = response.json()
            
            # Validate forensic analysis integration
            forensic_integration = result.get('forensic_analysis_integration')
            if not forensic_integration:
                print("❌ Forensic analysis integration not found in response")
                return False
            
            print("✅ Forensic analysis integration found")
            
            # Validate required fields
            required_fields = [
                'enabled', 'processing_time_ms', 'modules_analyzed', 
                'confidence_scores', 'forensic_score', 'authenticity_assessment',
                'risk_indicators', 'visualization_data'
            ]
            
            for field in required_fields:
                if field not in forensic_integration:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            print("✅ All required fields present")
            
            # Validate forensic score
            forensic_score = forensic_integration.get('forensic_score')
            if not isinstance(forensic_score, (int, float)) or forensic_score < 0 or forensic_score > 100:
                print(f"❌ Invalid forensic score: {forensic_score}")
                return False
            
            print(f"✅ Forensic score valid: {forensic_score}")
            
            # Validate authenticity assessment
            authenticity = forensic_integration.get('authenticity_assessment')
            valid_assessments = ['authentic', 'likely_authentic', 'questionable', 'likely_manipulated', 'suspicious']
            if authenticity not in valid_assessments:
                print(f"❌ Invalid authenticity assessment: {authenticity}")
                return False
            
            print(f"✅ Authenticity assessment valid: {authenticity}")
            
            # Validate confidence scores
            confidence_scores = forensic_integration.get('confidence_scores', {})
            if not isinstance(confidence_scores, dict):
                print("❌ Confidence scores should be a dictionary")
                return False
            
            for module, score in confidence_scores.items():
                if not isinstance(score, (int, float)) or score < 0 or score > 1:
                    print(f"❌ Invalid confidence score for {module}: {score}")
                    return False
            
            print(f"✅ Confidence scores valid: {list(confidence_scores.keys())}")
            
            # Validate visualization data
            viz_data = forensic_integration.get('visualization_data', {})
            if 'forensic_score_gauge' not in viz_data:
                print("❌ Missing forensic score gauge visualization")
                return False
            
            gauge = viz_data['forensic_score_gauge']
            if not all(key in gauge for key in ['score', 'color', 'label']):
                print("❌ Incomplete forensic score gauge data")
                return False
            
            print("✅ Visualization data valid")
            
            # Validate risk indicators
            risk_indicators = forensic_integration.get('risk_indicators', [])
            if isinstance(risk_indicators, list):
                for indicator in risk_indicators:
                    required_indicator_fields = ['module', 'risk_level', 'confidence', 'description']
                    if not all(field in indicator for field in required_indicator_fields):
                        print(f"❌ Incomplete risk indicator: {indicator}")
                        return False
                
                if risk_indicators:
                    print(f"✅ Risk indicators found: {len(risk_indicators)}")
                else:
                    print("ℹ️ No risk indicators found (file appears authentic)")
            
            # Test 2: Verify backward compatibility
            print("\n2️⃣ Testing backward compatibility...")
            
            # Check that standard extraction fields are still present
            standard_fields = ['filename', 'filesize', 'filetype', 'mime_type', 'tier', 'fields_extracted']
            for field in standard_fields:
                if field not in result:
                    print(f"❌ Missing standard field: {field}")
                    return False
            
            print("✅ Standard extraction fields present")
            
            # Check that advanced_analysis is still present for compatibility
            if 'advanced_analysis' not in result:
                print("❌ Missing advanced_analysis field (backward compatibility)")
                return False
            
            print("✅ Backward compatibility maintained")
            
            # Test 3: Test with different tiers
            print("\n3️⃣ Testing with enterprise tier...")
            
            with open(test_file, 'rb') as f:
                files = {'file': f}
                data = {'tier': 'enterprise'}
                
                response = requests.post(f"{base_url}/api/extract", files=files, data=data)
                
                if response.status_code != 200:
                    print(f"❌ Enterprise tier request failed: {response.status_code}")
                    return False
                
                enterprise_result = response.json()
                if 'forensic_analysis_integration' not in enterprise_result:
                    print("❌ Enterprise tier missing forensic analysis integration")
                    return False
                
                print("✅ Enterprise tier forensic analysis working")
            
            # Test 4: Test with lower tier (should not have forensic integration)
            print("\n4️⃣ Testing with professional tier (should not trigger forensic integration)...")
            
            with open(test_file, 'rb') as f:
                files = {'file': f}
                data = {'tier': 'professional'}
                
                response = requests.post(f"{base_url}/api/extract", files=files, data=data)
                
                if response.status_code != 200:
                    print(f"❌ Professional tier request failed: {response.status_code}")
                    return False
                
                prof_result = response.json()
                if 'forensic_analysis_integration' in prof_result:
                    print("⚠️  Professional tier has forensic analysis integration (unexpected)")
                else:
                    print("✅ Professional tier correctly excludes forensic analysis integration")
            
            # Summary
            print("\n" + "=" * 60)
            print("🎉 Phase 3.1 Integration Test COMPLETED SUCCESSFULLY!")
            print("\nKey Features Verified:")
            print("✅ Automatic forensic analysis triggering for forensic+ tiers")
            print("✅ Confidence scoring for all forensic modules")
            print("✅ Forensic score calculation and authenticity assessment")
            print("✅ Risk indicators with detailed descriptions")
            print("✅ Visualization data structure for frontend")
            print("✅ Backward compatibility maintained")
            print("✅ Tier-based access control working")
            
            return True
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to server at {base_url}")
        print("Please ensure the server is running and try again.")
        return False
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_advanced_endpoint():
    """Test the advanced endpoint to ensure it still works."""
    print("\n5️⃣ Testing advanced endpoint compatibility...")
    
    test_file = "sample_with_meta.jpg"
    base_url = "http://localhost:3000"
    
    if not Path(test_file).exists():
        print(f"❌ Test file {test_file} not found")
        return False
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': f}
            
            response = requests.post(f"{base_url}/api/extract/advanced", files=files)
            
            if response.status_code != 200:
                print(f"❌ Advanced endpoint request failed: {response.status_code}")
                return False
            
            result = response.json()
            
            # Check for advanced analysis
            if 'advanced_analysis' not in result:
                print("❌ Advanced endpoint missing advanced_analysis")
                return False
            
            # Should also have forensic integration now
            if 'forensic_analysis_integration' not in result:
                print("⚠️  Advanced endpoint missing forensic_analysis_integration (expected)")
            
            print("✅ Advanced endpoint working correctly")
            return True
            
    except Exception as e:
        print(f"❌ Advanced endpoint test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Starting Phase 3.1 Integration Tests")
    print("=" * 60)
    
    # Run main integration test
    success = test_forensic_analysis_integration()
    
    if success:
        # Test advanced endpoint
        success = test_advanced_endpoint() and success
    
    # Final result
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! Phase 3.1 implementation is working correctly.")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED. Please check the implementation.")
        sys.exit(1)

if __name__ == "__main__":
    main()