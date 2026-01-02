from server.extractor.modules.forensic_metadata import extract_forensic_metadata_metadata


def test_extract_forensic_metadata_metadata_basic(tmp_path):
    sample = tmp_path / "sample.bin"
    sample.write_bytes(b"forensic-test")

    result = extract_forensic_metadata_metadata(str(sample))

    assert result["is_valid_forensic_metadata"] is True
    assert "extracted_fields" in result
    assert "forensic" in result["extracted_fields"]
    assert result["fields_extracted"] >= 0
