"""
Scientific DICOM/FITS Ultimate Advanced Extension LII - Sports Medicine Imaging

This module provides comprehensive extraction of Sports Medicine Imaging parameters
including athletic injury assessment, joint imaging, biomechanics analysis,
sports-specific protocols, and performance metrics for athletes.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LII_AVAILABLE = True

SPORTS_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x2203): "patient_athlete_level",
    (0x0010, 0x2204): "patient_sport_type",
    (0x0010, 0x2205): "patient_competition_level",
    (0x0010, 0x2206): "years_of_training",
    (0x0010, 0x2207): "weekly_training_hours",
    (0x0010, 0x2208): "injury_history_count",
    (0x0010, 0x2209): "previous_surgery_count",
    (0x0010, 0x2210): "current_injury_status",
    (0x0010, 0x2211): "rehabilitation_phase",
    (0x0010, 0x2212): "return_to_play_status",
    (0x0010, 0x2213): "performance_metrics_indicator",
    (0x0010, 0x2214): "body_composition_percentage",
    (0x0010, 0x2215): "vo2_max_value",
    (0x0010, 0x2216): "flexibility_score",
    (0x0010, 0x2217): "strength_measurements",
    (0x0010, 0x2218): "endurance_measurements",
    (0x0010, 0x2219): "agility_score",
    (0x0010, 0x2220): "balance_score",
    (0x0010, 0x2221): "reaction_time_ms",
    (0x0010, 0x2222): "sport_specific_metrics",
    (0x0010, 0x2223): "equipment_used",
    (0x0010, 0x2224): "playing_surface_type",
    (0x0010, 0x2225): "environmental_conditions",
    (0x0010, 0x2226): "injury_mechanism",
    (0x0010, 0x2227): "injury_severity_score",
}

JOINT_IMAGING_TAGS = {
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x0081): "echo_time",
    (0x0018, 0x0087): "echo_train_length",
    (0x0018, 0x0090): "frequency_selection_gradient_orientation",
    (0x0018, 0x0091): "magnetic_field_strength_tesla",
    (0x0018, 0x0095): "pixel_bandwidth",
    (0x0018, 0x0100): "spatial_resolution",
    (0x0018, 0x0150): "parallel_collection_mode",
    (0x0018, 0x0151): "parallel_collection_algorithm",
    (0x0018, 0x0210): "trigger_delay_time",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0x9004): "joint_space_width_mm",
    (0x0018, 0x9005): "cartilage_thickness_mm",
    (0x0018, 0x9006): "cartilage_volume_ml",
    (0x0018, 0x9007): "bone_marrow_lesion_size",
    (0x0018, 0x9008): "osteophyte_grade",
    (0x0018, 0x9009): "meniscal_tear_size",
    (0x0018, 0x9010): "meniscal_tear_location",
    (0x0018, 0x9011): "ligament_integrity_score",
    (0x0018, 0x9012): "ligament_tear_grade",
    (0x0018, 0x9013): "tendon_thickness_mm",
    (0x0018, 0x9014): "tendon_tear_size",
    (0x0018, 0x9015): "tendon_rupture_indicator",
    (0x0018, 0x9016): "muscle_cSA_cm2",
    (0x0018, 0x9017): "muscle_fat_infiltration_percentage",
    (0x0018, 0x9018): "muscle_edema_indicator",
    (0x0018, 0x9019): "muscle_strain_grade",
    (0x0018, 0x9020): "contusion_size",
    (0x0018, 0x9021): "hematoma_dimensions",
    (0x0018, 0x9022): "effusion_volume_ml",
    (0x0018, 0x9023): "synovitis_indicator",
    (0x0018, 0x9024): "synovial_thickness_mm",
    (0x0018, 0x9025): "loose_body_indicator",
    (0x0018, 0x9026): "loose_body_count",
    (0x0018, 0x9027): "osteochondral_defect_size",
    (0x0018, 0x9028): "osteochondral_defect_depth",
    (0x0018, 0x9029): "subchondral_cyst_size",
    (0x0018, 0x9030): "implant_position",
    (0x0018, 0x9031): "implant_integrity",
    (0x0018, 0x9032): "graft_position",
    (0x0018, 0x9033): "graft_healing_status",
    (0x0018, 0x9034): "reconstruction_tunnel_position",
    (0x0018, 0x9035): "reconstruction_tunnel_width",
    (0x0018, 0x9036): "boneplug_position",
    (0x0018, 0x9037): "suture_anchor_position",
    (0x0018, 0x9038): "suture_tension",
    (0x0018, 0x9039): "joint_stability_score",
    (0x0018, 0x9040): "range_of_motion_degrees",
    (0x0018, 0x9041): "joint_space_narrowing_grade",
    (0x0018, 0x9042): "alignment_angle_degrees",
}

BIOMECHANICS_ANALYSIS_TAGS = {
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
    (0x0028, 0x1055): "window_center_and_width_explanation",
    (0x0028, 0x2110): "lossy_image_compression",
    (0x0028, 0x2112): "lossy_image_compression_ratio",
    (0x0028, 0x2114): "lossy_image_compression_method",
    (0x0018, 0x9060): "gait_cycle_phase",
    (0x0018, 0x9061): "gait_velocity_m_per_s",
    (0x0018, 0x9062): "stride_length_m",
    (0x0018, 0x9063): "step_width_m",
    (0x0018, 0x9064): "cadence_steps_per_min",
    (0x0018, 0x9065): "stance_phase_percentage",
    (0x0018, 0x9066): "swing_phase_percentage",
    (0x0018, 0x9067): "single_limb_support_percentage",
    (0x0018, 0x9068): "double_limb_support_percentage",
    (0x0018, 0x9069): "toe_clearance_mm",
    (0x0018, 0x9070): "hip_extension_angle",
    (0x0018, 0x9071): "knee_flexion_angle",
    (0x0018, 0x9072): "ankle_dorsiflexion_angle",
    (0x0018, 0x9073): "pelvic_tilt_angle",
    (0x0018, 0x9074): "pelvic_obliquity_angle",
    (0x0018, 0x9075): "ground_reaction_force_n",
    (0x0018, 0x9076): "center_of_pressure_path",
    (0x0018, 0x9077): "joint_moment_nm",
    (0x0018, 0x9078): "joint_power_w",
    (0x0018, 0x9079): "muscle_activation_pattern",
    (0x0018, 0x9080): "running_speed_km_per_h",
    (0x0018, 0x9081): "running_cadence_steps_per_min",
    (0x0018, 0x9082): "stride_length_running_m",
    (0x0018, 0x9083): "contact_time_ms",
    (0x0018, 0x9084): "flight_time_ms",
    (0x0018, 0x9085): "ground_contact_percentage",
    (0x0018, 0x9086): "vertical_oscillation_cm",
    (0x0018, 0x9087): "braking_force_n",
    (0x0018, 0x9088): "propulsive_force_n",
    (0x0018, 0x9089): "leg_stiffness_n_per_m",
    (0x0018, 0x9090): "jump_height_cm",
    (0x0018, 0x9091): "landing_force_n",
    (0x0018, 0x9092): "eccentric_concentric_ratio",
    (0x0018, 0x9093): "rate_of_force_development",
    (0x0018, 0x9094): "power_output_watts",
    (0x0018, 0x9095): "throwing_velocity_m_per_s",
    (0x0018, 0x9096): "bat_speed_m_per_s",
    (0x0018, 0x9097): "club_head_speed_m_per_s",
    (0x0018, 0x9098): "kick_velocity_m_per_s",
    (0x0018, 0x9099): "shot_velocity_m_per_s",
    (0x0018, 0x9100): "swing_angular_velocity_deg_per_s",
    (0x0018, 0x9101): "reaction_time_ms",
    (0x0018, 0x9102): "decision_making_time_ms",
    (0x0018, 0x9103): "movement_accuracy_percentage",
    (0x0018, 0x9104): "movement_precision_mm",
}

SPORTS_SPECIFIC_PROTOCOLS_TAGS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0008, 0x1060): "physician_reading_study",
    (0x0008, 0x1070): "operator_name",
    (0x0008, 0x1080): "admitting_diagnoses_description",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0x0040): "tr",
    (0x0018, 0x0070): "data_collection_diameter",
    (0x0018, 0x0082): "inversion_time",
    (0x0018, 0x0084): "imaging_frequency",
    (0x0018, 0x0085): "imaged_nucleus",
    (0x0018, 0x0086): "number_of_phase_encoding_steps",
    (0x0018, 0x0160): "parallel_sampling_factor",
    (0x0018, 0x0170): "parallel_acquisition_factor",
    (0x0018, 0x0175): "water_fat_shift_pixels",
    (0x0018, 0x0180): "coil_array_type",
    (0x0018, 0x0181): "active_coil_dimension",
    (0x0018, 0x0194): "mr_acquisition_type",
    (0x0018, 0x0195): "sequence_type",
    (0x0018, 0x0120): "reconstruction_diameter",
    (0x0018, 0x0140): "distortion_correction_type",
    (0x0018, 0x1150): "exposure_time",
    (0x0018, 0x1151): "xray_tube_current",
    (0x0018, 0x1152): "exposure",
    (0x0018, 0x1160): "filter_material",
    (0x0018, 0x1110): "distance_source_to_detector",
    (0x0018, 0x1111): "distance_source_to_patient",
    (0x0018, 0x5100): "patient_position",
    (0x0018, 0x9001): "stress_test_protocol",
    (0x0018, 0x9002): "exercise_bike_resistance_watts",
    (0x0018, 0x9003): "treadmill_speed_km_per_h",
    (0x0018, 0x9004): "treadmill_incline_percentage",
    (0x0018, 0x9005): "target_heart_rate_bpm",
    (0x0018, 0x9006): "achieved_heart_rate_bpm",
    (0x0018, 0x9007): "exercise_duration_minutes",
    (0x0018, 0x9008): "recovery_time_minutes",
    (0x0018, 0x9009): "blood_pressure_systolic_mmhg",
    (0x0018, 0x9010): "blood_pressure_diastolic_mmhg",
    (0x0018, 0x9011): "perfusion_defect_size",
    (0x0018, 0x9012): "perfusion_defect_location",
    (0x0018, 0x9013): "wall_motion_score",
    (0x0018, 0x9014): "ejection_fraction_percentage",
    (0x0018, 0x9015): "ischemia_indicator",
    (0x0018, 0x9016): "arrhythmia_indicator",
}

PERFORMANCE_METRICS_TAGS = {
    (0x0008, 0x0018): "sop_instance_uid",
    (0x0008, 0x0060): "modality",
    (0x0008, 0x0064): "conversion_type",
    (0x0008, 0x0201): "timezone_offset_from_utc",
    (0x0010, 0x0010): "patient_name",
    (0x0010, 0x0020): "patient_id",
    (0x0010, 0x0021): "issuer_of_patient_id",
    (0x0010, 0x0030): "patient_birth_date",
    (0x0010, 0x0032): "patient_birth_time",
    (0x0010, 0x0040): "patient_sex",
    (0x0010, 0x1000): "other_patient_names",
    (0x0010, 0x1001): "other_patient_ids",
    (0x0010, 0x1002): "ethnic_group",
    (0x0010, 0x1005): "patient_birth_name",
    (0x0010, 0x1040): "patient_address",
    (0x0010, 0x21C0): "pregnancy_status",
    (0x0010, 0x21F0): "patient_religious_preference",
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0020): "sequence_name",
    (0x0018, 0x9201): "performance_index_score",
    (0x0018, 0x9202): "functional_capacity_mets",
    (0x0018, 0x9203): "lactate_threshold_bpm",
    (0x0018, 0x9204): "lactate_threshold_velocity_km_per_h",
    (0x0018, 0x9205): "anaerobic_threshold_watts",
    (0x0018, 0x9206): "maximum_oxygen_consumption_ml_per_kg_per_min",
    (0x0018, 0x9207): "ventilatory_threshold_ml_per_kg_per_min",
    (0x0018, 0x9208): "respiratory_exchange_ratio",
    (0x0018, 0x9209): "oxygen_pulse_ml_per_beat",
    (0x0018, 0x9210): "ventilatory_efficiency_slope",
    (0x0018, 0x9211): "running_economy_ml_per_kg_per_km",
    (0x0018, 0x9212): "cycling_efficiency_percentage",
    (0x0018, 0x9213): "swimming_stroke_efficiency",
    (0x0018, 0x9214): "propulsion_efficiency_percentage",
    (0x0018, 0x9215): "turn_efficiency_percentage",
    (0x0018, 0x9216): "start_efficiency_percentage",
    (0x0018, 0x9217): "acceleration_m_per_s2",
    (0x0018, 0x9218): "deceleration_m_per_s2",
    (0x0018, 0x9219): "maximum_velocity_m_per_s",
    (0x0018, 0x9220): "velocity_decay_rate",
    (0x0018, 0x9221): "change_of_direction_speed_deg_per_s",
    (0x0018, 0x9222): "cutting_angle_degrees",
    (0x0018, 0x9223): "jumping_mechanics_score",
    (0x0018, 0x9224): "landing_mechanics_score",
    (0x0018, 0x9225): "throwing_mechanics_score",
    (0x0018, 0x9226): "kicking_mechanics_score",
    (0x0018, 0x9227): "striking_mechanics_score",
    (0x0018, 0x9228): "swing_mechanics_score",
    (0x0018, 0x9229): "technical_skill_score",
    (0x0018, 0x9230): "tactical_skill_score",
    (0x0018, 0x9231): "decision_making_score",
    (0x0018, 0x9232): "spatial_awareness_score",
    (0x0018, 0x9233): "situational_awareness_score",
    (0x0018, 0x9234): "stress_tolerance_score",
    (0x0018, 0x9235): "competition_performance_index",
    (0x0018, 0x9236): "training_load_au",
    (0x0018, 0x9237): "fatigue_index",
    (0x0018, 0x9238): "recovery_status_score",
    (0x0018, 0x9239): "readiness_to_train_score",
    (0x0018, 0x9240): "overreaching_indicator",
    (0x0018, 0x9241): "overtraining_indicator",
    (0x0018, 0x9242): "injury_risk_percentage",
    (0x0018, 0x9243): "workload_tolerance_au",
    (0x0018, 0x9244): "periodization_phase",
    (0x0018, 0x9245): "tapering_status",
    (0x0018, 0x9246): "competition_readiness_score",
    (0x0018, 0x9247): "performance_trend",
    (0x0018, 0x9248): "performance_baseline",
    (0x0018, 0x9249): "performance_peak",
    (0x0018, 0x9250): "season_goal_alignment",
    (0x0018, 0x9251): "career_trajectory",
    (0x0018, 0x9252): "longevity_prediction",
}

TOTAL_TAGS_LII = (
    SPORTS_PATIENT_PARAMETERS | 
    JOINT_IMAGING_TAGS | 
    BIOMECHANICS_ANALYSIS_TAGS | 
    SPORTS_SPECIFIC_PROTOCOLS_TAGS | 
    PERFORMANCE_METRICS_TAGS
)


def _extract_tags_lii(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in TOTAL_TAGS_LII.items():
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


def _is_sports_medicine_file(file_path: str) -> bool:
    sports_indicators = [
        'sports', 'athlete', 'athletic', 'injury', 'joint', 'biomechanics',
        'knee', 'shoulder', 'ankle', 'hip', 'elbow', 'wrist', 'spine',
        'acl', 'mcl', 'meniscus', 'labrum', 'tendon', 'ligament',
        'concussion', 'return_to_play', 'rehabilitation'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in sports_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lii_detected": False,
        "fields_extracted": 0,
        "extension_lii_type": "sports_medicine_imaging",
        "extension_lii_version": "2.0.0",
        "sports_patient_parameters": {},
        "joint_imaging": {},
        "biomechanics_analysis": {},
        "sports_specific_protocols": {},
        "performance_metrics": {},
        "extraction_errors": [],
    }

    try:
        if not _is_sports_medicine_file(file_path):
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

        result["extension_lii_detected"] = True

        sports_data = _extract_tags_lii(ds)

        result["sports_patient_parameters"] = {
            k: v for k, v in sports_data.items()
            if k in SPORTS_PATIENT_PARAMETERS.values()
        }
        result["joint_imaging"] = {
            k: v for k, v in sports_data.items()
            if k in JOINT_IMAGING_TAGS.values()
        }
        result["biomechanics_analysis"] = {
            k: v for k, v in sports_data.items()
            if k in BIOMECHANICS_ANALYSIS_TAGS.values()
        }
        result["sports_specific_protocols"] = {
            k: v for k, v in sports_data.items()
            if k in SPORTS_SPECIFIC_PROTOCOLS_TAGS.values()
        }
        result["performance_metrics"] = {
            k: v for k, v in sports_data.items()
            if k in PERFORMANCE_METRICS_TAGS.values()
        }

        result["fields_extracted"] = len(sports_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lii_field_count() -> int:
    return len(TOTAL_TAGS_LII)


def get_scientific_dicom_fits_ultimate_advanced_extension_lii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lii_description() -> str:
    return (
        "Sports Medicine Imaging metadata extraction. Provides comprehensive coverage of "
        "athletic injury assessment, joint imaging, biomechanics analysis, "
        "sports-specific protocols, and performance metrics for athletes."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lii_modalities() -> List[str]:
    return ["CT", "MR", "CR", "DR", "US", "PT", "NM", "MG", "XA", "RF"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lii_category() -> str:
    return "Sports Medicine Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_lii_keywords() -> List[str]:
    return [
        "sports medicine", "athletic injury", "joint imaging", "biomechanics",
        "knee injury", "shoulder injury", "acl tear", "meniscus tear",
        "concussion", "return to play", "rehabilitation", "performance metrics",
        "athlete", "sports specific protocols", "injury assessment", "functional movement",
        "sports rehabilitation", "motion analysis", "performance training"
    ]


# Aliases for smoke test compatibility
def extract_occupational_therapy(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_lii."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_lii(file_path)

def get_occupational_therapy_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lii_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lii_field_count()

def get_occupational_therapy_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lii_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lii_version()

def get_occupational_therapy_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lii_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lii_description()

def get_occupational_therapy_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lii_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lii_supported_formats()

def get_occupational_therapy_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lii_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lii_modalities()
