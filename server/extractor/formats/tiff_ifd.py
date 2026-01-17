from __future__ import annotations

import hashlib
import struct
from typing import Any


def _read_exact(f, n: int) -> bytes:
    data = f.read(n)
    if len(data) != n:
        raise EOFError("Unexpected end of file")
    return data


def extract_tiff_container_metadata(filepath: str, max_ifds: int = 32) -> dict[str, Any] | None:
    """
    Lightweight TIFF/BigTIFF container parser.

    Reports:
    - Endianness and BigTIFF flag
    - IFD count (best-effort)
    - Tag count per IFD (no value decoding)
    """
    try:
        with open(filepath, "rb") as f:
            endian = _read_exact(f, 2)
            if endian == b"II":
                bo = "<"
            elif endian == b"MM":
                bo = ">"
            else:
                return None

            magic = struct.unpack(bo + "H", _read_exact(f, 2))[0]
            is_bigtiff = magic == 43
            if not (magic == 42 or is_bigtiff):
                return None

            if is_bigtiff:
                offset_size = struct.unpack(bo + "H", _read_exact(f, 2))[0]
                _ = _read_exact(f, 2)  # reserved
                if offset_size != 8:
                    return None
                ifd_offset = struct.unpack(bo + "Q", _read_exact(f, 8))[0]
            else:
                ifd_offset = struct.unpack(bo + "I", _read_exact(f, 4))[0]

            ifd_summaries: list[dict[str, Any]] = []
            seen_offsets: set[int] = set()
            for _ in range(max_ifds):
                if ifd_offset == 0 or ifd_offset in seen_offsets:
                    break
                seen_offsets.add(ifd_offset)
                f.seek(ifd_offset)

                if is_bigtiff:
                    entry_count = struct.unpack(bo + "Q", _read_exact(f, 8))[0]
                    entry_size = 20
                else:
                    entry_count = struct.unpack(bo + "H", _read_exact(f, 2))[0]
                    entry_size = 12

                # Skip entries (we only count them)
                f.seek(entry_size * entry_count, 1)

                if is_bigtiff:
                    ifd_offset = struct.unpack(bo + "Q", _read_exact(f, 8))[0]
                else:
                    ifd_offset = struct.unpack(bo + "I", _read_exact(f, 4))[0]

                ifd_summaries.append({"entry_count": int(entry_count)})

        return {
            "available": True,
            "format": "TIFF",
            "endianness": "little" if bo == "<" else "big",
            "is_bigtiff": is_bigtiff,
            "ifd_count": len(ifd_summaries),
            "ifds": ifd_summaries,
            "header_sha256": hashlib.sha256(open(filepath, "rb").read(64)).hexdigest(),
        }
    except Exception:
        return None

