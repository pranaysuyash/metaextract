#!/usr/bin/env python3
"""
Test script for the new advanced analysis API endpoints
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server', 'extractor'))

def test_forensic_capabilities():
    """Test the forensic capabilities endpoint logic"""
    print("🧪 Testing forensic capabilities...")
    
    # Simulate the capabilities logic
    tiers = ['free', 'professional', 'forensic', 'enterprise']
    
    for tier in tiers:
        print(f"\n📊 Tier: {tier}")
        advanced_available = tier != 'free'
        print(f"  Advanced analysis: {advanced_available}")
        
        modules_available = tier in ['professional', 'forensic', 'enterprise']
        print(f"  Forensic modules: {modules_available}")
        
        batch_files = {
            'enterprise': 100,
            'forensic': 50, 
            'professional': 25,
            'free': 0
        }.get(tier, 0)
        print(f"  Max batch files: {batch_files}")
        
        reports_available = tier == 'enterprise'
        print(f"  Forensic reports: {reports_available}")

def test_advanced_analysis_integration():
    """Test that advanced analysis modules can be imported"""
    print("\n🔬 Testing advanced analysis integration...")
    
    try:
        from modules.steganography import SteganographyDetector
        print("✅ Steganography module available")
    except ImportError as e:
        print(f"❌ Steganography module: {e}")
    
    try:
        from modules.comparison import compare_metadata_files
        print("✅ Comparison module available")
    except ImportError as e:
        print(f"❌ Comparison module: {e}")
    
    try:
        from modules.timeline import reconstruct_timeline
        print("✅ Timeline module available")
    except ImportError as e:
        print(f"❌ Timeline module: {e}")
    
    try:
        from comprehensive_metadata_engine import extract_comprehensive_metadata
        print("✅ Comprehensive engine available")
    except ImportError as e:
        print(f"❌ Comprehensive engine: {e}")

def test_sample_advanced_analysis():
    """Test advanced analysis on sample file"""
    print("\n🎯 Testing sample advanced analysis...")
    
    try:
        from comprehensive_metadata_engine import extract_comprehensive_metadata
        
        # Test with our sample image
        result = extract_comprehensive_metadata('test.jpg', tier='professional')
        
        print(f"✅ Analysis completed")
        print(f"  Fields extracted: {result.get('extraction_info', {}).get('fields_extracted', 0)}")
        
        # Check for advanced analysis results
        advanced_fields = [
            'steganography_analysis',
            'manipulation_detection', 
            'ai_detection',
            'burned_metadata',
            'metadata_comparison'
        ]
        
        for field in advanced_fields:
            if field in result:
                print(f"  {field}: ✅")
            else:
                print(f"  {field}: ❌")
                
    except Exception as e:
        print(f"❌ Advanced analysis failed: {e}")

if __name__ == "__main__":
    print("🚀 Advanced API Integration Test")
    print("=" * 50)
    
    test_forensic_capabilities()
    test_advanced_analysis_integration()
    test_sample_advanced_analysis()
    
    print("\n" + "=" * 50)
    print("✅ Advanced API integration tests completed!")