#!/usr/bin/env python3
"""
Enhanced Image Metadata Extractor for MetaExtract.

This module provides comprehensive image metadata extraction for JPEG, PNG, TIFF,
WebP, GIF, HEIC, and PSD formats. It integrates ExifTool as the primary extractor
with pure-Python fallbacks.

Features:
- ExifTool integration (primary, full coverage)
- exifread fallback (pure Python, basic EXIF)
- XMP packet parsing
- ICC profile extraction
- GPS coordinate normalization
- DateTime normalization
- Sensitivity-based redaction

Author: MetaExtract Team
Version: 2.0.0
"""

import logging
import os
import subprocess
import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

EXIFTOOL_PATH = "/opt/homebrew/bin/exiftool"
EXIFTOOL_AVAILABLE = os.path.exists(EXIFTOOL_PATH) and os.access(EXIFTOOL_PATH, os.X_OK)

try:
    from PIL import Image, ExifTags
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import exifread
    EXIFREAD_AVAILABLE = True
except ImportError:
    EXIFREAD_AVAILABLE = False

try:
    import iptcinfo3
    IPTC_AVAILABLE = True
except ImportError:
    IPTC_AVAILABLE = False

try:
    from ..core.base_engine import BaseExtractor, ExtractionContext, ExtractionResult, ExtractionStatus
    BASE_ENGINE_AVAILABLE = True
except ImportError:
    BASE_ENGINE_AVAILABLE = False
    ExtractionContext = None
    ExtractionResult = None
    ExtractionStatus = None
    BaseExtractor = None


class EnhancedImageExtractor:
    """
    Enhanced image metadata extractor with ExifTool integration.
    
    This extractor provides comprehensive coverage of embedded image metadata
    including EXIF, IPTC, XMP, ICC profiles, and vendor-specific MakerNotes.
    """
    
    SUPPORTED_FORMATS = [
        '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.gif', '.bmp',
        '.webp', '.heic', '.heif', '.avif', '.psd', '.cr2', '.cr3',
        '.nef', '.arw', '.dng', '.orf', '.rw2', '.pef', '.x3f'
    ]
    
    SENSITIVITY_HIGH = ["gps", "serial", "owner", "contact", "person"]
    SENSITIVITY_MODERATE = ["datetime", "location", "creator"]
    SENSITIVITY_LOW = ["camera", "lens", "software"]
    
    def __init__(self, redact_sensitive: bool = True, product_mode: str = "extract+redact", name: str = "EnhancedImageExtractor"):
        """Initialize the enhanced extractor."""
        self.name = name
        self.supported_formats = self.SUPPORTED_FORMATS
        self.redact_sensitive = redact_sensitive
        self.product_mode = product_mode
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.extraction_stats = {
            "exiftool_used": False,
            "exifread_used": False,
            "pill_used": False,
            "iptc_used": False,
            "xmp_parsed": False,
            "icc_parsed": False,
            "errors": []
        }
    
    def can_extract(self, filepath: str) -> bool:
        """Check if we can extract metadata from this file."""
        ext = Path(filepath).suffix.lower()
        return ext in self.supported_formats
    
    def extract(self, filepath: str) -> Dict[str, Any]:
        """
        Extract metadata from an image file.
        
        Args:
            filepath: Path to the image file
            
        Returns:
            Dictionary containing all extracted metadata
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        result = {
            "file_info": self._extract_file_info(filepath),
            "surfaces": {},
            "extraction_stats": self.extraction_stats,
            "extraction_timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        if EXIFTOOL_AVAILABLE:
            try:
                exiftool_result = self._extract_with_exiftool(filepath)
                if exiftool_result:
                    self._merge_exiftool_result(result, exiftool_result)
                    self.extraction_stats["exiftool_used"] = True
                    return result
            except Exception as e:
                self.extraction_stats["errors"].append(f"ExifTool failed: {str(e)}")
                logger.warning(f"ExifTool extraction failed: {e}")
        
        if EXIFREAD_AVAILABLE:
            try:
                exif_data = self._extract_exifread(filepath)
                if exif_data:
                    result["surfaces"]["exif"] = exif_data
                    self.extraction_stats["exifread_used"] = True
            except Exception as e:
                self.extraction_stats["errors"].append(f"exifread failed: {str(e)}")
        
        if IPTC_AVAILABLE:
            try:
                iptc_data = self._extract_iptc(filepath)
                if iptc_data:
                    result["surfaces"]["iptc"] = iptc_data
                    self.extraction_stats["iptc_used"] = True
            except Exception as e:
                self.extraction_stats["errors"].append(f"IPTC extraction failed: {str(e)}")
        
        if PIL_AVAILABLE:
            try:
                pil_data = self._extract_pil(filepath)
                if pil_data:
                    result["surfaces"]["pil"] = pil_data
                    self.extraction_stats["pill_used"] = True
            except Exception as e:
                self.extraction_stats["errors"].append(f"PIL extraction failed: {str(e)}")
        
        if self.redact_sensitive and self.product_mode in ["extract+redact", "extract+index"]:
            result = self._apply_redaction(result)
        
        return result
    
    def _extract_file_info(self, filepath: str) -> Dict[str, Any]:
        """Extract basic file information."""
        stat = os.stat(filepath)
        path = Path(filepath)
        
        return {
            "filename": path.name,
            "file_size_bytes": stat.st_size,
            "modified_timestamp": stat.st_mtime,
            "file_extension": path.suffix.lower(),
            "mime_type": self._get_mime_type(filepath)
        }
    
    def _get_mime_type(self, filepath: str) -> str:
        """Get MIME type based on extension."""
        ext = Path(filepath).suffix.lower()
        mime_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.heic': 'image/heic',
            '.heif': 'image/heif',
            '.avif': 'image/avif',
            '.psd': 'image/x-photoshop',
        }
        return mime_map.get(ext, 'application/octet-stream')
    
    def _extract_with_exiftool(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract metadata using ExifTool."""
        if not EXIFTOOL_AVAILABLE:
            return None
        
        cmd = [
            EXIFTOOL_PATH,
            '-j', '-a', '-G1', '-s',
            '-overwrite_original',
            filepath
        ]
        
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                logger.warning(f"ExifTool error: {result.stderr}")
                return None
            
            output = result.stdout.strip()
            if output:
                data = json.loads(output)
                return data[0] if data else None
            
        except subprocess.TimeoutExpired:
            self.extraction_stats["errors"].append("ExifTool timeout")
        except json.JSONDecodeError as e:
            self.extraction_stats["errors"].append(f"ExifTool JSON parse error: {str(e)}")
        except Exception as e:
            self.extraction_stats["errors"].append(f"ExifTool unexpected error: {str(e)}")
        
        return None
    
    def _get_value(self, data: Dict, key: str) -> Any:
        """Get a value from ExifTool data, checking both simple and grouped keys."""
        if key in data:
            return data[key]
        for k, v in data.items():
            if k.endswith(":" + key) or k == key:
                return v
        return None
    
    def _merge_exiftool_result(self, result: Dict, exiftool_data: Dict) -> None:
        """Merge ExifTool results into our schema."""
        result["file_info"]["image_width"] = self._get_value(exiftool_data, "ImageWidth")
        result["file_info"]["image_height"] = self._get_value(exiftool_data, "ImageHeight")
        result["file_info"]["color_components"] = self._get_value(exiftool_data, "ColorComponents")
        result["file_info"]["bit_depth"] = self._get_value(exiftool_data, "BitsPerSample")
        
        result["surfaces"] = {
            "container": self._group_container_metadata(exiftool_data),
            "exif_ifd0": self._group_exif_ifd0(exiftool_data),
            "exif_exif": self._group_exif_exif(exiftool_data),
            "exif_gps": self._group_exif_gps(exiftool_data),
            "iptc": self._group_iptc(exiftool_data),
            "xmp": self._group_xmp(exiftool_data),
            "icc": self._group_icc(exiftool_data),
            "makernote": self._group_makernotes(exiftool_data)
        }
        
        result["normalized"] = {
            "gps_decimal": self._normalize_gps(exiftool_data),
            "datetime_iso": self._normalize_datetime(exiftool_data),
            "rationals": self._normalize_rationals(exiftool_data)
        }
        
        self.extraction_stats["xmp_parsed"] = any(k.startswith("XMP-") for k in exiftool_data.keys())
        self.extraction_stats["icc_parsed"] = any(k.startswith("ICC") for k in exiftool_data.keys())
    
    def _group_container_metadata(self, data: Dict) -> Dict[str, Any]:
        """Group container/marker metadata."""
        container = {}
        file_type = self._get_value(data, "FileType")
        
        if file_type == "JPEG":
            container["format"] = "JPEG"
            container["jfif_version"] = self._get_value(data, "JFIFVersion")
            container["app_markers"] = [k for k in data.keys() if k.startswith("APP")]
        elif file_type == "PNG":
            container["format"] = "PNG"
            container["width"] = self._get_value(data, "ImageWidth")
            container["height"] = self._get_value(data, "ImageHeight")
        elif file_type == "TIFF":
            container["format"] = "TIFF"
            container["byte_order"] = self._get_value(data, "ExifByteOrder")
        elif file_type == "WEBP":
            container["format"] = "WebP"
        
        container["mime_type"] = self._get_value(data, "MIMEType")
        container["encoding_process"] = self._get_value(data, "EncodingProcess")
        
        return container
    
    def _group_exif_ifd0(self, data: Dict) -> Dict[str, Any]:
        """Group EXIF IFD0 metadata."""
        return {
            "make": self._get_value(data, "Make"),
            "model": self._get_value(data, "Model"),
            "software": self._get_value(data, "Software"),
            "artist": self._get_value(data, "Artist"),
            "copyright": self._get_value(data, "Copyright"),
            "datetime": self._get_value(data, "DateTime"),
            "orientation": self._get_value(data, "Orientation"),
            "x_resolution": self._get_value(data, "XResolution"),
            "y_resolution": self._get_value(data, "YResolution"),
            "resolution_unit": self._get_value(data, "ResolutionUnit"),
            "has_thumbnail": self._get_value(data, "ThumbnailOffset") is not None
        }
    
    def _group_exif_exif(self, data: Dict) -> Dict[str, Any]:
        """Group EXIF EXIF IFD metadata."""
        return {
            "exposure_time": self._get_value(data, "ExposureTime"),
            "f_number": self._get_value(data, "FNumber"),
            "iso_speed_ratings": self._get_value(data, "ISOSpeedRatings"),
            "metering_mode": self._get_value(data, "MeteringMode"),
            "flash": self._get_value(data, "Flash"),
            "focal_length": self._get_value(data, "FocalLength"),
            "focal_length_35mm": self._get_value(data, "FocalLengthIn35mmFilm"),
            "color_space": self._get_value(data, "ColorSpace"),
            "pixel_x_dimension": self._get_value(data, "PixelXDimension"),
            "pixel_y_dimension": self._get_value(data, "PixelYDimension"),
            "datetime_original": self._get_value(data, "DateTimeOriginal"),
            "datetime_digitized": self._get_value(data, "DateTimeDigitized"),
            "lens_make": self._get_value(data, "LensMake"),
            "lens_model": self._get_value(data, "LensModel"),
            "camera_serial_number": self._get_value(data, "CameraSerialNumber"),
            "camera_owner_name": self._get_value(data, "CameraOwnerName"),
            "exposure_mode": self._get_value(data, "ExposureMode"),
            "white_balance": self._get_value(data, "WhiteBalance"),
            "scene_capture_type": self._get_value(data, "SceneCaptureType"),
            "exif_version": self._get_value(data, "ExifVersion")
        }
    
    def _group_exif_gps(self, data: Dict) -> Dict[str, Any]:
        """Group GPS metadata."""
        return {
            "version_id": self._get_value(data, "GPSVersionID"),
            "latitude": self._get_value(data, "GPSLatitude"),
            "latitude_ref": self._get_value(data, "GPSLatitudeRef"),
            "longitude": self._get_value(data, "GPSLongitude"),
            "longitude_ref": self._get_value(data, "GPSLongitudeRef"),
            "altitude": self._get_value(data, "GPSAltitude"),
            "timestamp": self._get_value(data, "GPSTimeStamp"),
            "datestamp": self._get_value(data, "GPSDateStamp"),
            "processing_method": self._get_value(data, "GPSProcessingMethod"),
            "position_composite": self._get_value(data, "GPSPosition")
        }
    
    def _group_iptc(self, data: Dict) -> Dict[str, Any]:
        """Group IPTC metadata."""
        return {
            "keywords": self._get_value(data, "Keywords"),
            "caption": self._get_value(data, "Caption-Abstract"),
            "headline": self._get_value(data, "Headline"),
            "byline": self._get_value(data, "By-line"),
            "credit": self._get_value(data, "Credit"),
            "source": self._get_value(data, "Source"),
            "copyright_notice": self._get_value(data, "CopyrightNotice"),
            "city": self._get_value(data, "City"),
            "province_state": self._get_value(data, "Province-State"),
            "country_primary_location": self._get_value(data, "Country-PrimaryLocationName"),
            "country_code": self._get_value(data, "Country-PrimaryLocationCode"),
            "date_created": self._get_value(data, "DateCreated"),
            "urgency": self._get_value(data, "Urgency"),
            "object_name": self._get_value(data, "ObjectName"),
            "ai_system_used": self._get_value(data, "AISystemUsed"),
            "ai_prompt": self._get_value(data, "AIPromptInformation")
        }
    
    def _group_xmp(self, data: Dict) -> Dict[str, Any]:
        """Group XMP namespace metadata."""
        return {
            "dc_title": self._get_value(data, "Title"),
            "dc_creator": self._get_value(data, "Creator"),
            "dc_description": self._get_value(data, "Description"),
            "dc_subject": self._get_value(data, "Subject"),
            "dc_rights": self._get_value(data, "Rights"),
            "dc_format": self._get_value(data, "Format"),
            "dc_date": self._get_value(data, "Date"),
            "dc_type": self._get_value(data, "Type"),
            "xmp_creator_tool": self._get_value(data, "CreatorTool"),
            "xmp_create_date": self._get_value(data, "CreateDate"),
            "xmp_modify_date": self._get_value(data, "ModifyDate"),
            "xmp_rights_marked": self._get_value(data, "Marked"),
            "xmp_rights_web_statement": self._get_value(data, "WebStatement"),
            "xmpmm_document_id": self._get_value(data, "DocumentID"),
            "xmpmm_instance_id": self._get_value(data, "InstanceID"),
            "photoshop_headline": self._get_value(data, "Headline"),
            "photoshop_color_mode": self._get_value(data, "ColorMode")
        }
    
    def _group_icc(self, data: Dict) -> Dict[str, Any]:
        """Group ICC profile metadata."""
        return {
            "profile_version": self._get_value(data, "ProfileVersion"),
            "profile_class": self._get_value(data, "ProfileClass"),
            "color_space": self._get_value(data, "ColorSpaceData"),
            "connection_space": self._get_value(data, "ProfileConnectionSpace"),
            "profile_datetime": self._get_value(data, "ProfileDateTime"),
            "profile_signature": self._get_value(data, "ProfileFileSignature"),
            "primary_platform": self._get_value(data, "PrimaryPlatform"),
            "rendering_intent": self._get_value(data, "RenderingIntent"),
            "profile_creator": self._get_value(data, "ProfileCreator"),
            "description": self._get_value(data, "ProfileDescription"),
            "copyright": self._get_value(data, "ProfileCopyright"),
            "media_white_point": self._get_value(data, "MediaWhitePoint"),
            "red_matrix": self._get_value(data, "RedMatrixColumn"),
            "green_matrix": self._get_value(data, "GreenMatrixColumn"),
            "blue_matrix": self._get_value(data, "BlueMatrixColumn")
        }
    
    def _group_makernotes(self, data: Dict) -> Dict[str, Any]:
        """Group vendor-specific MakerNotes."""
        makernote = {}
        
        if any(k.startswith("Canon") for k in data.keys()):
            makernote["vendor"] = "Canon"
            makernote["shutter_count"] = self._get_value(data, "ShutterCount")
        elif any(k.startswith("Nikon") for k in data.keys()):
            makernote["vendor"] = "Nikon"
            makernote["shutter_count"] = self._get_value(data, "ShutterCount")
        elif any(k.startswith("Sony") for k in data.keys()):
            makernote["vendor"] = "Sony"
            makernote["shutter_count"] = self._get_value(data, "ShutterCount")
        
        return makernote
    
    def _normalize_gps(self, data: Dict) -> Optional[Dict[str, float]]:
        """Normalize GPS coordinates to decimal degrees."""
        lat = self._get_value(data, "GPSLatitude")
        lat_ref = self._get_value(data, "GPSLatitudeRef") or "N"
        lon = self._get_value(data, "GPSLongitude")
        lon_ref = self._get_value(data, "GPSLongitudeRef") or "E"
        
        if not lat or not lon:
            return None
        
        def parse_dms(dms_str):
            if not dms_str:
                return None
            match = re.match(r"(\d+)\s*deg\s+(\d+)'([^'\"]+)\"?", str(dms_str))
            if match:
                deg = float(match.group(1))
                min = float(match.group(2))
                sec = float(match.group(3))
                return deg + min / 60 + sec / 3600
            return None
        
        lat_decimal = parse_dms(lat)
        lon_decimal = parse_dms(lon)
        
        if lat_decimal is None or lon_decimal is None:
            return None
        
        if lat_ref in ["S", "W"]:
            lat_decimal = -lat_decimal
        if lon_ref in ["S", "W"]:
            lon_decimal = -lon_decimal
        
        alt = self._get_value(data, "GPSAltitude")
        altitude = None
        if alt:
            try:
                altitude = float(str(alt).replace(" m", ""))
            except:
                pass
        
        return {
            "latitude": round(lat_decimal, 6),
            "longitude": round(lon_decimal, 6),
            "altitude": altitude
        }
    
    def _normalize_datetime(self, data: Dict) -> Optional[str]:
        """Normalize EXIF datetime to ISO 8601."""
        dt = self._get_value(data, "DateTimeOriginal") or self._get_value(data, "DateTime")
        if not dt:
            return None
        
        try:
            dt_obj = datetime.strptime(str(dt), "%Y:%m:%d %H:%M:%S")
            return dt_obj.isoformat() + "Z"
        except ValueError:
            return None
    
    def _normalize_rationals(self, data: Dict) -> Dict[str, float]:
        """Normalize rational numbers."""
        rationals = {}
        
        et = self._get_value(data, "ExposureTime")
        if et:
            et_str = str(et)
            if "/" in et_str:
                parts = et_str.split("/")
                rationals["exposure_time_seconds"] = float(parts[0]) / float(parts[1])
            else:
                rationals["exposure_time_seconds"] = float(et_str)
        
        fnumber = self._get_value(data, "FNumber")
        if fnumber:
            rationals["f_number"] = float(fnumber)
        
        fl = self._get_value(data, "FocalLength")
        if fl:
            fl_str = str(fl)
            if "/" in fl_str:
                parts = fl_str.split("/")
                rationals["focal_length_mm"] = float(parts[0]) / float(parts[1])
            else:
                rationals["focal_length_mm"] = float(fl_str)
        
        return rationals
    
    def _apply_redaction(self, result: Dict) -> Dict:
        """Apply sensitivity-based redaction to extracted metadata."""
        redaction_log = []
        
        for surface_name, surface_data in result.get("surfaces", {}).items():
            if not isinstance(surface_data, dict):
                continue
            
            redacted_surface = {}
            for key, value in surface_data.items():
                if value is None:
                    continue
                
                should_redact = False
                
                for pattern in self.SENSITIVITY_HIGH:
                    if pattern in key.lower():
                        should_redact = True
                        break
                
                if not should_redact and self.product_mode == "extract+redact":
                    for pattern in self.SENSITIVITY_MODERATE:
                        if pattern in key.lower():
                            should_redact = True
                            break
                
                if should_redact:
                    redaction_log.append(f"Redacted: {surface_name}.{key}")
                    redacted_surface[key] = {"redacted": True, "original_type": type(value).__name__}
                else:
                    redacted_surface[key] = value
            
            result["surfaces"][surface_name] = redacted_surface
        
        result["redaction_log"] = redaction_log
        result["redaction_applied"] = len(redaction_log) > 0
        
        return result
    
    def _extract_exifread(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract EXIF using exifread (fallback)."""
        if not EXIFREAD_AVAILABLE:
            return None
        
        try:
            with open(filepath, "rb") as f:
                tags = exifread.process_file(f, details=False)
            
            if not tags:
                return None
            
            exif = {}
            for tag_name, tag_value in tags.items():
                if tag_name.startswith('JPEGThumbnail'):
                    continue
                
                if hasattr(tag_value, 'printable'):
                    exif[tag_name] = tag_value.printable
                else:
                    exif[tag_name] = str(tag_value)
            
            return exif
        
        except Exception as e:
            logger.warning(f"exifread extraction error: {e}")
            return None
    
    def _extract_iptc(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract IPTC using iptcinfo3 (fallback)."""
        if not IPTC_AVAILABLE:
            return None
        
        ext = Path(filepath).suffix.lower()
        if ext not in {".jpg", ".jpeg", ".tif", ".tiff"}:
            return None
        
        try:
            iptc_info = iptcinfo3.IPTCInfo(filepath)
            if not iptc_info:
                return None
            
            iptc = {}
            for key, value in iptc_info._data.items():
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-8', errors='ignore')
                    except:
                        value = str(value)
                iptc[key] = value
            
            return iptc if iptc else None
        
        except Exception as e:
            logger.warning(f"IPTC extraction error: {e}")
            return None
    
    def _extract_pil(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract basic metadata using PIL (fallback)."""
        if not PIL_AVAILABLE:
            return None
        
        try:
            with Image.open(filepath) as img:
                pil_data = {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "has_transparency": img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                }
                
                if hasattr(img, '_getexif') and img._getexif():
                    exif = {}
                    for tag, value in img._getexif().items():
                        tag_name = ExifTags.TAGS.get(tag, tag)
                        exif[tag_name] = str(value)
                    if exif:
                        pil_data["basic_exif"] = exif
                
                return pil_data
        
        except Exception as e:
            logger.warning(f"PIL extraction error: {e}")
            return None
    
    def get_extraction_info(self) -> Dict[str, Any]:
        """Get information about this extractor."""
        return {
            "name": self.name,
            "supported_formats": self.supported_formats,
            "version": "2.0.0",
            "exiftool_available": EXIFTOOL_AVAILABLE,
            "exifread_available": EXIFREAD_AVAILABLE,
            "iptc_available": IPTC_AVAILABLE,
            "pil_available": PIL_AVAILABLE
        }


class BaseEngineEnhancedImageExtractor(BaseExtractor):
    """
    Wrapper that integrates EnhancedImageExtractor with BaseExtractor interface.
    Used when running within the MetaExtract engine.
    """
    
    def __init__(self, redact_sensitive: bool = True, product_mode: str = "extract+redact"):
        """Initialize with BaseExtractor interface."""
        super().__init__(
            name="EnhancedImageExtractor",
            supported_formats=EnhancedImageExtractor.SUPPORTED_FORMATS
        )
        self._extractor = EnhancedImageExtractor(
            redact_sensitive=redact_sensitive,
            product_mode=product_mode,
            name="EnhancedImageExtractor"
        )
    
    def _extract_metadata(self, context: ExtractionContext) -> Dict[str, Any]:
        """Extract metadata using the enhanced extractor."""
        return self._extractor.extract(context.filepath)
    
    def get_extraction_info(self) -> Dict[str, Any]:
        """Get extractor information."""
        return self._extractor.get_extraction_info()


def extract_image_metadata(filepath: str, redact_sensitive: bool = True, product_mode: str = "extract+redact") -> Dict[str, Any]:
    """
    Convenience function for image metadata extraction.
    
    Args:
        filepath: Path to the image file
        redact_sensitive: Whether to redact sensitive fields
        product_mode: extract-only, extract+redact, or extract+index
        
    Returns:
        Dictionary containing extracted and normalized metadata
    """
    extractor = EnhancedImageExtractor(
        redact_sensitive=redact_sensitive,
        product_mode=product_mode
    )
    return extractor.extract(filepath)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: enhanced_image_extractor.py <image_file> [redact=true/false]")
        sys.exit(1)
    
    filepath = sys.argv[1]
    redact = sys.argv[2].lower() != "false" if len(sys.argv) > 2 else True
    
    result = extract_image_metadata(filepath, redact_sensitive=redact)
    print(json.dumps(result, indent=2, default=str))
