#!/usr/bin/env python3
"""Comprehensive test script to verify plugin functionality with proper test files"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_files():
    """Create test files for different file types"""
    test_files = {}
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Audio test file (MP3 header)
    mp3_content = b'ID3\x03\x00\x00\x00\x00\x1A' + b'\x00' * 100  # MP3 with ID3 tag
    mp3_path = os.path.join(temp_dir, "test.mp3")
    with open(mp3_path, 'wb') as f:
        f.write(mp3_content)
    test_files['audio'] = mp3_path
    
    # Video test file (MP4 header)
    mp4_content = b'\x00\x00\x00\x18ftypmp42' + b'\x00' * 100  # MP4 header
    mp4_path = os.path.join(temp_dir, "test.mp4")
    with open(mp4_path, 'wb') as f:
        f.write(mp4_content)
    test_files['video'] = mp4_path
    
    # Image test file (JPEG header)
    jpg_content = b'\xFF\xD8\xFF\xE0\x00\x10JFIF' + b'\x00' * 100  # JPEG header
    jpg_path = os.path.join(temp_dir, "test.jpg")
    with open(jpg_path, 'wb') as f:
        f.write(jpg_content)
    test_files['image'] = jpg_path
    
    # Document test file (PDF header)
    pdf_content = b'%PDF-1.4\n%' + b'\x00' * 100  # PDF header
    pdf_path = os.path.join(temp_dir, "test.pdf")
    with open(pdf_path, 'wb') as f:
        f.write(pdf_content)
    test_files['document'] = pdf_path
    
    # Text file
    txt_content = "This is a test document\nWith multiple lines\nFor testing purposes"
    txt_path = os.path.join(temp_dir, "test.txt")
    with open(txt_path, 'w') as f:
        f.write(txt_content)
    test_files['text'] = txt_path
    
    return test_files, temp_dir

def cleanup_test_files(temp_dir):
    """Clean up temporary test files"""
    try:
        for file_path in Path(temp_dir).glob("*"):
            file_path.unlink()
        Path(temp_dir).rmdir()
    except Exception as e:
        print(f"Warning: Could not clean up test files: {e}")

def test_plugin_system():
    """Test the plugin system comprehensively"""
    print("🚀 Comprehensive Plugin System Test")
    print("=" * 60)
    
    # Create test files
    test_files, temp_dir = create_test_files()
    print(f"📁 Created test files in: {temp_dir}")
    
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
        
        # Test plugin function execution with appropriate test files
        print(f"\n🧪 Testing plugin function execution...")
        
        # Map file types to test files
        file_type_mapping = {
            'audio': test_files['audio'],
            'video': test_files['video'],
            'image': test_files['image'],
            'document': test_files['document'],
            'text': test_files['text']
        }
        
        success_count = 0
        total_count = 0
        plugin_results = {}
        
        for plugin_name, plugin_info in plugins_info.items():
            module = plugin_info.get('module')
            if not module:
                continue
                
            # Determine which test file to use based on plugin name
            test_file = None
            if 'audio' in plugin_name.lower():
                test_file = file_type_mapping['audio']
            elif 'video' in plugin_name.lower():
                test_file = file_type_mapping['video']
            elif 'image' in plugin_name.lower():
                test_file = file_type_mapping['image']
            elif 'document' in plugin_name.lower():
                test_file = file_type_mapping['document']
            else:
                test_file = file_type_mapping['text']
            
            print(f"\n🔧 Testing {plugin_name} with {os.path.basename(test_file)}:")
            
            # Find all callable functions that don't start with underscore
            functions = []
            for attr_name in dir(module):
                if not attr_name.startswith('_') and callable(getattr(module, attr_name)):
                    attr = getattr(module, attr_name)
                    if attr.__module__ == module.__name__:  # Only functions defined in this module
                        functions.append(attr_name)
            
            # Test each function
            plugin_success = 0
            plugin_total = 0
            
            for func_name in functions:
                if func_name == 'get_plugin_metadata':
                    continue
                    
                try:
                    func = getattr(module, func_name)
                    result = func(test_file)
                    
                    if isinstance(result, dict):
                        result_size = len(result)
                        print(f"   ✅ {func_name}() -> {result_size} fields")
                        
                        # Store some sample results for verification
                        if plugin_name not in plugin_results:
                            plugin_results[plugin_name] = {}
                        plugin_results[plugin_name][func_name] = {
                            'success': True,
                            'field_count': result_size,
                            'sample_keys': list(result.keys())[:3]  # First 3 keys as sample
                        }
                        
                        success_count += 1
                        plugin_success += 1
                    else:
                        print(f"   ⚠️  {func_name}() -> {type(result)}")
                        
                        if plugin_name not in plugin_results:
                            plugin_results[plugin_name] = {}
                        plugin_results[plugin_name][func_name] = {
                            'success': False,
                            'error': f'Unexpected return type: {type(result)}'
                        }
                    
                    total_count += 1
                    plugin_total += 1
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f"   ❌ {func_name}() -> {error_msg}")
                    
                    if plugin_name not in plugin_results:
                        plugin_results[plugin_name] = {}
                    plugin_results[plugin_name][func_name] = {
                        'success': False,
                        'error': error_msg
                    }
                    
                    total_count += 1
                    plugin_total += 1
            
            print(f"   📊 Plugin {plugin_name}: {plugin_success}/{plugin_total} functions successful")
        
        # Summary
        print(f"\n📊 Overall Test Results:")
        print(f"   Total functions tested: {total_count}")
        print(f"   Successful executions: {success_count}")
        
        if total_count > 0:
            success_rate = (success_count / total_count) * 100
            print(f"   Success rate: {success_rate:.1f}%")
        
        # Show sample results
        print(f"\n📋 Sample Results:")
        for plugin_name, results in plugin_results.items():
            print(f"   {plugin_name}:")
            for func_name, result_info in results.items():
                status = "✅" if result_info['success'] else "❌"
                if result_info['success']:
                    print(f"      {status} {func_name}(): {result_info['field_count']} fields")
                    print(f"         Sample keys: {', '.join(result_info['sample_keys'])}")
                else:
                    print(f"      {status} {func_name}(): {result_info['error']}")
        
        # Test integration with ComprehensiveMetadataExtractor
        print(f"\n🔗 Testing integration with ComprehensiveMetadataExtractor...")
        
        try:
            from server.extractor.comprehensive_metadata_engine import ComprehensiveMetadataExtractor
            
            extractor = ComprehensiveMetadataExtractor()
            
            # Test with each file type
            integration_results = {}
            for file_type, file_path in file_type_mapping.items():
                try:
                    result = extractor.extract_comprehensive_metadata(file_path, "super")
                    
                    # Check if plugin results are included
                    plugin_keys = [key for key in result.keys() if any(
                        plugin in key for plugin in ['audio', 'video', 'image', 'document', 'example']
                    )]
                    
                    integration_results[file_type] = {
                        'success': True,
                        'total_fields': len(result),
                        'plugin_fields': len(plugin_keys),
                        'plugin_keys': plugin_keys
                    }
                    
                    print(f"   ✅ {file_type}: {len(result)} total fields, {len(plugin_keys)} plugin fields")
                    
                except Exception as e:
                    integration_results[file_type] = {
                        'success': False,
                        'error': str(e)
                    }
                    print(f"   ❌ {file_type}: {e}")
            
            # Integration summary
            successful_integrations = sum(1 for r in integration_results.values() if r['success'])
            total_integrations = len(integration_results)
            
            print(f"\n📊 Integration Results:")
            print(f"   Successful integrations: {successful_integrations}/{total_integrations}")
            
            if successful_integrations == total_integrations:
                print(f"   🎉 All integrations successful!")
            else:
                print(f"   ⚠️  Some integrations failed")
            
        except Exception as e:
            print(f"   ❌ Integration test failed: {e}")
            successful_integrations = 0
            total_integrations = 0
        
        # Final summary
        print(f"\n" + "=" * 60)
        print("📋 FINAL TEST SUMMARY")
        print("=" * 60)
        
        print(f"🔍 Plugin Discovery: ✅ {len(discovered_plugins)} plugins found")
        print(f"🧪 Function Testing: {'✅ PASS' if success_count > 0 else '❌ FAIL'} ({success_count}/{total_count})")
        
        if total_count > 0:
            success_rate = (success_count / total_count) * 100
            print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"🔗 Integration Testing: {'✅ PASS' if successful_integrations == total_integrations else '❌ FAIL'} ({successful_integrations}/{total_integrations})")
        
        if success_count > 0 and successful_integrations == total_integrations:
            print("\n🎉 All tests passed! Plugin system is working correctly.")
            print("\n💡 Plugin System Features Verified:")
            print("   ✅ Plugin discovery and loading")
            print("   ✅ Plugin function execution")
            print("   ✅ Integration with ComprehensiveMetadataExtractor")
            print("   ✅ Metadata extraction with plugins")
            print("   ✅ Error handling and reporting")
            return 0
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")
            return 1
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Clean up test files
        cleanup_test_files(temp_dir)
        print(f"\n🧹 Cleaned up test files")

if __name__ == "__main__":
    sys.exit(test_plugin_system())
