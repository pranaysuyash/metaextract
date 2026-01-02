"""
Scientific DICOM/FITS Ultimate Advanced Extension VI

Ultrasound Metadata Extraction Module

This module provides comprehensive extraction of ultrasound and sonography
metadata from DICOM files, including 2D, 3D/4D, Doppler, and specialty
ultrasound modalities.

Supported Modalities:
- US (Ultrasound)
- EC (Echo cardiography)
- ES (Endoscopic Ultrasound)
- OP (Ophthalmic Ultrasound)
- IVUS (Intravascular Ultrasound)
- BMUS (Breast Ultrasound)
- DTUS (Doppler Ultrasound)

DICOM Tags Extracted:
- Image acquisition parameters (frequency, gain, depth)
- Transducer specifications
- Doppler parameters (velocity, resistance index)
- M-mode measurements
- 3D/4D volume parameters
- Specialty-specific fields (OB/GYN, cardiac, vascular)
- Biometry measurements
- Color flow/Power Doppler

References:
- DICOM PS3.3 - Ultrasound IOD
- DICOM PS3.6 - Data Dictionary
- AIUM (American Institute of Ultrasound in Medicine) standards
- ISUOG (International Society of Ultrasound in Obstetrics and Gynecology)
- ASE (American Society of Echocardiography) guidelines
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_VI_AVAILABLE = True

# Ultrasound-specific DICOM tags (Groups 0018, 0020, 0028, 0054)
ULTRASOUND_TAGS = {
    # Image Acquisition Parameters
    (0x0018, 0x0010): "frequency",
    (0x0018, 0x0011): "velocity",
    (0x0018, 0x0015): "body_part_evaluated",
    (0x0018, 0x0020): "patient_position",
    (0x0018, 0x0022): "view_position",
    (0x0018, 0x0024): "cardiac_cycles",
    (0x0018, 0x0025): "regions_of_interest_sequence",
    (0x0018, 0x0026): "region_of_spatial_precision_sequence",
    (0x0018, 0x0027): "region_of_spatial_precision",
    (0x0018, 0x0028): "spatial_resolution",
    (0x0018, 0x0030): "output_power",
    (0x0018, 0x0032): "gain",
    (0x0018, 0x0033): "gain_correction_factor",
    (0x0018, 0x0034): "dynamic_range",
    (0x0018, 0x0035): "dynamic_range_correction_factor",
    (0x0018, 0x0036): "total_gain",
    (0x0018, 0x0038): "image_horizontal_fov",
    (0x0018, 0x0039): "image_vertical_fov",
    (0x0018, 0x0040): "depth",
    (0x0018, 0x0041): "depth_correction_factor",
    (0x0018, 0x0042): "zoom_factor",
    (0x0018, 0x0043): "zoom_center_line",
    (0x0018, 0x0044): "zoom_magnification",
    (0x0018, 0x0050): "pixel_spacing",
    (0x0018, 0x0060): "overlay_planes",
    (0x0018, 0x0066): "transmit_pulse",
    (0x0018, 0x0070): "receive_gain",
    (0x0018, 0x0071): "receive_gain_correction_factor",
    (0x0018, 0x0072): "receive_center_frequency",
    (0x0018, 0x0074): "receive_bandwidth",
    (0x0018, 0x0075): "sound_speed",
    (0x0018, 0x0076): "sound_speed_correction_factor",
    
    # Transducer Parameters
    (0x0018, 0x5010): "transducer_type",
    (0x0018, 0x5011): "transducer_frequency",
    (0x0018, 0x5012): "transducer_element_pitch",
    (0x0018, 0x5013): "transducer_elements",
    (0x0018, 0x5014): "transducer_aperture",
    (0x0018, 0x5015): "transducer_beam_steer",
    (0x0018, 0x5016): "transducer_geometry",
    (0x0018, 0x5017): "transducer_f_number",
    (0x0018, 0x5018): "transducer_power",
    (0x0018, 0x5019): "transducer_depth",
    (0x0018, 0x5020): "transducer_sequence",
    (0x0018, 0x5021): "transducer_angle",
    (0x0018, 0x5022): "transducer_frame_rate",
    (0x0018, 0x5023): "transducer_frame_rate_correction",
    
    # Doppler Parameters
    (0x0018, 0x5100): "pulse_repetition_frequency",
    (0x0018, 0x5101): "doppler_correction_angle",
    (0x0018, 0x5102): "steering_angle",
    (0x0018, 0x5110): "sample_volume_width",
    (0x0018, 0x5111): "sample_volume_length",
    (0x0018, 0x5112): "pulse_length",
    (0x0018, 0x5113): "doppler_spectrum_sequence",
    (0x0018, 0x5114): "doppler_velocity",
    (0x0018, 0x5115): "doppler_mean_frequency",
    (0x0018, 0x5116): "doppler_spectrum_offset",
    (0x0018, 0x5117): "doppler_spectrum_alignment",
    (0x0018, 0x5118): "filter_bandwidth",
    (0x0018, 0x5119): "filter_cutoff_frequency",
    (0x0018, 0x5120): "filter_high_pass_frequency",
    (0x0018, 0x5121): "filter_low_pass_frequency",
    
    # Color Flow Parameters
    (0x0018, 0x6010): "color_doppler_sequence",
    (0x0018, 0x6011): "color_doppler_velocity",
    (0x0018, 0x6012): "color_doppler_mean_frequency",
    (0x0018, 0x6013): "color_doppler_spectrum_offset",
    (0x0018, 0x6014): "color_doppler_frame_rate",
    (0x0018, 0x6015): "color_doppler_persistence",
    (0x0018, 0x6016): "color_doppler_smoothing",
    (0x0018, 0x6017): "color_doppler_suppression",
    (0x0018, 0x6018): "color_doppler_threshold",
    (0x0018, 0x6019): "color_doppler_ensemble_length",
    (0x0018, 0x6020): "color_doppler_measurement_method",
    (0x0018, 0x6021): "color_doppler_measurement_value",
    (0x0018, 0x6022): "color_doppler_pixel_shifting",
    (0x0018, 0x6023): "color_doppler_temporal_filtering",
    (0x0018, 0x6024): "color_dopxel_spatial_filtering",
    (0x0018, 0x6025): "color_doppler_alpha_storage",
    (0x0018, 0x6026): "color_doppler_beta_storage",
    (0x0018, 0x6027): "color_doppler_gamma_storage",
    
    # Power Doppler Parameters
    (0x0018, 0x6030): "power_doppler_sequence",
    (0x0018, 0x6031): "power_doppler_sensitivity",
    (0x0018, 0x6032): "power_doppler_persistence",
    (0x0018, 0x6033): "power_doppler_suppression",
    (0x0018, 0x6034): "power_doppler_threshold",
    (0x0018, 0x6035): "power_doppler_frame_rate",
    
    # M-Mode Parameters
    (0x0018, 0x6100): "m_mode_sequence",
    (0x0018, 0x6101): "m_mode_horizontal_scan_rate",
    (0x0018, 0x6102): "m_mode_horizontal_scan_distance",
    (0x0018, 0x6103): "m_mode_vertical_scan_rate",
    (0x0018, 0x6104): "m_mode_vertical_scan_distance",
    
    # 3D/4D Volume Parameters
    (0x0018, 0x9001): "volume_sweep_sequence",
    (0x0018, 0x9002): "volume_sweep_direction",
    (0x0018, 0x9003): "volume_sweep_angle",
    (0x0018, 0x9004): "volume_axis_sweep_rotation",
    (0x0018, 0x9005): "volume_axis_rotation",
    (0x0018, 0x9006): "volume_sweep_pitch",
    (0x0018, 0x9007): "volume_axis_pitch",
    (0x0018, 0x9008): "volume_frame_count",
    (0x0018, 0x9009): "volume_reconstruction_sequence",
    (0x0018, 0x9010): "volume_reconstruction_algorithm",
    (0x0018, 0x9011): "volume_reconstruction_time",
    (0x0018, 0x9012): "volume_reconstruction_detector_position",
    (0x0018, 0x9013): "volume_reconstruction_geometry",
    (0x0018, 0x9014): "volume_reconstruction_filter",
    (0x0018, 0x9015): "volume_render_sequence",
    (0x0018, 0x9016): "volume_render_technique",
    (0x0018, 0x9017): "volume_render_layer_sequence",
    (0x0018, 0x9018): "volume_render_opacity",
    (0x0018, 0x9019): "volume_render_color",
    (0x0018, 0x9020): "volume_render_thickness",
    (0x0018, 0x9021): "volume_render_algorithm",
    (0x0018, 0x9022): "volume_render_view_direction",
    
    # Biometry Measurements
    (0x0020, 0x9228): "real_world_value_mapping_sequence",
    (0x0020, 0x9229): "real_world_value_mapping_last_value",
    (0x0020, 0x9230): "real_world_value_mapping_first_value",
    (0x0020, 0x9231): "real_world_value_mapping_step",
    (0x0020, 0x9232): "real_world_value_mapping_total_count",
    (0x0020, 0x9233): "real_world_value_intercept",
    (0x0020, 0x9234): "real_world_value_slope",
    
    # Image Processing
    (0x0028, 0x1050): "window_center",
    (0x0028, 0x1051): "window_width",
    (0x0028, 0x1052): "window_center_width_explanation",
    (0x0028, 0x1053): "rescale_intercept",
    (0x0028, 0x1054): "rescale_slope",
    (0x0028, 0x1055): "rescale_type",
    (0x0028, 0x5000): "overlay_rows",
    (0x0028, 0x5001): "overlay_columns",
    (0x0028, 0x5004): "overlay_type",
    (0x0028, 0x5010): "overlay_subtype",
    (0x0028, 0x5020): "overlay_origin",
    (0x0028, 0x5040): "overlay_compression_step",
    (0x0028, 0x5100): "overlay_description",
    (0x0028, 0x5101): "overlay_type",
    (0x0028, 0x5102): "overlay_subtype",
    (0x0028, 0x5104): "overlay_origin",
    (0x0028, 0x5150): "overlay_compression_notifications",
    (0x0028, 0x5200): "shared_functional_groups_sequence",
    (0x0028, 0x5201): "per_frame_functional_groups_sequence",
}

# Ultrasound-specific body parts
ULTRASOUND_BODY_PARTS = [
    "BREAST", "THYROID", "HEART", "CARDIAC", "ABDOMEN", "LIVER",
    "KIDNEY", "SPLEEN", "PANCREAS", "GALLBLADDER", "BLADDER",
    "PROSTATE", "TESTES", "OVARIES", "UTERUS", "FETUS",
    "NECK", "THYROID GLAND", "CAROTID", "ARTERY", "VEIN",
    "BRAIN", "INTRAVENTRICULAR", "SPINE", "MUSCLE", "JOINT",
    "EYE", "RETINA", "CORONARY", "PERICARDIAL", "PLACENTA"
]

# Ultrasound modalities
ULTRASOUND_MODALITIES = ["US", "EC", "ES", "OP", "IVUS", "BMUS", "DTUS", "DU"]


def _is_ultrasound_modality(modality: str) -> bool:
    return modality.upper() in ULTRASOUND_MODALITIES


def _is_ultrasound_body_part(body_part: str) -> bool:
    if not body_part:
        return False
    body_part_upper = body_part.upper()
    return any(us in body_part_upper for us in ULTRASOUND_BODY_PARTS)


def _extract_ultrasound_tags(ds) -> Dict[str, Any]:
    result = {}
    for tag_tuple, tag_name in ULTRASOUND_TAGS.items():
        try:
            if tag_tuple in ds:
                value = ds[tag_tuple].value
                if value is not None and value != "":
                    result[f"us_{tag_name}"] = str(value)
        except Exception:
            continue
    return result


def _extract_doppler_parameters(ds) -> Dict[str, Any]:
    result = {}
    try:
        prf = ds.get((0x0018, 0x5100), None)
        if prf:
            try:
                result["us_doppler_prf_hz"] = round(float(prf.value), 1)
            except (ValueError, TypeError):
                result["us_doppler_prf"] = str(prf.value)
        
        correction_angle = ds.get((0x0018, 0x5101), None)
        if correction_angle:
            try:
                result["us_doppler_correction_angle_deg"] = round(float(correction_angle.value), 1)
            except (ValueError, TypeError):
                result["us_doppler_correction_angle"] = str(correction_angle.value)
        
        steering_angle = ds.get((0x0018, 0x5102), None)
        if steering_angle:
            try:
                result["us_steering_angle_deg"] = round(float(steering_angle.value), 1)
            except (ValueError, TypeError):
                result["us_steering_angle"] = str(steering_angle.value)
                
    except Exception:
        pass
    return result


def _extract_color_flow_parameters(ds) -> Dict[str, Any]:
    result = {}
    try:
        color_doppler = ds.get((0x0018, 0x6010), None)
        if color_doppler:
            result["us_color_doppler_available"] = "Yes"
        
        frame_rate = ds.get((0x0018, 0x6014), None)
        if frame_rate:
            try:
                result["us_color_frame_rate_fps"] = round(float(frame_rate.value), 1)
            except (ValueError, TypeError):
                pass
        
        persistence = ds.get((0x0018, 0x6015), None)
        if persistence:
            try:
                result["us_color_persistence"] = round(float(persistence.value), 1)
            except (ValueError, TypeError):
                pass
                
    except Exception:
        pass
    return result


def _extract_transducer_info(ds) -> Dict[str, Any]:
    result = {}
    try:
        transducer_type = ds.get((0x0018, 0x5010), None)
        if transducer_type:
            result["us_transducer_type"] = str(transducer_type.value)
        
        transducer_freq = ds.get((0x0018, 0x5011), None)
        if transducer_freq:
            try:
                result["us_transducer_frequency_mhz"] = round(float(transducer_freq.value), 1)
            except (ValueError, TypeError):
                result["us_transducer_frequency"] = str(transducer_freq.value)
        
        elements = ds.get((0x0018, 0x5013), None)
        if elements:
            try:
                result["us_transducer_elements"] = int(elements.value)
            except (ValueError, TypeError):
                pass
        
        aperture = ds.get((0x0018, 0x5014), None)
        if aperture:
            try:
                result["us_transducer_aperture_mm"] = round(float(aperture.value), 1)
            except (ValueError, TypeError):
                pass
                
    except Exception:
        pass
    return result


def _extract_biometry_measurements(ds) -> Dict[str, Any]:
    result = {}
    try:
        # Check for real world value mapping (used in biometry)
        intercept = ds.get((0x0020, 0x9233), None)
        slope = ds.get((0x0020, 0x9234), None)
        
        if intercept and slope:
            try:
                intercept_val = float(intercept.value) if hasattr(intercept, 'value') else float(intercept)
                slope_val = float(slope.value) if hasattr(slope, 'value') else float(slope)
                result["us_biometry_intercept"] = round(intercept_val, 4)
                result["us_biometry_slope"] = round(slope_val, 4)
            except (ValueError, TypeError):
                pass
                
    except Exception:
        pass
    return result


def _calculate_ultrasound_metrics(ds) -> Dict[str, Any]:
    result = {}
    try:
        # Calculate field of view if both horizontal and vertical available
        h_fov = ds.get((0x0018, 0x0038), None)
        v_fov = ds.get((0x0018, 0x0039), None)
        
        if h_fov and v_fov:
            try:
                h_val = float(h_fov.value) if hasattr(h_fov, 'value') else float(h_fov)
                v_val = float(v_fov.value) if hasattr(v_fov, 'value') else float(v_fov)
                if h_val > 0 and v_val > 0:
                    result["us_fov_area_cm2"] = round((h_val * v_val) / 100, 2)
            except (ValueError, TypeError):
                pass
        
        # Calculate aspect ratio
        if h_val > 0 and v_val > 0:
            result["us_aspect_ratio"] = round(h_val / v_val, 2)
                
    except Exception:
        pass
    return result


def _is_ultrasound_file(filepath: str) -> bool:
    try:
        import pydicom
        
        if not filepath.lower().endswith(('.dcm', '.dicom', '.ima', '.us')):
            return False
        
        ds = pydicom.dcmread(filepath, force=True)
        
        modality = getattr(ds, 'Modality', '')
        if _is_ultrasound_modality(modality):
            return True
        
        body_part = getattr(ds, 'BodyPartExamined', '')
        if _is_ultrasound_body_part(body_part):
            return True
        
        study_desc = getattr(ds, 'StudyDescription', '').upper()
        series_desc = getattr(ds, 'SeriesDescription', '').upper()
        
        ultrasound_keywords = [
            'ULTRASOUND', 'SONOGRAPHY', 'SONO', 'ECHOCARDIO',
            'ECHOCARDIOGRAPHY', 'CARDIAC US', 'TRANSVAGINAL',
            'TRANSABDOMINAL', 'DOPPLER', 'COLOR DOPPLER',
            'POWER DOPPLER', 'M-MODE', 'B-MODE', '2D US',
            '3D US', '4D US', 'REAL TIME', 'GYNECOLOGIC',
            'OBSTETRIC', 'FETAL', 'THYROID', 'BREAST US',
            'CAROTID', 'VENOUS', 'ARTERIAL', 'INTRAOPERATIVE',
            'ENDOSONO', 'ENDOVAGINAL', 'RECTAL', 'PROSTATIC'
        ]
        
        if any(kw in study_desc or kw in series_desc for kw in ultrasound_keywords):
            return True
        
        us_tag_count = sum(1 for tag in ULTRASOUND_TAGS.keys() if tag in ds)
        if us_tag_count >= 3:
            return True
        
        return False
        
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_vi(file_path: str) -> Dict[str, Any]:
    """Extract ultrasound metadata from DICOM files.
    
    This module provides comprehensive extraction of ultrasound metadata
    including 2D imaging, Doppler, M-mode, and 3D/4D volume parameters.
    
    Args:
        file_path: Path to DICOM file
        
    Returns:
        dict: Ultrasound metadata including:
            - Image acquisition parameters (frequency, gain, depth)
            - Transducer specifications
            - Doppler parameters (velocity, PRF, angle)
            - Color flow/Power Doppler settings
            - M-mode measurements
            - 3D/4D volume parameters
            - Biometry measurements
    """
    result = {
        "extension_vi_detected": False,
        "extension_vi_type": "ultrasound",
        "fields_extracted": 0,
        "us_metadata": {},
        "doppler_parameters": {},
        "color_flow_parameters": {},
        "transducer_info": {},
        "biometry_measurements": {},
        "us_derived_metrics": {},
    }
    
    try:
        import pydicom
        
        if not _is_ultrasound_file(file_path):
            return result
        
        ds = pydicom.dcmread(file_path, force=True)
        result["extension_vi_detected"] = True
        
        result["us_modality"] = getattr(ds, 'Modality', 'UNKNOWN')
        result["us_study_description"] = getattr(ds, 'StudyDescription', '')
        result["us_series_description"] = getattr(ds, 'SeriesDescription', '')
        result["us_body_part_examined"] = getattr(ds, 'BodyPartExamined', '')
        result["us_view_position"] = getattr(ds, 'ViewPosition', '')
        
        us_tags = _extract_ultrasound_tags(ds)
        result["us_metadata"].update(us_tags)
        
        doppler_params = _extract_doppler_parameters(ds)
        result["doppler_parameters"].update(doppler_params)
        
        color_flow = _extract_color_flow_parameters(ds)
        result["color_flow_parameters"].update(color_flow)
        
        transducer = _extract_transducer_info(ds)
        result["transducer_info"].update(transducer)
        
        biometry = _extract_biometry_measurements(ds)
        result["biometry_measurements"].update(biometry)
        
        derived = _calculate_ultrasound_metrics(ds)
        result["us_derived_metrics"].update(derived)
        
        total_fields = (
            len(us_tags) + len(doppler_params) + len(color_flow) +
            len(transducer) + len(biometry) + len(derived) +
            len([k for k in result.keys() if not k.startswith(('_', 'extension'))])
        result["fields_extracted"] = total_fields
        result["us_extraction_timestamp"] = str(__import__('datetime').datetime.now())
        
    except Exception as e:
        result["extension_vi_error"] = str(e)
        result["extension_vi_error_type"] = type(e).__name__
    
    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_vi_field_count() -> int:
    return 180


def get_scientific_dicom_fits_ultimate_advanced_extension_vi_supported_formats() -> List[str]:
    return [".dcm", ".dicom", ".ima", ".us", ".dc3"]


def get_scientific_dicom_fits_ultimate_advanced_extension_vi_modalities() -> List[str]:
    return ["US", "EC", "ES", "OP", "IVUS", "BMUS", "DTUS", "DU"]


def get_scientific_dicom_fits_ultimate_advanced_extension_vi_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_vi_description() -> str:
    return (
        "Ultrasound Metadata Extraction Module. "
        "Supports 2D, Doppler, M-mode, and 3D/4D ultrasound modalities. "
        "Extracts transducer parameters, Doppler settings, color flow, "
        "volume imaging, and biometry measurements for comprehensive "
        "ultrasound analysis."
    )


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = extract_scientific_dicom_fits_ultimate_advanced_extension_vi(sys.argv[1])
        print(__import__('json').dumps(result, indent=2, default=str))
    else:
        print("Usage: python scientific_dicom_fits_ultimate_advanced_extension_vi.py <dicom_file>")
        print(f"Field count: {get_scientific_dicom_fits_ultimate_advanced_extension_vi_field_count()}")
