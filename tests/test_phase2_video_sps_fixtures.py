import os
from server.extractor.modules import video_codec_details as vcd

FIX_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


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


def test_write_and_read_sps_fixtures(tmp_path):
    # Create two fixtures
    f1 = tmp_path / 'fixtures' / 'sps_chroma0_bd8.bin'
    f1.parent.mkdir(parents=True, exist_ok=True)
    rbsp0 = make_sps_rbsp(seq_id=7, chroma=0, bdl=0, bdc=0)
    f1.write_bytes(rbsp0)

    f2 = tmp_path / 'fixtures' / 'sps_chroma3_bd12.bin'
    rbsp3 = make_sps_rbsp(seq_id=9, chroma=3, bdl=4, bdc=4)
    f2.write_bytes(rbsp3)

    # Read and parse
    b0 = f1.read_bytes()
    info0 = vcd.parse_h264_sps(b0)
    assert info0.get('seq_parameter_set_id') == 7
    assert info0.get('chroma_format_idc') == 0

    b3 = f2.read_bytes()
    info3 = vcd.parse_h264_sps(b3)
    assert info3.get('seq_parameter_set_id') == 9
    assert info3.get('chroma_format_idc') == 3
    assert info3.get('bit_depth_luma_parsed') == 12
