#!/usr/bin/env python3
"""
Tests for extraction observability utilities.

Run with: python -m pytest server/extractor/test_extraction_observability.py -v
"""

import pytest
from .extraction_observability import (
    record_top_level_provenance,
    build_provenance_summary,
    detect_sensitive_fields,
    build_sensitive_fields_summary,
    flatten_dict,
    diff_extraction_results,
    add_observability_to_result,
)


class TestProvenanceTracking:
    """Tests for provenance tracking functionality."""

    def test_record_top_level_provenance_basic(self):
        """Test recording provenance for basic module output."""
        provenance = {}
        conflicts = []

        record_top_level_provenance(
            module_name="test_module",
            module_output={"exif": {"key": "value"}, "gps": {"lat": 0}},
            provenance=provenance,
            conflicts=conflicts,
        )

        assert provenance["exif"] == "test_module"
        assert provenance["gps"] == "test_module"
        assert len(conflicts) == 0

    def test_record_top_level_provenance_conflict(self):
        """Test recording a provenance conflict."""
        provenance = {"exif": "module_a"}
        conflicts = []

        record_top_level_provenance(
            module_name="module_b",
            module_output={"exif": {"different": "data"}},
            provenance=provenance,
            conflicts=conflicts,
        )

        # Provenance should still show first module
        assert provenance["exif"] == "module_a"
        # Conflict should be recorded
        assert len(conflicts) == 1
        assert conflicts[0]["key"] == "exif"
        assert conflicts[0]["first_module"] == "module_a"
        assert conflicts[0]["second_module"] == "module_b"

    def test_record_top_level_provenance_skips_internal_keys(self):
        """Test that internal keys are skipped."""
        provenance = {}
        conflicts = []

        record_top_level_provenance(
            module_name="test_module",
            module_output={
                "extraction_info": {},
                "performance": {},
                "_locked": True,
                "valid_key": {"data": 1},
            },
            provenance=provenance,
            conflicts=conflicts,
        )

        assert "extraction_info" not in provenance
        assert "performance" not in provenance
        assert "_locked" not in provenance
        assert "valid_key" in provenance

    def test_build_provenance_summary(self):
        """Test building provenance summary."""
        provenance = {"exif": "base", "gps": "mobile"}
        conflicts = [{"key": "makernote", "first_module": "a", "second_module": "b"}]

        summary = build_provenance_summary(provenance, conflicts)

        assert summary["module_provenance"]["exif"] == "base"
        assert summary["conflict_count"] == 1
        assert len(summary["provenance_conflicts"]) == 1


class TestSensitiveFieldDetection:
    """Tests for sensitive field detection."""

    def test_detect_gps_fields(self):
        """Test detection of GPS-related fields."""
        data = {
            "exif": {
                "GPSLatitude": 37.7749,
                "GPSLongitude": -122.4194,
            }
        }

        hits = detect_sensitive_fields(data)
        kinds = {h["kind"] for h in hits}

        assert "gps" in kinds

    def test_detect_device_id_fields(self):
        """Test detection of device ID fields."""
        data = {
            "exif": {
                "SerialNumber": "ABC123",
                "InternalSerialNumber": "XYZ789",
            }
        }

        hits = detect_sensitive_fields(data)
        kinds = {h["kind"] for h in hits}

        assert "device_id" in kinds

    def test_detect_person_fields(self):
        """Test detection of person-related fields."""
        data = {
            "iptc": {
                "CameraOwnerName": "John Doe",
                "Artist": "Jane Smith",
            }
        }

        hits = detect_sensitive_fields(data)
        kinds = {h["kind"] for h in hits}

        assert "person" in kinds

    def test_sensitive_fields_limit(self):
        """Test that sensitive fields are limited."""
        # Create a large nested structure with many sensitive keys
        data = {f"GPSField{i}": i for i in range(500)}

        hits = detect_sensitive_fields(data)

        assert len(hits) <= 200  # MAX_SENSITIVE_FIELDS

    def test_build_sensitive_fields_summary(self):
        """Test building sensitive fields summary."""
        data = {
            "gps": {"latitude": 0, "longitude": 0},
            "exif": {"SerialNumber": "ABC"},
        }

        summary = build_sensitive_fields_summary(data)

        assert "sensitive_fields_detected" in summary
        assert "sensitive_fields_count" in summary
        assert "sensitive_fields_by_kind" in summary


class TestDiffFunctions:
    """Tests for diff and flatten functions."""

    def test_flatten_dict_basic(self):
        """Test flattening a nested dict."""
        data = {
            "a": {"b": 1, "c": 2},
            "d": 3,
        }

        flat = flatten_dict(data)

        assert flat["a.b"] == 1
        assert flat["a.c"] == 2
        assert flat["d"] == 3

    def test_flatten_dict_with_list(self):
        """Test flattening a dict with lists."""
        data = {
            "items": [1, 2, 3],
        }

        flat = flatten_dict(data)

        assert flat["items[0]"] == 1
        assert flat["items[1]"] == 2
        assert flat["items[2]"] == 3

    def test_diff_extraction_results_added_keys(self):
        """Test detecting added keys in diff."""
        main = {"a": 1}
        shadow = {"a": 1, "b": 2}

        diff = diff_extraction_results(main, shadow)

        assert diff["added_keys_count"] == 1
        assert "b" in diff["added_keys"]

    def test_diff_extraction_results_removed_keys(self):
        """Test detecting removed keys in diff."""
        main = {"a": 1, "b": 2}
        shadow = {"a": 1}

        diff = diff_extraction_results(main, shadow)

        assert diff["removed_keys_count"] == 1
        assert "b" in diff["removed_keys"]

    def test_diff_extraction_results_changed_keys(self):
        """Test detecting changed keys in diff."""
        main = {"a": 1}
        shadow = {"a": 2}

        diff = diff_extraction_results(main, shadow)

        assert diff["changed_keys_count"] == 1
        assert "a" in diff["changed_keys"]


class TestObservabilityIntegration:
    """Tests for the main observability integration."""

    def test_add_observability_to_result(self):
        """Test adding observability data to a result."""
        result = {
            "file": {"path": "/test.jpg"},
            "exif": {"GPSLatitude": 37.0},
            "extraction_info": {"tier": "super"},
        }
        provenance = {"exif": "base_engine", "file": "base_engine"}
        conflicts = []

        updated = add_observability_to_result(
            result=result,
            provenance=provenance,
            conflicts=conflicts,
            shadow_info=None,
        )

        assert "provenance" in updated["extraction_info"]
        assert "sensitive_fields" in updated["extraction_info"]
        assert "shadow" in updated["extraction_info"]
        # Verify version field exists for schema evolution
        assert "observability_version" in updated["extraction_info"]
        assert updated["extraction_info"]["observability_version"] == 1

    def test_add_observability_with_shadow(self):
        """Test adding observability data with shadow results."""
        result = {
            "file": {"path": "/test.jpg"},
            "extraction_info": {},
        }
        shadow_info = {
            "enabled": True,
            "duration_seconds": 0.5,
            "result": {"extra_field": 123},
            "error": None,
        }

        updated = add_observability_to_result(
            result=result,
            provenance={},
            conflicts=[],
            shadow_info=shadow_info,
        )

        shadow_summary = updated["extraction_info"]["shadow"]["image_master"]
        assert shadow_summary["enabled"] is True
        assert shadow_summary["duration_seconds"] == 0.5
        assert shadow_summary.get("diff") is not None

    def test_add_observability_shadow_error(self):
        """Test handling shadow mode errors gracefully."""
        result = {
            "file": {"path": "/test.jpg"},
            "extraction_info": {},
        }
        shadow_info = {
            "enabled": True,
            "duration_seconds": 0.1,
            "error": "Timeout exceeded",
        }

        updated = add_observability_to_result(
            result=result,
            provenance={},
            conflicts=[],
            shadow_info=shadow_info,
        )

        shadow_summary = updated["extraction_info"]["shadow"]["image_master"]
        assert shadow_summary["error"] == "Timeout exceeded"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
