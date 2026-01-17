from __future__ import annotations

import struct
from typing import Any


EXR_MAGIC = 20000630


def _read_cstr(f, max_len: int = 4096) -> str:
    out = bytearray()
    while len(out) < max_len:
        b = f.read(1)
        if not b:
            raise EOFError("Unexpected end of file")
        if b == b"\x00":
            return out.decode("utf-8", errors="replace")
        out.extend(b)
    raise ValueError("String too long")


def extract_exr_container_metadata(filepath: str) -> dict[str, Any] | None:
    """
    Parse OpenEXR header attribute list (name/type/size/value) until empty name.
    """
    try:
        with open(filepath, "rb") as f:
            magic = struct.unpack("<I", f.read(4))[0]
            if magic != EXR_MAGIC:
                return None
            version = struct.unpack("<I", f.read(4))[0]

            attrs: list[dict[str, Any]] = []
            while True:
                name = _read_cstr(f)
                if name == "":
                    break
                attr_type = _read_cstr(f)
                size = struct.unpack("<I", f.read(4))[0]
                # Skip value bytes
                f.seek(size, 1)
                if len(attrs) < 200:
                    attrs.append({"name": name, "type": attr_type, "size": size})

        return {"available": True, "format": "EXR", "version": version, "attributes": attrs}
    except Exception:
        return None

