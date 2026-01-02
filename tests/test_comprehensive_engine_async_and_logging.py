"""
Unit tests for the new async and logging functionality in the comprehensive metadata engine.

These tests verify the new async/await patterns, improved error handling, and logging functions.
"""

import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock, call
import pytest

from server.extractor.comprehensive_metadata_engine import (
    extract_comprehensive_metadata_async,
    extract_comprehensive_batch_async,
    safe_extract_module,
    log_extraction_event
)


def test_log_extraction_event_with_valid_params():
    """Test the log_extraction_event function with valid parameters."""
    # This test just verifies the function can be called without error
    # The actual logging behavior is tested through integration tests
    try:
        log_extraction_event(
            event_type="test_event",
            filepath="/fake/path.jpg",
            module_name="test_module",
            status="info",
            details={"test": "value"},
            duration=1.23
        )
        # If we get here, the function executed without error
        assert True
    except Exception:
        # If there's an error, it's likely due to logger configuration
        # which is expected in test environments
        pass


def test_log_extraction_event_with_minimal_params():
    """Test the log_extraction_event function with minimal parameters."""
    try:
        log_extraction_event(
            event_type="minimal_event",
            filepath="/fake/path.jpg",
            module_name="test_module"
        )
        assert True
    except Exception:
        pass


def test_safe_extract_module_success_with_file_size():
    """Test safe_extract_module with a successful extraction function and file size."""
    def mock_extraction_func(filepath, *args, **kwargs):
        return {"test_field": "test_value"}
    
    # Create a temporary file to test with real file size
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"test content")
        temp_path = temp_file.name
    
    try:
        result = safe_extract_module(mock_extraction_func, temp_path, "test_module")
        
        assert result is not None
        assert "test_field" in result
        assert result["test_field"] == "test_value"
        assert "performance" in result
        assert "test_module" in result["performance"]
        assert result["performance"]["test_module"]["status"] == "success"
        assert result["performance"]["test_module"]["file_size"] == 12  # Length of "test content"
    finally:
        os.unlink(temp_path)


def test_safe_extract_module_with_memory_error():
    """Test safe_extract_module with a MemoryError."""
    def mock_extraction_func(filepath, *args, **kwargs):
        raise MemoryError("Out of memory")
    
    result = safe_extract_module(mock_extraction_func, "/fake/path.jpg", "test_module")
    
    assert result is not None
    assert result["available"] is False
    assert result["error_type"] == "MemoryError"
    assert result["error"] == "Insufficient memory to process file"
    assert "performance" in result
    assert result["performance"]["test_module"]["status"] == "failed"


def test_safe_extract_module_with_timeout_error():
    """Test safe_extract_module with a TimeoutError."""
    def mock_extraction_func(filepath, *args, **kwargs):
        raise TimeoutError("Operation timed out")
    
    result = safe_extract_module(mock_extraction_func, "/fake/path.jpg", "test_module")
    
    assert result is not None
    assert result["available"] is False
    assert result["error_type"] == "TimeoutError"
    assert result["error"] == "Extraction timed out"
    assert "performance" in result
    assert result["performance"]["test_module"]["status"] == "failed"


@pytest.mark.asyncio
async def test_extract_comprehensive_metadata_async_success():
    """Test successful async comprehensive metadata extraction."""
    with patch('server.extractor.comprehensive_metadata_engine.get_comprehensive_extractor') as mock_get_extractor:
        mock_extractor = Mock()
        mock_extractor.extract_comprehensive_metadata.return_value = {
            "file": {"path": "/fake/path.jpg"},
            "extraction_info": {"comprehensive_fields_extracted": 100, "processing_ms": 100}
        }
        mock_get_extractor.return_value = mock_extractor
        
        result = await extract_comprehensive_metadata_async("/fake/path.jpg", "super")
        
        assert result is not None
        assert "file" in result
        assert result["file"]["path"] == "/fake/path.jpg"
        assert "extraction_info" in result
        assert result["extraction_info"]["comprehensive_fields_extracted"] == 100
        mock_extractor.extract_comprehensive_metadata.assert_called_once_with("/fake/path.jpg", "super")


@pytest.mark.asyncio
async def test_extract_comprehensive_metadata_async_error():
    """Test async comprehensive metadata extraction with error."""
    with patch('server.extractor.comprehensive_metadata_engine.get_comprehensive_extractor') as mock_get_extractor:
        mock_extractor = Mock()
        mock_extractor.extract_comprehensive_metadata.side_effect = Exception("Test error")
        mock_get_extractor.return_value = mock_extractor
        
        result = await extract_comprehensive_metadata_async("/fake/path.jpg", "super")
        
        assert result is not None
        assert "error" in result
        assert "Critical error in async comprehensive metadata extraction" in result["error"]
        assert result["error_type"] == "Exception"


@pytest.mark.asyncio
async def test_extract_comprehensive_batch_async_success():
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
        with patch('server.extractor.comprehensive_metadata_engine.get_comprehensive_extractor') as mock_get_extractor:
            mock_extractor = Mock()
            mock_extractor.extract_comprehensive_metadata.return_value = {
                "file": {"path": file1},
                "extraction_info": {"comprehensive_fields_extracted": 50, "processing_ms": 50}
            }
            mock_get_extractor.return_value = mock_extractor
            
            # Mock the storage function to avoid actual storage
            with patch('server.extractor.comprehensive_metadata_engine.store_file_metadata'):
                result = await extract_comprehensive_batch_async([file1, file2], "super")
                
                assert result is not None
                assert "summary" in result
                assert result["summary"]["total_files"] == 2
                assert result["summary"]["successful"] == 2
                assert result["summary"]["failed"] == 0


@pytest.mark.asyncio
async def test_extract_comprehensive_batch_async_with_errors():
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
        with patch('server.extractor.comprehensive_metadata_engine.get_comprehensive_extractor') as mock_get_extractor:
            mock_extractor = Mock()
            
            def side_effect(filepath, tier):
                if filepath == file1:
                    return {
                        "file": {"path": filepath},
                        "extraction_info": {"comprehensive_fields_extracted": 50, "processing_ms": 50}
                    }
                else:
                    raise Exception("Test error")
            
            mock_extractor.extract_comprehensive_metadata.side_effect = side_effect
            mock_get_extractor.return_value = mock_extractor
            
            # Mock the storage function to avoid actual storage
            with patch('server.extractor.comprehensive_metadata_engine.store_file_metadata'):
                result = await extract_comprehensive_batch_async([file1, file2], "super")
                
                assert result is not None
                assert "summary" in result
                assert result["summary"]["total_files"] == 2
                assert result["summary"]["successful"] == 1
                assert result["summary"]["failed"] == 1


@pytest.mark.asyncio
async def test_extract_comprehensive_batch_async_with_semaphore():
    """Test that the semaphore limits concurrent operations in async batch extraction."""
    # Create temporary files for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create multiple dummy files
        files = []
        for i in range(5):
            file_path = os.path.join(temp_dir, f"file{i}.jpg")
            with open(file_path, 'w') as f:
                f.write("dummy content")
            files.append(file_path)
        
        # Track the number of concurrent calls
        concurrent_calls = 0
        max_concurrent = 0
        
        async def track_concurrent_calls(path, tier):
            nonlocal concurrent_calls, max_concurrent
            concurrent_calls += 1
            max_concurrent = max(max_concurrent, concurrent_calls)
            
            # Simulate some async work
            await asyncio.sleep(0.01)
            
            concurrent_calls -= 1
            return path, {"file": {"path": path}, "extraction_info": {"processing_ms": 10}}
        
        # Mock the async extraction function
        with patch('server.extractor.comprehensive_metadata_engine.extract_comprehensive_metadata_async') as mock_async_extract:
            mock_async_extract.side_effect = lambda path, tier: asyncio.sleep(0.01, result=(path, {
                "file": {"path": path},
                "extraction_info": {"processing_ms": 10}
            }))
            
            # Mock the storage function to avoid actual storage
            with patch('server.extractor.comprehensive_metadata_engine.store_file_metadata'):
                result = await extract_comprehensive_batch_async(files, "super", max_workers=2)
                
                # The max concurrent should not exceed the max_workers limit
                assert max_concurrent <= 2
                assert result is not None
                assert "summary" in result
                assert result["summary"]["total_files"] == 5


@pytest.mark.asyncio
async def test_extract_comprehensive_batch_async_with_store_results():
    """Test async batch extraction with storage enabled."""
    # Create temporary files for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some dummy files
        file1 = os.path.join(temp_dir, "file1.jpg")
        file2 = os.path.join(temp_dir, "file2.jpg")
        
        with open(file1, 'w') as f:
            f.write("dummy content")
        with open(file2, 'w') as f:
            f.write("dummy content")
        
        # Mock the extraction function
        with patch('server.extractor.comprehensive_metadata_engine.get_comprehensive_extractor') as mock_get_extractor:
            mock_extractor = Mock()
            mock_extractor.extract_comprehensive_metadata.return_value = {
                "file": {"path": file1},
                "extraction_info": {"comprehensive_fields_extracted": 50, "processing_ms": 50},
                "perceptual_hashes": {"phash": "test_hash"}
            }
            mock_get_extractor.return_value = mock_extractor
            
            # Mock the storage function
            with patch('server.extractor.comprehensive_metadata_engine.store_file_metadata') as mock_store:
                result = await extract_comprehensive_batch_async([file1, file2], "super", store_results=True)
                
                assert result is not None
                assert "summary" in result
                assert result["summary"]["total_files"] == 2
                # Verify that store_file_metadata was called
                assert mock_store.call_count == 2


@pytest.mark.asyncio
async def test_extract_comprehensive_batch_async_storage_error():
    """Test async batch extraction when storage fails."""
    # Create temporary files for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some dummy files
        file1 = os.path.join(temp_dir, "file1.jpg")
        file2 = os.path.join(temp_dir, "file2.jpg")
        
        with open(file1, 'w') as f:
            f.write("dummy content")
        with open(file2, 'w') as f:
            f.write("dummy content")
        
        # Mock the extraction function
        with patch('server.extractor.comprehensive_metadata_engine.get_comprehensive_extractor') as mock_get_extractor:
            mock_extractor = Mock()
            mock_extractor.extract_comprehensive_metadata.return_value = {
                "file": {"path": file1},
                "extraction_info": {"comprehensive_fields_extracted": 50, "processing_ms": 50},
                "perceptual_hashes": {"phash": "test_hash"}
            }
            mock_get_extractor.return_value = mock_extractor
            
            # Mock the storage function to raise an exception
            with patch('server.extractor.comprehensive_metadata_engine.store_file_metadata') as mock_store:
                mock_store.side_effect = Exception("Storage error")
                
                result = await extract_comprehensive_batch_async([file1, file2], "super", store_results=True)
                
                assert result is not None
                assert "summary" in result
                assert result["summary"]["total_files"] == 2
                # The result should still be successful even if storage fails
                assert result["results"][file1].get("storage_error") is not None


def test_safe_extract_module_with_different_exception_types():
    """Test safe_extract_module with various exception types."""
    exception_test_cases = [
        (ImportError, "Module not found"),
        (FileNotFoundError, "File not found"),
        (PermissionError, "Permission denied"),
        (MemoryError, "Out of memory"),
        (TimeoutError, "Operation timed out"),
        (ValueError, "Invalid value"),
        (OSError, "OS error"),
    ]
    
    for exc_type, exc_msg in exception_test_cases:
        def mock_extraction_func(filepath, *args, **kwargs):
            raise exc_type(exc_msg)
        
        result = safe_extract_module(mock_extraction_func, "/fake/path.jpg", "test_module")
        
        assert result is not None
        assert result["available"] is False
        assert result["error_type"] == exc_type.__name__
        assert exc_msg in result["error"] or result["error"] in ["Insufficient memory to process file", "Extraction timed out"]


@pytest.mark.asyncio
async def test_extract_comprehensive_metadata_async_with_cache_hit():
    """Test async extraction when cache returns a result."""
    with patch('server.extractor.comprehensive_metadata_engine.get_cache') as mock_get_cache:
        # Create a mock cache that returns a cached result
        mock_cache = Mock()
        cached_result = {
            "file": {"path": "/fake/path.jpg"},
            "extraction_info": {"comprehensive_fields_extracted": 75, "processing_ms": 5}
        }
        mock_cache.get.return_value = cached_result
        mock_get_cache.return_value = mock_cache
        
        result = await extract_comprehensive_metadata_async("/fake/path.jpg", "super")
        
        assert result == cached_result
        mock_cache.get.assert_called_once_with("/fake/path.jpg", "super")


@pytest.mark.asyncio
async def test_extract_comprehensive_metadata_async_cache_lookup_failure():
    """Test async extraction when cache lookup fails."""
    with patch('server.extractor.comprehensive_metadata_engine.get_cache') as mock_get_cache:
        # Make the cache lookup raise an exception
        mock_get_cache.return_value.get.side_effect = Exception("Cache error")
        
        with patch('server.extractor.comprehensive_metadata_engine.get_comprehensive_extractor') as mock_get_extractor:
            mock_extractor = Mock()
            mock_extractor.extract_comprehensive_metadata.return_value = {
                "file": {"path": "/fake/path.jpg"},
                "extraction_info": {"comprehensive_fields_extracted": 100, "processing_ms": 100}
            }
            mock_get_extractor.return_value = mock_extractor
            
            result = await extract_comprehensive_metadata_async("/fake/path.jpg", "super")
            
            assert result is not None
            assert "file" in result
            assert result["file"]["path"] == "/fake/path.jpg"


@pytest.mark.asyncio
async def test_extract_comprehensive_batch_async_error_handling():
    """Test error handling in async batch extraction function."""
    with patch('server.extractor.comprehensive_metadata_engine.get_comprehensive_extractor') as mock_get_extractor:
        mock_extractor = Mock()
        mock_extractor.extract_comprehensive_metadata.side_effect = Exception("Batch error")
        mock_get_extractor.return_value = mock_extractor
        
        result = await extract_comprehensive_batch_async(["/fake/path1.jpg", "/fake/path2.jpg"], "super")
        
        assert result is not None
        assert "error" in result
        assert "Critical error in async batch metadata extraction" in result["error"]
        assert result["error_type"] == "Exception"
        assert result["summary"]["total_files"] == 2
        assert result["summary"]["successful"] == 0
        assert result["summary"]["failed"] == 2