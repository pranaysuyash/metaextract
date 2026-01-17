from __future__ import annotations

import struct
from typing import Any


def _read_exact(f, n: int) -> bytes:
    data = f.read(n)
    if len(data) != n:
        raise EOFError("Unexpected end of file")
    return data


def extract_jp2_container_metadata(filepath: str, max_boxes: int = 4096) -> dict[str, Any] | None:
    """
    JP2/JPEG2000 container scanner (top-level boxes only).

    Supports:
    - JP2 file format (box-based; starts with the JP2 signature box)
    - JPEG2000 codestream (J2K; starts with SOC marker 0xFF4F)
    """
    try:
        with open(filepath, "rb") as f:
            prefix = f.read(16)
            if len(prefix) < 12:
                return None

            # JPEG2000 codestream: SOC marker 0xFF4F.
            if prefix.startswith(b"\xff\x4f"):
                return {"available": True, "format": "JPEG2000", "container": "codestream"}

            # JP2 signature box: length=12, type='jP  ', magic=0x0d0a870a
            if not (
                prefix[0:4] == b"\x00\x00\x00\x0c"
                and prefix[4:8] == b"jP  "
                and prefix[8:12] == b"\x0d\x0a\x87\x0a"
            ):
                return None

            box_counts: dict[str, int] = {"jP  ": 1}
            brands: dict[str, Any] | None = None
            pos = 12
            f.seek(0, 2)
            file_size = f.tell()
            while pos + 8 <= file_size and sum(box_counts.values()) < max_boxes:
                f.seek(pos)
                l = struct.unpack(">I", _read_exact(f, 4))[0]
                t = _read_exact(f, 4).decode("ascii", errors="replace")
                if l < 8:
                    break
                payload_len = l - 8
                if t == "ftyp" and payload_len >= 8:
                    payload = _read_exact(f, min(payload_len, 256))
                    major = payload[0:4].decode("ascii", errors="replace")
                    minor = int.from_bytes(payload[4:8], "big")
                    compat = [
                        payload[i : i + 4].decode("ascii", errors="replace")
                        for i in range(8, len(payload) - (len(payload) % 4), 4)
                    ]
                    brands = {"major_brand": major, "minor_version": minor, "compatible_brands": compat}
                else:
                    f.seek(payload_len, 1)

                box_counts[t] = box_counts.get(t, 0) + 1
                pos += l

        return {"available": True, "format": "JP2", "box_counts": box_counts, "ftyp": brands}
    except Exception:
        return None
