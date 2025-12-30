import struct

from server.extractor.modules import audio_codec_details as acd


def test_parse_dsf_header(tmp_path):
    chunk_size = 28
    file_size = 200
    metadata_offset = 0
    fmt_size = 52
    fmt_data = (
        struct.pack("<I", 1)  # format_version
        + struct.pack("<I", 0)  # format_id
        + struct.pack("<I", 0)  # channel_type
        + struct.pack("<I", 2)  # channel_num
        + struct.pack("<I", 2822400)  # sampling_frequency
        + struct.pack("<I", 1)  # bits_per_sample
        + struct.pack("<Q", 1000)  # sample_count
        + struct.pack("<I", 4096)  # block_size_per_channel
        + struct.pack("<I", 0)  # reserved
    )
    dsf = (
        b"DSD "
        + struct.pack("<Q", chunk_size)
        + struct.pack("<Q", file_size)
        + struct.pack("<Q", metadata_offset)
        + b"fmt "
        + struct.pack("<Q", fmt_size)
        + fmt_data
    )
    path = tmp_path / "sample.dsf"
    path.write_bytes(dsf)

    parsed = acd._parse_dsf_header(str(path))
    assert parsed["format"] == "DSF"
    assert parsed["channel_num"] == 2
    assert parsed["sampling_frequency"] == 2822400
