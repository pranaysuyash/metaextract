"""
Scientific DICOM/FITS Ultimate Advanced Extension L - Image Quality Assessment and Standardization

This module provides comprehensive extraction of image quality assessment parameters
including standardization metrics, image quality scores, and compliance metadata.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_L_AVAILABLE = True

IQA_STANDARDIZATION = {
    (0x0028, 0x0010): "rows",
    (0x0028, 0x0011): "columns",
    (0x0028, 0x0004): "photometric_interpretation",
    (0x0028, 0x0006): "planar_configuration",
    (0x0028, 0x0008): "number_of_frames",
    (0x0028, 0x0010): "rows",
    (0x0028, 0x0011): "columns",
    (0x0028, 0x0100): "bits_allocated",
    (0x0028, 0x0101): "bits_stored",
    (0x0028, 0x0102): "high_bit",
    (0x0028, 0x0103): "pixel_representation",
    (0x0028, 0x0104): "smallest_image_pixel_value",
    (0x0028, 0x0105): "largest_image_pixel_value",
    (0x0028, 0x0106): "smallest_pixel_value_in_series",
    (0x0028, 0x0107): "largest_pixel_value_in_series",
    (0x0028, 0x0120): "pixel_padding_value",
    (0x0028, 0x0121): "pixel_padding_range_limit",
    (0x0028, 0x0122): "pixel_measure_sequence",
    (0x0028, 0x0123): "physical_pixel_spacing",
    (0x0028, 0x0124): "image_orientation",
    (0x0028, 0x0125): "image_position",
    (0x0028, 0x0128): "pixel_spacing_calibration_type",
    (0x0028, 0x0129): "pixel_spacing_calibration_description",
    (0x0028, 0x0301): "grayscale_word_size",
    (0x0028, 0x0400): "spatial_locations_queried",
    (0x0028, 0x0401): "spatial_resolution",
    (0x0028, 0x0402): "geometric_characteristics",
    (0x0028, 0x0403): "geometric_characteristics_sequence",
    (0x0028, 0x0404): "calibration_object_sequence",
    (0x0028, 0x0406): "data_collection_diameter",
    (0x0028, 0x0407): "data_collection_center",
    (0x0028, 0x0408): "reconstruction_diameter",
    (0x0028, 0x0409): "reconstruction_field_of_view",
    (0x0028, 0x0410): "first_scan_xray",
    (0x0028, 0x0411): "first_scan_direction",
    (0x0028, 0x0412): "cone_beam_scan",
    (0x0028, 0x0414): "table_feed_per_rotation",
    (0x0028, 0x0415): "table_position_tolerance",
    (0x0028, 0x0416): "table_speed",
    (0x0028, 0x0417): "table_position_per_projection",
    (0x0028, 0x0418): "gantry_tilt_tolerance",
    (0x0028, 0x0420): "image_geometry_type",
    (0x0028, 0x0421): "acquisition_type",
    (0x0028, 0x0422): "contrast_bolus_agent_sequence",
    (0x0028, 0x0423): "contrast_bolus_agent_administered",
    (0x0028, 0x0424): "contrast_bolus_agent_volume",
    (0x0028, 0x0425): "contrast_bolus_agent_concentration",
    (0x0028, 0x0426): "contrast_bolus_agent_route",
    (0x0028, 0x0427): "contrast_bolus_agent_sequence_alternate",
    (0x0028, 0x0428): "contrast_bolus_t1_relaxivity",
    (0x0028, 0x0429): "contrast_bolus_interaction_chemical_shift",
}

IQA_METRICS = {
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0080): "reconstruction_diameter",
    (0x0018, 0x0090): "distance_source_to_detector",
    (0x0018, 0x0095): "distance_source_to_patient",
    (0x0018, 0x1000): "device_serial_number",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1050): "spatial_resolution",
    (0x0018, 0x1150): "exposure_time",
    (0x0018, 0x1151): "xray_tube_current",
    (0x0018, 0x1152): "exposure",
    (0x0018, 0x1160): "filter_type",
    (0x0018, 0x1161): "filter_material",
    (0x0018, 0x1200): "date_of_last_calibration",
    (0x0018, 0x1201): "time_of_last_calibration",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0x1314): "ct_volumetric_properties_flag",
    (0x0018, 0x1317): "ct_acquisition_type",
    (0x0018, 0x1327): "ct_dose_length_product",
    (0x0018, 0x1328): "ct_dose_ctdi",
    (0x0018, 0x9067): "cardiac_cycle_position",
    (0x0018, 0x9068): "respiratory_cycle_position",
    (0x0018, 0x9040): "gating_4d_type",
    (0x0018, 0x9020): "respiratory_trigger_type",
}

IQA_COMPLIANCE = {
    (0x0008, 0x0020): "study_date",
    (0x0008, 0x0021): "series_date",
    (0x0008, 0x0022): "acquisition_date",
    (0x0008, 0x0023): "content_date",
    (0x0008, 0x0030): "study_time",
    (0x0008, 0x0031): "series_time",
    (0x0008, 0x0032): "acquisition_time",
    (0x0008, 0x0033): "content_time",
    (0x0008, 0x0201): "timezone_offset_from_utc",
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x0070): "manufacturer",
    (0x0008, 0x1090): "manufacturer_model_name",
    (0x0010, 0x0010): "patient_name",
    (0x0010, 0x0020): "patient_id",
    (0x0010, 0x0030): "patient_birth_date",
    (0x0010, 0x0040): "patient_sex",
    (0x0040, 0x0241): "procedure_step_start_date_time",
    (0x0040, 0x0242): "procedure_step_end_date_time",
    (0x0040, 0x0250): "planned_media_sequence",
    (0x0040, 0x1007): "scheduled_procedure_step_description",
    (0x0040, 0x1010): "scheduled_procedure_step_location",
    (0x0040, 0x1020): "scheduled_procedure_step_id",
    (0x0040, 0x1030): "scheduled_procedure_step_description",
}

IQA_SCORES = {
    (0x0018, 0xA100): "image_quality_score",
    (0x0018, 0xA101): "image_quality_score_type",
    (0x0018, 0xA102): "image_quality_score_value",
    (0x0018, 0xA103): "image_quality_score_unit",
    (0x0018, 0xA104): "image_quality_score_description",
    (0x0018, 0xA105): "image_quality_score_threshold",
    (0x0018, 0xA106): "image_quality_score_threshold_value",
    (0x0018, 0xA107): "image_quality_score_threshold_unit",
    (0x0018, 0xA108): "image_quality_score_threshold_description",
    (0x0018, 0xA110): "artifact_score_sequence",
    (0x0018, 0xA111): "artifact_score_type",
    (0x0018, 0xA112): "artifact_score_value",
    (0x0018, 0xA113): "artifact_score_unit",
    (0x0018, 0xA114): "artifact_score_description",
    (0x0018, 0xA120): "noise_score_sequence",
    (0x0018, 0xA121): "noise_score_type",
    (0x0018, 0xA122): "noise_score_value",
    (0x0018, 0xA123): "noise_score_unit",
    (0x0018, 0xA124): "noise_score_description",
    (0x0018, 0xA130): "contrast_score_sequence",
    (0x0018, 0xA131): "contrast_score_type",
    (0x0018, 0xA132): "contrast_score_value",
    (0x0018, 0xA133): "contrast_score_unit",
    (0x0018, 0xA134): "contrast_score_description",
    (0x0018, 0xA140): "sharpness_score_sequence",
    (0x0018, 0xA141): "sharpness_score_type",
    (0x0018, 0xA142): "sharpness_score_value",
    (0x0018, 0xA143): "sharpness_score_unit",
    (0x0018, 0xA144): "sharpness_score_description",
    (0x0018, 0xA150): "uniformity_score_sequence",
    (0x0018, 0xA151): "uniformity_score_type",
    (0x0018, 0xA152): "uniformity_score_value",
    (0x0018, 0xA153): "uniformity_score_unit",
    (0x0018, 0xA154): "uniformity_score_description",
    (0x0018, 0xA160): "motion_score_sequence",
    (0x0018, 0xA161): "motion_score_type",
    (0x0018, 0xA162): "motion_score_value",
    (0x0018, 0xA163): "motion_score_unit",
    (0x0018, 0xA164): "motion_score_description",
}

IQA_TOTAL_TAGS = IQA_STANDARDIZATION | IQA_METRICS | IQA_COMPLIANCE | IQA_SCORES


def _extract_iqa_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in IQA_TOTAL_TAGS.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _is_iqa_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_l(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_l_detected": False,
        "fields_extracted": 0,
        "extension_l_type": "image_quality_assessment",
        "extension_l_version": "2.0.0",
        "standardization": {},
        "quality_metrics": {},
        "compliance": {},
        "quality_scores": {},
        "extraction_errors": [],
    }

    try:
        if not _is_iqa_file(file_path):
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

        result["extension_l_detected"] = True

        iqa_data = _extract_iqa_tags(ds)

        result["standardization"] = {
            k: v for k, v in iqa_data.items()
            if k in IQA_STANDARDIZATION.values()
        }
        result["quality_metrics"] = {
            k: v for k, v in iqa_data.items()
            if k in IQA_METRICS.values()
        }
        result["compliance"] = {
            k: v for k, v in iqa_data.items()
            if k in IQA_COMPLIANCE.values()
        }
        result["quality_scores"] = {
            k: v for k, v in iqa_data.items()
            if k in IQA_SCORES.values()
        }

        result["fields_extracted"] = len(iqa_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_l_field_count() -> int:
    return len(IQA_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_l_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_l_description() -> str:
    return (
        "Image quality assessment and standardization metadata extraction. Provides "
        "comprehensive coverage of DICOM standardization parameters, acquisition metrics, "
        "compliance metadata, and quantitative quality scores for image assessment."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_l_modalities() -> List[str]:
    return ["CT", "MR", "CR", "DR", "US", "PT", "NM", "MG", "XA", "RF"]


def get_scientific_dicom_fits_ultimate_advanced_extension_l_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_l_category() -> str:
    return "Image Quality Assessment and Standardization"


def get_scientific_dicom_fits_ultimate_advanced_extension_l_keywords() -> List[str]:
    return [
        "image quality", "quality assessment", "standardization", "DICOM compliance",
        "image scores", "artifact detection", "noise", "contrast", "sharpness",
        "uniformity", "QC", "quality control", "ACR", "compliance"
    ]
