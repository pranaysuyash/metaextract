#!/usr/bin/env python3
"""
Test script for Metadata Quality Agent
Validates quality assessment functionality
"""

import sys
import json
sys.path.insert(0, '/Users/pranay/Projects/metaextract/server/extractor')

from metadata_quality_agent import (
    MetadataQualityAgent,
    assess_metadata_quality,
    QualityLevel,
    ExtractionStatus
)


def test_good_quality_metadata():
    """Test with high-quality metadata from a typical photo."""
    metadata = {
        "basic_properties": {
            "file_name": "IMG_1234.JPG",
            "file_size": 5242880,
            "file_type": "image/jpeg",
            "mime_type": "image/jpeg",
            "width": 4032,
            "height": 3024,
            "orientation": 1
        },
        "exif": {
            "make": "Apple",
            "model": "iPhone 14 Pro",
            "datetime_original": "2024-01-15T10:30:00",
            "exposure_time": "1/120",
            "f_number": "f/1.8",
            "iso": 100,
            "focal_length": "6.86 mm",
            "flash": "No flash",
            "white_balance": "Auto"
        },
        "gps": {
            "gps_latitude": 37.7749,
            "gps_longitude": -122.4194,
            "gps_altitude": 10.5,
            "gps_timestamp": "2024-01-15T10:30:00"
        },
        "icc_profile": {
            "color_space": "sRGB",
            "profile_version": "4.0.0",
            "profile_class": "Display Device"
        },
        "xmp": {
            "dc:creator": "John Doe",
            "dc:title": "Sample Photo",
            "photoshop:ColorMode": "3"
        }
    }

    agent = MetadataQualityAgent()
    report = agent.assess_extraction_result(
        extracted_metadata=metadata,
        file_type="image/jpeg",
        file_size=5242880,
        extraction_time_ms=150.0
    )

    print("=== Good Quality Test ===")
    print(f"Overall Score: {report.overall_score}")
    print(f"Quality Level: {report.overall_level.value}")
    print(f"Completeness: {report.completeness_score}")
    print(f"Validity: {report.validity_score}")
    print(f"Consistency: {report.consistency_score}")
    print(f"Fields Extracted: {report.total_fields_extracted}")
    print(f"Fields Expected: {report.total_fields_expected}")
    print(f"Critical Issues: {len(report.critical_issues)}")
    print(f"Recommendations: {len(report.recommendations)}")
    print()

    assert report.overall_score >= 70, f"Expected good score, got {report.overall_score}"
    print("✓ Good quality test passed")


def test_poor_quality_metadata():
    """Test with minimal/poor quality metadata."""
    metadata = {
        "unknown_field": "some_value"
    }

    agent = MetadataQualityAgent()
    report = agent.assess_extraction_result(
        extracted_metadata=metadata,
        file_type="image/jpeg"
    )

    print("=== Poor Quality Test ===")
    print(f"Overall Score: {report.overall_score}")
    print(f"Quality Level: {report.overall_level.value}")
    print(f"Completeness: {report.completeness_score}")
    print(f"Critical Issues: {len(report.critical_issues)}")
    print()

    # With no recognized fields, should have critical issues
    assert len(report.critical_issues) >= 5, f"Expected multiple critical issues, got {len(report.critical_issues)}"
    print("✓ Poor quality test passed")


def test_malformed_metadata():
    """Test with malformed values."""
    metadata = {
        "basic_properties": {
            "file_name": "test.jpg",
            "file_size": 1000,
            "width": 1024,
            "height": 768
        },
        "exif": {
            "datetime_original": "invalid-date",
            "iso": "not-a-number",
            "f_number": "f/"
        },
        "gps": {
            "gps_latitude": 200.0,
            "gps_longitude": -200.0
        }
    }

    agent = MetadataQualityAgent()
    report = agent.assess_extraction_result(
        extracted_metadata=metadata,
        file_type="image/jpeg"
    )

    print("=== Malformed Data Test ===")
    print(f"Overall Score: {report.overall_score}")
    print(f"Validity Score: {report.validity_score}")
    print(f"Quality Level: {report.overall_level.value}")
    print()

    assert report.validity_score < 80, f"Expected low validity, got {report.validity_score}"
    print("✓ Malformed data test passed")


def test_empty_metadata():
    """Test with empty metadata."""
    metadata = {}

    agent = MetadataQualityAgent()
    report = agent.assess_extraction_result(
        extracted_metadata=metadata,
        file_type="image/jpeg"
    )

    print("=== Empty Metadata Test ===")
    print(f"Overall Score: {report.overall_score}")
    print(f"Quality Level: {report.overall_level.value}")
    print(f"Critical Issues: {len(report.critical_issues)}")
    print()

    # Empty metadata should have critical issues
    assert len(report.critical_issues) >= 5, f"Expected critical issues, got {len(report.critical_issues)}"
    print("✓ Empty metadata test passed")


def test_convenience_function():
    """Test the convenience function."""
    metadata = {
        "width": 1920,
        "height": 1080,
        "file_size": 2048000
    }

    report = assess_metadata_quality(
        metadata=metadata,
        file_type="image/png",
        file_size=2048000,
        extraction_time_ms=50.0
    )

    print("=== Convenience Function Test ===")
    print(f"Overall Score: {report.overall_score}")
    print(f"File Type: {report.file_type}")
    print(f"Extraction Time: {report.extraction_time_ms}ms")
    print()

    assert report.overall_score > 0, "Should have a valid score"
    print("✓ Convenience function test passed")


def test_quality_summary():
    """Test quality summary generation."""
    metadata = {
        "width": 1920,
        "height": 1080,
        "make": "Canon",
        "model": "EOS R5"
    }

    agent = MetadataQualityAgent()
    report = agent.assess_extraction_result(
        extracted_metadata=metadata,
        file_type="image/jpeg"
    )

    summary = agent.get_quality_summary(report)

    print("=== Quality Summary Test ===")
    print(json.dumps(summary, indent=2))
    print()

    assert "overall_score" in summary
    assert "overall_level" in summary
    assert "completeness" in summary
    print("✓ Quality summary test passed")


def test_compare_reports():
    """Test report comparison."""
    agent = MetadataQualityAgent()

    metadata1 = {"width": 1024, "height": 768}
    report1 = agent.assess_extraction_result(metadata1, "image/jpeg")

    metadata2 = {
        "width": 1920,
        "height": 1080,
        "make": "Sony",
        "model": "A7IV"
    }
    report2 = agent.assess_extraction_result(metadata2, "image/jpeg")

    comparison = agent.compare_reports(report1, report2)

    print("=== Report Comparison Test ===")
    print(json.dumps(comparison, indent=2))
    print()

    assert comparison["improved"] == True, "Report 2 should be better than report 1"
    print("✓ Report comparison test passed")


def run_all_tests():
    """Run all tests."""
    print("Running Metadata Quality Agent Tests\n")
    print("=" * 50)

    try:
        test_good_quality_metadata()
        test_poor_quality_metadata()
        test_malformed_metadata()
        test_empty_metadata()
        test_convenience_function()
        test_quality_summary()
        test_compare_reports()

        print("\n" + "=" * 50)
        print("All tests passed! ✓")
        return 0
    except AssertionError as e:
        print(f"\nTest failed: {e}")
        return 1
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
