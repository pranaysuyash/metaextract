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

MP4_CONTAINER_ATOMS = {
    b"moov", b"trak", b"mdia", b"minf", b"stbl", b"udta", b"meta", b"ilst"
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
        "pictures": [],
        "user_text": [],
        "chapters": [],
        "table_of_contents": [],
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
            text = _decode_id3_text(frame_data[1:], encoding)
            parts = _split_id3_strings(text)
            if parts:
                result["url_frames"][parts[0]] = parts[1] if len(parts) > 1 else ""
        elif frame_id_str == "COMM":
            if len(frame_data) >= 4:
                encoding = frame_data[0]
                language = frame_data[1:4].decode("latin1", errors="ignore")
                comment_text = _decode_id3_text(frame_data[4:], encoding)
                result["comments"].append({"language": language, "text": comment_text})
        elif frame_id_str == "USLT":
            if len(frame_data) >= 4:
                encoding = frame_data[0]
                language = frame_data[1:4].decode("latin1", errors="ignore")
                lyric_text = _decode_id3_text(frame_data[4:], encoding)
                result["lyrics"].append({"language": language, "text": lyric_text})
        elif frame_id_str == "APIC":
            if len(frame_data) >= 4:
                encoding = frame_data[0]
                rest = frame_data[1:]
                mime_end = rest.find(b"\x00")
                mime = rest[:mime_end].decode("latin1", errors="ignore") if mime_end >= 0 else ""
                after_mime = rest[mime_end + 1:] if mime_end >= 0 else b""
                picture_type = after_mime[0] if after_mime else 0
                desc_text = _decode_id3_text(after_mime[1:], encoding)
                desc_parts = _split_id3_strings(desc_text)
                data_offset = 1 + (len(desc_parts[0]) + 1 if desc_parts else 0)
                picture_data_len = max(0, len(after_mime) - data_offset)
                result["pictures"].append({
                    "mime": mime,
                    "type": picture_type,
                    "description": desc_parts[0] if desc_parts else "",
                    "size_bytes": picture_data_len,
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
        elif frame_id_str == "UFID":
            owner_end = frame_data.find(b"\x00")
            owner = frame_data[:owner_end].decode("latin1", errors="ignore") if owner_end >= 0 else ""
            identifier = frame_data[owner_end + 1:] if owner_end >= 0 else b""
            result["other_frames"]["UFID"] = {
                "owner": owner,
                "identifier_length": len(identifier),
            }
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
                result["table_of_contents"].append({
                    "element_id": element_id,
                    "flags": flags_byte,
                    "entry_count": entry_count,
                })
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
        is_text = (item_flags & 0x00000006) == 0
        result["items"][key] = {
            "value": value.decode("utf-8", errors="ignore") if is_text else value.hex(),
            "is_text": is_text,
            "flags": item_flags,
        }
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
        "fmt": {},
        "data": {},
        "info": {},
        "cue_points": [],
        "sampler": {},
        "bext": {},
        "ixml": {},
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
                    else:
                        f.seek(list_data_size, 1)
                elif chunk_id == b"bext":
                    bext_data = f.read(chunk_size)
                    result["bext"] = _parse_bext_chunk(bext_data)
                elif chunk_id == b"iXML":
                    ixml_data = f.read(chunk_size)
                    result["ixml"] = _parse_ixml_chunk(ixml_data)
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
    result: Dict[str, Any] = {"tags": {}, "raw_tags": {}, "tag_count": 0}
    ilst_location = _find_mp4_ilst(filepath)
    if not ilst_location:
        return result
    start, size = ilst_location
    try:
        with open(filepath, "rb") as f:
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
    return 520  # Expanded Phase 2 target
