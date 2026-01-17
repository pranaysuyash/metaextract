from __future__ import annotations

import struct
from typing import Any


def _read_exact(f, n: int) -> bytes:
    data = f.read(n)
    if len(data) != n:
        raise EOFError("Unexpected end of file")
    return data


def extract_bmp_container_metadata(filepath: str) -> dict[str, Any] | None:
    """
    Parse BMP file header + DIB header (BITMAPINFOHEADER and common variants).
    """
    try:
        with open(filepath, "rb") as f:
            sig = _read_exact(f, 2)
            if sig != b"BM":
                return None

            file_size = struct.unpack("<I", _read_exact(f, 4))[0]
            _ = _read_exact(f, 4)  # reserved
            pixel_offset = struct.unpack("<I", _read_exact(f, 4))[0]

            dib_size = struct.unpack("<I", _read_exact(f, 4))[0]
            dib = _read_exact(f, dib_size - 4) if dib_size >= 4 else b""

            width = height = bpp = compression = None
            if dib_size >= 40 and len(dib) >= 36:
                width = struct.unpack("<i", dib[0:4])[0]
                height = struct.unpack("<i", dib[4:8])[0]
                bpp = struct.unpack("<H", dib[10:12])[0]
                compression = struct.unpack("<I", dib[12:16])[0]

            return {
                "available": True,
                "format": "BMP",
                "file_size": file_size,
                "pixel_data_offset": pixel_offset,
                "dib_header_size": dib_size,
                "width": width,
                "height": height,
                "bits_per_pixel": bpp,
                "compression": compression,
            }
    except Exception:
        return None

