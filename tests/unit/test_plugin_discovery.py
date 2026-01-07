#!/usr/bin/env python3
"""Test script to verify plugin discovery and loading"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_plugin_discovery():
    """Test that all plugins can be discovered and loaded"""
    print("🔍 Testing Plugin Discovery and Loading")
    print("=" * 50)
    
    try:
        # Import the module discovery functions
        from server.extractor.module_discovery import (
            discover_and_load_plugins_global, 
            enable_plugins_global,
            get_discovered_plugins_global
        )
        
        print("✅ Successfully imported module_discovery")
        
        # Enable plugins globally
        enable_plugins_global(True)
        print("✅ Enabled plugins globally")
        
        # Discover plugins
        discover_and_load_plugins_global()
        print(f"✅ Plugin discovery completed")
        
        # Get discovered plugins info
        plugins_info = get_discovered_plugins_func()
        discovered_plugins = list(plugins_info.keys())
        print(f"✅ Found {len(discovered_plugins)} plugins/modules")
        
        # List all discovered plugins
        for i, plugin in enumerate(discovered_plugins, 1):
            print(f"   {i}. {plugin}")
        
        # Get detailed plugin info
        plugins_info = get_discovered_plugins_global()
        print(f"\n📊 Plugin Details:")
        for plugin_name, plugin_info in plugins_info.items():
            print(f"   📦 {plugin_name}:")
            print(f"      Module: {plugin_info.get('module', 'N/A')}")
            print(f"      Path: {plugin_info.get('path', 'N/A')}")
            
            # Try to get plugin metadata
            try:
                module = plugin_info.get('module')
                if module and hasattr(module, 'get_plugin_metadata'):
                    metadata = module.get_plugin_metadata()
                    print(f"      Version: {metadata.get('version', 'N/A')}")
                    print(f"      Author: {metadata.get('author', 'N/A')}")
                elif module:
                    # Try static metadata
                    version = getattr(module, 'PLUGIN_VERSION', 'N/A')
                    author = getattr(module, 'PLUGIN_AUTHOR', 'N/A')
                    print(f"      Version: {version}")
                    print(f"      Author: {author}")
            except Exception as e:
                print(f"      Metadata Error: {e}")
        
        print(f"\n🎉 Plugin discovery successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("This might mean the module_discovery system needs to be updated")
        print("Trying to import the function directly...")
        try:
            # Try importing the function directly
            from server.extractor.module_discovery import get_discovered_plugins_global
            print("✅ Successfully imported get_discovered_plugins_global")
            return test_plugin_discovery_with_function(get_discovered_plugins_global)
        except ImportError as e2:
            print(f"❌ Still cannot import: {e2}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_plugin_discovery_with_function():
    """Test plugin discovery using the provided function"""
    print("🔍 Testing Plugin Discovery and Loading")
    print("=" * 50)
    
    try:
        # Import the module discovery functions
        from server.extractor.module_discovery import (
            discover_and_load_plugins_global, 
            enable_plugins_global
        )
        
        print("✅ Successfully imported module_discovery")
        
        # Enable plugins globally
        enable_plugins_global(True)
        print("✅ Enabled plugins globally")
        
        # Discover plugins
        discovered_plugins = discover_and_load_plugins_global()
        print(f"✅ Discovered {len(discovered_plugins)} plugins")
        
        # List all discovered plugins
        for i, plugin in enumerate(discovered_plugins, 1):
            print(f"   {i}. {plugin}")
        
        # Get detailed plugin info
        plugins_info = get_discovered_plugins()
        print(f"\n📊 Plugin Details:")
        for plugin_name, plugin_info in plugins_info.items():
            print(f"   📦 {plugin_name}:")
            print(f"      Type: {plugin_info.get('type', 'N/A')}")
            print(f"      Module: {plugin_info.get('module', 'N/A')}")
            print(f"      Path: {plugin_info.get('path', 'N/A')}")
            
            # Try to get plugin metadata
            try:
                module = plugin_info.get('module')
                if module and hasattr(module, 'get_plugin_metadata'):
                    metadata = module.get_plugin_metadata()
                    print(f"      Version: {metadata.get('version', 'N/A')}")
                    print(f"      Author: {metadata.get('author', 'N/A')}")
                elif module:
                    # Try static metadata
                    version = getattr(module, 'PLUGIN_VERSION', 'N/A')
                    author = getattr(module, 'PLUGIN_AUTHOR', 'N/A')
                    print(f"      Version: {version}")
                    print(f"      Author: {author}")
            except Exception as e:
                print(f"      Metadata Error: {e}")
        
        print(f"\n🎉 Plugin discovery successful!")
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_plugin_functions():
    """Test that plugin functions can be called"""
    print("\n🧪 Testing Plugin Function Execution")
    print("=" * 50)
    
    try:
        from server.extractor.module_discovery import get_discovered_plugins
        
        plugins_info = get_discovered_plugins()
        
        if not plugins_info:
            print("❌ No plugins discovered")
            return False
        
        success_count = 0
        total_count = 0
        
        for plugin_name, plugin_info in plugins_info.items():
            module = plugin_info.get('module')
            if not module:
                continue
                
            print(f"\n🔧 Testing {plugin_name}:")
            
            # Find all callable functions that don't start with underscore
            functions = []
            for attr_name in dir(module):
                if not attr_name.startswith('_') and callable(getattr(module, attr_name)):
                    attr = getattr(module, attr_name)
                    if attr.__module__ == module.__name__:  # Only functions defined in this module
                        functions.append(attr_name)
            
            print(f"   Found {len(functions)} functions: {', '.join(functions)}")
            
            # Test each function with a dummy file path
            for func_name in functions:
                try:
                    func = getattr(module, func_name)
                    
                    # Skip if it's the metadata function
                    if func_name == 'get_plugin_metadata':
                        continue
                    
                    # Call the function with a test file path
                    result = func("test_file.test")
                    
                    if isinstance(result, dict):
                        print(f"   ✅ {func_name}() returned dict with {len(result)} keys")
                        success_count += 1
                    else:
                        print(f"   ⚠️  {func_name}() returned non-dict: {type(result)}")
                    
                    total_count += 1
                    
                except Exception as e:
                    print(f"   ❌ {func_name}() error: {e}")
                    total_count += 1
        
        print(f"\n📊 Function Test Results:")
        print(f"   Total functions tested: {total_count}")
        print(f"   Successful executions: {success_count}")
        print(f"   Success rate: {success_count/total_count*100:.1f}%" if total_count > 0 else "N/A")
        
        return success_count == total_count
        
    except Exception as e:
        print(f"❌ Error testing plugin functions: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 MetaExtract Plugin System Test")
    print("=" * 50)
    
    # Test 1: Plugin Discovery
    discovery_success = test_plugin_discovery()
    
    # Test 2: Plugin Functions
    if discovery_success:
        function_success = test_plugin_functions()
    else:
        function_success = False
    
    # Final summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    print(f"🔍 Plugin Discovery: {'✅ PASS' if discovery_success else '❌ FAIL'}")
    print(f"🧪 Function Testing: {'✅ PASS' if function_success else '❌ FAIL'}")
    
    if discovery_success and function_success:
        print("\n🎉 All tests passed! Plugin system is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
