#!/usr/bin/env python3
"""Debug test to identify plugin loading issues"""

import sys
import os
import tempfile

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Debug plugin loading"""
    print("🐞 Debug Plugin Loading Test")
    print("=" * 40)
    
    try:
        # Test 1: Basic import
        print("1. Testing basic imports...")
        from server.extractor.module_discovery import (
            enable_plugins_global,
            discover_and_load_plugins_global,
            get_discovered_plugins_global
        )
        print("   ✅ Imports successful")
        
        # Test 2: Enable plugins
        print("2. Enabling plugins...")
        enable_plugins_global(True)
        print("   ✅ Plugins enabled")
        
        # Test 3: Discover plugins with timing
        print("3. Discovering plugins...")
        import time
        start_time = time.time()
        
        # Just enable and discover, don't load yet
        discover_and_load_plugins_global()
        
        discovery_time = time.time() - start_time
        print(f"   ✅ Discovery completed in {discovery_time:.2f}s")
        
        # Test 4: Get plugin info
        print("4. Getting plugin info...")
        plugins_info = get_discovered_plugins_global()
        print(f"   ✅ Found {len(plugins_info)} plugins")
        
        # Test 5: Test one plugin manually
        print("5. Testing one plugin manually...")
        if plugins_info:
            plugin_name = list(plugins_info.keys())[0]
            plugin_info = plugins_info[plugin_name]
            module = plugin_info.get('module')
            
            print(f"   Testing plugin: {plugin_name}")
            print(f"   Module: {module}")
            print(f"   Module type: {type(module)}")
            
            if module:
                # Test one function
                functions = plugin_info.get('functions', [])
                if functions:
                    func_name = functions[0]
                    print(f"   Testing function: {func_name}")
                    
                    # Create a test file
                    with tempfile.NamedTemporaryFile(suffix='.test', delete=False) as f:
                        f.write(b'test content')
                        test_file = f.name
                    
                    try:
                        func = getattr(module, func_name)
                        start_time = time.time()
                        result = func(test_file)
                        exec_time = time.time() - start_time
                        
                        print(f"   ✅ Function executed in {exec_time:.3f}s")
                        print(f"   Result type: {type(result)}")
                        if isinstance(result, dict):
                            print(f"   Result keys: {list(result.keys())}")
                        
                    except Exception as e:
                        print(f"   ❌ Function error: {e}")
                    finally:
                        os.unlink(test_file)
        
        print("\n✅ Debug test completed successfully")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
