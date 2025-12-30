from server.extractor.modules import video_codec_details as vcd


def encode_ue(v: int) -> str:
    # Exp-Golomb UE coding as bits string
    info = v + 1
    k = info.bit_length() - 1
    prefix = '0' * k
    info_bits = format(info, 'b')
    return prefix + info_bits


def bits_to_bytes(bs: str) -> bytes:
    # Pad to byte
    pad = (8 - (len(bs) % 8)) % 8
    bs_padded = bs + ('0' * pad)
    out = bytearray()
    for i in range(0, len(bs_padded), 8):
        out.append(int(bs_padded[i:i+8], 2))
    return bytes(out)


def make_sps_rbsp(profile_idc=100, constraint=0, level_idc=42, seq_id=0, chroma=1, bdl=2, bdc=2):
    # Build header bytes
    header = bytes([profile_idc, constraint, level_idc])
    # Append ue(seq_id), ue(chroma), ue(bit_depth_luma_minus8), ue(bit_depth_chroma_minus8)
    bits = encode_ue(seq_id) + encode_ue(chroma) + encode_ue(bdl) + encode_ue(bdc)
    return header + bits_to_bytes(bits)


def test_parse_h264_sps_exp_golomb():
    rbsp = make_sps_rbsp(profile_idc=100, constraint=0, level_idc=42, seq_id=0, chroma=1, bdl=2, bdc=2)
    info = vcd.parse_h264_sps(rbsp)
    assert info.get('profile_idc') == 100
    assert info.get('seq_parameter_set_id') == 0
    assert info.get('chroma_format_idc') == 1
    assert info.get('bit_depth_luma_parsed') == 10
    assert info.get('bit_depth_chroma_parsed') == 10
