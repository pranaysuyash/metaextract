import io
import struct

from server.extractor.modules import container_metadata as cm


def test_parse_mvhd_atom_version0():
    data = bytearray(100)
    data[0] = 0  # version
    data[1:4] = b"\x00\x00\x00"
    data[4:8] = struct.pack(">I", 10)  # creation
    data[8:12] = struct.pack(">I", 20)  # modification
    data[12:16] = struct.pack(">I", 1000)  # timescale
    data[16:20] = struct.pack(">I", 5000)  # duration
    data[20:24] = struct.pack(">I", 65536)  # rate 1.0
    data[24:26] = struct.pack(">H", 256)  # volume 1.0
    data[96:100] = struct.pack(">I", 3)  # next_track_id

    res = cm.parse_mvhd_atom(io.BytesIO(bytes(data)), len(data))
    assert res["timescale"] == 1000
    assert res["duration"] == 5000
    assert res["preferred_rate"] == 1.0
    assert res["preferred_volume"] == 1.0
    assert res["next_track_id"] == 3


def test_parse_stsd_atom_video_entry():
    entry_size = 86
    entry = bytearray(entry_size)
    entry[0:4] = struct.pack(">I", entry_size)
    entry[4:8] = b"avc1"
    entry[14:16] = struct.pack(">H", 1)
    entry[32:34] = struct.pack(">H", 1920)
    entry[34:36] = struct.pack(">H", 1080)

    stsd = bytearray()
    stsd.extend(b"\x00\x00\x00\x00")
    stsd.extend(struct.pack(">I", 1))
    stsd.extend(entry)

    res = cm.parse_stsd_atom(io.BytesIO(bytes(stsd)), len(stsd))
    assert res["entry_count"] == 1
    assert res["entries"][0]["codec_fourcc"] == "avc1"
    assert res["entries"][0]["width"] == 1920
    assert res["entries"][0]["height"] == 1080
