#!/usr/bin/env python3
"""Simple test script to verify plugin discovery and loading"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main test function"""
    print("🚀 Simple Plugin System Test")
    print("=" * 50)
    
    try:
        # Import the module discovery functions
        from server.extractor.module_discovery import (
            discover_and_load_plugins_global, 
            enable_plugins_global,
            get_discovered_plugins_global
        )
        
        print("✅ Successfully imported module_discovery functions")
        
        # Enable plugins globally
        enable_plugins_global(True)
        print("✅ Enabled plugins globally")
        
        # Discover plugins
        print("🔍 Discovering plugins...")
        discover_and_load_plugins_global()
        print("✅ Plugin discovery completed")
        
        # Get discovered plugins info
        plugins_info = get_discovered_plugins_global()
        discovered_plugins = list(plugins_info.keys())
        
        print(f"📊 Found {len(discovered_plugins)} plugins/modules:")
        
        # List all discovered plugins
        for i, plugin_name in enumerate(discovered_plugins, 1):
            plugin_info = plugins_info[plugin_name]
            plugin_type = plugin_info.get('type', 'unknown')
            print(f"   {i}. {plugin_name} ({plugin_type})")
            
            # Show some details
            if plugin_type == 'plugin':
                metadata = plugin_info.get('metadata', {})
                version = metadata.get('version', 'N/A')
                author = metadata.get('author', 'N/A')
                print(f"      Version: {version}, Author: {author}")
            
            # Show functions
            functions = plugin_info.get('functions', [])
            if functions:
                print(f"      Functions: {', '.join(functions)}")
        
        # Test plugin function execution
        print(f"\n🧪 Testing plugin function execution...")
        
        test_file = "test_file.test"
        success_count = 0
        total_count = 0
        
        for plugin_name, plugin_info in plugins_info.items():
            module = plugin_info.get('module')
            if not module:
                continue
                
            # Find all callable functions that don't start with underscore
            functions = []
            for attr_name in dir(module):
                if not attr_name.startswith('_') and callable(getattr(module, attr_name)):
                    attr = getattr(module, attr_name)
                    if attr.__module__ == module.__name__:  # Only functions defined in this module
                        functions.append(attr_name)
            
            # Test each function
            for func_name in functions:
                if func_name == 'get_plugin_metadata':
                    continue
                    
                try:
                    func = getattr(module, func_name)
                    result = func(test_file)
                    
                    if isinstance(result, dict):
                        print(f"   ✅ {plugin_name}.{func_name}() -> {len(result)} fields")
                        success_count += 1
                    else:
                        print(f"   ⚠️  {plugin_name}.{func_name}() -> {type(result)}")
                    
                    total_count += 1
                    
                except Exception as e:
                    print(f"   ❌ {plugin_name}.{func_name}() -> {e}")
                    total_count += 1
        
        # Summary
        print(f"\n📊 Test Results:")
        print(f"   Total functions tested: {total_count}")
        print(f"   Successful executions: {success_count}")
        if total_count > 0:
            success_rate = (success_count / total_count) * 100
            print(f"   Success rate: {success_rate:.1f}%")
        
        if success_count == total_count and total_count > 0:
            print("\n🎉 All tests passed! Plugin system is working correctly.")
            return 0
        else:
            print("\n⚠️  Some tests failed or no functions were tested.")
            return 1
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
