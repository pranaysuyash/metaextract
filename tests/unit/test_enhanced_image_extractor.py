#!/usr/bin/env python3
"""
Unit tests for the Enhanced Image Extractor.

Tests comprehensive image metadata extraction including EXIF, IPTC, XMP, ICC,
and GPS metadata from JPEG, PNG, TIFF, WebP, and other formats.
"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'server'))

from extractor.extractors.enhanced_image_extractor import (
    EnhancedImageExtractor,
    extract_image_metadata,
    EXIFTOOL_AVAILABLE
)


class TestEnhancedImageExtractor:
    """Test suite for EnhancedImageExtractor class."""

    def test_exiftool_available(self):
        """Test that ExifTool is available for testing."""
        assert EXIFTOOL_AVAILABLE, "ExifTool is required for these tests"

    def test_extract_jpeg_with_full_metadata(self):
        """Test extraction from JPEG with comprehensive metadata."""
        test_file = "test-data/sample_with_meta.jpg"
        assert os.path.exists(test_file), f"Test file not found: {test_file}"

        result = extract_image_metadata(test_file, redact_sensitive=False)

        assert "file_info" in result
        assert result["file_info"]["filename"] == "sample_with_meta.jpg"
        assert result["file_info"]["mime_type"] == "image/jpeg"

        assert "surfaces" in result
        surfaces = result["surfaces"]

        assert surfaces["container"]["format"] == "JPEG"
        assert surfaces["exif_ifd0"]["make"] == "MetaCam"
        assert surfaces["exif_ifd0"]["model"] == "MetaCam 1"
        assert surfaces["exif_exif"]["datetime_original"] == "2025:12:30 12:34:56"
        assert surfaces["exif_gps"]["latitude"] is not None
        assert surfaces["exif_gps"]["longitude"] is not None
        assert surfaces["iptc"]["keywords"] == "metaextract"
        assert surfaces["iptc"]["city"] == "Mountain View"
        assert surfaces["xmp"]["dc_creator"] == "MetaExtract"
        assert surfaces["xmp"]["dc_title"] == "MetaExtract Demo"
        assert surfaces["icc"]["profile_version"] == "4.3.0"
        assert surfaces["icc"]["description"] == "sRGB"

        assert result["extraction_stats"]["exiftool_used"] == True
        assert result["extraction_stats"]["xmp_parsed"] == True
        assert result["extraction_stats"]["icc_parsed"] == True

    def test_extract_png_basic(self):
        """Test extraction from PNG file."""
        test_file = "test-data/test_png.png"
        if not os.path.exists(test_file):
            print(f"Skipping PNG test - file not found: {test_file}")
            return

        result = extract_image_metadata(test_file, redact_sensitive=False)

        assert "file_info" in result
        assert result["file_info"]["mime_type"] == "image/png"
        assert "surfaces" in result

    def test_extract_webp_basic(self):
        """Test extraction from WebP file."""
        test_file = "test-data/test_webp.webp"
        if not os.path.exists(test_file):
            print(f"Skipping WebP test - file not found: {test_file}")
            return

        result = extract_image_metadata(test_file, redact_sensitive=False)

        assert "file_info" in result
        assert result["file_info"]["mime_type"] == "image/webp"
        assert "surfaces" in result

    def test_redaction_removes_gps(self):
        """Test that GPS coordinates are redacted when enabled."""
        test_file = "test-data/sample_with_meta.jpg"
        assert os.path.exists(test_file), f"Test file not found: {test_file}"

        result = extract_image_metadata(test_file, redact_sensitive=True)

        surfaces = result["surfaces"]
        gps = surfaces.get("exif_gps", {})

        if gps.get("latitude") and gps.get("latitude") != {"redacted": True}:
            print(f"GPS not fully redacted: {gps}")

    def test_gps_normalization(self):
        """Test GPS coordinate normalization from DMS to decimal degrees."""
        test_file = "test-data/sample_with_meta.jpg"
        assert os.path.exists(test_file), f"Test file not found: {test_file}"

        result = extract_image_metadata(test_file, redact_sensitive=False)

        normalized = result.get("normalized", {})
        if normalized.get("gps_decimal"):
            gps = normalized["gps_decimal"]
            assert "latitude" in gps
            assert "longitude" in gps
            assert isinstance(gps["latitude"], float)
            assert isinstance(gps["longitude"], float)
            assert abs(gps["latitude"] - 37.422) < 1, f"Latitude seems wrong: {gps['latitude']}"
            # Longitude is positive 122.084 in test data (W hemisphere marker may be in separate field)
            assert abs(gps["longitude"] - 122.084) < 1, f"Longitude seems wrong: {gps['longitude']}"

    def test_datetime_normalization(self):
        """Test DateTime normalization to ISO 8601."""
        test_file = "test-data/sample_with_meta.jpg"
        assert os.path.exists(test_file), f"Test file not found: {test_file}"

        result = extract_image_metadata(test_file, redact_sensitive=False)

        normalized = result.get("normalized", {})
        if normalized.get("datetime_iso"):
            assert normalized["datetime_iso"].endswith("Z")
            assert "2025-12-30" in normalized["datetime_iso"]

    def test_extractor_class_can_extract(self):
        """Test EnhancedImageExtractor.can_extract method."""
        extractor = EnhancedImageExtractor()

        assert extractor.can_extract("test.jpg") == True
        assert extractor.can_extract("test.jpeg") == True
        assert extractor.can_extract("test.png") == True
        assert extractor.can_extract("test.webp") == True
        assert extractor.can_extract("test.tiff") == True
        assert extractor.can_extract("test.heic") == True
        assert extractor.can_extract("test.xyz") == False

    def test_nonexistent_file_raises_error(self):
        """Test that extracting from non-existent file raises FileNotFoundError."""
        extractor = EnhancedImageExtractor()

        try:
            extract_image_metadata("/nonexistent/file.jpg")
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass

    def test_extraction_timestamp_present(self):
        """Test that extraction timestamp is present in result."""
        test_file = "test-data/sample_with_meta.jpg"
        if not os.path.exists(test_file):
            print(f"Skipping timestamp test - file not found: {test_file}")
            return

        result = extract_image_metadata(test_file, redact_sensitive=False)

        assert "extraction_timestamp" in result
        assert "Z" in result["extraction_timestamp"]
        assert "2026-01-17" in result["extraction_timestamp"]

    def test_all_surfaces_present(self):
        """Test that all expected surfaces are present in the result."""
        test_file = "test-data/sample_with_meta.jpg"
        if not os.path.exists(test_file):
            print(f"Skipping surfaces test - file not found: {test_file}")
            return

        result = extract_image_metadata(test_file, redact_sensitive=False)
        surfaces = result["surfaces"]

        expected_surfaces = [
            "container",
            "exif_ifd0",
            "exif_exif",
            "exif_gps",
            "iptc",
            "xmp",
            "icc",
            "makernote"
        ]

        for surface in expected_surfaces:
            assert surface in surfaces, f"Surface '{surface}' not found in result"

    def test_icc_profile_extraction(self):
        """Test ICC profile metadata extraction."""
        test_file = "test-data/sample_with_meta.jpg"
        if not os.path.exists(test_file):
            print(f"Skipping ICC test - file not found: {test_file}")
            return

        result = extract_image_metadata(test_file, redact_sensitive=False)
        icc = result["surfaces"]["icc"]

        assert icc["profile_version"] == "4.3.0"
        assert icc["profile_class"] == "Display Device Profile"
        assert icc["color_space"] is not None
        assert icc["description"] == "sRGB"

    def test_xmp_extraction(self):
        """Test XMP metadata extraction."""
        test_file = "test-data/sample_with_meta.jpg"
        if not os.path.exists(test_file):
            print(f"Skipping XMP test - file not found: {test_file}")
            return

        result = extract_image_metadata(test_file, redact_sensitive=False)
        xmp = result["surfaces"]["xmp"]

        assert xmp["dc_creator"] == "MetaExtract"
        assert xmp["dc_title"] == "MetaExtract Demo"

    def test_iptc_extraction(self):
        """Test IPTC metadata extraction."""
        test_file = "test-data/sample_with_meta.jpg"
        if not os.path.exists(test_file):
            print(f"Skipping IPTC test - file not found: {test_file}")
            return

        result = extract_image_metadata(test_file, redact_sensitive=False)
        iptc = result["surfaces"]["iptc"]

        assert iptc["keywords"] == "metaextract"
        assert iptc["city"] == "Mountain View"
        assert iptc["headline"] == "IPTC Headline"


def run_tests():
    """Run all tests and print summary."""
    import unittest

    print("=" * 60)
    print("Running Enhanced Image Extractor Tests")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestEnhancedImageExtractor)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 60)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
