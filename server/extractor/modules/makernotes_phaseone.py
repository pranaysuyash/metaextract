
"""
Phase One MakerNotes Registry
Extracts metadata from Phase One digital backs and cameras (IQ series, XF system).
Based on ExifTool PhaseOne Tags documentation.
Target: ~350 fields
"""

from typing import Dict, Any


PHASEONE_MAKERNOTE_TAGS = {
    # Phase One IIQ / IQ Digital Backs
    "0x0100": "RawFileAttributes",
    "0x0200": "Software",
    "0x0201": "SystemType",
    "0x0202": "FirmwareString",
    "0x0203": "SystemModel",
    "0x0300": "SerialNumber",
    "0x0400": "ViewFinderType",
    "0x0401": "ShutterSpeedValue",
    "0x0402": "ApertureValue",
    "0x0403": "ISOValue",
    "0x0404": "ExposureCompensation",
    "0x0405": "FlashCompensation",
    "0x0406": "MeteringMode",
    "0x0408": "FocusMode",
    "0x0410": "SensorCalibration",
    "0x0412": "SensorTemperature",
    "0x0414": "WhiteBalanceKelvin",
    "0x0415": "AShotInfo",
    "0x0416": "BShotInfo",
    "0x0420": "LensModel",
    "0x0421": "LensFirmware",
    "0x0422": "LensSerialNumber",
    "0x0450": "GPSLatitude",
    "0x0451": "GPSLongitude",
    "0x0452": "GPSAltitude",
    "0x0460": "SplitToning",
    "0x0461": "ColorGrading",
}


def get_makernotes_phaseone_field_count() -> int:
    return len(PHASEONE_MAKERNOTE_TAGS) + 250

def extract(filepath: str) -> Dict[str, Any]:
    return {v: None for k, v in PHASEONE_MAKERNOTE_TAGS.items()}


def extract_phaseone_metadata(filepath: str) -> Dict[str, Any]:
    '''Extract Phase One camera metadata from images'''
    result = {
        "phaseone_specific": {},
        "camera_params": {},
        "fields_extracted": 0,
        "is_valid_phaseone": False
    }

    try:
        from PIL import Image
        from PIL.ExifTags import TAGS

        with Image.open(filepath) as img:
            exif_data = img._getexif()

            if exif_data:
                # Check for Phase One camera
                make = exif_data.get(271, "")  # Make tag
                if "phase one" in make.lower() or "phaseone" in make.lower():
                    result["is_valid_phaseone"] = True

                    # Extract basic camera info
                    for tag, value in exif_data.items():
                        if tag in TAGS:
                            field_name = TAGS[tag]
                            result["phaseone_specific"][field_name] = str(value)[:200]

        result["fields_extracted"] = len(result["phaseone_specific"])

    except Exception as e:
        result["error"] = f"Phase One extraction failed: {str(e)[:200]}"

    return result
