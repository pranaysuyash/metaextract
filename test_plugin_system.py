#!/usr/bin/env python3
"""
Test script for enhanced plugin system.
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
    from extractor.module_discovery import ModuleRegistry
    from extractor.exceptions.extraction_exceptions import (
        ConfigurationError,
        DependencyError
    )
    print("✅ Successfully imported plugin system components")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running this from the project root directory")
    sys.exit(1)


def test_plugin_discovery_basic():
    """Test basic plugin discovery functionality."""
    print("\n🧪 Testing Basic Plugin Discovery...")
    
    try:
        registry = ModuleRegistry()
        
        # Test with non-existent directory - should handle gracefully
        registry.enable_plugins(True, ["/path/to/nonexistent/directory"])
        registry.discover_and_load_plugins()
        
        # Should complete without errors, just with 0 plugins loaded
        if registry.plugins_loaded_count == 0 and registry.plugins_failed_count == 0:
            print(f"✅ Handled non-existent directory gracefully (0 plugins loaded)")
            return True
        else:
            print(f"❌ Unexpected plugin counts: loaded={registry.plugins_loaded_count}, failed={registry.plugins_failed_count}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        traceback.print_exc()
        return False


def test_plugin_discovery_with_valid_plugin():
    """Test plugin discovery with a valid plugin."""
    print("\n🧪 Testing Plugin Discovery with Valid Plugin...")
    
    # Create a temporary directory with a test plugin
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a simple test plugin
        test_plugin_content = '''
# Test Plugin
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "Test Author"
PLUGIN_DESCRIPTION = "Test plugin for validation"
PLUGIN_LICENSE = "MIT"

def extract_test_plugin_metadata(filepath: str) -> dict:
    """Test extraction function."""
    return {"plugin_test": "data", "filepath": filepath}

def analyze_test_plugin_content(filepath: str) -> dict:
    """Test analysis function."""
    return {"plugin_analysis": "result"}
'''
        
        test_plugin_path = Path(temp_dir) / "test_plugin.py"
        with open(test_plugin_path, 'w') as f:
            f.write(test_plugin_content)
        
        try:
            registry = ModuleRegistry()
            registry.enable_plugins(True, [temp_dir])
            registry.discover_and_load_plugins()
            
            if registry.plugins_loaded_count == 1:
                print(f"✅ Successfully loaded {registry.plugins_loaded_count} plugin")
                
                # Check if the plugin was registered correctly
                if "test_plugin" in registry.loaded_plugins:
                    plugin_info = registry.loaded_plugins["test_plugin"]
                    functions = plugin_info["functions"]
                    
                    if len(functions) == 2:
                        print(f"✅ Found {len(functions)} plugin functions")
                        print(f"   Functions: {list(functions.keys())}")
                        
                        # Check plugin metadata
                        metadata = plugin_info["metadata"]
                        if metadata["version"] == "1.0.0":
                            print("✅ Plugin metadata extracted correctly")
                            return True
                        else:
                            print(f"❌ Unexpected plugin version: {metadata['version']}")
                            return False
                    else:
                        print(f"❌ Expected 2 functions but found {len(functions)}")
                        return False
                else:
                    print("❌ Plugin not found in registry")
                    return False
            else:
                print(f"❌ Expected 1 loaded plugin but got {registry.plugins_loaded_count}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            traceback.print_exc()
            return False


def test_plugin_discovery_with_dependencies():
    """Test plugin discovery with dependencies."""
    print("\n🧪 Testing Plugin Discovery with Dependencies...")
    
    # Create a temporary directory with a test plugin that has dependencies
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test plugin with dependencies
        test_plugin_content = '''
# This will cause an ImportError at plugin load time
import nonexistent_library

PLUGIN_VERSION = "1.0.0"

def extract_test_plugin_metadata(filepath: str) -> dict:
    """Test extraction function."""
    return {"plugin_test": "data"}
'''
        
        test_plugin_path = Path(temp_dir) / "test_dep_plugin.py"
        with open(test_plugin_path, 'w') as f:
            f.write(test_plugin_content)
        
        try:
            registry = ModuleRegistry()
            registry.enable_plugins(True, [temp_dir])
            registry.discover_and_load_plugins()
            
            if registry.plugins_loaded_count == 0:
                print(f"✅ Correctly failed to load plugin with missing dependency")
                
                # Check if the plugin was in errors
                if "test_dep_plugin" in registry.plugin_load_errors:
                    print("✅ Plugin correctly added to load errors")
                    return True
                else:
                    print("❌ Plugin not found in load errors")
                    return False
            else:
                print(f"❌ Expected 0 loaded plugins but got {registry.plugins_loaded_count}")
                return False
                
        except DependencyError as e:
            print(f"✅ Correctly raised DependencyError: {e.message}")
            print(f"   Missing dependency: {e.context.get('missing_dependency')}")
            return True
        except Exception as e:
            print(f"❌ Unexpected exception: {type(e).__name__}: {e}")
            traceback.print_exc()
            return False


def test_plugin_health_monitoring():
    """Test plugin health monitoring functionality."""
    print("\n🧪 Testing Plugin Health Monitoring...")
    
    # Create a temporary directory with a test plugin
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a simple test plugin
        test_plugin_content = '''
PLUGIN_VERSION = "1.0.0"

def extract_test_plugin_metadata(filepath: str) -> dict:
    """Test extraction function."""
    return {"plugin_test": "data"}
'''
        
        test_plugin_path = Path(temp_dir) / "test_plugin.py"
        with open(test_plugin_path, 'w') as f:
            f.write(test_plugin_content)
        
        try:
            registry = ModuleRegistry()
            registry.enable_plugins(True, [temp_dir])
            registry.discover_and_load_plugins()
            
            # Check if health monitoring is initialized
            if hasattr(registry, 'health_stats') and registry.health_stats:
                health_metrics = registry.health_stats
                
                # Check if plugin health data exists
                if "test_plugin" in health_metrics:
                    plugin_health = health_metrics["test_plugin"]
                    
                    expected_keys = ['error_count', 'success_count', 'last_error', 'last_success', 'status', 'last_check', 'type']
                    missing_keys = [key for key in expected_keys if key not in plugin_health]
                    
                    if not missing_keys and plugin_health['type'] == 'plugin':
                        print(f"✅ Plugin health monitoring initialized correctly")
                        print(f"   Status: {plugin_health['status']}")
                        return True
                    else:
                        print(f"❌ Missing health data keys: {missing_keys}")
                        return False
                else:
                    print("❌ Plugin not found in health monitoring")
                    return False
            else:
                print("❌ Health monitoring not initialized")
                return False
                
        except Exception as e:
            print(f"❌ Health monitoring test failed: {e}")
            traceback.print_exc()
            return False


def main():
    """Run all plugin system tests."""
    print("🚀 Starting Enhanced Plugin System Tests")
    print("=" * 50)
    
    tests = [
        test_plugin_discovery_basic,
        test_plugin_discovery_with_valid_plugin,
        test_plugin_discovery_with_dependencies,
        test_plugin_health_monitoring
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
        print("🎉 All tests passed! Plugin system is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)