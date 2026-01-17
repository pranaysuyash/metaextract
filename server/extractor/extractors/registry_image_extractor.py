#!/usr/bin/env python3
"""
Registry-Based Image Extractor

This module provides a proper integration with the existing comprehensive
registry-based image extraction system.

Uses:
- image_extraction_manager (unified entry point)
- image_extensions registry (6+ extensions including enhanced_master)
- 48+ metadata categories with 300+ fields

Author: MetaExtract Team
Version: 5.0.0
"""

import logging
import sys
import os
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Add modules directory to path for registry imports
_MODULES_DIR = Path(__file__).parent / 'modules'
sys.path.insert(0, str(_MODULES_DIR))

try:
    from image_extensions import get_global_registry, ImageExtractionResult
    from image_extraction_manager import (
        extract_image_metadata as registry_extract,
        get_image_manager,
        ImageExtractionManager
    )
    REGISTRY_AVAILABLE = True
except ImportError as e:
    REGISTRY_AVAILABLE = False
    logger.warning(f"Registry system not available: {e}")


class RegistryImageExtractor:
    """
    Image extractor using the comprehensive registry system.
    
    Provides access to:
    - 6+ specialized extensions (basic, advanced, universal, complete_gps, specialized_modules, enhanced_master)
    - 48+ metadata categories
    - 300+ fields with data
    - Parallel extraction for performance
    """
    
    SUPPORTED_FORMATS = [
        '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.gif', '.bmp',
        '.webp', '.heic', '.heif', '.avif', '.psd',
        '.cr2', '.cr3', '.nef', '.arw', '.dng', '.orf', '.rw2', '.pef', '.x3f', '.sr2',
        '.dcm', '.dicom',
        '.fits', '.fts', '.h5',
        '.svg', '.exr',
    ]
    
    def __init__(self, tier: str = "advanced"):
        """Initialize the registry-based extractor."""
        self.tier = tier
        self.extraction_stats = {
            "registry_used": False,
            "fields_extracted": 0,
            "categories_covered": 0,
            "extensions_used": [],
            "errors": []
        }
        
        if REGISTRY_AVAILABLE:
            self.manager = get_image_manager()
            self.registry = self.manager.registry
        else:
            self.manager = None
            self.registry = None
    
    def can_extract(self, filepath: str) -> bool:
        """Check if we can extract from this file."""
        ext = Path(filepath).suffix.lower()
        return ext in self.SUPPORTED_FORMATS
    
    def extract(self, filepath: str) -> Dict[str, Any]:
        """
        Extract comprehensive metadata using the registry system.
        
        Args:
            filepath: Path to the image file
            
        Returns:
            Dictionary containing extracted metadata
        """
        if not os.path.exists(filepath):
            return self._error_result(filepath, "File not found")
        
        start_time = datetime.utcnow()
        
        try:
            if not REGISTRY_AVAILABLE or not self.manager:
                return self._fallback_extraction(filepath)
            
            # Use the registry system
            result = self.manager.extract_image_metadata(
                filepath,
                tier=self.tier,
                performance_tracking=True
            )
            
            # Transform result to our format
            return self._transform_result(result, filepath, start_time)
            
        except Exception as e:
            self.extraction_stats["errors"].append(str(e))
            logger.error(f"Registry extraction failed: {e}")
            return self._fallback_extraction(filepath)
    
    def _transform_result(
        self, 
        registry_result: Dict[str, Any], 
        filepath: str,
        start_time: datetime
    ) -> Dict[str, Any]:
        """Transform registry result to our standard format."""
        
        success = registry_result.get("success", False)
        metadata = registry_result.get("metadata", {})
        
        # Count fields with data
        def count_fields(d, depth=0):
            if depth > 10:
                return 0
            count = 0
            for k, v in d.items():
                if isinstance(v, dict) and v:
                    count += count_fields(v, depth + 1)
                elif v not in [None, {}, [], "", 0]:
                    count += 1
            return count
        
        fields_extracted = count_fields(metadata)
        categories_covered = len(metadata)
        
        # Get extensions used
        perf = registry_result.get("extraction_performance", {})
        extensions_used = perf.get("extensions_used", [])
        
        self.extraction_stats["registry_used"] = True
        self.extraction_stats["fields_extracted"] = fields_extracted
        self.extraction_stats["categories_covered"] = categories_covered
        self.extraction_stats["extensions_used"] = extensions_used
        
        # Build our result
        return {
            "file_info": self._build_file_info(filepath),
            "metadata": metadata,
            "surfaces": self._organize_surfaces(metadata),
            "normalized": self._normalize_metadata(metadata),
            "extraction_info": {
                "timestamp": start_time.isoformat() + "Z",
                "source": "registry_enhanced_master",
                "success": success,
                "registry_used": True,
                "fields_extracted": fields_extracted,
                "categories_covered": categories_covered,
                "extensions_used": extensions_used,
                "processing_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
                "errors": self.extraction_stats["errors"]
            }
        }
    
    def _build_file_info(self, filepath: str) -> Dict[str, Any]:
        """Build file information."""
        stat = os.stat(filepath)
        path = Path(filepath)
        
        return {
            "filename": path.name,
            "file_size_bytes": stat.st_size,
            "modified_timestamp": stat.st_mtime,
            "file_extension": path.suffix.lower(),
            "mime_type": self._get_mime_type(filepath)
        }
    
    def _get_mime_type(self, filepath: str) -> str:
        """Get MIME type based on extension."""
        ext = Path(filepath).suffix.lower()
        mime_map = {
            '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
            '.png': 'image/png', '.tiff': 'image/tiff',
            '.tif': 'image/tiff', '.gif': 'image/gif',
            '.bmp': 'image/bmp', '.webp': 'image/webp',
            '.heic': 'image/heic', '.heif': 'image/heif',
            '.avif': 'image/avif', '.psd': 'image/x-photoshop',
            '.dcm': 'application/dicom', '.dicom': 'application/dicom',
            '.svg': 'image/svg+xml', '.exr': 'image/openexr',
        }
        return mime_map.get(ext, 'application/octet-stream')
    
    def _organize_surfaces(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Organize metadata into standard surfaces."""
        surfaces = {}
        
        # Map registry categories to standard surfaces
        surface_mapping = {
            "exif": ["exif", "exif_advanced", "exif_camera", "exif_analysis_performance"],
            "iptc": ["iptc"],
            "xmp": ["xmp"],
            "gps": ["gps", "geospatial_analysis"],
            "icc": ["icc_profile"],
            "camera": ["camera_data"],
            "image": ["image_analysis", "image_quality_analysis", "technical_metadata"],
            "forensic": ["forensic", "perceptual_hashes"],
            "mobile": ["mobile_metadata"],
            "thumbnail": ["thumbnail"],
        }
        
        for surface, keys in surface_mapping.items():
            surface_data = {}
            for key in keys:
                if key in metadata and metadata[key]:
                    if isinstance(metadata[key], dict):
                        surface_data.update(metadata[key])
                    else:
                        surface_data[key] = metadata[key]
            if surface_data:
                surfaces[surface] = surface_data
        
        return surfaces
    
    def _normalize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize key metadata fields."""
        normalized = {}
        
        # GPS normalization
        if "gps" in metadata:
            gps = metadata["gps"]
            if isinstance(gps, dict):
                if gps.get("latitude") and gps.get("longitude"):
                    normalized["gps_decimal"] = {
                        "latitude": gps["latitude"],
                        "longitude": gps["longitude"],
                        "altitude": gps.get("altitude")
                    }
        
        # Basic dimensions
        if "width" in metadata and "height" in metadata:
            normalized["dimensions"] = {
                "width": metadata["width"],
                "height": metadata["height"],
                "megapixels": metadata.get("megapixels", 0)
            }
        
        return normalized
    
    def _fallback_extraction(self, filepath: str) -> Dict[str, Any]:
        """Fallback extraction using basic PIL."""
        result = {
            "file_info": self._build_file_info(filepath),
            "metadata": {},
            "surfaces": {},
            "normalized": {},
            "extraction_info": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "fallback_pil",
                "success": False,
                "registry_used": False,
                "fields_extracted": 0,
                "errors": ["Registry unavailable, fallback extraction failed"]
            }
        }
        
        # Try basic PIL extraction
        try:
            from PIL import Image
            with Image.open(filepath) as img:
                result["metadata"]["format"] = img.format
                result["metadata"]["mode"] = img.mode
                result["metadata"]["width"] = img.width
                result["metadata"]["height"] = img.height
                result["metadata"]["megapixels"] = round(img.width * img.height / 1_000_000, 2)
                result["extraction_info"]["success"] = True
                result["extraction_info"]["fields_extracted"] = 5
        except Exception as e:
            result["extraction_info"]["errors"].append(f"Fallback failed: {str(e)}")
        
        return result
    
    def _error_result(self, filepath: str, error: str) -> Dict[str, Any]:
        """Create error result."""
        return {
            "file_info": self._build_file_info(filepath) if os.path.exists(filepath) else {},
            "metadata": {},
            "surfaces": {},
            "normalized": {},
            "extraction_info": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "registry_error",
                "success": False,
                "registry_used": REGISTRY_AVAILABLE,
                "fields_extracted": 0,
                "errors": [error]
            }
        }
    
    def get_extraction_info(self) -> Dict[str, Any]:
        """Get extractor information."""
        return {
            "name": "RegistryImageExtractor",
            "version": "5.0.0",
            "supported_formats": len(self.SUPPORTED_FORMATS),
            "registry_available": REGISTRY_AVAILABLE,
            "extensions_available": self.manager.get_available_extensions() if self.manager else [],
            "tier": self.tier
        }


try:
    from ..core.base_engine import BaseExtractor, ExtractionContext
    BASE_ENGINE_AVAILABLE = True
except ImportError:
    BASE_ENGINE_AVAILABLE = False
    BaseExtractor = None
    ExtractionContext = None


class BaseEngineRegistryExtractor(BaseExtractor if BASE_ENGINE_AVAILABLE else object):
    """
    BaseExtractor wrapper for registry-based extraction.
    Used when running within the MetaExtract engine.
    """
    
    def __init__(self, tier: str = "advanced"):
        """Initialize with BaseExtractor interface."""
        if BASE_ENGINE_AVAILABLE:
            super().__init__(
                name="RegistryImageExtractor",
                supported_formats=RegistryImageExtractor.SUPPORTED_FORMATS
            )
        else:
            self.name = "RegistryImageExtractor"
            self.supported_formats = RegistryImageExtractor.SUPPORTED_FORMATS
            self.logger = logging.getLogger(f"{__name__}.RegistryImageExtractor")
        
        self._extractor = RegistryImageExtractor(tier=tier)
    
    def _extract_metadata(self, context) -> Dict[str, Any]:
        """Extract metadata using the registry-based extractor."""
        if hasattr(context, 'filepath'):
            filepath = context.filepath
        else:
            filepath = context
        return self._extractor.extract(filepath)
    
    def get_extraction_info(self) -> Dict[str, Any]:
        """Get extractor information."""
        return self._extractor.get_extraction_info()


def extract_image_metadata(filepath: str, tier: str = "advanced") -> Dict[str, Any]:
    """
    Convenience function for registry-based image metadata extraction.
    
    Args:
        filepath: Path to the image file
        tier: Extraction tier ('basic', 'advanced', 'universal')
        
    Returns:
        Dictionary containing extracted metadata
    """
    extractor = RegistryImageExtractor(tier=tier)
    return extractor.extract(filepath)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: registry_image_extractor.py <image_file> [tier]")
        print("  tier: basic, advanced (default), universal")
        sys.exit(1)
    
    filepath = sys.argv[1]
    tier = sys.argv[2] if len(sys.argv) > 2 else "advanced"
    
    result = extract_image_metadata(filepath, tier=tier)
    
    import json
    print(json.dumps(result, indent=2, default=str))
