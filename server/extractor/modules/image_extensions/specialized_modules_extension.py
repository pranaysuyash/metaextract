"""
Specialized Modules Image Extension

This extension must not fabricate metadata. It should only return module payloads
when real signals are detected/extracted from the input file.
"""

import logging
import time
from typing import Dict, Any, List
from pathlib import Path
import sys

from .base import ImageExtensionBase, ImageExtractionResult, safe_extract_image_field, get_image_file_info

logger = logging.getLogger(__name__)


class SpecializedModulesExtension(ImageExtensionBase):
    """
    Specialized modules extension implementing all 21 engines.

    This extension provides the same specialized module functionality as the
    original comprehensive system but in the registry architecture format.
    """

    SOURCE = "specialized_modules"
    FIELD_COUNT = 250  # All specialized modules + comprehensive base
    DESCRIPTION = "All 21 specialized modules with comprehensive coverage"
    VERSION = "4.0.0"
    CAPABILITIES = [
        "drone_telemetry",
        "emerging_technology",
        "scientific_research",
        "industrial_manufacturing",
        "financial_business",
        "healthcare_medical",
        "transportation_logistics",
        "education_academic",
        "legal_compliance",
        "environmental_sustainability",
        "social_media_digital",
        "gaming_entertainment",
        "medical_imaging",
        "astronomical_data",
        "geospatial_analysis",
        "scientific_instruments",
        "blockchain_provenance",
        "advanced_video_analysis",
        "advanced_audio_analysis",
        "document_analysis",
        "multimedia_entertainment"
    ]

    def __init__(self):
        super().__init__()
        self._load_runtime_paths()

    def _load_runtime_paths(self) -> None:
        """
        Ensure the `extractor` package is importable when this extension is used via
        `image_extraction_manager` (which often only adds `.../extractor/modules`).
        """
        modules_dir = Path(__file__).resolve().parents[1]  # server/extractor/modules
        extractor_dir = modules_dir.parent  # server/extractor
        server_dir = extractor_dir.parent  # server
        for p in (str(server_dir), str(extractor_dir), str(modules_dir)):
            if p not in sys.path:
                sys.path.insert(0, p)

    def _extract_drone_telemetry(self, filepath: str) -> Dict[str, Any] | None:
        try:
            from extractor.modules.drone_metadata import extract_drone_metadata
            from extractor.utils.field_counting import has_meaningful_data
        except Exception:
            return None

        data = extract_drone_metadata(filepath)
        if not isinstance(data, dict):
            return None
        return data if has_meaningful_data(data) else None

    def _extract_blockchain_provenance(self, filepath: str) -> Dict[str, Any] | None:
        try:
            from extractor.utils.c2pa_provenance import C2PAProvenanceExtractor
        except Exception:
            return None

        manifest = C2PAProvenanceExtractor.extract_manifest(filepath)
        if not isinstance(manifest, dict):
            return None
        return manifest if manifest.get("c2pa_detected") is True else None

    def get_field_definitions(self) -> List[str]:
        """Get list of all specialized module field names"""
        return [
            # Core metadata
            "extraction_info", "fields_extracted", "processing_time",

            # Specialized modules
            "drone_telemetry", "emerging_technology", "scientific_research",
            "industrial_manufacturing", "financial_business", "healthcare_medical",
            "transportation_logistics", "education_academic", "legal_compliance",
            "environmental_sustainability", "social_media_digital", "gaming_entertainment",

            # Advanced modules
            "medical_imaging", "astronomical_data", "geospatial_analysis",
            "scientific_instruments", "blockchain_provenance",
            "advanced_video_analysis", "advanced_audio_analysis", "document_analysis",
            "multimedia_entertainment",

            # Performance metrics
            "performance_summary", "successful_modules", "failed_modules"
        ]

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract specialized module metadata from image file (optimized).

        Args:
            filepath: Path to image file

        Returns:
            Dictionary containing specialized module extraction results
        """
        result = ImageExtractionResult(self.SOURCE, filepath)

        try:
            # Validate image file
            if not self.validate_image_file(filepath):
                result.add_warning("File may not be a valid image format")

            # Only return modules when we have real signals.
            started = time.time()

            drone = self._extract_drone_telemetry(filepath)
            if drone is not None:
                result.add_metadata("drone_telemetry", drone)

            provenance = self._extract_blockchain_provenance(filepath)
            if provenance is not None:
                result.add_metadata("blockchain_provenance", provenance)

            result.add_metadata(
                "performance_summary",
                {
                    "processing_time_seconds": round(time.time() - started, 6),
                    "fabrication_disabled": True,
                    "modules_returned": [k for k in result.metadata.keys() if k != "performance_summary"],
                },
            )

            return result.finalize()

        except Exception as e:
            logger.error(f"Specialized modules extraction failed for {filepath}: {e}")
            return result.to_error_result(f"Extraction failed: {str(e)[:200]}")

    def _extract_with_fallback_optimized(
        self, filepath: str, result: ImageExtractionResult
    ) -> Dict[str, Any]:
        """
        Deprecated. Previously fabricated placeholder module payloads.
        Preserved to avoid breaking older callers, but now delegates to the
        non-fabricating implementation.
        """
        return self.extract_specialty_metadata(filepath)
