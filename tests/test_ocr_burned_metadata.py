"""
Unit tests for the OCR burned metadata module.

These tests verify the functionality of the OCR burned metadata extraction module,
including error handling, logging, async operations, and various extraction scenarios.
"""

import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from server.extractor.modules.ocr_burned_metadata import (
    extract_burned_metadata,
    extract_burned_metadata_async,
    BurnedMetadataExtractor
)


def test_burned_metadata_extractor_initialization():
    """Test that the burned metadata extractor initializes correctly."""
    extractor = BurnedMetadataExtractor()
    
    assert extractor is not None
    assert hasattr(extractor, 'extract')
    assert hasattr(extractor, '_run_ocr')
    assert hasattr(extractor, '_parse_ocr_text')


@patch('server.extractor.modules.ocr_burned_metadata.subprocess.run')
def test_extract_burned_metadata_success(mock_subprocess_run):
    """Test successful burned metadata extraction."""
    # Mock tesseract being available
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.return_value.stdout = "Lat 12.923974° Long 77.625419°"
    
    with patch('server.extractor.modules.ocr_burned_metadata.Path.exists', return_value=True):
        result = extract_burned_metadata("/fake/path.jpg")
        
        assert result is not None
        assert "has_burned_metadata" in result
        assert result["has_burned_metadata"] is True
        assert "parsed_data" in result
        assert "gps" in result["parsed_data"]


@patch('server.extractor.modules.ocr_burned_metadata.subprocess.run')
def test_extract_burned_metadata_no_ocr(mock_subprocess_run):
    """Test burned metadata extraction when OCR is not available."""
    # Mock tesseract not being available
    mock_subprocess_run.side_effect = FileNotFoundError()
    
    extractor = BurnedMetadataExtractor()
    result = extractor.extract("/fake/path.jpg")
    
    assert result is not None
    assert "ocr_available" in result
    assert result["ocr_available"] is False
    assert "warning" in result


@patch('server.extractor.modules.ocr_burned_metadata.subprocess.run')
def test_extract_burned_metadata_with_error(mock_subprocess_run):
    """Test burned metadata extraction with OCR error."""
    # Mock tesseract returning an error
    mock_subprocess_run.return_value.returncode = 1
    mock_subprocess_run.return_value.stderr = "Tesseract error"
    
    with patch('server.extractor.modules.ocr_burned_metadata.Path.exists', return_value=True):
        result = extract_burned_metadata("/fake/path.jpg")
        
        assert result is not None
        assert "has_burned_metadata" in result
        assert result["has_burned_metadata"] is False


def test_extract_burned_metadata_nonexistent_file():
    """Test burned metadata extraction with non-existent file."""
    result = extract_burned_metadata("/nonexistent/file.jpg")
    
    assert result is not None
    assert "has_burned_metadata" in result
    assert result["has_burned_metadata"] is False


@patch('server.extractor.modules.ocr_burned_metadata.subprocess.run')
def test_extract_burned_metadata_with_gps_data(mock_subprocess_run):
    """Test burned metadata extraction with GPS data."""
    # Mock tesseract returning GPS data
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.return_value.stdout = "Lat 12.923974° Long 77.625419°"
    
    with patch('server.extractor.modules.ocr_burned_metadata.Path.exists', return_value=True):
        result = extract_burned_metadata("/fake/path.jpg")
        
        assert result is not None
        assert "has_burned_metadata" in result
        assert result["has_burned_metadata"] is True
        assert "parsed_data" in result
        assert "gps" in result["parsed_data"]
        assert "latitude" in result["parsed_data"]["gps"]
        assert "longitude" in result["parsed_data"]["gps"]


@patch('server.extractor.modules.ocr_burned_metadata.subprocess.run')
def test_extract_burned_metadata_with_location_data(mock_subprocess_run):
    """Test burned metadata extraction with location data."""
    # Mock tesseract returning location data
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.return_value.stdout = "New York, NY, USA"
    
    with patch('server.extractor.modules.ocr_burned_metadata.Path.exists', return_value=True):
        result = extract_burned_metadata("/fake/path.jpg")
        
        assert result is not None
        assert "has_burned_metadata" in result
        assert result["has_burned_metadata"] is True
        assert "parsed_data" in result
        assert "location" in result["parsed_data"]
        assert result["parsed_data"]["location"]["city"] == "New York"


@patch('server.extractor.modules.ocr_burned_metadata.subprocess.run')
def test_extract_burned_metadata_with_timestamp_data(mock_subprocess_run):
    """Test burned metadata extraction with timestamp data."""
    # Mock tesseract returning timestamp data
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.return_value.stdout = "Monday, 15/08/2023 10:30 AM"
    
    with patch('server.extractor.modules.ocr_burned_metadata.Path.exists', return_value=True):
        result = extract_burned_metadata("/fake/path.jpg")
        
        assert result is not None
        assert "has_burned_metadata" in result
        assert result["has_burned_metadata"] is True
        assert "parsed_data" in result
        assert "timestamp" in result["parsed_data"]


@patch('server.extractor.modules.ocr_burned_metadata.subprocess.run')
def test_extract_burned_metadata_with_weather_data(mock_subprocess_run):
    """Test burned metadata extraction with weather data."""
    # Mock tesseract returning weather data
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.return_value.stdout = "Temperature: 25°C, Humidity: 60%"
    
    with patch('server.extractor.modules.ocr_burned_metadata.Path.exists', return_value=True):
        result = extract_burned_metadata("/fake/path.jpg")
        
        assert result is not None
        assert "has_burned_metadata" in result
        assert result["has_burned_metadata"] is True
        assert "parsed_data" in result
        assert "weather" in result["parsed_data"]
        assert "temperature" in result["parsed_data"]["weather"]
        assert "humidity" in result["parsed_data"]["weather"]


@patch('server.extractor.modules.ocr_burned_metadata.subprocess.run')
def test_extract_burned_metadata_with_camera_app(mock_subprocess_run):
    """Test burned metadata extraction with camera app watermark."""
    # Mock tesseract returning camera app data
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.return_value.stdout = "GPS Map Camera"
    
    with patch('server.extractor.modules.ocr_burned_metadata.Path.exists', return_value=True):
        result = extract_burned_metadata("/fake/path.jpg")
        
        assert result is not None
        assert "has_burned_metadata" in result
        assert result["has_burned_metadata"] is True
        assert "parsed_data" in result
        assert "camera_app" in result["parsed_data"]
        assert result["parsed_data"]["camera_app"] == "GPS Map Camera"


@patch('server.extractor.modules.ocr_burned_metadata.subprocess.run')
def test_extract_burned_metadata_with_compass_data(mock_subprocess_run):
    """Test burned metadata extraction with compass data."""
    # Mock tesseract returning compass data
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.return_value.stdout = "45° N"
    
    with patch('server.extractor.modules.ocr_burned_metadata.Path.exists', return_value=True):
        result = extract_burned_metadata("/fake/path.jpg")
        
        assert result is not None
        assert "has_burned_metadata" in result
        assert result["has_burned_metadata"] is True
        assert "parsed_data" in result
        assert "compass" in result["parsed_data"]
        assert "degrees" in result["parsed_data"]["compass"]
        assert "direction" in result["parsed_data"]["compass"]


@patch('server.extractor.modules.ocr_burned_metadata.subprocess.run')
def test_extract_burned_metadata_empty_ocr_result(mock_subprocess_run):
    """Test burned metadata extraction with empty OCR result."""
    # Mock tesseract returning empty result
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.return_value.stdout = ""
    
    with patch('server.extractor.modules.ocr_burned_metadata.Path.exists', return_value=True):
        result = extract_burned_metadata("/fake/path.jpg")
        
        assert result is not None
        assert "has_burned_metadata" in result
        assert result["has_burned_metadata"] is False


@pytest.mark.asyncio
@patch('server.extractor.modules.ocr_burned_metadata.subprocess.run')
async def test_extract_burned_metadata_async_success(mock_subprocess_run):
    """Test successful async burned metadata extraction."""
    # Mock tesseract being available
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.return_value.stdout = "Lat 12.923974° Long 77.625419°"
    
    with patch('server.extractor.modules.ocr_burned_metadata.Path.exists', return_value=True):
        result = await extract_burned_metadata_async("/fake/path.jpg")
        
        assert result is not None
        assert "has_burned_metadata" in result
        assert result["has_burned_metadata"] is True
        assert "parsed_data" in result
        assert "gps" in result["parsed_data"]


@pytest.mark.asyncio
@patch('server.extractor.modules.ocr_burned_metadata.subprocess.run')
async def test_extract_burned_metadata_async_with_error(mock_subprocess_run):
    """Test async burned metadata extraction with OCR error."""
    # Mock tesseract returning an error
    mock_subprocess_run.return_value.returncode = 1
    mock_subprocess_run.return_value.stderr = "Tesseract error"
    
    with patch('server.extractor.modules.ocr_burned_metadata.Path.exists', return_value=True):
        result = await extract_burned_metadata_async("/fake/path.jpg")
        
        assert result is not None
        assert "has_burned_metadata" in result
        assert result["has_burned_metadata"] is False


@pytest.mark.asyncio
async def test_extract_burned_metadata_async_nonexistent_file():
    """Test async burned metadata extraction with non-existent file."""
    result = await extract_burned_metadata_async("/nonexistent/file.jpg")
    
    assert result is not None
    assert "has_burned_metadata" in result
    assert result["has_burned_metadata"] is False


@pytest.mark.asyncio
@patch('server.extractor.modules.ocr_burned_metadata.BurnedMetadataExtractor.extract')
async def test_extract_burned_metadata_async_exception_handling(mock_extract):
    """Test async burned metadata extraction handles exceptions."""
    mock_extract.side_effect = Exception("Test exception")
    
    result = await extract_burned_metadata_async("/fake/path.jpg")
    
    assert result is not None
    assert "error" in result
    assert "Critical error in async burned metadata extraction" in result["error"]


def test_parse_ocr_text_with_gps():
    """Test parsing OCR text with GPS coordinates."""
    extractor = BurnedMetadataExtractor()
    text = "Lat 12.923974° Long 77.625419°"
    result = extractor._parse_ocr_text(text)
    
    assert result is not None
    assert "gps" in result
    assert "latitude" in result["gps"]
    assert "longitude" in result["gps"]


def test_parse_ocr_text_with_location():
    """Test parsing OCR text with location."""
    extractor = BurnedMetadataExtractor()
    text = "New York, NY, USA"
    result = extractor._parse_ocr_text(text)
    
    assert result is not None
    assert "location" in result
    assert result["location"]["city"] == "New York"


def test_parse_ocr_text_with_timestamp():
    """Test parsing OCR text with timestamp."""
    extractor = BurnedMetadataExtractor()
    text = "Monday, 15/08/2023 10:30 AM"
    result = extractor._parse_ocr_text(text)
    
    assert result is not None
    assert "timestamp" in result


def test_parse_ocr_text_with_weather():
    """Test parsing OCR text with weather data."""
    extractor = BurnedMetadataExtractor()
    text = "Temperature: 25°C, Humidity: 60%"
    result = extractor._parse_ocr_text(text)
    
    assert result is not None
    assert "weather" in result
    assert "temperature" in result["weather"]
    assert "humidity" in result["weather"]


def test_parse_ocr_text_with_camera_app():
    """Test parsing OCR text with camera app."""
    extractor = BurnedMetadataExtractor()
    text = "GPS Map Camera"
    result = extractor._parse_ocr_text(text)
    
    assert result is not None
    assert "camera_app" in result
    assert result["camera_app"] == "GPS Map Camera"


def test_parse_ocr_text_empty():
    """Test parsing empty OCR text."""
    extractor = BurnedMetadataExtractor()
    text = ""
    result = extractor._parse_ocr_text(text)
    
    assert result is not None
    assert isinstance(result, dict)
    assert len(result) == 0 or ("parsing_errors" in result and len(result) == 1)


def test_parse_ocr_text_with_compass():
    """Test parsing OCR text with compass direction."""
    extractor = BurnedMetadataExtractor()
    text = "45° N"
    result = extractor._parse_ocr_text(text)
    
    assert result is not None
    assert "compass" in result
    assert "degrees" in result["compass"]
    assert "direction" in result["compass"]


def test_calculate_confidence():
    """Test confidence calculation."""
    extractor = BurnedMetadataExtractor()
    
    # Test with GPS data (should be high confidence)
    parsed_with_gps = {"gps": {"latitude": 12.34, "longitude": 56.78}}
    confidence = extractor._calculate_confidence(parsed_with_gps)
    assert confidence == "high"
    
    # Test with location data (should be medium confidence)
    parsed_with_location = {"location": {"city": "New York", "state": "NY", "country": "USA"}}
    confidence = extractor._calculate_confidence(parsed_with_location)
    assert confidence == "medium"
    
    # Test with timestamp data (should be medium confidence)
    parsed_with_timestamp = {"timestamp": "Monday, 15/08/2023 10:30 AM"}
    confidence = extractor._calculate_confidence(parsed_with_timestamp)
    assert confidence == "medium"
    
    # Test with weather data (should be low confidence)
    parsed_with_weather = {"weather": {"temperature": "25°C"}}
    confidence = extractor._calculate_confidence(parsed_with_weather)
    assert confidence == "low"
    
    # Test with no significant data (should be none confidence)
    parsed_with_nothing = {"camera_app": "GPS Map Camera"}
    confidence = extractor._calculate_confidence(parsed_with_nothing)
    assert confidence == "low"
    
    # Test with empty data (should be none confidence)
    parsed_empty = {}
    confidence = extractor._calculate_confidence(parsed_empty)
    assert confidence == "none"