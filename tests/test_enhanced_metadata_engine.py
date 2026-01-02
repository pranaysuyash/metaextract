"""
Unit tests for the enhanced metadata engine.

These tests verify the functionality of the enhanced metadata extraction engine,
including error handling, logging, async operations, and various extraction scenarios.
"""

import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from server.extractor.metadata_engine_enhanced import (
    extract_metadata_enhanced,
    extract_batch_metadata,
    extract_metadata_enhanced_async,
    extract_batch_metadata_async,
    EnhancedMetadataExtractor,
    get_enhanced_extractor
)


def test_enhanced_extractor_initialization():
    """Test that the enhanced extractor initializes correctly."""
    extractor = EnhancedMetadataExtractor()
    
    assert extractor is not None
    assert hasattr(extractor, 'extract_metadata')
    assert hasattr(extractor, 'extract_batch')
    assert extractor.max_workers == 4


def test_get_enhanced_extractor_singleton():
    """Test that get_enhanced_extractor returns the same instance."""
    extractor1 = get_enhanced_extractor()
    extractor2 = get_enhanced_extractor()
    
    assert extractor1 is extractor2


@patch('server.extractor.metadata_engine_enhanced.extract_comprehensive_metadata')
def test_extract_metadata_success(mock_extract_comprehensive):
    """Test successful enhanced metadata extraction."""
    mock_extract_comprehensive.return_value = {
        "file": {"path": "/fake/path.jpg"},
        "extraction_info": {"engine_version": "4.0.0"}
    }
    
    extractor = EnhancedMetadataExtractor()
    result = extractor.extract_metadata("/fake/path.jpg", "super")
    
    assert result is not None
    assert "file" in result
    assert result["file"]["path"] == "/fake/path.jpg"
    assert "extraction_info" in result
    assert result["extraction_info"]["engine_version"] == "4.0.0"
    mock_extract_comprehensive.assert_called_once_with("/fake/path.jpg", "super")


@patch('server.extractor.metadata_engine_enhanced.extract_comprehensive_metadata')
def test_extract_metadata_with_error(mock_extract_comprehensive):
    """Test enhanced metadata extraction with error."""
    mock_extract_comprehensive.return_value = {
        "error": "Test error",
        "file": {"path": "/fake/path.jpg"}
    }
    
    extractor = EnhancedMetadataExtractor()
    result = extractor.extract_metadata("/fake/path.jpg", "super")
    
    assert result is not None
    assert "error" in result
    assert result["error"] == "Test error"


@patch('server.extractor.metadata_engine_enhanced.extract_comprehensive_metadata')
def test_extract_metadata_exception_handling(mock_extract_comprehensive):
    """Test enhanced metadata extraction handles exceptions."""
    mock_extract_comprehensive.side_effect = Exception("Test exception")
    
    extractor = EnhancedMetadataExtractor()
    result = extractor.extract_metadata("/fake/path.jpg", "super")
    
    assert result is not None
    assert "error" in result
    assert "Critical error in enhanced metadata extraction" in result["error"]


def test_extract_metadata_with_nonexistent_file():
    """Test extraction with a non-existent file."""
    extractor = EnhancedMetadataExtractor()
    result = extractor.extract_metadata("/nonexistent/file.jpg", "super")
    
    assert result is not None
    assert "error" in result


@patch('server.extractor.metadata_engine_enhanced.extract_comprehensive_metadata')
@pytest.mark.asyncio
async def test_extract_metadata_enhanced_async_success(mock_extract_comprehensive):
    """Test successful async enhanced metadata extraction."""
    mock_extract_comprehensive.return_value = {
        "file": {"path": "/fake/path.jpg"},
        "extraction_info": {"engine_version": "4.0.0"}
    }
    
    result = await extract_metadata_enhanced_async("/fake/path.jpg", "super")
    
    assert result is not None
    assert "file" in result
    assert result["file"]["path"] == "/fake/path.jpg"
    assert "extraction_info" in result
    assert result["extraction_info"]["engine_version"] == "4.0.0"


@patch('server.extractor.metadata_engine_enhanced.extract_comprehensive_metadata')
@pytest.mark.asyncio
async def test_extract_metadata_enhanced_async_with_error(mock_extract_comprehensive):
    """Test async enhanced metadata extraction with error."""
    mock_extract_comprehensive.return_value = {
        "error": "Test error",
        "file": {"path": "/fake/path.jpg"}
    }
    
    result = await extract_metadata_enhanced_async("/fake/path.jpg", "super")
    
    assert result is not None
    assert "error" in result
    assert result["error"] == "Test error"


@patch('server.extractor.metadata_engine_enhanced.extract_comprehensive_metadata')
@pytest.mark.asyncio
async def test_extract_metadata_enhanced_async_exception_handling(mock_extract_comprehensive):
    """Test async enhanced metadata extraction handles exceptions."""
    mock_extract_comprehensive.side_effect = Exception("Test exception")
    
    result = await extract_metadata_enhanced_async("/fake/path.jpg", "super")
    
    assert result is not None
    assert "error" in result
    assert "Critical error in async enhanced metadata extraction" in result["error"]


@pytest.mark.asyncio
async def test_extract_metadata_enhanced_async_nonexistent_file():
    """Test async extraction with a non-existent file."""
    result = await extract_metadata_enhanced_async("/nonexistent/file.jpg", "super")
    
    assert result is not None
    assert "error" in result


def test_extract_batch_metadata_success():
    """Test successful batch metadata extraction."""
    # Create temporary files for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some dummy files
        file1 = os.path.join(temp_dir, "file1.jpg")
        file2 = os.path.join(temp_dir, "file2.jpg")
        
        with open(file1, 'w') as f:
            f.write("dummy content")
        with open(file2, 'w') as f:
            f.write("dummy content")
        
        # Mock the extraction function to avoid actual metadata extraction
        with patch('server.extractor.metadata_engine_enhanced.extract_comprehensive_metadata') as mock_extract:
            mock_extract.return_value = {
                "file": {"path": file1},
                "extraction_info": {"engine_version": "4.0.0"}
            }
            
            result = asyncio.run(extract_batch_metadata([file1, file2], "super"))
            
            assert result is not None
            assert "summary" in result
            assert result["summary"]["total_files"] == 2
            assert result["summary"]["successful"] == 2
            assert result["summary"]["failed"] == 0


def test_extract_batch_metadata_with_errors():
    """Test batch metadata extraction with some errors."""
    # Create temporary files for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some dummy files
        file1 = os.path.join(temp_dir, "file1.jpg")
        file2 = os.path.join(temp_dir, "file2.jpg")
        
        with open(file1, 'w') as f:
            f.write("dummy content")
        with open(file2, 'w') as f:
            f.write("dummy content")
        
        # Mock the extraction function to simulate one success and one failure
        with patch('server.extractor.metadata_engine_enhanced.extract_comprehensive_metadata') as mock_extract:
            def side_effect(filepath, tier):
                if filepath == file1:
                    return {
                        "file": {"path": filepath},
                        "extraction_info": {"engine_version": "4.0.0"}
                    }
                else:
                    return {
                        "error": "Test error",
                        "file": {"path": filepath}
                    }
            
            mock_extract.side_effect = side_effect
            
            result = asyncio.run(extract_batch_metadata([file1, file2], "super"))
            
            assert result is not None
            assert "summary" in result
            assert result["summary"]["total_files"] == 2
            assert result["summary"]["successful"] == 1
            assert result["summary"]["failed"] == 1


@pytest.mark.asyncio
async def test_extract_batch_metadata_async_success():
    """Test successful async batch metadata extraction."""
    # Create temporary files for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some dummy files
        file1 = os.path.join(temp_dir, "file1.jpg")
        file2 = os.path.join(temp_dir, "file2.jpg")
        
        with open(file1, 'w') as f:
            f.write("dummy content")
        with open(file2, 'w') as f:
            f.write("dummy content")
        
        # Mock the extraction function to avoid actual metadata extraction
        with patch('server.extractor.metadata_engine_enhanced.extract_comprehensive_metadata') as mock_extract:
            mock_extract.return_value = {
                "file": {"path": file1},
                "extraction_info": {"engine_version": "4.0.0"}
            }
            
            result = await extract_batch_metadata_async([file1, file2], "super")
            
            assert result is not None
            assert "summary" in result
            assert result["summary"]["total_files"] == 2
            assert result["summary"]["successful"] == 2
            assert result["summary"]["failed"] == 0


@pytest.mark.asyncio
async def test_extract_batch_metadata_async_with_errors():
    """Test async batch metadata extraction with some errors."""
    # Create temporary files for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some dummy files
        file1 = os.path.join(temp_dir, "file1.jpg")
        file2 = os.path.join(temp_dir, "file2.jpg")
        
        with open(file1, 'w') as f:
            f.write("dummy content")
        with open(file2, 'w') as f:
            f.write("dummy content")
        
        # Mock the extraction function to simulate one success and one failure
        with patch('server.extractor.metadata_engine_enhanced.extract_comprehensive_metadata') as mock_extract:
            def side_effect(filepath, tier):
                if filepath == file1:
                    return {
                        "file": {"path": filepath},
                        "extraction_info": {"engine_version": "4.0.0"}
                    }
                else:
                    return {
                        "error": "Test error",
                        "file": {"path": filepath}
                    }
            
            mock_extract.side_effect = side_effect
            
            result = await extract_batch_metadata_async([file1, file2], "super")
            
            assert result is not None
            assert "summary" in result
            assert result["summary"]["total_files"] == 2
            assert result["summary"]["successful"] == 1
            assert result["summary"]["failed"] == 1


@pytest.mark.asyncio
async def test_extract_batch_metadata_async_exception_handling():
    """Test async batch metadata extraction handles exceptions."""
    with patch('server.extractor.metadata_engine_enhanced.get_enhanced_extractor') as mock_get_extractor:
        mock_extractor = Mock()
        mock_extractor.extract_batch.side_effect = Exception("Test exception")
        mock_get_extractor.return_value = mock_extractor
        
        result = await extract_batch_metadata_async(["/fake/path1.jpg", "/fake/path2.jpg"], "super")
        
        assert result is not None
        assert "error" in result
        assert "Critical error in async batch metadata extraction" in result["error"]
        assert result["error_type"] == "Exception"
        assert result["summary"]["total_files"] == 2
        assert result["summary"]["successful"] == 0
        assert result["summary"]["failed"] == 2


def test_enhanced_extractor_with_advanced_analysis():
    """Test enhanced extractor with advanced analysis enabled."""
    with patch('server.extractor.metadata_engine_enhanced.extract_comprehensive_metadata') as mock_extract:
        mock_extract.return_value = {
            "file": {"path": "/fake/path.jpg"},
            "extraction_info": {"engine_version": "4.0.0"}
        }
        
        extractor = EnhancedMetadataExtractor()
        result = extractor.extract_metadata("/fake/path.jpg", "super", enable_advanced_analysis=True)
        
        assert result is not None
        assert "file" in result
        assert result["file"]["path"] == "/fake/path.jpg"


@pytest.mark.asyncio
async def test_extract_metadata_enhanced_async_with_advanced_analysis():
    """Test async enhanced extraction with advanced analysis."""
    with patch('server.extractor.metadata_engine_enhanced.extract_comprehensive_metadata') as mock_extract:
        mock_extract.return_value = {
            "file": {"path": "/fake/path.jpg"},
            "extraction_info": {"engine_version": "4.0.0"}
        }
        
        result = await extract_metadata_enhanced_async("/fake/path.jpg", "super", enable_advanced_analysis=True)
        
        assert result is not None
        assert "file" in result
        assert result["file"]["path"] == "/fake/path.jpg"


def test_enhanced_extractor_performance_metrics():
    """Test enhanced extractor with performance metrics enabled."""
    with patch('server.extractor.metadata_engine_enhanced.extract_comprehensive_metadata') as mock_extract:
        mock_extract.return_value = {
            "file": {"path": "/fake/path.jpg"},
            "extraction_info": {"engine_version": "4.0.0"}
        }
        
        extractor = EnhancedMetadataExtractor()
        result = extractor.extract_metadata("/fake/path.jpg", "super", include_performance_metrics=True)
        
        assert result is not None
        assert "file" in result
        assert result["file"]["path"] == "/fake/path.jpg"


@pytest.mark.asyncio
async def test_extract_batch_metadata_async_empty_list():
    """Test async batch extraction with an empty file list."""
    result = await extract_batch_metadata_async([], "super")
    
    assert result is not None
    assert "summary" in result
    assert result["summary"]["total_files"] == 0
    assert result["summary"]["successful"] == 0
    assert result["summary"]["failed"] == 0


def test_extract_batch_metadata_empty_list():
    """Test batch extraction with an empty file list."""
    result = asyncio.run(extract_batch_metadata([], "super"))
    
    assert result is not None
    assert "summary" in result
    assert result["summary"]["total_files"] == 0
    assert result["summary"]["successful"] == 0
    assert result["summary"]["failed"] == 0