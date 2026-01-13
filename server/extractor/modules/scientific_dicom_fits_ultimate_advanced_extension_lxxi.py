"""
Scientific DICOM/FITS Ultimate Advanced Extension LXXI - Trauma Imaging II

DEPRECATED: This module has been renamed to trauma_imaging_advanced.py
This file is kept for backward compatibility only.

Use the new module instead:
    from .trauma_imaging_advanced import extract_trauma_imaging_advanced
"""

from .trauma_imaging_advanced import (
    TRAUMA_IMAGING_ADVANCED_AVAILABLE,
    TRAUMA_PATIENT_PARAMETERS,
    TOTAL_TAGS_LXXI,
    extract_scientific_dicom_fits_ultimate_advanced_extension_lxxi,
    extract_trauma_imaging_advanced,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxxi_field_count,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxxi_version,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxxi_description,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxxi_modalities,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxxi_supported_formats,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxxi_category,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxxi_keywords,
    get_trauma_imaging_advanced_field_count,
    get_trauma_imaging_advanced_version,
    get_trauma_imaging_advanced_description,
)

SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXI_AVAILABLE = TRAUMA_IMAGING_ADVANCED_AVAILABLE
TRAUMA_TOTAL_TAGS = TOTAL_TAGS_LXXI  # Alias for compatibility

__all__ = [
    'SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXI_AVAILABLE',
    'TRAUMA_TOTAL_TAGS',
    'extract_scientific_dicom_fits_ultimate_advanced_extension_lxxi',
    'get_scientific_dicom_fits_ultimate_advanced_extension_lxxi_field_count',
    'extract_trauma_imaging_advanced',
    'get_trauma_imaging_advanced_field_count',
]
