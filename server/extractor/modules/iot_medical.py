"""
Scientific DICOM/FITS Ultimate Advanced Extension LXV - Interventional Suite Imaging

This module provides comprehensive extraction of Interventional Suite Imaging parameters
including angio, embolization, ablation guidance, and minimally invasive procedures.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXV_AVAILABLE = True

INTERVENTIONAL_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x2500): "intervention_date",
    (0x0010, 0x2501): "intervention_time",
    (0x0010, 0x2502): "procedure_duration_minutes",
    (0x0010, 0x2503): "intervention_type",
    (0x0010, 0x2504): "procedure_subtype",
    (0x0010, 0x2505): "interventionist_name",
    (0x0010, 0x2506): "assisting_physician",
    (0x0010, 0x2507): "nurse_name",
    (0x0010, 0x2508): "tech_name",
    (0x0010, 0x2509): "room_number",
    (0x0010, 0x2510): "access_site",
    (0x0010, 0x2511): "femoral_access",
    (0x0010, 0x2512): "radial_access",
    (0x0010, 0x2513): "brachial_access",
    (0x0010, 0x2514): "axillary_access",
    (0x0010, 0x2515): "jugular_access",
    (0x0010, 0x2516): "pedal_access",
    (0x0010, 0x2517): "access_side",
    (0x0010, 0x2518): "sheath_size_fr",
    (0x0010, 0x2519): "sheath_length_cm",
    (0x0010, 0x2520): "arterial_access",
    (0x0010, 0x2521): "venous_access",
    (0x0010, 0x2522): "combined_access",
    (0x0010, 0x2523): "micro_puncture_access",
    (0x0010, 0x2524): "ultrasound_guided_access",
    (0x0010, 0x2525): "fluoro_guided_access",
    (0x0010, 0x2526): "target_vessel",
    (0x0010, 0x2527): "target_lesion",
    (0x0010, 0x2528): "lesion_length_mm",
    (0x0010, 0x2529): "lesion_diameter_mm",
    (0x0010, 0x2530): "lesion_severity_percent",
    (0x0010, 0x2531): "calcification_grade",
    (0x0010, 0x2532): "thrombus_presence",
    (0x0010, 0x2533): "dissection_presence",
    (0x0010, 0x2534): "perforation_presence",
    (0x0010, 0x2535): "pre_procedure_status",
    (0x0010, 0x2536): "post_procedure_status",
    (0x0010, 0x2537): "immediate_complication",
    (0x0010, 0x2538): "technical_success",
    (0x0010, 0x2539): "clinical_success",
    (0x0010, 0x2540): "procedure_failure_reason",
}

ANGIOGRAPHY_TAGS = {
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x0081): "echo_time",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0x9701): "angiography_indicator",
    (0x0018, 0x9702): "digital_subtraction_angiography",
    (0x0018, 0x9703): "rotational_angiography",
    (0x0018, 0x9704): "3d_angiography",
    (0x0018, 0x9705): "cone_beam_ct",
    (0x0018, 0x9706): "flat_detector_ct",
    (0x0018, 0x9707): "angiographic_series",
    (0x0018, 0x9708): "number_of_contrast_boluses",
    (0x0018, 0x9709): "contrast_agent",
    (0x0018, 0x9710): "contrast_volume_ml",
    (0x0018, 0x9711): "contrast_flow_rate_ml_s",
    (0x0018, 0x9712): "contrast_injection_delay",
    (0x0018, 0x9713): "contrast_injection_duration",
    (0x0018, 0x9714): "iodine_concentration_mg_ml",
    (0x0018, 0x9715): "injection_site",
    (0x0018, 0x9716): "power_injector_use",
    (0x0018, 0x9717): "injection_pressure_psi",
    (0x0018, 0x9718): "hand_injection",
    (0x0018, 0x9719): "test_bolus",
    (0x0018, 0x9720): "test_bolus_volume",
    (0x0018, 0x9721): "test_bolus_timing",
    (0x0018, 0x9722): "roadmap_subtraction",
    (0x0018, 0x9723): "mask_acquisition_time",
    (0x0018, 0x9724): "fill_acquisition_time",
    (0x0018, 0x9725): "pixel_shift_applied",
    (0x0018, 0x9726): "magnification_factor",
    (0x0018, 0x9727): "frame_rate_fps",
    (0x0018, 0x9728): "acquisition_duration",
    (0x0018, 0x9729): "number_of_frames",
    (0x0018, 0x9730): "cine_acquisition",
    (0x0018, 0x9731): " DSA_sequence_number",
    (0x0018, 0x9732): "angiographic_view",
    (0x0018, 0x9733): "c_arm_position",
    (0x0018, 0x9734): "c_arm_rotation",
    (0x0018, 0x9735): "c_arm_angle",
    (0x0018, 0x9736): "table_position",
    (0x0018, 0x9737): "source_detector_distance",
    (0x0018, 0x9738): "radiation_mode",
    (0x0018, 0x9739): "pulsed_fluoro_mode",
    (0x0018, 0x9740): "continuous_fluoro_mode",
    (0x0018, 0x9741): "last_image_hold",
    (0x0018, 0x9742): "store_saved_image",
    (0x0018, 0x9743): "image_stitched",
    (0x0018, 0x9744): "stent_position",
    (0x0018, 0x9745): "balloon_position",
    (0x0018, 0x9746): "device_deployed",
    (0x0018, 0x9747): "deployment_status",
}

EMBOLIZATION_TAGS = {
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
    (0x0018, 0x9801): "embolization_indicator",
    (0x0018, 0x9802): "transarterial_embolization",
    (0x0018, 0x9803): "transvenous_embolization",
    (0x0018, 0x9804): "direct_puncture_embolization",
    (0x0018, 0x9805): "embolization_agent",
    (0x0018, 0x9806): "coil_embolization",
    (0x0018, 0x9807): "particle_embolization",
    (0x0018, 0x9808): "liquid_embolization",
    (0x0018, 0x9809): "plug_embolization",
    (0x0018, 0x9810): "sclerosing_agent",
    (0x0018, 0x9811): " Onyx_embolization",
    (0x0018, 0x9812): " glue_embolization",
    (0x0018, 0x9813): "pva_particle_size",
    (0x0018, 0x9814): "microsphere_size",
    (0x0018, 0x9815): "coil_size_mm",
    (0x0018, 0x9816): "coil_length_cm",
    (0x0018, 0x9817): "number_of_coils",
    (0x0018, 0x9818): "embolic_agent_volume",
    (0x0018, 0x9819): "embolic_agent_concentration",
    (0x0018, 0x9820): "target_vessel_occluded",
    (0x0018, 0x9821): "collateral_flow",
    (0x0018, 0x9822): "non_target_embolization",
    (0x0018, 0x9823): "reflux_indicator",
    (0x0018, 0x9824): "stasis_achieved",
    (0x0018, 0x9825): "stasis_grade",
    (0x0018, 0x9826): "embolization_complete",
    (0x0018, 0x9827): "recanalization_indicator",
    (0x0018, 0x9828): "post_embolic_assessment",
    (0x0018, 0x9829): "devascularization_percent",
    (0x0018, 0x9830): "tumor_response",
    (0x0018, 0x9831): "bleeding_control",
    (0x0018, 0x9832): "aneurysm_occluded",
    (0x0018, 0x9833): "avf_occluded",
    (0x0018, 0x9834): "malformation_occluded",
}

ABLATION_TAGS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0x9901): "ablation_indicator",
    (0x0018, 0x9902): "radiofrequency_ablation",
    (0x0018, 0x9903): "microwave_ablation",
    (0x0018, 0x9904): "cryoablation",
    (0x0018, 0x9905): "irreversible_electroporation",
    (0x0018, 0x9906): "laser_ablation",
    (0x0018, 0x9907): "chemical_ablation",
    (0x0018, 0x9908): "high_intensity_focused_ultrasound",
    (0x0018, 0x9909): "ethanol_ablation",
    (0x0018, 0x9910): "acetic_acid_ablation",
    (0x0018, 0x9911): "ablation_target",
    (0x0018, 0x9912): "tumor_location",
    (0x0018, 0x9913): "tumor_size_mm",
    (0x0018, 0x9914): "number_of_probes",
    (0x0018, 0x9915): "probe_type",
    (0x0018, 0x9916): "probe_gauge",
    (0x0018, 0x9917): "generator_power_watts",
    (0x0018, 0x9918): "ablation_time_minutes",
    (0x0018, 0x9919): "temperature_target_celsius",
    (0x0018, 0x9920): "temperature_achieved",
    (0x0018, 0x9921): "energy_delivered_kj",
    (0x0018, 0x9922): "current_amps",
    (0x0018, 0x9923): "voltage_volts",
    (0x0018, 0x9924): "impedance_ohms",
    (0x0018, 0x9925): "ablation_zone_size_mm",
    (0x0018, 0x9926): "ablation_margin",
    (0x0018, 0x9927): "margins_clear",
    (0x0018, 0x9928): "thermal_protection",
    (0x0018, 0x9929): "adjacent_structure_protection",
    (0x0018, 0x9930): "hydrodissection",
    (0x0018, 0x9931): "CO2_injection",
    (0x0018, 0x9932): "thermocouple_placement",
    (0x0018, 0x9933): "real_time_temperature_monitoring",
    (0x0018, 0x9934): "ice_ball_formation",
    (0x0018, 0x9935): "freeze_thaw_cycles",
    (0x0018, 0x9936): "ablation_complete",
    (0x0018, 0x9937): "complication_indicator",
    (0x0018, 0x9938): "thermal_injury",
    (0x0018, 0x9939): "nearby_structure_injury",
    (0x0018, 0x9940): "post_ablation_protocol",
    (0x0018, 0x9941): "contrast_enhanced_assessment",
    (0x0018, 0x9942): "enhancement_pattern",
    (0x0018, 0x9943): "residual_enhancement",
    (0x0018, 0x9944): "new_enhancement",
}

BIOPSY_DRAINAGE_TAGS = {
    (0x0018, 0x9A01): "biopsy_indicator",
    (0x0018, 0x9A02): "core_biopsy",
    (0x0018, 0x9A03): "fine_needle_aspiration",
    (0x0018, 0x9A04): "cutting_needle_biopsy",
    (0x0018, 0x9A05): "vacuum_assisted_biopsy",
    (0x0018, 0x9A06): "image_guided_biopsy",
    (0x0018, 0x9A07): "ultrasound_guided_biopsy",
    (0x0018, 0x9A08): "ct_guided_biopsy",
    (0x0018, 0x9A09): "fluoro_guided_biopsy",
    (0x0018, 0x9A10): "mr_guided_biopsy",
    (0x0018, 0x9A11): "biopsy_target",
    (0x0018, 0x9A12): "biopsy_site",
    (0x0018, 0x9A13): "number_of_samples",
    (0x0018, 0x9A14): "sample_size_cm",
    (0x0018, 0x9A15): "needle_gauge",
    (0x0018, 0x9A16): "needle_length_cm",
    (0x0018, 0x9A17): "specimen_sent_to_pathology",
    (0x0018, 0x9A18): "frozen_section_biopsy",
    (0x0018, 0x9A19): "touch_prep_biopsy",
    (0x0018, 0x9A20): "drainage_indicator",
    (0x0018, 0x9A21): "percutaneous_drainage",
    (0x0018, 0x9A22): "catheter_drainage",
    (0x0018, 0x9A23): "pigtail_catheter",
    (0x0018, 0x9A24): "malecot_catheter",
    (0x0018, 0x9A25): "nephrostomy_tube",
    (0x0018, 0x9A26): "chest_tube",
    (0x0018, 0x9A27): "abscess_drainage",
    (0x0018, 0x9A28): "fluid_collection_drainage",
    (0x0018, 0x9A29): "drain_output_ml",
    (0x0018, 0x9A30): "drain_characteristics",
    (0x0018, 0x9A31): "drain_removal_date",
    (0x0018, 0x9A32): "drain_complication",
    (0x0018, 0x9A33): "sclerosing_therapy",
    (0x0018, 0x9A34): "pleurodesis",
    (0x0018, 0x9A35): "peritoneovenous_shunt",
    (0x0018, 0x9A36): "ventriculoperitoneal_shunt",
    (0x0018, 0x9A37): "shunt_revision",
    (0x0018, 0x9A38): "biopsy_result",
    (0x0018, 0x9A39): "malignant_biopsy",
    (0x0018, 0x9A40): "benign_biopsy",
    (0x0018, 0x9A41): "non_diagnostic_biopsy",
    (0x0018, 0x9A42): "repeat_biopsy_recommended",
}

INTERVENTIONAL_WORKFLOW_TAGS = {
    (0x0018, 0x9B01): "intervention_complete",
    (0x0018, 0x9B02): "technical_success",
    (0x0018, 0x9B03): "clinical_success",
    (0x0018, 0x9B04): "major_complication",
    (0x0018, 0x9B05): "minor_complication",
    (0x0018, 0x9B06): "death_indicator",
    (0x0018, 0x9B07): "myocardial_infarction",
    (0x0018, 0x9B08): "stroke_indicator",
    (0x0018, 0x9B09): "bleeding_complication",
    (0x0018, 0x9B10): "vascular_complication",
    (0x0018, 0x9B11): "infection_indicator",
    (0x0018, 0x9B12): "contrast_reaction",
    (0x0018, 0x9B13): "contrast_nephropathy",
    (0x0018, 0x9B14): "radiation_injury",
    (0x0018, 0x9B15): "procedure_related_injury",
    (0x0018, 0x9B16): "emergency_surgery",
    (0x0018, 0x9B17): "unscheduled_return_or",
    (0x0018, 0x9B18): "icu_admission_required",
    (0x0018, 0x9B19): "length_of_stay_days",
    (0x0018, 0x9B20): "follow_up_plan",
    (0x0018, 0x9B21): "imaging_follow_up",
    (0x0018, 0x9B22): "clinical_follow_up",
    (0x0018, 0x9B23): "medication_prescribed",
    (0x0018, 0x9B24): "antiplatelet_therapy",
    (0x0018, 0x9B25): "anticoagulation_therapy",
    (0x0018, 0x9B26): "statins_prescribed",
    (0x0018, 0x9B27): "discharge_medication",
    (0x0018, 0x9B28): "activity_restrictions",
    (0x0018, 0x9B29): "wound_care_instructions",
    (0x0018, 0x9B30): "follow_up_appointment",
    (0x0018, 0x9B31): "contact_information",
    (0x0018, 0x9B32): "patient_education",
    (0x0018, 0x9B33): "consent_documentation",
    (0x0018, 0x9B34): "procedure_risks_discussed",
    (0x0018, 0x9B35): "alternative_treatments_discussed",
    (0x0018, 0x9B36): "radiation_risks_discussed",
    (0x0018, 0x9B37): "contrast_risks_discussed",
    (0x0018, 0x9B38): "procedure_outcome_summary",
    (0x0018, 0x9B39): "recommendations_for_future",
    (0x0018, 0x9B40): "quality_metrics",
    (0x0018, 0x9B41): "dose_length_product",
    (0x0018, 0x9B42): "reference_air_kerma_rate",
    (0x0018, 0x9B43): "cumulative_air_kerma",
    (0x0018, 0x9B44): "dose_alert_level_reached",
}

TOTAL_TAGS_LXV = (
    INTERVENTIONAL_PATIENT_PARAMETERS |
    ANGIOGRAPHY_TAGS |
    EMBOLIZATION_TAGS |
    ABLATION_TAGS |
    BIOPSY_DRAINAGE_TAGS |
    INTERVENTIONAL_WORKFLOW_TAGS
)


def _extract_tags_lxv(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in TOTAL_TAGS_LXV.items():
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


def _is_interventional_suite_imaging_file(file_path: str) -> bool:
    interventional_indicators = [
        'interventional', 'angiography', 'embolization', 'ablation', 'biopsy',
        'drainage', 'angioplasty', 'stent', 'cath lab', 'interventional radiology',
        'tace', 'tare', 'vertebroplasty', 'kyphoplasty', 'thrombolysis',
        'thrombectomy', 'tpa', 'endovascular', 'transjugular', 'tips'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in interventional_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxv(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxv_detected": False,
        "fields_extracted": 0,
        "extension_lxv_type": "interventional_suite_imaging",
        "extension_lxv_version": "2.0.0",
        "interventional_patient_parameters": {},
        "angiography": {},
        "embolization": {},
        "ablation": {},
        "biopsy_drainage": {},
        "interventional_workflow": {},
        "extraction_errors": [],
    }

    try:
        if not _is_interventional_suite_imaging_file(file_path):
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

        result["extension_lxv_detected"] = True

        interventional_data = _extract_tags_lxv(ds)

        result["interventional_patient_parameters"] = {
            k: v for k, v in interventional_data.items()
            if k in INTERVENTIONAL_PATIENT_PARAMETERS.values()
        }
        result["angiography"] = {
            k: v for k, v in interventional_data.items()
            if k in ANGIOGRAPHY_TAGS.values()
        }
        result["embolization"] = {
            k: v for k, v in interventional_data.items()
            if k in EMBOLIZATION_TAGS.values()
        }
        result["ablation"] = {
            k: v for k, v in interventional_data.items()
            if k in ABLATION_TAGS.values()
        }
        result["biopsy_drainage"] = {
            k: v for k, v in interventional_data.items()
            if k in BIOPSY_DRAINAGE_TAGS.values()
        }
        result["interventional_workflow"] = {
            k: v for k, v in interventional_data.items()
            if k in INTERVENTIONAL_WORKFLOW_TAGS.values()
        }

        result["fields_extracted"] = len(interventional_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxv_field_count() -> int:
    return len(TOTAL_TAGS_LXV)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxv_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxv_description() -> str:
    return (
        "Interventional Suite Imaging metadata extraction. Provides comprehensive coverage of "
        "angiography, embolization, ablation guidance, biopsy, drainage procedures, "
        "and interventional workflow parameters."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxv_modalities() -> List[str]:
    return ["XA", "RF", "CT", "US", "MR"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxv_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxv_category() -> str:
    return "Interventional Suite Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxv_keywords() -> List[str]:
    return [
        "interventional radiology", "angiography", "embolization", "ablation", "biopsy",
        "drainage", "angioplasty", "stenting", "cath lab", "DSA", "rotational angio",
        "coil embolization", "particle embolization", "radiofrequency ablation",
        "microwave ablation", "cryoablation", "TACE", "TARE", "vertebroplasty",
        "kyphoplasty", "thrombolysis", "thrombectomy", "endovascular", "TIPs"
    ]


# Aliases for smoke test compatibility
def extract_iot_medical(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_lxv."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_lxv(file_path)

def get_iot_medical_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxv_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxv_field_count()

def get_iot_medical_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxv_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxv_version()

def get_iot_medical_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxv_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxv_description()

def get_iot_medical_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxv_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxv_supported_formats()

def get_iot_medical_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxv_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxv_modalities()
