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


def _frame_v22(frame_id: str, data: bytes) -> bytes:
    size = len(data)
    size_bytes = bytes([(size >> 16) & 0xFF, (size >> 8) & 0xFF, size & 0xFF])
    return frame_id.encode("latin1") + size_bytes + data


def _tag(frames: bytes) -> bytes:
    header = b"ID3" + bytes([4, 0, 0]) + _syncsafe(len(frames))
    return header + frames


def test_id3_comm_uslt_sylt_wxxx():
    comm = b"\x03" + b"eng" + b"desc\x00" + b"comment"
    uslt = b"\x03" + b"eng" + b"lyrics\x00" + b"line1"
    sylt = (
        b"\x03"
        + b"eng"
        + bytes([1, 1])
        + b"sync\x00"
        + b"hello\x00"
        + (1000).to_bytes(4, "big")
        + b"world\x00"
        + (2000).to_bytes(4, "big")
    )
    wxxx = b"\x03" + b"site\x00" + b"https://example.com"
    frames = b"".join([
        _frame("COMM", comm),
        _frame("USLT", uslt),
        _frame("SYLT", sylt),
        _frame("WXXX", wxxx),
    ])
    parsed = acd._parse_id3v2_tag(_tag(frames))
    assert parsed["comments"][0]["description"] == "desc"
    assert parsed["lyrics"][0]["description"] == "lyrics"
    assert parsed["sync_lyrics"][0]["entry_count"] == 2
    assert parsed["url_frames"]["site"] == "https://example.com"


def test_id3_rbuf_rva2_pcst():
    rbuf = bytes([0x00, 0x01, 0x20, 0x01]) + (1234).to_bytes(4, "big")
    rva2 = (
        b"test\x00"
        + bytes([1, 16])
        + (500).to_bytes(2, "big", signed=False)
        + (800).to_bytes(2, "big", signed=False)
    )
    pcst = b"\x01"
    frames = b"".join([
        _frame("RBUF", rbuf),
        _frame("RVA2", rva2),
        _frame("PCST", pcst),
    ])
    parsed = acd._parse_id3v2_tag(_tag(frames))
    assert parsed["buffer"]["buffer_size"] == 0x0120
    assert parsed["relative_volume"][0]["identification"] == "test"
    assert parsed["podcast"]["is_podcast"] is True


def test_id3v22_mapping_pic_frame():
    # ID3v2.2 tag with PIC frame (image format) and TXX custom text
    pic = (
        b"\x03"  # UTF-8
        + b"PNG"
        + b"\x03"
        + b"cover\x00"
        + b"\x89PNGDATA"
    )
    txx = b"\x03" + b"desc\x00" + b"value"
    frames = b"".join([
        _frame_v22("PIC", pic),
        _frame_v22("TXX", txx),
    ])
    header = b"ID3" + bytes([2, 0, 0]) + _syncsafe(len(frames))
    parsed = acd._parse_id3v2_tag(header + frames)
    assert parsed["pictures"][0]["mime"] == "PNG"
    assert parsed["user_text"][0]["description"] == "desc"
