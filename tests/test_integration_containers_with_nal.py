import struct
from pathlib import Path
from server.extractor.modules import container_metadata as cm
from server.extractor.modules import video_codec_details as vcd


def write_mp4_with_mdat(path: Path, mdat_payload: bytes, major_brand: bytes = b'isom'):
    with open(path, 'wb') as f:
        # Write ftyp atom
        compatible = b'isom' + b'avc1'
        ftyp_size = 8 + 8 + len(compatible)
        f.write(struct.pack('>I4s', ftyp_size, b'ftyp'))
        f.write(major_brand)
        f.write(struct.pack('>I', 0))
        f.write(compatible)

        # Write mdat atom with payload
        mdat_size = 8 + len(mdat_payload)
        f.write(struct.pack('>I4s', mdat_size, b'mdat'))
        f.write(mdat_payload)


def find_nal_start(data: bytes) -> int:
    idx = data.find(b'\x00\x00\x00\x01')
    if idx >= 0:
        return idx
    idx = data.find(b'\x00\x00\x01')
    return idx


def test_container_mdat_contains_h264_sps(tmp_path):
    sps_nal = bytes([0x00, 0x00, 0x00, 0x01, 0x67, 100, 0, 42])  # start code + nal (0x67)
    mp4 = tmp_path / 'with_sps.mp4'
    write_mp4_with_mdat(mp4, sps_nal)

    cm_res = cm.extract_container_metadata(str(mp4))
    assert cm_res.get('format_type') == 'MP4/MOV'
    assert cm_res.get('mp4_atoms', {}).get('ftyp')

    # Read file and locate NAL start
    data = mp4.read_bytes()
    idx = find_nal_start(data)
    assert idx >= 0

    # Extract nal starting from found index and parse
    start_len = 4 if data[idx:idx+4] == b'\x00\x00\x00\x01' else 3
    nal = data[idx + start_len: idx + start_len + 8]
    sps_info = vcd.parse_h264_sps(nal)
    assert sps_info.get('profile_idc') == 100
    assert sps_info.get('level_idc') == 42


def test_container_mdat_contains_hevc_vps(tmp_path):
    # Use simple VPS pattern: start code + nal header with type 32 shifted left + payload
    vps_nal = bytes([0x00, 0x00, 0x00, 0x01, (32 << 1), 0x00, 2, 0x80, 120])
    mp4 = tmp_path / 'with_vps.mp4'
    write_mp4_with_mdat(mp4, vps_nal)

    cm_res = cm.extract_container_metadata(str(mp4))
    assert cm_res.get('format_type') == 'MP4/MOV'

    data = mp4.read_bytes()
    idx = find_nal_start(data)
    assert idx >= 0

    start_len = 4 if data[idx:idx+4] == b'\x00\x00\x00\x01' else 3
    nal = data[idx + start_len: idx + start_len + 9]
    vps_info = vcd.parse_hevc_vps(nal)
    assert isinstance(vps_info, dict)
    assert vps_info.get('general_profile_idc') is not None
    assert 'general_level_idc' in vps_info
