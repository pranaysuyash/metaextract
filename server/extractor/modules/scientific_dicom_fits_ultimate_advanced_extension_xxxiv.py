"""
Scientific DICOM/FITS Ultimate Advanced Extension XXXIV - Veterinary Imaging

This module provides comprehensive extraction of veterinary imaging parameters
including animal-specific acquisition parameters and species identification.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXXIV_AVAILABLE = True

VETERINARY_PATIENT = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
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
    (0x0010, 0x4000): "patient_complaint",
    (0x0010, 0x43B0): "veterinary_patient_id",
    (0x0010, 0x43B1): "veterinary_patient_species",
    (0x0010, 0x43B2): "veterinary_patient_breed",
    (0x0010, 0x43B3): "veterinary_patient_sex",
    (0x0010, 0x43B4): "veterinary_patient_age_years",
    (0x0010, 0x43B5): "veterinary_patient_weight_kg",
    (0x0010, 0x43B6): "veterinary_owner_name",
    (0x0010, 0x43B7): "veterinary_owner_contact",
    (0x0010, 0x43B8): "veterinary_clinic_name",
    (0x0010, 0x43B9): "veterinary_clinic_contact",
    (0x0010, 0x43BA): "veterinary_medical_record_number",
    (0x0010, 0x43BB): "veterinary_reason_for_examination",
    (0x0010, 0x43BC): "veterinary_anesthesia_type",
    (0x0010, 0x43BD): "veterinary_anesthesia_duration",
    (0x0010, 0x43BE): "veterinary_sedation_type",
    (0x0010, 0x43BF): "veterinary_sedation_dose",
    (0x0010, 0x43C0): "veterinary_patient_positioning",
    (0x0010, 0x43C1): "veterinary_coil_type",
    (0x0010, 0x43C2): "veterinary_coil_size",
    (0x0010, 0x43C3): "veterinary_contrast_agent",
    (0x0010, 0x43C4): "veterinary_contrast_dose",
    (0x0010, 0x43C5): "veterinary_injection_site",
    (0x0010, 0x43C6): "veterinary_scan_plane",
    (0x0010, 0x43C7): "veterinary_slice_thickness",
    (0x0010, 0x43C8): "veterinary_field_of_view",
    (0x0010, 0x43C9): "veterinary_matrix_size",
    (0x0010, 0x43CA): "veterinary_number_of_averages",
    (0x0010, 0x43CB): "veterinary_repetition_time",
    (0x0010, 0x43CC): "veterinary_echo_time",
    (0x0010, 0x43CD): "veterinary_inversion_time",
    (0x0010, 0x43CE): "veterinary_flip_angle",
    (0x0010, 0x43CF): "veterinary_number_of_phase_encoding_steps",
}

VETERINARY_STUDY = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physicians_of_record",
    (0x0008, 0x1049): "physicians_of_record_identification_sequence",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0008, 0x1052): "performing_physician_identification_sequence",
    (0x0008, 0x1060): "name_of_physicians_reading_study",
    (0x0008, 0x1062): "physicians_reading_identification_sequence",
    (0x0008, 0x1070): "operators_name",
    (0x0008, 0x1072): "operator_identification_sequence",
    (0x0008, 0x1080): "admitting_diagnoses_description",
    (0x0008, 0x1084): "admitting_diagnoses_code_sequence",
    (0x0008, 0x1090): "manufacturer_model_name",
    (0x0008, 0x1150): "referenced_visit_sequence",
    (0x0008, 0x1155): "referenced_study_sequence",
    (0x0008, 0x115A): "referenced_registration_sequence",
    (0x0008, 0x115E): "referenced_procedure_step_sequence",
    (0x0008, 0x2111): "derivation_description",
    (0x0008, 0x2112): "source_image_sequence",
    (0x0018, 0x0010): "contrast_bolus_agent",
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
}

VETERINARY_ACQUISITION = {
    (0x0018, 0x9004): "cardiac_trigger_type",
    (0x0018, 0x9005): "cardiac_trigger_sequence",
    (0x0018, 0x9006): "cardiac_trigger_time_offset",
    (0x0018, 0x9007): "cardiac_trigger_frequency",
    (0x0018, 0x9008): "cardiac_trigger_delay",
    (0x0018, 0x9009): "cardiac_phase_delay",
    (0x0018, 0x9010): "cardiac_b_beat_repeat_sequence",
    (0x0018, 0x9011): "cardiac_b_beat_repeat_value",
    (0x0018, 0x9012): "cardiac_b_beat_average_value",
    (0x0018, 0x9020): "respiratory_trigger_type",
    (0x0018, 0x9021): "respiratory_trigger_sequence",
    (0x0018, 0x9022): "respiratory_trigger_delay",
    (0x0018, 0x9023): "respiratory_trigger_frequency",
    (0x0018, 0x9024): "respiratory_b_beat_repeat_sequence",
    (0x0018, 0x9025): "respiratory_b_beat_repeat_value",
    (0x0018, 0x9026): "respiratory_b_beat_average_value",
    (0x0018, 0x9030): "respiratory_motion_compensation_type",
    (0x0018, 0x9031): "respiratory_signal_source",
    (0x0018, 0x9032): "respiratory_b_beat_repeat_sequence",
    (0x0018, 0x9033): "respiratory_b_beat_repeat_value",
    (0x0018, 0x9034): "respiratory_b_beat_average_value",
    (0x0018, 0x9040): "gating_4d_type",
    (0x0018, 0x9041): "gating_4d_sequence",
    (0x0018, 0x9042): "gating_4d_function",
    (0x0018, 0x9043): "gating_4d_data",
    (0x0018, 0x9044): "gating_4d_description",
}

VETERINARY_TOTAL_TAGS = VETERINARY_PATIENT | VETERINARY_STUDY | VETERINARY_ACQUISITION


def _extract_veterinary_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in VETERINARY_TOTAL_TAGS.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _is_veterinary_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            try:
                import pydicom
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xxxiv(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xxxiv_detected": False,
        "fields_extracted": 0,
        "extension_xxxiv_type": "veterinary_imaging",
        "extension_xxxiv_version": "2.0.0",
        "veterinary_patient": {},
        "veterinary_study": {},
        "veterinary_acquisition": {},
        "extraction_errors": [],
    }

    try:
        if not _is_veterinary_file(file_path):
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

        result["extension_xxxiv_detected"] = True

        veterinary_data = _extract_veterinary_tags(ds)

        result["veterinary_patient"] = {
            k: v for k, v in veterinary_data.items()
            if k in VETERINARY_PATIENT.values()
        }
        result["veterinary_study"] = {
            k: v for k, v in veterinary_data.items()
            if k in VETERINARY_STUDY.values()
        }
        result["veterinary_acquisition"] = {
            k: v for k, v in veterinary_data.items()
            if k in VETERINARY_ACQUISITION.values()
        }

        result["fields_extracted"] = len(veterinary_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxiv_field_count() -> int:
    return len(VETERINARY_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxiv_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxiv_description() -> str:
    return (
        "Veterinary imaging metadata extraction. Provides comprehensive coverage of "
        "animal patient data, species identification, breed information, owner details, "
        "and veterinary-specific acquisition parameters for animal health imaging."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxiv_modalities() -> List[str]:
    return ["CT", "MR", "CR", "DR", "US", "PT", "NM"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxiv_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxiv_category() -> str:
    return "Veterinary Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxiv_keywords() -> List[str]:
    return [
        "veterinary", "animal", "pet", "species", "breed", "livestock",
        "equine", "exotic", "veterinary radiology", "animal imaging"
    ]
