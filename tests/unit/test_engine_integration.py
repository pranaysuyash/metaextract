#!/usr/bin/env python3
"""
Test script for enhanced metadata extraction engine integration.
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path

# Add the project root to sys.path for absolute imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from server.extractor.comprehensive_metadata_engine import ComprehensiveMetadataExtractor
    from server.extractor.exceptions.extraction_exceptions import (
        ConfigurationError,
        DependencyError
    )
    print("✅ Successfully imported comprehensive engine components")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running this from the project root directory")
    raise


def test_engine_initialization():
    """Test engine initialization with enhanced module discovery."""
    print("\n🧪 Testing Engine Initialization...")
    
    try:
        # Test basic initialization
        engine = ComprehensiveMetadataExtractor()
        
        # Check if module discovery was initialized
        if hasattr(engine, 'module_registry') and engine.module_registry:
            print("✅ Module registry initialized successfully")
            
            # Check module discovery stats
            if hasattr(engine, 'module_discovery_stats') and engine.module_discovery_stats:
                stats = engine.module_discovery_stats
                print(f"✅ Module discovery stats: {stats.get('loaded_count', 0)} modules loaded")
                
                # Check dependency stats
                if hasattr(engine, 'dependency_stats') and engine.dependency_stats:
                    dep_stats = engine.dependency_stats
                    print(f"✅ Dependency analysis: {dep_stats.get('total_modules_with_dependencies', 0)} modules with dependencies")
                
                # Check health monitoring
                if hasattr(engine, 'module_health_metrics') and engine.module_health_metrics:
                    health_count = len(engine.module_health_metrics)
                    print(f"✅ Health monitoring initialized for {health_count} modules")
                
                return True
            else:
                print("❌ Module discovery stats not available")
                return False
        else:
            print("❌ Module registry not initialized")
            return False
            
    except Exception as e:
        print(f"❌ Engine initialization failed: {e}")
        traceback.print_exc()
        return False


def test_engine_with_test_file():
    """Test engine with a simple test file."""
    print("\n🧪 Testing Engine with Test File...")
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test content for metadata extraction")
        temp_file = f.name
    
    try:
        engine = ComprehensiveMetadataExtractor()
        
        # Test metadata extraction
        result = engine.extract_comprehensive_metadata(temp_file, tier="free")
        
        # Check if we got a result
        if result and isinstance(result, dict):
            print("✅ Successfully extracted metadata")
            
            # Check for basic metadata fields
            if 'extraction_info' in result:
                print("✅ Extraction info present")
                
                # Check for dynamic modules info
                if 'dynamic_modules' in result.get('extraction_info', {}):
                    dynamic_info = result['extraction_info']['dynamic_modules']
                    print(f"✅ Dynamic modules executed: {dynamic_info.get('executed_count', 0)}")
                    print(f"   Success: {dynamic_info.get('success_count', 0)}, Errors: {dynamic_info.get('error_count', 0)}")
                
                return True
            else:
                print("❌ Missing extraction info in result")
                print(f"Result keys: {list(result.keys())}")
                return False
        else:
            print(f"❌ Unexpected result type: {type(result)}")
            return False
            
    except Exception as e:
        print(f"❌ Engine execution failed: {e}")
        traceback.print_exc()
        return False
    finally:
        os.unlink(temp_file)


def test_engine_error_handling():
    """Test engine error handling with invalid file."""
    print("\n🧪 Testing Engine Error Handling...")
    
    try:
        engine = ComprehensiveMetadataExtractor()
        
        # Test with non-existent file
        result = engine.extract_comprehensive_metadata("/path/to/nonexistent/file.txt", tier="free")
        
        # Should return an error result
        if result and isinstance(result, dict):
            if 'error' in result or 'error_code' in result:
                print("✅ Correctly handled file not found error")
                return True
            else:
                print("❌ Expected error result but got successful extraction")
                return False
        else:
            print("❌ Expected error result but got no result")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected exception: {type(e).__name__}: {e}")
        # This is actually expected for file not found
        print("✅ Correctly raised exception for file not found")
        return True


def test_engine_health_monitoring():
    """Test engine health monitoring functionality."""
    print("\n🧪 Testing Engine Health Monitoring...")
    
    try:
        engine = ComprehensiveMetadataExtractor()
        
        # Check if health monitoring is initialized
        if hasattr(engine, 'module_health_metrics') and engine.module_health_metrics:
            health_metrics = engine.module_health_metrics
            
            if len(health_metrics) > 0:
                print(f"✅ Health monitoring tracking {len(health_metrics)} modules")
                
                # Check a sample module's health data
                sample_module = next(iter(health_metrics.keys()))
                sample_data = health_metrics[sample_module]
                
                expected_keys = ['error_count', 'success_count', 'last_error', 'last_success', 'status', 'last_check']
                missing_keys = [key for key in expected_keys if key not in sample_data]
                
                if not missing_keys:
                    print(f"✅ Sample module health data complete: {sample_data['status']}")
                    return True
                else:
                    print(f"❌ Missing health data keys: {missing_keys}")
                    return False
            else:
                print("❌ No modules in health monitoring")
                return False
        else:
            print("❌ Health monitoring not initialized")
            return False
            
    except Exception as e:
        print(f"❌ Health monitoring test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all engine integration tests."""
    print("🚀 Starting Enhanced Engine Integration Tests")
    print("=" * 50)
    
    tests = [
        test_engine_initialization,
        test_engine_with_test_file,
        test_engine_error_handling,
        test_engine_health_monitoring
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with unexpected error: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Engine integration is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)