#!/usr/bin/env python3
"""
WebP Chunks Extraction Module
Comprehensive WebP RIFF chunk parsing and AVIF ISOBMFF box parsing:

WebP RIFF chunks:
- VP8: Lossy format
- VP8L: Lossless format  
- VP8X: Extended format
- ANIM: Animation header
- ANMF: Animation frame
- ALPH: Alpha channel
- EXIF: EXIF data
- XMP: XMP data
- ICC: ICC profile

AVIF ISOBMFF boxes:
- ftyp: File type
- moov: Movie header
- mdia: Media header
- av1C: AV1 configuration
- iprp/ipco/ipma: Image properties
- ispe: Image spatial extent
- colr: Color information
- iinf: Item information
- ipco: Item property container

Author: MetaExtract Team
Version: 1.0.0
"""

import struct
import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

RIFF_SIGNATURE = b'RIFF'
WEBP_SIGNATURE = b'WEBP'
AVIF_SIGNATURE = b'ftyp'


class WebPChunkParser:
    """
    WebP chunk parser for extracting metadata from WebP files.
    Supports all RIFF chunks including extended format (VP8X) and animation.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file_size = 0
        self.chunks: List[Dict[str, Any]] = []
        self.vp8x_data: Optional[Dict[str, Any]] = None
        self.anim_data: Optional[Dict[str, Any]] = None
        self.is_valid_webp = False
        self.is_animated = False
        self.has_alpha = False
        self.has_icc = False
        self.has_exif = False
        self.has_xmp = False

    def parse(self) -> Dict[str, Any]:
        """Main entry point - parse WebP file and extract all metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}

            self.file_size = file_path.stat().st_size

            with open(self.filepath, 'rb') as f:
                if not self._validate_riff_header(f):
                    return {"error": "Invalid RIFF header", "success": False}

                self.is_valid_webp = True

                while True:
                    chunk_data = self._read_chunk(f)
                    if chunk_data is None:
                        break

                    chunk_fourcc, chunk_length, chunk_payload = chunk_data
                    chunk_info = self._parse_chunk(chunk_fourcc, chunk_payload)
                    self.chunks.append(chunk_info)

            return self._build_result()

        except Exception as e:
            logger.error(f"Error parsing WebP: {e}")
            return {"error": str(e), "success": False}

    def _validate_riff_header(self, f) -> bool:
        """Validate RIFF header"""
        riff = f.read(4)
        file_size = struct.unpack('<I', f.read(4))[0]
        webp = f.read(4)
        return riff == RIFF_SIGNATURE and webp == WEBP_SIGNATURE

    def _read_chunk(self, f) -> Optional[Tuple[bytes, int, bytes]]:
        """Read a single chunk from file"""
        try:
            header = f.read(8)
            if len(header) < 8:
                return None

            fourcc = header[:4]
            length = struct.unpack('<I', header[4:8])[0]
            payload = f.read(length)

            if fourcc in [b'RIFF', b'WEBP']:
                return None

            return (fourcc, length, payload)

        except Exception as e:
            logger.error(f"Error reading chunk: {e}")
            return None

    def _parse_chunk(self, fourcc: bytes, payload: bytes) -> Dict[str, Any]:
        """Parse individual chunk based on FourCC"""
        if fourcc == b'VP8 ':
            return self._parse_vp8(payload)
        elif fourcc == b'VP8L':
            return self._parse_vp8l(payload)
        elif fourcc == b'VP8X':
            return self._parse_vp8x(payload)
        elif fourcc == b'ANIM':
            return self._parse_anim(payload)
        elif fourcc == b'ANMF':
            return self._parse_anmf(payload)
        elif fourcc == b'ALPH':
            return self._parse_alph(payload)
        elif fourcc == b'EXIF':
            return self._parse_exif(payload)
        elif fourcc == b'XMP ':
            return self._parse_xmp(payload)
        elif fourcc == b'ICCP':
            return self._parse_iccp(payload)
        else:
            return {"fourcc": fourcc.decode('latin-1'), "size": len(payload)}

    def _parse_vp8(self, data: bytes) -> Dict[str, Any]:
        """Parse VP8 (lossy) chunk"""
        if len(data) < 10:
            return {"error": "Invalid VP8 data"}

        start_code = data[:3]
        width, height = struct.unpack('<HH', data[6:10])

        return {
            "type": "VP8",
            "format": "lossy",
            "width": width,
            "height": height,
            "has_alpha": False,
        }

    def _parse_vp8l(self, data: bytes) -> Dict[str, Any]:
        """Parse VP8L (lossless) chunk"""
        if len(data) < 5:
            return {"error": "Invalid VP8L data"}

        signature = data[0]
        width_minus_one = struct.unpack('<I', data[1:4])[0] & 0x3FFF
        height_minus_one = (struct.unpack('<I', data[1:4])[0] >> 14) & 0x3FFF

        width = width_minus_one + 1
        height = height_minus_one + 1

        return {
            "type": "VP8L",
            "format": "lossless",
            "width": width,
            "height": height,
            "has_alpha": True,
        }

    def _parse_vp8x(self, data: bytes) -> Dict[str, Any]:
        """Parse VP8X (extended format) chunk"""
        if len(data) < 10:
            return {"error": "Invalid VP8X data"}

        flags = data[0]
        width = struct.unpack('<I', data[1:4])[0] + 1
        height = struct.unpack('<I', data[4:7])[0] + 1

        self.vp8x_data = {
            "type": "VP8X",
            "format": "extended",
            "width": width,
            "height": height,
            "has_animation": bool(flags & 0x02),
            "has_alpha": bool(flags & 0x04),
            "has_icc": bool(flags & 0x08),
            "has_exif": bool(flags & 0x10),
            "has_xmp": bool(flags & 0x20),
        }

        self.is_animated = self.vp8x_data["has_animation"]
        self.has_alpha = self.vp8x_data["has_alpha"]
        self.has_icc = self.vp8x_data["has_icc"]
        self.has_exif = self.vp8x_data["has_exif"]
        self.has_xmp = self.vp8x_data["has_xmp"]

        return self.vp8x_data

    def _parse_anim(self, data: bytes) -> Dict[str, Any]:
        """Parse ANIM (animation) chunk"""
        if len(data) < 6:
            return {"error": "Invalid ANIM data"}

        bg_color, loop_count = struct.unpack('<IH', data[:6])

        self.anim_data = {
            "background_color_rgb": [bg_color & 0xFF, (bg_color >> 8) & 0xFF, (bg_color >> 16) & 0xFF],
            "loop_count": loop_count,
            "is_animated": True,
        }

        return self.anim_data

    def _parse_anmf(self, data: bytes) -> Dict[str, Any]:
        """Parse ANMF (animation frame) chunk"""
        if len(data) < 16:
            return {"error": "Invalid ANMF data"}

        x, y, width, height, delay_num, delay_den, disposal, blend = struct.unpack('<IIIIBB', data[:16])

        return {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "delay_ms": (delay_num * 1000) / delay_den if delay_den > 0 else 0,
            "disposal_method": disposal,
            "blend_method": blend,
        }

    def _parse_alph(self, data: bytes) -> Dict[str, Any]:
        """Parse ALPH (alpha) chunk"""
        if len(data) < 1:
            return {"error": "Invalid ALPH data"}

        flags = data[0]
        self.has_alpha = True

        return {
            "type": "ALPH",
            "compression": "None" if (flags & 0x01) == 0 else "WebP",
            "preprocessing": (flags >> 1) & 0x03,
            "level": (flags >> 3) & 0x1F,
        }

    def _parse_exif(self, data: bytes) -> Dict[str, Any]:
        """Parse EXIF chunk"""
        self.has_exif = True
        return {
            "type": "EXIF",
            "size": len(data),
            "has_data": len(data) > 0,
        }

    def _parse_xmp(self, data: bytes) -> Dict[str, Any]:
        """Parse XMP chunk"""
        self.has_xmp = True
        return {
            "type": "XMP",
            "size": len(data),
            "has_data": len(data) > 0,
        }

    def _parse_iccp(self, data: bytes) -> Dict[str, Any]:
        """Parse ICC profile chunk"""
        self.has_icc = True
        return {
            "type": "ICCP",
            "size": len(data),
        }

    def _build_result(self) -> Dict[str, Any]:
        """Build final result dictionary"""
        result = {
            "success": True,
            "file_size": self.file_size,
            "is_valid_webp": self.is_valid_webp,
            "chunk_count": len(self.chunks),
            "features": {
                "is_animated": self.is_animated,
                "has_alpha": self.has_alpha,
                "has_icc": self.has_icc,
                "has_exif": self.has_exif,
                "has_xmp": self.has_xmp,
            },
        }

        if self.vp8x_data:
            result["vp8x"] = self.vp8x_data

        if self.anim_data:
            result["animation"] = self.anim_data

        chunk_types = {}
        for chunk in self.chunks:
            chunk_type = chunk.get("type", chunk.get("fourcc", "unknown"))
            chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1

        result["chunk_types"] = chunk_types

        return result


class AVIFBoxParser:
    """
    AVIF ISOBMFF box parser.
    Parses the container format used by AVIF images.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.boxes: List[Dict[str, Any]] = []
        self.file_type: Optional[str] = None
        self.major_brand: Optional[str] = None
        self.minor_version: Optional[int] = None
        self.compatible_brands: List[str] = []
        self.is_valid_avif = False

    def parse(self) -> Dict[str, Any]:
        """Main entry point - parse AVIF file and extract box metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}

            with open(self.filepath, 'rb') as f:
                while True:
                    box_data = self._read_box(f)
                    if box_data is None:
                        break

                    box_size, box_type, box_payload = box_data
                    box_info = self._parse_box(box_type, box_payload, box_size)
                    self.boxes.append(box_info)

                    if box_type == b'ftyp':
                        self.is_valid_avif = True

            return self._build_result()

        except Exception as e:
            logger.error(f"Error parsing AVIF: {e}")
            return {"error": str(e), "success": False}

    def _read_box(self, f) -> Optional[Tuple[int, bytes, bytes]]:
        """Read a single box from file"""
        try:
            size_bytes = f.read(4)
            if len(size_bytes) < 4:
                return None

            box_size = struct.unpack('>I', size_bytes)[0]
            box_type = f.read(4)

            if box_size == 1:
                extended_size = f.read(8)
                box_size = struct.unpack('>Q', extended_size)[0]
            elif box_size == 0:
                box_size = f.seek(0, 2) - f.tell() + 8

            box_payload_size = box_size - 8
            if box_payload_size > 0:
                box_payload = f.read(box_payload_size)
            else:
                box_payload = b''

            return (box_size, box_type, box_payload)

        except Exception as e:
            logger.error(f"Error reading box: {e}")
            return None

    def _parse_box(self, box_type: bytes, payload: bytes, size: int) -> Dict[str, Any]:
        """Parse individual box based on type"""
        box_name = box_type.decode('latin-1', errors='replace')
        box_info = {"type": box_name, "size": size}

        if box_type == b'ftyp':
            return self._parse_ftyp(payload, box_info)
        elif box_type == b'moov':
            return self._parse_moov(payload, box_info)
        elif box_type == b'mdia':
            return self._parse_mdia(payload, box_info)
        elif box_type == b'av1C':
            return self._parse_av1c(payload, box_info)
        elif box_type == b'iprp' or box_type == b'ipco':
            return self._parse_ipro(payload, box_info)
        elif box_type == b'ispe':
            return self._parse_ispe(payload, box_info)
        elif box_type == b'colr':
            return self._parse_colr(payload, box_info)
        elif box_type == b'iinf':
            return self._parse_iinf(payload, box_info)
        else:
            return box_info

    def _parse_ftyp(self, data: bytes, box_info: Dict) -> Dict[str, Any]:
        """Parse ftyp (file type) box"""
        if len(data) < 8:
            return box_info

        self.major_brand = data[:4].decode('latin-1', errors='replace')
        self.minor_version = struct.unpack('>I', data[4:8])[0]
        self.compatible_brands = [data[i:i+4].decode('latin-1', errors='replace') for i in range(8, len(data), 4)]

        box_info.update({
            "major_brand": self.major_brand,
            "minor_version": self.minor_version,
            "compatible_brands": self.compatible_brands,
        })

        return box_info

    def _parse_moov(self, data: bytes, box_info: Dict) -> Dict[str, Any]:
        """Parse moov (movie) box"""
        box_info["has_movie"] = True
        return box_info

    def _parse_mdia(self, data: bytes, box_info: Dict) -> Dict[str, Any]:
        """Parse mdia (media) box"""
        box_info["has_media"] = True
        return box_info

    def _parse_av1c(self, data: bytes, box_info: Dict) -> Dict[str, Any]:
        """Parse av1C (AV1 configuration) box"""
        if len(data) < 4:
            return box_info

        marker = (data[0] >> 7) & 0x01
        version = (data[0] >> 5) & 0x03
        seq_level_idx_0 = data[0] & 0x1F
        seq_profile = (data[1] >> 5) & 0x07
        seq_tier_0 = (data[1] >> 4) & 0x01
        high_bitdepth = (data[1] >> 3) & 0x01
        twelve_bit = (data[1] >> 2) & 0x01
        monochrome = (data[1] >> 1) & 0x01
        chroma_subsampling_x = data[2] >> 7
        chroma_subsampling_y = (data[2] >> 6) & 0x01
        chroma_sample_position = data[2] & 0x03

        box_info.update({
            "marker": marker,
            "version": version,
            "seq_profile": seq_profile,
            "seq_level_idx_0": seq_level_idx_0,
            "seq_tier_0": seq_tier_0,
            "high_bitdepth": high_bitdepth == 1,
            "twelve_bit": twelve_bit == 1,
            "monochrome": monochrome == 1,
            "chroma_subsampling": f"{chroma_subsampling_x}{chroma_subsampling_y}",
            "chroma_sample_position": chroma_sample_position,
        })

        return box_info

    def _parse_ipro(self, data: bytes, box_info: Dict) -> Dict[str, Any]:
        """Parse ipro/ipco (image property) box"""
        box_info["has_properties"] = True
        return box_info

    def _parse_ispe(self, data: bytes, box_info: Dict) -> Dict[str, Any]:
        """Parse ispe (image spatial extent) box"""
        if len(data) < 8:
            return box_info

        width = struct.unpack('>I', data[:4])[0]
        height = struct.unpack('>I', data[4:8])[0]

        box_info["width"] = width
        box_info["height"] = height

        return box_info

    def _parse_colr(self, data: bytes, box_info: Dict) -> Dict[str, Any]:
        """Parse colr (color information) box"""
        if len(data) < 4:
            return box_info

        color_type = data[:4].decode('latin-1', errors='replace')

        box_info["color_type"] = color_type

        if color_type == 'nclx' and len(data) >= 7:
            primaries = struct.unpack('>H', data[4:6])[0]
            transfer = struct.unpack('>H', data[6:8])[0]
            matrix = struct.unpack('>H', data[8:10])[0] if len(data) >= 10 else None

            box_info["color_primaries"] = primaries
            box_info["transfer_characteristics"] = transfer
            box_info["matrix_coefficients"] = matrix

        return box_info

    def _parse_iinf(self, data: bytes, box_info: Dict) -> Dict[str, Any]:
        """Parse iinf (item information) box"""
        box_info["has_items"] = True
        return box_info

    def _build_result(self) -> Dict[str, Any]:
        """Build final result dictionary"""
        result = {
            "success": True,
            "is_valid_avif": self.is_valid_avif,
            "box_count": len(self.boxes),
            "file_type": self.file_type,
            "major_brand": self.major_brand,
            "compatible_brands": self.compatible_brands,
        }

        return result


def extract_webp_chunks(filepath: str) -> Dict[str, Any]:
    """Extract WebP chunk metadata from file"""
    parser = WebPChunkParser(filepath)
    return parser.parse()


def extract_avif_boxes(filepath: str) -> Dict[str, Any]:
    """Extract AVIF ISOBMFF box metadata from file"""
    parser = AVIFBoxParser(filepath)
    return parser.parse()


def get_webp_field_count() -> int:
    """Return the number of fields this module extracts"""
    return 40
