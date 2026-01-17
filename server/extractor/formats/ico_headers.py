from __future__ import annotations

import struct
from typing import Any


def _read_exact(f, n: int) -> bytes:
    data = f.read(n)
    if len(data) != n:
        raise EOFError("Unexpected end of file")
    return data


def extract_ico_container_metadata(filepath: str) -> dict[str, Any] | None:
    """
    Parse ICO/CUR header (ICONDIR) and directory entries (ICONDIRENTRY).
    """
    try:
        with open(filepath, "rb") as f:
            header = _read_exact(f, 6)
            reserved, icon_type, count = struct.unpack("<HHH", header)
            if reserved != 0 or icon_type not in (1, 2) or count == 0:
                return None

            entries: list[dict[str, Any]] = []
            for _ in range(min(count, 256)):
                b = _read_exact(f, 16)
                width, height, color_count, reserved2, planes, bit_count, size, offset = struct.unpack(
                    "<BBBBHHII", b
                )
                entries.append(
                    {
                        "width": 256 if width == 0 else width,
                        "height": 256 if height == 0 else height,
                        "color_count": color_count,
                        "planes": planes,
                        "bit_count": bit_count,
                        "size_bytes": size,
                        "offset": offset,
                    }
                )

        return {
            "available": True,
            "format": "ICO" if icon_type == 1 else "CUR",
            "images": entries,
            "count": len(entries),
        }
    except Exception:
        return None

