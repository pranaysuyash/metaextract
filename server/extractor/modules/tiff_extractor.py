#!/usr/bin/env python3
"""
TIFF/IFD Metadata Extractor
Extracts comprehensive metadata from TIFF/IFD files.
"""

import logging
import struct
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


TIFF_SIGNATURES = [
    b'II\\x2a\\x00',
    b'MM\\x00\\x2a',
]

BYTE_ORDERS = {
    b'II': 'little',
    b'MM': 'big',
}

TAG_TYPES = {
    1: 'BYTE',
    2: 'ASCII',
    3: 'SHORT',
    4: 'LONG',
    5: 'RATIONAL',
    6: 'SBYTE',
    7: 'UNDEFINED',
    8: 'SSHORT',
    9: 'SLONG',
    10: 'SRATIONAL',
    11: 'FLOAT',
    12: 'DOUBLE',
}

COMPRESSION_CODES = {
    1: 'None (raw)',
    2: 'CCITT 1D',
    3: 'Group 3 Fax',
    4: 'Group 4 Fax',
    5: 'LZW',
    6: 'JPEG (old)',
    7: 'JPEG (new)',
    8: 'Deflate',
    9: 'JBIG',
    10: 'Deflate',
    32773: 'PackBits',
}

PHOTOMETRIC_INTERPRETATIONS = {
    0: 'WhiteIsZero',
    1: 'BlackIsZero',
    2: 'RGB',
    3: 'RGB Palette',
    4: 'Transparency Mask',
    5: 'CMYK',
    6: 'YCbCr',
    8: 'CIELab',
    9: 'ICCLab',
    10: 'ITULab',
    32803: 'CFA (Color Filter Array)',
    34892: 'Linear Raw',
}

EXIF_TAGS = {
    36864: 'ExifVersion',
    37121: 'ComponentsConfiguration',
    37122: 'CompressedBitsPerPixel',
    40960: 'FlashpixVersion',
    40961: 'ColorSpace',
    40962: 'PixelYDimension',
    40963: 'PixelXDimension',
    41483: 'SceneType',
    41484: 'ExposureProgram',
    41486: 'SpectralSensitivity',
    41492: 'ISOSpeedRatings',
    41493: 'OECF',
    41728: 'FileSource',
    41729: 'SceneType',
    41985: 'CustomRendered',
    41986: 'ExposureMode',
    41987: 'WhiteBalance',
    41988: 'DigitalZoomRatio',
    41989: 'FocalLengthIn35mmFilm',
    41990: 'SceneCaptureType',
    41991: 'GainControl',
    41992: 'Contrast',
    41993: 'Saturation',
    41994: 'Sharpness',
    41995: 'DeviceSettingDescription',
    42016: 'ImageUniqueID',
    42032: 'CameraOwnerName',
    42033: 'BodySerialNumber',
    42034: 'LensSpecification',
    42035: 'LensModel',
    42036: 'LensSerialNumber',
    42130: 'RawImageCenter',
    42240: 'WhitePoint',
    42241: 'PrimaryChromaticities',
    42932: 'YCbCrCoefficients',
    42933: 'YCbCrSubSampling',
    42934: 'YCbCrPositioning',
    42935: 'ReferenceBlackWhite',
    43000: 'Rating',
    43001: 'RatingPercent',
    43232: 'ImageDescription',
    43233: 'Artist',
    43234: 'Copyright',
    50000: 'XMP',
    50001: 'ImageNumber',
    50002: 'OwnerName',
    50003: 'CameraSerialNumber',
    50004: 'ImageSpecialType',
}


class TIFFExtractor:
    """
    Comprehensive TIFF/IFD metadata extractor.
    Supports TIFF, BigTIFF, and various IFD-based formats.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file_data: Optional[bytes] = None
        self.file_size = 0
        self.is_valid_tiff = False
        self.byte_order = 'little'
        self.tiff_info: Dict[str, Any] = {}
        self.ifds: List[Dict[str, Any]] = []
        
    def parse(self) -> Dict[str, Any]:
        """Main entry point - parse TIFF file"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            self.file_size = file_path.stat().st_size
            
            with open(self.filepath, 'rb') as f:
                self.file_data = f.read()
            
            if len(self.file_data) < 8:
                return {"error": "File too small", "success": False}
            
            header = self.file_data[:8]
            if header[:2] not in TIFF_SIGNATURES:
                return {"error": "Not a valid TIFF file", "success": False}
            
            self.is_valid_tiff = True
            self.byte_order = 'little' if header[:2] == b'II' else 'big'
            
            ifd_offset = struct.unpack(self.byte_order + 'I', header[4:8])[0]
            self._parse_ifd(ifd_offset)
            self._build_result()
            
            return self.tiff_info
            
        except Exception as e:
            logger.error(f"Error parsing TIFF: {e}")
            return {"error": str(e), "success": False}
    
    def _parse_ifd(self, offset: int, max_entries: int = 100) -> Optional[Dict[str, Any]]:
        """Parse an Image File Directory (IFD)"""
        if offset == 0 or offset >= len(self.file_data):
            return None
        
        try:
            num_entries = struct.unpack(self.byte_order + 'H', self.file_data[offset:offset + 2])[0]
            ifd = {
                "offset": offset,
                "num_entries": num_entries,
                "tags": {},
                "next_ifd_offset": 0
            }
            
            entry_offset = offset + 2
            for _ in range(min(num_entries, max_entries)):
                if entry_offset + 12 > len(self.file_data):
                    break
                
                tag = struct.unpack(self.byte_order + 'H', self.file_data[entry_offset:entry_offset + 2])[0]
                tag_type = struct.unpack(self.byte_order + 'H', self.file_data[entry_offset + 2:entry_offset + 4])[0]
                count = struct.unpack(self.byte_order + 'I', self.file_data[entry_offset + 4:entry_offset + 8])[0]
                
                type_name = TAG_TYPES.get(tag_type, f'Unknown({tag_type})')
                value_bytes = self.file_data[entry_offset + 8:entry_offset + 12]
                value_offset = struct.unpack(self.byte_order + 'I', value_bytes)[0]
                
                tag_info = self._decode_tag_value(tag, tag_type, count, value_offset)
                if tag_info:
                    ifd["tags"][tag] = tag_info
                
                entry_offset += 12
            
            if entry_offset + 4 <= len(self.file_data):
                next_ifd = struct.unpack(self.byte_order + 'I', self.file_data[entry_offset:entry_offset + 4])[0]
                ifd["next_ifd_offset"] = next_ifd
            
            self.ifds.append(ifd)
            return ifd
            
        except Exception as e:
            logger.error(f"Error parsing IFD at offset {offset}: {e}")
            return None
    
    def _decode_tag_value(self, tag: int, tag_type: int, count: int, value_offset: int) -> Optional[Dict[str, Any]]:
        """Decode a single tag value"""
        try:
            type_size = [0, 1, 1, 2, 4, 8, 1, 1, 2, 4, 8, 4, 8]
            type_size = type_size[min(tag_type, 12)]
            total_size = count * type_size
            
            if total_size <= 4:
                data = value_offset.to_bytes(4, byteorder='little' if self.byte_order == 'little' else 'big')
            else:
                if value_offset + total_size > len(self.file_data):
                    return None
                data = self.file_data[value_offset:value_offset + total_size]
            
            value = self._parse_value_by_type(tag, tag_type, count, data)
            
            return {
                "tag": tag,
                "tag_name": self._get_tag_name(tag),
                "type": TAG_TYPES.get(tag_type, f'Unknown({tag_type})'),
                "count": count,
                "value": value,
                "offset": value_offset if total_size > 4 else None
            }
            
        except Exception as e:
            logger.debug(f"Error decoding tag {tag}: {e}")
            return None
    
    def _parse_value_by_type(self, tag: int, tag_type: int, count: int, data: bytes) -> Any:
        """Parse value based on its type"""
        try:
            if tag_type == 2:
                return data.rstrip(b'\\x00').decode('utf-8', errors='replace')
            
            elif tag_type == 1:
                return list(data)
            
            elif tag_type == 3:
                if count == 1:
                    return struct.unpack(self.byte_order + 'H', data[:2])[0]
                elif count == 2:
                    return list(struct.unpack(self.byte_order + 'HH', data[:4]))
                return [struct.unpack(self.byte_order + 'H', data[i:i+2])[0] for i in range(0, min(count * 2, len(data)), 2)]
            
            elif tag_type == 4:
                if count == 1:
                    return struct.unpack(self.byte_order + 'I', data[:4])[0]
                elif count == 2:
                    return list(struct.unpack(self.byte_order + 'II', data[:8]))
                return [struct.unpack(self.byte_order + 'I', data[i:i+4])[0] for i in range(0, min(count * 4, len(data)), 4)]
            
            elif tag_type == 5:
                values = []
                for i in range(count):
                    num = struct.unpack(self.byte_order + 'I', data[i * 8:i * 8 + 4])[0]
                    den = struct.unpack(self.byte_order + 'I', data[i * 8 + 4:i * 8 + 8])[0]
                    values.append(num / den if den != 0 else 0)
                return values[0] if count == 1 else values
            
            elif tag_type == 6:
                return list(data)
            
            elif tag_type == 7:
                return list(data)
            
            elif tag_type == 8:
                if count == 1:
                    return struct.unpack(self.byte_order + 'h', data[:2])[0]
                return [struct.unpack(self.byte_order + 'h', data[i:i+2])[0] for i in range(0, min(count * 2, len(data)), 2)]
            
            elif tag_type == 9:
                if count == 1:
                    return struct.unpack(self.byte_order + 'i', data[:4])[0]
                return [struct.unpack(self.byte_order + 'i', data[i:i+4])[0] for i in range(0, min(count * 4, len(data)), 4)]
            
            elif tag_type == 10:
                values = []
                for i in range(count):
                    num = struct.unpack(self.byte_order + 'i', data[i * 8:i * 8 + 4])[0]
                    den = struct.unpack(self.byte_order + 'i', data[i * 8 + 4:i * 8 + 8])[0]
                    values.append(num / den if den != 0 else 0)
                return values[0] if count == 1 else values
            
            elif tag_type == 11:
                return struct.unpack('f', data[:4])[0]
            
            elif tag_type == 12:
                return struct.unpack('d', data[:8])[0]
            
            return data.hex()
            
        except Exception as e:
            logger.debug(f"Error parsing value by type: {e}")
            return None
    
    def _get_tag_name(self, tag: int) -> str:
        """Get human-readable tag name"""
        tag_names = {
            254: 'NewSubfileType',
            255: 'SubfileType',
            256: 'ImageWidth',
            257: 'ImageLength',
            258: 'BitsPerSample',
            259: 'Compression',
            262: 'PhotometricInterpretation',
            273: 'StripOffsets',
            274: 'Orientation',
            277: 'SamplesPerPixel',
            278: 'RowsPerStrip',
            279: 'StripByteCounts',
            282: 'XResolution',
            283: 'YResolution',
            284: 'PlanarConfiguration',
            296: 'ResolutionUnit',
            305: 'Software',
            315: 'Artist',
            316: 'HostComputer',
            317: 'Predictor',
            318: 'WhitePoint',
            319: 'PrimaryChromaticities',
            322: 'TileWidth',
            323: 'TileLength',
            324: 'TileOffsets',
            325: 'TileByteCounts',
            330: 'SubIFDs',
            339: 'SampleFormat',
            36864: 'ExifVersion',
            37121: 'ComponentsConfiguration',
            37377: 'ISOSpeedRatings',
            37380: 'ExposureBiasValue',
            37381: 'MaxApertureValue',
            37382: 'MeteringMode',
            37383: 'LightSource',
            37384: 'Flash',
            37385: 'FocalLength',
            37386: 'MakerNote',
            37387: 'FlashpixVersion',
            37388: 'ColorSpace',
            37389: 'PixelXDimension',
            37390: 'PixelYDimension',
            37500: 'UserComment',
            37510: 'ImageDescription',
            40960: 'FlashpixVersion',
            40961: 'ColorSpace',
            40962: 'PixelYDimension',
            40963: 'PixelXDimension',
            41483: 'SceneType',
            41484: 'ExposureProgram',
            41486: 'SpectralSensitivity',
            41728: 'FileSource',
            41985: 'CustomRendered',
            41986: 'ExposureMode',
            41987: 'WhiteBalance',
            41988: 'DigitalZoomRatio',
            41989: 'FocalLengthIn35mmFilm',
            42016: 'ImageUniqueID',
            42032: 'CameraOwnerName',
            42033: 'BodySerialNumber',
            42036: 'LensModel',
            42037: 'LensSerialNumber',
            50000: 'XMP',
            50001: 'ImageNumber',
            50002: 'OwnerName',
            50003: 'CameraSerialNumber',
        }
        
        return tag_names.get(tag, f'Tag_{tag}')
    
    def _build_result(self):
        """Build the final result dictionary"""
        self.tiff_info["is_valid_tiff"] = self.is_valid_tiff
        self.tiff_info["byte_order"] = self.byte_order
        self.tiff_info["file_size_bytes"] = self.file_size
        self.tiff_info["ifd_count"] = len(self.ifds)
        
        if self.ifds:
            first_ifd = self.ifds[0]
            
            for tag, tag_info in first_ifd["tags"].items():
                if tag_info:
                    tag_name = tag_info.get("tag_name", f"Tag_{tag}")
                    if isinstance(tag_name, str) and not tag_name.startswith("Tag_"):
                        self.tiff_info[tag_name.lower()] = tag_info["value"]
            
            self.tiff_info["image_width"] = first_ifd["tags"].get(256, {}).get("value") if 256 in first_ifd["tags"] else None
            self.tiff_info["image_length"] = first_ifd["tags"].get(257, {}).get("value") if 257 in first_ifd["tags"] else None
            self.tiff_info["bits_per_sample"] = first_ifd["tags"].get(258, {}).get("value") if 258 in first_ifd["tags"] else None
            self.tiff_info["samples_per_pixel"] = first_ifd["tags"].get(277, {}).get("value") if 277 in first_ifd["tags"] else None
            
            compression = first_ifd["tags"].get(259, {}).get("value") if 259 in first_ifd["tags"] else None
            if compression:
                self.tiff_info["compression_name"] = COMPRESSION_CODES.get(compression, f'Unknown({compression})')
            
            photometric = first_ifd["tags"].get(262, {}).get("value") if 262 in first_ifd["tags"] else None
            if photometric:
                self.tiff_info["photometric_name"] = PHOTOMETRIC_INTERPRETATIONS.get(photometric, f'Unknown({photometric})')
            
            orientation = first_ifd["tags"].get(274, {}).get("value") if 274 in first_ifd["tags"] else None
            if orientation:
                orientation_map = {1: 'Top-left', 2: 'Top-right', 3: 'Bottom-right', 4: 'Bottom-left', 5: 'Left-top', 6: 'Right-top', 7: 'Right-bottom', 8: 'Left-bottom'}
                self.tiff_info["orientation_name"] = orientation_map.get(orientation, f'Unknown({orientation})')
        
        self.tiff_info["success"] = True


class BigTIFFExtractor:
    """BigTIFF format extractor (supports files > 4GB)"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file_data: Optional[bytes] = None
        
    def parse(self) -> Dict[str, Any]:
        """Parse BigTIFF file"""
        try:
            with open(self.filepath, 'rb') as f:
                self.file_data = f.read()
            
            if len(self.file_data) < 16:
                return {"error": "File too small", "success": False}
            
            if self.file_data[:2] != b'II' and self.file_data[:2] != b'MM':
                return {"error": "Not a valid TIFF file", "success": False}
            
            version = struct.unpack('H', self.file_data[2:4])[0]
            if version != 43:
                return {"error": f"Not a TIFF file (version: {version})", "success": False}
            
            offset_size = struct.unpack('H', self.file_data[4:6])[0]
            if offset_size != 8:
                return {"error": f"Unsupported offset size: {offset_size}", "success": False}
            
            tags = {}
            offset = struct.unpack('Q', self.file_data[8:16])[0]
            
            return {
                "is_bigtiff": True,
                "offset_size": offset_size,
                "first_ifd_offset": offset,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error parsing BigTIFF: {e}")
            return {"error": str(e), "success": False}


class GeoTIFFExtractor:
    """GeoTIFF extension extractor ( geospatial metadata)"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        
    def parse(self) -> Dict[str, Any]:
        """Parse GeoTIFF metadata"""
        try:
            from .tiff_extractor import TIFFExtractor
            tiff = TIFFExtractor(self.filepath)
            result = tiff.parse()
            
            if not result.get("success"):
                return result
            
            geo_keys = {}
            model_tie_points = None
            model_pixel_scale = None
            
            return {
                "is_geotiff": True,
                "geo_keys": geo_keys,
                "model_tie_points": model_tie_points,
                "model_pixel_scale": model_pixel_scale,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error parsing GeoTIFF: {e}")
            return {"error": str(e), "success": False}
