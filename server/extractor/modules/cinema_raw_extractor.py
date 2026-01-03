#!/usr/bin/env python3
"""
CinemaDNG and ARRI RAW Metadata Extractor
Extracts comprehensive metadata from CinemaDNG and ARRI RAW formats.
"""

import logging
import struct
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


ARRI_SIGNATURE = b'ARRI'
CINEMADNG_SIGNATURE = b'MM\x00*'


ARRI_PRODUCT_IDS = {
    0x1845: 'ALEXA',
    0x1846: 'ALEXA Mini',
    0x1847: 'ALEXA 65',
    0x1848: 'ALEXA LF',
    0x1849: 'ALEXA Mini LF',
    0x1850: 'ARRI Signature Prime',
}


class CinemaDNGExtractor:
    """
    Comprehensive CinemaDNG metadata extractor.
    Supports Adobe CinemaDNG format with TIFF-based container.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file_data: Optional[bytes] = None
        self.is_valid_cinematadng = False
        self.dng_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Main entry point - parse CinemaDNG file"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            with open(self.filepath, 'rb') as f:
                self.file_data = f.read()
            
            if len(self.file_data) < 8:
                return {"error": "File too small", "success": False}
            
            header = self.file_data[:8]
            if header[:4] == CINEMADNG_SIGNATURE[:4]:
                self.is_valid_cinematadng = True
                self._parse_tiff_header()
            else:
                return {"error": "Not a valid CinemaDNG file", "success": False}
            
            self._build_result()
            return self.dng_info
            
        except Exception as e:
            logger.error(f"Error parsing CinemaDNG: {e}")
            return {"error": str(e), "success": False}
    
    def _parse_tiff_header(self):
        """Parse TIFF header for DNG tags"""
        if not self.file_data or len(self.file_data) < 8:
            return
        
        byte_order = 'little' if self.file_data[:2] == b'II' else 'big'
        ifd_offset = struct.unpack(byte_order + 'I', self.file_data[4:8])[0]
        
        self.dng_info["byte_order"] = byte_order
        self.dng_info["ifd_offset"] = ifd_offset
        self.dng_info["is_cinematadng"] = True
        
        self._parse_dng_tags(ifd_offset, byte_order)
    
    def _parse_dng_tags(self, offset: int, byte_order: str):
        """Parse DNG-specific TIFF tags"""
        if offset + 2 > len(self.file_data):
            return
        
        num_entries = struct.unpack(byte_order + 'H', self.file_data[offset:offset + 2])[0]
        
        for i in range(num_entries):
            entry_offset = offset + 2 + i * 12
            if entry_offset + 12 > len(self.file_data):
                break
            
            tag = struct.unpack(byte_order + 'H', self.file_data[entry_offset:entry_offset + 2])[0]
            tag_type = struct.unpack(byte_order + 'H', self.file_data[entry_offset + 2:entry_offset + 4])[0]
            count = struct.unpack(byte_order + 'I', self.file_data[entry_offset + 4:entry_offset + 8])[0]
            
            self._process_dng_tag(tag, tag_type, count, entry_offset, byte_order)
    
    def _process_dng_tag(self, tag: int, tag_type: int, count: int, offset: int, byte_order: str):
        """Process individual DNG tag"""
        dng_tags = {
            50706: 'DNGVersion',
            50707: 'DNGBackwardVersion',
            50708: 'UniqueCameraModel',
            50709: 'LocalizedCameraModel',
            50710: 'ColorMatrix1',
            50711: 'ColorMatrix2',
            50712: 'CalibrationIlluminant1',
            50713: 'CalibrationIlluminant2',
            50714: 'ForwardMatrix1',
            50715: 'ForwardMatrix2',
            50717: 'ActiveArea',
            50718: 'MaskedAreas',
            50720: 'AsShotNeutral',
            50721: 'AsShotWhiteXY',
            50722: 'BaselineExposure',
            50723: 'BaselineNoise',
            50724: 'BaselineSharpness',
            50727: 'BayerGreenSplit',
            50728: 'ChromaBlurRadius',
            50729: 'CFARepeatPatternDim',
            50730: 'CFAPattern',
            50731: 'LinearizationTable',
            50732: 'BlackLevelRepeatDim',
            50733: 'BlackLevel',
            50734: 'BlackLevelDeltaH',
            50735: 'BlackLevelDeltaV',
            50736: 'WhiteLevel',
            50737: 'DefaultScale',
            50738: 'DefaultCropOrigin',
            50739: 'DefaultCropSize',
            50740: 'ColorMatrix1',
            50741: 'ColorMatrix2',
            50778: 'OpcodeList1',
            50779: 'OpcodeList2',
            50780: 'OpcodeList3',
            50827: 'RawImageUniqueID',
            50828: 'OriginalRawFileName',
            50830: 'ProfileLookTableDims',
            50831: 'ProfileLookTableData',
            50931: 'DefaultUserCrop',
            50934: 'NEFProperties',
            50966: 'DNGPrivateData',
            50967: 'MakerNoteSafety',
            51041: 'GainMap',
            51042: 'GainMapDesc',
            51043: 'WarpRectilinear',
            51044: 'WarpFisheye',
            51045: 'WarpFisheyeDistortion',
        }
        
        tag_name = dng_tags.get(tag, f'Tag_{tag}')
        self.dng_info[f"dng_{tag_name.lower()}"] = True


class ARRIExtractor:
    """
    Comprehensive ARRI RAW metadata extractor.
    Supports ALEXA, ALEXA Mini, ALEXA 65, ALEXA LF, and ALEXI Signature formats.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file_data: Optional[bytes] = None
        self.is_valid_arri = False
        self.arri_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Main entry point - parse ARRI file"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            file_size = file_path.stat().st_size
            with open(self.filepath, 'rb') as f:
                header = f.read(4096)
            
            if len(header) < 8:
                return {"error": "File too small", "success": False}
            
            if header[:4] != ARRI_SIGNATURE:
                return {"error": "Not a valid ARRI file", "success": False}
            
            self.is_valid_arri = True
            self._parse_arri_header(header)
            self._build_result()
            
            return self.arri_info
            
        except Exception as e:
            logger.error(f"Error parsing ARRI file: {e}")
            return {"error": str(e), "success": False}
    
    def _parse_arri_header(self, header: bytes):
        """Parse ARRI-specific header metadata"""
        self.arri_info["is_arri_raw"] = True
        
        offset = 4
        
        if offset + 4 <= len(header):
            product_id = struct.unpack('>H', header[offset:offset + 2])[0]
            product_id2 = struct.unpack('>H', header[offset + 2:offset + 4])[0] if offset + 4 <= len(header) else 0
            
            self.arri_info["product_id"] = f"0x{product_id:04X}"
            self.arri_info["product_id_secondary"] = f"0x{product_id2:04X}"
            
            camera_name = ARRI_PRODUCT_IDS.get(product_id, 'Unknown ARRI Camera')
            self.arri_info["camera_model"] = camera_name
        
        offset = 24
        if offset + 4 <= len(header):
            width = struct.unpack('>I', header[offset:offset + 4])[0]
            height = struct.unpack('>I', header[offset + 4:offset + 8])[0] if offset + 8 <= len(header) else 0
            
            self.arri_info["image_width"] = width
            self.arri_info["image_height"] = height
        
        offset = 40
        if offset + 4 <= len(header):
            frame_rate = struct.unpack('>f', header[offset:offset + 4])[0]
            self.arri_info["frame_rate"] = round(frame_rate, 2)
        
        offset = 56
        if offset + 8 <= len(header):
            exposure_time = struct.unpack('>d', header[offset:offset + 8])[0]
            self.arri_info["exposure_time_seconds"] = exposure_time
        
        offset = 64
        if offset + 4 <= len(header):
            iso_value = struct.unpack('>f', header[offset:offset + 4])[0]
            self.arri_info["iso_speed"] = int(iso_value)
        
        offset = 80
        if offset + 4 <= len(header):
            sensor_name_length = struct.unpack('>I', header[offset:offset + 4])[0]
            if offset + 4 + sensor_name_length <= len(header):
                sensor_name = header[offset + 4:offset + 4 + sensor_name_length].decode('utf-8', errors='replace')
                self.arri_info["sensor_name"] = sensor_name
        
        offset = 104
        if offset + 4 <= len(header):
            lens_name_length = struct.unpack('>I', header[offset:offset + 4])[0]
            if offset + 4 + lens_name_length <= len(header):
                lens_name = header[offset + 4:offset + 4 + lens_name_length].decode('utf-8', errors='replace')
                self.arri_info["lens_name"] = lens_name
        
        self.arri_info["color_depth"] = 16
        self.arri_info["compression"] = 'Uncompressed or Lossless'
    
    def _build_result(self):
        """Build the final result dictionary"""
        self.arri_info["is_valid_arri"] = self.is_valid_arri
        
        if "image_width" in self.arri_info and "image_height" in self.arri_info:
            w = self.arri_info["image_width"]
            h = self.arri_info["image_height"]
            if h > 0:
                self.arri_info["aspect_ratio"] = round(w / h, 4)
            self.arri_info["megapixels"] = round(w * h / 1000000, 2)
        
        self.arri_info["success"] = True


class CinemaRAWExtractor:
    """Unified extractor for various cinema RAW formats"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        
    def parse(self) -> Dict[str, Any]:
        """Detect and parse cinema RAW format"""
        try:
            with open(self.filepath, 'rb') as f:
                header = f.read(16)
            
            if len(header) < 4:
                return {"error": "File too small", "success": False}
            
            if header[:4] == ARRI_SIGNATURE:
                from .cinema_raw_extractor import ARRIExtractor
                extractor = ARRIExtractor(self.filepath)
                return extractor.parse()
            
            elif header[:2] in (b'II', b'MM'):
                from .cinema_raw_extractor import CinemaDNGExtractor
                extractor = CinemaDNGExtractor(self.filepath)
                return extractor.parse()
            
            else:
                return {"error": "Unknown cinema RAW format", "success": False}
                
        except Exception as e:
            logger.error(f"Error parsing cinema RAW: {e}")
            return {"error": str(e), "success": False}
