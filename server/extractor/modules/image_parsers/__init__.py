"""
Image Format Parsers - Unified Architecture
===========================================

Format-specific parsers for all major image types:
- JPEG: ExifTool + native IFD parsing
- PNG: Chunk-based parsing (tEXt, zTXt, iTXt, ICC)
- GIF: Application extensions, comment extensions
- WebP: RIFF container, EXIF/XMP chunks
- TIFF: IFD-based tag parsing
- HEIC: MP4 box structure parsing
- AVIF: ISOBMFF/HEIF container, av01 codec
- PSD: Resource fork parsing
- SVG: XML metadata extraction
- BMP: DIB header parsing
- RAW: Camera-specific metadata (via ExifTool)

Key Principles:
1. Each parser extracts ONLY what the format supports
2. No synthetic/placeholder modules
3. Proper field counting (non-null leaf values only)
4. ExifTool as canonical parser where available
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import subprocess
import struct
import json

logger = logging.getLogger(__name__)

try:
    from ...utils.field_counting import (
        count_meaningful_fields,
        DEFAULT_FIELD_COUNT_IGNORED_KEYS,
    )
except Exception:  # pragma: no cover
    count_meaningful_fields = None  # type: ignore[assignment]
    DEFAULT_FIELD_COUNT_IGNORED_KEYS = set()  # type: ignore[assignment]


class FormatParser(ABC):
    """Base class for all format-specific parsers."""
    
    FORMAT_NAME: str = "base"
    SUPPORTED_EXTENSIONS: List[str] = []
    CAN_USE_EXIFTOOL: bool = True
    
    @abstractmethod
    def parse(self, filepath: str) -> Dict[str, Any]:
        """Parse the image file and return metadata dict."""
        pass
    
    @abstractmethod
    def get_real_field_count(self, metadata: Dict[str, Any]) -> int:
        """Count only non-null leaf values, ignoring bookkeeping."""
        pass
    
    @abstractmethod
    def can_parse(self, filepath: str) -> bool:
        """Check if this parser can handle the file."""
        pass
    
    def _run_exiftool(self, filepath: str, args: List[str] = None) -> Optional[Dict[str, Any]]:
        """Run ExifTool and return parsed result."""
        if not self.CAN_USE_EXIFTOOL:
            return None
            
        try:
            cmd = ["/opt/homebrew/bin/exiftool", "-j", "-a", "-G1"]
            if args:
                cmd.extend(args)
            cmd.append(filepath)
            
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout)
                return data[0] if data else None
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
            logger.debug(f"ExifTool not available or failed: {e}")
        
        return None
    
    def _count_real_fields(self, data: Any, depth: int = 0, max_depth: int = 10) -> int:
        if count_meaningful_fields is None:
            return 0

        ignored = set(DEFAULT_FIELD_COUNT_IGNORED_KEYS)
        # In format parsers, `version` is often meaningful (e.g., SVG version); do not ignore it.
        ignored.discard("version")
        # Parser-local bookkeeping keys
        ignored |= {
            "analysis_type",
            "optimized_mode",
            "fallback_mode",
            "status",
            "cache_hits",
            "cache_misses",
            "cache_hit_rate",
            "performance_score",
        }
        return count_meaningful_fields(data, ignored_keys=ignored, max_depth=max_depth)
    
    def _has_real_data(self, data: Any) -> bool:
        """Check if data contains any real/meaningful content."""
        return self._count_real_fields(data) > 0


class ImageParserRegistry:
    """Registry of all available format parsers."""
    
    def __init__(self):
        self._parsers: Dict[str, FormatParser] = {}
        self._register_default_parsers()
    
    def _register_default_parsers(self):
        """Register all default format parsers."""
        from .jpeg_parser import JpegParser
        from .png_parser import PngParser
        from .gif_parser import GifParser
        from .bmp_parser import BmpParser
        from .webp_parser import WebpParser
        from .tiff_parser import TiffParser
        from .heic_parser import HeicParser
        from .avif_parser import AvifParser
        from .psd_parser import PsdParser
        from .svg_parser import SvgParser
        
        self.register(JpegParser())
        self.register(PngParser())
        self.register(GifParser())
        self.register(BmpParser())
        self.register(WebpParser())
        self.register(TiffParser())
        self.register(HeicParser())
        self.register(AvifParser())
        self.register(PsdParser())
        self.register(SvgParser())
        
        # Try to import specialized parsers
        try:
            from .dicom_parser import DicomParser
            self.register(DicomParser())
        except ImportError:
            logger.info("DICOM parser not available")
        
        try:
            from .fits_parser import FitsParser
            self.register(FitsParser())
        except ImportError:
            logger.info("FITS parser not available")

        # Try to import RAW parser (optional / dependency-gated)
        try:
            from .raw_parser import RawParser

            self.register(RawParser())
        except ImportError:
            logger.info("RAW parser not available")
    
    def register(self, parser: FormatParser):
        """Register a format parser."""
        for ext in parser.SUPPORTED_EXTENSIONS:
            self._parsers[ext.lower()] = parser
    
    def get_parser(self, filepath: str) -> Optional[FormatParser]:
        """Get the appropriate parser for a file."""
        ext = Path(filepath).suffix.lower()
        return self._parsers.get(ext)
    
    def get_all_parsers(self) -> List[FormatParser]:
        """Get all registered parsers."""
        return list(self._parsers.values())
    
    def get_supported_extensions(self) -> List[str]:
        """Get all supported file extensions."""
        return list(self._parsers.keys())


# Singleton instance
_registry: Optional[ImageParserRegistry] = None


def get_parser_registry() -> ImageParserRegistry:
    """Get the global parser registry."""
    global _registry
    if _registry is None:
        _registry = ImageParserRegistry()
    return _registry


def parse_image_metadata(filepath: str) -> Dict[str, Any]:
    """
    Unified entry point for parsing image metadata.
    
    Args:
        filepath: Path to the image file
        
    Returns:
        Dictionary containing:
        - format: Image format name
        - metadata: Extracted metadata
        - fields_extracted: Count of real fields
        - extraction_method: 'exiftool' or 'native'
        - supported: Whether format is supported
    """
    registry = get_parser_registry()
    parser = registry.get_parser(filepath)
    
    if not parser:
        return {
            "success": False,
            "format": "unknown",
            "supported": False,
            "error": f"Unsupported format: {Path(filepath).suffix}",
            "fields_extracted": 0,
            "metadata": {}
        }
    
    if not Path(filepath).exists():
        return {
            "success": False,
            "format": parser.FORMAT_NAME,
            "supported": True,
            "error": "File not found",
            "fields_extracted": 0,
            "metadata": {}
        }
    
    try:
        metadata = parser.parse(filepath)
        real_fields = parser.get_real_field_count(metadata)
        
        return {
            "success": True,
            "format": parser.FORMAT_NAME,
            "supported": True,
            "fields_extracted": real_fields,
            "metadata": metadata,
            "extraction_method": "exiftool" if parser.CAN_USE_EXIFTOOL else "native"
        }
    except Exception as e:
        logger.error(f"Parsing failed for {filepath}: {e}")
        return {
            "success": False,
            "format": parser.FORMAT_NAME if parser else "unknown",
            "supported": True,
            "error": str(e)[:200],
            "fields_extracted": 0,
            "metadata": {}
        }
