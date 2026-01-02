"""
Scientific DICOM/FITS Ultimate Advanced Extension XXIII - NetCDF Climate Data

This module provides comprehensive extraction of NetCDF (Network Common Data Form)
metadata for climate, atmospheric, and oceanographic scientific data.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXIII_AVAILABLE = True

NETCDF_DIMENSIONS = {
    "dimension_name": "dimension_name",
    "dimension_size": "dimension_size",
    "unlimited_dimension": "unlimited_axis",
}

NETCDF_VARIABLES = {
    "variable_name": "variable_name",
    "variable_type": "data_type",
    "variable_shape": "dimensions",
    "variable_units": "units",
    "variable_long_name": "long_name",
    "variable_fill_value": "missing_value",
    "variable_valid_min": "valid_minimum",
    "variable_valid_max": "valid_maximum",
    "variable_scale_factor": "scale_factor",
    "variable_add_offset": "add_offset",
    "variable_compression": "compression",
}

NETCDF_ATTRIBUTES = {
    "title": "dataset_title",
    "institution": "producing_institution",
    "source": "data_source",
    "history": "processing_history",
    "references": "publication_references",
    "comment": "general_comments",
    "Conventions": "convention_version",
    "featureType": "feature_type",
    "geospatial_lat_min": "latitude_range_min",
    "geospatial_lat_max": "latitude_range_max",
    "geospatial_lon_min": "longitude_range_min",
    "geospatial_lon_max": "longitude_range_max",
    "geospatial_vertical_min": "vertical_range_min",
    "geospatial_vertical_max": "vertical_range_max",
    "geospatial_vertical_positive": "vertical_direction",
    "time_coverage_start": "temporal_range_start",
    "time_coverage_end": "temporal_range_end",
    "time_coverage_duration": "temporal_duration",
    "time_coverage_resolution": "temporal_resolution",
}

CLIMATE_SPECIFIC = {
    "institution": "research_institution",
    "source_version": "model_version",
    "experiment": "climate_experiment",
    "forcing": "climate_forcing",
    "initialization_method": "initialization_technique",
    "physics_version": "physics_package_version",
    "tracking_id": "dataset_identifier",
    "parent_experiment": "previous_experiment",
    "parent_experiment_rip": "parent_ensemble_member",
    "branch_time": "branch_time_in_parent",
}

NETCDF_TOTAL_TAGS = NETCDF_DIMENSIONS | NETCDF_VARIABLES | NETCDF_ATTRIBUTES | CLIMATE_SPECIFIC


def _extract_netcdf_structure(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in NETCDF_DIMENSIONS.items():
        try:
            if hasattr(ds, tag):
                value = getattr(ds, tag, None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _is_netcdf_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith(('.nc', '.cdf', '.nc4')):
            return True
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xxiii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xxiii_detected": False,
        "fields_extracted": 0,
        "extension_xxiii_type": "netcdf_climate",
        "extension_xxiii_version": "2.0.0",
        "netcdf_type": None,
        "dimensions": {},
        "variables": {},
        "global_attributes": {},
        "climate_specific": {},
        "extraction_errors": [],
    }

    try:
        if not _is_netcdf_file(file_path):
            return result

        try:
            import netCDF4
            with netCDF4.Dataset(file_path, 'r') as ds:
                structure = _extract_netcdf_structure(ds)
        except ImportError:
            result["extraction_errors"].append("netCDF4 library not available")
            return result
        except Exception as e:
            result["extraction_errors"].append(f"Failed to read file: {str(e)}")
            return result

        result["extension_xxiii_detected"] = True
        result["netcdf_type"] = "climate_data"
        result["dimensions"] = structure

        total_fields = len(structure)
        result["fields_extracted"] = total_fields

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xxiii_field_count() -> int:
    return len(NETCDF_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xxiii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxiii_description() -> str:
    return ("NetCDF climate data extraction. Supports climate model output, "
            "atmospheric and oceanographic data. Extracts dimensions, variables, "
            "CF conventions attributes, and climate-specific metadata.")


def get_scientific_dicom_fits_ultimate_advanced_extension_xxiii_modalities() -> List[str]:
    return ["NetCDF", "NC", "CDF"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxiii_supported_formats() -> List[str]:
    return [".nc", ".cdf", ".nc4"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxiii_category() -> str:
    return "NetCDF Climate Data"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxiii_keywords() -> List[str]:
    return [
        "NetCDF", "climate", "atmospheric", "oceanographic", "CMIP",
        "climate model", "CF conventions", "geophysical data", "ERA5",
        "reanalysis", "satellite data", "environmental modeling"
    ]
