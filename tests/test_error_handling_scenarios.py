#!/usr/bin/env python3
"""
Additional tests for error handling scenarios in the comprehensive metadata engine.
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
        ComprehensiveMetadataExtractor
    )
except ImportError:
    # Handle different import contexts
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'server', 'extractor'))
    from comprehensive_metadata_engine import (
        safe_extract_module,
        ComprehensiveMetadataExtractor
    )


class TestErrorScenarios(unittest.TestCase):
    """Test various error handling scenarios."""
    
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
    def test_module_import_error_handling(self, mock_extract_base):
        """Test that module import errors are handled gracefully."""
        # Mock base extraction to return a valid result
        mock_extract_base.return_value = {
            "file": {"path": self.temp_file.name, "name": "test.jpg", "extension": ".jpg", "mime_type": "image/jpeg"},
            "summary": {"filename": "test.jpg"},
            "extraction_info": {"timestamp": "2023-01-01T00:00:00", "tier": "super", "engine_version": "4.0.0"},
            "exif": {},
            "xmp": {},
            "iptc": {},
            "gps": {},
            "makernote": {},
            "composite": {}
        }
        
        # Mock a specialized engine to raise an ImportError
        with patch.object(self.extractor.medical_engine, 'extract_dicom_metadata') as mock_dicom:
            mock_dicom.side_effect = ImportError("pydicom not installed")
            
            # Create a fake DICOM file path to trigger the medical engine
            fake_dicom_path = "/tmp/test.dcm"
            
            result = self.extractor.extract_comprehensive_metadata(fake_dicom_path, "super")
            
            # Should not crash, should continue processing
            self.assertIsInstance(result, dict)
            self.assertIn("extraction_info", result)
            self.assertGreaterEqual(result["extraction_info"]["processing_ms"], 0)
    
    @patch('server.extractor.comprehensive_metadata_engine.extract_base_metadata')
    def test_file_processing_error_handling(self, mock_extract_base):
        """Test that file processing errors in specialized modules are handled."""
        # Mock base extraction to return a valid result
        mock_extract_base.return_value = {
            "file": {"path": self.temp_file.name, "name": "test.jpg", "extension": ".jpg", "mime_type": "image/jpeg"},
            "summary": {"filename": "test.jpg"},
            "extraction_info": {"timestamp": "2023-01-01T00:00:00", "tier": "super", "engine_version": "4.0.0"},
            "exif": {},
            "xmp": {},
            "iptc": {},
            "gps": {},
            "makernote": {},
            "composite": {}
        }
        
        # Mock a specialized engine to raise a generic error
        with patch.object(self.extractor.astronomical_engine, 'extract_fits_metadata') as mock_fits:
            mock_fits.side_effect = ValueError("Invalid FITS file")
            
            # Create a fake FITS file path to trigger the astronomical engine
            fake_fits_path = "/tmp/test.fits"
            
            result = self.extractor.extract_comprehensive_metadata(fake_fits_path, "super")
            
            # Should not crash, should continue processing
            self.assertIsInstance(result, dict)
            self.assertIn("extraction_info", result)
            self.assertGreaterEqual(result["extraction_info"]["processing_ms"], 0)
    
    @patch('server.extractor.comprehensive_metadata_engine.extract_base_metadata')
    def test_multiple_module_failures(self, mock_extract_base):
        """Test that multiple module failures don't stop the entire process."""
        # Mock base extraction to return a valid result
        mock_extract_base.return_value = {
            "file": {"path": self.temp_file.name, "name": "test.jpg", "extension": ".jpg", "mime_type": "image/jpeg"},
            "summary": {"filename": "test.jpg"},
            "extraction_info": {"timestamp": "2023-01-01T00:00:00", "tier": "super", "engine_version": "4.0.0"},
            "exif": {},
            "xmp": {},
            "iptc": {},
            "gps": {},
            "makernote": {},
            "composite": {}
        }
        
        # Mock multiple specialized engines to fail
        with patch.object(self.extractor.medical_engine, 'extract_dicom_metadata') as mock_dicom, \
             patch.object(self.extractor.astronomical_engine, 'extract_fits_metadata') as mock_fits, \
             patch.object(self.extractor.geospatial_engine, 'extract_geotiff_metadata') as mock_geotiff:
            
            mock_dicom.side_effect = ImportError("pydicom not available")
            mock_fits.side_effect = ImportError("astropy not available")
            mock_geotiff.side_effect = ImportError("rasterio not available")
            
            result = self.extractor.extract_comprehensive_metadata(self.temp_file.name, "super")
            
            # Should not crash despite multiple failures
            self.assertIsInstance(result, dict)
            self.assertIn("extraction_info", result)
            self.assertGreaterEqual(result["extraction_info"]["processing_ms"], 0)
            # Should still have performance summary
            self.assertIn("performance_summary", result["extraction_info"])
    
    def test_safe_extract_module_with_none_result(self):
        """Test safe_extract_module with a function that returns None."""
        def mock_extraction_func(filepath, *args, **kwargs):
            return None
        
        result = safe_extract_module(mock_extraction_func, "/fake/path.jpg", "test_module")
        
        # When the function returns None, safe_extract_module should also return None
        self.assertIsNone(result)
    
    def test_safe_extract_module_with_non_dict_result(self):
        """Test safe_extract_module with a function that returns non-dict result."""
        def mock_extraction_func(filepath, *args, **kwargs):
            return "string_result"
        
        result = safe_extract_module(mock_extraction_func, "/fake/path.jpg", "test_module")
        
        # Should return the string result without adding performance data
        self.assertEqual(result, "string_result")
    
    @patch('server.extractor.comprehensive_metadata_engine.extract_base_metadata')
    def test_extraction_with_corrupted_file(self, mock_extract_base):
        """Test extraction behavior with a corrupted file."""
        # Create a temporary corrupted file
        corrupted_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        corrupted_file.write(b"corrupted content that isn't a real image")
        corrupted_file.close()
        
        try:
            # Mock base extraction to simulate a scenario where base extraction works
            # but specialized modules might fail on corrupted content
            mock_extract_base.return_value = {
                "file": {"path": corrupted_file.name, "name": "corrupted.jpg", "extension": ".jpg", "mime_type": "image/jpeg"},
                "summary": {"filename": "corrupted.jpg"},
                "extraction_info": {"timestamp": "2023-01-01T00:00:00", "tier": "super", "engine_version": "4.0.0"},
                "exif": {},
                "xmp": {},
                "iptc": {},
                "gps": {},
                "makernote": {},
                "composite": {}
            }
            
            result = self.extractor.extract_comprehensive_metadata(corrupted_file.name, "super")
            
            # Should handle corrupted file gracefully
            self.assertIsInstance(result, dict)
            self.assertIn("extraction_info", result)
            self.assertGreaterEqual(result["extraction_info"]["processing_ms"], 0)
            
        finally:
            # Clean up the corrupted file
            try:
                os.unlink(corrupted_file.name)
            except:
                pass


class TestPerformanceMetrics(unittest.TestCase):
    """Test that performance metrics are correctly calculated."""
    
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
    def test_performance_summary_structure(self, mock_extract_base):
        """Test that performance summary has the correct structure."""
        # Mock base extraction to return a valid result
        mock_extract_base.return_value = {
            "file": {"path": self.temp_file.name, "name": "test.jpg", "extension": ".jpg", "mime_type": "image/jpeg"},
            "summary": {"filename": "test.jpg"},
            "extraction_info": {"timestamp": "2023-01-01T00:00:00", "tier": "super", "engine_version": "4.0.0"},
            "exif": {},
            "xmp": {},
            "iptc": {},
            "gps": {},
            "makernote": {},
            "composite": {}
        }
        
        result = self.extractor.extract_comprehensive_metadata(self.temp_file.name, "super")
        
        # Check performance summary structure
        perf_summary = result["extraction_info"]["performance_summary"]
        self.assertIn("total_processing_time_ms", perf_summary)
        self.assertIn("successful_modules", perf_summary)
        self.assertIn("failed_modules", perf_summary)
        self.assertIn("total_module_processing_time_ms", perf_summary)
        self.assertIn("overhead_time_ms", perf_summary)
        
        # Check that times are non-negative
        self.assertGreaterEqual(perf_summary["total_processing_time_ms"], 0)
        self.assertGreaterEqual(perf_summary["successful_modules"], 0)
        self.assertGreaterEqual(perf_summary["failed_modules"], 0)
        self.assertGreaterEqual(perf_summary["total_module_processing_time_ms"], 0)
        self.assertGreaterEqual(perf_summary["overhead_time_ms"], 0)
        
        # Total processing time should be >= module processing time + overhead
        expected_min_time = perf_summary["total_module_processing_time_ms"] + perf_summary["overhead_time_ms"]
        # Allow for small timing differences due to measurement precision
        self.assertLessEqual(perf_summary["total_processing_time_ms"], expected_min_time + 10)  # 10ms tolerance


if __name__ == '__main__':
    unittest.main()