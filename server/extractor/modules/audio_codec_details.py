"""
Phase 2: Audio Codec Deep Analysis
MP3 LAME tags, AAC profiles, FLAC metadata blocks, Opus headers, Vorbis comments
Target: +200-300 fields
"""

from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import struct
import subprocess
import json
import hashlib
import xml.etree.ElementTree as ET


# AAC Profiles
AAC_PROFILES = {
    1: "AAC Main",
    2: "AAC LC (Low Complexity)",
    3: "AAC SSR (Scalable Sample Rate)",
    4: "AAC LTP (Long Term Prediction)",
    5: "SBR (Spectral Band Replication) / HE-AAC",
    29: "HE-AAC v2 (PS)"
}

# MP3 Channel Modes
MP3_CHANNEL_MODES = {
    0: "Stereo",
    1: "Joint Stereo",
    2: "Dual Channel",
    3: "Mono"
}

# MP3 Emphasis
MP3_EMPHASIS = {
    0: "None",
    1: "50/15 ms",
    2: "Reserved",
    3: "CCIT J.17"
}

# FLAC Block Types
FLAC_BLOCK_TYPES = {
    0: "STREAMINFO",
    1: "PADDING",
    2: "APPLICATION",
    3: "SEEKTABLE",
    4: "VORBIS_COMMENT",
    5: "CUESHEET",
    6: "PICTURE"
}

# ADTS sample rates (index -> Hz)
ADTS_SAMPLE_RATES = [
    96000, 88200, 64000, 48000,
    44100, 32000, 24000, 22050,
    16000, 12000, 11025, 8000,
    7350, None, None, None
]

# ID3v1 genre list (standard 80 entries)
ID3_GENRES = [
    "Blues", "Classic Rock", "Country", "Dance", "Disco", "Funk", "Grunge",
    "Hip-Hop", "Jazz", "Metal", "New Age", "Oldies", "Other", "Pop", "R&B",
    "Rap", "Reggae", "Rock", "Techno", "Industrial", "Alternative",
    "Ska", "Death Metal", "Pranks", "Soundtrack", "Euro-Techno", "Ambient",
    "Trip-Hop", "Vocal", "Jazz+Funk", "Fusion", "Trance", "Classical",
    "Instrumental", "Acid", "House", "Game", "Sound Clip", "Gospel", "Noise",
    "AlternRock", "Bass", "Soul", "Punk", "Space", "Meditative",
    "Instrumental Pop", "Instrumental Rock", "Ethnic", "Gothic", "Darkwave",
    "Techno-Industrial", "Electronic", "Pop-Folk", "Eurodance", "Dream",
    "Southern Rock", "Comedy", "Cult", "Gangsta", "Top 40", "Christian Rap",
    "Pop/Funk", "Jungle", "Native American", "Cabaret", "New Wave",
    "Psychadelic", "Rave", "Showtunes", "Trailer", "Lo-Fi", "Tribal",
    "Acid Punk", "Acid Jazz", "Polka", "Retro", "Musical", "Rock & Roll",
    "Hard Rock"
]

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
    b"\xa9grp": "grouping",
    b"\xa9enc": "encoded_by",
    b"\xa9lyr": "lyrics",
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
    b"stik": "media_type",
    b"hdvd": "hd_video",
    b"pcst": "podcast",
    b"tvsn": "tv_season",
    b"tves": "tv_episode",
    b"tvsh": "tv_show",
    b"tvnn": "tv_network",
    b"purd": "purchase_date",
    b"soar": "sort_artist",
    b"soal": "sort_album",
    b"sonm": "sort_title",
    b"----": "freeform",
}

MP4_CONTAINER_ATOMS = {
    b"moov", b"trak", b"mdia", b"minf", b"stbl", b"udta", b"meta", b"ilst", b"chpl", b"chap"
}

RIFF_INFO_TAGS = {
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

ASF_HEADER_GUID = bytes.fromhex("3026B2758E66CF11A6D900AA0062CE6C")
ASF_FILE_PROPERTIES_GUID = bytes.fromhex("A1DCAB8C47A9CF118EE400C00C205365")


def _read_file_header(filepath: str, size: int = 64) -> bytes:
    try:
        with open(filepath, "rb") as f:
            return f.read(size)
    except Exception as e:
        return b""


def _read_file_tail(filepath: str, size: int = 256) -> bytes:
    try:
        with open(filepath, "rb") as f:
            f.seek(0, 2)
            file_size = f.tell()
            f.seek(max(0, file_size - size), 0)
            return f.read(size)
    except Exception as e:
        return b""


def _count_fields(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, dict):
        return sum(_count_fields(v) for v in value.values())
    if isinstance(value, list):
        return sum(_count_fields(v) for v in value)
    return 1


def _syncsafe_to_int(data: bytes) -> int:
    if len(data) < 4:
        return 0
    return ((data[0] & 0x7F) << 21) | ((data[1] & 0x7F) << 14) | ((data[2] & 0x7F) << 7) | (data[3] & 0x7F)


def _decode_id3_text(data: bytes, encoding: int) -> str:
    if not data:
        return ""
    try:
        if encoding == 0:
            return data.decode("latin1", errors="ignore").rstrip("\x00")
        if encoding == 1:
            return data.decode("utf-16", errors="ignore").rstrip("\x00")
        if encoding == 2:
            return data.decode("utf-16-be", errors="ignore").rstrip("\x00")
        if encoding == 3:
            return data.decode("utf-8", errors="ignore").rstrip("\x00")
    except Exception as e:
        return ""
    return data.decode("latin1", errors="ignore").rstrip("\x00")


def _split_id3_strings(text: str) -> List[str]:
    return [part for part in text.split("\x00") if part]

def _split_terminated_bytes(data: bytes, encoding: int) -> Tuple[bytes, bytes]:
    if encoding in (1, 2):
        terminator = b"\x00\x00"
    else:
        terminator = b"\x00"
    idx = data.find(terminator)
    if idx < 0:
        return data, b""
    return data[:idx], data[idx + len(terminator):]

def _parse_signed_bits(value_bytes: bytes, bits: int) -> Optional[int]:
    if bits <= 0 or not value_bytes:
        return None
    total = int.from_bytes(value_bytes, "big")
    sign_bit = 1 << (bits - 1)
    if total & sign_bit:
        total -= 1 << bits
    return total


def _parse_id3v2_tag(data: bytes) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "id3v2_present": False,
        "version": None,
        "flags": {},
        "tag_size": 0,
        "extended_header_size": 0,
        "frame_count": 0,
        "frame_ids": [],
        "text_frames": {},
        "url_frames": {},
        "comments": [],
        "lyrics": [],
        "sync_lyrics": [],
        "pictures": [],
        "user_text": [],
        "chapters": [],
        "table_of_contents": [],
        "event_timing": [],
        "relative_volume": [],
        "reverb": {},
        "buffer": {},
        "ownership": {},
        "links": [],
        "podcast": {},
        "involved_people": [],
        "musician_credits": [],
        "commercial": {},
        "group_registration": [],
        "signature": {},
        "seek_offset": None,
        "equalization": [],
        "mpeg_lookup_table": {},
        "audio_seek_points": {},
        "other_frames": {},
    }

    if len(data) < 10 or data[0:3] != b"ID3":
        return result

    result["id3v2_present"] = True
    version_major = data[3]
    version_minor = data[4]
    flags = data[5]
    tag_size = _syncsafe_to_int(data[6:10])
    result["version"] = f"2.{version_major}.{version_minor}"
    result["flags"] = {
        "unsynchronisation": bool(flags & 0x80),
        "extended_header": bool(flags & 0x40),
        "experimental": bool(flags & 0x20),
        "footer_present": bool(flags & 0x10),
    }
    result["tag_size"] = tag_size

    frames_data = data[10:10 + tag_size]
    if result["flags"]["unsynchronisation"]:
        frames_data = frames_data.replace(b"\xFF\x00", b"\xFF")

    offset = 0
    if result["flags"]["extended_header"] and len(frames_data) >= 4:
        if version_major == 3:
            ext_size = struct.unpack(">I", frames_data[0:4])[0]
        else:
            ext_size = _syncsafe_to_int(frames_data[0:4])
        result["extended_header_size"] = ext_size
        offset = 4 + ext_size if ext_size > 0 else 0

    frame_id_len = 4
    frame_size_len = 4
    if version_major == 2:
        frame_id_len = 3
        frame_size_len = 3
        id3v22_map = {
            "TT2": "TIT2",
            "TP1": "TPE1",
            "TP2": "TPE2",
            "TP3": "TPE3",
            "TAL": "TALB",
            "TRK": "TRCK",
            "TPA": "TPOS",
            "TCO": "TCON",
            "TYE": "TYER",
            "TLE": "TLEN",
            "TCR": "TCOP",
            "TMT": "TMED",
            "TSS": "TSSE",
            "TEN": "TENC",
            "TOA": "TOPE",
            "TOL": "TOLY",
            "TOT": "TOAL",
            "TOR": "TDOR",
            "TXX": "TXXX",
            "WAF": "WOAF",
            "WAR": "WOAR",
            "WCM": "WCOM",
            "WCP": "WCOP",
            "WPB": "WPUB",
            "WXX": "WXXX",
            "COM": "COMM",
            "ULT": "USLT",
            "PIC": "APIC",
            "POP": "POPM",
            "CNT": "PCNT",
            "UFI": "UFID",
            "GEO": "GEOB",
        }

    while offset + frame_id_len + frame_size_len <= len(frames_data):
        frame_id = frames_data[offset:offset + frame_id_len]
        if frame_id.strip(b"\x00") == b"":
            break
        offset += frame_id_len

        if version_major == 2:
            frame_size = (frames_data[offset] << 16) | (frames_data[offset + 1] << 8) | frames_data[offset + 2]
            offset += 3
            frame_flags = b""
        else:
            raw_size = frames_data[offset:offset + 4]
            frame_size = _syncsafe_to_int(raw_size) if version_major == 4 else struct.unpack(">I", raw_size)[0]
            offset += 4
            frame_flags = frames_data[offset:offset + 2]
            offset += 2

        if frame_size <= 0 or offset + frame_size > len(frames_data):
            break

        frame_data = frames_data[offset:offset + frame_size]
        offset += frame_size

        frame_id_str = frame_id.decode("latin1", errors="ignore")
        original_frame_id = frame_id_str
        if version_major == 2:
            frame_id_str = id3v22_map.get(frame_id_str, frame_id_str)
        result["frame_ids"].append(frame_id_str)
        result["frame_count"] += 1

        if frame_id_str.startswith("T") and frame_id_str != "TXXX":
            encoding = frame_data[0] if frame_data else 0
            text = _decode_id3_text(frame_data[1:], encoding)
            parts = _split_id3_strings(text)
            result["text_frames"][frame_id_str] = parts if len(parts) > 1 else text
        elif frame_id_str == "TXXX":
            encoding = frame_data[0] if frame_data else 0
            text = _decode_id3_text(frame_data[1:], encoding)
            parts = _split_id3_strings(text)
            if parts:
                result["user_text"].append({"description": parts[0], "value": parts[1:]})
        elif frame_id_str.startswith("W") and frame_id_str != "WXXX":
            url = frame_data.decode("latin1", errors="ignore").rstrip("\x00")
            result["url_frames"][frame_id_str] = url
        elif frame_id_str == "WXXX":
            encoding = frame_data[0] if frame_data else 0
            desc_bytes, url_bytes = _split_terminated_bytes(frame_data[1:], encoding)
            description = _decode_id3_text(desc_bytes, encoding)
            url = url_bytes.decode("latin1", errors="ignore").rstrip("\x00")
            if description:
                result["url_frames"][description] = url
            else:
                result["url_frames"]["_unnamed"] = url
        elif frame_id_str == "COMM":
            if len(frame_data) >= 4:
                encoding = frame_data[0]
                language = frame_data[1:4].decode("latin1", errors="ignore")
                desc_bytes, text_bytes = _split_terminated_bytes(frame_data[4:], encoding)
                description = _decode_id3_text(desc_bytes, encoding)
                comment_text = _decode_id3_text(text_bytes, encoding)
                result["comments"].append({
                    "language": language,
                    "description": description,
                    "text": comment_text,
                })
        elif frame_id_str == "USLT":
            if len(frame_data) >= 4:
                encoding = frame_data[0]
                language = frame_data[1:4].decode("latin1", errors="ignore")
                desc_bytes, text_bytes = _split_terminated_bytes(frame_data[4:], encoding)
                description = _decode_id3_text(desc_bytes, encoding)
                lyric_text = _decode_id3_text(text_bytes, encoding)
                result["lyrics"].append({
                    "language": language,
                    "description": description,
                    "text": lyric_text,
                })
        elif frame_id_str == "SYLT":
            if len(frame_data) >= 6:
                encoding = frame_data[0]
                language = frame_data[1:4].decode("latin1", errors="ignore")
                timestamp_format = frame_data[4]
                content_type = frame_data[5]
                desc_bytes, rest = _split_terminated_bytes(frame_data[6:], encoding)
                description = _decode_id3_text(desc_bytes, encoding)
                entries = []
                max_entries = 50
                while rest and len(entries) < max_entries:
                    text_bytes, rest = _split_terminated_bytes(rest, encoding)
                    if len(rest) < 4:
                        break
                    timestamp = struct.unpack(">I", rest[0:4])[0]
                    rest = rest[4:]
                    text_value = _decode_id3_text(text_bytes, encoding)
                    entries.append({"text": text_value, "timestamp": timestamp})
                result["sync_lyrics"].append({
                    "language": language,
                    "timestamp_format": timestamp_format,
                    "content_type": content_type,
                    "description": description,
                    "entry_count": len(entries),
                    "entries": entries,
                })
        elif frame_id_str == "APIC":
            if len(frame_data) >= 4:
                encoding = frame_data[0]
                rest = frame_data[1:]
                if original_frame_id == "PIC" and len(rest) >= 4:
                    mime = rest[:3].decode("latin1", errors="ignore")
                    after_mime = rest[3:]
                else:
                    mime_end = rest.find(b"\x00")
                    mime = rest[:mime_end].decode("latin1", errors="ignore") if mime_end >= 0 else ""
                    after_mime = rest[mime_end + 1:] if mime_end >= 0 else b""
                picture_type = after_mime[0] if after_mime else 0
                desc_bytes, pic_bytes = _split_terminated_bytes(after_mime[1:], encoding)
                description = _decode_id3_text(desc_bytes, encoding)
                picture_data_len = len(pic_bytes)
                result["pictures"].append({
                    "mime": mime,
                    "type": picture_type,
                    "description": description,
                    "size_bytes": picture_data_len,
                })
        elif frame_id_str == "GEOB":
            if len(frame_data) >= 4:
                encoding = frame_data[0]
                rest = frame_data[1:]
                mime_bytes, rest = _split_terminated_bytes(rest, 0)
                mime = mime_bytes.decode("latin1", errors="ignore")
                filename_bytes, rest = _split_terminated_bytes(rest, encoding)
                description_bytes, rest = _split_terminated_bytes(rest, encoding)
                filename = _decode_id3_text(filename_bytes, encoding)
                description = _decode_id3_text(description_bytes, encoding)
                result["other_frames"].setdefault("GEOB", []).append({
                    "mime": mime,
                    "filename": filename,
                    "description": description,
                    "data_length": len(rest),
                })
        elif frame_id_str == "POPM":
            email_end = frame_data.find(b"\x00")
            email = frame_data[:email_end].decode("latin1", errors="ignore") if email_end >= 0 else ""
            rating = frame_data[email_end + 1] if email_end + 1 < len(frame_data) else None
            play_count = None
            if email_end + 2 < len(frame_data):
                play_count = int.from_bytes(frame_data[email_end + 2:], "big")
            result["other_frames"]["POPM"] = {
                "email": email,
                "rating": rating,
                "play_count": play_count,
            }
        elif frame_id_str == "PCNT":
            result["other_frames"]["PCNT"] = int.from_bytes(frame_data, "big")
        elif frame_id_str == "SEEK":
            if len(frame_data) >= 4:
                result["seek_offset"] = struct.unpack(">I", frame_data[0:4])[0]
        elif frame_id_str == "SIGN":
            if frame_data:
                result["signature"] = {
                    "group_symbol": frame_data[0],
                    "signature_length": max(0, len(frame_data) - 1),
                }
        elif frame_id_str == "ASPI":
            if len(frame_data) >= 8:
                data_start = struct.unpack(">I", frame_data[0:4])[0]
                data_length = struct.unpack(">I", frame_data[4:8])[0]
                if len(frame_data) >= 11:
                    point_count = struct.unpack(">H", frame_data[8:10])[0]
                    bits_per_point = frame_data[10]
                    bytes_per_point = (bits_per_point + 7) // 8 if bits_per_point else 0
                    index_data = frame_data[11:]
                    points = []
                    if bytes_per_point > 0:
                        for i in range(0, min(len(index_data), point_count * bytes_per_point), bytes_per_point):
                            points.append(int.from_bytes(index_data[i:i + bytes_per_point], "big"))
                    result["audio_seek_points"] = {
                        "data_start": data_start,
                        "data_length": data_length,
                        "point_count": point_count,
                        "bits_per_point": bits_per_point,
                        "bytes_per_point": bytes_per_point,
                        "index_bytes": len(index_data),
                        "points_preview": points[:20],
                    }
                else:
                    index_data = frame_data[8:]
                    result["audio_seek_points"] = {
                        "data_start": data_start,
                        "data_length": data_length,
                        "index_bytes": len(index_data),
                    }
        elif frame_id_str == "GRID":
            owner_bytes, rest = _split_terminated_bytes(frame_data, 0)
            if rest:
                result["group_registration"].append({
                    "owner_id": owner_bytes.decode("latin1", errors="ignore"),
                    "group_symbol": rest[0],
                    "data_length": max(0, len(rest) - 1),
                })
        elif frame_id_str == "COMR":
            if len(frame_data) >= 10:
                encoding = frame_data[0]
                rest = frame_data[1:]
                price_bytes, rest = _split_terminated_bytes(rest, 0)
                price = price_bytes.decode("latin1", errors="ignore")
                valid_until = rest[:8].decode("latin1", errors="ignore") if len(rest) >= 8 else ""
                rest = rest[8:] if len(rest) >= 8 else b""
                contact_bytes, rest = _split_terminated_bytes(rest, 0)
                contact_url = contact_bytes.decode("latin1", errors="ignore")
                received_as = rest[0] if rest else None
                rest = rest[1:] if rest else b""
                seller_bytes, rest = _split_terminated_bytes(rest, encoding)
                description_bytes, rest = _split_terminated_bytes(rest, encoding)
                seller = _decode_id3_text(seller_bytes, encoding)
                description = _decode_id3_text(description_bytes, encoding)
                logo_mime_bytes, rest = _split_terminated_bytes(rest, 0)
                logo_mime = logo_mime_bytes.decode("latin1", errors="ignore")
                result["commercial"] = {
                    "price": price,
                    "valid_until": valid_until,
                    "contact_url": contact_url,
                    "received_as": received_as,
                    "seller": seller,
                    "description": description,
                    "logo_mime": logo_mime,
                    "logo_size": len(rest),
                }
        elif frame_id_str == "EQU2":
            if len(frame_data) >= 2:
                interpolation = frame_data[0]
                identifier_bytes, rest = _split_terminated_bytes(frame_data[1:], 0)
                identifier = identifier_bytes.decode("latin1", errors="ignore")
                entries = []
                pos = 1 + len(identifier_bytes) + 1
                while pos + 4 <= len(frame_data):
                    frequency = struct.unpack(">H", frame_data[pos:pos + 2])[0]
                    adjustment = struct.unpack(">h", frame_data[pos + 2:pos + 4])[0]
                    entries.append({
                        "frequency": frequency,
                        "adjustment": adjustment,
                    })
                    pos += 4
                result["equalization"].append({
                    "interpolation_method": interpolation,
                    "identifier": identifier,
                    "band_count": len(entries),
                    "bands": entries[:50],
                })
        elif frame_id_str == "MLLT":
            if len(frame_data) >= 6:
                frames_between = struct.unpack(">H", frame_data[0:2])[0]
                bytes_between = int.from_bytes(frame_data[2:5], "big")
                ms_between = frame_data[5]
                lookup_bytes = frame_data[6:]
                result["mpeg_lookup_table"] = {
                    "frames_between_ref": frames_between,
                    "bytes_between_ref": bytes_between,
                    "ms_between_ref": ms_between,
                    "table_bytes": len(lookup_bytes),
                }
        elif frame_id_str == "UFID":
            owner_end = frame_data.find(b"\x00")
            owner = frame_data[:owner_end].decode("latin1", errors="ignore") if owner_end >= 0 else ""
            identifier = frame_data[owner_end + 1:] if owner_end >= 0 else b""
            result["other_frames"]["UFID"] = {
                "owner": owner,
                "identifier_length": len(identifier),
            }
        elif frame_id_str in ("TIPL", "TMCL"):
            encoding = frame_data[0] if frame_data else 0
            text = _decode_id3_text(frame_data[1:], encoding)
            parts = _split_id3_strings(text)
            pairs = []
            for idx in range(0, len(parts), 2):
                if idx + 1 < len(parts):
                    pairs.append({"role": parts[idx], "person": parts[idx + 1]})
            if frame_id_str == "TIPL":
                result["involved_people"] = pairs
            else:
                result["musician_credits"] = pairs
        elif frame_id_str == "PRIV":
            owner_end = frame_data.find(b"\x00")
            owner = frame_data[:owner_end].decode("latin1", errors="ignore") if owner_end >= 0 else ""
            data_len = len(frame_data) - owner_end - 1 if owner_end >= 0 else len(frame_data)
            result["other_frames"].setdefault("PRIV", []).append({
                "owner": owner,
                "data_length": data_len,
            })
        elif frame_id_str == "GEOB":
            result["other_frames"].setdefault("GEOB", []).append({
                "data_length": len(frame_data),
            })
        elif frame_id_str == "CHAP":
            if len(frame_data) >= 16:
                element_id_end = frame_data.find(b"\x00")
                element_id = frame_data[:element_id_end].decode("latin1", errors="ignore") if element_id_end >= 0 else ""
                pos = element_id_end + 1 if element_id_end >= 0 else 0
                if pos + 16 <= len(frame_data):
                    start_time = struct.unpack(">I", frame_data[pos:pos + 4])[0]
                    end_time = struct.unpack(">I", frame_data[pos + 4:pos + 8])[0]
                    start_offset = struct.unpack(">I", frame_data[pos + 8:pos + 12])[0]
                    end_offset = struct.unpack(">I", frame_data[pos + 12:pos + 16])[0]
                    result["chapters"].append({
                        "element_id": element_id,
                        "start_time_ms": start_time,
                        "end_time_ms": end_time,
                        "start_offset": start_offset,
                        "end_offset": end_offset,
                    })
        elif frame_id_str == "CTOC":
            if len(frame_data) >= 4:
                element_id_end = frame_data.find(b"\x00")
                element_id = frame_data[:element_id_end].decode("latin1", errors="ignore") if element_id_end >= 0 else ""
                pos = element_id_end + 1 if element_id_end >= 0 else 0
                flags_byte = frame_data[pos] if pos < len(frame_data) else 0
                entry_count = frame_data[pos + 1] if pos + 1 < len(frame_data) else 0
                entry_ids = []
                pos += 2
                for _ in range(entry_count):
                    entry_end = frame_data.find(b"\x00", pos)
                    if entry_end < 0:
                        break
                    entry_ids.append(frame_data[pos:entry_end].decode("latin1", errors="ignore"))
                    pos = entry_end + 1
                result["table_of_contents"].append({
                    "element_id": element_id,
                    "flags": flags_byte,
                    "entry_count": entry_count,
                    "entry_ids": entry_ids,
                })
        elif frame_id_str == "ETCO":
            if len(frame_data) >= 1:
                time_format = frame_data[0]
                events = []
                pos = 1
                while pos + 5 <= len(frame_data):
                    event_type = frame_data[pos]
                    timestamp = struct.unpack(">I", frame_data[pos + 1:pos + 5])[0]
                    events.append({"event_type": event_type, "timestamp": timestamp})
                    pos += 5
                result["event_timing"] = {
                    "time_format": time_format,
                    "event_count": len(events),
                    "events": events,
                }
        elif frame_id_str == "RBUF":
            if len(frame_data) >= 8:
                buffer_size = int.from_bytes(frame_data[0:3], "big")
                embedded_info = frame_data[3]
                offset_to_next = struct.unpack(">I", frame_data[4:8])[0]
                result["buffer"] = {
                    "buffer_size": buffer_size,
                    "embedded_info_flag": embedded_info,
                    "offset_to_next_tag": offset_to_next,
                }
        elif frame_id_str == "RVRB":
            if len(frame_data) >= 12:
                vals = struct.unpack(">6H", frame_data[0:12])
                result["reverb"] = {
                    "reverb_left": vals[0],
                    "reverb_right": vals[1],
                    "bounces_left": vals[2],
                    "bounces_right": vals[3],
                    "feedback_left": vals[4],
                    "feedback_right": vals[5],
                }
        elif frame_id_str == "RVA2":
            owner_bytes, rest = _split_terminated_bytes(frame_data, 0)
            owner = owner_bytes.decode("latin1", errors="ignore")
            channels = []
            pos = len(owner_bytes) + 1
            while pos + 2 <= len(frame_data):
                channel_type = frame_data[pos]
                volume_bits = frame_data[pos + 1]
                pos += 2
                byte_len = (volume_bits + 7) // 8
                if pos + (byte_len * 2) > len(frame_data):
                    break
                volume_adjust = _parse_signed_bits(frame_data[pos:pos + byte_len], volume_bits)
                pos += byte_len
                peak_volume = _parse_signed_bits(frame_data[pos:pos + byte_len], volume_bits)
                pos += byte_len
                channels.append({
                    "channel_type": channel_type,
                    "volume_bits": volume_bits,
                    "volume_adjustment": volume_adjust,
                    "peak_volume": peak_volume,
                })
            result["relative_volume"].append({
                "identification": owner,
                "channel_count": len(channels),
                "channels": channels,
            })
        elif frame_id_str == "LINK":
            if len(frame_data) >= 5:
                frame_identifier = frame_data[0:4].decode("latin1", errors="ignore")
                rest = frame_data[4:]
                url_end = rest.find(b"\x00")
                url = rest[:url_end].decode("latin1", errors="ignore") if url_end >= 0 else ""
                additional = rest[url_end + 1:] if url_end >= 0 else b""
                result["links"].append({
                    "frame_identifier": frame_identifier,
                    "url": url,
                    "additional_data_length": len(additional),
                })
        elif frame_id_str == "OWNE":
            if len(frame_data) >= 10:
                encoding = frame_data[0]
                price_bytes, rest = _split_terminated_bytes(frame_data[1:], 0)
                price = price_bytes.decode("latin1", errors="ignore")
                date = rest[:8].decode("latin1", errors="ignore") if len(rest) >= 8 else ""
                seller_bytes = rest[8:] if len(rest) > 8 else b""
                seller = _decode_id3_text(seller_bytes, encoding)
                result["ownership"] = {
                    "price_paid": price,
                    "purchase_date": date,
                    "seller": seller,
                }
        elif frame_id_str == "PCST":
            flag = frame_data[0] if frame_data else 0
            result["podcast"]["is_podcast"] = bool(flag)
        else:
            result["other_frames"][frame_id_str] = {
                "size": frame_size,
                "flags": frame_flags.hex() if frame_flags else None,
            }

    return result


def _parse_id3v1_tag(data: bytes) -> Dict[str, Any]:
    result = {"id3v1_present": False}
    if len(data) < 128 or data[0:3] != b"TAG":
        return result
    result["id3v1_present"] = True
    result["title"] = data[3:33].decode("latin1", errors="ignore").rstrip("\x00").strip()
    result["artist"] = data[33:63].decode("latin1", errors="ignore").rstrip("\x00").strip()
    result["album"] = data[63:93].decode("latin1", errors="ignore").rstrip("\x00").strip()
    result["year"] = data[93:97].decode("latin1", errors="ignore").rstrip("\x00").strip()
    comment = data[97:127]
    if comment[28] == 0:
        result["comment"] = comment[0:28].decode("latin1", errors="ignore").rstrip("\x00").strip()
        result["track"] = comment[29]
    else:
        result["comment"] = comment.decode("latin1", errors="ignore").rstrip("\x00").strip()
    genre_index = data[127]
    result["genre_index"] = genre_index
    result["genre"] = ID3_GENRES[genre_index] if genre_index < len(ID3_GENRES) else None
    return result


def _read_id3v2_from_file(filepath: str) -> Dict[str, Any]:
    header = _read_file_header(filepath, 10)
    if len(header) < 10 or header[0:3] != b"ID3":
        return {}
    tag_size = _syncsafe_to_int(header[6:10])
    try:
        with open(filepath, "rb") as f:
            data = f.read(10 + tag_size)
        return _parse_id3v2_tag(data)
    except Exception as e:
        return {}


def _read_id3v1_from_file(filepath: str) -> Dict[str, Any]:
    tail = _read_file_tail(filepath, 128)
    if len(tail) < 128:
        return {}
    return _parse_id3v1_tag(tail[-128:])


def _parse_ape_tag_data(data: bytes) -> Dict[str, Any]:
    result: Dict[str, Any] = {"ape_present": False}
    if len(data) < 32:
        return result
    if data[0:8] != b"APETAGEX":
        if data[-32:-24] == b"APETAGEX":
            data = data[-32:] + data[:-32]
        else:
            return result
    version = struct.unpack("<I", data[8:12])[0]
    size = struct.unpack("<I", data[12:16])[0]
    item_count = struct.unpack("<I", data[16:20])[0]
    flags = struct.unpack("<I", data[20:24])[0]
    result.update({
        "ape_present": True,
        "version": version,
        "size": size,
        "item_count": item_count,
        "flags": flags,
        "items": {},
    })
    offset = 32
    for _ in range(item_count):
        if offset + 8 > len(data):
            break
        value_size = struct.unpack("<I", data[offset:offset + 4])[0]
        item_flags = struct.unpack("<I", data[offset + 4:offset + 8])[0]
        offset += 8
        key_end = data.find(b"\x00", offset)
        if key_end == -1:
            break
        key = data[offset:key_end].decode("utf-8", errors="ignore")
        offset = key_end + 1
        value = data[offset:offset + value_size]
        offset += value_size
        item_type = (item_flags >> 1) & 0x3
        type_map = {0: "text", 1: "binary", 2: "external", 3: "reserved"}
        entry: Dict[str, Any] = {
            "flags": item_flags,
            "type": type_map.get(item_type, "unknown"),
        }
        if item_type == 0:
            entry["value"] = value.decode("utf-8", errors="ignore")
        elif item_type == 1:
            description = ""
            data_bytes = value
            if key.lower().startswith("cover art"):
                split = value.split(b"\x00", 1)
                if len(split) == 2:
                    description = split[0].decode("utf-8", errors="ignore")
                    data_bytes = split[1]
            entry.update({
                "description": description,
                "data_size": len(data_bytes),
                "data_preview": data_bytes[:16].hex(),
            })
        elif item_type == 2:
            entry["value"] = value.decode("utf-8", errors="ignore")
        else:
            entry["value"] = value.hex()

        result["items"][key] = entry
    return result


def _parse_adts_header(data: bytes) -> Dict[str, Any]:
    if len(data) < 7:
        return {}
    b0, b1, b2, b3, b4, b5, b6 = data[0:7]
    syncword = ((b0 << 4) | (b1 >> 4)) & 0xFFF
    if syncword != 0xFFF:
        return {}
    mpeg_version = "MPEG-2" if ((b1 >> 3) & 0x1) else "MPEG-4"
    protection_absent = bool(b1 & 0x1)
    profile = ((b2 >> 6) & 0x3) + 1
    sampling_index = (b2 >> 2) & 0xF
    sample_rate = ADTS_SAMPLE_RATES[sampling_index] if sampling_index < len(ADTS_SAMPLE_RATES) else None
    channel_config = ((b2 & 0x1) << 2) | ((b3 >> 6) & 0x3)
    frame_length = ((b3 & 0x3) << 11) | (b4 << 3) | ((b5 >> 5) & 0x7)
    buffer_fullness = ((b5 & 0x1F) << 6) | ((b6 >> 2) & 0x3F)
    num_raw_blocks = b6 & 0x3
    return {
        "mpeg_version": mpeg_version,
        "protection_absent": protection_absent,
        "profile_idc": profile,
        "sample_rate": sample_rate,
        "sampling_index": sampling_index,
        "channel_config": channel_config,
        "frame_length": frame_length,
        "buffer_fullness": buffer_fullness,
        "raw_data_blocks": num_raw_blocks + 1,
    }


def _parse_xing_header(data: bytes, offset: int) -> Dict[str, Any]:
    if offset + 8 > len(data):
        return {}
    flags = struct.unpack(">I", data[offset + 4:offset + 8])[0]
    pos = offset + 8
    result: Dict[str, Any] = {"flags": flags}
    if flags & 0x1 and pos + 4 <= len(data):
        result["frames"] = struct.unpack(">I", data[pos:pos + 4])[0]
        pos += 4
    if flags & 0x2 and pos + 4 <= len(data):
        result["bytes"] = struct.unpack(">I", data[pos:pos + 4])[0]
        pos += 4
    if flags & 0x4 and pos + 100 <= len(data):
        result["toc"] = list(data[pos:pos + 100])
        pos += 100
    if flags & 0x8 and pos + 4 <= len(data):
        result["quality"] = struct.unpack(">I", data[pos:pos + 4])[0]
    return result


def _parse_vbri_header(data: bytes, offset: int) -> Dict[str, Any]:
    if offset + 26 > len(data):
        return {}
    version = struct.unpack(">H", data[offset + 4:offset + 6])[0]
    delay = struct.unpack(">H", data[offset + 6:offset + 8])[0]
    quality = struct.unpack(">H", data[offset + 8:offset + 10])[0]
    bytes_total = struct.unpack(">I", data[offset + 10:offset + 14])[0]
    frames_total = struct.unpack(">I", data[offset + 14:offset + 18])[0]
    return {
        "version": version,
        "delay": delay,
        "quality": quality,
        "bytes": bytes_total,
        "frames": frames_total,
    }


def _parse_lame_tag(data: bytes, offset: int) -> Dict[str, Any]:
    if offset + 24 > len(data):
        return {}
    encoder = data[offset:offset + 9].decode("latin1", errors="ignore").rstrip("\x00")
    rev_method = data[offset + 9]
    lowpass_hz = data[offset + 10] * 100
    delay_padding = (data[offset + 21] << 16) | (data[offset + 22] << 8) | data[offset + 23]
    encoder_delay = delay_padding >> 12
    encoder_padding = delay_padding & 0xFFF
    return {
        "encoder": encoder,
        "tag_revision": (rev_method >> 4) & 0x0F,
        "vbr_method": rev_method & 0x0F,
        "lowpass_hz": lowpass_hz,
        "encoder_delay_samples": encoder_delay,
        "encoder_padding_samples": encoder_padding,
    }


def _read_ogg_packets(filepath: str, max_packets: int = 6, max_pages: int = 50) -> List[bytes]:
    packets: List[bytes] = []
    try:
        with open(filepath, "rb") as f:
            packet_buffer = b""
            pages_read = 0
            while len(packets) < max_packets and pages_read < max_pages:
                header = f.read(27)
                if len(header) < 27 or header[0:4] != b"OggS":
                    break
                seg_count = header[26]
                segments = f.read(seg_count)
                if len(segments) < seg_count:
                    break
                total = sum(segments)
                page_data = f.read(total)
                if len(page_data) < total:
                    break
                offset = 0
                for seg_len in segments:
                    packet_buffer += page_data[offset:offset + seg_len]
                    offset += seg_len
                    if seg_len < 255:
                        packets.append(packet_buffer)
                        packet_buffer = b""
                        if len(packets) >= max_packets:
                            break
                pages_read += 1
    except Exception as e:
        return packets
    return packets


def _parse_opus_head(packet: bytes) -> Dict[str, Any]:
    if not packet.startswith(b"OpusHead") or len(packet) < 19:
        return {}
    return {
        "version": packet[8],
        "channels": packet[9],
        "pre_skip": struct.unpack("<H", packet[10:12])[0],
        "input_sample_rate": struct.unpack("<I", packet[12:16])[0],
        "output_gain": struct.unpack("<h", packet[16:18])[0],
        "channel_mapping_family": packet[18],
        "stream_count": packet[19] if len(packet) > 19 else None,
        "coupled_count": packet[20] if len(packet) > 20 else None,
    }


def _parse_vorbis_id_header(packet: bytes) -> Dict[str, Any]:
    if len(packet) < 30 or packet[0] != 0x01 or packet[1:7] != b"vorbis":
        return {}
    version = struct.unpack("<I", packet[7:11])[0]
    channels = packet[11]
    sample_rate = struct.unpack("<I", packet[12:16])[0]
    bitrate_max = struct.unpack("<I", packet[16:20])[0]
    bitrate_nom = struct.unpack("<I", packet[20:24])[0]
    bitrate_min = struct.unpack("<I", packet[24:28])[0]
    blocksize = packet[28]
    blocksize_0 = 1 << (blocksize & 0x0F)
    blocksize_1 = 1 << ((blocksize >> 4) & 0x0F)
    framing = packet[29]
    return {
        "vorbis_version": version,
        "channels": channels,
        "sample_rate": sample_rate,
        "bitrate_maximum_bps": bitrate_max,
        "bitrate_nominal_bps": bitrate_nom,
        "bitrate_minimum_bps": bitrate_min,
        "blocksize_0": blocksize_0,
        "blocksize_1": blocksize_1,
        "framing_flag": framing,
    }


def _parse_vorbis_comments(packet: bytes, signature: bytes) -> Dict[str, Any]:
    if len(packet) < 8 or packet[0:len(signature)] != signature:
        return {}
    offset = len(signature)
    if offset + 4 > len(packet):
        return {}
    vendor_len = struct.unpack("<I", packet[offset:offset + 4])[0]
    offset += 4
    vendor = packet[offset:offset + vendor_len].decode("utf-8", errors="ignore")
    offset += vendor_len
    if offset + 4 > len(packet):
        return {"vendor_string": vendor}
    comment_count = struct.unpack("<I", packet[offset:offset + 4])[0]
    offset += 4
    comments: Dict[str, Any] = {}
    raw_comments = []
    for _ in range(comment_count):
        if offset + 4 > len(packet):
            break
        length = struct.unpack("<I", packet[offset:offset + 4])[0]
        offset += 4
        value = packet[offset:offset + length].decode("utf-8", errors="ignore")
        offset += length
        raw_comments.append(value)
        if "=" in value:
            key, val = value.split("=", 1)
            key_lower = key.lower()
            if key_lower in comments:
                if isinstance(comments[key_lower], list):
                    comments[key_lower].append(val)
                else:
                    comments[key_lower] = [comments[key_lower], val]
            else:
                comments[key_lower] = val
    return {
        "vendor_string": vendor,
        "comment_count": comment_count,
        "raw_comments": raw_comments,
        "comments": comments,
    }


def _parse_riff_chunks(filepath: str) -> Dict[str, Any]:
    result = {
        "riff_type": None,
        "chunk_count": 0,
        "chunks": [],
        "ds64": {},
        "fmt": {},
        "data": {},
        "info": {},
        "cue_points": [],
        "sampler": {},
        "bext": {},
        "ixml": {},
        "cart": {},
        "adtl": {},
        "axml": {},
    }
    try:
        with open(filepath, "rb") as f:
            header = f.read(12)
            if len(header) < 12 or header[0:4] not in [b"RIFF", b"RF64"]:
                return result
            riff_type = header[8:12].decode("latin1", errors="ignore")
            result["riff_type"] = riff_type
            file_size = Path(filepath).stat().st_size
            while f.tell() + 8 <= file_size:
                chunk_header = f.read(8)
                if len(chunk_header) < 8:
                    break
                chunk_id = chunk_header[0:4]
                chunk_size = struct.unpack("<I", chunk_header[4:8])[0]
                chunk_start = f.tell()
                result["chunks"].append({
                    "id": chunk_id.decode("latin1", errors="ignore"),
                    "size": chunk_size,
                    "offset": chunk_start,
                })
                result["chunk_count"] += 1

                if chunk_id == b"fmt ":
                    fmt_data = f.read(chunk_size)
                    result["fmt"] = _parse_wave_fmt(fmt_data)
                elif chunk_id == b"data":
                    result["data"] = {"size": chunk_size}
                    f.seek(chunk_size, 1)
                elif chunk_id == b"LIST":
                    list_type = f.read(4)
                    list_data_size = chunk_size - 4
                    if list_type == b"INFO":
                        info_data = f.read(list_data_size)
                        result["info"] = _parse_riff_info(info_data)
                    elif list_type == b"adtl":
                        adtl_data = f.read(list_data_size)
                        result["adtl"] = _parse_adtl_list(adtl_data)
                    else:
                        f.seek(list_data_size, 1)
                elif chunk_id == b"ds64":
                    ds64_data = f.read(chunk_size)
                    result["ds64"] = _parse_ds64_chunk(ds64_data)
                elif chunk_id == b"bext":
                    bext_data = f.read(chunk_size)
                    result["bext"] = _parse_bext_chunk(bext_data)
                elif chunk_id == b"iXML":
                    ixml_data = f.read(chunk_size)
                    result["ixml"] = _parse_ixml_chunk(ixml_data)
                elif chunk_id == b"cart":
                    cart_data = f.read(chunk_size)
                    result["cart"] = _parse_cart_chunk(cart_data)
                elif chunk_id == b"axml":
                    axml_data = f.read(chunk_size)
                    result["axml"] = _parse_axml_chunk(axml_data)
                elif chunk_id == b"cue ":
                    cue_data = f.read(chunk_size)
                    result["cue_points"] = _parse_cue_chunk(cue_data)
                elif chunk_id == b"smpl":
                    smpl_data = f.read(chunk_size)
                    result["sampler"] = _parse_smpl_chunk(smpl_data)
                else:
                    f.seek(chunk_size, 1)

                if chunk_size % 2 == 1:
                    f.seek(1, 1)
    except Exception as e:
        return result
    return result


def _parse_ds64_chunk(data: bytes) -> Dict[str, Any]:
    if len(data) < 28:
        return {}
    riff_size = struct.unpack("<Q", data[0:8])[0]
    data_size = struct.unpack("<Q", data[8:16])[0]
    sample_count = struct.unpack("<Q", data[16:24])[0]
    table_length = struct.unpack("<I", data[24:28])[0]
    table = []
    offset = 28
    for _ in range(table_length):
        if offset + 12 > len(data):
            break
        chunk_id = data[offset:offset + 4].decode("latin1", errors="ignore")
        size = struct.unpack("<Q", data[offset + 4:offset + 12])[0]
        table.append({"chunk_id": chunk_id, "size": size})
        offset += 12
    return {
        "riff_size": riff_size,
        "data_size": data_size,
        "sample_count": sample_count,
        "table_length": table_length,
        "table": table,
    }


def _parse_adtl_list(data: bytes) -> Dict[str, Any]:
    result = {
        "labels": [],
        "notes": [],
        "texts": [],
    }
    offset = 0
    while offset + 8 <= len(data):
        chunk_id = data[offset:offset + 4]
        chunk_size = struct.unpack("<I", data[offset + 4:offset + 8])[0]
        offset += 8
        chunk_data = data[offset:offset + chunk_size]
        offset += chunk_size
        if chunk_id == b"labl":
            if len(chunk_data) >= 4:
                cue_id = struct.unpack("<I", chunk_data[0:4])[0]
                text = chunk_data[4:].decode("latin1", errors="ignore").rstrip("\x00")
                result["labels"].append({"cue_id": cue_id, "text": text})
        elif chunk_id == b"note":
            if len(chunk_data) >= 4:
                cue_id = struct.unpack("<I", chunk_data[0:4])[0]
                text = chunk_data[4:].decode("latin1", errors="ignore").rstrip("\x00")
                result["notes"].append({"cue_id": cue_id, "text": text})
        elif chunk_id == b"ltxt":
            if len(chunk_data) >= 20:
                cue_id = struct.unpack("<I", chunk_data[0:4])[0]
                sample_length = struct.unpack("<I", chunk_data[4:8])[0]
                purpose_id = chunk_data[8:12].decode("latin1", errors="ignore")
                country = struct.unpack("<H", chunk_data[12:14])[0]
                language = struct.unpack("<H", chunk_data[14:16])[0]
                dialect = struct.unpack("<H", chunk_data[16:18])[0]
                code_page = struct.unpack("<H", chunk_data[18:20])[0]
                text = chunk_data[20:].decode("latin1", errors="ignore").rstrip("\x00")
                result["texts"].append({
                    "cue_id": cue_id,
                    "sample_length": sample_length,
                    "purpose_id": purpose_id,
                    "country": country,
                    "language": language,
                    "dialect": dialect,
                    "code_page": code_page,
                    "text": text,
                })
        if chunk_size % 2 == 1:
            offset += 1
    return result


def _parse_axml_chunk(data: bytes) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    try:
        xml_text = data.decode("utf-8", errors="ignore").strip()
        result["raw"] = xml_text
        try:
            root = ET.fromstring(xml_text)
            result["root_tag"] = root.tag
            result["attribute_count"] = len(root.attrib)
        except Exception:
            result["parse_error"] = True
    except Exception:
        return result
    return result


def _parse_cart_chunk(data: bytes) -> Dict[str, Any]:
    if len(data) < 2048:
        return {}
    offset = 0

    def read_str(length: int) -> str:
        nonlocal offset
        value = data[offset:offset + length]
        offset += length
        return value.decode("latin1", errors="ignore").rstrip("\x00").strip()

    def read_u32() -> int:
        nonlocal offset
        if offset + 4 > len(data):
            offset = len(data)
            return 0
        value = struct.unpack("<I", data[offset:offset + 4])[0]
        offset += 4
        return value

    def read_timer() -> Dict[str, Any]:
        nonlocal offset
        if offset + 8 > len(data):
            offset = len(data)
            return {}
        usage = data[offset:offset + 4].decode("latin1", errors="ignore")
        value = struct.unpack("<I", data[offset + 4:offset + 8])[0]
        offset += 8
        return {"usage": usage, "value": value}

    result = {
        "version": read_u32(),
        "title": read_str(64),
        "artist": read_str(64),
        "cut_id": read_str(64),
        "client_id": read_str(64),
        "category": read_str(64),
        "classification": read_str(64),
        "out_cue": read_str(64),
        "start_date": read_str(10),
        "start_time": read_str(8),
        "end_date": read_str(10),
        "end_time": read_str(8),
        "producer_app_id": read_str(64),
        "producer_app_version": read_str(64),
        "user_def": read_str(64),
        "level_reference": read_u32(),
        "post_timers": [],
        "url": "",
        "tag_text": "",
    }

    for _ in range(8):
        timer = read_timer()
        if timer:
            result["post_timers"].append(timer)

    if offset + 276 <= len(data):
        offset += 276  # reserved

    if offset + 1024 <= len(data):
        result["url"] = read_str(1024)

    if offset < len(data):
        result["tag_text"] = data[offset:].decode("latin1", errors="ignore").rstrip("\x00").strip()

    return result


def _parse_extended80(data: bytes) -> Optional[float]:
    if len(data) < 10:
        return None
    sign = 1 if (data[0] & 0x80) else 0
    exponent = ((data[0] & 0x7F) << 8) | data[1]
    mantissa = int.from_bytes(data[2:10], "big")
    if exponent == 0 and mantissa == 0:
        return 0.0
    integer_bit = (mantissa >> 63) & 0x01
    fraction = mantissa & ((1 << 63) - 1)
    value = (integer_bit + (fraction / (1 << 63))) * (2 ** (exponent - 16383))
    if sign:
        value = -value
    return value


def _parse_aiff_comm(data: bytes) -> Dict[str, Any]:
    if len(data) < 18:
        return {}
    channels = struct.unpack(">H", data[0:2])[0]
    num_frames = struct.unpack(">I", data[2:6])[0]
    sample_size = struct.unpack(">H", data[6:8])[0]
    sample_rate = _parse_extended80(data[8:18])
    return {
        "channels": channels,
        "num_frames": num_frames,
        "sample_size_bits": sample_size,
        "sample_rate": sample_rate,
    }


def _parse_aiff_chunks(filepath: str) -> Dict[str, Any]:
    result = {
        "form_type": None,
        "chunk_count": 0,
        "chunks": [],
        "comm": {},
        "ssnd": {},
        "text": {},
        "comments": [],
        "markers": [],
        "instrument": {},
    }
    try:
        with open(filepath, "rb") as f:
            header = f.read(12)
            if len(header) < 12 or header[0:4] != b"FORM":
                return result
            result["form_type"] = header[8:12].decode("latin1", errors="ignore")
            file_size = Path(filepath).stat().st_size
            while f.tell() + 8 <= file_size:
                chunk_header = f.read(8)
                if len(chunk_header) < 8:
                    break
                chunk_id = chunk_header[0:4]
                chunk_size = struct.unpack(">I", chunk_header[4:8])[0]
                chunk_start = f.tell()
                result["chunks"].append({
                    "id": chunk_id.decode("latin1", errors="ignore"),
                    "size": chunk_size,
                    "offset": chunk_start,
                })
                result["chunk_count"] += 1
                chunk_data = f.read(chunk_size)

                if chunk_id == b"COMM":
                    result["comm"] = _parse_aiff_comm(chunk_data)
                elif chunk_id == b"SSND":
                    if len(chunk_data) >= 8:
                        offset = struct.unpack(">I", chunk_data[0:4])[0]
                        block_size = struct.unpack(">I", chunk_data[4:8])[0]
                        result["ssnd"] = {
                            "offset": offset,
                            "block_size": block_size,
                            "data_size": max(0, chunk_size - 8),
                        }
                elif chunk_id in [b"NAME", b"AUTH", b"ANNO"]:
                    key = chunk_id.decode("latin1", errors="ignore").lower()
                    result["text"][key] = chunk_data.decode("latin1", errors="ignore").rstrip("\x00")
                elif chunk_id == b"COMT":
                    if len(chunk_data) >= 2:
                        count = struct.unpack(">H", chunk_data[0:2])[0]
                        pos = 2
                        for _ in range(count):
                            if pos + 8 > len(chunk_data):
                                break
                            timestamp = struct.unpack(">I", chunk_data[pos:pos + 4])[0]
                            marker_id = struct.unpack(">H", chunk_data[pos + 4:pos + 6])[0]
                            text_len = struct.unpack(">H", chunk_data[pos + 6:pos + 8])[0]
                            pos += 8
                            text = chunk_data[pos:pos + text_len].decode("latin1", errors="ignore")
                            pos += text_len
                            result["comments"].append({
                                "timestamp": timestamp,
                                "marker_id": marker_id,
                                "text": text,
                            })
                elif chunk_id == b"MARK":
                    if len(chunk_data) >= 2:
                        count = struct.unpack(">H", chunk_data[0:2])[0]
                        pos = 2
                        for _ in range(count):
                            if pos + 6 > len(chunk_data):
                                break
                            marker_id = struct.unpack(">H", chunk_data[pos:pos + 2])[0]
                            position = struct.unpack(">I", chunk_data[pos + 2:pos + 6])[0]
                            name_len = chunk_data[pos + 6] if pos + 6 < len(chunk_data) else 0
                            pos += 7
                            name = chunk_data[pos:pos + name_len].decode("latin1", errors="ignore")
                            pos += name_len
                            if name_len % 2 == 0:
                                pos += 1
                            result["markers"].append({
                                "marker_id": marker_id,
                                "position": position,
                                "name": name,
                            })
                elif chunk_id == b"INST":
                    if len(chunk_data) >= 20:
                        result["instrument"] = {
                            "base_note": chunk_data[0],
                            "detune": chunk_data[1],
                            "low_note": chunk_data[2],
                            "high_note": chunk_data[3],
                            "low_velocity": chunk_data[4],
                            "high_velocity": chunk_data[5],
                            "gain": struct.unpack(">h", chunk_data[6:8])[0],
                        }

                if chunk_size % 2 == 1:
                    f.seek(1, 1)
    except Exception:
        return result
    return result


def _parse_dsf_header(filepath: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    try:
        with open(filepath, "rb") as f:
            header = f.read(12)
            if len(header) < 12 or header[0:4] != b"DSD ":
                return result
            chunk_size = struct.unpack("<Q", header[4:12])[0]
            file_size = struct.unpack("<Q", f.read(8))[0]
            metadata_offset = struct.unpack("<Q", f.read(8))[0]
            fmt_id = f.read(4)
            if fmt_id != b"fmt ":
                return result
            fmt_size = struct.unpack("<Q", f.read(8))[0]
            fmt_data = f.read(min(fmt_size, 52))
            if len(fmt_data) < 52:
                return result
            result = {
                "format": "DSF",
                "chunk_size": chunk_size,
                "file_size": file_size,
                "metadata_offset": metadata_offset,
                "format_version": struct.unpack("<I", fmt_data[0:4])[0],
                "format_id": struct.unpack("<I", fmt_data[4:8])[0],
                "channel_type": struct.unpack("<I", fmt_data[8:12])[0],
                "channel_num": struct.unpack("<I", fmt_data[12:16])[0],
                "sampling_frequency": struct.unpack("<I", fmt_data[16:20])[0],
                "bits_per_sample": struct.unpack("<I", fmt_data[20:24])[0],
                "sample_count": struct.unpack("<Q", fmt_data[24:32])[0],
                "block_size_per_channel": struct.unpack("<I", fmt_data[32:36])[0],
            }
            if metadata_offset and metadata_offset < file_size:
                f.seek(metadata_offset, 0)
                id3_header = f.read(10)
                if len(id3_header) == 10 and id3_header[0:3] == b"ID3":
                    tag_size = _syncsafe_to_int(id3_header[6:10])
                    max_size = 2 * 1024 * 1024
                    read_size = min(tag_size, max_size)
                    id3_data = id3_header + f.read(read_size)
                    result["id3_present"] = True
                    result["id3_tag_size"] = tag_size
                    result["id3"] = _parse_id3v2_tag(id3_data)
    except Exception:
        return result
    return result


def _parse_dsdiff_header(filepath: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    try:
        with open(filepath, "rb") as f:
            header = f.read(12)
            if len(header) < 12 or header[0:4] != b"FRM8":
                return result
            form_size = struct.unpack(">Q", header[4:12])[0]
            form_type = f.read(4)
            if form_type not in [b"DSD ", b"DST "]:
                return result
            result["format"] = "DSDIFF"
            result["form_type"] = form_type.decode("latin1", errors="ignore")
            result["form_size"] = form_size

            end_pos = min(Path(filepath).stat().st_size, form_size + 12)
            while f.tell() + 12 <= end_pos:
                chunk_id = f.read(4)
                if len(chunk_id) < 4:
                    break
                chunk_size = struct.unpack(">Q", f.read(8))[0]
                chunk_start = f.tell()
                chunk_data = f.read(chunk_size)

                if chunk_id == b"FVER" and len(chunk_data) >= 4:
                    result["format_version"] = struct.unpack(">I", chunk_data[0:4])[0]
                elif chunk_id == b"PROP" and len(chunk_data) >= 4:
                    prop_type = chunk_data[0:4]
                    result["prop_type"] = prop_type.decode("latin1", errors="ignore")
                    prop_offset = 4
                    while prop_offset + 12 <= len(chunk_data):
                        sub_id = chunk_data[prop_offset:prop_offset + 4]
                        sub_size = struct.unpack(">Q", chunk_data[prop_offset + 4:prop_offset + 12])[0]
                        prop_offset += 12
                        sub_data = chunk_data[prop_offset:prop_offset + sub_size]
                        prop_offset += sub_size

                        if sub_id == b"FS  " and len(sub_data) >= 4:
                            result["sample_rate"] = struct.unpack(">I", sub_data[0:4])[0]
                        elif sub_id == b"CHNL" and len(sub_data) >= 2:
                            channel_count = struct.unpack(">H", sub_data[0:2])[0]
                            result["channel_count"] = channel_count
                            channel_ids = []
                            pos = 2
                            for _ in range(channel_count):
                                if pos + 4 > len(sub_data):
                                    break
                                channel_ids.append(sub_data[pos:pos + 4].decode("latin1", errors="ignore"))
                                pos += 4
                            result["channel_ids"] = channel_ids
                        elif sub_id == b"CMPR" and len(sub_data) >= 5:
                            comp_id = sub_data[0:4].decode("latin1", errors="ignore")
                            name_len = sub_data[4]
                            name = sub_data[5:5 + name_len].decode("latin1", errors="ignore")
                            result["compression_id"] = comp_id
                            result["compression_name"] = name
                        if sub_size % 2 == 1:
                            prop_offset += 1
                elif chunk_id in [b"DSD ", b"DST "]:
                    result["audio_chunk_id"] = chunk_id.decode("latin1", errors="ignore")
                    result["audio_chunk_size"] = chunk_size
                elif chunk_id.strip() == b"ID3":
                    result["id3_present"] = True
                    result["id3_size"] = chunk_size

                if chunk_size % 2 == 1:
                    f.seek(1, 1)
                if f.tell() <= chunk_start:
                    break
    except Exception:
        return result
    return result


def _parse_wave_fmt(data: bytes) -> Dict[str, Any]:
    if len(data) < 16:
        return {}
    result = {}
    audio_format = struct.unpack("<H", data[0:2])[0]
    result["audio_format"] = audio_format
    result["channels"] = struct.unpack("<H", data[2:4])[0]
    result["sample_rate"] = struct.unpack("<I", data[4:8])[0]
    result["byte_rate"] = struct.unpack("<I", data[8:12])[0]
    result["block_align"] = struct.unpack("<H", data[12:14])[0]
    result["bits_per_sample"] = struct.unpack("<H", data[14:16])[0]
    if len(data) >= 18:
        extra_size = struct.unpack("<H", data[16:18])[0]
        result["extra_size"] = extra_size
        if audio_format == 0xFFFE and len(data) >= 18 + extra_size:
            valid_bits = struct.unpack("<H", data[18:20])[0]
            channel_mask = struct.unpack("<I", data[20:24])[0]
            subformat_guid = data[24:40].hex()
            result["valid_bits_per_sample"] = valid_bits
            result["channel_mask"] = channel_mask
            result["subformat_guid"] = subformat_guid
    return result


def _parse_riff_info(data: bytes) -> Dict[str, Any]:
    info: Dict[str, Any] = {}
    offset = 0
    while offset + 8 <= len(data):
        tag = data[offset:offset + 4]
        size = struct.unpack("<I", data[offset + 4:offset + 8])[0]
        offset += 8
        value = data[offset:offset + size].decode("latin1", errors="ignore").rstrip("\x00").strip()
        offset += size
        if size % 2 == 1:
            offset += 1
        key = RIFF_INFO_TAGS.get(tag, tag.decode("latin1", errors="ignore"))
        info[key] = value
    return info


def _parse_bext_chunk(data: bytes) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    offset = 0
    def read_str(length: int) -> str:
        nonlocal offset
        if offset + length > len(data):
            offset = len(data)
            return ""
        value = data[offset:offset + length]
        offset += length
        return value.decode("latin1", errors="ignore").rstrip("\x00").strip()

    def read_bytes(length: int) -> bytes:
        nonlocal offset
        if offset + length > len(data):
            offset = len(data)
            return b""
        value = data[offset:offset + length]
        offset += length
        return value

    result["description"] = read_str(256)
    result["originator"] = read_str(32)
    result["originator_reference"] = read_str(32)
    result["origination_date"] = read_str(10)
    result["origination_time"] = read_str(8)
    time_ref_bytes = read_bytes(8)
    if len(time_ref_bytes) == 8:
        result["time_reference"] = struct.unpack("<Q", time_ref_bytes)[0]
    version_bytes = read_bytes(2)
    if len(version_bytes) == 2:
        result["version"] = struct.unpack("<H", version_bytes)[0]
    umid = read_bytes(64)
    if umid:
        result["umid"] = umid.hex()
    if len(data) >= 602:
        loudness_bytes = read_bytes(10)
        if len(loudness_bytes) == 10:
            result["loudness_value"] = struct.unpack("<H", loudness_bytes[0:2])[0]
            result["loudness_range"] = struct.unpack("<H", loudness_bytes[2:4])[0]
            result["max_true_peak_level"] = struct.unpack("<H", loudness_bytes[4:6])[0]
            result["max_momentary_loudness"] = struct.unpack("<H", loudness_bytes[6:8])[0]
            result["max_short_term_loudness"] = struct.unpack("<H", loudness_bytes[8:10])[0]
        remaining = data[offset:]
        if remaining:
            result["coding_history"] = remaining.decode("latin1", errors="ignore").rstrip("\x00").strip()
    else:
        remaining = data[offset:]
        if remaining:
            result["coding_history"] = remaining.decode("latin1", errors="ignore").rstrip("\x00").strip()
    return result


def _parse_ixml_chunk(data: bytes) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    try:
        text = data.decode("utf-8", errors="ignore").strip("\x00").strip()
        if not text:
            return result
        root = ET.fromstring(text)
        for elem in root.iter():
            if elem is root:
                continue
            if elem.text and elem.text.strip():
                key = elem.tag
                value = elem.text.strip()
                if key in result:
                    if isinstance(result[key], list):
                        result[key].append(value)
                    else:
                        result[key] = [result[key], value]
                else:
                    result[key] = value
    except Exception as e:
        return result
    return result


def _parse_cue_chunk(data: bytes) -> List[Dict[str, Any]]:
    cues = []
    if len(data) < 4:
        return cues
    count = struct.unpack("<I", data[0:4])[0]
    offset = 4
    for _ in range(count):
        if offset + 24 > len(data):
            break
        cue_id = struct.unpack("<I", data[offset:offset + 4])[0]
        position = struct.unpack("<I", data[offset + 4:offset + 8])[0]
        data_chunk_id = data[offset + 8:offset + 12].decode("latin1", errors="ignore")
        chunk_start = struct.unpack("<I", data[offset + 12:offset + 16])[0]
        block_start = struct.unpack("<I", data[offset + 16:offset + 20])[0]
        sample_offset = struct.unpack("<I", data[offset + 20:offset + 24])[0]
        cues.append({
            "cue_id": cue_id,
            "position": position,
            "data_chunk_id": data_chunk_id,
            "chunk_start": chunk_start,
            "block_start": block_start,
            "sample_offset": sample_offset,
        })
        offset += 24
    return cues


def _parse_smpl_chunk(data: bytes) -> Dict[str, Any]:
    if len(data) < 36:
        return {}
    manufacturer = struct.unpack("<I", data[0:4])[0]
    product = struct.unpack("<I", data[4:8])[0]
    sample_period = struct.unpack("<I", data[8:12])[0]
    midi_unity = struct.unpack("<I", data[12:16])[0]
    midi_pitch_fraction = struct.unpack("<I", data[16:20])[0]
    smpte_format = struct.unpack("<I", data[20:24])[0]
    smpte_offset = struct.unpack("<I", data[24:28])[0]
    num_loops = struct.unpack("<I", data[28:32])[0]
    sampler_data = struct.unpack("<I", data[32:36])[0]
    return {
        "manufacturer": manufacturer,
        "product": product,
        "sample_period": sample_period,
        "midi_unity_note": midi_unity,
        "midi_pitch_fraction": midi_pitch_fraction,
        "smpte_format": smpte_format,
        "smpte_offset": smpte_offset,
        "num_loops": num_loops,
        "sampler_data_bytes": sampler_data,
    }


def _find_mp4_ilst(filepath: str) -> Optional[Tuple[int, int]]:
    try:
        file_size = Path(filepath).stat().st_size
        with open(filepath, "rb") as f:
            for atom_type, start, size in _iter_mp4_atoms(f, 0, file_size, 6):
                if atom_type == b"ilst":
                    return start, size
    except Exception as e:
        return None
    return None


def _iter_mp4_atoms(f, start: int, size: int, max_depth: int) -> List[Tuple[bytes, int, int]]:
    results: List[Tuple[bytes, int, int]] = []
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
        results.append((atom_type, data_start, data_size))

        if atom_type in MP4_CONTAINER_ATOMS and max_depth > 0:
            child_start = data_start
            child_size = data_size
            if atom_type == b"meta":
                child_start += 4
                child_size = max(0, child_size - 4)
            results.extend(_iter_mp4_atoms(f, child_start, child_size, max_depth - 1))

        f.seek(data_start + data_size, 0)
    return results


def _parse_mp4_ilst(filepath: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "tags": {},
        "raw_tags": {},
        "tag_count": 0,
        "chapters": [],
        "chapter_track_ids": [],
    }
    ilst_location = _find_mp4_ilst(filepath)
    start = None
    size = None
    if ilst_location:
        start, size = ilst_location
    try:
        with open(filepath, "rb") as f:
            if start is not None and size is not None:
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
            result["chapters"] = _parse_mp4_chapter_list(f)
            result["chapter_track_ids"] = _parse_mp4_chap_track_refs(f)
    except Exception as e:
        return result
    return result


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
                decoded = _decode_mp4_data(data_type, data_payload)
                data_values.append(decoded)
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
    elif item_type in [b"cpil", b"pgap", b"pcst", b"hdvd"] and raw_payloads:
        result["value"] = bool(raw_payloads[0][0]) if raw_payloads[0] else None
    elif item_type == b"tmpo" and raw_payloads:
        payload = raw_payloads[0]
        if len(payload) >= 2:
            result["value"] = struct.unpack(">H", payload[0:2])[0]
    elif item_type == b"stik" and raw_payloads:
        media_code = raw_payloads[0][0] if raw_payloads[0] else 0
        media_map = {
            0: "movie",
            1: "music",
            2: "audiobook",
            6: "music_video",
            9: "movie",
            10: "tv_show",
            11: "booklet",
            14: "ringtone",
            21: "podcast",
        }
        result["value"] = {"code": media_code, "label": media_map.get(media_code, "unknown")}
    elif data_values:
        result["value"] = data_values[0] if len(data_values) == 1 else data_values
    if mean_value and name_value and data_values:
        key = f"{mean_value}:{name_value}"
        result["freeform"][key] = data_values[0] if len(data_values) == 1 else data_values
    return result


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


def _parse_mp4_chapter_list(f) -> List[Dict[str, Any]]:
    chapters = []
    try:
        atoms = _iter_mp4_atoms(f, 0, Path(f.name).stat().st_size, max_depth=3)
        chpl_atoms = [a for a in atoms if a[0] == b"chpl"]
        if not chpl_atoms:
            return chapters
        atom_type, start, size = chpl_atoms[0]
        f.seek(start, 0)
        payload = f.read(size)
        if len(payload) < 8:
            return chapters
        entry_count = payload[4]
        pos = 5
        for _ in range(entry_count):
            if pos + 9 > len(payload):
                break
            start_time = struct.unpack(">Q", payload[pos:pos + 8])[0]
            title_len = payload[pos + 8]
            pos += 9
            title = payload[pos:pos + title_len].decode("utf-8", errors="ignore")
            pos += title_len
            chapters.append({
                "start_time": start_time,
                "title": title,
            })
        return chapters
    except Exception:
        return chapters


def _parse_mp4_chap_track_refs(f) -> List[int]:
    track_ids: List[int] = []
    try:
        atoms = _iter_mp4_atoms(f, 0, Path(f.name).stat().st_size, max_depth=3)
        chap_atoms = [a for a in atoms if a[0] == b"chap"]
        for _, start, size in chap_atoms:
            f.seek(start, 0)
            payload = f.read(size)
            for i in range(0, len(payload), 4):
                if i + 4 <= len(payload):
                    track_ids.append(struct.unpack(">I", payload[i:i + 4])[0])
        return track_ids
    except Exception:
        return track_ids


def _parse_asf_header(filepath: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"asf_detected": False}
    try:
        with open(filepath, "rb") as f:
            header_guid = f.read(16)
            if header_guid != ASF_HEADER_GUID:
                return result
            result["asf_detected"] = True
            header_size = struct.unpack("<Q", f.read(8))[0]
            object_count = struct.unpack("<I", f.read(4))[0]
            f.read(2)
            result["header_size"] = header_size
            result["object_count"] = object_count
            for _ in range(object_count):
                obj_guid = f.read(16)
                if len(obj_guid) < 16:
                    break
                obj_size = struct.unpack("<Q", f.read(8))[0]
                obj_data = f.read(max(0, obj_size - 24))
                if obj_guid == ASF_FILE_PROPERTIES_GUID and len(obj_data) >= 80:
                    file_id = obj_data[0:16].hex()
                    file_size = struct.unpack("<Q", obj_data[16:24])[0]
                    creation_date = struct.unpack("<Q", obj_data[24:32])[0]
                    data_packets = struct.unpack("<Q", obj_data[32:40])[0]
                    play_duration = struct.unpack("<Q", obj_data[40:48])[0]
                    send_duration = struct.unpack("<Q", obj_data[48:56])[0]
                    preroll = struct.unpack("<Q", obj_data[56:64])[0]
                    flags = struct.unpack("<I", obj_data[64:68])[0]
                    min_packet = struct.unpack("<I", obj_data[68:72])[0]
                    max_packet = struct.unpack("<I", obj_data[72:76])[0]
                    max_bitrate = struct.unpack("<I", obj_data[76:80])[0]
                    result["file_properties"] = {
                        "file_id": file_id,
                        "file_size": file_size,
                        "creation_time_filetime": creation_date,
                        "data_packets_count": data_packets,
                        "play_duration_100ns": play_duration,
                        "send_duration_100ns": send_duration,
                        "preroll_ms": preroll,
                        "flags": flags,
                        "min_packet_size": min_packet,
                        "max_packet_size": max_packet,
                        "max_bitrate": max_bitrate,
                    }
    except Exception as e:
        return result
    return result


def extract_audio_codec_details(filepath: str) -> Dict[str, Any]:
    """
    Extract comprehensive audio codec metadata.
    
    Supports:
    - MP3: LAME tags, VBR info, encoder settings (~80 fields)
    - AAC: Profile, SBR/PS flags, frame length (~40 fields)
    - FLAC: Metadata blocks, MD5, compression (~50 fields)
    - Opus: Header, channel mapping, pre-skip (~30 fields)
    - Vorbis: Comment headers, vendor string (~40 fields)
    - Generic: Sample rate, bit depth, channels
    
    Target: ~240 fields
    """
    result = {
        "detection": {},
        "id3_details": {},
        "ape_details": {},
        "mp4_details": {},
        "riff_details": {},
        "bwf_details": {},
        "ixml_details": {},
        "asf_details": {},
        "dsd_details": {},
        "aiff_details": {},
        "mp3_details": {},
        "aac_details": {},
        "flac_details": {},
        "opus_details": {},
        "vorbis_details": {},
        "replaygain": {},
        "generic_audio": {},
        "fields_extracted": 0
    }
    
    try:
        path = Path(filepath)
        if not path.exists():
            result["error"] = "File not found"
            return result

        header = _read_file_header(filepath, 64)
        tail = _read_file_tail(filepath, 256)
        ext = path.suffix.lower()
        signature = None
        if header.startswith(b"ID3") or (len(header) > 1 and header[0] == 0xFF and (header[1] & 0xE0) == 0xE0):
            signature = "mp3"
        elif header.startswith(b"fLaC"):
            signature = "flac"
        elif header.startswith(b"OggS"):
            signature = "ogg"
        elif header[0:4] in [b"RIFF", b"RF64"]:
            signature = "riff"
        elif header[0:4] == b"FORM" and len(header) >= 12 and header[8:12] in [b"AIFF", b"AIFC"]:
            signature = "aiff"
        elif header[0:4] == b"DSD ":
            signature = "dsf"
        elif header[0:4] == b"FRM8":
            signature = "dsdiff"
        elif header[0:4] == b"MAC ":
            signature = "ape"
        elif len(header) >= 8 and header[4:8] == b"ftyp":
            signature = "mp4"
        elif len(header) >= 2 and header[0] == 0xFF and (header[1] & 0xF6) in [0xF0, 0xF2, 0xF4, 0xF6]:
            signature = "adts"
        elif header[0:16] == ASF_HEADER_GUID:
            signature = "asf"

        result["detection"] = {
            "extension": ext,
            "signature": signature,
            "id3v2_header": header.startswith(b"ID3"),
            "id3v1_footer": tail[-128:-125] == b"TAG" if len(tail) >= 128 else False,
        }

        id3v2 = _read_id3v2_from_file(filepath)
        if id3v2:
            result["id3_details"]["id3v2"] = id3v2
        id3v1 = _read_id3v1_from_file(filepath)
        if id3v1:
            result["id3_details"]["id3v1"] = id3v1

        probe_data = run_audio_ffprobe(filepath)
        audio_streams = [s for s in probe_data.get("streams", []) if s.get("codec_type") == "audio"] if probe_data else []
        primary_stream = audio_streams[0] if audio_streams else {}
        codec_name = primary_stream.get("codec_name", "").lower() if primary_stream else ""

        # Format-specific extraction
        if signature == "mp3" or codec_name == "mp3":
            result["mp3_details"] = extract_mp3_details(filepath, primary_stream)
        if signature == "adts" or codec_name == "aac":
            result["aac_details"] = extract_aac_details(filepath, primary_stream)
        if signature == "flac" or codec_name == "flac":
            result["flac_details"] = extract_flac_details(filepath)
        if signature == "ogg" or codec_name in ["opus", "vorbis"]:
            ogg_packets = _read_ogg_packets(filepath)
            if ogg_packets:
                opus_head = _parse_opus_head(ogg_packets[0])
                if opus_head:
                    result["opus_details"] = extract_opus_details(filepath, primary_stream, ogg_packets)
                vorbis_id = _parse_vorbis_id_header(ogg_packets[0])
                if vorbis_id:
                    result["vorbis_details"] = extract_vorbis_details(filepath, primary_stream, ogg_packets)
        if signature == "riff" and header[8:12] in [b"WAVE", b"RF64"]:
            result["riff_details"] = _parse_riff_chunks(filepath)
            if result["riff_details"].get("bext"):
                result["bwf_details"] = result["riff_details"]["bext"]
            if result["riff_details"].get("ixml"):
                result["ixml_details"] = result["riff_details"]["ixml"]
        if signature == "aiff":
            result["aiff_details"] = _parse_aiff_chunks(filepath)
        if signature == "dsf" or ext == ".dsf":
            result["dsd_details"] = _parse_dsf_header(filepath)
        if signature == "dsdiff" or ext in [".dff", ".dsd"]:
            result["dsd_details"] = _parse_dsdiff_header(filepath)
        if signature == "mp4" or ext in [".m4a", ".mp4", ".m4b"]:
            result["mp4_details"] = _parse_mp4_ilst(filepath)
        if signature == "asf":
            result["asf_details"] = _parse_asf_header(filepath)

        # APE tags (often appended to MP3/APE)
        if signature == "ape" or tail.endswith(b"APETAGEX") or (len(tail) >= 32 and tail[-32:-24] == b"APETAGEX"):
            ape_offset = None
            try:
                with open(filepath, "rb") as f:
                    f.seek(-32, 2)
                    footer = f.read(32)
                    if footer[0:8] == b"APETAGEX":
                        ape_size = struct.unpack("<I", footer[12:16])[0]
                        ape_offset = max(0, path.stat().st_size - ape_size)
                        f.seek(ape_offset, 0)
                        ape_data = f.read(ape_size)
                        result["ape_details"] = _parse_ape_tag_data(ape_data)
            except Exception as e:
                pass  # TODO: Consider logging: logger.debug(f'Handled exception: {e}')

        # Generic audio properties
        if primary_stream:
            result["generic_audio"] = extract_generic_audio_properties(primary_stream)

        # ReplayGain consolidation
        replaygain = {}
        for source in [
            result["id3_details"].get("id3v2", {}).get("text_frames", {}),
            result["id3_details"].get("id3v1", {}),
            result.get("flac_details", {}).get("vorbis_comments", {}).get("comment_map", {}),
            result.get("vorbis_details", {}).get("vorbis_comments", {}).get("comments", {}),
            result.get("opus_details", {}).get("opus_tags", {}).get("comments", {}),
            result.get("mp4_details", {}).get("tags", {}),
            result.get("ape_details", {}).get("items", {}),
        ]:
            for key, value in source.items():
                key_lower = key.lower()
                if "replaygain" in key_lower:
                    if isinstance(value, dict) and "value" in value:
                        replaygain[key_lower] = value["value"]
                    else:
                        replaygain[key_lower] = value
        if replaygain:
            result["replaygain"] = replaygain

        # Count fields (exclude fields_extracted itself)
        result["fields_extracted"] = sum(
            _count_fields(value)
            for key, value in result.items()
            if key not in ["fields_extracted"]
        )
        
    except Exception as e:
        result["error"] = str(e)[:200]
    
    return result


def run_audio_ffprobe(filepath: str) -> Optional[Dict]:
    """Run ffprobe on audio file."""
    try:
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams",
            filepath
        ]
        
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if proc.returncode != 0:
            return None
        
        return json.loads(proc.stdout)
    
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return None


def extract_mp3_details(filepath: str, stream: Dict) -> Dict[str, Any]:
    """
    Extract MP3-specific metadata (~80 fields).
    
    Includes:
    - LAME encoder tags (version, VBR method, quality)
    - Xing/Info VBR headers
    - Frame header details
    - Encoder delay/padding
    """
    result = {}
    
    # Basic codec info
    result["codec_name"] = stream.get("codec_name")
    result["codec_long_name"] = stream.get("codec_long_name")
    
    # Bitrate info
    bitrate = stream.get("bit_rate")
    if bitrate:
        result["bit_rate_bps"] = int(bitrate)
        result["bit_rate_kbps"] = round(int(bitrate) / 1000, 1)
    
    # Sample rate and channels
    result["sample_rate"] = stream.get("sample_rate")
    result["channels"] = stream.get("channels")
    result["channel_layout"] = stream.get("channel_layout")
    
    # Duration
    duration = stream.get("duration")
    if duration:
        result["duration_seconds"] = float(duration)
    
    # Parse MP3 frame header from file
    try:
        with open(filepath, 'rb') as f:
            # Skip ID3v2 tag if present
            header = f.read(10)
            if header[0:3] == b'ID3':
                # ID3v2 header present
                size = ((header[6] & 0x7F) << 21) | ((header[7] & 0x7F) << 14) | \
                       ((header[8] & 0x7F) << 7) | (header[9] & 0x7F)
                f.seek(size + 10)
            else:
                f.seek(0)
            
            # Find MP3 sync word (0xFFE or 0xFFF)
            frame_header = None
            while True:
                data = f.read(4)
                if len(data) < 4:
                    break
                
                if data[0] == 0xFF and (data[1] & 0xE0) == 0xE0:
                    frame_header = data
                    break
                
                f.seek(-3, 1)  # Back up 3 bytes
            
            if frame_header:
                mp3_frame = parse_mp3_frame_header(frame_header)
                result.update(mp3_frame)

            # Read first chunk for Xing/VBRI/LAME
            f.seek(0, 0)
            if header[0:3] == b'ID3':
                f.seek(size + 10)
            first_chunk = f.read(4096)
            if first_chunk:
                xing_offset = first_chunk.find(b"Xing")
                if xing_offset == -1:
                    xing_offset = first_chunk.find(b"Info")
                if xing_offset != -1:
                    result["xing_header"] = _parse_xing_header(first_chunk, xing_offset)

                vbri_offset = first_chunk.find(b"VBRI")
                if vbri_offset != -1:
                    result["vbri_header"] = _parse_vbri_header(first_chunk, vbri_offset)

                lame_offset = first_chunk.find(b"LAME")
                if lame_offset != -1:
                    result["lame_tag"] = _parse_lame_tag(first_chunk, lame_offset)
                    if result["lame_tag"].get("encoder_delay_samples") is not None:
                        result["encoder_delay_samples"] = result["lame_tag"]["encoder_delay_samples"]
                        result["encoder_padding_samples"] = result["lame_tag"]["encoder_padding_samples"]
    
    except Exception as e:
        pass  # TODO: Consider logging: logger.debug(f'Handled exception: {e}')
    
    # Look for LAME tags in stream tags
    tags = stream.get("tags", {})
    
    if "encoder" in tags:
        encoder = tags["encoder"]
        result["encoder"] = encoder
        
        # Parse LAME version
        if "LAME" in encoder:
            result["is_lame_encoded"] = True
            result["lame_version"] = encoder.split("LAME")[-1].strip()
            
            # LAME quality preset detection
            if "V0" in encoder:
                result["lame_preset"] = "V0 (245 kbps)"
            elif "V2" in encoder:
                result["lame_preset"] = "V2 (190 kbps)"
            elif "V4" in encoder:
                result["lame_preset"] = "V4 (165 kbps)"
            elif "V6" in encoder:
                result["lame_preset"] = "V6 (130 kbps)"
            elif "V8" in encoder:
                result["lame_preset"] = "V8 (115 kbps)"
        else:
            result["is_lame_encoded"] = False
    
    # VBR detection
    result["vbr_detected"] = bool(result.get("xing_header") or result.get("vbri_header"))
    result["vbr_method"] = None
    result["vbr_quality"] = None
    if result.get("lame_tag"):
        result["vbr_method"] = result["lame_tag"].get("vbr_method")
        result["vbr_quality"] = result["lame_tag"].get("tag_revision")
    result.setdefault("encoder_delay_samples", None)
    result.setdefault("encoder_padding_samples", None)
    
    # Replay gain
    if "replaygain_track_gain" in tags:
        result["replaygain_track_gain"] = tags["replaygain_track_gain"]
    if "replaygain_track_peak" in tags:
        result["replaygain_track_peak"] = tags["replaygain_track_peak"]
    
    return result


def parse_mp3_frame_header(header: bytes) -> Dict[str, Any]:
    """Parse MP3 frame header."""
    result = {}
    
    # Byte 1: sync word (0xFF)
    result["sync_word"] = hex(header[0])
    
    # Byte 2: MPEG version, layer, protection
    byte2 = header[1]
    mpeg_version = (byte2 >> 3) & 0x03
    layer = (byte2 >> 1) & 0x03
    protection = byte2 & 0x01
    
    result["mpeg_version"] = {0: "MPEG 2.5", 2: "MPEG 2", 3: "MPEG 1"}.get(mpeg_version, "Reserved")
    result["layer"] = {1: "Layer III", 2: "Layer II", 3: "Layer I"}.get(layer, "Reserved")
    result["crc_protection"] = protection == 0
    
    # Byte 3: bitrate, sample rate, padding, private
    byte3 = header[2]
    bitrate_index = (byte3 >> 4) & 0x0F
    samplerate_index = (byte3 >> 2) & 0x03
    padding = (byte3 >> 1) & 0x01
    private_bit = byte3 & 0x01
    
    result["padding_bit"] = padding == 1
    result["private_bit"] = private_bit == 1
    
    # Bitrate and sample rate lookup
    bitrate_table = None
    if result["mpeg_version"] == "MPEG 1" and result["layer"] == "Layer III":
        bitrate_table = [None, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, None]
    elif result["mpeg_version"] in ["MPEG 2", "MPEG 2.5"] and result["layer"] == "Layer III":
        bitrate_table = [None, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, None]

    sample_rate_table = None
    if result["mpeg_version"] == "MPEG 1":
        sample_rate_table = [44100, 48000, 32000, None]
    elif result["mpeg_version"] == "MPEG 2":
        sample_rate_table = [22050, 24000, 16000, None]
    elif result["mpeg_version"] == "MPEG 2.5":
        sample_rate_table = [11025, 12000, 8000, None]

    if bitrate_table and bitrate_index < len(bitrate_table):
        result["bitrate_kbps"] = bitrate_table[bitrate_index]
    if sample_rate_table and samplerate_index < len(sample_rate_table):
        result["sample_rate_hz"] = sample_rate_table[samplerate_index]

    # Byte 4: channel mode, mode extension, copyright, original
    byte4 = header[3]
    channel_mode = (byte4 >> 6) & 0x03
    mode_extension = (byte4 >> 4) & 0x03
    copyright = (byte4 >> 3) & 0x01
    original = (byte4 >> 2) & 0x01
    emphasis = byte4 & 0x03
    
    result["channel_mode"] = MP3_CHANNEL_MODES.get(channel_mode, "Unknown")
    result["mode_extension"] = mode_extension
    result["copyrighted"] = copyright == 1
    result["original"] = original == 1
    result["emphasis"] = MP3_EMPHASIS.get(emphasis, "Unknown")
    
    return result


def extract_aac_details(filepath: str, stream: Dict) -> Dict[str, Any]:
    """
    Extract AAC-specific metadata (~40 fields).
    
    Includes:
    - Profile (AAC-LC, HE-AAC, HE-AACv2)
    - SBR (Spectral Band Replication) flag
    - PS (Parametric Stereo) flag
    - Frame length, sample rate
    """
    result = {}
    
    result["codec_name"] = stream.get("codec_name")
    result["codec_long_name"] = stream.get("codec_long_name")
    
    # Profile
    profile_str = stream.get("profile", "").lower()
    result["profile_string"] = profile_str
    
    if "lc" in profile_str:
        result["profile"] = "AAC-LC"
        result["profile_idc"] = 2
        result["has_sbr"] = False
        result["has_ps"] = False
    elif "he-aac" in profile_str or "he_aac" in profile_str:
        if "v2" in profile_str or "ps" in profile_str:
            result["profile"] = "HE-AAC v2 (AAC-LC + SBR + PS)"
            result["profile_idc"] = 29
            result["has_sbr"] = True
            result["has_ps"] = True
        else:
            result["profile"] = "HE-AAC (AAC-LC + SBR)"
            result["profile_idc"] = 5
            result["has_sbr"] = True
            result["has_ps"] = False
    elif "main" in profile_str:
        result["profile"] = "AAC Main"
        result["profile_idc"] = 1
        result["has_sbr"] = False
        result["has_ps"] = False
    else:
        result["profile"] = "Unknown AAC"
        result["has_sbr"] = False
        result["has_ps"] = False
    
    # Sample rate
    result["sample_rate"] = stream.get("sample_rate")
    
    # If SBR is present, output sample rate is doubled
    if result["has_sbr"] and result["sample_rate"]:
        result["sbr_sample_rate"] = int(result["sample_rate"]) * 2
    
    # Channels
    result["channels"] = stream.get("channels")
    result["channel_layout"] = stream.get("channel_layout")
    
    # Bitrate
    bitrate = stream.get("bit_rate")
    if bitrate:
        result["bit_rate_bps"] = int(bitrate)
        result["bit_rate_kbps"] = round(int(bitrate) / 1000, 1)
    
    # Frame size
    frame_size = stream.get("frame_size")
    if frame_size:
        result["frame_size_samples"] = frame_size
    else:
        # AAC-LC default: 1024 samples
        # HE-AAC: 2048 samples (due to SBR)
        result["frame_size_samples"] = 2048 if result["has_sbr"] else 1024
    
    # Duration
    duration = stream.get("duration")
    if duration:
        result["duration_seconds"] = float(duration)
    
    # Bit depth
    bits_per_sample = stream.get("bits_per_sample")
    if bits_per_sample:
        result["bits_per_sample"] = bits_per_sample
    else:
        result["bits_per_sample"] = 16  # Default
    
    # AAC tools
    result["uses_tns"] = True  # Temporal Noise Shaping (always in AAC)
    result["uses_pns"] = True  # Perceptual Noise Substitution
    result["uses_intensity_stereo"] = False  # Would need bitstream analysis
    result["uses_ms_stereo"] = False

    # ADTS header (raw AAC)
    adts_header = _parse_adts_header(_read_file_header(filepath, 7))
    if adts_header:
        result["adts_header"] = adts_header
        if not result.get("sample_rate") and adts_header.get("sample_rate"):
            result["sample_rate"] = adts_header["sample_rate"]
        result["profile_idc"] = adts_header.get("profile_idc", result.get("profile_idc"))
    
    return result


def extract_flac_details(filepath: str) -> Dict[str, Any]:
    """
    Extract FLAC-specific metadata (~50 fields).
    
    Includes:
    - STREAMINFO: min/max block size, frame size, sample rate, channels, bit depth, total samples, MD5
    - Metadata blocks: VORBIS_COMMENT, PICTURE, CUESHEET
    - Compression level estimate
    """
    result = {
        "picture_blocks": [],
        "cuesheet": {},
        "seektable": {},
        "applications": [],
        "padding_bytes": 0,
    }
    
    try:
        with open(filepath, 'rb') as f:
            # Read FLAC signature
            sig = f.read(4)
            if sig != b'fLaC':
                result["error"] = "Not a FLAC file"
                return result
            
            result["signature"] = "fLaC"
            result["is_flac"] = True
            
            # Read metadata blocks
            blocks = []
            while True:
                block_header = f.read(1)
                if len(block_header) < 1:
                    break
                
                is_last = (block_header[0] & 0x80) != 0
                block_type = block_header[0] & 0x7F
                
                size_bytes = f.read(3)
                block_size = (size_bytes[0] << 16) | (size_bytes[1] << 8) | size_bytes[2]
                
                block_data = f.read(block_size)
                
                blocks.append({
                    "type": block_type,
                    "type_name": FLAC_BLOCK_TYPES.get(block_type, f"Unknown ({block_type})"),
                    "size": block_size,
                    "is_last": is_last
                })
                
                # Parse STREAMINFO
                if block_type == 0 and len(block_data) == 34:
                    streaminfo = parse_flac_streaminfo(block_data)
                    result.update(streaminfo)
                
                # Parse VORBIS_COMMENT
                if block_type == 4:
                    comments = parse_flac_vorbis_comment(block_data)
                    result["vorbis_comments"] = comments

                if block_type == 1:
                    result["padding_bytes"] += block_size

                if block_type == 2 and len(block_data) >= 4:
                    app_id = block_data[0:4].decode("latin1", errors="ignore")
                    result["applications"].append({
                        "app_id": app_id,
                        "data_size": block_size - 4,
                    })

                if block_type == 3:
                    seekpoints = []
                    for i in range(0, len(block_data), 18):
                        if i + 18 > len(block_data):
                            break
                        sample_number = struct.unpack(">Q", block_data[i:i + 8])[0]
                        stream_offset = struct.unpack(">Q", block_data[i + 8:i + 16])[0]
                        frame_samples = struct.unpack(">H", block_data[i + 16:i + 18])[0]
                        seekpoints.append({
                            "sample_number": sample_number,
                            "stream_offset": stream_offset,
                            "frame_samples": frame_samples,
                        })
                    result["seektable"] = {"seekpoints": seekpoints, "seekpoint_count": len(seekpoints)}

                if block_type == 5:
                    result["cuesheet"] = _parse_flac_cuesheet(block_data)

                if block_type == 6:
                    picture = _parse_flac_picture_block(block_data)
                    if picture:
                        result["picture_blocks"].append(picture)
                
                if is_last:
                    break
            
            result["metadata_blocks"] = blocks
            result["total_metadata_blocks"] = len(blocks)
            result["metadata_block_types"] = [b["type_name"] for b in blocks]
    
    except Exception as e:
        result["error"] = str(e)[:200]
    
    return result


def parse_flac_streaminfo(data: bytes) -> Dict[str, Any]:
    """Parse FLAC STREAMINFO block."""
    result = {}
    
    # Min block size (16 bits)
    result["min_block_size"] = (data[0] << 8) | data[1]
    
    # Max block size (16 bits)
    result["max_block_size"] = (data[2] << 8) | data[3]
    
    # Min frame size (24 bits)
    result["min_frame_size"] = (data[4] << 16) | (data[5] << 8) | data[6]
    
    # Max frame size (24 bits)
    result["max_frame_size"] = (data[7] << 16) | (data[8] << 8) | data[9]
    
    # Sample rate (20 bits), channels (3 bits), bit depth (5 bits), total samples (36 bits)
    # Bytes 10-17
    sample_rate_high = (data[10] << 12) | (data[11] << 4) | (data[12] >> 4)
    result["sample_rate"] = sample_rate_high
    
    channels = ((data[12] & 0x0E) >> 1) + 1
    result["channels"] = channels
    
    bits_per_sample = (((data[12] & 0x01) << 4) | (data[13] >> 4)) + 1
    result["bits_per_sample"] = bits_per_sample
    
    total_samples = ((data[13] & 0x0F) << 32) | (data[14] << 24) | (data[15] << 16) | (data[16] << 8) | data[17]
    result["total_samples"] = total_samples
    
    # Duration
    if result["sample_rate"] > 0:
        result["duration_seconds"] = total_samples / result["sample_rate"]
    
    # MD5 signature (16 bytes)
    md5_hex = data[18:34].hex()
    result["md5_signature"] = md5_hex
    result["has_md5"] = md5_hex != "00" * 16
    
    return result


def parse_flac_vorbis_comment(data: bytes) -> Dict[str, Any]:
    """Parse FLAC Vorbis comment block."""
    result = {}
    
    try:
        offset = 0
        
        # Vendor string length (32-bit little-endian)
        vendor_len = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        
        # Vendor string
        vendor_string = data[offset:offset+vendor_len].decode('utf-8', errors='ignore')
        result["vendor_string"] = vendor_string
        offset += vendor_len
        
        # User comment list length
        comment_count = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        
        result["comment_count"] = comment_count
        result["comments"] = []
        result["comment_map"] = {}
        
        for i in range(comment_count):
            if offset + 4 > len(data):
                break
            
            comment_len = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            if offset + comment_len > len(data):
                break
            
            comment = data[offset:offset+comment_len].decode('utf-8', errors='ignore')
            result["comments"].append(comment)
            if "=" in comment:
                key, val = comment.split("=", 1)
                key_lower = key.lower()
                if key_lower in result["comment_map"]:
                    if isinstance(result["comment_map"][key_lower], list):
                        result["comment_map"][key_lower].append(val)
                    else:
                        result["comment_map"][key_lower] = [result["comment_map"][key_lower], val]
                else:
                    result["comment_map"][key_lower] = val
            offset += comment_len
    
    except Exception as e:
        pass  # TODO: Consider logging: logger.debug(f'Handled exception: {e}')
    
    return result


def _parse_flac_picture_block(data: bytes) -> Dict[str, Any]:
    if len(data) < 32:
        return {}
    offset = 0
    picture_type = struct.unpack(">I", data[offset:offset + 4])[0]
    offset += 4
    mime_len = struct.unpack(">I", data[offset:offset + 4])[0]
    offset += 4
    mime = data[offset:offset + mime_len].decode("utf-8", errors="ignore")
    offset += mime_len
    desc_len = struct.unpack(">I", data[offset:offset + 4])[0]
    offset += 4
    description = data[offset:offset + desc_len].decode("utf-8", errors="ignore")
    offset += desc_len
    width = struct.unpack(">I", data[offset:offset + 4])[0]
    height = struct.unpack(">I", data[offset + 4:offset + 8])[0]
    depth = struct.unpack(">I", data[offset + 8:offset + 12])[0]
    colors = struct.unpack(">I", data[offset + 12:offset + 16])[0]
    offset += 16
    data_len = struct.unpack(">I", data[offset:offset + 4])[0]
    offset += 4
    picture_data = data[offset:offset + data_len]
    return {
        "picture_type": picture_type,
        "mime_type": mime,
        "description": description,
        "width": width,
        "height": height,
        "color_depth": depth,
        "colors": colors,
        "data_length": data_len,
        "data_md5": hashlib.md5(picture_data).hexdigest() if picture_data else None,
    }


def _parse_flac_cuesheet(data: bytes) -> Dict[str, Any]:
    result: Dict[str, Any] = {"tracks": []}
    if len(data) < 396:
        return result
    catalog = data[0:128].decode("latin1", errors="ignore").rstrip("\x00").strip()
    lead_in = struct.unpack(">Q", data[128:136])[0]
    flags = data[136]
    is_cd = bool(flags & 0x80)
    offset = 137 + 258
    if offset >= len(data):
        return result
    track_count = data[offset]
    offset += 1
    result.update({
        "catalog_number": catalog,
        "lead_in_samples": lead_in,
        "is_cd": is_cd,
        "track_count": track_count,
    })
    for _ in range(track_count):
        if offset + 36 > len(data):
            break
        track_offset = struct.unpack(">Q", data[offset:offset + 8])[0]
        track_number = data[offset + 8]
        isrc = data[offset + 9:offset + 21].decode("latin1", errors="ignore").rstrip("\x00").strip()
        track_flags = data[offset + 21]
        track_type = bool(track_flags & 0x80)
        pre_emphasis = bool(track_flags & 0x40)
        offset += 22 + 13
        if offset >= len(data):
            break
        index_count = data[offset]
        offset += 1
        indices = []
        for _ in range(index_count):
            if offset + 12 > len(data):
                break
            idx_offset = struct.unpack(">Q", data[offset:offset + 8])[0]
            idx_number = data[offset + 8]
            indices.append({
                "offset_samples": idx_offset,
                "index_number": idx_number,
            })
            offset += 12
        result["tracks"].append({
            "offset_samples": track_offset,
            "track_number": track_number,
            "isrc": isrc,
            "track_type": track_type,
            "pre_emphasis": pre_emphasis,
            "index_count": index_count,
            "indices": indices,
        })
    return result


def extract_opus_details(filepath: str, stream: Dict, ogg_packets: Optional[List[bytes]] = None) -> Dict[str, Any]:
    """
    Extract Opus-specific metadata (~30 fields).
    
    Includes:
    - Opus header: version, channel count, pre-skip, input sample rate, output gain
    - Channel mapping family
    """
    result = {}
    
    result["codec_name"] = stream.get("codec_name")
    result["codec_long_name"] = stream.get("codec_long_name")
    
    # Sample rate (Opus always outputs 48 kHz)
    result["opus_output_sample_rate"] = 48000
    result["input_sample_rate"] = stream.get("sample_rate", 48000)
    
    # Channels
    result["channels"] = stream.get("channels")
    result["channel_layout"] = stream.get("channel_layout")
    
    # Bitrate
    bitrate = stream.get("bit_rate")
    if bitrate:
        result["bit_rate_bps"] = int(bitrate)
        result["bit_rate_kbps"] = round(int(bitrate) / 1000, 1)
    
    # Opus header parsing
    if ogg_packets:
        opus_head = _parse_opus_head(ogg_packets[0])
        if opus_head:
            result["opus_header"] = opus_head
            result["pre_skip_samples"] = opus_head.get("pre_skip")
            result["output_gain"] = opus_head.get("output_gain")
            result["channel_mapping_family"] = opus_head.get("channel_mapping_family")
            result["opus_version"] = opus_head.get("version")
            if opus_head.get("channels"):
                result["channels"] = opus_head.get("channels")
        if len(ogg_packets) > 1:
            tags = _parse_vorbis_comments(ogg_packets[1], b"OpusTags")
            if tags:
                result["opus_tags"] = tags
    else:
        result["pre_skip_samples"] = 0
        result["output_gain"] = 0
        result["channel_mapping_family"] = 0
        result["opus_version"] = 1
    
    # Frame size (Opus supports variable frame sizes)
    result["frame_sizes_supported"] = [2.5, 5, 10, 20, 40, 60]  # ms
    result["default_frame_size_ms"] = 20
    
    # Duration
    duration = stream.get("duration")
    if duration:
        result["duration_seconds"] = float(duration)
    
    return result


def extract_vorbis_details(filepath: str, stream: Dict, ogg_packets: Optional[List[bytes]] = None) -> Dict[str, Any]:
    """
    Extract Vorbis-specific metadata (~40 fields).
    
    Includes:
    - Vorbis version
    - Audio channels, sample rate, bitrate (nominal, max, min)
    - Block sizes
    - Vendor string
    """
    result = {}
    
    result["codec_name"] = stream.get("codec_name")
    result["codec_long_name"] = stream.get("codec_long_name")
    
    # Sample rate
    result["sample_rate"] = stream.get("sample_rate")
    
    # Channels
    result["channels"] = stream.get("channels")
    result["channel_layout"] = stream.get("channel_layout")
    
    # Bitrate
    bitrate = stream.get("bit_rate")
    if bitrate:
        result["bitrate_nominal_bps"] = int(bitrate)
        result["bitrate_nominal_kbps"] = round(int(bitrate) / 1000, 1)
    
    # Max/min bitrate (not always present)
    result["bitrate_maximum_bps"] = None
    result["bitrate_minimum_bps"] = None
    
    # Block sizes and vendor (from header)
    if ogg_packets:
        vorbis_id = _parse_vorbis_id_header(ogg_packets[0])
        if vorbis_id:
            result.update(vorbis_id)
        if len(ogg_packets) > 1:
            comments = _parse_vorbis_comments(ogg_packets[1], b"\x03vorbis")
            if comments:
                result["vorbis_comments"] = comments
                result["vendor_string"] = comments.get("vendor_string")
    else:
        result["blocksize_0"] = 64  # Short block (typical)
        result["blocksize_1"] = 2048  # Long block (typical)
        tags = stream.get("tags", {})
        if "vendor" in tags or "encoder" in tags:
            result["vendor_string"] = tags.get("vendor", tags.get("encoder", "Unknown"))
        else:
            result["vendor_string"] = "Xiph.Org libVorbis"
        result["vorbis_version"] = 0
    
    # Duration
    duration = stream.get("duration")
    if duration:
        result["duration_seconds"] = float(duration)
    
    # Quality mode (if VBR)
    tags = stream.get("tags", {})
    if "q" in str(tags.get("encoder", "")).lower():
        result["vbr_quality_mode"] = True
    
    return result


def extract_generic_audio_properties(stream: Dict) -> Dict[str, Any]:
    """Extract generic audio properties applicable to all codecs."""
    result = {}
    
    # Codec
    result["codec_name"] = stream.get("codec_name")
    result["codec_long_name"] = stream.get("codec_long_name")
    result["codec_tag"] = stream.get("codec_tag_string")
    
    # Sample format
    result["sample_fmt"] = stream.get("sample_fmt")
    result["sample_rate"] = stream.get("sample_rate")
    
    # Channels
    result["channels"] = stream.get("channels")
    result["channel_layout"] = stream.get("channel_layout")
    
    # Bit depth
    bits_per_sample = stream.get("bits_per_sample")
    if bits_per_sample:
        result["bits_per_sample"] = bits_per_sample
    
    # Bitrate
    bitrate = stream.get("bit_rate")
    if bitrate:
        result["bit_rate_bps"] = int(bitrate)
        result["bit_rate_kbps"] = round(int(bitrate) / 1000, 1)
        
        # Bits per sample (calculated)
        if result["sample_rate"] and result["channels"]:
            bits_per_sample_calc = int(bitrate) / (int(result["sample_rate"]) * int(result["channels"]))
            result["bits_per_sample_calculated"] = round(bits_per_sample_calc, 2)
    
    # Duration
    duration = stream.get("duration")
    if duration:
        result["duration_seconds"] = float(duration)
    
    # Frame size
    frame_size = stream.get("frame_size")
    if frame_size:
        result["frame_size"] = frame_size
    
    # Stream index
    result["stream_index"] = stream.get("index")
    
    return result


def get_audio_codec_details_field_count() -> int:
    """Return estimated field count for audio codec details module."""
    return 930  # Expanded Phase 2 target
