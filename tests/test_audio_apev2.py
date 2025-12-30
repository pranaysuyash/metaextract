import struct

from server.extractor.modules import audio_codec_details as acd


def test_parse_apev2_cover_art():
    key = "Cover Art (Front)"
    description = b"front"
    data_bytes = b"\x89PNGDATA"
    value = description + b"\x00" + data_bytes
    item_flags = 0x00000002  # binary
    item = (
        struct.pack("<I", len(value))
        + struct.pack("<I", item_flags)
        + key.encode("utf-8")
        + b"\x00"
        + value
    )
    size = 32 + len(item)
    header = (
        b"APETAGEX"
        + struct.pack("<I", 2000)
        + struct.pack("<I", size)
        + struct.pack("<I", 1)
        + struct.pack("<I", 0)
        + b"\x00" * 8
    )
    blob = header + item

    parsed = acd._parse_ape_tag_data(blob)
    cover = parsed["items"][key]
    assert cover["type"] == "binary"
    assert cover["description"] == "front"
    assert cover["data_size"] == len(data_bytes)
