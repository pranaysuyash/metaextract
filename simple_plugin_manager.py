#!/usr/bin/env python3
"""
Simple Plugin Manager for MetaExtract
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🚀 Simple Plugin Manager")
    print("=" * 40)
    
    try:
        # Import MetaExtract modules
        from server.extractor.module_discovery import (
            enable_plugins_global,
            discover_and_load_plugins_global,
            get_discovered_plugins_global
        )
        
        print("✅ Successfully imported MetaExtract modules")
        
        # Enable and discover plugins
        enable_plugins_global(True)
        discover_and_load_plugins_global()
        
        # Get plugin info
        plugins_info = get_discovered_plugins_global()
        
        print(f"📊 Found {len(plugins_info)} plugins/modules:")
        
        for i, (plugin_name, plugin_info) in enumerate(plugins_info.items(), 1):
            plugin_type = plugin_info.get('type', 'unknown')
            functions = plugin_info.get('functions', [])
            enabled = plugin_info.get('enabled', True)
            
            print(f"{i}. {plugin_name} ({plugin_type})")
            print(f"   Status: {'✅ Enabled' if enabled else '❌ Disabled'}")
            print(f"   Functions: {len(functions)}")
            
            if plugin_type == 'plugin':
                metadata = plugin_info.get('metadata', {})
                version = metadata.get('version', 'N/A')
                author = metadata.get('author', 'N/A')
                print(f"   Version: {version}, Author: {author}")
            
            print()
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
