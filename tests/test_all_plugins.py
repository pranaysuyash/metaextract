#!/usr/bin/env python3
"""
Comprehensive test suite for all MetaExtract plugins
"""

import pytest
import tempfile
import os
import sys

# Add project root to path (go up one level from tests/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_plugin_loading():
    """Test that all plugins can be loaded"""
    from server.extractor.module_discovery import (
        enable_plugins_global,
        discover_and_load_plugins_global,
        get_discovered_plugins_global
    )
    
    # Enable and discover plugins
    enable_plugins_global(True)
    discover_and_load_plugins_global()
    
    # Get plugin info
    plugins_info = get_discovered_plugins_global()
    
    # Verify we have plugins
    assert len(plugins_info) > 0, "No plugins found"
    
    # Verify all plugins have required structure
    for plugin_name, plugin_info in plugins_info.items():
        assert "type" in plugin_info
        assert "module" in plugin_info
        assert "functions" in plugin_info
        
        # Verify module is loaded
        module = plugin_info["module"]
        assert module is not None
        
        # Verify functions exist
        functions = plugin_info["functions"]
        assert isinstance(functions, list)
        assert len(functions) > 0
        
        # Verify each function exists in module
        for func_name in functions:
            assert hasattr(module, func_name), f"Function {func_name} not found in {plugin_name}"
            func = getattr(module, func_name)
            assert callable(func), f"{func_name} in {plugin_name} is not callable"


def test_plugin_functions_with_test_files():
    """Test all plugin functions with appropriate test files"""
    from server.extractor.module_discovery import get_discovered_plugins_global
    
    # Get plugin info
    plugins_info = get_discovered_plugins_global()
    
    # Create test files for different types
    test_files = {}
    
    # Audio test file
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
        f.write(b'ID3\x03\x00\x00\x00\x00\x1A' + b'\x00' * 100)
        test_files['audio'] = f.name
    
    # Video test file
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
        f.write(b'\x00\x00\x00\x18ftypmp42' + b'\x00' * 100)
        test_files['video'] = f.name
    
    # Image test file
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        f.write(b'\xFF\xD8\xFF\xE0\x00\x10JFIF' + b'\x00' * 100)
        test_files['image'] = f.name
    
    # Document test file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        f.write(b'%PDF-1.4\n%' + b'\x00' * 100)
        test_files['document'] = f.name
    
    try:
        # Test each plugin with appropriate file
        for plugin_name, plugin_info in plugins_info.items():
            module = plugin_info["module"]
            functions = plugin_info["functions"]
            
            # Determine which test file to use
            test_file = None
            if 'audio' in plugin_name.lower():
                test_file = test_files['audio']
            elif 'video' in plugin_name.lower():
                test_file = test_files['video']
            elif 'image' in plugin_name.lower():
                test_file = test_files['image']
            elif 'document' in plugin_name.lower():
                test_file = test_files['document']
            else:
                # Use audio file as default
                test_file = test_files['audio']
            
            print(f"Testing {plugin_name} with {os.path.basename(test_file)}")
            
            # Test each function
            for func_name in functions:
                if func_name == 'get_plugin_metadata':
                    continue
                
                try:
                    func = getattr(module, func_name)
                    result = func(test_file)
                    
                    # Verify result is a dictionary
                    assert isinstance(result, dict), f"{func_name} returned non-dict"
                    
                    # Verify result has expected structure
                    result_keys = list(result.keys())
                    assert len(result_keys) > 0, f"{func_name} returned empty dict"
                    
                    # Verify processed flag exists
                    for key in result_keys:
                        if isinstance(result[key], dict) and 'processed' in result[key]:
                            assert result[key]['processed'] in [True, False]
                            break
                    
                except Exception as e:
                    pytest.fail(f"Error in {plugin_name}.{func_name}(): {e}")
    
    finally:
        # Clean up test files
        for file_path in test_files.values():
            try:
                os.unlink(file_path)
            except:
                pass


def test_plugin_metadata():
    """Test plugin metadata functions"""
    from server.extractor.module_discovery import get_discovered_plugins_global
    
    # Get plugin info
    plugins_info = get_discovered_plugins_global()
    
    # Test metadata for each plugin
    for plugin_name, plugin_info in plugins_info.items():
        module = plugin_info["module"]
        
        # Check for metadata function
        if hasattr(module, 'get_plugin_metadata'):
            metadata_func = getattr(module, 'get_plugin_metadata')
            
            # Call metadata function
            metadata = metadata_func()
            
            # Verify metadata structure
            assert isinstance(metadata, dict)
            assert "version" in metadata
            assert "author" in metadata
            assert "description" in metadata
            assert "license" in metadata
            
            # Verify metadata values
            assert isinstance(metadata["version"], str)
            assert isinstance(metadata["author"], str)
            assert isinstance(metadata["description"], str)
            assert isinstance(metadata["license"], str)


def test_plugin_integration():
    """Test plugin integration with ComprehensiveMetadataExtractor"""
    from server.extractor.comprehensive_metadata_engine import ComprehensiveMetadataExtractor
    import tempfile
    
    # Create test files
    test_files = {
        'audio': None,
        'video': None,
        'image': None,
        'document': None
    }
    
    try:
        # Create audio test file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(b'ID3\x03\x00\x00\x00\x00\x1A' + b'\x00' * 100)
            test_files['audio'] = f.name
        
        # Create extractor
        extractor = ComprehensiveMetadataExtractor()
        
        # Test with audio file
        result = extractor.extract_comprehensive_metadata(test_files['audio'], "super")
        
        # Verify result contains plugin data
        assert isinstance(result, dict)
        assert len(result) > 0
        
        # Check for plugin results
        plugin_keys = [key for key in result.keys() if any(
            plugin in key for plugin in ['audio', 'video', 'image', 'document', 'example']
        )]
        
        assert len(plugin_keys) > 0, "No plugin results found in extraction"
        
        # Verify plugin results have expected structure
        for key in plugin_keys:
            assert isinstance(result[key], dict)
            if 'processed' in result[key]:
                assert result[key]['processed'] in [True, False]
        
    finally:
        # Clean up
        for file_path in test_files.values():
            if file_path and os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                except:
                    pass


if __name__ == "__main__":
    # Run tests
    test_plugin_loading()
    print("✅ Plugin loading test passed")
    
    test_plugin_functions_with_test_files()
    print("✅ Plugin function test passed")
    
    test_plugin_metadata()
    print("✅ Plugin metadata test passed")
    
    test_plugin_integration()
    print("✅ Plugin integration test passed")
    
    print("\n🎉 All plugin tests passed!")
