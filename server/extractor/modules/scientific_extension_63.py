"""
Scientific DICOM/FITS Extension 63 (LXIII) - Critical Care Imaging

DEPRECATED: This module has been renamed to critical_care_imaging.py
This file is kept for backward compatibility only.

Use the new module instead:
    from .critical_care_imaging import extract_critical_care_imaging
"""

from .critical_care_imaging import (
    CRITICAL_CARE_IMAGING_AVAILABLE,
    ICU_PATIENT_PARAMETERS,
    ICU_TOTAL_TAGS,
    extract_scientific_dicom_fits_ultimate_advanced_extension_lxiii,
    extract_critical_care_imaging,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxiii_field_count,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxiii_version,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxiii_description,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxiii_modalities,
    get_scientific_dicom_fits_ultimate_advanced_extension_lxiii_supported_formats,
    get_critical_care_imaging_field_count,
    get_critical_care_imaging_version,
    get_critical_care_imaging_description,
)

SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXIII_AVAILABLE = CRITICAL_CARE_IMAGING_AVAILABLE

__all__ = [
    'SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXIII_AVAILABLE',
    'extract_scientific_dicom_fits_ultimate_advanced_extension_lxiii',
    'extract_critical_care_imaging',
    'get_critical_care_imaging_field_count',
]
