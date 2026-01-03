"""
Image Extraction Manager
Unified entry point for all image metadata extraction operations
"""

import logging
import time
from typing import Dict, Any, Optional, List
from pathlib import Path

import sys
import os
from pathlib import Path

# Add the modules directory to the path to import image_extensions
modules_dir = Path(__file__).parent
sys.path.insert(0, str(modules_dir))

from image_extensions import (
    get_global_registry,
    ImageExtractionResult
)

logger = logging.getLogger(__name__)


class ImageExtractionManager:
    """
    Main manager for image metadata extraction operations.

    Provides a unified interface for image extraction with automatic
    extension selection, fallback handling, and performance tracking.
    """

    def __init__(self):
        self.registry = get_global_registry()

    def extract_image_metadata(
        self,
        filepath: str,
        tier: str = "advanced",
        performance_tracking: bool = True
    ) -> Dict[str, Any]:
        """
        Extract metadata from image file using the best available extension.

        Args:
            filepath: Path to image file
            tier: Extraction tier ('basic', 'advanced', 'universal')
            performance_tracking: Whether to track performance metrics

        Returns:
            Dictionary containing extraction results with standardized format
        """
        start_time = time.time()

        try:
            # Validate input
            if not filepath or not Path(filepath).exists():
                return self._create_error_result(
                    filepath,
                    "File not found or invalid path",
                    tier
                )

            # Determine extraction strategy based on tier
            extraction_result = self.registry.extract_with_best_extension(
                filepath,
                preferred_tier=tier
            )

            # Add tier information
            extraction_result["requested_tier"] = tier
            extraction_result["actual_tier"] = extraction_result.get("source", tier)

            # Add performance tracking if requested
            if performance_tracking:
                total_time = time.time() - start_time
                extraction_result["total_processing_time"] = total_time
                extraction_result["performance_stats"] = self.registry.get_performance_stats()

            return extraction_result

        except Exception as e:
            logger.error(f"Image extraction manager failed for {filepath}: {e}")
            return self._create_error_result(
                filepath,
                f"Extraction manager error: {str(e)[:200]}",
                tier
            )

    def extract_with_specific_extension(
        self,
        filepath: str,
        extension_source: str
    ) -> Dict[str, Any]:
        """
        Extract metadata using a specific extension.

        Args:
            filepath: Path to image file
            extension_source: Name of extension to use ('basic', 'advanced', 'universal')

        Returns:
            Dictionary containing extraction results
        """
        try:
            result = self.registry.extract_with_extension(extension_source, filepath)

            if not result:
                return self._create_error_result(
                    filepath,
                    f"Extension '{extension_source}' not found or failed",
                    extension_source
                )

            result["requested_extension"] = extension_source
            return result

        except Exception as e:
            logger.error(f"Specific extension extraction failed: {e}")
            return self._create_error_result(
                filepath,
                f"Specific extension error: {str(e)[:200]}",
                extension_source
            )

    def batch_extract(
        self,
        filepaths: List[str],
        tier: str = "advanced",
        max_parallel: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Extract metadata from multiple image files.

        Args:
            filepaths: List of file paths to process
            tier: Extraction tier to use
            max_parallel: Maximum number of parallel extractions

        Returns:
            List of extraction results
        """
        results = []

        # For simplicity, process sequentially (can be enhanced with parallel processing)
        for filepath in filepaths:
            try:
                result = self.extract_image_metadata(filepath, tier)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch extraction failed for {filepath}: {e}")
                results.append(self._create_error_result(
                    filepath,
                    str(e)[:200],
                    tier
                ))

        return results

    def get_available_extensions(self) -> List[str]:
        """Get list of available extension sources"""
        return self.registry.get_all_extensions()

    def get_extension_info(self, source: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific extension"""
        return self.registry.get_extension_info(source)

    def get_all_extensions_info(self) -> List[Dict[str, Any]]:
        """Get information about all available extensions"""
        return self.registry.get_all_extensions_info()

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "registry_status": self.registry.get_registry_summary(),
            "available_extensions": self.get_available_extensions(),
            "extension_details": self.get_all_extensions_info()
        }

    def _create_error_result(
        self,
        filepath: str,
        error_message: str,
        tier: str
    ) -> Dict[str, Any]:
        """Create standardized error result"""
        return {
            "source": "manager",
            "source_file": filepath,
            "fields_extracted": 0,
            "metadata": {},
            "extraction_time": 0.0,
            "total_processing_time": 0.0,
            "requested_tier": tier,
            "actual_tier": "error",
            "errors": [error_message],
            "warnings": [],
            "success": False
        }

    def calculate_credit_cost(
        self,
        extraction_result: Dict[str, Any],
        base_cost: int = 1
    ) -> int:
        """
        Calculate appropriate credit cost based on extraction complexity.

        Args:
            extraction_result: Result from extract_image_metadata
            base_cost: Base credit cost

        Returns:
            Number of credits to charge
        """
        try:
            # Get file size from metadata
            file_size_mb = 0
            if "metadata" in extraction_result:
                file_info = extraction_result["metadata"].get("file_info", {})
                file_size_mb = file_info.get("size_mb", 0)

            # Get fields extracted
            fields_extracted = extraction_result.get("fields_extracted", 0)

            # Get tier used
            actual_tier = extraction_result.get("actual_tier", "basic")

            # Calculate cost
            tier_multiplier = {
                "advanced": 2.0,
                "basic": 1.0,
                "universal": 1.0,
                "fallback": 0.5
            }.get(actual_tier, 1.0)

            size_multiplier = 1.0
            if file_size_mb > 10:
                size_multiplier = 1.5
            elif file_size_mb > 20:
                size_multiplier = 2.0

            field_bonus = min(fields_extracted / 100, 1.0)

            final_cost = base_cost * tier_multiplier * size_multiplier + field_bonus

            return max(1, int(final_cost))  # Minimum 1 credit

        except Exception as e:
            logger.warning(f"Error calculating credit cost: {e}")
            return base_cost  # Fallback to base cost


# Singleton instance
_manager_instance: Optional[ImageExtractionManager] = None


def get_image_manager() -> ImageExtractionManager:
    """
    Get the global image extraction manager instance.

    Returns:
        Global manager instance
    """
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = ImageExtractionManager()
        logger.info("Created global image extraction manager")
    return _manager_instance


def extract_image_metadata(
    filepath: str,
    tier: str = "advanced",
    performance_tracking: bool = True
) -> Dict[str, Any]:
    """
    Convenience function for image metadata extraction.

    Args:
        filepath: Path to image file
        tier: Extraction tier ('basic', 'advanced', 'universal')
        performance_tracking: Whether to track performance metrics

    Returns:
        Dictionary containing extraction results
    """
    manager = get_image_manager()
    return manager.extract_image_metadata(filepath, tier, performance_tracking)