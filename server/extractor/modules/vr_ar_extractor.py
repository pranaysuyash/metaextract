#!/usr/bin/env python3
"""
VR/AR and Stereoscopic Image Metadata Extractor
Extracts metadata from VR, AR, 360°, and stereoscopic image formats.
"""

import logging
import json
import struct
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class StereoscopicExtractor:
    """
    Stereoscopic 3D image metadata extractor.
    Supports side-by-side, anaglyph, and other 3D formats.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.stereo_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse stereoscopic image metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            result = {
                "is_stereoscopic": False,
                "stereo_type": None,
                "left_frame": {},
                "right_frame": {},
                "parallax": {},
            }
            
            with open(self.filepath, 'rb') as f:
                header = f.read(1024)
            
            result["file_size"] = len(header)
            
            if b'MPO' in header[:20]:
                result["is_stereoscopic"] = True
                result["stereo_type"] = "Multi-Picture Object"
                result.update(self._parse_mpo(header))
            
            elif b'JP' in header[:2] and b'F9' in header[2:4]:
                result["is_stereoscopic"] = True
                result["stereo_type"] = "JPEG Stereo"
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"Error parsing stereoscopic image: {e}")
            return {"error": str(e), "success": False}
    
    def _parse_mpo(self, header: bytes) -> Dict[str, Any]:
        """Parse Multi-Picture Object header"""
        result = {}
        
        if len(header) >= 100:
            if b'MP' in header[20:40]:
                result["has_mp_header"] = True
        
        result["image_count"] = 0
        result["images"] = []
        
        offset = 0
        while offset < len(header) - 16:
            if header[offset:offset + 2] == b'\xff\xd8':
                result["image_count"] += 1
                offset += 2
            else:
                offset += 1
        
        return result


class VRExtractor:
    """
    VR (Virtual Reality) image metadata extractor.
    Supports 360° equirectangular, cubemap, and other VR formats.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.vr_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse VR/360° image metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            with open(self.filepath, 'rb') as f:
                header = f.read(2048)
            
            result = {
                "is_vr_image": False,
                "projection_type": None,
                "stereo_mode": None,
                "viewing_hint": None,
            }
            
            xmp_data = self._extract_xmp(header)
            if xmp_data:
                result.update(self._parse_vr_xmp(xmp_data))
            
            if b'Photo Sphere' in header or b'@PhotoSphere' in header:
                result["is_vr_image"] = True
                result["projection_type"] = "equirectangular"
            
            exif_data = self._extract_exif(header)
            if exif_data:
                result.update(self._parse_vr_exif(exif_data))
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"Error parsing VR image: {e}")
            return {"error": str(e), "success": False}
    
    def _extract_xmp(self, data: bytes) -> Optional[str]:
        """Extract XMP data from image"""
        try:
            xmp_start = data.find(b'<x:xmpmeta')
            if xmp_start == -1:
                xmp_start = data.find(b'x:xmpmeta')
            if xmp_start == -1:
                return None
            
            xmp_end = data.find(b'</x:xmpmeta>', xmp_start)
            if xmp_end == -1:
                xmp_end = data.find(b'</rdf:RDF>', xmp_start)
            
            if xmp_end > xmp_start:
                return data[xmp_start:xmp_end + 10].decode('utf-8', errors='replace')
            
            return None
        except Exception:
            return None
    
    def _extract_exif(self, data: bytes) -> Dict[str, Any]:
        """Extract basic EXIF data"""
        result = {}
        
        exif_offset = data.find(b'Exif\\x00\\x00')
        if exif_offset == -1:
            exif_offset = data.find(b'Exif\x00\x00')
        
        if exif_offset > 0 and exif_offset < len(data) - 100:
            result["has_exif"] = True
        
        return result
    
    def _parse_vr_xmp(self, xmp: str) -> Dict[str, Any]:
        """Parse VR-specific XMP metadata"""
        result = {"xmp_vr_data": True}
        
        if 'GPano:' in xmp or 'gphoto:' in xmp.lower():
            result["has_gpano"] = True
            
            if 'CroppedAreaImageWidth' in xmp:
                result["cropped_width"] = True
            if 'CroppedAreaImageHeight' in xmp:
                result["cropped_height"] = True
            if 'FullPanoWidth' in xmp:
                result["full_pano_width"] = True
            if 'FullPanoHeight' in xmp:
                result["full_pano_height"] = True
        
        if 'stereo' in xmp.lower():
            result["is_stereo_vr"] = True
            result["stereo_mode"] = "multi-view"
        
        return result
    
    def _parse_vr_exif(self, exif: Dict) -> Dict[str, Any]:
        """Parse VR-specific EXIF data"""
        result = {"exif_vr_data": True}
        
        if exif.get("has_exif"):
            result["has_vr_exif"] = True
        
        return result


class ARExtractor:
    """
    AR (Augmented Reality) metadata extractor.
    Supports AR-specific formats and markers.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.ar_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse AR image metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            result = {
                "is_ar_content": False,
                "ar_type": None,
                "tracking_type": None,
                "anchor_type": None,
            }
            
            with open(self.filepath, 'rb') as f:
                header = f.read(1024)
            
            if b'AR' in header[:100] or b'ARKit' in header[:100]:
                result["is_ar_content"] = True
                result["ar_type"] = "AR Framework"
            
            if b'Vuforia' in header[:100] or b'VUFO' in header[:100]:
                result["is_ar_content"] = True
                result["ar_type"] = "Vuforia"
                result["tracking_type"] = "marker-based"
            
            if b'ARCore' in header[:100] or b'AR' in header[:100]:
                result["is_ar_content"] = True
                result["ar_type"] = "ARCore"
                result["tracking_type"] = "markerless"
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"Error parsing AR content: {e}")
            return {"error": str(e), "success": False}


class CubemapExtractor:
    """
    Cubemap/environment map metadata extractor.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        
    def parse(self) -> Dict[str, Any]:
        """Parse cubemap metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            result = {
                "is_cubemap": False,
                "face_count": 0,
                "projection_type": "cubemap",
                "faces": [],
            }
            
            suffixes = ['_px', '_nx', '_py', '_ny', '_pz', '_nz']
            base_name = file_path.stem
            
            for suffix in suffixes:
                face_path = file_path.parent / f"{base_name}{suffix}{file_path.suffix}"
                if face_path.exists():
                    result["faces"].append(face_path.name)
            
            result["face_count"] = len(result["faces"])
            result["is_cubemap"] = result["face_count"] == 6
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"Error parsing cubemap: {e}")
            return {"error": str(e), "success": False}


class LightFieldExtractor:
    """
    Light field camera metadata extractor.
    Supports Lytro, Raytrix, and other light field formats.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.lf_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse light field image metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            result = {
                "is_light_field": False,
                "microlens_array": {},
                "refocus_range": {},
                "aperture_settings": {},
            }
            
            with open(self.filepath, 'rb') as f:
                header = f.read(4096)
            
            if b'Lytro' in header[:100] or b'LYTRO' in header[:100]:
                result["is_light_field"] = True
                result["light_field_type"] = "Lytro"
                result.update(self._parse_lytro_header(header))
            
            elif b'Raytrix' in header[:100] or b'RAYTRIX' in header[:100]:
                result["is_light_field"] = True
                result["light_field_type"] = "Raytrix"
            
            elif b'REFOCUS' in header or b'MICRO' in header:
                result["is_light_field"] = True
                result["light_field_type"] = "Generic"
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"Error parsing light field: {e}")
            return {"error": str(e), "success": False}
    
    def _parse_lytro_header(self, header: bytes) -> Dict[str, Any]:
        """Parse Lytro-specific header"""
        result = {}
        
        try:
            if b'micro' in header.lower() or b'Micro' in header:
                result["has_microlens_info"] = True
            
            if b'raw' in header.lower() or b'RAW' in header:
                result["raw_format"] = True
            
            result["decoded"] = False
            result["requires_decoding"] = True
            
        except Exception:
            pass
        
        return result


class OmnidirectionalMediaExtractor:
    """
    Omnidirectional media (360° video/image) metadata extractor.
    Supports omnidirectional formats and projections.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.omni_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse omnidirectional media metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            result = {
                "is_omnidirectional": False,
                "projection": None,
                "horizontal_fov": 360,
                "vertical_fov": 180,
                "interpupillary_distance": 0.065,
            }
            
            with open(self.filepath, 'rb') as f:
                header = f.read(2048)
            
            if b'equirect' in header.lower() or b'EQUIRECT' in header:
                result["is_omnidirectional"] = True
                result["projection"] = "equirectangular"
            
            elif b'cubemap' in header.lower() or b'CUBEMAP' in header:
                result["is_omnidirectional"] = True
                result["projection"] = "cubemap"
            
            elif b'fisheye' in header.lower() or b'FISHEYE' in header:
                result["is_omnidirectional"] = True
                result["projection"] = "fisheye"
            
            elif b' pyramidal' in header.lower() or b'PYRAMIDAL' in header:
                result["is_omnidirectional"] = True
                result["projection"] = "pyramidal"
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"Error parsing omnidirectional media: {e}")
            return {"error": str(e), "success": False}
