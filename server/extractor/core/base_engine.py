"""
Base extraction engine for MetaExtract.

Provides the foundational abstract base class for all metadata extractors
and defines the standard interface for extraction operations.
"""

import logging
import traceback
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

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
        Extract metadata from a file.
        
        Args:
            context: Extraction context containing file information
            
        Returns:
            ExtractionResult containing metadata and status
        """
        start_time = time.time()
        
        try:
            if not self.can_extract(context.filepath):
                return ExtractionResult(
                    metadata={},
                    status=ExtractionStatus.SKIPPED,
                    processing_time_ms=(time.time() - start_time) * 1000,
                    error_message=f"File format not supported by {self.name}"
                )
            
            # Call the abstract extraction method
            metadata = self._extract_metadata(context)
            
            processing_time = (time.time() - start_time) * 1000
            
            return ExtractionResult(
                metadata=metadata or {},
                status=ExtractionStatus.SUCCESS,
                processing_time_ms=processing_time,
                extraction_info={
                    "extractor": self.name,
                    "file_type": context.file_extension,
                    "tier": context.tier
                }
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            error_msg = f"Extraction failed in {self.name}: {str(e)}"
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            return ExtractionResult(
                metadata={},
                status=ExtractionStatus.FAILED,
                processing_time_ms=processing_time,
                error_message=error_msg,
                extraction_info={
                    "extractor": self.name,
                    "error_type": type(e).__name__,
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
        for lib_name in self.required_libraries:
            try:
                __import__(lib_name)
                availability[lib_name] = True
            except ImportError:
                availability[lib_name] = False
                self.logger.warning(f"Required library '{lib_name}' not available for {self.name}")
        
        return availability
    
    def is_available(self) -> bool:
        """
        Check if this specialized extractor is available.
        
        Returns:
            True if all required libraries are available
        """
        return all(self._libraries_available.values())
    
    def can_extract(self, filepath: str) -> bool:
        """
        Check if this extractor can handle the file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            True if available and file format is supported
        """
        if not self.is_available():
            return False
            
        return super().can_extract(filepath)