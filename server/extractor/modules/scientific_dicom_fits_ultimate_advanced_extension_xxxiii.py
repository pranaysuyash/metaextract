"""
Scientific DICOM/FITS Ultimate Advanced Extension XXXIII - Ophthalmic Imaging

This module provides comprehensive extraction of ophthalmic imaging parameters
including retinal scans, OCT, fundus photography, and visual field tests.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXXIII_AVAILABLE = True

OPHTHALMIC_IMAGING = {
    (0x0022, 0x0001): "eye_movement_captured",
    (0x0022, 0x0003): "visual_field_horizontal_extent",
    (0x0022, 0x0004): "visual_field_vertical_extent",
    (0x0022, 0x0005): "visual_field_test_point_sequence",
    (0x0022, 0x0006): "visual_field_test_point",
    (0x0022, 0x0007): "visual_field_test_point_sensitivity",
    (0x0022, 0x0008): "visual_field_test_point_reliability",
    (0x0022, 0x0010): "ophthalmic_frame_location_sequence",
    (0x0022, 0x0011): "reference_coordinate_system",
    (0x0022, 0x0012): "visual_field_test_reliability_indicator",
    (0x0022, 0x0015): "visual_field_index_values",
    (0x0022, 0x0016): "visual_field_regression_indicator",
    (0x0022, 0x0017): "visual_field_globals_sequence",
    (0x0022, 0x0018): "visual_field_global_result_index",
    (0x0022, 0x0019): "visual_field_global_result_value",
    (0x0022, 0x0020): "visual_field_threshold_data",
    (0x0022, 0x0021): "visual_field_test_pattern",
    (0x0022, 0x0022): "ophthalmic_patient_history_sequence",
    (0x0022, 0x0023): "metabolic_state_prior_to_imaging",
    (0x0022, 0x0024): "visual_field_test_duration",
    (0x0022, 0x0025): "visual_field_test_point_sequence",
    (0x0022, 0x0030): "ophthalmic_acquisition_device_type",
    (0x0022, 0x0031): "ophthalmic_image_laterality",
    (0x0022, 0x0032): "ophthalmic_field_of_view_sequence",
    (0x0022, 0x0033): "ophthalmic_field_of_view_description",
    (0x0022, 0x0034): "ophthalmic_field_of_view_rotation",
    (0x0022, 0x0035): "ophthalmic_field_of_view_reflection",
    (0x0022, 0x0036): "ophthalmic_acquisition_device_calibration_sequence",
    (0x0022, 0x0037): "ophthalmic_acquisition_device_parameter_id",
    (0x0022, 0x0038): "ophthalmic_acquisition_device_parameter_value",
    (0x0022, 0x0039): "ophthalmic_acquisition_device_parameter_unit",
    (0x0022, 0x0040): "ophthalmic_image_type",
    (0x0022, 0x0041): "ophthalmic_image_type_description",
    (0x0022, 0x0042): "scan_pattern_type",
    (0x0022, 0x0043): "reference_plane_normal",
    (0x0022, 0x0044): "reference_plane_description",
    (0x0022, 0x0045): "reference_plane_distance",
    (0x0022, 0x0046): "reference_plane_orientation",
    (0x0022, 0x0047): "depth_scan_range",
    (0x0022, 0x0048): "depth_scan_resolution",
    (0x0022, 0x0049): "maximum_depth_distortion",
    (0x0022, 0x004A): "along_scan_distortion",
    (0x0022, 0x004B): "maximum_angular_distortion",
    (0x0022, 0x004C): "maximum_depth_under_sampling",
    (0x0022, 0x004D): "coherence_gate_position",
    (0x0022, 0x004E): "coherence_gate_width",
    (0x0022, 0x0050): "ophthalmic_volume_description",
    (0x0022, 0x0051): "ophthalmic_acquisition_method_code_sequence",
    (0x0022, 0x0052): "ophthalmic_acquisition_method",
    (0x0022, 0x0053): "scan_pattern_code_sequence",
    (0x0022, 0x0054): "scan_pattern",
    (0x0022, 0x0060): "referenced_image_sequence",
    (0x0022, 0x0061): "referenced_image_number",
    (0x0022, 0x0062): "display_window_horizontal_lower_bound",
    (0x0022, 0x0063): "display_window_horizontal_upper_bound",
    (0x0022, 0x0064): "display_window_vertical_lower_bound",
    (0x0022, 0x0065): "display_window_vertical_upper_bound",
    (0x0022, 0x0070): "ophthalmic_quality_metric_sequence",
    (0x0022, 0x0071): "ophthalmic_quality_metric_type",
    (0x0022, 0x0072): "ophthalmic_quality_metric_value",
    (0x0022, 0x0073): "ophthalmic_quality_metric_unit",
    (0x0022, 0x0080): "ophthalmic_map_quality_rating_sequence",
    (0x0022, 0x0081): "ophthalmic_map_quality_rating",
    (0x0022, 0x0082): "ophthalmic_map_quality_rating_description",
    (0x0022, 0x0090): "stereometric_intervals_sequence",
    (0x0022, 0x0091): "stereometric_interval",
    (0x0022, 0x0092): "stereometric_interval_count",
    (0x0022, 0x0093): "number_of_stereometric_intervals",
    (0x0022, 0x0094): "stereometric_measurements_sequence",
    (0x0022, 0x0095): "stereometric_measurement_value",
    (0x0022, 0x0096): "stereometric_measurement_unit",
    (0x0022, 0x00A0): "ophthalmic_rim_border_sequence",
    (0x0022, 0x00A1): "rim_border_description",
    (0x0022, 0x00A2): "rim_border_radius",
    (0x0022, 0x00A3): "rim_border_count",
    (0x0022, 0x00A4): "rim_border_coordinates_sequence",
    (0x0022, 0x00A5): "rim_border_x_coordinate",
    (0x0022, 0x00A6): "rim_border_y_coordinate",
    (0x0022, 0x00B0): "optic_disc_cup_sequence",
    (0x0022, 0x00B1): "optic_disc_cup_description",
    (0x0022, 0x00B2): "optic_disc_cup_horizontal_extent",
    (0x0022, 0x00B3): "optic_disc_cup_vertical_extent",
    (0x0022, 0x00B4): "optic_disc_cup_area",
    (0x0022, 0x00B5): "optic_disc_cup_area_unit",
    (0x0022, 0x00C0): "optic_disc_cup_to_disc_ratio_sequence",
    (0x0022, 0x00C1): "optic_disc_cup_to_disc_horizontal_ratio",
    (0x0022, 0x00C2): "optic_disc_cup_to_disc_vertical_ratio",
    (0x0022, 0x00D0): "optic_disc_diameter_sequence",
    (0x0022, 0x00D1): "optic_disc_diameter_horizontal",
    (0x0022, 0x00D2): "optic_disc_diameter_vertical",
    (0x0022, 0x00E0): "optic_disc_radius_sequence",
    (0x0022, 0x00E1): "optic_disc_radius_horizontal",
    (0x0022, 0x00E2): "optic_disc_radius_vertical",
    (0x0022, 0x00F0): "fundus_photography_fov_type",
    (0x0022, 0x00F1): "fundus_photography_fov_description",
    (0x0022, 0x00F2): "fundus_photography_fov_rotation",
    (0x0022, 0x0100): "ophthalmic_camera_calibration_sequence",
    (0x0022, 0x0101): "ophthalmic_camera_calibration_focal_length",
    (0x0022, 0x0102): "ophthalmic_camera_calibration_principal_point",
    (0x0022, 0x0103): "ophthalmic_camera_calibration_distortion_correction",
    (0x0022, 0x0110): "macular_grid_thickness_sequence",
    (0x0022, 0x0111): "macular_grid_thickness_horizontal",
    (0x0022, 0x0112): "macular_grid_thickness_vertical",
    (0x0022, 0x0113): "macular_grid_spacing_sequence",
    (0x0022, 0x0114): "macular_grid_spacing_horizontal",
    (0x0022, 0x0115): "macular_grid_spacing_vertical",
    (0x0022, 0x0120): "ophthalmic_angiographic_quality_metric_sequence",
    (0x0022, 0x0121): "ophthalmic_angiographic_quality_metric_type",
    (0x0022, 0x0122): "ophthalmic_angiographic_quality_metric_value",
    (0x0022, 0x0130): "angiographic_exposure_compensation_sequence",
    (0x0022, 0x0131): "angiographic_exposure_compensation_value",
    (0x0022, 0x0140): "ophthalmic_angiography_image_type_code_sequence",
    (0x0022, 0x0141): "ophthalmic_angiography_image_type",
    (0x0022, 0x0150): "ophthalmic_fundus_grade_sequence",
    (0x0022, 0x0151): "ophthalmic_fundus_grade",
    (0x0022, 0x0152): "ophthalmic_fundus_grade_description",
    (0x0022, 0x0160): "ophthalmic_biomarker_measurement_sequence",
    (0x0022, 0x0161): "ophthalmic_biomarker_measurement_type",
    (0x0022, 0x0162): "ophthalmic_biomarker_measurement_value",
    (0x0022, 0x0163): "ophthalmic_biomarker_measurement_unit",
    (0x0022, 0x0170): "ophthalmic_elastography_sequence",
    (0x0022, 0x0171): "ophthalmic_elastography_type",
    (0x0022, 0x0172): "ophthalmic_elastography_measurement_value",
    (0x0022, 0x0180): "implicit_modulation_transfer_function_sequence",
    (0x0022, 0x0181): "implicit_modulation_transfer_function_parameter",
    (0x0022, 0x0182): "implicit_modulation_transfer_function_value",
    (0x0022, 0x0190): "explicit_modulation_transfer_function_sequence",
    (0x0022, 0x0191): "explicit_modulation_transfer_function_parameter",
    (0x0022, 0x0192): "explicit_modulation_transfer_function_value",
}

INTRAOCULAR_LENS = {
    (0x0022, 0x0200): "intraocular_lens_parameters_sequence",
    (0x0022, 0x0201): "intraocular_lens_power",
    (0x0022, 0x0202): "intraocular_lens_constant_a",
    (0x0022, 0x0203): "intraocular_lens_constant_a0",
    (0x0022, 0x0204): "intraocular_lens_constant_a1",
    (0x0022, 0x0205): "intraocular_lens_constant_a2",
    (0x0022, 0x0206): "intraocular_lens_steepest_keratometry",
    (0x0022, 0x0207): "intraocular_lens_average_keratometry",
    (0x0022, 0x0208): "intraocular_lens_axial_length",
    (0x0022, 0x0209): "intraocular_lens_predicted_refraction",
    (0x0022, 0x0210): "intraocular_lens_calculation_formula",
    (0x0022, 0x0211): "intraocular_lens_formula_version",
    (0x0022, 0x0212): "intraocular_lens_formula_name",
    (0x0022, 0x0213): "intraocular_lens_formula_comment",
    (0x0022, 0x0220): "iol_master_eye_selection",
    (0x0022, 0x0221): "iol_master_eye",
    (0x0022, 0x0230): "pre_op_keratometry_sequence",
    (0x0022, 0x0231): "pre_op_keratometry_value",
    (0x0022, 0x0232): "pre_op_keratometry_axis",
}

KERATOMETRY = {
    (0x0022, 0x0300): "keratometry_sequence",
    (0x0022, 0x0301): "keratometry_value",
    (0x0022, 0x0302): "keratometry_axis",
    (0x0022, 0x0303): "keratometry_type",
    (0x0022, 0x0304): "keratometry_description",
    (0x0022, 0x0305): "simulated_keratometry_sequence",
    (0x0022, 0x0306): "simulated_keratometry_value",
    (0x0022, 0x0307): "simulated_keratometry_axis",
    (0x0022, 0x0310): "keratometry_reading_sequence",
    (0x0022, 0x0311): "keratometry_reading_value",
    (0x0022, 0x0312): "keratometry_reading_axis",
    (0x0022, 0x0320): "keratometry_instrument_settings_sequence",
    (0x0022, 0x0321): "keratometry_instrument_magnification",
    (0x0022, 0x0322): "keratometry_instrument_calibration",
}

REFRACTION = {
    (0x0022, 0x0400): "refraction_sequence",
    (0x0022, 0x0401): "sphere_power",
    (0x0022, 0x0402): "cylinder_power",
    (0x0022, 0x0403): "cylinder_axis",
    (0x0022, 0x0404): "refraction_type",
    (0x0022, 0x0405): "refraction_description",
    (0x0022, 0x0406): "pupil_diameter",
    (0x0022, 0x0407): "pupil_dilation",
    (0x0022, 0x0408): "vertex_distance",
    (0x0022, 0x0409): "near_add",
    (0x0022, 0x0410): "intermediate_add",
    (0x0022, 0x0411): "distance_add",
    (0x0022, 0x0412): "sphere_equivalent",
    (0x0022, 0x0420): "corneal_topography_sequence",
    (0x0022, 0x0421): "corneal_topography_type",
    (0x0022, 0x0422): "corneal_topography_description",
    (0x0022, 0x0423): "corneal_topography_value",
    (0x0022, 0x0430): "wavefront_aberration_sequence",
    (0x0022, 0x0431): "wavefront_aberration_type",
    (0x0022, 0x0432): "wavefront_aberration_description",
    (0x0022, 0x0433): "wavefront_aberration_value",
    (0x0022, 0x0440): "subjective_refraction_sequence",
    (0x0022, 0x0441): "subjective_refraction_value",
    (0x0022, 0x0442): "subjective_refraction_axis",
    (0x0022, 0x0450): "objective_refraction_sequence",
    (0x0022, 0x0451): "objective_refraction_value",
    (0x0022, 0x0452): "objective_refraction_axis",
}

OPHTHALMIC_TOTAL_TAGS = (
    OPHTHALMIC_IMAGING | INTRAOCULAR_LENS | KERATOMETRY | REFRACTION
)


def _extract_ophthalmic_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in OPHTHALMIC_TOTAL_TAGS.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _is_ophthalmic_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            try:
                import pydicom
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                modality = getattr(ds, 'Modality', '')
                if modality in ['OP', 'OT', 'MR', 'CT']:
                    return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xxxiii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xxxiii_detected": False,
        "fields_extracted": 0,
        "extension_xxxiii_type": "ophthalmic_imaging",
        "extension_xxxiii_version": "2.0.0",
        "ophthalmic_imaging": {},
        "intraocular_lens": {},
        "keratometry": {},
        "refraction": {},
        "extraction_errors": [],
    }

    try:
        if not _is_ophthalmic_file(file_path):
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

        result["extension_xxxiii_detected"] = True

        ophthalmic_data = _extract_ophthalmic_tags(ds)

        result["ophthalmic_imaging"] = {
            k: v for k, v in ophthalmic_data.items()
            if k in OPHTHALMIC_IMAGING.values()
        }
        result["intraocular_lens"] = {
            k: v for k, v in ophthalmic_data.items()
            if k in INTRAOCULAR_LENS.values()
        }
        result["keratometry"] = {
            k: v for k, v in ophthalmic_data.items()
            if k in KERATOMETRY.values()
        }
        result["refraction"] = {
            k: v for k, v in ophthalmic_data.items()
            if k in REFRACTION.values()
        }

        result["fields_extracted"] = len(ophthalmic_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxiii_field_count() -> int:
    return len(OPHTHALMIC_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxiii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxiii_description() -> str:
    return (
        "Ophthalmic imaging metadata extraction. Provides comprehensive coverage of "
        "retinal imaging, OCT, fundus photography, visual field tests, intraocular "
        "lens parameters, keratometry, and refraction measurements for eye care."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxiii_modalities() -> List[str]:
    return ["OP", "OT", "MR", "CT"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxiii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxiii_category() -> str:
    return "Ophthalmic Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxiii_keywords() -> List[str]:
    return [
        "ophthalmic", "retina", "OCT", "fundus", "visual field", "glaucoma",
        "macula", "optic disc", "keratometry", "refraction", "IOL", "cornea"
    ]
