"""
Smart Context Engine

Provides intelligent metadata analysis features:
- Auto-categorization of files by type and content
- AI-powered relevance filtering
- Relationship mapping between metadata fields
- Context-aware field importance scoring
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# ============================================================================
# File Type Categories
# ============================================================================

class FileCategory(Enum):
    SMARTPHONE_PHOTO = "smartphone"
    DSLR_PHOTO = "dslr"
    MIRRORLESS_PHOTO = "mirrorless"
    DRONE_PHOTO = "drone"
    ACTION_CAMERA = "action_camera"
    SCREENSHOT = "screenshot"
    SCANNED_DOCUMENT = "scanned"
    AI_GENERATED = "ai_generated"
    EDITED_PHOTO = "edited"
    RAW_PHOTO = "raw"
    VIDEO_PROFESSIONAL = "video_pro"
    VIDEO_CONSUMER = "video_consumer"
    AUDIO_MUSIC = "audio_music"
    AUDIO_PODCAST = "audio_podcast"
    DOCUMENT_PDF = "document_pdf"
    DOCUMENT_OFFICE = "document_office"
    SCIENTIFIC_MEDICAL = "scientific_medical"
    SCIENTIFIC_ASTRONOMY = "scientific_astronomy"
    UNKNOWN = "unknown"


@dataclass
class FileAnalysis:
    """Analysis result for a file."""
    category: FileCategory
    confidence: float
    subcategories: List[str]
    relevant_fields: List[str]
    hidden_fields: List[str]
    importance_scores: Dict[str, float]
    relationships: List[Dict[str, Any]]
    context_notes: List[str]


# ============================================================================
# Device Detection Patterns
# ============================================================================

SMARTPHONE_PATTERNS = [
    r"iphone",
    r"ipad",
    r"pixel\s*\d",
    r"galaxy\s*(s|a|note|z)",
    r"oneplus",
    r"huawei",
    r"xiaomi",
    r"oppo",
    r"vivo",
    r"samsung\s*sm-",
    r"motorola",
    r"nokia",
    r"lg-",
    r"htc",
    r"sony\s*(xperia|xz)",
]

DRONE_PATTERNS = [
    r"dji",
    r"mavic",
    r"phantom",
    r"mini\s*\d",
    r"air\s*\d",
    r"inspire",
    r"autel",
    r"parrot",
    r"skydio",
    r"fc\d{4}",  # DJI camera identifiers
]

ACTION_CAMERA_PATTERNS = [
    r"gopro",
    r"hero\s*\d",
    r"insta\s*360",
    r"dji\s*(action|osmo)",
    r"akaso",
    r"sjcam",
]

DSLR_PATTERNS = [
    r"canon\s*(eos|rebel|[0-9]+d)",
    r"nikon\s*(d\d{3,4}|z\s*\d)",
    r"sony\s*(ilca|alpha|a\d{4}|a\d{1,2})",
    r"pentax\s*k-",
]

MIRRORLESS_PATTERNS = [
    r"sony\s*(ilce|a[67]\d{3})",
    r"fujifilm\s*(x-|gfx)",
    r"olympus\s*(e-m|pen)",
    r"panasonic\s*(dc-|lumix)",
    r"canon\s*(eos\s*(r|m))",
    r"nikon\s*z",
    r"leica\s*(sl|cl|q)",
]

AI_GENERATION_PATTERNS = [
    r"midjourney",
    r"dall-?e",
    r"stable\s*diffusion",
    r"stablediffusion",
    r"comfyui",
    r"automatic1111",
    r"novelai",
    r"dream\s*studio",
    r"adobe\s*firefly",
]

EDITING_SOFTWARE_PATTERNS = [
    r"photoshop",
    r"lightroom",
    r"capture\s*one",
    r"affinity",
    r"gimp",
    r"darktable",
    r"luminar",
    r"on1",
    r"dxo",
    r"snapseed",
    r"vsco",
]


# ============================================================================
# Field Importance Scoring
# ============================================================================

# Default importance scores by field (0-1 scale)
FIELD_IMPORTANCE = {
    # High importance (0.8-1.0) - Always show
    "DateTimeOriginal": 1.0,
    "Make": 0.95,
    "Model": 0.95,
    "GPSLatitude": 0.95,
    "GPSLongitude": 0.95,
    "ImageWidth": 0.9,
    "ImageHeight": 0.9,
    "FileSize": 0.9,
    "SerialNumber": 0.85,
    "LensModel": 0.85,
    "SHA256": 0.85,

    # Medium importance (0.5-0.8) - Show in standard view
    "ExposureTime": 0.75,
    "FNumber": 0.75,
    "ISO": 0.75,
    "FocalLength": 0.7,
    "Flash": 0.65,
    "WhiteBalance": 0.65,
    "ExposureMode": 0.6,
    "MeteringMode": 0.6,
    "Software": 0.6,
    "Artist": 0.6,
    "Copyright": 0.6,
    "GPSAltitude": 0.55,
    "Orientation": 0.55,

    # Low importance (0.2-0.5) - Show in advanced view only
    "ColorSpace": 0.45,
    "ExposureCompensation": 0.45,
    "SceneType": 0.4,
    "SubjectDistance": 0.4,
    "DigitalZoomRatio": 0.4,
    "Contrast": 0.35,
    "Saturation": 0.35,
    "Sharpness": 0.35,
    "BrightnessValue": 0.35,
    "MaxApertureValue": 0.3,
    "LightSource": 0.3,

    # Very low importance (0-0.2) - Raw view only
    "InteropIndex": 0.15,
    "ExifVersion": 0.1,
    "ComponentsConfiguration": 0.1,
    "FlashpixVersion": 0.1,
    "CustomRendered": 0.1,
}

# Category-specific importance modifiers
CATEGORY_IMPORTANCE_MODIFIERS = {
    FileCategory.DRONE_PHOTO: {
        "GPSAltitude": 0.95,  # Altitude very important for drones
        "FlightYawDegree": 0.9,
        "FlightPitchDegree": 0.9,
        "FlightRollDegree": 0.9,
        "GimbalYawDegree": 0.85,
    },
    FileCategory.SMARTPHONE_PHOTO: {
        "LensModel": 0.5,  # Less important on phones
        "HDRGainMapVersion": 0.8,  # Computational photography
        "ProRAW": 0.8,
        "LivePhoto": 0.75,
    },
    FileCategory.AI_GENERATED: {
        "Software": 1.0,  # Critical to identify generator
        "UserComment": 0.95,  # Often contains prompts
        "Parameters": 0.95,
        "Model": 0.9,
    },
    FileCategory.SCIENTIFIC_MEDICAL: {
        "PatientID": 1.0,
        "StudyDate": 1.0,
        "Modality": 1.0,
        "BodyPartExamined": 0.95,
        "SliceThickness": 0.9,
    },
}


# ============================================================================
# Field Relationships
# ============================================================================

FIELD_RELATIONSHIPS = {
    "GPSLatitude": ["GPSLongitude", "GPSAltitude", "GPSTimeStamp"],
    "GPSLongitude": ["GPSLatitude", "GPSAltitude", "GPSTimeStamp"],
    "Make": ["Model", "SerialNumber", "LensModel"],
    "Model": ["Make", "SerialNumber", "Software"],
    "ExposureTime": ["FNumber", "ISO", "ExposureMode"],
    "FNumber": ["ExposureTime", "ISO", "MaxApertureValue"],
    "ISO": ["ExposureTime", "FNumber"],
    "FocalLength": ["FocalLengthIn35mmFormat", "LensModel"],
    "DateTimeOriginal": ["CreateDate", "ModifyDate", "GPSTimeStamp"],
    "ImageWidth": ["ImageHeight", "ExifImageWidth"],
    "ImageHeight": ["ImageWidth", "ExifImageHeight"],
    "Flash": ["FlashMode", "FlashEnergy", "FlashReturn"],
    "WhiteBalance": ["ColorTemperature", "WBShiftAB", "WBShiftGM"],
    "Software": ["ProcessingSoftware", "CreatorTool", "HistorySoftwareAgent"],
}


# ============================================================================
# Analysis Functions
# ============================================================================

def detect_file_category(metadata: Dict[str, Any]) -> Tuple[FileCategory, float, List[str]]:
    """
    Detect the category of a file based on its metadata.

    Returns:
        Tuple of (category, confidence, subcategories)
    """
    make = str(metadata.get("exif", {}).get("Make", "")).lower()
    model = str(metadata.get("exif", {}).get("Model", "")).lower()
    software = str(metadata.get("exif", {}).get("Software", "")).lower()
    mime_type = str(metadata.get("mime_type", "")).lower()

    combined = f"{make} {model} {software}"
    subcategories = []

    # Check for AI-generated content
    for pattern in AI_GENERATION_PATTERNS:
        if re.search(pattern, combined, re.IGNORECASE):
            subcategories.append("ai_generated")
            return FileCategory.AI_GENERATED, 0.95, subcategories

    # Check file type
    if mime_type.startswith("video/"):
        # Determine video type
        bitrate = metadata.get("video", {}).get("format", {}).get("bit_rate", 0)
        if isinstance(bitrate, str):
            try:
                bitrate = int(bitrate)
            except ValueError:
                bitrate = 0

        if bitrate > 50000000:  # >50Mbps
            return FileCategory.VIDEO_PROFESSIONAL, 0.8, ["high_bitrate"]
        return FileCategory.VIDEO_CONSUMER, 0.7, []

    if mime_type.startswith("audio/"):
        tags = metadata.get("audio", {}).get("tags", {})
        if tags.get("album") or tags.get("artist"):
            return FileCategory.AUDIO_MUSIC, 0.85, []
        return FileCategory.AUDIO_PODCAST, 0.6, []

    if mime_type == "application/pdf":
        return FileCategory.DOCUMENT_PDF, 0.95, []

    # Image analysis
    if mime_type.startswith("image/"):
        # Check for drone
        for pattern in DRONE_PATTERNS:
            if re.search(pattern, combined, re.IGNORECASE):
                subcategories.append("aerial")
                return FileCategory.DRONE_PHOTO, 0.9, subcategories

        # Check for action camera
        for pattern in ACTION_CAMERA_PATTERNS:
            if re.search(pattern, combined, re.IGNORECASE):
                subcategories.append("action")
                return FileCategory.ACTION_CAMERA, 0.9, subcategories

        # Check for smartphone
        for pattern in SMARTPHONE_PATTERNS:
            if re.search(pattern, combined, re.IGNORECASE):
                # Check for computational photography features
                if metadata.get("exif", {}).get("HDRGainMapVersion"):
                    subcategories.append("hdr")
                if metadata.get("exif", {}).get("LivePhoto"):
                    subcategories.append("live_photo")
                return FileCategory.SMARTPHONE_PHOTO, 0.9, subcategories

        # Check for DSLR
        for pattern in DSLR_PATTERNS:
            if re.search(pattern, combined, re.IGNORECASE):
                return FileCategory.DSLR_PHOTO, 0.85, subcategories

        # Check for mirrorless
        for pattern in MIRRORLESS_PATTERNS:
            if re.search(pattern, combined, re.IGNORECASE):
                return FileCategory.MIRRORLESS_PHOTO, 0.85, subcategories

        # Check for edited image
        for pattern in EDITING_SOFTWARE_PATTERNS:
            if re.search(pattern, software, re.IGNORECASE):
                subcategories.append("edited")
                return FileCategory.EDITED_PHOTO, 0.7, subcategories

        # Check for RAW
        ext = str(metadata.get("file", {}).get("extension", "")).lower()
        raw_extensions = [".cr2", ".cr3", ".nef", ".arw", ".orf", ".rw2", ".dng", ".raw"]
        if ext in raw_extensions:
            return FileCategory.RAW_PHOTO, 0.95, []

        # Check for screenshot (no camera metadata)
        if not make and not model and not metadata.get("exif", {}).get("ExposureTime"):
            return FileCategory.SCREENSHOT, 0.6, []

    return FileCategory.UNKNOWN, 0.3, subcategories


def calculate_field_importance(
    field_name: str,
    category: FileCategory,
    base_importance: Optional[float] = None
) -> float:
    """
    Calculate importance score for a field based on category context.
    """
    # Get base importance
    if base_importance is not None:
        importance = base_importance
    else:
        importance = FIELD_IMPORTANCE.get(field_name, 0.3)

    # Apply category-specific modifiers
    if category in CATEGORY_IMPORTANCE_MODIFIERS:
        modifier = CATEGORY_IMPORTANCE_MODIFIERS[category].get(field_name)
        if modifier is not None:
            importance = modifier

    return min(1.0, max(0.0, importance))


def get_related_fields(field_name: str) -> List[str]:
    """Get fields related to the given field."""
    return FIELD_RELATIONSHIPS.get(field_name, [])


def filter_relevant_fields(
    metadata: Dict[str, Any],
    category: FileCategory,
    min_importance: float = 0.3
) -> Dict[str, Any]:
    """
    Filter metadata to only include fields above importance threshold.
    """
    result = {}

    def filter_dict(data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        filtered = {}
        for key, value in data.items():
            if key.startswith("_"):
                continue

            full_key = f"{prefix}.{key}" if prefix else key
            importance = calculate_field_importance(key, category)

            if isinstance(value, dict):
                sub_filtered = filter_dict(value, full_key)
                if sub_filtered:
                    filtered[key] = sub_filtered
            elif importance >= min_importance:
                filtered[key] = value

        return filtered

    for section_name, section_data in metadata.items():
        if isinstance(section_data, dict):
            filtered_section = filter_dict(section_data, section_name)
            if filtered_section:
                result[section_name] = filtered_section
        else:
            result[section_name] = section_data

    return result


def analyze_file(metadata: Dict[str, Any]) -> FileAnalysis:
    """
    Perform comprehensive analysis of file metadata.
    """
    # Detect category
    category, confidence, subcategories = detect_file_category(metadata)

    # Calculate importance scores for all fields
    importance_scores = {}
    relevant_fields = []
    hidden_fields = []

    def analyze_dict(data: Dict[str, Any], prefix: str = ""):
        for key, value in data.items():
            if key.startswith("_"):
                continue

            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                analyze_dict(value, full_key)
            else:
                importance = calculate_field_importance(key, category)
                importance_scores[full_key] = importance

                if importance >= 0.5:
                    relevant_fields.append(full_key)
                elif importance < 0.3:
                    hidden_fields.append(full_key)

    for section_name, section_data in metadata.items():
        if isinstance(section_data, dict):
            analyze_dict(section_data, section_name)

    # Find relationships
    relationships = []
    for field in relevant_fields:
        field_name = field.split(".")[-1]
        related = get_related_fields(field_name)
        if related:
            relationships.append({
                "field": field,
                "related_to": related,
                "type": "data_relationship"
            })

    # Generate context notes
    context_notes = []

    if category == FileCategory.DRONE_PHOTO:
        context_notes.append("Drone photo detected - flight data may be available")
    elif category == FileCategory.AI_GENERATED:
        context_notes.append("AI-generated content detected - check Software field for generator")
    elif category == FileCategory.SMARTPHONE_PHOTO:
        context_notes.append("Smartphone photo - computational photography features may be present")
    elif category == FileCategory.EDITED_PHOTO:
        context_notes.append("Image has been edited - check Software for editing history")

    # Check for GPS data
    if metadata.get("gps") and not metadata["gps"].get("_locked"):
        context_notes.append("Location data present - can be mapped")

    # Check for sensitive data
    if metadata.get("exif", {}).get("SerialNumber"):
        context_notes.append("Device serial number present - forensically significant")

    return FileAnalysis(
        category=category,
        confidence=confidence,
        subcategories=subcategories,
        relevant_fields=relevant_fields,
        hidden_fields=hidden_fields,
        importance_scores=importance_scores,
        relationships=relationships,
        context_notes=context_notes,
    )


def get_top_fields(
    metadata: Dict[str, Any],
    count: int = 7,
    category: Optional[FileCategory] = None
) -> List[Tuple[str, Any, float]]:
    """
    Get the most important fields from metadata.

    Returns:
        List of (field_name, value, importance_score) tuples
    """
    if category is None:
        category, _, _ = detect_file_category(metadata)

    fields_with_scores = []

    def collect_fields(data: Dict[str, Any], prefix: str = ""):
        for key, value in data.items():
            if key.startswith("_"):
                continue

            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                collect_fields(value, full_key)
            elif value is not None and value != "":
                importance = calculate_field_importance(key, category)
                fields_with_scores.append((full_key, value, importance))

    for section_name, section_data in metadata.items():
        if isinstance(section_data, dict) and not section_data.get("_locked"):
            collect_fields(section_data, section_name)

    # Sort by importance and return top N
    fields_with_scores.sort(key=lambda x: x[2], reverse=True)
    return fields_with_scores[:count]


# ============================================================================
# Export
# ============================================================================

__all__ = [
    "FileCategory",
    "FileAnalysis",
    "detect_file_category",
    "calculate_field_importance",
    "get_related_fields",
    "filter_relevant_fields",
    "analyze_file",
    "get_top_fields",
]
