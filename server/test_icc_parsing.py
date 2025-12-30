#!/usr/bin/env python3
"""Sanity checks for ICC header and tag parsing."""

import struct

from extractor.modules.icc_profile import (
    _parse_icc_header,
    _parse_icc_tag_table,
    _parse_icc_tag_details,
)


def build_icc_bytes() -> bytes:
    text = "Test Profile"
    ascii_len = len(text) + 1
    tag_payload = bytearray()
    tag_payload.extend(b"desc")
    tag_payload.extend(b"\x00\x00\x00\x00")
    tag_payload.extend(struct.pack(">I", ascii_len))
    tag_payload.extend(text.encode("ascii"))
    tag_payload.extend(b"\x00")
    while len(tag_payload) % 4 != 0:
        tag_payload.extend(b"\x00")

    tag_offset = 128 + 4 + 12
    tag_size = len(tag_payload)
    total_size = tag_offset + tag_size

    data = bytearray(total_size)
    data[0:4] = struct.pack(">I", total_size)
    data[4:8] = b"APPL"
    data[8:12] = bytes([4, 0x20, 0x00, 0x00])
    data[12:16] = b"mntr"
    data[16:20] = b"RGB "
    data[20:24] = b"XYZ "
    data[24:36] = struct.pack(">6H", 2025, 1, 1, 12, 0, 0)
    data[40:44] = b"MSFT"
    data[48:52] = b"APPL"
    data[52:56] = b"TEST"
    data[80:84] = b"TEST"

    data[128:132] = struct.pack(">I", 1)
    data[132:136] = b"desc"
    data[136:140] = struct.pack(">I", tag_offset)
    data[140:144] = struct.pack(">I", tag_size)

    data[tag_offset:tag_offset + tag_size] = tag_payload

    return bytes(data)


def run() -> None:
    icc_bytes = build_icc_bytes()
    header = _parse_icc_header(icc_bytes)
    tag_table = _parse_icc_tag_table(icc_bytes)
    tag_details = _parse_icc_tag_details(icc_bytes, tag_table)

    assert header["profile_size"] == len(icc_bytes)
    assert header["device_class"] == "mntr"
    assert header["color_space"] == "RGB"
    assert tag_table["tag_count"] == 1
    assert tag_details["desc"]["type"] == "desc"
    assert tag_details["desc"]["description"] == "Test Profile"

    print("✅ ICC parsing checks passed.")


if __name__ == "__main__":
    run()
