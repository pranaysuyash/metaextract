from server.extractor.modules import audio_codec_details as acd


def _syncsafe(value: int) -> bytes:
    return bytes([
        (value >> 21) & 0x7F,
        (value >> 14) & 0x7F,
        (value >> 7) & 0x7F,
        value & 0x7F,
    ])


def _frame(frame_id: str, data: bytes) -> bytes:
    size = _syncsafe(len(data))
    return frame_id.encode("latin1") + size + b"\x00\x00" + data


def _tag(frames: bytes) -> bytes:
    header = b"ID3" + bytes([4, 0, 0]) + _syncsafe(len(frames))
    return header + frames


def test_id3_aspi_parsing():
    # data_start=100, data_length=1000, 2 points, 8 bits per point, points 3 and 7
    aspi = (
        b"\x00\x00\x00\x64"
        + b"\x00\x00\x03\xe8"
        + b"\x00\x02"
        + b"\x08"
        + b"\x03\x07"
    )
    frames = _frame("ASPI", aspi)
    parsed = acd._parse_id3v2_tag(_tag(frames))
    seek = parsed["audio_seek_points"]
    assert seek["point_count"] == 2
    assert seek["points_preview"] == [3, 7]
