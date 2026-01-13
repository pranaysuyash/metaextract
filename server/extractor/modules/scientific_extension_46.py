"""
Scientific DICOM/FITS Extension 46 (XLVI) - Vascular Imaging

DEPRECATED: This module has been renamed to vascular_imaging.py
This file is kept for backward compatibility only.

Use the new module instead:
    from .vascular_imaging import extract_vascular_imaging
"""

from .vascular_imaging import (
    VASCULAR_IMAGING_AVAILABLE,
    VASCULAR_CTA,
    VASCULAR_ANALYSIS,
    VASCULAR_MRA,
    VASCULAR_TOTAL_TAGS,
    extract_scientific_dicom_fits_ultimate_advanced_extension_xlvi,
    extract_scientific_extension_46,
    extract_vascular_imaging,
    get_scientific_dicom_fits_ultimate_advanced_extension_xlvi_field_count,
    get_scientific_extension_46_field_count,
    get_scientific_extension_46_version,
    get_scientific_extension_46_description,
    get_scientific_extension_46_supported_formats,
    get_scientific_extension_46_modalities,
    get_vascular_imaging_field_count,
    get_vascular_imaging_version,
    get_vascular_imaging_description,
)

SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XLVI_AVAILABLE = VASCULAR_IMAGING_AVAILABLE

__all__ = [
    'SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XLVI_AVAILABLE',
    'extract_scientific_dicom_fits_ultimate_advanced_extension_xlvi',
    'extract_scientific_extension_46',
    'get_scientific_extension_46_field_count',
    'extract_vascular_imaging',
    'get_vascular_imaging_field_count',
]
