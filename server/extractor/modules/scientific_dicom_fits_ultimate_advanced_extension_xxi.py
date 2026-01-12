"""
Scientific DICOM/FITS Ultimate Advanced Extension XXI - FITS Astronomical Imaging

DEPRECATED: This module has been renamed to fits_astronomical_imaging.py
This file is kept for backward compatibility only.

Use the new module instead:
    from .fits_astronomical_imaging import extract_fits_astronomical_imaging
"""

from .fits_astronomical_imaging import (
    FITS_ASTRONOMICAL_IMAGING_AVAILABLE,
    FITS_ASTRONOMICAL_TAGS,
    WCS_TAGS,
    PHOTOMETRY_TAGS,
    FITS_TOTAL_TAGS,
    extract_scientific_dicom_fits_ultimate_advanced_extension_xxi,
    extract_fits_astronomical_imaging,
    get_scientific_dicom_fits_ultimate_advanced_extension_xxi_field_count,
    get_scientific_dicom_fits_ultimate_advanced_extension_xxi_version,
    get_scientific_dicom_fits_ultimate_advanced_extension_xxi_description,
    get_scientific_dicom_fits_ultimate_advanced_extension_xxi_modalities,
    get_scientific_dicom_fits_ultimate_advanced_extension_xxi_supported_formats,
    get_scientific_dicom_fits_ultimate_advanced_extension_xxi_category,
    get_scientific_dicom_fits_ultimate_advanced_extension_xxi_keywords,
    get_fits_astronomical_imaging_field_count,
    get_fits_astronomical_imaging_version,
    get_fits_astronomical_imaging_description,
)

SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXI_AVAILABLE = FITS_ASTRONOMICAL_IMAGING_AVAILABLE

__all__ = [
    'SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXI_AVAILABLE',
    'extract_scientific_dicom_fits_ultimate_advanced_extension_xxi',
    'get_scientific_dicom_fits_ultimate_advanced_extension_xxi_field_count',
    'extract_fits_astronomical_imaging',
    'get_fits_astronomical_imaging_field_count',
]
