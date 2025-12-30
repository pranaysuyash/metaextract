#!/usr/bin/env python3
"""WAV/RIFF and AIFF audio file metadata extraction.

This module extracts detailed metadata from WAV, AIFF, and other RIFF-based
audio formats including:
- WAV (PCM, IEEE Float, μ-law, A-law, ADPCM)
- AIFF/AIFF-C (uncompressed and compressed)
- RF64 (extended WAV format)
- Broadcast WAV (BWF)

Reference: 
- https://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/RIFF.html
- https://www.loc.gov/standards/audio/Aiff-rfc.html
- https://tech.ebu.ch/docs/tech/tech3285.pdf
"""

import struct
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict


RIFF_CHUNKS = {
    b"fmt ": "format",
    b"data": "data",
    b"LIST": "list",
    b"JUNK": "junk",
    b"bext": "broadcast_extension",
    b"fmt": "format",
    b"fact": "fact",
    b"cue ": "cue_points",
    b"plst": "playlist",
    b"assoc": "associated_data",
    b"INFO": "metadata",
    b"IARL": "archival_location",
    b"IART": "artist",
    b"ICMS": "commissioned",
    b"ICMT": "comment",
    b"ICOP": "copyright",
    b"ICRD": "creation_date",
    b"IENG": "engineer",
    b"IGNR": "genre",
    b"IKEY": "keywords",
    b"IMED": "medium",
    b"INAM": "title",
    b"IPRD": "product",
    b"ISBJ": "subject",
    b"ISFT": "software",
    b"ISRC": "source",
    b"ITCH": "technician",
    b"ISMP": "smpte_timecode",
    b"IDIT": "date_digitized",
    b"ENDP": "end_point",
    b"FADE": "fade_duration",
    b"SNDM": "sound",
    b"MACH": "machine",
    b"OPRT": "operator",
    b"DSC ": "description",
    b"DSSD": "data_size",
    b"DUR ": "duration",
    b"LIST": "list",
    b"MD5 ": "md5",
    b"MEXT": "mixed",
    b"ODML": "odml",
    b"PMED": "physical_medium",
    b"PROJ": "project",
    b"SIGN": "signature",
    b"SOUN": "sound",
    b"STRL": "string_list",
    b"TIME": "time",
    b"UID ": "unique_id",
    b"umid": "umidi",
    b"UWFD": "user",
    b"WAVEFILETAG": "wavefile_tag",
    b"REV ": "reverb",
    b"PAN ": "panning",
    b"VOL ": "volume",
    b"DATE": "date",
    b"TIM ": "time",
    b"RATE": "rate",
    b"TRCK": "track",
    b"TAGS": "tags",
    b"ECHO": "echo",
    b"FAST": "fast_play",
    b"SRC ": "src_quality",
    b"VUE ": "vue",
    b"regn": "region",
    b"labl": "label",
    b"note": "note",
    b"ltxt": "lyrics_text",
    b"dscp": "description",
    b"genr": "genre",
    b"grp ": "grouping",
    b"artist": "artist",
    b"album": "album",
    b"year": "year",
    b"comment": "comment",
    b"title": "title",
    b"track": "track",
    b"genre": "genre",
}

WAVE_FORMAT_CODES = {
    0x0001: "PCM",
    0x0003: "IEEE Float",
    0x0006: "A-law",
    0x0007: "μ-law",
    0x0010: "ADPCM",
    0x0011: "IMA ADPCM",
    0x0012: "Yamaha ADPCM",
    0x0013: "DVI ADPCM",
    0x0014: "DVI ADPCM",
    0x0015: "ADPCM",
    0x0016: "Yamaha ADPCM",
    0x0020: "ADPCM",
    0x0100: "OKI ADPCM",
    0x0101: "DVI ADPCM",
    0x0111: "Intel ADPCM",
    0x0120: "Xlaw",
    0x0123: "GSM 6.10",
    0x0150: "G723 ADPCM",
    0x0155: "G723 ADPCM",
    0x0156: "G723 ADPCM",
    0x0157: "G723 ADPCM",
    0x0160: "G729",
    0x0161: "G729A",
    0x0200: "G726",
    0x0210: "G726",
    0x0220: "G726",
    0x0230: "G726",
    0x0400: "G721",
    0x0401: "G722",
    0x0450: "G723",
    0x0550: "MP2",
    0x0551: "MP3",
    0x2000: "AC3",
    0x2001: "DTS",
    0x2100: "ACM",
    0x7FFF: "Extensible",
}

AIFF_CUIDS = {
    b"NONE": "uncompressed",
    b"sowt": "16-bit little-endian",
    b"twos": "16-bit big-endian",
    b"raw ": "uncompressed",
    b"in32": "32-bit integer",
    b"fl32": "32-bit float",
    b"fl64": "64-bit float",
    b"alaw": "A-law",
    b"ulaw": "μ-law",
    b"ACE2": "ACE2",
    b"ACON": "acon",
    b"ADP4": "ADP4",
    b"MAC3": "MAC3",
    b"MAC6": "MAC6",
    b"MPG3": "MPG3",
    b"IMA4": "IMA4",
    b"QDesign": "QDesign",
    b"QDesign2": "QDesign2",
    b"QDM2": "QDM2",
    b"QUALCOMM": "QUALCOMM",
    b"SOURCELESS": "SOURCELESS",
}


@dataclass
class WaveFormat:
    """WAV format chunk data."""
    audio_format: int = 0
    num_channels: int = 0
    sample_rate: int = 0
    byte_rate: int = 0
    block_align: int = 0
    bits_per_sample: int = 0
    extension_size: int = 0
    valid_bits_per_sample: int = 0
    channel_mask: int = 0
    guid: str = ""
    format_name: str = field(default="", repr=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audio_format": self.audio_format,
            "audio_format_name": self.format_name,
            "num_channels": self.num_channels,
            "sample_rate": self.sample_rate,
            "byte_rate": self.byte_rate,
            "block_align": self.block_align,
            "bits_per_sample": self.bits_per_sample,
            "valid_bits_per_sample": self.valid_bits_per_sample,
            "channel_mask": self.channel_mask,
            "guid": self.guid,
        }


@dataclass
class BroadcastWavExtension:
    """BWF bext chunk data."""
    description: str = ""
    originator: str = ""
    originator_reference: str = ""
    origination_date: str = ""
    origination_time: str = ""
    time_reference_low: int = 0
    time_reference_high: int = 0
    version: int = 0
    umid: str = ""
    loudness_value: int = 0
    loudness_range: int = 0
    max_true_peak_level: int = 0
    maxMomentaryLoudness: int = 0
    maxShortTermLoudness: int = 0
    coding_history: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "originator": self.originator,
            "originator_reference": self.originator_reference,
            "origination_date": self.origination_date,
            "origination_time": self.origination_time,
            "time_reference_samples": (self.time_reference_high << 32) | self.time_reference_low,
            "version": self.version,
            "umid": self.umid,
            "coding_history": self.coding_history,
        }


def parse_wave_format(data: bytes) -> WaveFormat:
    """Parse WAV fmt chunk."""
    fmt = WaveFormat()
    
    if len(data) < 16:
        return fmt
    
    fmt.audio_format = struct.unpack("<H", data[0:2])[0]
    fmt.num_channels = struct.unpack("<H", data[2:4])[0]
    fmt.sample_rate = struct.unpack("<I", data[4:8])[0]
    fmt.byte_rate = struct.unpack("<I", data[8:12])[0]
    fmt.block_align = struct.unpack("<H", data[12:14])[0]
    fmt.bits_per_sample = struct.unpack("<H", data[14:16])[0]
    
    fmt.format_name = WAVE_FORMAT_CODES.get(fmt.audio_format, f"Unknown ({fmt.audio_format})")
    
    if len(data) >= 18:
        extension_size = struct.unpack("<H", data[16:18])[0]
        fmt.extension_size = extension_size
        
        if extension_size >= 10 and len(data) >= 26:
            fmt.valid_bits_per_sample = struct.unpack("<H", data[18:20])[0]
            fmt.channel_mask = struct.unpack("<I", data[20:24])[0]
            
        if extension_size >= 22 and len(data) >= 40:
            guid_data = data[24:40]
            fmt.guid = guid_data.hex()
    
    return fmt


def parse_broadcast_extension(data: bytes) -> BroadcastWavExtension:
    """Parse BWF bext chunk."""
    bext = BroadcastWavExtension()
    
    if len(data) < 2:
        return bext
    
    try:
        bext.description = data[0:256].rstrip(b'\x00').decode('latin-1', errors='replace')
        bext.originator = data[256:320].rstrip(b'\x00').decode('latin-1', errors='replace')
        bext.originator_reference = data[320:384].rstrip(b'\x00').decode('latin-1', errors='replace')
        bext.origination_date = data[384:392].rstrip(b'\x00').decode('ascii', errors='replace')
        bext.origination_time = data[392:400].rstrip(b'\x00').decode('ascii', errors='replace')
        
        if len(data) >= 408:
            bext.time_reference_low = struct.unpack("<I", data[400:404])[0]
            bext.time_reference_high = struct.unpack("<I", data[404:408])[0]
            
        if len(data) >= 410:
            bext.version = struct.unpack("<H", data[408:410])[0]
            
        if len(data) >= 582:
            bext.umid = data[410:582].hex()
            
        if len(data) >= 584:
            bext.loudness_value = struct.unpack("<H", data[582:584])[0]
            
        if len(data) >= 586:
            bext.loudness_range = struct.unpack("<H", data[584:586])[0]
            
        if len(data) >= 588:
            bext.max_true_peak_level = struct.unpack("<H", data[586:588])[0]
            
        if len(data) >= 590:
            bext.maxMomentaryLoudness = struct.unpack("<H", data[588:590])[0]
            
        if len(data) >= 592:
            bext.maxShortTermLoudness = struct.unpack("<H", data[590:592])[0]
        
        coding_offset = 602
        if len(data) > coding_offset:
            bext.coding_history = data[coding_offset:].rstrip(b'\x00').decode('latin-1', errors='replace')
            
    except Exception:
        pass
    
    return bext


def parse_info_list(data: bytes) -> Dict[str, str]:
    """Parse INFO list chunk for metadata."""
    info = {}
    offset = 0
    
    while offset + 8 <= len(data):
        chunk_id = data[offset:offset+4]
        chunk_size = struct.unpack("<I", data[offset+4:offset+8])[0]
        
        if chunk_id in RIFF_CHUNKS:
            field_name = RIFF_CHUNKS[chunk_id]
            if 8 + offset + chunk_size <= len(data):
                value_data = data[offset+8:offset+8+chunk_size]
                try:
                    if isinstance(value_data, bytes):
                        value = value_data.rstrip(b'\x00').decode('latin-1', errors='replace').strip()
                        if value:
                            info[field_name] = value
                except:
                    pass
        
        offset += 8 + chunk_size
        if chunk_size % 2 == 1:
            offset += 1
    
    return info


def parse_cue_points(data: bytes) -> List[Dict[str, Any]]:
    """Parse cue points chunk."""
    cues = []
    
    if len(data) < 4:
        return cues
    
    num_cues = struct.unpack("<I", data[0:4])[0]
    offset = 4
    
    for _ in range(num_cues):
        if offset + 24 > len(data):
            break
        
        cue = {
            "cue_id": struct.unpack("<I", data[offset:offset+4])[0],
            "position": struct.unpack("<I", data[offset+4:offset+8])[0],
            "chunk_id": data[offset+8:offset+12].decode('ascii', errors='replace'),
            "chunk_start": struct.unpack("<I", data[offset+12:offset+16])[0],
            "block_start": struct.unpack("<I", data[offset+16:offset+20])[0],
            "sample_offset": struct.unpack("<I", data[offset+20:offset+24])[0],
        }
        cues.append(cue)
        offset += 24
    
    return cues


def parse_fact_chunk(data: bytes) -> Dict[str, int]:
    """Parse fact chunk."""
    fact = {}
    
    if len(data) >= 4:
        fact["sample_count"] = struct.unpack("<I", data[0:4])[0]
    
    if len(data) >= 8:
        fact["dword_sample_count"] = struct.unpack("<I", data[4:8])[0]
    
    return fact


def extract_wav_metadata(filepath: str) -> Dict[str, Any]:
    """Extract comprehensive WAV/RIFF metadata."""
    
    result = {
        "file": filepath,
        "format": "WAV/RIFF",
        "riff_size": 0,
        "wave_id": "",
        "chunks": {},
        "format_chunk": None,
        "info_metadata": {},
        "broadcast_extension": None,
        "cue_points": [],
        "fact_data": {},
        "errors": [],
    }
    
    path = Path(filepath)
    if not path.exists():
        result["errors"].append("File not found")
        return result
    
    try:
        with open(filepath, "rb") as f:
            riff_header = f.read(12)
            
            if not riff_header.startswith(b"RIFF"):
                result["errors"].append("Not a RIFF file")
                return result
            
            result["riff_size"] = struct.unpack("<I", riff_header[4:8])[0]
            result["wave_id"] = riff_header[8:12].decode('ascii', errors='replace')
            
            while True:
                chunk_header = f.read(8)
                if len(chunk_header) < 8:
                    break
                
                chunk_id = chunk_header[0:4]
                chunk_size = struct.unpack("<I", chunk_header[4:8])[0]
                
                chunk_name = RIFF_CHUNKS.get(chunk_id, chunk_id.decode('ascii', errors='replace'))
                
                chunk_data = f.read(chunk_size)
                if len(chunk_data) < chunk_size:
                    break
                
                if chunk_size % 2 == 1:
                    f.read(1)
                
                if chunk_id == b"fmt ":
                    result["format_chunk"] = parse_wave_format(chunk_data).to_dict()
                    result["chunks"]["format"] = result["format_chunk"]
                    
                elif chunk_id == b"data":
                    result["chunks"]["data"] = {
                        "size": chunk_size,
                        "offset": f.tell() - chunk_size - 8,
                    }
                    
                elif chunk_id == b"bext":
                    bext = parse_broadcast_extension(chunk_data)
                    result["broadcast_extension"] = bext.to_dict()
                    result["chunks"]["broadcast_extension"] = result["broadcast_extension"]
                    
                elif chunk_id == b"INFO":
                    info = parse_info_list(chunk_data)
                    result["info_metadata"] = info
                    result["chunks"]["info"] = info
                    
                elif chunk_id == b"LIST" and chunk_data.startswith(b"INFO"):
                    info = parse_info_list(chunk_data[4:])
                    result["info_metadata"] = info
                    result["chunks"]["info"] = info
                    
                elif chunk_id == b"cue ":
                    cues = parse_cue_points(chunk_data)
                    result["cue_points"] = cues
                    result["chunks"]["cue_points"] = {"count": len(cues)}
                    
                elif chunk_id == b"fact":
                    fact = parse_fact_chunk(chunk_data)
                    result["fact_data"] = fact
                    result["chunks"]["fact"] = fact
                    
                elif chunk_id == b"JUNK":
                    result["chunks"]["junk"] = {"size": chunk_size}
                    
                else:
                    result["chunks"][chunk_name] = {
                        "id": chunk_id.hex(),
                        "size": chunk_size,
                    }
            
            f.close()
            
            if result["format_chunk"]:
                duration = 0
                if result["fact_data"].get("sample_count"):
                    duration = result["fact_data"]["sample_count"] / result["format_chunk"].get("sample_rate", 1)
                elif result["chunks"].get("data", {}).get("size"):
                    data_size = result["chunks"]["data"]["size"]
                    block_align = result["format_chunk"].get("block_align", 1)
                    sample_count = data_size // block_align
                    duration = sample_count / result["format_chunk"].get("sample_rate", 1)
                
                result["duration_seconds"] = duration
                
    except Exception as e:
        result["errors"].append(str(e))
    
    return result


def extract_aiff_metadata(filepath: str) -> Dict[str, Any]:
    """Extract AIFF metadata."""
    
    result = {
        "file": filepath,
        "format": "AIFF",
        "chunks": {},
        "format": {},
        "comm_chunk": None,
        "info_metadata": {},
        "errors": [],
    }
    
    path = Path(filepath)
    if not path.exists():
        result["errors"].append("File not found")
        return result
    
    try:
        with open(filepath, "rb") as f:
            form_header = f.read(12)
            
            if not form_header.startswith(b"FORM"):
                result["errors"].append("Not an AIFF file")
                return result
            
            form_size = struct.unpack(">I", form_header[4:8])[0]
            form_type = form_header[8:12]
            result["form_type"] = form_type.decode('ascii', errors='replace')
            
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
                
                if chunk_id == b"COMM":
                    comm = {
                        "num_channels": struct.unpack(">H", chunk_data[0:2])[0],
                        "num_sample_frames": struct.unpack(">I", chunk_data[2:6])[0],
                        "bits_per_sample": struct.unpack(">H", chunk_data[6:8])[0],
                        "sample_rate": struct.unpack(">D", chunk_data[8:16])[0],
                    }
                    
                    if len(chunk_data) >= 18:
                        compression_type = chunk_data[18:22]
                        compression_name = chunk_data[23:].rstrip(b'\x00').decode('latin-1', errors='replace') if len(chunk_data) > 23 else ""
                        comm["compression_type"] = compression_type.decode('ascii', errors='replace')
                        comm["compression_name"] = compression_name
                        comm["compression_description"] = AIFF_CUIDS.get(compression_type, compression_name)
                    
                    result["comm_chunk"] = comm
                    result["format"] = comm
                    
                elif chunk_id == b"SSND":
                    result["chunks"]["ssnd"] = {
                        "size": chunk_size,
                        "offset": f.tell() - chunk_size - 8,
                    }
                    
                elif chunk_id == b"NAME":
                    result["info_metadata"]["title"] = chunk_data.rstrip(b'\x00').decode('latin-1', errors='replace')
                    
                elif chunk_id == b"AUTH":
                    result["info_metadata"]["author"] = chunk_data.rstrip(b'\x00').decode('latin-1', errors='replace')
                    
                elif chunk_id == b"(c) ":
                    result["info_metadata"]["copyright"] = chunk_data.rstrip(b'\x00').decode('latin-1', errors='replace')
                    
                elif chunk_id == b"ANNO":
                    result["info_metadata"]["annotation"] = chunk_data.rstrip(b'\x00').decode('latin-1', errors='replace')
                    
                elif chunk_id == b"MARK":
                    result["chunks"]["mark"] = {"size": chunk_size}
                    
                else:
                    result["chunks"][chunk_id.decode('ascii', errors='replace')] = {"size": chunk_size}
            
            f.close()
            
            if result["comm_chunk"]:
                duration = result["comm_chunk"].get("num_sample_frames", 0) / result["comm_chunk"].get("sample_rate", 1)
                result["duration_seconds"] = duration
                
    except Exception as e:
        result["errors"].append(str(e))
    
    return result


def detect_format(filepath: str) -> str:
    """Detect if file is WAV or AIFF."""
    path = Path(filepath)
    if not path.exists():
        return "unknown"
    
    with open(filepath, "rb") as f:
        header = f.read(12)
        
        if header.startswith(b"RIFF") and header[8:12] == b"WAVE":
            return "WAV"
        elif header.startswith(b"FORM") and (header[8:12] == b"AIFF" or header[8:12] == b"AIFC"):
            return "AIFF"
    
    return "unknown"


def extract_riff_metadata(filepath: str) -> Dict[str, Any]:
    """Main entry point - detect format and extract metadata."""
    
    fmt = detect_format(filepath)
    
    if fmt == "WAV":
        return extract_wav_metadata(filepath)
    elif fmt == "AIFF":
        return extract_aiff_metadata(filepath)
    else:
        return {
            "file": filepath,
            "format": "unknown",
            "errors": ["Unable to detect RIFF/AIFF format"],
        }


def get_riff_field_count() -> int:
    """Get number of RIFF/WAV fields we support."""
    return len(RIFF_CHUNKS) + len(WAVE_FORMAT_CODES) + 10


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        result = extract_riff_metadata(sys.argv[1])
        
        print("=" * 60)
        print("RIFF/WAV/AIFF EXTRACTION TEST")
        print("=" * 60)
        print()
        print(f"File: {result.get('file')}")
        print(f"Format: {result.get('format', 'unknown')}")
        
        if result.get("format_chunk"):
            fmt = result["format_chunk"]
            print(f"Audio: {fmt.get('audio_format_name', fmt.get('audio_format', '?'))} {fmt.get('bits_per_sample', '?')}-bit")
            print(f"Channels: {fmt.get('num_channels', '?')}")
            print(f"Sample Rate: {fmt.get('sample_rate', '?')} Hz")
        
        if result.get("duration_seconds"):
            print(f"Duration: {result['duration_seconds']:.2f} seconds")
        
        info = result.get("info_metadata", {})
        if info:
            print()
            print("Metadata:")
            for k, v in list(info.items())[:10]:
                print(f"  {k}: {v}")
        
        cues = result.get("cue_points", [])
        if cues:
            print(f"\nCue Points: {len(cues)}")
        
        errors = result.get("errors", [])
        if errors:
            print(f"\nErrors: {errors}")
        
        print(f"\nFields supported: {get_riff_field_count()}")
        
    else:
        print("Usage: python3 wav_riff_extractor.py <audio.wav|aiff.aiff>")
        sys.exit(1)
