import struct

from server.extractor.modules import audio_codec_details as acd


def _chunk(chunk_id: bytes, payload: bytes) -> bytes:
    size = struct.pack(">Q", len(payload))
    return chunk_id + size + payload + (b"\x00" if len(payload) % 2 == 1 else b"")


def test_parse_dsdiff_header(tmp_path):
    fver = _chunk(b"FVER", struct.pack(">I", 0x01050000))
    fs = _chunk(b"FS  ", struct.pack(">I", 2822400))
    chnl = _chunk(b"CHNL", struct.pack(">H", 2) + b"SLFT" + b"SRGT")
    cmpr = _chunk(b"CMPR", b"DSD " + bytes([3]) + b"raw")
    prop_payload = b"SND " + fs + chnl + cmpr
    prop = _chunk(b"PROP", prop_payload)
    form_payload = b"DSD " + fver + prop
    form = b"FRM8" + struct.pack(">Q", len(form_payload)) + form_payload

    path = tmp_path / "sample.dff"
    path.write_bytes(form)

    parsed = acd._parse_dsdiff_header(str(path))
    assert parsed["format"] == "DSDIFF"
    assert parsed["sample_rate"] == 2822400
    assert parsed["channel_count"] == 2
    assert parsed["compression_id"] == "DSD "
