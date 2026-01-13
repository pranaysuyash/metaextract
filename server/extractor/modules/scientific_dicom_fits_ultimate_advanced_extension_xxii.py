"""
Scientific DICOM/FITS Ultimate Advanced Extension XXII - HDF5 Scientific Data

DEPRECATED: This module has been renamed to hdf5_scientific_data.py
This file is kept for backward compatibility only.

Use the new module instead:
    from .hdf5_scientific_data import extract_hdf5_scientific_data
"""

from .hdf5_scientific_data import (
    HDF5_SCIENTIFIC_DATA_AVAILABLE,
    HDF5_STRUCTURE_TAGS,
    HDF5_ATTRIBUTES,
    HDF5_DATASETS,
    HDF5_TOTAL_TAGS,
    extract_scientific_dicom_fits_ultimate_advanced_extension_xxii,
    extract_hdf5_scientific_data,
    get_scientific_dicom_fits_ultimate_advanced_extension_xxii_field_count,
    get_scientific_dicom_fits_ultimate_advanced_extension_xxii_version,
    get_scientific_dicom_fits_ultimate_advanced_extension_xxii_description,
    get_scientific_dicom_fits_ultimate_advanced_extension_xxii_modalities,
    get_scientific_dicom_fits_ultimate_advanced_extension_xxii_supported_formats,
    get_scientific_dicom_fits_ultimate_advanced_extension_xxii_category,
    get_scientific_dicom_fits_ultimate_advanced_extension_xxii_keywords,
    get_hdf5_scientific_data_field_count,
    get_hdf5_scientific_data_version,
    get_hdf5_scientific_data_description,
)

SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXII_AVAILABLE = HDF5_SCIENTIFIC_DATA_AVAILABLE

__all__ = [
    'SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXII_AVAILABLE',
    'extract_scientific_dicom_fits_ultimate_advanced_extension_xxii',
    'get_scientific_dicom_fits_ultimate_advanced_extension_xxii_field_count',
    'extract_hdf5_scientific_data',
    'get_hdf5_scientific_data_field_count',
]
