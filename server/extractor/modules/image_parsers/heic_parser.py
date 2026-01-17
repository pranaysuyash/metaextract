"""
HEIC Parser
===========

Extracts metadata from HEIC/HEIF images (ISO BMFF container).

No placeholders:
- If ExifTool is available, use it for canonical metadata.
- Otherwise, fall back to lightweight ISO BMFF box scanning (ftyp + presence signals).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from . import FormatParser, logger
from .computed_metadata import compute_all_metadata


class HeicParser(FormatParser):
    FORMAT_NAME = "HEIC"
    SUPPORTED_EXTENSIONS = [".heic", ".heif"]
    CAN_USE_EXIFTOOL = True

    def parse(self, filepath: str) -> Dict[str, Any]:
        exiftool_data = self._run_exiftool(filepath)
        if exiftool_data:
            metadata = self._process_exiftool_output(exiftool_data)
        else:
            metadata = self._parse_with_isobmff(filepath)

        width = metadata.get("width")
        height = metadata.get("height")
        if isinstance(width, int) and isinstance(height, int) and width > 0 and height > 0:
            computed = compute_all_metadata(
                filepath=filepath,
                width=width,
                height=height,
                format_name=metadata.get("format") or "HEIC",
                mode=metadata.get("color_mode") or "RGBA",
                exif=metadata.get("exif", {}) if isinstance(metadata.get("exif"), dict) else {},
                gps=metadata.get("gps", {}) if isinstance(metadata.get("gps"), dict) else {},
                icc_profile=metadata.get("icc_profile", {}) if isinstance(metadata.get("icc_profile"), dict) else {},
                file_size=metadata.get("file_size"),
            )
            metadata.update(computed)

        return metadata

    def _process_exiftool_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        out["format"] = data.get("FileType") or data.get("File:FileType") or "HEIC"
        out["width"] = self._parse_int(
            data.get("ImageWidth") or data.get("File:ImageWidth") or data.get("HEIC:ImageWidth")
        )
        out["height"] = self._parse_int(
            data.get("ImageHeight") or data.get("File:ImageHeight") or data.get("HEIC:ImageHeight")
        )

        ftyp_major = data.get("MajorBrand") or data.get("File:MajorBrand")
        if ftyp_major:
            out["brand"] = ftyp_major

        gps_lat = data.get("GPSLatitude")
        gps_lon = data.get("GPSLongitude")
        if gps_lat is not None or gps_lon is not None:
            out["gps"] = {"latitude": gps_lat, "longitude": gps_lon, "altitude": data.get("GPSAltitude")}

        exif: Dict[str, Any] = {}
        for key in (
            "Make",
            "Model",
            "Software",
            "DateTimeOriginal",
            "ExposureTime",
            "FNumber",
            "ISOSpeedRatings",
            "FocalLength",
            "Flash",
            "Rotation",
        ):
            v = data.get(key)
            if v is not None:
                exif[key.lower()] = v
        if exif:
            out["exif"] = exif

        return out

    def _parse_with_isobmff(self, filepath: str) -> Dict[str, Any]:
        out: Dict[str, Any] = {"format": "HEIC"}
        try:
            from ...formats.isobmff_boxes import extract_isobmff_box_metadata

            bmff = extract_isobmff_box_metadata(filepath)
            if bmff:
                out["container"] = bmff
                ftyp = bmff.get("ftyp") if isinstance(bmff, dict) else None
                if isinstance(ftyp, dict):
                    out["brand"] = ftyp.get("major_brand")
                    out["compatible_brands"] = ftyp.get("compatible_brands")
                if bmff.get("exif_box"):
                    out["exif"] = {"present": True}
        except Exception as e:
            logger.debug(f"HEIC ISOBMFF parse failed: {e}")

        try:
            out["file_size"] = Path(filepath).stat().st_size
        except Exception:
            pass
        return out

    def _parse_int(self, value: Any) -> Optional[int]:
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            s = value.strip()
            digits = "".join(ch for ch in s if ch.isdigit())
            try:
                return int(digits) if digits else None
            except Exception:
                return None
        return None

    def get_real_field_count(self, metadata: Dict[str, Any]) -> int:
        return self._count_real_fields(metadata)

    def can_parse(self, filepath: str) -> bool:
        return Path(filepath).suffix.lower() in self.SUPPORTED_EXTENSIONS


def parse_heic(filepath: str) -> Dict[str, Any]:
    return HeicParser().parse(filepath)

