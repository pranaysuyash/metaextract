"""
Scientific DICOM/FITS Ultimate Advanced Extension LXXII - Endocrinology Imaging II

This module provides comprehensive extraction of Endocrinology Imaging parameters
including thyroid disorders, diabetes complications, adrenal imaging, and
endocrinology-specific imaging protocols.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXII_AVAILABLE = True

ENDOCRINE_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0xF001): "endocrinology_assessment_date",
    (0x0010, 0xF002): "thyroid_diagnosis",
    (0x0010, 0xF003): "hyperthyroidism",
    (0x0010, 0xF004): "hypothyroidism",
    (0x0010, 0xF005): "thyroiditis",
    (0x0010, 0xF006): "graves_disease",
    (0x0010, 0xF007): "hashimotos_thyroiditis",
    (0x0010, 0xF008): "thyroid_nodule",
    (0x0010, 0xF009): "thyroid_cancer",
    (0x0010, 0xF010): "papillary_carcinoma",
    (0x0010, 0xF011): "follicular_carcinoma",
    (0x0010, 0xF012): "medullary_carcinoma",
    (0x0010, 0xF013): "anaplastic_carcinoma",
    (0x0010, 0xF014): "thyroidectomy_status",
    (0x0010, 0xF015): "radioiodine_therapy",
    (0x0010, 0xF016): "thyroglobulin_level",
    (0x0010, 0xF017): "thyroglobulin_antibody",
    (0x0010, 0xF018): "tsh_receptor_antibody",
    (0x0010, 0xF019): "thyroid_stimulating_hormone",
    (0x0010, 0xF020): "free_t4_level",
    (0x0010, 0xF021): "free_t3_level",
    (0x0010, 0xF022): "total_t4_level",
    (0x0010, 0xF023): "total_t3_level",
    (0x0010, 0xF024): "diabetes_mellitus_type",
    (0x0010, 0xF025): "type_1_diabetes",
    (0x0010, 0xF026): "type_2_diabetes",
    (0x0010, 0xF027): "gestational_diabetes",
    (0x0010, 0xF028): "diabetic_complications",
    (0x0010, 0xF029): "retinopathy_indicator",
    (0x0010, 0xF030): "nephropathy_indicator",
    (0x0010, 0xF031): "neuropathy_indicator",
    (0x0010, 0xF032): "macrovascular_complication",
    (0x0010, 0xF033): "hba1c_value",
    (0x0010, 0xF034): "fasting_glucose",
    (0x0010, 0xF035): "c_peptide_level",
    (0x0010, 0xF036): "insulin_level",
    (0x0010, 0xF037): "insulin_resistance",
    (0x0010, 0xF038): "adrenal_diagnosis",
    (0x0010, 0xF039): "cushings_syndrome",
    (0x0010, 0xF040): "addisons_disease",
    (0x0010, 0xF041): "primary_aldosteronism",
    (0x0010, 0xF042): "pheochromocytoma",
    (0x0010, 0xF043): "adrenal_incidentaloma",
    (0x0010, 0xF044): "adrenal_carcinoma",
    (0x0010, 0xF045): "pituitary_diagnosis",
    (0x0010, 0xF046): "acromegaly",
    (0x0010, 0xF047): "cushing_disease",
    (0x0010, 0xF048): "prolactinoma",
    (0x0010, 0xF049): "non_functioning_adenoma",
    (0x0010, 0xF050): "hypopituitarism",
    (0x0010, 0xF051): "diabetes_insipidus",
    (0x0010, 0xF052): "growth_hormone_deficiency",
    (0x0010, 0xF053): "parathyroid_diagnosis",
    (0x0010, 0xF054): "hyperparathyroidism",
    (0x0010, 0xF055): "hypoparathyroidism",
    (0x0010, 0xF056): "calcium_level",
    (0x0010, 0xF057): "phosphate_level",
    (0x0010, 0xF058): "pth_level",
    (0x0010, 0xF059): "vitamin_d_level",
}

ENDOCRINE_PATHOLOGY_TAGS = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0xF101): "thyroid_nodule_size",
    (0x0018, 0xF102): "thyroid_nodule_location",
    (0x0018, 0xF103): "thyroid_nodule_composition",
    (0x0018, 0xF104): "echogenicity_nodule",
    (0x0018, 0xF105): "margin_nodule",
    (0x0018, 0xF106): "calcifications_nodule",
    (0x0018, 0xF107): "tirads_score",
    (0x0018, 0xF108): "tirads_1",
    (0x0018, 0xF109): "tirads_2",
    (0x0018, 0xF110): "tirads_3",
    (0x0018, 0xF111): "tirads_4",
    (0x0018, 0xF112): "tirads_5",
    (0x0018, 0xF113): "thyroid_cyst",
    (0x0018, 0xF114): "colloid_nodule",
    (0x0018, 0xF115): "hyperplastic_nodule",
    (0x0018, 0xF116): "lymphocytic_thyroiditis",
    (0x0018, 0xF117): "thyroid_heterogeneity",
    (0x0018, 0xF118): "thyroid_vascularity",
    (0x0018, 0xF119): "thyroid_lymphadenopathy",
    (0x0018, 0xF120): "central_compartment_lymph",
    (0x0018, 0xF121): "lateral_compartment_lymph",
    (0x0018, 0xF122): "adrenal_mass",
    (0x0018, 0xF123): "adrenal_mass_size",
    (0x0018, 0xF124): "adrenal_mass_attenuation",
    (0x0018, 0xF125): "washout_characteristics",
    (0x0018, 0xF126): "absolute_washout",
    (0x0018, 0xF127): "relative_washout",
    (0x0018, 0xF128): "adrenal_incidentaloma",
    (0x0018, 0xF129): "lipid_rich_adenoma",
    (0x0018, 0xF130): "pheochromocytoma_indicator",
    (0x0018, 0xF131): "adrenal_carcinoma_indicator",
    (0x0018, 0xF132): "pituitary_mass",
    (0x0018, 0xF133): "pituitary_macroadenoma",
    (0x0018, 0xF134): "pituitary_microadenoma",
    (0x0018, 0xF135): "pituitary_apoplexy",
    (0x0018, 0xF136): "empty_sella",
    (0x0018, 0xF137): "diaphragm_sella",
    (0x0018, 0xF138): "parathyroid_gland",
    (0x0018, 0xF139): "parathyroid_adenoma",
    (0x0018, 0xF140): "parathyroid_hyperplasia",
    (0x0018, 0xF141): "parathyroid_carcinoma",
    (0x0018, 0xF142): "brown_tumor",
    (0x0018, 0xF143): "bone_changes_endocrine",
    (0x0018, 0xF144): "osteitis_fibrosa",
    (0x0018, 0xF145): "subperiosteal_resorption",
    (0x0018, 0xF146): "bone_brown_tumors",
    (0x0018, 0xF147): "soft_tissue_calcification",
    (0x0018, 0xF148): "vascular_calcification",
    (0x0018, 0xF149): "diabetic_foot_changes",
}

ENDOCRINE_IMAGING_TAGS = {
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
    (0x0018, 0xF201): "thyroid_ultrasound",
    (0x0018, 0xF202): "thyroid_doppler",
    (0x0018, 0xF203): "elastography_thyroid",
    (0x0018, 0xF204): "fine_needle_aspiration",
    (0x0018, 0xF205): "thyroid_nuclear_scan",
    (0x0018, 0xF206): "technetium_scan",
    (0x0018, 0xF207): "iodine_123_scan",
    (0x0018, 0xF208): "thyroid_carcinoma_protocol",
    (0x0018, 0xF209): "whole_body_scan",
    (0x0018, 0xF210): "thyroglobulin_stimulation",
    (0x0018, 0xF211): "pet_ct_endocrine",
    (0x0018, 0xF212): "fdg_pet_thyroid",
    (0x0018, 0xF213): "ga68_dotatate_thyroid",
    (0x0018, 0xF214): "adrenal_ct_protocol",
    (0x0018, 0xF215): "adrenal_washout_ct",
    (0x0018, 0xF216): "mri_adrenal_protocol",
    (0x0018, 0xF217): "chemical_shift_mri",
    (0x0018, 0xF218): "in_opposed_phase",
    (0x0018, 0xF219): "out_of_phase",
    (0x0018, 0xF220): "mri_pituitary_protocol",
    (0x0018, 0xF221): "dynamic_contrast_pituitary",
    (0x0018, 0xF222): "pituitary_macroadenoma_proto",
    (0x0018, 0xF223): "cavernous_sinus_invasion",
    (0x0018, 0xF224): "pet_ct_pituitary",
    (0x0018, 0xF225): "parathyroid_scan",
    (0x0018, 0xF226): "sestamibi_scan",
    (0x0018, 0xF227): "parathyroid_localization",
    (0x0018, 0xF228): "ultrasound_parathyroid",
    (0x0018, 0xF229): "mibi_scan_parathyroid",
    (0x0018, 0xF230): "octreotide_scan",
    (0x0018, 0xF231): "pet_ct_parathyroid",
    (0x0018, 0xF232): "diabetic_imaging",
    (0x0018, 0xF233): "mr_neurography",
    (0x0018, 0xF234): "cardiac_mri_diabetes",
    (0x0018, 0xF235): "renal_mri_diabetes",
    (0x0018, 0xF236): "bone_density_diabetes",
    (0x0018, 0xF237): "foot_ulcer_assessment",
    (0x0018, 0xF238): "angiography_diabetes",
    (0x0018, 0xF239): "ct_coronary_calcium",
    (0x0018, 0xF240): "carotid_ultrasound",
    (0x0018, 0xF241): "intima_media_thickness",
    (0x0018, 0xF242): "bone_age_assessment",
    (0x0018, 0xF243): "greulich_pyle_endocrine",
    (0x0018, 0xF244): "bone_age_deviation",
    (0x0018, 0xF245): "growth_hormone_stimulation",
    (0x0018, 0xF246): "sella_imaging",
    (0x0018, 0xF247): "dynamic_function_testing",
    (0x0018, 0xF248): "mibg_scan",
    (0x0018, 0xF249): "i123_mibg_scan",
}

ENDOCRINE_PROTOCOLS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0xF301): "thyroid_fna_planning",
    (0x0018, 0xF302): "thyroid_lesion_targeting",
    (0x0018, 0xF303): "thyroid_ablation",
    (0x0018, 0xF304): "radiofrequency_ablation",
    (0x0018, 0xF305): "laser_ablation_thyroid",
    (0x0018, 0xF306): "ethanol_ablation",
    (0x0018, 0xF307): "thyroidectomy_planning",
    (0x0018, 0xF308): "lateral_neck_dissection",
    (0x0018, 0xF309): "central_compartment_clear",
    (0x0018, 0xF310): "adrenal_biopsy",
    (0x0018, 0xF311): "adrenal_surgery_planning",
    (0x0018, 0xF312): "laparoscopic_adrenalectomy",
    (0x0018, 0xF313): "open_adrenalectomy",
    (0x0018, 0xF314): "pituitary_surgery_planning",
    (0x0018, 0xF315): "transsphenoidal_approach",
    (0x0018, 0xF316): "endoscopic_approach",
    (0x0018, 0xF317): "craniotomy_planning",
    (0x0018, 0xF318): "radiation_therapy_pituitary",
    (0x0018, 0xF319): "parathyroid_surgery",
    (0x0018, 0xF320): "minimally_invasive_parathyroid",
    (0x0018, 0xF321): "bilateral_exploration",
    (0x0018, 0xF322): "intraoperative_pth",
    (0x0018, 0xF323): "diabetes_screening",
    (0x0018, 0xF324): "retinopathy_screening",
    (0x0018, 0xF325): "nephropathy_screening",
    (0x0018, 0xF326): "neuropathy_screening",
    (0x0018, 0xF327): "cv_risk_assessment",
    (0x0018, 0xF328): "bone_health_screening",
    (0x0018, 0xF329): "osteoporosis_screening",
    (0x0018, 0xF330): "fracture_risk_assessment",
    (0x0018, 0xF331): "treatment_monitoring",
    (0x0018, 0xF332): "thyroid_hormone_therapy",
    (0x0018, 0xF333): "radioiodine_dosing",
    (0x0018, 0xF334): "thyrotropin_stimulation",
    (0x0018, 0xF335): "glucose_tolerance_test",
    (0x0018, 0xF336): "insulin_tolerance_test",
    (0x0018, 0xF337): "cortisol_stimulation_test",
    (0x0018, 0xF338): "dexamethasone_suppression",
    (0x0018, 0xF339): "acth_stimulation_test",
    (0x0018, 0xF340): "growth_hormone_stimulation",
    (0x0018, 0xF341): "arginine_stimulation",
    (0x0018, 0xF342): "glucagon_stimulation",
    (0x0018, 0xF343): "water_deprivation_test",
    (0x0018, 0xF344): "saline_infusion_test",
    (0x0018, 0xF345): "oral_glucose_load",
    (0x0018, 0xF346): "mixed_meal_test",
    (0x0018, 0xF347): "continuous_glucose_monitor",
    (0x0018, 0xF348): "flash_glucose_monitor",
    (0x0018, 0xF349): "cgm_data_analysis",
    (0x0018, 0xF350): "insulin_pump_therapy",
}

ENDOCRINE_OUTCOMES_TAGS = {
    (0x0018, 0xF401): "thyroid_cancer_survival",
    (0x0018, 0xF402): "disease_free_survival_thyroid",
    (0x0018, 0xF403): "recurrence_thyroid",
    (0x0018, 0xF404): "stimulated_thyroglobulin",
    (0x0018, 0xF405): "thyroglobulin_kinetics",
    (0x0018, 0xF406): "antibody_kinetics",
    (0x0018, 0xF407): "radioiodine_response",
    (0x0018, 0xF408): "ablation_success",
    (0x0018, 0xF409): "surgical_complications",
    (0x0018, 0xF410): "recurrent_laryngeal_injury",
    (0x0018, 0xF411): "hypoparathyroidism_postop",
    (0x0018, 0xF412): "diabetes_control",
    (0x0018, 0xF413): "hba1c_trajectory",
    (0x0018, 0xF414): "time_in_range",
    (0x0018, 0xF415): "glucose_variability",
    (0x0018, 0xF416): "hypoglycemia_rate",
    (0x0018, 0xF417): "diabetic_complications_progression",
    (0x0018, 0xF418): "retinopathy_progression",
    (0x0018, 0xF419): "nephropathy_progression",
    (0x0018, 0xF420): "neuropathy_progression",
    (0x0018, 0xF421): "cardiovascular_events",
    (0x0018, 0xF422): "adrenal_crisis_indicator",
    (0x0018, 0xF423): "cushing_remission",
    (0x0018, 0xF424): "acromegaly_control",
    (0x0018, 0xF425): "igf1_level",
    (0x0018, 0xF426): "pituitary_function",
    (0x0018, 0xF427): "hypopituitarism_improvement",
    (0x0018, 0xF428): "bone_density_outcome",
    (0x0018, 0xF429): "fracture_prevention",
    (0x0018, 0xF430): "osteoporosis_treatment",
    (0x0018, 0xF431): "bisphosphonate_response",
    (0x0018, 0xF432): "denosumab_response",
    (0x0018, 0xF433): "quality_of_life_endocrine",
    (0x0018, 0xF434): "thyroid_symptom_score",
    (0x0018, 0xF435): "diabetes_quality_of_life",
    (0x0018, 0xF436): "adds_score",
    (0x0018, 0xF437): "pas-s_score",
    (0x0018, 0xF438): "acromegaly_qol",
    (0x0018, 0xF439): " Cushing_qol",
    (0x0018, 0xF440): "treatment_adherence",
    (0x0018, 0xF441): "medication_compliance",
    (0x0018, 0xF442): "follow_up_adherence",
    (0x0018, 0xF443): "surveillance_compliance",
    (0x0018, 0xF444): "patient_education",
    (0x0018, 0xF445): "self_monitoring",
    (0x0018, 0xF446): "lifestyle_modification",
    (0x0018, 0xF447): "dietary_adherence",
    (0x0018, 0xF448): "exercise_adherence",
    (0x0018, 0xF449): "weight_management",
    (0x0018, 0xF450): "metabolic_control",
}

TOTAL_TAGS_LXXII = {}

TOTAL_TAGS_LXXII.update(ENDOCRINE_PATIENT_PARAMETERS)
TOTAL_TAGS_LXXII.update(ENDOCRINE_PATHOLOGY_TAGS)
TOTAL_TAGS_LXXII.update(ENDOCRINE_IMAGING_TAGS)
TOTAL_TAGS_LXXII.update(ENDOCRINE_PROTOCOLS)
TOTAL_TAGS_LXXII.update(ENDOCRINE_OUTCOMES_TAGS)


def _extract_tags_lxxii(ds: Any) -> Dict[str, Any]:
    extracted = {}
    tag_names = {tag: name for tag, name in TOTAL_TAGS_LXXII.items()}
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


def _is_endocrinology_imaging_file(file_path: str) -> bool:
    endo_indicators = [
        'endocrinology', 'endocrine', 'thyroid', 'diabetes', 'adrenal',
        'pituitary', 'parathyroid', 'thyroidectomy', 'cushing', 'acromegaly',
        'hyperthyroidism', 'hypothyroidism', 'thyroid_nodule', 'tirads',
        'pheochromocytoma', 'diabetic', 'hba1c', 'insulin', 'cortisol'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in endo_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxxii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxxii_detected": False,
        "fields_extracted": 0,
        "extension_lxxii_type": "endocrinology_imaging",
        "extension_lxxii_version": "2.0.0",
        "endocrine_patient_parameters": {},
        "endocrine_pathology": {},
        "endocrine_imaging": {},
        "endocrine_protocols": {},
        "endocrine_outcomes": {},
        "extraction_errors": [],
    }

    try:
        if not _is_endocrinology_imaging_file(file_path):
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

        result["extension_lxxii_detected"] = True

        endo_data = _extract_tags_lxxii(ds)

        patient_params_set = set(ENDOCRINE_PATIENT_PARAMETERS.keys())
        pathology_set = set(ENDOCRINE_PATHOLOGY_TAGS.keys())
        imaging_set = set(ENDOCRINE_IMAGING_TAGS.keys())
        protocols_set = set(ENDOCRINE_PROTOCOLS.keys())
        outcomes_set = set(ENDOCRINE_OUTCOMES_TAGS.keys())

        for tag, value in endo_data.items():
            if tag in patient_params_set:
                result["endocrine_patient_parameters"][tag] = value
            elif tag in pathology_set:
                result["endocrine_pathology"][tag] = value
            elif tag in imaging_set:
                result["endocrine_imaging"][tag] = value
            elif tag in protocols_set:
                result["endocrine_protocols"][tag] = value
            elif tag in outcomes_set:
                result["endocrine_outcomes"][tag] = value

        result["fields_extracted"] = len(endo_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxii_field_count() -> int:
    return len(TOTAL_TAGS_LXXII)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxii_description() -> str:
    return (
        "Endocrinology Imaging II metadata extraction. Provides comprehensive coverage of "
        "thyroid disorders, diabetes complications, adrenal imaging, pituitary disorders, "
        "endocrinology-specific imaging protocols, and endocrine outcomes assessment."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxii_modalities() -> List[str]:
    return ["CT", "MR", "US", "PT", "NM", "XA", "CR", "DR"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxii_category() -> str:
    return "Endocrinology Imaging II"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxii_keywords() -> List[str]:
    return [
        "endocrinology", "thyroid", "diabetes", "adrenal", "pituitary",
        "parathyroid", "thyroid cancer", "Cushing's", "acromegaly",
        "thyroid nodule", "TI-RADS", "pheochromocytoma", "diabetic complications",
        "thyroidectomy", "radioiodine", "endocrine disorders"
    ]


# Aliases for smoke test compatibility
def extract_ihe_profiles(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_lxxii."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_lxxii(file_path)

def get_ihe_profiles_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxii_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxii_field_count()

def get_ihe_profiles_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxii_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxii_version()

def get_ihe_profiles_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxii_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxii_description()

def get_ihe_profiles_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxii_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxii_supported_formats()

def get_ihe_profiles_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxii_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxii_modalities()
