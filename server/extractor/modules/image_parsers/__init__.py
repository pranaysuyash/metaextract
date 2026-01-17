"""
Image Format Parsers - Unified Architecture
============================================

Format-specific parsers for all major image types:
- JPEG: ExifTool + native IFD parsing
- PNG: Chunk-based parsing (tEXt, zTXt, iTXt, ICC)
- GIF: Application extensions, comment extensions
- WebP: RIFF container, EXIF/XMP chunks
- TIFF: IFD-based tag parsing
- HEIC/AVIF: MP4 box structure parsing
- PSD: Resource fork parsing
- SVG: XML metadata extraction
- RAW: Camera-specific metadata (CR2, NEF, ARW, etc.)

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
        """
        Count only non-null leaf values.
        
        Ignores:
        - Bookkeeping keys: source, errors, warnings, performance, extraction_info
        - Null/empty values
        - Placeholder values: 'unknown', 'N/A', None, {}, [], ""
        
        Counts:
        - Non-empty strings, numbers, booleans
        - Non-empty dicts with real data
        """
        if depth > max_depth:
            return 0
            
        # Bookkeeping keys to ignore
        bookkeeping_keys = {
            'source', 'errors', 'warnings', 'performance', 'extraction_info',
            'fields_extracted', 'available', 'analysis_type', 'optimized_mode',
            'fallback_mode', 'status', 'duration_seconds', 'cache_hits',
            'cache_misses', 'cache_hit_rate', 'performance_score'
        }
        
        if isinstance(data, dict):
            count = 0
            for key, value in data.items():
                # Skip bookkeeping keys
                if key in bookkeeping_keys:
                    continue
                # Skip keys that are just indicators
                if key.startswith('_'):
                    continue
                count += self._count_real_fields(value, depth + 1, max_depth)
            return count
            
        elif isinstance(data, list):
            count = 0
            for item in data:
                count += self._count_real_fields(item, depth + 1, max_depth)
            return count
            
        else:
            # It's a leaf value
            if data is None:
                return 0
            if isinstance(data, (str, bytes)):
                if not data or data in ['', b'', 'unknown', 'N/A', 'none', 'null']:
                    return 0
                return 1
            if isinstance(data, (int, float)):
                if data == 0:
                    return 0
                return 1
            if isinstance(data, bool):
                return 1 if data else 0
            return 0
    
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
        from .webp_parser import WebpParser
        from .tiff_parser import TiffParser
        from .heic_parser import HeicParser
        from .psd_parser import PsdParser
        from .svg_parser import SvgParser
        
        self.register(JpegParser())
        self.register(PngParser())
        self.register(GifParser())
        self.register(WebpParser())
        self.register(TiffParser())
        self.register(HeicParser())
        self.register(PsdParser())
        self.register(SvgParser())
        
        # Try to import RAW parser (requires additional dependencies)
        try:
            from .raw_parser import RawParser
            self.register(RawParser())
        except ImportError:
            logger.info("RAW parser not available (missing dependencies)")
    
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
