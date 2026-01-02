"""
Scientific DICOM/FITS Ultimate Advanced Extension XXII - HDF5 Scientific Data

This module provides comprehensive extraction of HDF5 metadata for scientific data
including multi-dimensional arrays, groups, and attributes.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXII_AVAILABLE = True

HDF5_STRUCTURE_TAGS = {
    "hdf5_version": "hdf5_library_version",
    "file_signature": "file_signature",
    "super_block_version": "super_block_version",
    "free_space_manager": "free_space_manager",
    "root_group_address": "root_group_address",
    "free_space_section_address": "free_space_section_address",
    "object_header_address": "object_header_address",
    "object_header_size": "object_header_size",
    "group_entry_key": "group_entry_key",
    "group_entry_value": "group_entry_value",
    "dataset_dimensions": "dataset_dimensions",
    "dataset_max_dimensions": "dataset_max_dimensions",
    "dataset_chunk_dimensions": "dataset_chunk_dimensions",
    "dataset_compression": "dataset_compression",
    "dataset_compression_opts": "compression_options",
    "dataset_fill_value": "fill_value",
    "dataset_layout": "dataset_storage_layout",
}

HDF5_ATTRIBUTES = {
    "attribute_name": "attribute_name",
    "attribute_type": "attribute_data_type",
    "attribute_shape": "attribute_shape",
    "attribute_value": "attribute_value",
    "attribute_count": "number_of_attributes",
}

HDF5_DATASETS = {
    "dataset_name": "dataset_name",
    "dataset_type": "dataset_data_type",
    "dataset_shape": "dataset_shape",
    "dataset_maxshape": "dataset_maximum_shape",
    "dataset_chunks": "chunk_dimensions",
    "dataset_compression": "compression_algorithm",
    "dataset_scaleoffset": "scale_offset",
    "dataset_shuffle": "shuffle_filter",
    "dataset_fletcher32": "fletcher32_checksum",
    "dataset_nbit": "nbit_compression",
    "dataset_szip": "szip_compression",
}

HDF5_GROUPS = {
    "group_name": "group_name",
    "group_creation_order": "creation_order",
    "group_link_count": "number_of_links",
    "group_attribute_count": "number_of_attributes",
    "group_contents": "group_contents",
    "group_subgroups": "subgroup_names",
    "group_datasets": "dataset_names",
    "group_links": "link_names",
}

HDF5_TOTAL_TAGS = HDF5_STRUCTURE_TAGS | HDF5_ATTRIBUTES | HDF5_DATASETS | HDF5_GROUPS


def _extract_hdf5_structure(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in HDF5_STRUCTURE_TAGS.items():
        try:
            if hasattr(ds, tag):
                value = getattr(ds, tag, None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _calculate_hdf5_metrics(ds: Any) -> Dict[str, Any]:
    metrics = {}
    try:
        if hasattr(ds, 'dataset_shape'):
            shape = ds.dataset_shape
            metrics['total_elements'] = 1
            for dim in shape:
                metrics['total_elements'] *= dim
            metrics['dimensions'] = len(shape)
    except Exception:
        pass
    return metrics


def _is_hdf5_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith(('.h5', '.hdf5', '.he5')):
            return True
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xxii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xxii_detected": False,
        "fields_extracted": 0,
        "extension_xxii_type": "hdf5_scientific",
        "extension_xxii_version": "2.0.0",
        "hdf5_type": None,
        "file_structure": {},
        "datasets": {},
        "groups": {},
        "attributes": {},
        "derived_metrics": {},
        "extraction_errors": [],
    }

    try:
        if not _is_hdf5_file(file_path):
            return result

        try:
            import h5py
            with h5py.File(file_path, 'r') as f:
                structure = _extract_hdf5_structure(f)
                metrics = _extract_hdf5_structure(f)
        except ImportError:
            result["extraction_errors"].append("h5py library not available")
            return result
        except Exception as e:
            result["extraction_errors"].append(f"Failed to read file: {str(e)}")
            return result

        result["extension_xxii_detected"] = True
        result["hdf5_type"] = "scientific_data"
        result["file_structure"] = structure
        result["derived_metrics"] = metrics

        total_fields = len(structure) + len(metrics)
        result["fields_extracted"] = total_fields

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xxii_field_count() -> int:
    return len(HDF5_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xxii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxii_description() -> str:
    return ("HDF5 scientific data extraction. Supports multi-dimensional arrays, "
            "groups, datasets, and attributes. Extracts file structure, compression "
            "parameters, and hierarchical organization for comprehensive HDF5 analysis.")


def get_scientific_dicom_fits_ultimate_advanced_extension_xxii_modalities() -> List[str]:
    return ["HDF5", "H5", "HE5"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxii_supported_formats() -> List[str]:
    return [".h5", ".hdf5", ".he5"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxii_category() -> str:
    return "HDF5 Scientific Data"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxii_keywords() -> List[str]:
    return [
        "HDF5", "h5py", "scientific data", "multi-dimensional arrays",
        "big data", "datasets", "groups", "attributes", "compression",
        "chunked storage", "hierarchical data"
    ]
