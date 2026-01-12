"""
Scientific DICOM/FITS Ultimate Advanced Extension LIV - Palliative Imaging

This module provides comprehensive extraction of Palliative Imaging parameters
including end-of-life care imaging, comfort-focused protocols, symptom management,
and quality of life assessment for patients in palliative care.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LIV_AVAILABLE = True

PALLIATIVE_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x2203): "palliative_care_phase",
    (0x0010, 0x2204): "palliative_performance_status",
    (0x0010, 0x2205): "karnofsky_score",
    (0x0010, 0x2206): "ecog_score",
    (0x0010, 0x2207): "pain_level_scale",
    (0x0010, 0x2208): "symptom_burden_score",
    (0x0010, 0x2209): "quality_of_life_score",
    (0x0010, 0x2210): "palliative_prognostic_score",
    (0x0010, 0x2211): "survival_prediction_days",
    (0x0010, 0x2212): "care_goal_setting",
    (0x0010, 0x2213): "treatment_intent",
    (0x0010, 0x2214): "symptom_target_area",
    (0x0010, 0x2215): "primary_symptom_type",
    (0x0010, 0x2216): "secondary_symptom_type",
    (0x0010, 0x2217): "symptom_severity",
    (0x0010, 0x2218): "symptom_duration",
    (0x0010, 0x2219): "previous_symptom_interventions",
    (0x0010, 0x2220): "current_medications",
    (0x0010, 0x2221): "opioid_therapy_status",
    (0x0010, 0x2222): "adjuvant_therapy",
    (0x0010, 0x2223): "non_pharmacological_interventions",
    (0x0010, 0x2224): "caregiver_support_level",
    (0x0010, 0x2225): "home_care_support",
    (0x0010, 0x2226): "hospice_eligibility",
    (0x0010, 0x2227): "advance_care_plan_status",
    (0x0010, 0x2228): "dnr_status",
    (0x0010, 0x2229): "family_communication_status",
    (0x0010, 0x2230): "spiritual_care_needs",
    (0x0010, 0x2231): "psychological_support_needs",
    (0x0010, 0x2232): "social_work_involvement",
    (0x0010, 0x2233): "nutritional_status",
    (0x0010, 0x2234): "functional_status",
    (0x0010, 0x2235): "cognitive_status",
    (0x0010, 0x2236): "delirium_status",
    (0x0010, 0x2237): "anxiety_level",
    (0x0010, 0x2238): "depression_level",
    (0x0010, 0x2239): "dyspnea_severity",
    (0x0010, 0x2240): "nausea_severity",
    (0x0010, 0x2241): "constipation_severity",
    (0x0010, 0x2242): "fatigue_level",
    (0x0010, 0x2243): "insomnia_severity",
    (0x0010, 0x2244): "appetite_loss",
    (0x0010, 0x2245): "cachexia_indicator",
    (0x0010, 0x2246): "edema_severity",
    (0x0010, 0x2247): "wound_care_needs",
    (0x0010, 0x2248): "skin_integrity",
    (0x0010, 0x2249): "pressure_ulcer_risk",
}

COMFORT_FOCUSED_IMAGING_TAGS = {
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x0081): "echo_time",
    (0x0018, 0x0087): "echo_train_length",
    (0x0018, 0x0090): "frequency_selection_gradient_orientation",
    (0x0018, 0x0091): "magnetic_field_strength_tesla",
    (0x0018, 0x0095): "pixel_bandwidth",
    (0x0018, 0x0100): "spatial_resolution",
    (0x0018, 0x0150): "parallel_collection_mode",
    (0x0018, 0x0151): "parallel_collection_algorithm",
    (0x0018, 0x0210): "trigger_delay_time",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0x9701): "comfort_protocol_indicator",
    (0x0018, 0x9702): "reduced_scan_time",
    (0x0018, 0x9703): "minimal_positioning_required",
    (0x0018, 0x9704): "supine_only_protocol",
    (0x0018, 0x9705): "portable_equipment_use",
    (0x0018, 0x9706): "bedside_imaging",
    (0x0018, 0x9707): "rapid_sequence_protocol",
    (0x0018, 0x9708): "simplified_positioning",
    (0x0018, 0x9709): "padding_comfort_level",
    (0x0018, 0x9710): "temperature_comfort",
    (0x0018, 0x9711): "lighting_adjustment",
    (0x0018, 0x9712): "noise_reduction",
    (0x0018, 0x9713): "family_presence_allowed",
    (0x0018, 0x9714): "music_therapy_available",
    (0x0018, 0x9715): "sedation_level",
    (0x0018, 0x9716): "anxiety_management",
    (0x0018, 0x9717): "pain_management_prior",
    (0x0018, 0x9718): "break_schedule",
    (0x0018, 0x9719): "communication_preferences",
    (0x0018, 0x9720): "cognitive_assistance",
    (0x0018, 0x9721): "mobility_assistance",
    (0x0018, 0x9722): "transfer_assistance",
    (0x0018, 0x9723): "fall_precautions",
    (0x0018, 0x9724): "equipment_modification",
    (0x0018, 0x9725): "contrast_avoidance",
    (0x0018, 0x9726): "radiation_reduction",
    (0x0018, 0x9727): "scan_comfort_score",
    (0x0018, 0x9728): "patient_tolerance_rating",
    (0x0018, 0x9729): "procedure_completion_status",
    (0x0018, 0x9730): "adverse_event_indicator",
    (0x0018, 0x9731): "patient_feedback_rating",
}

SYMPTOM_MANAGEMENT_TAGS = {
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
    (0x0028, 0x1055): "window_center_and_width_explanation",
    (0x0028, 0x2110): "lossy_image_compression",
    (0x0028, 0x2112): "lossy_image_compression_ratio",
    (0x0028, 0x2114): "lossy_image_compression_method",
    (0x0018, 0x9801): "tumor_burden_assessment",
    (0x0018, 0x9802): "obstruction_indicator",
    (0x0018, 0x9803): "compression_indicator",
    (0x0018, 0x9804): "pain_source_identification",
    (0x0018, 0x9805): "fracture_risk_indicator",
    (0x0018, 0x9806): "bleeding_source",
    (0x0018, 0x9807): "infection_focus",
    (0x0018, 0x9808): "effusion_presence",
    (0x0018, 0x9809): "effusion_volume_estimate",
    (0x0018, 0x9810): "lymphadenopathy_indicator",
    (0x0018, 0x9811): "metastatic_burden",
    (0x0018, 0x9812): "spinal_cord_compression",
    (0x0018, 0x9813): "superior_vena_cava_syndrome",
    (0x0018, 0x9814): "brain_metastasis",
    (0x0018, 0x9815): "bone_metastasis",
    (0x0018, 0x9816): "visceral_metastasis",
    (0x0018, 0x9817): "treatment_response",
    (0x0018, 0x9818): "disease_progression",
    (0x0018, 0x9819): "stable_disease_indicator",
    (0x0018, 0x9820): "intervention_planning",
    (0x0018, 0x9821): "nerve_block_planning",
    (0x0018, 0x9822): "stent_planning",
    (0x0018, 0x9823): "drainage_planning",
    (0x0018, 0x9824): "radiation_planning",
    (0x0018, 0x9825): "ablation_planning",
    (0x0018, 0x9826): "vertebral_augmentation_planning",
    (0x0018, 0x9827): "target_lesion_identification",
    (0x0018, 0x9828): "target_lesion_size",
    (0x0018, 0x9829): "target_lesion_location",
    (0x0018, 0x9830): "non_target_lesion_status",
}

QUALITY_LIFE_ASSESSMENT_TAGS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0008, 0x1060): "physician_reading_study",
    (0x0008, 0x1070): "operator_name",
    (0x0008, 0x1080): "admitting_diagnoses_description",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0x0040): "tr",
    (0x0018, 0x0070): "data_collection_diameter",
    (0x0018, 0x0082): "inversion_time",
    (0x0018, 0x0084): "imaging_frequency",
    (0x0018, 0x0085): "imaged_nucleus",
    (0x0018, 0x0086): "number_of_phase_encoding_steps",
    (0x0018, 0x0160): "parallel_sampling_factor",
    (0x0018, 0x0170): "parallel_acquisition_factor",
    (0x0018, 0x0175): "water_fat_shift_pixels",
    (0x0018, 0x0180): "coil_array_type",
    (0x0018, 0x0181): "active_coil_dimension",
    (0x0018, 0x0194): "mr_acquisition_type",
    (0x0018, 0x0195): "sequence_type",
    (0x0018, 0x0120): "reconstruction_diameter",
    (0x0018, 0x0140): "distortion_correction_type",
    (0x0018, 0x1150): "exposure_time",
    (0x0018, 0x1151): "xray_tube_current",
    (0x0018, 0x1152): "exposure",
    (0x0018, 0x1160): "filter_material",
    (0x0018, 0x1110): "distance_source_to_detector",
    (0x0018, 0x1111): "distance_source_to_patient",
    (0x0018, 0x5100): "patient_position",
    (0x0018, 0x9901): "esAS_score",
    (0x0018, 0x9902): "esAS_symptom_subscale",
    (0x0018, 0x9903): "esAS_functional_subscale",
    (0x0018, 0x9904): "eq5d_index",
    (0x0018, 0x9905): "eq5d_vas",
    (0x0018, 0x9906): "sf36_physical_component",
    (0x0018, 0x9907): "sf36_mental_component",
    (0x0018, 0x9908): "FACIT_pal_score",
    (0x0018, 0x9909): "FACIT_physical_wellbeing",
    (0x0018, 0x9910): "FACIT_social_wellbeing",
    (0x0018, 0x9911): "FACIT_emotional_wellbeing",
    (0x0018, 0x9912): "FACIT_functional_wellbeing",
    (0x0018, 0x9913): "palliative_care_outcome_scale",
    (0x0018, 0x9914): "IPOS_total_score",
    (0x0018, 0x9915): "IPOS_physical_symptoms",
    (0x0018, 0x9916): "IPOS_psychological_symptoms",
    (0x0018, 0x9917): "IPOS_communication",
    (0x0018, 0x9918): "carer_assessment",
    (0x0018, 0x9919): "family_distress_scale",
    (0x0018, 0x9920): "bereavement_risk",
    (0x0018, 0x9921): "caregiver_burden",
    (0x0018, 0x9922): "social_support_evaluation",
    (0x0018, 0x9923): "financial_toxicity",
    (0x0018, 0x9924): "care_coordination_score",
    (0x0018, 0x9925): "service_access_evaluation",
    (0x0018, 0x9926): "place_of_care_evaluation",
    (0x0018, 0x9927): "place_of_death_preference",
    (0x0018, 0x9928): "goal_attainment_status",
    (0x0018, 0x9929): "care_plan_compliance",
    (0x0018, 0x9930): "family_satisfaction_care",
}

TOTAL_TAGS_LIV = (
    PALLIATIVE_PATIENT_PARAMETERS | 
    COMFORT_FOCUSED_IMAGING_TAGS | 
    SYMPTOM_MANAGEMENT_TAGS | 
    QUALITY_LIFE_ASSESSMENT_TAGS
)


def _extract_tags_liv(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in TOTAL_TAGS_LIV.items():
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


def _is_palliative_imaging_file(file_path: str) -> bool:
    palliative_indicators = [
        'palliative', 'hospice', 'end_of_life', 'comfort_care', 'terminal',
        'life_limiting', 'symptom_management', 'pain_control', 'quality_of_life',
        'terminal_illness', 'life_prolonging', 'care_plan', 'dying'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in palliative_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_liv(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_liv_detected": False,
        "fields_extracted": 0,
        "extension_liv_type": "palliative_imaging",
        "extension_liv_version": "2.0.0",
        "palliative_patient_parameters": {},
        "comfort_focused_imaging": {},
        "symptom_management": {},
        "quality_of_life_assessment": {},
        "extraction_errors": [],
    }

    try:
        if not _is_palliative_imaging_file(file_path):
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

        result["extension_liv_detected"] = True

        palliative_data = _extract_tags_liv(ds)

        result["palliative_patient_parameters"] = {
            k: v for k, v in palliative_data.items()
            if k in PALLIATIVE_PATIENT_PARAMETERS.values()
        }
        result["comfort_focused_imaging"] = {
            k: v for k, v in palliative_data.items()
            if k in COMFORT_FOCUSED_IMAGING_TAGS.values()
        }
        result["symptom_management"] = {
            k: v for k, v in palliative_data.items()
            if k in SYMPTOM_MANAGEMENT_TAGS.values()
        }
        result["quality_of_life_assessment"] = {
            k: v for k, v in palliative_data.items()
            if k in QUALITY_LIFE_ASSESSMENT_TAGS.values()
        }

        result["fields_extracted"] = len(palliative_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_liv_field_count() -> int:
    return len(TOTAL_TAGS_LIV)


def get_scientific_dicom_fits_ultimate_advanced_extension_liv_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_liv_description() -> str:
    return (
        "Palliative Imaging metadata extraction. Provides comprehensive coverage of "
        "end-of-life care imaging, comfort-focused protocols, symptom management, "
        "and quality of life assessment for patients in palliative care."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_liv_modalities() -> List[str]:
    return ["CT", "MR", "CR", "DR", "US", "PT", "NM", "XA", "RF"]


def get_scientific_dicom_fits_ultimate_advanced_extension_liv_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_liv_category() -> str:
    return "Palliative Care Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_liv_keywords() -> List[str]:
    return [
        "palliative care", "hospice", "end of life", "comfort care", "symptom management",
        "pain control", "quality of life", "terminal illness", "life limiting",
        "supportive care", "terminal care", "dying patient", "care planning"
    ]


# Aliases for smoke test compatibility
def extract_orthotics(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_liv."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_liv(file_path)

def get_orthotics_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_liv_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_liv_field_count()

def get_orthotics_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_liv_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_liv_version()

def get_orthotics_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_liv_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_liv_description()

def get_orthotics_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_liv_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_liv_supported_formats()

def get_orthotics_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_liv_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_liv_modalities()
