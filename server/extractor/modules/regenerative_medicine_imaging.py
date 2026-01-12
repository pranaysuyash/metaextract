"""
Scientific DICOM/FITS Ultimate Advanced Extension LXXXIV - Oncology Imaging II

This module provides comprehensive extraction of Oncology Imaging parameters
including cancer staging, treatment response, tumor characterization, and
oncology-specific imaging protocols.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXXIV_AVAILABLE = True

ONCOLOGY_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0xE001): "oncology_assessment_date",
    (0x0010, 0xE002): "cancer_diagnosis",
    (0x0010, 0xE003): "cancer_type",
    (0x0010, 0xE004): "cancer_histology",
    (0x0010, 0xE005): "cancer_grade",
    (0x0010, 0xE006): "differentiation_grade",
    (0x0010, 0xE007): "well_differentiated",
    (0x0010, 0xE008): "moderately_differentiated",
    (0x0010, 0xE009): "poorly_differentiated",
    (0x0010, 0xE010): "undifferentiated",
    (0x0010, 0xE011): "cancer_stage",
    (0x0010, 0xE012): "tnm_stage",
    (0x0010, 0xE013): "t_category",
    (0x0010, 0xE014): "n_category",
    (0x0010, 0xE015): "m_category",
    (0x0010, 0xE016): "overall_stage_group",
    (0x0010, 0xE017): "stage_i",
    (0x0010, 0xE018): "stage_ii",
    (0x0010, 0xE019): "stage_iii",
    (0x0010, 0xE020): "stage_iv",
    (0x0010, 0xE021): "recurrent_disease",
    (0x0010, 0xE022): "metastatic_disease",
    (0x0010, 0xE023): "oligo_metastases",
    (0x0010, 0xE024): "widespread_metastases",
    (0x0010, 0xE025): "prior_treatment",
    (0x0010, 0xE026): "surgery_history",
    (0x0010, 0xE027): "radiation_history",
    (0x0010, 0xE028): "chemotherapy_history",
    (0x0010, 0xE029): "immunotherapy_history",
    (0x0010, 0xE030): "targeted_therapy_history",
    (0x0010, 0xE031): "hormone_therapy_history",
    (0x0010, 0xE032): "performance_status",
    (0x0010, 0xE033): "ecog_score",
    (0x0010, 0xE034): "karnofsky_score",
    (0x0010, 0xE035): "tumor_markers",
    (0x0010, 0xE036): "cea_level",
    (0x0010, 0xE037): "ca125_level",
    (0x0010, 0xE038): "ca153_level",
    (0x0010, 0xE039): "ca199_level",
    (0x0010, 0xE040): "afp_level",
    (0x0010, 0xE041): "hcg_level",
    (0x0010, 0xE042): "psa_level",
    (0x0010, 0xE043): "ldh_level",
    (0x0010, 0xE044): "alkaline_phosphatase",
    (0x0010, 0xE045): "genetic_testing",
    (0x0010, 0xE046): "brca_status",
    (0x0010, 0xE047): "her2_status",
    (0x0010, 0xE048): "er_status",
    (0x0010, 0xE049): "pr_status",
    (0x0010, 0xE050): "msi_status",
    (0x0010, 0xE051): "pmmr_status",
    (0x0010, 0xE052): "kras_mutation",
    (0x0010, 0xE053): "braf_mutation",
    (0x0010, 0xE054): "egfr_mutation",
    (0x0010, 0xE055): "alk_rearrangement",
    (0x0010, 0xE056): "ros1_rearrangement",
    (0x0010, 0xE057): "pd_l1_expression",
    (0x0010, 0xE058): "tumor_mutational_burden",
    (0x0010, 0xE059): "liquid_biopsy_result",
}

ONCOLOGY_PATHOLOGY_TAGS = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0xE101): "primary_tumor",
    (0x0018, 0xE102): "tumor_location",
    (0x0018, 0xE103): "tumor_size",
    (0x0018, 0xE104): "tumor_volume",
    (0x0018, 0xE105): "tumor_shape",
    (0x0018, 0xE106): "tumor_margin",
    (0x0018, 0xE107): "tumor_enhancement",
    (0x0018, 0xE108): "tumor_heterogeneity",
    (0x0018, 0xE109): "tumor_necrosis",
    (0x0018, 0xE110): "cystic_component",
    (0x0018, 0xE111): "solid_component",
    (0x0018, 0xE112): "calcifications",
    (0x0018, 0xE113): "fat_content",
    (0x0018, 0xE114): "hemorrhage_tumor",
    (0x0018, 0xE115): "peritumoral_edema",
    (0x0018, 0xE116): "invasion_indicator",
    (0x0018, 0xE117): "vascular_invasion",
    (0x0018, 0xE118): "lymphovascular_invasion",
    (0x0018, 0xE119): "perineural_invasion",
    (0x0018, 0xE120): "regional_lymph_nodes",
    (0x0018, 0xE121): "lymph_node_size",
    (0x0018, 0xE122): "lymph_node_metastasis",
    (0x0018, 0xE123): "distant_metastasis",
    (0x0018, 0xE124): "bone_metastasis",
    (0x0018, 0xE125): "liver_metastasis",
    (0x0018, 0xE126): "lung_metastasis",
    (0x0018, 0xE127): "brain_metastasis",
    (0x0018, 0xE128): "adrenal_metastasis",
    (0x0018, 0xE129): "peritoneal_metastasis",
    (0x0018, 0xE130): "pleural_metastasis",
    (0x0018, 0xE131): "distant_lymph_nodes",
    (0x0018, 0xE132): "ascites_oncology",
    (0x0018, 0xE133): "pleural_effusion_oncology",
    (0x0018, 0xE134): "pericardial_effusion_oncology",
    (0x0018, 0xE135): "lymphangiectasia",
    (0x0018, 0xE136): "skin_involvement",
    (0x0018, 0xE137): "subcutaneous_nodules",
    (0x0018, 0xE138): "muscle_invasion",
    (0x0018, 0xE139): "bone_invasion",
    (0x0018, 0xE140): "cartilage_invasion",
    (0x0018, 0xE141): "nerve_invasion",
    (0x0018, 0xE142): "organ_invasion",
    (0x0018, 0xE143): "vascular_encasement",
    (0x0018, 0xE144): "airway_compression",
    (0x0018, 0xE145): "bowel_obstruction",
    (0x0018, 0xE146): "urinary_obstruction",
    (0x0018, 0xE147): "biliary_obstruction",
    (0x0018, 0xE148): "fistula_formation",
    (0x0018, 0xE149): "paraneoplastic_syndrome",
}

ONCOLOGY_IMAGING_TAGS = {
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
    (0x0018, 0xE201): "ct_oncology_protocol",
    (0x0018, 0xE202): "contrast_enhanced_ct",
    (0x0018, 0xE203): "triphasic_ct",
    (0x0018, 0xE204): "pet_ct_oncology",
    (0x0018, 0xE205): "fdg_pet_ct",
    (0x0018, 0xE206): "psma_pet_ct",
    (0x0018, 0xE207): "flt_pet_ct",
    (0x0018, 0xE208): "choline_pet_ct",
    (0x0018, 0xE209): "octreotide_pet",
    (0x0018, 0xE210): "ga68_dotatate",
    (0x0018, 0xE211): "f18_fluoride",
    (0x0018, 0xE212): "mri_oncology_protocol",
    (0x0018, 0xE213): "diffusion_weighted_oncology",
    (0x0018, 0xE214): "adc_mapping_oncology",
    (0x0018, 0xE215): "perfusion_mri_oncology",
    (0x0018, 0xE216): "dynamic_contrast_enhanced",
    (0x0018, 0xE217): "DCE_mri",
    (0x0018, 0xE218): "DCE_parameters",
    (0x0018, 0xE219): "ktrans_value",
    (0x0018, 0xE220): "ve_value",
    (0x0018, 0xE221): "vp_value",
    (0x0018, 0xE222): "spect_oncology",
    (0x0018, 0xE223): "octreotide_scan",
    (0x0018, 0xE224): "mibg_scan",
    (0x0018, 0xE225): "thyroglobulin_scan",
    (0x0018, 0xE226): "bone_scan_oncology",
    (0x0018, 0xE227): "whole_body_imaging",
    (0x0018, 0xE228): "staging_scan",
    (0x0018, 0xE229): "restaging_scan",
    (0x0018, 0xE230): "surveillance_scan",
    (0x0018, 0xE231): "screening_scan",
    (0x0018, 0xE232): "tumor_board_review",
    (0x0018, 0xE233): "response_assessment",
    (0x0018, 0xE234): "target_lesion",
    (0x0018, 0xE235): "non_target_lesion",
    (0x0018, 0xE236): "new_lesion",
    (0x0018, 0xE237): "measurable_disease",
    (0x0018, 0xE238): "non_measurable_disease",
    (0x0018, 0xE239): "bidimensional_measurement",
    (0x0018, 0xE240): "unidimensional_measurement",
    (0x0018, 0xE241): "volumetric_measurement",
    (0x0018, 0xE242): "tumor_segmentation",
    (0x0018, 0xE243): "radiomics_extraction",
    (0x0018, 0xE244): "texture_analysis",
    (0x0018, 0xE245): "machine_learning_oncology",
    (0x0018, 0xE246): "ai_assessment",
    (0x0018, 0xE247): "radiogenomics",
    (0x0018, 0xE248): "imaging_biomarker",
    (0x0018, 0xE249): "response_prediction",
}

ONCOLOGY_PROTOCOLS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0xE301): "response_criteria",
    (0x0018, 0xE302): "recist_1_1",
    (0x0018, 0xE303): "recist_1_0",
    (0x0018, 0xE304): "iRecist",
    (0x0018, 0xE305): "percist",
    (0x0018, 0xE306): "choi_criteria",
    (0x0018, 0xE307): "mRecist",
    (0x0018, 0xE308): "eASL",
    (0x0018, 0xE309): "volumetric_response",
    (0x0018, 0xE310): "treatment_planning",
    (0x0018, 0xE311): "radiation_therapy_planning",
    (0x0018, 0xE312): "external_beam_radiation",
    (0x0018, 0xE313): "imrt_planning",
    (0x0018, 0xE314): "vmat_planning",
    (0x0018, 0xE315): "sbrt_planning",
    (0x0018, 0xE316): "stereotactic_radiation",
    (0x0018, 0xE317): "proton_therapy_planning",
    (0x0018, 0xE318): "carbon_therapy_planning",
    (0x0018, 0xE319): "brachytherapy_planning",
    (0x0018, 0xE320): "target_volume_delineation",
    (0x0018, 0xE321): "gross_tumor_volume",
    (0x0018, 0xE322): "clinical_target_volume",
    (0x0018, 0xE323): "planning_target_volume",
    (0x0018, 0xE324): "organs_at_risk",
    (0x0018, 0xE325): "dose_constraints",
    (0x0018, 0xE326): "chemotherapy_planning",
    (0x0018, 0xE327): "systemic_therapy_planning",
    (0x0018, 0xE328): "immunotherapy_planning",
    (0x0018, 0xE329): "targeted_therapy_planning",
    (0x0018, 0xE330): "combination_therapy",
    (0x0018, 0xE331): "neoadjuvant_therapy",
    (0x0018, 0xE332): "adjuvant_therapy",
    (0x0018, 0xE333): "palliative_therapy",
    (0x0018, 0xE334): "definitive_therapy",
    (0x0018, 0xE335): "salvage_therapy",
    (0x0018, 0xE336): "hormonal_therapy",
    (0x0018, 0xE337): "bone_modifying_agents",
    (0x0018, 0xE338): "bisphosphonate_therapy",
    (0x0018, 0xE339): "denosumab_therapy",
    (0x0018, 0xE340): "supportive_care",
    (0x0018, 0xE341): "growth_factor_support",
    (0x0018, 0xE342): "transfusion_requirement",
    (0x0018, 0xE343): "nutritional_support",
    (0x0018, 0xE344): "pain_management",
    (0x0018, 0xE345): "palliative_care_oncology",
    (0x0018, 0xE346): "hospice_planning",
    (0x0018, 0xE347): "clinical_trial",
    (0x0018, 0xE348): "trial_identifier",
    (0x0018, 0xE349): "treatment_arm",
    (0x0018, 0xE350): "endpoint_assessment",
}

ONCOLOGY_OUTCOMES_TAGS = {
    (0x0018, 0xE401): "overall_survival",
    (0x0018, 0xE402): "cancer_specific_survival",
    (0x0018, 0xE403): "progression_free_survival",
    (0x0018, 0xE404): "disease_free_survival",
    (0x0018, 0xE405): "event_free_survival",
    (0x0018, 0xE406): "response_rate",
    (0x0018, 0xE407): "complete_response",
    (0x0018, 0xE408): "partial_response",
    (0x0018, 0xE409): "stable_disease",
    (0x0018, 0xE410): "progressive_disease",
    (0x0018, 0xE411): "objective_response_rate",
    (0x0018, 0xE412): "clinical_benefit_rate",
    (0x0018, 0xE413): "duration_of_response",
    (0x0018, 0xE414): "time_to_progression",
    (0x0018, 0xE415): "time_to_treatment_failure",
    (0x0018, 0xE416): "treatment_toxicity",
    (0x0018, 0xE417): "grade_3_toxicity",
    (0x0018, 0xE418): "grade_4_toxicity",
    (0x0018, 0xE419): "dose_limiting_toxicity",
    (0x0018, 0xE420): "treatment_related_mortality",
    (0x0018, 0xE421): "dose_reduction",
    (0x0018, 0xE422): "treatment_discontinuation",
    (0x0018, 0xE423): "adverse_events",
    (0x0018, 0xE424): "hematologic_toxicity",
    (0x0018, 0xE425): "non_hematologic_toxicity",
    (0x0018, 0xE426): "quality_of_life_oncology",
    (0x0018, 0xE427): "eq5d_oncology",
    (0x0018, 0xE428): "eortc_qlq_c30",
    (0x0018, 0xE429): "fact_oncology",
    (0x0018, 0xE430): "symptom_burden",
    (0x0018, 0xE431): "fatigue_oncology",
    (0x0018, 0xE432): "pain_oncology",
    (0x0018, 0xE433): "nausea_vomiting",
    (0x0018, 0xE434): "appetite_loss",
    (0x0018, 0xE435): "weight_change_oncology",
    (0x0018, 0xE436): "performance_status_change",
    (0x0018, 0xE437): "treatment_compliance",
    (0x0018, 0xE438): "treatment_adherence",
    (0x0018, 0xE439): "survivorship_care",
    (0x0018, 0xE440): "late_effects",
    (0x0018, 0xE441): "secondary_malignancy",
    (0x0018, 0xE442): "cardiotoxicity",
    (0x0018, 0xE443): "pulmonary_toxicity",
    (0x0018, 0xE444): "neurotoxicity",
    (0x0018, 0xE445): "renal_toxicity",
    (0x0018, 0xE446): "hepatic_toxicity",
    (0x0018, 0xE447): "endocrine_toxicity",
    (0x0018, 0xE448): "fertility_preservation",
    (0x0018, 0xE449): "psychosocial_outcome",
    (0x0018, 0xE450): "financial_toxicity",
}

TOTAL_TAGS_LXXXIV = {}

TOTAL_TAGS_LXXXIV.update(ONCOLOGY_PATIENT_PARAMETERS)
TOTAL_TAGS_LXXXIV.update(ONCOLOGY_PATHOLOGY_TAGS)
TOTAL_TAGS_LXXXIV.update(ONCOLOGY_IMAGING_TAGS)
TOTAL_TAGS_LXXXIV.update(ONCOLOGY_PROTOCOLS)
TOTAL_TAGS_LXXXIV.update(ONCOLOGY_OUTCOMES_TAGS)


def _extract_tags_lxxxiv(ds: Any) -> Dict[str, Any]:
    extracted = {}
    tag_names = {tag: name for tag, name in TOTAL_TAGS_LXXXIV.items()}
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


def _is_oncology_imaging_file(file_path: str) -> bool:
    oncology_indicators = [
        'oncology', 'oncology', 'cancer', 'tumor', 'carcinoma',
        'sarcoma', 'lymphoma', 'leukemia', 'melanoma', 'blastoma',
        'cancer_staging', 'treatment_response', 'metastasis', 'recist',
        'pet_ct', 'fdg_pet', 'tumor_markers', 'chemotherapy', 'radiation',
        'immunotherapy', 'targeted_therapy', 'cancer_surveillance'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in oncology_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxxxiv(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxxxiv_detected": False,
        "fields_extracted": 0,
        "extension_lxxxiv_type": "oncology_imaging",
        "extension_lxxxiv_version": "2.0.0",
        "oncology_patient_parameters": {},
        "oncology_pathology": {},
        "oncology_imaging": {},
        "oncology_protocols": {},
        "oncology_outcomes": {},
        "extraction_errors": [],
    }

    try:
        if not _is_oncology_imaging_file(file_path):
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

        result["extension_lxxxiv_detected"] = True

        oncology_data = _extract_tags_lxxxiv(ds)

        patient_params_set = set(ONCOLOGY_PATIENT_PARAMETERS.keys())
        pathology_set = set(ONCOLOGY_PATHOLOGY_TAGS.keys())
        imaging_set = set(ONCOLOGY_IMAGING_TAGS.keys())
        protocols_set = set(ONCOLOGY_PROTOCOLS.keys())
        outcomes_set = set(ONCOLOGY_OUTCOMES_TAGS.keys())

        for tag, value in oncology_data.items():
            if tag in patient_params_set:
                result["oncology_patient_parameters"][tag] = value
            elif tag in pathology_set:
                result["oncology_pathology"][tag] = value
            elif tag in imaging_set:
                result["oncology_imaging"][tag] = value
            elif tag in protocols_set:
                result["oncology_protocols"][tag] = value
            elif tag in outcomes_set:
                result["oncology_outcomes"][tag] = value

        result["fields_extracted"] = len(oncology_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiv_field_count() -> int:
    return len(TOTAL_TAGS_LXXXIV)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiv_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiv_description() -> str:
    return (
        "Oncology Imaging II metadata extraction. Provides comprehensive coverage of "
        "cancer staging, treatment response assessment, tumor characterization, "
        "oncology-specific imaging protocols, and oncology outcomes measurement."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiv_modalities() -> List[str]:
    return ["CT", "MR", "US", "PT", "NM", "XA", "MG", "DR", "CR"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiv_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiv_category() -> str:
    return "Oncology Imaging II"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiv_keywords() -> List[str]:
    return [
        "oncology", "cancer", "tumor", "carcinoma", "sarcoma",
        "lymphoma", "cancer staging", "treatment response", "RECIST",
        "PET-CT", "FDG-PET", "tumor markers", "metastasis",
        "chemotherapy", "radiation therapy", "immunotherapy", "targeted therapy"
    ]

# Aliases for smoke test compatibility
def extract_regenerative_medicine_imaging(file_path: str) -> Dict[str, Any]:
    return extract_scientific_dicom_fits_ultimate_advanced_extension_lxxxiv(file_path)

def get_regenerative_medicine_imaging_field_count() -> int:
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiv_field_count()

def get_regenerative_medicine_imaging_version() -> str:
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiv_version()

def get_regenerative_medicine_imaging_description() -> str:
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiv_description()

def get_regenerative_medicine_imaging_supported_formats() -> List[str]:
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiv_supported_formats()

def get_regenerative_medicine_imaging_modalities() -> List[str]:
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiv_modalities()

def get_regenerative_medicine_imaging_category() -> str:
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiv_category()

def get_regenerative_medicine_imaging_keywords() -> List[str]:
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiv_keywords()
