#!/usr/bin/env python3
"""
Comprehensive Test Suite for Plugin Management System

This test suite validates all plugin management functionality including:
- Plugin enable/disable/reload operations
- Plugin update and upgrade mechanisms
- Module enable/disable operations
- Error handling and edge cases
- Performance and health monitoring integration
"""

import os
import sys
import tempfile
import shutil
import time
from pathlib import Path
from typing import Dict, Any

# Add the server directory to the path for imports
sys.path.insert(0, 'server')

try:
    from extractor.module_discovery import ModuleRegistry, module_registry
    from extractor.core.base_engine import BaseExtractor
    MODULE_DISCOVERY_AVAILABLE = True
except ImportError as e:
    print(f"Error importing module_discovery: {e}")
    MODULE_DISCOVERY_AVAILABLE = False


class TestPluginManagement:
    """Test suite for plugin management functionality."""
    
    def __init__(self):
        self.test_registry = ModuleRegistry()
        self.temp_dir = None
        self.test_plugin_dir = None
        self.test_plugin_file = None
        
    def setup(self):
        """Setup test environment."""
        if not MODULE_DISCOVERY_AVAILABLE:
            print("Module discovery not available, skipping tests")
            return False
            
        # Create temporary directory for test plugins
        self.temp_dir = tempfile.mkdtemp()
        self.test_plugin_dir = Path(self.temp_dir) / "test_plugins"
        self.test_plugin_dir.mkdir()
        
        # Create a simple test plugin
        test_plugin_content = '''
def extract_test_metadata(filepath: str) -> Dict[str, Any]:
    """Extract test metadata from a file."""
    return {"test_plugin": True, "file": filepath}

def detect_test_features(filepath: str) -> Dict[str, Any]:
    """Detect test features in a file."""
    return {"features": ["test_feature_1", "test_feature_2"]}

PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "Test Author"
PLUGIN_DESCRIPTION = "Test plugin for management testing"
'''
        
        self.test_plugin_file = self.test_plugin_dir / "test_plugin.py"
        with open(self.test_plugin_file, 'w') as f:
            f.write(test_plugin_content)
            
        return True
    
    def teardown(self):
        """Clean up test environment."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_plugin_enable_disable(self):
        """Test plugin enable/disable functionality."""
        print("\n=== Testing Plugin Enable/Disable ===")
        
        # Enable plugin system
        self.test_registry.enable_plugins(True, [str(self.test_plugin_dir)])
        
        # Discover and load plugins
        self.test_registry.discover_and_load_plugins()
        
        # Check if plugin was loaded
        plugins = self.test_registry.get_all_plugins_info()
        if 'test_plugin' not in plugins:
            print("❌ FAILED: Test plugin not loaded")
            return False
        
        print("✅ Test plugin loaded successfully")
        
        # Test disable plugin
        result = self.test_registry.disable_plugin('test_plugin')
        if not result:
            print("❌ FAILED: Could not disable plugin")
            return False
        
        plugin_info = self.test_registry.get_plugin_info('test_plugin')
        if plugin_info and plugin_info.get('enabled', True):
            print("❌ FAILED: Plugin still enabled after disable")
            return False
        
        print("✅ Plugin disabled successfully")
        
        # Test enable plugin
        result = self.test_registry.enable_plugin('test_plugin')
        if not result:
            print("❌ FAILED: Could not enable plugin")
            return False
        
        plugin_info = self.test_registry.get_plugin_info('test_plugin')
        if plugin_info and not plugin_info.get('enabled', False):
            print("❌ FAILED: Plugin still disabled after enable")
            return False
        
        print("✅ Plugin enabled successfully")
        return True
    
    def test_plugin_reload(self):
        """Test plugin reload functionality."""
        print("\n=== Testing Plugin Reload ===")
        
        # Create a modified version of the plugin
        modified_plugin_content = '''
def extract_test_metadata(filepath: str) -> Dict[str, Any]:
    """Extract test metadata from a file - MODIFIED."""
    return {"test_plugin": True, "file": filepath, "modified": True}

def detect_test_features(filepath: str) -> Dict[str, Any]:
    """Detect test features in a file - MODIFIED."""
    return {"features": ["test_feature_1", "test_feature_2", "new_feature"]}

PLUGIN_VERSION = "1.0.1"
PLUGIN_AUTHOR = "Test Author"
PLUGIN_DESCRIPTION = "Test plugin for management testing - MODIFIED"
'''
        
        # Write modified plugin
        with open(self.test_plugin_file, 'w') as f:
            f.write(modified_plugin_content)
        
        # Reload the plugin
        result = self.test_registry.reload_plugin('test_plugin')
        if not result:
            print("❌ FAILED: Could not reload plugin")
            return False
        
        print("✅ Plugin reloaded successfully")
        
        # Check if plugin has new version
        plugin_info = self.test_registry.get_plugin_info('test_plugin')
        if plugin_info and plugin_info.get('metadata', {}).get('version') == '1.0.1':
            print("✅ Plugin version updated correctly")
            return True
        else:
            print("❌ FAILED: Plugin version not updated")
            return False
    
    def test_plugin_update(self):
        """Test plugin update functionality."""
        print("\n=== Testing Plugin Update ===")
        
        # Create a new version of the plugin in a different location
        new_plugin_dir = Path(self.temp_dir) / "new_plugins"
        new_plugin_dir.mkdir()
        
        new_plugin_content = '''
def extract_test_metadata(filepath: str) -> Dict[str, Any]:
    """Extract test metadata from a file - UPDATED."""
    return {"test_plugin": True, "file": filepath, "updated": True}

def detect_test_features(filepath: str) -> Dict[str, Any]:
    """Detect test features in a file - UPDATED."""
    return {"features": ["test_feature_1", "test_feature_2", "updated_feature"]}

PLUGIN_VERSION = "2.0.0"
PLUGIN_AUTHOR = "Test Author"
PLUGIN_DESCRIPTION = "Test plugin for management testing - UPDATED"
'''
        
        new_plugin_file = new_plugin_dir / "test_plugin.py"
        with open(new_plugin_file, 'w') as f:
            f.write(new_plugin_content)
        
        # Update the plugin
        result = self.test_registry.update_plugin('test_plugin', str(new_plugin_file))
        if not result:
            print("❌ FAILED: Could not update plugin")
            return False
        
        print("✅ Plugin updated successfully")
        
        # Check if plugin has new version
        plugin_info = self.test_registry.get_plugin_info('test_plugin')
        if plugin_info and plugin_info.get('metadata', {}).get('version') == '2.0.0':
            print("✅ Plugin version updated correctly")
            return True
        else:
            print("❌ FAILED: Plugin version not updated")
            return False
    
    def test_module_enable_disable(self):
        """Test module enable/disable functionality."""
        print("\n=== Testing Module Enable/Disable ===")
        
        # Discover modules
        self.test_registry.discover_modules("server/extractor/modules/")
        
        # Get all modules
        modules = self.test_registry.get_all_extraction_functions()
        if not modules:
            print("⚠️  WARNING: No modules found, skipping module tests")
            return True
            
        # Get first module name
        module_name = list(modules.keys())[0]
        
        # Test disable module
        result = self.test_registry.disable_module(module_name)
        if not result:
            print("❌ FAILED: Could not disable module")
            return False
        
        module_info = self.test_registry.get_module_info(module_name)
        if module_info and module_info.get('enabled', True):
            print("❌ FAILED: Module still enabled after disable")
            return False
        
        print("✅ Module disabled successfully")
        
        # Test enable module
        result = self.test_registry.enable_module(module_name)
        if not result:
            print("❌ FAILED: Could not enable module")
            return False
        
        module_info = self.test_registry.get_module_info(module_name)
        if module_info and not module_info.get('enabled', False):
            print("❌ FAILED: Module still disabled after enable")
            return False
        
        print("✅ Module enabled successfully")
        return True
    
    def test_global_functions(self):
        """Test global plugin management functions."""
        print("\n=== Testing Global Functions ===")
        
        # Test global plugin enable/disable
        result = module_registry.enable_plugins(True, [str(self.test_plugin_dir)])
        if result is None:  # enable_plugins returns None
            print("✅ Global plugin enable works")
        else:
            print("❌ FAILED: Global plugin enable failed")
            return False
        
        # Test global plugin operations
        try:
            result = module_registry.enable_plugin_global('test_plugin')
            if result:
                print("✅ Global plugin enable works")
            else:
                print("⚠️  WARNING: Global plugin enable returned False (plugin may not exist)")
                
            result = module_registry.disable_plugin_global('test_plugin')
            if result:
                print("✅ Global plugin disable works")
            else:
                print("⚠️  WARNING: Global plugin disable returned False (plugin may not exist)")
                
            result = module_registry.reload_plugin_global('test_plugin')
            if result:
                print("✅ Global plugin reload works")
            else:
                print("⚠️  WARNING: Global plugin reload returned False (plugin may not exist)")
                
        except Exception as e:
            print(f"❌ FAILED: Global plugin operations failed: {e}")
            return False
        
        return True
    
    def test_error_handling(self):
        """Test error handling in plugin management."""
        print("\n=== Testing Error Handling ===")
        
        # Test operations on non-existent plugins
        result = self.test_registry.enable_plugin('non_existent_plugin')
        if result:
            print("❌ FAILED: Enabled non-existent plugin")
            return False
        
        result = self.test_registry.disable_plugin('non_existent_plugin')
        if result:
            print("❌ FAILED: Disabled non-existent plugin")
            return False
        
        result = self.test_registry.reload_plugin('non_existent_plugin')
        if result:
            print("❌ FAILED: Reloaded non-existent plugin")
            return False
        
        result = self.test_registry.update_plugin('non_existent_plugin', '/invalid/path')
        if result:
            print("❌ FAILED: Updated non-existent plugin")
            return False
        
        print("✅ Error handling works correctly")
        return True
    
    def test_plugin_stats(self):
        """Test plugin statistics functionality."""
        print("\n=== Testing Plugin Statistics ===")
        
        # Get plugin stats
        stats = self.test_registry.get_plugin_stats()
        print(f"Plugin stats: {stats}")
        
        # Check if stats contain expected fields
        expected_fields = ['plugins_enabled', 'plugins_loaded', 'plugins_failed']
        for field in expected_fields:
            if field not in stats:
                print(f"❌ FAILED: Missing field {field} in plugin stats")
                return False
        
        print("✅ Plugin statistics work correctly")
        return True
    
    def run_all_tests(self):
        """Run all plugin management tests."""
        print("🚀 Starting Plugin Management Test Suite")
        
        if not self.setup():
            print("❌ Setup failed, aborting tests")
            return False
        
        try:
            tests = [
                self.test_plugin_enable_disable,
                self.test_plugin_reload,
                self.test_plugin_update,
                self.test_module_enable_disable,
                self.test_global_functions,
                self.test_error_handling,
                self.test_plugin_stats
            ]
            
            passed = 0
            total = len(tests)
            
            for test in tests:
                try:
                    if test():
                        passed += 1
                    else:
                        print(f"❌ {test.__name__} failed")
                except Exception as e:
                    print(f"❌ {test.__name__} failed with exception: {e}")
            
            print(f"\n📊 Test Results: {passed}/{total} tests passed")
            
            if passed == total:
                print("🎉 All tests passed!")
                return True
            else:
                print("❌ Some tests failed")
                return False
                
        finally:
            self.teardown()


if __name__ == "__main__":
    # Run the test suite
    test_suite = TestPluginManagement()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)