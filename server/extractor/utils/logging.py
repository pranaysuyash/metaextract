"""
MetaExtract Structured Logging Module

Provides consistent, structured logging across all Python modules.
Replaces print() statements with proper logging that supports:
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Structured JSON output for production
- Human-readable output for development
- Context enrichment (module, function, file being processed)
- Performance timing
"""

import logging
import json
import sys
import os
import time
import traceback
from datetime import datetime
from typing import Any, Dict, Optional, Union
from functools import wraps
from contextlib import contextmanager


# ============================================================================
# Custom Log Formatter for JSON Output
# ============================================================================

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging in production."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info) if record.exc_info[2] else None
            }

        # Add any extra fields
        if hasattr(record, "extra_fields"):
            log_data["context"] = record.extra_fields

        return json.dumps(log_data, default=str)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for development console output."""

    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)

        # Format the base message
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        level = f"{color}{record.levelname:8}{self.RESET}"
        name = f"\033[90m{record.name}\033[0m"
        message = record.getMessage()

        formatted = f"{timestamp} | {level} | {name} | {message}"

        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{color}{self._formatException(record.exc_info)}{self.RESET}"

        return formatted


# ============================================================================
# Logger Factory
# ============================================================================

_loggers: Dict[str, logging.Logger] = {}


def get_logger(
    name: str,
    level: Optional[int] = None,
    json_output: bool = False
) -> logging.Logger:
    """
    Get or create a logger with the given name.

    Args:
        name: Logger name (typically module name)
        level: Log level (defaults to environment variable LOG_LEVEL or INFO)
        json_output: Whether to use JSON format (for production)

    Returns:
        Configured logger instance
    """
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)

    # Determine log level
    if level is None:
        level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
        level = getattr(logging, level_str, logging.INFO)

    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Create handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    # Choose formatter based on environment
    if json_output or os.environ.get("LOG_FORMAT") == "json":
        formatter = JSONFormatter()
    else:
        formatter = ColoredFormatter()

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Don't propagate to root logger
    logger.propagate = False

    _loggers[name] = logger
    return logger


# ============================================================================
# Convenience Functions
# ============================================================================

# Default logger for the metaextract module
_default_logger = None

def _get_default_logger() -> logging.Logger:
    global _default_logger
    if _default_logger is None:
        _default_logger = get_logger("metaextract")
    return _default_logger


def debug(message: str, **kwargs: Any) -> None:
    """Log a debug message."""
    _get_default_logger().debug(message, extra={"extra_fields": kwargs} if kwargs else {})


def info(message: str, **kwargs: Any) -> None:
    """Log an info message."""
    _get_default_logger().info(message, extra={"extra_fields": kwargs} if kwargs else {})


def warning(message: str, **kwargs: Any) -> None:
    """Log a warning message."""
    _get_default_logger().warning(message, extra={"extra_fields": kwargs} if kwargs else {})


def error(message: str, exc_info: bool = False, **kwargs: Any) -> None:
    """Log an error message."""
    _get_default_logger().error(message, exc_info=exc_info, extra={"extra_fields": kwargs} if kwargs else {})


def critical(message: str, exc_info: bool = False, **kwargs: Any) -> None:
    """Log a critical message."""
    _get_default_logger().critical(message, exc_info=exc_info, extra={"extra_fields": kwargs} if kwargs else {})


# ============================================================================
# Decorators and Context Managers
# ============================================================================

def log_execution_time(logger: Optional[logging.Logger] = None, level: int = logging.DEBUG):
    """
    Decorator to log function execution time.

    Usage:
        @log_execution_time()
        def my_function():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log = logger or _get_default_logger()
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed = (time.perf_counter() - start) * 1000
                log.log(level, f"{func.__name__} completed in {elapsed:.2f}ms")
                return result
            except Exception as e:
                elapsed = (time.perf_counter() - start) * 1000
                log.error(f"{func.__name__} failed after {elapsed:.2f}ms: {e}")
                raise
        return wrapper
    return decorator


@contextmanager
def log_context(operation: str, logger: Optional[logging.Logger] = None, **context):
    """
    Context manager for logging operation start/end with timing.

    Usage:
        with log_context("extracting EXIF", file=filepath):
            # do extraction
            pass
    """
    log = logger or _get_default_logger()
    start = time.perf_counter()

    context_str = ", ".join(f"{k}={v}" for k, v in context.items())
    log.debug(f"Starting: {operation}" + (f" ({context_str})" if context_str else ""))

    try:
        yield
        elapsed = (time.perf_counter() - start) * 1000
        log.debug(f"Completed: {operation} ({elapsed:.2f}ms)")
    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000
        log.error(f"Failed: {operation} after {elapsed:.2f}ms - {e}")
        raise


class LogCapture:
    """
    Capture log messages for testing or inspection.

    Usage:
        with LogCapture() as capture:
            logger.info("test message")
        assert "test message" in capture.messages
    """

    def __init__(self, logger_name: str = "metaextract"):
        self.logger_name = logger_name
        self.messages: list[str] = []
        self.records: list[logging.LogRecord] = []
        self._handler: Optional[logging.Handler] = None

    def __enter__(self):
        class CaptureHandler(logging.Handler):
            def __init__(self, capture: 'LogCapture'):
                super().__init__()
                self.capture = capture

            def emit(self, record: logging.LogRecord):
                self.capture.messages.append(record.getMessage())
                self.capture.records.append(record)

        self._handler = CaptureHandler(self)
        logging.getLogger(self.logger_name).addHandler(self._handler)
        return self

    def __exit__(self, *args):
        if self._handler:
            logging.getLogger(self.logger_name).removeHandler(self._handler)


# ============================================================================
# Extraction-Specific Logging
# ============================================================================

class ExtractionLogger:
    """
    Specialized logger for metadata extraction operations.
    Tracks extraction progress and provides structured output.
    """

    def __init__(self, filepath: str, tier: str = "enterprise"):
        self.filepath = filepath
        self.tier = tier
        self.logger = get_logger(f"metaextract.extraction")
        self.start_time = time.perf_counter()
        self.modules_processed: list[str] = []
        self.errors: list[Dict[str, Any]] = []
        self.fields_extracted = 0

    def start(self) -> None:
        """Log extraction start."""
        self.start_time = time.perf_counter()
        self.logger.info(
            f"Starting extraction",
            extra={"extra_fields": {
                "file": os.path.basename(self.filepath),
                "tier": self.tier
            }}
        )

    def module_start(self, module_name: str) -> None:
        """Log module extraction start."""
        self.logger.debug(f"Processing module: {module_name}")

    def module_complete(self, module_name: str, field_count: int = 0) -> None:
        """Log module extraction complete."""
        self.modules_processed.append(module_name)
        self.fields_extracted += field_count
        self.logger.debug(f"Completed module: {module_name} ({field_count} fields)")

    def module_error(self, module_name: str, error: Exception) -> None:
        """Log module extraction error."""
        self.errors.append({
            "module": module_name,
            "error": str(error),
            "type": type(error).__name__
        })
        self.logger.warning(f"Error in module {module_name}: {error}")

    def complete(self) -> Dict[str, Any]:
        """Log extraction complete and return summary."""
        elapsed_ms = (time.perf_counter() - self.start_time) * 1000

        summary = {
            "file": os.path.basename(self.filepath),
            "tier": self.tier,
            "elapsed_ms": round(elapsed_ms, 2),
            "modules_processed": len(self.modules_processed),
            "fields_extracted": self.fields_extracted,
            "errors": len(self.errors)
        }

        self.logger.info(
            f"Extraction complete: {self.fields_extracted} fields in {elapsed_ms:.2f}ms",
            extra={"extra_fields": summary}
        )

        return summary


# ============================================================================
# Migration Helper
# ============================================================================

def migrate_print_to_log(message: str, level: str = "info") -> None:
    """
    Helper function to replace print() calls during migration.
    Maps to appropriate log level.

    Usage:
        # Replace: print(f"Processing {file}")
        # With: migrate_print_to_log(f"Processing {file}")
    """
    log_func = {
        "debug": debug,
        "info": info,
        "warning": warning,
        "error": error,
        "critical": critical
    }.get(level.lower(), info)

    log_func(message)


# Export public API
__all__ = [
    "get_logger",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "log_execution_time",
    "log_context",
    "LogCapture",
    "ExtractionLogger",
    "migrate_print_to_log",
    "JSONFormatter",
    "ColoredFormatter",
]
