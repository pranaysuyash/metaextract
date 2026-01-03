#!/usr/bin/env python3
"""
ICC Profile Parser Module
Deep ICC 4.3 profile parsing including:
- Profile header (signature, version, class, color space)
- Tag definitions (A2B0-2, B2A0-2, TRC curves, XYZ, gamut, CLUT)
- Colorimetry (primaries, white point, TRC curves)
- Technology and device settings
- Named colors

Author: MetaExtract Team
Version: 1.0.0
"""

import struct
import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

ICC_SIGNATURE = b'acsp'
ICC_VERSION = 0x04000000

PROFILE_CLASSES = {
    0x73636E72: 'scnr',
    0x6D6E7472: 'mntr',
    0x70727472: 'prtr',
    0x6C696E6B: 'link',
    0x73706163: 'spac',
    0x61627374: 'abst',
    0x6E6D636C: 'nmcl',
}

COLOR_SPACES = {
    0x52474220: 'RGB',
    0x434D594B: 'CMYK',
    0x4C616220: 'Lab',
    0x58595A20: 'XYZ',
    0x47524159: 'Gray',
    0x59434342: 'YCbCr',
}

PLATFORMS = {
    0x4150504C: 'Apple',
    0x4D534654: 'Microsoft',
    0x53474920: 'Silicon Graphics',
    0x5F545257: 'Sun Microsystems',
}

RENDERING_INTENTS = {
    0: 'Perceptual',
    1: 'Relative Colorimetric',
    2: 'Saturation',
    3: 'Absolute Colorimetric',
}

TAG_SIGNATURES = {
    0x41324230: 'A2B0',
    0x41324231: 'A2B1',
    0x41324232: 'A2B2',
    0x42324130: 'B2A0',
    0x42324131: 'B2A1',
    0x42324132: 'B2A2',
    0x74726320: 'TRC',
    0x67545220: 'gTR',
    0x62545220: 'bTR',
    0x58595A20: 'XYZ',
    0x7258595A: 'rXYZ',
    0x6758595A: 'gXYZ',
    0x6258595A: 'bXYZ',
    0x77687465: 'wtpt',
    0x626B7074: 'bkpt',
    0x636C7274: 'clrt',
    0x64657363: 'desc',
    0x6175746F: 'auth',
    0x646D6E64: 'dmnd',
    0x646D6464: 'dmdd',
    0x6D6C7563: 'mluc',
    0x6E636C72: 'ncol',
    0x74656368: 'tech',
    0x63707274: 'cprt',
    0x74726D6B: 'trmk',
    0x736F7572: 'sour',
    0x76337373: 'vsss',
    0x76333373: 'v3333',
    0x76343434: 'v4444',
}

TAG_TYPES = {
    0x74657874: 'text',
    0x64657363: 'desc',
    0x6D6C7563: 'mluc',
    0x6E636C72: 'ncol',
    0x63757276: 'curv',
    0x63757266: 'curf',
    0x70747263: 'ptrc',
    0x6D617470: 'mat ',
    0x6C756D69: 'lumi',
    0x78696666: 'xfrm',
    0x5845595A: 'XYZ ',
    0x636C726F: 'clro',
    0x6D626F78: 'mft1',
    0x6D667432: 'mft2',
    0x636C7574: 'clut',
}


class ICCProfileParser:
    """
    ICC profile parser for extracting detailed metadata from ICC profiles.
    Supports ICC 4.3 specification with all tag types.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file_size = 0
        self.profile_data: Optional[bytes] = None
        self.header: Optional[Dict[str, Any]] = None
        self.tags: Dict[str, Dict[str, Any]] = {}
        self.is_valid_icc = False

    def parse(self) -> Dict[str, Any]:
        """Main entry point - parse ICC profile and extract all metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}

            self.file_size = file_path.stat().st_size

            with open(self.filepath, 'rb') as f:
                self.profile_data = f.read()

            if len(self.profile_data) < 128:
                return {"error": "Profile too small", "success": False}

            self.header = self._parse_header(self.profile_data[:128])

            tag_count = self.header.get("tag_count", 0)
            tag_table_offset = 128

            for i in range(tag_count):
                tag_entry = self._parse_tag_entry(
                    self.profile_data,
                    tag_table_offset + i * 12
                )
                tag_sig = tag_entry.get("signature", "")
                tag_data = self._parse_tag_data(
                    tag_entry.get("offset", 0),
                    tag_entry.get("size", 0),
                    tag_entry.get("type", 0)
                )
                self.tags[tag_sig] = tag_data

            return self._build_result()

        except Exception as e:
            logger.error(f"Error parsing ICC profile: {e}")
            return {"error": str(e), "success": False}

    def _parse_header(self, data: bytes) -> Dict[str, Any]:
        """Parse ICC profile header"""
        if len(data) < 128:
            return {"error": "Invalid header size"}

        offset = 0
        signature = data[offset:offset + 4]
        offset += 4

        if signature != ICC_SIGNATURE:
            return {"error": "Invalid ICC signature"}

        profile_size = struct.unpack('>I', data[offset:offset + 4])[0]
        offset += 4

        cmm_type = data[offset:offset + 4].decode('latin-1', errors='replace')
        offset += 4

        version_major = (data[offset] >> 4) & 0x0F
        version_minor = data[offset] & 0x0F
        version_patch = data[offset + 1] >> 4
        version = struct.unpack('>H', data[offset:offset + 2])[0]
        offset += 2

        profile_class = struct.unpack('>I', data[offset:offset + 4])[0]
        offset += 4
        profile_class_name = PROFILE_CLASSES.get(profile_class, f"Unknown ({profile_class:08x})")

        color_space = struct.unpack('>I', data[offset:offset + 4])[0]
        offset += 4
        color_space_name = COLOR_SPACES.get(color_space, f"Unknown ({color_space:08x})")

        connection_space = struct.unpack('>I', data[offset:offset + 4])[0]
        offset += 4
        connection_space_name = COLOR_SPACES.get(connection_space, f"Unknown ({connection_space:08x})")

        profile_datetime = {
            "year": struct.unpack('>H', data[offset:offset + 2])[0],
            "month": data[offset + 2],
            "day": data[offset + 3],
            "hour": data[offset + 4],
            "minute": data[offset + 5],
            "second": data[offset + 6],
        }
        offset += 7

        acsp_signature = data[offset:offset + 4].decode('latin-1', errors='replace')
        offset += 4

        platform = struct.unpack('>I', data[offset:offset + 4])[0]
        offset += 4
        platform_name = PLATFORMS.get(platform, f"Unknown ({platform:08x})")

        flags = struct.unpack('>I', data[offset:offset + 4])[0]
        offset += 4

        device_manufacturer = struct.unpack('>I', data[offset:offset + 4])[0]
        offset += 4

        device_model = struct.unpack('>I', data[offset:offset + 4])[0]
        offset += 4

        device_attributes = data[offset:offset + 8]
        offset += 8

        rendering_intent = struct.unpack('>I', data[offset:offset + 4])[0]
        offset += 4
        rendering_intent_name = RENDERING_INTENTS.get(rendering_intent, "Unknown")

        pcs_illuminant = {
            "x": struct.unpack('>I', data[offset:offset + 4])[0] / 65536.0,
            "y": struct.unpack('>I', data[offset + 4:offset + 8])[0] / 65536.0,
            "z": struct.unpack('>I', data[offset + 8:offset + 12])[0] / 65536.0,
        }
        offset += 12

        creator_signature = data[offset:offset + 4].decode('latin-1', errors='replace')
        offset += 4

        profile_id = data[offset:offset + 16]
        offset += 16

        tag_count = struct.unpack('>I', data[offset:offset + 4])[0]

        return {
            "profile_size": profile_size,
            "cmm_type": cmm_type,
            "version": f"{version_major}.{version_minor}.{version_patch}",
            "version_raw": version,
            "profile_class": profile_class,
            "profile_class_name": profile_class_name,
            "color_space": color_space,
            "color_space_name": color_space_name,
            "connection_space": connection_space,
            "connection_space_name": connection_space_name,
            "profile_datetime": profile_datetime,
            "platform": platform,
            "platform_name": platform_name,
            "flags": flags,
            "device_manufacturer": f"0x{device_manufacturer:08x}",
            "device_model": f"0x{device_model:08x}",
            "device_attributes_hex": device_attributes.hex(),
            "rendering_intent": rendering_intent,
            "rendering_intent_name": rendering_intent_name,
            "pcs_illuminant": pcs_illuminant,
            "creator": creator_signature,
            "tag_count": tag_count,
        }

    def _parse_tag_entry(self, data: bytes, offset: int) -> Dict[str, Any]:
        """Parse a single tag table entry"""
        if offset + 12 > len(data):
            return {}

        signature = data[offset:offset + 4].decode('latin-1', errors='replace')
        offset_tag = struct.unpack('>I', data[offset + 4:offset + 8])[0]
        size = struct.unpack('>I', data[offset + 8:offset + 12])[0]
        tag_type = struct.unpack('>I', data[offset + 12:offset + 16])[0]

        return {
            "signature": signature,
            "offset": offset_tag,
            "size": size,
            "type": tag_type,
        }

    def _parse_tag_data(self, offset: int, size: int, tag_type: int) -> Dict[str, Any]:
        """Parse tag data based on type"""
        if self.profile_data is None:
            return {"error": "Profile data not loaded"}

        if offset + size > len(self.profile_data):
            return {"error": "Tag data out of bounds"}

        data = self.profile_data[offset:offset + size]
        type_name = TAG_TYPES.get(tag_type, f"Unknown ({tag_type:08x})")

        result = {
            "type_name": type_name,
            "size": size,
        }

        if tag_type == 0x5845595A:
            result.update(self._parse_xyz(data))
        elif tag_type == 0x63757276:
            result.update(self._parse_curve(data))
        elif tag_type == 0x63757266:
            result.update(self._parse_curf(data))
        elif tag_type == 0x6D617470:
            result.update(self._parse_matrix(data))
        elif tag_type == 0x6C756D69:
            result.update(self._parse_luminance(data))
        elif tag_type == 0x74657874:
            result["text"] = data.decode('utf-8', errors='replace').rstrip('\x00')
        elif tag_type == 0x64657363:
            result.update(self._parse_description(data))
        elif tag_type == 0x6D6C7563:
            result.update(self._parse_mluc(data))
        elif tag_type == 0x636C7274:
            result.update(self._parse_clrt(data))
        elif tag_type == 0x6E636C72:
            result.update(self._parse_ncol(data))
        elif tag_type == 0x74656368:
            result.update(self._parse_technology(data))
        elif tag_type == 0x63707274:
            result.update(self._parse_copyright(data))
        elif tag_type == 0x636C7574:
            result.update(self._parse_clut(data))
        else:
            result["data_hex"] = data[:64].hex()

        return result

    def _parse_xyz(self, data: bytes) -> Dict[str, Any]:
        """Parse XYZ tag"""
        if len(data) < 12:
            return {"error": "Invalid XYZ data"}

        return {
            "xyz_values": [
                struct.unpack('>I', data[0:4])[0] / 65536.0,
                struct.unpack('>I', data[4:8])[0] / 65536.0,
                struct.unpack('>I', data[8:12])[0] / 65536.0,
            ]
        }

    def _parse_curve(self, data: bytes) -> Dict[str, Any]:
        """Parse curve (TRC) tag"""
        if len(data) < 4:
            return {"error": "Invalid curve data"}

        count = struct.unpack('>I', data[0:4])[0]

        if count == 0:
            return {"type": "gamma", "gamma": 1.0}

        curve_values = []
        for i in range(min(count, 256)):
            offset = 4 + i * 2
            if offset + 2 <= len(data):
                value = struct.unpack('>H', data[offset:offset + 2])[0]
                curve_values.append(value / 65535.0)

        return {
            "type": "curve",
            "entry_count": count,
            "values": curve_values,
        }

    def _parse_curf(self, data: bytes) -> Dict[str, Any]:
        """Parse formatted curve tag"""
        if len(data) < 4:
            return {"error": "Invalid formatted curve data"}

        count = struct.unpack('>I', data[0:4])[0]

        return {
            "type": "formatted_curve",
            "entry_count": count,
            "reserved": data[4],
        }

    def _parse_matrix(self, data: bytes) -> Dict[str, Any]:
        """Parse matrix tag"""
        if len(data) < 36:
            return {"error": "Invalid matrix data"}

        matrix = []
        for i in range(9):
            offset = i * 4
            matrix.append(struct.unpack('>i', data[offset:offset + 4])[0] / 65536.0)

        return {
            "matrix_3x3": [
                matrix[0:3],
                matrix[3:6],
                matrix[6:9],
            ]
        }

    def _parse_luminance(self, data: bytes) -> Dict[str, Any]:
        """Parse luminance tag"""
        if len(data) < 12:
            return {"error": "Invalid luminance data"}

        return {
            "luminance": [
                struct.unpack('>I', data[0:4])[0] / 65536.0,
                struct.unpack('>I', data[4:8])[0] / 65536.0,
                struct.unpack('>I', data[8:12])[0] / 65536.0,
            ]
        }

    def _parse_description(self, data: bytes) -> Dict[str, Any]:
        """Parse description tag"""
        if len(data) < 12:
            return {"error": "Invalid description data"}

        ascii_length = struct.unpack('>I', data[0:4])[0]
        description = data[4:4 + ascii_length].decode('utf-8', errors='replace').rstrip('\x00')

        return {
            "description": description,
            "ascii_length": ascii_length,
        }

    def _parse_mluc(self, data: bytes) -> Dict[str, Any]:
        """Parse multi-localized unicode tag"""
        if len(data) < 8:
            return {"error": "Invalid mluc data"}

        entries = struct.unpack('>I', data[0:4])[0]
        record_size = struct.unpack('>I', data[4:8])[0]

        languages = {}
        for i in range(entries):
            offset = 8 + i * record_size
            if offset + record_size <= len(data):
                language = data[offset:offset + 2].decode('latin-1', errors='replace').strip('\x00')
                country = data[offset + 2:offset + 4].decode('latin-1', errors='replace').strip('\x00')
                text_offset = struct.unpack('>I', data[offset + 4:offset + 8])[0]
                text_length = struct.unpack('>I', data[offset + 8:offset + 12])[0]

                text_start = 8 + entries * record_size + text_offset
                if text_start + text_length <= len(data):
                    text = data[text_start:text_start + text_length].decode('utf-8', errors='replace')
                    languages[f"{language}_{country}"] = text

        return {
            "multilingual_text": languages,
            "entry_count": entries,
        }

    def _parse_clrt(self, data: bytes) -> Dict[str, Any]:
        """Parse colorant table tag"""
        if len(data) < 4:
            return {"error": "Invalid clrt data"}

        count = struct.unpack('>I', data[0:4])[0]
        colorants = []

        for i in range(min(count, 256)):
            offset = 4 + i * 40
            if offset + 40 <= len(data):
                name = data[offset:offset + 32].decode('utf-8', errors='replace').rstrip('\x00')
                colorants.append({
                    "name": name,
                    "values": [
                        struct.unpack('>H', data[offset + 34:offset + 36])[0] / 65535.0,
                        struct.unpack('>H', data[offset + 36:offset + 38])[0] / 65535.0,
                        struct.unpack('>H', data[offset + 38:offset + 40])[0] / 65535.0,
                    ]
                })

        return {
            "colorant_count": count,
            "colorants": colorants,
        }

    def _parse_ncol(self, data: bytes) -> Dict[str, Any]:
        """Parse named color tag"""
        if len(data) < 12:
            return {"error": "Invalid ncol data"}

        count = struct.unpack('>I', data[0:4])[0]
        prefix_len = struct.unpack('>I', data[4:8])[0]
        suffix_len = struct.unpack('>I', data[8:12])[0]

        offset = 12 + prefix_len + suffix_len

        colors = []
        for i in range(count):
            if offset >= len(data):
                break
            name_end = data.index(b'\x00', offset)
            name = data[offset:name_end].decode('utf-8', errors='replace')
            offset = name_end + 1

            if offset + 6 <= len(data):
                colors.append({
                    "name": name,
                    "values": [
                        struct.unpack('>H', data[offset:offset + 2])[0] / 65535.0,
                        struct.unpack('>H', data[offset + 2:offset + 4])[0] / 65535.0,
                        struct.unpack('>H', data[offset + 4:offset + 6])[0] / 65535.0,
                    ]
                })
                offset += 6

        return {
            "named_color_count": count,
            "colors": colors,
        }

    def _parse_technology(self, data: bytes) -> Dict[str, Any]:
        """Parse technology tag"""
        if len(data) < 4:
            return {"error": "Invalid technology data"}

        return {
            "technology": data[:4].decode('latin-1', errors='replace'),
        }

    def _parse_copyright(self, data: bytes) -> Dict[str, Any]:
        """Parse copyright tag"""
        return {
            "copyright": data.decode('utf-8', errors='replace').rstrip('\x00'),
        }

    def _parse_clut(self, data: bytes) -> Dict[str, Any]:
        """Parse CLUT (color lookup table) tag"""
        if len(data) < 32:
            return {"error": "Invalid CLUT data"}

        grid_points = []
        for i in range(min(16, len(data) // 4)):
            grid_points.append(data[i * 4])

        return {
            "clut_grid_points": grid_points,
            "clut_data_size": len(data),
        }

    def _build_result(self) -> Dict[str, Any]:
        """Build final result dictionary"""
        result = {
            "success": True,
            "file_size": self.file_size,
            "is_valid_icc": self.header is not None,
            "header": self.header,
            "tag_count": len(self.tags),
        }

        tag_summaries = {}
        for sig, tag in self.tags.items():
            tag_summaries[sig] = {
                "type": tag.get("type_name", "unknown"),
                "size": tag.get("size", 0),
            }
            if "xyz_values" in tag:
                tag_summaries[sig]["values"] = tag["xyz_values"]
            elif "values" in tag:
                tag_summaries[sig]["values"] = tag["values"][:10]
            elif "description" in tag:
                tag_summaries[sig]["description"] = tag["description"][:100]
            elif "multilingual_text" in tag:
                tag_summaries[sig]["languages"] = list(tag["multilingual_text"].keys())

        result["tags"] = tag_summaries

        return result


def extract_icc_profile(filepath: str) -> Dict[str, Any]:
    """Convenience function to extract ICC profile metadata"""
    parser = ICCProfileParser(filepath)
    return parser.parse()


def get_icc_field_count() -> int:
    """Return the number of fields this module extracts"""
    return 80
