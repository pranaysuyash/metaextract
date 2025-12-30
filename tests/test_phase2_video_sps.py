from server.extractor.modules import video_codec_details as vcd


def test_parse_h264_sps_with_nal_header():
    # SPS NAL with NAL header 0x67 followed by profile_idc=0x64 (100), constraint=0x00, level=0x2A (42)
    nal = bytes([0x67, 0x64, 0x00, 0x2A, 0xFF])
    info = vcd.parse_h264_sps(nal)
    assert info['profile_idc'] == 100
    assert info['constraint_flags'] == 0
    assert info['level_idc'] == 42


def test_parse_h264_sps_with_start_code():
    nal = b'\x00\x00\x00\x01' + bytes([0x67, 0x64, 0x00, 0x2A])
    info = vcd.parse_h264_sps(nal)
    assert info['profile_idc'] == 100
    assert info['level_idc'] == 42


def test_extract_h264_integration_with_extradata():
    stream = {
        'codec_name': 'h264',
        'codec_long_name': 'H.264 / AVC',
        'profile': 100,
        'level': 42,
        'pix_fmt': 'yuv420p',
        'width': 1920,
        'height': 1080,
        'extradata': bytes([0x67, 0x64, 0x00, 0x2A])
    }
    res = vcd.extract_h264_deep_analysis(stream, '/dev/null')
    assert res.get('sps_profile_idc') == 100
    assert res.get('sps_level_idc') == 42
