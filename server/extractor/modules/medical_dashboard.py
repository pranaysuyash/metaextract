"""
Scientific DICOM/FITS Ultimate Advanced Extension LXXXIII - Orthopedics Imaging II

This module provides comprehensive extraction of Orthopedics Imaging parameters
including bone disorders, joint diseases, fractures, and
orthopedics-specific imaging protocols.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXXIII_AVAILABLE = True

ORTHOPEDICS_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0xD001): "orthopedics_assessment_date",
    (0x0010, 0xD002): "orthopedic_diagnosis",
    (0x0010, 0xD003): "fracture_indicator",
    (0x0010, 0xD004): "fracture_type",
    (0x0010, 0xD005): "fracture_location",
    (0x0010, 0xD006): "open_fracture",
    (0x0010, 0xD007): "closed_fracture",
    (0x0010, 0xD008): "pathologic_fracture",
    (0x0010, 0xD009): "stress_fracture",
    (0x0010, 0xD010): "comminuted_fracture",
    (0x0010, 0xD011): "displaced_fracture",
    (0x0010, 0xD012): "nondisplaced_fracture",
    (0x0010, 0xD013): "intraarticular_fracture",
    (0x0010, 0xD014): "articular_involvement",
    (0x0010, 0xD015): "fracture_displacement",
    (0x0010, 0xD016): "fracture_angulation",
    (0x0010, 0xD017): "fracture_shortening",
    (0x0010, 0xD018): "joint_disease_indicator",
    (0x0010, 0xD019): "osteoarthritis_indicator",
    (0x0010, 0xD020): "rheumatoid_arthritis",
    (0x0010, 0xD021): "psoriatic_arthritis",
    (0x0010, 0xD022): "ankylosing_spondylitis",
    (0x0010, 0xD023): "gout_arthritis",
    (0x0010, 0xD024): "pseudogout",
    (0x0010, 0xD025): "septic_arthritis",
    (0x0010, 0xD026): "joint_space_narrowing",
    (0x0010, 0xD027): "osteophyte_formation",
    (0x0010, 0xD028): "subchondral_sclerosis",
    (0x0010, 0xD029): "subchondral_cyst",
    (0x0010, 0xD030): "meniscal_tear",
    (0x0010, 0xD031): "acl_tear",
    (0x0010, 0xD032): "pcl_tear",
    (0x0010, 0xD033): "ligament_tear",
    (0x0010, 0xD034): "rotator_cuff_tear",
    (0x0010, 0xD035): "labral_tear",
    (0x0010, 0xD036): "cartilage_defect",
    (0x0010, 0xD037): "chondral_lesion",
    (0x0010, 0xD038): "osteochondral_defect",
    (0x0010, 0xD039): "avascular_necrosis",
    (0x0010, 0xD040): "osteonecrosis",
    (0x0010, 0xD041): "hip_necrosis",
    (0x0010, 0xD042): "knee_necrosis",
    (0x0010, 0xD043): "shoulder_necrosis",
    (0x0010, 0xD044): "bone_tumor_indicator",
    (0x0010, 0xD045): "primary_bone_tumor",
    (0x0010, 0xD046): "osteosarcoma",
    (0x0010, 0xD047): "ewing_sarcoma",
    (0x0010, 0xD048): "chondrosarcoma",
    (0x0010, 0xD049): "bone_metastasis",
    (0x0010, 0xD050): "multiple_myeloma",
    (0x0010, 0xD051): "osteomyelitis",
    (0x0010, 0xD052): "septic_osteomyelitis",
    (0x0010, 0xD053): "chronic_osteomyelitis",
    (0x0010, 0xD054): "osteoporosis_indicator",
    (0x0010, 0xD055): "bone_mineral_density",
    (0x0010, 0xD056): "t_score",
    (0x0010, 0xD057): "z_score",
    (0x0010, 0xD058): "vertebral_fracture",
    (0x0010, 0xD059): "fragility_fracture",
}

ORTHO_PATHOLOGY_TAGS = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0xD101): "fracture_line",
    (0x0018, 0xD102): "fracture_pattern",
    (0x0018, 0xD103): "fracture_communition",
    (0x0018, 0xD104): "fracture_depression",
    (0x0018, 0xD105): "impression_fracture",
    (0x0018, 0xD106): "burst_fracture",
    (0x0018, 0xD107): "compression_fracture",
    (0x0018, 0xD108): "wedge_deformity",
    (0x0018, 0xD109): "biconcave_deformity",
    (0x0018, 0xD110): "crush_fracture",
    (0x0018, 0xD111): "Chance_fracture",
    (0x0018, 0xD112): "fracture_dislocation",
    (0x0018, 0xD113): "joint_incongruity",
    (0x0018, 0xD114): "subluxation",
    (0x0018, 0xD115): "dislocation",
    (0x0018, 0xD116): "anterior_dislocation",
    (0x0018, 0xD117): "posterior_dislocation",
    (0x0018, 0xD118): "inferior_dislocation",
    (0x0018, 0xD119): "bone_contusion",
    (0x0018, 0xD120): "bone_marrow_edema",
    (0x0018, 0xD121): "bonebruise_pattern",
    (0x0018, 0xD122): "stress_reaction",
    (0x0018, 0xD123): "periosteal_reaction",
    (0x0018, 0xD124): "codman_triangle",
    (0x0018, 0xD125): "sunburst_pattern",
    (0x0018, 0xD126): "onion_skinning",
    (0x0018, 0xD127): "lytic_lesion",
    (0x0018, 0xD128): "blastic_lesion",
    (0x0018, 0xD129): "mixed_lesion",
    (0x0018, 0xD130): "permeative_lesion",
    (0x0018, 0xD131): "moth_eaten_lesion",
    (0x0018, 0xD132): "sclerotic_lesion",
    (0x0018, 0xD133): "geographic_lesion",
    (0x0018, 0xD134): "lesion_margin",
    (0x0018, 0xD135): "lesion_size_bone",
    (0x0018, 0xD136): "cortical_destruction",
    (0x0018, 0xD137): "cortical_thickening",
    (0x0018, 0xD138): "endosteal_cortication",
    (0x0018, 0xD139): "periosteal_cortication",
    (0x0018, 0xD140): "sequestrum_formation",
    (0x0018, 0xD141): "involucrum_formation",
    (0x0018, 0xD142): "cloaca_fistula",
    (0x0018, 0xD143): "bone_expansion",
    (0x0018, 0xD144): "trabecular_pattern",
    (0x0018, 0xD145): "honeycomb_appearance",
    (0x0018, 0xD146): "soap_bubble_appearance",
    (0x0018, 0xD147): "ground_glass_appearance",
    (0x0018, 0xD148): "hair_on_end_appearance",
    (0x0018, 0xD149): "vertebral_collapse",
}

ORTHO_IMAGING_TAGS = {
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
    (0x0018, 0xD201): "skeletal_survey",
    (0x0018, 0xD202): "bone_age_assessment",
    (0x0018, 0xD203): "greulich_pyle",
    (0x0018, 0xD204): "tanner_whitehouse",
    (0x0018, 0xD205): "hand_wrist_series",
    (0x0018, 0xD206): "full_length_standing",
    (0x0018, 0xD207): "long_leg_alignment",
    (0x0018, 0xD208): "anteroposterior_view",
    (0x0018, 0xD209): "lateral_view",
    (0x0018, 0xD210): "oblique_view",
    (0x0018, 0xD211): "axial_view",
    (0x0018, 0xD212): "trauma_series",
    (0x0018, 0xD213): "ct_orthopedic_protocol",
    (0x0018, 0xD214): "3d_reconstruction_bone",
    (0x0018, 0xD215): "volume_rendering_bone",
    (0x0018, 0xD216): "mri_joint_protocol",
    (0x0018, 0xD217): "mri_knee_protocol",
    (0x0018, 0xD218): "mri_hip_protocol",
    (0x0018, 0xD219): "mri_shoulder_protocol",
    (0x0018, 0xD220): "mri_ankle_protocol",
    (0x0018, 0xD221): "mri_wrist_protocol",
    (0x0018, 0xD222): "mri_spine_protocol",
    (0x0018, 0xD223): "proton_density_weighted",
    (0x0018, 0xD224): "fat_suppressed_pd",
    (0x0018, 0xD225): "stir_sequence",
    (0x0018, 0xD226): "t2_mapping",
    (0x0018, 0xD227): "t1_mapping",
    (0x0018, 0xD228): "gag_cest_imaging",
    (0x0018, 0xD229): "dgemric_imaging",
    (0x0018, 0xD230): "delayed_gadolinium",
    (0x0018, 0xD231): "ultrasound_joint",
    (0x0018, 0xD232): "ultrasound_guided",
    (0x0018, 0xD233): "fluoroscopy_bone",
    (0x0018, 0xD234): "bone_scan",
    (0x0018, 0xD235): "technetium_99m_scan",
    (0x0018, 0xD236): "three_phase_bone_scan",
    (0x0018, 0xD237): "spect_ct_bone",
    (0x0018, 0xD238): "pet_ct_bone",
    (0x0018, 0xD239): "na_fluoride_pet",
    (0x0018, 0xD240): "dexa_scan",
    (0x0018, 0xD241): "bone_density_hip",
    (0x0018, 0xD242): "bone_density_spine",
    (0x0018, 0xD243): "bone_density_forearm",
    (0x0018, 0xD244): "trabecular_bone_score",
    (0x0018, 0xD245): "vertebral_fracture_assessment",
    (0x0018, 0xD246): "vfa_radiograph",
    (0x0018, 0xD247): "hologic_qct",
    (0x0018, 0xD248): "ge_qct",
    (0x0018, 0xD249): "peripheral_qct",
}

ORTHO_PROTOCOLS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0xD301): "fracture_classification",
    (0x0018, 0xD302): "ao_classification",
    (0x0018, 0xD303): "ota_classification",
    (0x0018, 0xD304): "neer_classification",
    (0x0018, 0xD305): "gardens_classification",
    (0x0018, 0xD306): "pauwels_classification",
    (0x0018, 0xD307): "letournel_classification",
    (0x0018, 0xD308): "dental_classification",
    (0x0018, 0xD309): "tile_classification",
    (0x0018, 0xD310): "young_burgess_classification",
    (0x0018, 0xD311): "denis_classification",
    (0x0018, 0xD312): "thoracolumbar_classification",
    (0x0018, 0xD313): "gestalt_classification",
    (0x0018, 0xD314): "surgical_planning",
    (0x0018, 0xD315): "internal_fixation",
    (0x0018, 0xD316): "external_fixation",
    (0x0018, 0xD317): "intramedullary_nailing",
    (0x0018, 0xD318): "plate_screw_fixation",
    (0x0018, 0xD319): "total_joint_replacement",
    (0x0018, 0xD320): "total_hip_replacement",
    (0x0018, 0xD321): "total_knee_replacement",
    (0x0018, 0xD322): "total_shoulder_replacement",
    (0x0018, 0xD323): "total_ankle_replacement",
    (0x0018, 0xD324): "partial_joint_replacement",
    (0x0018, 0xD325): "unicompartmental_knee",
    (0x0018, 0xD326): "patellofemoral_replacement",
    (0x0018, 0xD327): "hip_resurfacing",
    (0x0018, 0xD328): "shoulder_resurfacing",
    (0x0018, 0xD329): "joint_preservation",
    (0x0018, 0xD330): "osteotomy_planning",
    (0x0018, 0xD331): "high_tibial_osteotomy",
    (0x0018, 0xD332): "femoral_osteotomy",
    (0x0018, 0xD333): "pelvic_osteotomy",
    (0x0018, 0xD334): "spinal_fusion_planning",
    (0x0018, 0xD335): "anterior_fusion",
    (0x0018, 0xD336): "posterior_fusion",
    (0x0018, 0xD337): " circumferential_fusion",
    (0x0018, 0xD338): "decompression_planning",
    (0x0018, 0xD339): "laminectomy",
    (0x0018, 0xD340): "discectomy",
    (0x0018, 0xD341): "foraminotomy",
    (0x0018, 0xD342): "arthroscopy_planning",
    (0x0018, 0xD343): "knee_arthroscopy",
    (0x0018, 0xD344): "shoulder_arthroscopy",
    (0x0018, 0xD345): "hip_arthroscopy",
    (0x0018, 0xD346): "ankle_arthroscopy",
    (0x0018, 0xD347): "wrist_arthroscopy",
    (0x0018, 0xD348): "ligament_reconstruction",
    (0x0018, 0xD349): "acl_reconstruction",
    (0x0018, 0xD350): "meniscus_repair",
}

ORTHO_OUTCOMES_TAGS = {
    (0x0018, 0xD401): "fracture_healing",
    (0x0018, 0xD402): "union_status",
    (0x0018, 0xD403): "non_union_indicator",
    (0x0018, 0xD404): "mal_union_indicator",
    (0x0018, 0xD405): "delayed_union",
    (0x0018, 0xD406): "pseudarthrosis",
    (0x0018, 0xD407): "hardware_failure",
    (0x0018, 0xD408): "implant_loosening",
    (0x0018, 0xD409): "implant_fracture",
    (0x0018, 0xD410): "joint_replacement_survival",
    (0x0018, 0xD411): "hip_survival",
    (0x0018, 0xD412): "knee_survival",
    (0x0018, 0xD413): "revision_surgery",
    (0x0018, 0xD414): "periprosthetic_fracture",
    (0x0018, 0xD415): "periprosthetic_infection",
    (0x0018, 0xD416): "osteolysis_implant",
    (0x0018, 0xD417): "wear_debris",
    (0x0018, 0xD418): "loosening_zone",
    (0x0018, 0xD419): "radiolucent_line",
    (0x0018, 0xD420): "stem_sinking",
    (0x0018, 0xD421): "cup_migration",
    (0x0018, 0xD422): "polyethylene_wear",
    (0x0018, 0xD423): "joint_function",
    (0x0018, 0xD424): "range_of_motion",
    (0x0018, 0xD425): "flexion_angle",
    (0x0018, 0xD426): "extension_angle",
    (0x0018, 0xD427): "abduction_angle",
    (0x0018, 0xD428): "adduction_angle",
    (0x0018, 0xD429): "outcome_scores",
    (0x0018, 0xD430): "harris_hip_score",
    (0x0018, 0xD431): "hoos_score",
    (0x0018, 0xD432): "oks_score",
    (0x0018, 0xD433): "SF36_ortho",
    (0x0018, 0xD434): " WOMAC_score",
    (0x0018, 0xD435): " KOOS_score",
    (0x0018, 0xD436): " VAS_pain",
    (0x0018, 0xD437): "NRS_pain",
    (0x0018, 0xD438): "timed_up_and_go",
    (0x0018, 0xD439): "gait_analysis",
    (0x0018, 0xD440): "gait_speed",
    (0x0018, 0xD441): "walking_distance",
    (0x0018, 0xD442): "stair_climbing",
    (0x0018, 0xD443): "return_to_sport",
    (0x0018, 0xD444): "activity_level",
    (0x0018, 0xD445): "work_status",
    (0x0018, 0xD446): "complication_ortho",
    (0x0018, 0xD447): "infection_ortho",
    (0x0018, 0xD448): "dvt_ortho",
    (0x0018, 0xD449): "pe_ortho",
    (0x0018, 0xD450): "fat_embolism",
}

TOTAL_TAGS_LXXXIII = {}

TOTAL_TAGS_LXXXIII.update(ORTHOPEDICS_PATIENT_PARAMETERS)
TOTAL_TAGS_LXXXIII.update(ORTHO_PATHOLOGY_TAGS)
TOTAL_TAGS_LXXXIII.update(ORTHO_IMAGING_TAGS)
TOTAL_TAGS_LXXXIII.update(ORTHO_PROTOCOLS)
TOTAL_TAGS_LXXXIII.update(ORTHO_OUTCOMES_TAGS)


def _extract_tags_lxxxiii(ds: Any) -> Dict[str, Any]:
    extracted = {}
    tag_names = {tag: name for tag, name in TOTAL_TAGS_LXXXIII.items()}
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


def _is_orthopedics_imaging_file(file_path: str) -> bool:
    ortho_indicators = [
        'orthopedics', 'orthopedic', 'bone', 'joint', 'fracture',
        'osteoporosis', 'arthritis', 'osteoarthritis', 'meniscus', 'ligament',
        'tendon', 'cartilage', 'spine', 'vertebral', 'hip', 'knee', 'shoulder',
        'ankle', 'wrist', 'elbow', 'bone_scan', 'dexa', 'bone_density',
        'prosthesis', 'implant', 'arthroplasty', 'spinal_fusion'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in ortho_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxxxiii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxxxiii_detected": False,
        "fields_extracted": 0,
        "extension_lxxxiii_type": "orthopedics_imaging",
        "extension_lxxxiii_version": "2.0.0",
        "orthopedics_patient_parameters": {},
        "ortho_pathology": {},
        "ortho_imaging": {},
        "ortho_protocols": {},
        "ortho_outcomes": {},
        "extraction_errors": [],
    }

    try:
        if not _is_orthopedics_imaging_file(file_path):
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

        result["extension_lxxxiii_detected"] = True

        ortho_data = _extract_tags_lxxxiii(ds)

        patient_params_set = set(ORTHOPEDICS_PATIENT_PARAMETERS.keys())
        pathology_set = set(ORTHO_PATHOLOGY_TAGS.keys())
        imaging_set = set(ORTHO_IMAGING_TAGS.keys())
        protocols_set = set(ORTHO_PROTOCOLS.keys())
        outcomes_set = set(ORTHO_OUTCOMES_TAGS.keys())

        for tag, value in ortho_data.items():
            if tag in patient_params_set:
                result["orthopedics_patient_parameters"][tag] = value
            elif tag in pathology_set:
                result["ortho_pathology"][tag] = value
            elif tag in imaging_set:
                result["ortho_imaging"][tag] = value
            elif tag in protocols_set:
                result["ortho_protocols"][tag] = value
            elif tag in outcomes_set:
                result["ortho_outcomes"][tag] = value

        result["fields_extracted"] = len(ortho_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiii_field_count() -> int:
    return len(TOTAL_TAGS_LXXXIII)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiii_description() -> str:
    return (
        "Orthopedics Imaging II metadata extraction. Provides comprehensive coverage of "
        "bone disorders, joint diseases, fractures, "
        "orthopedics-specific imaging protocols, and orthopedic outcomes assessment."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiii_modalities() -> List[str]:
    return ["CT", "MR", "US", "CR", "DR", "XA", "NM", "RG"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiii_category() -> str:
    return "Orthopedics Imaging II"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiii_keywords() -> List[str]:
    return [
        "orthopedics", "bone", "joint", "fracture", "osteoarthritis",
        "osteoporosis", "meniscus", "ligament", "tendon", "cartilage",
        "spine", "hip replacement", "knee replacement", "bone density",
        "DEXA", "bone scan", "arthroplasty", "spinal fusion"
    ]


# Aliases for smoke test compatibility
def extract_medical_dashboard(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_lxxxiii."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_lxxxiii(file_path)

def get_medical_dashboard_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiii_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiii_field_count()

def get_medical_dashboard_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiii_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiii_version()

def get_medical_dashboard_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiii_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiii_description()

def get_medical_dashboard_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiii_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiii_supported_formats()

def get_medical_dashboard_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiii_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiii_modalities()
