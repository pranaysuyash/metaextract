"""
Scientific DICOM/FITS Extension 77 (LXXVII) - Geriatric Imaging II

DEPRECATED: This module has been renamed to geriatric_imaging_advanced.py
This file is kept for backward compatibility only.

Use the new module instead:
    from .geriatric_imaging_advanced import extract_geriatric_imaging_advanced
"""

from .geriatric_imaging_advanced import (
    GERIATRIC_IMAGING_ADVANCED_AVAILABLE,
    GERIATRIC_PATIENT_PARAMETERS,
    GERIATRIC_TOTAL_TAGS,
    extract_scientific_dicom_fits_ultimate_advanced_extension_lxxvii,
    extract_geriatric_imaging_advanced,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxxvii_field_count,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxxvii_version,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxxvii_description,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxxvii_modalities,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxxvii_supported_formats,
    get_geriatric_imaging_advanced_field_count,
    get_geriatric_imaging_advanced_version,
    get_geriatric_imaging_advanced_description,
)

SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXVII_AVAILABLE = GERIATRIC_IMAGING_ADVANCED_AVAILABLE

__all__ = [
    'SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXVII_AVAILABLE',
    'extract_scientific_dicom_fits_ultimate_advanced_extension_lxxvii',
    'extract_geriatric_imaging_advanced',
    'get_geriatric_imaging_advanced_field_count',
]
