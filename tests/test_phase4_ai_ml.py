# tests/test_phase4_ai_ml.py

import pytest
import os
import tempfile
import json
from server.extractor.modules import ai_ml_metadata as aiml


def test_ai_ml_module_imports():
    """Test that the ai_ml_metadata module can be imported and has expected functions."""
    assert hasattr(aiml, 'extract_ai_ml_metadata')
    assert hasattr(aiml, 'extract_ai_ml_complete')
    assert hasattr(aiml, 'get_ai_ml_field_count')


def test_ai_ml_field_count():
    """Test that get_ai_ml_field_count returns a reasonable number."""
    count = aiml.get_ai_ml_field_count()
    assert isinstance(count, int)
    assert count > 40  # Should have at least 40+ fields


def test_extract_ai_ml_with_invalid_file():
    """Test extraction with non-existent file."""
    result = aiml.extract_ai_ml_complete('/nonexistent/file.h5')
    assert isinstance(result, dict)
    assert 'ai_ml_extraction_error' in result


def test_extract_ai_ml_config_json():
    """Test extraction from JSON configuration file."""
    config_data = {
        "model": {
            "type": "transformer",
            "layers": 12,
            "heads": 8,
            "hidden_size": 768
        },
        "training": {
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 100
        },
        "optimizer": "adam",
        "loss": "cross_entropy"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_path = f.name

    try:
        result = aiml.extract_ai_ml_complete(temp_path)
        assert isinstance(result, dict)
        assert 'ai_ml_extraction_error' not in result
        assert result['config_file_present'] is True
        assert result['config_format'] == 'json'
        assert result['config_has_structure'] is True
        assert result['config_model_type'] == 'transformer'
        assert result['config_learning_rate'] == 0.001
        assert result['config_batch_size'] == 32
        assert result['config_optimizer'] == 'adam'
    finally:
        os.unlink(temp_path)


def test_detect_model_type():
    """Test model type detection."""
    # Test JSON config detection
    config_data = {"model": "bert", "layers": 12}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_path = f.name

    try:
        model_type = aiml._detect_model_type(temp_path)
        assert model_type == 'config'
    finally:
        os.unlink(temp_path)


def test_extract_general_properties():
    """Test extraction of general model properties."""
    # Create a dummy file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.h5', delete=False) as f:
        f.write("dummy content")
        temp_path = f.name

    try:
        result = aiml.extract_ai_ml_complete(temp_path)
        assert 'model_file_size' in result
        assert 'model_filename' in result
        assert isinstance(result['model_file_size'], int)
        assert result['model_filename'].endswith('.h5')
    finally:
        os.unlink(temp_path)