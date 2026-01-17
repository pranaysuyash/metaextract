from __future__ import annotations

import hashlib
from typing import Any


def _read_exact(f, n: int) -> bytes:
    data = f.read(n)
    if len(data) != n:
        raise EOFError("Unexpected end of file")
    return data


def _scan_jpeg_segments(filepath: str, max_segments: int = 2048) -> dict[str, Any] | None:
    with open(filepath, "rb") as f:
        if _read_exact(f, 2) != b"\xff\xd8":  # SOI
            return None

        segments: list[dict[str, Any]] = []
        sof: dict[str, Any] | None = None
        app_segments: dict[str, list[int]] = {}
        exif: dict[str, Any] | None = None
        xmp: dict[str, Any] | None = None
        icc: dict[str, Any] | None = None
        jfif: dict[str, Any] | None = None

        for _ in range(max_segments):
            # Markers are 0xFF prefixed, with optional fill bytes.
            b = f.read(1)
            if not b:
                break
            if b != b"\xff":
                # We are likely in entropy-coded scan; stop.
                break
            while True:
                marker_b = _read_exact(f, 1)
                if marker_b != b"\xff":
                    break
            marker = marker_b[0]

            # Standalone markers
            if marker in (0xD9,):  # EOI
                segments.append({"marker": "EOI"})
                break
            if 0xD0 <= marker <= 0xD7:  # RSTn
                segments.append({"marker": f"RST{marker-0xD0}"})
                continue
            if marker in (0x01,):  # TEM
                segments.append({"marker": "TEM"})
                continue

            # Variable-length segment: 2-byte big-endian length includes the length bytes.
            length = int.from_bytes(_read_exact(f, 2), "big")
            if length < 2:
                break
            payload = _read_exact(f, length - 2)

            name = f"0x{marker:02X}"
            if 0xE0 <= marker <= 0xEF:
                app = f"APP{marker-0xE0}"
                name = app
                app_segments.setdefault(app, []).append(len(payload))
            elif 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                name = f"SOF{marker-0xC0}"
            elif marker == 0xDA:
                name = "SOS"
            elif marker == 0xDB:
                name = "DQT"
            elif marker == 0xC4:
                name = "DHT"
            elif marker == 0xDD:
                name = "DRI"
            elif marker == 0xFE:
                name = "COM"

            segments.append({"marker": name, "length": len(payload)})

            # Parse SOF for dimensions
            if name.startswith("SOF") and len(payload) >= 6:
                precision = payload[0]
                height = int.from_bytes(payload[1:3], "big")
                width = int.from_bytes(payload[3:5], "big")
                components = payload[5]
                sof = {
                    "marker": name,
                    "precision": precision,
                    "width": width,
                    "height": height,
                    "components": components,
                }

            # Detect JFIF (APP0)
            if name == "APP0" and payload.startswith(b"JFIF\x00") and len(payload) >= 14:
                jfif = {
                    "version_major": payload[5],
                    "version_minor": payload[6],
                    "density_units": payload[7],
                    "x_density": int.from_bytes(payload[8:10], "big"),
                    "y_density": int.from_bytes(payload[10:12], "big"),
                }

            # Detect EXIF (APP1)
            if name == "APP1" and payload.startswith(b"Exif\x00\x00"):
                exif = {
                    "size_bytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                }

            # Detect XMP (APP1)
            if name == "APP1" and payload.startswith(b"http://ns.adobe.com/xap/1.0/\x00"):
                xmp_payload = payload.split(b"\x00", 1)[1] if b"\x00" in payload else b""
                xmp = {
                    "size_bytes": len(xmp_payload),
                    "sha256": hashlib.sha256(xmp_payload).hexdigest(),
                }

            # Detect ICC profile (APP2)
            if name == "APP2" and payload.startswith(b"ICC_PROFILE\x00") and len(payload) >= 14:
                icc = {
                    "size_bytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                }

            if name == "SOS":
                # Start of scan; image data follows.
                break

        return {
            "available": True,
            "format": "JPEG",
            "sof": sof,
            "app_segments": app_segments,
            "jfif": jfif,
            "exif_app1": exif,
            "xmp_app1": xmp,
            "icc_app2": icc,
            "segments_scanned": len(segments),
        }


def extract_jpeg_container_metadata(filepath: str) -> dict[str, Any] | None:
    try:
        return _scan_jpeg_segments(filepath)
    except Exception:
        return None

