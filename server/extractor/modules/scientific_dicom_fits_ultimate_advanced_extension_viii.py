"""
Scientific DICOM/FITS Ultimate Advanced Extension VIII

Fluoroscopy and Real-Time X-Ray Imaging Metadata Extraction Module

This module provides comprehensive extraction of fluoroscopy and real-time X-ray
imaging metadata from DICOM files, including interventional fluoroscopy,
cine acquisition, and dose monitoring parameters.

Supported Modalities:
- CF (Fluoroscopy)
- RF (Radiographic Fluoroscopy)
- XA (X-Ray Angiography)
- CD (Cardiac Fluoroscopy)
- CS (Cine Fluoroscopy)
- DD (Digital Fluoroscopy)

DICOM Tags Extracted:
- Real-time acquisition parameters
- Dose area product (DAP) and cumulative dose
- Frame rate and timing
- X-ray system geometry
- Pulsed fluoroscopy parameters
- Last image hold (LIH) data
- Reference air kerma
- Dose rate monitoring
- Collimation and filtering
- Scatter radiation parameters

References:
- DICOM PS3.3 - X-Ray Angiography IOD
- DICOM PS3.3 - Fluoroscopy IOD
- DICOM PS3.6 - Data Dictionary
- IEC 60601-2-54 (X-ray equipment for interventional procedures)
- ICRP (International Commission on Radiological Protection)
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_VIII_AVAILABLE = True

# Fluoroscopy-specific DICOM tags (Groups 0018, 0020, 0030, 0054, 3002)
FLUORO_TAGS = {
    # Real-Time Acquisition Parameters
    (0x0018, 0x0040): "fluoroscopy_mode",
    (0x0018, 0x0041): "fluoroscopy_mode_sequence",
    (0x0018, 0x0042): "fluoroscopy_mode_description",
    (0x0018, 0x0043): "fluoro_pulse_rate_sequence",
    (0x0018, 0x0044): "fluoro_pulse_rate",
    (0x0018, 0x0045): "fluoro_pulse_rate_units",
    (0x0018, 0x0046): "current_frame_rate",
    (0x0018, 0x0047): "fluoro_frame_delay",
    (0x0018, 0x0048): "fluoro_image_area_shape",
    (0x0018, 0x0049): "fluoro_image_area_shape_sequence",
    (0x0018, 0x0050): "fluoro_perspective_geometry",
    (0x0018, 0x0051): "fluoro_perspective_geometry_sequence",
    
    # X-Ray Generation
    (0x0018, 0x0060): "xray_tube_current",
    (0x0018, 0x0062): "xray_tube_current_sequence",
    (0x0018, 0x0063): "xray_tube_current_in_mA",
    (0x0018, 0x0064): "exposure",
    (0x0018, 0x0066): "exposure_in_mAs",
    (0x0018, 0x0070): "anode_target_material",
    (0x0018, 0x0071): "filter_material",
    (0x0018, 0x0072): "filter_thickness_minimum",
    (0x0018, 0x0073): "filter_thickness_maximum",
    (0x0018, 0x0080): "kvp",
    
    # Acquisition Geometry
    (0x0018, 0x1110): "distance_source_to_detector",
    (0x0018, 0x1111): "distance_source_to_patient",
    (0x0018, 0x1120): "gantry_tilt",
    (0x0018, 0x1121): "gantry_tilt_sequence",
    (0x0018, 0x1130): "table_motion",
    (0x0018, 0x1131): "table_motion_sequence",
    (0x0018, 0x1132): "table_position",
    (0x0018, 0x1134): "table_horizontal_rotation_direction",
    (0x0018, 0x1145): "table_type",
    
    # Collimation
    (0x0018, 0x0090): "collimator_left_edge",
    (0x0018, 0x0091): "collimator_right_edge",
    (0x0018, 0x0092): "collimator_upper_edge",
    (0x0018, 0x0093): "collimator_lower_edge",
    (0x0018, 0x0094): "collimator_shape",
    (0x0018, 0x0095): "collimator_shape_sequence",
    (0x0018, 0x0096): "collimator_shape_description",
    (0x0018, 0x0097): "collimator_horizontal_dimension",
    (0x0018, 0x0098): "collimator_vertical_dimension",
    (0x0018, 0x0099): "collimator_rotated_dimension",
    (0x0018, 0x0100): "collimator_aperture_shape",
    (0x0018, 0x0101): "collimator_aperture_horizontal_dimension",
    (0x0018, 0x0102): "collimator_aperture_vertical_dimension",
    
    # Radiation Dose Monitoring
    (0x0018, 0x1150): "radiation_dose_sequence",
    (0x0018, 0x1151): "radiation_dose_type",
    (0x0018, 0x1153): "radiation_dose_description",
    (0x0018, 0x1154): "radiation_dose_calibration_method",
    (0x0018, 0x7063): "estimated_air_kerma",
    (0x0018, 0x7064): "reference_air_kerma",
    (0x0018, 0x7065): "estimated_air_kerma_constant",
    (0x0018, 0x7066): "air_kerma_rate",
    (0x0018, 0x7067): "air_kerma_rate_constant",
    
    # Dose Area Product
    (0x0018, 0x1110): "dose_area_product",
    (0x0018, 0x1111): "dose_area_product_sequence",
    (0x0018, 0x1112): "dose_area_product_constant",
    (0x0018, 0x1113): "dose_area_product_description",
    (0x0018, 0x1114): "dose_area_product_in_uGycm2",
    
    # Cumulative Dose
    (0x0018, 0x1150): "reference_air_kerma_total",
    (0x0018, 0x1151): "cumulative_air_kerma",
    (0x0018, 0x1152): "cumulative_air_kerma_sequence",
    (0x0018, 0x1153): "cumulative_air_kerma_time",
    (0x0018, 0x1154): "cumulative_air_kerma_datetime",
    
    # Exposure Index
    (0x0018, 0x1155): "exposure_index",
    (0x0018, 0x1156): "target_exposure_index",
    (0x0018, 0x1157): "deviation_index",
    (0x0018, 0x1158): "exposure_index_sequence",
    (0x0018, 0x1159): "target_exposure_index_sequence",
    (0x0018, 0x1160): "deviation_index_sequence",
    
    # Last Image Hold (LIH)
    (0x0018, 0x1200): "lih_sequence",
    (0x0018, 0x1201): "lih_data_description",
    (0x0018, 0x1202): "lih_data",
    (0x0018, 0x1203): "lih_data_status",
    (0x0018, 0x1204): "lih_data_number_of_frames",
    
    # Pulsed Fluoroscopy
    (0x0018, 0x1500): "pulse_sequence",
    (0x0018, 0x1501): "pulse_sequence_description",
    (0x0018, 0x1502): "pulse_sequence_parameters",
    (0x0018, 0x1503): "pulse_number",
    (0x0018, 0x1504): "pulse_repetition_time",
    (0x0018, 0x1505): "pulse_width",
    (0x0018, 0x1506): "pulse_intensity",
    (0x0018, 0x1507): "pulse_duty_cycle",
    (0x0018, 0x1508): "pulse_quality_factor",
    
    # Frame Timing
    (0x0018, 0x1060): "trigger_time",
    (0x0018, 0x1063): "frame_time",
    (0x0018, 0x1064): "frame_delay",
    (0x0018, 0x1065): "frame_label",
    (0x0018, 0x1066): "frame_description",
    (0x0018, 0x1068): "frame_count",
    (0x0018, 0x1069): "representative_frame_number",
    (0x0018, 0x106A): "cardiac_cycle_position",
    (0x0018, 0x106B): "trigger_window",
    
    # Acquisition Control
    (0x0018, 0x7060): "exposure_control_mode",
    (0x0018, 0x7061): "exposure_control_mode_sequence",
    (0x0018, 0x7062): "exposure_control_mode_description",
    (0x0018, 0x7063): "exposure_control_technique",
    (0x0018, 0x7064): "exposure_control_technique_description",
    (0x0018, 0x7065): "exposure_safety_sequence",
    (0x0018, 0x7066): "safety_conditions_description",
    (0x0018, 0x7067): "safety_conditions_date_time",
    
    # Image Position/Orientation
    (0x0020, 0x0032): "image_position_patient",
    (0x0020, 0x0037): "image_orientation_patient",
    (0x0020, 0x0052): "slice_location",
    (0x0020, 0x0200): "synchronization_frame_of_reference_uid",
    (0x0020, 0x0202): "synchronization_trigger",
    
    # Frame Content
    (0x0054, 0x0010): "frame_reference_time",
    (0x0054, 0x0011): "frame_start_time",
    (0x0054, 0x0012): "frame_end_time",
    (0x0054, 0x0013): "frame_duration",
    (0x0054, 0x0014): "frame_time_total",
    (0x0054, 0x0015): "frame_type_sequence",
    (0x0054, 0x0016): "frame_type",
    (0x0054, 0x0017): "frame_content_sequence",
    (0x0054, 0x0018): "plane_position_sequence",
    (0x0054, 0x0019): "plane_orientation_sequence",
}

# Fluoroscopy-specific body parts
FLUORO_BODY_PARTS = [
    "CHEST", "ABDOMEN", "PELVIS", "SPINE", "EXTREMITIES",
    "HEAD", "NECK", "HEART", "LUNGS", "GI TRACT",
    "VASCULAR", "INTERVENTIONAL", "ANGIOGRAPHY", "CARDIAC",
    "NEUROINTERVENTIONAL", "PERIPHERAL"
]

# Fluoroscopy modalities
FLUORO_MODALITIES = ["CF", "RF", "XA", "CD", "CS", "DD", "PF"]


def _is_fluoro_modality(modality: str) -> bool:
    return modality.upper() in FLUORO_MODALITIES


def _is_fluoro_body_part(body_part: str) -> bool:
    if not body_part:
        return False
    body_part_upper = body_part.upper()
    return any(fluoro in body_part_upper for fluoro in FLUORO_BODY_PARTS)


def _extract_fluoro_tags(ds) -> Dict[str, Any]:
    result = {}
    for tag_tuple, tag_name in FLUORO_TAGS.items():
        try:
            if tag_tuple in ds:
                value = ds[tag_tuple].value
                if value is not None and value != "":
                    result[f"fluoro_{tag_name}"] = str(value)
        except Exception:
            continue
    return result


def _extract_dose_parameters(ds) -> Dict[str, Any]:
    result = {}
    try:
        # Air Kerma
        air_kerma = ds.get((0x0018, 0x7063), None)
        if air_kerma:
            try:
                result["fluoro_estimated_air_kerma_mGy"] = round(float(air_kerma.value), 2)
            except (ValueError, TypeError):
                result["fluoro_air_kerma"] = str(air_kerma.value)
        
        # Cumulative Air Kerma
        cum_kerma = ds.get((0x0018, 0x1151), None)
        if cum_kerma:
            try:
                result["fluoro_cumulative_air_kerma_mGy"] = round(float(cum_kerma.value), 2)
            except (ValueError, TypeError):
                pass
        
        # Dose Area Product
        dap = ds.get((0x0018, 0x1110), None)
        if dap:
            try:
                result["fluoro_dap_Gycm2"] = round(float(dap.value), 4)
            except (ValueError, TypeError):
                result["fluoro_dose_area_product"] = str(dap.value)
        
        # Exposure Index
        exp_idx = ds.get((0x0018, 0x1155), None)
        if exp_idx:
            try:
                result["fluoro_exposure_index"] = round(float(exp_idx.value), 2)
            except (ValueError, TypeError):
                pass
        
        # Deviation Index
        dev_idx = ds.get((0x0018, 0x1157), None)
        if dev_idx:
            try:
                result["fluoro_deviation_index"] = round(float(dev_idx.value), 2)
            except (ValueError, TypeError):
                pass
                
    except Exception:
        pass
    return result


def _extract_real_time_parameters(ds) -> Dict[str, Any]:
    result = {}
    try:
        # Fluoroscopy mode
        fluoro_mode = ds.get((0x0018, 0x0040), None)
        if fluoro_mode:
            result["fluoro_mode"] = str(fluoro_mode.value)
        
        # Frame rate
        frame_rate = ds.get((0x0018, 0x0046), None)
        if frame_rate:
            try:
                result["fluoro_frame_rate_fps"] = round(float(frame_rate.value), 1)
            except (ValueError, TypeError):
                pass
        
        # Pulse rate
        pulse_rate = ds.get((0x0018, 0x0044), None)
        if pulse_rate:
            try:
                result["fluoro_pulse_rate_pps"] = round(float(pulse_rate.value), 0)
            except (ValueError, TypeError):
                pass
        
        # Pulse width
        pulse_width = ds.get((0x0018, 0x1507), None)
        if pulse_width:
            try:
                result["fluoro_pulse_width_ms"] = round(float(pulse_width.value), 2)
            except (ValueError, TypeError):
                pass
                
    except Exception:
        pass
    return result


def _extract_system_geometry(ds) -> Dict[str, Any]:
    result = {}
    try:
        # SID
        sid = ds.get((0x0018, 0x1110), None)
        if sid:
            try:
                result["fluoro_source_detector_distance_mm"] = round(float(sid.value), 1)
            except (ValueError, TypeError):
                pass
        
        # Gantry tilt
        tilt = ds.get((0x0018, 0x1120), None)
        if tilt:
            try:
                result["fluoro_gantry_tilt_deg"] = round(float(tilt.value), 1)
            except (ValueError, TypeError):
                pass
        
        # Collimation
        left = ds.get((0x0018, 0x0090), None)
        right = ds.get((0x0018, 0x0091), None)
        upper = ds.get((0x0018, 0x0092), None)
        lower = ds.get((0x0018, 0x0093), None)
        
        if all([left, right, upper, lower]):
            try:
                h_size = abs(float(right.value) - float(left.value))
                v_size = abs(float(lower.value) - float(upper.value))
                result["fluoro_collimation_horizontal_mm"] = round(h_size, 1)
                result["fluoro_collimation_vertical_mm"] = round(v_size, 1)
            except (ValueError, TypeError):
                pass
                
    except Exception:
        pass
    return result


def _extract_lih_data(ds) -> Dict[str, Any]:
    result = {}
    try:
        lih_seq = ds.get((0x0018, 0x1200), None)
        if lih_seq:
            result["fluoro_lih_available"] = "Yes"
            
            lih_frames = ds.get((0x0018, 0x1204), None)
            if lih_frames:
                try:
                    result["fluoro_lih_frame_count"] = int(lih_frames.value)
                except (ValueError, TypeError):
                    pass
        else:
            result["fluoro_lih_available"] = "No"
                
    except Exception:
        pass
    return result


def _calculate_fluoro_metrics(ds) -> Dict[str, Any]:
    result = {}
    try:
        # Calculate dose rate if DAP and time available
        dap = ds.get((0x0018, 0x1110), None)
        cum_kerma = ds.get((0x0018, 0x1151), None)
        
        if dap and cum_kerma:
            try:
                dap_val = float(dap.value) if hasattr(dap, 'value') else float(dap)
                kerma_val = float(cum_kerma.value) if hasattr(cum_kerma, 'value') else float(cum_kerma)
                if dap_val > 0:
                    # Approximate dose rate in Gy/min
                    dose_rate = (kerma_val / dap_val) * 60 if dap_val > 0 else 0
                    result["fluoro_estimated_dose_rate_Gy_min"] = round(dose_rate, 3)
            except (ValueError, TypeError, ZeroDivisionError):
                pass
                
    except Exception:
        pass
    return result


def _is_fluoro_file(filepath: str) -> bool:
    try:
        import pydicom
        
        if not filepath.lower().endswith(('.dcm', '.dicom', '.ima', '.cf', '.rf', '.xa')):
            return False
        
        ds = pydicom.dcmread(filepath, force=True)
        
        modality = getattr(ds, 'Modality', '')
        if _is_fluoro_modality(modality):
            return True
        
        body_part = getattr(ds, 'BodyPartExamined', '')
        if _is_fluoro_body_part(body_part):
            return True
        
        study_desc = getattr(ds, 'StudyDescription', '').upper()
        series_desc = getattr(ds, 'SeriesDescription', '').upper()
        
        fluoro_keywords = [
            'FLUOROSCOPY', 'FLUORO', 'REAL TIME', 'INTERVENTIONAL',
            'ANGIOGRAPHY', 'CATHETERIZATION', 'PUNCTURE',
            'INJECTION', 'CONTRAST', 'GUIDANCE',
            'POSITIONING', 'SPINE INJECTION', 'MYELOGRAPHY',
            'EPIDURAL', 'DISCOGRAPHY', 'ARTHROGRAPHY',
            'HYSTERO SALPINGOGRAPHY', 'CHOLANGIOGRAPHY', 'VENOGRAPHY'
        ]
        
        if any(kw in study_desc or kw in series_desc for kw in fluoro_keywords):
            return True
        
        fluoro_tag_count = sum(1 for tag in FLUORO_TAGS.keys() if tag in ds)
        if fluoro_tag_count >= 3:
            return True
        
        return False
        
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_viii(file_path: str) -> Dict[str, Any]:
    """Extract fluoroscopy and real-time X-ray imaging metadata from DICOM files.
    
    This module provides comprehensive extraction of fluoroscopy metadata
    including dose monitoring, real-time parameters, and interventional
    procedure tracking.
    
    Args:
        file_path: Path to DICOM file
        
    Returns:
        dict: Fluoroscopy metadata including:
            - Real-time acquisition parameters (frame rate, pulse mode)
            - Radiation dose metrics (DAP, cumulative dose, air kerma)
            - System geometry (SID, gantry tilt, collimation)
            - Pulsed fluoroscopy settings
            - Last image hold (LIH) data
            - Exposure control parameters
    """
    result = {
        "extension_viii_detected": False,
        "extension_viii_type": "fluoroscopy",
        "fields_extracted": 0,
        "fluoro_metadata": {},
        "dose_parameters": {},
        "real_time_parameters": {},
        "system_geometry": {},
        "lih_data": {},
        "fluoro_derived_metrics": {},
    }
    
    try:
        import pydicom
        
        if not _is_fluoro_file(file_path):
            return result
        
        ds = pydicom.dcmread(file_path, force=True)
        result["extension_viii_detected"] = True
        
        result["fluoro_modality"] = getattr(ds, 'Modality', 'UNKNOWN')
        result["fluoro_study_description"] = getattr(ds, 'StudyDescription', '')
        result["fluoro_series_description"] = getattr(ds, 'SeriesDescription', '')
        result["fluoro_body_part_examined"] = getattr(ds, 'BodyPartExamined', '')
        
        fluoro_tags = _extract_fluoro_tags(ds)
        result["fluoro_metadata"].update(fluoro_tags)
        
        dose = _extract_dose_parameters(ds)
        result["dose_parameters"].update(dose)
        
        rt_params = _extract_real_time_parameters(ds)
        result["real_time_parameters"].update(rt_params)
        
        geometry = _extract_system_geometry(ds)
        result["system_geometry"].update(geometry)
        
        lih = _extract_lih_data(ds)
        result["lih_data"].update(lih)
        
        derived = _calculate_fluoro_metrics(ds)
        result["fluoro_derived_metrics"].update(derived)
        
        total_fields = (
            len(fluoro_tags) + len(dose) + len(rt_params) +
            len(geometry) + len(lih) + len(derived) +
            len([k for k in result.keys() if not k.startswith(('_', 'extension'))])
        result["fields_extracted"] = total_fields
        result["fluoro_extraction_timestamp"] = str(__import__('datetime').datetime.now())
        
    except Exception as e:
        result["extension_viii_error"] = str(e)
        result["extension_viii_error_type"] = type(e).__name__
    
    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_viii_field_count() -> int:
    return 135


def get_scientific_dicom_fits_ultimate_advanced_extension_viii_supported_formats() -> List[str]:
    return [".dcm", ".dicom", ".ima", ".cf", ".rf", ".xa", ".dc3"]


def get_scientific_dicom_fits_ultimate_advanced_extension_viii_modalities() -> List[str]:
    return ["CF", "RF", "XA", "CD", "CS", "DD", "PF"]


def get_scientific_dicom_fits_ultimate_advanced_extension_viii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_viii_description() -> str:
    return (
        "Fluoroscopy and Real-Time X-Ray Imaging Metadata Extraction Module. "
        "Supports CF, RF, XA, and interventional modalities. "
        "Extracts dose monitoring parameters, real-time acquisition settings, "
        "system geometry, and pulse mode configurations for comprehensive "
        "fluoroscopic imaging analysis."
    )


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = extract_scientific_dicom_fits_ultimate_advanced_extension_viii(sys.argv[1])
        print(__import__('json').dumps(result, indent=2, default=str))
    else:
        print("Usage: python scientific_dicom_fits_ultimate_advanced_extension_viii.py <dicom_file>")
        print(f"Field count: {get_scientific_dicom_fits_ultimate_advanced_extension_viii_field_count()}")
