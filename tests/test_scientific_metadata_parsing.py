import struct

from server.extractor.modules import scientific_medical as sm


def test_parse_geokey_directory_basic():
    key_dir = [1, 1, 0, 1, 1024, 0, 1, 2]
    parsed = sm._parse_geokey_directory(key_dir)
    assert parsed["key_count"] == 1
    assert parsed["keys"][0]["key_id"] == 1024
    assert parsed["keys"][0]["value"] == 2


def test_parse_las_header_basic(tmp_path):
    header = bytearray()
    header.extend(b"LASF")
    header.extend(struct.pack("<H", 1))  # file source id
    header.extend(struct.pack("<H", 0))  # global encoding
    header.extend(b"\x00" * 16)  # project id
    header.extend(struct.pack("<B", 1))  # version major
    header.extend(struct.pack("<B", 2))  # version minor
    header.extend(b"SYS".ljust(32, b"\x00"))
    header.extend(b"GEN".ljust(32, b"\x00"))
    header.extend(struct.pack("<H", 1))  # day
    header.extend(struct.pack("<H", 2024))  # year
    header.extend(struct.pack("<H", 227))  # header size
    header.extend(struct.pack("<I", 227))  # offset to point data
    header.extend(struct.pack("<I", 0))  # num vlrs
    header.extend(struct.pack("<B", 1))  # point data format
    header.extend(struct.pack("<H", 28))  # point data record length
    header.extend(struct.pack("<I", 100))  # num point records
    header.extend(struct.pack("<5I", 100, 0, 0, 0, 0))
    header.extend(struct.pack("<3d", 0.01, 0.01, 0.01))
    header.extend(struct.pack("<3d", 0.0, 0.0, 0.0))
    header.extend(struct.pack("<2d", 1.0, 0.0))
    header.extend(struct.pack("<2d", 2.0, 0.0))
    header.extend(struct.pack("<2d", 3.0, 0.0))

    las_path = tmp_path / "sample.las"
    las_path.write_bytes(bytes(header))

    parsed = sm._parse_las_header(str(las_path))
    assert parsed["signature"] == "LASF"
    assert parsed["version_major"] == 1
    assert parsed["version_minor"] == 2
    assert parsed["num_point_records"] == 100
