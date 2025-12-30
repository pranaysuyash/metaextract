from server.extractor.modules import video_codec_details as vcd


def test_parse_av1_sequence_header_basic():
    # Create a minimal mocked OBU with header 0x12 then payload [profile=1, level=2]
    obu = bytes([0x12, 0x00, 0x01, 0x02])
    info = vcd.parse_av1_sequence_header(obu)
    assert info.get('profile') in (0, 1, 2)
    assert info.get('level') == 2


def test_integration_extract_av1():
    stream = {
        'codec_name': 'av1',
        'codec_long_name': 'AV1',
        'profile': 0,
        'level': 2,
        'pix_fmt': 'yuv420p10le',
        'extradata': bytes([0x12, 0x00, 0x02, 0x03])
    }
    res = vcd.extract_av1_deep_analysis(stream, '/dev/null')
    assert isinstance(res, dict)
    assert 'profile' in res or 'frame_rate_fps' in res
