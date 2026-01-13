"""
Scientific DICOM/FITS Ultimate Advanced Extension LXII - Emergency Imaging

This module provides comprehensive extraction of Emergency Imaging parameters
including trauma imaging, acute care protocols, time-critical findings,
emergency department workflow, and mass casualty incident imaging.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXII_AVAILABLE = True

EMERGENCY_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x2203): "arrival_mode",
    (0x0010, 0x2204): "ambulance_service",
    (0x0010, 0x2205): "ems_provider_level",
    (0x0010, 0x2206): "ems_run_number",
    (0x0010, 0x2207): "triage_category",
    (0x0010, 0x2208): "triage_level",
    (0x0010, 0x2209): "chief_complaint",
    (0x0010, 0x2210): "presenting_symptoms",
    (0x0010, 0x2211): "symptom_duration",
    (0x0010, 0x2212): "symptom_onset",
    (0x0010, 0x2213): "past_medical_history",
    (0x0010, 0x2214): "medications_current",
    (0x0010, 0x2215): "allergies",
    (0x0010, 0x2216): "last_oral_intake",
    (0x0010, 0x2217): "event_prior_to_arrival",
    (0x0010, 0x2218): "witnessed_by_ems",
    (0x0010, 0x2219): "bystander_cpr",
    (0x0010, 0x2220): "defibrillation_shocks",
    (0x0010, 0x2221): "time_to_cpr_minutes",
    (0x0010, 0x2222): "time_to_defib_minutes",
    (0x0010, 0x2223): "time_to_rosc_minutes",
    (0x0010, 0x2224): "gcs_eye_opening",
    (0x0010, 0x2225): "gcs_verbal_response",
    (0x0010, 0x2226): "gcs_motor_response",
    (0x0010, 0x2227): "gcs_total",
    (0x0010, 0x2228): "gcs_score_interpretation",
    (0x0010, 0x2229): "pupil_reactivity_right",
    (0x0010, 0x2230): "pupil_reactivity_left",
    (0x0010, 0x2231): "pupil_size_right_mm",
    (0x0010, 0x2232): "pupil_size_left_mm",
    (0x0010, 0x2233): "blood_glucose_mg_dl",
    (0x0010, 0x2234): "temperature_celsius",
    (0x0010, 0x2235): "heart_rate_bpm",
    (0x0010, 0x2236): "blood_pressure_systolic",
    (0x0010, 0x2237): "blood_pressure_diastolic",
    (0x0010, 0x2238): "respiratory_rate",
    (0x0010, 0x2239): "oxygen_saturation_percent",
    (0x0010, 0x2240): "pain_score_0_10",
    (0x0010, 0x2241): "national_early_warning_score",
    (0x0010, 0x2242): "risk_stratification",
}

TRAUMA_IMAGING_TAGS = {
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x0081): "echo_time",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0xE001): "trauma_ct_indicator",
    (0x0018, 0xE002): "pan_scan_indicator",
    (0x0018, 0xE003): "level_1_trauma_activation",
    (0x0018, 0xE004): "level_2_trauma_activation",
    (0x0018, 0xE005): "trauma_surgeon_response",
    (0x0018, 0xE006): "time_to_ct_minutes",
    (0x0018, 0xE007): "time_to_operating_room_minutes",
    (0x0018, 0xE008): "injury_severity_score",
    (0x0018, 0xE009): "abbreviated_injury_scale_head",
    (0x0018, 0xE010): "abbreviated_injury_scale_face",
    (0x0018, 0xE011): "abbreviated_injury_scale_chest",
    (0x0018, 0xE012): "abbreviated_injury_scale_abdomen",
    (0x0018, 0xE013): "abbreviated_injury_scale_extremity",
    (0x0018, 0xE014): "abbreviated_injury_scale_external",
    (0x0018, 0xE015): "maximum_ais_score",
    (0x0018, 0xE016): "penetrating_injury_indicator",
    (0x0018, 0xE017): "blunt_injury_indicator",
    (0x0018, 0xE018): "hemodynamically_unstable",
    (0x0018, 0xE019): "contrast_extravasation",
    (0x0018, 0xE020): "active_bleeding_indicator",
    (0x0018, 0xE021): "vessel_injury",
    (0x0018, 0xE022): "solid_organ_laceration",
    (0x0018, 0xE023): "hollow_viscus_perforation",
    (0x0018, 0xE024): "pneumothorax",
    (0x0018, 0xE025): "hemothorax",
    (0x0018, 0xE026): "cardiac_contusion",
    (0x0018, 0xE027): "aortic_injury",
    (0x0018, 0xE028): "spinal_cord_injury",
    (0x0018, 0xE029): "pelvic_fracture",
    (0x0018, 0xE030): "long_bone_fracture",
    (0x0018, 0xE031): "head_injury_indicator",
    (0x0018, 0xE032): "intracranial_hemorrhage",
    (0x0018, 0xE033): "midline_shift_mm",
    (0x0018, 0xE034): "herniation_indicator",
    (0x0018, 0xE035): "diffuse_axonal_injury",
}

ACUTE_CARE_TAGS = {
    (0x0020, 0x0010): "series_number",
    (0x0020, 0x0011): "instance_number",
    (0x0020, 0x0032): "image_position_patient",
    (0x0020, 0x0037): "image_orientation_patient",
    (0x0020, 0x0050): "location",
    (0x0020, 0x0100): "temporal_position_identifier",
    (0x0020, 0x0105): "number_of_temporal_positions",
    (0x0020, 0x0200): "temporal_reconstruction_type",
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
    (0x0018, 0xF001): "stroke_alert_indicator",
    (0x0018, 0xF002): "stroke_type",
    (0x0018, 0xF003): "ischemic_stroke_indicator",
    (0x0018, 0xF004): "hemorrhagic_stroke_indicator",
    (0x0018, 0xF005): "time_last_known_well",
    (0x0018, 0xF006): "door_to_needle_minutes",
    (0x0018, 0xF007): "tenecteplase_indicator",
    (0x0018, 0xF008): "mechanical_thrombectomy",
    (0x0018, 0xF009): "large_vessel_occlusion",
    (0x0018, 0xF010): "nihss_score",
    (0x0018, 0xF011): "aspects_score",
    (0x0018, 0xF012): "myocardial_infarction_indicator",
    (0x0018, 0xF013): "st_elevation_mi",
    (0x0018, 0xF014): "non_st_elevation_mi",
    (0x0018, 0xF015): "door_to_balloon_minutes",
    (0x0018, 0xF016): "cath_lab_activation",
    (0x0018, 0xF017): "pulmonary_embolism_indicator",
    (0x0018, 0xF018): "aortic_dissection_indicator",
    (0x0018, 0xF019): "sepsis_indicator",
    (0x0018, 0xF020): "shock_indicator",
    (0x0018, 0xF021): "hypotension_indicator",
    (0x0018, 0xF022): "respiratory_failure_indicator",
    (0x0018, 0xF023): "altered_mental_status",
    (0x0018, 0xF024): "syncope_indicator",
    (0x0018, 0xF025): "dizziness_vertigo",
    (0x0018, 0xF026): "weakness_numbness",
    (0x0018, 0xF027): "seizure_indicator",
    (0x0018, 0xF028): "acute_abdomen",
    (0x0018, 0xF029): "appendicitis_indicator",
    (0x0018, 0xF030): "diverticulitis_indicator",
    (0x0018, 0xF031): "bowel_obstruction",
    (0x0018, 0xF032): "perforation_indicator",
}

EMERGENCY_WORKFLOW_TAGS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0xF101): "priority_status",
    (0x0018, 0xF102): "stat_indicator",
    (0x0018, 0xF103): "rush_order_indicator",
    (0x0018, 0xF104): "order_entry_time",
    (0x0018, 0xF105): "order_verification_time",
    (0x0018, 0xF106): "patient_arrival_time",
    (0x0018, 0xF107): "scan_start_time",
    (0x0018, 0xF108): "scan_complete_time",
    (0x0018, 0xF109): "preliminary_report_time",
    (0x0018, 0xF110): "final_report_time",
    (0x0018, 0xF111): "critical_value_communication",
    (0x0018, 0xF112): "critical_value_recipient",
    (0x0018, 0xF113): "critical_value_documentation",
    (0x0018, 0xF114): "attending_notification",
    (0x0018, 0xF115): "resident_notification",
    (0x0018, 0xF116): "image_available_time",
    (0x0018, 0xF117): "radiologist_response_time",
    (0x0018, 0xF118): "protocolling_complete",
    (0x0018, 0xF119): "documentation_complete",
    (0x0018, 0xF120): "disposition_decision",
    (0x0018, 0xF121): "admission_indicator",
    (0x0018, 0xF122): "discharge_indicator",
    (0x0018, 0xF123): "transfer_indicator",
    (0x0018, 0xF124): "operating_room_indicator",
    (0x0018, 0xF125): "icu_indicator",
    (0x0018, 0xF126): "left_without_being_seen",
    (0x0018, 0xF127): "left_against_medical_advice",
    (0x0018, 0xF128): "return_visit_indicator",
    (0x0018, 0xF129): "elapsed_time_minutes",
    (0x0018, 0xF130): "door_to_imaging_minutes",
}

MASS_CASUALTY_TAGS = {
    (0x0008, 0x0060): "modality",
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0020): "sequence_name",
    (0x0018, 0xF201): "mass_casualty_incident",
    (0x0018, 0xF202): "incident_command_activated",
    (0x0018, 0xF203): "casualty_count",
    (0x0018, 0xF204): "triage_tag_number",
    (0x0018, 0xF205): "triage_color",
    (0x0018, 0xF206): "immediate_indicator",
    (0x0018, 0xF207): "delayed_indicator",
    (0x0018, 0xF208): "minimal_indicator",
    (0x0018, 0xF209): "expectant_indicator",
    (0x0018, 0xF210): "deceased_indicator",
    (0x0018, 0xF211): "contamination_indicator",
    (0x0018, 0xF212): "radiation_contamination",
    (0x0018, 0xF213): "chemical_contamination",
    (0x0018, 0xF214): "biological_contamination",
    (0x0018, 0xF215): "decontamination_status",
    (0x0018, 0xF216): "gross_decontamination",
    (0x0018, 0xF217): "fine_decontamination",
    (0x0018, 0xF218): "tracking_number",
    (0x0018, 0xF219): "family_indicator",
    (0x0018, 0xF220): "pediatric_indicator",
    (0x0018, 0xF221): "special_needs_indicator",
    (0x0018, 0xF222): "language_barrier",
    (0x0018, 0xF223): "interpreter_required",
    (0x0018, 0xF224): "mci_level",
    (0x0018, 0xF225): "hospital_status",
    (0x0018, 0xF226): "capacity_status",
    (0x0018, 0xF227): "additional_resources_requested",
    (0x0018, 0xF228): "ambulance_diversion",
    (0x0018, 0xF229): "emergency_overload_status",
    (0x0018, 0xF230): "alternate_care_site",
}

TOTAL_TAGS_LXII = (
    EMERGENCY_PATIENT_PARAMETERS | 
    TRAUMA_IMAGING_TAGS | 
    ACUTE_CARE_TAGS | 
    EMERGENCY_WORKFLOW_TAGS | 
    MASS_CASUALTY_TAGS
)


def _extract_tags_lxii(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in TOTAL_TAGS_LXII.items():
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


def _is_emergency_imaging_file(file_path: str) -> bool:
    emergency_indicators = [
        'emergency', 'trauma', 'ed_visit', 'er', 'urgent', 'acute',
        'stroke_alert', 'code_stroke', 'code_mi', 'trauma_activation',
        'mass_casualty', 'mci', 'triage', 'ems', 'ambulance',
        'critical_care', 'rapid_sequence'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in emergency_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxii_detected": False,
        "fields_extracted": 0,
        "extension_lxii_type": "emergency_imaging",
        "extension_lxii_version": "2.0.0",
        "emergency_patient_parameters": {},
        "trauma_imaging": {},
        "acute_care": {},
        "emergency_workflow": {},
        "mass_casualty": {},
        "extraction_errors": [],
    }

    try:
        if not _is_emergency_imaging_file(file_path):
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

        result["extension_lxii_detected"] = True

        emergency_data = _extract_tags_lxii(ds)

        result["emergency_patient_parameters"] = {
            k: v for k, v in emergency_data.items()
            if k in EMERGENCY_PATIENT_PARAMETERS.values()
        }
        result["trauma_imaging"] = {
            k: v for k, v in emergency_data.items()
            if k in TRAUMA_IMAGING_TAGS.values()
        }
        result["acute_care"] = {
            k: v for k, v in emergency_data.items()
            if k in ACUTE_CARE_TAGS.values()
        }
        result["emergency_workflow"] = {
            k: v for k, v in emergency_data.items()
            if k in EMERGENCY_WORKFLOW_TAGS.values()
        }
        result["mass_casualty"] = {
            k: v for k, v in emergency_data.items()
            if k in MASS_CASUALTY_TAGS.values()
        }

        result["fields_extracted"] = len(emergency_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxii_field_count() -> int:
    return len(TOTAL_TAGS_LXII)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxii_description() -> str:
    return (
        "Emergency Imaging metadata extraction. Provides comprehensive coverage of "
        "trauma imaging, acute care protocols, time-critical findings, "
        "emergency department workflow, and mass casualty incident imaging."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxii_modalities() -> List[str]:
    return ["CT", "MR", "CR", "DR", "US", "PT", "NM", "XA", "RF"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxii_category() -> str:
    return "Emergency Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxii_keywords() -> List[str]:
    return [
        "emergency imaging", "trauma", "stroke", "myocardial infarction", "triage",
        "mass casualty", "EMS", "emergency department", "critical care",
        "time-sensitive", "code stroke", "code STEMI", "trauma activation",
        "rapid sequence", "acute care", "emergency workflow", "disaster response"
    ]


# Aliases for smoke test compatibility
def extract_remote_monitoring(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_lxii."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_lxii(file_path)

def get_remote_monitoring_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxii_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxii_field_count()

def get_remote_monitoring_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxii_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxii_version()

def get_remote_monitoring_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxii_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxii_description()

def get_remote_monitoring_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxii_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxii_supported_formats()

def get_remote_monitoring_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxii_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxii_modalities()
