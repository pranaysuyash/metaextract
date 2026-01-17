from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass
from typing import Any


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


@dataclass(frozen=True)
class PngChunk:
    chunk_type: str
    length: int
    offset: int


def _read_exact(f, n: int) -> bytes:
    data = f.read(n)
    if len(data) != n:
        raise EOFError("Unexpected end of file")
    return data


def _limit_text(value: str, max_len: int = 4096) -> str:
    if len(value) <= max_len:
        return value
    return value[:max_len] + "…"


def extract_png_container_metadata(filepath: str) -> dict[str, Any] | None:
    """
    Extract container-level PNG metadata by parsing the PNG chunk stream.

    This is intentionally independent of ExifTool and Pillow EXIF helpers.
    It focuses on container features like IHDR, text chunks, pHYs, iCCP, and eXIf.
    """
    try:
        with open(filepath, "rb") as f:
            sig = _read_exact(f, 8)
            if sig != PNG_SIGNATURE:
                return None

            chunks: list[PngChunk] = []
            chunk_counts: dict[str, int] = {}
            texts: dict[str, str] = {}
            itxt_keys: list[str] = []
            ztxt_keys: list[str] = []
            ihdr: dict[str, Any] | None = None
            phys: dict[str, Any] | None = None
            gama: float | None = None
            srgb: dict[str, Any] | None = None
            iccp: dict[str, Any] | None = None
            exif: dict[str, Any] | None = None

            offset = 8
            while True:
                length_bytes = f.read(4)
                if not length_bytes:
                    break
                if len(length_bytes) != 4:
                    return None
                length = struct.unpack(">I", length_bytes)[0]
                ctype = _read_exact(f, 4)
                chunk_type = ctype.decode("ascii", errors="replace")
                data = _read_exact(f, length)
                _ = _read_exact(f, 4)  # crc

                chunks.append(PngChunk(chunk_type=chunk_type, length=length, offset=offset))
                chunk_counts[chunk_type] = chunk_counts.get(chunk_type, 0) + 1

                if chunk_type == "IHDR" and length == 13:
                    w, h, bit_depth, color_type, compression, flt, interlace = struct.unpack(
                        ">IIBBBBB", data
                    )
                    ihdr = {
                        "width": w,
                        "height": h,
                        "bit_depth": bit_depth,
                        "color_type": color_type,
                        "compression_method": compression,
                        "filter_method": flt,
                        "interlace_method": interlace,
                    }

                elif chunk_type == "pHYs" and length == 9:
                    ppux, ppuy, unit = struct.unpack(">IIB", data)
                    phys = {
                        "pixels_per_unit_x": ppux,
                        "pixels_per_unit_y": ppuy,
                        "unit_specifier": unit,
                        "unit": "meter" if unit == 1 else "unknown",
                    }

                elif chunk_type == "gAMA" and length == 4:
                    (g,) = struct.unpack(">I", data)
                    if g:
                        gama = g / 100000.0

                elif chunk_type == "sRGB" and length == 1:
                    srgb = {"rendering_intent": data[0]}

                elif chunk_type == "iCCP":
                    # profile name (latin-1), NUL, compression method, compressed profile bytes
                    nul = data.find(b"\x00")
                    if nul != -1 and nul + 2 <= len(data):
                        profile_name = data[:nul].decode("latin-1", errors="replace")
                        compression_method = data[nul + 1]
                        compressed = data[nul + 2 :]
                        iccp = {
                            "profile_name": profile_name,
                            "compression_method": compression_method,
                            "compressed_size_bytes": len(compressed),
                            "sha256": hashlib.sha256(compressed).hexdigest(),
                        }

                elif chunk_type == "eXIf":
                    # Raw EXIF payload (TIFF). Do not parse here; expose presence + hash.
                    exif = {
                        "size_bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest(),
                    }

                elif chunk_type == "tEXt":
                    nul = data.find(b"\x00")
                    if nul != -1:
                        key = data[:nul].decode("latin-1", errors="replace").strip()
                        value = data[nul + 1 :].decode("latin-1", errors="replace")
                        if key and key not in texts and len(texts) < 50:
                            texts[key] = _limit_text(value)

                elif chunk_type == "zTXt":
                    nul = data.find(b"\x00")
                    if nul != -1 and nul + 2 <= len(data):
                        key = data[:nul].decode("latin-1", errors="replace").strip()
                        if key and len(ztxt_keys) < 50:
                            ztxt_keys.append(key)

                elif chunk_type == "iTXt":
                    nul = data.find(b"\x00")
                    if nul != -1:
                        key = data[:nul].decode("latin-1", errors="replace").strip()
                        if key and len(itxt_keys) < 50:
                            itxt_keys.append(key)

                offset += 12 + length
                if chunk_type == "IEND":
                    break

        return {
            "available": True,
            "format": "PNG",
            "ihdr": ihdr,
            "chunk_counts": chunk_counts,
            "chunks_total": len(chunks),
            "text": {"tEXt": texts, "zTXt_keys": ztxt_keys, "iTXt_keys": itxt_keys},
            "pHYs": phys,
            "gAMA": gama,
            "sRGB": srgb,
            "iCCP": iccp,
            "eXIf": exif,
        }
    except Exception:
        return None

