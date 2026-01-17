from __future__ import annotations

from typing import Any


def extract_jxl_container_metadata(filepath: str) -> dict[str, Any] | None:
    """
    Detect JPEG XL codestream or BMFF container signatures.

    This is a lightweight detector and does not decode the image.
    """
    try:
        with open(filepath, "rb") as f:
            prefix = f.read(96)

        # Codestream signature: 0xFF0A
        if prefix.startswith(b"\xff\x0a"):
            return {"available": True, "format": "JXL", "container": "codestream"}

        # BMFF signature box for JXL: size=12, type='JXL ', magic=0x0d0a870a
        has_jxl_signature_box = (
            len(prefix) >= 12
            and prefix[0:4] == b"\x00\x00\x00\x0c"
            and prefix[4:8] == b"JXL "
            and prefix[8:12] == b"\x0d\x0a\x87\x0a"
        )

        # Try to locate an `ftyp` box early and read brands best-effort.
        ftyp_idx = prefix.find(b"ftyp")
        ftyp: dict[str, Any] | None = None
        if ftyp_idx >= 4 and ftyp_idx + 16 <= len(prefix):
            major = prefix[ftyp_idx + 4 : ftyp_idx + 8].decode("ascii", errors="replace")
            minor = int.from_bytes(prefix[ftyp_idx + 8 : ftyp_idx + 12], "big")
            compat_raw = prefix[ftyp_idx + 12 : ftyp_idx + 64]
            compat = [
                compat_raw[i : i + 4].decode("ascii", errors="replace")
                for i in range(0, len(compat_raw) - (len(compat_raw) % 4), 4)
            ]
            ftyp = {"major_brand": major, "minor_version": minor, "compatible_brands": compat}

        brands_blob = (ftyp.get("major_brand", "") + " " + " ".join(ftyp.get("compatible_brands", []))).lower() if ftyp else ""
        is_jxl_brand = ("jxl" in brands_blob) or has_jxl_signature_box
        if is_jxl_brand:
            out: dict[str, Any] = {"available": True, "format": "JXL", "container": "isobmff"}
            if has_jxl_signature_box:
                out["signature_box"] = True
            if ftyp:
                out["ftyp"] = ftyp
            return out
        return None
    except Exception:
        return None
