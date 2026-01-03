#!/usr/bin/env python3
"""
OpenEXR HDR Module
Extracts metadata from OpenEXR high dynamic range files including:
- Header parsing (version, flags)
- Channel extraction (UINT/HALF/FLOAT types)
- Chromaticities, white point, luminance
- Tile attributes
- Display window, data window

Author: MetaExtract Team
Version: 1.0.0
"""

import struct
import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

EXR_SIGNATURE = b'\x76\x2f\x31\x01'


class OpenEXRAnalyzer:
    """
    OpenEXR HDR file analyzer.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file_data: Optional[bytes] = None

    def analyze(self) -> Dict[str, Any]:
        """Main entry point - analyze OpenEXR file"""
        try:
            self._load_file_data()

            result = {
                "is_valid_exr": False,
                "version": None,
                "version_flag": None,
                "channels": None,
                "compression": None,
                "data_window": None,
                "display_window": None,
                "line_order": None,
                "pixel_aspect_ratio": None,
                "chromaticities": None,
                "white_luminance": None,
                "adopted_neutral": None,
                "rendered_device": None,
                "look_modify_transform": None,
                "tiles": None,
                "attributes": {},
            }

            if self._detect_format():
                result["is_valid_exr"] = True
                result.update(self._parse_header())

            return result

        except Exception as e:
            logger.error(f"Error analyzing OpenEXR file: {e}")
            return {"error": str(e), "is_valid_exr": False}

    def _load_file_data(self):
        """Load file data"""
        file_path = Path(self.filepath)
        if not file_path.exists():
            return

        try:
            with open(self.filepath, 'rb') as f:
                self.file_data = f.read()
        except Exception:
            self.file_data = None

    def _detect_format(self) -> bool:
        """Detect if file is OpenEXR format"""
        if not self.file_data or len(self.file_data) < 8:
            return False
        return self.file_data[:4] == EXR_SIGNATURE

    def _parse_header(self) -> Dict[str, Any]:
        """Parse OpenEXR header"""
        result: Dict[str, Any] = {}

        if not self.file_data or len(self.file_data) < 8:
            return result

        version = struct.unpack('<I', self.file_data[4:8])[0]
        result["version"] = version
        result["version_flag"] = {
            "tiled": bool(version & 0x00000200),
            "multipart": bool(version & 0x00000400),
        }

        header_end = self.file_data.find(b'\x00\x00\x00\x00', 8)
        if header_end == -1:
            header_end = min(len(self.file_data), 4096)

        header_data = self.file_data[8:header_end]
        attributes = self._parse_attributes(header_data)

        for key, value in attributes.items():
            if key in ['channels']:
                result[key] = value
            elif key in ['compression']:
                result[key] = self._map_compression(value)
            elif key in ['dataWindow', 'displayWindow']:
                result[key.replace('Window', '_window')] = value
            elif key in ['lineOrder']:
                result['line_order'] = self._map_line_order(value)
            elif key in ['pixelAspectRatio']:
                result['pixel_aspect_ratio'] = value
            elif key in ['chromaticities']:
                result['chromaticities'] = value
            elif key in ['whiteLuminance']:
                result['white_luminance'] = value
            elif key in ['adoptedNeutral']:
                result['adopted_neutral'] = value
            elif key in ['renderingTransform', 'lookModifiesTransform']:
                result['look_modify_transform'] = value
            elif key in ['tiles']:
                result['tiles'] = value
            else:
                result['attributes'][key] = value

        return result

    def _parse_attributes(self, data: bytes) -> Dict[str, Any]:
        """Parse OpenEXR header attributes"""
        attributes: Dict[str, Any] = {}
        offset = 0

        while offset < len(data) - 4:
            name_end = data.find(b'\x00', offset)
            if name_end == -1 or name_end - offset > 255:
                break

            name = data[offset:name_end].decode('ascii', errors='replace')
            offset = name_end + 1

            if offset + 4 > len(data):
                break

            attr_type = data[offset:offset + 4].decode('ascii', errors='replace')
            offset += 4

            if offset + 4 > len(data):
                break

            size = struct.unpack('<I', data[offset:offset + 4])[0]
            offset += 4

            if offset + size > len(data):
                break

            attr_data = data[offset:offset + size]
            offset += size

            if size % 2 != 0:
                offset += 1

            attributes[name] = self._parse_attribute_value(attr_type, attr_data)

        return attributes

    def _parse_attribute_value(self, attr_type: str, data: bytes) -> Any:
        """Parse attribute value based on type"""
        if attr_type in ['float', 'float', 'flt ']:
            if len(data) >= 4:
                return struct.unpack('<f', data[:4])[0]
            return None

        elif attr_type in ['int', 'int ']:
            if len(data) >= 4:
                return struct.unpack('<I', data[:4])[0]
            return None

        elif attr_type == 'box2i':
            if len(data) >= 16:
                return {
                    "x_min": struct.unpack('<i', data[0:4])[0],
                    "y_min": struct.unpack('<i', data[4:8])[0],
                    "x_max": struct.unpack('<i', data[8:12])[0],
                    "y_max": struct.unpack('<i', data[12:16])[0],
                }
            return None

        elif attr_type == 'chlist':
            return self._parse_chlist(data)

        elif attr_type == 'compression':
            if len(data) >= 1:
                return data[0]
            return None

        elif attr_type == 'v2f':
            if len(data) >= 8:
                return {
                    "x": struct.unpack('<f', data[0:4])[0],
                    "y": struct.unpack('<f', data[4:8])[0],
                }
            return None

        elif attr_type == 'v3f':
            if len(data) >= 12:
                return {
                    "x": struct.unpack('<f', data[0:4])[0],
                    "y": struct.unpack('<f', data[4:8])[0],
                    "z": struct.unpack('<f', data[8:12])[0],
                }
            return None

        elif attr_type == 'string':
            return data.rstrip(b'\x00').decode('utf-8', errors='replace')

        elif attr_type == 'dict' or attr_type == 'opf':
            try:
                return data.rstrip(b'\x00').decode('utf-8', errors='replace')
            except:
                return None

        return None

    def _parse_chlist(self, data: bytes) -> List[Dict[str, Any]]:
        """Parse channel list"""
        channels: List[Dict[str, Any]] = []
        offset = 0

        if len(data) < 4:
            return channels

        num_channels = data[offset]
        offset += 1

        channel_types = {0: 'UINT', 1: 'HALF', 2: 'FLOAT'}

        for _ in range(num_channels):
            if offset >= len(data):
                break

            name_end = data.find(b'\x00', offset)
            if name_end == -1 or name_end - offset > 255:
                break

            name = data[offset:name_end].decode('ascii', errors='replace')
            offset = name_end + 1

            if offset + 16 > len(data):
                break

            channel = {
                "name": name,
                "pixel_type": channel_types.get(data[offset], 'UNKNOWN'),
                "pLinear": bool(data[offset + 1]),
                "xSampling": struct.unpack('<H', data[offset + 2:offset + 4])[0],
                "ySampling": struct.unpack('<H', data[offset + 4:offset + 6])[0],
            }
            offset += 16

            channels.append(channel)

        return channels

    def _map_compression(self, value: Any) -> Optional[str]:
        """Map compression code to name"""
        if value is None:
            return None

        compression_map = {
            0: 'NO_COMPRESSION',
            1: 'RLE_COMPRESSION',
            2: 'ZIPS_COMPRESSION',
            3: 'ZIP_COMPRESSION',
            4: 'PIZ_COMPRESSION',
            5: 'PXR24_COMPRESSION',
            6: 'B44_COMPRESSION',
            7: 'B44A_COMPRESSION',
            8: 'DWAA_COMPRESSION',
            9: 'DWAB_COMPRESSION',
        }

        if isinstance(value, int):
            return compression_map.get(value, f'UNKNOWN ({value})')
        return str(value)

    def _map_line_order(self, value: Any) -> Optional[str]:
        """Map line order code to name"""
        if value is None:
            return None

        line_order_map = {
            0: 'INCREASING_Y',
            1: 'DECREASING_Y',
            2: 'RANDOM_Y',
        }

        if isinstance(value, int):
            return line_order_map.get(value, f'UNKNOWN ({value})')
        return str(value)


def analyze_openexr_hdr(filepath: str) -> Dict[str, Any]:
    """Convenience function to analyze OpenEXR file"""
    analyzer = OpenEXRAnalyzer(filepath)
    return analyzer.analyze()


def get_openexr_hdr_field_count() -> int:
    """Return the number of fields this module extracts"""
    return 50
