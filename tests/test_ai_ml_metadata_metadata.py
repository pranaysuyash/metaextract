from server.extractor.modules.ai_ml_metadata_registry import extract_ai_ml_metadata_metadata


def test_extract_ai_ml_metadata_metadata_invalid_path():
    result = extract_ai_ml_metadata_metadata(None)
    assert "error" in result


def test_extract_ai_ml_metadata_metadata_smoke(tmp_path):
    model_path = tmp_path / "checkpoint_model"
    model_path.write_bytes(b"dummy")

    result = extract_ai_ml_metadata_metadata(str(model_path))

    assert result["is_valid_ai_ml_metadata"] is True
    assert "ai_ml_metadata_metadata" in result
    assert result["fields_extracted"] >= 0
