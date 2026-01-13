"""
Scientific DICOM/FITS Ultimate Advanced Extension XX - Various Medical Modalities

DEPRECATED: This module has been renamed to veterinary_research_imaging.py
This file is kept for backward compatibility only.

Use the new module instead:
    from .veterinary_research_imaging import extract_veterinary_research_imaging
"""

from .veterinary_research_imaging import (
    VETERINARY_RESEARCH_IMAGING_AVAILABLE,
    VETERINARY_TAGS,
    RESEARCH_TAGS,
    EMERGING_TAGS,
    MULTIMODAL_TAGS,
    VARIOUS_MODALITIES_TOTAL_TAGS,
    extract_scientific_dicom_fits_ultimate_advanced_extension_xx,
    extract_veterinary_research_imaging,
    get_scientific_dicom_fits_ultimate_advanced_extension_xx_field_count,
    get_scientific_dicom_fits_ultimate_advanced_extension_xx_version,
    get_scientific_dicom_fits_ultimate_advanced_extension_xx_description,
    get_scientific_dicom_fits_ultimate_advanced_extension_xx_modalities,
    get_scientific_dicom_fits_ultimate_advanced_extension_xx_supported_formats,
    get_scientific_dicom_fits_ultimate_advanced_extension_xx_category,
    get_scientific_dicom_fits_ultimate_advanced_extension_xx_keywords,
    get_veterinary_research_imaging_field_count,
    get_veterinary_research_imaging_version,
    get_veterinary_research_imaging_description,
)

SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XX_AVAILABLE = VETERINARY_RESEARCH_IMAGING_AVAILABLE

__all__ = [
    'SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XX_AVAILABLE',
    'extract_scientific_dicom_fits_ultimate_advanced_extension_xx',
    'get_scientific_dicom_fits_ultimate_advanced_extension_xx_field_count',
    'extract_veterinary_research_imaging',
    'get_veterinary_research_imaging_field_count',
]
