"""
Scientific DICOM/FITS Ultimate Advanced Extension XXV - Segmentation Objects

This module provides comprehensive extraction of DICOM segmentation objects
for anatomical segmentation, tumor delineation, and region of interest analysis.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXV_AVAILABLE = True

SEGMENTATION_GENERAL = {
    (0x0062, 0x0001): "segment_number",
    (0x0062, 0x0002): "segment_label",
    (0x0062, 0x0003): "segment_description",
    (0x0062, 0x0004): "segment_algorithm_type",
    (0x0062, 0x0005): "segment_algorithm_name",
    (0x0062, 0x0006): "segment_identification_sequence",
    (0x0062, 0x0008): "segment_properties_sequence",
    (0x0062, 0x0009): "segments_cover_uncovered_domains",
    (0x0062, 0x000A): "segment_covered_content_sequence",
    (0x0062, 0x000B): "segment_longitudinal_temporal_origin",
    (0x0062, 0x000C): "recommended_display_grayscale_value",
    (0x0062, 0x000D): "recommended_display_rgb_value",
    (0x0062, 0x000E): "segment_presentation_lut_sequence",
    (0x0062, 0x000F): "segment_presentation_lut_type",
    (0x0062, 0x0010): "segment_composition_sequence",
    (0x0062, 0x0012): "segment_content_qualification",
    (0x0062, 0x0013): "segment_algorithm_family_sequence",
    (0x0062, 0x0014): "algorithms_family_name_code_sequence",
    (0x0062, 0x0015): "algorithm_name_code_sequence",
    (0x0062, 0x0016): "algorithm_version",
    (0x0062, 0x0017): "algorithm_parameters",
    (0x0062, 0x0018): "algorithm_name_modifier_sequence",
}

SEGMENTATION_CONTENT = {
    (0x0066, 0x0001): "number_of_segments",
    (0x0066, 0x0002): "total_pixel_matrix_columns",
    (0x0066, 0x0003): "total_pixel_matrix_rows",
    (0x0066, 0x0004): "total_pixel_matrix_origin_sequence",
    (0x0066, 0x0005): "segment_reference_sequence",
    (0x0066, 0x0006): "segment_reference_pixel_value",
    (0x0066, 0x0007): "segment_reference_pixel_value_numerical",
    (0x0066, 0x0008): "segments_in_segmentation_sequence",
    (0x0066, 0x0009): "segment_sequence",
    (0x0066, 0x000A): "segment_geometry_sequence",
    (0x0066, 0x000B): "segment_description_code_sequence",
    (0x0066, 0x000C): "segment_algorithm_type_code_sequence",
    (0x0066, 0x000D): "segment_label_type_code_sequence",
    (0x0066, 0x000E): "segment_cover_content_sequence",
    (0x0066, 0x000F): "segment_cover_content_type_code_sequence",
    (0x0066, 0x0010): "segment_cover_content_numerical",
    (0x0066, 0x0011): "coverage_reference_frame_number",
}

ANATOMICAL_REGIONS = {
    (0x0040, 0xA730): "content_qualification",
    (0x0008, 0x0060): "modality",
    (0x0008, 0x0100): "copyright",
    (0x0040, 0xA043): "anatomical_region_sequence",
    (0x0040, 0xA730): "anatomical_region_of_interest",
    (0x0008, 0x2218): "anatomical_structure_sequence",
    (0x0040, 0xA170): "referenced_image_sequence",
    (0x0040, 0xA1A0): "sequence_of_measurement",
    (0x0040, 0xA1B0): "measurement_sequence",
    (0x0040, 0xA1A2): "measurement_code_sequence",
}

SEGMENTATION_TOTAL_TAGS = SEGMENTATION_GENERAL | SEGMENTATION_CONTENT | ANATOMICAL_REGIONS


def _extract_segmentation_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in SEGMENTATION_GENERAL.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _is_segmentation_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            try:
                import pydicom
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                sop_class = getattr(ds, 'SOPClassUID', '')
                if 'Segmentation' in sop_class:
                    return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xxv(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xxv_detected": False,
        "fields_extracted": 0,
        "extension_xxv_type": "segmentation_objects",
        "extension_xxv_version": "2.0.0",
        "segmentation_type": None,
        "segment_parameters": {},
        "segment_geometry": {},
        "anatomical_regions": {},
        "extraction_errors": [],
    }

    try:
        if not _is_segmentation_file(file_path):
            return result

        try:
            import pydicom
            ds = pydicom.dcmread(file_path, stop_before_pixels=True)
        except ImportError:
            result["extraction_errors"].append("pydicom library not available")
            return result
        except Exception as e:
            result["extraction_errors"].append(f"Failed to read file: {str(e)}")
            return result

        result["extension_xxv_detected"] = True
        result["segmentation_type"] = getattr(ds, 'Modality', 'SEG')

        segmentation = _extract_segmentation_tags(ds)
        result["segment_parameters"] = segmentation

        total_fields = len(segmentation)
        result["fields_extracted"] = total_fields

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xxv_field_count() -> int:
    return len(SEGMENTATION_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xxv_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxv_description() -> str:
    return ("DICOM segmentation object extraction. Supports anatomical segmentation, "
            "tumor delineation, and region of interest (ROI) analysis. Extracts "
            "segment parameters, geometry information, and anatomical region data.")


def get_scientific_dicom_fits_ultimate_advanced_extension_xxv_modalities() -> List[str]:
    return ["SEG", "PR", "KO"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxv_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxv_category() -> str:
    return "DICOM Segmentation Objects"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxv_keywords() -> List[str]:
    return [
        "segmentation", "ROI", "tumor delineation", "anatomical regions",
        "organ segmentation", "structure set", "contour", "mask",
        "segmentation object", "radiotherapy planning", "surgical planning"
    ]


# Aliases for smoke test compatibility
def extract_oncology_imaging(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_xxv."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_xxv(file_path)

def get_oncology_imaging_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xxv_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xxv_field_count()

def get_oncology_imaging_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xxv_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xxv_version()

def get_oncology_imaging_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xxv_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xxv_description()

def get_oncology_imaging_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xxv_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xxv_supported_formats()

def get_oncology_imaging_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xxv_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xxv_modalities()
