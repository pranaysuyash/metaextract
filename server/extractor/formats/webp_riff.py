from __future__ import annotations

import hashlib
import struct
from typing import Any


def _read_exact(f, n: int) -> bytes:
    data = f.read(n)
    if len(data) != n:
        raise EOFError("Unexpected end of file")
    return data


def extract_webp_container_metadata(filepath: str) -> dict[str, Any] | None:
    """
    Extract container-level WebP metadata by parsing RIFF/WEBP chunks.

    Captures:
    - VP8X feature flags and canvas size (if present)
    - EXIF/XMP/ICCP chunk presence and sizes
    - Animation chunk presence
    """
    try:
        with open(filepath, "rb") as f:
            riff = _read_exact(f, 4)
            if riff != b"RIFF":
                return None
            _ = _read_exact(f, 4)  # file size
            webp = _read_exact(f, 4)
            if webp != b"WEBP":
                return None

            chunk_counts: dict[str, int] = {}
            vp8x: dict[str, Any] | None = None
            exif: dict[str, Any] | None = None
            xmp: dict[str, Any] | None = None
            iccp: dict[str, Any] | None = None
            anim: dict[str, Any] | None = None

            while True:
                header = f.read(8)
                if not header:
                    break
                if len(header) != 8:
                    break
                fourcc = header[:4].decode("ascii", errors="replace")
                size = struct.unpack("<I", header[4:])[0]
                data = _read_exact(f, size)
                if size % 2 == 1:
                    _ = f.read(1)  # padding

                chunk_counts[fourcc] = chunk_counts.get(fourcc, 0) + 1

                if fourcc == "VP8X" and size >= 10:
                    flags = data[0]
                    canvas_w = int.from_bytes(data[4:7], "little") + 1
                    canvas_h = int.from_bytes(data[7:10], "little") + 1
                    vp8x = {
                        "flags": flags,
                        "has_iccp": bool(flags & 0x20),
                        "has_exif": bool(flags & 0x08),
                        "has_xmp": bool(flags & 0x04),
                        "has_animation": bool(flags & 0x02),
                        "canvas_width": canvas_w,
                        "canvas_height": canvas_h,
                    }

                elif fourcc == "EXIF":
                    exif = {
                        "size_bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest(),
                    }

                elif fourcc == "XMP ":
                    xmp = {
                        "size_bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest(),
                    }

                elif fourcc == "ICCP":
                    iccp = {
                        "size_bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest(),
                    }

                elif fourcc in ("ANIM", "ANMF"):
                    if anim is None:
                        anim = {"present": True, "chunks": {}}
                    anim["chunks"][fourcc] = anim["chunks"].get(fourcc, 0) + 1

        return {
            "available": True,
            "format": "WEBP",
            "chunk_counts": chunk_counts,
            "vp8x": vp8x,
            "exif": exif,
            "xmp": xmp,
            "iccp": iccp,
            "animation": anim,
        }
    except Exception:
        return None

