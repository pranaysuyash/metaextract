"""
Core extraction engine components for MetaExtract.

This module provides the foundational classes and interfaces for the
metadata extraction system, including base extractors, orchestrators,
and context management.
"""

from .base_engine import BaseExtractor, ExtractionContext, ExtractionResult
from .orchestrator import ExtractionOrchestrator

__all__ = [
    'BaseExtractor',
    'ExtractionContext', 
    'ExtractionResult',
    'ExtractionOrchestrator'
]