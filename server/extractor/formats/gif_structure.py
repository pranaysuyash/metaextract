from __future__ import annotations

import hashlib
import struct
from typing import Any


def _read_exact(f, n: int) -> bytes:
    data = f.read(n)
    if len(data) != n:
        raise EOFError("Unexpected end of file")
    return data


def _read_subblocks(f) -> bytes:
    parts: list[bytes] = []
    while True:
        size_b = _read_exact(f, 1)
        size = size_b[0]
        if size == 0:
            break
        parts.append(_read_exact(f, size))
    return b"".join(parts)


def extract_gif_container_metadata(filepath: str) -> dict[str, Any] | None:
    """
    Extract container-level GIF metadata by parsing the GIF block structure.

    Focuses on:
    - Logical Screen Descriptor + Global Color Table
    - Frame count (image descriptors)
    - Looping info (NETSCAPE2.0 app extension)
    - Presence of XMP application extension
    - Comment blocks
    """
    try:
        with open(filepath, "rb") as f:
            header = _read_exact(f, 6)
            if header[:3] != b"GIF":
                return None
            version = header[3:].decode("ascii", errors="replace")

            lsd = _read_exact(f, 7)
            width, height, packed, bg_color_index, pixel_aspect = struct.unpack("<HHBBB", lsd)
            global_color_table_flag = (packed & 0b1000_0000) != 0
            gct_size_code = packed & 0b0000_0111
            gct_entries = 2 ** (gct_size_code + 1) if global_color_table_flag else 0
            if global_color_table_flag:
                _ = _read_exact(f, gct_entries * 3)

            frames = 0
            comment_blocks = 0
            loop_count: int | None = None
            xmp: dict[str, Any] | None = None

            while True:
                sentinel_b = f.read(1)
                if not sentinel_b:
                    break
                sentinel = sentinel_b[0]

                if sentinel == 0x3B:  # trailer
                    break

                if sentinel == 0x2C:  # image descriptor
                    _ = _read_exact(f, 9)
                    packed_b = _read_exact(f, 1)[0]
                    local_color_table_flag = (packed_b & 0b1000_0000) != 0
                    lct_size_code = packed_b & 0b0000_0111
                    if local_color_table_flag:
                        lct_entries = 2 ** (lct_size_code + 1)
                        _ = _read_exact(f, lct_entries * 3)
                    _ = _read_exact(f, 1)  # LZW min code size
                    _ = _read_subblocks(f)  # image data
                    frames += 1
                    continue

                if sentinel == 0x21:  # extension
                    label = _read_exact(f, 1)[0]

                    if label == 0xFE:  # comment extension
                        _ = _read_subblocks(f)
                        comment_blocks += 1
                        continue

                    if label == 0xFF:  # application extension
                        block_size = _read_exact(f, 1)[0]
                        app_id = _read_exact(f, block_size)
                        app_identifier = app_id[:8].decode("ascii", errors="replace")
                        app_auth = app_id[8:11].decode("ascii", errors="replace") if len(app_id) >= 11 else ""
                        payload = _read_subblocks(f)

                        # NETSCAPE2.0 looping
                        if app_identifier == "NETSCAPE" and payload[:3] == b"\x01":
                            if len(payload) >= 5:
                                loop_count = int.from_bytes(payload[1:3], "little", signed=False)

                        # XMP (common identifier: "XMP Data")
                        if app_identifier.startswith("XMP Data") or b"xmp" in app_id.lower():
                            xmp = {
                                "application_identifier": app_identifier,
                                "application_auth": app_auth,
                                "size_bytes": len(payload),
                                "sha256": hashlib.sha256(payload).hexdigest(),
                            }
                        continue

                    # Other extension labels: consume sub-blocks (e.g. GCE, plain text)
                    if label in (0xF9, 0x01):
                        block_size = _read_exact(f, 1)[0]
                        _ = _read_exact(f, block_size)
                        _ = _read_subblocks(f)
                        continue

                    # Unknown extension: best-effort skip sub-blocks
                    _ = _read_subblocks(f)
                    continue

                # Unknown sentinel; abort parsing
                break

        return {
            "available": True,
            "format": "GIF",
            "version": version,
            "logical_screen": {
                "width": width,
                "height": height,
                "global_color_table": {
                    "present": global_color_table_flag,
                    "entries": gct_entries,
                },
                "background_color_index": bg_color_index,
                "pixel_aspect_ratio": pixel_aspect,
            },
            "frames": frames,
            "loop_count": loop_count,
            "comments": {"count": comment_blocks},
            "xmp": xmp,
        }
    except Exception:
        return None

