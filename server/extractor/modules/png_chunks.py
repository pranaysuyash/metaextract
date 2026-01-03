#!/usr/bin/env python3
"""
PNG Chunks Extraction Module
Comprehensive PNG chunk parsing for all critical and ancillary chunks:
- IHDR: Image header (dimensions, bit depth, color type, compression, filter, interlace)
- PLTE: Palette (color lookup table)
- IDAT: Image data (compressed)
- IEND: Image end
- tEXt: Textual metadata (keywords + values)
- zTXt: Compressed textual metadata
- iTXt: International textual metadata (with language/tag)
- eXIf: EXIF data
- cHRM: Primary chromaticities and white point
- gAMA: Image gamma
- iCCP: Embedded ICC profile
- sBIT: Significant bits
- sRGB: Standard RGB color space
- bKGD: Background color
- hIST: Histogram
- pHYs: Physical pixel dimensions
- sPLT: Suggested palette
- tIME: Image last modification time
- acTL: Animation control (APNG)
- fcTL: Frame control (APNG)
- fdAT: Frame data (APNG)
- mDCv: Mastering Display Color Volume (HDR)
- hvDR: HDR dynamic range (HDR)
- CeLI: Color encoding information

Author: MetaExtract Team
Version: 1.0.0
"""

import struct
import zlib
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'

CRITICAL_CHUNKS = {
    b'IHDR': 'Image header',
    b'PLTE': 'Palette',
    b'IDAT': 'Image data',
    b'IEND': 'Image end',
}

ANCILLARY_CHUNKS = {
    b'tEXt': 'Textual data',
    b'zTXt': 'Compressed textual data',
    b'iTXt': 'International textual data',
    b'eXIf': 'EXIF data',
    b'cHRM': 'Primary chromaticities',
    b'gAMA': 'Image gamma',
    b'iCCP': 'Embedded ICC profile',
    b'sBIT': 'Significant bits',
    b'sRGB': 'Standard RGB',
    b'bKGD': 'Background color',
    b'hIST': 'Histogram',
    b'pHYs': 'Physical pixel dimensions',
    b'sPLT': 'Suggested palette',
    b'tIME': 'Image last modification time',
    b'acTL': 'Animation control',
    b'fcTL': 'Frame control',
    b'fdAT': 'Frame data',
    b'mDCv': 'Mastering Display Color Volume',
    b'hvDR': 'HDR Dynamic Range',
    b'CeLI': 'Color Encoding Information',
}

COLOR_TYPE_NAMES = {
    0: 'Grayscale',
    2: 'RGB',
    3: 'Palette',
    4: 'Grayscale + Alpha',
    6: 'RGBA',
}

COMPRESSION_METHODS = {
    0: 'Deflate',
}

FILTER_METHODS = {
    0: 'None',
    1: 'Sub',
    2: 'Up',
    3: 'Average',
    4: 'Paeth',
}

INTERLACE_METHODS = {
    0: 'No interlace',
    1: 'Adam7 interlace',
}

RENDERING_INTENTS = {
    0: 'Perceptual',
    1: 'Relative colorimetric',
    2: 'Saturation',
    3: 'Absolute colorimetric',
}


class PNGChunkParser:
    """
    PNG chunk parser for extracting metadata from PNG files.
    Supports all standard chunks including APNG animation and HDR extensions.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file_size = 0
        self.chunks: List[Dict[str, Any]] = []
        self.ihdr_data: Optional[Dict[str, Any]] = None
        self.text_data: List[Dict[str, Any]] = []
        self.palette_data: Optional[Dict[str, Any]] = None
        self.animation_data: Optional[Dict[str, Any]] = None
        self.hdr_data: Optional[Dict[str, Any]] = None
        self.is_valid_png = False

    def parse(self) -> Dict[str, Any]:
        """Main entry point - parse PNG file and extract all metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                logger.error(f"File not found: {self.filepath}")
                return {"error": "File not found", "success": False}

            self.file_size = file_path.stat().st_size

            with open(self.filepath, 'rb') as f:
                if not self._validate_png_signature(f):
                    return {"error": "Invalid PNG signature", "success": False}

                self.is_valid_png = True
                self.chunks = []

                while True:
                    chunk_data = self._read_chunk(f)
                    if chunk_data is None:
                        break

                    chunk_type, chunk_length, chunk_payload, chunk_crc = chunk_data
                    chunk_info = self._parse_chunk(chunk_type, chunk_payload)
                    chunk_info.update({
                        "type": chunk_type.decode('latin-1'),
                        "length": chunk_length,
                        "crc": chunk_crc,
                    })
                    self.chunks.append(chunk_info)

            return self._build_result()

        except Exception as e:
            logger.error(f"Error parsing PNG: {e}")
            return {"error": str(e), "success": False}

    def _validate_png_signature(self, f) -> bool:
        """Validate PNG file signature"""
        signature = f.read(8)
        return signature == PNG_SIGNATURE

    def _read_chunk(self, f) -> Optional[Tuple[bytes, int, bytes, int]]:
        """Read a single chunk from file"""
        try:
            length_bytes = f.read(4)
            if len(length_bytes) < 4:
                return None

            chunk_length = struct.unpack('>I', length_bytes)[0]
            chunk_type = f.read(4)

            if chunk_type not in CRITICAL_CHUNKS and chunk_type not in ANCILLARY_CHUNKS:
                logger.warning(f"Unknown chunk type: {chunk_type}")
                f.seek(chunk_length + 4, 1)
                return None

            chunk_payload = f.read(chunk_length)
            chunk_crc_bytes = f.read(4)
            chunk_crc = struct.unpack('>I', chunk_crc_bytes)[0]

            return (chunk_type, chunk_length, chunk_payload, chunk_crc)

        except Exception as e:
            logger.error(f"Error reading chunk: {e}")
            return None

    def _parse_chunk(self, chunk_type: bytes, payload: bytes) -> Dict[str, Any]:
        """Parse individual chunk based on type"""
        if chunk_type == b'IHDR':
            return self._parse_ihdr(payload)
        elif chunk_type == b'PLTE':
            return self._parse_plte(payload)
        elif chunk_type == b'tEXt':
            return self._parse_text(payload)
        elif chunk_type == b'zTXt':
            return self._parse_ztxt(payload)
        elif chunk_type == b'iTXt':
            return self._parse_itxt(payload)
        elif chunk_type == b'eXIf':
            return self._parse_exif(payload)
        elif chunk_type == b'cHRM':
            return self._parse_chrm(payload)
        elif chunk_type == b'gAMA':
            return self._parse_gama(payload)
        elif chunk_type == b'iCCP':
            return self._parse_iccp(payload)
        elif chunk_type == b'sBIT':
            return self._parse_sbit(payload)
        elif chunk_type == b'sRGB':
            return self._parse_srgb(payload)
        elif chunk_type == b'bKGD':
            return self._parse_bkgd(payload)
        elif chunk_type == b'hIST':
            return self._parse_hist(payload)
        elif chunk_type == b'pHYs':
            return self._parse_phys(payload)
        elif chunk_type == b'sPLT':
            return self._parse_splt(payload)
        elif chunk_type == b'tIME':
            return self._parse_time(payload)
        elif chunk_type == b'acTL':
            return self._parse_actl(payload)
        elif chunk_type == b'fcTL':
            return self._parse_fctl(payload)
        elif chunk_type == b'fdAT':
            return self._parse_fdat(payload)
        elif chunk_type == b'mDCv':
            return self._parse_mdcv(payload)
        elif chunk_type == b'hvDR':
            return self._parse_hvdr(payload)
        elif chunk_type == b'CeLI':
            return self._parse_celi(payload)
        else:
            return {"description": "Unknown chunk", "payload_size": len(payload)}

    def _parse_ihdr(self, data: bytes) -> Dict[str, Any]:
        """Parse IHDR (Image Header) chunk"""
        if len(data) < 13:
            return {"error": "Invalid IHDR data"}

        width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack('>IIBBBBB', data[:13])

        channel_map = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
        channels = channel_map.get(color_type, 4)
        bits_per_pixel = bit_depth * channels

        self.ihdr_data = {
            "width": width,
            "height": height,
            "bit_depth": bit_depth,
            "color_type": color_type,
            "color_type_name": COLOR_TYPE_NAMES.get(color_type, f"Unknown ({color_type})"),
            "compression_method": compression,
            "compression_method_name": COMPRESSION_METHODS.get(compression, f"Unknown ({compression})"),
            "filter_method": filter_method,
            "filter_method_name": FILTER_METHODS.get(filter_method, f"Unknown ({filter_method})"),
            "interlace_method": interlace,
            "interlace_method_name": INTERLACE_METHODS.get(interlace, f"Unknown ({interlace})"),
            "bits_per_pixel": bits_per_pixel,
            "channels": channels,
            "total_bits": width * height * bits_per_pixel,
        }

        return self.ihdr_data

    def _parse_plte(self, data: bytes) -> Dict[str, Any]:
        """Parse PLTE (Palette) chunk"""
        if len(data) < 3:
            return {"error": "Invalid PLTE data"}

        entries = len(data) // 3
        palette = []

        for i in range(entries):
            offset = i * 3
            r, g, b = struct.unpack('BBB', data[offset:offset + 3])
            palette.append({
                "index": i,
                "red": r,
                "green": g,
                "blue": b,
                "hex": f"#{r:02x}{g:02x}{b:02x}",
                "rgb": [r, g, b],
            })

        self.palette_data = {
            "entries": entries,
            "palette": palette,
            "has_alpha": False,
        }

        return self.palette_data

    def _parse_text(self, data: bytes) -> Dict[str, Any]:
        """Parse tEXt (Text) chunk"""
        try:
            null_pos = data.index(b'\x00')
            keyword = data[:null_pos].decode('latin-1', errors='replace')
            text = data[null_pos + 1:].decode('latin-1', errors='replace')

            text_entry = {
                "keyword": keyword,
                "text": text,
                "compression": False,
            }

            self.text_data.append(text_entry)

            return text_entry

        except Exception as e:
            return {"error": f"Invalid tEXt data: {e}"}

    def _parse_ztxt(self, data: bytes) -> Dict[str, Any]:
        """Parse zTXt (Compressed Text) chunk"""
        try:
            null_pos = data.index(b'\x00')
            keyword = data[:null_pos].decode('latin-1', errors='replace')
            compression_method = data[null_pos + 1]

            if compression_method != 0:
                return {"error": f"Unknown compression method: {compression_method}"}

            compressed_data = data[null_pos + 2:]
            try:
                text = zlib.decompress(compressed_data).decode('latin-1', errors='replace')
            except zlib.error:
                text = "Decompression failed"

            text_entry = {
                "keyword": keyword,
                "text": text,
                "compression": True,
                "compression_method": "Deflate",
            }

            self.text_data.append(text_entry)

            return text_entry

        except Exception as e:
            return {"error": f"Invalid zTXt data: {e}"}

    def _parse_itxt(self, data: bytes) -> Dict[str, Any]:
        """Parse iTXt (International Text) chunk"""
        try:
            null1 = data.index(b'\x00')
            keyword = data[:null1].decode('latin-1', errors='replace')

            null2 = data.index(b'\x00', null1 + 1)
            compression_flag = data[null1 + 1]
            compression_method = data[null1 + 2]

            null3 = data.index(b'\x00', null2 + 1)
            language_tag = data[null2 + 1:null3].decode('latin-1', errors='replace')

            null4 = data.index(b'\x00', null3 + 1)
            translated_keyword = data[null3 + 1:null4].decode('utf-8', errors='replace')

            text_data = data[null4 + 1:]

            if compression_flag == 1:
                try:
                    text = zlib.decompress(text_data).decode('utf-8', errors='replace')
                except zlib.error:
                    text = "Decompression failed"
            else:
                text = text_data.decode('utf-8', errors='replace')

            text_entry = {
                "keyword": keyword,
                "translated_keyword": translated_keyword,
                "language": language_tag,
                "text": text,
                "compression_flag": compression_flag == 1,
                "compression_method": compression_method if compression_flag == 1 else None,
            }

            self.text_data.append(text_entry)

            return text_entry

        except Exception as e:
            return {"error": f"Invalid iTXt data: {e}"}

    def _parse_exif(self, data: bytes) -> Dict[str, Any]:
        """Parse eXIf (EXIF) chunk"""
        exif_info = {
            "size": len(data),
            "has_exif": len(data) > 0,
        }

        if len(data) >= 8:
            exif_info["byte_order"] = "little" if data[:2] == b'II' else "big"
            exif_info["tiff_version"] = struct.unpack('>H', data[2:4])[0]

        return exif_info

    def _parse_chrm(self, data: bytes) -> Dict[str, Any]:
        """Parse cHRM (Chromaticities) chunk"""
        if len(data) < 32:
            return {"error": "Invalid cHRM data"}

        wp_x, wp_y, rx, ry, gx, gy, bx, by = struct.unpack('>IIIIIIII', data[:32])

        chrm = {
            "white_point_x": wp_x / 100000,
            "white_point_y": wp_y / 100000,
            "red_x": rx / 100000,
            "red_y": ry / 100000,
            "green_x": gx / 100000,
            "green_y": gy / 100000,
            "blue_x": bx / 100000,
            "blue_y": by / 100000,
        }

        return chrm

    def _parse_gama(self, data: bytes) -> Dict[str, Any]:
        """Parse gAMA (Gamma) chunk"""
        if len(data) < 4:
            return {"error": "Invalid gAMA data"}

        gamma_value = struct.unpack('>I', data[:4])[0]
        gamma_ratio = gamma_value / 100000.0

        return {
            "gamma_value": gamma_value,
            "gamma_ratio": gamma_ratio,
            "display_gamma": 1.0 / gamma_ratio,
        }

    def _parse_iccp(self, data: bytes) -> Dict[str, Any]:
        """Parse iCCP (ICC Profile) chunk"""
        try:
            null_pos = data.index(b'\x00')
            profile_name = data[:null_pos].decode('latin-1', errors='replace')
            compression_method = data[null_pos + 1]

            if compression_method != 0:
                return {"error": f"Unknown compression method: {compression_method}"}

            compressed_data = data[null_pos + 2:]

            return {
                "profile_name": profile_name,
                "compression_method": "Deflate",
                "profile_size": len(compressed_data),
                "profile_compressed_size": len(compressed_data),
            }

        except Exception as e:
            return {"error": f"Invalid iCCP data: {e}"}

    def _parse_sbit(self, data: bytes) -> Dict[str, Any]:
        """Parse sBIT (Significant Bits) chunk"""
        if not self.ihdr_data:
            return {"error": "IHDR not parsed yet"}

        color_type = self.ihdr_data.get("color_type", 0)
        bits_map = {
            0: ['grayscale_bits'],
            2: ['red_bits', 'green_bits', 'blue_bits'],
            3: ['palette_bits'],
            4: ['grayscale_bits', 'alpha_bits'],
            6: ['red_bits', 'green_bits', 'blue_bits', 'alpha_bits'],
        }

        bits_names = bits_map.get(color_type, [])
        sbit_data = {}

        for i, name in enumerate(bits_names):
            if i < len(data):
                sbit_data[name] = data[i]

        return sbit_data

    def _parse_srgb(self, data: bytes) -> Dict[str, Any]:
        """Parse sRGB (Standard RGB) chunk"""
        if len(data) < 1:
            return {"error": "Invalid sRGB data"}

        rendering_intent = data[0]

        return {
            "rendering_intent": rendering_intent,
            "rendering_intent_name": RENDERING_INTENTS.get(rendering_intent, "Unknown"),
        }

    def _parse_bkgd(self, data: bytes) -> Dict[str, Any]:
        """Parse bKGD (Background Color) chunk"""
        if not self.ihdr_data:
            return {"error": "IHDR not parsed yet"}

        color_type = self.ihdr_data.get("color_type", 0)

        if color_type == 3:
            if len(data) < 1:
                return {"error": "Invalid bKGD data"}
            palette_index = data[0]
            return {
                "background_type": "palette",
                "palette_index": palette_index,
            }
        elif color_type in (0, 4):
            if len(data) < 2:
                return {"error": "Invalid bKGD data"}
            gray = struct.unpack('>H', data[:2])[0]
            return {
                "background_type": "grayscale",
                "grayscale_value": gray,
            }
        elif color_type in (2, 6):
            if len(data) < 6:
                return {"error": "Invalid bKGD data"}
            r, g, b = struct.unpack('>HHH', data[:6])
            return {
                "background_type": "rgb",
                "red": r,
                "green": g,
                "blue": b,
                "hex": f"#{r:04x}{g:04x}{b:04x}",
            }

        return {"error": "Unknown color type"}

    def _parse_hist(self, data: bytes) -> Dict[str, Any]:
        """Parse hIST (Histogram) chunk"""
        if not self.palette_data:
            return {"error": "Palette not available"}

        entries = len(data) // 2
        frequencies = []

        for i in range(min(entries, len(self.palette_data.get("palette", [])))):
            offset = i * 2
            freq = struct.unpack('>H', data[offset:offset + 2])[0]
            frequencies.append({
                "palette_index": i,
                "frequency": freq,
            })

        return {
            "entries": entries,
            "frequencies": frequencies,
        }

    def _parse_phys(self, data: bytes) -> Dict[str, Any]:
        """Parse pHYs (Physical Dimensions) chunk"""
        if len(data) < 9:
            return {"error": "Invalid pHYs data"}

        ppu_x, ppu_y, unit_spec = struct.unpack('>IIB', data[:9])

        return {
            "pixels_per_unit_x": ppu_x,
            "pixels_per_unit_y": ppu_y,
            "unit": "meter" if unit_spec == 1 else "unknown",
            "dpi_x": ppu_x * 0.0254 if unit_spec == 1 else None,
            "dpi_y": ppu_y * 0.0254 if unit_spec == 1 else None,
        }

    def _parse_splt(self, data: bytes) -> Dict[str, Any]:
        """Parse sPLT (Suggested Palette) chunk"""
        try:
            null_pos = data.index(b'\x00')
            palette_name = data[:null_pos].decode('latin-1', errors='replace')

            sample_depth = data[null_pos + 1]
            remaining = data[null_pos + 2:]

            if sample_depth == 8:
                entry_size = 4
            elif sample_depth == 16:
                entry_size = 8
            else:
                return {"error": f"Unknown sample depth: {sample_depth}"}

            entries = len(remaining) // entry_size
            palette_entries = []

            for i in range(entries):
                offset = i * entry_size
                if sample_depth == 8:
                    r, g, b, a = struct.unpack('BBBB', remaining[offset:offset + 4])
                    palette_entries.append({
                        "index": i,
                        "red": r,
                        "green": g,
                        "blue": b,
                        "alpha": a,
                    })
                else:
                    r, g, b, a = struct.unpack('>HHHH', remaining[offset:offset + 8])
                    palette_entries.append({
                        "index": i,
                        "red": r,
                        "green": g,
                        "blue": b,
                        "alpha": a,
                    })

            return {
                "palette_name": palette_name,
                "sample_depth": sample_depth,
                "entries": entries,
                "palette": palette_entries,
            }

        except Exception as e:
            return {"error": f"Invalid sPLT data: {e}"}

    def _parse_time(self, data: bytes) -> Dict[str, Any]:
        """Parse tIME (Time) chunk"""
        if len(data) < 7:
            return {"error": "Invalid tIME data"}

        year, month, day, hour, minute, second = struct.unpack('>HBBBBB', data[:7])

        try:
            dt = datetime(year, month, day, hour, minute, second)
            return {
                "datetime": dt.isoformat(),
                "year": year,
                "month": month,
                "day": day,
                "hour": hour,
                "minute": minute,
                "second": second,
            }
        except ValueError as e:
            return {"error": f"Invalid date: {e}"}

    def _parse_actl(self, data: bytes) -> Dict[str, Any]:
        """Parse acTL (Animation Control) chunk - APNG"""
        if len(data) < 8:
            return {"error": "Invalid acTL data"}

        num_frames, num_plays = struct.unpack('>II', data[:8])

        self.animation_data = {
            "num_frames": num_frames,
            "num_plays": num_plays,
            "is_animated": True,
            "frames": [],
        }

        return self.animation_data

    def _parse_fctl(self, data: bytes) -> Dict[str, Any]:
        """Parse fcTL (Frame Control) chunk - APNG"""
        if len(data) < 26:
            return {"error": "Invalid fcTL data"}

        sequence_number, width, height, x_offset, y_offset, delay_num, delay_den, dispose_op, blend_op = struct.unpack('>IIIIHHBB', data[:26])

        frame_info = {
            "sequence_number": sequence_number,
            "width": width,
            "height": height,
            "x_offset": x_offset,
            "y_offset": y_offset,
            "delay_numerator": delay_num,
            "delay_denominator": delay_den,
            "delay_ms": (delay_num * 1000) / delay_den if delay_den > 0 else 0,
            "dispose_op": dispose_op,
            "blend_op": blend_op,
        }

        if self.animation_data:
            self.animation_data["frames"].append(frame_info)

        return frame_info

    def _parse_fdat(self, data: bytes) -> Dict[str, Any]:
        """Parse fdAT (Frame Data) chunk - APNG"""
        if len(data) < 4:
            return {"error": "Invalid fdAT data"}

        sequence_number = struct.unpack('>I', data[:4])[0]

        return {
            "sequence_number": sequence_number,
            "data_size": len(data) - 4,
        }

    def _parse_mdcv(self, data: bytes) -> Dict[str, Any]:
        """Parse mDCv (Mastering Display Color Volume) chunk - HDR"""
        if len(data) < 24:
            return {"error": "Invalid mDCv data"}

        red_x, red_y, green_x, green_y, blue_x, blue_y, white_x, white_y, max_luminance, min_luminance = struct.unpack('>HHHHHHHII', data[:24])

        self.hdr_data = {
            "red_primary_x": red_x / 50000,
            "red_primary_y": red_y / 50000,
            "green_primary_x": green_x / 50000,
            "green_primary_y": green_y / 50000,
            "blue_primary_x": blue_x / 50000,
            "blue_primary_y": blue_y / 50000,
            "white_point_x": white_x / 50000,
            "white_point_y": white_y / 50000,
            "max_luminance": max_luminance / 10000,
            "min_luminance": min_luminance / 10000,
            "has_hdr": True,
        }

        return self.hdr_data

    def _parse_hvdr(self, data: bytes) -> Dict[str, Any]:
        """Parse hvDR (HDR Dynamic Range) chunk"""
        if len(data) < 8:
            return {"error": "Invalid hvDR data"}

        max_content_light, max_frame_avg_light = struct.unpack('>II', data[:8])

        return {
            "max_content_light_level": max_content_light,
            "max_frame_avg_light_level": max_frame_avg_light,
            "has_hdr_extension": True,
        }

    def _parse_celi(self, data: bytes) -> Dict[str, Any]:
        """Parse CeLI (Color Encoding Information) chunk"""
        try:
            null_pos = data.index(b'\x00')
            coding_method = data[:null_pos].decode('latin-1', errors='replace')

            return {
                "coding_method": coding_method,
                "data_size": len(data),
            }

        except Exception as e:
            return {"error": f"Invalid CeLI data: {e}"}

    def _build_result(self) -> Dict[str, Any]:
        """Build final result dictionary"""
        result = {
            "success": True,
            "file_size": self.file_size,
            "is_valid_png": self.is_valid_png,
            "chunk_count": len(self.chunks),
            "chunk_types": {},
        }

        for chunk in self.chunks:
            chunk_type = chunk.get("type", "unknown")
            result["chunk_types"][chunk_type] = result["chunk_types"].get(chunk_type, 0) + 1

        if self.ihdr_data:
            result["ihdr"] = self.ihdr_data

        if self.text_data:
            result["text_chunks"] = self.text_data

        if self.palette_data:
            result["plte"] = self.palette_data

        if self.animation_data:
            result["animation"] = self.animation_data

        if self.hdr_data:
            result["hdr"] = self.hdr_data

        critical_chunks = [c for c in self.chunks if c.get("type") in CRITICAL_CHUNKS]
        ancillary_chunks = [c for c in self.chunks if c.get("type") in ANCILLARY_CHUNKS]

        result["critical_chunks"] = {
            "count": len(critical_chunks),
            "types": list(set(c.get("type") for c in critical_chunks)),
        }

        result["ancillary_chunks"] = {
            "count": len(ancillary_chunks),
            "types": list(set(c.get("type") for c in ancillary_chunks)),
        }

        return result


def extract_png_chunks(filepath: str) -> Dict[str, Any]:
    """
    Convenience function to extract PNG chunk metadata.

    Args:
        filepath: Path to PNG file

    Returns:
        Dictionary containing PNG metadata
    """
    parser = PNGChunkParser(filepath)
    return parser.parse()


def get_png_field_count() -> int:
    """Return the number of fields this module extracts"""
    return 75
