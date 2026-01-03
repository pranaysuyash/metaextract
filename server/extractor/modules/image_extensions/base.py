"""
Base classes and utilities for image extension modules
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ImageExtensionError(Exception):
    """Base exception for image extension errors"""
    pass


class ImageFileValidationError(ImageExtensionError):
    """Raised when image file validation fails"""
    pass


class ImageExtractionResult:
    """
    Standardized result format for all image extraction operations.
    Similar to DICOM extension result format.
    """

    def __init__(self, source: str, filepath: str):
        self.source = source
        self.filepath = filepath
        self.start_time = time.time()
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.metadata: Dict[str, Any] = {}
        self.fields_extracted = 0
        self.extraction_time = 0.0

    def add_error(self, error: str):
        """Add an error message"""
        self.errors.append(error)
        logger.error(f"{self.source} extraction error: {error}")

    def add_warning(self, warning: str):
        """Add a warning message"""
        self.warnings.append(warning)
        logger.warning(f"{self.source} extraction warning: {warning}")

    def add_metadata(self, key: str, value: Any):
        """Add metadata field and increment counter with smart field counting"""
        self.metadata[key] = value
        # Smart field counting - count nested fields in dictionaries
        if isinstance(value, dict):
            # Count actual fields in the dictionary (excluding empty ones)
            nested_count = sum(1 for v in value.values() if v is not None and v != {} and v != [])
            self.fields_extracted += max(1, nested_count)  # At least 1 for the key itself
        elif isinstance(value, (list, tuple)) and value:
            # Count list items if they're not empty
            self.fields_extracted += len([v for v in value if v is not None and v != {} and v != []])
        else:
            # Single field
            self.fields_extracted += 1

    def add_metadata_dict(self, data: Dict[str, Any]):
        """Add multiple metadata fields"""
        for key, value in data.items():
            if value is not None and value != {} and value != []:
                self.metadata[key] = value
                self.fields_extracted += 1

    def finalize(self) -> Dict[str, Any]:
        """Finalize the extraction result and return as dictionary"""
        self.extraction_time = time.time() - self.start_time

        return {
            "source": self.source,
            "source_file": self.filepath,
            "fields_extracted": self.fields_extracted,
            "metadata": self.metadata,
            "extraction_time": self.extraction_time,
            "errors": self.errors,
            "warnings": self.warnings,
            "success": len(self.errors) == 0
        }

    def to_error_result(self, error: str) -> Dict[str, Any]:
        """Create error result when extraction fails completely"""
        self.add_error(error)
        return self.finalize()


class ImageExtensionBase(ABC):
    """
    Abstract base class for all image specialty extensions.

    All extension modules should inherit from this class and implement
    the required methods to provide consistent image metadata extraction.
    """

    # Class attributes that must be defined by subclasses
    SOURCE: str = "unknown"
    FIELD_COUNT: int = 0
    DESCRIPTION: str = ""
    VERSION: str = "1.0.0"
    CAPABILITIES: List[str] = []

    def __init__(self):
        """Initialize the image extension"""
        if self.SOURCE == "unknown":
            raise ImageExtensionError("Subclass must define SOURCE attribute")

        self._field_definitions: Optional[List[str]] = None
        self._cached_field_count: Optional[int] = None

    @abstractmethod
    def get_field_definitions(self) -> List[str]:
        """
        Get list of image field names this extension can extract.

        Returns:
            List of field names
        """
        pass

    @abstractmethod
    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract specialty-specific metadata from image file.

        Args:
            filepath: Path to image file

        Returns:
            Dictionary containing extraction results in standardized format
        """
        pass

    def validate_image_file(self, filepath: str) -> bool:
        """
        Validate that the file is a supported image format.

        Args:
            filepath: Path to file to validate

        Returns:
            True if valid image file, False otherwise
        """
        try:
            path = Path(filepath)
            if not path.exists():
                return False

            # Check file extension
            valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'}
            if path.suffix.lower() not in valid_extensions:
                return False

            # Try to open with PIL if available
            try:
                from PIL import Image
                with Image.open(filepath) as img:
                    img.verify()
                return True
            except Exception:
                return False

        except Exception as e:
            logger.error(f"Image validation failed for {filepath}: {e}")
            return False

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported image file formats.

        Returns:
            List of supported file extensions
        """
        return ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']

    def get_field_count(self) -> int:
        """
        Get the number of fields this extension can extract.

        Returns:
            Number of fields
        """
        if self._cached_field_count is None:
            self._cached_field_count = len(self.get_field_definitions())
        return self._cached_field_count

    def get_capability_description(self) -> str:
        """
        Get human-readable description of extension capabilities.

        Returns:
            Description string
        """
        return f"{self.DESCRIPTION} (Capabilities: {', '.join(self.CAPABILITIES)})"

    def log_extraction_summary(self, result: Dict[str, Any]) -> None:
        """
        Log a summary of the extraction operation.

        Args:
            result: Extraction result dictionary
        """
        success_indicator = "✅" if result.get("success", False) else "❌"
        logger.info(
            f"{success_indicator} {self.SOURCE} extraction: "
            f"{result['fields_extracted']} fields in "
            f"{result['extraction_time']:.4f}s - "
            f"File: {result['source_file']}"
        )

        if result.get("errors"):
            for error in result["errors"]:
                logger.error(f"  Error: {error}")

        if result.get("warnings"):
            for warning in result["warnings"]:
                logger.warning(f"  Warning: {warning}")


def safe_extract_image_field(data: Dict[str, Any], field: str, default: Any = None) -> Any:
    """
    Safely extract a field from image metadata dictionary.

    Args:
        data: Dictionary containing image metadata
        field: Field name to extract
        default: Default value if field not found

    Returns:
        Field value or default
    """
    if not isinstance(data, dict):
        return default

    # Support nested field access with dot notation
    if '.' in field:
        parts = field.split('.')
        current = data
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current

    return data.get(field, default)


def get_image_file_info(filepath: str) -> Dict[str, Any]:
    """
    Get basic image file information.

    Args:
        filepath: Path to image file

    Returns:
        Dictionary containing file information
    """
    try:
        path = Path(filepath)
        stat = path.stat()

        return {
            "filename": path.name,
            "extension": path.suffix,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "modified_timestamp": stat.st_mtime,
            "created_timestamp": stat.st_ctime
        }
    except Exception as e:
        return {"error": f"Failed to get file info: {str(e)[:100]}"}