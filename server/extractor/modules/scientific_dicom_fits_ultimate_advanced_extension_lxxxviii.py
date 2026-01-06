"""
Scientific DICOM/FITS Ultimate Advanced Extension LXXXVIII - Sports Medicine Imaging II

This module provides comprehensive extraction of Sports Medicine Imaging parameters
including sports injuries, athletic performance, rehabilitation, and
sports medicine-specific imaging protocols.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXXVIII_AVAILABLE = True

SPORTS_MEDICINE_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x1001): "sports_medicine_assessment_date",
    (0x0010, 0xN002): "sport_played",
    (0x0010, 0xN003): "athletic_level",
    (0x0010, 0xN004): "professional_athlete",
    (0x0010, 0xN005): "collegiate_athlete",
    (0x0010, 0xN006): "high_school_athlete",
    (0x0010, 0xN007): "recreational_athlete",
    (0x0010, 0xN008): "weekend_warrior",
    (0x0010, 0xN009): "active_population",
    (0x0010, 0xN010): "injury_type",
    (0x0010, 0xN011): "acute_injury",
    (0x0010, 0xN012): "chronic_injury",
    (0x0010, 0xN013): "overuse_injury",
    (0x0010, 0xN014): "reinjury_indicator",
    (0x0010, 0xN015): "recurrent_injury",
    (0x0010, 0xN016): "time_since_injury",
    (0x0010, 0xN017): "injury_severity",
    (0x0010, 0xN018): "grade_1_strain",
    (0x0010, 0xN019): "grade_2_strain",
    (0x0010, 0xN020): "grade_3_strain",
    (0x0010, 0xN021): "grade_1_sprain",
    (0x0010, 0xN022): "grade_2_sprain",
    (0x0010, 0xN023): "grade_3_sprain",
    (0x0010, 0xN024): "concussion_indicator",
    (0x0010, 0xN025): "mild_tbi",
    (0x0010, 0xN026): "moderate_tbi",
    (0x0010, 0xN027): "severe_tbi",
    (0x0010, 0xN028): "post_concussion_syndrome",
    (0x0010, 0xN029): "joint_injury",
    (0x0010, 0xN030): "acl_tear",
    (0x0010, 0xN031): "mcl_tear",
    (0x0010, 0xN032): "pcl_tear",
    (0x0010, 0xN033): "meniscus_tear",
    (0x0010, 0xN034): "cartilage_injury",
    (0x0010, 0xN035): "osteoarthritis_sports",
    (0x0010, 0xN036): "tendon_rupture",
    (0x0010, 0xN037): "achilles_rupture",
    (0x0010, 0xN038): "quadriceps_rupture",
    (0x0010, 0xN039): "patellar_rupture",
    (0x0010, 0xN040): "stress_fracture",
    (0x0010, 0xN041): "bone_contusion",
    (0x0010, 0xN042): "muscle_strain",
    (0x0010, 0xN043): "hamstring_strain",
    (0x0010, 0xN044): "groin_strain",
    (0x0010, 0xN045): "calf_strain",
    (0x0010, 0xN046): "core_muscle_injury",
    (0x0010, 0xN047): "shoulder_instability",
    (0x0010, 0xN048): "bankart_lesion",
    (0x0010, 0xN049): "hill_sachs_defect",
    (0x0010, 0xN050): "rotator_cuff_tear",
    (0x0010, 0xN051): "partial_thickness",
    (0x0010, 0xN052): "full_thickness",
    (0x0010, 0xN053): "labral_tear",
    (0x0010, 0xN054): "slap_lesion",
    (0x0010, 0xN055): "thrower_shoulder",
    (0x0010, 0xN056): "swimmers_shoulder",
    (0x0010, 0xN057): "tennis_elbow",
    (0x0010, 0xN058): "golfers_elbow",
    (0x0010, 0xN059): "wrist_injury",
}

SPORTS_MEDICINE_PATHOLOGY_TAGS = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0xN101): "tendon_pathology",
    (0x0018, 0xN102): "tendinosis",
    (0x0018, 0xN103): "tendinopathy",
    (0x0018, 0xN104): "partial_tear_tendon",
    (0x0018, 0xN105): "complete_tear_tendon",
    (0x0018, 0xN106): "tendon_retraction",
    (0x0018, 0xN107): "tendon_gap",
    (0x0018, 0xN108): "muscle_edema",
    (0x0018, 0xN109): "muscle_hemorrhage",
    (0x0018, 0xN110): "muscle_atrophy",
    (0x0018, 0xN111): "muscle_fat_infiltration",
    (0x0018, 0xN112): "fascial_edema",
    (0x0018, 0xN113): "interstitial_edema",
    (0x0018, 0xN114): "ligament_pathology",
    (0x0018, 0xN115): "ligament_sprain",
    (0x0018, 0xN116): "ligament_tear",
    (0x0018, 0xN117): "ligament_instability",
    (0x0018, 0xN118): "laxity_measurement",
    (0x0018, 0xN119): "joint_effusion",
    (0x0018, 0xN120): "synovitis_sports",
    (0x0018, 0xN121): "pannus_formation",
    (0x0018, 0xN122): "loose_body",
    (0x0018, 0xN123): "osteochondral_defect",
    (0x0018, 0xN124): "chondral_lesion",
    (0x0018, 0xN125): "bone_marrow_edema_sports",
    (0x0018, 0xN126): "subchondral_fracture",
    (0x0018, 0xN127): "stress_reaction",
    (0x0018, 0xN128): "stress_fracture_line",
    (0x0018, 0xN129): "periostitis",
    (0x0018, 0xN130): "apophysitis",
    (0x0018, 0xN131): "osgood_schlatter",
    (0x0018, 0xN132): "sinding_larsen",
    (0x0018, 0xN133): "severs_disease",
    (0x0018, 0xN134): "osteochondritis",
    (0x0018, 0xN135): "osteochondrosis",
    (0x0018, 0xN136): "avascular_necrosis_sports",
    (0x0018, 0xN137): "kohler_disease",
    (0x0018, 0xN138): "freiberg_infarction",
    (0x0018, 0xN139): "neuroma_sports",
    (0x0018, 0xN140): "nerve_compression",
    (0x0018, 0xN141): "tarsal_tunnel",
    (0x0018, 0xN142): "carpal_tunnel_sports",
    (0x0018, 0xN143): "piriformis_syndrome",
    (0x0018, 0xN144): "sciatica_sports",
    (0x0018, 0xN145): "compartment_syndrome",
    (0x0018, 0xN146): "acute_compartment",
    (0x0018, 0xN147): "chronic_exertional",
    (0x0018, 0xN148): "pressure_measurement",
    (0x0018, 0xN149): "vascular_injury_sports",
}

SPORTS_MEDICINE_IMAGING_TAGS = {
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
    (0x0018, 0xN201): "mri_joint_protocol",
    (0x0018, 0xN202): "mri_knee_sports",
    (0x0018, 0xN203): "mri_shoulder_sports",
    (0x0018, 0xN204): "mri_ankle_sports",
    (0x0018, 0xN205): "mri_hip_sports",
    (0x0018, 0xN206): "mri_spine_sports",
    (0x0018, 0xN207): "mri_elbow_sports",
    (0x0018, 0xN208): "mri_wrist_sports",
    (0x0018, 0xN209): "mri_muscle_protocol",
    (0x0018, 0xN210): "diffusion_muscle",
    (0x0018, 0xN211): "fat_suppressed_muscle",
    (0x0018, 0xN212): "short_tau_inversion",
    (0x0018, 0xN213): "stir_sequence",
    (0x0018, 0xN214): "proton_density_sports",
    (0x0018, 0xN215): "t2_weighted_sports",
    (0x0018, 0xN216): "contrast_enhanced_sports",
    (0x0018, 0xN217): "arthrography_mri",
    (0x0018, 0xN218): "direct_arthrogram",
    (0x0018, 0xN219): "indirect_arthrogram",
    (0x0018, 0xN220): "ct_arthrogram",
    (0x0018, 0xN221): "3d_reconstruction",
    (0x0018, 0xN222): "ultrasound_sports",
    (0x0018, 0xN223): "musculoskeletal_ultrasound",
    (0x0018, 0xN224): "dynamic_ultrasound",
    (0x0018, 0xN225): "stress_ultrasound",
    (0x0018, 0xN226): "elastography_sports",
    (0x0018, 0xN227): "power_doppler_sports",
    (0x0018, 0xN228): "ct_bone_protocol",
    (0x0018, 0xN229): "fracture_assessment",
    (0x0018, 0xN230): "occult_fracture",
    (0x0018, 0xN231): "stress_fracture_ct",
    (0x0018, 0xN232): "pet_ct_sports",
    (0x0018, 0xN233): "bone_scan_sports",
    (0x0018, 0xN234): "spect_ct_sports",
    (0x0018, 0xN235): "xray_sports",
    (0x0018, 0xN236): "stress_views",
    (0x0018, 0xN237): "weight_bearing",
    (0x0018, 0xN238): "comparison_views",
    (0x0018, 0xN239): "fluoroscopy_sports",
    (0x0018, 0xN240): "injection_guided",
    (0x0018, 0xN241): "barbotage_procedure",
    (0x0018, 0xN242): "tenotomy_injection",
    (0x0018, 0xN243): "prp_injection_sports",
    (0x0018, 0xN244): "stem_cell_injection",
    (0x0018, 0xN245): "bone_marrow_aspirate",
    (0x0018, 0xN246): "prolotherapy",
    (0x0018, 0xN247): "image_guided_biopsy",
    (0x0018, 0xN248): "diagnostic_injection",
    (0x0018, 0xN249): "therapeutic_injection",
}

SPORTS_MEDICINE_PROTOCOLS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0xN301): "injury_classification",
    (0x0018, 0xN302): "return_to_play",
    (0x0018, 0xN303): "return_to_sport",
    (0x0018, 0xN304): "clearance_protocol",
    (0x0018, 0xN305): "functional_testing",
    (0x0018, 0xN306): "hop_testing",
    (0x0018, 0xN307): "single_hop",
    (0x0018, 0xN308): "triple_hop",
    (0x0018, 0xN309): "cross_over_hop",
    (0x0018, 0xN310): "timed_hop",
    (0x0018, 0xN311): "strength_testing",
    (0x0018, 0xN312): "isokinetic_testing",
    (0x0018, 0xN313): "dynamometry",
    (0x0018, 0xN314): "range_of_motion_testing",
    (0x0018, 0xN315): "goniometry",
    (0x0018, 0xN316): "balance_testing",
    (0x0018, 0xN317): "biodex_testing",
    (0x0018, 0xN318): "force_plate_testing",
    (0x0018, 0xN319): "motion_analysis",
    (0x0018, 0xN320): "gait_analysis",
    (0x0018, 0xN321): "running_analysis",
    (0x0018, 0xN322): "throwing_analysis",
    (0x0018, 0xN323): "biomechanics",
    (0x0018, 0xN324): "rehabilitation_protocol",
    (0x0018, 0xN325): "physical_therapy",
    (0x0018, 0xN326): "occupational_therapy",
    (0x0018, 0xN327): "aquatic_therapy",
    (0x0018, 0xN328): "strength_training",
    (0x0018, 0xN329): "plyometrics",
    (0x0018, 0xN330): "agility_training",
    (0x0018, 0xN331): "endurance_training",
    (0x0018, 0xN332): "flexibility_training",
    (0x0018, 0xN333): "manual_therapy",
    (0x0018, 0xN334): "joint_mobilization",
    (0x0018, 0xN335): "soft_tissue_mobilization",
    (0x0018, 0xN336): "modalities_sports",
    (0x0018, 0xN337): "electrostimulation",
    (0x0018, 0xN338): "ultrasound_therapy",
    (0x0018, 0xN339): "laser_therapy",
    (0x0018, 0xN340): "cryotherapy",
    (0x0018, 0xN341): "heat_therapy",
    (0x0018, 0xN342): "taping_sports",
    (0x0018, 0xN343): "kinesio_taping",
    (0x0018, 0xN344): "rigid_taping",
    (0x0018, 0xN345): "bracing_sports",
    (0x0018, 0xN346): "orthotic_device",
    (0x0018, 0xN347): "foot_orthotic",
    (0x0018, 0xN348): "ankle_brace",
    (0x0018, 0xN349): "knee_brace",
    (0x0018, 0xN350): "surgical_planning_sports",
}

SPORTS_MEDICINE_OUTCOMES_TAGS = {
    (0x0018, 0xN401): "return_to_sport_outcome",
    (0x0018, 0xN402): "return_to_play_rate",
    (0x0018, 0xN403): "time_to_return",
    (0x0018, 0xN404): "weeks_to_return",
    (0x0018, 0xN405): "months_to_return",
    (0x0018, 0xN406): "injury_recurrence",
    (0x0018, 0xN407): "reinjury_rate",
    (0x0018, 0xN408): "complication_sports",
    (0x0018, 0xN409): "surgical_complication",
    (0x0018, 0xN410): "infection_sports",
    (0x0018, 0xN411): "thromboembolism_sports",
    (0x0018, 0xN412): "functional_outcome",
    (0x0018, 0xN413): "lysholm_score",
    (0x0018, 0xN414): "ikdc_score",
    (0x0018, 0xN415): "tegner_score",
    (0x0018, 0xN416): "cincinnati_score",
    (0x0018, 0xN417): "womac_sports",
    (0x0018, 0xN418): "upper extremity_score",
    (0x0018, 0xN419): "rowe_score",
    (0x0018, 0xN420): "constant_score",
    (0x0018, 0xN421): "dash_score",
    (0x0018, 0xN422): "quick_dash",
    (0x0018, 0xN423): "strength_recovery",
    (0x0018, 0xN424): "strength_percentage",
    (0x0018, 0xN425): "symmetry_index",
    (0x0018, 0xN426): "hop_test_outcome",
    (0x0018, 0xN427): "limb_symmetry_index",
    (0x0018, 0xN428): "performance_metrics",
    (0x0018, 0xN429): "speed_recovery",
    (0x0018, 0xN430): "agility_recovery",
    (0x0018, 0xN431): "endurance_recovery",
    (0x0018, 0xN432): "power_recovery",
    (0x0018, 0xN433): "vertical_jump",
    (0x0018, 0xN434): "sprint_time",
    (0x0018, 0xN435): "reaction_time",
    (0x0018, 0xN436): "sports_specific_testing",
    (0x0018, 0xN437): "position_testing",
    (0x0018, 0xN438): "game_simulation",
    (0x0018, 0xN439): "practice_clearance",
    (0x0018, 0xN440): "full_contact_clearance",
    (0x0018, 0xN441): "competition_clearance",
    (0x0018, 0xN442): "long_term_outcome",
    (0x0018, 0xN443): "career_longevity",
    (0x0018, 0xN444): "draft_status",
    (0x0018, 0xN445): "scholarship_status",
    (0x0018, 0xN446): "retirement_sports",
    (0x0018, 0xN447): "quality_of_life_sports",
    (0x0018, 0xN448): "sf36_sports",
    (0x0018, 0xN449): "sf36_physical",
    (0x0018, 0xN450): "sf36_mental",
}

TOTAL_TAGS_LXXXVIII = {}

TOTAL_TAGS_LXXXVIII.update(SPORTS_MEDICINE_PATIENT_PARAMETERS)
TOTAL_TAGS_LXXXVIII.update(SPORTS_MEDICINE_PATHOLOGY_TAGS)
TOTAL_TAGS_LXXXVIII.update(SPORTS_MEDICINE_IMAGING_TAGS)
TOTAL_TAGS_LXXXVIII.update(SPORTS_MEDICINE_PROTOCOLS)
TOTAL_TAGS_LXXXVIII.update(SPORTS_MEDICINE_OUTCOMES_TAGS)


def _extract_tags_lxxxviii(ds: Any) -> Dict[str, Any]:
    extracted = {}
    tag_names = {tag: name for tag, name in TOTAL_TAGS_LXXXVIII.items()}
    for tag, name in tag_names.items():
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


def _is_sports_medicine_imaging_file(file_path: str) -> bool:
    sports_indicators = [
        'sports', 'sports_medicine', 'athlete', 'athletic', 'injury',
        'concussion', 'acl', 'meniscus', 'rotator_cuff', 'tendon',
        'ligament', 'strain', 'sprain', 'fracture_sports', 'rehabilitation',
        'return_to_play', 'return_to_sport', 'rehab', 'physical_therapy'
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


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxxxviii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxxxviii_detected": False,
        "fields_extracted": 0,
        "extension_lxxxviii_type": "sports_medicine_imaging",
        "extension_lxxxviii_version": "2.0.0",
        "sports_medicine_patient_parameters": {},
        "sports_medicine_pathology": {},
        "sports_medicine_imaging": {},
        "sports_medicine_protocols": {},
        "sports_medicine_outcomes": {},
        "extraction_errors": [],
    }

    try:
        if not _is_sports_medicine_imaging_file(file_path):
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

        result["extension_lxxxviii_detected"] = True

        sports_data = _extract_tags_lxxxviii(ds)

        patient_params_set = set(SPORTS_MEDICINE_PATIENT_PARAMETERS.keys())
        pathology_set = set(SPORTS_MEDICINE_PATHOLOGY_TAGS.keys())
        imaging_set = set(SPORTS_MEDICINE_IMAGING_TAGS.keys())
        protocols_set = set(SPORTS_MEDICINE_PROTOCOLS.keys())
        outcomes_set = set(SPORTS_MEDICINE_OUTCOMES_TAGS.keys())

        for tag, value in sports_data.items():
            if tag in patient_params_set:
                result["sports_medicine_patient_parameters"][tag] = value
            elif tag in pathology_set:
                result["sports_medicine_pathology"][tag] = value
            elif tag in imaging_set:
                result["sports_medicine_imaging"][tag] = value
            elif tag in protocols_set:
                result["sports_medicine_protocols"][tag] = value
            elif tag in outcomes_set:
                result["sports_medicine_outcomes"][tag] = value

        result["fields_extracted"] = len(sports_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxviii_field_count() -> int:
    return len(TOTAL_TAGS_LXXXVIII)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxviii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxviii_description() -> str:
    return (
        "Sports Medicine Imaging II metadata extraction. Provides comprehensive coverage of "
        "sports injuries, athletic performance, rehabilitation, "
        "sports medicine-specific imaging protocols, and sports medicine outcomes assessment."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxviii_modalities() -> List[str]:
    return ["MR", "CT", "US", "CR", "DR", "XA", "NM", "PT", "RG"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxviii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxviii_category() -> str:
    return "Sports Medicine Imaging II"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxviii_keywords() -> List[str]:
    return [
        "sports medicine", "sports injury", "athlete", "concussion",
        "ACL tear", "rotator cuff", "meniscus", "tendon", "ligament",
        "return to play", "rehabilitation", "physical therapy",
        "musculoskeletal MRI", "sports performance", "biomechanics"
    ]
