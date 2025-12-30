from server.extractor.modules import video_codec_details as vcd


def test_write_hevc_vps_fixture_and_parse(tmp_path):
    # Build a fake VPS NAL including 2-byte header then payload: profile=3, tier=0x80, level=122
    nal = bytes([ (32 << 1), 0x00, 3, 0x80, 122 ])
    p = tmp_path / 'vps.bin'
    p.write_bytes(nal)
    b = p.read_bytes()
    info = vcd.parse_hevc_vps(b)
    assert info.get('general_profile_idc') == 3
    assert info.get('general_level_idc') == 122


def test_write_av1_sequence_header_fixture_and_parse(tmp_path):
    # Minimal AV1 sequence header payload (heuristic): first byte profile low bits=1, level=10
    obu = bytes([0x12, 0x00, 0x01, 10])  # includes 0x12 header so parser will strip first two bytes
    p = tmp_path / 'av1_seq.bin'
    p.write_bytes(obu)
    b = p.read_bytes()
    info = vcd.parse_av1_sequence_header(b)
    assert info.get('profile') == 1
    assert info.get('level') == 10
