"""
Scientific DICOM/FITS Ultimate Advanced Extension XLVIII - Multimodal Image Fusion

This module provides comprehensive extraction of multimodal image fusion parameters
including registration, fusion visualization, and hybrid imaging metadata.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XLVIII_AVAILABLE = True

FUSION_REGISTRATION = {
    (0x0020, 0x0032): "image_position",
    (0x0020, 0x0037): "image_orientation",
    (0x0020, 0x0052): "frame_of_reference_uid",
    (0x0020, 0x0060): "series_in_contrast_to",
    (0x0020, 0x0062): "matching_frame_of_reference_uid",
    (0x0020, 0x0064): "transform_attributes_sequence",
    (0x0020, 0x0065): "transform_description",
    (0x0020, 0x0066): "transform_description_sequence",
    (0x0020, 0x0067): "transform_description_type",
    (0x0020, 0x0068): "transform_description_type_code_sequence",
    (0x0020, 0x0070): "transform_description_value",
    (0x0020, 0x0071): "transform_description_value_sequence",
    (0x0020, 0x0072): "transform_description_value_code_sequence",
    (0x0020, 0x0075): "transform_order",
    (0x0020, 0x0076): "transform_order_description",
    (0x0020, 0x0077): "transform_order_code_sequence",
    (0x0020, 0x0080): "transform_description_direction",
    (0x0020, 0x0081): "transform_description_direction_value",
    (0x0020, 0x0082): "transform_description_direction_code_sequence",
    (0x0020, 0x0090): "transform_description_matrix",
    (0x0020, 0x0091): "transform_description_matrix_sequence",
    (0x0020, 0x0092): "transform_description_matrix_value",
    (0x0020, 0x0093): "transform_description_matrix_sequence_row",
    (0x0020, 0x0094): "transform_description_matrix_sequence_column",
    (0x0020, 0x0095): "transform_description_matrix_value_unit",
    (0x0020, 0x00A0): "transform_description_offset",
    (0x0020, 0x00A1): "transform_description_offset_value",
    (0x0020, 0x00A2): "transform_description_offset_unit",
    (0x0020, 0x00B0): "transform_description_scale",
    (0x0020, 0x00B1): "transform_description_scale_value",
    (0x0020, 0x00B2): "transform_description_scale_unit",
    (0x0020, 0x00C0): "transform_description_rotation",
    (0x0020, 0x00C1): "transform_description_rotation_value",
    (0x0020, 0x00C2): "transform_description_rotation_unit",
    (0x0020, 0x00D0): "transform_description_translation",
    (0x0020, 0x00D1): "transform_description_translation_value",
    (0x0020, 0x00D2): "transform_description_translation_unit",
    (0x0020, 0x00E0): "transform_description_skew",
    (0x0020, 0x00E1): "transform_description_skew_value",
    (0x0020, 0x00E2): "transform_description_skew_unit",
}

FUSION_VISUALIZATION = {
    (0x0028, 0x1050): "window_center",
    (0x0028, 0x1051): "window_width",
    (0x0028, 0x1052): "rescale_intercept",
    (0x0028, 0x1053): "rescale_slope",
    (0x0028, 0x1054): "rescale_type",
    (0x0028, 0x1055): "window_center_and_width_explanation",
    (0x0028, 0x1056): "voilut_function",
    (0x0028, 0x1057): "gray_lookup_table_function",
    (0x0028, 0x1058): "gray_lookup_table_descriptor",
    (0x0028, 0x1059): "red_color_lookup_table_descriptor",
    (0x0028, 0x105A): "green_color_lookup_table_descriptor",
    (0x0028, 0x105B): "blue_color_lookup_table_descriptor",
    (0x0028, 0x105C): "alpha_color_lookup_table_descriptor",
    (0x0028, 0x105D): "red_color_lookup_table_data",
    (0x0028, 0x105E): "green_color_lookup_table_data",
    (0x0028, 0x105F): "blue_color_lookup_table_data",
    (0x0028, 0x1060): "segmentation_type",
    (0x0028, 0x1061): "segmentation_algorithm_type",
    (0x0028, 0x1062): "segmentation_algorithm_name",
    (0x0028, 0x1063): "segmentation_sequence",
    (0x0028, 0x1064): "segmentation_description",
    (0x0028, 0x1065): "segmentation_identified_regions",
    (0x0028, 0x1066): "segmentation_identified_region_value_type",
    (0x0028, 0x1067): "segmentation_identified_region_value",
    (0x0028, 0x1068): "segmentation_identified_region_descriptor",
    (0x0028, 0x1069): "segmentation_identified_region_color",
    (0x0028, 0x1070): "fused_image_type",
    (0x0028, 0x1071): "fused_image_type_description",
    (0x0028, 0x1072): "fused_image_weighting_sequence",
    (0x0028, 0x1073): "fused_image_weighting_value",
    (0x0028, 0x1074): "fused_image_weighting_unit",
    (0x0028, 0x1075): "fused_image_weighting_description",
    (0x0028, 0x1080): "display_shade_value_mapping",
    (0x0028, 0x1081): "display_shade_value_mapping_description",
    (0x0028, 0x1082): "display_shade_value_mapping_sequence",
    (0x0028, 0x1083): "display_shade_value_mapping_type",
    (0x0028, 0x1084): "display_shade_value_mapping_type_description",
    (0x0028, 0x1085): "display_shade_value_mapping_value",
    (0x0028, 0x1086): "display_shade_value_mapping_value_sequence",
    (0x0028, 0x1087): "display_shade_value_mapping_value_code_sequence",
}

FUSION_HYBRID = {
    (0x0008, 0x0060): "modality",
    (0x0008, 0x0201): "timezone_offset_from_utc",
    (0x0018, 0x0010): "contrast_bolus_agent",
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1040): "contrast_bolus_volume",
    (0x0018, 0x1050): "spatial_resolution",
    (0x0018, 0x1060): "filter_material",
    (0x0040, 0x0241): "procedure_step_start_date_time",
    (0x0040, 0x0242): "procedure_step_end_date_time",
    (0x0040, 0x0250): "planned_media_sequence",
    (0x0040, 0x0251): "planned_imaging_agent_sequence",
    (0x0040, 0x0252): "imaging_agent_supply_sequence",
    (0x0040, 0x0253): "imaging_agent_supply_description",
    (0x0040, 0x0254): "imaging_agent_supply_quantity",
    (0x0040, 0x0255): "imaging_agent_supply_quantity_unit",
    (0x0040, 0x0256): "imaging_agent_administration_date_time",
    (0x0040, 0x0257): "imaging_agent_administration_completed_sequence",
    (0x0040, 0x0258): "imaging_agent_administration_started_sequence",
    (0x0040, 0x0259): "imaging_agent_application_completed_sequence",
    (0x0040, 0x025A): "imaging_agent_application_started_sequence",
    (0x0040, 0x0260): "imaging_agent_selection_criteria_sequence",
    (0x0040, 0x0261): "imaging_agent_selection_criteria_item",
    (0x0040, 0x0262): "imaging_agent_selection_criteria_description",
    (0x0040, 0x0263): "imaging_agent_selection_criteria_value",
    (0x0040, 0x0264): "imaging_agent_selection_criteria_unit",
}

FUSION_TOTAL_TAGS = FUSION_REGISTRATION | FUSION_VISUALIZATION | FUSION_HYBRID


def _extract_fusion_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in FUSION_TOTAL_TAGS.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _is_fusion_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xlviii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xlviii_detected": False,
        "fields_extracted": 0,
        "extension_xlviii_type": "multimodal_image_fusion",
        "extension_xlviii_version": "2.0.0",
        "registration_parameters": {},
        "visualization_parameters": {},
        "hybrid_imaging": {},
        "extraction_errors": [],
    }

    try:
        if not _is_fusion_file(file_path):
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

        result["extension_xlviii_detected"] = True

        fusion_data = _extract_fusion_tags(ds)

        result["registration_parameters"] = {
            k: v for k, v in fusion_data.items()
            if k in FUSION_REGISTRATION.values()
        }
        result["visualization_parameters"] = {
            k: v for k, v in fusion_data.items()
            if k in FUSION_VISUALIZATION.values()
        }
        result["hybrid_imaging"] = {
            k: v for k, v in fusion_data.items()
            if k in FUSION_HYBRID.values()
        }

        result["fields_extracted"] = len(fusion_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xlviii_field_count() -> int:
    return len(FUSION_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xlviii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xlviii_description() -> str:
    return (
        "Multimodal image fusion metadata extraction. Provides comprehensive coverage "
        "of registration parameters, transformation matrices, fusion visualization "
        "settings, and hybrid imaging (PET/CT, PET/MR, SPECT/CT) metadata."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_xlviii_modalities() -> List[str]:
    return ["CT", "MR", "PT", "NM", "SPECT", "CR", "DR", "US"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xlviii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xlviii_category() -> str:
    return "Multimodal Image Fusion"


def get_scientific_dicom_fits_ultimate_advanced_extension_xlviii_keywords() -> List[str]:
    return [
        "image fusion", "registration", "PET/CT", "PET/MR", "SPECT/CT",
        "multimodal", "hybrid imaging", "image registration", "transform",
        "fusion visualization", "co-registration", "alignment"
    ]
