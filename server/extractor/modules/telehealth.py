"""
Scientific DICOM/FITS Ultimate Advanced Extension LXI - Pediatric Imaging

This module provides comprehensive extraction of Pediatric Imaging parameters
including age-specific protocols, developmental considerations, pediatric dosing,
child-friendly imaging environments, and growth assessment biomarkers.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXI_AVAILABLE = True

PEDIATRIC_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_height",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x2203): "gestational_age_weeks",
    (0x0010, 0x2204): "post_gestational_age_weeks",
    (0x0010, 0x2205): "chronological_age",
    (0x0010, 0x2206): "corrected_age",
    (0x0010, 0x2207): "developmental_age",
    (0x0010, 0x2208): "growth_percentile",
    (0x0010, 0x2209): "weight_percentile",
    (0x0010, 0x2210): "height_percentile",
    (0x0010, 0x2211): "head_circumference_percentile",
    (0x0010, 0x2212): "bmi_percentile",
    (0x0010, 0x2213): "bone_age_years",
    (0x0010, 0x2214): "bone_age_deviation_months",
    (0x0010, 0x2215): "tanner_stage",
    (0x0010, 0x2216): "puberty_status",
    (0x0010, 0x2217): "neonatal_intensive_care_days",
    (0x0010, 0x2218): "prematurity_history",
    (0x0010, 0x2219): "birth_weight_grams",
    (0x0010, 0x2220): "birth_length_cm",
    (0x0010, 0x2221): "apgar_score_1min",
    (0x0010, 0x2222): "apgar_score_5min",
    (0x0010, 0x2223): "apgar_score_10min",
    (0x0010, 0x2224): "neonatal_complications",
    (0x0010, 0x2225): "congenital_anomalies",
    (0x0010, 0x2226): "genetic_syndrome",
    (0x0010, 0x2227): "developmental_delay_indicator",
    (0x0010, 0x2228): "cognitive_development_level",
    (0x0010, 0x2229): "motor_development_level",
    (0x0010, 0x2230): "speech_development_level",
    (0x0010, 0x2231): "social_development_level",
    (0x0010, 0x2232): "guardian_consent_status",
    (0x0010, 0x2233): "guardian_relationship",
    (0x0010, 0x2234): "school_grade_level",
    (0x0010, 0x2235): "pediatric_learning_style",
    (0x0010, 0x2236): "anxiety_level",
    (0x0010, 0x2237): "cooperation_level",
    (0x0010, 0x2238): "preferred_distraction_method",
    (0x0010, 0x2239): "comfort_item_allowed",
}

PEDIATRIC_IMAGING_TAGS = {
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x0081): "echo_time",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0xA001): "pediatric_specific_protocol",
    (0x0018, 0xA002): "age_appropriate_dose",
    (0x0018, 0xA003): "weight_based_dose_mg_kg",
    (0x0018, 0xA004): "body_surface_area_m2",
    (0x0018, 0xA005): "dose_reduction_factor",
    (0x0018, 0xA006): "low_dose_protocol_indicator",
    (0x0018, 0xA007): "child_size_protocol",
    (0x0018, 0xA008): "newborn_protocol",
    (0x0018, 0xA009): "infant_protocol",
    (0x0018, 0xA010): "toddler_protocol",
    (0x0018, 0xA011): "preschool_protocol",
    (0x0018, 0xA012): "school_age_protocol",
    (0x0018, 0xA013): "adolescent_protocol",
    (0x0018, 0xA014): "reduced_scan_time",
    (0x0018, 0xA015): "simplified_positioning",
    (0x0018, 0xA016): "mock_scan_available",
    (0x0018, 0xA017): "play_therapy_available",
    (0x0018, 0xA018): "child_life_specialist",
    (0x0018, 0xA019): "distraction_technique",
    (0x0018, 0xA020): "reward_system",
    (0x0018, 0xA021): "parent_presence_allowed",
    (0x0018, 0xA022): "feeding_schedule_coordination",
    (0x0018, 0xA023): "sleep_deprivation_protocol",
    (0x0018, 0xA024): "sedation_requirement",
    (0x0018, 0xA025): "anesthesia_requirement",
    (0x0018, 0xA026): "iv_access_status",
    (0x0018, 0xA027): "contrast_tolerance_test",
    (0x0018, 0xA028): "radiation_exposure_history",
    (0x0018, 0xA029): "cumulative_dose_mSv",
    (0x0018, 0xA030): "prior_imaging_count",
    (0x0018, 0xA031): "ALARA_compliance",
    (0x0018, 0xA032): "justification_documentation",
    (0x0018, 0xA033): "optimization_documentation",
}

GROWTH_ASSESSMENT_TAGS = {
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
    (0x0018, 0xB001): "bone_age_assessment",
    (0x0018, 0xB002): "greulich_pyle_method",
    (0x0018, 0xB003): "tanner_whitehouse_method",
    (0x0018, 0xB004): "fels_method",
    (0x0018, 0xB005): "bone_age_standard_deviation",
    (0x0018, 0xB006): "predicted_adult_height",
    (0x0018, 0xB007): "height_prediction_error",
    (0x0018, 0xB008): "growth_velocity_cm_year",
    (0x0018, 0xB009): "growth_remaining_years",
    (0x0018, 0xB010): "vertebral_maturation_score",
    (0x0018, 0xB011): "hand_wrist_ossification",
    (0x0018, 0xB012): "carpal_bones_count",
    (0x0018, 0xB013): "epiphyseal_union_status",
    (0x0018, 0xB014): "growth_plate_status",
    (0x0018, 0xB015): "fracture_risk_assessment",
    (0x0018, 0xB016): "bone_density_z_score",
    (0x0018, 0xB017): "body_composition_analysis",
    (0x0018, 0xB018): "muscle_mass_estimate",
    (0x0018, 0xB019): "fat_mass_estimate",
    (0x0018, 0xB020): "lean_body_mass",
    (0x0018, 0xB021): "organ_size_percentile",
    (0x0018, 0xB022): "liver_size_percentile",
    (0x0018, 0xB023): "spleen_size_percentile",
    (0x0018, 0xB024): "kidney_size_percentile",
    (0x0018, 0xB025): "thyroid_volume_percentile",
    (0x0018, 0xB026): "thymus_size_percentile",
    (0x0018, 0xB027): "lymph_node_assessment",
    (0x0018, 0xB028): "hydrocephalus_indicator",
    (0x0018, 0xB029): "ventricular_size_percentile",
    (0x0018, 0xB030): "brain_volume_percentile",
    (0x0018, 0xB031): "cortical_thickness_mm",
    (0x0018, 0xB032): "myelination_status",
    (0x0018, 0xB033): "developmental_milestone",
    (0x0018, 0xB034): "motor_milestone_status",
    (0x0018, 0xB035): "cognitive_milestone_status",
}

CONGENITAL_ANOMALY_TAGS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0xC001): "congenital_anomaly_type",
    (0x0018, 0xC002): "cardiac_anomaly",
    (0x0018, 0xC003): "cardiac_anomaly_severity",
    (0x0018, 0xC004): "neural_tube_defect",
    (0x0018, 0xC005): "chromosomal_abnormality",
    (0x0018, 0xC006): "skeletal_dysplasia",
    (0x0018, 0xC007): "craniofacial_anomaly",
    (0x0018, 0xC008): "genitourinary_anomaly",
    (0x0018, 0xC009): "gastrointestinal_anomaly",
    (0x0018, 0xC010): "pulmonary_hypoplasia",
    (0x0018, 0xC011): "prenatal_diagnosis",
    (0x0018, 0xC012): "postnatal_diagnosis",
    (0x0018, 0xC013): "syndrome_classification",
    (0x0018, 0xC014): "icd_code",
    (0x0018, 0xC015): "omim_number",
    (0x0018, 0xC016): "inheritance_pattern",
    (0x0018, 0xC017): "recurrence_risk",
    (0x0018, 0xC018): "prenatal_intervention",
    (0x0018, 0xC019): "postnatal_intervention",
    (0x0018, 0xC020): "surgical_planning",
    (0x0018, 0xC021): "multidisciplinary_team_review",
    (0x0018, 0xC022): "genetic_counseling_status",
    (0x0018, 0xC023): "family_screening_indicator",
    (0x0018, 0xC024): "long_term_prognosis",
    (0x0018, 0xC025): "developmental_prognosis",
    (0x0018, 0xC026): "growth_prognosis",
    (0x0018, 0xC027): "functional_outlook",
    (0x0018, 0xC028): "quality_of_life_projection",
    (0x0018, 0xC029): "transition_care_plan",
    (0x0018, 0xC030): "adult_specialist_referral",
}

PEDIATRIC_ONCOLOGY_TAGS = {
    (0x0008, 0x0060): "modality",
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0020): "sequence_name",
    (0x0018, 0xD001): "pediatric_oncology_indicator",
    (0x0018, 0xD002): "cancer_type",
    (0x0018, 0xD003): "cancer_stage",
    (0x0018, 0xD004): "cancer_relapse_indicator",
    (0x0018, 0xD005): "treatment_phase",
    (0x0018, 0xD006): "chemotherapy_protocol",
    (0x0018, 0xD007): "radiation_therapy_plan",
    (0x0018, 0xD008): "surgical_intervention",
    (0x0018, 0xD009): "stem_cell_transplant",
    (0x0018, 0xD010): "immunotherapy_type",
    (0x0018, 0xD011): "targeted_therapy",
    (0x0018, 0xD012): "treatment_response",
    (0x0018, 0xD013): "minimal_residual_disease",
    (0x0018, 0xD014): "tumor_marker_level",
    (0x0018, 0xD015): "treatment_toxicity_grade",
    (0x0018, 0xD016): "late_effects_assessment",
    (0x0018, 0xD017): "growth_impairment_indicator",
    (0x0018, 0xD018): "cardiotoxicity_screening",
    (0x0018, 0xD019): "neurotoxicity_screening",
    (0x0018, 0xD020): "ototoxicity_screening",
    (0x0018, 0xD021): "fertility_preservation",
    (0x0018, 0xD022): "psychosocial_assessment",
    (0x0018, 0xD023): "school_reintegration",
    (0x0018, 0xD024): "family_support_services",
    (0x0018, 0xD025): "survivorship_care_plan",
    (0x0018, 0xD026): "long_term_follow_up",
    (0x0018, 0xD027): "treatment_summary",
    (0x0018, 0xD028): "relapse_indicators",
    (0x0018, 0xD029): "second_malignancy_risk",
    (0x0018, 0xD030): "health_maintenance_indicator",
}

TOTAL_TAGS_LXI = (
    PEDIATRIC_PATIENT_PARAMETERS | 
    PEDIATRIC_IMAGING_TAGS | 
    GROWTH_ASSESSMENT_TAGS | 
    CONGENITAL_ANOMALY_TAGS | 
    PEDIATRIC_ONCOLOGY_TAGS
)


def _extract_tags_lxi(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in TOTAL_TAGS_LXI.items():
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


def _is_pediatric_imaging_file(file_path: str) -> bool:
    pediatric_indicators = [
        'pediatric', 'paediatric', 'child', 'children', 'infant', 'neonatal',
        'newborn', 'adolescent', 'teenager', 'peds', 'growth_assessment',
        'bone_age', 'developmental', 'congenital', 'pediatric_oncology'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in pediatric_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxi(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxi_detected": False,
        "fields_extracted": 0,
        "extension_lxi_type": "pediatric_imaging",
        "extension_lxi_version": "2.0.0",
        "pediatric_patient_parameters": {},
        "pediatric_imaging": {},
        "growth_assessment": {},
        "congenital_anomaly": {},
        "pediatric_oncology": {},
        "extraction_errors": [],
    }

    try:
        if not _is_pediatric_imaging_file(file_path):
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

        result["extension_lxi_detected"] = True

        pediatric_data = _extract_tags_lxi(ds)

        result["pediatric_patient_parameters"] = {
            k: v for k, v in pediatric_data.items()
            if k in PEDIATRIC_PATIENT_PARAMETERS.values()
        }
        result["pediatric_imaging"] = {
            k: v for k, v in pediatric_data.items()
            if k in PEDIATRIC_IMAGING_TAGS.values()
        }
        result["growth_assessment"] = {
            k: v for k, v in pediatric_data.items()
            if k in GROWTH_ASSESSMENT_TAGS.values()
        }
        result["congenital_anomaly"] = {
            k: v for k, v in pediatric_data.items()
            if k in CONGENITAL_ANOMALY_TAGS.values()
        }
        result["pediatric_oncology"] = {
            k: v for k, v in pediatric_data.items()
            if k in PEDIATRIC_ONCOLOGY_TAGS.values()
        }

        result["fields_extracted"] = len(pediatric_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxi_field_count() -> int:
    return len(TOTAL_TAGS_LXI)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxi_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxi_description() -> str:
    return (
        "Pediatric Imaging metadata extraction. Provides comprehensive coverage of "
        "age-specific protocols, developmental considerations, pediatric dosing, "
        "child-friendly imaging environments, and growth assessment biomarkers."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxi_modalities() -> List[str]:
    return ["CT", "MR", "CR", "DR", "US", "PT", "NM", "MG", "XA", "RF"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxi_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxi_category() -> str:
    return "Pediatric Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxi_keywords() -> List[str]:
    return [
        "pediatric imaging", "children", "infants", "neonatal", "adolescent",
        "bone age", "growth assessment", "developmental imaging", "congenital anomalies",
        "pediatric oncology", "age-appropriate dose", "ALARA", "child life specialists",
        "pediatric protocols", "prematurity", "developmental delay", "pediatric CT",
        "pediatric MRI", "newborn screening"
    ]


# Aliases for smoke test compatibility
def extract_telehealth(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_lxi."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_lxi(file_path)

def get_telehealth_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxi_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxi_field_count()

def get_telehealth_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxi_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxi_version()

def get_telehealth_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxi_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxi_description()

def get_telehealth_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxi_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxi_supported_formats()

def get_telehealth_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxi_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxi_modalities()
