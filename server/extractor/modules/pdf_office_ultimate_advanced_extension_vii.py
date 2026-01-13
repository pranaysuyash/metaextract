"""
PDF Office Ultimate Advanced Extension VII

DEPRECATED: This module has been renamed to pdf_office_forensics.py
This file is kept for backward compatibility only.

Use the new module instead:
    from .pdf_office_forensics import extract_pdf_office_forensics
"""

from .pdf_office_forensics import (
    PDF_OFFICE_FORENSICS_AVAILABLE,
    PDF_OFFICE_FORENSICS_TOTAL_TAGS,
    extract_pdf_office_forensics,
    extract_pdf_office_ultimate_advanced_extension_vii,
    get_pdf_office_forensics_field_count,
    get_pdf_office_ultimate_advanced_extension_vii_field_count,
    get_pdf_office_forensics_version,
    get_pdf_office_forensics_description,
    get_pdf_office_forensics_modalities,
    get_pdf_office_forensics_supported_formats,
    get_pdf_office_forensics_category,
    get_pdf_office_forensics_keywords,
)

PDF_OFFICE_ULTIMATE_ADVANCED_EXTENSION_VII_AVAILABLE = PDF_OFFICE_FORENSICS_AVAILABLE

__all__ = [
    'PDF_OFFICE_ULTIMATE_ADVANCED_EXTENSION_VII_AVAILABLE',
    'extract_pdf_office_ultimate_advanced_extension_vii',
    'get_pdf_office_ultimate_advanced_extension_vii_field_count',
    'extract_pdf_office_forensics',
    'get_pdf_office_forensics_field_count',
    'get_pdf_office_forensics_version',
    'get_pdf_office_forensics_description',
]
