from server.extractor.modules import video_codec_details as vcd


def test_parse_hevc_vps_basic():
    # Build a fake VPS NAL including 2-byte header then payload: profile_idc=1, tier (0x80 for high), level=120
    nal = bytes([ (32 << 1), 0x00, 1, 0x80, 120 ])
    info = vcd.parse_hevc_vps(nal)
    assert isinstance(info, dict)
    assert info.get('general_profile_idc') == 1
    assert info.get('general_tier_flag') in (0, 1)
    assert info.get('general_level_idc') == 120


def test_extract_hevc_integration_with_payload():
    stream = {
        'codec_name': 'hevc',
        'codec_long_name': 'HEVC / H.265',
        'profile': 2,
        'level': 120,
        'pix_fmt': 'yuv420p10le',
        'width': 3840,
        'height': 2160,
        'extradata': bytes([ (32 << 1), 0x00, 2, 0x80, 120 ])
    }
    res = vcd.extract_hevc_deep_analysis(stream, '/dev/null')
    # If parser succeeded, it should expose profile/tier/level keys
    assert res.get('profile_idc') == 2 or res.get('profile_name') is not None
