# Context Detection Engine
# Provides intelligent file context detection for dynamic UI adaptation

from .detector import ContextDetector, detect_file_context
from .profiles import CONTEXT_PROFILES, get_profile_for_context
from .analyzer import FileTypeAnalyzer, MetadataPatternAnalyzer

__all__ = [
    'ContextDetector',
    'detect_file_context',
    'CONTEXT_PROFILES',
    'get_profile_for_context',
    'FileTypeAnalyzer',
    'MetadataPatternAnalyzer',
]
