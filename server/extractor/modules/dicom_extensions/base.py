"""
Base classes and utilities for DICOM extension modules
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class DICOMExtensionError(Exception):
    """Base exception for DICOM extension errors"""
    pass


class DICOMFileValidationError(DICOMExtensionError):
    """Raised when DICOM file validation fails"""
    pass


class DICOMExtensionBase(ABC):
    """
    Abstract base class for all DICOM specialty extensions.

    All extension modules should inherit from this class and implement
    the required methods to provide consistent DICOM metadata extraction.
    """

    # Class attributes that must be defined by subclasses
    SPECIALTY: str = "unknown"
    FIELD_COUNT: int = 0
    REFERENCE: str = "DICOM Standard"
    DESCRIPTION: str = ""
    VERSION: str = "1.0.0"

    def __init__(self):
        """Initialize the DICOM extension"""
        if self.SPECIALTY == "unknown":
            raise DICOMExtensionError("Subclass must define SPECIALTY attribute")

        self._field_definitions: Optional[List[str]] = None
        self._cached_field_count: Optional[int] = None

    @abstractmethod
    def get_field_definitions(self) -> List[str]:
        """
        Get list of DICOM field names this extension can extract.

        Returns:
            List of DICOM field names (tag names or identifiers)
        """
        pass

    @abstractmethod
    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract specialty-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing:
                - specialty: str (specialty name)
                - fields_extracted: int (count)
                - metadata: dict (extracted fields and values)
                - extraction_time: float (seconds)
                - errors: list (any errors encountered)
        """
        pass

    def validate_dicom_file(self, filepath: str) -> bool:
        """
        Validate that the file is a readable DICOM file.

        Args:
            filepath: Path to file to validate

        Returns:
            True if valid DICOM file, False otherwise
        """
        try:
            path = Path(filepath)
            if not path.exists() or not path.is_file():
                logger.warning(f"File does not exist: {filepath}")
                return False

            import pydicom
            # Try to read with minimal validation
            pydicom.dcmread(filepath, stop_before_pixels=True, force=True)
            return True

        except Exception as e:
            logger.debug(f"DICOM validation failed for {filepath}: {e}")
            return False

    def get_field_count(self) -> int:
        """
        Get the number of fields this extension can extract.

        Returns:
            Number of extractable fields
        """
        if self._cached_field_count is None:
            self._cached_field_count = len(self.get_field_definitions())
        return self._cached_field_count

    def get_specialty_info(self) -> Dict[str, Any]:
        """
        Get information about this specialty extension.

        Returns:
            Dictionary with extension metadata
        """
        return {
            "specialty": self.SPECIALTY,
            "description": self.DESCRIPTION,
            "field_count": self.get_field_count(),
            "reference": self.REFERENCE,
            "version": self.VERSION,
            "class_name": self.__class__.__name__,
        }

    def log_extraction_summary(self, result: Dict[str, Any]) -> None:
        """
        Log a summary of the extraction results.

        Args:
            result: Result dictionary from extract_specialty_metadata
        """
        if result.get("fields_extracted", 0) > 0:
            logger.info(
                f"{self.SPECIALTY}: Extracted {result['fields_extracted']} fields "
                f"in {result.get('extraction_time', 0):.3f}s from {result.get('source_file', 'unknown')}"
            )

        if result.get("errors"):
            logger.warning(
                f"{self.SPECIALTY}: {len(result['errors'])} errors during extraction: "
                f"{result['errors'][:3]}"  # Log first 3 errors
            )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"specialty='{self.SPECIALTY}', "
            f"fields={self.get_field_count()}, "
            f"version='{self.VERSION}')"
        )


class DICOMExtractionResult:
    """
    Standardized result container for DICOM metadata extraction.
    """

    def __init__(
        self,
        specialty: str,
        source_file: str,
        fields_extracted: int,
        metadata: Dict[str, Any],
        extraction_time: float = 0.0,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
    ):
        self.specialty = specialty
        self.source_file = source_file
        self.fields_extracted = fields_extracted
        self.metadata = metadata
        self.extraction_time = extraction_time
        self.errors = errors or []
        self.warnings = warnings or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "specialty": self.specialty,
            "source_file": self.source_file,
            "fields_extracted": self.fields_extracted,
            "metadata": self.metadata,
            "extraction_time": self.extraction_time,
            "errors": self.errors,
            "warnings": self.warnings,
            "success": len(self.errors) == 0,
        }

    def is_successful(self) -> bool:
        """Check if extraction was successful"""
        return len(self.errors) == 0 and self.fields_extracted > 0


def safe_extract_dicom_field(dcm, field_name: str, default: Any = None) -> Any:
    """
    Safely extract a field from a DICOM object, handling common errors.

    Args:
        dcm: pydicom Dataset object
        field_name: Name of the field to extract
        default: Default value if field not found or error occurs

    Returns:
        Field value or default
    """
    try:
        if hasattr(dcm, field_name):
            value = getattr(dcm, field_name)
            # Convert DICOM values to strings for consistent handling
            if value is None:
                return default
            return str(value)
        return default
    except Exception as e:
        logger.debug(f"Error extracting DICOM field '{field_name}': {e}")
        return default


def get_dicom_file_info(filepath: str) -> Dict[str, Any]:
    """
    Get basic information about a DICOM file.

    Args:
        filepath: Path to DICOM file

    Returns:
        Dictionary with file information
    """
    try:
        import pydicom
        path = Path(filepath)

        dcm = pydicom.dcmread(filepath, stop_before_pixels=True, force=True)

        return {
            "file_path": str(path),
            "file_size": path.stat().st_size,
            "file_name": path.name,
            "sop_class_uid": safe_extract_dicom_field(dcm, "SOPClassUID"),
            "sop_instance_uid": safe_extract_dicom_field(dcm, "SOPInstanceUID"),
            "modality": safe_extract_dicom_field(dcm, "Modality"),
            "study_date": safe_extract_dicom_field(dcm, "StudyDate"),
            "series_description": safe_extract_dicom_field(dcm, "SeriesDescription"),
        }
    except Exception as e:
        logger.error(f"Error getting DICOM file info for {filepath}: {e}")
        return {
            "file_path": filepath,
            "error": str(e)
        }