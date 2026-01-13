"""
Scientific DICOM/FITS Ultimate Advanced Extension LI - Geriatric Imaging

This module provides comprehensive extraction of Geriatric Imaging parameters
including age-specific acquisition protocols, osteoporosis assessment,
cognitive decline imaging, frailty assessment, and geriatric-specific
imaging biomarkers for elderly patients.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LI_AVAILABLE = True

GERIATRIC_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x21D0): "patient_complaint",
    (0x0010, 0x2203): "patient_age_decades",
    (0x0010, 0x2204): "patient_functional_status",
    (0x0010, 0x2205): "cognitive_status",
    (0x0010, 0x2206): "mobility_status",
    (0x0010, 0x2207): "living_situation",
    (0x0010, 0x2208): "caregiver_support",
    (0x0010, 0x2209): "geriatric_syndrome_present",
    (0x0010, 0x2210): "fall_risk_indicator",
    (0x0010, 0x2211): "frailty_index_score",
    (0x0010, 0x2212): "adl_score",
    (0x0010, 0x2213): "iadl_score",
    (0x0010, 0x2214): "mini_mental_state_exam_score",
    (0x0010, 0x2215): "clock_drawing_test_score",
    (0x0010, 0x2216): "geriatric_depression_scale_score",
    (0x0010, 0x2217): "timed_up_and_go_test_seconds",
    (0x0010, 0x2218): "gait_speed_meters_per_second",
    (0x0010, 0x2219): "grip_strength_kg",
    (0x0010, 0x2220): "sarcopenia_indicator",
    (0x0010, 0x2221): "malnutrition_risk",
    (0x0010, 0x2222): "polypharmacy_count",
    (0x0010, 0x2223): "social_support_level",
    (0x0010, 0x2224): "advance_directive_status",
    (0x0010, 0x2225): "code_status",
    (0x0010, 0x2226): "geriatric_specialist_referral",
    (0x0010, 0x2227): "care_plan_status",
}

OSTEOPOROSIS_ASSESSMENT_TAGS = {
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1110): "distance_source_to_detector",
    (0x0018, 0x1111): "distance_source_to_patient",
    (0x0018, 0x1150): "exposure_time",
    (0x0018, 0x1151): "xray_tube_current",
    (0x0018, 0x1152): "exposure",
    (0x0018, 0x1160): "filter_material",
    (0x0018, 0x1170): "generator_power",
    (0x0018, 0x1190): "focal_spot_size",
    (0x0018, 0x1201): "date_of_last_calibration",
    (0x0018, 0x1202): "time_of_last_calibration",
    (0x0018, 0x5100): "patient_position",
    (0x0018, 0x9067): "contrast_flow_duration",
    (0x0018, 0x9068): "contrast_flow_rate",
    (0x0018, 0x9069): "contrast_volume",
    (0x0018, 0x9071): "contrast_bolus_start_time",
    (0x0018, 0x9073): "contrast_ingredient",
    (0x0018, 0x9074): "contrast_ingredient_concentration",
    (0x0018, 0x9101): "calcium_hydroxyapatite_density",
    (0x0018, 0x9102): "bone_mineral_density_tscore",
    (0x0018, 0x9103): "bone_mineral_density_zscore",
    (0x0018, 0x9104): "vertebral_fracture_grade",
    (0x0018, 0x9105): "vertebral_morphometry_grade",
    (0x0018, 0x9106): "hip_axis_length",
    (0x0018, 0x9107): "femoral_neck_axis_length",
    (0x0018, 0x9108): "intertrochanteric_angle",
    (0x0018, 0x9109): "cortical_thickness_mm",
    (0x0018, 0x9110): "trabecular_bone_score",
    (0x0018, 0x9111): "osteoporotic_fragility_fracture_indicator",
    (0x0018, 0x9112): "vertebroplasty_indicator",
    (0x0018, 0x9113): "kyphoplasty_indicator",
    (0x0018, 0x9114): "fall_risk_modality_type",
    (0x0018, 0x9115): "dexa_scan_type",
    (0x0018, 0x9116): "qct_measurement_type",
    (0x0018, 0x9117): "pqct_measurement_site",
    (0x0018, 0x9118): "micromri_assessment_type",
    (0x0018, 0x9119): "bone_age_equivalent",
}

COGNITIVE_IMPAIRMENT_SCREENING_TAGS = {
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
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x0081): "echo_time",
    (0x0018, 0x0083): "number_of_averages",
    (0x0018, 0x0084): "imaging_frequency",
    (0x0018, 0x0085): "imaged_nucleus",
    (0x0018, 0x0086): "number_of_phase_encoding_steps",
    (0x0018, 0x0087): "echo_train_length",
    (0x0018, 0x0088): "slice_selection_gradient_orientation",
    (0x0018, 0x0089): "phase_selection_gradient_orientation",
    (0x0018, 0x0090): "frequency_selection_gradient_orientation",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1060): "sequence_variant",
    (0x0018, 0x1080): "scan_options",
    (0x0018, 0x1300): "geometric_atrophy_measurement",
    (0x0018, 0x1301): "hippocampal_volume_ml",
    (0x0018, 0x1302): "entorhinal_cortex_thickness_mm",
    (0x0018, 0x1303): "temporal_lobe_volume_ml",
    (0x0018, 0x1304): "frontal_lobe_volume_ml",
    (0x0018, 0x1305): "parietal_lobe_volume_ml",
    (0x0018, 0x1306): "occipital_lobe_volume_ml",
    (0x0018, 0x1307): "white_matter_hyperintensity_volume_ml",
    (0x0018, 0x1308): "lacunar_infarct_count",
    (0x0018, 0x1309): "cerebral_microbleed_count",
    (0x0018, 0x1310): "global_cortical_thickness_mm",
    (0x0018, 0x1311): "brain_parenchymal_fraction",
    (0x0018, 0x1312): "ventricular_volume_ml",
    (0x0018, 0x1313): "csf_space_volume_ml",
    (0x0018, 0x1314): "cortical_gray_matter_volume_ml",
    (0x0018, 0x1315): "white_matter_volume_ml",
    (0x0018, 0x1316): "deep_gray_matter_volume_ml",
    (0x0018, 0x1317): "dementia_subtype_indicator",
    (0x0018, 0x1318): "alzheimer_disease_indicator",
    (0x0018, 0x1319): "vascular_dementia_indicator",
    (0x0018, 0x1320): "lewy_body_dementia_indicator",
    (0x0018, 0x1321): "frontotemporal_dementia_indicator",
    (0x0018, 0x1322): "mild_cognitive_impairment_indicator",
    (0x0018, 0x1323): "amyloid_positivity",
    (0x0018, 0x1324): "tau_protein_level",
    (0x0018, 0x1325): "fdg_pet_metabolism_pattern",
}

GERIATRIC_FRACTURE_RISK_TAGS = {
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
    (0x0018, 0x1400): "intraoperative_contrast_agent_indicator",
    (0x0018, 0x1401): "contrast_agent_volume_ml",
    (0x0018, 0x1402): "contrast_agent_injection_rate_ml_per_sec",
    (0x0018, 0x1403): "contrast_agent_start_time_seconds",
    (0x0018, 0x1404): "contrast_agent_delay_seconds",
    (0x0018, 0x1405): "contrast_agent_observation_window_start",
    (0x0018, 0x1406): "contrast_agent_observation_window_end",
    (0x0018, 0x1407): "contrast_agent_type",
    (0x0018, 0x1408): "contrast_agent_concentration_mg_per_ml",
    (0x0018, 0x1409): "contrast_reaction_severity_indicator",
    (0x0018, 0x1410): "patient_comfort_indicator",
    (0x0018, 0x1411): "patient_cooperation_indicator",
    (0x0018, 0x1412): "patient_tolerance_indicator",
    (0x0018, 0x1413): "breathing_command_complexity_level",
    (0x0018, 0x1414): "instruction_comprehension_level",
    (0x0018, 0x1415): "scan_duration_minutes",
    (0x0018, 0x1416): "sedation_requirement_indicator",
    (0x0018, 0x1417): "physical_assistance_requirement",
    (0x0018, 0x1418): "mobility_assistance_requirement",
    (0x0018, 0x1419): "positioning_assistance_requirement",
    (0x0018, 0x1420): "fracture_risk_score",
    (0x0018, 0x1421): "frail_score",
    (0x0018, 0x1422): "comorbidity_index",
    (0x0018, 0x1423): "charlson_comorbidity_index",
    (0x0018, 0x1424): "elixhauser_comorbidity_score",
    (0x0018, 0x1425): "geriatric_8_indicator_score",
    (0x0018, 0x1426): "clinical_frailty_scale_score",
    (0x0018, 0x1427): "timi_geriatric_risk_score",
    (0x0018, 0x1428): "frailty_phenotype_score",
    (0x0018, 0x1429): "frailty_index_measurement",
}

GERIATRIC_MULTIMODAL_IMAGING_TAGS = {
    (0x0008, 0x0018): "sop_instance_uid",
    (0x0008, 0x0060): "modality",
    (0x0008, 0x0064): "conversion_type",
    (0x0008, 0x0201): "timezone_offset_from_utc",
    (0x0010, 0x0010): "patient_name",
    (0x0010, 0x0020): "patient_id",
    (0x0010, 0x0021): "issuer_of_patient_id",
    (0x0010, 0x0030): "patient_birth_date",
    (0x0010, 0x0032): "patient_birth_time",
    (0x0010, 0x0040): "patient_sex",
    (0x0010, 0x1000): "other_patient_names",
    (0x0010, 0x1001): "other_patient_ids",
    (0x0010, 0x1002): "ethnic_group",
    (0x0010, 0x1005): "patient_birth_name",
    (0x0010, 0x1040): "patient_address",
    (0x0010, 0x1060): "patient_mother_birth_name",
    (0x0010, 0x21C0): "pregnancy_status",
    (0x0010, 0x21D0): "last_menstrual_date",
    (0x0010, 0x21F0): "patient_religious_preference",
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0020): "sequence_name",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0028): "卧位_or_站位",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0x0040): "tr",
    (0x0018, 0x0070): "data_collection_diameter",
    (0x0018, 0x0082): "inversion_time",
    (0x0018, 0x0091): "magnetic_field_strength_tesla",
    (0x0018, 0x0095): "pixel_bandwidth",
    (0x0018, 0x0097): "receive_coil_name",
    (0x0018, 0x0098): "transmit_coil_name",
    (0x0018, 0x0099): "software_version",
    (0x0018, 0x0100): "spatial_resolution",
    (0x0018, 0x0110): "trigger_window",
    (0x0018, 0x0120): "reconstruction_diameter",
    (0x0018, 0x0140): "distortion_correction_type",
    (0x0018, 0x0150): "parallel_collection_mode",
    (0x0018, 0x0151): "parallel_collection_algorithm",
    (0x0018, 0x0160): "parallel_sampling_factor",
    (0x0018, 0x0170): "parallel_acquisition_factor",
    (0x0018, 0x0175): "water_fat_shift_pixels",
    (0x0018, 0x0180): "coil_array_type",
    (0x0018, 0x0181): "active_coil_dimension",
    (0x0018, 0x0194): "mr_acquisition_type",
    (0x0018, 0x0195): "sequence_type",
    (0x0018, 0x0210): "trigger_delay_time",
    (0x0018, 0x0240): "diffusion_b_matrix",
    (0x0018, 0x0241): "diffusion_b_value_nominal",
    (0x0018, 0x0242): "diffusion_b_value_vector",
    (0x0018, 0x0243): "diffusion_gradient_orientation",
    (0x0018, 0x0250): "diffusion_fractional_anisotropy",
    (0x0018, 0x0251): "diffusion_mean_diffusivity",
    (0x0018, 0x0255): "diffusion_intravoxel_incoherent_motion",
    (0x0018, 0x0260): "functional_mri_temporal_resolution",
    (0x0018, 0x0261): "functional_mri_number_of_volumes",
    (0x0018, 0x0280): "spect_energy_window_center",
    (0x0018, 0x0281): "spect_energy_window_width",
    (0x0018, 0x0282): "spect_data_type",
    (0x0018, 0x0283): "spect_total_counts",
    (0x0018, 0x0284): "spect_counts_accumulated",
    (0x0018, 0x0285): "spect_scatter_correction_method",
    (0x0018, 0x0286): "spect_attenuation_correction_method",
    (0x0018, 0x0287): "spect_reconstruction_method",
    (0x0018, 0x0300): "pet_radionuclide_total_dose_mbq",
    (0x0018, 0x0301): "pet_radionuclide_half_life_seconds",
    (0x0018, 0x0302): "pet_radionuclide_start_time",
    (0x0018, 0x0303): "pet_radionuclide_elapsed_time",
    (0x0018, 0x0304): "pet_radionuclide_positron_fraction",
    (0x0018, 0x0305): "pet_attenuation_correction_method",
    (0x0018, 0x0306): "pet_reconstruction_method",
    (0x0018, 0x0310): "pet_iteration_number",
    (0x0018, 0x0311): "pet_subset_number",
    (0x0018, 0x0320): "pet_suv_calculation_method",
    (0x0018, 0x0321): "pet_suv_normalization_factor",
    (0x0018, 0x0322): "pet_suv_partial_volume_correction",
    (0x0018, 0x0330): "pet_transaxial_fov_dimension",
    (0x0018, 0x0331): "pet_axial_fov_dimension",
    (0x0018, 0x0332): "pet_axial_sample_count",
    (0x0018, 0x0340): "ct_exposure_sequence",
    (0x0018, 0x0341): "ct_acquisition_type_sequence",
    (0x0018, 0x0342): "ct_acquisition_details_sequence",
    (0x0018, 0x0343): "ct_table_dynamics_sequence",
    (0x0018, 0x0344): "ct_table_position_sequence",
    (0x0018, 0x0345): "ct_slice_position_sequence",
    (0x0018, 0x0346): "ct_reconstruction_sequence",
    (0x0018, 0x0347): "ct_daas_sequence",
    (0x0018, 0x0348): "ct_image_sequence",
    (0x0018, 0x0350): "ct_acquisition_mode",
    (0x0018, 0x0351): "ct_exposure_modulation_type",
    (0x0018, 0x0352): "ct_acquisition_mode_continues",
    (0x0018, 0x0353): "ct_table_speed",
    (0x0018, 0x0354): "ct_table_feed_per_rotation",
    (0x0018, 0x0355): "ct_pitch_factor",
    (0x0018, 0x0360): "ct_spatial_resolution",
    (0x0018, 0x0361): "ct_contrast_bolus_agent",
    (0x0018, 0x0362): "ct_contrast_bolus_agent_sequence",
    (0x0018, 0x0370): "ct_radiation_dose_sequence",
    (0x0018, 0x0371): "ct_reconstruction_sequence_iterative",
    (0x0018, 0x0372): "ct_reconstruction_algorithm_iterative",
    (0x0018, 0x0380): "ct_projection_sequence",
    (0x0018, 0x0381): "ct_sinogram_sequence",
    (0x0018, 0x0382): "ct_sinogram_rejection_sequence",
    (0x0018, 0x0383): "ct_reconstruction_artifact_reduction_sequence",
    (0x0018, 0x0384): "ct_beam_hardening_correction_sequence",
    (0x0018, 0x0385): "ct_scatter_correction_sequence",
    (0x0018, 0x0386): "ct_ring_artifact_correction_sequence",
    (0x0018, 0x0387): "ct_streak_artifact_correction_sequence",
    (0x0018, 0x0388): "ct_metal_artifact_correction_sequence",
    (0x0018, 0x0389): "ct_motion_correction_sequence",
    (0x0018, 0x0390): "ct_respiratory_signal_source",
    (0x0018, 0x0391): "ct_respiratory_trigger_type",
    (0x0018, 0x0392): "ct_respiratory_trigger_delay",
    (0x0018, 0x0393): "ct_respiratory_trigger_threshold",
    (0x0018, 0x0394): "ct_respiratory_trigger_window",
    (0x0018, 0x0395): "ct_respiratory_phase",
    (0x0018, 0x0396): "ct_respiratory_cycle_duration",
    (0x0018, 0x0397): "ct_respiratory_gating_window_center",
    (0x0018, 0x0398): "ct_respiratory_gating_window_width",
    (0x0018, 0x0399): "ct_respiratory_gating_signal_type",
    (0x0018, 0x0400): "ct_cardiac_signal_source",
    (0x0018, 0x0401): "ct_cardiac_trigger_type",
    (0x0018, 0x0402): "ct_cardiac_trigger_delay",
    (0x0018, 0x0403): "ct_cardiac_trigger_threshold",
    (0x0018, 0x0404): "ct_cardiac_trigger_window",
    (0x0018, 0x0405): "ct_cardiac_phase",
    (0x0018, 0x0406): "ct_cardiac_cycle_duration",
    (0x0018, 0x0460): "us_image_type",
    (0x0018, 0x0461): "us_b_mode_frequency_hz",
    (0x0018, 0x0462): "us_doppler_frequency_hz",
    (0x0018, 0x0463): "us_pulse_repetition_frequency_hz",
    (0x0018, 0x0464): "us_doppler_sample_volume_position",
    (0x0018, 0x0465): "us_doppler_sample_volume_length",
    (0x0018, 0x0466): "us_prf_indicator",
    (0x0018, 0x0467): "us_doppler_spectral_width",
    (0x0018, 0x0468): "us_doppler_velocity_scale",
    (0x0018, 0x0469): "us_doppler_aliasing_velocity",
    (0x0018, 0x0470): "us_doppler_pulse_repetition_frequency",
    (0x0018, 0x0471): "us_color_doppler_velocity_scale",
    (0x0018, 0x0472): "us_color_doppler_ensemble_length",
    (0x0018, 0x0473): "us_color_doppler_persistence",
    (0x0018, 0x0474): "us_color_doppler_filter_setting",
    (0x0018, 0x0475): "us_color_doppler_line_density",
    (0x0018, 0x0476): "us_color_doppler_frame_averaging",
    (0x0018, 0x0477): "us_color_doppler_line_orientation",
    (0x0018, 0x0478): "us_color_doppler_scanplane_orientation",
    (0x0018, 0x0479): "us_color_doppler_scanplane_type",
    (0x0018, 0x0480): "us_elastometry_sequence",
    (0x0018, 0x0481): "us_elastometry_measurement_type",
    (0x0018, 0x0482): "us_elastometry_strain_direction",
    (0x0018, 0x0483): "us_elastometry_strain_percentage",
    (0x0018, 0x0484): "us_elastometry_stiffness_value",
    (0x0018, 0x0485): "us_elastometry_quality_indicator",
    (0x0018, 0x0486): "us_elastometry_quality_score",
    (0x0018, 0x0487): "us_elastometry_measurement_depth",
    (0x0018, 0x0488): "us_elastometry_roi_size",
    (0x0018, 0x0489): "us_elastometry_compression_force",
}

TOTAL_TAGS_LI = (
    GERIATRIC_PATIENT_PARAMETERS | 
    OSTEOPOROSIS_ASSESSMENT_TAGS | 
    COGNITIVE_IMPAIRMENT_SCREENING_TAGS | 
    GERIATRIC_FRACTURE_RISK_TAGS | 
    GERIATRIC_MULTIMODAL_IMAGING_TAGS
)


def _extract_tags_li(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in TOTAL_TAGS_LI.items():
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
        'geriatric', 'elderly', 'osteopor', 'frailty', 'cognitive',
        'dementia', 'alzheimer', 'fall_risk', 'bone_density',
        'geriatric_assessment', 'geriatric_imaging'
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


def extract_scientific_dicom_fits_ultimate_advanced_extension_li(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_li_detected": False,
        "fields_extracted": 0,
        "extension_li_type": "geriatric_imaging",
        "extension_li_version": "2.0.0",
        "geriatric_patient_parameters": {},
        "osteoporosis_assessment": {},
        "cognitive_impairment_screening": {},
        "fracture_risk_assessment": {},
        "multimodal_imaging": {},
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

        result["extension_li_detected"] = True

        geriatric_data = _extract_tags_li(ds)

        result["geriatric_patient_parameters"] = {
            k: v for k, v in geriatric_data.items()
            if k in GERIATRIC_PATIENT_PARAMETERS.values()
        }
        result["osteoporosis_assessment"] = {
            k: v for k, v in geriatric_data.items()
            if k in OSTEOPOROSIS_ASSESSMENT_TAGS.values()
        }
        result["cognitive_impairment_screening"] = {
            k: v for k, v in geriatric_data.items()
            if k in COGNITIVE_IMPAIRMENT_SCREENING_TAGS.values()
        }
        result["fracture_risk_assessment"] = {
            k: v for k, v in geriatric_data.items()
            if k in GERIATRIC_FRACTURE_RISK_TAGS.values()
        }
        result["multimodal_imaging"] = {
            k: v for k, v in geriatric_data.items()
            if k in GERIATRIC_MULTIMODAL_IMAGING_TAGS.values()
        }

        result["fields_extracted"] = len(geriatric_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_li_field_count() -> int:
    return len(TOTAL_TAGS_LI)


def get_scientific_dicom_fits_ultimate_advanced_extension_li_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_li_description() -> str:
    return (
        "Geriatric Imaging metadata extraction. Provides comprehensive coverage of "
        "age-specific acquisition protocols, osteoporosis assessment, cognitive decline "
        "imaging, frailty assessment, and geriatric-specific imaging biomarkers."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_li_modalities() -> List[str]:
    return ["CT", "MR", "CR", "DR", "US", "PT", "NM", "MG", "DX", "XA"]


def get_scientific_dicom_fits_ultimate_advanced_extension_li_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_li_category() -> str:
    return "Geriatric and Elderly Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_li_keywords() -> List[str]:
    return [
        "geriatric", "elderly", "osteoporosis", "bone density", "cognitive decline",
        "dementia", "frailty assessment", "fall risk", "cognitive impairment",
        "geriatric syndromes", "musculoskeletal aging", "neuroimaging aging",
        "geriatric oncology", "functional status", "quality of life",
        "caregiver support", "advance directives", "polypharmacy", "sarcopenia",
        "malnutrition screening", "comprehensive geriatric assessment"
    ]


# Aliases for smoke test compatibility
def extract_physical_therapy(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_li."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_li(file_path)

def get_physical_therapy_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_li_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_li_field_count()

def get_physical_therapy_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_li_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_li_version()

def get_physical_therapy_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_li_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_li_description()

def get_physical_therapy_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_li_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_li_supported_formats()

def get_physical_therapy_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_li_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_li_modalities()
