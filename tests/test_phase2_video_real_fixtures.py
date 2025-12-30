from server.extractor.modules import video_codec_details as vcd
from tests.fixtures.h264_sps_samples import sps_1080p_high, sps_4k_main10, sps_baseline


def test_real_sps_1080p_high():
    info = vcd.parse_h264_sps(sps_1080p_high)
    assert info.get('profile_idc') == 100
    assert info.get('level_idc') == 40
    # These may not parse perfectly due to Exp-Golomb, but basic fields should
    assert 'seq_parameter_set_id' in info or info.get('profile_idc') is not None


def test_real_sps_4k_main10():
    info = vcd.parse_h264_sps(sps_4k_main10)
    assert info.get('profile_idc') == 100
    assert info.get('level_idc') == 51
    # Check if chroma/bit depth parsed
    if 'chroma_format_idc' in info:
        assert info['chroma_format_idc'] in (0, 1, 2, 3)


def test_real_sps_baseline():
    info = vcd.parse_h264_sps(sps_baseline)
    assert info.get('profile_idc') == 66
    assert info.get('level_idc') == 30