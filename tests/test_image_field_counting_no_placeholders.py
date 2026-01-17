from __future__ import annotations

from server.extractor.comprehensive_metadata_engine import DroneUAVEngine
from server.extractor.utils.field_counting import (
    DEFAULT_FIELD_COUNT_IGNORED_KEYS,
    count_meaningful_fields,
)


def test_count_meaningful_fields_ignores_envelope_sections() -> None:
    payload = {
        "extraction_info": {"tier": "free", "fields_extracted": 999},
        "file": {"name": "x.png"},
        "summary": {"filename": "x.png"},
        "locked_fields": ["gps"],
        "image": {"format": "PNG", "width": 100, "height": 100},
        "exif": {},
        "gps": {"_locked": True},
        "performance": {"duration_seconds": 0.1},
        "available": True,
    }

    count = count_meaningful_fields(payload, ignored_keys=set(DEFAULT_FIELD_COUNT_IGNORED_KEYS))
    # Only meaningful leaves under `image` should count here.
    assert count == 3


def test_drone_telemetry_returns_none_when_no_meaningful_leaves() -> None:
    exiftool_data = {
        "exif": {"ISO": None, "ExposureTime": None, "FNumber": None, "FocalLength": None},
        "gps": {},
        "xmp": {},
        "other": {},
    }

    assert DroneUAVEngine.extract_drone_telemetry("does-not-matter", exiftool_data) is None


def test_drone_telemetry_returns_payload_when_signals_exist() -> None:
    exiftool_data = {
        "exif": {"ISO": 100, "ExposureTime": "1/60", "FNumber": 2.8, "FocalLength": 24.0},
        "gps": {"GPSLatitude": 12.34, "GPSLongitude": 56.78},
        "xmp": {},
        "other": {"DJI_FlightPitchRotation": 1.23},
    }

    out = DroneUAVEngine.extract_drone_telemetry("does-not-matter", exiftool_data)
    assert isinstance(out, dict)
    assert out.get("available") is True
