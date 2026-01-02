"""
Image Extension Registry
Central registry for all image specialty extensions
"""

import logging
from typing import Dict, List, Optional, Type, Any
from pathlib import Path

from .base import ImageExtensionBase, ImageExtensionError, ImageExtractionResult

logger = logging.getLogger(__name__)


class ImageExtractionRegistry:
    """
    Central registry for managing image specialty extensions.
    Similar to DICOMExtensionRegistry but for image metadata extraction.
    """

    def __init__(self):
        self._extensions: Dict[str, Type[ImageExtensionBase]] = {}
        self._instances: Dict[str, ImageExtensionBase] = {}
        self._extraction_stats = {
            "total_extractions": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "total_fields_extracted": 0,
            "total_extraction_time": 0.0
        }

    def register_extension(
        self,
        extension_class: Type[ImageExtensionBase],
        override: bool = False
    ) -> None:
        """
        Register an image extension class.

        Args:
            extension_class: Extension class to register
            override: Whether to override existing registration

        Raises:
            ImageExtensionError: If source already registered and override=False
        """
        # Create temporary instance to get source info
        try:
            temp_instance = extension_class()
            source = temp_instance.SOURCE
        except Exception as e:
            raise ImageExtensionError(
                f"Failed to instantiate extension class {extension_class.__name__}: {e}"
            )

        if source in self._extensions and not override:
            raise ImageExtensionError(
                f"Source '{source}' already registered with {self._extensions[source].__name__}. "
                f"Use override=True to replace."
            )

        self._extensions[source] = extension_class
        logger.info(f"Registered image extension: {source} ({extension_class.__name__})")

    def get_extension(self, source: str) -> Optional[ImageExtensionBase]:
        """
        Get an instance of a registered extension.

        Args:
            source: Source name (e.g., 'basic', 'advanced', 'exif')

        Returns:
            Extension instance or None if not found
        """
        if source not in self._extensions:
            logger.warning(f"Extension not found for source: {source}")
            return None

        # Create and cache instance if not exists
        if source not in self._instances:
            try:
                self._instances[source] = self._extensions[source]()
            except Exception as e:
                logger.error(f"Failed to instantiate extension {source}: {e}")
                return None

        return self._instances[source]

    def get_all_extensions(self) -> List[str]:
        """
        Get list of all registered extension sources.

        Returns:
            List of source names
        """
        return list(self._extensions.keys())

    def get_extension_info(self, source: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a registered extension.

        Args:
            source: Source name

        Returns:
            Dictionary with extension info or None if not found
        """
        extension = self.get_extension(source)
        if not extension:
            return None

        return {
            "source": extension.SOURCE,
            "description": extension.DESCRIPTION,
            "field_count": extension.get_field_count(),
            "capabilities": extension.CAPABILITIES,
            "version": extension.VERSION,
            "supported_formats": extension.get_supported_formats()
        }

    def get_all_extensions_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all registered extensions.

        Returns:
            List of extension info dictionaries
        """
        info_list = []
        for source in self.get_all_extensions():
            info = self.get_extension_info(source)
            if info:
                info_list.append(info)
        return info_list

    def extract_with_extension(
        self,
        source: str,
        filepath: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract metadata using a specific extension.

        Args:
            source: Extension source name
            filepath: Path to image file

        Returns:
            Extraction result dictionary or None if extension not found
        """
        extension = self.get_extension(source)
        if not extension:
            logger.error(f"Cannot extract - extension '{source}' not found")
            return None

        try:
            result = extension.extract_specialty_metadata(filepath)

            # Update statistics
            self._extraction_stats["total_extractions"] += 1
            if result.get("success", False):
                self._extraction_stats["successful_extractions"] += 1
            else:
                self._extraction_stats["failed_extractions"] += 1

            self._extraction_stats["total_fields_extracted"] += result.get("fields_extracted", 0)
            self._extraction_stats["total_extraction_time"] += result.get("extraction_time", 0.0)

            return result

        except Exception as e:
            logger.error(f"Extraction failed with extension '{source}': {e}")
            self._extraction_stats["total_extractions"] += 1
            self._extraction_stats["failed_extractions"] += 1

            return {
                "source": source,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": 0.0,
                "errors": [f"Extraction failed: {str(e)}"],
                "warnings": [],
                "success": False
            }

    def extract_with_best_extension(
        self,
        filepath: str,
        preferred_tier: str = "advanced"
    ) -> Dict[str, Any]:
        """
        Automatically select and use the best available extension.

        Args:
            filepath: Path to image file
            preferred_tier: Preferred extraction tier ('basic', 'advanced', 'fallback')

        Returns:
            Extraction result dictionary
        """
        # Define extension priority by tier
        tier_priority = {
            "advanced": ["advanced", "exif", "master", "basic"],
            "basic": ["basic", "fallback"],
            "fallback": ["fallback"]
        }

        priority_list = tier_priority.get(preferred_tier, tier_priority["advanced"])

        # Try extensions in priority order
        for source in priority_list:
            if source in self._extensions:
                result = self.extract_with_extension(source, filepath)
                if result and result.get("success", False):
                    logger.info(f"Used {source} extension for {preferred_tier} tier extraction")
                    return result

        # If all preferred extensions failed, try any available extension
        for source in self._extensions:
            result = self.extract_with_extension(source, filepath)
            if result and result.get("success", False):
                logger.warning(f"Fallback to {source} extension for extraction")
                return result

        # No extension succeeded
        return {
            "source": "none",
            "source_file": filepath,
            "fields_extracted": 0,
            "metadata": {},
            "extraction_time": 0.0,
            "errors": ["No suitable extension found for this file"],
            "warnings": [],
            "success": False
        }

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for all extractions.

        Returns:
            Dictionary containing performance metrics
        """
        stats = self._extraction_stats.copy()

        if stats["total_extractions"] > 0:
            stats["success_rate"] = stats["successful_extractions"] / stats["total_extractions"]
            stats["avg_fields_per_extraction"] = stats["total_fields_extracted"] / stats["total_extractions"]
            stats["avg_extraction_time"] = stats["total_extraction_time"] / stats["total_extractions"]
        else:
            stats["success_rate"] = 0.0
            stats["avg_fields_per_extraction"] = 0.0
            stats["avg_extraction_time"] = 0.0

        return stats

    def reset_stats(self) -> None:
        """Reset performance statistics"""
        self._extraction_stats = {
            "total_extractions": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "total_fields_extracted": 0,
            "total_extraction_time": 0.0
        }

    def get_registry_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of registry state.

        Returns:
            Dictionary containing registry information
        """
        return {
            "registered_extensions": len(self._extensions),
            "extension_sources": self.get_all_extensions(),
            "extension_info": self.get_all_extensions_info(),
            "performance_stats": self.get_performance_stats()
        }


# Global registry instance
_global_registry: Optional[ImageExtractionRegistry] = None


def get_global_registry() -> ImageExtractionRegistry:
    """
    Get the global image extension registry instance.

    Returns:
        Global registry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ImageExtractionRegistry()
        logger.info("Created global image extension registry")
    return _global_registry


def reset_global_registry() -> None:
    """Reset the global registry instance"""
    global _global_registry
    _global_registry = None
    logger.info("Reset global image extension registry")