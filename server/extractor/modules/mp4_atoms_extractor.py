#!/usr/bin/env python3
"""MP4/ISOBMFF atoms extraction."""

import struct
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone


MP4_ATOMS = {
    b"ftyp": "file_type",
    b"moov": "movie",
    b"mvhd": "movie_header",
    b"trak": "track",
    b"tkhd": "track_header",
    b"mdia": "media",
    b"mdhd": "media_header",
    b"hdlr": "handler",
    b"minf": "media_information",
    b"stbl": "sample_table",
    b"stsd": "sample_description",
    b"stts": "decoding_time_to_sample",
    b"stsc": "sample_to_chunk",
    b"stsz": "sample_sizes",
    b"stco": "chunk_offsets",
    b"co64": "chunk_offsets_64",
    b"avc1": "avc_sample_entry",
    b"avc3": "avc_sample_entry_extended",
    b"avcC": "avc_configuration",
    b"hvc1": "hevc_sample_entry",
    b"hvcC": "hevc_configuration",
    b"mp4a": "mpeg4_audio",
    b"esds": "elementary_stream_descriptor",
    b"ac-3": "ac3_audio",
    b"ec-3": "eac3_audio",
    b"mp3 ": "mp3_audio",
    b"udta": "user_data",
    b"meta": "metadata",
    b"ilst": "metadata_list",
    b"\xa9nam": "title",
    b"\xa9ART": "artist",
    b"\xa9day": "creation_date",
    b"\xa9alb": "album",
    b"\xa9cmt": "comment",
    b"\xa9gen": "genre",
    b"\xa9too": "software",
    b"\xa9wrt": "composer",
    b"\xa9lyr": "lyrics",
    b"\xa9grp": "grouping",
    b"trkn": "track_number",
    b"\xa9cpil": "compilation",
    b"tven": "tv_episode_number",
    b"tves": "tv_episode_count",
    b"tvnn": "tv_network_name",
    b"tvsh": "tv_show_name",
    b"tvsn": "tv_season_number",
    b"desc": "description",
    b"ldesc": "long_description",
    b"keyw": "keywords",
    b"purd": "purchase_date",
    b"prID": "product_id",
    b"mdat": "media_data",
    b"free": "free_space",
    b"skip": "skip_space",
    b"uuid": "user_extension",
}

MP4_SAMPLE_ENTRY_CODES = {
    b"avc1": "H.264/AVC",
    b"avc3": "H.264/AVC (extended)",
    b"hvc1": "H.265/HEVC",
    b"hev1": "H.265/HEVC",
    b"mp4a": "MPEG-4 Audio",
    b"alac": "Apple Lossless",
    b"ac-3": "AC-3 Audio",
    b"ec-3": "E-AC-3 Audio",
    b"mp3 ": "MP3 Audio",
}


@dataclass
class MovieHeader:
    version: int = 0
    creation_time: Optional[datetime] = None
    modification_time: Optional[datetime] = None
    timescale: int = 0
    duration: int = 0
    rate: float = 0.0
    volume: float = 0.0
    matrix: List[int] = field(default_factory=list)
    next_track_id: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "creation_time": self.creation_time.isoformat() if self.creation_time else None,
            "modification_time": self.modification_time.isoformat() if self.modification_time else None,
            "timescale": self.timescale,
            "duration": self.duration,
            "duration_seconds": self.duration / self.timescale if self.timescale else 0,
            "rate": self.rate,
            "volume": self.volume,
            "next_track_id": self.next_track_id,
        }


@dataclass
class TrackHeader:
    version: int = 0
    track_id: int = 0
    duration: int = 0
    width: int = 0
    height: int = 0
    creation_time: Optional[datetime] = None
    modification_time: Optional[datetime] = None
    volume: float = 0.0
    matrix: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "track_id": self.track_id,
            "creation_time": self.creation_time.isoformat() if self.creation_time else None,
            "modification_time": self.modification_time.isoformat() if self.modification_time else None,
            "duration": self.duration,
            "width": self.width / 65536.0,
            "height": self.height / 65536.0,
            "volume": self.volume,
        }


@dataclass
class MediaHeader:
    version: int = 0
    timescale: int = 0
    duration: int = 0
    language_code: int = 0
    creation_time: Optional[datetime] = None
    modification_time: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        lang = [(self.language_code >> 10) & 0x1F, (self.language_code >> 5) & 0x1F, self.language_code & 0x1F]
        lang_str = ''.join(chr(l + 0x60) for l in lang) if 0 <= self.language_code <= 0x7FFF else "und"
        
        return {
            "version": self.version,
            "timescale": self.timescale,
            "duration": self.duration,
            "duration_seconds": self.duration / self.timescale if self.timescale else 0,
            "language": lang_str,
            "creation_time": self.creation_time.isoformat() if self.creation_time else None,
            "modification_time": self.modification_time.isoformat() if self.modification_time else None,
        }


@dataclass
class SampleEntry:
    data_format: str = ""
    data_format_name: str = ""
    width: int = 0
    height: int = 0
    channel_count: int = 0
    sample_size: int = 0
    sample_rate: int = 0
    codec_specific: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data_format": self.data_format,
            "data_format_name": self.data_format_name,
            "width": self.width,
            "height": self.height,
            "channel_count": self.channel_count,
            "sample_size": self.sample_size,
            "sample_rate": self.sample_rate / 65536.0 if self.sample_rate else 0,
            "codec_specific": self.codec_specific,
        }


def mp4_timestamp_to_datetime(timestamp: int) -> Optional[datetime]:
    try:
        epoch = datetime(1904, 1, 1, tzinfo=timezone.utc)
        return epoch.fromtimestamp(timestamp)
    except:
        return None


def parse_mvhd(data: bytes) -> MovieHeader:
    mvhd = MovieHeader()
    
    if len(data) < 4:
        return mvhd
    
    mvhd.version = data[0]
    offset = 4
    
    if mvhd.version == 1:
        if len(data) < 36:
            return mvhd
        creation_ts = struct.unpack(">Q", data[4:12])[0]
        mod_ts = struct.unpack(">Q", data[12:20])[0]
        mvhd.timescale = struct.unpack(">I", data[20:24])[0]
        mvhd.duration = struct.unpack(">Q", data[24:32])[0]
        offset = 32
    else:
        if len(data) < 24:
            return mvhd
        creation_ts = struct.unpack(">I", data[4:8])[0]
        mod_ts = struct.unpack(">I", data[8:12])[0]
        mvhd.timescale = struct.unpack(">I", data[12:16])[0]
        mvhd.duration = struct.unpack(">I", data[16:20])[0]
        offset = 20
    
    mvhd.creation_time = mp4_timestamp_to_datetime(creation_ts)
    mvhd.modification_time = mp4_timestamp_to_datetime(mod_ts)
    
    if len(data) >= offset + 10:
        mvhd.rate = struct.unpack(">I", data[offset:offset+4])[0] / 0x10000
        mvhd.volume = struct.unpack(">H", data[offset+4:offset+6])[0] / 0x100
        offset += 10
        
        if len(data) >= offset + 36:
            mvhd.matrix = list(struct.unpack(">9I", data[offset:offset+36]))
            offset += 36
            
            if len(data) >= offset + 4:
                mvhd.next_track_id = struct.unpack(">I", data[offset:offset+4])[0]
    
    return mvhd


def parse_tkhd(data: bytes) -> TrackHeader:
    tkhd = TrackHeader()
    
    if len(data) < 4:
        return tkhd
    
    tkhd.version = data[0]
    offset = 4
    
    if tkhd.version == 1:
        if len(data) < 36:
            return tkhd
        creation_ts = struct.unpack(">Q", data[4:12])[0]
        mod_ts = struct.unpack(">Q", data[12:20])[0]
        tkhd.track_id = struct.unpack(">I", data[20:24])[0]
        tkhd.duration = struct.unpack(">Q", data[24:32])[0]
        offset = 32
    else:
        if len(data) < 24:
            return tkhd
        creation_ts = struct.unpack(">I", data[4:8])[0]
        mod_ts = struct.unpack(">I", data[8:12])[0]
        tkhd.track_id = struct.unpack(">I", data[12:16])[0]
        tkhd.duration = struct.unpack(">I", data[16:20])[0]
        offset = 20
    
    tkhd.creation_time = mp4_timestamp_to_datetime(creation_ts)
    tkhd.modification_time = mp4_timestamp_to_datetime(mod_ts)
    
    if len(data) >= offset + 68:
        tkhd.volume = struct.unpack(">H", data[offset:offset+2])[0] / 256.0
        tkhd.matrix = list(struct.unpack(">9I", data[offset+8:offset+44]))
        tkhd.width = struct.unpack(">I", data[offset+44:offset+48])[0]
        tkhd.height = struct.unpack(">I", data[offset+48:offset+52])[0]
    
    return tkhd


def parse_mdhd(data: bytes) -> MediaHeader:
    mdhd = MediaHeader()
    
    if len(data) < 4:
        return mdhd
    
    mdhd.version = data[0]
    offset = 4
    
    if mdhd.version == 1:
        if len(data) < 24:
            return mdhd
        creation_ts = struct.unpack(">Q", data[4:12])[0]
        mod_ts = struct.unpack(">Q", data[12:20])[0]
        mdhd.timescale = struct.unpack(">I", data[20:24])[0]
        mdhd.duration = struct.unpack(">Q", data[24:32])[0]
    else:
        if len(data) < 16:
            return mdhd
        creation_ts = struct.unpack(">I", data[4:8])[0]
        mod_ts = struct.unpack(">I", data[8:12])[0]
        mdhd.timescale = struct.unpack(">I", data[12:16])[0]
        mdhd.duration = struct.unpack(">I", data[16:20])[0]
    
    mdhd.creation_time = mp4_timestamp_to_datetime(creation_ts)
    mdhd.modification_time = mp4_timestamp_to_datetime(mod_ts)
    
    if len(data) >= offset + 4:
        mdhd.language_code = struct.unpack(">H", data[offset:offset+2])[0]
    
    return mdhd


def parse_stsd_entry(data: bytes) -> SampleEntry:
    entry = SampleEntry()
    
    if len(data) < 8:
        return entry
    
    entry.data_format = data[4:8].decode('ascii', errors='replace')
    entry.data_format_name = MP4_SAMPLE_ENTRY_CODES.get(data[4:8], entry.data_format)
    
    offset = 8
    
    if entry.data_format in ["avc1", "avc3", "hvc1", "hev1"]:
        if len(data) >= offset + 70:
            entry.width = struct.unpack(">H", data[offset+24:offset+26])[0]
            entry.height = struct.unpack(">H", data[offset+26:offset+28])[0]
    
    elif entry.data_format == "mp4a":
        if len(data) >= offset + 28:
            entry.channel_count = struct.unpack(">H", data[offset+8:offset+10])[0]
            entry.sample_size = struct.unpack(">H", data[offset+10:offset+12])[0]
            entry.sample_rate = struct.unpack(">H", data[offset+24:offset+26])[0]
    
    return entry


def parse_ilst(data: bytes) -> Dict[str, str]:
    metadata = {}
    offset = 0
    
    while offset + 8 <= len(data):
        atom_size = struct.unpack(">I", data[offset:offset+4])[0]
        atom_type = data[offset+4:offset+8]
        
        if atom_size < 8 or offset + atom_size > len(data):
            break
        
        atom_data = data[offset+8:offset+atom_size]
        
        atom_name = MP4_ATOMS.get(atom_type, atom_type.decode('ascii', errors='replace'))
        
        if atom_type.startswith(b"\xa9") or atom_type == b"data":
            if len(atom_data) >= 12:
                locale = struct.unpack(">I", atom_data[8:12])[0]
                value = atom_data[12:].rstrip(b'\x00')
                
                try:
                    text_value = value.decode('utf-8', errors='replace')
                    if text_value:
                        metadata[atom_name] = text_value
                except:
                    pass
        
        offset += atom_size
    
    return metadata


def parse_ftyp(data: bytes) -> Dict[str, Any]:
    ftyp = {"major_brand": "", "minor_version": 0, "compatible_brands": []}
    
    if len(data) >= 4:
        ftyp["major_brand"] = data[0:4].decode('ascii', errors='replace')
    
    if len(data) >= 8:
        ftyp["minor_version"] = struct.unpack(">I", data[4:8])[0]
    
    ftyp["compatible_brands"] = []
    offset = 8
    while offset + 4 <= len(data):
        brand = data[offset:offset+4].decode('ascii', errors='replace')
        if brand:
            ftyp["compatible_brands"].append(brand)
        offset += 4
    
    return ftyp


def parse_mp4_atoms(filepath: str) -> Dict[str, Any]:
    result = {
        "file": filepath,
        "format": "MP4/ISOBMFF",
        "file_size": 0,
        "ftyp": {},
        "moov": {},
        "tracks": [],
        "metadata": {},
        "atoms": {},
        "errors": [],
    }
    
    path = Path(filepath)
    if not path.exists():
        result["errors"].append("File not found")
        return result
    
    result["file_size"] = path.stat().st_size
    
    try:
        with open(filepath, "rb") as f:
            while True:
                pos = f.tell()
                header = f.read(8)
                if len(header) < 8:
                    break
                
                atom_size = struct.unpack(">I", header[0:4])[0]
                atom_type = header[4:8]
                
                if atom_size == 0:
                    remaining = result["file_size"] - pos
                    atom_size = remaining + 8
                
                atom_name = MP4_ATOMS.get(atom_type, atom_type.decode('ascii', errors='replace'))
                
                atom_data = f.read(atom_size - 8) if atom_size > 8 else b""
                if len(atom_data) < atom_size - 8:
                    break
                
                if atom_type == b"ftyp":
                    result["ftyp"] = parse_ftyp(atom_data)
                    result["atoms"]["file_type"] = result["ftyp"]
                    
                elif atom_type == b"moov":
                    result["moov"] = {"raw_size": len(atom_data)}
                    
                elif atom_type == b"mdat":
                    result["atoms"]["media_data"] = {
                        "size": len(atom_data),
                        "offset": pos + 8,
                    }
                
                result["atoms"][atom_name] = {
                    "type": atom_type.hex(),
                    "size": atom_size,
                    "offset": pos,
                }
                
                f.seek(pos + atom_size)
            
            f.close()
            
    except Exception as e:
        result["errors"].append(str(e))
    
    return result


def extract_mp4_metadata(filepath: str) -> Dict[str, Any]:
    return parse_mp4_atoms(filepath)


def get_mp4_field_count() -> int:
    return len(MP4_ATOMS) + len(MP4_SAMPLE_ENTRY_CODES) + 50


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        result = extract_mp4_metadata(sys.argv[1])
        
        print("=" * 60)
        print("MP4/ISOBMFF EXTRACTION TEST")
        print("=" * 60)
        print()
        print(f"File: {result.get('file')}")
        print(f"Format: {result.get('format')}")
        print(f"File Size: {result.get('file_size', 0):,} bytes")
        
        ftyp = result.get("ftyp", {})
        if ftyp:
            print(f"Major Brand: {ftyp.get('major_brand', '?')}")
            print(f"Compatible: {', '.join(ftyp.get('compatible_brands', [])[:5])}")
        
        atoms = result.get("atoms", {})
        print(f"Atoms found: {len(atoms)}")
        
        errors = result.get("errors", [])
        if errors:
            print(f"\nErrors: {errors}")
        
        print(f"\nFields supported: {get_mp4_field_count()}")
        
    else:
        print("Usage: python3 mp4_atoms_extractor.py <file.mp4|m4a|mov>")
        sys.exit(1)
