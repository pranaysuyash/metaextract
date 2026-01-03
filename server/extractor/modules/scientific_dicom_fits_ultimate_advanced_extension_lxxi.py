"""
Scientific DICOM/FITS Ultimate Advanced Extension LXXI - Trauma Imaging II

This module provides comprehensive extraction of Trauma Imaging parameters
including injury classification, ATLS protocols, trauma team activation,
and multidisciplinary trauma care coordination.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXI_AVAILABLE = True

TRAUMA_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x3101): "trauma_date",
    (0x0010, 0x3102): "trauma_time",
    (0x0010, 0x3103): "injury_datetime",
    (0x0010, 0x3104): "arrival_datetime",
    (0x0010, 0x3105): "primary_survey_complete",
    (0x0010, 0x3106): "secondary_survey_complete",
    (0x0010, 0x3107): "tertiary_survey_complete",
    (0x0010, 0x3108): "trauma_team_activation_level",
    (0x0010, 0x3109): "level_1_activation",
    (0x0010, 0x3110): "level_2_activation",
    (0x0010, 0x3111): "level_3_activation",
    (0x0010, 0x3112): "trauma_surgeon_presence",
    (0x0010, 0x3113): "neurosurgeon_presence",
    (0x0010, 0x3114): "orthopedic_surgeon_presence",
    (0x0010, 0x3115): "anesthesiologist_presence",
    (0x0010, 0x3116): "nurse_presence",
    (0x0010, 0x3117): "rt_presence",
    (0x0010, 0x3118): "trauma_mechanism",
    (0x0010, 0x3119): "motor_vehicle_collision",
    (0x0010, 0x3120): "fall_from_height",
    (0x0010, 0x3121): "penetrating_injury",
    (0x0010, 0x3122): "blunt_injury",
    (0x0010, 0x3123): "assault",
    (0x0010, 0x3124): "burn_injury",
    (0x0010, 0x3125): "drowning",
    (0x0010, 0x3126): "electrocution",
    (0x0010, 0x3127): "environmental_exposure",
    (0x0010, 0x3128): "work_related_injury",
    (0x0010, 0x3129): "sports_injury",
    (0x0010, 0x3130): "home_injury",
    (0x0010, 0x3131): "motorcycle_collision",
    (0x0010, 0x3132): "pedestrian_struck",
    (0x0010, 0x3133): "bicycle_collision",
    (0x0010, 0x3134): "fall_on_stairs",
    (0x0010, 0x3135): "fall_on_level",
    (0x0010, 0x3136): "height_of_fall_feet",
    (0x0010, 0x3137): "speed_of_impact_mph",
    (0x0010, 0x3138): "ejection_from_vehicle",
    (0x0010, 0x3139): "rollover_event",
    (0x0010, 0x3140): "helmet_use_indicator",
    (0x0010, 0x3141): "seatbelt_use_indicator",
    (0x0010, 0x3142): "airbag_deployment",
    (0x0010, 0x3143): "entrapped_indicator",
    (0x0010, 0x3144): "extrication_time_minutes",
    (0x0010, 0x3145): "ambulance_arrival_time",
    (0x0010, 0x3146): "helicopter_arrival_time",
    (0x0010, 0x3147): "scene_to_hospital_minutes",
    (0x0010, 0x3148): "interfacility_transfer",
    (0x0010, 0x3149): "transferring_facility",
    (0x0010, 0x3150): "gcs_eye_opening",
    (0x0010, 0x3151): "gcs_verbal_response",
    (0x0010, 0x3152): "gcs_motor_response",
    (0x0010, 0x3153): "gcs_total_score",
    (0x0010, 0x3154): "gcs_category",
}

INJURY_CLASSIFICATION_TAGS = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0xF301): "injury_diagnosis",
    (0x0018, 0xF302): "ais_code",
    (0x0018, 0xF303): "ais_severity",
    (0x0018, 0xF304): "ais_body_region",
    (0x0018, 0xF305): "iss_score",
    (0x0018, 0xF306): "iss_body_region_1",
    (0x0018, 0xF307): "iss_body_region_2",
    (0x0018, 0xF308): "iss_body_region_3",
    (0x0018, 0xF309): "niss_score",
    (0x0018, 0xF310): "injury_severity_score",
    (0x0018, 0xF311): "maximum_ais",
    (0x0018, 0xF312): "abbreviated_injury_scale",
    (0x0018, 0xF313): "head_injury_indicator",
    (0x0018, 0xF314): "face_injury_indicator",
    (0x0018, 0xF315): "neck_injury_indicator",
    (0x0018, 0xF316): "chest_injury_indicator",
    (0x0018, 0xF317): "abdomen_injury_indicator",
    (0x0018, 0xF318): "spine_injury_indicator",
    (0x0018, 0xF319): "extremity_injury_indicator",
    (0x0018, 0xF320): "external_injury_indicator",
    (0x0018, 0xF321): "pelvic_fracture_indicator",
    (0x0018, 0xF322): "hemorrhage_indicator",
    (0x0018, 0xF323): "tension_pneumothorax",
    (0x0018, 0xF324): "cardiac_tamponade",
    (0x0018, 0xF325): "open_fracture",
    (0x0018, 0xF326): "compartment_syndrome",
    (0x0018, 0xF327): "spinal_cord_injury",
    (0x0018, 0xF328): "traumatic_brain_injury",
    (0x0018, 0xF329): "tbi_severity",
    (0x0018, 0xF330): "mild_tbi",
    (0x0018, 0xF331): "moderate_tbi",
    (0x0018, 0xF332): "severe_tbi",
    (0x0018, 0xF333): "penetrating_head_injury",
    (0x0018, 0xF334): "blunt_head_injury",
    (0x0018, 0xF335): "intracranial_hemorrhage",
    (0x0018, 0xF336): "subdural_hematoma",
    (0x0018, 0xF337): "epidural_hematoma",
    (0x0018, 0xF338): "subarachnoid_hemorrhage",
    (0x0018, 0xF339): "intracerebral_hemorrhage",
    (0x0018, 0xF340): "cerebral_contusion",
    (0x0018, 0xF341): "diffuse_axonal_injury",
    (0x0018, 0xF342): "skull_fracture",
    (0x0018, 0xF343): "basilar_skull_fracture",
    (0x0018, 0xF344): "facial_fracture",
    (0x0018, 0xF345): "cervical_spine_fracture",
    (0x0018, 0xF346): "thoracic_spine_fracture",
    (0x0018, 0xF347): "lumbar_spine_fracture",
    (0x0018, 0xF348): "pelvic_fracture",
    (0x0018, 0xF349): "acetabular_fracture",
    (0x0018, 0xF350): "long_bone_fracture",
    (0x0018, 0xF351): "femur_fracture",
    (0x0018, 0xF352): "tibia_fracture",
    (0x0018, 0xF353): "humerus_fracture",
    (0x0018, 0xF354): "rib_fracture",
    (0x0018, 0xF355): "sternal_fracture",
    (0x0018, 0xF356): "scapular_fracture",
    (0x0018, 0xF357): "clavicular_fracture",
}

ATLS_PROTOCOL_TAGS = {
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
    (0x0018, 0xF401): "airway_management",
    (0x0018, 0xF402): "endotracheal_intubation_performed",
    (0x0018, 0xF403): "rapid_sequence_intubation",
    (0x0018, 0xF404): "difficult_airway",
    (0x0018, 0xF405): "cricothyrotomy",
    (0x0018, 0xF406): "surgical_airway",
    (0x0018, 0xF407): "supraglottic_airway",
    (0x0018, 0xF408): "nasal_airway",
    (0x0018, 0xF409): "oral_airway",
    (0x0018, 0xF410): "breathing_assessment",
    (0x0018, 0xF411): "chest_tube_placement",
    (0x0018, 0xF412): "chest_tube_size_fr",
    (0x0018, 0xF413): "chest_tube_location",
    (0x0018, 0xF414): "tube_thoracostomy",
    (0x0018, 0xF415): "needle_decompression",
    (0x0018, 0xF416): "ocd_indicator",
    (0x0018, 0xF417): "circulation_assessment",
    (0x0018, 0xF418): "venous_access_site",
    (0x0018, 0xF419): "central_line_placement",
    (0x0018, 0xF420): "arterial_line_placement",
    (0x0018, 0xF421): "intraosseous_access",
    (0x0018, 0xF422): "blood_transfusion",
    (0x0018, 0xF423): "prbc_units",
    (0x0018, 0xF424): "ffp_units",
    (0x0018, 0xF425): "platelet_units",
    (0x0018, 0xF426): "cryoprecipitate_units",
    (0x0018, 0xF427): "massive_transfusion_protocol",
    (0x0018, 0xF428): "txa_administered",
    (0x0018, 0xF429): "tranexamic_acid_dose",
    (0x0018, 0xF430): "disability_assessment",
    (0x0018, 0xF431): "pupil_examination",
    (0x0018, 0xF432): "left_pupil_size",
    (0x0018, 0xF433): "right_pupil_size",
    (0x0018, 0xF434): "left_pupil_reactivity",
    (0x0018, 0xF435): "right_pupil_reactivity",
    (0x0018, 0xF436): "motor_exam",
    (0x0018, 0xF437): "left_motor_response",
    (0x0018, 0xF438): "right_motor_response",
    (0x0018, 0xF439): "gcs_motor_6",
    (0x0018, 0xF440): "exposure_assessment",
    (0x0018, 0xF441): "log_roll_performed",
    (0x0018, 0xF442): "full_exposure_complete",
    (0x0018, 0xF443): "temperature_management",
    (0x0018, 0xF444): "hypothermia_indicator",
    (0x0018, 0xF445): "warming_device",
    (0x0018, 0xF446): "warming_method",
}

TRAUMA_IMAGING_PROTOCOLS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0xF501): "pan scan_protocol",
    (0x0018, 0xF502): "whole_body_ct",
    (0x0018, 0xF503): "head_ct_protocol",
    (0x0018, 0xF504): "face_ct_protocol",
    (0x0018, 0xF505): "neck_ct_protocol",
    (0x0018, 0xF506): "chest_ct_protocol",
    (0x0018, 0xF507): "abdomen_ct_protocol",
    (0x0018, 0xF508): "pelvis_ct_protocol",
    (0x0018, 0xF509): "spine_ct_protocol",
    (0x0018, 0xF510): "extremity_ct_protocol",
    (0x0018, 0xF511): "ct_angiography_head",
    (0x0018, 0xF512): "ct_angiography_chest",
    (0x0018, 0xF513): "ct_angiography_abdomen",
    (0x0018, 0xF514): "ct_angiography_pelvis",
    (0x0018, 0xF515): "contrast_enhanced",
    (0x0018, 0xF516): "non_contrast_ct",
    (0x0018, 0xF517): "triple_contrast_ct",
    (0x0018, 0xF518): "dual_contrast_ct",
    (0x0018, 0xF519): "contrast_volume_ml",
    (0x0018, 0xF520): "contrast_injection_rate",
    (0x0018, 0xF521): "delay_time_seconds",
    (0x0018, 0xF522): "arterial_phase",
    (0x0018, 0xF523): "venous_phase",
    (0x0018, 0xF524): "delayed_phase",
    (0x0018, 0xF525): "recon_kernel_head",
    (0x0018, 0xF526): "recon_kernel_body",
    (0x0018, 0xF527): "thin_slice_reconstruction",
    (0x0018, 0xF528): "thick_slice_reconstruction",
    (0x0018, 0xF529): "multiplanar_reformation",
    (0x0018, 0xF530): "3d_reconstruction",
    (0x0018, 0xF531): "volume_rendering",
    (0x0018, 0xF532): "maximum_intensity_projection",
    (0x0018, 0xF533): "minimum_intensity_projection",
    (0x0018, 0xF534): "trauma_series_complete",
    (0x0018, 0xF535): "radiology_ready_time",
    (0x0018, 0xF536): "preliminary_report_time",
    (0x0018, 0xF537): "final_report_time",
    (0x0018, 0xF538): "critical_findings_communication",
    (0x0018, 0xF539): "attending_notification_time",
    (0x0018, 0xF540): "surgeon_notification_time",
    (0x0018, 0xF541): "time_to_ct_minutes",
    (0x0018, 0xF542): "time_to_OR_minutes",
    (0x0018, 0xF543): "door_to_needle_time",
    (0x0018, 0xF544): "door_to_angio_time",
}

TRAUMA_OUTCOMES_TAGS = {
    (0x0018, 0xF601): "emergency_surgery_indicator",
    (0x0018, 0xF602): "or_procedure_performed",
    (0x0018, 0xF603): "damage_control_surgery",
    (0x0018, 0xF604): "definitive_surgery",
    (0x0018, 0xF605): "operative_time_minutes",
    (0x0018, 0xF606): "icu_admission",
    (0x0018, 0xF607): "icu_length_of_stay_days",
    (0x0018, 0xF608): "hospital_length_of_stay_days",
    (0x0018, 0xF609): "ventilator_days",
    (0x0018, 0xF610): "vasopressor_days",
    (0x0018, 0xF611): "complication_indicator",
    (0x0018, 0xF612): "infection_complication",
    (0x0018, 0xF613): "dvt_complication",
    (0x0018, 0xF614): "pe_complication",
    (0x0018, 0xF615): "sepsis_complication",
    (0x0018, 0xF616): "arf_complication",
    (0x0018, 0xF617): "mof_complication",
    (0x0018, 0xF618): "mortality_indicator",
    (0x0018, 0xF619): "mortality_24h",
    (0x0018, 0xF620): "mortality_48h",
    (0x0018, 0xF621): "mortality_7day",
    (0x0018, 0xF622): "mortality_30day",
    (0x0018, 0xF623): "discharge_disposition",
    (0x0018, 0xF624): "home_discharge",
    (0x0018, 0xF625): "rehab_discharge",
    (0x0018, 0xF626): "skilled_nursing_discharge",
    (0x0018, 0xF627): "ltach_discharge",
    (0x0018, 0xF628): "another_hospital_discharge",
    (0x0018, 0xF629): "ama_discharge",
    (0x0018, 0xF630): "triss_score",
    (0x0018, 0xF631): "rts_score",
    (0x0018, 0xF632): "pts_score",
    (0x0018, 0xF633): "outcome_prediction",
    (0x0018, 0xF634): "trauma_registry_entry",
    (0x0018, 0xF635): "quality_review_complete",
    (0x0018, 0xF636): "morbidity_mortality_review",
    (0x0018, 0xF637): "performance_improvement",
    (0x0018, 0xF638): "trauma_center_verification",
    (0x0018, 0xF639): "acs_verification_level",
    (0x0018, 0xF640): "trauma_center_designation",
}

TRAUMA_WORKFLOW_TAGS = {
    (0x0018, 0xF701): "trauma_activation_time",
    (0x0018, 0xF702): "trauma_team_arrival_time",
    (0x0018, 0xF703): "patient_arrival_time",
    (0x0018, 0xF704): "primary_survey_start",
    (0x0018, 0xF705): "primary_survey_end",
    (0x0018, 0xF706): "imaging_order_time",
    (0x0018, 0xF707): "imaging_complete_time",
    (0x0018, 0xF708): "report_available_time",
    (0x0018, 0xF709): "disposition_decision_time",
    (0x0018, 0xF710): "transfer_time",
    (0x0018, 0xF711): "or_start_time",
    (0x0018, 0xF712): "icu_arrival_time",
    (0x0018, 0xF713): "ed_stay_minutes",
    (0x0018, 0xF714): "total_ed_patients",
    (0x0018, 0xF715): "trauma_bay_occupancy",
    (0x0018, 0xF716): "ct_scanner_availability",
    (0x0018, 0xF717): "or_availability",
    (0x0018, 0xF718): "icu_bed_availability",
    (0x0018, 0xF719): "trauma_alert_activation",
    (0x0018, 0xF720): "code_stroke_activation",
    (0x0018, 0xF721): "code_stemi_activation",
    (0x0018, 0xF722): "massive_bleeding_protocol",
    (0x0018, 0xF723): "temperature_protocol",
    (0x0018, 0xF724): "damage_control_resuscitation",
    (0x0018, 0xF725): "permissive_hypotension",
    (0x0018, 0xF726): "balanced_resuscitation",
    (0x0018, 0xF727): "GO_team_activation",
    (0x0018, 0xF728): "specialist_consult_requested",
    (0x0018, 0xF729): "neurosurgery_consult",
    (0x0018, 0xF730): "orthopedic_consult",
    (0x0018, 0xF731): "cardiac_surgery_consult",
    (0x0018, 0xF732): "vascular_surgery_consult",
    (0x0018, 0xF733): "plastics_consult",
    (0x0018, 0xF734): "general_surgery_consult",
    (0x0018, 0xF735): "urology_consult",
    (0x0018, 0xF736): "ent_consult",
    (0x0018, 0xF737): "ophthalmology_consult",
    (0x0018, 0xF738): "oral_maxillofacial_consult",
    (0x0018, 0xF739): "rehabilitation_consult",
    (0x0018, 0xF740): "pain_management_consult",
    (0x0018, 0xF741): "psychiatry_consult",
    (0x0018, 0xF742): "social_work_consult",
    (0x0018, 0xF743): "case_management_consult",
}

TOTAL_TAGS_LXXI = (
    TRAUMA_PATIENT_PARAMETERS |
    INJURY_CLASSIFICATION_TAGS |
    ATLS_PROTOCOL_TAGS |
    TRAUMA_IMAGING_PROTOCOLS |
    TRAUMA_OUTCOMES_TAGS |
    TRAUMA_WORKFLOW_TAGS
)


def _extract_tags_lxxi(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in TOTAL_TAGS_LXXI.items():
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


def _is_trauma_imaging_file(file_path: str) -> bool:
    trauma_indicators = [
        'trauma', 'injury', 'fracture', 'bleeding', 'hemorrhage',
        'atls', 'gcs', 'ais', 'iss', 'tbi', 'car crash', 'mvc',
        'fall from height', 'penetrating trauma', 'blunt trauma',
        'motorcycle', 'pedestrian', 'hit and run', 'trauma center',
        'trauma bay', 'emergency surgery', 'damage control'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in trauma_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxxi(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxxi_detected": False,
        "fields_extracted": 0,
        "extension_lxxi_type": "trauma_imaging",
        "extension_lxxi_version": "2.0.0",
        "trauma_patient_parameters": {},
        "injury_classification": {},
        "atls_protocols": {},
        "trauma_imaging_protocols": {},
        "trauma_outcomes": {},
        "trauma_workflow": {},
        "extraction_errors": [],
    }

    try:
        if not _is_trauma_imaging_file(file_path):
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

        result["extension_lxxi_detected"] = True

        trauma_data = _extract_tags_lxxi(ds)

        result["trauma_patient_parameters"] = {
            k: v for k, v in trauma_data.items()
            if k in TRAUMA_PATIENT_PARAMETERS.values()
        }
        result["injury_classification"] = {
            k: v for k, v in trauma_data.items()
            if k in INJURY_CLASSIFICATION_TAGS.values()
        }
        result["atls_protocols"] = {
            k: v for k, v in trauma_data.items()
            if k in ATLS_PROTOCOL_TAGS.values()
        }
        result["trauma_imaging_protocols"] = {
            k: v for k, v in trauma_data.items()
            if k in TRAUMA_IMAGING_PROTOCOLS.values()
        }
        result["trauma_outcomes"] = {
            k: v for k, v in trauma_data.items()
            if k in TRAUMA_OUTCOMES_TAGS.values()
        }
        result["trauma_workflow"] = {
            k: v for k, v in trauma_data.items()
            if k in TRAUMA_WORKFLOW_TAGS.values()
        }

        result["fields_extracted"] = len(trauma_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxi_field_count() -> int:
    return len(TOTAL_TAGS_LXXI)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxi_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxi_description() -> str:
    return (
        "Trauma Imaging II metadata extraction. Provides comprehensive coverage of "
        "trauma patient parameters, injury classification (AIS, ISS), ATLS protocols, "
        "imaging protocols, outcomes, and trauma workflow management."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxi_modalities() -> List[str]:
    return ["CT", "MR", "CR", "DR", "XA", "US", "PT"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxi_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxi_category() -> str:
    return "Trauma Imaging II"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxi_keywords() -> List[str]:
    return [
        "trauma", "injury", "ATLS", "GCS", "AIS", "ISS", "NISS",
        "traumatic brain injury", "fracture", "hemorrhage", "ATLS protocols",
        "trauma team activation", "damage control", "trauma imaging",
        "CT trauma", "emergency surgery", "ICU", "outcomes", "mortality"
    ]
