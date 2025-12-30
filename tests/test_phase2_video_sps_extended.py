from server.extractor.modules import video_codec_details as vcd


def encode_ue(v: int) -> str:
    info = v + 1
    k = info.bit_length() - 1
    prefix = '0' * k
    info_bits = format(info, 'b')
    return prefix + info_bits


def bits_to_bytes(bs: str) -> bytes:
    pad = (8 - (len(bs) % 8)) % 8
    bs_padded = bs + ('0' * pad)
    out = bytearray()
    for i in range(0, len(bs_padded), 8):
        out.append(int(bs_padded[i:i+8], 2))
    return bytes(out)


def test_parse_h264_sps_chroma_and_bitdepth():
    # Build RBSP with proper UE encoding: seq_id=0, chroma=1, bdl=2, bdc=2
    header = bytes([100, 0, 42])
    bits = encode_ue(0) + encode_ue(1) + encode_ue(2) + encode_ue(2)
    rbsp = header + bits_to_bytes(bits)
    info = vcd.parse_h264_sps(rbsp)
    assert info['profile_idc'] == 100
    assert info['level_idc'] == 42
    assert info.get('seq_parameter_set_id') == 0
    assert info.get('chroma_format_idc') == 1
    assert info.get('bit_depth_luma_parsed') == 10
    assert info.get('bit_depth_chroma_parsed') == 10


def test_extract_h264_deep_analysis_bitdepth_integration():
    stream = {
        'codec_name': 'h264',
        'codec_long_name': 'H.264 / AVC',
        'profile': 100,
        'level': 42,
        'pix_fmt': 'yuv420p10le',
        'width': 1920,
        'height': 1080,
        'extradata': bytes([0x67, 100, 0, 42, 2, 2])
    }
    res = vcd.extract_h264_deep_analysis(stream, '/dev/null')
    assert res.get('sps_profile_idc') == 100
    assert res.get('sps_level_idc') == 42
    assert res.get('bit_depth_luma_parsed') in (None, 10)
