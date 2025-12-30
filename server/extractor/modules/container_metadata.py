"""
Phase 2: Container Format Deep Analysis
MP4/MOV atom parsing, MKV EBML structure, WebM elements, AVI RIFF chunks
Target: +300-400 fields
"""

from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import struct
import json


# MP4/MOV Atom Types
MP4_ATOM_TYPES = {
    b'ftyp': 'File Type',
    b'moov': 'Movie',
    b'mvhd': 'Movie Header',
    b'trak': 'Track',
    b'tkhd': 'Track Header',
    b'mdia': 'Media',
    b'mdhd': 'Media Header',
    b'hdlr': 'Handler Reference',
    b'minf': 'Media Information',
    b'stbl': 'Sample Table',
    b'stsd': 'Sample Description',
    b'stts': 'Time-to-Sample',
    b'stsc': 'Sample-to-Chunk',
    b'stsz': 'Sample Size',
    b'stco': 'Chunk Offset',
    b'co64': 'Chunk Offset 64',
    b'stss': 'Sync Sample (Keyframes)',
    b'udta': 'User Data',
    b'meta': 'Metadata',
    b'mdat': 'Media Data',
    b'free': 'Free Space',
    b'skip': 'Skip',
    b'wide': 'Wide',
    b'edts': 'Edit List',
    b'elst': 'Edit List Table',
}

MP4_CONTAINER_ATOMS = {
    b'moov', b'trak', b'mdia', b'minf', b'stbl', b'edts', b'udta', b'meta', b'ilst', b'dinf',
}

MP4_TAG_MAP = {
    b"\xa9nam": "title",
    b"\xa9ART": "artist",
    b"\xa9alb": "album",
    b"\xa9day": "date",
    b"\xa9gen": "genre",
    b"\xa9cmt": "comment",
    b"\xa9wrt": "composer",
    b"\xa9too": "encoder",
    b"\xa9cpy": "copyright",
    b"aART": "album_artist",
    b"trkn": "track_number",
    b"disk": "disc_number",
    b"gnre": "genre_code",
    b"tmpo": "tempo",
    b"cpil": "compilation",
    b"pgap": "gapless",
    b"rtng": "rating",
    b"covr": "cover_art",
    b"desc": "description",
    b"ldes": "long_description",
    b"\xa9lyr": "lyrics",
    b"----": "freeform",
}

# MKV EBML Element IDs
MKV_ELEMENTS = {
    0x1A45DFA3: 'EBML',
    0x4286: 'EBMLVersion',
    0x42F7: 'EBMLReadVersion',
    0x42F2: 'EBMLMaxIDLength',
    0x42F3: 'EBMLMaxSizeLength',
    0x4282: 'DocType',
    0x4287: 'DocTypeVersion',
    0x4285: 'DocTypeReadVersion',
    0x18538067: 'Segment',
    0x114D9B74: 'SeekHead',
    0x1549A966: 'Info',
    0x73A4: 'SegmentUID',
    0x7384: 'SegmentFilename',
    0x2AD7B1: 'TimecodeScale',
    0x4489: 'Duration',
    0x4461: 'DateUTC',
    0x7BA9: 'Title',
    0x4D80: 'MuxingApp',
    0x5741: 'WritingApp',
    0x1654AE6B: 'Tracks',
    0xAE: 'TrackEntry',
    0xD7: 'TrackNumber',
    0x73C5: 'TrackUID',
    0x83: 'TrackType',
    0xB9: 'FlagEnabled',
    0x88: 'FlagDefault',
    0x55AA: 'FlagForced',
    0x9C: 'FlagLacing',
    0x536E: 'Name',
    0x22B59C: 'Language',
    0x86: 'CodecID',
    0x63A2: 'CodecPrivate',
    0x258688: 'CodecName',
    0x1C53BB6B: 'Cues',
    0x1254C367: 'Tags',
    0x1043A770: 'Chapters',
    0xE0: 'Video',
    0xE1: 'Audio',
    0xB0: 'PixelWidth',
    0xBA: 'PixelHeight',
    0x54B0: 'DisplayWidth',
    0x54BA: 'DisplayHeight',
    0x54B2: 'DisplayUnit',
    0x53B8: 'StereoMode',
    0xB5: 'SamplingFrequency',
    0x78B5: 'OutputSamplingFrequency',
    0x9F: 'Channels',
    0x6264: 'BitDepth',
    0x7373: 'Tag',
    0x67C8: 'SimpleTag',
    0x45A3: 'TagName',
    0x4487: 'TagString',
    0x4485: 'TagBinary',
    0x45B9: 'EditionEntry',
    0xB6: 'ChapterAtom',
    0x91: 'ChapterTimeStart',
    0x92: 'ChapterTimeEnd',
    0x80: 'ChapterDisplay',
    0x85: 'ChapString',
    0x437C: 'ChapLanguage',
}

MKV_TRACK_TYPES = {
    1: "video",
    2: "audio",
    17: "subtitle",
}

AVI_INFO_TAGS = {
    b"IART": "artist",
    b"INAM": "title",
    b"IPRD": "album",
    b"ICMT": "comment",
    b"ICRD": "creation_date",
    b"IGNR": "genre",
    b"ICOP": "copyright",
    b"ISFT": "software",
    b"ITRK": "track_number",
    b"IPRT": "part",
    b"ISBJ": "subject",
    b"ISRC": "isrc",
    b"ITCH": "technician",
    b"IENG": "engineer",
    b"IKEY": "keywords",
    b"ILNG": "language",
    b"IMED": "medium",
    b"ISRF": "source_form",
}


def _count_fields(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, dict):
        return sum(_count_fields(v) for v in value.values())
    if isinstance(value, list):
        return sum(_count_fields(v) for v in value)
    return 1


def _iter_mp4_atoms(f, start: int, size: int, max_depth: int) -> List[Tuple[bytes, int, int, int]]:
    results: List[Tuple[bytes, int, int, int]] = []
    end = start + size
    f.seek(start, 0)
    while f.tell() + 8 <= end:
        header = f.read(8)
        if len(header) < 8:
            break
        atom_size = struct.unpack(">I", header[0:4])[0]
        atom_type = header[4:8]
        header_size = 8
        if atom_size == 1:
            extended = f.read(8)
            if len(extended) < 8:
                break
            atom_size = struct.unpack(">Q", extended)[0]
            header_size = 16
        elif atom_size == 0:
            atom_size = end - (f.tell() - 8)

        if atom_size < header_size:
            break
        data_start = f.tell()
        data_size = atom_size - header_size
        results.append((atom_type, data_start, data_size, header_size))

        if atom_type in MP4_CONTAINER_ATOMS and max_depth > 0:
            child_start = data_start
            child_size = data_size
            if atom_type == b"meta":
                child_start += 4
                child_size = max(0, child_size - 4)
            results.extend(_iter_mp4_atoms(f, child_start, child_size, max_depth - 1))

        f.seek(data_start + data_size, 0)
    return results


def _decode_mp4_data(data_type: int, data: bytes) -> Any:
    if data_type == 1:
        return data.decode("utf-8", errors="ignore")
    if data_type in [13, 14]:
        if data.startswith(b"\xff\xd8"):
            mime = "image/jpeg"
        elif data.startswith(b"\x89PNG"):
            mime = "image/png"
        else:
            mime = "application/octet-stream"
        return {"mime": mime, "size_bytes": len(data)}
    if len(data) == 2:
        return struct.unpack(">H", data)[0]
    if len(data) == 4:
        return struct.unpack(">I", data)[0]
    return data.hex()


def _parse_mp4_item(f, start: int, size: int, item_type: Optional[bytes] = None) -> Dict[str, Any]:
    result: Dict[str, Any] = {"value": None, "freeform": {}}
    f.seek(start, 0)
    end = start + size
    mean_value = None
    name_value = None
    data_values: List[Any] = []
    raw_payloads: List[bytes] = []
    while f.tell() + 8 <= end:
        header = f.read(8)
        if len(header) < 8:
            break
        atom_size = struct.unpack(">I", header[0:4])[0]
        atom_type = header[4:8]
        if atom_size < 8:
            break
        data_start = f.tell()
        data_size = atom_size - 8
        payload = f.read(data_size)
        if atom_type == b"mean":
            mean_value = payload[4:].decode("utf-8", errors="ignore").strip("\x00")
        elif atom_type == b"name":
            name_value = payload[4:].decode("utf-8", errors="ignore").strip("\x00")
        elif atom_type == b"data":
            if len(payload) >= 8:
                data_type = struct.unpack(">I", payload[0:4])[0]
                data_payload = payload[8:]
                raw_payloads.append(data_payload)
                data_values.append(_decode_mp4_data(data_type, data_payload))
        f.seek(data_start + data_size, 0)

    if item_type in [b"trkn", b"disk"] and raw_payloads:
        payload = raw_payloads[0]
        if len(payload) >= 6:
            current = struct.unpack(">H", payload[2:4])[0]
            total = struct.unpack(">H", payload[4:6])[0]
            result["value"] = {"current": current, "total": total}
    elif item_type == b"gnre" and raw_payloads:
        payload = raw_payloads[0]
        if len(payload) >= 2:
            result["value"] = struct.unpack(">H", payload[0:2])[0]
    elif item_type in [b"cpil", b"pgap"] and raw_payloads:
        result["value"] = bool(raw_payloads[0][0]) if raw_payloads[0] else None
    elif item_type == b"tmpo" and raw_payloads:
        payload = raw_payloads[0]
        if len(payload) >= 2:
            result["value"] = struct.unpack(">H", payload[0:2])[0]
    elif data_values:
        result["value"] = data_values[0] if len(data_values) == 1 else data_values

    if mean_value and name_value and data_values:
        key = f"{mean_value}:{name_value}"
        result["freeform"][key] = data_values[0] if len(data_values) == 1 else data_values
    return result


def _parse_mp4_ilst(filepath: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"tags": {}, "raw_tags": {}, "tag_count": 0}
    try:
        file_size = Path(filepath).stat().st_size
        with open(filepath, "rb") as f:
            for atom_type, start, size, _ in _iter_mp4_atoms(f, 0, file_size, 6):
                if atom_type != b"ilst":
                    continue
                f.seek(start, 0)
                end = start + size
                while f.tell() + 8 <= end:
                    item_header = f.read(8)
                    if len(item_header) < 8:
                        break
                    item_size = struct.unpack(">I", item_header[0:4])[0]
                    item_type = item_header[4:8]
                    if item_size < 8:
                        break
                    item_start = f.tell()
                    item_end = item_start + (item_size - 8)
                    item_data = _parse_mp4_item(f, item_start, item_size - 8, item_type)
                    friendly = MP4_TAG_MAP.get(item_type, item_type.decode("latin1", errors="ignore"))
                    result["raw_tags"][item_type.decode("latin1", errors="ignore")] = item_data
                    if friendly == "freeform":
                        for freeform_key, freeform_value in item_data.get("freeform", {}).items():
                            result["tags"][freeform_key] = freeform_value
                    else:
                        result["tags"][friendly] = item_data.get("value")
                    f.seek(item_end, 0)
                result["tag_count"] = len(result["tags"])
                break
    except Exception:
        return result
    return result


def _read_ebml_id(f) -> Tuple[int, int]:
    first = f.read(1)
    if not first:
        return 0, 0
    first_byte = first[0]
    mask = 0x80
    length = 1
    while length <= 4 and not (first_byte & mask):
        mask >>= 1
        length += 1
    if length > 4:
        return 0, 0
    value = first_byte
    rest = f.read(length - 1)
    for b in rest:
        value = (value << 8) | b
    return value, length


def _read_ebml_size(f) -> Tuple[int, int]:
    first = f.read(1)
    if not first:
        return 0, 0
    first_byte = first[0]
    mask = 0x80
    length = 1
    while length <= 8 and not (first_byte & mask):
        mask >>= 1
        length += 1
    if length > 8:
        return 0, 0
    value = first_byte & (mask - 1)
    rest = f.read(length - 1)
    for b in rest:
        value = (value << 8) | b
    unknown = (value == (1 << (7 * length)) - 1)
    return (-1 if unknown else value), length


def _iter_ebml_elements(data: bytes) -> List[Tuple[int, bytes]]:
    elements: List[Tuple[int, bytes]] = []
    offset = 0
    total = len(data)
    while offset < total:
        buf = data[offset:]
        f = memoryview(buf)
        if not f:
            break
        first_byte = f[0]
        mask = 0x80
        id_len = 1
        while id_len <= 4 and not (first_byte & mask):
            mask >>= 1
            id_len += 1
        if id_len > 4 or offset + id_len > total:
            break
        element_id = 0
        for i in range(id_len):
            element_id = (element_id << 8) | f[i]
        offset += id_len
        if offset >= total:
            break
        size_first = data[offset]
        mask = 0x80
        size_len = 1
        while size_len <= 8 and not (size_first & mask):
            mask >>= 1
            size_len += 1
        if size_len > 8 or offset + size_len > total:
            break
        size_value = size_first & (mask - 1)
        for i in range(1, size_len):
            size_value = (size_value << 8) | data[offset + i]
        offset += size_len
        if size_value == (1 << (7 * size_len)) - 1:
            size_value = total - offset
        element_data = data[offset:offset + size_value]
        offset += size_value
        elements.append((element_id, element_data))
    return elements


def extract_container_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract comprehensive container format metadata.
    
    Supports:
    - MP4/MOV: Atom structure, brands, timescales
    - MKV/WebM: EBML structure, segments, tracks
    - AVI: RIFF chunks, stream headers
    - Other: Format-specific metadata
    
    Target: ~350 fields
    """
    result = {
        "format_type": None,
        "mp4_atoms": {},
        "mkv_ebml": {},
        "avi_chunks": {},
        "stream_mapping": {},
        "timing_info": {},
        "metadata_atoms": {},
        "fields_extracted": 0
    }
    
    try:
        path = Path(filepath)
        if not path.exists():
            result["error"] = "File not found"
            return result
        
        # Detect container format by magic bytes
        with open(filepath, 'rb') as f:
            magic = f.read(12)
        
        if len(magic) < 8:
            result["error"] = "File too small"
            return result
        
        # MP4/MOV detection
        if magic[4:8] in [b'ftyp', b'mdat', b'moov', b'free', b'skip', b'wide']:
            result["format_type"] = "MP4/MOV"
            result["mp4_atoms"] = parse_mp4_atoms(filepath)
            result["metadata_atoms"] = extract_mp4_metadata_atoms(filepath)
            result["timing_info"] = extract_mp4_timing(filepath)
        
        # MKV/WebM detection
        elif magic[0:4] == b'\x1A\x45\xDF\xA3':
            result["format_type"] = "MKV/WebM"
            result["mkv_ebml"] = parse_mkv_ebml(filepath)
        
        # AVI detection
        elif magic[0:4] == b'RIFF' and magic[8:12] == b'AVI ':
            result["format_type"] = "AVI"
            result["avi_chunks"] = parse_avi_chunks(filepath)
        
        # Stream mapping
        stream_mapping = {
            "total_tracks": 0,
            "video_tracks": 0,
            "audio_tracks": 0,
            "subtitle_tracks": 0,
        }
        if result.get("mp4_atoms", {}).get("tracks"):
            for track in result["mp4_atoms"]["tracks"]:
                stream_mapping["total_tracks"] += 1
                handler = track.get("handler_type")
                if handler == "vide":
                    stream_mapping["video_tracks"] += 1
                elif handler == "soun":
                    stream_mapping["audio_tracks"] += 1
                elif handler in ["sbtl", "text", "subt"]:
                    stream_mapping["subtitle_tracks"] += 1
        if result.get("mkv_ebml", {}).get("tracks"):
            for track in result["mkv_ebml"]["tracks"]:
                stream_mapping["total_tracks"] += 1
                track_type = track.get("track_type")
                if track_type == "video":
                    stream_mapping["video_tracks"] += 1
                elif track_type == "audio":
                    stream_mapping["audio_tracks"] += 1
                elif track_type == "subtitle":
                    stream_mapping["subtitle_tracks"] += 1
        if result.get("avi_chunks", {}).get("streams"):
            for track in result["avi_chunks"]["streams"]:
                stream_mapping["total_tracks"] += 1
                track_type = track.get("stream_type")
                if track_type == "video":
                    stream_mapping["video_tracks"] += 1
                elif track_type == "audio":
                    stream_mapping["audio_tracks"] += 1
        result["stream_mapping"] = stream_mapping

        # Count fields
        result["fields_extracted"] = sum(
            _count_fields(value)
            for key, value in result.items()
            if key not in ["fields_extracted"]
        )
        
    except Exception as e:
        result["error"] = str(e)[:200]
    
    return result


def parse_mp4_atoms(filepath: str, max_depth: int = 6) -> Dict[str, Any]:
    """
    Parse MP4/MOV atom structure.
    
    Returns ~150 fields including:
    - ftyp: major_brand, minor_version, compatible_brands
    - mvhd: creation_time, modification_time, timescale, duration
    - tkhd: track_id, width, height, volume
    - mdhd: media_timescale, media_duration, language
    - stsd: codec details per track
    - stss: keyframe indices
    """
    result = {
        "ftyp": {},
        "mvhd": {},
        "tracks": [],
        "udta": {},
        "meta": {},
        "atom_tree": [],
        "total_atoms": 0,
        "container_atoms": 0,
        "data_atoms": 0
    }
    
    try:
        with open(filepath, 'rb') as f:
            file_size = Path(filepath).stat().st_size
            _parse_mp4_container(f, 0, file_size, result, max_depth, None)
    except Exception:
        pass
    
    return result


def _parse_mp4_container(f, start: int, size: int, result: Dict[str, Any], max_depth: int, current_track: Optional[Dict[str, Any]]) -> None:
    end = start + size
    f.seek(start, 0)
    while f.tell() + 8 <= end:
        header = f.read(8)
        if len(header) < 8:
            break
        atom_size = struct.unpack(">I", header[0:4])[0]
        atom_type = header[4:8]
        header_size = 8
        if atom_size == 1:
            extended = f.read(8)
            if len(extended) < 8:
                break
            atom_size = struct.unpack(">Q", extended)[0]
            header_size = 16
        elif atom_size == 0:
            atom_size = end - (f.tell() - 8)

        if atom_size < header_size:
            break
        data_start = f.tell()
        data_size = atom_size - header_size

        result["total_atoms"] += 1
        if atom_type == b"mdat":
            result["data_atoms"] += 1
        if atom_type in MP4_CONTAINER_ATOMS:
            result["container_atoms"] += 1

        result["atom_tree"].append({
            "type": atom_type.decode("latin1", errors="ignore"),
            "size": atom_size,
            "offset": data_start - header_size,
        })

        if atom_type in MP4_CONTAINER_ATOMS and max_depth > 0:
            child_start = data_start
            child_size = data_size
            if atom_type == b"meta":
                child_start += 4
                child_size = max(0, child_size - 4)
            if atom_type == b"trak":
                track: Dict[str, Any] = {}
                result["tracks"].append(track)
                _parse_mp4_container(f, child_start, child_size, result, max_depth - 1, track)
            else:
                _parse_mp4_container(f, child_start, child_size, result, max_depth - 1, current_track)
            f.seek(data_start + data_size, 0)
            continue

        f.seek(data_start, 0)
        if atom_type == b"ftyp":
            result["ftyp"] = parse_ftyp_atom(f, data_size)
        elif atom_type == b"mvhd":
            result["mvhd"] = parse_mvhd_atom(f, data_size)
        elif atom_type == b"tkhd" and current_track is not None:
            current_track.update(parse_tkhd_atom(f, data_size))
        elif atom_type == b"mdhd" and current_track is not None:
            current_track.update(parse_mdhd_atom(f, data_size))
        elif atom_type == b"hdlr" and current_track is not None:
            current_track.update(parse_hdlr_atom(f, data_size))
        elif atom_type == b"stsd" and current_track is not None:
            current_track["stsd"] = parse_stsd_atom(f, data_size)
        elif atom_type == b"stts" and current_track is not None:
            current_track["stts"] = parse_stts_atom(f, data_size)
        elif atom_type == b"ctts" and current_track is not None:
            current_track["ctts"] = parse_ctts_atom(f, data_size)
        elif atom_type == b"stsc" and current_track is not None:
            current_track["stsc"] = parse_stsc_atom(f, data_size)
        elif atom_type == b"stsz" and current_track is not None:
            current_track["stsz"] = parse_stsz_atom(f, data_size)
        elif atom_type in [b"stco", b"co64"] and current_track is not None:
            current_track[atom_type.decode("latin1")] = parse_stco_atom(f, data_size, is_64=(atom_type == b"co64"))
        elif atom_type == b"stss" and current_track is not None:
            current_track["stss"] = parse_stss_atom(f, data_size)
        elif atom_type == b"elst" and current_track is not None:
            current_track["elst"] = parse_elst_atom(f, data_size)

        f.seek(data_start + data_size, 0)


def parse_ftyp_atom(f, size: int) -> Dict[str, Any]:
    """Parse ftyp (File Type) atom."""
    result = {}
    
    try:
        data = f.read(size)
        if len(data) >= 8:
            result["major_brand"] = data[0:4].decode('latin1')
            result["minor_version"] = struct.unpack('>I', data[4:8])[0]
            
            compatible_brands = []
            offset = 8
            while offset + 4 <= len(data):
                brand = data[offset:offset+4].decode('latin1')
                compatible_brands.append(brand)
                offset += 4
            
            result["compatible_brands"] = compatible_brands
            result["compatible_brands_count"] = len(compatible_brands)
    
    except Exception as e:
        pass  # TODO: Consider logging: logger.debug(f'Handled exception: {e}')
    
    return result


def parse_mvhd_atom(f, size: int) -> Dict[str, Any]:
    """Parse mvhd (Movie Header) atom."""
    result = {}
    
    try:
        data = f.read(size)
        
        version = data[0]
        result["version"] = version
        result["flags"] = struct.unpack('>I', b'\x00' + data[1:4])[0]
        
        if version == 1:
            # 64-bit version
            result["creation_time"] = struct.unpack('>Q', data[4:12])[0]
            result["modification_time"] = struct.unpack('>Q', data[12:20])[0]
            result["timescale"] = struct.unpack('>I', data[20:24])[0]
            result["duration"] = struct.unpack('>Q', data[24:32])[0]
        else:
            # 32-bit version
            result["creation_time"] = struct.unpack('>I', data[4:8])[0]
            result["modification_time"] = struct.unpack('>I', data[8:12])[0]
            result["timescale"] = struct.unpack('>I', data[12:16])[0]
            result["duration"] = struct.unpack('>I', data[16:20])[0]
        
        # Convert to seconds
        if result["timescale"] > 0:
            result["duration_seconds"] = result["duration"] / result["timescale"]
        
        # Convert Mac epoch (1904) to Unix epoch (1970)
        MAC_EPOCH_OFFSET = 2082844800
        if result["creation_time"] > MAC_EPOCH_OFFSET:
            result["creation_time_unix"] = result["creation_time"] - MAC_EPOCH_OFFSET
            result["modification_time_unix"] = result["modification_time"] - MAC_EPOCH_OFFSET
        
        # Rate (fixed-point 16.16)
        offset = 32 if version == 1 else 20
        if len(data) >= offset + 4:
            rate_raw = struct.unpack('>I', data[offset:offset+4])[0]
            result["preferred_rate"] = rate_raw / 65536.0
        
        # Volume (fixed-point 8.8)
        if len(data) >= offset + 6:
            volume_raw = struct.unpack('>H', data[offset+4:offset+6])[0]
            result["preferred_volume"] = volume_raw / 256.0
        
        # Next track ID
        if len(data) >= offset + 80:
            result["next_track_id"] = struct.unpack('>I', data[offset+76:offset+80])[0]
    
    except Exception as e:
        pass  # TODO: Consider logging: logger.debug(f'Handled exception: {e}')
    
    return result


def parse_tkhd_atom(f, size: int) -> Dict[str, Any]:
    """Parse tkhd (Track Header) atom."""
    result = {}
    
    try:
        data = f.read(size)
        
        version = data[0]
        result["tkhd_version"] = version
        result["tkhd_flags"] = struct.unpack('>I', b'\x00' + data[1:4])[0]
        
        # Check flags
        result["track_enabled"] = (result["tkhd_flags"] & 0x000001) != 0
        result["track_in_movie"] = (result["tkhd_flags"] & 0x000002) != 0
        result["track_in_preview"] = (result["tkhd_flags"] & 0x000004) != 0
        
        if version == 1:
            result["track_creation_time"] = struct.unpack('>Q', data[4:12])[0]
            result["track_modification_time"] = struct.unpack('>Q', data[12:20])[0]
            result["track_id"] = struct.unpack('>I', data[20:24])[0]
            result["track_duration"] = struct.unpack('>Q', data[28:36])[0]
            offset = 36
        else:
            result["track_creation_time"] = struct.unpack('>I', data[4:8])[0]
            result["track_modification_time"] = struct.unpack('>I', data[8:12])[0]
            result["track_id"] = struct.unpack('>I', data[12:16])[0]
            result["track_duration"] = struct.unpack('>I', data[20:24])[0]
            offset = 24
        
        # Skip reserved bytes (8 bytes)
        offset += 8
        
        # Layer and alternate group
        if len(data) >= offset + 4:
            result["track_layer"] = struct.unpack('>h', data[offset:offset+2])[0]
            result["track_alternate_group"] = struct.unpack('>h', data[offset+2:offset+4])[0]
        offset += 4
        
        # Volume
        if len(data) >= offset + 2:
            volume_raw = struct.unpack('>H', data[offset:offset+2])[0]
            result["track_volume"] = volume_raw / 256.0
        offset += 2
        
        # Skip reserved (2 bytes)
        offset += 2
        
        # Matrix (36 bytes) - skip for now
        offset += 36
        
        # Width and height (fixed-point 16.16)
        if len(data) >= offset + 8:
            width_raw = struct.unpack('>I', data[offset:offset+4])[0]
            height_raw = struct.unpack('>I', data[offset+4:offset+8])[0]
            result["track_width"] = width_raw / 65536.0
            result["track_height"] = height_raw / 65536.0
    
    except Exception as e:
        pass  # TODO: Consider logging: logger.debug(f'Handled exception: {e}')
    
    return result


def parse_mdhd_atom(f, size: int) -> Dict[str, Any]:
    """Parse mdhd (Media Header) atom."""
    result = {}
    
    try:
        data = f.read(size)
        
        version = data[0]
        result["mdhd_version"] = version
        
        if version == 1:
            result["media_creation_time"] = struct.unpack('>Q', data[4:12])[0]
            result["media_modification_time"] = struct.unpack('>Q', data[12:20])[0]
            result["media_timescale"] = struct.unpack('>I', data[20:24])[0]
            result["media_duration"] = struct.unpack('>Q', data[24:32])[0]
            offset = 32
        else:
            result["media_creation_time"] = struct.unpack('>I', data[4:8])[0]
            result["media_modification_time"] = struct.unpack('>I', data[8:12])[0]
            result["media_timescale"] = struct.unpack('>I', data[12:16])[0]
            result["media_duration"] = struct.unpack('>I', data[16:20])[0]
            offset = 20
        
        # Duration in seconds
        if result["media_timescale"] > 0:
            result["media_duration_seconds"] = result["media_duration"] / result["media_timescale"]
        
        # Language (ISO 639-2/T)
        if len(data) >= offset + 2:
            lang_code = struct.unpack('>H', data[offset:offset+2])[0]
            # Each character is 5 bits, offset by 0x60
            lang_chars = [
                chr(((lang_code >> 10) & 0x1F) + 0x60),
                chr(((lang_code >> 5) & 0x1F) + 0x60),
                chr((lang_code & 0x1F) + 0x60)
            ]
            result["media_language"] = ''.join(lang_chars)
    
    except Exception as e:
        pass  # TODO: Consider logging: logger.debug(f'Handled exception: {e}')
    
    return result


def parse_hdlr_atom(f, size: int) -> Dict[str, Any]:
    """Parse hdlr (Handler Reference) atom."""
    result = {}
    
    try:
        data = f.read(size)
        
        version = data[0]
        result["hdlr_version"] = version
        
        # Component type (4 bytes) - skip
        # Component subtype (handler type)
        handler_type = data[8:12].decode('latin1')
        result["handler_type"] = handler_type
        result["handler_description"] = {
            'vide': 'Video Track',
            'soun': 'Audio Track',
            'hint': 'Hint Track',
            'meta': 'Metadata Track',
            'text': 'Text Track',
            'sbtl': 'Subtitle Track'
        }.get(handler_type, handler_type)
        
        # Skip reserved (12 bytes)
        # Component name (null-terminated string)
        if len(data) > 24:
            name_data = data[24:]
            # Remove null bytes
            name = name_data.rstrip(b'\x00').decode('utf-8', errors='ignore')
            result["handler_name"] = name
    
    except Exception as e:
        pass  # TODO: Consider logging: logger.debug(f'Handled exception: {e}')
    
    return result


def parse_stsd_atom(f, size: int) -> Dict[str, Any]:
    """Parse stsd (Sample Description) atom."""
    result = {"entry_count": 0, "entries": []}
    try:
        data = f.read(size)
        if len(data) < 8:
            return result
        result["version"] = data[0]
        result["flags"] = struct.unpack(">I", b"\x00" + data[1:4])[0]
        entry_count = struct.unpack(">I", data[4:8])[0]
        result["entry_count"] = entry_count
        offset = 8
        for _ in range(entry_count):
            if offset + 8 > len(data):
                break
            entry_size = struct.unpack(">I", data[offset:offset + 4])[0]
            entry_type = data[offset + 4:offset + 8]
            entry_data = data[offset:offset + entry_size]
            entry = parse_mp4_sample_entry(entry_type, entry_data)
            result["entries"].append(entry)
            offset += entry_size if entry_size > 0 else 0
            if entry_size == 0:
                break
    except Exception:
        return result
    return result


def parse_mp4_sample_entry(entry_type: bytes, entry_data: bytes) -> Dict[str, Any]:
    entry: Dict[str, Any] = {
        "codec_fourcc": entry_type.decode("latin1", errors="ignore"),
        "size": len(entry_data),
    }
    if len(entry_data) < 16:
        return entry
    data_reference_index = struct.unpack(">H", entry_data[14:16])[0]
    entry["data_reference_index"] = data_reference_index
    child_offset = 8
    if entry_type in [b"avc1", b"hvc1", b"hev1", b"mp4v", b"av01", b"vp09", b"avc3"]:
        if len(entry_data) >= 36:
            entry["width"] = struct.unpack(">H", entry_data[32:34])[0]
            entry["height"] = struct.unpack(">H", entry_data[34:36])[0]
        if len(entry_data) >= 52:
            entry["horiz_resolution"] = struct.unpack(">I", entry_data[36:40])[0] / 65536.0
            entry["vert_resolution"] = struct.unpack(">I", entry_data[40:44])[0] / 65536.0
        if len(entry_data) >= 54:
            entry["frame_count"] = struct.unpack(">H", entry_data[48:50])[0]
        if len(entry_data) >= 86:
            compressor = entry_data[50:82].rstrip(b"\x00")
            entry["compressor_name"] = compressor.decode("latin1", errors="ignore")
        if len(entry_data) >= 88:
            entry["depth"] = struct.unpack(">H", entry_data[82:84])[0]
        child_offset = 86
    elif entry_type in [b"mp4a", b"alac", b"ac-3", b"ec-3", b"Opus", b"fLaC"]:
        if len(entry_data) >= 28:
            entry["channel_count"] = struct.unpack(">H", entry_data[24:26])[0]
            entry["sample_size"] = struct.unpack(">H", entry_data[26:28])[0]
        if len(entry_data) >= 36:
            entry["sample_rate"] = struct.unpack(">I", entry_data[32:36])[0] / 65536.0
        child_offset = 36

    if len(entry_data) > child_offset:
        children = _parse_mp4_child_atoms(entry_data[child_offset:])
    else:
        children = {}
    if children:
        entry["child_atoms"] = children
    return entry


def _parse_mp4_child_atoms(data: bytes) -> Dict[str, Any]:
    children: Dict[str, Any] = {}
    offset = 0
    while offset + 8 <= len(data):
        atom_size = struct.unpack(">I", data[offset:offset + 4])[0]
        atom_type = data[offset + 4:offset + 8]
        if atom_size < 8 or offset + atom_size > len(data):
            break
        payload = data[offset + 8:offset + atom_size]
        atom_name = atom_type.decode("latin1", errors="ignore")
        if atom_type == b"avcC" and len(payload) >= 4:
            children["avcC"] = {
                "configuration_version": payload[0],
                "profile": payload[1],
                "compatibility": payload[2],
                "level": payload[3],
            }
        elif atom_type == b"hvcC" and len(payload) >= 12:
            children["hvcC"] = {
                "configuration_version": payload[0],
                "profile_space": (payload[1] >> 6) & 0x03,
                "tier_flag": (payload[1] >> 5) & 0x01,
                "profile_idc": payload[1] & 0x1F,
                "level_idc": payload[12] if len(payload) > 12 else payload[11],
            }
        elif atom_type == b"av1C" and len(payload) >= 4:
            seq_profile = (payload[1] >> 5) & 0x07
            seq_level_idx_0 = payload[1] & 0x1F
            children["av1C"] = {
                "marker": payload[0] >> 7,
                "version": payload[0] & 0x7F,
                "seq_profile": seq_profile,
                "seq_level_idx_0": seq_level_idx_0,
            }
        elif atom_type == b"esds":
            children["esds"] = _parse_mp4_esds(payload)
        elif atom_type == b"pasp" and len(payload) >= 8:
            h_spacing = struct.unpack(">I", payload[0:4])[0]
            v_spacing = struct.unpack(">I", payload[4:8])[0]
            children["pasp"] = {
                "h_spacing": h_spacing,
                "v_spacing": v_spacing,
                "pixel_aspect_ratio": (h_spacing / v_spacing) if v_spacing else None,
            }
        elif atom_type == b"clap" and len(payload) >= 32:
            width_n = struct.unpack(">I", payload[0:4])[0]
            width_d = struct.unpack(">I", payload[4:8])[0]
            height_n = struct.unpack(">I", payload[8:12])[0]
            height_d = struct.unpack(">I", payload[12:16])[0]
            horiz_n = struct.unpack(">i", payload[16:20])[0]
            horiz_d = struct.unpack(">i", payload[20:24])[0]
            vert_n = struct.unpack(">i", payload[24:28])[0]
            vert_d = struct.unpack(">i", payload[28:32])[0]
            children["clap"] = {
                "clean_width_n": width_n,
                "clean_width_d": width_d,
                "clean_height_n": height_n,
                "clean_height_d": height_d,
                "horiz_offset_n": horiz_n,
                "horiz_offset_d": horiz_d,
                "vert_offset_n": vert_n,
                "vert_offset_d": vert_d,
                "clean_width": (width_n / width_d) if width_d else None,
                "clean_height": (height_n / height_d) if height_d else None,
                "horiz_offset": (horiz_n / horiz_d) if horiz_d else None,
                "vert_offset": (vert_n / vert_d) if vert_d else None,
            }
        elif atom_type == b"colr" and len(payload) >= 4:
            color_type = payload[0:4].decode("latin1", errors="ignore")
            colr: Dict[str, Any] = {"type": color_type}
            if color_type in ["nclx", "nclc"] and len(payload) >= 10:
                colr["primaries"] = struct.unpack(">H", payload[4:6])[0]
                colr["transfer"] = struct.unpack(">H", payload[6:8])[0]
                colr["matrix"] = struct.unpack(">H", payload[8:10])[0]
                if len(payload) >= 11:
                    colr["full_range_flag"] = bool(payload[10] & 0x80)
            elif color_type in ["prof", "rICC"]:
                colr["icc_profile_size"] = max(0, len(payload) - 4)
            children["colr"] = colr
        elif atom_type == b"fiel" and len(payload) >= 2:
            children["fiel"] = {
                "field_count": payload[0],
                "field_order": payload[1],
            }
        elif atom_type == b"chan" and len(payload) >= 12:
            layout_tag = struct.unpack(">I", payload[0:4])[0]
            bitmap = struct.unpack(">I", payload[4:8])[0]
            desc_count = struct.unpack(">I", payload[8:12])[0]
            descriptions = []
            desc_offset = 12
            for _ in range(min(desc_count, 4)):
                if desc_offset + 20 > len(payload):
                    break
                label = struct.unpack(">I", payload[desc_offset:desc_offset + 4])[0]
                flags = struct.unpack(">I", payload[desc_offset + 4:desc_offset + 8])[0]
                descriptions.append({"label": label, "flags": flags})
                desc_offset += 20
            children["chan"] = {
                "layout_tag": layout_tag,
                "channel_bitmap": bitmap,
                "description_count": desc_count,
                "descriptions": descriptions,
            }
        elif atom_type == b"st3d" and len(payload) >= 1:
            children["st3d"] = {"stereo_mode": payload[0]}
        elif atom_type == b"sv3d" and len(payload) >= 8:
            children["sv3d"] = {"child_atoms": _parse_mp4_child_atoms(payload)}
        elif atom_type == b"uuid" and len(payload) >= 16:
            uuid_bytes = payload[0:16]
            uuid_str = "-".join([
                uuid_bytes[0:4].hex(),
                uuid_bytes[4:6].hex(),
                uuid_bytes[6:8].hex(),
                uuid_bytes[8:10].hex(),
                uuid_bytes[10:16].hex(),
            ])
            children["uuid"] = {"uuid": uuid_str, "payload_size": max(0, len(payload) - 16)}
        else:
            children[atom_name] = {"data_size": len(payload)}
        offset += atom_size
    return children


def _parse_mp4_esds(payload: bytes) -> Dict[str, Any]:
    result: Dict[str, Any] = {"data_size": len(payload)}
    offset = 0
    if len(payload) < 2:
        return result
    if payload[0] == 0x03:
        offset = 1
        desc_size, size_len = _read_mp4_descriptor_size(payload, offset)
        offset += size_len
        if offset + 2 <= len(payload):
            result["es_id"] = struct.unpack(">H", payload[offset:offset + 2])[0]
        offset += 3
    while offset + 2 < len(payload):
        tag = payload[offset]
        offset += 1
        size, size_len = _read_mp4_descriptor_size(payload, offset)
        offset += size_len
        if tag == 0x04 and offset + 13 <= len(payload):
            result["object_type"] = payload[offset]
            result["stream_type"] = (payload[offset + 1] >> 2) & 0x3F
            result["buffer_size_db"] = int.from_bytes(payload[offset + 2:offset + 5], "big")
            result["max_bitrate"] = struct.unpack(">I", payload[offset + 5:offset + 9])[0]
            result["avg_bitrate"] = struct.unpack(">I", payload[offset + 9:offset + 13])[0]
        elif tag == 0x05 and size >= 2 and offset + size <= len(payload):
            asc = payload[offset:offset + size]
            audio_obj = (asc[0] >> 3) & 0x1F
            freq_idx = ((asc[0] & 0x07) << 1) | ((asc[1] >> 7) & 0x01)
            channel_cfg = (asc[1] >> 3) & 0x0F
            result["audio_object_type"] = audio_obj
            result["audio_freq_index"] = freq_idx
            result["audio_channel_config"] = channel_cfg
        offset += size
    return result


def _read_mp4_descriptor_size(data: bytes, offset: int) -> Tuple[int, int]:
    size = 0
    count = 0
    while offset + count < len(data):
        byte = data[offset + count]
        size = (size << 7) | (byte & 0x7F)
        count += 1
        if not (byte & 0x80) or count >= 4:
            break
    return size, count


def parse_stts_atom(f, size: int) -> Dict[str, Any]:
    result = {"entry_count": 0, "total_samples": 0, "total_duration": 0}
    try:
        data = f.read(size)
        if len(data) < 8:
            return result
        entry_count = struct.unpack(">I", data[4:8])[0]
        result["entry_count"] = entry_count
        offset = 8
        for _ in range(entry_count):
            if offset + 8 > len(data):
                break
            sample_count = struct.unpack(">I", data[offset:offset + 4])[0]
            sample_delta = struct.unpack(">I", data[offset + 4:offset + 8])[0]
            result["total_samples"] += sample_count
            result["total_duration"] += sample_count * sample_delta
            offset += 8
    except Exception:
        return result
    return result


def parse_ctts_atom(f, size: int) -> Dict[str, Any]:
    result = {"entry_count": 0}
    try:
        data = f.read(size)
        if len(data) < 8:
            return result
        entry_count = struct.unpack(">I", data[4:8])[0]
        result["entry_count"] = entry_count
    except Exception:
        return result
    return result


def parse_stsc_atom(f, size: int) -> Dict[str, Any]:
    result = {"entry_count": 0}
    try:
        data = f.read(size)
        if len(data) < 8:
            return result
        entry_count = struct.unpack(">I", data[4:8])[0]
        result["entry_count"] = entry_count
    except Exception:
        return result
    return result


def parse_stsz_atom(f, size: int) -> Dict[str, Any]:
    result = {"sample_size": None, "sample_count": 0}
    try:
        data = f.read(size)
        if len(data) < 12:
            return result
        sample_size = struct.unpack(">I", data[4:8])[0]
        sample_count = struct.unpack(">I", data[8:12])[0]
        result["sample_size"] = sample_size
        result["sample_count"] = sample_count
        if sample_size == 0 and len(data) >= 12 + (sample_count * 4):
            sizes = []
            offset = 12
            for _ in range(sample_count):
                sizes.append(struct.unpack(">I", data[offset:offset + 4])[0])
                offset += 4
            result["min_sample_size"] = min(sizes) if sizes else None
            result["max_sample_size"] = max(sizes) if sizes else None
    except Exception:
        return result
    return result


def parse_stco_atom(f, size: int, is_64: bool = False) -> Dict[str, Any]:
    result = {"entry_count": 0}
    try:
        data = f.read(size)
        if len(data) < 8:
            return result
        entry_count = struct.unpack(">I", data[4:8])[0]
        result["entry_count"] = entry_count
        if entry_count > 0:
            width = 8 if is_64 else 4
            if len(data) >= 8 + width:
                first = struct.unpack(">Q", data[8:16])[0] if is_64 else struct.unpack(">I", data[8:12])[0]
                result["first_offset"] = first
    except Exception:
        return result
    return result


def parse_stss_atom(f, size: int) -> Dict[str, Any]:
    result = {"entry_count": 0}
    try:
        data = f.read(size)
        if len(data) < 8:
            return result
        entry_count = struct.unpack(">I", data[4:8])[0]
        result["entry_count"] = entry_count
    except Exception:
        return result
    return result


def parse_elst_atom(f, size: int) -> Dict[str, Any]:
    result = {"entry_count": 0, "entries": []}
    try:
        data = f.read(size)
        if len(data) < 8:
            return result
        version = data[0]
        entry_count = struct.unpack(">I", data[4:8])[0]
        result["entry_count"] = entry_count
        offset = 8
        for _ in range(entry_count):
            if version == 1 and offset + 20 <= len(data):
                duration = struct.unpack(">Q", data[offset:offset + 8])[0]
                media_time = struct.unpack(">q", data[offset + 8:offset + 16])[0]
                media_rate = struct.unpack(">H", data[offset + 16:offset + 18])[0]
                offset += 20
            elif version == 0 and offset + 12 <= len(data):
                duration = struct.unpack(">I", data[offset:offset + 4])[0]
                media_time = struct.unpack(">i", data[offset + 4:offset + 8])[0]
                media_rate = struct.unpack(">H", data[offset + 8:offset + 10])[0]
                offset += 12
            else:
                break
            result["entries"].append({
                "duration": duration,
                "media_time": media_time,
                "media_rate": media_rate,
            })
    except Exception:
        return result
    return result


def extract_mp4_metadata_atoms(filepath: str) -> Dict[str, Any]:
    """Extract metadata from udta/meta atoms."""
    result: Dict[str, Any] = {
        "has_metadata_atom": False,
        "metadata_format": None,
        "ilst": {},
    }
    ilst = _parse_mp4_ilst(filepath)
    if ilst.get("tag_count"):
        result["has_metadata_atom"] = True
        result["metadata_format"] = "ilst"
        result["ilst"] = ilst
    return result


def extract_mp4_timing(filepath: str) -> Dict[str, Any]:
    """Extract detailed timing information."""
    result = {
        "has_composition_time_offsets": False,
        "has_sync_samples": False,
        "stts_entries": 0,
        "ctts_entries": 0,
        "sync_sample_count": 0,
    }
    try:
        file_size = Path(filepath).stat().st_size
        with open(filepath, "rb") as f:
            for atom_type, start, size, _ in _iter_mp4_atoms(f, 0, file_size, 6):
                if atom_type == b"stts":
                    f.seek(start, 0)
                    stts = parse_stts_atom(f, size)
                    result["stts_entries"] += stts.get("entry_count", 0)
                elif atom_type == b"ctts":
                    f.seek(start, 0)
                    ctts = parse_ctts_atom(f, size)
                    result["ctts_entries"] += ctts.get("entry_count", 0)
                elif atom_type == b"stss":
                    f.seek(start, 0)
                    stss = parse_stss_atom(f, size)
                    result["sync_sample_count"] += stss.get("entry_count", 0)
        result["has_composition_time_offsets"] = result["ctts_entries"] > 0
        result["has_sync_samples"] = result["sync_sample_count"] > 0
    except Exception:
        return result
    return result


def parse_mkv_ebml(filepath: str) -> Dict[str, Any]:
    """
    Parse MKV/WebM EBML structure.
    
    Returns ~120 fields including:
    - EBML header: version, doctype
    - Segment info: UID, duration, muxing app
    - Track entries: codec, language, settings
    - Tags: metadata
    """
    result = {
        "ebml_header": {},
        "segment_info": {},
        "tracks": [],
        "tags": [],
        "chapters": [],
        "cues_present": False,
        "total_elements": 0
    }
    
    try:
        with open(filepath, 'rb') as f:
            ebml_id, _ = _read_ebml_id(f)
            if ebml_id != 0x1A45DFA3:
                return result
            header_size, _ = _read_ebml_size(f)
            if header_size <= 0:
                return result
            header_data = f.read(header_size)
            result["ebml_header"] = parse_ebml_header(header_data)

            segment_id, _ = _read_ebml_id(f)
            if segment_id != 0x18538067:
                return result
            segment_size, _ = _read_ebml_size(f)
            segment_start = f.tell()
            if segment_size == -1:
                f.seek(0, 2)
                segment_end = f.tell()
                f.seek(segment_start, 0)
            else:
                segment_end = segment_start + segment_size

            parsed = _parse_mkv_segment(f, segment_end)
            result.update(parsed)
    except Exception:
        pass
    
    return result


def parse_ebml_size(data: bytes) -> int:
    """Parse EBML variable-length size."""
    if not data:
        return 0
    
    first_byte = data[0]
    
    # Find length of size field
    length = 0
    mask = 0x80
    for i in range(8):
        if first_byte & mask:
            length = i + 1
            break
        mask >>= 1
    
    if length == 0:
        return 0
    
    # Extract size value
    size = first_byte & (mask - 1)
    for i in range(1, length):
        if i < len(data):
            size = (size << 8) | data[i]
    
    return size


def parse_ebml_header(data: bytes) -> Dict[str, Any]:
    """Parse EBML header."""
    result = {}
    for element_id, element_data in _iter_ebml_elements(data):
        if element_id == 0x4286:
            result["ebml_version"] = _ebml_uint(element_data)
        elif element_id == 0x42F7:
            result["ebml_read_version"] = _ebml_uint(element_data)
        elif element_id == 0x42F2:
            result["ebml_max_id_length"] = _ebml_uint(element_data)
        elif element_id == 0x42F3:
            result["ebml_max_size_length"] = _ebml_uint(element_data)
        elif element_id == 0x4282:
            result["doc_type"] = element_data.decode("utf-8", errors="ignore")
        elif element_id == 0x4287:
            result["doc_type_version"] = _ebml_uint(element_data)
        elif element_id == 0x4285:
            result["doc_type_read_version"] = _ebml_uint(element_data)
    return result


def _ebml_uint(data: bytes) -> int:
    if not data:
        return 0
    return int.from_bytes(data, "big", signed=False)


def _ebml_sint(data: bytes) -> int:
    if not data:
        return 0
    return int.from_bytes(data, "big", signed=True)


def _ebml_float(data: bytes) -> Optional[float]:
    if len(data) == 4:
        return struct.unpack(">f", data)[0]
    if len(data) == 8:
        return struct.unpack(">d", data)[0]
    return None


def _parse_mkv_segment(f, end: int) -> Dict[str, Any]:
    result = {
        "segment_info": {},
        "tracks": [],
        "tags": [],
        "chapters": [],
        "cues_present": False,
        "total_elements": 0,
    }
    while f.tell() < end:
        element_id, _ = _read_ebml_id(f)
        if element_id == 0:
            break
        size, _ = _read_ebml_size(f)
        if size == -1:
            size = end - f.tell()
        data_start = f.tell()
        if element_id == 0x1549A966:  # Info
            data = f.read(size)
            result["segment_info"] = _parse_mkv_info(data)
        elif element_id == 0x1654AE6B:  # Tracks
            data = f.read(size)
            result["tracks"] = _parse_mkv_tracks(data)
        elif element_id == 0x1254C367:  # Tags
            data = f.read(size)
            result["tags"] = _parse_mkv_tags(data)
        elif element_id == 0x1043A770:  # Chapters
            data = f.read(size)
            result["chapters"] = _parse_mkv_chapters(data)
        elif element_id == 0x1C53BB6B:  # Cues
            result["cues_present"] = True
            f.seek(size, 1)
        else:
            f.seek(size, 1)
        result["total_elements"] += 1
        f.seek(data_start + size, 0)
    return result


def _parse_mkv_info(data: bytes) -> Dict[str, Any]:
    info: Dict[str, Any] = {}
    for element_id, element_data in _iter_ebml_elements(data):
        if element_id == 0x73A4:
            info["segment_uid"] = element_data.hex()
        elif element_id == 0x7384:
            info["segment_filename"] = element_data.decode("utf-8", errors="ignore")
        elif element_id == 0x2AD7B1:
            info["timecode_scale"] = _ebml_uint(element_data)
        elif element_id == 0x4489:
            info["duration"] = _ebml_float(element_data)
        elif element_id == 0x4461:
            info["date_utc"] = _ebml_sint(element_data)
        elif element_id == 0x7BA9:
            info["title"] = element_data.decode("utf-8", errors="ignore")
        elif element_id == 0x4D80:
            info["muxing_app"] = element_data.decode("utf-8", errors="ignore")
        elif element_id == 0x5741:
            info["writing_app"] = element_data.decode("utf-8", errors="ignore")
    return info


def _parse_mkv_tracks(data: bytes) -> List[Dict[str, Any]]:
    tracks: List[Dict[str, Any]] = []
    for element_id, element_data in _iter_ebml_elements(data):
        if element_id != 0xAE:
            continue
        track: Dict[str, Any] = {}
        for sub_id, sub_data in _iter_ebml_elements(element_data):
            if sub_id == 0xD7:
                track["track_number"] = _ebml_uint(sub_data)
            elif sub_id == 0x73C5:
                track["track_uid"] = _ebml_uint(sub_data)
            elif sub_id == 0x83:
                track_type_code = _ebml_uint(sub_data)
                track["track_type_code"] = track_type_code
                track["track_type"] = MKV_TRACK_TYPES.get(track_type_code, "unknown")
            elif sub_id == 0xB9:
                track["flag_enabled"] = bool(_ebml_uint(sub_data))
            elif sub_id == 0x88:
                track["flag_default"] = bool(_ebml_uint(sub_data))
            elif sub_id == 0x55AA:
                track["flag_forced"] = bool(_ebml_uint(sub_data))
            elif sub_id == 0x9C:
                track["flag_lacing"] = bool(_ebml_uint(sub_data))
            elif sub_id == 0x536E:
                track["name"] = sub_data.decode("utf-8", errors="ignore")
            elif sub_id == 0x22B59C:
                track["language"] = sub_data.decode("utf-8", errors="ignore")
            elif sub_id == 0x86:
                track["codec_id"] = sub_data.decode("utf-8", errors="ignore")
            elif sub_id == 0x258688:
                track["codec_name"] = sub_data.decode("utf-8", errors="ignore")
            elif sub_id == 0x63A2:
                track["codec_private_size"] = len(sub_data)
            elif sub_id == 0xE0:
                track["video"] = _parse_mkv_video(sub_data)
            elif sub_id == 0xE1:
                track["audio"] = _parse_mkv_audio(sub_data)
        tracks.append(track)
    return tracks


def _parse_mkv_video(data: bytes) -> Dict[str, Any]:
    video: Dict[str, Any] = {}
    for element_id, element_data in _iter_ebml_elements(data):
        if element_id == 0xB0:
            video["pixel_width"] = _ebml_uint(element_data)
        elif element_id == 0xBA:
            video["pixel_height"] = _ebml_uint(element_data)
        elif element_id == 0x54B0:
            video["display_width"] = _ebml_uint(element_data)
        elif element_id == 0x54BA:
            video["display_height"] = _ebml_uint(element_data)
        elif element_id == 0x54B2:
            video["display_unit"] = _ebml_uint(element_data)
        elif element_id == 0x53B8:
            video["stereo_mode"] = _ebml_uint(element_data)
    return video


def _parse_mkv_audio(data: bytes) -> Dict[str, Any]:
    audio: Dict[str, Any] = {}
    for element_id, element_data in _iter_ebml_elements(data):
        if element_id == 0xB5:
            audio["sampling_frequency"] = _ebml_float(element_data)
        elif element_id == 0x78B5:
            audio["output_sampling_frequency"] = _ebml_float(element_data)
        elif element_id == 0x9F:
            audio["channels"] = _ebml_uint(element_data)
        elif element_id == 0x6264:
            audio["bit_depth"] = _ebml_uint(element_data)
    return audio


def _parse_mkv_tags(data: bytes) -> List[Dict[str, Any]]:
    tags: List[Dict[str, Any]] = []
    for element_id, element_data in _iter_ebml_elements(data):
        if element_id != 0x7373:
            continue
        tag_entry: Dict[str, Any] = {}
        for tag_id, tag_data in _iter_ebml_elements(element_data):
            if tag_id == 0x67C8:
                simple = {}
                for simple_id, simple_data in _iter_ebml_elements(tag_data):
                    if simple_id == 0x45A3:
                        simple["name"] = simple_data.decode("utf-8", errors="ignore")
                    elif simple_id == 0x4487:
                        simple["value"] = simple_data.decode("utf-8", errors="ignore")
                    elif simple_id == 0x4485:
                        simple["binary"] = simple_data.hex()
                if simple:
                    tag_entry.setdefault("simple_tags", []).append(simple)
        if tag_entry:
            tags.append(tag_entry)
    return tags


def _parse_mkv_chapters(data: bytes) -> List[Dict[str, Any]]:
    chapters: List[Dict[str, Any]] = []
    for element_id, element_data in _iter_ebml_elements(data):
        if element_id != 0x45B9:
            continue
        for chapter_id, chapter_data in _iter_ebml_elements(element_data):
            if chapter_id != 0xB6:
                continue
            chapter: Dict[str, Any] = {}
            for sub_id, sub_data in _iter_ebml_elements(chapter_data):
                if sub_id == 0x91:
                    chapter["time_start"] = _ebml_uint(sub_data)
                elif sub_id == 0x92:
                    chapter["time_end"] = _ebml_uint(sub_data)
                elif sub_id == 0x80:
                    for disp_id, disp_data in _iter_ebml_elements(sub_data):
                        if disp_id == 0x85:
                            chapter["display"] = disp_data.decode("utf-8", errors="ignore")
                        elif disp_id == 0x437C:
                            chapter["language"] = disp_data.decode("utf-8", errors="ignore")
            if chapter:
                chapters.append(chapter)
    return chapters


def parse_avi_chunks(filepath: str) -> Dict[str, Any]:
    """
    Parse AVI RIFF chunks.
    
    Returns ~80 fields including:
    - avih: frame rate, stream count, flags
    - strh: stream type, codec, frame rate
    - strf: format-specific details
    """
    result = {
        "riff_header": {},
        "avih": {},
        "streams": [],
        "idx1_present": False,
        "total_chunks": 0
    }
    
    try:
        with open(filepath, 'rb') as f:
            riff = f.read(4)
            if riff != b'RIFF':
                return result
            file_size = struct.unpack('<I', f.read(4))[0]
            avi_sig = f.read(4)
            if avi_sig != b'AVI ':
                return result
            result["riff_header"] = {
                "signature": "RIFF",
                "file_size": file_size,
                "format": "AVI",
            }
            file_end = Path(filepath).stat().st_size
            current_stream: Optional[Dict[str, Any]] = None
            while f.tell() + 8 <= file_end:
                chunk_id = f.read(4)
                if len(chunk_id) < 4:
                    break
                chunk_size = struct.unpack('<I', f.read(4))[0]
                chunk_start = f.tell()
                result["total_chunks"] += 1

                if chunk_id == b'LIST':
                    list_type = f.read(4)
                    list_size = chunk_size - 4
                    list_end = f.tell() + list_size
                    if list_type == b'hdrl':
                        _parse_avi_list(f, list_end, result)
                    elif list_type == b'strl':
                        stream = {}
                        result["streams"].append(stream)
                        current_stream = stream
                        _parse_avi_stream_list(f, list_end, current_stream)
                    elif list_type == b'INFO':
                        info_data = f.read(list_size)
                        result["riff_info"] = _parse_avi_info(info_data)
                    else:
                        f.seek(list_size, 1)
                elif chunk_id == b'avih':
                    avih_data = f.read(chunk_size)
                    result["avih"] = _parse_avi_avih(avih_data)
                elif chunk_id == b'idx1':
                    result["idx1_present"] = True
                    f.seek(chunk_size, 1)
                else:
                    f.seek(chunk_size, 1)

                if chunk_size % 2 == 1:
                    f.seek(1, 1)
                f.seek(chunk_start + chunk_size + (chunk_size % 2), 0)
    except Exception:
        pass
    
    return result


def _parse_avi_list(f, end: int, result: Dict[str, Any]) -> None:
    while f.tell() + 8 <= end:
        chunk_id = f.read(4)
        if len(chunk_id) < 4:
            break
        chunk_size = struct.unpack('<I', f.read(4))[0]
        chunk_start = f.tell()
        if chunk_id == b'avih':
            data = f.read(chunk_size)
            result["avih"] = _parse_avi_avih(data)
        elif chunk_id == b'LIST':
            list_type = f.read(4)
            list_size = chunk_size - 4
            list_end = f.tell() + list_size
            if list_type == b'strl':
                stream = {}
                result["streams"].append(stream)
                _parse_avi_stream_list(f, list_end, stream)
            elif list_type == b'INFO':
                info_data = f.read(list_size)
                result["riff_info"] = _parse_avi_info(info_data)
            else:
                f.seek(list_size, 1)
        else:
            f.seek(chunk_size, 1)
        if chunk_size % 2 == 1:
            f.seek(1, 1)
        f.seek(chunk_start + chunk_size + (chunk_size % 2), 0)


def _parse_avi_stream_list(f, end: int, stream: Dict[str, Any]) -> None:
    while f.tell() + 8 <= end:
        chunk_id = f.read(4)
        if len(chunk_id) < 4:
            break
        chunk_size = struct.unpack('<I', f.read(4))[0]
        chunk_start = f.tell()
        if chunk_id == b'strh':
            data = f.read(chunk_size)
            stream.update(_parse_avi_strh(data))
        elif chunk_id == b'strf':
            data = f.read(chunk_size)
            if stream.get("stream_type") == "video":
                stream["format"] = _parse_avi_strf_video(data)
            elif stream.get("stream_type") == "audio":
                stream["format"] = _parse_avi_strf_audio(data)
            else:
                stream["format"] = {"data_size": len(data)}
        else:
            f.seek(chunk_size, 1)
        if chunk_size % 2 == 1:
            f.seek(1, 1)
        f.seek(chunk_start + chunk_size + (chunk_size % 2), 0)


def _parse_avi_avih(data: bytes) -> Dict[str, Any]:
    if len(data) < 56:
        return {}
    return {
        "microsec_per_frame": struct.unpack('<I', data[0:4])[0],
        "max_bytes_per_sec": struct.unpack('<I', data[4:8])[0],
        "padding_granularity": struct.unpack('<I', data[8:12])[0],
        "flags": struct.unpack('<I', data[12:16])[0],
        "total_frames": struct.unpack('<I', data[16:20])[0],
        "initial_frames": struct.unpack('<I', data[20:24])[0],
        "stream_count": struct.unpack('<I', data[24:28])[0],
        "suggested_buffer_size": struct.unpack('<I', data[28:32])[0],
        "width": struct.unpack('<I', data[32:36])[0],
        "height": struct.unpack('<I', data[36:40])[0],
    }


def _parse_avi_strh(data: bytes) -> Dict[str, Any]:
    if len(data) < 56:
        return {}
    fcc_type = data[0:4]
    fcc_handler = data[4:8]
    stream_type = {
        b'vids': 'video',
        b'auds': 'audio',
        b'txts': 'text',
        b'subt': 'subtitle',
    }.get(fcc_type, fcc_type.decode("latin1", errors="ignore"))
    return {
        "stream_type": stream_type,
        "handler": fcc_handler.decode("latin1", errors="ignore"),
        "flags": struct.unpack('<I', data[8:12])[0],
        "priority": struct.unpack('<H', data[12:14])[0],
        "language": struct.unpack('<H', data[14:16])[0],
        "initial_frames": struct.unpack('<I', data[16:20])[0],
        "scale": struct.unpack('<I', data[20:24])[0],
        "rate": struct.unpack('<I', data[24:28])[0],
        "start": struct.unpack('<I', data[28:32])[0],
        "length": struct.unpack('<I', data[32:36])[0],
        "suggested_buffer_size": struct.unpack('<I', data[36:40])[0],
        "quality": struct.unpack('<I', data[40:44])[0],
        "sample_size": struct.unpack('<I', data[44:48])[0],
    }


def _parse_avi_strf_video(data: bytes) -> Dict[str, Any]:
    if len(data) < 40:
        return {}
    return {
        "header_size": struct.unpack('<I', data[0:4])[0],
        "width": struct.unpack('<I', data[4:8])[0],
        "height": struct.unpack('<I', data[8:12])[0],
        "planes": struct.unpack('<H', data[12:14])[0],
        "bit_count": struct.unpack('<H', data[14:16])[0],
        "compression": data[16:20].decode("latin1", errors="ignore"),
        "image_size": struct.unpack('<I', data[20:24])[0],
        "x_pels_per_meter": struct.unpack('<I', data[24:28])[0],
        "y_pels_per_meter": struct.unpack('<I', data[28:32])[0],
        "colors_used": struct.unpack('<I', data[32:36])[0],
        "colors_important": struct.unpack('<I', data[36:40])[0],
    }


def _parse_avi_strf_audio(data: bytes) -> Dict[str, Any]:
    if len(data) < 16:
        return {}
    result = {
        "format_tag": struct.unpack('<H', data[0:2])[0],
        "channels": struct.unpack('<H', data[2:4])[0],
        "samples_per_sec": struct.unpack('<I', data[4:8])[0],
        "avg_bytes_per_sec": struct.unpack('<I', data[8:12])[0],
        "block_align": struct.unpack('<H', data[12:14])[0],
        "bits_per_sample": struct.unpack('<H', data[14:16])[0],
    }
    if len(data) >= 18:
        result["cb_size"] = struct.unpack('<H', data[16:18])[0]
    return result


def _parse_avi_info(data: bytes) -> Dict[str, Any]:
    info: Dict[str, Any] = {}
    offset = 0
    while offset + 8 <= len(data):
        tag = data[offset:offset + 4]
        size = struct.unpack('<I', data[offset + 4:offset + 8])[0]
        offset += 8
        value = data[offset:offset + size].decode("latin1", errors="ignore").rstrip("\x00").strip()
        offset += size
        if size % 2 == 1:
            offset += 1
        key = AVI_INFO_TAGS.get(tag, tag.decode("latin1", errors="ignore"))
        info[key] = value
    return info


def get_container_metadata_field_count() -> int:
    """Return estimated field count for container metadata module."""
    return 620  # Expanded Phase 2 target
