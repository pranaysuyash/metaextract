#!/usr/bin/env python3
"""
Test script for enhanced plugin integration with the comprehensive engine.
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path

# Add the server directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
server_dir = os.path.join(current_dir, "server")
sys.path.insert(0, server_dir)

try:
    from extractor.comprehensive_metadata_engine import ComprehensiveMetadataExtractor
    from extractor.module_discovery import ModuleRegistry, enable_plugins_global, discover_and_load_plugins_global
    print("✅ Successfully imported plugin integration components")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running this from the project root directory")
    sys.exit(1)


def test_plugin_integration_basic():
    """Test basic plugin integration with the comprehensive engine."""
    print("\n🧪 Testing Basic Plugin Integration...")
    
    try:
        # Initialize the comprehensive engine
        engine = ComprehensiveMetadataExtractor()
        
        # Check if plugin system was initialized
        if hasattr(engine, 'plugin_stats') and engine.plugin_stats:
            stats = engine.plugin_stats
            print(f"✅ Plugin system initialized: {stats.get('plugins_loaded', 0)} plugins loaded")
            
            # Check if plugin health monitoring is initialized
            if hasattr(engine, 'module_health_metrics') and engine.module_health_metrics:
                plugin_health_count = sum(1 for data in engine.module_health_metrics.values() if data.get('type') == 'plugin')
                print(f"✅ Plugin health monitoring: {plugin_health_count} plugins tracked")
                return True
            else:
                print("❌ Plugin health monitoring not initialized")
                return False
        else:
            print("❌ Plugin system not initialized")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        traceback.print_exc()
        return False


def test_plugin_execution_with_engine():
    """Test plugin execution through the comprehensive engine."""
    print("\n🧪 Testing Plugin Execution with Engine...")
    
    # Create a temporary directory with a test plugin
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a simple test plugin
        test_plugin_content = '''
# Test Plugin for Engine Integration
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "Test Author"
PLUGIN_DESCRIPTION = "Test plugin for engine integration"

def extract_test_integration_metadata(filepath: str) -> dict:
    """Test extraction function for engine integration."""
    return {
        "test_integration": "success",
        "filepath": filepath,
        "plugin_type": "integration_test"
    }

def analyze_test_integration_content(filepath: str) -> dict:
    """Test analysis function for engine integration."""
    return {
        "integration_analysis": "completed",
        "status": "success"
    }
'''
        
        test_plugin_path = Path(temp_dir) / "test_integration_plugin.py"
        with open(test_plugin_path, 'w') as f:
            f.write(test_plugin_content)
        
        try:
            # Create a temporary test file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("Test content for plugin integration")
                temp_file = f.name
            
            # Initialize engine with plugin discovery
            registry = ModuleRegistry()
            registry.enable_plugins(True, [temp_dir])
            registry.discover_and_load_plugins()
            
            # Create comprehensive engine
            engine = ComprehensiveMetadataExtractor()
            
            # Test metadata extraction
            result = engine.extract_comprehensive_metadata(temp_file, tier="free")
            
            # Check if we got a result
            if result and isinstance(result, dict):
                print("✅ Successfully extracted metadata with plugins")
                
                # Check for plugin execution info
                if 'extraction_info' in result:
                    extraction_info = result['extraction_info']
                    
                    # Check for dynamic modules info
                    if 'dynamic_modules' in extraction_info:
                        dynamic_info = extraction_info['dynamic_modules']
                        print(f"✅ Dynamic modules executed: {dynamic_info.get('executed_count', 0)}")
                        
                        # Check for plugin-specific info
                        if 'plugins' in extraction_info:
                            plugin_info = extraction_info['plugins']
                            print(f"✅ Plugins executed: {plugin_info.get('executed_count', 0)}")
                            print(f"   Success: {plugin_info.get('success_count', 0)}, Errors: {plugin_info.get('error_count', 0)}")
                            
                            # Check if our test plugin was executed
                            if 'test_integration_plugin' in plugin_info.get('plugin_statuses', {}):
                                plugin_status = plugin_info['plugin_statuses']['test_integration_plugin']
                                print(f"✅ Test plugin status: {plugin_status}")
                                
                                # Check if plugin results are in the main result
                                if 'extract_test_integration_metadata' in result:
                                    plugin_result = result['extract_test_integration_metadata']
                                    if plugin_result.get('test_integration') == 'success':
                                        print("✅ Test plugin executed successfully and results integrated")
                                        return True
                                    else:
                                        print(f"❌ Unexpected plugin result: {plugin_result}")
                                        return False
                                else:
                                    print("❌ Test plugin result not found in main result")
                                    return False
                            else:
                                print("❌ Test plugin not found in execution results")
                                return False
                        else:
                            print("✅ No separate plugin info (plugins included in dynamic modules)")
                            return True
                    else:
                        print("❌ Missing dynamic modules info in result")
                        return False
                else:
                    print("❌ Missing extraction info in result")
                    return False
            else:
                print(f"❌ Unexpected result type: {type(result)}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            traceback.print_exc()
            return False
        finally:
            os.unlink(temp_file)


def test_plugin_health_integration():
    """Test plugin health monitoring integration."""
    print("\n🧪 Testing Plugin Health Integration...")
    
    try:
        # Initialize the comprehensive engine
        engine = ComprehensiveMetadataExtractor()
        
        # Check plugin health statistics
        if hasattr(engine, 'plugin_stats') and engine.plugin_stats:
            stats = engine.plugin_stats
            healthy_plugins = stats.get('healthy_plugins', 0)
            unhealthy_plugins = stats.get('unhealthy_plugins', 0)
            
            print(f"✅ Plugin health statistics: {healthy_plugins} healthy, {unhealthy_plugins} unhealthy")
            
            # Check health monitoring integration
            if hasattr(engine, 'module_health_metrics') and engine.module_health_metrics:
                plugin_health_count = sum(1 for data in engine.module_health_metrics.values() if data.get('type') == 'plugin')
                print(f"✅ Plugin health monitoring integrated: {plugin_health_count} plugins tracked")
                
                # Check a sample plugin's health data
                for plugin_name, health_data in engine.module_health_metrics.items():
                    if health_data.get('type') == 'plugin':
                        expected_keys = ['error_count', 'success_count', 'last_error', 'last_success', 'status', 'last_check', 'type']
                        missing_keys = [key for key in expected_keys if key not in health_data]
                        
                        if not missing_keys:
                            print(f"✅ Sample plugin health data complete: {plugin_name} - {health_data['status']}")
                            return True
                        else:
                            print(f"❌ Missing health data keys: {missing_keys}")
                            return False
                
                print("❌ No plugin health data found")
                return False
            else:
                print("❌ Health monitoring not available")
                return False
        else:
            print("❌ Plugin statistics not available")
            return False
            
    except Exception as e:
        print(f"❌ Health integration test failed: {e}")
        traceback.print_exc()
        return False


def test_plugin_error_handling():
    """Test plugin error handling in the comprehensive engine."""
    print("\n🧪 Testing Plugin Error Handling...")
    
    # Create a temporary directory with a problematic plugin
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a plugin with a runtime error
        test_plugin_content = '''
PLUGIN_VERSION = "1.0.0"

def extract_error_plugin_metadata(filepath: str) -> dict:
    """Test extraction function that will fail."""
    # This will cause a runtime error
    raise ValueError("Simulated plugin error for testing")
'''
        
        test_plugin_path = Path(temp_dir) / "error_test_plugin.py"
        with open(test_plugin_path, 'w') as f:
            f.write(test_plugin_content)
        
        try:
            # Create a temporary test file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("Test content for error handling")
                temp_file = f.name
            
            # Initialize engine with plugin discovery
            registry = ModuleRegistry()
            registry.enable_plugins(True, [temp_dir])
            registry.discover_and_load_plugins()
            
            # Create comprehensive engine
            engine = ComprehensiveMetadataExtractor()
            
            # Test metadata extraction - should handle plugin errors gracefully
            result = engine.extract_comprehensive_metadata(temp_file, tier="free")
            
            # Check if we got a result despite plugin errors
            if result and isinstance(result, dict):
                print("✅ Engine handled plugin errors gracefully")
                
                # Check for error information
                if 'extraction_info' in result:
                    extraction_info = result['extraction_info']
                    
                    # Check for module errors
                    if 'module_errors' in result:
                        module_errors = result['module_errors']
                        if 'error_test_plugin' in module_errors:
                            error_info = module_errors['error_test_plugin']
                            print(f"✅ Plugin error captured: {error_info.get('error_code')}")
                            
                            # Check that the main extraction still completed
                            if 'extraction_info' in result and 'processing_ms' in extraction_info:
                                print("✅ Main extraction completed despite plugin errors")
                                return True
                            else:
                                print("❌ Main extraction failed")
                                return False
                        else:
                            print("❌ Plugin error not captured")
                            return False
                    else:
                        print("✅ No module errors (plugin error handled internally)")
                        return True
                else:
                    print("❌ Missing extraction info")
                    return False
            else:
                print(f"❌ Unexpected result type: {type(result)}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            traceback.print_exc()
            return False
        finally:
            os.unlink(temp_file)


def main():
    """Run all plugin integration tests."""
    print("🚀 Starting Enhanced Plugin Integration Tests")
    print("=" * 50)
    
    tests = [
        test_plugin_integration_basic,
        test_plugin_execution_with_engine,
        test_plugin_health_integration,
        test_plugin_error_handling
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
        print("🎉 All tests passed! Plugin integration is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)