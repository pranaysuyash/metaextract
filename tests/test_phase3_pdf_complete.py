import pytest
from server.extractor.modules import pdf_metadata_complete as pdf


def test_pdf_complete_module_imports():
    """Test that the PDF complete module can be imported and has expected functions."""
    assert hasattr(pdf, 'extract_pdf_metadata_complete')
    assert hasattr(pdf, 'extract_pdf_complete')
    assert hasattr(pdf, 'get_pdf_complete_field_count')

    field_count = pdf.get_pdf_complete_field_count()
    assert isinstance(field_count, int)
    assert field_count > 0


def test_pdf_complete_field_count():
    """Test that field count matches expected structure."""
    count = pdf.get_pdf_complete_field_count()
    # Should be around 43 fields based on our implementation
    assert count >= 40
    assert count <= 60  # Reasonable upper bound


def test_extract_pdf_complete_with_invalid_file():
    """Test error handling for invalid PDF files."""
    result = pdf.extract_pdf_complete('/nonexistent/file.pdf')
    assert isinstance(result, dict)
    assert 'pdf_extraction_error' in result or len(result) == 0