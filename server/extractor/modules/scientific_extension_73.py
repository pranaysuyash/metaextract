"""
Scientific DICOM/FITS Extension 73 (LXXIII) - Rheumatology Imaging II

DEPRECATED: This module has been renamed to rheumatology_imaging_advanced.py
This file is kept for backward compatibility only.

Use the new module instead:
    from .rheumatology_imaging_advanced import extract_rheumatology_imaging_advanced
"""

from .rheumatology_imaging_advanced import (
    RHEUMATOLOGY_IMAGING_ADVANCED_AVAILABLE,
    RHEUMATOLOGY_PATIENT_PARAMETERS,
    RHEUMATOLOGY_TOTAL_TAGS,
    extract_scientific_dicom_fits_ultimate_advanced_extension_lxxiii,
    extract_rheumatology_imaging_advanced,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxxiii_field_count,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxxiii_version,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxxiii_description,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxxiii_modalities,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxxiii_supported_formats,
    get_rheumatology_imaging_advanced_field_count,
    get_rheumatology_imaging_advanced_version,
    get_rheumatology_imaging_advanced_description,
)

SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXIII_AVAILABLE = RHEUMATOLOGY_IMAGING_ADVANCED_AVAILABLE

__all__ = [
    'SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXIII_AVAILABLE',
    'extract_scientific_dicom_fits_ultimate_advanced_extension_lxxiii',
    'extract_rheumatology_imaging_advanced',
    'get_rheumatology_imaging_advanced_field_count',
]
