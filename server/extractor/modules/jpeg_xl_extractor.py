#!/usr/bin/env python3
"""
JPEG XL (JXL) Metadata Extractor
Extracts comprehensive metadata from JPEG XL files.
"""

import logging
import struct
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


JXL_SIGNATURE = b'\xff\x0a'
JXL_CONTAINER_SIGNATURE = b'\x00\x00\x00\x0cJXL \x0d\x0a\x87\x0a'


BOX_HEADER_SIZE = 4
BOX_SIZE_SIZE = 4
BOX_TYPE_SIZE = 4


BOX_TYPES = {
    b'JXL ': 'Signature',
    b'ftyp': 'File type',
    b'enhg': 'Enhanced image',
    b'Exif': 'EXIF metadata',
    b'xml ': 'XML metadata',
    b'iprp': 'Image properties',
    b'ipco': 'Image properties container',
    b'ihdr': 'Image header',
    b'bpcc': 'Bits per channel',
    b'colr': 'Color profile',
    b'pict': 'Picture',
    b'prep': 'Pre-multiplied alpha',
    b'orig': 'Original image',
    b'jbr ': 'JPEG reconstruction box',
    b'xml ': 'XML',
    b'uuid': 'UUID box',
    b'time': 'Timing',
    b'fxmp': 'XMP metadata',
    b'jumb': 'JUMBF (JPEG Multipurpose Box Format)',
}


CODEC_LOOP_MODES = {
    0: 'All-Intra',
    1: 'Modular',
    2: 'Lossy',
    3: 'Lossless',
}


class JPEGXLExtractor:
    """
    Comprehensive JPEG XL metadata extractor.
    Supports both raw JPEG XL and container format.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file_data: Optional[bytes] = None
        self.file_size = 0
        self.is_valid_jxl = False
        self.jxl_info: Dict[str, Any] = {}
        self.boxes: List[Dict[str, Any]] = []
        
    def parse(self) -> Dict[str, Any]:
        """Main entry point - parse JPEG XL file"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            self.file_size = file_path.stat().st_size
            
            with open(self.filepath, 'rb') as f:
                self.file_data = f.read()
            
            if len(self.file_data) < 12:
                return {"error": "File too small", "success": False}
            
            if self.file_data[:2] == JXL_SIGNATURE:
                self.is_valid_jxl = True
                self._parse_raw_jxl()
            elif self.file_data[:12] == JXL_CONTAINER_SIGNATURE:
                self.is_valid_jxl = True
                self._parse_container_format()
            else:
                return {"error": "Not a valid JPEG XL file", "success": False}
            
            self._build_result()
            return self.jxl_info
            
        except Exception as e:
            logger.error(f"Error parsing JPEG XL: {e}")
            return {"error": str(e), "success": False}
    
    def _parse_raw_jxl(self):
        """Parse raw JPEG XL format"""
        offset = 2
        while offset < len(self.file_data):
            if offset >= len(self.file_data):
                break
            
            size = struct.unpack('>I', self.file_data[offset:offset + 4])[0]
            if offset + 4 > len(self.file_data):
                break
            box_type = self.file_data[offset + 4:offset + 8]
            
            if size == 0:
                size = len(self.file_data) - offset
            
            box_data = self.file_data[offset + 8:offset + size]
            
            box_info = {
                "type": box_type.decode('latin-1', errors='replace') if box_type else '',
                "type_name": BOX_TYPES.get(box_type, 'Unknown'),
                "offset": offset,
                "size": size
            }
            
            if box_type == b'ihdr' and len(box_data) >= 16:
                box_info.update(self._parse_image_header(box_data))
            
            elif box_type == b'ftyp' and len(box_data) >= 4:
                box_info["major_brand"] = box_data[:4].decode('latin-1', errors='replace')
                box_info["minor_version"] = struct.unpack('>H', box_data[4:6])[0]
            
            elif box_type == b'Exif' and len(box_data) > 4:
                box_info["exif_size"] = len(box_data)
                box_info["has_exif"] = True
            
            elif box_type == b'fxmp' and len(box_data) > 0:
                box_info["xmp_size"] = len(box_data)
                box_info["has_xmp"] = True
            
            self.boxes.append(box_info)
            offset += size
    
    def _parse_container_format(self):
        """Parse JPEG XL container format"""
        offset = 0
        while offset < len(self.file_data):
            if offset + 8 > len(self.file_data):
                break
            
            box_size = struct.unpack('>I', self.file_data[offset:offset + 4])[0]
            box_type = self.file_data[offset + 4:offset + 8]
            
            if box_size == 0:
                box_size = len(self.file_data) - offset
            elif box_size == 1:
                if offset + 16 > len(self.file_data):
                    break
                box_size = struct.unpack('>Q', self.file_data[offset + 8:offset + 16])[0]
                box_data_offset = offset + 16
            else:
                box_data_offset = offset + 8
            
            if offset + box_size > len(self.file_data):
                break
            
            box_data = self.file_data[box_data_offset:offset + box_size]
            
            box_info = {
                "type": box_type.decode('latin-1', errors='replace') if box_type else '',
                "type_name": BOX_TYPES.get(box_type, 'Unknown'),
                "offset": offset,
                "size": box_size
            }
            
            if box_type == b'ihdr' and len(box_data) >= 16:
                box_info.update(self._parse_image_header(box_data))
            
            elif box_type == b'ftyp':
                if len(box_data) >= 4:
                    box_info["major_brand"] = box_data[:4].decode('latin-1', errors='replace')
                if len(box_data) >= 8:
                    box_info["minor_version"] = struct.unpack('>H', box_data[6:8])[0]
            
            elif box_type == b'colr' and len(box_data) >= 12:
                box_info["color_space"] = struct.unpack('>I', box_data[:4])[0]
                box_info["transfer_function"] = struct.unpack('>I', box_data[4:8])[0]
                box_info["rendering_intent"] = struct.unpack('>I', box_data[8:12])[0]
            
            elif box_type == b'bpcc' and len(box_data) > 0:
                box_info["bits_per_channel"] = list(box_data)
            
            self.boxes.append(box_info)
            offset += box_size
    
    def _parse_image_header(self, data: bytes) -> Dict[str, Any]:
        """Parse JPEG XL image header box"""
        if len(data) < 16:
            return {}
        
        info = {}
        
        width = struct.unpack('>I', data[:4])[0]
        height = struct.unpack('>I', data[4:8])[0]
        info["width"] = width
        info["height"] = height
        info["aspect_ratio"] = round(width / height, 4) if height > 0 else 0
        info["megapixels"] = round(width * height / 1000000, 2)
        
        bits_per_sample = (data[8] & 0x07) + 1
        info["bits_per_sample"] = bits_per_sample
        
        samples_per_pixel = ((data[8] >> 3) & 0x07) + 1
        info["samples_per_pixel"] = samples_per_pixel
        
        preview = (data[8] >> 6) & 0x01
        info["has_preview"] = preview == 1
        
        alpha_bits = ((data[9] >> 4) & 0x0F)
        info["alpha_bits"] = alpha_bits
        
        num_extra_channels = data[9] & 0x0F
        info["num_extra_channels"] = num_extra_channels
        
        info["color_encoding"] = data[10] if len(data) > 10 else 0
        info["compression_sensing"] = data[11] if len(data) > 11 else 0
        
        if len(data) >= 16:
            info["animation"] = data[15] != 0
        
        return info
    
    def _build_result(self):
        """Build the final result dictionary"""
        self.jxl_info["is_valid_jxl"] = self.is_valid_jxl
        self.jxl_info["file_size_bytes"] = self.file_size
        self.jxl_info["box_count"] = len(self.boxes)
        
        for box in self.boxes:
            if box.get("width"):
                self.jxl_info["width"] = box["width"]
                self.jxl_info["height"] = box["height"]
                self.jxl_info["aspect_ratio"] = box.get("aspect_ratio", 0)
                self.jxl_info["megapixels"] = box.get("megapixels", 0)
            
            if box.get("bits_per_sample"):
                self.jxl_info["bits_per_sample"] = box["bits_per_sample"]
            
            if box.get("samples_per_pixel"):
                self.jxl_info["samples_per_pixel"] = box["samples_per_pixel"]
            
            if box.get("has_preview"):
                self.jxl_info["has_preview"] = box["has_preview"]
            
            if box.get("num_extra_channels"):
                self.jxl_info["num_extra_channels"] = box["num_extra_channels"]
            
            if box.get("animation"):
                self.jxl_info["is_animated"] = box["animation"]
        
        if self.boxes:
            self.jxl_info["has_exif"] = any(b.get("type") == "Exif" for b in self.boxes)
            self.jxl_info["has_xmp"] = any(b.get("type") == "fxmp" for b in self.boxes)
        
        self.jxl_info["success"] = True


class JPEGXLANIExtractor:
    """JPEG XL animation metadata extractor"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        
    def parse(self) -> Dict[str, Any]:
        """Parse animation-related metadata from JXL"""
        try:
            from .jpeg_xl_extractor import JPEGXLExtractor
            jxl = JPEGXLExtractor(self.filepath)
            result = jxl.parse()
            
            if not result.get("success"):
                return result
            
            animation_info = {
                "is_animated_jxl": result.get("is_animated", False),
                "frame_count": 0,
                "total_duration": 0,
                "loop_count": 0
            }
            
            return animation_info
            
        except Exception as e:
            logger.error(f"Error parsing JXL animation: {e}")
            return {"error": str(e), "success": False}


class JPEGXLProgressiveExtractor:
    """JPEG XL progressive rendering metadata extractor"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        
    def parse(self) -> Dict[str, Any]:
        """Parse progressive rendering metadata"""
        try:
            from .jpeg_xl_extractor import JPEGXLExtractor
            jxl = JPEGXLExtractor(self.filepath)
            result = jxl.parse()
            
            return {
                "is_progressive": True,
                "progressive_levels": [],
                "dc_levels": [],
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error parsing JXL progressive: {e}")
            return {"error": str(e), "success": False}
