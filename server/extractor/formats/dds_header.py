from __future__ import annotations

import struct
from typing import Any


def _read_exact(f, n: int) -> bytes:
    data = f.read(n)
    if len(data) != n:
        raise EOFError("Unexpected end of file")
    return data


def extract_dds_container_metadata(filepath: str) -> dict[str, Any] | None:
    """
    Parse DDS header (DDSURFACEDESC2).
    """
    try:
        with open(filepath, "rb") as f:
            if _read_exact(f, 4) != b"DDS ":
                return None
            header_size = struct.unpack("<I", _read_exact(f, 4))[0]
            if header_size != 124:
                return None
            flags = struct.unpack("<I", _read_exact(f, 4))[0]
            height = struct.unpack("<I", _read_exact(f, 4))[0]
            width = struct.unpack("<I", _read_exact(f, 4))[0]
            pitch = struct.unpack("<I", _read_exact(f, 4))[0]
            depth = struct.unpack("<I", _read_exact(f, 4))[0]
            mipmap_count = struct.unpack("<I", _read_exact(f, 4))[0]
            _ = _read_exact(f, 44)  # reserved
            # Pixel format
            pf_size = struct.unpack("<I", _read_exact(f, 4))[0]
            pf_flags = struct.unpack("<I", _read_exact(f, 4))[0]
            fourcc = _read_exact(f, 4).decode("ascii", errors="replace")
            _ = _read_exact(f, 20)  # rest of pixel format
            caps = struct.unpack("<I", _read_exact(f, 4))[0]
            caps2 = struct.unpack("<I", _read_exact(f, 4))[0]
        return {
            "available": True,
            "format": "DDS",
            "width": width,
            "height": height,
            "mipmap_count": mipmap_count,
            "fourcc": fourcc.strip("\x00"),
            "flags": flags,
            "caps": caps,
            "caps2": caps2,
            "pitch_or_linear_size": pitch,
            "depth": depth,
            "pixel_format_size": pf_size,
            "pixel_format_flags": pf_flags,
        }
    except Exception:
        return None

