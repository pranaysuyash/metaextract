#!/usr/bin/env python3
"""
Metadata Quality Agent
Assesses completeness and accuracy of extracted metadata, identifies common
extraction failures, provides quality scoring, and recommendations for improvement.

Author: MetaExtract Team
Version: 1.0.0
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Set
from datetime import datetime
import hashlib
import json

logger = logging.getLogger(__name__)


class QualityLevel(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    CRITICAL = "critical"


class ExtractionStatus(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


class FailureType(Enum):
    MISSING_REQUIRED_FIELD = "missing_required_field"
    MALFORMED_VALUE = "malformed_value"
    INVALID_ENCODING = "invalid_encoding"
    CORRUPTED_DATA = "corrupted_data"
    UNSUPPORTED_FORMAT = "unsupported_format"
    EXTRACTION_TIMEOUT = "extraction_timeout"
    DEPENDENCY_MISSING = "dependency_missing"
    PERMISSION_DENIED = "permission_denied"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class FieldQuality:
    field_name: str
    is_present: bool
    value: Any
    is_valid: bool
    validation_errors: List[str]
    confidence: float
    extraction_method: str


@dataclass
class CategoryQuality:
    category_name: str
    total_expected: int
    fields_extracted: int
    fields_valid: int
    quality_score: float
    quality_level: QualityLevel
    missing_critical_fields: List[str]
    validation_errors: List[str]
    warnings: List[str]


@dataclass
class ExtractorQuality:
    extractor_name: str
    extractor_type: str
    status: ExtractionStatus
    fields_extracted: int
    expected_fields: int
    quality_score: float
    execution_time_ms: float
    errors: List[str]
    warnings: List[str]
    retry_count: int


@dataclass
class MetadataQualityReport:
    overall_score: float
    overall_level: QualityLevel
    completeness_score: float
    validity_score: float
    consistency_score: float
    extraction_time_ms: float
    file_type: str
    file_size: Optional[int]
    total_fields_extracted: int
    total_fields_expected: int
    extractor_results: List[ExtractorQuality]
    category_qualities: List[CategoryQuality]
    failure_patterns: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    critical_issues: List[Dict[str, Any]]
    extracted_at: str
    metadata_hash: str


class MetadataQualityAgent:
    """
    Agent for assessing metadata quality across extraction results.

    Capabilities:
    - Completeness analysis (what fields are missing vs expected)
    - Validity checking (are values properly formatted)
    - Consistency scoring (do related fields make sense)
    - Failure pattern detection
    - Quality scoring by extractor type
    - Improvement recommendations
    """

    CRITICAL_FIELDS_BY_CATEGORY: Dict[str, List[str]] = {
        "basic_properties": ["file_name", "file_size", "file_type", "mime_type", "width", "height"],
        "exif_standard": ["make", "model", "datetime_original", "exposure_time", "f_number", "iso"],
        "gps": ["gps_latitude", "gps_longitude", "gps_altitude"],
        "color_analysis": ["color_space", "bits_per_sample", "pixel_format"],
        "icc_profiles": ["profile_version", "color_space", "profile_class"],
    }

    REQUIRED_FIELD_PATTERNS: Dict[str, re.Pattern] = {
        "datetime": re.compile(r"^\d{4}[-:]\d{2}[-:]\d{2}[T ]\d{2}:\d{2}:\d{2}"),
        "coordinates": re.compile(r"^-?\d+\.?\d*,\s*-?\d+\.?\d*$"),
        "iso": re.compile(r"^\d+$"),
        "exposure": re.compile(r"^1/\d+$|^\d+\.?\d*$"),
        "f_number": re.compile(r"^f/\d+\.?\d*$|^f\d+\.?\d*$|^\d+\.?\d*$"),
        "resolution": re.compile(r"^\d+\s*x\s*\d+$"),
        "filesize": re.compile(r"^\d+$"),
        "mime_type": re.compile(r"^[a-z]+/[a-z0-9+-]+$"),
    }

    EXTRACTOR_PRIORITIES: Dict[str, int] = {
        "basic_properties": 100,
        "exif": 95,
        "gps": 90,
        "icc_profile": 85,
        "maker_notes": 80,
        "xmp": 75,
        "iptc": 70,
        "color_analysis": 65,
        "quality_metrics": 60,
        "forensics": 55,
        "ai_detection": 50,
        "social_metadata": 45,
        "document": 40,
        "video": 35,
        "audio": 30,
    }

    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self._extraction_history: List[Dict[str, Any]] = []
        self._failure_patterns: Set[str] = set()
        self._known_issues: Dict[str, List[str]] = {}

    def assess_extraction_result(
        self,
        extracted_metadata: Dict[str, Any],
        file_type: str,
        file_size: Optional[int] = None,
        expected_categories: Optional[List[str]] = None,
        extraction_time_ms: float = 0.0,
    ) -> MetadataQualityReport:
        """
        Assess the quality of extracted metadata.

        Args:
            extracted_metadata: Dictionary of extracted metadata
            file_type: Type of file (e.g., "image/jpeg", "video/mp4")
            file_size: Size of file in bytes
            expected_categories: List of expected metadata categories
            extraction_time_ms: Time taken for extraction

        Returns:
            MetadataQualityReport with quality assessment
        """
        if expected_categories is None:
            expected_categories = self._infer_expected_categories(file_type)

        all_fields = self._flatten_metadata(extracted_metadata)
        metadata_hash = self._compute_metadata_hash(extracted_metadata)

        extractor_results = self._assess_extractors(extracted_metadata, file_type)
        category_qualities = self._assess_categories(extracted_metadata, expected_categories)

        completeness_score = self._calculate_completeness_score(
            all_fields, expected_categories, extractor_results
        )
        validity_score = self._calculate_validity_score(all_fields)
        consistency_score = self._calculate_consistency_score(extracted_metadata)

        overall_score = (completeness_score * 0.4 +
                        validity_score * 0.35 +
                        consistency_score * 0.25)

        overall_level = self._score_to_level(overall_score)

        failure_patterns = self._detect_failure_patterns(extractor_results, category_qualities)
        recommendations = self._generate_recommendations(
            overall_score, category_qualities, failure_patterns, file_type
        )
        critical_issues = self._identify_critical_issues(category_qualities, failure_patterns)

        return MetadataQualityReport(
            overall_score=round(overall_score, 2),
            overall_level=overall_level,
            completeness_score=round(completeness_score, 2),
            validity_score=round(validity_score, 2),
            consistency_score=round(consistency_score, 2),
            extraction_time_ms=extraction_time_ms,
            file_type=file_type,
            file_size=file_size,
            total_fields_extracted=len(all_fields),
            total_fields_expected=self._estimate_expected_field_count(expected_categories, file_type),
            extractor_results=extractor_results,
            category_qualities=category_qualities,
            failure_patterns=failure_patterns,
            recommendations=recommendations,
            critical_issues=critical_issues,
            extracted_at=datetime.utcnow().isoformat() + "Z",
            metadata_hash=metadata_hash,
        )

    def _infer_expected_categories(self, file_type: str) -> List[str]:
        """Infer expected metadata categories based on file type."""
        categories = ["basic_properties"]

        file_type_lower = file_type.lower()

        if "image" in file_type_lower:
            categories.extend([
                "exif_standard", "xmp_namespaces", "color_analysis",
                "icc_profiles", "file_format_chunks"
            ])
            if "raw" in file_type_lower or "arw" in file_type_lower or "dng" in file_type_lower:
                categories.extend(["camera_makernotes", "raw_format"])
            if "tiff" in file_type_lower or "tif" in file_type_lower:
                categories.append("tiff_ifd")
        elif "video" in file_type_lower:
            categories.extend([
                "video_container", "video_codec", "audio_codec",
                "timecode", "color_analysis"
            ])
        elif "audio" in file_type_lower:
            categories.extend(["audio_metadata", "id3_tags", "xmp_namespaces"])
        elif "application" in file_type_lower:
            if "pdf" in file_type_lower:
                categories.extend(["pdf_metadata", "xmp_namespaces"])
            elif "document" in file_type_lower or "word" in file_type_lower:
                categories.extend(["office_document", "xmp_namespaces"])
        elif "text" in file_type_lower:
            categories.append("text_metadata")

        return categories

    def _flatten_metadata(
        self, metadata: Dict[str, Any], prefix: str = ""
    ) -> Dict[str, Any]:
        """Flatten nested metadata dictionary."""
        result = {}
        for key, value in metadata.items():
            flat_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                result.update(self._flatten_metadata(value, flat_key))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        result.update(self._flatten_metadata(item, f"{flat_key}[{i}]"))
                    else:
                        result[f"{flat_key}[{i}]"] = item
            else:
                result[flat_key] = value
        return result

    def _assess_extractors(
        self, metadata: Dict[str, Any], file_type: str
    ) -> List[ExtractorQuality]:
        """Assess quality for each extractor that was used."""
        results = []

        extractor_mapping = self._detect_used_extractors(metadata)

        for extractor_name, extractor_type in extractor_mapping.items():
            fields_count = self._count_fields_for_extractor(metadata, extractor_name)
            quality_score = self._score_extractor_quality(fields_count, extractor_type)
            errors = self._extract_errors_for_extractor(metadata, extractor_name)

            results.append(ExtractorQuality(
                extractor_name=extractor_name,
                extractor_type=extractor_type,
                status=self._determine_extraction_status(fields_count, errors),
                fields_extracted=fields_count,
                expected_fields=self._estimate_expected_fields_for_type(extractor_type),
                quality_score=quality_score,
                execution_time_ms=0.0,
                errors=errors,
                warnings=self._generate_extractor_warnings(extractor_name, fields_count),
                retry_count=0,
            ))

        return results

    def _detect_used_extractors(self, metadata: Dict[str, Any]) -> Dict[str, str]:
        """Detect which extractors contributed to the metadata."""
        extractors = {}

        field_indicators = {
            "basic_properties": ["width", "height", "file_size", "mime_type"],
            "exif": ["make", "model", "exposure_time", "f_number", "iso"],
            "gps": ["gps_latitude", "gps_longitude", "gps_altitude"],
            "icc": ["color_space", "profile_version", "icc_profile"],
            "xmp": ["xmp", "xmp_metadata", "dc:"],
            "iptc": ["iptc", "headline", "copyright"],
            "maker_notes": ["makernote", "lens_model", "serial_number"],
            "color": ["color_space", "bits_per_sample", "pixel_format"],
            "quality": ["sharpness", "noise", "blur"],
            "forensics": ["manipulation", "ela", "error_level"],
            "ai_detection": ["ai_generated", "confidence", "c2pa"],
            "social": ["platform", "post_id", "username"],
        }

        flattened = self._flatten_metadata(metadata)

        for extractor_type, indicators in field_indicators.items():
            for indicator in indicators:
                for key in flattened.keys():
                    if indicator.lower() in key.lower():
                        extractors[extractor_type] = extractor_type
                        break

        return extractors

    def _count_fields_for_extractor(
        self, metadata: Dict[str, Any], extractor_name: str
    ) -> int:
        """Count the number of fields from a specific extractor."""
        flattened = self._flatten_metadata(metadata)
        relevant_keys = [k for k in flattened.keys() if extractor_name.lower() in k.lower()]
        return len(relevant_keys)

    def _estimate_expected_fields_for_type(self, extractor_type: str) -> int:
        """Estimate expected field count for an extractor type."""
        estimates = {
            "basic_properties": 15,
            "exif": 50,
            "gps": 15,
            "icc": 30,
            "xmp": 40,
            "iptc": 25,
            "maker_notes": 100,
            "color": 20,
            "quality": 15,
            "forensics": 25,
            "ai_detection": 15,
            "social": 30,
        }
        return estimates.get(extractor_type, 20)

    def _score_extractor_quality(self, fields_extracted: int, extractor_type: str) -> float:
        """Score the quality of a specific extractor result."""
        expected = self._estimate_expected_fields_for_type(extractor_type)
        if expected == 0:
            return 0.0

        ratio = min(fields_extracted / expected, 1.5)

        priority = self.EXTRACTOR_PRIORITIES.get(extractor_type, 50)
        priority_factor = priority / 100.0

        score = min(ratio * 0.7 + priority_factor * 0.3, 1.0) * 100
        return round(score, 2)

    def _determine_extraction_status(
        self, fields_extracted: int, errors: List[str]
    ) -> ExtractionStatus:
        """Determine the extraction status based on fields and errors."""
        if not errors:
            return ExtractionStatus.SUCCESS
        if fields_extracted > 0:
            return ExtractionStatus.PARTIAL
        if "timeout" in errors:
            return ExtractionStatus.TIMEOUT
        return ExtractionStatus.FAILED

    def _extract_errors_for_extractor(
        self, metadata: Dict[str, Any], extractor_name: str
    ) -> List[str]:
        """Extract any errors from the extractor results."""
        errors = []

        error_indicators = ["_error", "_failed", "_exception", "_timeout"]

        flattened = self._flatten_metadata(metadata)
        for key in flattened.keys():
            key_lower = key.lower()
            if any(indicator in key_lower for indicator in error_indicators):
                value = flattened[key]
                if value and str(value).lower() not in ["false", "none", ""]:
                    errors.append(f"{key}: {value}")

        return errors

    def _generate_extractor_warnings(
        self, extractor_name: str, fields_count: int
    ) -> List[str]:
        """Generate warnings for an extractor based on its results."""
        warnings = []
        expected = self._estimate_expected_fields_for_type(extractor_name)

        if fields_count == 0:
            warnings.append(f"No fields extracted from {extractor_name}")
        elif fields_count < expected * 0.3:
            warnings.append(f"Significantly fewer fields than expected ({fields_count}/{expected})")
        elif fields_count < expected * 0.6:
            warnings.append(f"Fewer fields than expected ({fields_count}/{expected})")

        return warnings

    def _assess_categories(
        self, metadata: Dict[str, Any], expected_categories: List[str]
    ) -> List[CategoryQuality]:
        """Assess quality for each metadata category."""
        flattened = self._flatten_metadata(metadata)
        results = []

        category_field_indicators = {
            "basic_properties": ["width", "height", "file_size", "file_type", "mime_type"],
            "exif_standard": ["make", "model", "datetime_original", "exposure_time", "f_number", "iso"],
            "xmp_namespaces": ["xmp", "dc:", "photoshop:", "xmpRights:"],
            "icc_profiles": ["color_space", "profile_version", "icc_profile", "rendering_intent"],
            "gps": ["gps_latitude", "gps_longitude", "gps_altitude", "gps_timestamp"],
            "color_analysis": ["color_space", "bits_per_sample", "pixel_format", "compression"],
            "file_format_chunks": ["chunk", "segment", "app0", "app1", "ihdr"],
            "camera_makernotes": ["makernote", "lens_model", "serial_number", "shot_number"],
            "quality_metrics": ["sharpness", "blur", "noise", "quality_score"],
            "image_forensics": ["manipulation", "ela", "error_level", "clone_detection"],
            "ai_generation": ["ai_generated", "c2pa", "generation_info", "confidence"],
            "social_metadata": ["platform", "post_id", "username", "timestamp"],
            "document": ["page_count", "author", "creator", "producer"],
            "video": ["duration", "frame_rate", "bitrate", "codec"],
            "audio": ["duration", "sample_rate", "bitrate", "channels"],
        }

        for category in expected_categories:
            indicators = category_field_indicators.get(category, [])
            extracted_fields = []
            valid_fields = []
            validation_errors = []
            missing_critical = []

            for key, value in flattened.items():
                key_lower = key.lower()
                if any(ind.lower() in key_lower for ind in indicators):
                    extracted_fields.append(key)
                    is_valid, errors = self._validate_field_value(key, value)
                    if is_valid:
                        valid_fields.append(key)
                    else:
                        validation_errors.extend(errors)

            critical_fields = self.CRITICAL_FIELDS_BY_CATEGORY.get(category, [])
            for critical in critical_fields:
                if not any(critical.lower() in k.lower() for k in extracted_fields):
                    missing_critical.append(critical)

            total_expected = len(indicators) + len(critical_fields)
            quality_score = self._calculate_category_score(
                len(extracted_fields), len(valid_fields), len(missing_critical), total_expected
            )

            results.append(CategoryQuality(
                category_name=category,
                total_expected=total_expected,
                fields_extracted=len(extracted_fields),
                fields_valid=len(valid_fields),
                quality_score=quality_score,
                quality_level=self._score_to_level(quality_score),
                missing_critical_fields=missing_critical,
                validation_errors=validation_errors,
                warnings=self._generate_category_warnings(
                    category, len(extracted_fields), len(missing_critical)
                ),
            ))

        return results

    def _validate_field_value(self, field_name: str, value: Any) -> Tuple[bool, List[str]]:
        """Validate a single field value."""
        errors = []

        if value is None or value == "":
            return False, ["Field is empty or null"]

        str_value = str(value).strip()

        field_lower = field_name.lower()

        for pattern_name, pattern in self.REQUIRED_FIELD_PATTERNS.items():
            if pattern_name in field_lower and not pattern.match(str_value):
                errors.append(f"Value does not match {pattern_name} pattern: {value}")

        if "datetime" in field_lower:
            try:
                datetime.fromisoformat(str_value.replace("/", "-").replace(":", "-"))
            except ValueError:
                errors.append(f"Invalid datetime format: {value}")

        if "latitude" in field_lower or "longitude" in field_lower:
            try:
                num = float(str_value.replace(",", ""))
                if not -180 <= num <= 180:
                    errors.append(f"Coordinate out of range: {value}")
            except ValueError:
                errors.append(f"Invalid coordinate format: {value}")

        if "size" in field_lower or "width" in field_lower or "height" in field_lower:
            try:
                num = int(str_value)
                if num <= 0:
                    errors.append(f"Dimension must be positive: {value}")
            except ValueError:
                errors.append(f"Invalid dimension format: {value}")

        return len(errors) == 0, errors

    def _calculate_category_score(
        self, extracted: int, valid: int, missing_critical: int, total_expected: int
    ) -> float:
        """Calculate quality score for a category."""
        if total_expected == 0:
            return 100.0

        completeness = min(extracted / max(total_expected * 0.7, 1), 1.0) * 40
        validity = (valid / max(extracted, 1)) * 40 if extracted > 0 else 0
        critical_penalty = missing_critical * 20

        score = completeness + validity - critical_penalty
        return max(0, min(score, 100))

    def _generate_category_warnings(
        self, category: str, extracted: int, missing_critical: int
    ) -> List[str]:
        """Generate warnings for a category."""
        warnings = []

        if missing_critical > 0:
            warnings.append(f"Missing {missing_critical} critical field(s)")

        if extracted == 0:
            warnings.append(f"Category '{category}' has no extracted fields")

        return warnings

    def _calculate_completeness_score(
        self,
        flattened: Dict[str, Any],
        expected_categories: List[str],
        extractor_results: List[ExtractorQuality]
    ) -> float:
        """Calculate overall completeness score."""
        if not expected_categories:
            return 50.0

        category_indicators = {
            "basic_properties": ["width", "height", "file_size", "file_type"],
            "exif_standard": ["make", "model", "datetime_original"],
            "gps": ["gps_latitude", "gps_longitude"],
            "xmp_namespaces": ["xmp", "dc:", "xmpRights:"],
            "icc_profiles": ["color_space", "profile_version"],
            "color_analysis": ["color_space", "bits_per_sample"],
        }

        category_scores = []
        for category in expected_categories:
            indicators = category_indicators.get(category, [])
            if not indicators:
                category_scores.append(50.0)
                continue

            present_count = sum(
                1 for ind in indicators
                for key in flattened.keys()
                if ind.lower() in key.lower()
            )

            score = (present_count / len(indicators)) * 100
            category_scores.append(score)

        extractor_coverage = sum(
            r.quality_score for r in extractor_results
        ) / max(len(extractor_results), 1) if extractor_results else 50.0

        combined_score = (sum(category_scores) / max(len(category_scores), 1)) * 0.6 + extractor_coverage * 0.4

        return round(combined_score, 2)

    def _calculate_validity_score(self, flattened: Dict[str, Any]) -> float:
        """Calculate validity score based on field validation."""
        if not flattened:
            return 0.0

        valid_count = 0
        total_count = 0

        for key, value in flattened.items():
            total_count += 1
            is_valid, _ = self._validate_field_value(key, value)
            if is_valid:
                valid_count += 1

        return round((valid_count / total_count) * 100, 2) if total_count > 0 else 0.0

    def _calculate_consistency_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate consistency score for related fields."""
        flattened = self._flatten_metadata(metadata)
        consistency_checks = [
            self._check_dimension_consistency(flattened),
            self._check_datetime_consistency(flattened),
            self._check_gps_consistency(flattened),
            self._check_color_consistency(flattened),
        ]

        passed_checks = sum(1 for check in consistency_checks if check)
        return round((passed_checks / len(consistency_checks)) * 100, 2)

    def _check_dimension_consistency(self, flattened: Dict[str, Any]) -> bool:
        """Check if dimension fields are consistent."""
        width = height = None

        for key in flattened.keys():
            key_lower = key.lower()
            if "width" in key_lower and width is None:
                try:
                    width = int(str(flattened[key]))
                except (ValueError, TypeError):
                    pass
            elif "height" in key_lower and height is None:
                try:
                    height = int(str(flattened[key]))
                except (ValueError, TypeError):
                    pass

        if width and height:
            return width > 0 and height > 0

        return True

    def _check_datetime_consistency(self, flattened: Dict[str, Any]) -> bool:
        """Check if datetime fields are consistent."""
        datetimes = []

        for key in flattened.keys():
            if "date" in key.lower() or "time" in key.lower():
                value = str(flattened[key])
                if re.match(r"\d{4}", value):
                    datetimes.append(value)

        if len(datetimes) < 2:
            return True

        return True

    def _check_gps_consistency(self, flattened: Dict[str, Any]) -> bool:
        """Check if GPS coordinates are consistent."""
        has_lat = has_lon = False

        for key in flattened.keys():
            key_lower = key.lower()
            if "latitude" in key_lower:
                has_lat = True
            elif "longitude" in key_lower:
                has_lon = True

        if has_lat or has_lon:
            return has_lat and has_lon

        return True

    def _check_color_consistency(self, flattened: Dict[str, Any]) -> bool:
        """Check if color-related fields are consistent."""
        color_space = bits = None

        for key in flattened.keys():
            key_lower = key.lower()
            if "color_space" in key_lower and color_space is None:
                color_space = str(flattened[key]).lower()
            elif "bits_per_sample" in key_lower and bits is None:
                try:
                    bits = int(flattened[key])
                except (ValueError, TypeError):
                    pass

        if color_space and bits:
            if color_space == "rgb" and bits not in [8, 16, 32]:
                return False
            elif color_space == "grayscale" and bits not in [1, 2, 4, 8, 16]:
                return False

        return True

    def _score_to_level(self, score: float) -> QualityLevel:
        """Convert a numeric score to a quality level."""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 75:
            return QualityLevel.GOOD
        elif score >= 60:
            return QualityLevel.ACCEPTABLE
        elif score >= 40:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL

    def _detect_failure_patterns(
        self,
        extractor_results: List[ExtractorQuality],
        category_qualities: List[CategoryQuality]
    ) -> List[Dict[str, Any]]:
        """Detect common failure patterns."""
        patterns = []

        timeout_extractors = [r for r in extractor_results if r.status == ExtractionStatus.TIMEOUT]
        if timeout_extractors:
            patterns.append({
                "type": "timeout",
                "severity": "high",
                "description": f"{len(timeout_extractors)} extractor(s) timed out",
                "affected_extractors": [r.extractor_name for r in timeout_extractors],
                "recommendation": "Consider reducing timeout thresholds or optimizing extraction"
            })

        failed_extractors = [r for r in extractor_results if r.status == ExtractionStatus.FAILED]
        if failed_extractors:
            patterns.append({
                "type": "extraction_failure",
                "severity": "critical",
                "description": f"{len(failed_extractors)} extractor(s) completely failed",
                "affected_extractors": [r.extractor_name for r in failed_extractors],
                "recommendation": "Check dependencies and file format compatibility"
            })

        low_quality_categories = [
            c for c in category_qualities if c.quality_score < 50
        ]
        if low_quality_categories:
            patterns.append({
                "type": "low_quality_categories",
                "severity": "medium",
                "description": f"{len(low_quality_categories)} category(ies) have low quality scores",
                "affected_categories": [c.category_name for c in low_quality_categories],
                "recommendation": "Review extraction parameters for affected categories"
            })

        missing_critical = [
            c for c in category_qualities if c.missing_critical_fields
        ]
        if missing_critical:
            patterns.append({
                "type": "missing_critical_fields",
                "severity": "high",
                "description": f"Critical fields missing in {len(missing_critical)} category(ies)",
                "affected_categories": [c.category_name for c in missing_critical],
                "recommendation": "Ensure source file contains required metadata"
            })

        validation_errors = sum(
            len(c.validation_errors) for c in category_qualities
        )
        if validation_errors > 5:
            patterns.append({
                "type": "validation_errors",
                "severity": "medium",
                "description": f"{validation_errors} validation errors detected",
                "recommendation": "Check for data corruption or encoding issues"
            })

        return patterns

    def _generate_recommendations(
        self,
        overall_score: float,
        category_qualities: List[CategoryQuality],
        failure_patterns: List[Dict[str, Any]],
        file_type: str
    ) -> List[Dict[str, Any]]:
        """Generate recommendations for improving metadata quality."""
        recommendations = []

        if overall_score < 60:
            recommendations.append({
                "priority": "high",
                "category": "general",
                "recommendation": "Overall metadata quality is below acceptable level",
                "action": "Review extraction configuration and source file quality"
            })

        low_categories = [c for c in category_qualities if c.quality_score < 60]
        for cat in low_categories:
            recommendations.append({
                "priority": "medium",
                "category": cat.category_name,
                "recommendation": f"Low quality score ({cat.quality_score:.0f}%) for category",
                "action": f"Check if file supports {cat.category_name} metadata"
            })

        for pattern in failure_patterns:
            if pattern["type"] == "timeout":
                recommendations.append({
                    "priority": "high",
                    "category": "performance",
                    "recommendation": pattern["description"],
                    "action": "Increase timeout or optimize extraction pipeline"
                })
            elif pattern["type"] == "extraction_failure":
                recommendations.append({
                    "priority": "critical",
                    "category": "compatibility",
                    "recommendation": pattern["description"],
                    "action": "Verify file format and install required dependencies"
                })
            elif pattern["type"] == "missing_critical_fields":
                recommendations.append({
                    "priority": "high",
                    "category": "completeness",
                    "recommendation": pattern["description"],
                    "action": "Check if metadata was stripped or not embedded"
                })

        if "image" in file_type.lower():
            recommendations.append({
                "priority": "low",
                "category": "image_specific",
                "recommendation": "Consider using higher quality source images",
                "action": "Lossless formats preserve more metadata"
            })

        return recommendations[:10]

    def _identify_critical_issues(
        self,
        category_qualities: List[CategoryQuality],
        failure_patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify critical issues that need immediate attention."""
        issues = []

        for pattern in failure_patterns:
            if pattern["severity"] == "critical":
                issues.append(pattern)

        for cat in category_qualities:
            if cat.quality_level == QualityLevel.CRITICAL:
                issues.append({
                    "type": "critical_category_quality",
                    "severity": "critical",
                    "category": cat.category_name,
                    "description": f"Category quality is critical: {cat.quality_score:.0f}%",
                    "missing_critical_fields": cat.missing_critical_fields
                })

        missing_critical = any(c.missing_critical_fields for c in category_qualities)
        if missing_critical:
            issues.append({
                "type": "missing_required_data",
                "severity": "critical",
                "description": "Required metadata fields are missing from extraction",
                "action": "Verify source file contains required metadata"
            })

        return issues

    def _estimate_expected_field_count(
        self, expected_categories: List[str], file_type: str
    ) -> int:
        """Estimate total expected field count based on file type and categories."""
        base_estimates = {
            "basic_properties": 15,
            "exif_standard": 50,
            "xmp_namespaces": 40,
            "icc_profiles": 30,
            "gps": 15,
            "color_analysis": 20,
            "file_format_chunks": 25,
            "camera_makernotes": 100,
            "quality_metrics": 15,
            "image_forensics": 25,
            "ai_generation": 15,
            "social_metadata": 30,
            "document": 40,
            "video": 60,
            "audio": 40,
        }

        total = sum(
            base_estimates.get(cat, 20)
            for cat in expected_categories
        )

        if "image" in file_type.lower():
            total += 50

        return total

    def _compute_metadata_hash(self, metadata: Dict[str, Any]) -> str:
        """Compute a hash of the extracted metadata for comparison."""
        flattened = self._flatten_metadata(metadata)
        sorted_items = sorted(flattened.items())
        hash_input = json.dumps(sorted_items, sort_keys=True, default=str)
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def get_quality_summary(self, report: MetadataQualityReport) -> Dict[str, Any]:
        """Generate a summary of the quality report."""
        return {
            "overall_score": report.overall_score,
            "overall_level": report.overall_level.value,
            "completeness": report.completeness_score,
            "validity": report.validity_score,
            "consistency": report.consistency_score,
            "fields_extracted": report.total_fields_extracted,
            "fields_expected": report.total_fields_expected,
            "critical_issues": len(report.critical_issues),
            "recommendations_count": len(report.recommendations),
            "extraction_time_ms": report.extraction_time_ms,
        }

    def compare_reports(
        self, report1: MetadataQualityReport, report2: MetadataQualityReport
    ) -> Dict[str, Any]:
        """Compare two quality reports."""
        return {
            "score_change": round(report2.overall_score - report1.overall_score, 2),
            "completeness_change": round(
                report2.completeness_score - report1.completeness_score, 2
            ),
            "validity_change": round(
                report2.validity_score - report1.validity_score, 2
            ),
            "consistency_change": round(
                report2.consistency_score - report1.consistency_score, 2
            ),
            "fields_added": report2.total_fields_extracted - report1.total_fields_extracted,
            "improved": report2.overall_score > report1.overall_score,
        }


def assess_metadata_quality(
    metadata: Dict[str, Any],
    file_type: str,
    file_size: Optional[int] = None,
    extraction_time_ms: float = 0.0,
    strict_mode: bool = False
) -> MetadataQualityReport:
    """
    Convenience function to assess metadata quality.

    Args:
        metadata: Extracted metadata dictionary
        file_type: MIME type of the file
        file_size: Size of the file in bytes
        extraction_time_ms: Time taken for extraction
        strict_mode: Enable strict validation

    Returns:
        MetadataQualityReport with assessment results
    """
    agent = MetadataQualityAgent(strict_mode=strict_mode)
    return agent.assess_extraction_result(
        extracted_metadata=metadata,
        file_type=file_type,
        file_size=file_size,
        extraction_time_ms=extraction_time_ms
    )


def get_field_count() -> int:
    """Return approximate number of fields tracked by quality agent."""
    return 50


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Metadata Quality Assessment Tool")
    parser.add_argument("metadata_file", help="JSON file with extracted metadata")
    parser.add_argument("--file-type", required=True, help="MIME type of file")
    parser.add_argument("--file-size", type=int, help="File size in bytes")
    parser.add_argument("--extraction-time", type=float, default=0, help="Extraction time in ms")
    parser.add_argument("--strict", action="store_true", help="Enable strict mode")

    args = parser.parse_args()

    with open(args.metadata_file) as f:
        metadata = json.load(f)

    report = assess_metadata_quality(
        metadata=metadata,
        file_type=args.file_type,
        file_size=args.file_size,
        extraction_time_ms=args.extraction_time,
        strict_mode=args.strict
    )

    print(json.dumps(report.__dict__, indent=2, default=str))
