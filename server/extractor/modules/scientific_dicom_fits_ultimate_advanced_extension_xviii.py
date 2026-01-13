"""
Scientific DICOM/FITS Ultimate Advanced Extension XVIII - Functional MRI

DEPRECATED: This module has been renamed to functional_mri_imaging.py
This file is kept for backward compatibility only.

Use the new module instead:
    from .functional_mri_imaging import extract_functional_mri_imaging
"""

from .functional_mri_imaging import (
    FUNCTIONAL_MRI_IMAGING_AVAILABLE,
    FMRI_TAGS,
    BOLD_TAGS,
    RESTING_STATE_TAGS,
    FMRI_TOTAL_TAGS,
    extract_scientific_dicom_fits_ultimate_advanced_extension_xviii,
    extract_functional_mri_imaging,
    get_scientific_dicom_fits_ultimate_advanced_extension_xviii_field_count,
    get_scientific_dicom_fits_ultimate_advanced_extension_xviii_version,
    get_scientific_dicom_fits_ultimate_advanced_extension_xviii_description,
    get_scientific_dicom_fits_ultimate_advanced_extension_xviii_modalities,
    get_scientific_dicom_fits_ultimate_advanced_extension_xviii_supported_formats,
    get_scientific_dicom_fits_ultimate_advanced_extension_xviii_category,
    get_scientific_dicom_fits_ultimate_advanced_extension_xviii_keywords,
    get_functional_mri_imaging_field_count,
    get_functional_mri_imaging_version,
    get_functional_mri_imaging_description,
)

SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XVIII_AVAILABLE = FUNCTIONAL_MRI_IMAGING_AVAILABLE

__all__ = [
    'SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XVIII_AVAILABLE',
    'extract_scientific_dicom_fits_ultimate_advanced_extension_xviii',
    'get_scientific_dicom_fits_ultimate_advanced_extension_xviii_field_count',
    'extract_functional_mri_imaging',
    'get_functional_mri_imaging_field_count',
]
