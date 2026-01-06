"""
Base extraction engine for MetaExtract.

Provides the foundational abstract base class for all metadata extractors
and defines the standard interface for extraction operations.
"""

import logging
import traceback
import time
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Import custom exceptions
try:
    from ..exceptions.extraction_exceptions import (
        MetaExtractException, 
        ExtractionFailedError, 
        FileNotSupportedError,
        DependencyError,
        FileAccessError,
        ValidationError
    )
    EXTRACTION_EXCEPTIONS_AVAILABLE = True
except ImportError:
    # Fallback to basic exceptions if custom ones not available
    class MetaExtractException(Exception):
        pass
    class ExtractionFailedError(MetaExtractException):
        pass
    class FileNotSupportedError(MetaExtractException):
        pass
    class DependencyError(MetaExtractException):
        pass
    class FileAccessError(MetaExtractException):
        pass
    class ValidationError(MetaExtractException):
        pass
    EXTRACTION_EXCEPTIONS_AVAILABLE = False

logger = logging.getLogger(__name__)


class ExtractionStatus(Enum):
    """Status of metadata extraction operations."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ExtractionContext:
    """Context information for metadata extraction."""
    filepath: str
    file_size: int
    file_extension: str
    mime_type: str
    tier: str
    processing_options: Dict[str, Any]
    execution_stats: Dict[str, Any]
    
    def __post_init__(self):
        """Initialize default values."""
        if self.processing_options is None:
            self.processing_options = {}
        if self.execution_stats is None:
            self.execution_stats = {}


@dataclass
class ExtractionResult:
    """Result of metadata extraction operation."""
    metadata: Dict[str, Any]
    status: ExtractionStatus
    processing_time_ms: float
    error_message: Optional[str] = None
    warnings: List[str] = None
    extraction_info: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.warnings is None:
            self.warnings = []
        if self.extraction_info is None:
            self.extraction_info = {}


class BaseExtractor(ABC):
    """
    Abstract base class for all metadata extractors.
    
    Provides a standard interface for metadata extraction operations
    and common functionality for error handling, logging, and result formatting.
    """
    
    def __init__(self, name: str, supported_formats: List[str] = None):
        """
        Initialize the extractor.
        
        Args:
            name: Name of the extractor
            supported_formats: List of supported file extensions
        """
        self.name = name
        self.supported_formats = supported_formats or []
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    def can_extract(self, filepath: str) -> bool:
        """
        Check if this extractor can handle the given file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            True if the extractor can handle this file type
        """
        if not self.supported_formats:
            return True  # Assume universal if no specific formats defined
            
        file_ext = Path(filepath).suffix.lower()
        return file_ext in self.supported_formats
    
    def extract(self, context: ExtractionContext) -> ExtractionResult:
        """
        Extract metadata from a file with comprehensive error handling.
        
        Args:
            context: Extraction context containing file information
            
        Returns:
            ExtractionResult containing metadata and status
            
        Raises:
            ValidationError: If context validation fails
            FileAccessError: If file cannot be accessed
            FileNotSupportedError: If file format is not supported
            ExtractionFailedError: If extraction process fails
        """
        start_time = time.time()
        
        # Validate context first
        try:
            validation_warnings = self.validate_context(context)
            if validation_warnings:
                self.logger.warning(f"Validation warnings for {context.filepath}: {validation_warnings}")
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            error_msg = f"Context validation failed in {self.name}: {str(e)}"
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            if EXTRACTION_EXCEPTIONS_AVAILABLE:
                raise ValidationError(
                    message=error_msg,
                    field="context",
                    value=str(context),
                    context={"extractor": self.name, "filepath": context.filepath}
                ) from e
            else:
                return ExtractionResult(
                    metadata={},
                    status=ExtractionStatus.FAILED,
                    processing_time_ms=processing_time,
                    error_message=error_msg,
                    extraction_info={
                        "extractor": self.name,
                        "error_type": "ValidationError",
                        "file_type": context.file_extension
                    }
                )
        
        # Check file accessibility
        try:
            file_path = Path(context.filepath)
            if not file_path.exists():
                error_msg = f"File does not exist: {context.filepath}"
                if EXTRACTION_EXCEPTIONS_AVAILABLE:
                    raise FileAccessError(
                        filepath=context.filepath,
                        access_type="read",
                        context={"extractor": self.name}
                    )
                else:
                    processing_time = (time.time() - start_time) * 1000
                    return ExtractionResult(
                        metadata={},
                        status=ExtractionStatus.FAILED,
                        processing_time_ms=processing_time,
                        error_message=error_msg,
                        extraction_info={
                            "extractor": self.name,
                            "error_type": "FileAccessError",
                            "file_type": context.file_extension
                        }
                    )
            
            # Check file permissions
            if not os.access(context.filepath, os.R_OK):
                error_msg = f"No read permission for file: {context.filepath}"
                if EXTRACTION_EXCEPTIONS_AVAILABLE:
                    raise FileAccessError(
                        filepath=context.filepath,
                        access_type="read",
                        context={"extractor": self.name, "error": "permission_denied"}
                    )
                else:
                    processing_time = (time.time() - start_time) * 1000
                    return ExtractionResult(
                        metadata={},
                        status=ExtractionStatus.FAILED,
                        processing_time_ms=processing_time,
                        error_message=error_msg,
                        extraction_info={
                            "extractor": self.name,
                            "error_type": "FileAccessError",
                            "file_type": context.file_extension
                        }
                    )
        
        except FileAccessError:
            # Re-raise FileAccessError as it's already properly formatted
            raise
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            error_msg = f"File access check failed in {self.name}: {str(e)}"
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            if EXTRACTION_EXCEPTIONS_AVAILABLE:
                raise FileAccessError(
                    filepath=context.filepath,
                    access_type="check",
                    context={"extractor": self.name, "original_error": str(e)}
                ) from e
            else:
                return ExtractionResult(
                    metadata={},
                    status=ExtractionStatus.FAILED,
                    processing_time_ms=processing_time,
                    error_message=error_msg,
                    extraction_info={
                        "extractor": self.name,
                        "error_type": "FileAccessError",
                        "file_type": context.file_extension
                    }
                )
        
        # Check format support
        if not self.can_extract(context.filepath):
            error_msg = f"File format not supported by {self.name}: {context.file_extension}"
            if EXTRACTION_EXCEPTIONS_AVAILABLE:
                raise FileNotSupportedError(
                    filepath=context.filepath,
                    file_format=context.file_extension,
                    context={"extractor": self.name}
                )
            else:
                processing_time = (time.time() - start_time) * 1000
                return ExtractionResult(
                    metadata={},
                    status=ExtractionStatus.SKIPPED,
                    processing_time_ms=processing_time,
                    error_message=error_msg,
                    extraction_info={
                        "extractor": self.name,
                        "error_type": "FileNotSupportedError",
                        "file_type": context.file_extension
                    }
                )
        
        # Perform the actual extraction with comprehensive error handling
        try:
            # Call the abstract extraction method
            metadata = self._extract_metadata(context)
            
            processing_time = (time.time() - start_time) * 1000
            
            # Validate extracted metadata
            if metadata is None:
                metadata = {}
            
            return ExtractionResult(
                metadata=metadata,
                status=ExtractionStatus.SUCCESS,
                processing_time_ms=processing_time,
                warnings=validation_warnings if validation_warnings else [],
                extraction_info={
                    "extractor": self.name,
                    "file_type": context.file_extension,
                    "tier": context.tier,
                    "success": True
                }
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            error_msg = f"Extraction failed in {self.name}: {str(e)}"
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            # Enhanced error classification
            error_type = type(e).__name__
            error_category = self._classify_error(e)
            
            if EXTRACTION_EXCEPTIONS_AVAILABLE:
                raise ExtractionFailedError(
                    message=error_msg,
                    extractor_name=self.name,
                    filepath=context.filepath,
                    original_error=e,
                    context={
                        "error_category": error_category,
                        "file_type": context.file_extension,
                        "tier": context.tier
                    }
                ) from e
            else:
                return ExtractionResult(
                    metadata={},
                    status=ExtractionStatus.FAILED,
                    processing_time_ms=processing_time,
                    error_message=error_msg,
                    extraction_info={
                        "extractor": self.name,
                        "error_type": error_type,
                        "error_category": error_category,
                        "file_type": context.file_extension
                    }
                )
    
    @abstractmethod
    def _extract_metadata(self, context: ExtractionContext) -> Dict[str, Any]:
        """
        Abstract method to perform the actual metadata extraction.
        
        Args:
            context: Extraction context
            
        Returns:
            Dictionary containing extracted metadata
        """
        pass
    
    def validate_context(self, context: ExtractionContext) -> List[str]:
        """
        Validate the extraction context.
        
        Args:
            context: Extraction context to validate
            
        Returns:
            List of validation warnings (empty if valid)
        """
        warnings = []
        
        if not Path(context.filepath).exists():
            warnings.append(f"File does not exist: {context.filepath}")
        
        if not self.can_extract(context.filepath):
            warnings.append(f"File format may not be fully supported: {context.file_extension}")
        
        return warnings
    
    def get_extraction_info(self) -> Dict[str, Any]:
        """
        Get information about this extractor.
        
        Returns:
            Dictionary with extractor information
        """
        return {
            "name": self.name,
            "supported_formats": self.supported_formats,
            "version": "1.0.0"
        }
    
    def _classify_error(self, exception: Exception) -> str:
        """
        Classify an exception into error categories for better handling.
        
        Args:
            exception: The exception to classify
            
        Returns:
            String representing the error category
        """
        error_type = type(exception).__name__
        
        # File-related errors
        if error_type in ['FileNotFoundError', 'PermissionError', 'IsADirectoryError', 'NotADirectoryError']:
            return 'file_system'
        
        # Memory-related errors
        elif error_type in ['MemoryError', 'OutOfMemoryError']:
            return 'memory'
        
        # Data format errors
        elif error_type in ['ValueError', 'TypeError', 'AttributeError', 'KeyError', 'IndexError']:
            return 'data_format'
        
        # Library/dependency errors
        elif error_type in ['ImportError', 'ModuleNotFoundError']:
            return 'dependency'
        
        # Network/IO errors
        elif error_type in ['IOError', 'OSError', 'ConnectionError', 'TimeoutError']:
            return 'io_network'
        
        # Parsing errors
        elif error_type in ['JSONDecodeError', 'XMLSyntaxError', 'ConfigParserError']:
            return 'parsing'
        
        # Custom MetaExtract exceptions
        elif hasattr(exception, 'error_code'):
            return 'metaextract_specific'
        
        # All other errors
        else:
            return 'unknown'


class SpecializedExtractor(BaseExtractor):
    """
    Base class for specialized extractors (medical, astronomical, etc.).
    
    Provides additional functionality for domain-specific extraction.
    """
    
    def __init__(self, name: str, domain: str, required_libraries: List[str] = None):
        """
        Initialize specialized extractor.
        
        Args:
            name: Name of the extractor
            domain: Domain name (medical, astronomical, etc.)
            required_libraries: List of required library names
        """
        super().__init__(name)
        self.domain = domain
        self.required_libraries = required_libraries or []
        self._libraries_available = self._check_library_availability()
    
    def _check_library_availability(self) -> Dict[str, bool]:
        """Check availability of required libraries."""
        availability = {}
        missing_libraries = []
        
        for lib_name in self.required_libraries:
            try:
                __import__(lib_name)
                availability[lib_name] = True
            except ImportError as e:
                availability[lib_name] = False
                missing_libraries.append(lib_name)
                self.logger.warning(f"Required library '{lib_name}' not available for {self.name}: {str(e)}")
        
        # Raise dependency error if any libraries are missing and exceptions are available
        if missing_libraries and EXTRACTION_EXCEPTIONS_AVAILABLE:
            for lib_name in missing_libraries:
                raise DependencyError(
                    missing_dependency=lib_name,
                    context={
                        "extractor": self.name,
                        "domain": self.domain,
                        "all_missing": missing_libraries
                    }
                )
        
        return availability
    
    def is_available(self) -> bool:
        """
        Check if this specialized extractor is available.
        
        Returns:
            True if all required libraries are available
            
        Raises:
            DependencyError: If required libraries are missing (when exceptions available)
        """
        return all(self._libraries_available.values())
    
    def can_extract(self, filepath: str) -> bool:
        """
        Check if this extractor can handle the file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            True if available and file format is supported
            
        Raises:
            DependencyError: If required libraries are missing (when exceptions available)
        """
        if not self.is_available():
            return False
            
        return super().can_extract(filepath)
    
    def get_dependency_status(self) -> Dict[str, Any]:
        """
        Get detailed dependency status information.
        
        Returns:
            Dictionary with dependency availability and missing libraries
        """
        return {
            "available": self.is_available(),
            "libraries_available": self._libraries_available,
            "missing_libraries": [lib for lib, available in self._libraries_available.items() if not available],
            "domain": self.domain
        }