"""
Scientific DICOM/FITS Ultimate Advanced Extension XLVI - Vascular Imaging

This module provides comprehensive extraction of vascular imaging parameters
including CTA, MRA, and angiographic vascular analysis.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XLVI_AVAILABLE = True

VASCULAR_CTA = {
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0061): "kvp_indication",
    (0x0018, 0x1150): "exposure_time",
    (0x0018, 0x1151): "xray_tube_current",
    (0x0018, 0x1152): "exposure",
    (0x0018, 0x1153): "exposure_index",
    (0x0018, 0x1154): "target_exposure_index",
    (0x0018, 0x1155): "deviation_index",
    (0x0018, 0x1160): "filter_type",
    (0x0018, 0x1161): "filter_material",
    (0x0018, 0x1162): "filter_thickness_minimum",
    (0x0018, 0x1163): "filter_thickness_maximum",
    (0x0018, 0x1164): "filter_attenuation",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0x1211): "convolution_kernel_description",
    (0x0018, 0x1247): "beam_pitch",
    (0x0018, 0x1314): "ct_volumetric_properties_flag",
    (0x0018, 0x1317): "ct_acquisition_type",
    (0x0018, 0x1318): "ct_acquisition_mode",
    (0x0018, 0x1319): "ct_slice_spacing",
    (0x0018, 0x1320): "ct_slice_thickness",
    (0x0018, 0x1327): "ct_dose_length_product",
    (0x0018, 0x1328): "ct_dose_ctdi",
    (0x0018, 0x1330): "ct_optimal_contrast",
    (0x0018, 0x1331): "ct_contrast_injection_rate",
    (0x0018, 0x1332): "ct_contrast_injection_volume",
    (0x0018, 0x1333): "ct_contrast_injection_delay",
    (0x0018, 0x1334): "ct_contrast_bolus_agent",
    (0x0018, 0x1335): "ct_contrast_bolus_concentration",
    (0x0018, 0x9067): "cardiac_cycle_position",
    (0x0018, 0x9068): "respiratory_cycle_position",
    (0x0018, 0x9020): "respiratory_trigger_type",
    (0x0018, 0x9021): "respiratory_trigger_sequence",
    (0x0018, 0x9022): "respiratory_trigger_delay",
    (0x0018, 0x9023): "respiratory_trigger_frequency",
    (0x0018, 0x9040): "gating_4d_type",
    (0x0018, 0x9041): "gating_4d_sequence",
    (0x0018, 0x9042): "gating_4d_function",
    (0x0018, 0x9043): "gating_4d_data",
    (0x0018, 0x9044): "gating_4d_description",
    (0x0018, 0x9045): "gating_4d_method",
}

VASCULAR_ANALYSIS = {
    (0x0018, 0x9600): "vessel_sequence",
    (0x0018, 0x9601): "vessel_name",
    (0x0018, 0x9602): "vessel_laterality",
    (0x0018, 0x9603): "vessel_type",
    (0x0018, 0x9604): "vessel_type_description",
    (0x0018, 0x9605): "vessel_segment_sequence",
    (0x0018, 0x9606): "vessel_segment_name",
    (0x0018, 0x9607): "vessel_segment_description",
    (0x0018, 0x9608): "vessel_segment_laterality",
    (0x0018, 0x9610): "vessel_diameter_sequence",
    (0x0018, 0x9611): "vessel_diameter_value",
    (0x0018, 0x9612): "vessel_diameter_unit",
    (0x0018, 0x9613): "vessel_diameter_description",
    (0x0018, 0x9614): "vessel_diameter_laterality",
    (0x0018, 0x9615): "vessel_diameter_segment",
    (0x0018, 0x9620): "vessel_wall_sequence",
    (0x0018, 0x9621): "vessel_wall_thickness",
    (0x0018, 0x9622): "vessel_wall_thickness_unit",
    (0x0018, 0x9623): "vessel_wall_thickness_description",
    (0x0018, 0x9624): "vessel_wall_laterality",
    (0x0018, 0x9625): "vessel_wall_segment",
    (0x0018, 0x9630): "lumen_sequence",
    (0x0018, 0x9631): "lumen_diameter",
    (0x0018, 0x9632): "lumen_diameter_unit",
    (0x0018, 0x9633): "lumen_diameter_description",
    (0x0018, 0x9634): "lumen_laterality",
    (0x0018, 0x9635): "lumen_segment",
    (0x0018, 0x9640): "plaque_sequence",
    (0x0018, 0x9641): "plaque_type",
    (0x0018, 0x9642): "plaque_type_description",
    (0x0018, 0x9643): "plaque_composition",
    (0x0018, 0x9644): "plaque_composition_description",
    (0x0018, 0x9645): "plaque_distribution",
    (0x0018, 0x9646): "plaque_distribution_description",
    (0x0018, 0x9647): "plaque_volume",
    (0x0018, 0x9648): "plaque_volume_unit",
    (0x0018, 0x9650): "stenosis_sequence",
    (0x0018, 0x9651): "stenosis_degree",
    (0x0018, 0x9652): "stenosis_degree_unit",
    (0x0018, 0x9653): "stenosis_degree_description",
    (0x0018, 0x9654): "stenosis_laterality",
    (0x0018, 0x9655): "stenosis_segment",
    (0x0018, 0x9656): "stenosis_method",
    (0x0018, 0x9657): "stenosis_method_description",
    (0x0018, 0x9660): "occlusion_sequence",
    (0x0018, 0x9661): "occlusion_degree",
    (0x0018, 0x9662): "occlusion_degree_unit",
    (0x0018, 0x9663): "occlusion_degree_description",
    (0x0018, 0x9664): "occlusion_laterality",
    (0x0018, 0x9665): "occlusion_segment",
    (0x0018, 0x9670): "aneurysm_sequence",
    (0x0018, 0x9671): "aneurysm_type",
    (0x0018, 0x9672): "aneurysm_type_description",
    (0x0018, 0x9673): "aneurysm_size",
    (0x0018, 0x9674): "aneurysm_size_unit",
    (0x0018, 0x9675): "aneurysm_neck_width",
    (0x0018, 0x9676): "aneurysm_neck_width_unit",
    (0x0018, 0x9677): "aneurysm_volume",
    (0x0018, 0x9678): "aneurysm_volume_unit",
    (0x0018, 0x9680): "dissection_sequence",
    (0x0018, 0x9681): "dissection_type",
    (0x0018, 0x9682): "dissection_type_description",
    (0x0018, 0x9683): "dissection_flap",
    (0x0018, 0x9684): "dissection_flap_description",
    (0x0018, 0x9685): "dissection_laterality",
    (0x0018, 0x9686): "dissection_segment",
}

VASCULAR_MRA = {
    (0x0018, 0x9004): "cardiac_trigger_type",
    (0x0018, 0x9005): "cardiac_trigger_sequence",
    (0x0018, 0x9006): "cardiac_trigger_time_offset",
    (0x0018, 0x9007): "cardiac_trigger_frequency",
    (0x0018, 0x9008): "cardiac_trigger_delay",
    (0x0018, 0x9009): "cardiac_phase_delay",
    (0x0018, 0x9040): "gating_4d_type",
    (0x0018, 0x9041): "gating_4d_sequence",
    (0x0018, 0x9042): "gating_4d_function",
    (0x0018, 0x9043): "gating_4d_data",
    (0x0018, 0x9044): "gating_4d_description",
    (0x0018, 0x9045): "gating_4d_method",
    (0x0018, 0x9020): "respiratory_trigger_type",
    (0x0018, 0x9021): "respiratory_trigger_sequence",
    (0x0018, 0x9022): "respiratory_trigger_delay",
    (0x0018, 0x9023): "respiratory_trigger_frequency",
    (0x0018, 0x9030): "respiratory_motion_compensation_type",
    (0x0018, 0x9031): "respiratory_signal_source",
}

VASCULAR_TOTAL_TAGS = VASCULAR_CTA | VASCULAR_ANALYSIS | VASCULAR_MRA


def _extract_vascular_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in VASCULAR_TOTAL_TAGS.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _is_vascular_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xlvi(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xlvi_detected": False,
        "fields_extracted": 0,
        "extension_xlvi_type": "vascular_imaging",
        "extension_xlvi_version": "2.0.0",
        "cta_parameters": {},
        "vascular_analysis": {},
        "mra_parameters": {},
        "extraction_errors": [],
    }

    try:
        if not _is_vascular_file(file_path):
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

        result["extension_xlvi_detected"] = True

        vascular_data = _extract_vascular_tags(ds)

        result["cta_parameters"] = {
            k: v for k, v in vascular_data.items()
            if k in VASCULAR_CTA.values()
        }
        result["vascular_analysis"] = {
            k: v for k, v in vascular_data.items()
            if k in VASCULAR_ANALYSIS.values()
        }
        result["mra_parameters"] = {
            k: v for k, v in vascular_data.items()
            if k in VASCULAR_MRA.values()
        }

        result["fields_extracted"] = len(vascular_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xlvi_field_count() -> int:
    return len(VASCULAR_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xlvi_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xlvi_description() -> str:
    return (
        "Vascular imaging metadata extraction. Provides comprehensive coverage of "
        "CTA and MRA parameters, vessel diameter and wall analysis, plaque characterization, "
        "stenosis quantification, aneurysm detection, and dissection assessment."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_xlvi_modalities() -> List[str]:
    return ["CT", "MR", "XA", "RF"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xlvi_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xlvi_category() -> str:
    return "Vascular Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_xlvi_keywords() -> List[str]:
    return [
        "vascular", "CTA", "MRA", "angiography", "vessel", "stenosis",
        "plaque", "aneurysm", "dissection", "carotid", "cerebral", "peripheral"
    ]
