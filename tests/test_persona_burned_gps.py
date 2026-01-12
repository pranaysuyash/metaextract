#!/usr/bin/env python3
"""Test persona interpretation uses burned-overlay GPS as location when EXIF GPS missing."""

from extractor.persona_interpretation import add_persona_interpretation


def test_burned_overlay_gps_fallback():
    metadata = {
        # No embedded gps
        "gps": None,
        "burned_metadata": {
            "has_burned_metadata": True,
            "ocr_available": True,
            "extracted_text": "Some text with GPS",
            "parsed_data": {
                "gps": {"latitude": 12.923974, "longitude": 77.625419},
                "plus_code": "7J4VWJFG+H5",
            },
        },
    }

    enhanced = add_persona_interpretation(metadata, persona="phone_photo_sarah")
    location = enhanced.get("persona_interpretation", {}).get("plain_english_answers", {}).get("location", {})

    assert location.get("has_location") is True
    assert "burned-in overlay" in location.get("details", "") or "burned" in location.get("details", "")
    coords = location.get("coordinates", {})
    assert abs(coords.get("latitude", 0) - 12.923974) < 1e-6
    assert abs(coords.get("longitude", 0) - 77.625419) < 1e-6
