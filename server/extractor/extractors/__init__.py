"""
Specialized metadata extractors for MetaExtract.

This module contains domain-specific extractors for different file types
and metadata domains, including images, videos, audio, documents, and
scientific formats.
"""

from .image_extractor import ImageExtractor
from .video_extractor import VideoExtractor
from .audio_extractor import AudioExtractor
from .document_extractor import DocumentExtractor
from .enhanced_image_extractor import (
    EnhancedImageExtractor,
    BaseEngineEnhancedImageExtractor,
    extract_image_metadata
)
from .unified_image_extractor import (
    UnifiedImageExtractor,
    extract_image_metadata as unified_extract_image_metadata
)
from .registry_image_extractor import (
    RegistryImageExtractor,
    BaseEngineRegistryExtractor,
    extract_image_metadata as registry_extract_image_metadata
)

__all__ = [
    'ImageExtractor',
    'VideoExtractor',
    'AudioExtractor',
    'DocumentExtractor',
    'EnhancedImageExtractor',
    'BaseEngineEnhancedImageExtractor',
    'UnifiedImageExtractor',
    'RegistryImageExtractor',
    'BaseEngineRegistryExtractor',
    'extract_image_metadata',
    'unified_extract_image_metadata',
    'registry_extract_image_metadata'
]