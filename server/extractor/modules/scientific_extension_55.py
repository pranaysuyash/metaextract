"""
Scientific DICOM/FITS Extension 55 (LV) - Transplant Imaging

DEPRECATED: This module has been renamed to transplant_imaging.py
This file is kept for backward compatibility only.

Use the new module instead:
    from .transplant_imaging import extract_transplant_imaging
"""

from .transplant_imaging import (
    TRANSPLANT_IMAGING_AVAILABLE,
    TRANSPLANT_PATIENT_PARAMETERS,
    TRANSPLANT_TOTAL_TAGS,
    extract_scientific_dicom_fits_ultimate_advanced_extension_lv,
    extract_transplant_imaging,
    get_scientific_dicom_fits_ultimate_advanced_extension_lv_field_count,
    get_scientific_dicom_fits_ultimate_advanced_extension_lv_version,
    get_scientific_dicom_fits_ultimate_advanced_extension_lv_description,
    get_scientific_dicom_fits_ultimate_advanced_extension_lv_modalities,
    get_scientific_dicom_fits_ultimate_advanced_extension_lv_supported_formats,
    get_transplant_imaging_field_count,
    get_transplant_imaging_version,
    get_transplant_imaging_description,
)

SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LV_AVAILABLE = TRANSPLANT_IMAGING_AVAILABLE

__all__ = [
    'SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LV_AVAILABLE',
    'extract_scientific_dicom_fits_ultimate_advanced_extension_lv',
    'extract_transplant_imaging',
    'get_transplant_imaging_field_count',
]
