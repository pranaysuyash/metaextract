import tempfile
from server.extractor.modules import container_metadata as cm
from pathlib import Path
import struct


def make_ftyp_file(path: Path, major_brand=b'isom', minor_version=0, compatible_brands=(b'isom', b'avc1')):
    with open(path, 'wb') as f:
        # size (4) + type (4) + major_brand (4) + minor_version (4) + compatible_brands...
        compatible = b''.join(compatible_brands)
        size = 8 + 8 + len(compatible)
        f.write(struct.pack('>I4s', size, b'ftyp'))
        f.write(major_brand)
        f.write(struct.pack('>I', minor_version))
        f.write(compatible)


def test_parse_mp4_atoms_ftyp(tmp_path):
    p = tmp_path / 'test.mp4'
    make_ftyp_file(p)
    res = cm.parse_mp4_atoms(str(p))
    assert 'ftyp' in res
    assert res['ftyp'].get('major_brand') in ('isom', 'iso6', 'iso2', '3gp4') or res['ftyp'].get('major_brand') == 'isom'
    assert res['total_atoms'] >= 1


def test_extract_container_metadata_mp4(tmp_path):
    p = tmp_path / 'test2.mp4'
    make_ftyp_file(p, major_brand=b'mp42')
    res = cm.extract_container_metadata(str(p))
    assert res['format_type'] == 'MP4/MOV'
    assert res['mp4_atoms']['ftyp']['major_brand'] == 'mp42'
