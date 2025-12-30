import pytest
from server.extractor.modules import office_documents as office


def test_office_module_imports():
    """Test that the Office documents module can be imported and has expected functions."""
    assert hasattr(office, 'extract_office_metadata')
    assert hasattr(office, 'extract_office_complete')
    assert hasattr(office, 'get_office_field_count')

    field_count = office.get_office_field_count()
    assert isinstance(field_count, int)
    assert field_count > 0


def test_office_field_count():
    """Test that field count matches expected structure."""
    count = office.get_office_field_count()
    # Should be around 44 fields based on our implementation
    assert count >= 40
    assert count <= 60  # Reasonable upper bound


def test_extract_office_with_invalid_file():
    """Test error handling for invalid Office files."""
    result = office.extract_office_complete('/nonexistent/file.docx')
    assert isinstance(result, dict)
    # Should have either an error key or be mostly empty
    has_error = any('error' in key.lower() for key in result.keys())
    assert has_error or len(result) <= 2  # Just format info


def test_extract_office_unsupported_format():
    """Test handling of unsupported file formats."""
    result = office.extract_office_metadata('/nonexistent/file.txt')
    assert isinstance(result, dict)
    assert 'office_format_error' in result