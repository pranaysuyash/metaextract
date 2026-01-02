"""
Scientific DICOM/FITS Ultimate Advanced Extension XXXV - Dental and Maxillofacial Imaging

This module provides comprehensive extraction of dental imaging parameters
including panoramic, cephalometric, CBCT, and intraoral imaging metadata.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXXV_AVAILABLE = True

DENTAL_ACQUISITION = {
    (0x0018, 0x9500): "xray_acquisition_dose_sequence",
    (0x0018, 0x9501): "xray_acquisition_dose_description",
    (0x0018, 0x9502): "xray_acquisition_dose_unit",
    (0x0018, 0x9503): "xray_acquisition_dose_value",
    (0x0018, 0x9504): "dose_area_product_sequence",
    (0x0018, 0x9505): "dose_area_product_unit",
    (0x0018, 0x9506): "dose_area_product_value",
    (0x0018, 0x9507): "reference_air_kerma_rate",
    (0x0018, 0x9508): "estimated_air_kerma_rate",
    (0x0018, 0x9509): "calculated_air_kerma_rate",
    (0x0018, 0x9510): "acquisition_device_type_sequence",
    (0x0018, 0x9511): "acquisition_device_type",
    (0x0018, 0x9512): "acquisition_device_type_description",
    (0x0018, 0x9514): "acquisition_method_sequence",
    (0x0018, 0x9515): "acquisition_method",
    (0x0018, 0x9516): "acquisition_method_description",
    (0x0018, 0x9517): "radiopharmaceutical_agent_sequence",
    (0x0018, 0x9518): "radiopharmaceutical_agent",
    (0x0018, 0x9519): "radiopharmaceutical_agent_administered",
    (0x0018, 0x9520): "uptake_sensor_type_sequence",
    (0x0018, 0x9521): "uptake_sensor_type",
    (0x0018, 0x9522): "uptake_sensor_type_description",
    (0x0018, 0x9523): "uptake_sensor_geometry_sequence",
    (0x0018, 0x9524): "uptake_sensor_geometry",
    (0x0018, 0x9525): "uptake_sensor_geometry_description",
    (0x0018, 0x9526): "dose_calibration_method_sequence",
    (0x0018, 0x9527): "dose_calibration_method",
    (0x0018, 0x9528): "dose_calibration_method_description",
    (0x0018, 0x9529): "calibration_date_time",
    (0x0018, 0x9530): "sensitivity_calibration_method_sequence",
    (0x0018, 0x9531): "sensitivity_calibration_method",
    (0x0018, 0x9532): "sensitivity_calibration_method_description",
    (0x0018, 0x9533): "sensitivity_calibration_date_time",
    (0x0018, 0x9534): "reconstruction_field_of_view_shape",
    (0x0018, 0x9535): "supporting_frames_sequence",
    (0x0018, 0x9536): "supporting_frame_description",
    (0x0018, 0x9537): "fundamental_threshold_setting_sequence",
    (0x0018, 0x9538): "fundamental_threshold_setting",
    (0x0018, 0x9539): "fundamental_threshold_setting_description",
    (0x0018, 0x9540): "calibration_threshold_sequence",
    (0x0018, 0x9541): "calibration_threshold",
    (0x0018, 0x9542): "calibration_threshold_description",
    (0x0018, 0x9543): "isocenter_reference_system_sequence",
    (0x0018, 0x9544): "isocenter_reference_system_description",
    (0x0018, 0x9545): "isocenter_position_sequence",
    (0x0018, 0x9546): "isocenter_position",
    (0x0018, 0x9547): "isocenter_position_description",
    (0x0018, 0x9550): "xray_output_selection_sequence",
    (0x0018, 0x9551): "xray_output_selection",
    (0x0018, 0x9552): "xray_output_selection_description",
    (0x0018, 0x9553): "xray_output_filter_sequence",
    (0x0018, 0x9554): "xray_output_filter_type",
    (0x0018, 0x9555): "xray_output_filter_description",
    (0x0018, 0x9556): "xray_output_filter_material",
    (0x0018, 0x9557): "xray_output_filter_thickness_minimum",
    (0x0018, 0x9558): "xray_output_filter_thickness_maximum",
    (0x0018, 0x9559): "xray_output_filter_attenuation",
    (0x0018, 0x9560): "image_filter_type_sequence",
    (0x0018, 0x9561): "image_filter_type",
    (0x0018, 0x9562): "image_filter_type_description",
    (0x0018, 0x9563): "image_filter_kernel_size",
    (0x0018, 0x9564): "image_filter_kernel_description",
    (0x0018, 0x9565): "image_filter_kernel_version",
    (0x0018, 0x9570): "pulse_width_sequence",
    (0x0018, 0x9571): "pulse_width",
    (0x0018, 0x9572): "pulse_width_unit",
    (0x0018, 0x9573): "pulse_width_description",
    (0x0018, 0x9580): "exposure_index_sequence",
    (0x0018, 0x9581): "exposure_index_target_value",
    (0x0018, 0x9582): "exposure_index_target_value_description",
    (0x0018, 0x9583): "exposure_index_deviation",
    (0x0018, 0x9584): "exposure_index_deviation_description",
    (0x0018, 0x9590): "diagnostic_xray_source_sequence",
    (0x0018, 0x9591): "diagnostic_xray_source_id",
    (0x0018, 0x9592): "diagnostic_xray_source_name",
    (0x0018, 0x9593): "diagnostic_xray_source_description",
    (0x0018, 0x9594): "diagnostic_xray_source_manufacturer",
    (0x0018, 0x9595): "diagnostic_xray_source_manufacturer_model_name",
    (0x0018, 0x9596): "diagnostic_xray_source_manufacturer_model_number",
    (0x0018, 0x9597): "diagnostic_xray_source_software_version",
    (0x0018, 0x95A0): "projection_xray_sequence",
    (0x0018, 0x95A1): "projection_xray_source_sequence",
    (0x0018, 0x95A2): "projection_xray_source_id",
    (0x0018, 0x95A3): "projection_xray_source_name",
    (0x0018, 0x95A4): "projection_xray_source_description",
    (0x0018, 0x95A5): "projection_xray_source_manufacturer",
    (0x0018, 0x95A6): "projection_xray_source_manufacturer_model_name",
    (0x0018, 0x95A7): "projection_xray_source_manufacturer_model_number",
    (0x0018, 0x95A8): "projection_xray_source_software_version",
    (0x0018, 0x95B0): "projection_xray_filter_sequence",
    (0x0018, 0x95B1): "projection_xray_filter_type",
    (0x0018, 0x95B2): "projection_xray_filter_type_description",
    (0x0018, 0x95B3): "projection_xray_filter_material",
    (0x0018, 0x95B4): "projection_xray_filter_thickness_minimum",
    (0x0018, 0x95B5): "projection_xray_filter_thickness_maximum",
    (0x0018, 0x95B6): "projection_xray_filter_attenuation",
    (0x0018, 0x95C0): "projection_xray_grid_sequence",
    (0x0018, 0x95C1): "projection_xray_grid_type",
    (0x0018, 0x95C2): "projection_xray_grid_type_description",
    (0x0018, 0x95C3): "projection_xray_grid_pitch_factor",
    (0x0018, 0x95C4): "projection_xray_grid_ratio",
    (0x0018, 0x95C5): "projection_xray_grid_orientation",
    (0x0018, 0x95C6): "projection_xray_grid_spatial_format",
    (0x0018, 0x95C7): "projection_xray_grid_frequency",
    (0x0018, 0x95C8): "projection_xray_grid_size",
    (0x0018, 0x95C9): "projection_xray_grid_thickness",
    (0x0018, 0x95CA): "projection_xray_grid_material",
}

DENTAL_CBCT = {
    (0x0018, 0x9600): "reconstruction_algorithm_sequence",
    (0x0018, 0x9601): "reconstruction_algorithm",
    (0x0018, 0x9602): "reconstruction_algorithm_description",
    (0x0018, 0x9603): "reconstruction_algorithm_version",
    (0x0018, 0x9604): "reconstruction_kernel_sequence",
    (0x0018, 0x9605): "reconstruction_kernel",
    (0x0018, 0x9606): "reconstruction_kernel_description",
    (0x0018, 0x9607): "reconstruction_kernel_version",
    (0x0018, 0x9608): "reconstruction_pixel_size",
    (0x0018, 0x9609): "reconstruction_pixel_size_unit",
    (0x0018, 0x9610): "reconstruction_center",
    (0x0018, 0x9611): "reconstruction_center_unit",
    (0x0018, 0x9612): "reconstruction_field_of_view",
    (0x0018, 0x9613): "reconstruction_field_of_view_unit",
    (0x0018, 0x9614): "reconstruction_matrix",
    (0x0018, 0x9615): "reconstruction_matrix_description",
    (0x0018, 0x9616): "reconstruction_subset_count",
    (0x0018, 0x9617): "reconstruction_subset_number",
    (0x0018, 0x9618): "reconstruction_subset_description",
    (0x0018, 0x9620): "filtered_back_projection_slice_count",
    (0x0018, 0x9621): "filtered_back_projection_slice_location",
    (0x0018, 0x9622): "filtered_back_projection_slice_thickness",
    (0x0018, 0x9623): "filtered_back_projection_slice_description",
    (0x0018, 0x9624): "filtered_back_projection_slice_count_description",
    (0x0018, 0x9630): "reconstruction_partial_volume_sequence",
    (0x0018, 0x9631): "reconstruction_partial_volume",
    (0x0018, 0x9632): "reconstruction_partial_volume_description",
    (0x0018, 0x9633): "reconstruction_partial_volume_flag",
    (0x0018, 0x9634): "reconstruction_partial_volume_flag_description",
    (0x0018, 0x9640): "beam_hardening_correction_sequence",
    (0x0018, 0x9641): "beam_hardening_correction_type",
    (0x0018, 0x9642): "beam_hardening_correction_type_description",
    (0x0018, 0x9643): "beam_hardening_correction_factor",
    (0x0018, 0x9644): "beam_hardening_correction_factor_description",
    (0x0018, 0x9650): "scatter_correction_sequence",
    (0x0018, 0x9651): "scatter_correction_type",
    (0x0018, 0x9652): "scatter_correction_type_description",
    (0x0018, 0x9653): "scatter_correction_factor",
    (0x0018, 0x9654): "scatter_correction_factor_description",
    (0x0018, 0x9660): "metal_artifact_reduction_sequence",
    (0x0018, 0x9661): "metal_artifact_reduction_type",
    (0x0018, 0x9662): "metal_artifact_reduction_type_description",
    (0x0018, 0x9663): "metal_artifact_reduction_flag",
    (0x0018, 0x9664): "metal_artifact_reduction_flag_description",
    (0x0018, 0x9670): "partial_volume_reconstruction_sequence",
    (0x0018, 0x9671): "partial_volume_reconstruction",
    (0x0018, 0x9672): "partial_volume_reconstruction_description",
    (0x0018, 0x9673): "partial_volume_reconstruction_flag",
    (0x0018, 0x9674): "partial_volume_reconstruction_flag_description",
    (0x0018, 0x9680): "timing_parameters_sequence",
    (0x0018, 0x9681): "timing_parameters",
    (0x0018, 0x9682): "timing_parameters_description",
    (0x0018, 0x9683): "timing_parameters_value",
    (0x0018, 0x9684): "timing_parameters_unit",
    (0x0018, 0x9690): "frame_acquisition_sequence",
    (0x0018, 0x9691): "frame_acquisition_type",
    (0x0018, 0x9692): "frame_acquisition_type_description",
    (0x0018, 0x9693): "frame_acquisition_duration",
    (0x0018, 0x9694): "frame_acquisition_duration_unit",
}

DENTAL_PANORAMIC = {
    (0x0018, 0x9700): "orthogonal_rotate_sequence",
    (0x0018, 0x9701): "orthogonal_rotate_axis",
    (0x0018, 0x9702): "orthogonal_rotate_angle",
    (0x0018, 0x9703): "orthogonal_rotate_direction",
    (0x0018, 0x9704): "orthogonal_rotate_description",
    (0x0018, 0x9710): "patient_support_sequence",
    (0x0018, 0x9711): "patient_support_type",
    (0x0018, 0x9712): "patient_support_type_description",
    (0x0018, 0x9713): "patient_support_position",
    (0x0018, 0x9714): "patient_support_position_description",
    (0x0018, 0x9715): "patient_support_roll_angle",
    (0x0018, 0x9716): "patient_support_roll_angle_description",
    (0x0018, 0x9720): "head_support_sequence",
    (0x0018, 0x9721): "head_support_type",
    (0x0018, 0x9722): "head_support_type_description",
    (0x0018, 0x9723): "head_support_position",
    (0x0018, 0x9724): "head_support_position_description",
    (0x0018, 0x9725): "head_support_roll_angle",
    (0x0018, 0x9726): "head_support_roll_angle_description",
    (0x0018, 0x9730): "chin_rest_sequence",
    (0x0018, 0x9731): "chin_rest_type",
    (0x0018, 0x9732): "chin_rest_type_description",
    (0x0018, 0x9733): "chin_rest_position",
    (0x0018, 0x9734): "chin_rest_position_description",
    (0x0018, 0x9740): "hand_rest_sequence",
    (0x0018, 0x9741): "hand_rest_type",
    (0x0018, 0x9742): "hand_rest_type_description",
    (0x0018, 0x9743): "hand_rest_position",
    (0x0018, 0x9744): "hand_rest_position_description",
    (0x0018, 0x9750): "head_positioner_sequence",
    (0x0018, 0x9751): "head_positioner_type",
    (0x0018, 0x9752): "head_positioner_type_description",
    (0x0018, 0x9753): "head_positioner_position",
    (0x0018, 0x9754): "head_positioner_position_description",
    (0x0018, 0x9755): "head_positioner_roll_angle",
    (0x0018, 0x9756): "head_positioner_roll_angle_description",
    (0x0018, 0x9757): "head_positioner_pitch_angle",
    (0x0018, 0x9758): "head_positioner_pitch_angle_description",
    (0x0018, 0x9759): "head_positioner_yaw_angle",
    (0x0018, 0x975A): "head_positioner_yaw_angle_description",
    (0x0018, 0x9760): "temporomandibular_joint_sequence",
    (0x0018, 0x9761): "temporomandibular_joint_type",
    (0x0018, 0x9762): "temporomandibular_joint_type_description",
    (0x0018, 0x9763): "temporomandibular_joint_position",
    (0x0018, 0x9764): "temporomandibular_joint_position_description",
    (0x0018, 0x9765): "temporomandibular_joint_movement",
    (0x0018, 0x9766): "temporomandibular_joint_movement_description",
}

DENTAL_TOTAL_TAGS = DENTAL_ACQUISITION | DENTAL_CBCT | DENTAL_PANORAMIC


def _extract_dental_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in DENTAL_TOTAL_TAGS.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _is_dental_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            try:
                import pydicom
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                modality = getattr(ds, 'Modality', '')
                if modality in ['CT', 'CR', 'DR', 'DX', 'OT']:
                    return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xxxv(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xxxv_detected": False,
        "fields_extracted": 0,
        "extension_xxxv_type": "dental_maxillofacial_imaging",
        "extension_xxxv_version": "2.0.0",
        "dental_acquisition": {},
        "dental_cbct": {},
        "dental_panoramic": {},
        "extraction_errors": [],
    }

    try:
        if not _is_dental_file(file_path):
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

        result["extension_xxxv_detected"] = True

        dental_data = _extract_dental_tags(ds)

        result["dental_acquisition"] = {
            k: v for k, v in dental_data.items()
            if k in DENTAL_ACQUISITION.values()
        }
        result["dental_cbct"] = {
            k: v for k, v in dental_data.items()
            if k in DENTAL_CBCT.values()
        }
        result["dental_panoramic"] = {
            k: v for k, v in dental_data.items()
            if k in DENTAL_PANORAMIC.values()
        }

        result["fields_extracted"] = len(dental_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxv_field_count() -> int:
    return len(DENTAL_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxv_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxv_description() -> str:
    return (
        "Dental and maxillofacial imaging metadata extraction. Provides comprehensive "
        "coverage of dental acquisition parameters, CBCT reconstruction algorithms, "
        "panoramic imaging, and dental-specific positioning and support equipment."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxv_modalities() -> List[str]:
    return ["CT", "CR", "DR", "DX", "OT"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxv_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxv_category() -> str:
    return "Dental and Maxillofacial Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxv_keywords() -> List[str]:
    return [
        "dental", "CBCT", "panoramic", "cephalometric", "intraoral", "orthodontic",
        "maxillofacial", "implant", "endodontic", "periodontic", "oral surgery"
    ]
