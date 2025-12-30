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


def make_sps_rbsp(profile_idc=100, constraint=0, level_idc=42, seq_id=0, chroma=1, bdl=2, bdc=2):
    header = bytes([profile_idc, constraint, level_idc])
    bits = encode_ue(seq_id) + encode_ue(chroma) + encode_ue(bdl) + encode_ue(bdc)
    return header + bits_to_bytes(bits)


def test_sps_chroma_zero_and_three():
    rbsp0 = make_sps_rbsp(seq_id=1, chroma=0, bdl=0, bdc=0)
    info0 = vcd.parse_h264_sps(rbsp0)
    assert info0.get('seq_parameter_set_id') == 1
    assert info0.get('chroma_format_idc') == 0
    assert info0.get('bit_depth_luma_parsed') == 8
    assert info0.get('bit_depth_chroma_parsed') == 8

    rbsp3 = make_sps_rbsp(seq_id=2, chroma=3, bdl=4, bdc=4)
    info3 = vcd.parse_h264_sps(rbsp3)
    assert info3.get('seq_parameter_set_id') == 2
    assert info3.get('chroma_format_idc') == 3
    assert info3.get('bit_depth_luma_parsed') == 12
    assert info3.get('bit_depth_chroma_parsed') == 12


def test_sps_large_ue_values():
    # Large UE (e.g., 5000) to ensure read_ue handles multi-byte values
    rbsp = make_sps_rbsp(seq_id=5000, chroma=1, bdl=2, bdc=2)
    info = vcd.parse_h264_sps(rbsp)
    assert info.get('seq_parameter_set_id') == 5000


def test_sps_various_bit_depths():
    for b in range(0, 6):  # test increasing bit depths
        seq = b
        rbsp = make_sps_rbsp(seq_id=0, chroma=1, bdl=b, bdc=b)
        info = vcd.parse_h264_sps(rbsp)
        expected = 8 + b
        assert info.get('bit_depth_luma_parsed') == expected
        assert info.get('bit_depth_chroma_parsed') == expected
