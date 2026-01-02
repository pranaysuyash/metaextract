"""
Scientific DICOM/FITS Ultimate Advanced Extension X - Pathology/Whole Slide Imaging

This module provides comprehensive extraction of DICOM metadata for digital pathology
and whole slide imaging (WSI) formats. Supports pathology workflows including
histology, cytology, and specialized digital pathology modalities.

Supported Modalities:
- WSI: Whole Slide Imaging (primary)
- PX: Pathology (secondary)
- CS: Cystoscopy (related)
- Other pathology-related DICOM modalities

DICOM Tags Extracted:
- WSI acquisition parameters
- Slide and specimen metadata
- Focus and scanning parameters
- Image pyramid information
- Optical and illumination settings
- Pathology-specific measurements
- Staining and preparation information

References:
- DICOM Standard Part 3: Information Object Definitions
- DICOM Standard Part 16: Grayscale Softcopy Presentation State
- Digital Pathology Association guidelines
- Whole Slide Imaging validation standards

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_X_AVAILABLE = True

WSI_ACQUISITION_TAGS = {
    (0x0048, 0x0200): "imaged_volume_width",
    (0x0048, 0x0201): "imaged_volume_height",
    (0x0048, 0x0202): "imaged_volume_depth",
    (0x0048, 0x0210): "pixel_spacing_series",
    (0x0048, 0x0212): "slice_thickness_direction",
    (0x0048, 0x0214): "scan_options_pixels",
    (0x0048, 0x0216): "data_collection_diameter_pixels",
    (0x0048, 0x0218): "reconstruction_diameter_pixels",
    (0x0048, 0x0220): "reconstruction_angle_pixels",
    (0x0048, 0x0222): "filter_ring_ratio",
    (0x0048, 0x0224): "axial_detector_coverage",
    (0x0048, 0x0226): "gantry_or_detector_tilt",
    (0x0048, 0x0228): "gantry_or_detector_slew_angle",
    (0x0048, 0x0230): "table_height",
    (0x0048, 0x0232): "table_motion_step_vector",
    (0x0048, 0x0234): "table_position_sequence",
    (0x0048, 0x0236): "table_forward_direction",
    (0x0048, 0x0238): "table_horizontal_shift_vector",
    (0x0048, 0x0240): "table_cumulative_time",
    (0x0048, 0x0250): "body_part_thickness",
    (0x0048, 0x0252): "body_part_abbreviation",
    (0x0048, 0x0260): "view_window_center",
    (0x0048, 0x0261): "view_window_width",
    (0x0048, 0x0262): "view_window_center_and_width_explanation",
    (0x0048, 0x0264): "reverse_byte_order",
    (0x0048, 0x0266): "recommended_viewing_mode",
}

SLIDE_SPECIMEN_TAGS = {
    (0x0048, 0x0001): "specimen_accession_number",
    (0x0048, 0x0002): "specimen_sequence",
    (0x0048, 0x0003): "specimen_identifier",
    (0x0048, 0x0004): "specimen_localization_content_sequence",
    (0x0048, 0x0005): "specimen_preparation_sequence",
    (0x0048, 0x0006): "specimen_preparation_step_content_sequence",
    (0x0048, 0x0007): "specimen_preparation_step_index",
    (0x0048, 0x0008): "specimen_preparation_step_description",
    (0x0048, 0x0009): "specimen_preparation_step_anchoring_tag",
    (0x0048, 0x000A): "specimen_preparation_content_item_sequence",
    (0x0048, 0x0010): "slide_identifier",
    (0x0048, 0x0011): "slide_culture_type",
    (0x0048, 0x0012): "slide_preparation_content_sequence",
    (0x0048, 0x0020): "slide_surface_identifier",
    (0x0048, 0x0021): "slide_characteristics_content_sequence",
    (0x0048, 0x0022): "slide_label_content_sequence",
    (0x0048, 0x0100): "number_of_focal_planes",
    (0x0048, 0x0101): "number_of_optical_paths",
    (0x0048, 0x0102): "optical_path_sequence",
    (0x0048, 0x0103): "optical_path_identifier",
    (0x0048, 0x0104): "optical_path_description",
    (0x0048, 0x0105): "optical_path_information_sequence",
    (0x0048, 0x0106): "optical_path_characteristics_sequence",
    (0x0048, 0x0107): "area_of_calculation_sequence",
    (0x0048, 0x0108): "area_of_calculation_unit_sequence",
    (0x0048, 0x0109): "calculation_method_description",
    (0x0048, 0x0200): "imaged_volume_width",
    (0x0048, 0x0201): "imaged_volume_height",
    (0x0048, 0x0202): "imaged_volume_depth",
    (0x0048, 0x0210): "pixel_spacing_series",
    (0x0048, 0x0212): "slice_thickness_direction",
    (0x0048, 0x0214): "scan_options_pixels",
    (0x0048, 0x0216): "data_collection_diameter_pixels",
    (0x0048, 0x0218): "reconstruction_diameter_pixels",
    (0x0048, 0x021A): "reconstruction_field_of_view",
    (0x0048, 0x021C): "reconstruction_pixel_spacing",
    (0x0048, 0x0220): "reconstruction_angle",
    (0x0048, 0x0222): "filter_kernel_description",
    (0x0048, 0x0224): "axial_detector_coverage",
    (0x0048, 0x0226): "gantry_or_detector_tilt",
    (0x0048, 0x0228): "gantry_or_detector_slew_angle",
    (0x0048, 0x0230): "table_height",
    (0x0048, 0x0232): "table_motion_step_vector",
    (0x0048, 0x0234): "table_position_sequence",
    (0x0048, 0x0236): "table_forward_direction",
    (0x0048, 0x0238): "table_horizontal_shift_vector",
    (0x0048, 0x0240): "table_cumulative_time",
    (0x0048, 0x0250): "body_part_thickness",
    (0x0048, 0x0252): "body_part_abbreviation",
    (0x0048, 0x0253): "body_part_abbreviation_modifier_sequence",
    (0x0048, 0x0260): "view_window_center",
    (0x0048, 0x0261): "view_window_width",
    (0x0048, 0x0262): "view_window_center_and_width_explanation",
    (0x0048, 0x0264): "reverse_byte_order",
    (0x0048, 0x0266): "recommended_viewing_mode",
    (0x0048, 0x0268): "graphics_on_storage_media_flag",
    (0x0048, 0x026A): "graphics_storage_location",
    (0x0048, 0x0270): "patient_orientation_on_medium",
    (0x0048, 0x0280): "slide_labels_present_flag",
    (0x0048, 0x0281): "slide_label_sequence",
    (0x0048, 0x0282): "slide_number",
    (0x0048, 0x0283): "slide_barcode_value",
    (0x0048, 0x0284): "slide_barcode_symbology",
    (0x0048, 0x0290): "referenced_image_latest_sequence",
    (0x0048, 0x0291): "referenced_image_number",
    (0x0048, 0x0292): "displayed_area_bottom_right_hand_corner",
    (0x0048, 0x0293): "displayed_area_top_left_hand_corner",
    (0x0048, 0x0294): "displayed_area_selection_sequence",
    (0x0048, 0x0295): "displayed_area_subject_model_sequence",
    (0x0048, 0x0296): "displayed_area_units",
    (0x0048, 0x0297): "displayed_area_type",
    (0x0048, 0x0300): "polarity",
    (0x0048, 0x0302): "requested_decimate_cBehavior",
    (0x0048, 0x0304): "requested_decimate_target_magnification_factor",
    (0x0048, 0x0306): "decimate_cascade_result",
    (0x0048, 0x0308): "c_factor",
    (0x0048, 0x0310): "largest_pixel_value_in_series",
}

FOCUS_SCAN_TAGS = {
    (0x0048, 0x000B): "specimen_short_description",
    (0x0048, 0x000C): "specimen_preparation_step_content_item_sequence",
    (0x0048, 0x0013): "slide_identifier",
    (0x0048, 0x0014): "slide_locator_offset_sequence",
    (0x0048, 0x0015): "slide_locator_offset",
    (0x0048, 0x0016): "image_frame_locator_sequence",
    (0x0048, 0x0017): "frame_locator_offset",
    (0x0048, 0x0018): "slide_coords_system_sequence",
    (0x0048, 0x0019): "slide_coords_system_offset",
    (0x0048, 0x001A): "icc_profile",
    (0x0048, 0x0100): "number_of_focal_planes",
    (0x0048, 0x0101): "number_of_optical_paths",
    (0x0048, 0x0102): "optical_path_sequence",
    (0x0048, 0x0103): "optical_path_identifier",
    (0x0048, 0x0104): "optical_path_description",
    (0x0048, 0x0105): "optical_path_information_sequence",
    (0x0048, 0x0106): "optical_path_characteristics_sequence",
    (0x0048, 0x0107): "area_of_calculation_sequence",
    (0x0048, 0x0108): "area_of_calculation_unit_sequence",
    (0x0048, 0x0109): "calculation_method_description",
    (0x0048, 0x0200): "imaged_volume_width",
    (0x0048, 0x0201): "imaged_volume_height",
    (0x0048, 0x0202): "imaged_volume_depth",
    (0x0048, 0x0210): "pixel_spacing_series",
    (0x0048, 0x0212): "slice_thickness_direction",
    (0x0048, 0x0214): "scan_options_pixels",
    (0x0048, 0x0216): "data_collection_diameter_pixels",
    (0x0048, 0x0218): "reconstruction_diameter_pixels",
    (0x0048, 0x021A): "reconstruction_field_of_view",
    (0x0048, 0x021C): "reconstruction_pixel_spacing",
    (0x0048, 0x0220): "reconstruction_angle",
    (0x0048, 0x0222): "filter_kernel_description",
}

IMAGE_PYRAMID_TAGS = {
    (0x0008, 0x0018): "sop_instance_uid",
    (0x0008, 0x0201): "timezone_offset_from_utc",
    (0x0018, 0x0023): "spatial_resolution",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0090): "patient_position",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1100): "distance_source_to_detector",
    (0x0018, 0x1110): "distance_source_to_patient",
    (0x0018, 0x1120): "gantry_detector_tilt",
    (0x0018, 0x1130): "table_height",
    (0x0018, 0x1140): "table_motion",
    (0x0018, 0x1145): "table_position_extension_flag",
    (0x0018, 0x1147): "table_motion_step_vector",
    (0x0018, 0x1150): "table_speed",
    (0x0018, 0x1151): "table_nominal_velocity",
    (0x0018, 0x1152): "table_acceleration",
    (0x0018, 0x1153): "table_horizontal_displacement",
    (0x0040, 0x0241): "performed_procedure_step_start_date_time",
    (0x0040, 0x0242): "performed_procedure_step_end_date_time",
    (0x0040, 0x0243): "performed_procedure_step_discontinuation_reason_code_sequence",
    (0x0040, 0x0244): "procedure_step_state",
    (0x0040, 0x0250): "performed_procedure_type_description",
    (0x0040, 0x0253): "performed_procedure_type_code_sequence",
}

OPTICAL_ILLUMINATION_TAGS = {
    (0x0020, 0x0032): "image_position_patient",
    (0x0020, 0x0037): "image_orientation_patient",
    (0x0020, 0x0052): "frame_of_reference_uid",
    (0x0020, 0x0060): "laterality",
    (0x0020, 0x0062): "image_laterality",
    (0x0028, 0x0002): "samples_per_pixel",
    (0x0028, 0x0004): "photometric_interpretation",
    (0x0028, 0x0008): "number_of_frames",
    (0x0028, 0x0009): "frame_increment_pointer",
    (0x0028, 0x0010): "rows",
    (0x0028, 0x0011): "columns",
    (0x0028, 0x0030): "pixel_spacing",
    (0x0028, 0x0100): "bits_allocated",
    (0x0028, 0x0101): "bits_stored",
    (0x0028, 0x0102): "high_bit",
    (0x0028, 0x0103): "pixel_representation",
    (0x0028, 0x0106): "smallest_image_pixel_value",
    (0x0028, 0x0107): "largest_image_pixel_value",
    (0x0028, 0x1050): "window_center",
    (0x0028, 0x1051): "window_width",
    (0x0028, 0x1052): "rescale_intercept",
    (0x0028, 0x1053): "rescale_slope",
    (0x0028, 0x1054): "rescale_type",
    (0x0028, 0x1055): "window_center_width_explanation",
    (0x0028, 0x1056): "voilut_function",
    (0x0028, 0x1057): "recommended_viewing_mode",
}

PATHOLOGY_MEASUREMENT_TAGS = {
    (0x0040, 0x3001): "referenced_voxel_sequence",
    (0x0040, 0x3002): "referenced_voxel_index",
    (0x0040, 0x3003): "voxel_value_mapping_sequence",
    (0x0040, 0x3004): "mapped_pixel_value",
    (0x0040, 0x3005): "number_of_voxel_coordinates",
    (0x0040, 0x3006): "voxel_coordinate_sequence",
    (0x0040, 0x3007): "voxel_coordinate_value",
    (0x0040, 0x3008): "pixel_value_unit_code_sequence",
    (0x0040, 0x3009): "pixel_value_unit_description",
    (0x0040, 0x3010): "referenced_presentation_sequence",
    (0x0040, 0x3011): "presentation_sequence",
    (0x0040, 0x3012): "presentation_lut_sequence",
    (0x0040, 0x3013): "lut_data",
    (0x0040, 0x3014): "lut_function",
    (0x0040, 0x3015): "referenced_voi_lut_sequence",
    (0x0040, 0x3100): "image_processing_applied",
    (0x0040, 0x4050): "output_information_sequence",
    (0x0040, 0x4051): "desired_image_characteristics_sequence",
    (0x0040, 0x4052): "display_filter_sequence",
    (0x0048, 0x0001): "specimen_accession_number",
    (0x0048, 0x0002): "specimen_sequence",
    (0x0048, 0x0003): "specimen_identifier",
    (0x0048, 0x0004): "specimen_localization_content_sequence",
    (0x0048, 0x0005): "specimen_preparation_sequence",
    (0x0048, 0x0006): "specimen_preparation_step_content_sequence",
    (0x0048, 0x0007): "specimen_preparation_step_index",
    (0x0048, 0x0008): "specimen_preparation_step_description",
}

STAINING_PREPARATION_TAGS = {
    (0x0040, 0x0555): "referenced_staining_sequence",
    (0x0040, 0x0556): "staining_sequence",
    (0x0040, 0x0557): "staining_label_sequence",
    (0x0040, 0x0558): "staining_protocol_identification",
    (0x0040, 0x0559): "staining_protocol_description",
    (0x0040, 0x055A): "block_identifier",
    (0x0040, 0x055B): "slide_identifier",
    (0x0040, 0x055C): "label_type",
    (0x0040, 0x055D): "label_description",
    (0x0040, 0x055E): "stain_name_code_sequence",
    (0x0040, 0x055F): "stain_name",
    (0x0040, 0x0560): "stain_usage_sequence",
    (0x0040, 0x0561): "stain_used",
    (0x0040, 0x0562): "stain_not_used_reason",
    (0x0040, 0x0563): "roi_stain_usage_sequence",
    (0x0040, 0x0564): "roi_stain_used",
    (0x0040, 0x0565): "roi_stain_not_used_reason",
    (0x0040, 0x0566): "mounting_medium_usage_sequence",
    (0x0040, 0x0567): "mounting_medium_used",
    (0x0040, 0x0568): "mounting_medium_not_used_reason",
    (0x0040, 0x0569): "section_identifier",
    (0x0040, 0x056A): "section_number",
    (0x0040, 0x056B): "section_thickness",
    (0x0040, 0x056C): "section_preparation_sequence",
    (0x0040, 0x056D): "section_preparation_description",
    (0x0040, 0x056E): "focus_and_scan_parameters_sequence",
    (0x0040, 0x056F): "focus_parameter_unit",
    (0x0040, 0x0570): "focus_distance",
    (0x0040, 0x0571): "scan_direction",
}

WSI_TOTAL_TAGS = (
    WSI_ACQUISITION_TAGS | SLIDE_SPECIMEN_TAGS | FOCUS_SCAN_TAGS |
    IMAGE_PYRAMID_TAGS | OPTICAL_ILLUMINATION_TAGS | PATHOLOGY_MEASUREMENT_TAGS |
    STAINING_PREPARATION_TAGS
)


def _extract_wsi_acquisition_tags(ds: Any) -> Dict[str, Any]:
    """Extract WSI acquisition and scanning parameters."""
    extracted = {}
    for tag, name in WSI_ACQUISITION_TAGS.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
            elif hasattr(ds, name):
                value = getattr(ds, name, None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _extract_slide_specimen_tags(ds: Any) -> Dict[str, Any]:
    """Extract slide and specimen metadata."""
    extracted = {}
    for tag, name in SLIDE_SPECIMEN_TAGS.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
            elif hasattr(ds, name):
                value = getattr(ds, name, None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _extract_focus_scan_tags(ds: Any) -> Dict[str, Any]:
    """Extract focus and scanning parameters."""
    extracted = {}
    for tag, name in FOCUS_SCAN_TAGS.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
            elif hasattr(ds, name):
                value = getattr(ds, name, None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _extract_image_pyramid_tags(ds: Any) -> Dict[str, Any]:
    """Extract image pyramid and multi-resolution information."""
    extracted = {}
    for tag, name in IMAGE_PYRAMID_TAGS.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
            elif hasattr(ds, name):
                value = getattr(ds, name, None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _extract_optical_illumination_tags(ds: Any) -> Dict[str, Any]:
    """Extract optical and illumination settings."""
    extracted = {}
    for tag, name in OPTICAL_ILLUMINATION_TAGS.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
            elif hasattr(ds, name):
                value = getattr(ds, name, None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _extract_pathology_measurement_tags(ds: Any) -> Dict[str, Any]:
    """Extract pathology-specific measurements."""
    extracted = {}
    for tag, name in PATHOLOGY_MEASUREMENT_TAGS.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
            elif hasattr(ds, name):
                value = getattr(ds, name, None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _extract_staining_preparation_tags(ds: Any) -> Dict[str, Any]:
    """Extract staining and preparation information."""
    extracted = {}
    for tag, name in STAINING_PREPARATION_TAGS.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
            elif hasattr(ds, name):
                value = getattr(ds, name, None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _calculate_wsi_metrics(ds: Any) -> Dict[str, Any]:
    """Calculate derived WSI metrics and quality indicators."""
    metrics = {}
    try:
        if hasattr(ds, 'NumberOfFrames') and hasattr(ds, 'Rows') and hasattr(ds, 'Columns'):
            metrics['total_pixels_per_frame'] = ds.Rows * ds.Columns
            metrics['total_image_pixels'] = ds.NumberOfFrames * ds.Rows * ds.Columns
        if hasattr(ds, 'Rows'):
            metrics['image_height_pixels'] = ds.Rows
        if hasattr(ds, 'Columns'):
            metrics['image_width_pixels'] = ds.Columns
        if hasattr(ds, 'BitsAllocated') and hasattr(ds, 'BitsStored'):
            metrics['bits_per_sample'] = ds.BitsAllocated
            metrics['effective_bits'] = ds.BitsStored
        if hasattr(ds, 'SamplesPerPixel'):
            metrics['color_channels'] = ds.SamplesPerPixel
    except Exception as e:
        logger.debug(f"Could not calculate WSI metrics: {e}")
    return metrics


def _is_wsi_file(file_path: str) -> bool:
    """Check if file is likely a WSI/DICOM pathology file."""
    try:
        file_lower = file_path.lower()
        wsi_extensions = ['.dcm', '.dicom', '.wsi', '.svs', '.tiff', '.tif']
        has_wsi_ext = any(file_lower.endswith(ext) for ext in wsi_extensions)
        if has_wsi_ext:
            return True
        if file_lower.endswith('.dcm'):
            try:
                import pydicom
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                modality = getattr(ds, 'Modality', '')
                supported_pathology = ['WSI', 'PX', 'CS', 'SC', 'DG']
                if modality in supported_pathology:
                    return True
                if hasattr(ds, 'NumberOfFrames') and ds.NumberOfFrames > 100:
                    return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def _get_modality_specific_fields(ds: Any) -> Dict[str, Any]:
    """Extract modality-specific fields based on DICOM modality."""
    modality_fields = {}
    try:
        modality = getattr(ds, 'Modality', 'Unknown')
        modality_fields['pathology_modality'] = modality
        if modality == 'WSI':
            modality_fields['wsi_acquisition_detected'] = True
            modality_fields['whole_slide_imaging'] = True
        elif modality == 'PX':
            modality_fields['pathology_general_detected'] = True
        elif modality == 'CS':
            modality_fields['cystoscopy_detected'] = True
    except Exception as e:
        logger.debug(f"Could not extract modality-specific fields: {e}")
    return modality_fields


def _extract_quality_indicators(ds: Any) -> Dict[str, Any]:
    """Extract image quality indicators for pathology."""
    quality = {}
    try:
        if hasattr(ds, 'SpatialResolution'):
            quality['spatial_resolution_dpi'] = ds.SpatialResolution
        if hasattr(ds, 'ImageQualityFactor'):
            quality['image_quality_factor'] = ds.ImageQualityFactor
        if hasattr(ds, 'Magnification'):
            quality['magnification_factor'] = ds.Magnification
        if hasattr(ds, 'LensMagnification'):
            quality['lens_magnification'] = ds.LensMagnification
    except Exception as e:
        logger.debug(f"Could not extract quality indicators: {e}")
    return quality


def _extract_diagnostic_info(ds: Any) -> Dict[str, Any]:
    """Extract diagnostic and interpretation information."""
    diagnostic = {}
    try:
        if hasattr(ds, 'DiagnosticDescription'):
            diagnostic['diagnostic_description'] = ds.DiagnosticDescription
        if hasattr(ds, 'DiagnosticReportID'):
            diagnostic['diagnostic_report_id'] = ds.DiagnosticReportID
        if hasattr(ds, 'DiagnosticReportStatus'):
            diagnostic['diagnostic_report_status'] = ds.DiagnosticReportStatus
        if hasattr(ds, 'PerformingPhysicianName'):
            diagnostic['performing_physician'] = ds.PerformingPhysicianName
        if hasattr(ds, 'ReferringPhysicianName'):
            diagnostic['referring_physician'] = ds.ReferringPhysicianName
    except Exception as e:
        logger.debug(f"Could not extract diagnostic info: {e}")
    return diagnostic


def extract_scientific_dicom_fits_ultimate_advanced_extension_x(file_path: str) -> Dict[str, Any]:
    """
    Extract comprehensive DICOM metadata for pathology/whole slide imaging files.

    This function provides deep extraction of WSI DICOM files, supporting various
    pathology workflows including histology, cytology, and digital pathology modalities.
    The extraction includes acquisition parameters, slide metadata, focus information,
    optical settings, and pathology-specific measurements.

    Args:
        file_path: Path to the WSI/DICOM pathology file

    Returns:
        Dict containing:
        - extension_x_detected: bool indicating WSI/pathology detection
        - fields_extracted: count of successfully extracted fields
        - pathology_modality: detected modality type
        - wsi_metadata: comprehensive WSI acquisition and scanning parameters
        - slide_specimen_metadata: slide and specimen information
        - focus_scan_parameters: focus and scanning details
        - image_pyramid_info: multi-resolution image information
        - optical_illumination_settings: optical and illumination configuration
        - pathology_measurements: pathology-specific measurements
        - staining_preparation: staining and preparation information
        - derived_metrics: calculated metrics and quality indicators
        - quality_indicators: image quality parameters
        - diagnostic_information: diagnostic and interpretation data
    """
    result = {
        "extension_x_detected": False,
        "fields_extracted": 0,
        "extension_x_type": "pathology_wsi",
        "extension_x_version": "2.0.0",
        "pathology_modality": None,
        "wsi_metadata": {},
        "slide_specimen_metadata": {},
        "focus_scan_parameters": {},
        "image_pyramid_info": {},
        "optical_illumination_settings": {},
        "pathology_measurements": {},
        "staining_preparation": {},
        "derived_metrics": {},
        "quality_indicators": {},
        "diagnostic_information": {},
        "extraction_errors": [],
    }

    try:
        if not _is_wsi_file(file_path):
            logger.debug(f"File {file_path} does not appear to be a WSI/pathology DICOM file")
            return result

        try:
            import pydicom
            ds = pydicom.dcmread(file_path, stop_before_pixels=True)
        except ImportError:
            logger.warning("pydicom not available for WSI extraction")
            result["extraction_errors"].append("pydicom library not available")
            return result
        except Exception as e:
            logger.error(f"Failed to read DICOM file: {e}")
            result["extraction_errors"].append(f"Failed to read file: {str(e)}")
            return result

        result["extension_x_detected"] = True
        result["pathology_modality"] = getattr(ds, 'Modality', 'Unknown')

        wsi_acquisition = _extract_wsi_acquisition_tags(ds)
        slide_specimen = _extract_slide_specimen_tags(ds)
        focus_scan = _extract_focus_scan_tags(ds)
        image_pyramid = _extract_image_pyramid_tags(ds)
        optical_illumination = _extract_optical_illumination_tags(ds)
        pathology_measurements = _extract_pathology_measurement_tags(ds)
        staining_preparation = _extract_staining_preparation_tags(ds)
        modality_fields = _get_modality_specific_fields(ds)
        quality_indicators = _extract_quality_indicators(ds)
        diagnostic_info = _extract_diagnostic_info(ds)
        derived_metrics = _calculate_wsi_metrics(ds)

        result["wsi_metadata"] = wsi_acquisition
        result["slide_specimen_metadata"] = slide_specimen
        result["focus_scan_parameters"] = focus_scan
        result["image_pyramid_info"] = image_pyramid
        result["optical_illumination_settings"] = optical_illumination
        result["pathology_measurements"] = pathology_measurements
        result["staining_preparation"] = staining_preparation
        result["derived_metrics"] = derived_metrics
        result["quality_indicators"] = quality_indicators
        result["diagnostic_information"] = diagnostic_info

        total_fields = (
            len(wsi_acquisition) + len(slide_specimen) + len(focus_scan) +
            len(image_pyramid) + len(optical_illumination) + len(pathology_measurements) +
            len(staining_preparation) + len(modality_fields) + len(quality_indicators) +
            len(diagnostic_info) + len(derived_metrics)
        )
        result["fields_extracted"] = total_fields

        logger.debug(f"Extension X extracted {total_fields} fields from WSI file")

    except Exception as e:
        logger.error(f"Error in WSI extraction: {e}")
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_x_field_count() -> int:
    """Returns the number of DICOM tags defined in this extension module."""
    return len(WSI_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_x_version() -> str:
    """Returns the version number of this extension module."""
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_x_description() -> str:
    """Returns a description of this extension module."""
    return ("Comprehensive pathology and whole slide imaging (WSI) metadata extraction. "
            "Supports digital pathology workflows including histology, cytology, and "
            "specialized WSI modalities. Extracts acquisition parameters, slide metadata, "
            "focus information, optical settings, staining details, and pathology-specific "
            "measurements for comprehensive digital pathology analysis.")


def get_scientific_dicom_fits_ultimate_advanced_extension_x_modalities() -> List[str]:
    """Returns list of supported DICOM modalities for this extension."""
    return ["WSI", "PX", "CS", "SC", "DG", "SD", "SM"]


def get_scientific_dicom_fits_ultimate_advanced_extension_x_supported_formats() -> List[str]:
    """Returns list of supported file formats for this extension."""
    return [".dcm", ".dicom", ".wsi", ".svs", ".tiff", ".tif"]


def get_scientific_dicom_fits_ultimate_advanced_extension_x_category() -> str:
    """Returns the category classification for this extension."""
    return "Pathology and Whole Slide Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_x_keywords() -> List[str]:
    """Returns keywords associated with this extension for searchability."""
    return [
        "pathology", "whole slide imaging", "WSI", "histology", "cytology",
        "digital pathology", "slide scanner", "specimen", "staining",
        "immunohistochemistry", "IHC", "microscopy", "tissue section",
        "optical path", "focal plane", "multi-resolution", "image pyramid"
    ]
