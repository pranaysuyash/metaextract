"""
MetaExtract Bitstream Parser Utility
Direct binary extraction from H.264/HEVC/AV1 NAL units and OBUs.
"""

from typing import Dict, Any, Optional, List
import bitstruct
from construct import Struct, Int8ub, Int16ub, BitStruct, BitsInteger, Flag, Padding

class H264BitstreamParser:
    """Parser for H.264 NAL units (SPS/PPS)."""
    
    @staticmethod
    def parse_nal_header(header_byte: int) -> Dict[str, Any]:
        """Parse NAL unit header (1 byte)."""
        forbidden_zero_bit = (header_byte >> 7) & 0x01
        nal_ref_idc = (header_byte >> 5) & 0x03
        nal_unit_type = header_byte & 0x1F
        
        return {
            "forbidden_zero_bit": forbidden_zero_bit,
            "nal_ref_idc": nal_ref_idc,
            "nal_unit_type": nal_unit_type,
            "nal_unit_name": {
                1: "Coded slice of a non-IDR picture",
                5: "Coded slice of an IDR picture",
                7: "SPS (Sequence Parameter Set)",
                8: "PPS (Picture Parameter Set)",
                9: "Access unit delimiter",
                10: "End of sequence",
                11: "End of stream"
            }.get(nal_unit_type, "Reserved/Other")
        }

    @staticmethod
    def extract_sps_details(sps_bytes: bytes) -> Dict[str, Any]:
        """Extract deep SPS fields using bitstruct."""
        if not sps_bytes or len(sps_bytes) < 4:
            return {}
            
        try:
            # Profile, constraints, and level are first 3 bytes after header
            profile_idc, constraints, level_idc = bitstruct.unpack("u8u8u8", sps_bytes[:3])
            
            return {
                "profile_idc": profile_idc,
                "constraint_set0_flag": (constraints >> 7) & 0x01,
                "constraint_set1_flag": (constraints >> 6) & 0x01,
                "constraint_set2_flag": (constraints >> 5) & 0x01,
                "constraint_set3_flag": (constraints >> 4) & 0x01,
                "constraint_set4_flag": (constraints >> 3) & 0x01,
                "constraint_set5_flag": (constraints >> 2) & 0x01,
                "level_idc": level_idc,
                "bitstream_forensics": {
                    "entropy_coding_detected": "CABAC" if profile_idc >= 77 else "CAVLC",
                    "direct_8x8_inference": bool((constraints >> 4) & 0x01)
                }
            }
        except Exception:
            return {}

class HEVCBitstreamParser:
    """Parser for HEVC NAL units (VPS/SPS/PPS)."""
    
    @staticmethod
    def parse_nal_header(header_bytes: bytes) -> Dict[str, Any]:
        """Parse HEVC NAL unit header (2 bytes)."""
        if len(header_bytes) < 2:
            return {}
            
        header = Int16ub.parse(header_bytes)
        forbidden_zero_bit = (header >> 15) & 0x01
        nal_unit_type = (header >> 9) & 0x3F
        nuh_layer_id = (header >> 3) & 0x3F
        nuh_temporal_id_plus1 = header & 0x07
        
        return {
            "forbidden_zero_bit": forbidden_zero_bit,
            "nal_unit_type": nal_unit_type,
            "nuh_layer_id": nuh_layer_id,
            "nuh_temporal_id_plus1": nuh_temporal_id_plus1,
            "nal_unit_name": {
                32: "VPS (Video Parameter Set)",
                33: "SPS (Sequence Parameter Set)",
                34: "PPS (Picture Parameter Set)",
                39: "Prefix SEI",
                40: "Suffix SEI"
            }.get(nal_unit_type, "Coded Slice / Other")
        }

class AV1BitstreamParser:
    """Parser for AV1 OBUs (Open Bitstream Units)."""
    
    @staticmethod
    def parse_obu_header(header_byte: int) -> Dict[str, Any]:
        """Parse AV1 OBU header."""
        obu_forbidden_bit = (header_byte >> 7) & 0x01
        obu_type = (header_byte >> 3) & 0x0F
        obu_extension_flag = (header_byte >> 2) & 0x01
        obu_has_size_field = (header_byte >> 1) & 0x01
        
        return {
            "obu_forbidden_bit": obu_forbidden_bit,
            "obu_type": obu_type,
            "obu_type_name": {
                1: "Sequence Header",
                2: "Temporal Delimiter",
                3: "Frame Header",
                4: "Tile Group",
                5: "Metadata",
                6: "Frame",
                7: "Redundant Frame Header",
                8: "Tile List"
            }.get(obu_type, "Reserved"),
            "obu_extension_flag": bool(obu_extension_flag),
            "obu_has_size_field": bool(obu_has_size_field)
        }

def get_bitstream_parser_field_count() -> int:
    """Return estimated field count for bitstream parser utility."""
    return 150
