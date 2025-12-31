#!/usr/bin/env python3
"""
Comprehensive tests for the error handling system in the comprehensive metadata engine.
"""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import the functions we want to test
try:
    from server.extractor.comprehensive_metadata_engine import (
        safe_extract_module,
        ComprehensiveMetadataExtractor,
        extract_comprehensive_metadata
    )
except ImportError:
    # Handle different import contexts
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'server', 'extractor'))
    from comprehensive_metadata_engine import (
        safe_extract_module,
        ComprehensiveMetadataExtractor,
        extract_comprehensive_metadata
    )


class TestSafeExtractModule(unittest.TestCase):
    """Test the safe_extract_module function with various error scenarios."""
    
    def test_successful_extraction(self):
        """Test that successful extraction works properly."""
        def mock_extraction_func(filepath, *args, **kwargs):
            return {"data": "success", "file": filepath}
        
        result = safe_extract_module(mock_extraction_func, "/fake/path.jpg", "test_module")
        
        self.assertIsNotNone(result)
        self.assertEqual(result["data"], "success")
        self.assertIn("performance", result)
        self.assertIn("test_module", result["performance"])
        self.assertEqual(result["performance"]["test_module"]["status"], "success")
    
    def test_import_error_handling(self):
        """Test that ImportError is handled properly."""
        def mock_extraction_func(filepath, *args, **kwargs):
            raise ImportError("Module not found")
        
        result = safe_extract_module(mock_extraction_func, "/fake/path.jpg", "test_module")
        
        self.assertIsNotNone(result)
        self.assertFalse(result["available"])
        self.assertEqual(result["error_type"], "ImportError")
        self.assertEqual(result["module"], "test_module")
        self.assertIn("performance", result)
        self.assertIn("test_module", result["performance"])
        self.assertEqual(result["performance"]["test_module"]["status"], "failed")
        self.assertEqual(result["performance"]["test_module"]["error_type"], "ImportError")
    
    def test_file_not_found_error_handling(self):
        """Test that FileNotFoundError is handled properly."""
        def mock_extraction_func(filepath, *args, **kwargs):
            raise FileNotFoundError("File not found")
        
        result = safe_extract_module(mock_extraction_func, "/fake/path.jpg", "test_module")
        
        self.assertIsNotNone(result)
        self.assertFalse(result["available"])
        self.assertEqual(result["error_type"], "FileNotFoundError")
        self.assertEqual(result["module"], "test_module")
        self.assertIn("performance", result)
        self.assertIn("test_module", result["performance"])
        self.assertEqual(result["performance"]["test_module"]["status"], "failed")
        self.assertEqual(result["performance"]["test_module"]["error_type"], "FileNotFoundError")
    
    def test_permission_error_handling(self):
        """Test that PermissionError is handled properly."""
        def mock_extraction_func(filepath, *args, **kwargs):
            raise PermissionError("Permission denied")
        
        result = safe_extract_module(mock_extraction_func, "/fake/path.jpg", "test_module")
        
        self.assertIsNotNone(result)
        self.assertFalse(result["available"])
        self.assertEqual(result["error_type"], "PermissionError")
        self.assertEqual(result["module"], "test_module")
        self.assertIn("performance", result)
        self.assertIn("test_module", result["performance"])
        self.assertEqual(result["performance"]["test_module"]["status"], "failed")
        self.assertEqual(result["performance"]["test_module"]["error_type"], "PermissionError")
    
    def test_generic_exception_handling(self):
        """Test that generic exceptions are handled properly."""
        def mock_extraction_func(filepath, *args, **kwargs):
            raise ValueError("Invalid value")
        
        result = safe_extract_module(mock_extraction_func, "/fake/path.jpg", "test_module")
        
        self.assertIsNotNone(result)
        self.assertFalse(result["available"])
        self.assertEqual(result["error_type"], "ValueError")
        self.assertEqual(result["module"], "test_module")
        self.assertIn("performance", result)
        self.assertIn("test_module", result["performance"])
        self.assertEqual(result["performance"]["test_module"]["status"], "failed")
        self.assertEqual(result["performance"]["test_module"]["error_type"], "ValueError")
    
    def test_extraction_with_args_and_kwargs(self):
        """Test that the function properly passes arguments to the extraction function."""
        def mock_extraction_func(filepath, arg1, kwarg1=None):
            return {"data": f"success with {arg1} and {kwarg1}", "file": filepath}
        
        result = safe_extract_module(
            mock_extraction_func, 
            "/fake/path.jpg", 
            "test_module", 
            "test_arg", 
            kwarg1="test_kwarg"
        )
        
        self.assertIsNotNone(result)
        self.assertIn("success with test_arg and test_kwarg", result["data"])


class TestComprehensiveMetadataExtractor(unittest.TestCase):
    """Test the comprehensive metadata extractor with error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = ComprehensiveMetadataExtractor()
        
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        self.temp_file.write(b"fake image content")
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        try:
            os.unlink(self.temp_file.name)
        except:
            pass
    
    @patch('server.extractor.comprehensive_metadata_engine.extract_base_metadata')
    def test_extraction_with_base_error(self, mock_extract_base):
        """Test that errors in base extraction are handled properly."""
        # Mock should return a result with error but also with extraction_info to avoid the exception
        mock_extract_base.return_value = {
            "error": "Base extraction failed",
            "extraction_info": {"processing_ms": 0}
        }

        result = self.extractor.extract_comprehensive_metadata(self.temp_file.name, "super")

        self.assertIn("error", result)
        self.assertEqual(result["error"], "Base extraction failed")
        self.assertIn("extraction_info", result)
        self.assertIn("processing_ms", result["extraction_info"])
    
    @patch('server.extractor.comprehensive_metadata_engine.extract_base_metadata')
    def test_extraction_with_critical_error(self, mock_extract_base):
        """Test that critical errors in base extraction are handled properly."""
        mock_extract_base.side_effect = Exception("Critical failure")
        
        result = self.extractor.extract_comprehensive_metadata(self.temp_file.name, "super")
        
        self.assertIn("error", result)
        self.assertIn("Critical error in base metadata extraction", result["error"])
        self.assertIn("extraction_info", result)
        self.assertGreaterEqual(result["extraction_info"]["processing_ms"], 0)
    
    def test_extraction_with_nonexistent_file(self):
        """Test extraction with a nonexistent file."""
        result = self.extractor.extract_comprehensive_metadata("/nonexistent/file.jpg", "super")
        
        self.assertIn("error", result)
        self.assertGreaterEqual(result["extraction_info"]["processing_ms"], 0)
    
    @patch('server.extractor.comprehensive_metadata_engine.extract_base_metadata')
    def test_extraction_performance_tracking(self, mock_extract_base):
        """Test that performance tracking works correctly."""
        # Mock a successful base extraction
        mock_extract_base.return_value = {
            "file": {"path": self.temp_file.name, "name": "test.jpg", "extension": ".jpg", "mime_type": "image/jpeg"},
            "summary": {"filename": "test.jpg"},
            "extraction_info": {"timestamp": "2023-01-01T00:00:00", "tier": "super", "engine_version": "4.0.0"}
        }
        
        result = self.extractor.extract_comprehensive_metadata(self.temp_file.name, "super")
        
        # Check that performance metrics are included
        self.assertIn("extraction_info", result)
        self.assertIn("processing_ms", result["extraction_info"])
        self.assertIn("performance_summary", result["extraction_info"])
        self.assertIn("total_processing_time_ms", result["extraction_info"]["performance_summary"])
        self.assertGreaterEqual(result["extraction_info"]["processing_ms"], 0)


class TestExtractComprehensiveMetadata(unittest.TestCase):
    """Test the main extraction function with error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        self.temp_file.write(b"fake image content")
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        try:
            os.unlink(self.temp_file.name)
        except:
            pass
    
    def test_extract_comprehensive_metadata_basic(self):
        """Test basic functionality of the main extraction function."""
        # This test may fail if dependencies aren't installed, so we'll check for expected structure
        result = extract_comprehensive_metadata(self.temp_file.name, "super")
        
        # The result should always be a dictionary
        self.assertIsInstance(result, dict)
        
        # Should always have extraction_info
        self.assertIn("extraction_info", result)
        self.assertIn("comprehensive_version", result["extraction_info"])
        
        # Should have processing time tracking
        self.assertIn("processing_ms", result["extraction_info"])
        
        # Should have performance summary
        self.assertIn("performance_summary", result["extraction_info"])
        self.assertIn("total_processing_time_ms", result["extraction_info"]["performance_summary"])


if __name__ == '__main__':
    unittest.main()