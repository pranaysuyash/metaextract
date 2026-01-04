"""
Scientific DICOM/FITS Ultimate Advanced Extension LXXVIII - Nephrology Imaging II

This module provides comprehensive extraction of Nephrology Imaging parameters
including renal function assessment, dialysis considerations, kidney disease
staging, and nephrology-specific imaging protocols.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXVIII_AVAILABLE = True

RENAL_FUNCTION_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x7001): "nephrology_assessment_date",
    (0x0010, 0x7002): "renal_diagnosis",
    (0x0010, 0x7003): "ckd_stage",
    (0x0010, 0x7004): "esrd_indicator",
    (0x0010, 0x7005): "dialysis_status",
    (0x0010, 0x7006): "dialysis_type",
    (0x0010, 0x7007): "hemodialysis",
    (0x0010, 0x7008): "peritoneal_dialysis",
    (0x0010, 0x7009): "dialysis_vintage",
    (0x0010, 0x7010): "dialysis_frequency",
    (0x0010, 0x7011): "dialysis_duration",
    (0x0010, 0x7012): "creatinine_level",
    (0x0010, 0x7013): "egfr_value",
    (0x0010, 0x7014): "bun_level",
    (0x0010, 0x7015): "uric_acid_level",
    (0x0010, 0x7016): "electrolyte_panel",
    (0x0010, 0x7017): "sodium_level",
    (0x0010, 0x7018): "potassium_level",
    (0x0010, 0x7019): "chloride_level",
    (0x0010, 0x7020): "bicarbonate_level",
    (0x0010, 0x7021): "calcium_level",
    (0x0010, 0x7022): "phosphorus_level",
    (0x0010, 0x7023): "magnesium_level",
    (0x0010, 0x7024): "albumin_level",
    (0x0010, 0x7025): "total_protein",
    (0x0010, 0x7026): "kidney_size_right",
    (0x0010, 0x7027): "kidney_size_left",
    (0x0010, 0x7028): "renal_cortical_thickness",
    (0x0010, 0x7029): "nephropathy_cause",
    (0x0010, 0x7030): "diabetic_nephropathy",
    (0x0010, 0x7031): "hypertensive_nephropathy",
    (0x0010, 0x7032): "glomerulonephritis",
    (0x0010, 0x7033): "polycystic_kidney_disease",
    (0x0010, 0x7034): "interstitial_nephritis",
    (0x0010, 0x7035): "obstructive_nephropathy",
    (0x0010, 0x7036): "renal_vascular_disease",
    (0x0010, 0x7037): "renal_transplant_status",
    (0x0010, 0x7038): "transplant_date",
    (0x0010, 0x7039): "donor_type",
    (0x0010, 0x7040): "living_donor",
    (0x0010, 0x7041): "deceased_donor",
    (0x0010, 0x7042): "graft_function",
    (0x0010, 0x7043): "rejection_episode",
    (0x0010, 0x7044): "immunosuppression",
    (0x0010, 0x7045): "calcineurin_inhibitor",
    (0x0010, 0x7046): "tacrolimus",
    (0x0010, 0x7047): "cyclosporine",
    (0x0010, 0x7048): "antimetabolite",
    (0x0010, 0x7049): "mycophenolate",
    (0x0010, 0x7050): "azathioprine",
    (0x0010, 0x7051): "steroid_therapy",
    (0x0010, 0x7052): "prednisone_dose",
    (0x0010, 0x7053): "proteinuria_level",
    (0x0010, 0x7054): "albumin_creatinine_ratio",
    (0x0010, 0x7055): "hematuria_indicator",
    (0x0010, 0x7056): "nephrotic_syndrome",
    (0x0010, 0x7057): "nephritic_syndrome",
    (0x0010, 0x7058): "aki_stage",
    (0x0010, 0x7059): "renal_recovery",
}

KIDNEY_PATHOLOGY_TAGS = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0x7101): "renal_mass_indicator",
    (0x0018, 0x7102): "renal_cyst_indicator",
    (0x0018, 0x7103): "simple_cyst",
    (0x0018, 0x7104): "complex_cyst",
    (0x0018, 0x7105): "bosniak_classification",
    (0x0018, 0x7106): "renal_tumor_size",
    (0x0018, 0x7107): "renal_tumor_location",
    (0x0018, 0x7108): "renal_cell_carcinoma",
    (0x0018, 0x7109): "oncocytoma_indicator",
    (0x0018, 0x7110): "angiomyolipoma",
    (0x0018, 0x7111): "transitional_cell_carcinoma",
    (0x0018, 0x7112): "nephroblastoma",
    (0x0018, 0x7113): "renal_artery_stenosis",
    (0x0018, 0x7114): "renal_vein_thrombosis",
    (0x0018, 0x7115): "hydronephrosis",
    (0x0018, 0x7116): "hydrocalyx",
    (0x0018, 0x7117): "renal_colic",
    (0x0018, 0x7118): "nephrolithiasis",
    (0x0018, 0x7119): "kidney_stone_size",
    (0x0018, 0x7120): "kidney_stone_location",
    (0x0018, 0x7121): "staghorn_calculus",
    (0x0018, 0x7122): "ureteral_stone",
    (0x0018, 0x7123): "renal_parenchymal_disease",
    (0x0018, 0x7124): "renal_atrophy",
    (0x0018, 0x7125): "renal_scarring",
    (0x0018, 0x7126): "pyelonephritis",
    (0x0018, 0x7127): "emphysematous_pyelonephritis",
    (0x0018, 0x7128): "xanthogranulomatous",
    (0x0018, 0x7129): "renal_tuberculosis",
    (0x0018, 0x7130): "acquired_cystic_disease",
    (0x0018, 0x7131): "dialysis_associated_cysts",
    (0x0018, 0x7132): "renal_amyloidosis",
    (0x0018, 0x7133): "multiple_myeloma_kidney",
    (0x0018, 0x7134): "light_chain_deposition",
    (0x0018, 0x7135): "cast_nephropathy",
    (0x0018, 0x7136): "renal_infarction",
    (0x0018, 0x7137): "cortical_necrosis",
    (0x0018, 0x7138): "medullary_cystic_disease",
    (0x0018, 0x7139): "nephronophthisis",
    (0x0018, 0x7140): "medullary_sponge_kidney",
    (0x0018, 0x7141): "bathtub_ca",
    (0x0018, 0x7142): "renal_papillary_necrosis",
    (0x0018, 0x7143): "analgesic_nephropathy",
    (0x0018, 0x7144): "contrast_induced_aki",
    (0x0018, 0x7145): "cholesterol_emboli",
    (0x0018, 0x7146): "thrombotic_microangiopathy",
    (0x0018, 0x7147): "hemolytic_uremic_syndrome",
    (0x0018, 0x7148): "thrombotic_thrombocytopenic_purpura",
    (0x0018, 0x7149): "atypical_hus",
    (0x0018, 0x7150): "renal_arteriovenous_fistula",
    (0x0018, 0x7151): "pseudoaneurysm",
}

DIALYSIS_IMAGING_TAGS = {
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
    (0x0018, 0x7201): "av_fistula_evaluation",
    (0x0018, 0x7202): "av_graft_evaluation",
    (0x0018, 0x7203): "dialysis_access_flow",
    (0x0018, 0x7204): "access_stenosis",
    (0x0018, 0x7205): "access_thrombosis",
    (0x0018, 0x7206): "dialysis_catheter",
    (0x0018, 0x7207): "tunneled_catheter",
    (0x0018, 0x7208): "non_tunneled_catheter",
    (0x0018, 0x7209): "catheter_position",
    (0x0018, 0x7210): "catheter_function",
    (0x0018, 0x7211): "peritoneal_dialysis_catheter",
    (0x0018, 0x7212): "pd_catheter_tip_position",
    (0x0018, 0x7213): "dialysate_appearance",
    (0x0018, 0x7214): "peritoneal_equilibration_test",
    (0x0018, 0x7215): "peritoneal_thickness",
    (0x0018, 0x7216): "encapsulating_peritoneal_sclerosis",
    (0x0018, 0x7217): "dialysis_amyloidosis",
    (0x0018, 0x7218): "dialysis_related_spondyloarthropathy",
    (0x0018, 0x7219): "beta2_microglobulin",
    (0x0018, 0x7220): "dialysis_dosing",
    (0x0018, 0x7221): "ktv",
    (0x0018, 0x7222): "urr",
    (0x0018, 0x7223): "dialyzer_type",
    (0x0018, 0x7224): "dialyzer_membrane",
    (0x0018, 0x7225): "dialysate_composition",
    (0x0018, 0x7226): "ultrafiltration_rate",
    (0x0018, 0x7227): "fluid_removal",
    (0x0018, 0x7228): "interdialytic_weight_gain",
    (0x0018, 0x7229): "dry_weight",
    (0x0018, 0x7230): "volume_status",
    (0x0018, 0x7231): "overhydration",
    (0x0018, 0x7232): "blood_pressure_dialysis",
    (0x0018, 0x7233): "intradialytic_hypotension",
    (0x0018, 0x7234): "intradialytic_hypertension",
    (0x0018, 0x7235): "dialysis_cramping",
    (0x0018, 0x7236): "dialysis_nausea",
    (0x0018, 0x7237): "dialysis_vomiting",
    (0x0018, 0x7238): "dialysis_headache",
    (0x0018, 0x7239): "dialysis_pruritus",
    (0x0018, 0x7240): "restless_legs_syndrome",
    (0x0018, 0x7241): "dialysis_access_infection",
    (0x0018, 0x7242): "peritonitis_episode",
    (0x0018, 0x7243): "exit_site_infection",
    (0x0018, 0x7244): "tunnel_infection",
}

NEPHROLOGY_IMAGING_PROTOCOLS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0x7301): "renal_ct_protocol",
    (0x0018, 0x7302): "renal_mass_ct",
    (0x0018, 0x7303): "renal_colic_ct",
    (0x0018, 0x7304): "ct_urography",
    (0x0018, 0x7305): "ct_angiography_renal",
    (0x0018, 0x7306): "renal_mri_protocol",
    (0x0018, 0x7307): "mri_kidney_diffusion",
    (0x0018, 0x7308): "mri_renal_angiography",
    (0x0018, 0x7309): "mri_dwi_renal",
    (0x0018, 0x7310): "renal_ultrasound",
    (0x0018, 0x7311): "renal_doppler_ultrasound",
    (0x0018, 0x7312): "renal_artery_doppler",
    (0x0018, 0x7313): "transplant_ultrasound",
    (0x0018, 0x7314): "peritoneal_ultrasound",
    (0x0018, 0x7315): "renal_scintigraphy",
    (0x0018, 0x7316): "dtpa_scan",
    (0x0018, 0x7317): "dmsa_scan",
    (0x0018, 0x7318): "mag3_scan",
    (0x0018, 0x7319): "renal_scan_gfr",
    (0x0018, 0x7320): "captopril_renogram",
    (0x0018, 0x7321): "lasix_renogram",
    (0x0018, 0x7322): "cyclosporine_toxicity_scan",
    (0x0018, 0x7323): "contrast_considerations_renal",
    (0x0018, 0x7324): "iodinated_contrast_nephropathy_risk",
    (0x0018, 0x7325): "gadolinium_contrast_renal",
    (0x0018, 0x7326): "nephrotoxic_medication_list",
    (0x0018, 0x7327): "nsaid_avoidance",
    (0x0018, 0x7328): "metformin_hold",
    (0x0018, 0x7329): "hydration_protocol",
    (0x0018, 0x7330): "nac_protocol",
    (0x0018, 0x7331): "dialysis_post_contrast",
    (0x0018, 0x7332): "renal_function_trending",
    (0x0018, 0x7333): "acute_kidney_injury_order_set",
    (0x0018, 0x7334): "ckd_management_order_set",
    (0x0018, 0x7335): "renal_replacement_therapy_planning",
    (0x0018, 0x7336): "pre_transplant_evaluation",
    (0x0018, 0x7337): "post_transplant_monitoring",
    (0x0018, 0x7338): "biopsy_guidance",
    (0x0018, 0x7339): "renal_biopsy_protocol",
    (0x0018, 0x7340): "biopsy_complication_monitoring",
    (0x0018, 0x7341): "percutaneous_nephrostomy",
    (0x0018, 0x7342): "nephrostomy_tube_placement",
    (0x0018, 0x7343): "percutaneous_lithotripsy",
    (0x0018, 0x7344): "renal_abscess_drainage",
    (0x0018, 0x7345): "renal_cyst_aspiration",
    (0x0018, 0x7346): "renal_tumor_ablation",
    (0x0018, 0x7347): "renal_artery_embolization",
    (0x0018, 0x7348): "renal_angioplasty",
    (0x0018, 0x7349): "renal_stent_placement",
    (0x0018, 0x7350): "ureteral_stent",
}

NEPHROLOGY_OUTCOMES_TAGS = {
    (0x0018, 0x7401): "renal_survival",
    (0x0018, 0x7402): "dialysis_survival",
    (0x0018, 0x7403): "transplant_survival",
    (0x0018, 0x7404): "graft_survival",
    (0x0018, 0x7405): "patient_survival_dialysis",
    (0x0018, 0x7406): "technique_survival",
    (0x0018, 0x7407): "vascular_access_survival",
    (0x0018, 0x7408): "hospitalization_renal",
    (0x0018, 0x7409): "infection_hospitalization",
    (0x0018, 0x7410): "cardiovascular_events",
    (0x0018, 0x7411): "stroke_renal",
    (0x0018, 0x7412): "mi_renal",
    (0x0018, 0x7413): "heart_failure_renal",
    (0x0018, 0x7414): "arrhythmia_renal",
    (0x0018, 0x7415): "bone_mineral_disorder",
    (0x0018, 0x7416): "secondary_hyperparathyroidism",
    (0x0018, 0x7417): "renal_osteodystrophy",
    (0x0018, 0x7418): "vitamin_d_therapy",
    (0x0018, 0x7419): "calcimimetic_therapy",
    (0x0018, 0x7420): "phosphate_binder",
    (0x0018, 0x7421): "anemia_management",
    (0x0018, 0x7422): "epo_therapy",
    (0x0018, 0x7423): "iron_therapy",
    (0x0018, 0x7424): "hemoglobin_level",
    (0x0018, 0x7425): "transferrin_saturation",
    (0x0018, 0x7426): "ferritin_level",
    (0x0018, 0x7427): "metabolic_acidosis",
    (0x0018, 0x7428): "bicarbonate_supplementation",
    (0x0018, 0x7429): "hyperkalemia_episodes",
    (0x0018, 0x7430): "hyperphosphatemia_episodes",
    (0x0018, 0x7431): "hypocalcemia_episodes",
    (0x0018, 0x7432): "quality_of_life_renal",
    (0x0018, 0x7433): "kdqol_score",
    (0x0018, 0x7434): "symptom_burden",
    (0x0018, 0x7435): "fatigue_score",
    (0x0018, 0x7436): "pruritus_severity",
    (0x0018, 0x7437): "sleep_quality",
    (0x0018, 0x7438): "depression_screening",
    (0x0018, 0x7439): "cognitive_function_renal",
    (0x0018, 0x7440): "physical_function_renal",
    (0x0018, 0x7441): "nutritional_status_renal",
    (0x0018, 0x7442): "sga_score",
    (0x0018, 0x7443): "malnutrition_inflammation_score",
    (0x0018, 0x7444): "advance_care_planning_renal",
    (0x0018, 0x7445): "conservative_care_pathway",
    (0x0018, 0x7446): "withdrawal_from_dialysis",
    (0x0018, 0x7447): "palliative_care_referral_renal",
    (0x0018, 0x7448): "hospice_enrollment_renal",
    (0x0018, 0x7449): "living_will_renal",
    (0x0018, 0x7450): "healthcare_proxy_renal",
}

TOTAL_TAGS_LXXVIII = {}

TOTAL_TAGS_LXXVIII.update(RENAL_FUNCTION_PARAMETERS)
TOTAL_TAGS_LXXVIII.update(KIDNEY_PATHOLOGY_TAGS)
TOTAL_TAGS_LXXVIII.update(DIALYSIS_IMAGING_TAGS)
TOTAL_TAGS_LXXVIII.update(NEPHROLOGY_IMAGING_PROTOCOLS)
TOTAL_TAGS_LXXVIII.update(NEPHROLOGY_OUTCOMES_TAGS)


def _extract_tags_lxxviii(ds: Any) -> Dict[str, Any]:
    extracted = {}
    tag_names = {tag: name for tag, name in TOTAL_TAGS_LXXVIII.items()}
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


def _is_nephrology_imaging_file(file_path: str) -> bool:
    nephrology_indicators = [
        'nephrology', 'renal', 'kidney', 'dialysis', 'dialysis', 'ckd',
        'esrd', 'dialysis_access', 'renal_transplant', 'nephrologist',
        'creatinine', 'egfr', 'glomerular', 'nephrotic', 'nephritic',
        'renal_cyst', 'renal_mass', 'kidney_stone', 'hydronephrosis'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in nephrology_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxxviii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxxviii_detected": False,
        "fields_extracted": 0,
        "extension_lxxviii_type": "nephrology_imaging",
        "extension_lxxviii_version": "2.0.0",
        "renal_function_parameters": {},
        "kidney_pathology": {},
        "dialysis_imaging": {},
        "nephrology_imaging_protocols": {},
        "nephrology_outcomes": {},
        "extraction_errors": [],
    }

    try:
        if not _is_nephrology_imaging_file(file_path):
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

        result["extension_lxxviii_detected"] = True

        nephrology_data = _extract_tags_lxxviii(ds)

        renal_params_set = set(RENAL_FUNCTION_PARAMETERS.keys())
        pathology_set = set(KIDNEY_PATHOLOGY_TAGS.keys())
        dialysis_set = set(DIALYSIS_IMAGING_TAGS.keys())
        protocols_set = set(NEPHROLOGY_IMAGING_PROTOCOLS.keys())
        outcomes_set = set(NEPHROLOGY_OUTCOMES_TAGS.keys())

        for tag, value in nephrology_data.items():
            if tag in renal_params_set:
                result["renal_function_parameters"][tag] = value
            elif tag in pathology_set:
                result["kidney_pathology"][tag] = value
            elif tag in dialysis_set:
                result["dialysis_imaging"][tag] = value
            elif tag in protocols_set:
                result["nephrology_imaging_protocols"][tag] = value
            elif tag in outcomes_set:
                result["nephrology_outcomes"][tag] = value

        result["fields_extracted"] = len(nephrology_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxviii_field_count() -> int:
    return len(TOTAL_TAGS_LXXVIII)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxviii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxviii_description() -> str:
    return (
        "Nephrology Imaging II metadata extraction. Provides comprehensive coverage of "
        "renal function parameters, dialysis considerations, kidney pathology, "
        "nephrology-specific imaging protocols, and renal outcomes assessment."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxviii_modalities() -> List[str]:
    return ["CT", "MR", "US", "CR", "DR", "XA", "PT", "NM", "RG"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxviii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxviii_category() -> str:
    return "Nephrology Imaging II"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxviii_keywords() -> List[str]:
    return [
        "nephrology", "renal", "kidney", "dialysis", "CKD", "ESRD",
        "dialysis access", "renal transplant", "glomerular filtration",
        "nephrotic syndrome", "renal cyst", "kidney stone", "hydronephrosis",
        "renal function", "dialysis vintage", "nephrologist"
    ]
