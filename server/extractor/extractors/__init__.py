"""
Specialized metadata extractors for MetaExtract.

This module contains domain-specific extractors for different file types
and metadata domains, including images, videos, audio, documents, and
scientific formats.
"""

from .image_extractor import ImageExtractor
from .video_extractor import VideoExtractor

__all__ = [
    'ImageExtractor',
    'VideoExtractor'
]