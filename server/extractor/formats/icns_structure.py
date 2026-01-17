from __future__ import annotations

import struct
from typing import Any


def _read_exact(f, n: int) -> bytes:
    data = f.read(n)
    if len(data) != n:
        raise EOFError("Unexpected end of file")
    return data


def extract_icns_container_metadata(filepath: str, max_elements: int = 2048) -> dict[str, Any] | None:
    """
    Minimal ICNS parser: header + element table (type/length).
    """
    try:
        with open(filepath, "rb") as f:
            magic = _read_exact(f, 4)
            if magic != b"icns":
                return None
            total_len = struct.unpack(">I", _read_exact(f, 4))[0]
            elements: dict[str, int] = {}
            read = 8
            for _ in range(max_elements):
                if read + 8 > total_len:
                    break
                elem_type = _read_exact(f, 4).decode("ascii", errors="replace")
                elem_len = struct.unpack(">I", _read_exact(f, 4))[0]
                if elem_len < 8:
                    break
                payload_len = elem_len - 8
                f.seek(payload_len, 1)
                read += elem_len
                elements[elem_type] = elements.get(elem_type, 0) + 1

        return {"available": True, "format": "ICNS", "elements": elements, "total_length": total_len}
    except Exception:
        return None

