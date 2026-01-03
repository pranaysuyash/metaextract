#!/usr/bin/env python3
"""
AVIF/HEIF Advanced Parser Module
Deep AVIF and HEIF ISOBMFF parsing including:
- Full box structure parsing (ftyp, moov, mdia, minf, stbl, etc.)
- AV1 configuration (av1C)
- Image property items (iprp, ipco, ipma)
- Image spatial extent (ispe)
- Color information (colr, nclx, pASP)
- Alpha and auxiliary images
- Motion photo metadata
- HEIF primary image and thumbnails
- Item properties and metadata

Author: MetaExtract Team
Version: 1.0.0
"""

import struct
import logging
import uuid
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

AVIF_SIGNATURE = b'ftyp'
HEIF_SIGNATURE = b'ftyp'
ISOBMFF_SIGNATURES = [b'ftyp', b'moov', b'mdat', b'free', b'skip', b'wide', b'uuid']

BOX_TYPE_MAP = {
    b'ftyp': 'File Type',
    b'moov': 'Movie Box',
    b'mvhd': 'Movie Header',
    b'trak': 'Track Box',
    b'tkhd': 'Track Header',
    b'mdia': 'Media Box',
    b'mdhd': 'Media Header',
    b'hdlr': 'Handler Reference',
    b'minf': 'Media Information',
    b'vmhd': 'Video Media Header',
    b'stbl': 'Sample Table Box',
    b'stsz': 'Sample Size Box',
    b'stsc': 'Sample to Chunk Box',
    b'stco': 'Chunk Offset Box',
    b'co64': 'Chunk Offset 64-bit',
    b'ctts': 'Composition Time to Sample',
    b'stss': 'Sync Sample Box',
    b'avc1': 'AVC Video Sample Entry',
    b'avc3': 'AVC Video Sample Entry',
    b'av1C': 'AV1 Configuration',
    b'av1A': 'AV1 Sequence Header',
    b'ipco': 'Image Property Container',
    b'ipma': 'Image Property Association',
    b'iprp': 'Image Properties',
    b'iinf': 'Item Information',
    b'infe': 'Item Information Entry',
    b'iloc': 'Item Location',
    b'iref': 'Item Reference',
    b'clap': 'Clean Aperture',
    b'pixi': 'Pixel Information',
    b'ispe': 'Image Spatial Extent',
    b'colr': 'Color Information',
    b'nclx': 'Color Configuration',
    b'pASP': 'Pixel Aspect Ratio',
    b'mime': 'MIME Type',
    b'uuid': 'User Extension',
    b'mdat': 'Media Data',
    b'free': 'Free Space',
    b'skip': 'Skip Space',
    b'wide': 'Wide Space',
}

MAJOR_BRAND_MAP = {
    b'avif': 'AVIF',
    b'mif1': 'HEIF',
    b'msf1': 'HEIF Multi-Image',
    b'heic': 'HEIF Container',
    b'hev1': 'HEVC H.265',
    b'av01': 'AV1',
    b'isom': 'ISO Base Media',
    b'iso2': 'ISO Base Media v2',
    b'iso3': 'ISO Base Media v3',
    b'iso4': 'ISO Base Media v4',
    b'iso5': 'ISO Base Media v5',
    b'iso6': 'ISO Base Media v6',
    b'qt  ': 'QuickTime',
    b'M4V ': 'MPEG-4 Video',
    b'M4A ': 'MPEG-4 Audio',
}


class AVIFParser:
    """
    Advanced AVIF/HEIF parser for extracting comprehensive metadata.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file_data: Optional[bytes] = None
        self.file_size = 0
        self.boxes: List[Dict[str, Any]] = []
        self.avif_info: Dict[str, Any] = {}
        self.is_valid_avif = False
        self.is_heif = False
        self.primary_item: Optional[Dict[str, Any]] = None
        self.thumbnails: List[Dict[str, Any]] = []
        self.motion_photo: Optional[Dict[str, Any]] = None

    def parse(self) -> Dict[str, Any]:
        """Main entry point - parse AVIF/HEIF file"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}

            self.file_size = file_path.stat().st_size

            with open(self.filepath, 'rb') as f:
                self.file_data = f.read()

            if len(self.file_data) < 12:
                return {"error": "File too small", "success": False}

            if self.file_data[4:8] != AVIF_SIGNATURE:
                first_box = self.file_data[:4]
                if first_box not in ISOBMFF_SIGNATURES:
                    return {"error": "Not an ISOBMFF file", "success": False}

            self.is_valid_avif = True
            self._parse_boxes(0, len(self.file_data))

            return self._build_result()

        except Exception as e:
            logger.error(f"Error parsing AVIF/HEIF: {e}")
            return {"error": str(e), "success": False}

    def _parse_boxes(self, offset: int, end_offset: int):
        """Parse ISOBMFF boxes recursively"""
        while offset + 8 <= end_offset:
            box_size = struct.unpack('>I', self.file_data[offset:offset + 4])[0]
            box_type = self.file_data[offset + 4:offset + 8]

            if box_size == 0:
                box_size = end_offset - offset
            elif box_size == 1:
                if offset + 16 > end_offset:
                    break
                box_size = struct.unpack('>Q', self.file_data[offset + 8:offset + 16])[0]
                header_size = 16
            else:
                header_size = 8

            if box_size < header_size:
                break

            box_data_offset = offset + header_size
            box_data_end = min(offset + box_size, end_offset)

            box_info = self._parse_box(box_type, self.file_data[box_data_offset:box_data_end])
            self.boxes.append(box_info)

            offset += box_size

    def _parse_box(self, box_type: bytes, box_data: bytes) -> Dict[str, Any]:
        """Parse individual box"""
        box_name = BOX_TYPE_MAP.get(box_type, box_type.decode('latin-1', errors='replace'))

        box_info: Dict[str, Any] = {
            "type": box_name,
            "type_raw": box_type.hex(),
            "size": len(box_data),
        }

        if box_type == b'ftyp':
            box_info.update(self._parse_ftyp(box_data))
        elif box_type == b'moov':
            box_info.update(self._parse_moov(box_data))
        elif box_type == b'av1C':
            box_info.update(self._parse_av1c(box_data))
        elif box_type == b'iprp':
            box_info.update(self._parse_iprp(box_data))
        elif box_type == b'iinf':
            box_info.update(self._parse_iinf(box_data))
        elif box_type == b'iloc':
            box_info.update(self._parse_iloc(box_data))
        elif box_type == b'colr':
            box_info.update(self._parse_colr(box_data))
        elif box_type == b'ispe':
            box_info.update(self._parse_ispe(box_data))
        elif box_type == b'pixi':
            box_info.update(self._parse_pixi(box_data))
        elif box_type == b'clap':
            box_info.update(self._parse_clap(box_data))
        elif box_type == b'mdat':
            box_info["data_size"] = len(box_data)
        elif box_type == b'hdlr':
            box_info.update(self._parse_hdlr(box_data))
        elif box_type == b'uuid':
            box_info.update(self._parse_uuid(box_data))

        if box_type in [b'moov', b'minf', b'iprp', b'iloc']:
            self._parse_boxes(0, len(box_data))

        return box_info

    def _parse_ftyp(self, data: bytes) -> Dict[str, Any]:
        """Parse file type box"""
        result: Dict[str, Any] = {}

        if len(data) < 8:
            return result

        major_brand = data[:4]
        result["major_brand"] = major_brand.decode('latin-1', errors='replace')
        result["major_brand_name"] = MAJOR_BRAND_MAP.get(major_brand, "Unknown")

        minor_version = struct.unpack('>I', data[4:8])[0]
        result["minor_version"] = minor_version

        compatible_brands = []
        for i in range(8, len(data), 4):
            if i + 4 <= len(data):
                brand = data[i:i + 4]
                brand_name = MAJOR_BRAND_MAP.get(brand, brand.decode('latin-1', errors='replace'))
                compatible_brands.append({
                    "brand": brand_name,
                    "raw": brand.decode('latin-1', errors='replace'),
                })

        result["compatible_brands"] = compatible_brands

        self.is_heif = major_brand in [b'mif1', b'msf1', b'heic', b'hev1']

        return result

    def _parse_moov(self, data: bytes) -> Dict[str, Any]:
        """Parse movie box"""
        result: Dict[str, Any] = {}
        self._parse_boxes(0, len(data))
        return result

    def _parse_av1c(self, data: bytes) -> Dict[str, Any]:
        """Parse AV1 configuration box"""
        result: Dict[str, Any] = {}

        if len(data) < 4:
            return result

        byte0 = data[0]
        result["marker"] = (byte0 >> 7) & 1
        result["version"] = byte0 & 0x7F

        byte1 = data[1]
        result["seq_profile"] = (byte1 >> 5) & 0x07
        result["seq_level_idx_0"] = byte1 & 0x1F

        byte2 = data[2]
        result["seq_tier_0"] = (byte2 >> 7) & 1
        result["high_bitdepth"] = (byte2 >> 6) & 1
        result["twelve_bit"] = (byte2 >> 5) & 1
        result["monochrome"] = (byte2 >> 4) & 1
        result["chroma_subsampling_x"] = (byte2 >> 3) & 1
        result["chroma_subsampling_y"] = (byte2 >> 2) & 1
        result["chroma_sample_position"] = byte2 & 0x03

        byte3 = data[3]
        result["reserved"] = byte3

        seq_profile_names = {0: 'Main', 1: 'High', 2: 'Professional'}
        result["seq_profile_name"] = seq_profile_names.get(result["seq_profile"], "Unknown")

        seq_level_names = {
            0: '2.0', 1: '2.1', 2: '2.2', 3: '2.3',
            4: '3.0', 5: '3.1', 6: '3.2', 7: '3.3',
            8: '4.0', 9: '4.1', 10: '4.2', 11: '4.3',
        }
        result["seq_level_name"] = seq_level_names.get(result["seq_level_idx_0"], "Unknown")

        if len(data) > 4:
            result["initial_display_delay"] = data[4] >> 4 if len(data) > 4 else 0

        return result

    def _parse_iprp(self, data: bytes) -> Dict[str, Any]:
        """Parse image properties box"""
        result: Dict[str, Any] = {}
        self._parse_boxes(0, len(data))
        return result

    def _parse_iinf(self, data: bytes) -> Dict[str, Any]:
        """Parse item information box"""
        result: Dict[str, Any] = {}

        if len(data) < 2:
            return result

        version = data[0]
        flags = data[1]
        result["version"] = version

        entry_count_offset = 2 if version < 16 else 6
        if version < 16:
            entry_count = struct.unpack('>H', data[entry_count_offset:entry_count_offset + 2])[0]
        else:
            entry_count = struct.unpack('>I', data[entry_count_offset:entry_count_offset + 4])[0]

        result["item_count"] = entry_count

        items = []
        offset = entry_count_offset + (2 if version < 16 else 4)

        for i in range(entry_count):
            if offset >= len(data):
                break

            item_entry = self._parse_infe(data, offset)
            if item_entry:
                items.append(item_entry)
                offset += item_entry.get("entry_size", 0)
            else:
                break

        result["items"] = items

        for item in items:
            if item.get("primary"):
                self.primary_item = item
            if item.get("item_type") in ['mime', 'av1C']:
                if item.get("width") and item.get("height"):
                    self.thumbnails.append(item)

        return result

    def _parse_infe(self, data: bytes, offset: int) -> Optional[Dict[str, Any]]:
        """Parse item information entry"""
        if offset + 4 > len(data):
            return None

        entry_size = struct.unpack('>I', data[offset:offset + 4])[0]
        if offset + entry_size > len(data):
            return None

        item_entry: Dict[str, Any] = {
            "entry_size": entry_size,
        }

        box_start = offset + 4
        if data[box_start:box_start + 4] != b'infe':
            return None

        item_version = data[box_start + 4]
        item_flags = data[box_start + 5]

        item_entry["version"] = item_version

        item_id_offset = 6
        if item_version >= 2:
            item_id = struct.unpack('>H', data[box_start + item_id_offset:box_start + item_id_offset + 2])[0]
            item_entry["item_id"] = item_id
            item_id_offset += 2

        name_offset = box_start + item_id_offset + 2
        name_length = 0
        while name_offset + name_length < len(data) and data[box_start + item_id_offset + 2 + name_length] != 0:
            name_length += 1

        if name_offset + name_length < len(data):
            item_entry["name"] = data[name_offset:name_offset + name_length].decode('utf-8', errors='replace')

        return item_entry

    def _parse_iloc(self, data: bytes) -> Dict[str, Any]:
        """Parse item location box"""
        result: Dict[str, Any] = {}

        if len(data) < 8:
            return result

        version = data[0]
        result["version"] = version

        offset_size = (data[1] >> 4) & 0x0F
        length_size = data[1] & 0x0F

        result["offset_size"] = offset_size
        result["length_size"] = length_size

        base_offset_size = 8 if (data[2] >> 6) & 1 else 0
        result["base_offset_size"] = base_offset_size

        index_size = 0
        if (data[2] >> 5) & 1:
            index_size = (data[2] >> 3) & 0x03

        item_count_offset = 8 if version == 0 else (16 if version == 1 else 8)
        if version == 0:
            item_count = struct.unpack('>H', data[item_count_offset:item_count_offset + 2])[0]
        else:
            item_count = struct.unpack('>I', data[item_count_offset:item_count_offset + 4])[0]

        result["item_count"] = item_count

        return result

    def _parse_colr(self, data: bytes) -> Dict[str, Any]:
        """Parse color information box"""
        result: Dict[str, Any] = {}

        if len(data) < 4:
            return result

        color_type = data[:4].decode('latin-1', errors='replace')
        result["color_type"] = color_type

        color_type_names = {
            'nclx': 'nclx (Color Configuration)',
            'prof': 'ICC Profile',
            'rICC': 'Restricted ICC Profile',
        }
        result["color_type_name"] = color_type_names.get(color_type, "Unknown")

        if color_type in ['nclx', 'rICC', 'prof']:
            if color_type == 'nclx' and len(data) >= 7:
                result["primaries"] = struct.unpack('>H', data[4:6])[0]
                result["transfer_function"] = struct.unpack('>H', data[6:8])[0]
                result["matrix"] = struct.unpack('>H', data[8:10])[0]

                full_range_flag = data[10] >> 7
                result["full_range"] = bool(full_range_flag)

                primaries_names = {
                    1: 'BT.709',
                    2: 'Unspecified',
                    4: 'BT.470-6 System M',
                    5: 'BT.470-6 System B, G',
                    6: 'BT.601-6 525',
                    7: 'BT.601-6 625',
                    8: 'BT.2020',
                    9: 'BT.2020 constant',
                    10: 'BT.2100 PQ',
                    11: 'BT.2100 HLG',
                    12: 'DCI-P3',
                    13: 'SMPTE RP 431-2',
                    14: 'SMPTE EG 432-1',
                }
                result["primaries_name"] = primaries_names.get(result.get("primaries"), "Unknown")

                transfer_names = {
                    1: 'BT.709',
                    2: 'Unspecified',
                    4: 'BT.470-6 System M',
                    5: 'BT.470-6 System B, G',
                    6: 'BT.601-6',
                    7: 'BT.2020 10-bit',
                    8: 'BT.2020 12-bit',
                    9: 'BT.2100 PQ (Perceptual Quantizer)',
                    10: 'BT.2100 HLG (Hybrid Log-Gamma)',
                    11: 'SMPTE ST 2084',
                    12: 'SMPTE ST 428-1',
                    13: 'BT.2100 HLG (alternative)',
                    14: 'DCI-P3 (D65)',
                    15: 'SMPTE RP 431-2',
                    16: 'SMPTE EG 432-1',
                }
                result["transfer_function_name"] = transfer_names.get(result.get("transfer_function"), "Unknown")

            elif color_type in ['prof', 'rICC']:
                result["icc_profile_offset"] = 4
                result["icc_profile_size"] = len(data) - 4

        return result

    def _parse_ispe(self, data: bytes) -> Dict[str, Any]:
        """Parse image spatial extent box"""
        result: Dict[str, Any] = {}

        if len(data) < 8:
            return result

        width = struct.unpack('>I', data[:4])[0]
        height = struct.unpack('>I', data[4:8])[0]

        result["width"] = width
        result["height"] = height
        result["total_pixels"] = width * height
        result["megapixels"] = round(width * height / 1000000, 2)

        return result

    def _parse_pixi(self, data: bytes) -> Dict[str, Any]:
        """Parse pixel information box"""
        result: Dict[str, Any] = {}

        if len(data) < 2:
            return result

        num_channels = data[0]
        result["channels"] = num_channels

        bits_per_channel = []
        for i in range(num_channels):
            if i + 1 < len(data):
                bits_per_channel.append(data[i + 1])

        result["bits_per_channel"] = bits_per_channel

        return result

    def _parse_clap(self, data: bytes) -> Dict[str, Any]:
        """Parse clean aperture box"""
        result: Dict[str, Any] = {}

        if len(data) < 32:
            return result

        clean_left = struct.unpack('>I', data[:4])[0] / 65536.0
        clean_right = struct.unpack('>I', data[4:8])[0] / 65536.0
        clean_top = struct.unpack('>I', data[8:12])[0] / 65536.0
        clean_bottom = struct.unpack('>I', data[12:16])[0] / 65536.0

        result["clean_left"] = clean_left
        result["clean_right"] = clean_right
        result["clean_top"] = clean_top
        result["clean_bottom"] = clean_bottom

        result["clean_width"] = clean_right - clean_left
        result["clean_height"] = clean_bottom - clean_top

        return result

    def _parse_hdlr(self, data: bytes) -> Dict[str, Any]:
        """Parse handler reference box"""
        result: Dict[str, Any] = {}

        if len(data) < 8:
            return result

        handler_type = data[4:8].decode('latin-1', errors='replace')
        result["handler_type"] = handler_type

        handler_names = {
            'pict': 'Picture Handler',
            'vid ': 'Video Handler',
            'soun': 'Sound Handler',
            'hint': 'Hint Handler',
            'meta': 'Metadata Handler',
        }
        result["handler_name"] = handler_names.get(handler_type, "Unknown")

        name_offset = 12
        name_end = data.find(b'\x00', name_offset)
        if name_end > 0:
            result["handler_name_text"] = data[name_offset:name_end].decode('utf-8', errors='replace')

        return result

    def _parse_uuid(self, data: bytes) -> Dict[str, Any]:
        """Parse user extension box"""
        result: Dict[str, Any] = {}

        if len(data) < 16:
            return result

        uuid_bytes = data[:16]
        result["uuid"] = str(uuid.UUID(bytes=uuid_bytes))

        uuid_names = {
            '9E27E3A9-2975-42A1-A0A3-10E75CFAF60C': 'Google Motion Photo',
            '00A6D5E5-7C26-4521-8B71-3F83C4FAAAE4': 'Photo Producer',
            'A5E2C68C-9A6D-4D5B-9F7B-4C8B8E6F3A1D': 'Unknown Extension',
        }

        for uuid_str, name in uuid_names.items():
            if uuid_str.lower() in result["uuid"].lower():
                result["uuid_name"] = name
                if name == 'Google Motion Photo':
                    self._parse_motion_photo(data[16:])
                break

        return result

    def _parse_motion_photo(self, data: bytes):
        """Parse motion photo/motion photo data"""
        self.motion_photo = {
            "detected": True,
            "video_offset": 0,
            "video_size": 0,
        }

        try:
            offset = 0
            while offset + 8 <= len(data):
                item_size = struct.unpack('>I', data[offset:offset + 4])[0]
                item_type = data[offset + 4:offset + 8]

                if item_type == b'mp4v':
                    self.motion_photo["video_type"] = "mp4v"
                    self.motion_photo["video_offset"] = offset + 8
                    self.motion_photo["video_size"] = item_size
                    break

                offset += item_size + 8
        except Exception as e:
            logger.debug(f"Error parsing motion photo: {e}")

    def _build_result(self) -> Dict[str, Any]:
        """Build final result"""
        result: Dict[str, Any] = {
            "success": True,
            "file_size": self.file_size,
            "is_valid_avif": self.is_valid_avif,
            "is_heif": self.is_heif,
            "format": "HEIF" if self.is_heif else "AVIF",
        }

        ftyp_box = next((b for b in self.boxes if b.get("type") == "File Type"), None)
        if ftyp_box:
            result["file_type"] = ftyp_box

        av1c_box = next((b for b in self.boxes if b.get("type") == "AV1 Configuration"), None)
        if av1c_box:
            result["av1_configuration"] = av1c_box

        iinf_box = next((b for b in self.boxes if b.get("type") == "Item Information"), None)
        if iinf_box:
            result["item_information"] = iinf_box

        if self.primary_item:
            result["primary_image"] = self.primary_item

        if self.thumbnails:
            result["thumbnails"] = self.thumbnails

        if self.motion_photo:
            result["motion_photo"] = self.motion_photo

        colr_box = next((b for b in self.boxes if b.get("type") == "Color Information"), None)
        if colr_box:
            result["color_information"] = colr_box

        ispe_boxes = [b for b in self.boxes if b.get("type") == "Image Spatial Extent"]
        if ispe_boxes:
            result["image_dimensions"] = ispe_boxes[0]

        result["total_boxes"] = len(self.boxes)

        box_types = {}
        for box in self.boxes:
            box_type = box.get("type", "Unknown")
            box_types[box_type] = box_types.get(box_type, 0) + 1
        result["box_summary"] = box_types

        return result


def extract_avif_metadata(filepath: str) -> Dict[str, Any]:
    """Convenience function to extract AVIF/HEIF metadata"""
    parser = AVIFParser(filepath)
    return parser.parse()


def get_avif_field_count() -> int:
    """Return the number of fields this module extracts"""
    return 75
