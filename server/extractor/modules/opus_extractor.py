#!/usr/bin/env python3
"""Opus audio file metadata extraction.

This module extracts metadata from Ogg Opus files and raw Opus streams.
Opus is a lossy audio codec defined in RFC 6381 and RFC 6716.

Reference:
- https://www.opus-codec.org/
- RFC 6381 (Ogg Opus)
- IETF Opus specification
"""

import struct
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone


OPUS_TAGS = {
    "TITLE": "title",
    "ARTIST": "artist",
    "ALBUM": "album",
    "ALBUMARTIST": "album_artist",
    "TRACKNUMBER": "track_number",
    "DISCNUMBER": "disc_number",
    "DATE": "date",
    "ORIGINALDATE": "original_date",
    "GENRE": "genre",
    "COMMENT": "comment",
    "DESCRIPTION": "description",
    "COMPOSER": "composer",
    "CONDUCTOR": "conductor",
    "LYRICS": "lyrics",
    "COPYRIGHT": "copyright",
    "LICENSE": "license",
    "ENCODEDBY": "encoded_by",
    "ENCODER": "encoder",
    "ENCODERSOFTWARE": "encoder_software",
    "ENCODERSETTINGS": "encoder_settings",
    "ISRC": "isrc",
    "BARCODE": "barcode",
    "CATALOGNUMBER": "catalog_number",
    "RELEASESTATUS": "release_status",
    "RELEASETYPE": "release_type",
    "RELEASEcountry": "release_country",
    "ARTISTSORT": "artist_sort",
    "ALBUMARTISTSORT": "album_artist_sort",
    "ALBUMSORT": "album_sort",
    "TITLESORT": "title_sort",
    "MEDIA": "media_type",
    "TOTALTRACKS": "total_tracks",
    "TOTALDISCS": "total_discs",
    "WORK": "work",
    "MOVEMENT": "movement",
    "MOVEMENTNAME": "movement_name",
    "MOVEMENTNUMBER": "movement_number",
    "SHOWMOVEMENTNAME": "show_movement_name",
    "GROUPING": "grouping",
    "SUBTITLE": "subtitle",
    "VERSION": "version",
    "AUTHOR": "author",
    "CONTACT": "contact",
    "LOCATION": "location",
    "HISTORY": "history",
    "CROWDEDFUNDINGURL": "crowdfunding_url",
    "IMAGE": "image",
    "IMAGEURL": "image_url",
    "BPM": "bpm",
    "KEY": "key",
    "INITIALKEY": "initial_key",
    "MOOD": "mood",
    "STYLE": "style",
    "OCCASION": "occasion",
    "QUALITY": "quality",
    "ORIGINALFILENAME": "original_filename",
    "RIPDATE": "rip_date",
    "SOURCEMEDIA": "source_media",
    "LANGUAGE": "language",
    "SCRIPT": "script",
    "LABEL": "label",
    "ORGANIZATION": "organization",
    "CREATOR": "creator",
    "MAINTAINER": "maintainer",
    "VENDOR": "vendor",
    "PRODUCT": "product",
    "PACKAGE": "package",
    "CONTENTTYPE": "content_type",
    "SUBJECT": "subject",
    "ABSTRACT": "abstract",
    "SUMMARY": "summary",
    "keywords": "keywords",
    "SIGNER": "signer",
    "SIGNATUREURL": "signature_url",
}


OPUS_HEADERS = {
    b"OggS": "ogg_container",
    b"Opus": "opus_head",
    b"OpusTags": "opus_tags",
}


@dataclass
class OpusHead:
    """OpusHead identification header."""
    version: int = 0
    output_channels: int = 0
    pre_skip: int = 0
    input_sample_rate: int = 0
    output_gain: int = 0
    mapping_family: int = 0
    stream_count: int = 0
    coupled_count: int = 0
    channel_mapping: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "output_channels": self.output_channels,
            "pre_skip_samples": self.pre_skip,
            "input_sample_rate": self.input_sample_rate,
            "output_gain_db": self.output_gain / 256.0,
            "mapping_family": self.mapping_family,
            "stream_count": self.stream_count,
            "coupled_count": self.coupled_count,
            "channel_mapping": self.channel_mapping,
        }


@dataclass
class OpusTags:
    """OpusTags metadata."""
    vendor: str = ""
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vendor": self.vendor,
            "tags": self.tags,
        }


def parse_opus_head(data: bytes) -> OpusHead:
    """Parse OpusHead identification header."""
    head = OpusHead()
    
    if len(data) < 19:
        return head
    
    head.version = data[0]
    head.output_channels = data[1]
    head.pre_skip = struct.unpack("<I", data[2:6])[0]
    head.input_sample_rate = struct.unpack("<I", data[6:10])[0]
    head.output_gain = struct.unpack("<H", data[10:12])[0]
    head.mapping_family = data[12]
    
    if len(data) >= 20:
        head.stream_count = data[13]
        head.coupled_count = data[14]
        
        if head.output_channels > 2:
            head.channel_mapping = list(data[15:15 + head.output_channels])
    
    return head


def parse_opus_tags(data: bytes) -> OpusTags:
    """Parse OpusTags metadata."""
    tags = OpusTags()
    offset = 0
    
    if len(data) < 8:
        return tags
    
    vendor_length = struct.unpack("<I", data[0:4])[0]
    offset = 4
    
    if offset + vendor_length <= len(data):
        tags.vendor = data[offset:offset + vendor_length].decode('utf-8', errors='replace')
        offset += vendor_length
    
    if offset + 4 > len(data):
        return tags
    
    num_tags = struct.unpack("<I", data[offset:offset + 4])[0]
    offset += 4
    
    for _ in range(num_tags):
        if offset + 4 > len(data):
            break
            
        name_length = struct.unpack("<I", data[offset:offset + 4])[0]
        offset += 4
        
        if offset + name_length > len(data):
            break
            
        name = data[offset:offset + name_length].decode('utf-8', errors='replace')
        offset += name_length
        
        if offset + 4 > len(data):
            break
            
        value_length = struct.unpack("<I", data[offset:offset + 4])[0]
        offset += 4
        
        if offset + value_length > len(data):
            break
            
        value = data[offset:offset + value_length].decode('utf-8', errors='replace')
        offset += value_length
        
        normalized_name = OPUS_TAGS.get(name.upper(), name.lower())
        tags.tags[normalized_name] = value
    
    return tags


def extract_opus_metadata(filepath: str) -> Dict[str, Any]:
    """Extract Opus metadata from file."""
    
    result = {
        "file": filepath,
        "format": "Opus/Ogg",
        "file_size": 0,
        "opus_head": None,
        "opus_tags": None,
        "segments": [],
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
                header = f.read(27)
                if len(header) < 27:
                    break
                
                if not header.startswith(b"OggS"):
                    break
                
                version = header[4]
                header_type = header[5]
                granule_position = struct.unpack("<Q", header[6:14])[0]
                serial = struct.unpack("<I", header[14:18])[0]
                sequence = struct.unpack("<I", header[18:22])[0]
                checksum = struct.unpack("<I", header[22:26])[0]
                page_segments = header[26]
                
                segment_table = f.read(page_segments)
                total_segment_size = sum(segment_table)
                
                segment_data = f.read(total_segment_size) if total_segment_size > 0 else b""
                
                if segment_data.startswith(b"OpusHead"):
                    result["opus_head"] = parse_opus_head(segment_data[8:]).to_dict()
                    
                elif segment_data.startswith(b"OpusTags"):
                    result["opus_tags"] = parse_opus_tags(segment_data[9:]).to_dict()
                
                result["segments"].append({
                    "position": pos,
                    "granule": granule_position,
                    "serial": serial,
                    "sequence": sequence,
                    "type": header_type,
                    "size": total_segment_size,
                })
                
                if header_type & 0x04:
                    break
            
            f.close()
            
    except Exception as e:
        result["errors"].append(str(e))
    
    return result


def get_opus_field_count() -> int:
    """Get number of Opus fields we support."""
    return len(OPUS_TAGS) + 20


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        result = extract_opus_metadata(sys.argv[1])
        
        print("=" * 60)
        print("OPUS METADATA EXTRACTION TEST")
        print("=" * 60)
        print()
        print(f"File: {result.get('file')}")
        print(f"Format: {result.get('format')}")
        print(f"File Size: {result.get('file_size', 0):,} bytes")
        
        head = result.get("opus_head")
        if head:
            print(f"\nOpus Head:")
            print(f"  Version: {head.get('version', '?')}")
            print(f"  Channels: {head.get('output_channels', '?')}")
            print(f"  Sample Rate: {head.get('input_sample_rate', '?')} Hz")
            print(f"  Pre-skip: {head.get('pre_skip_samples', '?')} samples")
            print(f"  Mapping Family: {head.get('mapping_family', '?')}")
        
        tags = result.get("opus_tags")
        if tags:
            print(f"\nTags ({len(tags.get('tags', {}))}):")
            vendor = tags.get("vendor", "")
            if vendor:
                print(f"  Vendor: {vendor}")
            for k, v in list(tags.get("tags", {}).items())[:10]:
                print(f"  {k}: {v}")
        
        segments = result.get("segments", [])
        print(f"\nOgg Pages: {len(segments)}")
        
        errors = result.get("errors", [])
        if errors:
            print(f"\nErrors: {errors}")
        
        print(f"\nFields supported: {get_opus_field_count()}")
        
    else:
        print("Usage: python3 opus_extractor.py <file.opus|file.ogg>")
        sys.exit(1)
