"""
Image metadata extractor for MetaExtract.

Specialized extractor for image file formats including JPEG, PNG, TIFF,
WebP, and other image formats. Handles EXIF, IPTC, XMP, ICC profile,
and other image-specific metadata.
"""

import logging
import os
import traceback
from pathlib import Path
from typing import Any, Dict, Optional, List
import json
import subprocess
import tempfile
from datetime import datetime

from ..core.base_engine import BaseExtractor, ExtractionContext, ExtractionResult, ExtractionStatus

logger = logging.getLogger(__name__)

# Availability flags for optional libraries
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

# XMP support is complex and requires exempi library
# For now, we'll disable XMP extraction and can add it back later
XMP_AVAILABLE = False

# Global flag for exempi availability
_EXEMPI_AVAILABLE = None


class ImageExtractor(BaseExtractor):
    """
    Specialized extractor for image file formats.
    
    Supports JPEG, PNG, TIFF, WebP, and other common image formats.
    Extracts EXIF, IPTC, XMP, ICC profile, and other image metadata.
    """
    
    def __init__(self):
        """Initialize the image extractor."""
        supported_formats = [
            '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.gif', '.bmp',
            '.webp', '.svg', '.heic', '.heif', '.raw', '.cr2', '.nef',
            '.arw', '.dng', '.orf', '.rw2', '.pef', '.x3f'
        ]
        super().__init__("image_extractor", supported_formats)
        self.logger = logging.getLogger(__name__)
    
    def _extract_metadata(self, context: ExtractionContext) -> Dict[str, Any]:
        """
        Extract metadata from an image file.
        
        Args:
            context: Extraction context containing file information
            
        Returns:
            Dictionary containing extracted image metadata
        """
        filepath = context.filepath
        metadata = {}
        
        try:
            # Basic file information
            metadata["file_info"] = self._extract_file_info(filepath)
            
            # EXIF metadata
            if EXIFREAD_AVAILABLE:
                try:
                    exif_data = self._extract_exif_metadata(filepath)
                    if exif_data:
                        metadata["exif"] = exif_data
                except Exception as e:
                    self.logger.warning(f"EXIF extraction failed for {filepath}: {e}")
            
            # IPTC metadata
            if IPTC_AVAILABLE:
                try:
                    iptc_data = self._extract_iptc_metadata(filepath)
                    if iptc_data:
                        metadata["iptc"] = iptc_data
                except Exception as e:
                    self.logger.warning(f"IPTC extraction failed for {filepath}: {e}")
            
            # XMP metadata
            if XMP_AVAILABLE:
                try:
                    xmp_data = self._extract_xmp_metadata(filepath)
                    if xmp_data:
                        metadata["xmp"] = xmp_data
                except Exception as e:
                    self.logger.warning(f"XMP extraction failed for {filepath}: {e}")
            
            # GPS metadata
            if EXIFREAD_AVAILABLE:
                try:
                    gps_data = self._extract_gps_metadata(filepath)
                    if gps_data:
                        metadata["gps"] = gps_data
                except Exception as e:
                    self.logger.warning(f"GPS extraction failed for {filepath}: {e}")
            
            # ICC profile metadata
            try:
                icc_data = self._extract_icc_metadata(filepath)
                if icc_data:
                    metadata["icc_profile"] = icc_data
            except Exception as e:
                self.logger.warning(f"ICC profile extraction failed for {filepath}: {e}")
            
            # PIL metadata (as fallback)
            if PIL_AVAILABLE:
                try:
                    pil_data = self._extract_pil_metadata(filepath)
                    if pil_data:
                        metadata["pil"] = pil_data
                except Exception as e:
                    self.logger.warning(f"PIL extraction failed for {filepath}: {e}")
            
            # Add extraction statistics
            metadata["extraction_stats"] = {
                "exif_available": EXIFREAD_AVAILABLE,
                "iptc_available": IPTC_AVAILABLE,
                "xmp_available": XMP_AVAILABLE,
                "pil_available": PIL_AVAILABLE
            }
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Image extraction failed for {filepath}: {e}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _extract_file_info(self, filepath: str) -> Dict[str, Any]:
        """Extract basic file information."""
        try:
            stat_info = os.stat(filepath)
            path = Path(filepath)
            
            # Get creation time (platform dependent)
            if hasattr(stat_info, "st_birthtime"):
                created = stat_info.st_birthtime
            else:
                created = stat_info.st_ctime
            
            return {
                "filename": path.name,
                "file_size_bytes": stat_info.st_size,
                "created_timestamp": created,
                "modified_timestamp": stat_info.st_mtime,
                "file_extension": path.suffix.lower(),
                "absolute_path": str(path.absolute())
            }
        except Exception as e:
            self.logger.warning(f"Could not extract file info for {filepath}: {e}")
            return {}
    
    def _extract_exif_metadata(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract EXIF metadata using exifread."""
        if not EXIFREAD_AVAILABLE:
            return None
        
        try:
            with open(filepath, "rb") as f:
                tags = exifread.process_file(f, details=False)
            
            if not tags:
                return None
            
            exif_data = {}
            for tag_name, tag_value in tags.items():
                if tag_name.startswith('JPEGThumbnail'):
                    continue  # Skip binary thumbnail data
                
                # Convert tag value to string representation
                if hasattr(tag_value, 'printable'):
                    exif_data[tag_name] = str(tag_value.printable)
                else:
                    exif_data[tag_name] = str(tag_value)
            
            return exif_data if exif_data else None
            
        except Exception as e:
            self.logger.warning(f"EXIF extraction error for {filepath}: {e}")
            return None
    
    def _extract_iptc_metadata(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract IPTC metadata."""
        if not IPTC_AVAILABLE:
            return None
        
        ext = Path(filepath).suffix.lower()
        if ext not in {".jpg", ".jpeg", ".tif", ".tiff"}:
            return None  # IPTC is mainly in JPEG and TIFF
        
        try:
            iptc_info = iptcinfo3.IPTCInfo(filepath)
            if not iptc_info:
                return None
            
            iptc_data = {}
            for key, value in iptc_info._data.items():
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-8', errors='ignore')
                    except:
                        value = str(value)
                iptc_data[key] = value
            
            return iptc_data if iptc_data else None
            
        except Exception as e:
            self.logger.warning(f"IPTC extraction error for {filepath}: {e}")
            return None
    
    def _extract_xmp_metadata(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract XMP metadata."""
        # XMP extraction is complex and requires exempi library
        # For now, we'll skip it and can add it back later with proper implementation
        return None
    
    def _extract_gps_metadata(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract GPS metadata from EXIF."""
        if not EXIFREAD_AVAILABLE:
            return None
        
        try:
            with open(filepath, "rb") as f:
                tags = exifread.process_file(f, details=False)
            
            gps = {}
            
            # Extract GPS coordinates
            if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                lat_ref = str(tags.get('GPS GPSLatitudeRef', 'N'))
                lon_ref = str(tags.get('GPS GPSLongitudeRef', 'E'))
                
                lat = self._convert_gps_coords(tags['GPS GPSLatitude'], lat_ref)
                lon = self._convert_gps_coords(tags['GPS GPSLongitude'], lon_ref)
                
                if lat is not None and lon is not None:
                    gps["latitude"] = lat
                    gps["longitude"] = lon
            
            # Extract other GPS data
            gps_tags = {
                'GPS GPSAltitude': 'altitude',
                'GPS GPSDate': 'date',
                'GPS GPSTimeStamp': 'timestamp',
                'GPS GPSProcessingMethod': 'processing_method',
                'GPS GPSVersionID': 'version'
            }
            
            for exif_tag, gps_key in gps_tags.items():
                if exif_tag in tags:
                    gps[gps_key] = str(tags[exif_tag].printable if hasattr(tags[exif_tag], 'printable') else tags[exif_tag])
            
            return gps if gps else None
            
        except Exception as e:
            self.logger.warning(f"GPS extraction error for {filepath}: {e}")
            return None
    
    def _convert_gps_coords(self, gps_coords, ref: str) -> Optional[float]:
        """Convert GPS coordinates from EXIF format to decimal degrees."""
        try:
            if hasattr(gps_coords, 'values'):
                # Handle exifread coordinate format
                degrees, minutes, seconds = gps_coords.values
                decimal = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
                
                if ref in ['S', 'W']:
                    decimal = -decimal
                
                return decimal
            else:
                # Handle other formats
                coord_str = str(gps_coords)
                # Basic parsing - would need more sophisticated parsing for production
                return None
                
        except Exception as e:
            self.logger.warning(f"GPS coordinate conversion error: {e}")
            return None
    
    def _extract_icc_metadata(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract ICC profile metadata."""
        try:
            # This would require ICC profile parsing library
            # For now, return basic info if PIL is available
            if PIL_AVAILABLE:
                with Image.open(filepath) as img:
                    if hasattr(img, 'info') and 'icc_profile' in img.info:
                        icc_profile = img.info['icc_profile']
                        return {
                            "has_icc_profile": True,
                            "profile_size_bytes": len(icc_profile) if icc_profile else 0
                        }
            return None
        except Exception as e:
            self.logger.warning(f"ICC profile extraction error for {filepath}: {e}")
            return None
    
    def _extract_pil_metadata(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract metadata using PIL as fallback."""
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
                
                # Add basic EXIF if available
                if hasattr(img, '_getexif') and img._getexif():
                    exif = {}
                    for tag, value in img._getexif().items():
                        tag_name = Image.ExifTags.TAGS.get(tag, tag)
                        exif[tag_name] = str(value)
                    if exif:
                        pil_data["basic_exif"] = exif
                
                return pil_data
                
        except Exception as e:
            self.logger.warning(f"PIL extraction error for {filepath}: {e}")
            return None
    
    def get_extraction_info(self) -> Dict[str, Any]:
        """Get information about this extractor."""
        return {
            "name": self.name,
            "supported_formats": self.supported_formats,
            "capabilities": {
                "exif": EXIFREAD_AVAILABLE,
                "iptc": IPTC_AVAILABLE,
                "xmp": XMP_AVAILABLE,
                "gps": EXIFREAD_AVAILABLE,
                "icc_profile": PIL_AVAILABLE,
                "pil_fallback": PIL_AVAILABLE
            },
            "version": "1.0.0"
        }