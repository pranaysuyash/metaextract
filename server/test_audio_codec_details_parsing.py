#!/usr/bin/env python3
"""Sanity checks for audio codec detail parsers."""

import struct

from extractor.modules.audio_codec_details import (
    _parse_id3v2_tag,
    _parse_id3v1_tag,
    _parse_adts_header,
    _parse_bext_chunk,
    _parse_ape_tag_data,
)


def _syncsafe(size: int) -> bytes:
    return bytes([
        (size >> 21) & 0x7F,
        (size >> 14) & 0x7F,
        (size >> 7) & 0x7F,
        size & 0x7F,
    ])


def build_id3v2_tag() -> bytes:
    frame_data = b"\x03" + b"Test Song"
    frame_header = b"TIT2" + struct.pack(">I", len(frame_data)) + b"\x00\x00"
    tag_body = frame_header + frame_data
    header = b"ID3" + bytes([3, 0, 0]) + _syncsafe(len(tag_body))
    return header + tag_body


def build_id3v1_tag() -> bytes:
    tag = bytearray(128)
    tag[0:3] = b"TAG"
    tag[3:33] = b"Title".ljust(30, b"\x00")
    tag[33:63] = b"Artist".ljust(30, b"\x00")
    tag[63:93] = b"Album".ljust(30, b"\x00")
    tag[93:97] = b"1999"
    tag[97:125] = b"Comment".ljust(28, b"\x00")
    tag[125] = 0
    tag[126] = 7
    tag[127] = 13
    return bytes(tag)


def build_bext_chunk() -> bytes:
    data = bytearray(602)
    data[0:256] = b"Desc".ljust(256, b"\x00")
    data[256:288] = b"Originator".ljust(32, b"\x00")
    data[288:320] = b"Ref".ljust(32, b"\x00")
    data[320:330] = b"20240101"
    data[330:338] = b"12000000"
    data[338:346] = struct.pack("<Q", 123456)
    data[346:348] = struct.pack("<H", 1)
    data[348:412] = b"\x01" * 64
    data[412:422] = struct.pack("<5H", 23, 5, 10, 15, 20)
    data[422:] = b"coding-history"
    return bytes(data)


def build_ape_tag() -> bytes:
    key = b"REPLAYGAIN_TRACK_GAIN"
    value = b"+1.23 dB"
    item = struct.pack("<I", len(value)) + struct.pack("<I", 0) + key + b"\x00" + value
    size = 32 + len(item)
    header = b"APETAGEX" + struct.pack("<I", 2000) + struct.pack("<I", size)
    header += struct.pack("<I", 1) + struct.pack("<I", 0) + b"\x00" * 8
    return header + item


def run() -> None:
    id3v2 = _parse_id3v2_tag(build_id3v2_tag())
    assert id3v2["id3v2_present"] is True
    assert id3v2["text_frames"].get("TIT2") == "Test Song"

    id3v1 = _parse_id3v1_tag(build_id3v1_tag())
    assert id3v1["id3v1_present"] is True
    assert id3v1["title"] == "Title"
    assert id3v1["track"] == 7

    adts = _parse_adts_header(b"\xFF\xF1\x50\x80\x00\x1F\xFC")
    assert adts["sample_rate"] == 44100
    assert adts["channel_config"] == 2
    assert adts["profile_idc"] == 2

    bext = _parse_bext_chunk(build_bext_chunk())
    assert bext["description"] == "Desc"
    assert bext["originator"] == "Originator"
    assert bext["time_reference"] == 123456

    ape = _parse_ape_tag_data(build_ape_tag())
    assert ape["ape_present"] is True
    assert "REPLAYGAIN_TRACK_GAIN" in ape["items"]

    print("Audio codec parsing checks passed.")


if __name__ == "__main__":
    run()
