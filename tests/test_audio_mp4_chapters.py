import struct

from server.extractor.modules import audio_codec_details as acd


def _atom(atom_type: bytes, payload: bytes) -> bytes:
    size = 8 + len(payload)
    return struct.pack(">I", size) + atom_type + payload


def test_parse_mp4_chpl(tmp_path):
    chapter_payload = b"\x00\x00\x00\x00" + bytes([1]) + struct.pack(">Q", 1000) + bytes([4]) + b"Test"
    chpl = _atom(b"chpl", chapter_payload)
    meta = _atom(b"meta", b"\x00\x00\x00\x00" + chpl)
    udta = _atom(b"udta", meta)
    moov = _atom(b"moov", udta)

    path = tmp_path / "sample.m4a"
    path.write_bytes(moov)

    parsed = acd._parse_mp4_ilst(str(path))
    assert parsed["chapters"][0]["title"] == "Test"
