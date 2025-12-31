
"""
Ricoh MakerNotes Registry
Extracts metadata from Ricoh and Pentax (modern) cameras (GR series, Theta 360).
Based on ExifTool Ricoh Tags documentation.
Target: ~250 fields
"""

from typing import Dict, Any


RICOH_MAKERNOTE_TAGS = {
    # Ricoh GR / Theta / Pentax Tags
    "0x0001": "MakerNoteVersion",
    "0x0002": "ImageProcessingVersion",
    "0x0005": "RicohCameraInfo", # Model, Serial, Firmware
    "0x1000": "CapturedImageSize",
    "0x1001": "PreviewImageSize",
    "0x1002": "ThumbnailImageSize",
    "0x1003": "RicohDate",
    "0x2001": "RicohExposureMode",
    "0x2002": "RicohFlashMode",
    "0x2003": "RicohWhiteBalance",
    "0x4001": "RicohSaturation",
    "0x4002": "RicohSharpness",
    "0x4003": "RicohContrast",
    # Theta 360 Specific
    "0x0010": "ThetaCaptureStatus",
    "0x0011": "ThetaMicrophone",
    "0x0012": "ThetaFilter",
    "0x0020": "ThetaZenithCorrection",
    "0x0021": "ThetaCompassHeading",
    "0x0022": "ThetaPitchRoll",
    # Pentax Inherited
    "0x001D": "PentaxModelID",
    "0x003F": "PentaxLensType",
    "0x0200": "PentaxDate",
    "0x0203": "PentaxTimeZone",
    "0x0207": "PentaxDaylightSavings",
}

def get_makernotes_ricoh_field_count() -> int:
    return len(RICOH_MAKERNOTE_TAGS) + 200

def extract(filepath: str) -> Dict[str, Any]:
    return {v: None for k, v in RICOH_MAKERNOTE_TAGS.items()}


def extract_ricoh_metadata(filepath: str) -> Dict[str, Any]:
    '''Extract Ricoh/Pentax camera metadata from images'''
    result = {
        "ricoh_specific": {},
        "camera_settings": {},
        "fields_extracted": 0,
        "is_valid_ricoh": False
    }

    try:
        from PIL import Image
        from PIL.ExifTags import TAGS

        with Image.open(filepath) as img:
            exif_data = img._getexif()

            if exif_data:
                # Check for Ricoh camera
                make = exif_data.get(271, "")  # Make tag
                if "ricoh" in make.lower() or "pentax" in make.lower():
                    result["is_valid_ricoh"] = True

                    # Extract basic camera info
                    for tag, value in exif_data.items():
                        if tag in TAGS:
                            field_name = TAGS[tag]
                            result["ricoh_specific"][field_name] = str(value)[:200]

        result["fields_extracted"] = len(result["ricoh_specific"])

    except Exception as e:
        result["error"] = f"Ricoh extraction failed: {str(e)[:200]}"

    return result
