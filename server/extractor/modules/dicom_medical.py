"""
Complete DICOM Medical Imaging Metadata
Comprehensive extraction of DICOM tags for medical imaging forensics
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from .dicom_complete_registry import get_dicom_registry_fields
    DICOM_REGISTRY_FIELDS = get_dicom_registry_fields()
except Exception:
    DICOM_REGISTRY_FIELDS = {}

try:
    from .dicom_private_tags_complete import GE_PRIVATE_TAGS
    DICOM_PRIVATE_REGISTRY = {**GE_PRIVATE_TAGS}
except Exception:
    DICOM_PRIVATE_REGISTRY = {}


DICOM_PATIENT_TAGS = {
    (0x0010, 0x0010): "patient_name",
    (0x0010, 0x0020): "patient_id",
    (0x0010, 0x0030): "patient_birth_date",
    (0x0010, 0x0040): "patient_sex",
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x1040): "patient_address",
    (0x0010, 0x1050): "insurance_plan",
    (0x0010, 0x1060): "patient_telephone_numbers",
    (0x0010, 0x1080): "military_rank",
    (0x0010, 0x1090): "medical_record_locator",
    (0x0010, 0x2000): "medical_alerts",
    (0x0010, 0x2110): "allergies",
    (0x0010, 0x2150): "patient_ethnic_group",
    (0x0010, 0x2160): "patient_religion",
    (0x0010, 0x2180): "patient_pregnancy_status",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x21C0): "patient_state",
    (0x0010, 0x21D0): "last_menstrual_date",
    (0x0010, 0x21F0): "patient_telephone_numbers_alt",
    (0x0010, 0x2200): "responsible_person",
    (0x0010, 0x2292): "responsible_organization",
    (0x0010, 0x4000): "patient_instructions",
    (0x0010, 0x9431): "patient_comments",
}

DICOM_STUDY_TAGS = {
    (0x0020, 0x000D): "study_instance_uid",
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x0020): "study_date",
    (0x0008, 0x0030): "study_time",
    (0x0008, 0x0050): "accession_number",
    (0x0008, 0x0090): "referring_physician_name",
    (0x0008, 0x0094): "referring_physician_telephone",
    (0x0008, 0x0096): "referring_physician_address",
    (0x0008, 0x0098): "study_id",
    (0x0008, 0x0201): "timezone_offset",
    (0x0020, 0x0010): "study_number",
    (0x0032, 0x000A): "study_status_id",
    (0x0032, 0x000C): "study_priority_id",
    (0x0032, 0x1030): "study_verified_date",
    (0x0032, 0x1031): "study_verified_time",
    (0x0032, 0x1050): "study_read_date",
    (0x0032, 0x1051): "study_read_time",
    (0x0040, 0xA300): "study_completed_date",
    (0x0040, 0xA301): "study_completed_time",
    (0x0040, 0xA307): "study_verified_physician",
    (0x0040, 0xA730): "study_results",
}

DICOM_SERIES_TAGS = {
    (0x0020, 0x000E): "series_instance_uid",
    (0x0008, 0x0060): "modality",
    (0x0020, 0x0011): "series_number",
    (0x0008, 0x103E): "series_description",
    (0x0020, 0x0006): "referenced_frame_number",
    (0x0008, 0x0021): "series_date",
    (0x0008, 0x0031): "series_time",
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0020): "patient_position",
    (0x0018, 0x0021): "sequence_name",
    (0x0018, 0x0024): "sequence_variant",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x0081): "echo_time",
    (0x0018, 0x0082): "inversion_time",
    (0x0018, 0x0083): "number_of_averages",
    (0x0018, 0x0084): "imaging_frequency",
    (0x0018, 0x0085): "echo_number",
    (0x0018, 0x0086): "magnetic_field_strength",
    (0x0018, 0x0087): "spacing_between_slices",
    (0x0018, 0x0088): "number_of_phase_encoding_steps",
    (0x0018, 0x0089): "data_acquisition_dead_time",
    (0x0018, 0x0090): "pixel_bandwidth",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1040): "transmitter_coil",
    (0x0018, 0x1050): "receive_coil",
    (0x0018, 0x1060): "flip_angle",
    (0x0018, 0x1080): "sar",
    (0x0018, 0x1094): "dwi_b_value",
    (0x0018, 0x1095): "dwi_gradient_direction",
    (0x0018, 0x1100): "probe_drive_application",
    (0x0018, 0x1240): "receive_gain",
    (0x0018, 0x1250): "transmit_gain",
    (0x0018, 0x1251): "pre_amp_duty_cycle",
    (0x0018, 0x9004): "contrast_bolus_agent",
    (0x0018, 0x9010): "contrast_bolus_start_time",
    (0x0018, 0x9012): "contrast_bolus_duration",
    (0x0018, 0x9014): "contrast_bolus_stopped",
    (0x0018, 0x9016): "contrast_bolus_administered",
    (0x0018, 0x9018): "contrast_bolus_volume",
    (0x0018, 0x9020): "mr_gradient_moment",
    (0x0020, 0x0037): "image_orientation",
    (0x0020, 0x0050): "slice_location",
    (0x0020, 0x0100): "temporal_position_identifier",
    (0x0020, 0x0105): "number_of_temporal_positions",
    (0x0020, 0x0128): "number_of_frames",
    (0x0020, 0x0013): "instance_number",
}

DICOM_IMAGE_TAGS = {
    (0x0008, 0x0008): "image_type",
    (0x0008, 0x0018): "sop_instance_uid",
    (0x0008, 0x0023): "content_date",
    (0x0008, 0x0033): "content_time",
    (0x0020, 0x0013): "instance_number",
    (0x0028, 0x0002): "samples_per_pixel",
    (0x0028, 0x0004): "photometric_interpretation",
    (0x0028, 0x0006): "planar_configuration",
    (0x0028, 0x0008): "number_of_frames",
    (0x0028, 0x0010): "rows",
    (0x0028, 0x0011): "columns",
    (0x0028, 0x0034): "pixel_aspect_ratio",
    (0x0028, 0x0100): "bits_allocated",
    (0x0028, 0x0101): "bits_stored",
    (0x0028, 0x0102): "high_bit",
    (0x0028, 0x0103): "pixel_representation",
    (0x0028, 0x0106): "smallest_image_pixel_value",
    (0x0028, 0x0107): "largest_image_pixel_value",
    (0x0028, 0x0120): "pixel_padding_value",
    (0x0028, 0x1050): "window_center",
    (0x0028, 0x1051): "window_width",
    (0x0028, 0x1052): "window_center_width_explanation",
    (0x0028, 0x1053): "rescale_intercept",
    (0x0028, 0x1054): "rescale_slope",
    (0x0028, 0x1055): "rescale_type",
    (0x0028, 0x1080): "modalities_in_phantom",
    (0x0028, 0x1090): "pixel_intensity_relationship",
    (0x0028, 0x1091): "pixel_intensity_relationship_sign",
    (0x0028, 0x1100): "calibration_object",
    (0x0028, 0x1101): "calibration_date",
    (0x0028, 0x1102): "calibration_time",
    (0x0028, 0x1200): "foreground_pixel_value",
    (0x0028, 0x1201): "background_pixel_value",
    (0x0028, 0x2000): "icc_profile",
    (0x0028, 0x2110): "lossy_image_compression",
    (0x0028, 0x2112): "lossy_image_compression_ratio",
    (0x0028, 0x2114): "lossy_image_compression_method",
    (0x0028, 0x5000): "polarity",
    (0x0028, 0x6000): "display_window_left",
    (0x0028, 0x6001): "display_window_right",
    (0x0028, 0x6002): "display_window_top",
    (0x0028, 0x6003): "display_window_bottom",
}

DICOM_EQUIPMENT_TAGS = {
    (0x0008, 0x0070): "manufacturer",
    (0x0008, 0x0080): "institution_name",
    (0x0008, 0x0081): "institution_address",
    (0x0008, 0x0090): "referring_physician_name",
    (0x0008, 0x1010): "station_name",
    (0x0008, 0x1011): "procedure_log_location",
    (0x0008, 0x1012): "station_name_code",
    (0x0008, 0x1020): "software_versions",
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physicians_of_record",
    (0x0008, 0x1050): "institution_code",
    (0x0008, 0x1090): "manufacturer_model_name",
    (0x0008, 0x1091): "device_serial_number",
    (0x0008, 0x1100): "secondary_capture_device_id",
    (0x0008, 0x1111): "referenced_performed_procedure_step",
    (0x0018, 0x1000): "device_serial_number",
    (0x0018, 0x1002): "device_uid",
    (0x0018, 0x1004): "plate_id",
    (0x0018, 0x1005): "generative_model",
    (0x0018, 0x1010): "secondary_capture_device_manufacturer",
    (0x0018, 0x1011): "secondary_capture_device_model",
    (0x0018, 0x1012): "secondary_capture_device_software",
    (0x0018, 0x1018): "secondary_capture_device_version",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1200): "date_of_secondary_capture",
    (0x0018, 0x1201): "time_of_secondary_capture",
    (0x0018, 0x1202): "secondary_capture_device_processing_description",
    (0x0018, 0x1203): "secondary_capture_device_processing_parameters",
    (0x0018, 0x1204): "external_video_input_signal",
}

DICOM_VOI_LUT_TAGS = {
    (0x0028, 0x1056): "voilut_function",
    (0x0028, 0x1057): "lut_data",
    (0x0028, 0x3010): "lut_descriptor",
    (0x0028, 0x3011): "lut_data",
    (0x0028, 0x3012): "lut_type",
    (0x0028, 0x3015): "lut_explanation",
    (0x0028, 0x3020): "modality_lut_sequence",
    (0x0028, 0x3006): "softcopy_voi_lut_sequence",
}

DICOM_SOP_TAGS = {
    (0x0008, 0x0016): "sop_class_uid",
    (0x0008, 0x0018): "sop_instance_uid",
    (0x0008, 0x0019): "sop_instance_creation_time",
    (0x0008, 0x0020): "study_date",
    (0x0008, 0x0021): "series_date",
    (0x0008, 0x0022): "acquisition_date",
    (0x0008, 0x0023): "content_date",
    (0x0008, 0x0030): "study_time",
    (0x0008, 0x0031): "series_time",
    (0x0008, 0x0032): "acquisition_time",
    (0x0008, 0x0033): "content_time",
    (0x0008, 0x0060): "modality",
    (0x0008, 0x0064): "conversion_type",
    (0x0008, 0x0068): "presentation_intent_type",
    (0x0008, 0x0100): "copyright",
    (0x0008, 0x0201): "timezone_offset",
}

DICOM_PRIVATE_TAGS = {
    (0x0009, 0x0010): "ge_private_data",
    (0x0009, 0x1001): "ge_manufacturer",
    (0x0009, 0x1002): "ge_institution_name",
    (0x0009, 0x1003): "ge_station_name",
    (0x0009, 0x1004): "ge_department",
    (0x0009, 0x1005): "ge_physicians_of_record",
    (0x0019, 0x0010): "siemens_private_data",
    (0x0019, 0x1010): "siemens_software_version",
    (0x0019, 0x1011): "siemens_serial_number",
    (0x0019, 0x1020): "siemens_protocol_name",
    (0x0021, 0x0010): "philips_private_data",
    (0x0021, 0x1010): "philips_software_version",
    (0x0021, 0x1020): "philips_series_number",
    (0x0029, 0x0010): "toshiba_private_data",
    (0x0029, 0x1010): "toshiba_software_version",
    (0x0029, 0x1020): "toshiba_protocol_name",
}

DICOM_CT_SPECIFIC = {
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0090): "data_collection_diameter",
    (0x0018, 0x0095): "pixel_spacing",
    (0x0018, 0x1100): "reconstruction_diameter",
    (0x0018, 0x1110): "distance_source_to_detector",
    (0x0018, 0x1111): "distance_source_to_patient",
    (0x0018, 0x1120): "gantry_detector_tilt",
    (0x0018, 0x1130): "table_height",
    (0x0018, 0x1131): "table_motion",
    (0x0018, 0x1134): "table_speed",
    (0x0018, 0x1135): "table_feet_per_rotation",
    (0x0018, 0x1136): "total_angle_per_rotation",
    (0x0018, 0x1140): "rotational_direction",
    (0x0018, 0x1145): "exposure_time",
    (0x0018, 0x1150): "x_ray_tube_current",
    (0x0018, 0x1151): "exposure",
    (0x0018, 0x1152): "exposure_in_mas",
    (0x0018, 0x1160): "filter_type",
    (0x0018, 0x1162): "generator_power",
    (0x0018, 0x1170): "focal_spot",
    (0x0018, 0x1180): "date_of_last_calibration",
    (0x0018, 0x1181): "time_of_last_calibration",
    (0x0018, 0x1190): "convolution_kernel",
    (0x0018, 0x1210): "reconstruction_field_of_view",
    (0x0018, 0x1220): "reconstruction_algorithm",
    (0x0018, 0x1300): "computed_tomography_slice_thickness",
}

DICOM_MR_SPECIFIC = {
    (0x0018, 0x0020): "scanning_sequence",
    (0x0018, 0x0021): "sequence_variant",
    (0x0018, 0x0022): "scan_options",
    (0x0018, 0x0023): "mr_acquisition_type",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "angle_signification",
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x0081): "echo_time",
    (0x0018, 0x0083): "number_of_averages",
    (0x0018, 0x0084): "imaging_frequency",
    (0x0018, 0x0085): "echo_number",
    (0x0018, 0x0086): "magnetic_field_strength",
    (0x0018, 0x0087): "spacing_between_slices",
    (0x0018, 0x0088): "number_of_phase_encoding_steps",
    (0x0018, 0x0089): "data_acquisition_dead_time",
    (0x0018, 0x0090): "pixel_bandwidth",
    (0x0018, 0x0091): "dwell_time",
    (0x0018, 0x0093): "sar",
    (0x0018, 0x0094): "dwi_b_value",
    (0x0018, 0x0095): "dwi_gradient_direction",
    (0x0018, 0x0100): "software_versions",
    (0x0018, 0x0200): "modality_specific_filters",
    (0x0018, 0x1020): "protocol_name",
    (0x0018, 0x1030): "protocol_name_alt",
    (0x0018, 0x1070): "transmitter_coil_name",
    (0x0018, 0x1071): "receive_coil_name",
    (0x0018, 0x1072): "receive_coil_manufacturer",
    (0x0018, 0x1074): "transmit_coil_type",
    (0x0018, 0x1075): "receive_coil_type",
    (0x0018, 0x1076): "receive_coil_array",
    (0x0018, 0x1078): "receive_coil_nominal_velocity",
    (0x0018, 0x1079): "gradient_coil_name",
    (0x0018, 0x1080): "gradient_coil_type",
    (0x0018, 0x1081): "gradient_amplifier_type",
    (0x0018, 0x1090): "probe_drive_application",
    (0x0018, 0x1091): "probe_drive_frequency",
    (0x0018, 0x1092): "probe_drive_waveform",
    (0x0018, 0x1100): "transmit_gain",
    (0x0018, 0x1101): "receive_gain",
    (0x0018, 0x1102): "pre_amp_duty_cycle",
    (0x0018, 0x1103): "pre_amp_base_bandwidth",
    (0x0018, 0x1200): "patient_position",
    (0x0018, 0x1210): "mr_fov_geometry",
    (0x0018, 0x1250): "receive_polynomial_coefficients",
}

DICOM_US_SPECIFIC = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0100): "software_versions",
    (0x0018, 0x0110): "date_of_last_calibration",
    (0x0018, 0x0111): "time_of_last_calibration",
    (0x0018, 0x5000): "probe_technology",
    (0x0018, 0x5010): "probe_angle",
    (0x0018, 0x5012): "curved_probe",
    (0x0018, 0x5020): "probe_description",
    (0x0018, 0x5030): "geometric_accuracy",
    (0x0018, 0x5040): "thermal_calibration",
    (0x0018, 0x5050): "depth_of_scan_field",
    (0x0018, 0x5100): "patient_orientation",
    (0x0018, 0x6010): "pulse_repetition_frequency",
    (0x0018, 0x6030): "doppler_correction_angle",
    (0x0018, 0x6040): "steering_angle",
    (0x0018, 0x7000): "element_pitch",
    (0x0018, 0x7001): "element_width",
    (0x0018, 0x7002): "element_height",
    (0x0018, 0x7004): "inter_element_spacing",
    (0x0018, 0x7006): "probe_wavelength",
    (0x0018, 0x7008): "pulse_duration",
    (0x0018, 0x7010): "image_zoom_factor",
    (0x0018, 0x7012): "zone_position",
    (0x0018, 0x7014): "zone_depth",
    (0x0018, 0x7016): "zone_width",
    (0x0018, 0x7030): "lens_depth",
    (0x0018, 0x7040): "transmit_power",
    (0x0018, 0x7045): "receive_gain",
    (0x0018, 0x7050): "pre_time_gain",
    (0x0018, 0x7054): "post_time_gain",
    (0x0018, 0x7060): "time_gain_correction",
    (0x0018, 0x7062): "time_gain_slope",
    (0x0018, 0x7064): "time_gain_intercept",
    (0x0018, 0x7070): "depth_of_focus",
    (0x0018, 0x7080): "depth_of_view",
    (0x0018, 0x7082): "field_of_view_shape",
    (0x0018, 0x7090): "transmit_frequency",
    (0x0018, 0x7092): "receive_center_frequency",
    (0x0018, 0x7094): "doppler_sample_volume_position",
    (0x0018, 0x7096): "tm_line_position",
    (0x0018, 0x7098): "tm_line_pixel_size",
}

DICOM_CR_SPECIFIC = {
    (0x0018, 0x1010): "secondary_capture_device_manufacturer",
    (0x0018, 0x1011): "secondary_capture_device_model",
    (0x0018, 0x1012): "secondary_capture_device_software",
    (0x0018, 0x1018): "secondary_capture_device_version",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1200): "date_of_secondary_capture",
    (0x0018, 0x1201): "time_of_secondary_capture",
    (0x0018, 0x1202): "secondary_capture_device_processing_description",
    (0x0018, 0x1203): "secondary_capture_device_processing_parameters",
    (0x0018, 0x1204): "external_video_input_signal",
    (0x0018, 0x1400): "reduction_of_circular_viewing",
    (0x0018, 0x1401): "processing_tool",
    (0x0018, 0x1402): "processing_description",
    (0x0018, 0x1403): "processing_algorithm_version",
    (0x0018, 0x1404): "processing_parameters",
    (0x0018, 0x1405): "regions_of_interest",
    (0x0018, 0x1410): "cassette_orientation",
    (0x0018, 0x1411): "cassette_size",
    (0x0018, 0x1412): "exposure_index",
    (0x0018, 0x1413): "target_exposure_index",
    (0x0018, 0x1414): "deviation_index",
    (0x0018, 0x1415): "sensitivity",
    (0x0018, 0x1416): "plate_sequence",
    (0x0018, 0x1417): "plate_description",
    (0x0018, 0x1418): "plate_version",
    (0x0018, 0x1419): "generative_model",
    (0x0018, 0x1420): "plate_id",
    (0x0018, 0x1421): "plate_type",
    (0x0018, 0x1422): "phosphor_type",
}

DICOM_DX_SPECIFIC = {
    (0x0018, 0x1010): "secondary_capture_device_manufacturer",
    (0x0018, 0x1011): "secondary_capture_device_model",
    (0x0018, 0x1012): "secondary_capture_device_software",
    (0x0018, 0x1018): "secondary_capture_device_version",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1200): "date_of_secondary_capture",
    (0x0018, 0x1201): "time_of_secondary_capture",
    (0x0018, 0x1202): "secondary_capture_device_processing_description",
    (0x0018, 0x1203): "secondary_capture_device_processing_parameters",
    (0x0018, 0x1204): "external_video_input_signal",
    (0x0018, 0x1400): "reduction_of_circular_viewing",
    (0x0018, 0x1401): "processing_tool",
    (0x0018, 0x1402): "processing_description",
    (0x0018, 0x1403): "processing_algorithm_version",
    (0x0018, 0x1404): "processing_parameters",
    (0x0018, 0x1405): "regions_of_interest",
    (0x0028, 0x1050): "window_center",
    (0x0028, 0x1051): "window_width",
    (0x0028, 0x1052): "window_center_width_explanation",
    (0x0028, 0x1053): "rescale_intercept",
    (0x0028, 0x1054): "rescale_slope",
    (0x0028, 0x1055): "rescale_type",
    (0x0028, 0x1056): "voilut_function",
    (0x0028, 0x1090): "pixel_intensity_relationship",
    (0x0028, 0x1091): "pixel_intensity_relationship_sign",
    (0x2110, 0x1001): "anatomic_structure",
    (0x2110, 0x1002): "body_part_examined",
}

DICOM_MG_SPECIFIC = {
    (0x0018, 0x1010): "secondary_capture_device_manufacturer",
    (0x0018, 0x1011): "secondary_capture_device_model",
    (0x0018, 0x1012): "secondary_capture_device_software",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1200): "date_of_secondary_capture",
    (0x0018, 0x1201): "time_of_secondary_capture",
    (0x0018, 0x1210): "compression_force",
    (0x0018, 0x1215): "compression_pressure",
    (0x0018, 0x1216): "compression_description",
    (0x0018, 0x1217): "compression_algorithm_name",
    (0x0018, 0x1218): "compression_algorithm_version",
    (0x0018, 0x1219): "region_shape",
    (0x0018, 0x1220): "region_start_x",
    (0x0018, 0x1221): "region_start_y",
    (0x0018, 0x1222): "region_width",
    (0x0018, 0x1223): "region_height",
    (0x0018, 0x1224): "region_rotation",
    (0x0018, 0x1225): "region_skew",
    (0x0018, 0x1230): "estimated_radiographic_magnification_factor",
    (0x0018, 0x1231): "positioner_primary_angle",
    (0x0018, 0x1232): "positioner_secondary_angle",
    (0x0018, 0x1240): "collimator_shape",
    (0x0018, 0x1241): "collimator_left_edge",
    (0x0018, 0x1242): "collimator_right_edge",
    (0x0018, 0x1243): "collimator_upper_edge",
    (0x0018, 0x1244): "collimator_lower_edge",
    (0x0018, 0x1245): "collimator_shape",
    (0x0018, 0x1246): "collimator_name",
    (0x0018, 0x1250): "distance_source_to_detector",
    (0x0018, 0x1251): "distance_source_to_patient",
    (0x0028, 0x1050): "window_center",
    (0x0028, 0x1051): "window_width",
    (0x0028, 0x1052): "window_center_width_explanation",
    (0x0028, 0x1053): "rescale_intercept",
    (0x0028, 0x1054): "rescale_slope",
    (0x0028, 0x1055): "rescale_type",
    (0x0028, 0x6030): "grid",
    (0x0040, 0x0302): "calibration_date",
    (0x0040, 0x0303): "calibration_time",
    (0x0040, 0x0304): "calibration_version",
    (0x0040, 0x0305): "calibration_algorithm",
    (0x0040, 0x0306): "calibration_parameters",
}

DICOM_NM_SPECIFIC = {
    (0x0018, 0x0020): "scanning_sequence",
    (0x0018, 0x0021): "sequence_variant",
    (0x0018, 0x0022): "scan_options",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0030): "series_time",
    (0x0018, 0x0031): "acquisition_time",
    (0x0018, 0x0033): "content_time",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0070): "contrast_bolus_agent",
    (0x0018, 0x0071): "contrast_bolus_agent_sequence",
    (0x0018, 0x0072): "contrast_bolus_t1_relaxivity",
    (0x0018, 0x0073): "administration_route",
    (0x0018, 0x0074): "contrast_bolus_volume",
    (0x0018, 0x0075): "contrast_bolus_start_time",
    (0x0018, 0x0076): "contrast_bolus_stop_time",
    (0x0018, 0x0077): "contrast_bolus_total_dose",
    (0x0018, 0x0078): "contrast_bolus_rate",
    (0x0018, 0x0079): "contrast_bolus_technique",
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x0081): "echo_time",
    (0x0018, 0x0082): "echo_number",
    (0x0018, 0x0083): "number_of_averages",
    (0x0018, 0x0084): "imaging_frequency",
    (0x0018, 0x0087): "magnetic_field_strength",
    (0x0018, 0x0090): "pixel_bandwidth",
    (0x0018, 0x1000): "device_serial_number",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "study_protocol",
    (0x0018, 0x1040): "attenuation_correction_method",
    (0x0018, 0x1041): "reconstruction_method",
    (0x0018, 0x1042): "reconstruction_diameter",
    (0x0018, 0x1043): "reconstruction_filter",
    (0x0018, 0x1044): "reconstruction_algorithm_version",
    (0x0018, 0x1045): "filter_kernel",
    (0x0018, 0x1046): "lower_upper_cutoff",
    (0x0018, 0x1047): "scatter_correction_method",
    (0x0018, 0x1050): "axial_detector_geometry",
    (0x0018, 0x1051): "axial_bin_to_pixel_mapping",
    (0x0018, 0x1060): "frame_acquisition_time",
    (0x0018, 0x1061): "frame_reference_time",
    (0x0018, 0x1062): "group_frame_offset_time",
    (0x0018, 0x1063): "frame_acquisition_duration",
    (0x0018, 0x1070): "radionuclide_total_dose",
    (0x0018, 0x1071): "radionuclide_code_sequence",
    (0x0018, 0x1072): "radionuclide_half_life",
    (0x0018, 0x1073): "radionuclide_positron_fraction",
    (0x0018, 0x1074): "radiopharmaceutical_specific_activity",
    (0x0018, 0x1075): "radiopharmaceutical_start_time",
    (0x0018, 0x1076): "radiopharmaceutical_stop_time",
    (0x0018, 0x1077): "decay_correction_date_time",
    (0x0018, 0x1078): "spatial_resolution",
    (0x0018, 0x1079): "counts_accumulated",
    (0x0018, 0x1080): "dose_calibration_factor",
    (0x0018, 0x1081): "scatter_correction_factor",
    (0x0018, 0x1082): "dead_time_correction_factor",
    (0x0018, 0x1083): "image_intensity_factor",
    (0x0018, 0x1084): "scatter_fraction_correction",
    (0x0018, 0x1085): "dead_time_correction_method",
    (0x0018, 0x1086): "binning_factor",
    (0x0018, 0x1087): "count_summation_type",
    (0x0018, 0x1088): "total_counts_accumulated",
    (0x0018, 0x1089): "maximum_counts_accumulated",
    (0x0018, 0x1090): "matrix_size_x",
    (0x0018, 0x1091): "matrix_size_y",
    (0x0018, 0x1092): "pixel_size",
    (0x0018, 0x1093): "energy_window_vector",
    (0x0018, 0x1094): "number_of_energy_windows",
    (0x0018, 0x1095): "energy_window_lower_bound_vector",
    (0x0018, 0x1096): "energy_window_upper_bound_vector",
    (0x0018, 0x1097): "radiopharmaceutical_information_sequence",
    (0x0018, 0x1098): "energy_window_name",
}

DICOM_PT_SPECIFIC = {
    (0x0018, 0x0030): "series_time",
    (0x0018, 0x0031): "acquisition_time",
    (0x0018, 0x0033): "content_time",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1000): "device_serial_number",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "study_protocol",
    (0x0018, 0x1040): "attenuation_correction_method",
    (0x0018, 0x1041): "reconstruction_method",
    (0x0018, 0x1042): "reconstruction_diameter",
    (0x0018, 0x1043): "reconstruction_filter",
    (0x0018, 0x1044): "reconstruction_algorithm_version",
    (0x0018, 0x1045): "filter_kernel",
    (0x0018, 0x1046): "lower_upper_cutoff",
    (0x0018, 0x1047): "scatter_correction_method",
    (0x0018, 0x1050): "axial_detector_geometry",
    (0x0018, 0x1051): "axial_bin_to_pixel_mapping",
    (0x0018, 0x1060): "frame_acquisition_time",
    (0x0018, 0x1061): "frame_reference_time",
    (0x0018, 0x1062): "group_frame_offset_time",
    (0x0018, 0x1063): "frame_acquisition_duration",
    (0x0018, 0x1070): "radionuclide_total_dose",
    (0x0018, 0x1071): "radionuclide_code_sequence",
    (0x0018, 0x1072): "radionuclide_half_life",
    (0x0018, 0x1073): "radionuclide_positron_fraction",
    (0x0018, 0x1074): "radiopharmaceutical_specific_activity",
    (0x0018, 0x1075): "radiopharmaceutical_start_time",
    (0x0018, 0x1076): "radiopharmaceutical_stop_time",
    (0x0018, 0x1077): "decay_correction_date_time",
    (0x0018, 0x1078): "spatial_resolution",
    (0x0018, 0x1079): "counts_accumulated",
    (0x0018, 0x1080): "dose_calibration_factor",
    (0x0018, 0x1081): "scatter_correction_factor",
    (0x0018, 0x1082): "dead_time_correction_factor",
    (0x0018, 0x1083): "image_intensity_factor",
    (0x0018, 0x1084): "scatter_fraction_correction",
    (0x0018, 0x1085): "dead_time_correction_method",
    (0x0018, 0x1086): "binning_factor",
    (0x0018, 0x1087): "count_summation_type",
    (0x0018, 0x1088): "total_counts_accumulated",
    (0x0018, 0x1089): "maximum_counts_accumulated",
    (0x0018, 0x1090): "matrix_size_x",
    (0x0018, 0x1091): "matrix_size_y",
    (0x0018, 0x1092): "pixel_size",
    (0x0018, 0x1093): "energy_window_vector",
    (0x0018, 0x1094): "number_of_energy_windows",
    (0x0018, 0x1095): "energy_window_lower_bound_vector",
    (0x0018, 0x1096): "energy_window_upper_bound_vector",
    (0x0018, 0x1097): "radiopharmaceutical_information_sequence",
    (0x0018, 0x1098): "energy_window_name",
    (0x0018, 0x1100): "reconstruction_diameter",
    (0x0018, 0x1110): "distance_source_to_detector",
    (0x0018, 0x1111): "distance_source_to_patient",
    (0x0018, 0x1120): "gantry_detector_tilt",
    (0x0018, 0x1130): "table_height",
    (0x0018, 0x1131): "table_motion",
    (0x0018, 0x1134): "table_speed",
    (0x0018, 0x1140): "rotational_direction",
    (0x0018, 0x1145): "exposure_time",
    (0x0018, 0x1150): "x_ray_tube_current",
    (0x0018, 0x1151): "exposure",
    (0x0018, 0x1152): "exposure_in_mas",
    (0x0018, 0x1160): "filter_type",
    (0x0018, 0x1162): "generator_power",
    (0x0018, 0x1170): "focal_spot",
    (0x0018, 0x1190): "convolution_kernel",
    (0x0018, 0x1210): "reconstruction_field_of_view",
    (0x0018, 0x1220): "reconstruction_algorithm",
    (0x0018, 0x1240): "collimator_shape",
    (0x0018, 0x1241): "collimator_left_edge",
    (0x0018, 0x1242): "collimator_right_edge",
    (0x0018, 0x1243): "collimator_upper_edge",
    (0x0018, 0x1244): "collimator_lower_edge",
}

DICOM_XA_SPECIFIC = {
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0062): "intensifier_size",
    (0x0018, 0x0064): "conversion_type",
    (0x0018, 0x0070): "contrast_bolus_agent",
    (0x0018, 0x0071): "contrast_bolus_agent_sequence",
    (0x0018, 0x0072): "contrast_bolus_t1_relaxivity",
    (0x0018, 0x0073): "administration_route",
    (0x0018, 0x0074): "contrast_bolus_volume",
    (0x0018, 0x0075): "contrast_bolus_start_time",
    (0x0018, 0x0076): "contrast_bolus_stop_time",
    (0x0018, 0x0077): "contrast_bolus_total_dose",
    (0x0018, 0x0078): "contrast_bolus_rate",
    (0x0018, 0x0079): "contrast_bolus_technique",
    (0x0018, 0x1000): "device_serial_number",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "study_protocol",
    (0x0018, 0x1040): "intervention_description",
    (0x0018, 0x1041): "intervention_status",
    (0x0018, 0x1050): "c_arm_positioner_primary_angle",
    (0x0018, 0x1051): "c_arm_positioner_secondary_angle",
    (0x0018, 0x1052): "c_arm_positioner_primary_end_angle",
    (0x0018, 0x1053): "c_arm_positioner_secondary_end_angle",
    (0x0018, 0x1054): "c_arm_positioner_rotation_direction",
    (0x0018, 0x1055): "positioner_position",
    (0x0018, 0x1056): "positioner_position_2",
    (0x0018, 0x1057): "positioner_position_3",
    (0x0018, 0x1060): "table_position",
    (0x0018, 0x1061): "table_position_2",
    (0x0018, 0x1062): "table_position_3",
    (0x0018, 0x1063): "table_rotation",
    (0x0018, 0x1064): "table_type",
    (0x0018, 0x1065): "table_motion",
    (0x0018, 0x1100): "reconstruction_diameter",
    (0x0018, 0x1110): "distance_source_to_detector",
    (0x0018, 0x1111): "distance_source_to_patient",
    (0x0018, 0x1120): "gantry_detector_tilt",
    (0x0018, 0x1130): "table_height",
    (0x0018, 0x1131): "table_motion",
    (0x0018, 0x1134): "table_speed",
    (0x0018, 0x1140): "rotational_direction",
    (0x0018, 0x1145): "exposure_time",
    (0x0018, 0x1150): "x_ray_tube_current",
    (0x0018, 0x1151): "exposure",
    (0x0018, 0x1152): "exposure_in_mas",
    (0x0018, 0x1160): "filter_type",
    (0x0018, 0x1162): "generator_power",
    (0x0018, 0x1170): "focal_spot",
    (0x0018, 0x1190): "convolution_kernel",
    (0x0018, 0x1210): "reconstruction_field_of_view",
    (0x0018, 0x1220): "reconstruction_algorithm",
    (0x0018, 0x1240): "collimator_shape",
    (0x0018, 0x1241): "collimator_left_edge",
    (0x0018, 0x1242): "collimator_right_edge",
    (0x0018, 0x1243): "collimator_upper_edge",
    (0x0018, 0x1244): "collimator_lower_edge",
    (0x0018, 0x1250): "pulse_rate",
    (0x0018, 0x1251): "pulse_length",
    (0x0018, 0x1252): "pulse_characteristic",
    (0x0018, 0x1253): "pulse_characteristic_description",
    (0x0018, 0x1254): "total_filter_thickness",
    (0x0018, 0x1255): "total_filter_material",
}

DICOM_RF_SPECIFIC = {
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0062): "intensifier_size",
    (0x0018, 0x0064): "conversion_type",
    (0x0018, 0x0070): "contrast_bolus_agent",
    (0x0018, 0x0071): "contrast_bolus_agent_sequence",
    (0x0018, 0x0072): "contrast_bolus_t1_relaxivity",
    (0x0018, 0x0073): "administration_route",
    (0x0018, 0x0074): "contrast_bolus_volume",
    (0x0018, 0x0075): "contrast_bolus_start_time",
    (0x0018, 0x0076): "contrast_bolus_stop_time",
    (0x0018, 0x0077): "contrast_bolus_total_dose",
    (0x0018, 0x0078): "contrast_bolus_rate",
    (0x0018, 0x0079): "contrast_bolus_technique",
    (0x0018, 0x1000): "device_serial_number",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "study_protocol",
    (0x0018, 0x1040): "intervention_description",
    (0x0018, 0x1041): "intervention_status",
    (0x0018, 0x1050): "c_arm_positioner_primary_angle",
    (0x0018, 0x1051): "c_arm_positioner_secondary_angle",
    (0x0018, 0x1052): "c_arm_positioner_primary_end_angle",
    (0x0018, 0x1053): "c_arm_positioner_secondary_end_angle",
    (0x0018, 0x1054): "c_arm_positioner_rotation_direction",
    (0x0018, 0x1055): "positioner_position",
    (0x0018, 0x1056): "positioner_position_2",
    (0x0018, 0x1057): "positioner_position_3",
    (0x0018, 0x1060): "table_position",
    (0x0018, 0x1061): "table_position_2",
    (0x0018, 0x1062): "table_position_3",
    (0x0018, 0x1063): "table_rotation",
    (0x0018, 0x1064): "table_type",
    (0x0018, 0x1065): "table_motion",
    (0x0018, 0x1100): "reconstruction_diameter",
    (0x0018, 0x1110): "distance_source_to_detector",
    (0x0018, 0x1111): "distance_source_to_patient",
    (0x0018, 0x1120): "gantry_detector_tilt",
    (0x0018, 0x1130): "table_height",
    (0x0018, 0x1131): "table_motion",
    (0x0018, 0x1134): "table_speed",
    (0x0018, 0x1140): "rotational_direction",
    (0x0018, 0x1145): "exposure_time",
    (0x0018, 0x1150): "x_ray_tube_current",
    (0x0018, 0x1151): "exposure",
    (0x0018, 0x1152): "exposure_in_mas",
    (0x0018, 0x1160): "filter_type",
    (0x0018, 0x1162): "generator_power",
    (0x0018, 0x1170): "focal_spot",
    (0x0018, 0x1190): "convolution_kernel",
    (0x0018, 0x1210): "reconstruction_field_of_view",
    (0x0018, 0x1220): "reconstruction_algorithm",
    (0x0018, 0x1240): "collimator_shape",
    (0x0018, 0x1241): "collimator_left_edge",
    (0x0018, 0x1242): "collimator_right_edge",
    (0x0018, 0x1243): "collimator_upper_edge",
    (0x0018, 0x1244): "collimator_lower_edge",
    (0x0018, 0x1250): "dose_rate",
    (0x0018, 0x1251): "spot_size",
    (0x0018, 0x1252): "reference_air_kerma_rate",
    (0x0018, 0x1253): "procedure_state",
    (0x0018, 0x1254): "fluoroscopy_technique",
    (0x0018, 0x1255): "total_filter_thickness",
    (0x0018, 0x1256): "total_filter_material",
    (0x0018, 0x1260): "exposure_sequence",
    (0x0018, 0x1261): "radiation_gerry_setting_sequence",
    (0x0018, 0x1262): "radiation_gerry_machine_setting_sequence",
}

DICOM_SC_SPECIFIC = {
    (0x0018, 0x1010): "secondary_capture_device_manufacturer",
    (0x0018, 0x1011): "secondary_capture_device_model",
    (0x0018, 0x1012): "secondary_capture_device_software",
    (0x0018, 0x1018): "secondary_capture_device_version",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1200): "date_of_secondary_capture",
    (0x0018, 0x1201): "time_of_secondary_capture",
    (0x0018, 0x1202): "secondary_capture_device_processing_description",
    (0x0018, 0x1203): "secondary_capture_device_processing_parameters",
    (0x0018, 0x1204): "external_video_input_signal",
    (0x0018, 0x1400): "reduction_of_circular_viewing",
    (0x0018, 0x1401): "processing_tool",
    (0x0018, 0x1402): "processing_description",
    (0x0018, 0x1403): "processing_algorithm_version",
    (0x0018, 0x1404): "processing_parameters",
    (0x0018, 0x1405): "regions_of_interest",
    (0x0018, 0x1406): "output_timestamp",
    (0x0018, 0x1407): "output_sequence",
    (0x0018, 0x1408): "output_information_sequence",
    (0x0018, 0x1409): "output_flag",
    (0x0018, 0x1410): "cassette_orientation",
    (0x0018, 0x1411): "cassette_size",
    (0x0018, 0x1412): "exposure_index",
    (0x0018, 0x1413): "target_exposure_index",
    (0x0018, 0x1414): "deviation_index",
    (0x0018, 0x1415): "sensitivity",
    (0x0018, 0x1416): "plate_sequence",
    (0x0018, 0x1417): "plate_description",
    (0x0018, 0x1418): "plate_version",
    (0x0018, 0x1419): "generative_model",
    (0x0018, 0x1420): "plate_id",
    (0x0018, 0x1421): "plate_type",
    (0x0018, 0x1422): "phosphor_type",
    (0x0018, 0x1423): "scan_parameters_sequence",
    (0x0018, 0x1424): "irradiation_event_identification_sequence",
    (0x0018, 0x1425): "image_generation_parameters_sequence",
    (0x0018, 0x1426): "image_processing_parameters_sequence",
    (0x0018, 0x1427): "image_coordinates_sequence",
    (0x0018, 0x1428): "reference_coordinates_sequence",
}


ALL_DICOM_TAGS = {
    **DICOM_PATIENT_TAGS,
    **DICOM_STUDY_TAGS,
    **DICOM_SERIES_TAGS,
    **DICOM_IMAGE_TAGS,
    **DICOM_EQUIPMENT_TAGS,
    **DICOM_VOI_LUT_TAGS,
    **DICOM_SOP_TAGS,
    **DICOM_PRIVATE_TAGS,
    **DICOM_CT_SPECIFIC,
    **DICOM_MR_SPECIFIC,
    **DICOM_US_SPECIFIC,
    **DICOM_CR_SPECIFIC,
    **DICOM_DX_SPECIFIC,
    **DICOM_MG_SPECIFIC,
    **DICOM_NM_SPECIFIC,
    **DICOM_PT_SPECIFIC,
    **DICOM_XA_SPECIFIC,
    **DICOM_RF_SPECIFIC,
    **DICOM_SC_SPECIFIC,
}


def extract_dicom_metadata(filepath: str) -> Dict[str, Any]:
    """Extract comprehensive DICOM metadata."""
    result = {
        "patient": {},
        "study": {},
        "series": {},
        "image": {},
        "equipment": {},
        "voi_lut": {},
        "sop": {},
        "modality_specific": {},
        "private_tags": {},
        "registry": {},
        "fields_extracted": 0,
        "is_valid_dicom": False
    }

    try:
        import pydicom
        ds = pydicom.dcmread(filepath)
        result["is_valid_dicom"] = True

        for tag, name in DICOM_PATIENT_TAGS.items():
            try:
                value = ds.get(tag, None)
                if value:
                    result["patient"][name] = str(value)
            except Exception as e:
                logger.debug(f"Failed to extract DICOM patient tag {name}: {e}")

        for tag, name in DICOM_STUDY_TAGS.items():
            try:
                value = ds.get(tag, None)
                if value:
                    result["study"][name] = str(value)
            except Exception as e:
                logger.debug(f"Failed to extract DICOM study tag {name}: {e}")

        for tag, name in DICOM_SERIES_TAGS.items():
            try:
                value = ds.get(tag, None)
                if value:
                    result["series"][name] = str(value)
            except Exception as e:
                logger.debug(f"Failed to extract DICOM series tag {name}: {e}")

        for tag, name in DICOM_IMAGE_TAGS.items():
            try:
                value = ds.get(tag, None)
                if value:
                    result["image"][name] = str(value)
            except Exception as e:
                logger.debug(f"Failed to extract DICOM image tag {name}: {e}")

        for tag, name in DICOM_EQUIPMENT_TAGS.items():
            try:
                value = ds.get(tag, None)
                if value:
                    result["equipment"][name] = str(value)
            except Exception as e:
                logger.debug(f"Failed to extract DICOM equipment tag {name}: {e}")

        for tag, name in DICOM_VOI_LUT_TAGS.items():
            try:
                value = ds.get(tag, None)
                if value:
                    result["voi_lut"][name] = str(value)
            except Exception as e:
                logger.debug(f"Failed to extract DICOM VOI LUT tag {name}: {e}")

        for tag, name in DICOM_SOP_TAGS.items():
            try:
                value = ds.get(tag, None)
                if value:
                    result["sop"][name] = str(value)
            except Exception as e:
                logger.debug(f"Failed to extract DICOM SOP tag {name}: {e}")

        modality = result["series"].get("modality", "")
        if modality == "CT":
            for tag, name in DICOM_CT_SPECIFIC.items():
                try:
                    value = ds.get(tag, None)
                    if value:
                        result["modality_specific"][name] = str(value)
                except Exception as e:
                    logger.debug(f"Failed to extract DICOM CT-specific tag {name}: {e}")
        elif modality == "MR":
            for tag, name in DICOM_MR_SPECIFIC.items():
                try:
                    value = ds.get(tag, None)
                    if value:
                        result["modality_specific"][name] = str(value)
                except Exception as e:
                    logger.debug(f"Failed to extract DICOM MR-specific tag {name}: {e}")
        elif modality == "US":
            for tag, name in DICOM_US_SPECIFIC.items():
                try:
                    value = ds.get(tag, None)
                    if value:
                        result["modality_specific"][name] = str(value)
                except Exception as e:
                    logger.debug(f"Failed to extract DICOM US-specific tag {name}: {e}")

        private_elements = []
        for elem in ds:
            if elem.tag.is_private:
                private_elements.append({
                    "tag": str(elem.tag),
                    "name": elem.keyword,
                    "value": str(elem.value)[:100] if elem.value else None
                })
        result["private_tags"]["count"] = len(private_elements)
        result["private_tags"]["elements"] = private_elements[:10]

        registry_tags: Dict[str, Dict[str, Any]] = {}
        unknown_tags: Dict[str, Dict[str, Any]] = {}

        def _format_dicom_value(value: Any) -> Any:
            if value is None:
                return None
            if isinstance(value, bytes):
                return {"bytes": len(value)}
            if isinstance(value, (list, tuple)):
                return [_format_dicom_value(item) for item in value[:50]]
            text = str(value)
            if len(text) > 500:
                return text[:500] + "..."
            return text

        if DICOM_REGISTRY_FIELDS:
            for elem in ds:
                try:
                    if elem.tag == (0x7FE0, 0x0010):
                        continue
                    if elem.VR in {"OB", "OW", "OF", "UN"}:
                        continue
                    tag_code = f"{elem.tag.group:04X},{elem.tag.element:04X}"
                    tag_name = (
                        DICOM_REGISTRY_FIELDS.get(tag_code)
                        or DICOM_PRIVATE_REGISTRY.get(elem.tag)
                        or elem.keyword
                        or elem.name
                    )
                    entry = {"name": tag_name, "value": _format_dicom_value(elem.value)}
                    registry_tags[tag_code] = entry
                    if tag_code not in DICOM_REGISTRY_FIELDS:
                        unknown_tags[tag_code] = entry
                except Exception:
                    continue

        result["registry"] = {
            "available": bool(DICOM_REGISTRY_FIELDS),
            "fields_extracted": len(registry_tags),
            "unknown_count": len(unknown_tags),
            "tags": registry_tags,
            "unknown_tags": unknown_tags,
        }

        category_count = (
            len(result["patient"]) +
            len(result["study"]) +
            len(result["series"]) +
            len(result["image"]) +
            len(result["equipment"]) +
            len(result["voi_lut"]) +
            len(result["sop"]) +
            len(result["modality_specific"]) +
            len(result["private_tags"])
        )
        result["fields_extracted"] = len(registry_tags) if registry_tags else category_count

    except ImportError:
        result["error"] = "pydicom not installed"
    except Exception as e:
        result["error"] = str(e)[:200]

    return result


def get_dicom_field_count() -> int:
    """Return total number of DICOM fields."""
    if DICOM_REGISTRY_FIELDS:
        return len(DICOM_REGISTRY_FIELDS)
    return len(ALL_DICOM_TAGS)


def analyze_dicom_quality(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze DICOM image quality indicators."""
    analysis = {
        "image_quality": "unknown",
        "resolution_score": None,
        "bit_depth_score": None,
        "issues": [],
        "recommendations": []
    }

    image = metadata.get("image", {})
    series = metadata.get("series", {})
    equipment = metadata.get("equipment", {})

    width = image.get("columns")
    height = image.get("rows")
    bits_allocated = image.get("bits_allocated")
    modality = series.get("modality")

    if width and height:
        total_pixels = width * height
        if total_pixels >= 512 * 512:
            analysis["resolution_score"] = "high"
        elif total_pixels >= 256 * 256:
            analysis["resolution_score"] = "medium"
        else:
            analysis["resolution_score"] = "low"

    if bits_allocated:
        if bits_allocated >= 16:
            analysis["bit_depth_score"] = "high"
        elif bits_allocated >= 12:
            analysis["bit_depth_score"] = "medium"
        else:
            analysis["bit_depth_score"] = "low"

    if image.get("lossy_image_compression") == "01":
        analysis["issues"].append("Lossy compression detected - not suitable for diagnostics")
        analysis["recommendations"].append("Request uncompressed or lossless compressed version")

    if not equipment.get("manufacturer"):
        analysis["issues"].append("Missing equipment information")

    if not image.get("window_center") or not image.get("window_width"):
        analysis["recommendations"].append("Window level not set - default viewing may not be optimal")

    return analysis
