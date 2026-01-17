from __future__ import annotations

from typing import Any


def extract_pnm_container_metadata(filepath: str) -> dict[str, Any] | None:
    """
    Parse Netpbm header (P1-P6). Best-effort, supports comments.
    """
    try:
        with open(filepath, "rb") as f:
            data = f.read(4096)
        if not data.startswith(b"P"):
            return None
        parts: list[str] = []
        for token in data.split():
            if token.startswith(b"#"):
                continue
            parts.append(token.decode("ascii", errors="replace"))
            if len(parts) >= 4:
                break
        if len(parts) < 3:
            return None
        magic = parts[0]
        width = int(parts[1])
        height = int(parts[2])
        maxval = int(parts[3]) if magic not in ("P1", "P4") and len(parts) >= 4 else None
        return {
            "available": True,
            "format": "PNM",
            "magic": magic,
            "width": width,
            "height": height,
            "maxval": maxval,
        }
    except Exception:
        return None

