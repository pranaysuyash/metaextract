"""
Shared helpers for extractor modules.
Centralizes exact-duplicate utility functions.
"""

from typing import Any, Dict
import struct


def count_fields(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, dict):
        return sum(count_fields(v) for v in value.values())
    if isinstance(value, list):
        return sum(count_fields(v) for v in value)
    return 1


def safe_str(value: Any) -> str:
    try:
        return str(value)
    except Exception:
        return ""


def decode_mp4_data(data_type: int, data: bytes) -> Any:
    if data_type == 1:
        return data.decode("utf-8", errors="ignore")
    if data_type in [13, 14]:
        if data.startswith(b"\xff\xd8"):
            mime = "image/jpeg"
        elif data.startswith(b"\x89PNG"):
            mime = "image/png"
        else:
            mime = "application/octet-stream"
        return {"mime": mime, "size_bytes": len(data)}
    if len(data) == 2:
        return struct.unpack(">H", data)[0]
    if len(data) == 4:
        return struct.unpack(">I", data)[0]
    return data.hex()


def empty_extract(filepath: str) -> Dict[str, Any]:
    return {}
