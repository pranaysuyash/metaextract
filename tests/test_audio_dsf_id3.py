import struct

from server.extractor.modules import audio_codec_details as acd


def _syncsafe(value: int) -> bytes:
    return bytes([
        (value >> 21) & 0x7F,
        (value >> 14) & 0x7F,
        (value >> 7) & 0x7F,
        value & 0x7F,
    ])


def _id3_tag() -> bytes:
    frame_data = b"\x03" + b"Title"
    frame = b"TIT2" + _syncsafe(len(frame_data)) + b"\x00\x00" + frame_data
    header = b"ID3" + bytes([4, 0, 0]) + _syncsafe(len(frame))
    return header + frame


def test_parse_dsf_with_id3(tmp_path):
    fmt_data = (
        struct.pack("<I", 1)
        + struct.pack("<I", 0)
        + struct.pack("<I", 0)
        + struct.pack("<I", 2)
        + struct.pack("<I", 2822400)
        + struct.pack("<I", 1)
        + struct.pack("<Q", 1000)
        + struct.pack("<I", 4096)
        + struct.pack("<I", 0)
        + b"\x00" * 12
    )
    fmt_size = 52
    id3 = _id3_tag()
    header_size = 12 + 8 + 8 + 4 + 8 + fmt_size
    metadata_offset = header_size
    file_size = header_size + len(id3)
    dsf = (
        b"DSD "
        + struct.pack("<Q", 28)
        + struct.pack("<Q", file_size)
        + struct.pack("<Q", metadata_offset)
        + b"fmt "
        + struct.pack("<Q", fmt_size)
        + fmt_data
        + id3
    )
    path = tmp_path / "sample.dsf"
    path.write_bytes(dsf)

    parsed = acd._parse_dsf_header(str(path))
    assert parsed["id3_present"] is True
    assert parsed["id3"]["text_frames"]["TIT2"] == "Title"
