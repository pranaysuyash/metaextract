"""
Scientific DICOM/FITS Ultimate Advanced Extension XIX - Diffusion Imaging

DEPRECATED: This module has been renamed to diffusion_mri_imaging.py
This file is kept for backward compatibility only.

Use the new module instead:
    from .diffusion_mri_imaging import extract_diffusion_mri_imaging
"""

from .diffusion_mri_imaging import (
    DIFFUSION_MRI_IMAGING_AVAILABLE,
    DWI_TAGS,
    DTI_TAGS,
    ADVANCED_DIFFUSION_TAGS,
    DIFFUSION_TOTAL_TAGS,
    extract_scientific_dicom_fits_ultimate_advanced_extension_xix,
    extract_diffusion_mri_imaging,
    get_scientific_dicom_fits_ultimate_advanced_extension_xix_field_count,
    get_scientific_dicom_fits_ultimate_advanced_extension_xix_version,
    get_scientific_dicom_fits_ultimate_advanced_extension_xix_description,
    get_scientific_dicom_fits_ultimate_advanced_extension_xix_modalities,
    get_scientific_dicom_fits_ultimate_advanced_extension_xix_supported_formats,
    get_scientific_dicom_fits_ultimate_advanced_extension_xix_category,
    get_scientific_dicom_fits_ultimate_advanced_extension_xix_keywords,
    get_diffusion_mri_imaging_field_count,
    get_diffusion_mri_imaging_version,
    get_diffusion_mri_imaging_description,
)

SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XIX_AVAILABLE = DIFFUSION_MRI_IMAGING_AVAILABLE

__all__ = [
    'SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XIX_AVAILABLE',
    'extract_scientific_dicom_fits_ultimate_advanced_extension_xix',
    'get_scientific_dicom_fits_ultimate_advanced_extension_xix_field_count',
    'extract_diffusion_mri_imaging',
    'get_diffusion_mri_imaging_field_count',
]
