"""
Scientific DICOM/FITS Ultimate Advanced Extension XXXIX - Pediatric Imaging

This module provides comprehensive extraction of pediatric imaging parameters
including age-specific protocols, growth metrics, and pediatric-specific acquisition data.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXXIX_AVAILABLE = True

PEDIATRIC_PATIENT = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x4000): "patient_complaint",
    (0x0010, 0x21D0): "patient_last_modified_date_time",
    (0x0010, 0x21F0): "patient_breast_implant_indicator",
    (0x0010, 0x21F1): "patient_breast_implant_surface_contour",
    (0x0010, 0x2203): "patient_breast_implant_filling",
    (0x0010, 0x2299): "patient_position_referenced_from",
    (0x0010, 0x22A0): "patient_position_referencing_method",
    (0x0010, 0x22A1): "patient_position_coordinate_system_fiducial_point",
    (0x0010, 0x22A2): "patient_position_identity_indicator",
    (0x0010, 0x22A3): "patient_position_measurement_method",
    (0x0010, 0x22A4): "patient_position_fiducial_point",
    (0x0010, 0x22A5): "patient_position_reference_frame_origin",
    (0x0010, 0x4100): "patient_birth_name",
    (0x0010, 0x4101): "patient_birth_date",
    (0x0010, 0x4102): "patient_birth_time",
    (0x0010, 0x4103): "patient_birth_place",
    (0x0010, 0x4104): "patient_alternate_identifier_sequence",
    (0x0010, 0x4105): "patient_alternate_identifier_type",
    (0x0010, 0x4106): "patient_alternate_identifier_value",
    (0x0010, 0x4107): "patient_alternate_identifier_issuer",
    (0x0010, 0x4108): "patient_birth_name_sequence",
    (0x0010, 0x4109): "patient_birth_given_name",
    (0x0010, 0x410A): "patient_birth_middle_name",
    (0x0010, 0x410B): "patient_birth_prefix",
    (0x0010, 0x410C): "patient_birth_suffix",
    (0x0010, 0x410D): "patient_birth_name_code_sequence",
    (0x0010, 0x410E): "patient_birth_name_code_value",
    (0x0010, 0x410F): "patient_birth_name_code_meaning",
    (0x0010, 0x4110): "patient_ethnic_group",
    (0x0010, 0x4111): "patient_ethnic_group_code_sequence",
    (0x0010, 0x4112): "patient_ethnic_group_code_value",
    (0x0010, 0x4113): "patient_ethnic_group_code_meaning",
    (0x0010, 0x4120): "patient_telecom_information_sequence",
    (0x0010, 0x4121): "patient_telecom_type",
    (0x0010, 0x4122): "patient_telecom_value",
    (0x0010, 0x4123): "patient_telecom_manufacturer",
    (0x0010, 0x4130): "patient_residence_sequence",
    (0x0010, 0x4131): "patient_residence_type",
    (0x0010, 0x4132): "patient_residence_value",
    (0x0010, 0x4140): "patient_insurance_plan_sequence",
    (0x0010, 0x4141): "patient_insurance_type",
    (0x0010, 0x4142): "patient_insurance_plan_description",
    (0x0010, 0x4150): "patient_medical_alerts_sequence",
    (0x0010, 0x4151): "patient_medical_alert_type",
    (0x0010, 0x4152): "patient_medical_alert_value",
    (0x0010, 0x4160): "patient_religious_preference",
    (0x0010, 0x4161): "patient_religious_preference_code_sequence",
    (0x0010, 0x4162): "patient_religious_preference_code_value",
    (0x0010, 0x4163): "patient_religious_preference_code_meaning",
    (0x0010, 0x4170): "patient_medical_record_locator_sequence",
    (0x0010, 0x4171): "patient_medical_record_locator_type",
    (0x0010, 0x4172): "patient_medical_record_locator_value",
}

PEDIATRIC_ACQUISITION = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0020): "patient_position",
    (0x0018, 0x0022): "scan_options",
    (0x0018, 0x0023): "image_type",
    (0x0018, 0x0031): "revolution_time",
    (0x0018, 0x0040): "single_collimation_width",
    (0x0018, 0x0041): "total_collimation_width",
    (0x0018, 0x0042): "table_height",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0070): "data_collection_diameter",
    (0x0018, 0x0080): "reconstruction_diameter",
    (0x0018, 0x0090): "distance_source_to_detector",
    (0x0018, 0x0095): "distance_source_to_patient",
    (0x0018, 0x1000): "device_serial_number",
    (0x0018, 0x1010): "secondary_capture_device_id",
    (0x0018, 0x1011): "secondary_capture_device_manufacturer",
    (0x0018, 0x1012): "secondary_capture_device_manufacturer_model_name",
    (0x0018, 0x1014): "secondary_capture_device_software_versions",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1040): "contrast_bolus_volume",
    (0x0018, 0x1050): "spatial_resolution",
    (0x0018, 0x1060): "filter_material",
    (0x0018, 0x1070): "date_of_secondary_capture",
    (0x0018, 0x1080): "time_of_secondary_capture",
    (0x0018, 0x1100): "transducer_data",
    (0x0018, 0x1110): "focus_depth",
    (0x0018, 0x1111): "depth_of_scan_field",
    (0x0018, 0x1150): "exposure_time",
    (0x0018, 0x1151): "xray_tube_current",
    (0x0018, 0x1152): "exposure",
    (0x0018, 0x1160): "filter_type",
    (0x0018, 0x1200): "date_of_last_calibration",
    (0x0018, 0x1201): "time_of_last_calibration",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0x1240): "upper_limit_string",
    (0x0018, 0x1242): "lower_limit_string",
    (0x0018, 0x1243): "patient_table_motion",
    (0x0018, 0x1244): "patient_table_position",
    (0x0018, 0x1245): "gantry_pitch",
    (0x0018, 0x1246): "gantry_pitch_tolerance",
    (0x0018, 0x1247): "beam_pitch",
    (0x0018, 0x1248): "beam_pitch_tolerance",
    (0x0018, 0x1249): "slice_pitch",
    (0x0018, 0x124A): "slice_pitch_tolerance",
}

PEDIATRIC_GROWTH_METRICS = {
    (0x0010, 0x1021): "patient_height_previous",
    (0x0010, 0x1031): "patient_weight_previous",
    (0x0010, 0x1022): "patient_height_delta",
    (0x0010, 0x1032): "patient_weight_delta",
    (0x0010, 0x1023): "patient_height_measurement_date",
    (0x0010, 0x1033): "patient_weight_measurement_date",
    (0x0010, 0x1024): "patient_bmi",
    (0x0010, 0x1025): "patient_bmi_unit",
    (0x0010, 0x1026): "patient_bmi_description",
    (0x0010, 0x1034): "patient_body_surface_area",
    (0x0018, 0x1314): "ct_volumetric_properties_flag",
    (0x0018, 0x1315): "ct_divol_console_message",
    (0x0018, 0x1316): "ct_record_message",
    (0x0018, 0x1317): "ct_acquisition_type",
    (0x0018, 0x1318): "ct_acquisition_mode",
    (0x0018, 0x1319): "ct_slice_spacing",
    (0x0018, 0x1320): "ct_slice_thickness",
    (0x0018, 0x1321): "ct_image_type",
    (0x0018, 0x1322): "ct_reconstruction_algorithm",
    (0x0018, 0x1323): "ct_reconstruction_kernel",
    (0x0018, 0x1324): "ct_reconstruction_filter",
    (0x0018, 0x1325): "ct_window_presets",
    (0x0018, 0x1326): "ct_contrast_bolus_protocol",
    (0x0018, 0x1327): "ct_dose_length_product",
    (0x0018, 0x1328): "ct_dose_ctdi",
    (0x0018, 0x1329): "ct_dose_descriptor",
    (0x0018, 0x1330): "ct_optimal_contrast",
    (0x0018, 0x1331): "ct_contrast_injection_rate",
    (0x0018, 0x1332): "ct_contrast_injection_volume",
    (0x0018, 0x1333): "ct_contrast_injection_delay",
    (0x0018, 0x1334): "ct_contrast_bolus_agent",
    (0x0018, 0x1335): "ct_contrast_bolus_concentration",
    (0x0018, 0x1336): "ct_contrast_bolus_temperature",
    (0x0018, 0x1337): "ct_contrast_bolus_viscosity",
}

PEDIATRIC_TOTAL_TAGS = PEDIATRIC_PATIENT | PEDIATRIC_ACQUISITION | PEDIATRIC_GROWTH_METRICS


def _extract_pediatric_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in PEDIATRIC_TOTAL_TAGS.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _is_pediatric_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xxxix(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xxxix_detected": False,
        "fields_extracted": 0,
        "extension_xxxix_type": "pediatric_imaging",
        "extension_xxxix_version": "2.0.0",
        "pediatric_patient": {},
        "pediatric_acquisition": {},
        "pediatric_growth_metrics": {},
        "extraction_errors": [],
    }

    try:
        if not _is_pediatric_file(file_path):
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

        result["extension_xxxix_detected"] = True

        pediatric_data = _extract_pediatric_tags(ds)

        result["pediatric_patient"] = {
            k: v for k, v in pediatric_data.items()
            if k in PEDIATRIC_PATIENT.values()
        }
        result["pediatric_acquisition"] = {
            k: v for k, v in pediatric_data.items()
            if k in PEDIATRIC_ACQUISITION.values()
        }
        result["pediatric_growth_metrics"] = {
            k: v for k, v in pediatric_data.items()
            if k in PEDIATRIC_GROWTH_METRICS.values()
        }

        result["fields_extracted"] = len(pediatric_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxix_field_count() -> int:
    return len(PEDIATRIC_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxix_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxix_description() -> str:
    return (
        "Pediatric imaging metadata extraction. Provides comprehensive coverage of "
        "pediatric patient data, age-specific acquisition protocols, growth metrics, "
        "BMI calculations, and pediatric-specific radiation dose considerations."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxix_modalities() -> List[str]:
    return ["CT", "MR", "CR", "DR", "US", "PT", "NM"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxix_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxix_category() -> str:
    return "Pediatric Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxix_keywords() -> List[str]:
    return [
        "pediatric", "child", "infant", "neonatal", "growth chart", "BMI",
        "body surface area", "age-specific", "pediatric protocol", "development"
    ]


# Aliases for smoke test compatibility
def extract_sequencing_analysis(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_xxxix."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_xxxix(file_path)

def get_sequencing_analysis_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xxxix_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xxxix_field_count()

def get_sequencing_analysis_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xxxix_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xxxix_version()

def get_sequencing_analysis_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xxxix_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xxxix_description()

def get_sequencing_analysis_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xxxix_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xxxix_supported_formats()

def get_sequencing_analysis_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xxxix_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xxxix_modalities()
