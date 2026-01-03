"""
Exception classes for the MetaExtract extraction system.

This module defines a hierarchy of exceptions that can occur during
metadata extraction operations, providing detailed error information
and context for debugging and error handling.
"""

from typing import Any, Dict, Optional, List


class MetaExtractException(Exception):
    """
    Base exception for all MetaExtract errors.
    
    Provides standardized error information including error codes,
    context, and suggested actions for recovery.
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "GENERIC_ERROR",
        context: Optional[Dict[str, Any]] = None,
        suggested_action: Optional[str] = None,
        recoverable: bool = True,
        severity: str = "error"
    ):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            error_code: Standardized error code
            context: Additional context information
            suggested_action: Suggested action for recovery
            recoverable: Whether the error is recoverable
            severity: Error severity (info, warning, error, critical)
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.suggested_action = suggested_action
        self.recoverable = recoverable
        self.severity = severity
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "suggested_action": self.suggested_action,
            "recoverable": self.recoverable,
            "severity": self.severity
        }
    
    def __str__(self):
        """String representation of the exception."""
        details = f"[{self.error_code}] {self.message}"
        if self.context:
            details += f" Context: {self.context}"
        if self.suggested_action:
            details += f" Suggested action: {self.suggested_action}"
        return details


class ExtractionOrchestratorError(MetaExtractException):
    """Error during extraction orchestration."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "ORCHESTRATION_ERROR",
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            context=context,
            suggested_action="Check orchestrator configuration and extractor availability",
            **kwargs
        )


class ExtractorNotFoundError(MetaExtractException):
    """Requested extractor not found or not available."""
    
    def __init__(
        self,
        extractor_name: str,
        available_extractors: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Extractor '{extractor_name}' not found"
        if available_extractors:
            message += f". Available extractors: {', '.join(available_extractors)}"
        
        super().__init__(
            message=message,
            error_code="EXTRACTOR_NOT_FOUND",
            context=context or {"extractor_name": extractor_name},
            suggested_action="Check extractor name or install required dependencies",
            **kwargs
        )


class FileNotSupportedError(MetaExtractException):
    """File format is not supported by any extractor."""
    
    def __init__(
        self,
        filepath: str,
        file_format: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"File format not supported: {filepath}"
        if file_format:
            message += f" (format: {file_format})"
        
        super().__init__(
            message=message,
            error_code="FILE_NOT_SUPPORTED",
            context=context or {"filepath": filepath, "file_format": file_format},
            suggested_action="Check file format or install additional extractors",
            recoverable=False,
            **kwargs
        )


class ExtractionFailedError(MetaExtractException):
    """Metadata extraction failed during processing."""
    
    def __init__(
        self,
        message: str,
        extractor_name: Optional[str] = None,
        filepath: Optional[str] = None,
        original_error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        error_code = "EXTRACTION_FAILED"
        if extractor_name:
            error_code = f"EXTRACTION_FAILED_{extractor_name.upper()}"
        
        ctx = context or {}
        if extractor_name:
            ctx["extractor_name"] = extractor_name
        if filepath:
            ctx["filepath"] = filepath
        if original_error:
            ctx["original_error"] = str(original_error)
            ctx["original_error_type"] = type(original_error).__name__
        
        super().__init__(
            message=message,
            error_code=error_code,
            context=ctx,
            suggested_action="Check file integrity and extractor logs for details",
            **kwargs
        )


class ConfigurationError(MetaExtractException):
    """Configuration-related error."""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        ctx = context or {}
        if config_key:
            ctx["config_key"] = config_key
        
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            context=ctx,
            suggested_action="Check configuration settings and validation rules",
            **kwargs
        )


class ValidationError(MetaExtractException):
    """Validation error for input parameters or data."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        validation_rules: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        ctx = context or {}
        if field:
            ctx["field"] = field
        if value is not None:
            ctx["value"] = value
        if validation_rules:
            ctx["validation_rules"] = validation_rules
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            context=ctx,
            suggested_action="Check input parameters against validation rules",
            severity="warning",
            **kwargs
        )


class DependencyError(MetaExtractException):
    """Missing dependency or library error."""
    
    def __init__(
        self,
        missing_dependency: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Missing required dependency: {missing_dependency}"
        
        super().__init__(
            message=message,
            error_code="DEPENDENCY_ERROR",
            context=context or {"missing_dependency": missing_dependency},
            suggested_action=f"Install missing dependency: pip install {missing_dependency}",
            recoverable=False,
            **kwargs
        )


class TierLimitExceededError(MetaExtractException):
    """User tier limit exceeded error."""
    
    def __init__(
        self,
        tier: str,
        limit_type: str,
        current_value: Any,
        limit_value: Any,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Tier '{tier}' limit exceeded for {limit_type}: {current_value} > {limit_value}"
        
        super().__init__(
            message=message,
            error_code="TIER_LIMIT_EXCEEDED",
            context=context or {
                "tier": tier,
                "limit_type": limit_type,
                "current_value": current_value,
                "limit_value": limit_value
            },
            suggested_action="Upgrade to a higher tier or reduce request complexity",
            severity="warning",
            **kwargs
        )


class TimeoutError(MetaExtractException):
    """Operation timeout error."""
    
    def __init__(
        self,
        operation: str,
        timeout_seconds: float,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Operation '{operation}' timed out after {timeout_seconds} seconds"
        
        super().__init__(
            message=message,
            error_code="TIMEOUT_ERROR",
            context=context or {"operation": operation, "timeout_seconds": timeout_seconds},
            suggested_action="Increase timeout value or optimize operation performance",
            **kwargs
        )


class FileAccessError(MetaExtractException):
    """File access or permission error."""
    
    def __init__(
        self,
        filepath: str,
        access_type: str = "read",
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"File access error for '{filepath}': Cannot {access_type} file"
        
        super().__init__(
            message=message,
            error_code="FILE_ACCESS_ERROR",
            context=context or {"filepath": filepath, "access_type": access_type},
            suggested_action="Check file permissions and path accessibility",
            recoverable=False,
            **kwargs
        )