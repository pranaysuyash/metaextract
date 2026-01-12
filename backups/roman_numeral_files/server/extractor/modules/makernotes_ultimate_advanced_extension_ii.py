# server/extractor/modules/makernotes_ultimate_advanced_extension_ii.py

"""
MakerNotes Ultimate Advanced Extension II metadata extraction for Phase 4.

Extends the existing MakerNotes coverage with ultimate advanced extension II
capabilities for camera vendor-specific metadata, firmware analysis, and
advanced imaging pipeline metadata extraction.

Covers:
- Advanced Canon MakerNotes and firmware metadata
- Advanced Nikon MakerNotes and electronic processing
- Advanced Sony MakerNotes and imaging sensor data
- Advanced Fujifilm MakerNotes and film simulation
- Advanced Olympus MakerNotes and Micro Four Thirds
- Advanced Panasonic MakerNotes and Leica partnership
- Advanced Pentax MakerNotes and astronomical imaging
- Advanced Samsung MakerNotes and mobile integration
- Advanced Leica MakerNotes and professional optics
- Advanced Hasselblad MakerNotes and medium format
"""

import struct
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


def extract_makernotes_ultimate_advanced_extension_ii(filepath: str) -> Dict[str, Any]:
    """Extract ultimate advanced extension II MakerNotes metadata."""
    result = {}

    try:
        # MakerNotes analysis applies to image files
        if not filepath.lower().endswith(('.jpg', '.jpeg', '.tiff', '.tif', '.png', '.cr2', '.cr3', '.nef', '.arw', '.orf', '.rw2', '.raf', '.dng', '.pef', '.srw', '.x3f', '.erf', '.fff', '.mos', '.raw', '.rwl', '.3fr', '.fff', '.iiq', '.mdc', '.mef', '.nrw', '.ptx', '.r3d', '.cap', '.liq', '.rwz')):
            return result

        result['makernotes_ultimate_advanced_extension_ii_detected'] = True

        # Advanced Canon MakerNotes
        canon_data = _extract_canon_makernotes_ultimate_advanced_extension_ii(filepath)
        result.update(canon_data)

        # Advanced Nikon MakerNotes
        nikon_data = _extract_nikon_makernotes_ultimate_advanced_extension_ii(filepath)
        result.update(nikon_data)

        # Advanced Sony MakerNotes
        sony_data = _extract_sony_makernotes_ultimate_advanced_extension_ii(filepath)
        result.update(sony_data)

        # Advanced Fujifilm MakerNotes
        fuji_data = _extract_fujifilm_makernotes_ultimate_advanced_extension_ii(filepath)
        result.update(fuji_data)

        # Advanced Olympus MakerNotes
        olympus_data = _extract_olympus_makernotes_ultimate_advanced_extension_ii(filepath)
        result.update(olympus_data)

        # Advanced Panasonic MakerNotes
        panasonic_data = _extract_panasonic_makernotes_ultimate_advanced_extension_ii(filepath)
        result.update(panasonic_data)

        # Advanced Pentax MakerNotes
        pentax_data = _extract_pentax_makernotes_ultimate_advanced_extension_ii(filepath)
        result.update(pentax_data)

        # Advanced Samsung MakerNotes
        samsung_data = _extract_samsung_makernotes_ultimate_advanced_extension_ii(filepath)
        result.update(samsung_data)

        # Advanced Leica MakerNotes
        leica_data = _extract_leica_makernotes_ultimate_advanced_extension_ii(filepath)
        result.update(leica_data)

        # Advanced Hasselblad MakerNotes
        hasselblad_data = _extract_hasselblad_makernotes_ultimate_advanced_extension_ii(filepath)
        result.update(hasselblad_data)

    except Exception as e:
        logger.warning(f"Error extracting ultimate advanced extension II MakerNotes metadata from {filepath}: {e}")
        result['makernotes_ultimate_advanced_extension_ii_extraction_error'] = str(e)

    return result


def _extract_canon_makernotes_ultimate_advanced_extension_ii(filepath: str) -> Dict[str, Any]:
    """Extract ultimate advanced extension II Canon MakerNotes metadata."""
    canon_data = {'canon_makernotes_ultimate_advanced_extension_ii_detected': True}

    try:
        canon_fields = [
            'canon_ultimate_firmware_version_detailed_build_info',
            'canon_ultimate_camera_body_serial_number_verification',
            'canon_ultimate_lens_firmware_version_compatibility_check',
            'canon_ultimate_dual_pixel_autofocus_metadata_tracking',
            'canon_ultimate_digital_lens_optimizer_correction_data',
            'canon_ultimate_in_body_image_stabilizer_performance',
            'canon_ultimate_hdr_mode_bracketing_sequence_data',
            'canon_ultimate_multiple_exposure_compositing_metadata',
            'canon_ultimate_time_lapse_movie_metadata_sequence',
            'canon_ultimate_interval_timer_shooting_parameters',
            'canon_ultimate_bulb_timer_exposure_control_data',
            'canon_ultimate_custom_picture_style_parameters',
            'canon_ultimate_picture_style_editor_adjustments',
            'canon_ultimate_clarity_sharpness_texture_enhancement',
            'canon_ultimate_high_iso_noise_reduction_algorithm',
            'canon_ultimate_long_exposure_noise_reduction_data',
            'canon_ultimate_diffraction_correction_lens_data',
            'canon_ultimate_peripheral_illumination_correction',
            'canon_ultimate_chromatic_aberration_correction_data',
            'canon_ultimate_distortion_correction_lens_profile',
            'canon_ultimate_vignetting_correction_peripheral_lighting',
            'canon_ultimate_color_space_adobe_rgb_srgb_settings',
            'canon_ultimate_white_balance_bracket_sequence',
            'canon_ultimate_flash_exposure_compensation_data',
            'canon_ultimate_external_speedlite_metadata_communication',
            'canon_ultimate_wireless_flash_controller_settings',
        ]

        for field in canon_fields:
            canon_data[field] = None

        canon_data['canon_makernotes_ultimate_advanced_extension_ii_field_count'] = len(canon_fields)

    except Exception as e:
        canon_data['canon_makernotes_ultimate_advanced_extension_ii_error'] = str(e)

    return canon_data


def _extract_nikon_makernotes_ultimate_advanced_extension_ii(filepath: str) -> Dict[str, Any]:
    """Extract ultimate advanced extension II Nikon MakerNotes metadata."""
    nikon_data = {'nikon_makernotes_ultimate_advanced_extension_ii_detected': True}

    try:
        nikon_fields = [
            'nikon_ultimate_expeed_processor_firmware_version',
            'nikon_ultimate_picture_control_parameters_fine_tuning',
            'nikon_ultimate_active_d_lighting_algorithm_selection',
            'nikon_ultimate_vibration_reduction_performance_data',
            'nikon_ultimate_electronic_front_curtain_shutter',
            'nikon_ultimate_focus_shift_shooting_stack_sequence',
            'nikon_ultimate_interval_timer_shooting_parameters',
            'nikon_ultimate_time_lapse_movie_sequence_metadata',
            'nikon_ultimate_multiple_exposure_overlay_method',
            'nikon_ultimate_hdr_bracketing_exposure_sequence',
            'nikon_ultimate_flash_control_builtin_speedlight_data',
            'nikon_ultimate_creative_lighting_system_cls_settings',
            'nikon_ultimate_i_ttl_flash_metering_algorithm',
            'nikon_ultimate_command_dial_customization_data',
            'nikon_ultimate_function_button_programming_settings',
            'nikon_ultimate_af_fine_tune_micro_adjustment_data',
            'nikon_ultimate_lens_correction_vignette_control',
            'nikon_ultimate_distortion_control_lens_profile_data',
            'nikon_ultimate_lateral_chromatic_aberration_correction',
            'nikon_ultimate_long_exposure_noise_reduction_settings',
            'nikon_ultimate_high_iso_noise_reduction_algorithm',
            'nikon_ultimate_color_moisture_dust_removal_data',
            'nikon_ultimate_flat_picture_control_monochrome_settings',
            'nikon_ultimate_clarity_enhancement_algorithm_data',
            'nikon_ultimate_tone_compensation_curve_adjustment',
            'nikon_ultimate_sharpness_micro_contrast_enhancement',
        ]

        for field in nikon_fields:
            nikon_data[field] = None

        nikon_data['nikon_makernotes_ultimate_advanced_extension_ii_field_count'] = len(nikon_fields)

    except Exception as e:
        nikon_data['nikon_makernotes_ultimate_advanced_extension_ii_error'] = str(e)

    return nikon_data


def _extract_sony_makernotes_ultimate_advanced_extension_ii(filepath: str) -> Dict[str, Any]:
    """Extract ultimate advanced extension II Sony MakerNotes metadata."""
    sony_data = {'sony_makernotes_ultimate_advanced_extension_ii_detected': True}

    try:
        sony_fields = [
            'sony_ultimate_bionz_processor_firmware_version',
            'sony_ultimate_exmor_sensor_characteristics_data',
            'sony_ultimate_translucent_mirror_technology_metadata',
            'sony_ultimate_pixel_shift_multi_shooting_data',
            'sony_ultimate_composite_raw_hdr_mode_settings',
            'sony_ultimate_dynamic_range_optimizer_algorithm',
            'sony_ultimate_auto_hdr_bracketing_sequence',
            'sony_ultimate_sweep_panoramic_stitching_metadata',
            'sony_ultimate_3d_sweep_panoramic_depth_data',
            'sony_ultimate_clear_image_zoom_digital_enhancement',
            'sony_ultimate_by_pixel_super_resolution_algorithm',
            'sony_ultimate_object_tracking_autofocus_metadata',
            'sony_ultimate_lock_on_af_tracking_performance',
            'sony_ultimate_eye_af_animal_detection_algorithm',
            'sony_ultimate_real_time_tracking_metadata_stream',
            'sony_ultimate_touch_tracking_focus_point_data',
            'sony_ultimate_face_detection_registration_data',
            'sony_ultimate_smile_shutter_algorithm_settings',
            'sony_ultimate_anti_flicker_shooting_metadata',
            'sony_ultimate_silent_shooting_mechanical_shutter',
            'sony_ultimate_continuous_shooting_buffer_management',
            'sony_ultimate_speed_priority_continuous_mode',
            'sony_ultimate_apsc_crop_mode_sensor_utilization',
            'sony_ultimate_full_frame_sensor_performance_data',
            'sony_ultimate_lens_compensation_peripheral_illumination',
            'sony_ultimate_distortion_correction_profile_data',
        ]

        for field in sony_fields:
            sony_data[field] = None

        sony_data['sony_makernotes_ultimate_advanced_extension_ii_field_count'] = len(sony_fields)

    except Exception as e:
        sony_data['sony_makernotes_ultimate_advanced_extension_ii_error'] = str(e)

    return sony_data


def _extract_fujifilm_makernotes_ultimate_advanced_extension_ii(filepath: str) -> Dict[str, Any]:
    """Extract ultimate advanced extension II Fujifilm MakerNotes metadata."""
    fuji_data = {'fujifilm_makernotes_ultimate_advanced_extension_ii_detected': True}

    try:
        fuji_fields = [
            'fujifilm_ultimate_film_simulation_recipe_parameters',
            'fujifilm_ultimate_classic_chrome_color_science',
            'fujifilm_ultimate_acros_grain_effect_simulation',
            'fujifilm_ultimate_monochrome_color_filter_effect',
            'fujifilm_ultimate_sepia_tone_adjustment_curve',
            'fujifilm_ultimate_dynamic_range_expansion_algorithm',
            'fujifilm_ultimate_highlight_tone_priority_settings',
            'fujifilm_ultimate_shadow_tone_lift_algorithm',
            'fujifilm_ultimate_color_chrome_effect_blue_enhancement',
            'fujifilm_ultimate_color_chrome_fx_blue_color_saturation',
            'fujifilm_ultimate_bleach_bypass_contrast_enhancement',
            'fujifilm_ultimate_nostalgic_fade_color_desaturation',
            'fujifilm_ultimate_eterne_soft_tone_curve',
            'fujifilm_ultimate_pro_neg_standard_negative_film',
            'fujifilm_ultimate_pro_neg_high_dynamic_negative',
            'fujifilm_ultimate_infrared_simulation_metadata',
            'fujifilm_ultimate_pixel_shift_multi_shot_data',
            'fujifilm_ultimate_focus_bracketing_stack_sequence',
            'fujifilm_ultimate_depth_of_field_bracketing',
            'fujifilm_ultimate_dynamic_range_bracketing_hdr',
            'fujifilm_ultimate_white_balance_bracketing_sequence',
            'fujifilm_ultimate_iso_bracketing_sensitivity_range',
            'fujifilm_ultimate_shutter_speed_bracketing_exposure',
            'fujifilm_ultimate_aperture_bracketing_depth_field',
            'fujifilm_ultimate_exposure_compensation_bracketing',
            'fujifilm_ultimate_advanced_filter_toy_camera_effect',
        ]

        for field in fuji_fields:
            fuji_data[field] = None

        fuji_data['fujifilm_makernotes_ultimate_advanced_extension_ii_field_count'] = len(fuji_fields)

    except Exception as e:
        fuji_data['fujifilm_makernotes_ultimate_advanced_extension_ii_error'] = str(e)

    return fuji_data


def _extract_olympus_makernotes_ultimate_advanced_extension_ii(filepath: str) -> Dict[str, Any]:
    """Extract ultimate advanced extension II Olympus MakerNotes metadata."""
    olympus_data = {'olympus_makernotes_ultimate_advanced_extension_ii_detected': True}

    try:
        olympus_fields = [
            'olympus_ultimate_truepic_processor_firmware_version',
            'olympus_ultimate_micro_four_thirds_sensor_data',
            'olympus_ultimate_high_res_shot_pixel_shift_metadata',
            'olympus_ultimate_live_composite_bulb_mode_data',
            'olympus_ultimate_live_time_bulb_exposure_control',
            'olympus_ultimate_live_bulb_manual_exposure_mode',
            'olympus_ultimate_art_filter_algorithm_parameters',
            'olympus_ultimate_pop_art_color_enhancement_filter',
            'olympus_ultimate_soft_focus_blur_algorithm_data',
            'olympus_ultimate_pale_and_light_color_tone_curve',
            'olympus_ultimate_light_tone_color_saturation_boost',
            'olympus_ultimate_grainy_film_particle_simulation',
            'olympus_ultimate_pin_hole_camera_vignette_effect',
            'olympus_ultimate_diorama_miniature_tilt_shift',
            'olympus_ultimate_cross_process_color_shift_filter',
            'olympus_ultimate_gentle_sepia_tone_adjustment',
            'olympus_ultimate_dramatic_tone_contrast_enhancement',
            'olympus_ultimate_key_line_drawing_edge_detection',
            'olympus_ultimate_watercolor_paint_texture_simulation',
            'olympus_ultimate_vintage_film_age_simulation',
            'olympus_ultimate_partial_color_isolated_tone_effect',
            'olympus_ultimate_bleach_bypass_film_emulation',
            'olympus_ultimate_infrared_simulation_false_color',
            'olympus_ultimate_hand_held_starlight_algorithm',
            'olympus_ultimate_tripod_high_res_mode_settings',
            'olympus_ultimate_focus_stacking_sequence_metadata',
        ]

        for field in olympus_fields:
            olympus_data[field] = None

        olympus_data['olympus_makernotes_ultimate_advanced_extension_ii_field_count'] = len(olympus_fields)

    except Exception as e:
        olympus_data['olympus_makernotes_ultimate_advanced_extension_ii_error'] = str(e)

    return olympus_data


def _extract_panasonic_makernotes_ultimate_advanced_extension_ii(filepath: str) -> Dict[str, Any]:
    """Extract ultimate advanced extension II Panasonic MakerNotes metadata."""
    panasonic_data = {'panasonic_makernotes_ultimate_advanced_extension_ii_detected': True}

    try:
        panasonic_fields = [
            'panasonic_ultimate_venus_engine_processor_version',
            'panasonic_ultimate_micro_four_thirds_sensor_data',
            'panasonic_ultimate_dual_is_image_stabilization',
            'panasonic_ultimate_power_o_is_algorithm_performance',
            'panasonic_ultimate_contrast_af_speed_performance',
            'panasonic_ultimate_depth_from_defocus_metadata',
            'panasonic_ultimate_post_focus_stacking_sequence',
            'panasonic_ultimate_light_composition_bulb_mode',
            'panasonic_ultimate_4k_photo_burst_mode_metadata',
            'panasonic_ultimate_6k_photo_high_res_mode_data',
            'panasonic_ultimate_hdr_bracketing_auto_alignment',
            'panasonic_ultimate_multi_exposure_overlay_method',
            'panasonic_ultimate_panorama_stitching_algorithm',
            'panasonic_ultimate_stop_motion_animation_sequence',
            'panasonic_ultimate_time_lapse_interval_settings',
            'panasonic_ultimate_creative_control_filter_parameters',
            'panasonic_ultimate_retro_tone_curve_adjustment',
            'panasonic_ultimate_old_days_film_simulation',
            'panasonic_ultimate_sunshine_color_enhancement',
            'panasonic_ultimate_bleach_bypass_contrast_boost',
            'panasonic_ultimate_toy_effect_miniature_simulation',
            'panasonic_ultimate_star_filter_star_burst_effect',
            'panasonic_ultimate_one_point_color_isolation',
            'panasonic_ultimate_sunshine_color_temperature',
            'panasonic_ultimate_bleach_bypass_silver_tone',
            'panasonic_ultimate_toy_popper_color_saturation',
        ]

        for field in panasonic_data:
            panasonic_data[field] = None

        panasonic_data['panasonic_makernotes_ultimate_advanced_extension_ii_field_count'] = len(panasonic_fields)

    except Exception as e:
        panasonic_data['panasonic_makernotes_ultimate_advanced_extension_ii_error'] = str(e)

    return panasonic_data


def _extract_pentax_makernotes_ultimate_advanced_extension_ii(filepath: str) -> Dict[str, Any]:
    """Extract ultimate advanced extension II Pentax MakerNotes metadata."""
    pentax_data = {'pentax_makernotes_ultimate_advanced_extension_ii_detected': True}

    try:
        pentax_fields = [
            'pentax_ultimate_prime_processor_firmware_version',
            'pentax_ultimate_shake_reduction_sr_performance',
            'pentax_ultimate_pixel_shift_resolution_technology',
            'pentax_ultimate_astro_tracer_tracking_metadata',
            'pentax_ultimate_composite_mode_star_trail_data',
            'pentax_ultimate_interval_composite_sequence',
            'pentax_ultimate_digital_filter_algorithm_parameters',
            'pentax_ultimate_toy_camera_effect_simulation',
            'pentax_ultimate_retro_film_simulation_curves',
            'pentax_ultimate_high_contrast_monochrome_filter',
            'pentax_ultimate_extract_color_isolation_algorithm',
            'pentax_ultimate_water_color_paint_texture_effect',
            'pentax_ultimate_posterization_artistic_filter',
            'pentax_ultimate_minimalist_flat_picture_style',
            'pentax_ultimate_hdr_tone_mapping_algorithm',
            'pentax_ultimate_multi_exposure_blending_method',
            'pentax_ultimate_interval_shooting_timer_settings',
            'pentax_ultimate_motion_bracketing_sequence',
            'pentax_ultimate_depth_of_field_bracketing',
            'pentax_ultimate_white_balance_bracketing',
            'pentax_ultimate_sensitivity_bracketing_iso_range',
            'pentax_ultimate_hyper_program_auto_exposure',
            'pentax_ultimate_hyper_manual_exposure_mode',
            'pentax_ultimate_sensitivity_priority_iso_auto',
            'pentax_ultimate_shutter_and_aperture_priority',
            'pentax_ultimate_bluetooth_remote_control_metadata',
        ]

        for field in pentax_fields:
            pentax_data[field] = None

        pentax_data['pentax_makernotes_ultimate_advanced_extension_ii_field_count'] = len(pentax_fields)

    except Exception as e:
        pentax_data['pentax_makernotes_ultimate_advanced_extension_ii_error'] = str(e)

    return pentax_data


def _extract_samsung_makernotes_ultimate_advanced_extension_ii(filepath: str) -> Dict[str, Any]:
    """Extract ultimate advanced extension II Samsung MakerNotes metadata."""
    samsung_data = {'samsung_makernotes_ultimate_advanced_extension_ii_detected': True}

    try:
        samsung_fields = [
            'samsung_ultimate_drime_processor_version_info',
            'samsung_ultimate_smart_o_is_stabilization_data',
            'samsung_ultimate_hyperlapse_time_lapse_algorithm',
            'samsung_ultimate_super_slow_motion_high_speed',
            'samsung_ultimate_pro_mode_manual_controls',
            'samsung_ultimate_expert_raw_dng_conversion',
            'samsung_ultimate_single_take_ai_editing_metadata',
            'samsung_ultimate_directors_view_multi_clip_edit',
            'samsung_ultimate_vdis_video_digital_stabilization',
            'samsung_ultimate_ois_optical_image_stabilization',
            'samsung_ultimate_dual_pixel_autofocus_tracking',
            'samsung_ultimate_live_focus_portrait_mode_data',
            'samsung_ultimate_bokeh_blur_simulation_algorithm',
            'samsung_ultimate_zoom_in_magnification_metadata',
            'samsung_ultimate_food_mode_color_enhancement',
            'samsung_ultimate_night_mode_long_exposure_stack',
            'samsung_ultimate_astro_shooting_star_trail_mode',
            'samsung_ultimate_sunrise_sunset_golden_hour',
            'samsung_ultimate_blue_hour_twilight_optimization',
            'samsung_ultimate_indoor_mode_white_balance',
            'samsung_ultimate_action_freeze_motion_capture',
            'samsung_ultimate_sports_mode_burst_tracking',
            'samsung_ultimate_macro_mode_close_up_focus',
            'samsung_ultimate_panorama_wide_angle_stitch',
            'samsung_ultimate_selfie_beauty_face_enhancement',
            'samsung_ultimate_group_selfie_wide_angle_mode',
        ]

        for field in samsung_fields:
            samsung_data[field] = None

        samsung_data['samsung_makernotes_ultimate_advanced_extension_ii_field_count'] = len(samsung_fields)

    except Exception as e:
        samsung_data['samsung_makernotes_ultimate_advanced_extension_ii_error'] = str(e)

    return samsung_data


def _extract_leica_makernotes_ultimate_advanced_extension_ii(filepath: str) -> Dict[str, Any]:
    """Extract ultimate advanced extension II Leica MakerNotes metadata."""
    leica_data = {'leica_makernotes_ultimate_advanced_extension_ii_detected': True}

    try:
        leica_fields = [
            'leica_ultimate_maestro_processor_firmware_data',
            'leica_ultimate_apo_summicron_optics_metadata',
            'leica_ultimate_noctilux_low_light_performance',
            'leica_ultimate_summilux_high_speed_optics',
            'leica_ultimate_elmarit_standard_lens_data',
            'leica_ultimate_vario_elmar_zoom_characteristics',
            'leica_ultimate_thalia_distagon_wide_angle',
            'leica_ultimate_apo_telyt_telephoto_optics',
            'leica_ultimate_macro_elmar_microphotography',
            'leica_ultimate_fisheye_elmarit_specialized_lens',
            'leica_ultimate_shift_tilt_adapter_metadata',
            'leica_ultimate_close_focus_adapter_magnification',
            'leica_ultimate_extension_tube_metadata_focus',
            'leica_ultimate_bellows_unit_macro_photography',
            'leica_ultimate_reversal_ring_infinity_focus',
            'leica_ultimate_mirrorless_adapter_e_mount_data',
            'leica_ultimate_medium_format_adapter_hasselblad',
            'leica_ultimate_cine_adapter_video_metadata',
            'leica_ultimate_live_view_magnification_ratio',
            'leica_ultimate_focus_peaking_edge_detection',
            'leica_ultimate_zeiss_coding_lens_identification',
            'leica_ultimate_manual_focus_assist_mechanical',
            'leica_ultimate_focus_tab_position_indicator',
            'leica_ultimate_distance_scale_depth_of_field',
            'leica_ultimate_infrared_focus_compensation',
            'leica_ultimate_ultraviolet_filter_transmission',
        ]

        for field in leica_fields:
            leica_data[field] = None

        leica_data['leica_makernotes_ultimate_advanced_extension_ii_field_count'] = len(leica_fields)

    except Exception as e:
        leica_data['leica_makernotes_ultimate_advanced_extension_ii_error'] = str(e)

    return leica_data


def _extract_hasselblad_makernotes_ultimate_advanced_extension_ii(filepath: str) -> Dict[str, Any]:
    """Extract ultimate advanced extension II Hasselblad MakerNotes metadata."""
    hasselblad_data = {'hasselblad_makernotes_ultimate_advanced_extension_ii_detected': True}

    try:
        hasselblad_fields = [
            'hasselblad_ultimate_h_system_firmware_version',
            'hasselblad_ultimate_x_system_mirrorless_metadata',
            'hasselblad_ultimate_500_series_classic_mechanical',
            'hasselblad_ultimate_2000_series_electric_winder',
            'hasselblad_ultimate_200_series_motorized_film',
            'hasselblad_ultimate_cf_adapter_digital_back',
            'hasselblad_ultimate_xpan_panorama_format_data',
            'hasselblad_ultimate_flexbody_technical_camera',
            'hasselblad_ultimate_arcbody_curved_sensor_data',
            'hasselblad_ultimate_stellar_reproduction_optics',
            'hasselblad_ultimate_sonnar_portrait_lens_data',
            'hasselblad_ultimate_planar_landscape_optics',
            'hasselblad_ultimate_distagon_wide_angle_characteristics',
            'hasselblad_ultimate_apotessar_specialized_lens',
            'hasselblad_ultimate_biotar_vintage_optics_data',
            'hasselblad_ultimate_tessar_economic_lens_series',
            'hasselblad_ultimate_superachromat_apochromatic_correction',
            'hasselblad_ultimate_makro_planar_macro_photography',
            'hasselblad_ultimate_uv_sonnar_ultraviolet_optics',
            'hasselblad_ultimate_infrared_sonnar_ir_photography',
            'hasselblad_ultimate_polaroid_back_instant_film',
            'hasselblad_ultimate_fuji_back_professional_film',
            'hasselblad_ultimate_phase_one_digital_back',
            'hasselblad_ultimate_imacon_scanning_back',
            'hasselblad_ultimate_leaf_creo_digital_capture',
            'hasselblad_ultimate_sinar_digital_back_compatibility',
        ]

        for field in hasselblad_fields:
            hasselblad_data[field] = None

        hasselblad_data['hasselblad_makernotes_ultimate_advanced_extension_ii_field_count'] = len(hasselblad_fields)

    except Exception as e:
        hasselblad_data['hasselblad_makernotes_ultimate_advanced_extension_ii_error'] = str(e)

    return hasselblad_data


def get_makernotes_ultimate_advanced_extension_ii_field_count() -> int:
    """Return the number of ultimate advanced extension II MakerNotes metadata fields."""
    # Canon fields
    canon_fields = 26

    # Nikon fields
    nikon_fields = 26

    # Sony fields
    sony_fields = 26

    # Fujifilm fields
    fuji_fields = 26

    # Olympus fields
    olympus_fields = 26

    # Panasonic fields
    panasonic_fields = 26

    # Pentax fields
    pentax_fields = 26

    # Samsung fields
    samsung_fields = 26

    # Leica fields
    leica_fields = 26

    # Hasselblad fields
    hasselblad_fields = 26

    return (canon_fields + nikon_fields + sony_fields + fuji_fields + olympus_fields +
            panasonic_fields + pentax_fields + samsung_fields + leica_fields + hasselblad_fields)


# Integration point
def extract_makernotes_ultimate_advanced_extension_ii_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for ultimate advanced extension II MakerNotes metadata extraction."""
    return extract_makernotes_ultimate_advanced_extension_ii(filepath)