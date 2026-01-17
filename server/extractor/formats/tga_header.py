from __future__ import annotations

import struct
from typing import Any


def extract_tga_container_metadata(filepath: str) -> dict[str, Any] | None:
    """
    Parse TGA header (18 bytes).
    """
    try:
        with open(filepath, "rb") as f:
            header = f.read(18)
            if len(header) != 18:
                return None
            (
                id_len,
                cmap_type,
                img_type,
                cmap_first,
                cmap_len,
                cmap_depth,
                x_origin,
                y_origin,
                width,
                height,
                bpp,
                desc,
            ) = struct.unpack("<BBBHHBHHHHBB", header)
        return {
            "available": True,
            "format": "TGA",
            "image_type": img_type,
            "width": width,
            "height": height,
            "bits_per_pixel": bpp,
            "color_map_type": cmap_type,
            "color_map_length": cmap_len,
            "descriptor": desc,
            "id_length": id_len,
        }
    except Exception:
        return None

