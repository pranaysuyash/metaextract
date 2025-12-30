import struct

from server.extractor.modules import audio_codec_details as acd


def test_parse_rf64_ds64_chunk(tmp_path):
    ds64_payload = (
        struct.pack("<Q", 1000)
        + struct.pack("<Q", 900)
        + struct.pack("<Q", 100)
        + struct.pack("<I", 0)
    )
    ds64_chunk = b"ds64" + struct.pack("<I", len(ds64_payload)) + ds64_payload
    fmt_payload = struct.pack("<HHIIHH", 1, 2, 44100, 176400, 4, 16)
    fmt_chunk = b"fmt " + struct.pack("<I", len(fmt_payload)) + fmt_payload
    data_chunk = b"data" + struct.pack("<I", 0)
    header = b"RF64" + struct.pack("<I", 0) + b"WAVE"
    rf64 = header + ds64_chunk + fmt_chunk + data_chunk

    path = tmp_path / "sample.rf64"
    path.write_bytes(rf64)

    parsed = acd._parse_riff_chunks(str(path))
    assert parsed["riff_type"] == "WAVE"
    assert parsed["ds64"]["riff_size"] == 1000
    assert parsed["ds64"]["data_size"] == 900
