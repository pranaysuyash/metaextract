import struct

from server.extractor.modules import audio_codec_details as acd


def test_parse_aiff_comm_chunk(tmp_path):
    comm_data = (
        struct.pack(">H", 2)
        + struct.pack(">I", 100)
        + struct.pack(">H", 16)
        + b"\x00" * 10
    )
    form_size = 4 + 8 + len(comm_data)
    aiff = b"FORM" + struct.pack(">I", form_size) + b"AIFF"
    aiff += b"COMM" + struct.pack(">I", len(comm_data)) + comm_data

    path = tmp_path / "sample.aiff"
    path.write_bytes(aiff)

    parsed = acd._parse_aiff_chunks(str(path))
    assert parsed["form_type"] == "AIFF"
    assert parsed["comm"]["channels"] == 2
    assert parsed["comm"]["num_frames"] == 100
    assert parsed["comm"]["sample_size_bits"] == 16
