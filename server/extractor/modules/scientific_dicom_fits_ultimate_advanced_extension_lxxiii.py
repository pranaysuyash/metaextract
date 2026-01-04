"""
Scientific DICOM/FITS Ultimate Advanced Extension LXXIII - Rheumatology Imaging II

This module provides comprehensive extraction of Rheumatology Imaging parameters
including inflammatory arthritis, connective tissue diseases, autoimmune disorders,
and rheumatology-specific imaging protocols.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXIII_AVAILABLE = True

RHEUMATOLOGY_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x7010): "rheumatology_assessment_date",
    (0x0010, 0x7011): "rheumatologic_diagnosis",
    (0x0010, 0x7012): "rheumatoid_arthritis",
    (0x0010, 0x7013): "seropositive_ra",
    (0x0010, 0x7014): "seronegative_ra",
    (0x0010, 0x7015): "juvenile_idiopathic_arthritis",
    (0x0010, 0x7016): "psoriatic_arthritis",
    (0x0010, 0x7017): "ankylosing_spondylitis",
    (0x0010, 0x7018): "reactive_arthritis",
    (0x0010, 0x7019): "enteropathic_arthritis",
    (0x0010, 0x7020): "undifferentiated_spondyloarthritis",
    (0x0010, 0x7021): "systemic_lupus_erythematosus",
    (0x0010, 0x7022): "sle_diagnosis",
    (0x0010, 0x7023): "sle_renal_involvement",
    (0x0010, 0x7024): "sle_neuropsychiatric",
    (0x0010, 0x7025): "sle_hematologic",
    (0x0010, 0x7026): "antiphospholipid_syndrome",
    (0x0010, 0x7027): "sjogrens_syndrome",
    (0x0010, 0x7028): "scleroderma",
    (0x0010, 0x7029): "systemic_sclerosis",
    (0x0010, 0x7030): "limited_scleroderma",
    (0x0010, 0x7031): "diffuse_scleroderma",
    (0x0010, 0x7032): "inflammatory_myopathy",
    (0x0010, 0x7033): "dermatomyositis",
    (0x0010, 0x7034): "polymyositis",
    (0x0010, 0x7035): "inclusion_body_myositis",
    (0x0010, 0x7036): "vasculitis_indicator",
    (0x0010, 0x7037): "giant_cell_arteritis",
    (0x0010, 0x7029): "takayasu_arteritis",
    (0x0010, 0x7040): "granulomatosis_polyangiitis",
    (0x0010, 0x7041): "microscopic_polyangiitis",
    (0x0010, 0x7042): "eosinophilic_granulomatosis",
    (0x0010, 0x7043): "behcets_disease",
    (0x0010, 0x7044): "polymyalgia_rheumatica",
    (0x0010, 0x7045): "gout_indicator",
    (0x0010, 0x7046): "hyperuricemia",
    (0x0010, 0x7047): "acute_gout",
    (0x0010, 0x7048): "chronic_gout",
    (0x0010, 0x7049): "tophaceous_gout",
    (0x0010, 0x7050): "pseudogout",
    (0x0010, 0x7051): "calcium_pyrophosphate",
    (0x0010, 0x7052): "disease_activity_score",
    (0x0010, 0x7053): "das28_score",
    (0x0010, 0x7054): "sdas_score",
    (0x0010, 0x7055): "cdas_score",
    (0x0010, 0x7056): "basdai_score",
    (0x0010, 0x7057): "asdas_score",
    (0x0010, 0x7058): "sle_dai_score",
    (0x0010, 0x7059): "rf_factor",
    (0x0010, 0x7060): "anti_ccp_antibody",
    (0x0010, 0x7061): "ana_titer",
    (0x0010, 0x7062): "anti_dsdna",
    (0x0010, 0x7063): "anti_smith",
    (0x0010, 0x7064): "anti_roSSA",
    (0x0010, 0x7065): "anti_laSSB",
    (0x0010, 0x7066): "anti_centromere",
    (0x0010, 0x7067): "anti_scl70",
    (0x0010, 0x7068): "anti_jo1",
    (0x0010, 0x7069): "anca_pattern",
}

RHEUMATOLOGY_PATHOLOGY_TAGS = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0x7101): "synovial_hypertrophy",
    (0x0018, 0x7102): "synovial_proliferation",
    (0x0018, 0x7103): "pannus_formation",
    (0x0018, 0x7104): "cartilage_loss",
    (0x0018, 0x7105): "bone_erosion",
    (0x0018, 0x7106): "marginal_erosion",
    (0x0018, 0x7107): "central_erosion",
    (0x0018, 0x7108): "erosion_size",
    (0x0018, 0x7109): "erosion_count",
    (0x0018, 0x7110): "joint_space_narrowing",
    (0x0018, 0x7111): "subluxation",
    (0x0018, 0x7112): "deformity_indicator",
    (0x0018, 0x7113): "boutonniere_deformity",
    (0x0018, 0x7114): "swan_neck_deformity",
    (0x0018, 0x7115): "ulnar_deviation",
    (0x0018, 0x7116): "bouchard_nodes",
    (0x0018, 0x7117): "heberden_nodes",
    (0x0018, 0x7118): "harrison_nodes",
    (0x0018, 0x7119): "tenosynovitis",
    (0x0018, 0x7120): "paratenonitis",
    (0x0018, 0x7121): "enthesitis",
    (0x0018, 0x7122): "entheseal_change",
    (0x0018, 0x7123): "entheseal_erosion",
    (0x0018, 0x7124): "entheseal_sclerosis",
    (0x0018, 0x7125): "sacroiliitis",
    (0x0018, 0x7126): "grade_1_sacroiliitis",
    (0x0018, 0x7127): "grade_2_sacroiliitis",
    (0x0018, 0x7128): "grade_3_sacroiliitis",
    (0x0018, 0x7129): "grade_4_sacroiliitis",
    (0x0018, 0x7130): "spondylitis",
    (0x0018, 0x7131): "syndesmophyte",
    (0x0018, 0x7132): "marginal_syndesmophyte",
    (0x0018, 0x7133): "paramarginal_syndesmophyte",
    (0x0018, 0x7134): "bamboo_spine",
    (0x0018, 0x7135): "square_vertebrae",
    (0x0018, 0x7136): " Andersson_lesion",
    (0x0018, 0x7137): "periarticular_osteoporosis",
    (0x0018, 0x7138): "periostitis",
    (0x0018, 0x7139): "dactylitis",
    (0x0018, 0x7140): "sausage_digit",
    (0x0018, 0x7141): "psoriatic_nail",
    (0x0018, 0x7142): "oncholysis",
    (0x0018, 0x7143): "subungual_hyperkeratosis",
    (0x0018, 0x7144): "tophus_formation",
    (0x0018, 0x7145): "tophus_location",
    (0x0018, 0x7146): "tophus_size",
    (0x0018, 0x7147): "double_contour_sign",
    (0x0018, 0x7148): "urate_crystal",
    (0x0018, 0x7149): "chondrocalcinosis",
}

RHEUMATOLOGY_IMAGING_TAGS = {
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
    (0x0018, 0x7201): "hand_xray",
    (0x0018, 0x7202): "foot_xray",
    (0x0018, 0x7203): "wrist_xray",
    (0x0018, 0x7204): "knee_xray",
    (0x0018, 0x7205): "hip_xray",
    (0x0018, 0x7206): "spine_xray",
    (0x0018, 0x7207): "pelvis_xray",
    (0x0018, 0x7208): "joint_xray",
    (0x0018, 0x7209): "ct_joint_protocol",
    (0x0018, 0x7210): "ct_arthrography",
    (0x0018, 0x7211): "mri_joint_protocol",
    (0x0018, 0x7212): "mri_arthritis_protocol",
    (0x0018, 0x7213): "mri_hand_protocol",
    (0x0018, 0x7214): "mri_wrist_protocol",
    (0x0018, 0x7215): "mri_foot_protocol",
    (0x0018, 0x7216): "mri_spine_protocol",
    (0x0018, 0x7217): "mri_sacroiliac_joint",
    (0x0018, 0x7218): "whole_body_mri",
    (0x0018, 0x7219): "ultrasound_joint",
    (0x0018, 0x7220): "power_doppler_joint",
    (0x0018, 0x7221): "elastography_joint",
    (0x0018, 0x7222): "contrast_enhanced_ultrasound",
    (0x0018, 0x7223): "bone_scan_rheum",
    (0x0018, 0x7224): "spect_ct_rheum",
    (0x0018, 0x7225): "pet_ct_rheum",
    (0x0018, 0x7226): "fdg_pet_arthritis",
    (0x0018, 0x7227): "na_fluoride_bone",
    (0x0018, 0x7228): "dual_energy_ct",
    (0x0018, 0x7229): "uric_acid_imaging",
    (0x0018, 0x7230): "dexa_rheumatology",
    (0x0018, 0x7231): "trabecular_bone_score",
    (0x0018, 0x7232): "vertebral_fracture_assessment",
    (0x0018, 0x7233): "hr_pqct",
    (0x0018, 0x7234): "peripheral_qct",
    (0x0018, 0x7235): "capillaroscopy",
    (0x0018, 0x7236): "nailfold_capillaroscopy",
    (0x0018, 0x7237): "thermography",
    (0x0018, 0x7238): "infrared_imaging",
    (0x0018, 0x7239): "angiography_vasculitis",
    (0x0018, 0x7240): "mra_vasculitis",
    (0x0018, 0x7241): "cta_vasculitis",
    (0x0018, 0x7242): "pet_vasculitis",
    (0x0018, 0x7243): "temporal_artery_biopsy",
    (0x0018, 0x7244): "imaging_guided_biopsy",
    (0x0018, 0x7245): "synovial_biopsy",
    (0x0018, 0x7246): "bone_biopsy_rheum",
    (0x0018, 0x7247): "muscle_biopsy",
    (0x0018, 0x7248): "skin_biopsy_scleroderma",
    (0x0018, 0x7249): "renal_biopsy_lupus",
}

RHEUMATOLOGY_PROTOCOLS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0x7301): "arthritis_scoring",
    (0x0018, 0x7302): "sharp_score",
    (0x0018, 0x7303): "modified_sharp_score",
    (0x0018, 0x7304): "van_der_heijde_sharp",
    (0x0018, 0x7305): "genant_sharp_score",
    (0x0018, 0x7306): "rakulcsar_score",
    (0x0018, 0x7307): "omrac_score",
    (0x0018, 0x7308): "psoriatic_arthritis_score",
    (0x0018, 0x7309): "psax_score",
    (0x0018, 0x7310): "mossai_score",
    (0x0018, 0x7311): "spondyloarthritis_score",
    (0x0018, 0x7312): "basri_score",
    (0x0018, 0x7313): "basri_spine",
    (0x0018, 0x7314): "basri_hip",
    (0x0018, 0x7315): "ct_scoring",
    (0x0018, 0x7316): "mri_scoring",
    (0x0018, 0x7317): "ramris_score",
    (0x0018, 0x7318): "omeras_score",
    (0x0018, 0x7319): "sadas_score",
    (0x0018, 0x7320): "spada_score",
    (0x0018, 0x7321): "treatment_monitoring",
    (0x0018, 0x7322): "dmard_therapy",
    (0x0018, 0x7323): "biologic_therapy",
    (0x0018, 0x7324): "tnf_inhibitor",
    (0x0018, 0x7325): "il6_inhibitor",
    (0x0018, 0x7326): "b_cell_therapy",
    (0x0018, 0x7327): "t_cell_co_stimulation",
    (0x0018, 0x7328): "jak_inhibitor",
    (0x0018, 0x7329): "intra_articular_injection",
    (0x0018, 0x7330): "ultrasound_guided_injection",
    (0x0018, 0x7331): "fluoroscopic_guided",
    (0x0018, 0x7332): "steroid_injection",
    (0x0018, 0x7333): "hyaluronic_acid",
    (0x0018, 0x7334): "prp_injection",
    (0x0018, 0x7335): "synovectomy",
    (0x0018, 0x7336): "radioactive_synovectomy",
    (0x0018, 0x7337): "surgical_arthroplasty",
    (0x0018, 0x7338): "joint_replacement",
    (0x0018, 0x7339): "joint_fusion",
    (0x0018, 0x7340): "spinal_surgery",
    (0x0018, 0x7341): "sacroiliac_joint_injection",
    (0x0018, 0x7342): "epidural_injection",
    (0x0018, 0x7343): "facet_joint_injection",
    (0x0018, 0x7344): "nerve_root_injection",
    (0x0018, 0x7345): "trigger_point_injection",
    (0x0018, 0x7346): "bursa_injection",
    (0x0018, 0x7347): "tendon_sheath_injection",
    (0x0018, 0x7348): "enthesopathy_treatment",
    (0x0018, 0x7349): "extracorporeal_therapy",
    (0x0018, 0x7350): "plasmapheresis",
}

RHEUMATOLOGY_OUTCOMES_TAGS = {
    (0x0018, 0x7401): "disease_activity",
    (0x0018, 0x7402): "remission_indicator",
    (0x0018, 0x7403): "low_disease_activity",
    (0x0018, 0x7404): "boolean_remission",
    (0x0018, 0x7405): "index_based_remission",
    (0x0018, 0x7406): "radiographic_progression",
    (0x0018, 0x7407): "progression_rate",
    (0x0018, 0x7408): "no_radiographic_progression",
    (0x0018, 0x7409): "erosion_progression",
    (0x0018, 0x7410): "joint_space_narrowing_prog",
    (0x0018, 0x7411): "functional_status",
    (0x0018, 0x7412): "haq_score",
    (0x0018, 0x7413): "mhaq_score",
    (0x0018, 0x7414): "sf36_physical",
    (0x0018, 0x7415): "sf36_mental",
    (0x0018, 0x7416): "work_productivity",
    (0x0018, 0x7417): "disability_index",
    (0x0018, 0x7418): "treatment_response",
    (0x0018, 0x7419): "eular_response",
    (0x0018, 0x7420): "good_response",
    (0x0018, 0x7421): "moderate_response",
    (0x0018, 0x7422): "no_response",
    (0x0018, 0x7423): "adverse_events_rheum",
    (0x0018, 0x7424): "infection_risk",
    (0x0018, 0x7425): "infusion_reaction",
    (0x0018, 0x7426): "laboratory_monitoring",
    (0x0018, 0x7427): "liver_toxicity",
    (0x0018, 0x7428): "hematologic_toxicity",
    (0x0018, 0x7429): "complication_arthritis",
    (0x0018, 0x7430): "joint_destruction",
    (0x0018, 0x7431): "joint_replacement_needed",
    (0x0018, 0x7432): "surgery_required",
    (0x0018, 0x7433): "mortality_rheum",
    (0x0018, 0x7434): "cardiovascular_mortality",
    (0x0018, 0x7435): "malignancy_risk",
    (0x0018, 0x7436): "osteoporosis_fracture",
    (0x0018, 0x7437): "vertebral_fracture",
    (0x0018, 0x7438): "non_vertebral_fracture",
    (0x0018, 0x7439): "quality_of_life_rheum",
    (0x0018, 0x7440): "ra_qol",
    (0x0018, 0x7441): "as_qol",
    (0x0018, 0x7442): "sle_qol",
    (0x0018, 0x7443): "fatigue_score",
    (0x0018, 0x7444): "pain_score",
    (0x0018, 0x7445): "global_assessment",
    (0x0018, 0x7446): "patient_global",
    (0x0018, 0x7447): "physician_global",
    (0x0018, 0x7448): "morning_stiffness",
    (0x0018, 0x7449): "duration_stiffness",
    (0x0018, 0x7450): "flare_indicator",
}

TOTAL_TAGS_LXXIII = {}

TOTAL_TAGS_LXXIII.update(RHEUMATOLOGY_PATIENT_PARAMETERS)
TOTAL_TAGS_LXXIII.update(RHEUMATOLOGY_PATHOLOGY_TAGS)
TOTAL_TAGS_LXXIII.update(RHEUMATOLOGY_IMAGING_TAGS)
TOTAL_TAGS_LXXIII.update(RHEUMATOLOGY_PROTOCOLS)
TOTAL_TAGS_LXXIII.update(RHEUMATOLOGY_OUTCOMES_TAGS)


def _extract_tags_lxxiii(ds: Any) -> Dict[str, Any]:
    extracted = {}
    tag_names = {tag: name for tag, name in TOTAL_TAGS_LXXIII.items()}
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


def _is_rheumatology_imaging_file(file_path: str) -> bool:
    rheum_indicators = [
        'rheumatology', 'rheumatoid', 'arthritis', 'lupus', 'sle',
        'scleroderma', 'myositis', 'vasculitis', 'gout', 'ankylosing',
        'spondyloarthritis', 'psoriatic', 'inflammatory_arthritis',
        'autoimmune', 'das28', 'bone_erosion', 'synovitis', 'mri_arthritis'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in rheum_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxxiii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxxiii_detected": False,
        "fields_extracted": 0,
        "extension_lxxiii_type": "rheumatology_imaging",
        "extension_lxxiii_version": "2.0.0",
        "rheumatology_patient_parameters": {},
        "rheumatology_pathology": {},
        "rheumatology_imaging": {},
        "rheumatology_protocols": {},
        "rheumatology_outcomes": {},
        "extraction_errors": [],
    }

    try:
        if not _is_rheumatology_imaging_file(file_path):
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

        result["extension_lxxiii_detected"] = True

        rheum_data = _extract_tags_lxxiii(ds)

        patient_params_set = set(RHEUMATOLOGY_PATIENT_PARAMETERS.keys())
        pathology_set = set(RHEUMATOLOGY_PATHOLOGY_TAGS.keys())
        imaging_set = set(RHEUMATOLOGY_IMAGING_TAGS.keys())
        protocols_set = set(RHEUMATOLOGY_PROTOCOLS.keys())
        outcomes_set = set(RHEUMATOLOGY_OUTCOMES_TAGS.keys())

        for tag, value in rheum_data.items():
            if tag in patient_params_set:
                result["rheumatology_patient_parameters"][tag] = value
            elif tag in pathology_set:
                result["rheumatology_pathology"][tag] = value
            elif tag in imaging_set:
                result["rheumatology_imaging"][tag] = value
            elif tag in protocols_set:
                result["rheumatology_protocols"][tag] = value
            elif tag in outcomes_set:
                result["rheumatology_outcomes"][tag] = value

        result["fields_extracted"] = len(rheum_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxiii_field_count() -> int:
    return len(TOTAL_TAGS_LXXIII)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxiii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxiii_description() -> str:
    return (
        "Rheumatology Imaging II metadata extraction. Provides comprehensive coverage of "
        "inflammatory arthritis, connective tissue diseases, autoimmune disorders, "
        "rheumatology-specific imaging protocols, and rheumatology outcomes assessment."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxiii_modalities() -> List[str]:
    return ["CT", "MR", "US", "CR", "DR", "NM", "XA", "RG"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxiii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxiii_category() -> str:
    return "Rheumatology Imaging II"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxiii_keywords() -> List[str]:
    return [
        "rheumatology", "rheumatoid arthritis", "lupus", "SLE",
        "scleroderma", "vasculitis", "gout", "ankylosing spondylitis",
        "psoriatic arthritis", "inflammatory arthritis", "autoimmune",
        "arthritis imaging", "bone erosion", "synovitis", "DAS28"
    ]
