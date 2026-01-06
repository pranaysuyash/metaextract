#!/usr/bin/env python3
"""
Test script for enhanced module discovery system.
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
    print("✅ Successfully imported module discovery components")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running this from the project root directory")
    sys.exit(1)


def test_module_discovery_basic():
    """Test basic module discovery functionality."""
    print("\n🧪 Testing Basic Module Discovery...")
    
    try:
        registry = ModuleRegistry()
        
        # Test with non-existent directory
        try:
            registry.discover_modules("/path/to/nonexistent/directory")
            print("❌ Expected ConfigurationError for non-existent directory")
            return False
        except ConfigurationError as e:
            print(f"✅ Correctly raised ConfigurationError: {e.message}")
            return True
        except Exception as e:
            print(f"❌ Unexpected exception type: {type(e).__name__}: {e}")
            return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        traceback.print_exc()
        return False


def test_module_discovery_with_valid_directory():
    """Test module discovery with a valid directory."""
    print("\n🧪 Testing Module Discovery with Valid Directory...")
    
    # Create a temporary directory with a test module
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a simple test module
        test_module_content = '''
def extract_test_metadata(filepath: str) -> dict:
    """Test extraction function."""
    return {"test": "data", "filepath": filepath}

def analyze_test_content(filepath: str) -> dict:
    """Test analysis function."""
    return {"analysis": "result"}

MODULE_DEPENDENCIES = []
'''
        
        test_module_path = Path(temp_dir) / "test_module.py"
        with open(test_module_path, 'w') as f:
            f.write(test_module_content)
        
        try:
            registry = ModuleRegistry()
            registry.discover_modules(temp_dir)
            
            if registry.discovered_count == 1:
                print(f"✅ Successfully discovered {registry.discovered_count} module")
                if registry.loaded_count == 1:
                    print(f"✅ Successfully loaded {registry.loaded_count} module")
                    
                    # Check if the module was registered correctly
                    if "test_module" in registry.modules:
                        module_info = registry.modules["test_module"]
                        functions = module_info["functions"]
                        
                        if len(functions) == 2:
                            print(f"✅ Found {len(functions)} extraction functions")
                            print(f"   Functions: {list(functions.keys())}")
                            return True
                        else:
                            print(f"❌ Expected 2 functions but found {len(functions)}")
                            return False
                    else:
                        print("❌ Module not found in registry")
                        return False
                else:
                    print(f"❌ Expected 1 loaded module but got {registry.loaded_count}")
                    return False
            else:
                print(f"❌ Expected 1 discovered module but got {registry.discovered_count}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            traceback.print_exc()
            return False


def test_module_discovery_with_dependencies():
    """Test module discovery with dependencies."""
    print("\n🧪 Testing Module Discovery with Dependencies...")
    
    # Create a temporary directory with a test module that has dependencies
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test module with dependencies that fail at import time
        test_module_content = '''
# This will cause an ImportError at module load time
import nonexistent_library

def extract_test_metadata(filepath: str) -> dict:
    """Test extraction function."""
    return {"test": "data"}

MODULE_DEPENDENCIES = ["nonexistent_library"]
'''
        
        test_module_path = Path(temp_dir) / "test_dep_module.py"
        with open(test_module_path, 'w') as f:
            f.write(test_module_content)
        
        try:
            registry = ModuleRegistry()
            registry.discover_modules(temp_dir)
            
            if registry.discovered_count == 1:
                print(f"✅ Successfully discovered {registry.discovered_count} module")
                
                # The module should either fail to load or be disabled due to missing dependency
                if registry.failed_count >= 1 or "test_dep_module" in registry.disabled_modules:
                    print(f"✅ Correctly handled missing dependency (failed: {registry.failed_count}, disabled: {len(registry.disabled_modules)})")
                    
                    # Check if the module was disabled
                    if "test_dep_module" in registry.disabled_modules:
                        print("✅ Module correctly added to disabled modules list")
                    
                    # Check if dependency was detected
                    if "test_dep_module" in registry.module_dependencies:
                        deps = registry.module_dependencies["test_dep_module"]
                        print(f"✅ Dependencies detected: {deps}")
                    
                    return True
                else:
                    print(f"❌ Expected module to fail or be disabled due to missing dependency")
                    print(f"   Failed count: {registry.failed_count}")
                    print(f"   Disabled modules: {list(registry.disabled_modules)}")
                    return False
            else:
                print(f"❌ Expected 1 discovered module but got {registry.discovered_count}")
                return False
                
        except DependencyError as e:
            print(f"✅ Correctly raised DependencyError: {e.message}")
            print(f"   Missing dependency: {e.context.get('missing_dependency')}")
            return True
        except Exception as e:
            print(f"❌ Unexpected exception: {type(e).__name__}: {e}")
            traceback.print_exc()
            return False


def test_module_discovery_error_handling():
    """Test error handling in module discovery."""
    print("\n🧪 Testing Module Discovery Error Handling...")
    
    try:
        registry = ModuleRegistry()
        
        # Test various error conditions
        error_cases = [
            ("", "empty path"),
            (None, "None path"),
            ("/path/to/nonexistent", "non-existent path"),
            ("/etc/passwd", "file instead of directory")
        ]
        
        for path, description in error_cases:
            try:
                registry.discover_modules(path)
                print(f"❌ Expected error for {description} but succeeded")
                return False
            except (ConfigurationError, Exception) as e:
                print(f"✅ Correctly handled {description}: {type(e).__name__}")
            
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all module discovery tests."""
    print("🚀 Starting Enhanced Module Discovery Tests")
    print("=" * 50)
    
    tests = [
        test_module_discovery_basic,
        test_module_discovery_with_valid_directory,
        test_module_discovery_with_dependencies,
        test_module_discovery_error_handling
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
        print("🎉 All tests passed! Module discovery is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)