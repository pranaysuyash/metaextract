import struct

from server.extractor.modules import audio_codec_details as acd


def test_parse_axml_chunk(tmp_path):
    xml_payload = b"<?xml version='1.0'?><root attr='1'/>"
    axml_chunk = b"axml" + struct.pack("<I", len(xml_payload)) + xml_payload
    riff_size = 4 + len(axml_chunk)
    wave = b"RIFF" + struct.pack("<I", riff_size) + b"WAVE" + axml_chunk

    path = tmp_path / "sample.wav"
    path.write_bytes(wave)

    parsed = acd._parse_riff_chunks(str(path))
    assert parsed["axml"]["root_tag"] == "root"
