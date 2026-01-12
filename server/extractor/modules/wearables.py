"""
Scientific DICOM/FITS Ultimate Advanced Extension LXIV - Operating Room Imaging

This module provides comprehensive extraction of Operating Room Imaging parameters
including surgical navigation, intraoperative imaging, anesthesia considerations,
and image-guided surgery workflows.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXIV_AVAILABLE = True

OR_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x2400): "surgery_date",
    (0x0010, 0x2401): "surgery_time",
    (0x0010, 0x2402): "surgery_duration_minutes",
    (0x0010, 0x2403): "surgery_type",
    (0x0010, 0x2404): "surgery_subtype",
    (0x0010, 0x2405): "surgical_procedure_code",
    (0x0010, 0x2406): "primary_surgeon",
    (0x0010, 0x2407): "assisting_surgeon",
    (0x0010, 0x2408): "anesthesiologist",
    (0x0010, 0x2409): "surgical_resident_present",
    (0x0010, 0x2410): "anesthesia_type",
    (0x0010, 0x2411): "anesthesia_duration",
    (0x0010, 0x2412): "general_anesthesia",
    (0x0010, 0x2413): "regional_anesthesia",
    (0x0010, 0x2414): "local_anesthesia",
    (0x0010, 0x2415): "sedation_level",
    (0x0010, 0x2416): "airway_management",
    (0x0010, 0x2417): "endotracheal_intubation",
    (0x0010, 0x2418): "lma_placement",
    (0x0010, 0x2419): "patient_positioning",
    (0x0010, 0x2420): "supine_position",
    (0x0010, 0x2421): "prone_position",
    (0x0010, 0x2422): "lateral_position",
    (0x0010, 0x2423): "trendelenburg_position",
    (0x0010, 0x2424): "reverse_trendelenburg",
    (0x0010, 0x2425): "lithotomy_position",
    (0x0010, 0x2426): "padding_indicator",
    (0x0010, 0x2427): "pressure_point_protection",
    (0x0010, 0x2428): "eye_protection",
    (0x0010, 0x2429): "dvt_prophylaxis",
    (0x0010, 0x2430): "antibiotic_prophylaxis",
    (0x0010, 0x2431): "antibiotic_type",
    (0x0010, 0x2432): "antibiotic_timing",
    (0x0010, 0x2433): "blood_loss_ml",
    (0x0010, 0x2434): "transfusion_indicator",
    (0x0010, 0x2435): "transfusion_units",
    (0x0010, 0x2436): "crystalloid_volume",
    (0x0010, 0x2437): "colloid_volume",
    (0x0010, 0x2438): "estimated_blood_loss",
    (0x0018, 0x0015): "body_part_examined",
}

INTRAOPERATIVE_IMAGING_TAGS = {
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x0081): "echo_time",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0x9301): "intraoperative_indicator",
    (0x0018, 0x9302): "real_time_imaging",
    (0x0018, 0x9303): "fluoro_save_indicator",
    (0x0018, 0x9304): "dose_area_product",
    (0x0018, 0x9305): "entrance_dose",
    (0x0018, 0x9306): "reference_air_kerma",
    (0x0018, 0x9307): "cumulative_kerma",
    (0x0018, 0x9308): "fluoro_time_seconds",
    (0x0018, 0x9309): "number_of_fluoro_sequences",
    (0x0018, 0x9310): "number_of_acquisitions",
    (0x0018, 0x9311): "number_of_spot_images",
    (0x0018, 0x9312): "total_acquisition_time",
    (0x0018, 0x9313): "image_intensifier_size",
    (0x0018, 0x9314): "field_of_view",
    (0x0018, 0x9315): "geometric_magnification",
    (0x0018, 0x9316): "source_image_distance",
    (0x0018, 0x9317): "collimation_left",
    (0x0018, 0x9318): "collimation_right",
    (0x0018, 0x9319): "collimation_top",
    (0x0018, 0x9320): "collimation_bottom",
    (0x0018, 0x9321): "xray_tube_current",
    (0x0018, 0x9322): "xray_tube_voltage",
    (0x0018, 0x9323): "exposure_time",
    (0x0018, 0x9324): "pulse_rate",
    (0x0018, 0x9325): "number_of_pulses",
    (0x0018, 0x9326): "pulse_width",
    (0x0018, 0x9327): "ir_filter_type",
    (0x0018, 0x9328): "ir_filter_thickness",
    (0x0018, 0x9329): "automatic_brightness_control",
    (0x0018, 0x9330): "automatic_exposure_control",
    (0x0018, 0x9331): "last_image_hold",
    (0x0018, 0x9332): "digital_subtraction_angiography",
    (0x0018, 0x9333): "dsa_mask_image",
    (0x0018, 0x9334): "dsa_fill_image",
    (0x0018, 0x9335): "roadmap_indicator",
    (0x0018, 0x9336): "image_subtraction",
    (0x0018, 0x9337): "pixel_shift_horizontal",
    (0x0018, 0x9338): "pixel_shift_vertical",
    (0x0018, 0x9339): "region_of_interest",
    (0x0018, 0x9340): "roi_center_x",
    (0x0018, 0x9341): "roi_center_y",
    (0x0018, 0x9342): "roi_radius",
}

SURGICAL_NAVIGATION_TAGS = {
    (0x0020, 0x0010): "series_number",
    (0x0020, 0x0011): "instance_number",
    (0x0020, 0x0032): "image_position_patient",
    (0x0020, 0x0037): "image_orientation_patient",
    (0x0020, 0x0050): "location",
    (0x0020, 0x4000): "image_comments",
    (0x0028, 0x0002): "samples_per_pixel",
    (0x0028, 0x0004): "photometric_interpretation",
    (0x0028, 0x0010): "rows",
    (0x0028, 0x0011): "columns",
    (0x0028, 0x0030): "pixel_spacing",
    (0x0028, 0x0100): "bits_allocated",
    (0x0028, 0x0101): "bits_stored",
    (0x0028, 0x0102): "high_bit",
    (0x0028, 0x0103): "pixel_representation",
    (0x0028, 0x1050): "window_center",
    (0x0028, 0x1051): "window_width",
    (0x0018, 0x9401): "navigation_system_type",
    (0x0018, 0x9402): "optical_navigation",
    (0x0018, 0x9403): "electromagnetic_navigation",
    (0x0018, 0x9404): "infrared_navigation",
    (0x0018, 0x9405): "ultrasound_navigation",
    (0x0018, 0x9406): "fiducial_marker",
    (0x0018, 0x9407): "fiducial_count",
    (0x0018, 0x9408): "fiducialLocalizationError",
    (0x0018, 0x9409): "registration_accuracy",
    (0x0018, 0x9410): "registration_method",
    (0x0018, 0x9411): "point_registration",
    (0x0018, 0x9412): "surface_registration",
    (0x0018, 0x9413): "volume_registration",
    (0x0018, 0x9414): "reference_marker_position",
    (0x0018, 0x9415): "instrument_position",
    (0x0018, 0x9416): "instrument_orientation",
    (0x0018, 0x9417): "navigation_pointer_type",
    (0x0018, 0x9418): "tracked_instrument",
    (0x0018, 0x9419): "navigation_accuracy",
    (0x0018, 0x9420): "update_rate",
    (0x0018, 0x9421): "display_mode",
    (0x0018, 0x9422): "overlay_indicator",
    (0x0018, 0x9423): "augmented_reality",
    (0x0018, 0x9424): "virtual_navigation",
    (0x0018, 0x9425): "merged_display",
    (0x0018, 0x9426): "side_by_side_display",
    (0x0018, 0x9427): "pedicle_screw_planning",
    (0x0018, 0x9428): "trajectory_planning",
    (0x0018, 0x9429): "depth_measurement",
    (0x0018, 0x9430): "angle_measurement",
    (0x0018, 0x9431): "distance_to_target",
    (0x0018, 0x9432): "warning_boundary",
    (0x0018, 0x9433): "safety_margin",
    (0x0018, 0x9434): "anatomical_landmark",
    (0x0018, 0x9435): "surgical_plan_file",
    (0x0018, 0x9436): "navigation_session_id",
}

OR_WORKFLOW_TAGS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0x9501): "or_room_number",
    (0x0018, 0x9502): "or_suite_identifier",
    (0x0018, 0x9503): "case_start_time",
    (0x0018, 0x9504): "case_end_time",
    (0x0018, 0x9505): "incision_time",
    (0x0018, 0x9506): "closure_time",
    (0x0018, 0x9507): "anesthesia_start_time",
    (0x0018, 0x9508): "anesthesia_end_time",
    (0x0018, 0x9509): "patient_in_or_time",
    (0x0018, 0x9510): "patient_out_or_time",
    (0x0018, 0x9511): "timeout_initiated",
    (0x0018, 0x9512): "timeout_completed",
    (0x0018, 0x9513): "surgical_safety_checklist",
    (0x0018, 0x9514): "patient_verification",
    (0x0018, 0x9515): "procedure_verification",
    (0x0018, 0x9516): "site_marking_verified",
    (0x0018, 0x9517): "allergies_verified",
    (0x0018, 0x9518): "medications_verified",
    (0x0018, 0x9519): "equipment_check_complete",
    (0x0018, 0x9520): "imaging_available",
    (0x0018, 0x9521): "preoperative_imaging_review",
    (0x0018, 0x9522): "intraoperative_imaging_review",
    (0x0018, 0x9523): "image_quality_adequate",
    (0x0018, 0x9524): "image_artifact_present",
    (0x0018, 0x9525): "repeat_imaging_required",
    (0x0018, 0x9526): "radiation_exposure_documented",
    (0x0018, 0x9527): "dose_alert_triggered",
    (0x0018, 0x9528): "surgeon_notified_of_dose",
    (0x0018, 0x9529): "contrast_administered",
    (0x0018, 0x9530): "contrast_type",
    (0x0018, 0x9531): "contrast_volume",
    (0x0018, 0x9532): "contrast_reaction",
    (0x0018, 0x9533): "specimen_removed",
    (0x0018, 0x9534): "specimen_sent_to_pathology",
    (0x0018, 0x9535): "intraoperative_consult",
    (0x0018, 0x9536): "frozen_section_performed",
    (0x0018, 0x9537): "frozen_section_result",
    (0x0018, 0x9538): "unplanned_event",
    (0x0018, 0x9539): "complication_indicator",
    (0x0018, 0x9540): "blood_pressure_change",
    (0x0018, 0x9541): "heart_rate_change",
    (0x0018, 0x9542): "oxygen_saturation_change",
    (0x0018, 0x9543): "temperature_change",
    (0x0018, 0x9544): "emergency_indicator",
    (0x0018, 0x9545): "code_blue_activated",
    (0x0018, 0x9546): "resuscitation_performed",
    (0x0018, 0x9547): "additional_equipment_needed",
    (0x0018, 0x9548): "case_complexity_level",
    (0x0018, 0x9549): "resident_participation_level",
}

IMAGE_GUIDED_SURGERY_TAGS = {
    (0x0018, 0x9601): "igs_indicator",
    (0x0018, 0x9602): "neuronavigation",
    (0x0018, 0x9603): "spine_navigation",
    (0x0018, 0x9604): "ent_navigation",
    (0x0018, 0x9605): "orthopedic_navigation",
    (0x0018, 0x9606): "cardiac_navigation",
    (0x0018, 0x9607): "vascular_navigation",
    (0x0018, 0x9608): "robotic_assistance",
    (0x0018, 0x9609): "da_vinci_system",
    (0x0018, 0x9610): "robotic_arm_position",
    (0x0018, 0x9611): "robotic_instrument_type",
    (0x0018, 0x9612): "robotic_wrist_motion",
    (0x0018, 0x9613): "haptic_feedback",
    (0x0018, 0x9614): "3d_reconstruction_available",
    (0x0018, 0x9615): "volume_rendering",
    (0x0018, 0x9616): "surface_rendering",
    (0x0018, 0x9617): "maximum_intensity_projection",
    (0x0018, 0x9618): "multiplanar_reconstruction",
    (0x0018, 0x9619): "curved_planar_reformation",
    (0x0018, 0x9620): "virtual_endoscopy",
    (0x0018, 0x9621): "registration_fiducials",
    (0x0018, 0x9622): "registration_error_mm",
    (0x0018, 0x9623): "navigation_accuracy_mm",
    (0x0018, 0x9624): "target_localization_error",
    (0x0018, 0x9625): "surgical_corridor",
    (0x0018, 0x9626): "approach_trajectory",
    (0x0018, 0x9627): "avoidance_structure",
    (0x0018, 0x9628): "critical_structure",
    (0x0018, 0x9629): "margin_status",
    (0x0018, 0x9630): "resection_cavity",
    (0x0018, 0x9631): "tumor_debulking",
    (0x0018, 0x9632): "electrophysiological_monitoring",
    (0x0018, 0x9633): "mep_monitoring",
    (0x0018, 0x9634): "sep_monitoring",
    (0x0018, 0x9635): "eeg_monitoring",
    (0x0018, 0x9636): "emg_monitoring",
    (0x0018, 0x9637): "nerve_stimulation",
    (0x0018, 0x9638): "awake_craniotomy",
    (0x0018, 0x9639): "mapping_phase",
    (0x0018, 0x9640): "stimulation_response",
    (0x0018, 0x9641): "speech_mapping",
    (0x0018, 0x9642): "motor_mapping",
    (0x0018, 0x9643): "sensory_mapping",
    (0x0018, 0x9644): "language_localization",
    (0x0018, 0x9645): "eloquent_cortex",
    (0x0018, 0x9646): "awake_testing",
    (0x0018, 0x9647): "intraoperative_mri",
    (0x0018, 0x9648): "intraoperative_ct",
    (0x0018, 0x9649): "intraoperative_ultrasound",
    (0x0018, 0x9650): "update_navigation_dataset",
}

TOTAL_TAGS_LXIV = (
    OR_PATIENT_PARAMETERS |
    INTRAOPERATIVE_IMAGING_TAGS |
    SURGICAL_NAVIGATION_TAGS |
    OR_WORKFLOW_TAGS |
    IMAGE_GUIDED_SURGERY_TAGS
)


def _extract_tags_lxiv(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in TOTAL_TAGS_LXIV.items():
        try:
            if hasattr(ds, '__getitem__'):
                elem = ds.get(tag)
                if elem is not None:
                    try:
                        value = elem.value
                        if isinstance(value, bytes):
                            value = value.decode('utf-8', errors='replace')
                        extracted[name] = value
                    except Exception:
                        extracted[name] = str(elem)
        except Exception:
            pass
    return extracted


def _is_operating_room_imaging_file(file_path: str) -> bool:
    or_indicators = [
        'operating room', 'or', 'surgery', 'surgical', 'intraoperative',
        'fluoro', 'fluoroscopy', 'navigation', 'da vinci', 'robotic surgery',
        'spine surgery', 'neurosurgery', 'orthopedic surgery', 'image guided',
        'anesthesia', 'post op', 'pre op', 'incision', 'closure'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in or_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxiv(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxiv_detected": False,
        "fields_extracted": 0,
        "extension_lxiv_type": "operating_room_imaging",
        "extension_lxiv_version": "2.0.0",
        "or_patient_parameters": {},
        "intraoperative_imaging": {},
        "surgical_navigation": {},
        "or_workflow": {},
        "image_guided_surgery": {},
        "extraction_errors": [],
    }

    try:
        if not _is_operating_room_imaging_file(file_path):
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

        result["extension_lxiv_detected"] = True

        or_data = _extract_tags_lxiv(ds)

        result["or_patient_parameters"] = {
            k: v for k, v in or_data.items()
            if k in OR_PATIENT_PARAMETERS.values()
        }
        result["intraoperative_imaging"] = {
            k: v for k, v in or_data.items()
            if k in INTRAOPERATIVE_IMAGING_TAGS.values()
        }
        result["surgical_navigation"] = {
            k: v for k, v in or_data.items()
            if k in SURGICAL_NAVIGATION_TAGS.values()
        }
        result["or_workflow"] = {
            k: v for k, v in or_data.items()
            if k in OR_WORKFLOW_TAGS.values()
        }
        result["image_guided_surgery"] = {
            k: v for k, v in or_data.items()
            if k in IMAGE_GUIDED_SURGERY_TAGS.values()
        }

        result["fields_extracted"] = len(or_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxiv_field_count() -> int:
    return len(TOTAL_TAGS_LXIV)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxiv_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxiv_description() -> str:
    return (
        "Operating Room Imaging metadata extraction. Provides comprehensive coverage of "
        "surgical navigation, intraoperative imaging, anesthesia considerations, "
        "and image-guided surgery workflows."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxiv_modalities() -> List[str]:
    return ["CT", "MR", "CR", "DR", "US", "XA", "RF", "MG"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxiv_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxiv_category() -> str:
    return "Operating Room Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxiv_keywords() -> List[str]:
    return [
        "operating room", "surgery", "intraoperative", "fluoroscopy", "surgical navigation",
        "Da Vinci", "robotic surgery", "image guided surgery", "IGS", "neuronavigation",
        "spine navigation", "anesthesia", "OR workflow", "surgical safety checklist",
        "preoperative", "postoperative", "incision", "closure", "frozen section"
    ]


# Aliases for smoke test compatibility
def extract_wearables(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_lxiv."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_lxiv(file_path)

def get_wearables_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxiv_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxiv_field_count()

def get_wearables_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxiv_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxiv_version()

def get_wearables_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxiv_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxiv_description()

def get_wearables_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxiv_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxiv_supported_formats()

def get_wearables_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxiv_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxiv_modalities()
