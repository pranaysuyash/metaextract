"""
Scientific DICOM/FITS Ultimate Advanced Extension XXXI - Microscopy and Digital Pathology

This module provides comprehensive extraction of microscopy and digital pathology
parameters including histological staining, virtual slides, and histopathology metadata.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXXI_AVAILABLE = True

MICROSCOPY_OPTICAL_SYSTEM = {
    (0x0048, 0x0001): "microscopy_type",
    (0x0048, 0x0002): "magnification_power",
    (0x0048, 0x0003): "numerical_aperture",
    (0x0048, 0x0004): "objective_lens",
    (0x0048, 0x0005): "objective_lens_magnification",
    (0x0048, 0x0006): "objective_lens_numeric_aperture",
    (0x0048, 0x0007): "total_magnification",
    (0x0048, 0x0008): "field_number",
    (0x0048, 0x0009): "field_of_view",
    (0x0048, 0x000A): "field_of_view_unit",
    (0x0048, 0x000B): "optical_system",
    (0x0048, 0x000C): "microscope_manufacturer",
    (0x0048, 0x000D): "microscope_model",
    (0x0048, 0x000E): "microscope_serial_number",
    (0x0048, 0x000F): "microscope_software_version",
    (0x0048, 0x0010): "condenser_type",
    (0x0048, 0x0011): "condenser_numerical_aperture",
    (0x0048, 0x0012): "illumination_type",
    (0x0048, 0x0013): "illumination_wavelength",
    (0x0048, 0x0014): "filter_set",
    (0x0048, 0x0015): "filter_characteristics",
    (0x0048, 0x0016): "polarization_state",
    (0x0048, 0x0017): "phase_contrast_setting",
    (0x0048, 0x0018): "nominal_interpixel_spacing",
    (0x0048, 0x0019): "actual_interpixel_spacing",
    (0x0048, 0x001A): "nominal_vertical_interpixel_spacing",
    (0x0048, 0x001B): "actual_vertical_interpixel_spacing",
    (0x0048, 0x001C): "pixel_spacing_sequence",
    (0x0048, 0x001D): "microscope_description_sequence",
}

HISTOPATHOLOGY_STAINING = {
    (0x0048, 0x0100): "stain_type",
    (0x0048, 0x0101): "stain_name",
    (0x0048, 0x0102): "stain_description",
    (0x0048, 0x0103): "stain_protocol",
    (0x0048, 0x0104): "stain_reagent",
    (0x0048, 0x0105): "stain_reagent_lot_number",
    (0x0048, 0x0106): "stain_reagent_expiration_date",
    (0x0048, 0x0107): "stain_dye_concentration",
    (0x0048, 0x0108): "stain_dye_solvent",
    (0x0048, 0x0109): "stain_incubation_time",
    (0x0048, 0x010A): "stain_incubation_temperature",
    (0x0048, 0x010B): "stain_sequence",
    (0x0048, 0x010C): "multiple_stain_sequence",
    (0x0048, 0x010D): "slide_stain_sequence",
    (0x0048, 0x010E): "cover_glass_sequence",
    (0x0048, 0x0110): "cover_glass_thickness",
    (0x0048, 0x0111): "cover_glass_type",
    (0x0048, 0x0112): "mounting_medium_type",
    (0x0048, 0x0113): "mounting_medium_refractive_index",
}

VIRTUAL_SLIDE_METADATA = {
    (0x0048, 0x0200): "image_type",
    (0x0048, 0x0201): "virtual_slide_identifier",
    (0x0048, 0x0202): "virtual_slide_description",
    (0x0048, 0x0203): "scan_device_uid",
    (0x0048, 0x0204): "scan_software_uid",
    (0x0048, 0x0205): "scan_software_version",
    (0x0048, 0x0206): "scan_date_time",
    (0x0048, 0x0207): "scan_duration",
    (0x0048, 0x0208): "number_of_focal_planes",
    (0x0048, 0x0209): "focal_plane_sequence",
    (0x0048, 0x020A): "focal_plane_z_position",
    (0x0048, 0x020B): "number_of optical paths",
    (0x0048, 0x020C): "optical_path_sequence",
    (0x0048, 0x020D): "optical_path_identifier",
    (0x0048, 0x020E): "optical_path_description",
    (0x0048, 0x0210): "slide_reference_coordinates",
    (0x0048, 0x0211): "slide_origin_identifier",
    (0x0048, 0x0212): "slide_center_coordinates",
    (0x0048, 0x0213): "slide_upper_left_coordinates",
    (0x0048, 0x0214): "slide_lower_right_coordinates",
    (0x0048, 0x0215): "slide_scan_resolution",
    (0x0048, 0x0216): "total_pixel_matrix_columns",
    (0x0048, 0x0217): "total_pixel_matrix_rows",
    (0x0048, 0x0218): "levels_available",
    (0x0048, 0x0219): "level_description_sequence",
    (0x0048, 0x021A): "level_magnification",
    (0x0048, 0x021B): "level_downscale_factor",
    (0x0048, 0x021C): "tile_pixel_matrix_columns",
    (0x0048, 0x021D): "tile_pixel_matrix_rows",
    (0x0048, 0x021E): "number_of_tiles",
    (0x0048, 0x021F): "tile_sequence",
    (0x0048, 0x0220): "tile_position_in_total_pixel_matrix",
    (0x0048, 0x0221): "tile_position_reference",
    (0x0048, 0x0222): "tile_position_coordinates",
    (0x0048, 0x0223): "tile_dimension",
    (0x0048, 0x0224): "tile_encoded_image_size",
    (0x0048, 0x0225): "tile_type",
    (0x0048, 0x0226): "compression_type",
    (0x0048, 0x0227): "compression_quality_factor",
}

SLIDE_SPECIMEN_METADATA = {
    (0x0040, 0x0550): "specimen_preparation_step_sequence",
    (0x0040, 0x0551): "specimen_preparation_content_sequence",
    (0x0040, 0x0552): "specimen_preparation_step_index",
    (0x0040, 0x0553): "specimen_preparation_step_description",
    (0x0040, 0x0554): "specimen_preparation_step_absolute_position",
    (0x0040, 0x0555): "specimen_preparation_step_relative_position",
    (0x0040, 0x0560): "specimen_staining_sequence",
    (0x0040, 0x0561): "specimen_staining_laterality",
    (0x0040, 0x0562): "specimen_staining_annotation_sequence",
    (0x0040, 0x0563): "specimen_staining_protocol",
    (0x0040, 0x0564): "specimen_staining_description",
    (0x0040, 0x0565): "specimen_staining_agent",
    (0x0040, 0x0566): "specimen_staining_agent_sequence",
    (0x0040, 0x0567): "specimen_staining_concentration",
    (0x0048, 0x0300): "slide_specimen_path_sequence",
    (0x0048, 0x0301): "slide_specimen_path_description",
    (0x0048, 0x0302): "slide_specimen_path_uid",
    (0x0048, 0x0303): "specimen_tissue_selection_sequence",
    (0x0048, 0x0304): "specimen_tissue_localization",
    (0x0048, 0x0305): "specimen_block_sequence",
    (0x0048, 0x0306): "block_identifier",
    (0x0048, 0x0307): "block_description",
    (0x0048, 0x0308): "block_section_sequence",
    (0x0048, 0x0309): "block_section_index",
    (0x0048, 0x030A): "block_section_thickness",
    (0x0048, 0x030B): "block_section_location",
    (0x0048, 0x030C): "block_section_orientation",
    (0x0048, 0x030D): "block_section_stain_sequence",
    (0x0048, 0x0310): "image_frame_type_sequence",
    (0x0048, 0x0311): "image_frame_type",
    (0x0048, 0x0312): "image_frame_origin_sequence",
    (0x0048, 0x0313): "image_frame_origin",
    (0x0048, 0x0314): "optical_path_origin_sequence",
    (0x0048, 0x0315): "optical_path_origin",
    (0x0048, 0x0316): "image_frame_tile_name",
    (0x0048, 0x0317): "total_pixel_matrix_focal_planes",
}

IMMUNOHISTOCHEMISTRY = {
    (0x0048, 0x0400): "ihc_marker",
    (0x0048, 0x0401): "ihc_marker_name",
    (0x0048, 0x0402): "ihc_marker_result",
    (0x0048, 0x0403): "ihc_scoring_system",
    (0x0048, 0x0404): "ihc_positive_cells_percentage",
    (0x0048, 0x0405): "ihc_staining_intensity",
    (0x0048, 0x0406): "ihc_proportion_score",
    (0x0048, 0x0407): "ihc_intensity_score",
    (0x0048, 0x0408): "ihc_combined_score",
    (0x0048, 0x0409): "ihc_negative_control",
    (0x0048, 0x040A): "ihc_positive_control",
    (0x0048, 0x040B): "ihc_antibody",
    (0x0048, 0x040C): "ihc_antibody_catalog_number",
    (0x0048, 0x040D): "ihc_antibody_lot_number",
    (0x0048, 0x040E): "ihc_antibody_dilution",
    (0x0048, 0x040F): "ihc_visualization_method",
    (0x0048, 0x0410): "ihc_chromogen",
    (0x0048, 0x0411): "ihc_counterstain",
    (0x0048, 0x0412): "ihc_protocol",
    (0x0048, 0x0413): "ihc_assay_type",
    (0x0048, 0x0414): "ihc_quantification_method",
    (0x0048, 0x0415): "ihc_region_of_interest",
    (0x0048, 0x0416): "ihc_region_of_interest_description",
    (0x0048, 0x0417): "ihc_region_of_interest_area",
    (0x0048, 0x0418): "ihc_measurement_sequence",
    (0x0048, 0x0419): "ihc_measurement_value",
    (0x0048, 0x041A): "ihc_measurement_unit",
}

CONFOCAL_MICROSCOPY = {
    (0x0048, 0x0500): "confocal_imaging_mode",
    (0x0048, 0x0501): "laser_wavelength",
    (0x0048, 0x0502): "laser_power",
    (0x0048, 0x0503): "laser_spot_size",
    (0x0048, 0x0504): "pinhole_diameter",
    (0x0048, 0x0505): "pinhole_shape",
    (0x0048, 0x0506): "detector_gain",
    (0x0048, 0x0507): "detector_offset",
    (0x0048, 0x0508): "photomultiplier_voltage",
    (0x0048, 0x0509): "avalanche_photodiode_settings",
    (0x0048, 0x050A): "scan_type",
    (0x0048, 0x050B): "scan_direction",
    (0x0048, 0x050C): "scan_line_density",
    (0x0048, 0x050D): "scan_frame_time",
    (0x0048, 0x050E): "number_of_scan_lines",
    (0x0048, 0x050F): "pixel_dwell_time",
    (0x0048, 0x0510): "z_stack_sequence",
    (0x0048, 0x0511): "z_stack_start_position",
    (0x0048, 0x0512): "z_stack_step_size",
    (0x0048, 0x0513): "z_stack_number_of_steps",
    (0x0048, 0x0514): "z_stack_end_position",
    (0x0048, 0x0515): "multichannel_sequence",
    (0x0048, 0x0516): "channel_wavelength_sequence",
    (0x0048, 0x0517): "channel_label",
    (0x0048, 0x0518): "channel_acquisition_mode",
    (0x0048, 0x0519): "channel_spectral_filter",
    (0x0048, 0x051A): "channel_excitation_wavelength",
    (0x0048, 0x051B): "channel_emission_wavelength",
    (0x0048, 0x051C): "channel_detector_type",
    (0x0048, 0x051D): "channel_power",
    (0x0048, 0x051E): "channel_scan_mode",
}

ELECTRON_MICROSCOPY = {
    (0x0048, 0x0600): "electron_microscope_type",
    (0x0048, 0x0601): "electron_source_type",
    (0x0048, 0x0602): "accelerating_voltage",
    (0x0048, 0x0603): "beam_current",
    (0x0048, 0x0604): "spot_size",
    (0x0048, 0x0605): "magnification_calibration",
    (0x0048, 0x0606): "pixel_size_calibration",
    (0x0048, 0x0607): "calibration_unit",
    (0x0048, 0x0608): "specimen_holder_type",
    (0x0048, 0x0609): "specimen_tilt_angle",
    (0x0048, 0x060A): "specimen_rotation_angle",
    (0x0048, 0x060B): "vacuum_level",
    (0x0048, 0x060C): "gun_lens_setting",
    (0x0048, 0x060D): "condenser_lens_setting",
    (0x0048, 0x060E): "objective_lens_setting",
    (0x0048, 0x060F): "projection_lens_setting",
    (0x0048, 0x0610): "stigmator_setting",
    (0x0048, 0x0611): "astigmatism_correction",
    (0x0048, 0x0612): "defocus_value",
    (0x0048, 0x0613): "defocus_unit",
    (0x0048, 0x0614): "chromatic_aberration_correction",
    (0x0048, 0x0615): "spherical_aberration_correction",
    (0x0048, 0x0616): "energy_filter_type",
    (0x0048, 0x0617): "energy_filter_slit_width",
    (0x0048, 0x0618): "zero_loss_filter_setting",
    (0x0048, 0x0619): "detector_type",
    (0x0048, 0x061A): "detector_angle",
    (0x0048, 0x061B): "detector_collection_angle",
}

MICROSCOPY_TOTAL_TAGS = (
    MICROSCOPY_OPTICAL_SYSTEM | HISTOPATHOLOGY_STAINING | VIRTUAL_SLIDE_METADATA |
    SLIDE_SPECIMEN_METADATA | IMMUNOHISTOCHEMISTRY | CONFOCAL_MICROSCOPY | ELECTRON_MICROSCOPY
)


def _extract_microscopy_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    all_tags = MICROSCOPY_TOTAL_TAGS
    for tag, name in all_tags.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _is_microscopy_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            try:
                import pydicom
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                modality = getattr(ds, 'Modality', '')
                if modality in ['SM', 'GM', 'OT', 'PT', 'MR']:
                    return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xxxi(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xxxi_detected": False,
        "fields_extracted": 0,
        "extension_xxxi_type": "microscopy_digital_pathology",
        "extension_xxxi_version": "2.0.0",
        "optical_system": {},
        "staining": {},
        "virtual_slide": {},
        "specimen": {},
        "immunohistochemistry": {},
        "confocal": {},
        "electron_microscopy": {},
        "extraction_errors": [],
    }

    try:
        if not _is_microscopy_file(file_path):
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

        result["extension_xxxi_detected"] = True

        microscopy_data = _extract_microscopy_tags(ds)

        result["optical_system"] = {
            k: v for k, v in microscopy_data.items()
            if k in MICROSCOPY_OPTICAL_SYSTEM.values()
        }
        result["staining"] = {
            k: v for k, v in microscopy_data.items()
            if k in HISTOPATHOLOGY_STAINING.values()
        }
        result["virtual_slide"] = {
            k: v for k, v in microscopy_data.items()
            if k in VIRTUAL_SLIDE_METADATA.values()
        }
        result["specimen"] = {
            k: v for k, v in microscopy_data.items()
            if k in SLIDE_SPECIMEN_METADATA.values()
        }
        result["immunohistochemistry"] = {
            k: v for k, v in microscopy_data.items()
            if k in IMMUNOHISTOCHEMISTRY.values()
        }
        result["confocal"] = {
            k: v for k, v in microscopy_data.items()
            if k in CONFOCAL_MICROSCOPY.values()
        }
        result["electron_microscopy"] = {
            k: v for k, v in microscopy_data.items()
            if k in ELECTRON_MICROSCOPY.values()
        }

        total_fields = len(microscopy_data)
        result["fields_extracted"] = total_fields

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxi_field_count() -> int:
    return len(MICROSCOPY_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxi_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxi_description() -> str:
    return (
        "Microscopy and digital pathology metadata extraction. Provides comprehensive "
        "coverage of optical system parameters, histopathology staining, virtual slide "
        "metadata, specimen preparation, immunohistochemistry, confocal microscopy, "
        "and electron microscopy parameters for comprehensive digital pathology analysis."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxi_modalities() -> List[str]:
    return ["SM", "GM", "OT", "MR", "CT", "PT"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxi_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxi_category() -> str:
    return "Microscopy and Digital Pathology"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxi_keywords() -> List[str]:
    return [
        "microscopy", "digital pathology", "histopathology", "staining",
        "virtual slide", "WSI", "IHC", "immunohistochemistry", "confocal",
        "electron microscopy", "slide scanner", "whole slide imaging"
    ]
