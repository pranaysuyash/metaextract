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


def test_id3_advanced_frames():
    seek = b"\x00\x00\x04\xd2"
    sign = b"\x01" + b"\xAA\xBB\xCC"
    grid = b"owner\x00" + b"\x02" + b"\x10\x20"
    comr = (
        b"\x03"  # utf-8
        + b"USD5.00\x00"
        + b"20250101"
        + b"https://buy.example\x00"
        + b"\x01"
        + b"Seller\x00"
        + b"Desc\x00"
        + b"image/png\x00"
        + b"\x89PNG"
    )
    equ2 = b"\x01" + b"eq\x00" + b"\x00\x64\x00\x0a"
    mllt = b"\x00\x10" + b"\x00\x00\x20" + b"\x01" + b"\x00\x00"

    aspi = b"\x00\x00\x00\x01" + b"\x00\x00\x00\x02" + b"\x00\x01" + b"\x08" + b"\x05"

    frames = b"".join([
        _frame("SEEK", seek),
        _frame("SIGN", sign),
        _frame("GRID", grid),
        _frame("COMR", comr),
        _frame("EQU2", equ2),
        _frame("MLLT", mllt),
        _frame("ASPI", aspi),
    ])
    parsed = acd._parse_id3v2_tag(_tag(frames))

    assert parsed["seek_offset"] == 1234
    assert parsed["signature"]["group_symbol"] == 1
    assert parsed["group_registration"][0]["owner_id"] == "owner"
    assert parsed["commercial"]["price"] == "USD5.00"
    assert parsed["equalization"][0]["band_count"] == 1
    assert parsed["mpeg_lookup_table"]["frames_between_ref"] == 16
    assert parsed["audio_seek_points"]["point_count"] == 1
