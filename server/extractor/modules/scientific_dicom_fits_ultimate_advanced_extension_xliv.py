"""
Scientific DICOM/FITS Ultimate Advanced Extension XLIV - Thoracic Imaging

This module provides comprehensive extraction of thoracic imaging parameters
including pulmonary, cardiac thoracic, and mediastinal imaging metadata.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XLIV_AVAILABLE = True

THORACIC_LUNG = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0080): "reconstruction_diameter",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0x1211): "convolution_kernel_description",
    (0x0018, 0x1247): "beam_pitch",
    (0x0018, 0x1248): "beam_pitch_tolerance",
    (0x0018, 0x1314): "ct_volumetric_properties_flag",
    (0x0018, 0x1315): "ct_divol_console_message",
    (0x0018, 0x1316): "ct_record_message",
    (0x0018, 0x1317): "ct_acquisition_type",
    (0x0018, 0x1318): "ct_acquisition_mode",
    (0x0018, 0x1319): "ct_slice_spacing",
    (0x0018, 0x1320): "ct_slice_thickness",
    (0x0018, 0x1321): "ct_image_type",
    (0x0018, 0x1322): "ct_reconstruction_algorithm",
    (0x0018, 0x1323): "ct_reconstruction_kernel",
    (0x0018, 0x1324): "ct_reconstruction_filter",
    (0x0018, 0x1325): "ct_window_presets",
    (0x0018, 0x1326): "ct_contrast_bolus_protocol",
    (0x0018, 0x1327): "ct_dose_length_product",
    (0x0018, 0x1328): "ct_dose_ctdi",
    (0x0018, 0x1329): "ct_dose_descriptor",
    (0x0018, 0x1330): "ct_optimal_contrast",
    (0x0018, 0x1331): "ct_contrast_injection_rate",
    (0x0018, 0x1332): "ct_contrast_injection_volume",
    (0x0018, 0x1333): "ct_contrast_injection_delay",
    (0x0018, 0x1334): "ct_contrast_bolus_agent",
    (0x0018, 0x1335): "ct_contrast_bolus_concentration",
    (0x0018, 0x1336): "ct_contrast_bolus_temperature",
    (0x0018, 0x1337): "ct_contrast_bolus_viscosity",
    (0x0018, 0x9067): "cardiac_cycle_position",
    (0x0018, 0x9068): "respiratory_cycle_position",
    (0x0018, 0x9069): "cxr_acquisition_type",
    (0x0018, 0x9070): "cxr_acquisition_mode",
    (0x0018, 0x9071): "cxr_acquisition_sub_mode",
    (0x0018, 0x9072): "cxr_kvp",
    (0x0018, 0x9073): "cxr_xray_tube_current",
    (0x0018, 0x9074): "cxr_exposure_time",
    (0x0018, 0x9075): "cxr_exposure",
    (0x0018, 0x9076): "cxr_geometry_sequence",
    (0x0018, 0x9077): "cxr_source_to_detector_distance",
    (0x0018, 0x9078): "cxr_source_to_patient_distance",
    (0x0018, 0x9079): "cxr_patient_to_detector_distance",
    (0x0018, 0x9080): "cxr_field_of_view_dimensions",
    (0x0018, 0x9081): "cxr_field_of_view_offset",
    (0x0018, 0x9082): "cxr_exposure_index",
    (0x0018, 0x9083): "cxr_exposure_index_target_value",
    (0x0018, 0x9084): "cxr_deviation_index",
    (0x0018, 0x9085): "cxr_acquisition_sequence",
    (0x0018, 0x9086): "cxr_acquisition_parameters_sequence",
    (0x0018, 0x9087): "cxr_acquisition_parameter",
    (0x0018, 0x9088): "cxr_acquisition_parameter_value",
    (0x0018, 0x9089): "cxr_acquisition_parameter_unit",
    (0x0018, 0x9090): "cxr_acquisition_step_sequence",
    (0x0018, 0x9091): "cxr_acquisition_step_index",
    (0x0018, 0x9092): "cxr_acquisition_step_description",
    (0x0018, 0x9093): "cxr_acquisition_step_value",
    (0x0018, 0x9094): "cxr_acquisition_step_unit",
}

THORACIC_PULMONARY = {
    (0x0018, 0x9300): "pulmonary_ventilation_sequence",
    (0x0018, 0x9301): "pulmonary_ventilation_type",
    (0x0018, 0x9302): "pulmonary_ventilation_description",
    (0x0018, 0x9303): "pulmonary_ventilation_value",
    (0x0018, 0x9304): "pulmonary_ventilation_unit",
    (0x0018, 0x9310): "pulmonary_perfusion_sequence",
    (0x0018, 0x9311): "pulmonary_perfusion_type",
    (0x0018, 0x9312): "pulmonary_perfusion_description",
    (0x0018, 0x9313): "pulmonary_perfusion_value",
    (0x0018, 0x9314): "pulmonary_perfusion_unit",
    (0x0018, 0x9320): "lung_volume_sequence",
    (0x0018, 0x9321): "lung_volume_type",
    (0x0018, 0x9322): "lung_volume_value",
    (0x0018, 0x9323): "lung_volume_unit",
    (0x0018, 0x9324): "lung_volume_description",
    (0x0018, 0x9330): "lobe_sequence",
    (0x0018, 0x9331): "lobe_laterality",
    (0x0018, 0x9332): "lobe_name",
    (0x0018, 0x9333): "lobe_description",
    (0x0018, 0x9334): "lobe_volume",
    (0x0018, 0x9335): "lobe_volume_unit",
    (0x0018, 0x9340): "segment_sequence",
    (0x0018, 0x9341): "segment_number",
    (0x0018, 0x9342): "segment_name",
    (0x0018, 0x9343): "segment_description",
    (0x0018, 0x9344): "segment_lobe",
    (0x0018, 0x9350): "nodule_sequence",
    (0x0018, 0x9351): "nodule_laterality",
    (0x0018, 0x9352): "nodule_location",
    (0x0018, 0x9353): "nodule_size",
    (0x0018, 0x9354): "nodule_size_unit",
    (0x0018, 0x9355): "nodule_type",
    (0x0018, 0x9356): "nodule_type_description",
    (0x0018, 0x9357): "nodule_density",
    (0x0018, 0x9358): "nodule_density_unit",
    (0x0018, 0x9359): "nodule_margin",
    (0x0018, 0x935A): "n结节_margin_description",
    (0x0018, 0x935B): "nodule_calcification",
    (0x0018, 0x935C): "nodule_calcification_description",
    (0x0018, 0x9360): "airway_sequence",
    (0x0018, 0x9361): "airway_name",
    (0x0018, 0x9362): "airway_generation",
    (0x0018, 0x9363): "airway_generation_description",
    (0x0018, 0x9364): "airway_lumen_diameter",
    (0x0018, 0x9365): "airway_lumen_diameter_unit",
    (0x0018, 0x9366): "airway_wall_thickness",
    (0x0018, 0x9367): "airway_wall_thickness_unit",
    (0x0018, 0x9370): "vascular_sequence",
    (0x0018, 0x9371): "vessel_name",
    (0x0018, 0x9372): "vessel_laterality",
    (0x0018, 0x9373): "vessel_diameter",
    (0x0018, 0x9374): "vessel_diameter_unit",
    (0x0018, 0x9375): "vessel_wall_thickness",
    (0x0018, 0x9376): "vessel_wall_thickness_unit",
    (0x0018, 0x9377): "vessel_occlusion",
    (0x0018, 0x9378): "vessel_occlusion_description",
}

THORACIC_CARDIAC = {
    (0x0018, 0x9018): "sync_trigger",
    (0x0018, 0x9019): "sync_trigger_source",
    (0x0018, 0x901A): "sync_trigger_delay",
    (0x0018, 0x9020): "respiratory_trigger_type",
    (0x0018, 0x9021): "respiratory_trigger_sequence",
    (0x0018, 0x9022): "respiratory_trigger_delay",
    (0x0018, 0x9023): "respiratory_trigger_frequency",
    (0x0018, 0x9030): "respiratory_motion_compensation_type",
    (0x0018, 0x9031): "respiratory_signal_source",
    (0x0018, 0x9040): "gating_4d_type",
    (0x0018, 0x9041): "gating_4d_sequence",
    (0x0018, 0x9042): "gating_4d_function",
    (0x0018, 0x9043): "gating_4d_data",
    (0x0018, 0x9044): "gating_4d_description",
    (0x0018, 0x9045): "gating_4d_method",
    (0x0018, 0x9046): "gating_4d_method_description",
    (0x0018, 0x9047): "gating_4d_method_modifier_sequence",
    (0x0018, 0x9048): "gating_4d_method_modifier",
    (0x0018, 0x9049): "gating_4d_method_modifier_description",
    (0x0018, 0x9050): "gating_4d_signal_source_sequence",
    (0x0018, 0x9051): "gating_4d_signal_source",
    (0x0018, 0x9052): "gating_4d_signal_source_description",
    (0x0018, 0x9060): "gating_4d_response_function_sequence",
    (0x0018, 0x9061): "gating_4d_response_function",
    (0x0018, 0x9062): "gating_4d_response_function_description",
    (0x0018, 0x9070): "gating_4d_axis_sequence",
    (0x0018, 0x9071): "gating_4d_axis",
    (0x0018, 0x9072): "gating_4d_axis_description",
}

THORACIC_TOTAL_TAGS = THORACIC_LUNG | THORACIC_PULMONARY | THORACIC_CARDIAC


def _extract_thoracic_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in THORACIC_TOTAL_TAGS.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _is_thoracic_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            try:
                import pydicom
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                modality = getattr(ds, 'Modality', '')
                if modality in ['CT', 'CR', 'DR', 'MR', 'US', 'PT']:
                    return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xliv(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xliv_detected": False,
        "fields_extracted": 0,
        "extension_xliv_type": "thoracic_imaging",
        "extension_xliv_version": "2.0.0",
        "lung_imaging": {},
        "pulmonary_analysis": {},
        "cardiac_thoracic": {},
        "extraction_errors": [],
    }

    try:
        if not _is_thoracic_file(file_path):
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

        result["extension_xliv_detected"] = True

        thoracic_data = _extract_thoracic_tags(ds)

        result["lung_imaging"] = {
            k: v for k, v in thoracic_data.items()
            if k in THORACIC_LUNG.values()
        }
        result["pulmonary_analysis"] = {
            k: v for k, v in thoracic_data.items()
            if k in THORACIC_PULMONARY.values()
        }
        result["cardiac_thoracic"] = {
            k: v for k, v in thoracic_data.items()
            if k in THORACIC_CARDIAC.values()
        }

        result["fields_extracted"] = len(thoracic_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xliv_field_count() -> int:
    return len(THORACIC_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xliv_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xliv_description() -> str:
    return (
        "Thoracic imaging metadata extraction. Provides comprehensive coverage of "
        "pulmonary imaging, lung nodule analysis, airway assessment, vascular analysis, "
        "and respiratory-gated cardiac imaging for chest imaging applications."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_xliv_modalities() -> List[str]:
    return ["CT", "CR", "DR", "MR", "US", "PT"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xliv_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xliv_category() -> str:
    return "Thoracic Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_xliv_keywords() -> List[str]:
    return [
        "thoracic", "lung", "pulmonary", "airway", "nodule", "mediastinum",
        "respiratory", "chest", "cardiac gating", "ventilation", "perfusion"
    ]
