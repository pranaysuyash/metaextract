"""
Scientific DICOM/FITS Ultimate Advanced Extension LXXIX - Urology Imaging II

This module provides comprehensive extraction of Urology Imaging parameters
including prostate health, bladder function, urologic oncology, and 
urology-specific imaging protocols.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXIX_AVAILABLE = True

UROLOGY_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x8001): "urology_assessment_date",
    (0x0010, 0x8002): "prostate_specific_antigen",
    (0x0010, 0x8003): "psa_velocity",
    (0x0010, 0x8004): "psa_density",
    (0x0010, 0x8005): "free_psa",
    (0x0010, 0x8006): "psa_ratio",
    (0x0010, 0x8007): "prostate_volume",
    (0x0010, 0x8008): "psa_historic",
    (0x0010, 0x8009): "digital_rectal_exam",
    (0x0010, 0x8010): "prostate_nodule",
    (0x0010, 0x8011): "prostate_abnormality",
    (0x0010, 0x8012): "gleason_score",
    (0x0010, 0x8013): "gleason_grade_primary",
    (0x0010, 0x8014): "gleason_grade_secondary",
    (0x0010, 0x8015): "gleason_tertiary",
    (0x0010, 0x8016): "gleason_group",
    (0x0010, 0x8017): "prostate_cancer_stage",
    (0x0010, 0x8018): "tnm_stage",
    (0x0010, 0x8019): "clinical_stage",
    (0x0010, 0x8020): "pathologic_stage",
    (0x0010, 0x8021): "prostatectomy_status",
    (0x0010, 0x8022): "radiation_status",
    (0x0010, 0x8023): "hormone_status",
    (0x0010, 0x8024): "chemotherapy_status",
    (0x0010, 0x8025): "active_surveillance",
    (0x0010, 0x8026): "watchful_waiting",
    (0x0010, 0x8027): "bladder_diagnosis",
    (0x0010, 0x8028): "bladder_cancer_stage",
    (0x0010, 0x8029): "hematuria_presence",
    (0x0010, 0x8030): "gross_hematuria",
    (0x0010, 0x8031): "microscopic_hematuria",
    (0x0010, 0x8032): "urinary_symptoms",
    (0x0010, 0x8033): "lower_urinary_tract_symptoms",
    (0x0010, 0x8034): "ipps_score",
    (0x0010, 0x8035): "urinary_frequency",
    (0x0010, 0x8036): "urinary_urgency",
    (0x0010, 0x8037): "urinary_incontinence",
    (0x0010, 0x8038): "stress_incontinence",
    (0x0010, 0x8039): "urge_incontinence",
    (0x0010, 0x8040): "overflow_incontinence",
    (0x0010, 0x8041): "functional_incontinence",
    (0x0010, 0x8042): "nocturia_frequency",
    (0x0010, 0x8043): "urinary_retention",
    (0x0010, 0x8044): "post_void_residual",
    (0x0010, 0x8045): "uroflowmetry_peak",
    (0x0010, 0x8046): "uroflowmetry_volume",
    (0x0010, 0x8047): "uroflowmetry_time",
    (0x0010, 0x8048): "urodynamics_results",
    (0x0010, 0x8049): "bladder_capacity",
    (0x0010, 0x8050): "detrusor_overactivity",
    (0x0010, 0x8051): "bladder_outlet_obstruction",
    (0x0010, 0x8052): "sphincter_dysfunction",
    (0x0010, 0x8053): "erectile_function",
    (0x0010, 0x8054): "iief_score",
    (0x0010, 0x8055): "ejaculatory_function",
    (0x0010, 0x8056): "infertility_status",
    (0x0010, 0x8057): "sperm_count",
    (0x0010, 0x8058): "sperm_motility",
    (0x0010, 0x8059): "sperm_morphology",
}

UROLOGIC_ONCOLOGY_TAGS = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0x8101): "prostate_mri_indicator",
    (0x0018, 0x8102): "pi_rads_score",
    (0x0018, 0x8103): "pi_rads_v2",
    (0x0018, 0x8104): "pi_rads_v2_1",
    (0x0018, 0x8105): "pi_rads_v2_2",
    (0x0018, 0x8106): "lesion_location_prostate",
    (0x0018, 0x8107): "lesion_size_prostate",
    (0x0018, 0x8108): "lesion_apex",
    (0x0018, 0x8109): "lesion_mid_gland",
    (0x0018, 0x8110): "lesion_base",
    (0x0018, 0x8111): "lesion_peripheral_zone",
    (0x0018, 0x8112): "lesion_transition_zone",
    (0x0018, 0x8113): "extracapsular_extension",
    (0x0018, 0x8114): "seminal_vesicle_invasion",
    (0x0018, 0x8115): "lymph_node_involvement",
    (0x0018, 0x8116): "bone_metastasis",
    (0x0018, 0x8117): "prostate_specific_membrane_antigen",
    (0x0018, 0x8118): "psma_expression",
    (0x0018, 0x8119): "psma_pet_scan",
    (0x0018, 0x8120): "fluciclovine_scan",
    (0x0018, 0x8121): "choline_scan",
    (0x0018, 0x8122): "prostate_cancer_recurrence",
    (0x0018, 0x8123): "biochemical_recurrence",
    (0x0018, 0x8124): "psa_bounce",
    (0x0018, 0x8125): "psa_doubling_time",
    (0x0018, 0x8126): "prostate_biopsy_results",
    (0x0018, 0x8127): "positive_cores",
    (0x0018, 0x8128): "max_core_involvement",
    (0x0018, 0x8129): "percent_core_involvement",
    (0x0018, 0x8130): "perineural_invasion",
    (0x0018, 0x8131): "lymphovascular_invasion",
    (0x0018, 0x8132): "intraductal_carcinoma",
    (0x0018, 0x8133): "cribriform_pattern",
    (0x0018, 0x8134): "ductal_carcinoma",
    (0x0018, 0x8135): "mucin_production",
    (0x0018, 0x8136): "small_cell_carcinoma",
    (0x0018, 0x8137): "neuroendocrine_differentiation",
    (0x0018, 0x8138): "adenocarcinoma",
    (0x0018, 0x8139): "bladder_tumor_indicator",
    (0x0018, 0x8140): "bladder_cancer_type",
    (0x0018, 0x8141): "urothelial_carcinoma",
    (0x0018, 0x8142): "squamous_cell_carcinoma_bladder",
    (0x0018, 0x8143): "adenocarcinoma_bladder",
    (0x0018, 0x8144): "small_cell_bladder",
    (0x0018, 0x8145): "bladder_cancer_grade",
    (0x0018, 0x8146): "papillary_carcinoma",
    (0x0018, 0x8147): "carcinoma_in_situ",
    (0x0018, 0x8148): "muscle_invasive",
    (0x0018, 0x8149): "non_muscle_invasive",
}

BLADDER_FUNCTION_TAGS = {
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
    (0x0018, 0x8201): "cystoscopy_findings",
    (0x0018, 0x8202): "bladder_tumor_location",
    (0x0018, 0x8203): "bladder_tumor_size",
    (0x0018, 0x8204): "bladder_tumor_number",
    (0x0018, 0x8205): "bladder_wall_thickness",
    (0x0018, 0x8206): "trigone_involvement",
    (0x0018, 0x8207): "ureteral_orifice_involvement",
    (0x0018, 0x8208): "diverticulum_indicator",
    (0x0018, 0x8209): "bladder_stone",
    (0x0018, 0x8210): "foreign_body_bladder",
    (0x0018, 0x8211): "cystocele_grade",
    (0x0018, 0x8212): "rectocele_grade",
    (0x0018, 0x8213): "pelvic_organ_prolapse",
    (0x0018, 0x8214): "enterocele",
    (0x0018, 0x8215): "sigmoidocele",
    (0x0018, 0x8216): "uterine_prolapse",
    (0x0018, 0x8217): "vaginal_prolapse",
    (0x0018, 0x8218): "pelvic_floor_dysfunction",
    (0x0018, 0x8219): "interstitial_cystitis",
    (0x0018, 0x8220): "painful_bladder_syndrome",
    (0x0018, 0x8221): "hemorrhagic_cystitis",
    (0x0018, 0x8222): "radiation_cystitis",
    (0x0018, 0x8223): "chemical_cystitis",
    (0x0018, 0x8224): "infectious_cystitis",
    (0x0018, 0x8225): "recurrent_uti",
    (0x0018, 0x8226): "bladder_capacity_measured",
    (0x0018, 0x8227): "compliance_curve",
    (0x0018, 0x8228): "detrusor_pressure",
    (0x0018, 0x8229): "abdominal_pressure",
    (0x0018, 0x8230): "voiding_pressure_study",
    (0x0018, 0x8231): "electromyography_urethra",
    (0x0018, 0x8232): "urethral_pressure_profile",
    (0x0018, 0x8233): "max_urethral_closure_pressure",
    (0x0018, 0x8234): "functional_profile_length",
    (0x0018, 0x8235): "stress_urethral_pressure",
    (0x0018, 0x8236): "valsalva_leak_point_pressure",
    (0x0018, 0x8237): "cough_leak_point_pressure",
    (0x0018, 0x8238): "bladder_sensation",
    (0x0018, 0x8239): "first_sensation",
    (0x0018, 0x8240): "first_desire_to_void",
    (0x0018, 0x8241): "strong_desire_to_void",
    (0x0018, 0x8242): "cystometric_capacity",
    (0x0018, 0x8243): "volume_at_leak",
    (0x0018, 0x8244): "bladder_contractility_index",
}

UROLOGY_IMAGING_PROTOCOLS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0x8301): "prostate_mri_protocol",
    (0x0018, 0x8302): "prostate_t2_imaging",
    (0x0018, 0x8303): "prostate_dwi",
    (0x0018, 0x8304): "prostate_dce",
    (0x0018, 0x8305): "prostate_spectroscopy",
    (0x0018, 0x8306): "mp_mri_prostate",
    (0x0018, 0x8307): "prostate_ultrasound",
    (0x0018, 0x8308): "transrectal_ultrasound",
    (0x0018, 0x8309): "endocavitary_ultrasound",
    (0x0018, 0x8310): "elastography_prostate",
    (0x0018, 0x8311): "contrast_enhanced_prostate",
    (0x0018, 0x8312): "prostate_biopsy_guidance",
    (0x0018, 0x8313): "fusion_biopsy",
    (0x0018, 0x8314): "mri_ultrasound_fusion",
    (0x0018, 0x8315): "in_bore_biopsy",
    (0x0018, 0x8316): "ct_urography_protocol",
    (0x0018, 0x8317): "mr_urography",
    (0x0018, 0x8318): "ct_kub",
    (0x0018, 0x8319): "ct_pelvis",
    (0x0018, 0x8320): "mr_pelvis",
    (0x0018, 0x8321): "bone_scan_prostate",
    (0x0018, 0x8322): "psma_pet_ct",
    (0x0018, 0x8323): "f18_psma",
    (0x0018, 0x8324): "ga68_psma",
    (0x0018, 0x8325): "fluciclovine_pet",
    (0x0018, 0x8326): "cystectomy_planning",
    (0x0018, 0x8327): "neobladder_evaluation",
    (0x0018, 0x8328): "continent_diversion",
    (0x0018, 0x8329): "ileal_conduit",
    (0x0018, 0x8330): "ureterostomy",
    (0x0018, 0x8331): "bladder_augmentation",
    (0x0018, 0x8332): "prostatectomy_planning",
    (0x0018, 0x8333): "nerve_sparing_planning",
    (0x0018, 0x8334): "lymph_node_mapping",
    (0x0018, 0x8335): "sentinel_lymph_node",
    (0x0018, 0x8336): "radiation_planning_prostate",
    (0x0018, 0x8337): "brachytherapy_prostate",
    (0x0018, 0x8338): "seed_implant",
    (0x0018, 0x8339): "external_beam_prostate",
    (0x0018, 0x8340): "sbrt_prostate",
    (0x0018, 0x8341): "hifu_prostate",
    (0x0018, 0x8342): "cryotherapy_prostate",
    (0x0018, 0x8343): "laser_ablation_prostate",
    (0x0018, 0x8344): "rezum_prostate",
    (0x0018, 0x8345): "urolift_procedure",
    (0x0018, 0x8346): "aquablation_prostate",
    (0x0018, 0x8347): "transurethral_resection",
    (0x0018, 0x8348): "turp_planning",
    (0x0018, 0x8349): "holep_planning",
    (0x0018, 0x8350): "kidney_stone_protocol",
}

UROLOGY_OUTCOMES_TAGS = {
    (0x0018, 0x8401): "prostate_cancer_survival",
    (0x0018, 0x8402): "cancer_specific_survival",
    (0x0018, 0x8403): "overall_survival_prostate",
    (0x0018, 0x8404): "progression_free_survival",
    (0x0018, 0x8405): "biochemical_survival",
    (0x0018, 0x8406): "metastasis_free_survival",
    (0x0018, 0x8407): "prostatectomy_outcomes",
    (0x0018, 0x8408): "positive_margins",
    (0x0018, 0x8409): "surgical_margin_status",
    (0x0018, 0x8410): "continence_recovery",
    (0x0018, 0x8411): "continence_timeline",
    (0x0018, 0x8412): "pad_use",
    (0x0018, 0x8413): "erectile_function_recovery",
    (0x0018, 0x8414): "nerve_sparing_outcomes",
    (0x0018, 0x8415): "urinary_function",
    (0x0018, 0x8416): "sexual_function",
    (0x0018, 0x8417): "rectal_toxicity",
    (0x0018, 0x8418): "urinary_toxicity",
    (0x0018, 0x8419): "bowel_function",
    (0x0018, 0x8420): "quality_of_life_prostate",
    (0x0018, 0x8421): "epic_score",
    (0x0018, 0x8422): "epic_urinary_score",
    (0x0018, 0x8423): "epic_bowel_score",
    (0x0018, 0x8424): "epic_sexual_score",
    (0x0018, 0x8425): "epic_hormonal_score",
    (0x0018, 0x8426): "expanded_prostate_cancer_index",
    (0x0018, 0x8427): "urinary_symptom_score",
    (0x0018, 0x8428): "incontinence_severity",
    (0x0018, 0x8429): "overactive_bladder_score",
    (0x0018, 0x8430): "bladder_cancer_outcomes",
    (0x0018, 0x8431): "recurrence_bladder",
    (0x0018, 0x8432): "progression_bladder",
    (0x0018, 0x8433): "cystectomy_free_survival",
    (0x0018, 0x8434): "ureteroenteric_stricture",
    (0x0018, 0x8435): "metabolic_complications",
    (0x0018, 0x8436): "renal_function_diversion",
    (0x0018, 0x8437): "vitamin_b12_deficiency",
    (0x0018, 0x8438): "metabolic_acidosis_diversion",
    (0x0018, 0x8439): "stone_form_diversion",
    (0x0018, 0x8440): "neobladder_function",
    (0x0018, 0x8441): "daytime_voiding_frequency",
    (0x0018, 0x8442): "nighttime_voiding",
    (0x0018, 0x8443): "catheter_dependence",
    (0x0018, 0x8444): "continent_stomas",
    (0x0018, 0x8445): "stoma_complications",
    (0x0018, 0x8446): "parastomal_hernia",
    (0x0018, 0x8447): "urostomy_care",
    (0x0018, 0x8448): "sexual_function_diversion",
    (0x0018, 0x8449): "body_image",
    (0x0018, 0x8450): "psychosocial_adaptation",
}

TOTAL_TAGS_LXXIX = {}

TOTAL_TAGS_LXXIX.update(UROLOGY_PATIENT_PARAMETERS)
TOTAL_TAGS_LXXIX.update(UROLOGIC_ONCOLOGY_TAGS)
TOTAL_TAGS_LXXIX.update(BLADDER_FUNCTION_TAGS)
TOTAL_TAGS_LXXIX.update(UROLOGY_IMAGING_PROTOCOLS)
TOTAL_TAGS_LXXIX.update(UROLOGY_OUTCOMES_TAGS)


def _extract_tags_lxxix(ds: Any) -> Dict[str, Any]:
    extracted = {}
    tag_names = {tag: name for tag, name in TOTAL_TAGS_LXXIX.items()}
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


def _is_urology_imaging_file(file_path: str) -> bool:
    urology_indicators = [
        'urology', 'urologic', 'prostate', 'bladder', 'urothelial',
        'psa', 'gleason', 'pi-rads', 'prostatectomy', 'cystectomy',
        'urinary', 'incontinence', 'overactive_bladder', 'kidney_stone',
        'renal_stone', 'nephrolithiasis', 'uroflowmetry', 'urodynamics'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in urology_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxxix(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxxix_detected": False,
        "fields_extracted": 0,
        "extension_lxxix_type": "urology_imaging",
        "extension_lxxix_version": "2.0.0",
        "urology_patient_parameters": {},
        "urologic_oncology": {},
        "bladder_function": {},
        "urology_imaging_protocols": {},
        "urology_outcomes": {},
        "extraction_errors": [],
    }

    try:
        if not _is_urology_imaging_file(file_path):
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

        result["extension_lxxix_detected"] = True

        urology_data = _extract_tags_lxxix(ds)

        patient_params_set = set(UROLOGY_PATIENT_PARAMETERS.keys())
        oncology_set = set(UROLOGIC_ONCOLOGY_TAGS.keys())
        bladder_set = set(BLADDER_FUNCTION_TAGS.keys())
        protocols_set = set(UROLOGY_IMAGING_PROTOCOLS.keys())
        outcomes_set = set(UROLOGY_OUTCOMES_TAGS.keys())

        for tag, value in urology_data.items():
            if tag in patient_params_set:
                result["urology_patient_parameters"][tag] = value
            elif tag in oncology_set:
                result["urologic_oncology"][tag] = value
            elif tag in bladder_set:
                result["bladder_function"][tag] = value
            elif tag in protocols_set:
                result["urology_imaging_protocols"][tag] = value
            elif tag in outcomes_set:
                result["urology_outcomes"][tag] = value

        result["fields_extracted"] = len(urology_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxix_field_count() -> int:
    return len(TOTAL_TAGS_LXXIX)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxix_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxix_description() -> str:
    return (
        "Urology Imaging II metadata extraction. Provides comprehensive coverage of "
        "prostate health parameters, urologic oncology, bladder function assessment, "
        "urology-specific imaging protocols, and urology outcomes measurement."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxix_modalities() -> List[str]:
    return ["CT", "MR", "US", "CR", "DR", "XA", "PT", "NM", "MG"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxix_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxix_category() -> str:
    return "Urology Imaging II"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxix_keywords() -> List[str]:
    return [
        "urology", "prostate", "bladder", "PSA", "Gleason", "PI-RADS",
        "prostate cancer", "bladder cancer", "urinary incontinence",
        "overactive bladder", "kidney stone", "urodynamics", "prostatectomy",
        "cystectomy", "BPH", "urothelial carcinoma"
    ]
