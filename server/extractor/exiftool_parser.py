#!/usr/bin/env python3
"""
ExifTool Integration for MetaExtract

Provides comprehensive metadata extraction using exiftool CLI,
including parsed MakerNote data for all major camera manufacturers.

Requires: exiftool installed on the system
  - macOS: brew install exiftool
  - Ubuntu: apt install libimage-exiftool-perl
  - Windows: Download from https://exiftool.org/

This module extracts ~7000+ fields including:
- Complete Canon MakerNote (~80 fields)
- Complete Nikon MakerNote (~70 fields)  
- Complete Sony MakerNote (~60 fields)
- Complete Fujifilm MakerNote (~50 fields)
- Olympus, Panasonic, Pentax, Leica MakerNotes
- Full IPTC-IIM metadata (~50 fields)
- Full XMP metadata (~200+ namespaces)
- Video encoding parameters (H.264, HEVC, etc.)
- Audio codec details (MP3, AAC, FLAC specifics)
"""

import json
import subprocess
import logging
import shutil
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

try:
    from .metadata_engine import categorize_exiftool_output as categorize_exiftool_output_base
except ImportError:
    try:
        from metadata_engine import categorize_exiftool_output as categorize_exiftool_output_base  # type: ignore
    except ImportError:
        categorize_exiftool_output_base = None  # type: ignore

logger = logging.getLogger("metaextract.exiftool")

# Check if exiftool is available
EXIFTOOL_PATH = shutil.which("exiftool")
EXIFTOOL_AVAILABLE = EXIFTOOL_PATH is not None

if not EXIFTOOL_AVAILABLE:
    logger.warning("exiftool not found - MakerNote parsing will be limited")


# ============================================================================
# MakerNote Field Mappings by Manufacturer
# ============================================================================

CANON_MAKERNOTE_FIELDS = {
    # Camera Settings
    "MacroMode", "SelfTimer", "Quality", "CanonFlashMode", "ContinuousDrive",
    "FocusMode", "RecordMode", "CanonImageSize", "EasyMode", "DigitalZoom",
    "Contrast", "Saturation", "Sharpness", "CameraISO", "MeteringMode",
    "FocusRange", "AFPoint", "CanonExposureMode", "LensType", "MaxFocalLength",
    "MinFocalLength", "FocalUnits", "MaxAperture", "MinAperture",
    # Shot Info
    "AutoISO", "BaseISO", "MeasuredEV", "TargetAperture", "TargetExposureTime",
    "ExposureCompensation", "WhiteBalance", "SlowShutter", "SequenceNumber",
    "OpticalZoomCode", "CameraTemperature", "FlashGuideNumber", "AFPointsInFocus",
    "FlashExposureComp", "AutoExposureBracketing", "AEBBracketValue", "ControlMode",
    "FocusDistanceUpper", "FocusDistanceLower", "FNumber", "ExposureTime",
    "MeasuredEV2", "BulbDuration", "CameraType", "AutoRotate", "NDFilter",
    # Processing
    "ColorTone", "ColorSpace", "CanonImageType", "CanonFirmwareVersion",
    "FileNumber", "OwnerName", "SerialNumber", "InternalSerialNumber",
    "ColorDataVersion", "WBBracketMode", "WBBracketValueAB", "WBBracketValueGM",
    "FilterEffect", "ToningEffect", "MacroMagnification", "LiveViewShooting",
    "AFAreaMode", "AFPointSelected", "PrimaryAFPoint", "LensSerialNumber",
    "DustRemovalData", "CropInfo", "AspectRatio", "LensInfo",
}

NIKON_MAKERNOTE_FIELDS = {
    # Shooting Mode
    "ShootingMode", "ImageStabilization", "VRMode", "VibrationReduction",
    "AutoBracketRelease", "ProgramShift", "ExposureDifference", "FlashSyncMode",
    "FlashShutter", "FlashExposureComp", "FlashBracketComp", "FlashFocal",
    "FlashMode", "FlashSetting", "FlashType", "FlashInfo", "FlashColorFilter",
    "FlashGNDistance", "FlashFirmware",
    # Image Adjustment
    "ColorMode", "ImageAdjustment", "HueAdjustment", "NoiseReduction",
    "HighISONoiseReduction", "Saturation", "Sharpness", "Contrast",
    "Brightness", "FilterEffect", "ToningEffect", "MonochromeFilterEffect",
    "MonochromeToningEffect",
    # Focus Info
    "AFInfo", "AFInfo2", "AFAreaMode", "PhaseDetectAF", "ContrastDetectAF",
    "AFPointsUsed", "AFImageWidth", "AFImageHeight", "AFAreaXPosition",
    "AFAreaYPosition", "AFAreaWidth", "AFAreaHeight", "ContrastDetectAFInFocus",
    "FocusMode", "FocusPosition", "FocusDistance",
    # Scene Info
    "SceneMode", "SceneAssist", "SubjectProgram", "ActiveD-Lighting",
    "VignetteControl", "PictureControlData", "PictureControlVersion",
    "PictureControlName", "PictureControlBase",
    # Other
    "SerialNumber", "ShutterCount", "InternalSerialNumber", "LensData",
    "LensInfo", "RetouchHistory", "ImageDustOff", "MultiExposure",
}

SONY_MAKERNOTE_FIELDS = {
    # Camera Settings
    "ExposureMode", "ExposureCompensation", "Macro", "ShootingMode",
    "Quality", "SonyFlashMode", "FlashLevel", "ReleaseMode", "SequenceNumber",
    "AntiBlur", "SonyFocusMode", "AFMode", "AFIlluminator", "AFPoint",
    "FocusPosition", "Rotation", "SonyImageStabilization", "SonyImageSize",
    "SonyAspectRatio", "SonyContrast", "SonySaturation", "SonySharpness",
    "SonyBrightness", "ColorTemperature", "ColorCompensationFilter",
    # Shot Info
    "LongExposureNoiseReduction", "HighISONoiseReduction", "HDR",
    "MultiFrameNoiseReduction", "PictureEffect", "SoftSkinEffect",
    "VignetteCorrection", "LateralChromaticAberration", "DistortionCorrection",
    "WBShiftAB", "WBShiftGM", "AutoPortraitFramed",
    # Scene Info
    "SonySceneMode", "ZoneMatching", "DynamicRangeOptimizer", "CreativeStyle",
    "SonyColorMode", "FaceDetection", "FaceInfo",
    # Lens Info
    "SonyLensType", "LensInfo", "DistortionCorrParams", "SonyDateTime",
    "InternalSerialNumber", "ImageCount",
}

FUJIFILM_MAKERNOTE_FIELDS = {
    # Camera Settings
    "Version", "InternalSerialNumber", "Quality", "FujiSharpness",
    "FujiWhiteBalance", "FujiSaturation", "FujiContrast", "ColorTemperature",
    "FujiNoiseReduction", "HighISONoiseReduction", "FujiFlashMode",
    "FlashExposureComp", "FujiMacro", "FujiFocusMode", "SlowSync",
    "PictureMode", "ExposureCount", "Bracketing", "SequenceNumber",
    "BlurWarning", "FocusWarning", "ExposureWarning",
    # Film Simulation
    "FilmMode", "DynamicRange", "Development", "MinFocalLength",
    "MaxFocalLength", "MaxApertureAtMinFocal", "MaxApertureAtMaxFocal",
    "AutoDynamicRange", "FujiImageStabilization", "Rating", "ImageGeneration",
    "FacesDetected", "FacePositions", "NumFaceElements",
    # Other
    "FinePixColor", "SerialNumber", "ContinuousBracket", "DynamicRangeSetting",
    "ShadowTone", "HighlightTone", "ColorChrome", "GrainEffect",
}

# Add more manufacturers
OLYMPUS_MAKERNOTE_FIELDS = {
    "SpecialMode", "CompressionRatio", "PictureMode", "DigitalZoom",
    "SoftwareRelease", "CameraID", "DataDump", "PreviewImage",
    "BlackLevel", "WBMode", "WBBias", "RedBias", "BlueBias",
    "SerialNumber", "FlashDevice", "FocusRange", "MacroFocus",
    "SharpnessFactor", "FlashChargeLevel", "ColorMatrix", "LensType",
}

PANASONIC_MAKERNOTE_FIELDS = {
    "ImageQuality", "FirmwareVersion", "WhiteBalance", "FocusMode",
    "AFAreaMode", "ImageStabilization", "MacroMode", "ShootingMode",
    "Audio", "DataDump", "InternalSerialNumber", "Panasonic-ISO",
    "TextStamp", "OpticalZoomMode", "TimeSincePowerOn", "BurstMode",
    "SequenceNumber", "AdvancedSceneMode", "ShutterType", "SelfTimer",
}


# ============================================================================
# IPTC Field Definitions
# ============================================================================

IPTC_FIELDS = {
    # Envelope Record
    "EnvelopeRecordVersion", "Destination", "FileFormat", "FileFormatVersion",
    "ServiceIdentifier", "EnvelopeNumber", "ProductID", "EnvelopePriority",
    "DateSent", "TimeSent", "CodedCharacterSet", "UniqueObjectName",
    "ARMIdentifier", "ARMVersion",
    
    # Application Record
    "ApplicationRecordVersion", "ObjectTypeReference", "ObjectAttributeReference",
    "ObjectName", "EditStatus", "EditorialUpdate", "Urgency", "SubjectReference",
    "Category", "SupplementalCategories", "FixtureIdentifier", "Keywords",
    "ContentLocationCode", "ContentLocationName", "ReleaseDate", "ReleaseTime",
    "ExpirationDate", "ExpirationTime", "SpecialInstructions", "ActionAdvised",
    "ReferenceService", "ReferenceDate", "ReferenceNumber", "DateCreated",
    "TimeCreated", "DigitalCreationDate", "DigitalCreationTime",
    "OriginatingProgram", "ProgramVersion", "ObjectCycle", "By-line",
    "By-lineTitle", "City", "Sub-location", "Province-State",
    "Country-PrimaryLocationCode", "Country-PrimaryLocationName",
    "OriginalTransmissionReference", "Headline", "Credit", "Source",
    "CopyrightNotice", "Contact", "Caption-Abstract", "Writer-Editor",
    "RasterizedCaption", "ImageType", "ImageOrientation", "LanguageIdentifier",
    "AudioType", "AudioSamplingRate", "AudioSamplingResolution", "AudioDuration",
    "AudioOutcue", "PreviewFileFormat", "PreviewFileFormatVersion", "PreviewData",
}


# ============================================================================
# XMP Namespace Definitions
# ============================================================================

XMP_NAMESPACES = {
    "XMP-dc": "Dublin Core",
    "XMP-xmp": "XMP Basic",
    "XMP-xmpRights": "XMP Rights Management",
    "XMP-xmpMM": "XMP Media Management",
    "XMP-xmpBJ": "XMP Basic Job Ticket",
    "XMP-xmpTPg": "XMP Paged-Text",
    "XMP-xmpDM": "XMP Dynamic Media",
    "XMP-pdf": "Adobe PDF",
    "XMP-photoshop": "Photoshop",
    "XMP-crs": "Camera Raw Settings",
    "XMP-aux": "EXIF Auxiliary",
    "XMP-exif": "EXIF",
    "XMP-exifEX": "EXIF Extended",
    "XMP-tiff": "TIFF",
    "XMP-iptcCore": "IPTC Core",
    "XMP-iptcExt": "IPTC Extension",
    "XMP-plus": "PLUS License Data",
    "XMP-mwg-rs": "MWG Regions",
    "XMP-mwg-kw": "MWG Keywords",
    "XMP-mwg-coll": "MWG Collections",
    "XMP-lr": "Lightroom",
    "XMP-acdsee": "ACDSee",
    "XMP-digiKam": "digiKam",
    "XMP-MP": "Microsoft Photo",
    "XMP-apple-fi": "Apple Face Info",
}


# ============================================================================
# ExifTool Extraction Functions
# ============================================================================

def run_exiftool(filepath: str, args: List[str] = None) -> Optional[Dict[str, Any]]:
    """
    Run exiftool and return parsed JSON output.

    Args:
        filepath: Path to file
        args: Additional exiftool arguments

    Returns:
        Dictionary with extracted metadata
    """
    if not EXIFTOOL_AVAILABLE:
        return None

    # Validate and sanitize filepath to prevent command injection and path traversal
    try:
        path_obj = Path(filepath)

        # Resolve to absolute path to normalize it
        resolved_path = path_obj.resolve()

        # Verify the file exists and is a regular file (not a directory)
        if not resolved_path.exists():
            logger.error(f"File does not exist: {resolved_path}")
            return None

        if not resolved_path.is_file():
            logger.error(f"Path is not a file: {resolved_path}")
            return None

        # Check file size to prevent memory exhaustion (100MB limit)
        file_size = resolved_path.stat().st_size
        max_file_size = 100 * 1024 * 1024  # 100MB in bytes
        if file_size > max_file_size:
            logger.error(f"File too large: {file_size} bytes (max: {max_file_size}) for {resolved_path}")
            return None

        # Additional security check - ensure file is in allowed location
        # This prevents access to sensitive system files
        allowed_base_path = Path.cwd().resolve()  # Use current working directory as base
        try:
            resolved_path.relative_to(allowed_base_path)
        except ValueError:
            logger.error(f"Path traversal attempt detected: {filepath} (resolved: {resolved_path})")
            return None

        # Additional check: ensure the path doesn't contain any unusual characters
        # that might indicate an attempt to inject shell commands
        if any(char in str(resolved_path) for char in [';', '&', '|', '`', '$', '>', '<', '(', ')', '{', '}']):
            logger.error(f"Invalid characters in file path: {filepath}")
            return None

    except Exception as e:
        logger.error(f"Invalid file path: {filepath} - {e}")
        return None

    try:
        cmd = [
            EXIFTOOL_PATH,
            "-j",           # JSON output
            "-n",           # Numeric values
            "-G1",          # Group names level 1
            "-s",           # Short tag names
            "-a",           # Allow duplicate tags
            "-u",           # Unknown tags
            "-f",           # Force processing
        ]

        if args:
            cmd.extend(args)

        # Use the validated and resolved path to prevent path traversal
        cmd.append(str(resolved_path))

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout for large files
            check=False,  # Don't raise exception on non-zero exit
        )

        if result.returncode != 0:
            logger.error(f"exiftool error for {resolved_path}: {result.stderr} (return code: {result.returncode})")
            return None

        data = json.loads(result.stdout)
        return data[0] if data else None

    except subprocess.TimeoutExpired:
        logger.error(f"exiftool timed out for {resolved_path}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse exiftool output for {resolved_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"exiftool error for {resolved_path}: {e}")
        return None


def extract_all_metadata_exiftool(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract ALL metadata using exiftool.
    
    Returns comprehensive metadata including all MakerNotes, IPTC, XMP.
    """
    return run_exiftool(filepath, ["-All"])


def extract_makernotes_exiftool(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract MakerNote data using exiftool.
    
    Returns parsed MakerNote fields for supported manufacturers.
    """
    data = run_exiftool(filepath, ["-MakerNotes:all"])
    if not data:
        return None
    
    # Filter to only MakerNote tags
    makernotes = {}
    for key, value in data.items():
        if key.startswith("MakerNotes:") or key.startswith("Canon:") or \
           key.startswith("Nikon:") or key.startswith("Sony:") or \
           key.startswith("Fujifilm:") or key.startswith("Olympus:") or \
           key.startswith("Panasonic:") or key.startswith("Pentax:") or \
           key.startswith("Leica:") or key.startswith("Samsung:") or \
           key.startswith("Apple:") or key.startswith("DJI:") or \
           key.startswith("GoPro:") or key.startswith("Hasselblad:") or \
           key.startswith("PhaseOne:"):
            makernotes[key] = value
    
    return makernotes if makernotes else None


def extract_iptc_exiftool(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract IPTC metadata using exiftool.
    
    Returns all IPTC-IIM fields.
    """
    data = run_exiftool(filepath, ["-IPTC:all"])
    if not data:
        return None
    
    iptc = {}
    for key, value in data.items():
        if key.startswith("IPTC:"):
            clean_key = key.replace("IPTC:", "")
            iptc[clean_key] = value
    
    return iptc if iptc else None


def extract_xmp_exiftool(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract XMP metadata using exiftool.
    
    Returns all XMP namespaces and fields.
    """
    data = run_exiftool(filepath, ["-XMP:all"])
    if not data:
        return None
    
    xmp = {}
    for key, value in data.items():
        if key.startswith("XMP"):
            xmp[key] = value
    
    return xmp if xmp else None


def extract_video_codec_details(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract video codec-specific parameters using exiftool.
    
    Includes H.264/HEVC profile, level, encoding settings.
    """
    data = run_exiftool(filepath, [
        "-QuickTime:all",
        "-Track*:all", 
        "-H264:all",
        "-HEVC:all",
        "-VP8:all",
        "-VP9:all",
        "-AV1:all",
    ])
    
    if not data:
        return None
    
    codec_info = {}
    for key, value in data.items():
        if any(prefix in key for prefix in [
            "QuickTime:", "Track", "H264:", "HEVC:", "VP", "AV1:",
            "VideoCodec", "AudioCodec", "CompressorID", "MediaFormat"
        ]):
            codec_info[key] = value
    
    return codec_info if codec_info else None


def extract_audio_codec_details(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract audio codec-specific parameters using exiftool.
    
    Includes MP3/AAC/FLAC specific fields.
    """
    data = run_exiftool(filepath, [
        "-ID3:all",
        "-FLAC:all", 
        "-Vorbis:all",
        "-APE:all",
        "-ASF:all",
        "-RIFF:all",
        "-M4A:all",
        "-Opus:all",
    ])
    
    if not data:
        return None
    
    audio_info = {}
    for key, value in data.items():
        if any(prefix in key for prefix in [
            "ID3:", "FLAC:", "Vorbis:", "APE:", "ASF:", "RIFF:",
            "Composite:", "LAME", "Encoder", "Codec", "Audio"
        ]):
            audio_info[key] = value
    
    return audio_info if audio_info else None


# ============================================================================
# Organized Extraction
# ============================================================================

def categorize_exiftool_output(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Organize exiftool output into logical categories.
    
    Returns:
        Dictionary with categorized metadata
    """
    if categorize_exiftool_output_base:
        return categorize_exiftool_output_base(data)

    categories = {
        "file": {},
        "exif": {},
        "image": {},
        "gps": {},
        "makernote": {
            "canon": {},
            "nikon": {},
            "sony": {},
            "fujifilm": {},
            "olympus": {},
            "panasonic": {},
            "pentax": {},
            "leica": {},
            "apple": {},
            "dji": {},
            "gopro": {},
            "samsung": {},
            "other": {},
        },
        "iptc": {},
        "xmp": {
            "dc": {},          # Dublin Core
            "xmp": {},         # XMP Basic
            "xmpRights": {},   # Rights
            "xmpMM": {},       # Media Management
            "photoshop": {},   # Photoshop
            "crs": {},         # Camera Raw
            "lr": {},          # Lightroom
            "iptcCore": {},    # IPTC Core
            "iptcExt": {},     # IPTC Extension
            "other": {},
        },
        "video": {
            "format": {},
            "codec": {},
            "encoding": {},
            "quicktime": {},
        },
        "audio": {
            "format": {},
            "codec": {},
            "id3": {},
            "tags": {},
        },
        "composite": {},
        "other": {},
    }
    
    for key, value in data.items():
        # Skip null/empty values
        if value is None or value == "" or value == "-":
            continue
        
        # File info
        if key.startswith("System:") or key.startswith("File:"):
            clean_key = key.split(":", 1)[1] if ":" in key else key
            categories["file"][clean_key] = value
            
        # EXIF
        elif key.startswith("EXIF:"):
            clean_key = key.replace("EXIF:", "")
            categories["exif"][clean_key] = value
            
        # GPS
        elif key.startswith("GPS:") or "GPS" in key:
            clean_key = key.replace("GPS:", "").replace("EXIF:", "")
            categories["gps"][clean_key] = value
            
        # MakerNotes by manufacturer
        elif key.startswith("Canon:"):
            categories["makernote"]["canon"][key.replace("Canon:", "")] = value
        elif key.startswith("Nikon:"):
            categories["makernote"]["nikon"][key.replace("Nikon:", "")] = value
        elif key.startswith("Sony:"):
            categories["makernote"]["sony"][key.replace("Sony:", "")] = value
        elif key.startswith("Fujifilm:"):
            categories["makernote"]["fujifilm"][key.replace("Fujifilm:", "")] = value
        elif key.startswith("Olympus:"):
            categories["makernote"]["olympus"][key.replace("Olympus:", "")] = value
        elif key.startswith("Panasonic:"):
            categories["makernote"]["panasonic"][key.replace("Panasonic:", "")] = value
        elif key.startswith("Pentax:"):
            categories["makernote"]["pentax"][key.replace("Pentax:", "")] = value
        elif key.startswith("Leica:"):
            categories["makernote"]["leica"][key.replace("Leica:", "")] = value
        elif key.startswith("Apple:"):
            categories["makernote"]["apple"][key.replace("Apple:", "")] = value
        elif key.startswith("DJI:"):
            categories["makernote"]["dji"][key.replace("DJI:", "")] = value
        elif key.startswith("GoPro:"):
            categories["makernote"]["gopro"][key.replace("GoPro:", "")] = value
        elif key.startswith("Samsung:"):
            categories["makernote"]["samsung"][key.replace("Samsung:", "")] = value
        elif key.startswith("MakerNotes:"):
            categories["makernote"]["other"][key.replace("MakerNotes:", "")] = value
            
        # IPTC
        elif key.startswith("IPTC:"):
            categories["iptc"][key.replace("IPTC:", "")] = value
            
        # XMP namespaces
        elif key.startswith("XMP-dc:"):
            categories["xmp"]["dc"][key.replace("XMP-dc:", "")] = value
        elif key.startswith("XMP-xmp:"):
            categories["xmp"]["xmp"][key.replace("XMP-xmp:", "")] = value
        elif key.startswith("XMP-xmpRights:"):
            categories["xmp"]["xmpRights"][key.replace("XMP-xmpRights:", "")] = value
        elif key.startswith("XMP-xmpMM:"):
            categories["xmp"]["xmpMM"][key.replace("XMP-xmpMM:", "")] = value
        elif key.startswith("XMP-photoshop:"):
            categories["xmp"]["photoshop"][key.replace("XMP-photoshop:", "")] = value
        elif key.startswith("XMP-crs:"):
            categories["xmp"]["crs"][key.replace("XMP-crs:", "")] = value
        elif key.startswith("XMP-lr:"):
            categories["xmp"]["lr"][key.replace("XMP-lr:", "")] = value
        elif key.startswith("XMP-iptcCore:"):
            categories["xmp"]["iptcCore"][key.replace("XMP-iptcCore:", "")] = value
        elif key.startswith("XMP-iptcExt:"):
            categories["xmp"]["iptcExt"][key.replace("XMP-iptcExt:", "")] = value
        elif key.startswith("XMP"):
            categories["xmp"]["other"][key] = value
            
        # Video
        elif key.startswith("QuickTime:"):
            categories["video"]["quicktime"][key.replace("QuickTime:", "")] = value
        elif key.startswith("H264:") or key.startswith("HEVC:"):
            categories["video"]["codec"][key] = value
        elif "Video" in key or "Track" in key:
            categories["video"]["format"][key] = value
            
        # Audio
        elif key.startswith("ID3:"):
            categories["audio"]["id3"][key.replace("ID3:", "")] = value
        elif key.startswith("FLAC:") or key.startswith("Vorbis:"):
            categories["audio"]["codec"][key] = value
        elif "Audio" in key:
            categories["audio"]["format"][key] = value
            
        # Composite (calculated by exiftool)
        elif key.startswith("Composite:"):
            categories["composite"][key.replace("Composite:", "")] = value
            
        # Everything else
        else:
            categories["other"][key] = value
    
    # Clean up empty categories
    def remove_empty(d):
        if isinstance(d, dict):
            return {k: remove_empty(v) for k, v in d.items() if v and (not isinstance(v, dict) or remove_empty(v))}
        return d
    
    return remove_empty(categories)


def extract_comprehensive_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract comprehensive metadata using exiftool.
    
    This is the main entry point for exiftool-based extraction.
    
    Returns:
        Categorized metadata dictionary with all available fields
    """
    # Get all metadata
    raw_data = extract_all_metadata_exiftool(filepath)
    
    if not raw_data:
        return {"error": "exiftool extraction failed", "available": False}
    
    # Categorize the output
    categorized = categorize_exiftool_output(raw_data)
    
    # Add metadata counts
    def count_fields(d: Dict, depth: int = 0) -> int:
        count = 0
        for v in d.values():
            if isinstance(v, dict):
                count += count_fields(v, depth + 1)
            else:
                count += 1
        return count
    
    total_fields = count_fields(categorized)
    
    # Count by category
    field_counts = {}
    for cat, data in categorized.items():
        if isinstance(data, dict):
            field_counts[cat] = count_fields(data)
    
    categorized["_metadata"] = {
        "total_fields": total_fields,
        "field_counts": field_counts,
        "exiftool_available": True,
    }
    
    return categorized


# ============================================================================
# Manufacturer-Specific Extraction
# ============================================================================

def detect_camera_manufacturer(exif_data: Dict[str, Any]) -> Optional[str]:
    """Detect camera manufacturer from EXIF data."""
    make = exif_data.get("Make", "").lower()
    
    manufacturers = {
        "canon": ["canon"],
        "nikon": ["nikon"],
        "sony": ["sony"],
        "fujifilm": ["fujifilm", "fuji"],
        "olympus": ["olympus", "om digital"],
        "panasonic": ["panasonic", "lumix"],
        "pentax": ["pentax", "ricoh"],
        "leica": ["leica"],
        "apple": ["apple"],
        "samsung": ["samsung"],
        "dji": ["dji"],
        "gopro": ["gopro"],
        "hasselblad": ["hasselblad"],
        "phase one": ["phase one"],
    }
    
    for manufacturer, keywords in manufacturers.items():
        if any(kw in make for kw in keywords):
            return manufacturer
    
    return None


def get_manufacturer_specific_fields(manufacturer: str) -> set:
    """Get the expected MakerNote fields for a manufacturer."""
    field_sets = {
        "canon": CANON_MAKERNOTE_FIELDS,
        "nikon": NIKON_MAKERNOTE_FIELDS,
        "sony": SONY_MAKERNOTE_FIELDS,
        "fujifilm": FUJIFILM_MAKERNOTE_FIELDS,
        "olympus": OLYMPUS_MAKERNOTE_FIELDS,
        "panasonic": PANASONIC_MAKERNOTE_FIELDS,
    }
    return field_sets.get(manufacturer, set())


# ============================================================================
# CLI for Testing
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python exiftool_parser.py <file>")
        print(f"\nexiftool available: {EXIFTOOL_AVAILABLE}")
        if EXIFTOOL_AVAILABLE:
            print(f"exiftool path: {EXIFTOOL_PATH}")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    print(f"Extracting metadata from: {filepath}")
    print(f"exiftool available: {EXIFTOOL_AVAILABLE}")
    print("-" * 60)
    
    result = extract_comprehensive_metadata(filepath)
    
    print(json.dumps(result, indent=2, default=str))
