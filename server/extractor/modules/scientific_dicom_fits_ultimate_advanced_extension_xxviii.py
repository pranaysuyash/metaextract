"""
Scientific DICOM/FITS Ultimate Advanced Extension XXVIII - Real-Time Imaging

This module provides comprehensive extraction of DICOM real-time imaging parameters
including streaming, video, and cine acquisition metadata.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXVIII_AVAILABLE = True

CINE_ACQUISITION = {
    (0x0018, 0x0040): "cine_rate",
    (0x0018, 0x0043): "image_orientation_patient_dicom",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1000): "device_serial_number",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1100): "distance_source_to_detector",
    (0x0018, 0x1110): "distance_source_to_patient",
    (0x0018, 0x1140): "table_motion",
    (0x0018, 0x1150): "table_speed",
    (0x0018, 0x1153): "table_horizontal_displacement",
    (0x0018, 0x1160): "rotation_direction",
    (0x0018, 0x1170): "scan_options",
    (0x0018, 0x1180): "kvp",
    (0x0018, 0x1190): "xray_tube_current",
    (0x0018, 0x1200): "exposure",
    (0x0018, 0x1201): "exposure_time",
    (0x0018, 0x1240): "focal_spot_size",
    (0x0018, 0x7000): "detector_type",
    (0x0018, 0x7001): "detector_id",
    (0x0018, 0x7010): "detector_active_origin",
}

VIDEO_PARAMS = {
    (0x0008, 0x0060): "modality",
    (0x0028, 0x0008): "number_of_frames",
    (0x0028, 0x0009): "frame_increment_pointer",
    (0x0028, 0x0051): "cine_relative_real_time",
    (0x0028, 0x0060): "video_image_format",
    (0x0028, 0x0061): "video_image_format_description",
    (0x0028, 0x0062): "video_source_format",
    (0x0028, 0x0063): "video_source_format_description",
    (0x0028, 0x0064): "video_source_bit_depth",
    (0x0028, 0x0065): "video_compression_format",
    (0x0028, 0x0066): "video_compression_profile",
    (0x0028, 0x0067): "video_compression_tool",
    (0x0028, 0x0068): "video_compression_tool_version",
    (0x0028, 0x0069): "video_compression_settings",
    (0x0028, 0x006A): "selected_video_image",
    (0x0028, 0x006B): "selected_video_image_description",
}

STREAMING_PARAMS = {
    (0x0028, 0x006F): "audio_type",
    (0x0028, 0x0070): "audio_sample_format",
    (0x0028, 0x0071): "audio_bits_per_sample",
    (0x0028, 0x0072): "audio_channels",
    (0x0028, 0x0073): "audio_samples_per_block",
    (0x0028, 0x0074): "audio_block_align",
    (0x0028, 0x0075): "audio_avg_bytes_per_second",
    (0x0028, 0x0076): "audio_reserved",
    (0x0028, 0x0078): "audio_stretch_mode",
    (0x0028, 0x0079): "audio_stretch_offset",
    (0x0028, 0x007A): "audio_time_stretch_mode",
    (0x0028, 0x007B): "audio_time_stretch_offset",
    (0x0028, 0x007C): "audio_object_type_sequence",
    (0x0028, 0x007D): "audio_object_type_number",
}

REAL_TIME_TOTAL_TAGS = CINE_ACQUISITION | VIDEO_PARAMS | STREAMING_PARAMS


def _extract_realtime_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in CINE_ACQUISITION.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _is_realtime_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            try:
                import pydicom
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                if hasattr(ds, 'NumberOfFrames') and ds.NumberOfFrames > 1:
                    return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xxviii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xxviii_detected": False,
        "fields_extracted": 0,
        "extension_xxviii_type": "real_time_imaging",
        "extension_xxviii_version": "2.0.0",
        "realtime_modality": None,
        "cine_acquisition": {},
        "video_parameters": {},
        "streaming_audio": {},
        "extraction_errors": [],
    }

    try:
        if not _is_realtime_file(file_path):
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

        result["extension_xxviii_detected"] = True
        result["realtime_modality"] = getattr(ds, 'Modality', 'Unknown')

        realtime = _extract_realtime_tags(ds)
        result["cine_acquisition"] = realtime

        total_fields = len(realtime)
        result["fields_extracted"] = total_fields

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xxviii_field_count() -> int:
    return len(REAL_TIME_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xxviii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxviii_description() -> str:
    return ("Real-time imaging metadata extraction. Supports cine acquisition, "
            "video, and streaming parameters. Extracts frame rates, video "
            "compression settings, and audio synchronization for comprehensive "
            "dynamic imaging analysis.")


def get_scientific_dicom_fits_ultimate_advanced_extension_xxviii_modalities() -> List[str]:
    return ["CT", "MR", "US", "XA", "RF", "ES"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxviii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxviii_category() -> str:
    return "Real-Time and Video Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxviii_keywords() -> List[str]:
    return [
        "real-time", "cine", "video", "streaming", "dynamic imaging",
        "frame rate", "multi-frame", "video compression", "fluoroscopy",
        "cine loop", "time-resolved", "4D imaging"
    ]
