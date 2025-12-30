import struct

from server.extractor.modules import audio_codec_details as acd


def _subchunk(chunk_id: bytes, payload: bytes) -> bytes:
    size = struct.pack("<I", len(payload))
    pad = b"\x00" if len(payload) % 2 == 1 else b""
    return chunk_id + size + payload + pad


def test_parse_adtl_list(tmp_path):
    labl_payload = struct.pack("<I", 1) + b"intro\x00"
    ltxt_payload = (
        struct.pack("<I", 1)
        + struct.pack("<I", 44100)
        + b"capt"
        + struct.pack("<H", 1)
        + struct.pack("<H", 1)
        + struct.pack("<H", 1)
        + struct.pack("<H", 1252)
        + b"segment\x00"
    )
    adtl_data = _subchunk(b"labl", labl_payload) + _subchunk(b"ltxt", ltxt_payload)
    list_payload = b"adtl" + adtl_data
    list_chunk = b"LIST" + struct.pack("<I", len(list_payload)) + list_payload

    riff_size = 4 + len(list_chunk)
    wave = b"RIFF" + struct.pack("<I", riff_size) + b"WAVE" + list_chunk

    path = tmp_path / "sample.wav"
    path.write_bytes(wave)

    parsed = acd._parse_riff_chunks(str(path))
    assert parsed["adtl"]["labels"][0]["text"] == "intro"
    assert parsed["adtl"]["texts"][0]["text"] == "segment"
