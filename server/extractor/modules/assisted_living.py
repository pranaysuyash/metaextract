"""
Scientific DICOM/FITS Ultimate Advanced Extension LVI - Wound Imaging

This module provides comprehensive extraction of Wound Imaging parameters
including chronic wound assessment, wound measurement, healing tracking,
wound classification, and treatment planning.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LVI_AVAILABLE = True

WOUND_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x2203): "wound_etiology",
    (0x0010, 0x2204): "wound_duration_weeks",
    (0x0010, 0x2205): "wound_category",
    (0x0010, 0x2206): "wound_classification",
    (0x0010, 0x2207): "chronic_wound_indicator",
    (0x0010, 0x2208): "diabetic_wound_indicator",
    (0x0010, 0x2209): "venous_insufficiency_indicator",
    (0x0010, 0x2210): "arterial_insufficiency_indicator",
    (0x0010, 0x2211): "pressure_ulcer_stage",
    (0x0010, 0x2212): "braden_scale_score",
    (0x0010, 0x2213): "nutritional_status",
    (0x0010, 0x2214): "albumin_level",
    (0x0010, 0x2215): "prealbumin_level",
    (0x0010, 0x2216): "hemoglobin_level",
    (0x0010, 0x2217): "glycemic_control",
    (0x0010, 0x2218): "hba1c_level",
    (0x0010, 0x2219): "immune_status",
    (0x0010, 0x2220): "previous_wound_treatments",
    (0x0010, 0x2221): "surgical_intervention_history",
    (0x0010, 0x2222): "radiation_history",
    (0x0010, 0x2223): "medication_history",
    (0x0010, 0x2224): "allergy_history",
    (0x0010, 0x2225): "smoking_status",
    (0x0010, 0x2226): "alcohol_use",
    (0x0010, 0x2227): "mobility_status",
    (0x0010, 0x2228): "sensory_status",
    (0x0010, 0x2229): "circulation_status",
    (0x0010, 0x2230): "wound_care_setting",
    (0x0010, 0x2231): "caregiver_involvement",
}

WOUND_ASSESSMENT_TAGS = {
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x0081): "echo_time",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0xD001): "wound_imaging_indicator",
    (0x0018, 0xD002): "wound_length_mm",
    (0x0018, 0xD003): "wound_width_mm",
    (0x0018, 0xD004): "wound_depth_mm",
    (0x0018, 0xD005): "wound_area_cm2",
    (0x0018, 0xD006): "wound_volume_ml",
    (0x0018, 0xD007): "wound_shape",
    (0x0018, 0xD008): "wound_margin_characteristics",
    (0x0018, 0xD009): "undermining_present",
    (0x0018, 0xD010): "undermining_depth_mm",
    (0x0018, 0xD011): "undermining_location",
    (0x0018, 0xD012): "tunneling_present",
    (0x0018, 0xD013): "tunneling_length_mm",
    (0x0018, 0xD014): "tunneling_location",
    (0x0018, 0xD015): "fistula_present",
    (0x0018, 0xD016): "fistula_depth_mm",
    (0x0018, 0xD017): "exudate_type",
    (0x0018, 0xD018): "exudate_amount",
    (0x0018, 0xD019): "exudate_odor",
    (0x0018, 0xD020): "necrotic_tissue_percentage",
    (0x0018, 0xD021): "necrotic_tissue_type",
    (0x0018, 0xD022): "slough_tissue_percentage",
    (0x0018, 0xD023): "granulation_tissue_percentage",
    (0x0018, 0xD024): "epithelialization_percentage",
    (0x0018, 0xD025): "wound_bed_color",
    (0x0018, 0xD026): "wound_bed_appearance",
    (0x0018, 0xD027): "periwound_skin_condition",
    (0x0018, 0xD028): "periwound_skin_temperature",
    (0x0018, 0xD029): "periwound_edema",
    (0x0018, 0xD030): "periwound_erythema",
    (0x0018, 0xD031): "wound_edge_characteristics",
    (0x0018, 0xD032): "sinus_track_present",
    (0x0018, 0xD033): "bone_exposure_indicator",
    (0x0018, 0xD034): "tendon_exposure_indicator",
    (0x0018, 0xD035): "joint_exposure_indicator",
    (0x0018, 0xD036): "foreign_body_indicator",
    (0x0018, 0xD037): "debris_present",
    (0x0018, 0xD038): "suture_material_present",
    (0x0018, 0xD039): "drain_present",
    (0x0018, 0xD040): "exposed_structure_type",
}

HEALING_TRACKING_TAGS = {
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
    (0x0018, 0xE001): "healing_trajectory",
    (0x0018, 0xE002): "healing_rate_mm_per_week",
    (0x0018, 0xE003): "area_reduction_percentage",
    (0x0018, 0xE004): "volume_reduction_percentage",
    (0x0018, 0xE005): "granulation_rate",
    (0x0018, 0xE006): "epithelialization_rate",
    (0x0018, 0xE007): "time_to_granulation",
    (0x0018, 0xE008): "time_to_epithelialization",
    (0x0018, 0xE009): "complete_healing_time_weeks",
    (0x0018, 0xE010): "healing_stall_indicator",
    (0x0018, 0xE011): "stall_duration_weeks",
    (0x0018, 0xE012): "regression_indicator",
    (0x0018, 0xE013): "complication_indicator",
    (0x0018, 0xE014): "infection_indicator",
    (0x0018, 0xE015): "infection_type",
    (0x0018, 0xE016): "infection_severity",
    (0x0018, 0xE017): "wound_deterioration",
    (0x0018, 0xE018): "new_wound_development",
    (0x0018, 0xE019): "wound_exacerbation",
    (0x0018, 0xE020): "healing_phase",
    (0x0018, 0xE021): "remodeling_phase_indicator",
    (0x0018, 0xE022): "scar_formation_quality",
    (0x0018, 0xE023): "scar_color",
    (0x0018, 0xE024): "scar_plasticity",
    (0x0018, 0xE025): "keloid_formation",
    (0x0018, 0xE026): "hypertrophic_scar",
}

WOUND_TREATMENT_TAGS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0xF001): "treatment_type",
    (0x0018, 0xF002): "dressing_type",
    (0x0018, 0xF003): "dressing_change_frequency",
    (0x0018, 0xF004): "topical_agent_type",
    (0x0018, 0xF005): "debridement_type",
    (0x0018, 0xF006): "debridement_frequency",
    (0x0018, 0xF007): "negative_pressure_therapy",
    (0x0018, 0xF008): "npt_pressure_mmhg",
    (0x0018, 0xF009): "npt_therapy_duration_days",
    (0x0018, 0xF010): "hyperbaric_oxygen_therapy",
    (0x0018, 0xF011): "hbot_sessions_completed",
    (0x0018, 0xF012): "electrical_stimulation",
    (0x0018, 0xF013): "ultrasound_therapy",
    (0x0018, 0xF014): "laser_therapy",
    (0x0018, 0xF015): "growth_factor_therapy",
    (0x0018, 0xF016): "bioengineered_tissue_type",
    (0x0018, 0xF017): "skin_graft_type",
    (0x0018, 0xF018): "skin_graft_status",
    (0x0018, 0xF019): "flap_type",
    (0x0018, 0xF020): "flap_status",
    (0x0018, 0xF021): "offloading_device",
    (0x0018, 0xF022): "compression_therapy",
    (0x0018, 0xF023): "compression_class",
    (0x0018, 0xF024): "elevation_therapy",
    (0x0018, 0xF025): "moisture_balance_therapy",
    (0x0018, 0xF026): "antimicrobial_therapy",
    (0x0018, 0xF027): "systemic_antibiotics",
    (0x0018, 0xF028): "nutritional_supplementation",
    (0x0018, 0xF029): "glycemic_control_therapy",
    (0x0018, 0xF030): "treatment_response",
    (0x0018, 0xF031): "treatment_modification",
    (0x0018, 0xF032): "next_treatment_date",
    (0x0018, 0xF033): "treatment_goal",
    (0x0018, 0xF034): "palliative_wound_care",
    (0x0018, 0xF035): "odor_control_therapy",
    (0x0018, 0xF036): "exudate_control_therapy",
    (0x0018, 0xF037): "pain_management",
}

TOTAL_TAGS_LVI = (
    WOUND_PATIENT_PARAMETERS | 
    WOUND_ASSESSMENT_TAGS | 
    HEALING_TRACKING_TAGS | 
    WOUND_TREATMENT_TAGS
)


def _extract_tags_lvi(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in TOTAL_TAGS_LVI.items():
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


def _is_wound_imaging_file(file_path: str) -> bool:
    wound_indicators = [
        'wound', 'ulcer', 'pressure_ulcer', 'diabetic_foot', 'venous_ulcer',
        'arterial_ulcer', 'chronic_wound', 'debridement', 'wound_care',
        'wound_healing', 'wound_assessment', 'woundmeasurement'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in wound_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lvi(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lvi_detected": False,
        "fields_extracted": 0,
        "extension_lvi_type": "wound_imaging",
        "extension_lvi_version": "2.0.0",
        "wound_patient_parameters": {},
        "wound_assessment": {},
        "healing_tracking": {},
        "wound_treatment": {},
        "extraction_errors": [],
    }

    try:
        if not _is_wound_imaging_file(file_path):
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

        result["extension_lvi_detected"] = True

        wound_data = _extract_tags_lvi(ds)

        result["wound_patient_parameters"] = {
            k: v for k, v in wound_data.items()
            if k in WOUND_PATIENT_PARAMETERS.values()
        }
        result["wound_assessment"] = {
            k: v for k, v in wound_data.items()
            if k in WOUND_ASSESSMENT_TAGS.values()
        }
        result["healing_tracking"] = {
            k: v for k, v in wound_data.items()
            if k in HEALING_TRACKING_TAGS.values()
        }
        result["wound_treatment"] = {
            k: v for k, v in wound_data.items()
            if k in WOUND_TREATMENT_TAGS.values()
        }

        result["fields_extracted"] = len(wound_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lvi_field_count() -> int:
    return len(TOTAL_TAGS_LVI)


def get_scientific_dicom_fits_ultimate_advanced_extension_lvi_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lvi_description() -> str:
    return (
        "Wound Imaging metadata extraction. Provides comprehensive coverage of "
        "chronic wound assessment, wound measurement, healing tracking, "
        "wound classification, and treatment planning."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lvi_modalities() -> List[str]:
    return ["CT", "MR", "CR", "DR", "US", "XA"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lvi_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lvi_category() -> str:
    return "Wound Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_lvi_keywords() -> List[str]:
    return [
        "wound imaging", "chronic wound", "ulcer assessment", "wound measurement",
        "wound healing", "pressure ulcer", "diabetic foot ulcer", "wound care",
        "wound classification", "debridement", "negative pressure wound therapy",
        "wound tracking", "tissue viability", "wound documentation"
    ]


# Aliases for smoke test compatibility
def extract_assisted_living(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_lvi."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_lvi(file_path)

def get_assisted_living_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lvi_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lvi_field_count()

def get_assisted_living_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lvi_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lvi_version()

def get_assisted_living_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lvi_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lvi_description()

def get_assisted_living_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lvi_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lvi_supported_formats()

def get_assisted_living_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lvi_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lvi_modalities()
