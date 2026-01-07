#!/usr/bin/env python3
"""
Test script for enhanced error handling in the metadata extraction engine.
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path


# Add the project root to sys.path for absolute imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from server.extractor.core.base_engine import BaseExtractor, SpecializedExtractor, ExtractionContext, ExtractionStatus
    from server.extractor.exceptions.extraction_exceptions import (
        MetaExtractException, 
        ExtractionFailedError, 
        FileNotSupportedError,
        DependencyError,
        FileAccessError,
        ValidationError
    )
    print("✅ Successfully imported all required modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running this from the project root directory")
    raise


def test_basic_error_handling():
    """Test basic error handling in BaseExtractor."""
    print("\n🧪 Testing Basic Error Handling...")
    
    class TestExtractor(BaseExtractor):
        def __init__(self):
            super().__init__("TestExtractor", [".txt"])
        
        def _extract_metadata(self, context):
            # Simulate an extraction error
            raise ValueError("Simulated extraction error")
    
    extractor = TestExtractor()
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("test content")
        temp_file = f.name
    
    try:
        context = ExtractionContext(
            filepath=temp_file,
            file_size=os.path.getsize(temp_file),
            file_extension=".txt",
            mime_type="text/plain",
            tier="free",
            processing_options={},
            execution_stats={}
        )
        
        # This should raise an ExtractionFailedError
        try:
            result = extractor.extract(context)
            print(f"❌ Expected exception but got result: {result.status}")
            return False
        except ExtractionFailedError as e:
            print(f"✅ Correctly raised ExtractionFailedError: {e.message}")
            print(f"   Error code: {e.error_code}")
            print(f"   Context: {e.context}")
            return True
        except Exception as e:
            print(f"❌ Unexpected exception type: {type(e).__name__}: {e}")
            return False
    finally:
        os.unlink(temp_file)


def test_file_not_found():
    """Test FileNotFoundError handling."""
    print("\n🧪 Testing File Not Found Handling...")
    
    class TestExtractor(BaseExtractor):
        def __init__(self):
            super().__init__("TestExtractor", [".txt"])
        
        def _extract_metadata(self, context):
            return {"test": "data"}
    
    extractor = TestExtractor()
    
    # Non-existent file
    fake_file = "/path/to/nonexistent/file.txt"
    
    context = ExtractionContext(
        filepath=fake_file,
        file_size=100,
        file_extension=".txt",
        mime_type="text/plain",
        tier="free",
        processing_options={},
        execution_stats={}
    )
    
    try:
        result = extractor.extract(context)
        print(f"❌ Expected exception but got result: {result.status}")
        return False
    except FileAccessError as e:
        print(f"✅ Correctly raised FileAccessError: {e.message}")
        print(f"   Error code: {e.error_code}")
        print(f"   Filepath: {e.context.get('filepath')}")
        return True
    except Exception as e:
        print(f"❌ Unexpected exception type: {type(e).__name__}: {e}")
        return False


def test_file_not_supported():
    """Test FileNotSupportedError handling."""
    print("\n🧪 Testing File Not Supported Handling...")
    
    class TestExtractor(BaseExtractor):
        def __init__(self):
            super().__init__("TestExtractor", [".txt"])  # Only supports .txt
        
        def _extract_metadata(self, context):
            return {"test": "data"}
    
    extractor = TestExtractor()
    
    # Create a temporary file with unsupported extension
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{"test": "data"}')
        temp_file = f.name
    
    try:
        context = ExtractionContext(
            filepath=temp_file,
            file_size=os.path.getsize(temp_file),
            file_extension=".json",
            mime_type="application/json",
            tier="free",
            processing_options={},
            execution_stats={}
        )
        
        try:
            result = extractor.extract(context)
            print(f"❌ Expected exception but got result: {result.status}")
            return False
        except FileNotSupportedError as e:
            print(f"✅ Correctly raised FileNotSupportedError: {e.message}")
            print(f"   Error code: {e.error_code}")
            print(f"   File format: {e.context.get('file_format')}")
            return True
        except Exception as e:
            print(f"❌ Unexpected exception type: {type(e).__name__}: {e}")
            return False
    finally:
        os.unlink(temp_file)


def test_specialized_extractor_dependencies():
    """Test dependency handling in SpecializedExtractor."""
    print("\n🧪 Testing Specialized Extractor Dependency Handling...")
    
    # Create a concrete implementation of SpecializedExtractor
    class TestSpecializedExtractor(SpecializedExtractor):
        def __init__(self):
            super().__init__(
                name="TestSpecializedExtractor",
                domain="test",
                required_libraries=["nonexistent_library_12345"]
            )
        
        def _extract_metadata(self, context):
            return {"test": "data"}
    
    try:
        # This should raise DependencyError for non-existent library
        extractor = TestSpecializedExtractor()
        print("❌ Expected DependencyError during initialization")
        return False
    except DependencyError as e:
        print(f"✅ Correctly raised DependencyError: {e.message}")
        print(f"   Error code: {e.error_code}")
        print(f"   Missing dependency: {e.context.get('missing_dependency')}")
        return True
    except Exception as e:
        print(f"❌ Unexpected exception type: {type(e).__name__}: {e}")
        return False


def test_successful_extraction():
    """Test successful extraction scenario."""
    print("\n🧪 Testing Successful Extraction...")
    
    class TestExtractor(BaseExtractor):
        def __init__(self):
            super().__init__("TestExtractor", [".txt"])
        
        def _extract_metadata(self, context):
            return {
                "filename": context.filepath,
                "size": context.file_size,
                "extension": context.file_extension
            }
    
    extractor = TestExtractor()
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("test content")
        temp_file = f.name
    
    try:
        context = ExtractionContext(
            filepath=temp_file,
            file_size=os.path.getsize(temp_file),
            file_extension=".txt",
            mime_type="text/plain",
            tier="free",
            processing_options={},
            execution_stats={}
        )
        
        result = extractor.extract(context)
        
        if result.status == ExtractionStatus.SUCCESS:
            print(f"✅ Successful extraction: {result.status}")
            print(f"   Metadata keys: {list(result.metadata.keys())}")
            print(f"   Processing time: {result.processing_time_ms:.2f}ms")
            return True
        else:
            print(f"❌ Expected SUCCESS but got: {result.status}")
            print(f"   Error: {result.error_message}")
            return False
    finally:
        os.unlink(temp_file)


def main():
    """Run all error handling tests."""
    print("🚀 Starting Enhanced Error Handling Tests")
    print("=" * 50)
    
    tests = [
        test_basic_error_handling,
        test_file_not_found,
        test_file_not_supported,
        test_specialized_extractor_dependencies,
        test_successful_extraction
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
        print("🎉 All tests passed! Error handling is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)