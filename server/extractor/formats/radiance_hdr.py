from __future__ import annotations

from typing import Any


def extract_radiance_hdr_container_metadata(filepath: str) -> dict[str, Any] | None:
    """
    Parse Radiance HDR header (text) until blank line; capture resolution line.
    """
    try:
        with open(filepath, "rb") as f:
            header = f.read(8192)
        if not (header.startswith(b"#?RADIANCE") or header.startswith(b"#?RGBE")):
            return None
        text = header.decode("ascii", errors="replace")
        lines = text.splitlines()
        resolution = None
        for line in lines:
            if line.startswith(("-Y ", "+Y ", "-X ", "+X ")):
                resolution = line.strip()
                break
        return {"available": True, "format": "HDR", "resolution": resolution}
    except Exception:
        return None


def extract_radiance_hdr_metadata(filepath: str) -> dict[str, Any] | None:
    # Back-compat alias (older name).
    return extract_radiance_hdr_container_metadata(filepath)
