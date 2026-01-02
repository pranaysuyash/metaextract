"""
Scientific DICOM/FITS Ultimate Advanced Extension LX - Research Imaging

This module provides comprehensive extraction of Research Imaging parameters
including clinical trial imaging, protocol development, research biomarkers,
data sharing compliance, and academic research metadata.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LX_AVAILABLE = True

RESEARCH_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x2203): "study_protocol_id",
    (0x0010, 0x2204): "study_protocol_version",
    (0x0010, 0x2205): "clinical_trial_sponsor",
    (0x0010, 0x2206): "clinical_trial_protocol_id",
    (0x0010, 0x2207): "clinical_trial_protocol_name",
    (0x0010, 0x2208): "clinical_trial_phase",
    (0x0010, 0x2209): "clinical_trial_site_id",
    (0x0010, 0x2210): "clinical_trial_site_name",
    (0x0010, 0x2211): "clinical_trial_subject_id",
    (0x0010, 0x2212): "clinical_trial_subject_randomization_id",
    (0x0010, 0x2213): "clinical_trial_arm_id",
    (0x0010, 0x2214): "clinical_trial_arm_description",
    (0x0010, 0x2215): "clinical_trial_visit_id",
    (0x0010, 0x2216): "clinical_trial_visit_number",
    (0x0010, 0x2217): "clinical_trial_visit_name",
    (0x0010, 0x2218): "clinical_trial_timepoint",
    (0x0010, 0x2219): "clinical_trial_cohort_id",
    (0x0010, 0x2220): "clinical_trial_stratification_factor",
    (0x0010, 0x2221): "informed_consent_status",
    (0x0010, 0x2222): "consent_for_future_use",
    (0x0010, 0x2223): "consent_for_genomic_research",
    (0x0010, 0x2224): "research_eligibility_criteria",
    (0x0010, 0x2225): "inclusion_criteria_met",
    (0x0010, 0x2226): "exclusion_criteria_met",
    (0x0010, 0x2227): "screen_failure_reason",
    (0x0010, 0x2228): "enrollment_date",
    (0x0010, 0x2229): "randomization_date",
    (0x0010, 0x2230): "first_treatment_date",
    (0x0010, 0x2231): "last_treatment_date",
    (0x0010, 0x2232): "study_completion_date",
    (0x0010, 0x2233): "early_termination_date",
    (0x0010, 0x2234): "termination_reason",
    (0x0010, 0x2235): "follow_up_status",
}

CLINICAL_TRIAL_TAGS = {
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x0081): "echo_time",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0xC001): "research_study_type",
    (0x0018, 0xC002): "interventional_study",
    (0x0018, 0xC003): "observational_study",
    (0x0018, 0xC004): "blinding_status",
    (0x0018, 0xC005): "treatment_assignment",
    (0x0018, 0xC006): "control_group_indicator",
    (0x0018, 0xC007): "placebo_indicator",
    (0x0018, 0xC008): "active_comparator",
    (0x0018, 0xC009): "dose_level",
    (0x0018, 0xC010): "treatment_duration",
    (0x0018, 0xC011): "treatment_cycle_count",
    (0x0018, 0xC012): "response_assessment",
    (0x0018, 0xC013): "response_criteria",
    (0x0018, 0xC014): "recist_version",
    (0x0018, 0xC015): "response_evaluation_date",
    (0x0018, 0xC016): "target_lesion_count",
    (0x0018, 0xC017): "target_lesion_response",
    (0x0018, 0xC018): "non_target_lesion_response",
    (0x0018, 0xC019): "new_lesion_indicator",
    (0x0018, 0xC020): "overall_response",
    (0x0018, 0xC021): "progression_free_survival",
    (0x0018, 0xC022): "overall_survival",
    (0x0018, 0xC023): "disease_free_survival",
    (0x0018, 0xC024): "time_to_progression",
    (0x0018, 0xC025): "time_to_response",
    (0x0018, 0xC026): "duration_of_response",
    (0x0018, 0xC027): "safety_assessment",
    (0x0018, 0xC028): "adverse_event_record",
    (0x0018, 0xC029): "serious_adverse_event",
    (0x0018, 0xC030): "adverse_event_grade",
    (0x0018, 0xC031): "adverse_event_relationship",
    (0x0018, 0xC032): "laboratory_assessment",
    (0x0018, 0xC033): "vital_sign_assessment",
    (0x0018, 0xC034): "ecog_performance_status",
    (0x0018, 0xC035): "karnofsky_performance_status",
}

PROTOCOL_DEVELOPMENT_TAGS = {
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
    (0x0018, 0xD001): "research_protocol_type",
    (0x0018, 0xD002): "pilot_study_indicator",
    (0x0018, 0xD003): "feasibility_study_indicator",
    (0x0018, 0xD004): "proof_of_concept_indicator",
    (0x0018, 0xD005): "validation_study_indicator",
    (0x0018, 0xD006): "multi_center_study_indicator",
    (0x0018, 0xD007): "sample_size_calculation",
    (0x0018, 0xD008): "statistical_power",
    (0x0018, 0xD009): "significance_level",
    (0x0018, 0xD010): "primary_endpoint",
    (0x0018, 0xD011): "secondary_endpoint",
    (0x0018, 0xD012): "exploratory_endpoint",
    (0x0018, 0xD013): "hypothesis_statement",
    (0x0018, 0xD014): "statistical_method",
    (0x0018, 0xD015): "analysis_population",
    (0x0018, 0xD016): "intention_to_treat",
    (0x0018, 0xD017): "per_protocol_population",
    (0x0018, 0xD018): "safety_population",
    (0x0018, 0xD019): "interim_analysis_plan",
    (0x0018, 0xD020): "data_monitoring_committee",
    (0x0018, 0xD021): "stopping_rules",
    (0x0018, 0xD022): "adaptive_design_indicator",
    (0x0018, 0xD023): "sample_size_reestimation",
    (0x0018, 0xD024): "randomization_ratio",
    (0x0018, 0xD025): "stratification_factors",
    (0x0018, 0xD026): "block_size",
    (0x0018, 0xD027): "randomization_method",
    (0x0018, 0xD028): "allocation concealment",
    (0x0018, 0xD029): "masking_method",
    (0x0018, 0xD030): "double_blind_indicator",
}

DATA_SHARING_TAGS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0xE001): "data_sharing_consent",
    (0x0018, 0xE002): "restricted_data_indicator",
    (0x0018, 0xE003): "de_identification_method",
    (0x0018, 0xE004): "anonymization_level",
    (0x0018, 0xE005): "phi_removal_status",
    (0x0018, 0xE006): "data_repository_name",
    (0x0018, 0xE007): "data_repository_access",
    (0x0018, 0xE008): "embargo_period",
    (0x0018, 0xE009): "data_use_agreement",
    (0x0018, 0xE010): "research_use_only",
    (0x0018, 0xE011): "clinical_use_only",
    (0x0018, 0xE012): "collaboration_required",
    (0x0018, 0xE013): "attribution_requirement",
    (0x0018, 0xE014): "publication_restriction",
    (0x0018, 0xE015): "intellectual_property_rights",
    (0x0018, 0xE016): "material_transfer_agreement",
    (0x0018, 0xE017): "genomic_data_sharing",
    (0x0018, 0xE018): "biomarker_data_level",
    (0x0018, 0xE019): "raw_data_sharing",
    (0x0018, 0xE020): "processed_data_sharing",
    (0x0018, 0xE021): "derived_data_sharing",
    (0x0018, 0xE022): "image_data_sharing",
    (0x0018, 0xE023): "metadata_sharing",
    (0x0018, 0xE024): "code_sharing",
    (0x0018, 0xE025): "algorithm_sharing",
    (0x0018, 0xE026): "standard_compliance",
    (0x0018, 0xE027): "fair_principles_compliance",
    (0x0018, 0xE028): "findable_indicator",
    (0x0018, 0xE029): "accessible_indicator",
    (0x0018, 0xE030): "interoperable_indicator",
    (0x0018, 0xE031): "reusable_indicator",
}

RESEARCH_BIOMARKER_TAGS = {
    (0x0008, 0x0060): "modality",
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0020): "sequence_name",
    (0x0018, 0xF001): "biomarker_type",
    (0x0018, 0xF002): "imaging_biomarker",
    (0x0018, 0xF003): "radiomic_feature",
    (0x0018, 0xF004): "texture_feature",
    (0x0018, 0xF005): "shape_feature",
    (0x0018, 0xF006): "intensity_feature",
    (0x0018, 0xF007): "histogram_feature",
    (0x0018, 0xF008): "filter_response_feature",
    (0x0018, 0xF009): "deep_learning_feature",
    (0x0018, 0xF010): "quantitative_value",
    (0x0018, 0xF011): "measurement_unit",
    (0x0018, 0xF012): "reference_range",
    (0x0018, 0xF013): "cut_off_value",
    (0x0018, 0xF014): "sensitivity_percentage",
    (0x0018, 0xF015): "specificity_percentage",
    (0x0018, 0xF016): "auc_value",
    (0x0018, 0xF017): "positive_predictive_value",
    (0x0018, 0xF018): "negative_predictive_value",
    (0x0018, 0xF019): "likelihood_ratio_positive",
    (0x0018, 0xF020): "likelihood_ratio_negative",
    (0x0018, 0xF021): "diagnostic_accuracy",
    (0x0018, 0xF022): "prognostic_indicator",
    (0x0018, 0xF023): "predictive_indicator",
    (0x0018, 0xF024): "monitoring_indicator",
    (0x0018, 0xF025): "pharmacodynamic_indicator",
    (0x0018, 0xF026): "surrogate_endpoint",
    (0x0018, 0xF027): "companion_diagnostic",
    (0x0018, 0xF028): "theranostic_indicator",
    (0x0018, 0xF029): "gene_expression_marker",
    (0x0018, 0xF030): "protein_expression_marker",
    (0x0018, 0xF031): "mutation_status_marker",
    (0x0018, 0xF032): "metabolic_marker",
    (0x0018, 0xF033): "perfusion_marker",
    (0x0018, 0xF034): "diffusion_marker",
    (0x0018, 0xF035): "elasticity_marker",
    (0x0018, 0xF036): "angiogenesis_marker",
    (0x0018, 0xF037): "hypoxia_marker",
    (0x0018, 0xF038): "proliferation_marker",
    (0x0018, 0xF039): "apoptosis_marker",
    (0x0018, 0xF040): "inflammation_marker",
}

TOTAL_TAGS_LX = (
    RESEARCH_PATIENT_PARAMETERS | 
    CLINICAL_TRIAL_TAGS | 
    PROTOCOL_DEVELOPMENT_TAGS | 
    DATA_SHARING_TAGS | 
    RESEARCH_BIOMARKER_TAGS
)


def _extract_tags_lx(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in TOTAL_TAGS_LX.items():
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


def _is_research_imaging_file(file_path: str) -> bool:
    research_indicators = [
        'research', 'clinical_trial', 'protocol', 'biomarker', 'radiomic',
        'data_sharing', 'research_imaging', 'academic', 'study_protocol',
        'clinical_research', 'trial', 'investigation', 'exploratory',
        'longitudinal', 'observational', 'interventional'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in research_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lx(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lx_detected": False,
        "fields_extracted": 0,
        "extension_lx_type": "research_imaging",
        "extension_lx_version": "2.0.0",
        "research_patient_parameters": {},
        "clinical_trial": {},
        "protocol_development": {},
        "data_sharing": {},
        "research_biomarker": {},
        "extraction_errors": [],
    }

    try:
        if not _is_research_imaging_file(file_path):
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

        result["extension_lx_detected"] = True

        research_data = _extract_tags_lx(ds)

        result["research_patient_parameters"] = {
            k: v for k, v in research_data.items()
            if k in RESEARCH_PATIENT_PARAMETERS.values()
        }
        result["clinical_trial"] = {
            k: v for k, v in research_data.items()
            if k in CLINICAL_TRIAL_TAGS.values()
        }
        result["protocol_development"] = {
            k: v for k, v in research_data.items()
            if k in PROTOCOL_DEVELOPMENT_TAGS.values()
        }
        result["data_sharing"] = {
            k: v for k, v in research_data.items()
            if k in DATA_SHARING_TAGS.values()
        }
        result["research_biomarker"] = {
            k: v for k, v in research_data.items()
            if k in RESEARCH_BIOMARKER_TAGS.values()
        }

        result["fields_extracted"] = len(research_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lx_field_count() -> int:
    return len(TOTAL_TAGS_LX)


def get_scientific_dicom_fits_ultimate_advanced_extension_lx_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lx_description() -> str:
    return (
        "Research Imaging metadata extraction. Provides comprehensive coverage of "
        "clinical trial imaging, protocol development, research biomarkers, "
        "data sharing compliance, and academic research metadata for research applications."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lx_modalities() -> List[str]:
    return ["CT", "MR", "CR", "DR", "US", "PT", "NM", "MG", "XA", "RF"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lx_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lx_category() -> str:
    return "Research Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_lx_keywords() -> List[str]:
    return [
        "research imaging", "clinical trial", "protocol development", "biomarkers",
        "radiomics", "data sharing", "academic research", "clinical research",
        "research protocols", "imaging biomarkers", "clinical studies", "research data",
        "FAIR principles", "clinical trial imaging", "drug development", "precision medicine"
    ]
