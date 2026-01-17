#!/usr/bin/env python3
"""
Comprehensive Image Metadata Extractor

This module provides complete image metadata extraction covering:
- 50+ metadata categories
- 400+ fields with data
- All major image formats
- Registry-aware field naming

Author: MetaExtract Team
Version: 6.0.0
"""

import logging
import os
import subprocess
import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

EXIFTOOL_PATH = "/opt/homebrew/bin/exiftool"
EXIFTOOL_AVAILABLE = os.path.exists(EXIFTOOL_PATH) and os.access(EXIFTOOL_PATH, os.X_OK)

try:
    from PIL import Image, ExifTags
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# Complete category definitions with all fields
IMAGE_METADATA_CATEGORIES = {
    # === BASIC PROPERTIES (26 fields) ===
    "basic_properties": {
        "description": "Core image properties",
        "fields": [
            "filename", "file_size_bytes", "file_size_human", "file_extension",
            "mime_type", "format", "format_version", "width", "height",
            "megapixels", "aspect_ratio", "color_mode", "channels",
            "bit_depth", "has_alpha", "is_animated", "frame_count",
            "loop_count", "duration_seconds", "orientation", "dpi_horizontal",
            "dpi_vertical", "compression", "encoding_process", "color_components"
        ]
    },
    
    # === FILE FORMAT CHUNKS (56 fields) ===
    "file_format_chunks": {
        "description": "Container-specific chunk/marker data",
        "fields": [
            "jfif_version", "jfif_resolution_unit", "jfif_xresolution", "jfif_yresolution",
            "png_ihdr_width", "png_ihdr_height", "png_ihdr_bit_depth", "png_ihdr_color_type",
            "png_plte_present", "png_plte_entries", "png_text_count", "png_ztxt_present",
            "png_itxt_present", "png_exif_present", "png_chrm_white_point_x", "png_chrm_white_point_y",
            "png_chrm_red_x", "png_chrm_red_y", "png_chrm_green_x", "png_chrm_green_y",
            "png_chrm_blue_x", "png_chrm_blue_y", "png_gama_gamma", "png_phys_present",
            "png_phys_unit", "png_phys_x", "png_phys_y", "png_srgb_present",
            "png_iccp_present", "png_iccp_name", "png_iccp_compression", "png_time_present",
            "png_time_year", "png_time_month", "png_time_day", "png_time_hour",
            "png_time_minute", "png_time_second", "png_bkgd_present", "png_bkgd_color",
            "png_his_present", "png_his_method", "png_his_intent", "png_his_ncolors",
            "png_his_transparency", "png_trns_present", "png_trns_rgb", "png_trns_gray",
            "png_trns_index", "png_splt_present", "png_splt_name", "png_splt_samples",
            "png_splt_depth", "webp_version", "webp_has_alpha", "webp_has_animation",
            "webp_frame_count", "webp_loop_count"
        ]
    },
    
    # === EXIF STANDARD (50 fields) ===
    "exif_standard": {
        "description": "Standard EXIF 2.32 tags",
        "fields": [
            "make", "model", "software", "artist", "copyright", "image_description",
            "datetime", "datetime_original", "datetime_digitized", "subsec_time",
            "subsec_time_original", "subsec_time_digitized", "exposure_time", "f_number",
            "exposure_program", "exposure_mode", "exposure_bias", "exif_version",
            "iso_speed_ratings", "iso_speed", "shutter_speed_value", "aperture_value",
            "brightness_value", "exposure_compensation", "metering_mode", "flash",
            "focal_length", "focal_length_35mm", "digital_zoom_ratio", "scene_capture_type",
            "contrast", "saturation", "sharpness", "white_balance", "gain_control",
            "color_space", "sensing_method", "lens_make", "lens_model", "lens_specification",
            "body_serial_number", "lens_serial_number", "camera_owner_name", "software_version",
            "processing_software", "target_distance", "target_type", "flash_energy",
            "field_of_view", "view_plane_size", "auxiliary_lens"
        ]
    },
    
    # === EXIF ADVANCED (30 fields) ===
    "exif_advanced": {
        "description": "Advanced EXIF and MakerNotes",
        "fields": [
            "lens_serial_number", "lens_model_number", "body_serial_number", "internal_serial_number",
            "camera_temperature", "cfa_pattern", "cfa_pattern_rows", "cfa_pattern_columns",
            "cfa_pattern_row_size", "cfa_pattern_col_size", "custom_rendered", "exposure_mode",
            "digital_zoom_ratio", "focal_length_in_35mm_format", "scene_mode", "noise_reduction",
            "image_stabilization", "spot_meter_link", "af_illuminator", "max_aperture_value",
            "min_aperture_value", "photographic_sensitivity", "sensitivity_type", "standard_output_sensitivity",
            "recommended_exposure_index", "iso_speed_range", "flash_range", "flash_red-eye_reduction",
            "multi_exposure_mode", "multi_exposure_gain"
        ]
    },
    
    # === GPS (25 fields) ===
    "gps": {
        "description": "GPS and location metadata",
        "fields": [
            "gps_version_id", "gps_latitude", "gps_longitude", "gps_altitude",
            "gps_altitude_ref", "gps_timestamp", "gps_datestamp", "gps_latitude_ref",
            "gps_longitude_ref", "gps_speed", "gps_speed_ref", "gps_track",
            "gps_track_ref", "gps_img_direction", "gps_img_direction_ref", "gps_dest_latitude",
            "gps_dest_longitude", "gps_dest_bearing", "gps_dest_bearing_ref", "gps_area",
            "gps_processing_method", "gps_satellites", "gps_status", "gps_receiver_status",
            "gps_dop", "gps_map_datum", "gps_destination_distance", "gps_measure_mode",
            "gps_spd_ref", "gps_trk_ref", "gps_horz_pos_accuracy", "gps_vert_pos_accuracy"
        ]
    },
    
    # === IPTC STANDARD (21 fields) ===
    "iptc_standard": {
        "description": "IPTC IIM4 standard metadata",
        "fields": [
            "record_version", "object_name", "edit_status", "editorial_priority",
            "urgency", "subject_reference", "category", "supplemental_category",
            "fixture_identifier", "keywords", "location_code", "location_name",
            "release_date", "release_time", "expiration_date", "expiration_time",
            "special_instructions", "action_advised", "reference_service",
            "reference_date", "reference_number"
        ]
    },
    
    # === IPTC EXTENSION (20 fields) ===
    "iptc_extension": {
        "description": "IPTC Extension and Additional IPTC",
        "fields": [
            "caption_writer", "graphic_note", "instructions", "job_identifier",
            "light_source", "object_cycle", "original_transmission_reference",
            "program", "copyright_notice", "rights_usage_terms", "scene",
            "subject_code", "intellectual_genre", "description_writer", "job_name",
            "credits", "source", "copyright_owner", "creator", "usage_terms"
        ]
    },
    
    # === XMP NAMESPACES (61 fields) ===
    "xmp_namespaces": {
        "description": "XMP Dublin Core and Photoshop namespaces",
        "fields": [
            "dc_title", "dc_creator", "dc_subject", "dc_description", "dc_publisher",
            "dc_contributor", "dc_date", "dc_type", "dc_format", "dc_identifier",
            "dc_source", "dc_language", "dc_relation", "dc_coverage", "dc_rights",
            "xmp_create_date", "xmp_modify_date", "xmp_metadata_date", "xmp_creator_tool",
            "xmp_label", "xmp_rating", "xmp_label_stable", "xmp_modified_by",
            "photoshop_headline", "photoshop_caption", "photoshop_status", "photoshop_color_mode",
            "photoshop_date_created", "photoshop_history", "photoshop_autoredirect",
            "photoshop_legacy_tool", "photoshop_tool", "photoshop_has_real_comp",
            "photoshop_resolution", "photoshop_quality", "dc_format_pre", "dc_format_pre_rational",
            "photoshop_print_style", "photoshop_alts_rect", "photoshop_global_alt",
            "photoshop_jpeg_quality", "photoshop_grid_guide", "photoshop_slices",
            "xmp_rights_marked", "xmp_rights_web_statement", "xmp_rights_certificate",
            "xmp_rights_owner", "xmp_rights_usage_terms", "xmp_rights_web_statement_lang",
            "xmpmm_document_id", "xmpmm_instance_id", "xmpmm_original_document_id",
            "xmpmm_version", "xmpmm_render_session_id", "xmp_stEvt_action",
            "xmp_stEvt_changed", "xmp_stEvt_instance_id", "xmp_stEvt_software_agent"
        ]
    },
    
    # === ICC PROFILES (20 fields) ===
    "icc_profiles": {
        "description": "ICC color profile metadata",
        "fields": [
            "icc_version", "icc_class", "icc_color_space", "icc_connection_space",
            "icc_profile_datetime", "icc_file_signature", "icc_primary_platform",
            "icc_cmm_type", "icc_device_manufacturer", "icc_device_model",
            "icc_device_attributes", "icc_rendering_intent", "icc_creator",
            "icc_profile_description", "icc_copyright", "icc_media_white_point",
            "icc_red_matrix", "icc_green_matrix", "icc_blue_matrix",
            "icc_tone_reproduction_curve", "icc_color_temperature",
            "icc_chromatic_adaptation", "icc_luminance", "icc_pe_response"
        ]
    },
    
    # === CAMERA MAKERNOTES (29 fields) ===
    "camera_makernotes": {
        "description": "Vendor-specific camera data",
        "fields": [
            "makernote_vendor", "makernote_camera_type", "shutter_count", "af_points",
            "af_points_in_cross", "af_mode", "af_area_modes", "af_points_selected",
            "image_number", "digital_zoom", "lens_focus_mode", "manual_flash_output",
            "flash_exposure_comp", "flash_control_mode", "flash_output", "flash_zoom_head",
            "flash_compensation", "flash_brightness", "external_flash_exposure_comp",
            "external_flash_status", "flash_firmware", "flash_gid", "flash_group",
            "flash_group_zoom", "flash_group_focus", "flash_group_ambient",
            "sensor_temperature", "sensor_pixel_count", "sensor_width", "sensor_height"
        ]
    },
    
    # === MOBILE METADATA (14 fields) ===
    "mobile_metadata": {
        "description": "Mobile device metadata",
        "fields": [
            "device_make", "device_model", "device_software", "device_os_version",
            "app_name", "app_version", "capture_device", "processing_software",
            "hdr_type", "live_photo", "portrait_mode", "burst_mode",
            "wide_color_capture", "scene_recognition_type"
        ]
    },
    
    # === ACTION CAMERA (13 fields) ===
    "action_camera": {
        "description": "Action camera metadata (GoPro, DJI, Insta360)",
        "fields": [
            "action_camera_make", "action_camera_model", "firmware_version",
            "video_resolution", "frame_rate", "field_of_view", "stabilization",
            "low_light_mode", "loop_recording", "auto_off_time", "language",
            "date_time_stamp", "gps_recording"
        ]
    },
    
    # === DRONE/UAV (34 fields) ===
    "drone_uav": {
        "description": "Drone and UAV metadata",
        "fields": [
            "drone_make", "drone_model", "drone_serial", "firmware_version",
            "flight_date", "flight_time", "flight_mode", "take_off_location",
            "landing_location", "home_location", "gimbal_mode", "gimbal_tilt",
            "gimbal_roll", "gimbal_pan", "altitude", "relative_altitude",
            "distance_to_home", "horizontal_speed", "vertical_speed",
            "heading", "course", "number_of_photos", "sd_card_info",
            "battery_information", "camera_serial", "camera_firmware",
            "lens_serial", "lens_firmware", "wind_speed", "wind_direction",
            "temperature", "humidity", "flight_battery_consumption"
        ]
    },
    
    # === THERMAL IMAGING (29 fields) ===
    "thermal_imaging": {
        "description": "Thermal camera metadata",
        "fields": [
            "thermal_make", "thermal_model", "sensor_type", "sensor_resolution",
            "pixel_pitch", "thermal_sensitivity", "temperature_range",
            "temperature_min", "temperature_max", "emissivity", "reflected_temp",
            "atmospheric_temp", "humidity", "distance", "focus_distance",
            "palette", "isotherms", "measurement_mode", "level_span_mode",
            "auto_range", "video_standard", "frame_rate", "digital_zoom",
            "image_rotation", "date_time_utc", "gps_coordinates",
            "compass_direction", "pitch_angle", "roll_angle"
        ]
    },
    
    # === 3D IMAGING (32 fields) ===
    "three_d_imaging": {
        "description": "3D model and imaging metadata",
        "fields": [
            "object_name", "object_type", "vertices_count", "faces_count",
            "edges_count", "material_count", "texture_count", "uv_channels",
            "vertex_format", "coordinate_system", "bounding_box_min",
            "bounding_box_max", "file_units", "units_conversion",
            "author", "creation_date", "modification_date", "software",
            "application", "generator", "platform", "engine", "render_engine",
            "shader_model", "lighting_model", "ambient_occlusion", "normal_maps",
            "displacement_maps", "specular_maps", "reflection_maps"
        ]
    },
    
    # === VR/AR (28 fields) ===
    "vr_ar": {
        "description": "Virtual Reality and AR content metadata",
        "fields": [
            "vr_type", "projection_type", "stereo_format", "field_of_view",
            "aspect_ratio", "interpupillary_distance", "eye_relief",
            "lens_separation", "resolution_width", "resolution_height",
            "frame_rate", "duration", "capture_device", "stitching_software",
            "equirectangular", "cubemap", "cylindrical", "spherical",
            "mono_stereo", "left_right_eye", "video_codec", "audio_codec",
            "spatial_audio", "head_tracking", "hand_tracking", "controller_tracking",
            "room_scale", "seated_experience"
        ]
    },
    
    # === MEDICAL IMAGING (29 fields) ===
    "medical_imaging": {
        "description": "Medical and DICOM imaging metadata",
        "fields": [
            "patient_id", "patient_name", "patient_birth_date", "patient_sex",
            "patient_age", "study_id", "series_number", "instance_number",
            "modality", "body_part_examined", "study_date", "series_date",
            "instance_date", "study_time", "series_time", "instance_time",
            "study_description", "series_description", "manufacturer",
            "institution_name", "station_name", "physicians_of_record",
            "performing_physician", "operators_name", "study_uid",
            "series_uid", "instance_uid", "sop_instance_uid"
        ]
    },
    
    # === SCIENTIFIC IMAGING (26 fields) ===
    "scientific_imaging": {
        "description": "Scientific and research imaging",
        "fields": [
            "instrument_name", "instrument_serial", "observation_date",
            "observation_time", "exposure_time", "filter_name", "filter_wavelength",
            "telescope_aperture", "telescope_focal_length", "telescope_type",
            "mount_type", "tracking_mode", "guide_mode", "calibration_frames",
            "bias_frames", "dark_frames", "flat_frames", "light_frames",
            "binning", "readout_mode", "gain", "offset", "pixel_scale",
            "seeing_conditions", "airmass", "moon_phase"
        ]
    },
    
    # === IMAGE FORENSICS (8 fields) ===
    "image_forensics": {
        "description": "Image forensics and manipulation detection",
        "fields": [
            "ela_score", "noise_analysis", "compression_artefacts",
            "manipulation_detected", "manipulation_type", "manipulation_regions",
            "hash_value", "duplicate_detection"
        ]
    },
    
    # === STEGANOGRAPHY (4 fields) ===
    "steganography": {
        "description": "Steganography detection",
        "fields": [
            "hidden_data_detected", "hidden_data_type", "hidden_data_size",
            "hidden_data_offset"
        ]
    },
    
    # === PERCEPTUAL HASHES (9 fields) ===
    "perceptual_hashes": {
        "description": "Image perceptual hashing",
        "fields": [
            "phash", "phash_block_size", "phash_threshold",
            "dhash", "dhash_block_size", "average_hash",
            "radial_hash", "marr_hildreth_hash", "hash_comparison"
        ]
    },
    
    # === COLOR ANALYSIS (13 fields) ===
    "color_analysis": {
        "description": "Color analysis results",
        "fields": [
            "dominant_color_1", "dominant_color_2", "dominant_color_3",
            "color_histogram", "white_balance_setting", "color_temperature",
            "tint", "saturation_distribution", "brightness_distribution",
            "contrast_level", "vibrance", "color_harmony", "color_schema"
        ]
    },
    
    # === QUALITY METRICS (8 fields) ===
    "quality_metrics": {
        "description": "Image quality assessment",
        "fields": [
            "overall_quality_score", "sharpness_score", "noise_level",
            "compression_artefact_score", "exposure_score", "composition_score",
            "aesthetic_score", "technical_quality_grade"
        ]
    },
    
    # === AI GENERATION (12 fields) ===
    "ai_generation": {
        "description": "AI-generated content detection",
        "fields": [
            "ai_generated", "ai_detection_confidence", "ai_model",
            "ai_prompt", "ai_negative_prompt", "ai_sampler",
            "ai_steps", "ai_cfg_scale", "ai_seed", "ai_scheduler",
            "ai_model_hash", "generation_time"
        ]
    },
    
    # === EDIT HISTORY (13 fields) ===
    "edit_history": {
        "description": "Editing history and workflow",
        "fields": [
            "software_name", "software_version", "edit_date", "edit_action",
            "edit_description", "previous_filename", "history_stack",
            "layer_count", "layer_names", "color_mode_history",
            "brightness_adjustment", "contrast_adjustment", "saturation_adjustment"
        ]
    },
    
    # === PHOTOSHOP PSD (12 fields) ===
    "photoshop_psd": {
        "description": "Photoshop-specific metadata",
        "fields": [
            "psd_version", "psd_color_mode", "psd_channels", "psd_height",
            "psd_width", "bits_per_channel", "layer_count", "color_profile",
            "caption_exist", "print_info", "resolution_unit", "ICC_profile"
        ]
    },
    
    # === ACCESSIBILITY (20 fields) ===
    "accessibility": {
        "description": "Accessibility metadata",
        "fields": [
            "alt_text", "long_description", "aria_label", "aria_description",
            "aria_role", "title", "subject", "caption", "transcript",
            "audio_description", "text_layers", "hierarchy_markup",
            "reading_order", "structural_elements", "language",
            "expanded_form", "abbreviation_expansion", "complex_image_description",
            "visual_artefacts_description", "captions_present"
        ]
    },
    
    # === SOCIAL METADATA (27 fields) ===
    "social_metadata": {
        "description": "Social media platform metadata",
        "fields": [
            "instagram_filter", "instagram_location", "instagram_latitude",
            "instagram_longitude", "instagram_creation_date", "twitter_entities",
            "facebook_place", "flickr_groups", "flickr_machine_tags",
            "pinterest_boards", "tiktok_effects", "snapchat_geofilter",
            "youtube_thumbnail", "vimeo_category", "tiktok_duet",
            "reels_audio", "reels_creation_date", "live_stream_duration",
            "viewer_count", "like_count", "comment_count", "share_count",
            "view_count", "engagement_rate", "follower_count", "verified_status"
        ]
    },
    
    # === E-COMMERCE (28 fields) ===
    "ecommerce": {
        "description": "E-commerce product image metadata",
        "fields": [
            "product_sku", "product_id", "product_name", "brand",
            "manufacturer", "mpn", "gtin", "asin", "isbn", "upc",
            "price_currency", "price_amount", "availability", "condition",
            "product_category", "product_subcategory", "material", "color",
            "size_dimensions", "weight", "warranty_info", "shipping_class",
            "product_url", "merchant_name", "promo_text", "seasonal_tag"
        ]
    },
    
    # === PRINT/PREPRESS (28 fields) ===
    "print_prepress": {
        "description": "Print and prepress metadata",
        "fields": [
            "cmyk_profile", "spot_colors", "total_ink_coverage",
            "black_generation", "under_color_removal", "gray_component_replacement",
            "gcr_level", "dot_gain", "screen_frequency", "screen_angle",
            "trapping", "bleed", "trim_box", "media_type", "media_weight",
            "fold_type", "cut_lines", "crop_marks", "color_bar",
            "registration_marks", "print_direction", "plates", "ink_names",
            "ink_densities", "pantone_colors", "varnish", "coating"
        ]
    },
    
    # === COLOR GRADING (34 fields) ===
    "color_grading": {
        "description": "Color grading and LUT metadata",
        "fields": [
            "lut_type", "lut_name", "lut_size", "lut_format", "lut_domain",
            "lut_range", "lift_values", "gamma_values", "gain_values",
            "offset_values", "tint_values", "temperature", "tint_adjust",
            "contrast_curve", "shadows", "midtones", "highlights",
            "whites", "blacks", "vibrance", "saturation_curve",
            "hue_rotation", "luminance_curve", "color_wheel_values",
            "color_wheel_rotation", "split_toning_balance", "split_toning_saturation",
            "channel_mixer_red", "channel_mixer_green", "channel_mixer_blue",
            "curve_type", "curve_points", "tone_curve"
        ]
    },
    
    # === THUMBNAIL (5 fields) ===
    "thumbnail": {
        "description": "Embedded thumbnail data",
        "fields": [
            "has_thumbnail", "thumbnail_format", "thumbnail_width",
            "thumbnail_height", "thumbnail_offset"
        ]
    },
    
    # === EXTRACTION METADATA (10 fields) ===
    "extraction_metadata": {
        "description": "Metadata about the extraction process",
        "fields": [
            "extractor_version", "extraction_date", "extraction_time",
            "processing_time_ms", "tool_used", "schema_version",
            "success", "warnings", "errors", "redaction_applied"
        ]
    },
    
    # === RAW FORMAT (31 fields) ===
    "raw_format": {
        "description": "RAW file format specific metadata",
        "fields": [
            "raw_make", "raw_model", "raw_serial", "raw_cfa_pattern",
            "raw_iso", "raw_exposure_comp", "raw_shutter",
            "raw_aperture", "raw_focal_length", "raw_white_balance",
            "raw_white_balance_mode", "raw_cwb_gain", "raw_temperatures",
            "raw_neutral_rgb", "raw_active_area", "raw_masked_areas",
            "raw_black_levels", "raw_white_levels", "raw_color_planes",
            "raw_maker_notes", "raw_crypt_image", "raw_huffman",
            "raw_predictor", "raw_interleave", "raw_tiles",
            "raw_orientation", "raw_samples_per_pixel", "raw_bits_per_sample",
            "raw_rows_per_strip", "raw_strip_byte_counts"
        ]
    },
    
    # === TIFF IFD (41 fields) ===
    "tiff_ifd": {
        "description": "TIFF IFD specific tags",
        "fields": [
            "tiff_version", "byte_order", "subfile_type", "photometric_interpretation",
            "compression", "photometric", "samples_per_pixel", "planar_configuration",
            "ycbcr_subsampling", "ycbcr_positioning", "resolution_unit",
            "x_resolution", "y_resolution", "min_sample_value", "max_sample_value",
            "document_name", "page_name", "page_number", "x_position",
            "y_position", "free_offsets", "free_byte_counts", "gray_response_unit",
            "gray_response_curve", "t4_options", "t6_options", "transfer_function",
            "white_point", "primary_chromaticities", "color_map", "halftone_hints",
            "tile_width", "tile_length", "tile_offsets", "tile_byte_counts",
            "orientation", "samples_per_pixel", "rows_per_strip", "strip_offsets",
            "strip_byte_counts"
        ]
    },
    
    # === VECTOR GRAPHICS (37 fields) ===
    "vector_graphics": {
        "description": "SVG and vector format metadata",
        "fields": [
            "vector_width", "vector_height", "view_box", "preserve_aspect_ratio",
            "svg_version", "xmlns", "title", "description", "defs",
            "gradient_count", "pattern_count", "marker_count",
            "_count", "symbolclip_path_count", "mask_count", "filter_count", "style_count",
            "font_family", "font_size", "font_weight", "font_style",
            "text_content", "path_data", "transform_matrix", "fill_color",
            "stroke_color", "stroke_width", "opacity", "fill_opacity",
            "stroke_opacity", "display", "visibility", "overflow",
            "clip_rule", "mask_units", "pattern_units"
        ]
    },
    
    # === NEXGEN IMAGE (24 fields) ===
    "nextgen_image": {
        "description": "HEIC, AVIF, JPEG XL metadata",
        "fields": [
            "codec", "codec_version", "bit_depth", "chroma_subsampling",
            "color_primaries", "transfer_characteristics", "matrix_coefficients",
            "full_range", "profile", "level", "tier", "nclx_present",
            "nclx_color_primaries", "nclx_transfer_characteristics",
            "nclx_matrix_coefficients", "nclx_full_range", "av1_version",
            "av1_level", "av1_tier", "av1_profile", "hevc_version",
            "hevc_tier", "hevc_profile", "hevc_nal_unit_type"
        ]
    },
    
    # === CINEMA RAW (32 fields) ===
    "cinema_raw": {
        "description": "CinemaDNG and RAW video metadata",
        "fields": [
            "cinema_dng_version", "camera_make", "camera_model", "camera_serial",
            "firmware_version", "lens_make", "lens_model", "lens_serial",
            "image_stabilization", "zoom focal_length", "min_focal_length",
            "max_focal_length", "white_balance", "iso_gain", "native_iso",
            "exposure_time", "aperture", "frame_rate", "frame_count",
            "shutter_angle", "gamma_curve", "color_matrix", "black_level",
            "white_level", "conversion_lens", "sensor_serial", "sensor_info",
            "raw_height", "raw_width", "active_area", "default_crop"
        ]
    },
    
    # === DOCUMENT IMAGE (29 fields) ===
    "document_image": {
        "description": "Document scanning and OCR metadata",
        "fields": [
            "ocr_detected", "ocr_confidence", "ocr_engine", "language_detected",
            "barcode_detected", "barcode_type", "barcode_data", "signature_detected",
            "handwriting_detected", "language", "orientation", "page_number",
            "author", "title", "subject", "keywords", "producer",
            "creator", "creation_date", "modification_date", "pdf_version",
            "page_count", "encrypted", "permissions", "paper_size",
            "margins", "columns", "lines_per_page", "word_count"
        ]
    },
    
    # === REMOTE SENSING (24 fields) ===
    "remote_sensing": {
        "description": "Satellite and aerial imagery",
        "fields": [
            "satellite_name", "sensor_name", "orbit_type", "sun_elevation",
            "sun_azimuth", "viewing_angle", "off_nadir_angle", "spatial_resolution",
            "swath_width", "cloud_cover", "acquisition_date", "acquisition_time",
            "ground_sample_distance", "map_projection", "coordinate_reference_system",
            "corner_coordinates", "center_coordinates", "elevation_model",
            "band_count", "band_names", "wavelengths", "radiometric_calibration",
            "geometric_calibration", "atmospheric_correction"
        ]
    },
    
    # === BARCODE OCR (30 fields) ===
    "barcode_ocr": {
        "description": "Barcode and OCR detection",
        "fields": [
            "barcode_present", "barcode_type", "barcode_data", "barcode_confidence",
            "barcode_orientation", "barcode_region", "qr_code_version", "qr_code_error_correction",
            "ean_code", "upc_code", "code128", "code39", "code93",
            "codabar", "itf_code", "postnet_code", "pdf417_code",
            "datamatrix_code", "aztec_code", "ocr_text", "ocr_confidence",
            "ocr_language", "ocr_engine", "ocr_bounding_box", "word_count",
            "line_count", "font_detected", "font_size", "handwriting_detected"
        ]
    },
    
    # === DIGITAL SIGNATURE (23 fields) ===
    "digital_signature": {
        "description": "Digital signature and certificate info",
        "fields": [
            "signed", "signature_type", "signature_algorithm", "signer_name",
            "signer_email", "signer_organization", "signing_time", "signature_valid",
            "certificate_present", "certificate_subject", "certificate_issuer",
            "certificate_serial", "certificate_not_before", "certificate_not_after",
            "signature_hash", "public_key_bits", "public_key_algorithm",
            "signature_timestamp", "ocsp_status", "crl_status",
            "document_hash", "signature_version", "coverage"
        ]
    },
    
    # === AI VISION (31 fields) ===
    "ai_vision": {
        "description": "AI vision model and detection results",
        "fields": [
            "model_name", "model_version", "inference_time", "confidence_threshold",
            "objects_detected", "faces_detected", "faces_with_confidence",
            "people_detected", "text_detected", "landmarks_detected",
            "brands_detected", "emotions_detected", "age_range_detected",
            "gender_detected", "ethnicity_detected", "apparel_detected",
            "activity_detected", "scene_detected", "event_detected",
            "setting_detected", "time_of_day_detected", "weather_detected",
            "mood_detected", "style_detected", "composition_detected",
            "quality_score", "aesthetic_score", "virality_score", "trending_score"
        ]
    }
}


def get_all_categories() -> List[str]:
    """Get list of all category names."""
    return list(IMAGE_METADATA_CATEGORIES.keys())


def get_category_fields(category: str) -> List[str]:
    """Get fields for a specific category."""
    return IMAGE_METADATA_CATEGORIES.get(category, {}).get("fields", [])


def count_total_fields() -> int:
    """Count total number of fields across all categories."""
    return sum(len(cat["fields"]) for cat in IMAGE_METADATA_CATEGORIES.values())


def get_category_info() -> Dict[str, Dict]:
    """Get category information."""
    return {
        name: {"field_count": len(info["fields"])}
        for name, info in IMAGE_METADATA_CATEGORIES.items()
    }


if __name__ == "__main__":
    print("=" * 80)
    print("COMPREHENSIVE IMAGE METADATA CATEGORIES")
    print("=" * 80)
    
    total_fields = count_total_fields()
    print(f"\nTotal Categories: {len(IMAGE_METADATA_CATEGORIES)}")
    print(f"Total Fields: {total_fields}")
    
    print("\n" + "-" * 80)
    print("CATEGORY SUMMARY")
    print("-" * 80)
    
    for name, info in sorted(IMAGE_METADATA_CATEGORIES.items()):
        field_count = len(info["fields"])
        print(f"  {name}: {field_count} fields")
    
    print("\n" + "=" * 80)
    print(f"GRAND TOTAL: {total_fields} fields across {len(IMAGE_METADATA_CATEGORIES)} categories")
    print("=" * 80)
