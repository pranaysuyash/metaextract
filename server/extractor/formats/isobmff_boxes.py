from __future__ import annotations

import hashlib
import struct
from typing import Any


def _read_exact(f, n: int) -> bytes:
    data = f.read(n)
    if len(data) != n:
        raise EOFError("Unexpected end of file")
    return data


def extract_isobmff_box_metadata(filepath: str, max_boxes: int = 5000) -> dict[str, Any] | None:
    """
    ISO BMFF (ISOBMFF) box scanner for HEIC/HEIF/AVIF (and other BMFF-based images).

    This does not decode images; it only walks top-level boxes and records:
    - ftyp brands
    - presence of `meta`, `mdat`, `moov`, `iloc`, `iinf`, `Exif`
    """
    try:
        with open(filepath, "rb") as f:
            file_size = f.seek(0, 2)
            f.seek(0)

            brands: dict[str, Any] | None = None
            box_counts: dict[str, int] = {}
            found: set[str] = set()
            exif_box: dict[str, Any] | None = None

            pos = 0
            for _ in range(max_boxes):
                if pos + 8 > file_size:
                    break
                f.seek(pos)
                size = struct.unpack(">I", _read_exact(f, 4))[0]
                box_type = _read_exact(f, 4).decode("ascii", errors="replace")
                header_size = 8
                if size == 1:
                    size = struct.unpack(">Q", _read_exact(f, 8))[0]
                    header_size = 16
                if size < header_size:
                    break

                box_counts[box_type] = box_counts.get(box_type, 0) + 1
                found.add(box_type)

                # ftyp
                if box_type == "ftyp" and size >= header_size + 8:
                    payload = _read_exact(f, min(int(size - header_size), 512))
                    major = payload[0:4].decode("ascii", errors="replace")
                    minor = int.from_bytes(payload[4:8], "big")
                    compat = [
                        payload[i : i + 4].decode("ascii", errors="replace")
                        for i in range(8, len(payload) - (len(payload) % 4), 4)
                    ]
                    brands = {"major_brand": major, "minor_version": minor, "compatible_brands": compat}

                if box_type.lower() == "exif":
                    f.seek(pos + header_size)
                    payload = _read_exact(f, min(int(size - header_size), 4096))
                    exif_box = {
                        "size_bytes": int(size - header_size),
                        "sha256_prefix": hashlib.sha256(payload).hexdigest(),
                    }

                pos += int(size)

            return {
                "available": True,
                "container": "isobmff",
                "ftyp": brands,
                "box_counts": box_counts,
                "found_boxes": sorted(found),
                "exif_box": exif_box,
            }
    except Exception:
        return None

