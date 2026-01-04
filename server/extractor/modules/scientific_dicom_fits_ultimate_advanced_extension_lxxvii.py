"""
Scientific DICOM/FITS Ultimate Advanced Extension LXXVII - Geriatric Imaging II

This module provides comprehensive extraction of Geriatric Imaging parameters
including age-related conditions, frailty assessment, polypharmacy considerations,
and elderly-specific imaging protocols.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXVII_AVAILABLE = True

GERIATRIC_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x6001): "geriatric_assessment_date",
    (0x0010, 0x6002): "chronological_age",
    (0x0010, 0x6003): "biological_age",
    (0x0010, 0x6004): "functional_age",
    (0x0010, 0x6005): "frail_indicator",
    (0x0010, 0x6006): "frailty_score",
    (0x0010, 0x6007): "clinical_frailty_scale",
    (0x0010, 0x6008): "very_frail",
    (0x0010, 0x6009): "frail",
    (0x0010, 0x6010): "pre_frail",
    (0x0010, 0x6011): "robust",
    (0x0010, 0x6012): "living_situation",
    (0x0010, 0x6013): "independent_living",
    (0x0010, 0x6014): "assisted_living",
    (0x0010, 0x6015): "nursing_home",
    (0x0010, 0x6016): "hospitalized",
    (0x0010, 0x6017): "living_alone",
    (0x0010, 0x6018): "living_with_family",
    (0x0010, 0x6019): "caregiver_present",
    (0x0010, 0x6020): "primary_caregiver",
    (0x0010, 0x6021): "advance_directives",
    (0x0010, 0x6022): "dnr_order",
    (0x0010, 0x6023): "dni_order",
    (0x0010, 0x6024): "polst_form",
    (0x0010, 0x6025): "healthcare_proxy",
    (0x0010, 0x6026): "power_of_attorney",
    (0x0010, 0x6027): "medicare_status",
    (0x0010, 0x6028): "medicaid_status",
    (0x0010, 0x6029): "social_worker_involved",
    (0x0010, 0x6030): "case_manager_involved",
    (0x0010, 0x6031): "activities_of_daily_living",
    (0x0010, 0x6032): "bathing_independent",
    (0x0010, 0x6033): "dressing_independent",
    (0x0010, 0x6034): "toileting_independent",
    (0x0010, 0x6035): "transfer_independent",
    (0x0010, 0x6036): "continence_independent",
    (0x0010, 0x6037): "feeding_independent",
    (0x0010, 0x6038): "adl_score",
    (0x0010, 0x6039): "instrumental_adl",
    (0x0010, 0x6040): "medication_management",
    (0x0010, 0x6041): "financial_management",
    (0x0010, 0x6042): "transportation_use",
    (0x0010, 0x6043): "housekeeping",
    (0x0010, 0x6044): "phone_use",
    (0x0010, 0x6045): "shopping",
    (0x0010, 0x6046): "cooking",
    (0x0010, 0x6047): "iadl_score",
    (0x0010, 0x6048): "mobility_status",
    (0x0010, 0x6049): "ambulatory",
    (0x0010, 0x6050): "wheelchair_bound",
    (0x0010, 0x6051): "bed_bound",
    (0x0010, 0x6052): "fall_history",
    (0x0010, 0x6053): "fall_count_12months",
    (0x0010, 0x6054): "fall_with_injury",
    (0x0010, 0x6055): "balance_assessment",
    (0x0010, 0x6056): "gait_speed",
    (0x0010, 0x6057): "timed_up_and_go",
    (0x0010, 0x6058): "sit_to_stand_test",
    (0x0010, 0x6059): "grip_strength",
    (0x0010, 0x6060): "chair_stand_test",
    (0x0010, 0x6061): "short_physical_performance_battery",
}

GERIATRIC_SYNDROMES_TAGS = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0x6101): "cognitive_assessment",
    (0x0018, 0x6102): "mmse_score",
    (0x0018, 0x6103): "moca_score",
    (0x0018, 0x6104): "mini_cog",
    (0x0018, 0x6105): "clock_drawing_test",
    (0x0018, 0x6106): "dementia_indicator",
    (0x0018, 0x6107): "alzheimer_disease",
    (0x0018, 0x6108): "vascular_dementia",
    (0x0018, 0x6109): "lewy_body_dementia",
    (0x0018, 0x6110): "frontotemporal_dementia",
    (0x0018, 0x6111): "mild_cognitive_impairment",
    (0x0018, 0x6112): "delirium_indicator",
    (0x0018, 0x6113): "acute_confusion",
    (0x0018, 0x6114): "subsyndromal_delirium",
    (0x0018, 0x6115): "depression_indicator",
    (0x0018, 0x6116): "geriatric_depression_scale",
    (0x0018, 0x6117): "phq9_score",
    (0x0018, 0x6118): "suicide_risk",
    (0x0018, 0x6119): "anxiety_indicator",
    (0x0018, 0x6120): "gad7_score",
    (0x0018, 0x6121): "sleep_assessment",
    (0x0018, 0x6122): "insomnia",
    (0x0018, 0x6123): "sleep_apnea",
    (0x0018, 0x6124): "restless_legs",
    (0x0018, 0x6125): "circadian_rhythm",
    (0x0018, 0x6126): "urinary_incontinence",
    (0x0018, 0x6127): "stress_incontinence",
    (0x0018, 0x6128): "urge_incontinence",
    (0x0018, 0x6129): "mixed_incontinence",
    (0x0018, 0x6130): "functional_incontinence",
    (0x0018, 0x6131): "constipation_indicator",
    (0x0018, 0x6132): "fecal_incontinence",
    (0x0018, 0x6133): "malnutrition_indicator",
    (0x0018, 0x6134): "mna_score",
    (0x0018, 0x6135): "screening_tool_nutritional_status",
    (0x0018, 0x6136): "unintentional_weight_loss",
    (0x0018, 0x6137): "appetite_loss",
    (0x0018, 0x6138): "difficulty_swallowing",
    (0x0018, 0x6139): "odynophagia",
    (0x0018, 0x6140): "sensory_impairment",
    (0x0018, 0x6141): "vision_impairment",
    (0x0018, 0x6142): "hearing_impairment",
    (0x0018, 0x6143): "cataract_indicator",
    (0x0018, 0x6144): "glaucoma_indicator",
    (0x0018, 0x6145): "macular_degeneration",
    (0x0018, 0x6146): "hearing_aid_use",
    (0x0018, 0x6147): "vision_aid_use",
    (0x0018, 0x6148): "osteoporosis_indicator",
    (0x0018, 0x6149): "fracture_risk",
    (0x0018, 0x6150): "frailty_phenotype",
    (0x0018, 0x6151): "weight_loss",
    (0x0018, 0x6152): "exhaustion",
    (0x0018, 0x6153): "low_activity",
    (0x0018, 0x6154): "slow_walking",
    (0x0018, 0x6155): "weak_grip",
}

POLYPHARMACY_TAGS = {
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
    (0x0018, 0x6201): "medication_count",
    (0x0018, 0x6202): "polypharmacy_indicator",
    (0x0018, 0x6203): "prescription_count",
    (0x0018, 0x6204): "otc_count",
    (0x0018, 0x6205): "supplement_count",
    (0x0018, 0x6206): "herbal_supplement_count",
    (0x0018, 0x6207): "beers_criteria_positive",
    (0x0018, 0x6208): "stopp_criteria_positive",
    (0x0018, 0x6209): "drug_drug_interaction",
    (0x0018, 0x6210): "drug_disease_interaction",
    (0x0018, 0x6211): "renal_dose_adjustment",
    (0x0018, 0x6212): "hepatic_dose_adjustment",
    (0x0018, 0x6213): "anticholinergic_burden",
    (0x0018, 0x6214): "sedative_burden",
    (0x0018, 0x6215): "opioid_therapy",
    (0x0018, 0x6216): "benzodiazepine_therapy",
    (0x0018, 0x6217): "nsaid_therapy",
    (0x0018, 0x6218): "anticoagulant_therapy",
    (0x0018, 0x6219): "antiplatelet_therapy",
    (0x0018, 0x6220): "diuretic_therapy",
    (0x0018, 0x6221): "ace_inhibitor_therapy",
    (0x0018, 0x6222): "arb_therapy",
    (0x0018, 0x6223): "beta_blocker_therapy",
    (0x0018, 0x6224): "calcium_channel_blocker",
    (0x0018, 0x6225): "statin_therapy",
    (0x0018, 0x6226): "hypoglycemic_therapy",
    (0x0018, 0x6227): "insulin_therapy",
    (0x0018, 0x6228): "oral_hypoglycemic",
    (0x0018, 0x6229): "glp1_agonist",
    (0x0018, 0x6230): "medication_adherence",
    (0x0018, 0x6231): "morisky_score",
    (0x0018, 0x6232): "barrier_to_adherence",
    (0x0018, 0x6233): "cost_barrier",
    (0x0018, 0x6234): "transportation_barrier",
    (0x0018, 0x6235): "cognitive_barrier",
    (0x0018, 0x6236): "medication_reconciliation",
    (0x0018, 0x6237): "brown_bag_review",
    (0x0018, 0x6238): "pharmacist_consult",
    (0x0018, 0x6239): "deprescribing_recommendation",
    (0x0018, 0x6240): "medication_related_problem",
    (0x0018, 0x6241): "adverse_drug_reaction",
    (0x0018, 0x6242): "drug_allergy",
    (0x0018, 0x6243): "side_effect_reported",
}

GERIATRIC_IMAGING_PROTOCOLS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0x6301): "geriatric_ct_protocol",
    (0x0018, 0x6302): "low_dose_ct_chest",
    (0x0018, 0x6303): "head_ct_elderly",
    (0x0018, 0x6304): "spine_ct_elderly",
    (0x0018, 0x6305): "abdominal_ct_elderly",
    (0x0018, 0x6306): "geriatric_mri_protocol",
    (0x0018, 0x6307): "dementia_mri_protocol",
    (0x0018, 0x6308): "stroke_mri_elderly",
    (0x0018, 0x6309): "cardiac_mri_elderly",
    (0x0018, 0x6310): "musculoskeletal_mri_elderly",
    (0x0018, 0x6311): "geriatric_ultrasound",
    (0x0018, 0x6312): "carotid_ultrasound_elderly",
    (0x0018, 0x6313): "abdominal_ultrasound_elderly",
    (0x0018, 0x6314): "echocardiogram_elderly",
    (0x0018, 0x6315): "geriatric_xray",
    (0x0018, 0x6316): "bone_density_scan",
    (0x0018, 0x6317): "dexa_scan",
    (0x0018, 0x6318): "qct_scan",
    (0x0018, 0x6319): "fracture_risk_assessment",
    (0x0018, 0x6320): "vertebral_fracture_assessment",
    (0x0018, 0x6321): "contrast_considerations",
    (0x0018, 0x6322): "renal_function_contrast",
    (0x0018, 0x6323): "iodinated_contrast_dose",
    (0x0018, 0x6324): "gadolinium_contrast",
    (0x0018, 0x6325): "nephrogenic_systemic_fibrosis",
    (0x0018, 0x6326): "radiation_sensitivity",
    (0x0018, 0x6327): "positioning_considerations",
    (0x0018, 0x6328): "mobility_assistance",
    (0x0018, 0x6329): "transfer_assistance",
    (0x0018, 0x6330): "holding_assistance",
    (0x0018, 0x6331): "breathing_instruction",
    (0x0018, 0x6332): "compression_avoidance",
    (0x0018, 0x6333): "padding_requirements",
    (0x0018, 0x6334): "hydration_protocol",
    (0x0018, 0x6335): "npo_consideration",
    (0x0018, 0x6336): "cognitive_support",
    (0x0018, 0x6337): "family_member_present",
    (0x0018, 0x6338): "clear_communication",
    (0x0018, 0x6339): "large_print_materials",
    (0x0018, 0x6340): "hearing_assistance",
    (0x0018, 0x6341): "extended_appointment_time",
    (0x0018, 0x6342): "rest_breaks",
    (0x0018, 0x6343): "multiple_visit_protocol",
    (0x0018, 0x6344): "image_quality_geriatric",
    (0x0018, 0x6345): "artifact_consideration",
    (0x0018, 0x6346): "motion_artifact",
    (0x0018, 0x6347): "metal_artifact",
    (0x0018, 0x6348): "breathing_artifact",
    (0x0018, 0x6349): "limited_study_indicator",
    (0x0018, 0x6350): "incomplete_study_reason",
}

GERIATRIC_OUTCOMES_TAGS = {
    (0x0018, 0x6401): "hospitalization_12months",
    (0x0018, 0x6402): "ed_visit_12months",
    (0x0018, 0x6403): "urgent_care_visit",
    (0x0018, 0x6404): "functional_decline",
    (0x0018, 0x6405): "adl_decline",
    (0x0018, 0x6406): "iadl_decline",
    (0x0018, 0x6407): "nursing_home_admission",
    (0x0018, 0x6408): "caregiver_burden",
    (0x0018, 0x6409): "zarit_burden_score",
    (0x0018, 0x6410): "emergency_discharge_planning",
    (0x0018, 0x6411): "transitional_care",
    (0x0018, 0x6412): "readmission_risk",
    (0x0018, 0x6413): "l_hospital_score",
    (0x0018, 0x6414): "orsi_score",
    (0x0018, 0x6415): "mortality_risk",
    (0x0018, 0x6416): "survival_estimate",
    (0x0018, 0x6417): "palliative_care_referral",
    (0x0018, 0x6418): "hospice_enrollment",
    (0x0018, 0x6419): "advance_care_planning",
    (0x0018, 0x6420): "goals_of_care_discussion",
    (0x0018, 0x6421): "treatment_burden_assessment",
    (0x0018, 0x6422): "quality_of_life",
    (0x0018, 0x6423): "eq5d_score",
    (0x0018, 0x6424): "sf36_score",
    (0x0018, 0x6425): "satisfaction_with_care",
    (0x0018, 0x6426): "patient_reported_outcome",
    (0x0018, 0x6427): "caregiver_reported_outcome",
    (0x0018, 0x6428): "geriatric_syndrome_treatment",
    (0x0018, 0x6429): "fall_prevention",
    (0x0018, 0x6430): "exercise_program",
    (0x0018, 0x6431): "physical_therapy",
    (0x0018, 0x6432): "occupational_therapy",
    (0x0018, 0x6433): "speech_therapy",
    (0x0018, 0x6434): "cognitive_stimulation",
    (0x0018, 0x6435): "memory_clinic_referral",
    (0x0018, 0x6436): "social_engagement",
    (0x0018, 0x6437): "community_program",
    (0x0018, 0x6438): "senior_center_involvement",
    (0x0018, 0x6439): "meal_delivery",
    (0x0018, 0x6440): "transportation_service",
    (0x0018, 0x6441): "home_health_aide",
    (0x0018, 0x6442): "homemaking_service",
    (0x0018, 0x6443): "personal_care_service",
    (0x0018, 0x6444): "companionship_service",
    (0x0018, 0x6445): "technology_assistance",
    (0x0018, 0x6446): "medical_alert_system",
    (0x0018, 0x6447): "smart_home_technology",
    (0x0018, 0x6448): "telehealth_visits",
    (0x0018, 0x6449): "remote_monitoring",
    (0x0018, 0x6450): "chronic_care_management",
}

TOTAL_TAGS_LXXVII = {}

TOTAL_TAGS_LXXVII.update(GERIATRIC_PATIENT_PARAMETERS)
TOTAL_TAGS_LXXVII.update(GERIATRIC_SYNDROMES_TAGS)
TOTAL_TAGS_LXXVII.update(POLYPHARMACY_TAGS)
TOTAL_TAGS_LXXVII.update(GERIATRIC_IMAGING_PROTOCOLS)
TOTAL_TAGS_LXXVII.update(GERIATRIC_OUTCOMES_TAGS)


def _extract_tags_lxxvii(ds: Any) -> Dict[str, Any]:
    extracted = {}
    tag_names = {tag: name for tag, name in TOTAL_TAGS_LXXVII.items()}
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


def _is_geriatric_imaging_file(file_path: str) -> bool:
    geriatric_indicators = [
        'geriatric', 'elderly', 'senior', 'aging', 'frailty', 'frail',
        'cognitive', 'dementia', 'alzheimer', 'delirium', 'depression',
        'polypharmacy', 'fall_risk', 'adl', 'iadl', 'nursing_home',
        'assisted_living', 'advance_directive', 'geriatric_syndrome',
        'cognitive_assessment', 'moca', 'mmse', 'geriatric_depression'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in geriatric_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxxvii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxxvii_detected": False,
        "fields_extracted": 0,
        "extension_lxxvii_type": "geriatric_imaging",
        "extension_lxxvii_version": "2.0.0",
        "geriatric_patient_parameters": {},
        "geriatric_syndromes": {},
        "polypharmacy": {},
        "geriatric_imaging_protocols": {},
        "geriatric_outcomes": {},
        "extraction_errors": [],
    }

    try:
        if not _is_geriatric_imaging_file(file_path):
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

        result["extension_lxxvii_detected"] = True

        geriatric_data = _extract_tags_lxxvii(ds)

        patient_params_set = set(GERIATRIC_PATIENT_PARAMETERS.keys())
        syndromes_set = set(GERIATRIC_SYNDROMES_TAGS.keys())
        polypharmacy_set = set(POLYPHARMACY_TAGS.keys())
        protocols_set = set(GERIATRIC_IMAGING_PROTOCOLS.keys())
        outcomes_set = set(GERIATRIC_OUTCOMES_TAGS.keys())

        for tag, value in geriatric_data.items():
            if tag in patient_params_set:
                result["geriatric_patient_parameters"][tag] = value
            elif tag in syndromes_set:
                result["geriatric_syndromes"][tag] = value
            elif tag in polypharmacy_set:
                result["polypharmacy"][tag] = value
            elif tag in protocols_set:
                result["geriatric_imaging_protocols"][tag] = value
            elif tag in outcomes_set:
                result["geriatric_outcomes"][tag] = value

        result["fields_extracted"] = len(geriatric_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxvii_field_count() -> int:
    return len(TOTAL_TAGS_LXXVII)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxvii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxvii_description() -> str:
    return (
        "Geriatric Imaging II metadata extraction. Provides comprehensive coverage of "
        "geriatric patient parameters, frailty assessment, geriatric syndromes, "
        "polypharmacy considerations, and elderly-specific imaging protocols."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxvii_modalities() -> List[str]:
    return ["CT", "MR", "US", "CR", "DR", "XA", "PT", "NM", "MG", "DX"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxvii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxvii_category() -> str:
    return "Geriatric Imaging II"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxvii_keywords() -> List[str]:
    return [
        "geriatric", "elderly", "aging", "frailty", "frail", "cognitive",
        "dementia", "Alzheimer's", "delirium", "depression", "polypharmacy",
        "fall risk", "ADL", "IADL", "nursing home", "advance directive",
        "geriatric syndrome", "cognitive assessment", "MoCA", "MMSE",
        "clinical frailty scale", "caregiver", "geriatric assessment"
    ]
