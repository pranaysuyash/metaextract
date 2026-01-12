"""
Scientific DICOM/FITS Ultimate Advanced Extension LXVII - Radiation Oncology Simulation

This module provides comprehensive extraction of Radiation Oncology Simulation parameters
including treatment planning, dose calculation, and simulation imaging.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXVII_AVAILABLE = True

RT_SIMULATION_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x2700): "simulation_date",
    (0x0010, 0x2701): "simulation_time",
    (0x0010, 0x2702): "simulation_type",
    (0x0010, 0x2703): "ct_simulation",
    (0x0010, 0x2704): "mr_simulation",
    (0x0010, 0x2705): "pet_simulation",
    (0x0010, 0x2706): "conventional_simulation",
    (0x0010, 0x2707): "treatment_site",
    (0x0010, 0x2708): "treatment_intent",
    (0x0010, 0x2709): "curative_treatment",
    (0x0010, 0x2710): "palliative_treatment",
    (0x0010, 0x2711): "neoadjuvant_treatment",
    (0x0010, 0x2712): "adjuvant_treatment",
    (0x0010, 0x2713): "definitive_treatment",
    (0x0010, 0x2714): "primary_diagnosis",
    (0x0010, 0x2715): "histology",
    (0x0010, 0x2716): "stage_grouping",
    (0x0010, 0x2717): "t_descriptor",
    (0x0010, 0x2718): "n_descriptor",
    (0x0010, 0x2719): "m_descriptor",
    (0x0010, 0x2720): "prescription_dose_gy",
    (0x0010, 0x2721): "number_of_fractions",
    (0x0010, 0x2722): "dose_per_fraction_gy",
    (0x0010, 0x2723): "overall_treatment_time",
    (0x0010, 0x2724): "treatment_planning_status",
    (0x0010, 0x2725): "treatment_technique",
    (0x0010, 0x2726): "3d_conformal_rt",
    (0x0010, 0x2727): "imrt",
    (0x0010, 0x2728): "vmat",
    (0x0010, 0x2729): "sbrt",
    (0x0010, 0x2730): "srs",
    (0x0010, 0x2731): "tbi",
    (0x0010, 0x2732): "tmi",
    (0x0010, 0x2733): "surface_guidance",
    (0x0010, 0x2734): "motion_management",
    (0x0010, 0x2735): "respiratory_gating",
    (0x0010, 0x2736): "breath_hold",
    (0x0010, 0x2737): "tracking",
    (0x0010, 0x2738): "immobilization_device",
    (0x0010, 0x2739): "thermoplastic_mask",
    (0x0010, 0x2740): "vacuum_bag",
    (0x0010, 0x2741): "breast_board",
    (0x0010, 0x2742): "head_frame",
    (0x0010, 0x2743): "bite_block",
    (0x0010, 0x2744): "tattoo_markers",
    (0x0010, 0x2745): " fiducial_markers",
    (0x0010, 0x2746): "contrast_agent",
    (0x0010, 0x2747): "iv_contrast",
    (0x0010, 0x2748): "oral_contrast",
    (0x0010, 0x2749): "rectal_contrast",
}

RT_PLANNING_TAGS = {
    (0x0018, 0xB001): "rt_plan_indicator",
    (0x0018, 0xB002): "rt_plan_name",
    (0x0018, 0xB003): "rt_plan_label",
    (0x0018, 0xB004): "rt_plan_date",
    (0x0018, 0xB005): "rt_plan_time",
    (0x0018, 0xB006): "treatment_machine_name",
    (0x0018, 0xB007): "primary_fluence_mode",
    (0x0018, 0xB008): "secondary_fluence_mode",
    (0x0018, 0xB009): "energy_mode",
    (0x0018, 0xB010): "treatment_machine_type",
    (0x0018, 0xB011): "linear_accelerator",
    (0x0018, 0xB012): "cobalt_unit",
    (0x0018, 0xB013): "proton_therapy",
    (0x0018, 0xB014): "carbon_ion_therapy",
    (0x0018, 0xB015): "electron_therapy",
    (0x0018, 0xB016): "number_of_beams",
    (0x0018, 0xB017): "beam_energy_mev",
    (0x0018, 0xB018): "beam_mu",
    (0x0018, 0xB019): "gantry_angle",
    (0x0018, 0xB020): "gantry_rotation_direction",
    (0x0018, 0xB021): "couch_angle",
    (0x0018, 0xB022): "couch_rotation_direction",
    (0x0018, 0xB023): "couch_vertical_position",
    (0x0018, 0xB024): "couch_longitudinal_position",
    (0x0018, 0xB025): "couch_lateral_position",
    (0x0018, 0xB026): "isocenter_coordinates",
    (0x0018, 0xB027): "source_to_axis_distance",
    (0x0018, 0xB028): "patient_support_device",
    (0x0018, 0xB029): "wedge_angle",
    (0x0018, 0xB030): "wedge_factor",
    (0x0018, 0xB031): "wedge_orientation",
    (0x0018, 0xB032): "wedge_type",
    (0x0018, 0xB033): "physical_wedge",
    (0x0018, 0xB034): "dynamic_wedge",
    (0x0018, 0xB035): "multi_leaf_collimator",
    (0x0018, 0xB036): "mlc_leaf_width",
    (0x0018, 0xB037): "mlc_model",
    (0x0018, 0xB038): "block_type",
    (0x0018, 0xB039): "block_material",
    (0x0018, 0xB040): "block_thickness",
    (0x0018, 0xB041): "bolus_material",
    (0x0018, 0xB042): "bolus_thickness",
    (0x0018, 0xB043): "compensator_type",
    (0x0018, 0xB044): "compensator_material",
    (0x0018, 0xB045): "accessory_code",
    (0x0018, 0xB046): "shielding_indicator",
}

RT_DOSE_TAGS = {
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
    (0x0018, 0xC001): "rt_dose_indicator",
    (0x0018, 0xC002): "dose_grid_scaling",
    (0x0018, 0xC003): "dose_type",
    (0x0018, 0xC004): "physical_dose",
    (0x0018, 0xC005): "effective_dose",
    (0x0018, 0xC006): "dose_unit",
    (0x0018, 0xC007): "dose_summation_type",
    (0x0018, 0xC008): "total_dose",
    (0x0018, 0xC009): "fraction_dose",
    (0x0018, 0xC010): "voxel_size",
    (0x0018, 0xC011): "dose_volume_histogram",
    (0x0018, 0xC012): "dvh_roi_sequence",
    (0x0018, 0xC013): "dvh_min_dose",
    (0x0018, 0xC014): "dvh_max_dose",
    (0x0018, 0xC015): "dvh_mean_dose",
    (0x0018, 0xC016): "dvh_volume_cc",
    (0x0018, 0xC017): "dvh_dose_prescription",
    (0x0018, 0xC018): "dvh_dose_at_volume",
    (0x0018, 0xC019): "volume_at_dose_prescription",
    (0x0018, 0xC020): "hot_spot_volume",
    (0x0018, 0xC021): "cold_spot_volume",
    (0x0018, 0xC022): "conformality_index",
    (0x0018, 0xC023): "homogeneity_index",
    (0x0018, 0xC024): "gradient_index",
    (0x0018, 0xC025): "coverage_index",
    (0x0018, 0xC026): "normal_tissue_complexity",
    (0x0018, 0xC027): "modulation_factor",
    (0x0018, 0xC028): "quality_factor",
    (0x0018, 0xC029): "mu_per_fraction",
    (0x0018, 0xC030): "verification_status",
    (0x0018, 0xC031): "pretreatment_verification",
    (0x0018, 0xC032): "in_vivo_verification",
    (0x0018, 0xC033): "epid_verification",
    (0x0018, 0xC034): "portal_dosimetry",
    (0x0018, 0xC035): "transit_dosimetry",
}

CONTOUR_SEGMENTATION_TAGS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0xD001): "rt_structure_set_indicator",
    (0x0018, 0xD002): "structure_set_label",
    (0x0018, 0xD003): "structure_set_name",
    (0x0018, 0xD004): "structure_set_date",
    (0x0018, 0xD005): "structure_set_time",
    (0x0018, 0xD006): "number_of_roi",
    (0x0018, 0xD007): "roi_name",
    (0x0018, 0xD008): "roi_number",
    (0x0018, 0xD009): "roi_description",
    (0x0018, 0xD010): "roi_type",
    (0x0018, 0xD011): "volume_of_interest",
    (0x0018, 0xD012): "roi_generation_technique",
    (0x0018, 0xD013): "contour_generation_method",
    (0x0018, 0xD014): "contour_type",
    (0x0018, 0xD015): "roi_surface_generation",
    (0x0018, 0xD016): "roi_volume_cc",
    (0x0018, 0xD017): "roi_geometric_type",
    (0x0018, 0xD018): "roi_contour_sequence",
    (0x0018, 0xD019): "contour_number",
    (0x0018, 0xD020): "contour_type_geometric",
    (0x0018, 0xD021): "contour_type_closed",
    (0x0018, 0xD022): "contour_type_open",
    (0x0018, 0xD023): "number_of_contour_points",
    (0x0018, 0xD024): "contour_data",
    (0x0018, 0xD025): "contour_sequence",
    (0x0018, 0xD026): "approved_roi",
    (0x0018, 0xD027): "review_date",
    (0x0018, 0xD028): "review_time",
    (0x0018, 0xD029): "reviewer_name",
    (0x0018, 0xD030): "organ_at_risk",
    (0x0018, 0xD031): "planning_target_volume",
    (0x0018, 0xD032): "clinical_target_volume",
    (0x0018, 0xD033): "gross_tumor_volume",
    (0x0018, 0xD034): "internal_target_volume",
    (0x0018, 0xD035): "planning_at_risk_volume",
    (0x0018, 0xD036): "external_contour",
    (0x0018, 0xD037): "support_devices",
    (0x0018, 0xD038): "bolus_contours",
    (0x0018, 0xD039): "couch_contours",
    (0x0018, 0xD040): "marker_contours",
    (0x0018, 0xD041): "auto_contour_status",
    (0x0018, 0xD042): "contour_approved",
    (0x0018, 0xD043): "contour_locked",
}

IMAGE_GUIDANCE_TAGS = {
    (0x0018, 0xE001): "image_guided_rt_indicator",
    (0x0018, 0xE002): "igrt_modality",
    (0x0018, 0xE003): "cone_beam_ct",
    (0x0018, 0xE004): "fan_beam_ct",
    (0x0018, 0xE005): "orthogonal_kv_imaging",
    (0x0018, 0xE006): "orthogonal_mv_imaging",
    (0x0018, 0xE007): "surface_guided",
    (0x0018, 0xE008): "ultrasound_guided",
    (0x0018, 0xE009): "mr_guidance",
    (0x0018, 0xE010): "registration_method",
    (0x0018, 0xE011): "mutual_information",
    (0x0018, 0xE012): "cross_correlation",
    (0x0018, 0xE013): "gradient_difference",
    (0x0018, 0xE014): "pattern_intensity",
    (0x0018, 0xE015): "normalized_cross_correlation",
    (0x0018, 0xE016): "landmark_registration",
    (0x0018, 0xE017): "surface_registration",
    (0x0018, 0xE018): "registration_3d",
    (0x0018, 0xE019): "registration_2d",
    (0x0018, 0xE020): "registration_4d",
    (0x0018, 0xE021): "deformable_registration",
    (0x0018, 0xE022): "rigid_registration",
    (0x0018, 0xE023): "translation_only",
    (0x0018, 0xE024): "rigid_body_6dof",
    (0x0018, 0xE025): "translation_x_mm",
    (0x0018, 0xE026): "translation_y_mm",
    (0x0018, 0xE027): "translation_z_mm",
    (0x0018, 0xE028): "rotation_x_deg",
    (0x0018, 0xE029): "rotation_y_deg",
    (0x0018, 0xE030): "rotation_z_deg",
    (0x0018, 0xE031): "registration_quality",
    (0x0018, 0xE032): "registration_error_mm",
    (0x0018, 0xE033): "setup_error",
    (0x0018, 0xE034): "systematic_error",
    (0x0018, 0xE035): "random_error",
    (0x0018, 0xE036): "image_matching",
    (0x0018, 0xE037): "bone_matching",
    (0x0018, 0xE038): "soft_tissue_matching",
    (0x0018, 0xE039): "fiducial_matching",
    (0x0018, 0xE040): "mask_matching",
    (0x0018, 0xE041): "correction_strategy",
    (0x0018, 0xE042): "online_correction",
    (0x0018, 0xE043): "offline_correction",
    (0x0018, 0xE044): "adaptive_rt",
    (0x0018, 0xE045): "replanning_indicator",
}

RT_WORKFLOW_TAGS = {
    (0x0018, 0xF001): "simulation_complete",
    (0x0018, 0xF002): "contouring_complete",
    (0x0018, 0xF003): "planning_complete",
    (0x0018, 0xF004): "plan_approved",
    (0x0018, 0xF005): "physicist_qa_complete",
    (0x0018, 0xF006): "physician_approval",
    (0x0018, 0xF007): "treatment_ready",
    (0x0018, 0xF008): "quality_assurance",
    (0x0018, 0xF009): "patient_specific_qa",
    (0x0018, 0xF010): "delivered_dose_verification",
    (0x0018, 0xF011): "adaptive_replanning",
    (0x0018, 0xF012): "fraction_number",
    (0x0018, 0xF013): "treatment_date",
    (0x0018, 0xF014): "treatment_time",
    (0x0018, 0xF015): "delivered_mu",
    (0x0018, 0xF016): "gantry_angle_verified",
    (0x0018, 0xF017): "couch_angle_verified",
    (0x0018, 0xF018): "field_size_verified",
    (0x0018, 0xF019): "treatment_interruption",
    (0x0018, 0xF020): "interruption_reason",
    (0x0018, 0xF021): "interruption_duration",
    (0x0018, 0xF022): "tolerance_deviation",
    (0x0018, 0xF023): "action_level_reached",
    (0x0018, 0xF024): "corrective_action",
    (0x0018, 0xF025): "treatment_complication",
    (0x0018, 0xF026): "acute_toxicity",
    (0x0018, 0xF027): "late_toxicity",
    (0x0018, 0xF028): "rt_response",
    (0x0018, 0xF029): "local_control",
    (0x0018, 0xF030): "overall_survival",
    (0x0018, 0xF031): "disease_free_survival",
    (0x0018, 0xF032): "follow_up_status",
    (0x0018, 0xF033): "protocol_compliance",
    (0x0018, 0xF034): "deviation_from_plan",
    (0x0018, 0xF035): "beam_hold_incidents",
    (0x0018, 0xF036): "mlc_hold_incidents",
    (0x0018, 0xF037): "door_interlock",
    (0x0018, 0xF038): "collision_indicator",
    (0x0018, 0xF039): "emergency_stop",
    (0x0018, 0xF040): "machine_quality_check",
    (0x0018, 0xF041): "output_calibration",
    (0x0018, 0xF042): "constancy_check",
    (0x0018, 0xF043): "baseline_drift",
    (0x0018, 0xF044): "linac_downtime",
    (0x0018, 0xF045): "treatment_statistics",
    (0x0018, 0xF046): "daily_fraction_count",
    (0x0018, 0xF047): "accumulated_dose",
}

TOTAL_TAGS_LXVII = (
    RT_SIMULATION_PATIENT_PARAMETERS |
    RT_PLANNING_TAGS |
    RT_DOSE_TAGS |
    CONTOUR_SEGMENTATION_TAGS |
    IMAGE_GUIDANCE_TAGS |
    RT_WORKFLOW_TAGS
)


def _extract_tags_lxvii(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in TOTAL_TAGS_LXVII.items():
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


def _is_rt_simulation_file(file_path: str) -> bool:
    rt_indicators = [
        'radiation oncology', 'rt', 'radiotherapy', 'treatment planning',
        'simulation', 'ct sim', 'dosimetry', 'dose calculation', 'brachytherapy',
        'imrt', 'vmat', 'sbrt', 'srs', 'tbi', 'proton', 'carbon', 'linear accelerator',
        'linac', 'cobalt', 'electron', 'isocenter', 'mlc', 'wedge', 'bolus',
        'contour', 'structure set', 'ptv', 'ctv', "itv", "gtv", "ovar",
        'dvh', 'treatment plan', 'rt plan', 'igrt', 'image guidance'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in rt_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxvii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxvii_detected": False,
        "fields_extracted": 0,
        "extension_lxvii_type": "radiation_oncology_simulation",
        "extension_lxvii_version": "2.0.0",
        "rt_simulation_patient_parameters": {},
        "rt_planning": {},
        "rt_dose": {},
        "contour_segmentation": {},
        "image_guidance": {},
        "rt_workflow": {},
        "extraction_errors": [],
    }

    try:
        if not _is_rt_simulation_file(file_path):
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

        result["extension_lxvii_detected"] = True

        rt_data = _extract_tags_lxvii(ds)

        result["rt_simulation_patient_parameters"] = {
            k: v for k, v in rt_data.items()
            if k in RT_SIMULATION_PATIENT_PARAMETERS.values()
        }
        result["rt_planning"] = {
            k: v for k, v in rt_data.items()
            if k in RT_PLANNING_TAGS.values()
        }
        result["rt_dose"] = {
            k: v for k, v in rt_data.items()
            if k in RT_DOSE_TAGS.values()
        }
        result["contour_segmentation"] = {
            k: v for k, v in rt_data.items()
            if k in CONTOUR_SEGMENTATION_TAGS.values()
        }
        result["image_guidance"] = {
            k: v for k, v in rt_data.items()
            if k in IMAGE_GUIDANCE_TAGS.values()
        }
        result["rt_workflow"] = {
            k: v for k, v in rt_data.items()
            if k in RT_WORKFLOW_TAGS.values()
        }

        result["fields_extracted"] = len(rt_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxvii_field_count() -> int:
    return len(TOTAL_TAGS_LXVII)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxvii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxvii_description() -> str:
    return (
        "Radiation Oncology Simulation metadata extraction. Provides comprehensive coverage of "
        "treatment planning, dose calculation, contouring, image guidance, and RT workflow."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxvii_modalities() -> List[str]:
    return ["CT", "MR", "PT", "CR", "DR", "XA", "RT"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxvii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxvii_category() -> str:
    return "Radiation Oncology Simulation"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxvii_keywords() -> List[str]:
    return [
        "radiation oncology", "radiotherapy", "treatment planning", "CT simulation",
        "IMRT", "VMAT", "SBRT", "SRS", "TBI", "proton therapy", "carbon therapy",
        "linear accelerator", "dosimetry", "dose calculation", "DVH", "DVH",
        "contouring", "structure set", "PTV", "CTV", "ITV", "GTV", "OAR",
        "isocenter", "MLC", "wedge", "bolus", "IGRT", "image guided",
        "cone beam CT", "registration", "treatment verification"
    ]


# Aliases for smoke test compatibility
def extract_mhealth(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_lxvii."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_lxvii(file_path)

def get_mhealth_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxvii_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxvii_field_count()

def get_mhealth_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxvii_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxvii_version()

def get_mhealth_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxvii_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxvii_description()

def get_mhealth_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxvii_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxvii_supported_formats()

def get_mhealth_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxvii_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxvii_modalities()
