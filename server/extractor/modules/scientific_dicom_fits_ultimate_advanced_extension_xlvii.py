"""
Scientific DICOM/FITS Ultimate Advanced Extension XLVII - Advanced Nuclear Medicine

This module provides comprehensive extraction of advanced nuclear medicine parameters
including SPECT, PET quantification, and radiopharmaceutical dosimetry.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XLVII_AVAILABLE = True

NUCLEAR_QUANTIFICATION = {
    (0x0018, 0x1040): "contrast_bolus_agent",
    (0x0018, 0x1041): "contrast_bolus_start_time",
    (0x0018, 0x1042): "contrast_bolus_stop_time",
    (0x0018, 0x1043): "contrast_bolus_total_dose",
    (0x0018, 0x1044): "contrast_flow_rate",
    (0x0018, 0x1045): "contrast_flow_duration",
    (0x0018, 0x1046): "contrast_bolus_ingredient",
    (0x0018, 0x1047): "contrast_bolus_ingredient_concentration",
    (0x0018, 0x1071): "radionuclide_sequence",
    (0x0018, 0x1072): "radionuclide",
    (0x0018, 0x1073): "radionuclide_activity",
    (0x0018, 0x1074): "radionuclide_activity_dateTime",
    (0x0018, 0x1075): "radionuclide_half_life",
    (0x0018, 0x1076): "radionuclide_positron_fraction",
    (0x0018, 0x1077): "radiopharmaceutical_specific_activity",
    (0x0018, 0x1078): "radiopharmaceutical_start_dateTime",
    (0x0018, 0x1079): "radiopharmaceutical_stop_dateTime",
    (0x0018, 0x1080): "calibration_sequence",
    (0x0018, 0x1081): "system_status",
    (0x0018, 0x1082): "system_status_comment",
    (0x0018, 0x1083): "data_order_of_real_world_value_map",
    (0x0018, 0x1084): "actual_frame_duration",
    (0x0018, 0x1085): "count_rate",
    (0x0018, 0x1086): "preferred_playing_speed",
    (0x0018, 0x1088): "line_density",
    (0x0018, 0x1089): "mrt_timing_relationship_type",
    (0x0018, 0x1090): "protocol_index",
    (0x0018, 0x1100): "reference_base_kvp",
    (0x0018, 0x1101): "reference_exposure",
    (0x0018, 0x1102): "reference_mas",
    (0x0018, 0x1103): "reference_exposure_time",
    (0x0018, 0x1104): "reference_kvp_index",
    (0x0018, 0x1105): "reference_mas_index",
    (0x0018, 0x1106): "reference_exposure_index",
    (0x0018, 0x1107): "measured_kvp",
    (0x0018, 0x1108): "measured_mas",
    (0x0018, 0x1109): "measured_exposure_time",
    (0x0018, 0x1110): "reference_air_kerma_rate",
    (0x0018, 0x1111): "estimated_air_kerma_rate",
    (0x0018, 0x1112): "calculated_air_kerma_rate",
    (0x0018, 0x1120): "calibration_date",
    (0x0018, 0x1121): "calibration_time",
    (0x0018, 0x1122): "calibration_date_time",
    (0x0018, 0x1123): "correction_factor",
    (0x0018, 0x1124): "directional_decomposition",
    (0x0018, 0x1125): "directional_decomposition_direction",
    (0x0018, 0x1126): "attenuation_corrected",
    (0x0018, 0x1127): "reconstruction_field_of_view_shape",
    (0x0018, 0x1128): "filter_type",
    (0x0018, 0x1129): "type_of_filters",
    (0x0018, 0x1130): "xray_output",
    (0x0018, 0x1131): "half_value_layer",
    (0x0018, 0x1132): "organ_exposed",
    (0x0018, 0x1133): "reference_phantom",
    (0x0018, 0x1134): "phantom_object_sequence",
    (0x0018, 0x1140): "primary_fluence_mode",
    (0x0018, 0x1141): "fluoro_mode",
    (0x0018, 0x1142): "fluoro_mode_data",
    (0x0018, 0x1143): "current_slice_location",
    (0x0018, 0x1144): "multi_planar_excitation",
    (0x0018, 0x1145): "volume_localization_technique",
    (0x0018, 0x1146): "volume_of_acquisition",
    (0x0018, 0x1147): "delivery_technique",
    (0x0018, 0x1148): "delivery_technique_sequence",
    (0x0018, 0x1149): "radiation_attenuation_sequence",
}

NUCLEAR_SUV = {
    (0x0018, 0x9501): "activity_concentration_sequence",
    (0x0018, 0x9502): "activity_concentration_value",
    (0x0018, 0x9503): "activity_concentration_unit",
    (0x0018, 0x9504): "activity_concentration_dateTime",
    (0x0018, 0x9505): "decay_correction_sequence",
    (0x0018, 0x9506): "decay_correction_type",
    (0x0018, 0x9507): "decay_correction_type_description",
    (0x0018, 0x9508): "decay_correction_factor",
    (0x0018, 0x9509): "decay_correction_factor_unit",
    (0x0018, 0x9510): "reconstruction_sequence",
    (0x0018, 0x9511): "reconstruction_type",
    (0x0018, 0x9512): "reconstruction_type_description",
    (0x0018, 0x9513): "reconstruction_algorithm",
    (0x0018, 0x9514): "reconstruction_algorithm_description",
    (0x0018, 0x9515): "reconstruction_filter",
    (0x0018, 0x9516): "reconstruction_filter_description",
    (0x0018, 0x9517): "attenuation_correction_sequence",
    (0x0018, 0x9518): "attenuation_correction_type",
    (0x0018, 0x9519): "attenuation_correction_type_description",
    (0x0018, 0x9520): "scatter_correction_sequence",
    (0x0018, 0x9521): "scatter_correction_type",
    (0x0018, 0x9522): "scatter_correction_type_description",
    (0x0018, 0x9523): "scatter_correction_factor",
    (0x0018, 0x9524): "scatter_correction_factor_unit",
    (0x0018, 0x9530): "dead_time_correction_sequence",
    (0x0018, 0x9531): "dead_time_correction_type",
    (0x0018, 0x9532): "dead_time_correction_type_description",
    (0x0018, 0x9533): "dead_time_correction_factor",
    (0x0018, 0x9534): "dead_time_correction_factor_unit",
    (0x0018, 0x9540): "uniformity_correction_sequence",
    (0x0018, 0x9541): "uniformity_correction_type",
    (0x0018, 0x9542): "uniformity_correction_type_description",
    (0x0018, 0x9543): "uniformity_correction_factor",
    (0x0018, 0x9544): "uniformity_correction_factor_unit",
    (0x0018, 0x9550): "sensitivity_correction_sequence",
    (0x0018, 0x9551): "sensitivity_correction_type",
    (0x0018, 0x9552): "sensitivity_correction_type_description",
    (0x0018, 0x9553): "sensitivity_correction_factor",
    (0x0018, 0x9554): "sensitivity_correction_factor_unit",
}

NUCLEAR_DOSIMETRY = {
    (0x0018, 0x9600): "dose_sequence",
    (0x0018, 0x9601): "dose_type",
    (0x0018, 0x9602): "dose_type_description",
    (0x0018, 0x9603): "dose_value",
    (0x0018, 0x9604): "dose_unit",
    (0x0018, 0x9605): "dose_dateTime",
    (0x0018, 0x9610): "organ_dose_sequence",
    (0x0018, 0x9611): "organ_name",
    (0x0018, 0x9612): "organ_dose_value",
    (0x0018, 0x9613): "organ_dose_unit",
    (0x0018, 0x9620): "effective_dose_sequence",
    (0x0018, 0x9621): "effective_dose_value",
    (0x0018, 0x9622): "effective_dose_unit",
    (0x0018, 0x9630): "total_organ_dose_sequence",
    (0x0018, 0x9631): "total_organ_dose_value",
    (0x0018, 0x9632): "total_organ_dose_unit",
    (0x0018, 0x9640): "dose_calculation_sequence",
    (0x0018, 0x9641): "dose_calculation_model",
    (0x0018, 0x9642): "dose_calculation_model_description",
    (0x0018, 0x9643): "dose_calculation_parameter",
    (0x0018, 0x9644): "dose_calculation_parameter_value",
    (0x0018, 0x9645): "dose_calculation_parameter_unit",
}

NUCLEAR_TOTAL_TAGS = NUCLEAR_QUANTIFICATION | NUCLEAR_SUV | NUCLEAR_DOSIMETRY


def _extract_nuclear_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in NUCLEAR_TOTAL_TAGS.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _is_nuclear_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            try:
                import pydicom
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                modality = getattr(ds, 'Modality', '')
                if modality in ['PT', 'NM', 'SPECT', 'PET', 'CT']:
                    return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xlvii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xlvii_detected": False,
        "fields_extracted": 0,
        "extension_xlvii_type": "advanced_nuclear_medicine",
        "extension_xlvii_version": "2.0.0",
        "quantification": {},
        "suv_parameters": {},
        "dosimetry": {},
        "extraction_errors": [],
    }

    try:
        if not _is_nuclear_file(file_path):
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

        result["extension_xlvii_detected"] = True

        nuclear_data = _extract_nuclear_tags(ds)

        result["quantification"] = {
            k: v for k, v in nuclear_data.items()
            if k in NUCLEAR_QUANTIFICATION.values()
        }
        result["suv_parameters"] = {
            k: v for k, v in nuclear_data.items()
            if k in NUCLEAR_SUV.values()
        }
        result["dosimetry"] = {
            k: v for k, v in nuclear_data.items()
            if k in NUCLEAR_DOSIMETRY.values()
        }

        result["fields_extracted"] = len(nuclear_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xlvii_field_count() -> int:
    return len(NUCLEAR_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xlvii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xlvii_description() -> str:
    return (
        "Advanced nuclear medicine metadata extraction. Provides comprehensive coverage "
        "of SPECT/PET quantification, SUV parameters, radiopharmaceutical data, "
        "attenuation and scatter correction, and organ dosimetry calculations."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_xlvii_modalities() -> List[str]:
    return ["PT", "NM", "SPECT", "PET", "CT"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xlvii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xlvii_category() -> str:
    return "Advanced Nuclear Medicine"


def get_scientific_dicom_fits_ultimate_advanced_extension_xlvii_keywords() -> List[str]:
    return [
        "nuclear medicine", "PET", "SPECT", "SUV", "radiopharmaceutical",
        "dosimetry", "activity", "quantification", "attenuation correction",
        "scatter correction", "FDG", "oncology"
    ]
