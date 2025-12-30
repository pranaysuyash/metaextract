#!/usr/bin/env python3
"""
MetaExtract - Forensic-Grade Metadata Extraction Engine v3.0

Extracts 7,000+ metadata fields from any file including:
- Filesystem metadata (times, size, permissions, owner, extended attributes)
- EXIF data (ALL tags including proprietary MakerNote)
- **PARSED MakerNotes** for Canon, Nikon, Sony, Fujifilm, Olympus, Panasonic, etc.
- GPS coordinates (with decimal conversion, Google Maps URLs)
- Image properties (resolution, color space, ICC profiles)
- Video properties (ALL ffprobe fields - format, streams, chapters, HDR)
- **Video codec specifics** (H.264 profile/level, HEVC, VP9, AV1 params)
- Audio properties (ID3, Vorbis, AAC tags, album art detection)
- **Audio codec specifics** (MP3 LAME info, AAC profile, FLAC MD5)
- PDF metadata (pages, author, encryption, form fields)
- SVG metadata (viewBox, elements, scripts detection)
- File integrity (MD5, SHA256, SHA1, CRC32 hashes)
- Calculated/inferred metadata (aspect ratios, file age, time periods)
- Extended attributes (macOS Finder tags, Spotlight metadata)
- **Full IPTC-IIM metadata** (~50 fields)
- **Full XMP metadata** (20+ namespaces, 200+ fields)

Usage:
    python metadata_engine.py photo.jpg
    python metadata_engine.py photo.jpg --tier premium
    python metadata_engine.py video.mp4 --output metadata.json

Requirements:
    Core: pillow, exifread, ffmpeg-python, mutagen, pypdf
    Enhanced: exiftool (for parsed MakerNotes, full IPTC/XMP)
    
    Install exiftool:
      macOS: brew install exiftool
      Ubuntu: apt install libimage-exiftool-perl
      Windows: https://exiftool.org/

Author: MetaExtract
Version: 3.0.0
"""

import os
import sys
import json
import stat
import hashlib
import logging
import mimetypes
import re
import base64
import subprocess
import platform
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List, Sequence
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("metaextract")
_EXEMPI_AVAILABLE: Optional[bool] = None

# ============================================================================
# Library Availability Checks
# ============================================================================

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import exifread
    EXIFREAD_AVAILABLE = True
except ImportError:
    EXIFREAD_AVAILABLE = False

try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False

try:
    import mutagen
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.mp4 import MP4
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    try:
        from PyPDF2 import PdfReader
        PYPDF_AVAILABLE = True
    except ImportError:
        PYPDF_AVAILABLE = False

# Phase 2 module availability (deep analysis)
try:
    from .video_codec_details import extract_video_codec_details
    VIDEO_CODEC_DETAILS_AVAILABLE = True
except Exception as e:
    VIDEO_CODEC_DETAILS_AVAILABLE = False

try:
    from .container_metadata import extract_container_metadata
    CONTAINER_METADATA_AVAILABLE = True
except Exception as e:
    CONTAINER_METADATA_AVAILABLE = False

try:
    from .audio_codec_details import extract_audio_codec_details
    AUDIO_CODEC_DETAILS_AVAILABLE = True
except Exception as e:
    AUDIO_CODEC_DETAILS_AVAILABLE = False

try:
    from .scientific_medical import extract_scientific_metadata, detect_scientific_format
    SCIENTIFIC_AVAILABLE = True
except Exception:
    SCIENTIFIC_AVAILABLE = False

try:
    from .scientific_data import extract_hdf5_metadata, extract_netcdf_metadata
    SCIENTIFIC_DATA_AVAILABLE = True
except Exception:
    SCIENTIFIC_DATA_AVAILABLE = False

try:
    from .video_telemetry import extract_video_telemetry
    VIDEO_TELEMETRY_AVAILABLE = True
except Exception:
    VIDEO_TELEMETRY_AVAILABLE = False

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIF_AVAILABLE = True
except ImportError:
    HEIF_AVAILABLE = False

try:
    import xattr
    XATTR_AVAILABLE = True
except ImportError:
    XATTR_AVAILABLE = False

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

try:
    from iptcinfo3 import IPTCInfo
    IPTC_AVAILABLE = True
except ImportError:
    IPTC_AVAILABLE = False

try:
    from libxmp import ExempiLoadError, XMPFiles, XMPError, consts as xmp_consts
    XMP_AVAILABLE = True
except ImportError:
    XMP_AVAILABLE = False
    xmp_consts = None  # type: ignore[assignment]
    XMPFiles = None  # type: ignore[assignment]
    ExempiLoadError = None  # type: ignore[assignment]
    XMPError = None  # type: ignore[assignment]

try:
    import imagehash
    IMAGEHASH_AVAILABLE = True
except ImportError:
    IMAGEHASH_AVAILABLE = False

try:
    from .metadata_mapper import MetadataMapper
except ImportError:
    try:
        from metadata_mapper import MetadataMapper
    except ImportError:
        MetadataMapper = None  # type: ignore[assignment]

EXIFTOOL_PATH = shutil.which("exiftool")
EXIFTOOL_AVAILABLE = EXIFTOOL_PATH is not None

# ============================================================================
# Tier Configuration
# ============================================================================

class Tier(Enum):
    FREE = "free"
    STARTER = "starter"
    PREMIUM = "premium"
    SUPER = "super"

@dataclass
class TierConfig:
    file_hashes: bool = False
    filesystem_details: bool = False
    calculated_fields: bool = False
    gps_data: bool = False
    makernotes: bool = False
    iptc_xmp: bool = False
    perceptual_hashes: bool = False
    thumbnails: bool = False
    video_encoding: bool = False
    audio_details: bool = False
    pdf_details: bool = False
    extended_attributes: bool = False
    raw_exif: bool = False
    forensic_details: bool = False
    serial_numbers: bool = False
    exiftool_enhanced: bool = False
    burned_metadata: bool = False
    metadata_comparison: bool = False
    # Phase 2 toggles
    video_codec_details: bool = False
    container_details: bool = False
    audio_codec_details: bool = False
    scientific_details: bool = False
    # Phase 3 toggles
    pdf_complete: bool = False
    office_documents: bool = False
    web_social_metadata: bool = False
    email_metadata: bool = False
    # Phase 4 toggles
    ai_ml_metadata: bool = False
    blockchain_nft_metadata: bool = False
    ar_vr_metadata: bool = False
    iot_metadata: bool = False

TIER_CONFIGS = {
    Tier.FREE: TierConfig(),
    Tier.STARTER: TierConfig(
        file_hashes=True, filesystem_details=True, calculated_fields=True,
        gps_data=True, audio_details=True, pdf_details=True, forensic_details=True,
        perceptual_hashes=True, thumbnails=True,
    ),
    Tier.PREMIUM: TierConfig(
        file_hashes=True, filesystem_details=True, calculated_fields=True,
        gps_data=True, makernotes=True, iptc_xmp=True, video_encoding=True,
        audio_details=True, pdf_details=True, extended_attributes=True,
        perceptual_hashes=True, thumbnails=True,
        raw_exif=True, forensic_details=True, serial_numbers=True, exiftool_enhanced=True,
        burned_metadata=True, metadata_comparison=True,
        # Phase 2 capabilities enabled for Premium
        video_codec_details=True, container_details=True, audio_codec_details=True,
        scientific_details=True,
        # Phase 3 capabilities
        pdf_complete=True,
        office_documents=True,
        web_social_metadata=True,
        email_metadata=True,
        # Phase 4 capabilities
        ai_ml_metadata=True,
        blockchain_nft_metadata=True,
        ar_vr_metadata=True,
        iot_metadata=True,
    ),
    Tier.SUPER: TierConfig(
        file_hashes=True, filesystem_details=True, calculated_fields=True,
        gps_data=True, makernotes=True, iptc_xmp=True, video_encoding=True,
        audio_details=True, pdf_details=True, extended_attributes=True,
        perceptual_hashes=True, thumbnails=True,
        raw_exif=True, forensic_details=True, serial_numbers=True, exiftool_enhanced=True,
        burned_metadata=True, metadata_comparison=True,
        video_codec_details=True, container_details=True, audio_codec_details=True,
        scientific_details=True,
    ),
}

# ============================================================================
# Utility Functions
# ============================================================================

def human_readable_size(size_bytes: float) -> str:
    if size_bytes == 0:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def human_readable_time_delta(delta: timedelta) -> str:
    seconds = int(abs(delta.total_seconds()))
    if seconds < 60: return "just now"
    elif seconds < 3600: return f"{seconds // 60} minute{'s' if seconds // 60 != 1 else ''} ago"
    elif seconds < 86400: return f"{seconds // 3600} hour{'s' if seconds // 3600 != 1 else ''} ago"
    elif seconds < 604800: return f"{seconds // 86400} day{'s' if seconds // 86400 != 1 else ''} ago"
    elif seconds < 2592000: return f"{seconds // 604800} week{'s' if seconds // 604800 != 1 else ''} ago"
    elif seconds < 31536000: return f"{seconds // 2592000} month{'s' if seconds // 2592000 != 1 else ''} ago"
    else: return f"{seconds // 31536000} year{'s' if seconds // 31536000 != 1 else ''} ago"

def dms_to_decimal(dms: Sequence, ref: str) -> Optional[float]:
    try:
        if len(dms) < 3: return None
        def to_float(val):
            if hasattr(val, 'num') and hasattr(val, 'den'):
                return float(val.num) / float(val.den) if val.den != 0 else 0
            return float(val)
        degrees, minutes, seconds = to_float(dms[0]), to_float(dms[1]), to_float(dms[2])
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        if ref.upper() in ["S", "W"]: decimal = -decimal
        return round(decimal, 8)
    except: return None

def format_dms(decimal: float, is_latitude: bool) -> str:
    absolute = abs(decimal)
    degrees = int(absolute)
    minutes_decimal = (absolute - degrees) * 60
    minutes = int(minutes_decimal)
    seconds = (minutes_decimal - minutes) * 60
    direction = ("N" if decimal >= 0 else "S") if is_latitude else ("E" if decimal >= 0 else "W")
    return f"{degrees}° {minutes}' {seconds:.2f}\" {direction}"

def safe_str(value: Any) -> Optional[str]:
    if value is None: return None
    if isinstance(value, bytes):
        try: return value.decode('utf-8', errors='ignore')
        except: return base64.b64encode(value).decode('ascii')[:100] + "..."
    if isinstance(value, (list, tuple)): return ", ".join(str(v) for v in value[:10])
    return str(value)

def detect_mime_type(filepath: str) -> str:
    mime_type = None
    if MAGIC_AVAILABLE:
        try: mime_type = magic.from_file(filepath, mime=True)
        except: pass
    if not mime_type: mime_type = mimetypes.guess_type(filepath)[0]
    return mime_type or "application/octet-stream"

def _normalize_metadata_key(key: str) -> str:
    key_clean = key.strip().lower()
    key_clean = re.sub(r"[^a-z0-9]+", " ", key_clean)
    return " ".join(key_clean.split())

def _coerce_metadata_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, (list, tuple)):
        coerced = [_coerce_metadata_value(item) for item in value]
        return [item for item in coerced if item not in (None, "")]
    return str(value)

def extract_iptc_metadata(filepath: str) -> Optional[Dict[str, Any]]:
    if not IPTC_AVAILABLE:
        return None

    ext = Path(filepath).suffix.lower()
    if ext not in {".jpg", ".jpeg", ".tif", ".tiff"}:
        return None

    iptc_field_map = {
        "object name": "title",
        "headline": "headline",
        "caption abstract": "description",
        "keywords": "keywords",
        "by line": "creator",
        "credit": "credit_line",
        "source": "source",
        "copyright notice": "copyright",
        "special instructions": "instructions",
        "city": "location_city",
        "province state": "location_state",
        "country primary location name": "location_country",
        "country primary location code": "location_country_code",
        "sublocation": "location_sublocation",
        "intellectual genre": "intellectual_genre",
        "scene": "scene_code",
        "subject reference": "subject_code",
        "event": "event",
    }

    try:
        info = IPTCInfo(filepath, force=True)
        raw: Dict[str, Any] = {}
        fields: Dict[str, Any] = {}
        data_source = getattr(info, "_data", None) or info

        for key, value in data_source.items():
            if hasattr(data_source, "_key_as_str"):
                try:
                    key_str = data_source._key_as_str(key)
                except Exception as e:
                    key_str = str(key)
            else:
                key_str = str(key)
            cleaned = _coerce_metadata_value(value)
            if cleaned in (None, "", []):
                continue
            raw[key_str] = cleaned

            normalized_key = _normalize_metadata_key(key_str)
            mapped_key = iptc_field_map.get(normalized_key)
            if mapped_key and mapped_key not in fields:
                fields[mapped_key] = cleaned

        if not raw and not fields:
            return None

        return {"fields": fields, "raw": raw}
    except Exception as e:
        logger.error(f"Error extracting IPTC metadata: {e}")
        return None

def _extract_xmp_property(xmp, namespace: str, name: str) -> Optional[str]:
    try:
        value = xmp.get_property(namespace, name)
    except Exception as e:
        return None
    if value in (None, ""):
        return None
    return str(value).strip()

def _extract_xmp_array(xmp, namespace: str, name: str) -> List[str]:
    items: List[str] = []
    try:
        count = xmp.count_array_items(namespace, name)
    except Exception as e:
        count = 0

    for idx in range(1, count + 1):
        try:
            item = xmp.get_array_item(namespace, name, idx)
        except Exception as e:
            continue
        if item not in (None, ""):
            items.append(str(item).strip())

    if not items:
        fallback = _extract_xmp_property(xmp, namespace, name)
        if fallback:
            items.append(fallback)

    return items

def extract_xmp_metadata(filepath: str) -> Optional[Dict[str, Any]]:
    global _EXEMPI_AVAILABLE
    if not XMP_AVAILABLE or xmp_consts is None:
        return None

    if _EXEMPI_AVAILABLE is None:
        try:
            import ctypes.util
            lib_path = ctypes.util.find_library("exempi")
            if not lib_path:
                for candidate in ("/opt/homebrew/lib/libexempi.dylib", "/opt/local/lib/libexempi.dylib"):
                    if os.path.exists(candidate):
                        lib_path = candidate
                        break
            _EXEMPI_AVAILABLE = bool(lib_path)
        except Exception as e:
            _EXEMPI_AVAILABLE = False

    if not _EXEMPI_AVAILABLE:
        return None

    xmpfile = None
    try:
        xmpfile = XMPFiles(file_path=filepath, open_forupdate=False)
        xmp = xmpfile.get_xmp()
        if xmp is None:
            return None

        raw: Dict[str, Any] = {}
        fields: Dict[str, Any] = {}

        ns_dc = getattr(xmp_consts, "XMP_NS_DC", None)
        ns_photoshop = getattr(xmp_consts, "XMP_NS_PHOTOSHOP", None) or getattr(xmp_consts, "XMP_NS_Photoshop", None)
        ns_xmp = getattr(xmp_consts, "XMP_NS_XMP", None)
        ns_rights = getattr(xmp_consts, "XMP_NS_XMP_RIGHTS", None) or getattr(xmp_consts, "XMP_NS_XMP_Rights", None)
        ns_iptc = (
            getattr(xmp_consts, "XMP_NS_IPTCCORE", None)
            or getattr(xmp_consts, "XMP_NS_IPTCCore", None)
            or getattr(xmp_consts, "XMP_NS_IPTC_CORE", None)
        )

        dc_data: Dict[str, Any] = {}
        dc_title = _extract_xmp_array(xmp, ns_dc, "title") if ns_dc else []
        if dc_title:
            dc_data["title"] = dc_title
            fields["title"] = dc_title[0]

        dc_description = _extract_xmp_array(xmp, ns_dc, "description") if ns_dc else []
        if dc_description:
            dc_data["description"] = dc_description
            fields["description"] = dc_description[0]

        dc_creator = _extract_xmp_array(xmp, ns_dc, "creator") if ns_dc else []
        if dc_creator:
            dc_data["creator"] = dc_creator
            fields["creator"] = dc_creator

        dc_subject = _extract_xmp_array(xmp, ns_dc, "subject") if ns_dc else []
        if dc_subject:
            dc_data["subject"] = dc_subject
            fields["keywords"] = dc_subject

        dc_rights = _extract_xmp_array(xmp, ns_dc, "rights") if ns_dc else []
        if dc_rights:
            dc_data["rights"] = dc_rights

        if dc_data:
            raw["dc"] = dc_data

        photoshop_data: Dict[str, Any] = {}
        headline = _extract_xmp_property(xmp, ns_photoshop, "Headline") if ns_photoshop else None
        if headline:
            photoshop_data["headline"] = headline
            fields["headline"] = headline

        credit = _extract_xmp_property(xmp, ns_photoshop, "Credit") if ns_photoshop else None
        if credit:
            photoshop_data["credit"] = credit
            fields["credit_line"] = credit

        source = _extract_xmp_property(xmp, ns_photoshop, "Source") if ns_photoshop else None
        if source:
            photoshop_data["source"] = source
            fields["source"] = source

        instructions = _extract_xmp_property(xmp, ns_photoshop, "Instructions") if ns_photoshop else None
        if instructions:
            photoshop_data["instructions"] = instructions
            fields["instructions"] = instructions

        city = _extract_xmp_property(xmp, ns_photoshop, "City") if ns_photoshop else None
        if city:
            photoshop_data["city"] = city
            fields["location_city"] = city

        state = _extract_xmp_property(xmp, ns_photoshop, "State") if ns_photoshop else None
        if state:
            photoshop_data["state"] = state
            fields["location_state"] = state

        country = _extract_xmp_property(xmp, ns_photoshop, "Country") if ns_photoshop else None
        if country:
            photoshop_data["country"] = country
            fields["location_country"] = country

        if photoshop_data:
            raw["photoshop"] = photoshop_data

        xmp_data: Dict[str, Any] = {}
        creator_tool = _extract_xmp_property(xmp, ns_xmp, "CreatorTool") if ns_xmp else None
        if creator_tool:
            xmp_data["creator_tool"] = creator_tool
            fields["creator_tool"] = creator_tool

        if xmp_data:
            raw["xmp"] = xmp_data

        iptc_core: Dict[str, Any] = {}
        if ns_iptc:
            iptc_location = _extract_xmp_property(xmp, ns_iptc, "Location")
            if iptc_location:
                iptc_core["location"] = iptc_location
                fields["location_sublocation"] = iptc_location

            iptc_country_code = _extract_xmp_property(xmp, ns_iptc, "CountryCode")
            if iptc_country_code:
                iptc_core["country_code"] = iptc_country_code
                fields["location_country_code"] = iptc_country_code

            iptc_event = _extract_xmp_property(xmp, ns_iptc, "Event")
            if iptc_event:
                iptc_core["event"] = iptc_event
                fields["event"] = iptc_event

            iptc_genre = _extract_xmp_property(xmp, ns_iptc, "IntellectualGenre")
            if iptc_genre:
                iptc_core["intellectual_genre"] = iptc_genre
                fields["intellectual_genre"] = iptc_genre

            iptc_scene = _extract_xmp_array(xmp, ns_iptc, "Scene")
            if iptc_scene:
                iptc_core["scene"] = iptc_scene
                fields["scene_code"] = iptc_scene

            iptc_subject = _extract_xmp_array(xmp, ns_iptc, "SubjectCode")
            if iptc_subject:
                iptc_core["subject_code"] = iptc_subject
                fields["subject_code"] = iptc_subject

            if iptc_core:
                raw["iptc_core"] = iptc_core

        rights_data: Dict[str, Any] = {}
        usage_terms = _extract_xmp_array(xmp, ns_rights, "UsageTerms") if ns_rights else []
        if usage_terms:
            rights_data["usage_terms"] = usage_terms
            fields["rights_usage_terms"] = usage_terms

        if rights_data:
            raw["xmp_rights"] = rights_data

        if not fields and not raw:
            return None

        return {"fields": fields, "raw": raw}
    except ExempiLoadError:
        _EXEMPI_AVAILABLE = False
        return None
    except XMPError as e:
        logger.error(f"Error extracting XMP metadata: {e}")
        return None
    except Exception as e:
        logger.error(f"Error extracting XMP metadata: {e}")
        return None
    finally:
        if xmpfile is not None:
            try:
                xmpfile.close_file()
            except Exception as e:
                pass  # TODO: Consider logging: logger.debug(f'Handled exception: {e}')

def extract_perceptual_hashes(filepath: str) -> Optional[Dict[str, Any]]:
    if not PIL_AVAILABLE:
        return {"available": False, "reason": "pillow not installed"}
    if not IMAGEHASH_AVAILABLE:
        return {"available": False, "reason": "imagehash not installed"}

    try:
        with Image.open(filepath) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")

            hashes: Dict[str, Any] = {
                "available": True,
                "phash": str(imagehash.phash(img, hash_size=8)),
                "dhash": str(imagehash.dhash(img, hash_size=8)),
                "ahash": str(imagehash.average_hash(img, hash_size=8)),
            }

            try:
                hashes["whash"] = str(imagehash.whash(img, hash_size=8))
            except Exception as e:
                pass  # TODO: Consider logging: logger.debug(f'Handled exception: {e}')

            return hashes
    except Exception as e:
        logger.error(f"Error calculating perceptual hashes: {e}")
        return {"available": False, "error": str(e)}

def extract_thumbnail(filepath: str) -> Optional[Dict[str, Any]]:
    if not PIL_AVAILABLE:
        return None
    try:
        with Image.open(filepath) as img:
            has_embedded = hasattr(img, "_getexif") and img._getexif() is not None
            img.thumbnail((160, 160))
            return {"has_embedded": has_embedded, "width": img.width, "height": img.height}
    except Exception as e:
        logger.error(f"Error extracting thumbnail: {e}")
        return None

# ============================================================================
# ExifTool Integration
# ============================================================================

def run_exiftool(filepath: str, args: List[str] = None) -> Optional[Dict[str, Any]]:
    """Run exiftool and return parsed JSON output."""
    if not EXIFTOOL_AVAILABLE:
        return None
    try:
        cmd = [EXIFTOOL_PATH, "-j", "-n", "-G1", "-s", "-a", "-u", "-f"]
        if args: cmd.extend(args)
        cmd.append(filepath)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0: return None
        data = json.loads(result.stdout)
        return data[0] if data else None
    except: return None

def categorize_exiftool_output(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Organize exiftool output into logical categories."""
    categories: Dict[str, Any] = {
        "file": {},
        "image_container": {},
        "exif": {},
        "exif_ifd": {
            "ifd0": {},
            "exif": {},
            "sub_ifd": {},
            "gps": {},
            "interop": {},
            "thumbnail": {},
        },
        "gps": {},
        "interoperability": {},
        "thumbnail_metadata": {},
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
            "hasselblad": {},
            "phase_one": {},
            "minolta": {},
            "ricoh": {},
            "sigma": {},
            "other": {},
        },
        "iptc": {},
        "xmp": {},
        "xmp_namespaces": {
            "dc": {},
            "xmp": {},
            "xmpMM": {},
            "xmpRights": {},
            "photoshop": {},
            "crs": {},
            "lr": {},
            "iptcCore": {},
            "iptcExt": {},
            "aux": {},
            "exif": {},
            "exifEX": {},
            "tiff": {},
            "plus": {},
            "mwg_rs": {},
            "mwg_kw": {},
            "mwg_coll": {},
            "gCamera": {},
            "gDepth": {},
            "gImage": {},
            "gPano": {},
            "gSpherical": {},
            "gFocus": {},
            "apple": {},
            "apple_photos": {},
            "adobe_stock": {},
            "other": {},
        },
        "icc_profile": {},
        "video": {},
        "audio": {},
        "composite": {},
        "other": {},
    }

    exif_ifd_groups = {
        "IFD0": "ifd0",
        "ExifIFD": "exif",
        "SubIFD": "sub_ifd",
        "GPS": "gps",
        "InteropIFD": "interop",
        "IFD1": "thumbnail",
        "Thumbnail": "thumbnail",
        "Interop": "interop",
        "EXIF": "exif",
    }

    image_container_groups = {
        "JFIF",
        "JPEG",
        "PNG",
        "GIF",
        "BMP",
        "TIFF",
        "HEIF",
        "HEIC",
        "WEBP",
        "JP2",
        "JXL",
        "Photoshop",
        "Adobe",
        "APP1",
        "APP14",
    }

    makernote_groups = {
        "Canon": "canon",
        "CanonCustom": "canon",
        "Nikon": "nikon",
        "NikonCustom": "nikon",
        "Sony": "sony",
        "SonyIDC": "sony",
        "Fujifilm": "fujifilm",
        "FujiFilm": "fujifilm",
        "Olympus": "olympus",
        "Panasonic": "panasonic",
        "Pentax": "pentax",
        "Leica": "leica",
        "Apple": "apple",
        "DJI": "dji",
        "GoPro": "gopro",
        "Samsung": "samsung",
        "Hasselblad": "hasselblad",
        "PhaseOne": "phase_one",
        "Phase One": "phase_one",
        "Minolta": "minolta",
        "KonicaMinolta": "minolta",
        "Ricoh": "ricoh",
        "Sigma": "sigma",
    }

    xmp_group_map = {
        "XMP-dc": "dc",
        "XMP-xmp": "xmp",
        "XMP-xmpMM": "xmpMM",
        "XMP-xmpRights": "xmpRights",
        "XMP-photoshop": "photoshop",
        "XMP-crs": "crs",
        "XMP-lr": "lr",
        "XMP-iptcCore": "iptcCore",
        "XMP-iptcExt": "iptcExt",
        "XMP-aux": "aux",
        "XMP-exif": "exif",
        "XMP-exifEX": "exifEX",
        "XMP-tiff": "tiff",
        "XMP-plus": "plus",
        "XMP-mwg-rs": "mwg_rs",
        "XMP-mwg-kw": "mwg_kw",
        "XMP-mwg-coll": "mwg_coll",
        "XMP-GCamera": "gCamera",
        "XMP-GDepth": "gDepth",
        "XMP-GImage": "gImage",
        "XMP-GPano": "gPano",
        "XMP-GSpherical": "gSpherical",
        "XMP-GFocus": "gFocus",
        "XMP-apple-fi": "apple",
        "XMP-apple-photos": "apple_photos",
        "XMP-AdobeStock": "adobe_stock",
    }

    thumbnail_tags = {
        "ThumbnailImage",
        "PreviewImage",
        "JpgFromRaw",
        "PreviewTIFF",
        "PreviewImageLength",
    }

    def normalize_binary_value(raw_value: Any) -> Any:
        if isinstance(raw_value, str):
            match = re.search(r"Binary data (\d+) bytes", raw_value)
            if match:
                return f"Binary data ({match.group(1)} bytes)"
        return raw_value

    def store_value(bucket: Dict[str, Any], tag: str, value: Any) -> None:
        if tag in bucket:
            existing = bucket[tag]
            if isinstance(existing, list):
                existing.append(value)
            else:
                bucket[tag] = [existing, value]
        else:
            bucket[tag] = value

    for key, raw_value in data.items():
        if raw_value is None or raw_value == "" or raw_value == "-":
            continue

        value = normalize_binary_value(raw_value)
        if value is None or value == "":
            continue

        if ":" in key:
            group, tag = key.split(":", 1)
        else:
            group, tag = "", key

        if group in ("System", "File", "ExifTool"):
            store_value(categories["file"], tag, value)
            continue

        if group in image_container_groups:
            store_value(categories["image_container"], tag, value)
            continue

        if group in exif_ifd_groups:
            section = exif_ifd_groups[group]
            store_value(categories["exif_ifd"][section], tag, value)
            if section == "gps":
                store_value(categories["gps"], tag, value)
            elif section == "interop":
                store_value(categories["interoperability"], tag, value)
                store_value(categories["exif"], tag, value)
            elif section == "thumbnail":
                store_value(categories["thumbnail_metadata"], tag, value)
            else:
                store_value(categories["exif"], tag, value)
            continue

        if group in makernote_groups:
            vendor = makernote_groups[group]
            store_value(categories["makernote"][vendor], tag, value)
            continue

        if group.startswith("MakerNotes"):
            store_value(categories["makernote"]["other"], tag, value)
            continue

        if group.startswith("IPTC"):
            store_value(categories["iptc"], tag, value)
            continue

        if group.startswith("XMP"):
            store_value(categories["xmp"], key, value)
            ns_bucket = xmp_group_map.get(group, "other")
            store_value(categories["xmp_namespaces"][ns_bucket], tag, value)
            continue

        if group == "ICC_Profile":
            store_value(categories["icc_profile"], tag, value)
            continue

        if group.startswith("Composite"):
            store_value(categories["composite"], tag, value)
            continue

        if group.startswith("QuickTime") or group.startswith("Track") or group in {"H264", "HEVC", "AV1", "VP8", "VP9"}:
            store_value(categories["video"], key, value)
            continue

        if group.startswith("ID3") or group in {"FLAC", "Vorbis", "APE", "ASF", "RIFF", "M4A", "Opus"}:
            store_value(categories["audio"], key, value)
            continue

        if tag in thumbnail_tags or "Thumbnail" in tag or "PreviewImage" in tag:
            store_value(categories["thumbnail_metadata"], tag, value)
            continue

        store_value(categories["other"], key, value)

    def prune_empty(obj: Any) -> Any:
        if isinstance(obj, dict):
            cleaned = {k: prune_empty(v) for k, v in obj.items() if v not in ({}, [], None)}
            return {k: v for k, v in cleaned.items() if v not in ({}, [], None)}
        if isinstance(obj, list):
            return [item for item in obj if item not in ({}, [], None)]
        return obj

    return prune_empty(categories)

def extract_with_exiftool(filepath: str) -> Optional[Dict[str, Any]]:
    """Extract ALL metadata using exiftool."""
    raw = run_exiftool(filepath, ["-All"])
    if not raw: return None
    return categorize_exiftool_output(raw)

def _detect_thumbnail_mime(data: bytes) -> Optional[str]:
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG"):
        return "image/png"
    if data.startswith(b"II*\x00") or data.startswith(b"MM\x00*"):
        return "image/tiff"
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return "image/gif"
    if data.startswith(b"RIFF") and b"WEBP" in data[8:16]:
        return "image/webp"
    return None

def extract_embedded_thumbnails(filepath: str) -> Optional[Dict[str, Any]]:
    if not EXIFTOOL_AVAILABLE:
        return None
    tags = [
        "ThumbnailImage",
        "PreviewImage",
        "JpgFromRaw",
        "PreviewTIFF",
        "PreviewPNG",
        "EmbeddedImage",
    ]
    results: Dict[str, Any] = {}
    for tag in tags:
        try:
            cmd = [EXIFTOOL_PATH, "-b", f"-{tag}", filepath]
            proc = subprocess.run(cmd, capture_output=True, timeout=60)
            if proc.returncode != 0:
                continue
            payload = proc.stdout or b""
            if not payload:
                continue
            mime_type = _detect_thumbnail_mime(payload)
            results[tag] = {
                "size_bytes": len(payload),
                "mime_type": mime_type,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "data_base64": base64.b64encode(payload).decode("ascii"),
            }
        except Exception as e:
            continue
    return results if results else None

# ============================================================================
# Core Extraction Functions
# ============================================================================

def extract_filesystem_metadata(filepath: str) -> Dict[str, Any]:
    try:
        stat_info = os.stat(filepath)
        path = Path(filepath)
        created = datetime.fromtimestamp(stat_info.st_birthtime if hasattr(stat_info, "st_birthtime") else stat_info.st_ctime)
        modified = datetime.fromtimestamp(stat_info.st_mtime)
        accessed = datetime.fromtimestamp(stat_info.st_atime)
        changed = datetime.fromtimestamp(stat_info.st_ctime)
        mode = stat_info.st_mode
        owner_name, group_name = str(stat_info.st_uid), str(stat_info.st_gid)
        if platform.system() != "Windows":
            try:
                import pwd, grp
                owner_name = pwd.getpwuid(stat_info.st_uid).pw_name
                group_name = grp.getgrgid(stat_info.st_gid).gr_name
            except: pass
        file_type = "regular"
        if stat.S_ISDIR(mode):
            file_type = "directory"
        elif stat.S_ISLNK(mode):
            file_type = "symlink"
        elif stat.S_ISFIFO(mode):
            file_type = "fifo"
        elif stat.S_ISSOCK(mode):
            file_type = "socket"
        elif stat.S_ISBLK(mode):
            file_type = "block_device"
        elif stat.S_ISCHR(mode):
            file_type = "char_device"
        return {
            "size_bytes": stat_info.st_size, "size_human": human_readable_size(stat_info.st_size),
            "created": created.isoformat(), "modified": modified.isoformat(), "accessed": accessed.isoformat(),
            "changed": changed.isoformat(),
            "permissions_octal": oct(stat.S_IMODE(mode)), "permissions_human": stat.filemode(mode),
            "owner": owner_name, "owner_uid": stat_info.st_uid, "group": group_name, "group_gid": stat_info.st_gid,
            "inode": stat_info.st_ino, "device": stat_info.st_dev, "hard_links": stat_info.st_nlink,
            "file_type": file_type, "is_hidden": path.name.startswith('.'),
        }
    except Exception as e: return {"error": str(e)}

def extract_file_hashes(filepath: str) -> Dict[str, str]:
    try:
        hashers = {"md5": hashlib.md5(), "sha256": hashlib.sha256(), "sha1": hashlib.sha1()}
        import zlib
        crc = 0
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                for h in hashers.values(): h.update(chunk)
                crc = zlib.crc32(chunk, crc)
        result = {algo: h.hexdigest() for algo, h in hashers.items()}
        result["crc32"] = format(crc & 0xFFFFFFFF, '08x')
        return result
    except Exception as e: return {"error": str(e)}

def extract_extended_attributes(filepath: str) -> Dict[str, Any]:
    if not XATTR_AVAILABLE: return {"available": False}
    try:
        x = xattr.xattr(filepath)
        attrs = {}
        for key in x.list():
            try:
                value = x.get(key)
                key_str = key.decode() if isinstance(key, bytes) else key
                try: attrs[key_str] = value.decode('utf-8')
                except: attrs[key_str] = f"base64:{base64.b64encode(value).decode('ascii')[:200]}"
            except: pass
        return {"available": True, "count": len(attrs), "attributes": attrs}
    except: return {"available": False}

def extract_exif_basic(filepath: str) -> Optional[Dict[str, Any]]:
    if not EXIFREAD_AVAILABLE: return None
    try:
        with open(filepath, "rb") as f:
            tags = exifread.process_file(f, details=True)
        if not tags: return None
        result = {"exif": {}, "gps": {}, "makernote_raw": {}, "interoperability": {}, "thumbnail": {}}
        for tag, value in tags.items():
            tag_value = safe_str(value)
            if tag_value is None: continue
            if tag.startswith("GPS "):
                result["gps"][tag.replace("GPS ", "")] = tag_value
            elif tag.startswith("Interoperability "):
                result["interoperability"][tag.replace("Interoperability ", "")] = tag_value
            elif tag.startswith("Thumbnail "):
                result["thumbnail"][tag.replace("Thumbnail ", "")] = tag_value
            elif "MakerNote" in tag:
                result["makernote_raw"][tag] = tag_value
            else:
                result["exif"][tag.replace("EXIF ", "").replace("Image ", "")] = tag_value
        if not result["interoperability"]:
            result.pop("interoperability", None)
        if not result["thumbnail"]:
            result.pop("thumbnail", None)
        return result
    except: return None

def extract_gps_metadata(filepath: str) -> Optional[Dict[str, Any]]:
    if not EXIFREAD_AVAILABLE: return None
    try:
        with open(filepath, "rb") as f:
            tags = exifread.process_file(f, details=False)
        gps = {}
        if "GPS GPSLatitude" in tags and "GPS GPSLatitudeRef" in tags:
            lat = dms_to_decimal(tags["GPS GPSLatitude"].values, str(tags["GPS GPSLatitudeRef"]))
            if lat:
                gps["latitude_decimal"] = lat
                gps["latitude_dms"] = format_dms(lat, True)
        if "GPS GPSLongitude" in tags and "GPS GPSLongitudeRef" in tags:
            lon = dms_to_decimal(tags["GPS GPSLongitude"].values, str(tags["GPS GPSLongitudeRef"]))
            if lon:
                gps["longitude_decimal"] = lon
                gps["longitude_dms"] = format_dms(lon, False)
        if "latitude_decimal" in gps and "longitude_decimal" in gps:
            lat, lon = gps["latitude_decimal"], gps["longitude_decimal"]
            gps["coordinates"] = f"{lat:.6f}, {lon:.6f}"
            gps["google_maps_url"] = f"https://www.google.com/maps?q={lat},{lon}"
            gps["openstreetmap_url"] = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=15"
        if "GPS GPSAltitude" in tags:
            try:
                alt = tags["GPS GPSAltitude"].values[0]
                gps["altitude_meters"] = round(float(alt.num) / float(alt.den), 2)
            except: pass
        gps_fields = {
            "GPS GPSTimeStamp": "timestamp",
            "GPS GPSDateStamp": "datestamp",
            "GPS GPSSpeed": "speed",
            "GPS GPSSpeedRef": "speed_ref",
            "GPS GPSTrack": "track",
            "GPS GPSTrackRef": "track_ref",
            "GPS GPSImgDirection": "image_direction",
            "GPS GPSImgDirectionRef": "image_direction_ref",
            "GPS GPSSatellites": "satellites",
            "GPS GPSDOP": "dop",
            "GPS GPSMapDatum": "map_datum",
            "GPS GPSProcessingMethod": "processing_method",
        }
        for tag, key in gps_fields.items():
            if tag in tags:
                gps[key] = safe_str(tags[tag])
        return gps if gps else None
    except: return None

def extract_image_properties(filepath: str) -> Optional[Dict[str, Any]]:
    if not PIL_AVAILABLE: return None
    try:
        with Image.open(filepath) as img:
            frames = getattr(img, "n_frames", 1)
            properties = {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "dpi": img.info.get("dpi"),
                "bits_per_pixel": len(img.getbands()) * 8 if hasattr(img, "getbands") else None,
                "color_palette": "yes" if img.palette else "no",
                "animation": frames > 1,
                "frames": frames,
                "icc_profile": "yes" if img.info.get("icc_profile") else "no",
                "is_animated": getattr(img, "is_animated", False),
                "n_frames": frames,
                "has_icc_profile": bool(img.info.get("icc_profile")),
                "has_transparency": "transparency" in img.info or img.mode in ("RGBA", "LA"),
            }
            try:
                from .modules.icc_profile import extract_icc_profile_metadata, analyze_color_accuracy
                icc_details = extract_icc_profile_metadata(filepath)
                if icc_details and "error" not in icc_details:
                    properties["icc_profile_details"] = icc_details
                color_accuracy = analyze_color_accuracy(filepath)
                if color_accuracy:
                    properties["color_accuracy"] = color_accuracy
            except Exception as e:
                properties["icc_profile_details"] = {"error": str(e)}
            return properties
    except: return None

def extract_video_properties(filepath: str) -> Optional[Dict[str, Any]]:
    try:
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", "-show_chapters", filepath]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0: return None
        return json.loads(result.stdout)
    except: return None

def extract_audio_properties(filepath: str) -> Optional[Dict[str, Any]]:
    if not MUTAGEN_AVAILABLE: return None
    try:
        audio = mutagen.File(filepath)
        if not audio: return None
        result = {
            "format": type(audio).__name__,
            "length_seconds": round(audio.info.length, 2) if hasattr(audio.info, "length") else None,
            "length_human": None,
            "bitrate": getattr(audio.info, "bitrate", None),
            "sample_rate": getattr(audio.info, "sample_rate", None),
            "channels": getattr(audio.info, "channels", None),
            "bits_per_sample": getattr(audio.info, "bits_per_sample", None),
        }
        length_seconds = result.get("length_seconds")
        if isinstance(length_seconds, (int, float)):
            mins = int(length_seconds // 60)
            secs = int(length_seconds % 60)
            result["length_human"] = f"{mins}:{secs:02d}"
        tags = {}
        if audio.tags:
            for key, value in audio.tags.items():
                try:
                    tag_name = str(key).split(":")[0]
                    if hasattr(value, "text"): tags[tag_name] = str(value.text[0]) if value.text else None
                    elif isinstance(value, list): tags[tag_name] = str(value[0]) if value else None
                    else: tags[tag_name] = safe_str(value)
                except: pass
        result["tags"] = {
            "title": tags.get("TIT2") or tags.get("TITLE") or tags.get("title"),
            "artist": tags.get("TPE1") or tags.get("ARTIST") or tags.get("artist"),
            "album": tags.get("TALB") or tags.get("ALBUM") or tags.get("album"),
            "year": tags.get("TDRC") or tags.get("DATE") or tags.get("date"),
            "genre": tags.get("TCON") or tags.get("GENRE") or tags.get("genre"),
            "track_number": tags.get("TRCK") or tags.get("TRACKNUMBER") or tags.get("tracknumber"),
            "composer": tags.get("TCOM") or tags.get("COMPOSER") or tags.get("composer"),
            "album_artist": tags.get("TPE2") or tags.get("ALBUMARTIST") or tags.get("albumartist"),
            "comment": tags.get("COMM") or tags.get("COMMENT") or tags.get("comment"),
            "lyrics": tags.get("USLT") or tags.get("LYRICS"),
        }
        result["has_album_art"] = False
        if hasattr(audio, "pictures") and audio.pictures:
            result["has_album_art"] = True
            result["album_art_count"] = len(audio.pictures)
        elif audio.tags and any("APIC" in str(k) for k in audio.tags.keys()):
            result["has_album_art"] = True
        result["raw_tags"] = tags
        return result
    except: return None

def extract_pdf_properties(filepath: str) -> Optional[Dict[str, Any]]:
    if not PYPDF_AVAILABLE: return None
    try:
        reader = PdfReader(filepath)
        info = dict(reader.metadata or {})
        result = {
            "page_count": len(reader.pages), "is_encrypted": reader.is_encrypted,
            "author": info.get("/Author"), "title": info.get("/Title"),
            "creator": info.get("/Creator"), "producer": info.get("/Producer"),
            "creation_date": safe_str(info.get("/CreationDate")),
            "modification_date": safe_str(info.get("/ModDate")),
            "subject": info.get("/Subject"),
            "keywords": info.get("/Keywords"),
        }
        if reader.pages and reader.pages[0].mediabox:
            width = float(reader.pages[0].mediabox.width)
            height = float(reader.pages[0].mediabox.height)
            result["page_width_pts"] = width
            result["page_height_pts"] = height
            result["page_width"] = width
            result["page_height"] = height
        return result
    except: return None

def extract_svg_properties(filepath: str) -> Optional[Dict[str, Any]]:
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(filepath)
        root = tree.getroot()
        svg_data: Dict[str, Any] = {
            "width": root.get("width"),
            "height": root.get("height"),
            "viewBox": root.get("viewBox"),
            "version": root.get("version"),
        }
        if svg_data["viewBox"] and not svg_data["width"]:
            parts = svg_data["viewBox"].split()
            if len(parts) >= 4:
                svg_data["viewBox_width"] = parts[2]
                svg_data["viewBox_height"] = parts[3]
        svg_data["element_count"] = len(list(root.iter()))
        svg_data["path_count"] = len(root.findall(".//{http://www.w3.org/2000/svg}path") or root.findall(".//path"))
        style_elements = root.findall(".//{http://www.w3.org/2000/svg}style") or root.findall(".//style")
        svg_data["has_embedded_styles"] = len(style_elements) > 0
        script_elements = root.findall(".//{http://www.w3.org/2000/svg}script") or root.findall(".//script")
        svg_data["has_scripts"] = len(script_elements) > 0
        return svg_data
    except: return None

def calculate_metadata(metadata: Dict[str, Any], current_time: datetime) -> Dict[str, Any]:
    calc = {}
    img = metadata.get("image")
    if img and img.get("width") and img.get("height"):
        w, h = img["width"], img["height"]
        from math import gcd
        d = gcd(w, h) or 1
        calc["aspect_ratio"] = f"{w//d}:{h//d}"
        try:
            calc["aspect_ratio_decimal"] = round(float(w) / float(h), 3)
        except Exception as e:
            pass  # TODO: Consider logging: logger.debug(f'Handled exception: {e}')
        calc["megapixels"] = round(w * h / 1_000_000, 2)
        calc["orientation"] = "landscape" if w > h else "portrait" if h > w else "square"
    video = metadata.get("video") or {}
    fmt = video.get("format") if isinstance(video, dict) else None
    if isinstance(fmt, dict):
        duration_value = fmt.get("duration")
        try:
            duration = float(duration_value) if duration_value is not None else None
        except Exception as e:
            duration = None
        if duration:
            calc["duration_human"] = f"{int(duration // 60)}:{int(duration % 60):02d}"
            size_bytes = metadata.get("filesystem", {}).get("size_bytes")
            if isinstance(size_bytes, (int, float)) and duration:
                calc["size_per_second"] = human_readable_size(size_bytes / duration)
    fs = metadata.get("filesystem", {})
    if fs.get("created"):
        try:
            created = datetime.fromisoformat(fs["created"])
            delta = current_time - created
            calc["file_age_days"] = delta.days
            calc["file_age_human"] = human_readable_time_delta(delta)
            calc["file_age"] = {
                "days": delta.days,
                "hours": int(delta.total_seconds() // 3600),
                "human_readable": human_readable_time_delta(delta),
            }
        except: pass
    if fs.get("modified"):
        try:
            modified = datetime.fromisoformat(fs["modified"])
            delta = current_time - modified
            calc["time_since_modified"] = {
                "days": delta.days,
                "hours": int(delta.total_seconds() // 3600),
                "human_readable": human_readable_time_delta(delta),
            }
        except: pass
    if fs.get("accessed"):
        try:
            accessed = datetime.fromisoformat(fs["accessed"])
            delta = current_time - accessed
            calc["time_since_accessed"] = {
                "days": delta.days,
                "hours": int(delta.total_seconds() // 3600),
                "human_readable": human_readable_time_delta(delta),
            }
        except: pass
    return calc

# ============================================================================
# Main Extraction Function
# ============================================================================

def extract_metadata(filepath: str, tier: str = "super") -> Dict[str, Any]:
    current_time = datetime.now()
    path = Path(filepath)
    
    if not path.exists(): return {"error": f"File not found: {filepath}"}
    if not path.is_file(): return {"error": f"Not a file: {filepath}"}
    
    try: tier_enum = Tier(tier.lower())
    except ValueError: tier_enum = Tier.SUPER
    
    tier_config = TIER_CONFIGS[tier_enum]
    mime_type = detect_mime_type(filepath)
    
    result = {
        "extraction_info": {
            "timestamp": current_time.isoformat(), "tier": tier, "engine_version": "3.0.0",
            "exiftool_used": False,
            "libraries": {
                "pillow": PIL_AVAILABLE, "exifread": EXIFREAD_AVAILABLE, "ffmpeg": FFMPEG_AVAILABLE,
                "mutagen": MUTAGEN_AVAILABLE, "pypdf": PYPDF_AVAILABLE, "xattr": XATTR_AVAILABLE,
                "exiftool": EXIFTOOL_AVAILABLE, "iptcinfo3": IPTC_AVAILABLE,
                "xmp": XMP_AVAILABLE, "imagehash": IMAGEHASH_AVAILABLE,
            }
        },
        "file": {"path": str(path.absolute()), "name": path.name, "extension": path.suffix.lower(), "mime_type": mime_type},
        "summary": {}, "locked_fields": [],
        "thumbnail": None, "perceptual_hashes": None,
        "iptc_raw": None, "xmp_raw": None,
    }
    
    fs_data = extract_filesystem_metadata(filepath)
    result["summary"] = {
        "filename": path.name, "filesize": fs_data.get("size_human", "Unknown"),
        "filesize_bytes": fs_data.get("size_bytes", 0), "filetype": path.suffix.upper().lstrip('.') or "Unknown",
        "mime_type": mime_type,
    }
    
    if tier_config.filesystem_details: result["filesystem"] = fs_data
    else:
        result["filesystem"] = {"size_bytes": fs_data.get("size_bytes"), "size_human": fs_data.get("size_human"), "_locked": True}
        result["locked_fields"].append("filesystem_details")
    
    if tier_config.file_hashes: result["hashes"] = extract_file_hashes(filepath)
    else: result["hashes"] = {"_locked": True}; result["locked_fields"].append("hashes")
    
    if tier_config.extended_attributes: result["extended_attributes"] = extract_extended_attributes(filepath)
    else: result["extended_attributes"] = {"_locked": True}; result["locked_fields"].append("extended_attributes")
    
    # ExifTool extraction (Premium+)
    exiftool_data = None
    if tier_config.exiftool_enhanced and EXIFTOOL_AVAILABLE:
        exiftool_data = extract_with_exiftool(filepath)
        if exiftool_data: result["extraction_info"]["exiftool_used"] = True
    
    ext = path.suffix.lower()
    
    # Images
    if mime_type and mime_type.startswith("image"):
        result["image"] = extract_image_properties(filepath)
        if result["image"]:
            result["summary"]["width"] = result["image"].get("width")
            result["summary"]["height"] = result["image"].get("height")

        if tier_config.thumbnails:
            result["thumbnail"] = extract_thumbnail(filepath)
            embedded_thumbs = extract_embedded_thumbnails(filepath)
            if embedded_thumbs:
                result["embedded_thumbnails"] = embedded_thumbs
        else:
            result["thumbnail"] = {"_locked": True}
            result["locked_fields"].append("thumbnail")
            result["embedded_thumbnails"] = {"_locked": True}
            result["locked_fields"].append("embedded_thumbnails")

        if tier_config.perceptual_hashes:
            result["perceptual_hashes"] = extract_perceptual_hashes(filepath)
        else:
            result["perceptual_hashes"] = {"_locked": True}
            result["locked_fields"].append("perceptual_hashes")
        
        if exiftool_data:
            result["exif"] = exiftool_data.get("exif", {})
            result["gps"] = exiftool_data.get("gps", {}) if tier_config.gps_data else {"_locked": True}
            result["composite"] = exiftool_data.get("composite", {})
            exif_ifd = exiftool_data.get("exif_ifd")
            if isinstance(exif_ifd, dict):
                if not tier_config.gps_data and isinstance(exif_ifd.get("gps"), dict):
                    exif_ifd = dict(exif_ifd)
                    exif_ifd["gps"] = {"_locked": True}
                result["exif_ifd"] = exif_ifd
            if exiftool_data.get("interoperability"):
                result["interoperability"] = exiftool_data["interoperability"]
            if exiftool_data.get("thumbnail_metadata"):
                result["thumbnail_metadata"] = exiftool_data["thumbnail_metadata"]
            if exiftool_data.get("image_container"):
                result["image_container"] = exiftool_data["image_container"]
            if exiftool_data.get("icc_profile"):
                result["icc_profile"] = exiftool_data["icc_profile"]
            
            if tier_config.makernotes and exiftool_data.get("makernote"):
                result["makernote"] = exiftool_data["makernote"]
                for mfr, fields in exiftool_data["makernote"].items():
                    if isinstance(fields, dict):
                        result["summary"][f"makernote_{mfr}_fields"] = len(fields)
            elif exiftool_data.get("makernote"):
                result["makernote"] = {"_locked": True}
                result["locked_fields"].append("makernote")
            
            if tier_config.iptc_xmp:
                if exiftool_data.get("iptc"):
                    result["iptc"] = exiftool_data["iptc"]
                    result["iptc_raw"] = exiftool_data["iptc"]
                if exiftool_data.get("xmp"):
                    result["xmp"] = exiftool_data["xmp"]
                    result["xmp_raw"] = exiftool_data["xmp"]
                if exiftool_data.get("xmp_namespaces"):
                    result["xmp_namespaces"] = exiftool_data["xmp_namespaces"]
            else:
                if exiftool_data.get("iptc"):
                    result["iptc"] = {"_locked": True, "_count": len(exiftool_data["iptc"])}
                    result["locked_fields"].append("iptc")
                if exiftool_data.get("xmp"):
                    result["xmp"] = {"_locked": True, "_count": len(exiftool_data["xmp"])}
                    result["locked_fields"].append("xmp")
                if exiftool_data.get("xmp_namespaces"):
                    ns_count = sum(
                        len(v) for v in exiftool_data["xmp_namespaces"].values() if isinstance(v, dict)
                    )
                    result["xmp_namespaces"] = {"_locked": True, "_count": ns_count}
                    result["locked_fields"].append("xmp_namespaces")
        else:
            basic_exif = extract_exif_basic(filepath)
            if basic_exif:
                result["exif"] = basic_exif.get("exif", {})
                if basic_exif.get("interoperability"):
                    result["interoperability"] = basic_exif["interoperability"]
                if basic_exif.get("thumbnail"):
                    result["thumbnail_metadata"] = basic_exif["thumbnail"]
                if tier_config.makernotes: result["makernote"] = {"raw": basic_exif.get("makernote_raw", {})}
                else: result["makernote"] = {"_locked": True}; result["locked_fields"].append("makernote")
            if tier_config.gps_data:
                gps = extract_gps_metadata(filepath)
                if gps: result["gps"] = gps
            else: result["gps"] = {"_locked": True}; result["locked_fields"].append("gps")
            if tier_config.iptc_xmp:
                iptc_data = extract_iptc_metadata(filepath)
                if iptc_data:
                    fields = iptc_data.get("fields") or {}
                    raw = iptc_data.get("raw") or {}
                    result["iptc"] = fields or raw
                    if raw:
                        result["iptc_raw"] = raw
                xmp_data = extract_xmp_metadata(filepath)
                if xmp_data:
                    fields = xmp_data.get("fields") or {}
                    raw = xmp_data.get("raw") or {}
                    result["xmp"] = fields or raw
                    if raw:
                        result["xmp_raw"] = raw
            else:
                result["iptc"] = {"_locked": True}
                result["xmp"] = {"_locked": True}
                result["locked_fields"].extend(["iptc", "xmp"])
    
    # Video
    elif mime_type and mime_type.startswith("video"):
        if tier_config.video_encoding:
            result["video"] = extract_video_properties(filepath)
            # Deep codec details (Phase 2)
            if tier_config.video_codec_details and VIDEO_CODEC_DETAILS_AVAILABLE:
                try:
                    result["video"]["codec_details"] = extract_video_codec_details(filepath)
                except Exception as e:
                    logger.warning(f"Failed to extract video codec details: {e}")
                    result["video"]["codec_details"] = {"error": str(e)}
            if (
                tier_config.video_codec_details
                and tier_config.exiftool_enhanced
                and VIDEO_TELEMETRY_AVAILABLE
            ):
                try:
                    result["video"]["telemetry"] = extract_video_telemetry(filepath)
                except Exception as e:
                    logger.warning(f"Failed to extract video telemetry: {e}")
                    result["video"]["telemetry"] = {"error": str(e)}
            if exiftool_data and exiftool_data.get("video"):
                if result.get("video"): result["video"]["exiftool_details"] = exiftool_data["video"]
                else: result["video"] = exiftool_data["video"]
        else: result["video"] = {"_locked": True}; result["locked_fields"].append("video")

        # Container-level metadata (MP4/MKV/AVI)
        if tier_config.container_details and CONTAINER_METADATA_AVAILABLE:
            try:
                result["container"] = extract_container_metadata(filepath)
            except Exception as e:
                logger.warning(f"Failed to extract container metadata: {e}")
                result["container"] = {"error": str(e)}
        else:
            if "container" not in result:
                result["container"] = {"_locked": True}
                result["locked_fields"].append("container")
    
    # Audio
    elif mime_type and mime_type.startswith("audio") or ext in [".mp3", ".flac", ".ogg", ".wav", ".m4a"]:
        if tier_config.audio_details:
            result["audio"] = extract_audio_properties(filepath)
            # Deep audio codec details (Phase 2)
            if tier_config.audio_codec_details and AUDIO_CODEC_DETAILS_AVAILABLE:
                try:
                    result["audio"]["codec_details"] = extract_audio_codec_details(filepath)
                except Exception as e:
                    logger.warning(f"Failed to extract audio codec details: {e}")
                    result["audio"]["codec_details"] = {"error": str(e)}
            if exiftool_data and exiftool_data.get("audio"):
                if result.get("audio"): result["audio"]["exiftool_details"] = exiftool_data["audio"]
                else: result["audio"] = exiftool_data["audio"]
        else: result["audio"] = {"_locked": True}; result["locked_fields"].append("audio")
    
    # PDF
    elif mime_type == "application/pdf" or ext == ".pdf":
        if tier_config.pdf_details:
            result["pdf"] = extract_pdf_properties(filepath)
            # Phase 3: Complete PDF metadata extraction
            if tier_config.pdf_complete:
                try:
                    from .modules.pdf_metadata_complete import extract_pdf_complete
                    complete_pdf = extract_pdf_complete(filepath)
                    if complete_pdf:
                        result["pdf_complete"] = complete_pdf
                except ImportError:
                    pass  # Module not available
        else:
            result["pdf"] = {"_locked": True}
            result["locked_fields"].append("pdf")
    
    # Office documents (OOXML, ODF, iWork)
    elif ext in [".docx", ".xlsx", ".pptx", ".odt", ".ods", ".odp", ".pages", ".numbers", ".keynote"]:
        if tier_config.office_documents:
            try:
                from .modules.office_documents import extract_office_complete
                office_data = extract_office_complete(filepath)
                if office_data:
                    result["office"] = office_data
            except ImportError:
                pass  # Module not available
        else:
            result["office"] = {"_locked": True}
            result["locked_fields"].append("office")
    
    # Web and Social Media metadata (HTML, HTM)
    elif ext in [".html", ".htm"]:
        if tier_config.web_social_metadata:
            try:
                from .modules.web_social_metadata import extract_web_social_complete
                web_social_data = extract_web_social_complete(filepath)
                if web_social_data:
                    result["web_social"] = web_social_data
            except ImportError:
                pass  # Module not available
        else:
            result["web_social"] = {"_locked": True}
            result["locked_fields"].append("web_social")
    
    # Email and Communication metadata (.eml, .msg, .mbox)
    elif ext in [".eml", ".msg", ".mbox"]:
        if tier_config.email_metadata:
            try:
                from .modules.email_metadata import extract_email_complete
                email_data = extract_email_complete(filepath)
                if email_data:
                    result["email"] = email_data
            except ImportError:
                pass  # Module not available
        else:
            result["email"] = {"_locked": True}
            result["locked_fields"].append("email")
    
    # AI/ML Model metadata (various ML model formats)
    elif ext in [".h5", ".pb", ".pth", ".pt", ".onnx", ".pkl", ".joblib", ".model", ".tflite", ".mlmodel", ".caffemodel"] or (ext in [".json", ".yaml", ".yml", ".cfg", ".ini"] and any(x in filepath.lower() for x in ["model", "config", "hyper", "param", "train"])):
        if tier_config.ai_ml_metadata:
            try:
                from .modules.ai_ml_metadata import extract_ai_ml_complete
                ai_ml_data = extract_ai_ml_complete(filepath)
                if ai_ml_data:
                    result["ai_ml"] = ai_ml_data
            except ImportError:
                pass  # Module not available
        else:
            result["ai_ml"] = {"_locked": True}
            result["locked_fields"].append("ai_ml")
    
    # Blockchain/NFT metadata (various crypto-related formats)
    elif ext in [".abi", ".sol", ".vy", ".rs", ".keystore", ".tx", ".trx", ".blk"] or (ext in [".json", ".config", ".env"] and any(x in filepath.lower() for x in ["nft", "token", "contract", "wallet", "blockchain", "crypto"])):
        if tier_config.blockchain_nft_metadata:
            try:
                from .modules.blockchain_nft_metadata import extract_blockchain_nft_complete
                blockchain_data = extract_blockchain_nft_complete(filepath)
                if blockchain_data:
                    result["blockchain_nft"] = blockchain_data
            except ImportError:
                pass  # Module not available
        else:
            result["blockchain_nft"] = {"_locked": True}
            result["locked_fields"].append("blockchain_nft")
    
    # AR/VR content metadata (3D models, scenes, animations)
    elif ext in [".obj", ".fbx", ".gltf", ".glb", ".dae", ".3ds", ".blend", ".usd", ".usda", ".usdc", ".usdz", ".x3d", ".wrl", ".scn", ".scene", ".unity", ".unreal"]:
        if tier_config.ar_vr_metadata:
            try:
                from .modules.ar_vr_metadata import extract_ar_vr_complete
                ar_vr_data = extract_ar_vr_complete(filepath)
                if ar_vr_data:
                    result["ar_vr"] = ar_vr_data
            except ImportError:
                pass  # Module not available
        else:
            result["ar_vr"] = {"_locked": True}
            result["locked_fields"].append("ar_vr")
    
    # IoT device metadata (device configs, sensor data, telemetry)
    elif (ext in [".json", ".xml", ".yaml", ".yml", ".config", ".conf", ".ini", ".cfg", ".properties", ".env", ".csv", ".tsv", ".log", ".data"] and
          any(x in filepath.lower() for x in ["iot", "device", "sensor", "firmware", "telemetry", "mqtt", "coap", "zigbee", "bluetooth", "wifi", "configuration", "config", "settings", "calibration"])):
        if tier_config.iot_metadata:
            try:
                from .modules.iot_metadata import extract_iot_complete
                iot_data = extract_iot_complete(filepath)
                if iot_data:
                    result["iot"] = iot_data
            except ImportError:
                pass  # Module not available
        else:
            result["iot"] = {"_locked": True}
            result["locked_fields"].append("iot")
    
    # SVG
    elif ext == ".svg": result["svg"] = extract_svg_properties(filepath)

    # Scientific/medical formats (DICOM, FITS, GeoTIFF, LAS)
    if SCIENTIFIC_AVAILABLE:
        scientific_detect = detect_scientific_format(filepath)
        if scientific_detect.get("is_scientific"):
            if tier_config.scientific_details:
                scientific_data = extract_scientific_metadata(filepath)
                if scientific_data:
                    result["scientific"] = scientific_data
                    result["summary"]["scientific_format"] = scientific_data.get("format_type")
            else:
                result["scientific"] = {"_locked": True}
                result["locked_fields"].append("scientific")

    # Scientific data formats (HDF5, NetCDF)
    hdf5_exts = {".h5", ".hdf5", ".he5"}
    netcdf_exts = {".nc", ".netcdf", ".nc4"}
    if ext in hdf5_exts or ext in netcdf_exts:
        if ext in hdf5_exts:
            result["summary"]["scientific_data_format"] = "HDF5"
        else:
            result["summary"]["scientific_data_format"] = "NetCDF"
        if tier_config.scientific_details:
            if SCIENTIFIC_DATA_AVAILABLE:
                if ext in hdf5_exts:
                    result["scientific_data"] = extract_hdf5_metadata(filepath)
                else:
                    result["scientific_data"] = extract_netcdf_metadata(filepath)
            else:
                result["scientific_data"] = {
                    "available": False,
                    "reason": "scientific data module not available",
                }
        else:
            result["scientific_data"] = {"_locked": True}
            result["locked_fields"].append("scientific_data")
    
    # Calculated
    if tier_config.calculated_fields: result["calculated"] = calculate_metadata(result, current_time)
    else: result["calculated"] = {"_locked": True}; result["locked_fields"].append("calculated")

    # Normalized/searchable fields
    if MetadataMapper is not None:
        try:
            mapper = MetadataMapper()
            result["normalized"] = mapper.map_metadata(result)
        except Exception as e:
            result["normalized"] = {}
    
    # Forensic (expanded)
    if tier_config.forensic_details:
        try:
            from modules.forensic_metadata import extract_forensic_metadata
            result["forensic"] = extract_forensic_metadata(filepath)
        except Exception as e:
            logger.warning(f"Failed to extract forensic metadata: {e}")
            # Fallback to minimal forensic info
            result["forensic"] = {"creation_timestamp": fs_data.get("created"), "modification_timestamp": fs_data.get("modified")}
            if result.get("exif"):
                result["forensic"]["device_make"] = result["exif"].get("Make")
                result["forensic"]["device_model"] = result["exif"].get("Model")
                if tier_config.serial_numbers:
                    result["forensic"]["serial_number"] = result["exif"].get("SerialNumber")
    else:
        result["forensic"] = {"_locked": True}
        result["locked_fields"].append("forensic")
    
    # Burned Metadata (OCR from image overlays)
    if tier_config.burned_metadata and mime_type and mime_type.startswith("image"):
        try:
            from modules.ocr_burned_metadata import extract_burned_metadata
            result["burned_metadata"] = extract_burned_metadata(filepath)
        except Exception as e:
            logger.warning(f"Failed to extract burned metadata: {e}")
            result["burned_metadata"] = {"has_burned_metadata": False, "ocr_available": False, "error": str(e)}
    else:
        result["burned_metadata"] = {"_locked": True}
        result["locked_fields"].append("burned_metadata")
    
    # Metadata Comparison (verify embedded vs burned data)
    if tier_config.metadata_comparison and mime_type and mime_type.startswith("image"):
        try:
            from modules.metadata_comparator import compare_metadata
            embedded_data = {
                "gps": result.get("gps", {}),
                "datetime_original": result.get("exif", {}).get("DateTimeOriginal"),
                "datetime_digitized": result.get("exif", {}).get("DateTimeDigitized"),
                "datetime": result.get("exif", {}).get("DateTime"),
            }
            burned_data = result.get("burned_metadata", {})
            result["metadata_comparison"] = compare_metadata(embedded_data, burned_data)
        except Exception as e:
            logger.warning(f"Failed to compare metadata: {e}")
            result["metadata_comparison"] = {"error": str(e)}
    else:
        result["metadata_comparison"] = {"_locked": True}
        result["locked_fields"].append("metadata_comparison")
    
    def count_fields(obj):
        if not isinstance(obj, dict): return 1 if obj is not None else 0
        return sum(count_fields(v) for k, v in obj.items() if not k.startswith("_"))
    
    result["extraction_info"]["fields_extracted"] = count_fields(result)
    result["extraction_info"]["locked_categories"] = len(result["locked_fields"])
    
    return result

# ============================================================================
# CLI
# ============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="MetaExtract - Forensic Metadata Extraction")
    parser.add_argument("file", help="File to extract metadata from")
    parser.add_argument("--tier", "-t", default="super", choices=["free", "starter", "premium", "super"])
    parser.add_argument("--output", "-o", help="Output JSON file")
    parser.add_argument("--quiet", "-q", action="store_true", help="JSON only output")
    args = parser.parse_args()
    
    if not args.quiet:
        print(f"MetaExtract v3.0.0 - Extracting from: {args.file}", file=sys.stderr)
        print(f"Tier: {args.tier} | ExifTool: {'✓' if EXIFTOOL_AVAILABLE else '✗'}", file=sys.stderr)
    
    result = extract_metadata(args.file, tier=args.tier)
    json_out = json.dumps(result, indent=2, default=str)
    
    if args.output:
        with open(args.output, "w") as f: f.write(json_out)
        if not args.quiet: print(f"Saved to: {args.output}", file=sys.stderr)
    else: print(json_out)

if __name__ == "__main__":
    main()
