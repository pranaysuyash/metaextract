from __future__ import annotations

import hashlib
import struct
from typing import Any


def _read_exact(f, n: int) -> bytes:
    data = f.read(n)
    if len(data) != n:
        raise EOFError("Unexpected end of file")
    return data


def extract_psd_container_metadata(filepath: str) -> dict[str, Any] | None:
    """
    Minimal PSD/PSB parser for header + resource section sizes.

    Does not decode image data. Reports:
    - dimensions, channels, depth, color mode
    - resource section length + presence of XMP resource (0x0424) if detectable
    """
    try:
        with open(filepath, "rb") as f:
            sig = _read_exact(f, 4)
            if sig != b"8BPS":
                return None
            version = struct.unpack(">H", _read_exact(f, 2))[0]
            _ = _read_exact(f, 6)  # reserved
            channels = struct.unpack(">H", _read_exact(f, 2))[0]
            height = struct.unpack(">I", _read_exact(f, 4))[0]
            width = struct.unpack(">I", _read_exact(f, 4))[0]
            depth = struct.unpack(">H", _read_exact(f, 2))[0]
            color_mode = struct.unpack(">H", _read_exact(f, 2))[0]

            color_mode_len = struct.unpack(">I", _read_exact(f, 4))[0]
            f.seek(color_mode_len, 1)

            resource_len = struct.unpack(">I", _read_exact(f, 4))[0]
            resource_data = _read_exact(f, min(resource_len, 1024 * 1024))
            xmp_present = b"http://ns.adobe.com/xap/1.0/" in resource_data or b"XMP" in resource_data
            resources_sha256 = hashlib.sha256(resource_data).hexdigest()

            # Skip any remaining resources
            if resource_len > len(resource_data):
                f.seek(resource_len - len(resource_data), 1)

            layer_mask_len = struct.unpack(">I", _read_exact(f, 4))[0]
            # Do not read layer/mask payload; it can be large.

        return {
            "available": True,
            "format": "PSD" if version == 1 else "PSB" if version == 2 else "PSD_UNKNOWN",
            "version": version,
            "width": width,
            "height": height,
            "channels": channels,
            "depth": depth,
            "color_mode": color_mode,
            "color_mode_data_length": color_mode_len,
            "image_resources_length": resource_len,
            "image_resources_sha256": resources_sha256,
            "xmp_resource_likely_present": xmp_present,
            "layer_mask_info_length": layer_mask_len,
        }
    except Exception:
        return None

