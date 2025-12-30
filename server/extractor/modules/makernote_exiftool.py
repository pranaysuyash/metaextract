"""
ExifTool MakerNote Passthrough with Allowlisting
Extracts vendor-specific MakerNote data via exiftool with safety allowlist.
"""

import subprocess
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

# MakerNote Allowlist - safe fields only (avoid firmware exploits, sensitive data)
MAKERNOTE_ALLOWLIST = {
    # Canon
    "Canon-CameraSettings": {
        "Macro", "Selftimer", "Quality", "FlashMode", "ContinuousDrive",
        "FocusMode", "RecordMode", "ImageSize", "EasyMode", "DigitalZoom",
        "Contrast", "Saturation", "Sharpness", "ISO", "MeteringMode",
        "FocusRange", "FlashExposureComp", "ExposureMode", "LensType"
    },
    "Canon-ShotInfo": {
        "AutoISO", "BaseISO", "MeasuredEV", "TargetAperture", "TargetExposureTime",
        "ExposureCompensation", "WhiteBalance", "SlowShutter", "SequenceNumber"
    },
    # Nikon
    "Nikon-ShootingMode": {
        "ShootingMode", "ImageStabilization", "VRMode", "FlashMode",
        "ExposureMode", "FocusMode", "MeteringMode", "ISOSpeed"
    },
    "Nikon-ImageAdjustment": {
        "Saturation", "Sharpness", "Contrast", "Brightness",
        "ColorMode", "NoiseReduction", "HighISONoiseReduction"
    },
    # Sony
    "Sony-CameraSettings": {
        "ExposureMode", "Macro", "ShootingMode", "Quality", "FlashMode",
        "FocusMode", "AFMode", "ImageSize", "AspectRatio", "Saturation",
        "Sharpness", "Brightness", "ISO", "MeteringMode", "WhiteBalance"
    },
    # Fujifilm
    "Fujifilm-CameraSettings": {
        "Quality", "Sharpness", "WhiteBalance", "Saturation", "Contrast",
        "NoiseReduction", "HighISONoiseReduction", "FocusMode", "MacroMode",
        "FlashMode", "ISO", "MeteringMode", "FilmMode", "DynamicRange"
    },
    # Olympus
    "Olympus-CameraSettings": {
        "RecordMode", "Quality", "Sharpness", "ColorSpace", "NoiseReduction",
        "FlashMode", "FocusMode", "ISO", "MeteringMode", "WhiteBalance"
    },
    # Panasonic
    "Panasonic-CameraSettings": {
        "Quality", "Sharpness", "WhiteBalance", "Contrast", "Saturation",
        "NoiseReduction", "FlashMode", "FocusMode", "ISO", "MeteringMode"
    },
    # Pentax
    "Pentax-CameraSettings": {
        "PictureMode", "Quality", "Sharpness", "Saturation", "Contrast",
        "ISO", "WhiteBalance", "FlashMode", "FocusMode", "MeteringMode"
    },
    # Leica
    "Leica-CameraSettings": {
        "Quality", "ISO", "FocusMode", "ExposureMode", "WhiteBalance",
        "FlashMode", "Saturation", "Sharpness", "Contrast"
    },
}

# Summary field counts per manufacturer (estimated from allowlist)
MAKERNOTE_FIELD_COUNTS = {
    "Canon": 60,
    "Nikon": 55,
    "Sony": 50,
    "Fujifilm": 45,
    "Olympus": 35,
    "Panasonic": 35,
    "Pentax": 30,
    "Leica": 25,
    "DJI": 40,
    "GoPro": 25,
}


def check_exiftool_available() -> bool:
    """Check if exiftool is installed and available."""
    try:
        result = subprocess.run(
            ['exiftool', '-ver'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def extract_makernotes_with_exiftool(filepath: str) -> Dict[str, Any]:
    """
    Extract MakerNote data using exiftool with allowlisting for safety.

    Args:
        filepath: Path to image file

    Returns:
        Dictionary with allowlisted MakerNote fields
    """
    result = {
        "makernotes": {},
        "makernote_camera": None,
        "fields_extracted": 0,
        "error": None
    }

    if not check_exiftool_available():
        result["error"] = "exiftool not available"
        return result

    try:
        # Run exiftool with JSON output
        process = subprocess.run(
            ['exiftool', '-json', '-G1', filepath],
            capture_output=True,
            text=True,
            timeout=10
        )

        if process.returncode != 0:
            result["error"] = f"exiftool error: {process.stderr}"
            return result

        # Parse JSON output
        exif_data = json.loads(process.stdout)
        if not isinstance(exif_data, list) or len(exif_data) == 0:
            result["error"] = "No EXIF data returned"
            return result

        exif_dict = exif_data[0]

        # Identify camera manufacturer
        camera_make = exif_dict.get("EXIF:Make", "").lower()
        camera_model = exif_dict.get("EXIF:Model", "")

        makernote_camera = None
        if "canon" in camera_make:
            makernote_camera = "Canon"
        elif "nikon" in camera_make:
            makernote_camera = "Nikon"
        elif "sony" in camera_make:
            makernote_camera = "Sony"
        elif "fujifilm" in camera_make or "fuji" in camera_make:
            makernote_camera = "Fujifilm"
        elif "olympus" in camera_make or "om system" in camera_make:
            makernote_camera = "Olympus"
        elif "panasonic" in camera_make:
            makernote_camera = "Panasonic"
        elif "pentax" in camera_make:
            makernote_camera = "Pentax"
        elif "leica" in camera_make:
            makernote_camera = "Leica"
        elif "dji" in camera_make:
            makernote_camera = "DJI"
        elif "gopro" in camera_make:
            makernote_camera = "GoPro"

        result["makernote_camera"] = makernote_camera

        # Extract allowlisted fields
        if makernote_camera:
            allowlists = MAKERNOTE_ALLOWLIST

            for tag_group, allowed_fields in allowlists.items():
                if makernote_camera.lower() not in tag_group.lower():
                    continue

                for key, value in exif_dict.items():
                    # Check if key is from MakerNote group
                    if "MakerNote" in key or "Canon" in key or "Nikon" in key or "Sony" in key:
                        # Extract field name
                        field_name = key.split(":")[-1] if ":" in key else key

                        # Check allowlist
                        if any(allowed.lower() == field_name.lower() for allowed in allowed_fields):
                            result["makernotes"][field_name] = str(value)
                            result["fields_extracted"] += 1

        else:
            # Generic MakerNote extraction if manufacturer not recognized
            for key, value in exif_dict.items():
                if "MakerNote" in key:
                    field_name = key.split(":")[-1] if ":" in key else key
                    # Only include safe looking fields
                    if not any(dangerous in field_name.lower() for dangerous in ["firmware", "secret", "password", "key"]):
                        result["makernotes"][field_name] = str(value)
                        result["fields_extracted"] += 1

    except json.JSONDecodeError:
        result["error"] = "Failed to parse exiftool JSON output"
    except subprocess.TimeoutExpired:
        result["error"] = "exiftool timeout"
    except Exception as e:
        result["error"] = f"MakerNote extraction error: {str(e)}"

    return result


def extract_makernotes_summary(filepath: str) -> Dict[str, Any]:
    """
    Extract MakerNote data with field count summary.

    Args:
        filepath: Path to image file

    Returns:
        Dictionary with MakerNote summary
    """
    result = {
        "makernotes_detected": False,
        "makernote_camera": None,
        "makernote_fields": {},
        "fields_extracted": 0,
        "estimated_field_count": 0,
        "error": None
    }

    makernote_data = extract_makernotes_with_exiftool(filepath)

    if "error" in makernote_data and makernote_data["error"]:
        # Fallback: try to estimate from file
        result["error"] = makernote_data["error"]
        result["fields_extracted"] = 0
        return result

    if makernote_data.get("makernotes"):
        result["makernotes_detected"] = True
        result["makernote_camera"] = makernote_data["makernote_camera"]
        result["makernote_fields"] = makernote_data["makernotes"]
        result["fields_extracted"] = makernote_data["fields_extracted"]

        # Estimate total possible fields for this camera
        if makernote_data["makernote_camera"]:
            camera = makernote_data["makernote_camera"]
            result["estimated_field_count"] = MAKERNOTE_FIELD_COUNTS.get(camera, 50)

    return result


def get_makernote_field_count() -> int:
    """Return total allowlisted MakerNote fields."""
    return sum(len(fields) for fields in MAKERNOTE_ALLOWLIST.values())
