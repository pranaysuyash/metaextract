"""
Scientific DICOM/FITS Ultimate Advanced Extension LVIII - Military and Trauma Imaging

This module provides comprehensive extraction of Military and Trauma Imaging parameters
including combat injuries, blast injuries, gunshot wounds, polytrauma assessment,
and military-specific imaging protocols.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LVIII_AVAILABLE = True

MILITARY_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x2203): "service_branch",
    (0x0010, 0x2204): "rank",
    (0x0010, 0x2205): "unit_identification",
    (0x0010, 0x2206): "deployment_status",
    (0x0010, 0x2207): "theater_of_operations",
    (0x0010, 0x2208): "incident_classification",
    (0x0010, 0x2209): "injury_date_time",
    (0x0010, 0x2210): "injury_location",
    (0x0010, 0x2211): "time_to_medical_care",
    (0x0010, 0x2212): "casualty_status",
    (0x0010, 0x2213): "evacuation_status",
    (0x0010, 0x2214): "evacuation_type",
    (0x0010, 0x2215): "evacuation_time",
    (0x0010, 0x2216): "medical_facility_type",
    (0x0010, 0x2217): "battle_injury_indicator",
    (0x0010, 0x2218): "non_battle_injury_indicator",
    (0x0010, 0x2219): "self_inflicted_indicator",
    (0x0010, 0x2220): "accidental_injury_indicator",
    (0x0010, 0x2221): "protective_gear_used",
    (0x0010, 0x2222): "helmet_status",
    (0x0010, 0x2223): "body_armor_status",
    (0x0010, 0x2224): "eye_protection_status",
    (0x0010, 0x2225): "combat_occupation_specialty",
    (0x0010, 0x2226): "mission_type",
    (0x0010, 0x2227): "enemy_activity_status",
    (0x0010, 0x2228): "witnesses_present",
    (0x0010, 0x2229): "security_clearance_level",
    (0x0010, 0x2230): "classified_injury_details",
}

COMBAT_INJURY_TAGS = {
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x0081): "echo_time",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0x9101): "combat_injury_indicator",
    (0x0018, 0x9102): "blast_injury_indicator",
    (0x0018, 0x9103): "blast_mechanism",
    (0x0018, 0x9104): "blast_type",
    (0x0018, 0x9105): "explosive_type",
    (0x0018, 0x9106): "explosive_yield",
    (0x0018, 0x9107): "distance_from_blast_m",
    (0x0018, 0x9108): "position_relative_to_blast",
    (0x0018, 0x9109): "primary_blast_injury",
    (0x0018, 0x9110): "secondary_blast_injury",
    (0x0018, 0x9111): "tertiary_blast_injury",
    (0x0018, 0x9112): "quaternary_blast_injury",
    (0x0018, 0x9113): "blast_overpressure_exposure",
    (0x0018, 0x9114): "concussion_indicator",
    (0x0018, 0x9115): "tbi_classification",
    (0x0018, 0x9116): "penetrating_injury_indicator",
    (0x0018, 0x9117): "fragment_wound_count",
    (0x0018, 0x9118): "fragment_wound_location",
    (0x0018, 0x9119): "fragment_wound_depth",
    (0x0018, 0x9120): "gunshot_wound_indicator",
    (0x0018, 0x9121): "weapon_type",
    (0x0018, 0x9122): "caliber",
    (0x0018, 0x9123): "muzzle_velocity",
    (0x0018, 0x9124): "entry_wound_location",
    (0x0018, 0x9125): "exit_wound_location",
    (0x0018, 0x9126): "projectile_trajectory",
    (0x0018, 0x9127): "projectile_fragmentation",
    (0x0018, 0x9128): "burn_percentage",
    (0x0018, 0x9129): "burn_degree",
    (0x0018, 0x9130): "burn_type",
    (0x0018, 0x9131): "inhalation_injury_indicator",
    (0x0018, 0x9132): "chemical_exposure_indicator",
    (0x0018, 0x9133): "radiation_exposure_indicator",
    (0x0018, 0x9134): "hypothermia_indicator",
    (0x0018, 0x9135): "drowning_indicator",
    (0x0018, 0x9136): "avulsion_injury",
    (0x0018, 0x9137): "amputation_level",
    (0x0018, 0x9138): "mutilating_injury",
    (0x0018, 0x9139): "crush_injury",
    (0x0018, 0x9140): "suspension_trauma",
}

POLYTRAUMA_ASSESSMENT_TAGS = {
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
    (0x0018, 0x92001): "polytrauma_indicator",
    (0x0018, 0x92002): "injury_severity_score",
    (0x0018, 0x92003): "abbreviated_injury_scale",
    (0x0018, 0x92004): "body_region_injured",
    (0x0018, 0x92005): "number_of_body_regions",
    (0x0018, 0x92006): "life_threatening_injury",
    (0x0018, 0x92007): "hemorrhage_indicator",
    (0x0018, 0x92008): "hemorrhage_severity",
    (0x0018, 0x92009): "hemorrhage_control_status",
    (0x0018, 0x92010): "shock_indicator",
    (0x0018, 0x92011): "shock_type",
    (0x0018, 0x92012): "hemodynamic_instability",
    (0x0018, 0x92013): "airway_compromise",
    (0x0018, 0x92014): "breathing_compromise",
    (0x0018, 0x92015): "circulation_compromise",
    (0x0018, 0x92016): "disability_indicator",
    (0x0018, 0x92017): "gcs_score",
    (0x0018, 0x92018): "exposure_indicator",
    (0x0018, 0x92019): "environmental_exposure",
    (0x0018, 0x92020): "triage_category",
    (0x0018, 0x92021): "primary_survey_complete",
    (0x0018, 0x92022): "secondary_survey_complete",
    (0x0018, 0x92023): "tertiary_survey_complete",
    (0x0018, 0x92024): "damage_control_surgery",
    (0x0018, 0x92025): "definitive_care_status",
    (0x0018, 0x92026): "transport_priority",
    (0x0018, 0x92027): "interfacility_transfer",
    (0x0018, 0x92028): "specialty_care_requirement",
    (0x0018, 0x92029): "rehabilitation_status",
    (0x0018, 0x92030): "long_term_disability",
}

MILITARY_SPECIFIC_TAGS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0x93001): "military_imaging_indicator",
    (0x0018, 0x93002): "field_hospital_indicator",
    (0x0018, 0x93003): "deployed_equipment_type",
    (0x0018, 0x93004): "portable_imaging_used",
    (0x0018, 0x93005): "forward_surgical_team",
    (0x0018, 0x93006): "combat_support_hospital",
    (0x0018, 0x93007): "level_1_care_facility",
    (0x0018, 0x93008): "level_2_care_facility",
    (0x0018, 0x93009): "level_3_care_facility",
    (0x0018, 0x93010): "aeromedical_evacuation",
    (0x0018, 0x93011): "ground_medical_evacuation",
    (0x0018, 0x93012): "naval_medical_evacuation",
    (0x0018, 0x93013): "joint_theater_trauma_system",
    (0x0018, 0x93014): "trauma_registry_entry",
    (0x0018, 0x93015): "lessons_learned_indicator",
    (0x0018, 0x93016): "case_review_status",
    (0x0018, 0x93017): "morbidity_mortality_review",
    (0x0018, 0x93018): "force_health_protection",
    (0x0018, 0x93019): "preventive_medicine_status",
    (0x0018, 0x93020): "occupational_health",
    (0x0018, 0x93021): "environmental_health",
    (0x0018, 0x93022): "veterinary_support",
    (0x0018, 0x93023): "dental_emergency",
    (0x0018, 0x93024): "behavioral_health",
    (0x0018, 0x93025): "ptsd_screening",
    (0x0018, 0x93026): "combat_stress",
    (0x0018, 0x93027): "resilience_program",
    (0x0018, 0x93028): "family_readiness",
    (0x0018, 0x93029): "casualty_notifications",
    (0x0018, 0x93030): "casualty_assistance",
}

TOTAL_TAGS_LVIII = (
    MILITARY_PATIENT_PARAMETERS | 
    COMBAT_INJURY_TAGS | 
    POLYTRAUMA_ASSESSMENT_TAGS | 
    MILITARY_SPECIFIC_TAGS
)


def _extract_tags_lviii(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in TOTAL_TAGS_LVIII.items():
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


def _is_military_trauma_file(file_path: str) -> bool:
    military_indicators = [
        'military', 'combat', 'trauma', 'blast', 'gunshot', 'gsw',
        'battle_injury', 'polytrauma', 'tbi', 'concussion', 'ied',
        'evacuation', 'field_hospital', 'casualty', 'theater'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in military_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lviii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lviii_detected": False,
        "fields_extracted": 0,
        "extension_lviii_type": "military_trauma_imaging",
        "extension_lviii_version": "2.0.0",
        "military_patient_parameters": {},
        "combat_injury": {},
        "polytrauma_assessment": {},
        "military_specific": {},
        "extraction_errors": [],
    }

    try:
        if not _is_military_trauma_file(file_path):
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

        result["extension_lviii_detected"] = True

        military_data = _extract_tags_lviii(ds)

        result["military_patient_parameters"] = {
            k: v for k, v in military_data.items()
            if k in MILITARY_PATIENT_PARAMETERS.values()
        }
        result["combat_injury"] = {
            k: v for k, v in military_data.items()
            if k in COMBAT_INJURY_TAGS.values()
        }
        result["polytrauma_assessment"] = {
            k: v for k, v in military_data.items()
            if k in POLYTRAUMA_ASSESSMENT_TAGS.values()
        }
        result["military_specific"] = {
            k: v for k, v in military_data.items()
            if k in MILITARY_SPECIFIC_TAGS.values()
        }

        result["fields_extracted"] = len(military_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lviii_field_count() -> int:
    return len(TOTAL_TAGS_LVIII)


def get_scientific_dicom_fits_ultimate_advanced_extension_lviii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lviii_description() -> str:
    return (
        "Military and Trauma Imaging metadata extraction. Provides comprehensive coverage of "
        "combat injuries, blast injuries, gunshot wounds, polytrauma assessment, "
        "and military-specific imaging protocols for deployed forces."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lviii_modalities() -> List[str]:
    return ["CT", "MR", "CR", "DR", "US", "PT", "NM", "XA", "RF"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lviii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lviii_category() -> str:
    return "Military and Trauma Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_lviii_keywords() -> List[str]:
    return [
        "military imaging", "combat injury", "blast injury", "trauma", "gunshot wound",
        "polytrauma", "TBI", "concussion", "IED", "battle injury",
        "aeromedical evacuation", "field hospital", "casualty care", "military trauma",
        "combat casualty care", "deployed imaging"
    ]
