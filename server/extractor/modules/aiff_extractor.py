#!/usr/bin/env python3
"""AIFF/AIFF-C audio file metadata extraction.

This module extracts detailed metadata from AIFF and AIFF-C files.
AIFF (Audio Interchange File Format) is a container format developed by Apple.

Reference:
- https://www.loc.gov/standards/audio/Aiff-rfc.html
- Apple AIFF specification
"""

import struct
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone


AIFF_CHUNKS = {
    b"FORM": "form_header",
    b"COMM": "common",
    b"SSND": "sound_data",
    b"NAME": "name_title",
    b"AUTH": "author",
    b"(c) ": "copyright",
    b"ANNO": "annotation",
    b"MARK": "markers",
    b"INST": "instrument",
    b"COMT": "comments",
    b"ID3 ": "id3_metadata",
    b"FVER": "format_version",
    b"UTF8": "utf8_metadata",
    b"UMID": "umid",
    b"MEDD": "metadata_edit_date",
    b"TIMD": "time_edit_date",
    b"MUID": "creator_id",
    b"PTCH": "pitch",
    b"SMPTE": "smpte_timecode",
    b"CLIP": "clip_region",
    b"GEOB": "generic_binary",
    b"APPL": "application",
    b"JUNK": "padding",
    b"FREE": "free_space",
}


AIFF_COMPRESSION_TYPES = {
    b"NONE": ("uncompressed", "Standard PCM"),
    b"sowt": ("16-bit little-endian", "16-bit PCM (Little Endian)"),
    b"twos": ("16-bit big-endian", "16-bit PCM (Big Endian)"),
    b"in32": ("32-bit integer", "32-bit Integer"),
    b"fl32": ("32-bit float", "32-bit Floating Point"),
    b"fl64": ("64-bit float", "64-bit Floating Point"),
    b"alaw": ("A-law", "A-law G.711"),
    b"ulaw": ("mu-law", "μ-law G.711"),
    b"ACE2": ("ACE2", "ACE2 Codec"),
    b"ACON": ("acon", "Audio Conversation"),
    b"ADP4": ("ADP4", "ADP4 Codec"),
    b"MAC3": ("MAC3", "MAC3 Codec"),
    b"MAC6": ("MAC6", "MAC6 Codec"),
    b"MPG3": ("MPG3", "MPEG-3 Audio"),
    b"IMA4": ("IMA4", "IMA4 ADPCM"),
    b"QDesign": ("QDesign", "QDesign Audio"),
    b"QDesign2": ("QDesign2", "QDesign2 Audio"),
    b"QDM2": ("QDM2", "QDM2 Audio"),
    b"QUALCOMM": ("QUALCOMM", "QUALCOMM Audio"),
    b"SOURCELESS": ("SOURCELESS", "Sourceless"),
}


@dataclass
class AIFFCommon:
    """AIFF COMM chunk."""
    num_channels: int = 0
    num_sample_frames: int = 0
    bits_per_sample: int = 0
    sample_rate: int = 0
    compression_type: str = ""
    compression_name: str = ""
    duration: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "num_channels": self.num_channels,
            "num_sample_frames": self.num_sample_frames,
            "bits_per_sample": self.bits_per_sample,
            "sample_rate": self.sample_rate,
            "compression_type": self.compression_type,
            "compression_name": self.compression_name,
            "duration_seconds": self.duration,
        }


@dataclass
class AIFFInstrument:
    """AIFF INST chunk (instrument)."""
    base_note: int = 0
    detune: int = 0
    low_note: int = 0
    high_note: int = 0
    low_velocity: int = 0
    high_velocity: int = 0
    gain: int = 0
    sustain_loop_start: int = 0
    sustain_loop_end: int = 0
    release_loop_start: int = 0
    release_loop_end: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "base_note_midi": self.base_note,
            "detune_cents": self.detune,
            "low_note_midi": self.low_note,
            "high_note_midi": self.high_note,
            "low_velocity": self.low_velocity,
            "high_velocity": self.high_velocity,
            "gain_db": self.gain,
            "sustain_loop": {"start": self.sustain_loop_start, "end": self.sustain_loop_end},
            "release_loop": {"start": self.release_loop_start, "end": self.release_loop_end},
        }


@dataclass
class AIFFMarker:
    """AIFF marker."""
    id: int = 0
    position: int = 0
    name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "position": self.position,
            "name": self.name,
        }


@dataclass
class AIFFComment:
    """AIFF comment entry."""
    count: int = 0
    timestamp: int = 0
    marker_id: int = 0
    text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.count,
            "timestamp": self.timestamp,
            "marker_id": self.marker_id,
            "text": self.text,
        }


def parse_ieee_extended(data: bytes) -> float:
    """Parse 80-bit IEEE 754 extended precision float."""
    if len(data) < 10:
        return 0.0
    
    try:
        sign = data[0] >> 7
        exponent = ((data[0] & 0x7F) << 8) | data[1]
        mantissa = data[2:]
        
        if exponent == 0 and all(m == 0 for m in mantissa):
            return 0.0
        
        if exponent == 0x7FFF:
            return float('inf')
        
        value = 0.0
        for i, b in enumerate(mantissa):
            value += b * (2 ** (-8 * (i + 1)))
        
        value = (1 + value) * (2 ** (exponent - 16383))
        
        return -value if sign else value
    except:
        return 0.0


def parse_aiff_common(data: bytes) -> AIFFCommon:
    """Parse AIFF COMM chunk."""
    comm = AIFFCommon()
    
    if len(data) < 18:
        return comm
    
    comm.num_channels = struct.unpack(">H", data[0:2])[0]
    comm.num_sample_frames = struct.unpack(">I", data[2:6])[0]
    comm.bits_per_sample = struct.unpack(">H", data[6:8])[0]
    comm.sample_rate = int(parse_ieee_extended(data[8:18]))
    
    if len(data) >= 22:
        comm.compression_type = data[18:22].decode('ascii', errors='replace')
        comp_info = AIFF_COMPRESSION_TYPES.get(data[18:22], (comm.compression_type, "Unknown"))
        comm.compression_name = comp_info[1]
    
    if comm.sample_rate > 0:
        comm.duration = comm.num_sample_frames / comm.sample_rate
    
    return comm


def parse_aiff_instrument(data: bytes) -> AIFFInstrument:
    """Parse AIFF INST chunk."""
    inst = AIFFInstrument()
    
    if len(data) < 20:
        return inst
    
    inst.base_note = data[0]
    inst.detune = data[1]
    inst.low_note = data[2]
    inst.high_note = data[3]
    inst.low_velocity = data[4]
    inst.high_velocity = data[5]
    inst.gain = struct.unpack(">h", data[6:8])[0]
    inst.sustain_loop_start = struct.unpack(">H", data[8:10])[0]
    inst.sustain_loop_end = struct.unpack(">H", data[10:12])[0]
    inst.release_loop_start = struct.unpack(">H", data[12:14])[0]
    inst.release_loop_end = struct.unpack(">H", data[14:16])[0]
    
    return inst


def parse_aiff_markers(data: bytes) -> List[AIFFMarker]:
    """Parse AIFF MARK chunk."""
    markers = []
    
    if len(data) < 2:
        return markers
    
    num_markers = struct.unpack(">H", data[0:2])[0]
    offset = 2
    
    for _ in range(num_markers):
        if offset + 8 > len(data):
            break
        
        marker_id = struct.unpack(">H", data[offset:offset+2])[0]
        position = struct.unpack(">I", data[offset+2:offset+6])[0]
        
        name_length = data[offset+6]
        name_data = data[offset+7:offset+7+name_length]
        name = name_data.decode('latin-1', errors='replace')
        
        markers.append(AIFFMarker(id=marker_id, position=position, name=name))
        offset += 8 + name_length
        
        if offset % 2 == 1:
            offset += 1
    
    return markers


def parse_aiff_comments(data: bytes) -> List[AIFFComment]:
    """Parse AIFF COMT chunk."""
    comments = []
    
    if len(data) < 2:
        return comments
    
    num_comments = struct.unpack(">H", data[0:2])[0]
    offset = 2
    
    for i in range(num_comments):
        if offset + 12 > len(data):
            break
        
        timestamp = struct.unpack(">I", data[offset:offset+4])[0]
        marker_id = struct.unpack(">H", data[offset+4:offset+6])[0]
        count = i + 1
        
        text_length = struct.unpack(">H", data[offset+6:offset+8])[0]
        text_data = data[offset+8:offset+8+text_length]
        text = text_data.decode('latin-1', errors='replace')
        
        comments.append(AIFFComment(count=count, timestamp=timestamp, marker_id=marker_id, text=text))
        offset += 8 + text_length
        
        if offset % 2 == 1:
            offset += 1
    
    return comments


def extract_aiff_metadata(filepath: str) -> Dict[str, Any]:
    """Extract AIFF metadata from file."""
    
    result = {
        "file": filepath,
        "format": "AIFF",
        "file_size": 0,
        "form_type": "",
        "common": None,
        "instrument": None,
        "markers": [],
        "comments": [],
        "metadata": {},
        "chunks": {},
        "errors": [],
    }
    
    path = Path(filepath)
    if not path.exists():
        result["errors"].append("File not found")
        return result
    
    result["file_size"] = path.stat().st_size
    
    try:
        with open(filepath, "rb") as f:
            form_header = f.read(12)
            
            if not form_header.startswith(b"FORM"):
                result["errors"].append("Not an AIFF file")
                return result
            
            result["file_size"] = struct.unpack(">I", form_header[4:8])[0]
            result["form_type"] = form_header[8:12].decode('ascii', errors='replace')
            
            while True:
                chunk_header = f.read(8)
                if len(chunk_header) < 8:
                    break
                
                chunk_id = chunk_header[0:4]
                chunk_size = struct.unpack(">I", chunk_header[4:8])[0]
                
                if chunk_size % 2 == 1:
                    chunk_size += 1
                
                chunk_data = f.read(chunk_size)
                if len(chunk_data) < chunk_size:
                    break
                
                chunk_name = AIFF_CHUNKS.get(chunk_id, chunk_id.decode('ascii', errors='replace'))
                
                if chunk_id == b"COMM":
                    result["common"] = parse_aiff_common(chunk_data).to_dict()
                    result["chunks"]["common"] = result["common"]
                    
                elif chunk_id == b"NAME":
                    result["metadata"]["title"] = chunk_data.rstrip(b'\x00').decode('latin-1', errors='replace')
                    
                elif chunk_id == b"AUTH":
                    result["metadata"]["author"] = chunk_data.rstrip(b'\x00').decode('latin-1', errors='replace')
                    
                elif chunk_id == b"(c) ":
                    result["metadata"]["copyright"] = chunk_data.rstrip(b'\x00').decode('latin-1', errors='replace')
                    
                elif chunk_id == b"ANNO":
                    result["metadata"]["annotation"] = chunk_data.rstrip(b'\x00').decode('latin-1', errors='replace')
                    
                elif chunk_id == b"INST":
                    result["instrument"] = parse_aiff_instrument(chunk_data).to_dict()
                    result["chunks"]["instrument"] = result["instrument"]
                    
                elif chunk_id == b"MARK":
                    result["markers"] = [m.to_dict() for m in parse_aiff_markers(chunk_data)]
                    result["chunks"]["markers"] = {"count": len(result["markers"])}
                    
                elif chunk_id == b"COMT":
                    result["comments"] = [c.to_dict() for c in parse_aiff_comments(chunk_data)]
                    result["chunks"]["comments"] = {"count": len(result["comments"])}
                    
                elif chunk_id == b"ID3 " or chunk_id == b"ID3":
                    result["chunks"]["id3"] = {"size": len(chunk_data)}
                    
                elif chunk_id == b"SSND":
                    result["chunks"]["sound_data"] = {
                        "size": len(chunk_data),
                        "offset": f.tell() - chunk_size,
                    }
                    
                else:
                    result["chunks"][chunk_name] = {"size": len(chunk_data)}
            
            f.close()
            
    except Exception as e:
        result["errors"].append(str(e))
    
    return result


def get_aiff_field_count() -> int:
    """Get number of AIFF fields we support."""
    return len(AIFF_CHUNKS) + len(AIFF_COMPRESSION_TYPES) + 30


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        result = extract_aiff_metadata(sys.argv[1])
        
        print("=" * 60)
        print("AIFF METADATA EXTRACTION TEST")
        print("=" * 60)
        print()
        print(f"File: {result.get('file')}")
        print(f"Format: {result.get('format')}")
        print(f"Form Type: {result.get('form_type', '?')}")
        print(f"File Size: {result.get('file_size', 0):,} bytes")
        
        common = result.get("common")
        if common:
            print(f"\nAudio Properties:")
            print(f"  Channels: {common.get('num_channels', '?')}")
            print(f"  Bits: {common.get('bits_per_sample', '?')}")
            print(f"  Sample Rate: {common.get('sample_rate', '?')} Hz")
            print(f"  Duration: {common.get('duration_seconds', 0):.2f}s")
            print(f"  Compression: {common.get('compression_name', '?')}")
        
        instrument = result.get("instrument")
        if instrument:
            print(f"\nInstrument:")
            print(f"  Base Note: {instrument.get('base_note_midi', '?')}")
            print(f"  Detune: {instrument.get('detune_cents', '?')} cents")
        
        metadata = result.get("metadata", {})
        if metadata:
            print(f"\nMetadata:")
            for k, v in metadata.items():
                print(f"  {k}: {v}")
        
        markers = result.get("markers", [])
        if markers:
            print(f"\nMarkers: {len(markers)}")
        
        comments = result.get("comments", [])
        if comments:
            print(f"Comments: {len(comments)}")
        
        chunks = result.get("chunks", {})
        print(f"\nChunks: {len(chunks)}")
        
        errors = result.get("errors", [])
        if errors:
            print(f"\nErrors: {errors}")
        
        print(f"\nFields supported: {get_aiff_field_count()}")
        
    else:
        print("Usage: python3 aiff_extractor.py <file.aiff|aifc>")
        sys.exit(1)
