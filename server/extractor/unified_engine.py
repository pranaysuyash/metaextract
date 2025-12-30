#!/usr/bin/env python3
"""
MetaExtract - Unified Metadata Extraction Engine v5.0

Consolidates all three metadata engines into a single, clean interface:
- metadata_engine.py (v3.0) - Base extraction
- metadata_engine_enhanced.py (v3.2) - Performance optimizations
- comprehensive_metadata_engine.py (v4.0) - Specialized engines

This unified engine provides:
1. Single entry point for all extraction needs
2. Automatic engine selection based on file type and tier
3. Consistent API across all extraction modes
4. Backward compatibility with existing code

Author: MetaExtract Team
Version: 5.0.0 - Unified Edition
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional, List, Union
from enum import Enum
from dataclasses import dataclass, field

# Configure logging
logger = logging.getLogger("metaextract.unified")

# ============================================================================
# Unified Tier System
# ============================================================================

class UnifiedTier(Enum):
    """Unified tier system mapping to frontend tier names."""
    FREE = "free"
    PROFESSIONAL = "professional"  # Maps to starter/premium
    FORENSIC = "forensic"          # Maps to premium
    ENTERPRISE = "enterprise"      # Maps to super

# Map frontend tiers to internal engine tiers
TIER_MAPPING = {
    "free": "free",
    "professional": "starter",
    "forensic": "premium",
    "enterprise": "super",
    # Also accept original tier names
    "starter": "starter",
    "premium": "premium",
    "super": "super",
}

@dataclass
class ExtractionOptions:
    """Configuration options for metadata extraction."""
    tier: str = "professional"
    include_performance_metrics: bool = False
    enable_advanced_analysis: bool = False
    enable_cache: bool = True
    max_workers: int = 4
    store_results: bool = False

    # Feature toggles
    extract_thumbnails: bool = True
    extract_perceptual_hashes: bool = True
    extract_specialized: bool = True  # DICOM, FITS, GeoTIFF, etc.

    def get_internal_tier(self) -> str:
        """Convert frontend tier to internal engine tier."""
        return TIER_MAPPING.get(self.tier.lower(), "starter")


# ============================================================================
# Unified Engine Interface
# ============================================================================

class UnifiedMetadataExtractor:
    """
    Unified metadata extraction engine consolidating all three engines.

    Usage:
        extractor = UnifiedMetadataExtractor()

        # Simple extraction
        result = extractor.extract("photo.jpg")

        # With options
        result = extractor.extract("photo.jpg", options=ExtractionOptions(
            tier="forensic",
            enable_advanced_analysis=True
        ))

        # Batch extraction
        results = await extractor.extract_batch(["a.jpg", "b.jpg"])
    """

    def __init__(self, default_options: ExtractionOptions = None):
        self.default_options = default_options or ExtractionOptions()
        self._enhanced_extractor = None
        self._comprehensive_extractor = None
        self._engines_initialized = False

    def _init_engines(self):
        """Lazy initialization of extraction engines."""
        if self._engines_initialized:
            return

        try:
            from .metadata_engine_enhanced import (
                EnhancedMetadataExtractor,
                get_enhanced_extractor
            )
            self._enhanced_extractor = get_enhanced_extractor()
        except ImportError as e:
            logger.warning(f"Enhanced extractor not available: {e}")

        try:
            from .comprehensive_metadata_engine import (
                ComprehensiveMetadataExtractor,
                get_comprehensive_extractor
            )
            self._comprehensive_extractor = get_comprehensive_extractor()
        except ImportError as e:
            logger.warning(f"Comprehensive extractor not available: {e}")

        self._engines_initialized = True

    def extract(
        self,
        filepath: str,
        options: ExtractionOptions = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Extract metadata from a single file.

        Args:
            filepath: Path to the file
            options: Extraction options (uses defaults if not provided)
            **kwargs: Additional options that override ExtractionOptions

        Returns:
            Dictionary containing extracted metadata
        """
        self._init_engines()

        # Merge options
        opts = options or self.default_options
        if kwargs:
            opts = ExtractionOptions(
                tier=kwargs.get('tier', opts.tier),
                include_performance_metrics=kwargs.get('include_performance_metrics', opts.include_performance_metrics),
                enable_advanced_analysis=kwargs.get('enable_advanced_analysis', opts.enable_advanced_analysis),
                enable_cache=kwargs.get('enable_cache', opts.enable_cache),
                max_workers=kwargs.get('max_workers', opts.max_workers),
                store_results=kwargs.get('store_results', opts.store_results),
                extract_thumbnails=kwargs.get('extract_thumbnails', opts.extract_thumbnails),
                extract_perceptual_hashes=kwargs.get('extract_perceptual_hashes', opts.extract_perceptual_hashes),
                extract_specialized=kwargs.get('extract_specialized', opts.extract_specialized),
            )

        internal_tier = opts.get_internal_tier()

        # Validate file exists
        if not os.path.exists(filepath):
            return {"error": f"File not found: {filepath}"}

        if not os.path.isfile(filepath):
            return {"error": f"Not a file: {filepath}"}

        # Determine which engine to use based on options and file type
        file_ext = Path(filepath).suffix.lower()

        # Use comprehensive engine for specialized file types
        specialized_extensions = {
            '.dcm', '.dicom',  # DICOM
            '.fits', '.fit', '.fts',  # FITS
            '.h5', '.hdf5', '.he5',  # HDF5
            '.nc', '.netcdf', '.nc4',  # NetCDF
            '.shp',  # Shapefile
        }

        use_comprehensive = (
            opts.extract_specialized and
            (file_ext in specialized_extensions or opts.enable_advanced_analysis)
        )

        try:
            if use_comprehensive and self._comprehensive_extractor:
                result = self._comprehensive_extractor.extract_comprehensive_metadata(
                    filepath,
                    internal_tier
                )
            elif self._enhanced_extractor:
                result = self._enhanced_extractor.extract_metadata(
                    filepath,
                    internal_tier,
                    opts.include_performance_metrics,
                    opts.enable_advanced_analysis
                )
            else:
                # Fallback to base engine
                from .metadata_engine import extract_metadata
                result = extract_metadata(filepath, internal_tier)

        except Exception as e:
            logger.error(f"Extraction failed for {filepath}: {e}")
            return {"error": f"Extraction failed: {str(e)}"}

        # Add unified engine metadata
        if "extraction_info" in result:
            result["extraction_info"]["unified_engine_version"] = "5.0.0"
            result["extraction_info"]["requested_tier"] = opts.tier
            result["extraction_info"]["internal_tier"] = internal_tier

        return result

    async def extract_batch(
        self,
        filepaths: List[str],
        options: ExtractionOptions = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Extract metadata from multiple files concurrently.

        Args:
            filepaths: List of file paths
            options: Extraction options
            **kwargs: Additional options

        Returns:
            Dictionary with 'results' mapping filepath to metadata,
            and 'summary' with batch statistics
        """
        self._init_engines()

        opts = options or self.default_options
        if kwargs:
            opts = ExtractionOptions(**{**vars(opts), **kwargs})

        internal_tier = opts.get_internal_tier()

        # Use enhanced extractor's batch method if available
        if self._enhanced_extractor:
            return await self._enhanced_extractor.extract_batch(
                filepaths,
                internal_tier,
                opts.max_workers
            )

        # Fallback: sequential extraction
        results = {}
        successful = 0
        failed = 0

        for filepath in filepaths:
            result = self.extract(filepath, opts)
            results[filepath] = result
            if "error" in result:
                failed += 1
            else:
                successful += 1

        return {
            "results": results,
            "summary": {
                "total_files": len(filepaths),
                "successful": successful,
                "failed": failed
            }
        }

    def extract_with_comparison(
        self,
        filepaths: List[str],
        options: ExtractionOptions = None,
        comparison_mode: str = "detailed"
    ) -> Dict[str, Any]:
        """
        Extract and compare metadata from multiple files.

        Args:
            filepaths: List of file paths to compare
            options: Extraction options
            comparison_mode: "detailed", "summary", or "differences_only"

        Returns:
            Comparison results with extracted metadata
        """
        self._init_engines()

        opts = options or self.default_options
        internal_tier = opts.get_internal_tier()

        # Extract metadata from all files
        metadata_list = []
        for filepath in filepaths:
            result = self.extract(filepath, opts)
            if "error" not in result:
                metadata_list.append(result)

        if len(metadata_list) < 2:
            return {"error": "At least 2 valid files required for comparison"}

        # Try to use comparison module
        try:
            from .modules.comparison import compare_metadata_files
            comparison = compare_metadata_files(metadata_list, comparison_mode)
            return {
                "metadata": {fp: m for fp, m in zip(filepaths, metadata_list)},
                "comparison": comparison
            }
        except ImportError:
            return {
                "metadata": {fp: m for fp, m in zip(filepaths, metadata_list)},
                "comparison": {"error": "Comparison module not available"}
            }

    def get_available_engines(self) -> Dict[str, Any]:
        """Return information about available extraction engines."""
        self._init_engines()

        engines = {
            "unified_engine": {
                "version": "5.0.0",
                "available": True
            },
            "base_engine": {
                "version": "3.0.0",
                "available": False
            },
            "enhanced_engine": {
                "version": "3.2.0",
                "available": self._enhanced_extractor is not None
            },
            "comprehensive_engine": {
                "version": "4.0.0",
                "available": self._comprehensive_extractor is not None
            }
        }

        # Check base engine
        try:
            from .metadata_engine import extract_metadata
            engines["base_engine"]["available"] = True
        except ImportError:
            pass

        # Check specialized engines from comprehensive
        try:
            from .comprehensive_metadata_engine import (
                DICOM_AVAILABLE, FITS_AVAILABLE, RASTERIO_AVAILABLE,
                FIONA_AVAILABLE, HDF5_AVAILABLE, NETCDF_AVAILABLE,
                OPENCV_AVAILABLE, LIBROSA_AVAILABLE
            )
            engines["specialized_engines"] = {
                "medical_imaging": DICOM_AVAILABLE,
                "astronomical_data": FITS_AVAILABLE,
                "geospatial_raster": RASTERIO_AVAILABLE,
                "geospatial_vector": FIONA_AVAILABLE,
                "hdf5_data": HDF5_AVAILABLE,
                "netcdf_data": NETCDF_AVAILABLE,
                "image_analysis": OPENCV_AVAILABLE,
                "audio_analysis": LIBROSA_AVAILABLE
            }
        except ImportError:
            engines["specialized_engines"] = {}

        return engines


# ============================================================================
# Convenience Functions (Backward Compatible)
# ============================================================================

# Global unified extractor instance
_unified_extractor: Optional[UnifiedMetadataExtractor] = None

def get_unified_extractor() -> UnifiedMetadataExtractor:
    """Get or create the global unified extractor instance."""
    global _unified_extractor
    if _unified_extractor is None:
        _unified_extractor = UnifiedMetadataExtractor()
    return _unified_extractor


def extract_metadata(
    filepath: str,
    tier: str = "professional",
    **kwargs
) -> Dict[str, Any]:
    """
    Extract metadata from a file using the unified engine.

    This is the main entry point for metadata extraction.
    Backward compatible with all previous engine interfaces.

    Args:
        filepath: Path to the file
        tier: Extraction tier (free, professional, forensic, enterprise)
        **kwargs: Additional options

    Returns:
        Dictionary containing extracted metadata
    """
    extractor = get_unified_extractor()
    options = ExtractionOptions(tier=tier, **kwargs)
    return extractor.extract(filepath, options)


async def extract_batch(
    filepaths: List[str],
    tier: str = "professional",
    max_workers: int = 4,
    **kwargs
) -> Dict[str, Any]:
    """
    Extract metadata from multiple files concurrently.

    Args:
        filepaths: List of file paths
        tier: Extraction tier
        max_workers: Maximum concurrent extractions
        **kwargs: Additional options

    Returns:
        Batch extraction results
    """
    extractor = get_unified_extractor()
    options = ExtractionOptions(tier=tier, max_workers=max_workers, **kwargs)
    return await extractor.extract_batch(filepaths, options)


def extract_with_advanced_analysis(
    filepath: str,
    tier: str = "forensic",
    **kwargs
) -> Dict[str, Any]:
    """
    Extract metadata with advanced forensic analysis enabled.

    Args:
        filepath: Path to the file
        tier: Extraction tier
        **kwargs: Additional options

    Returns:
        Dictionary with metadata and advanced analysis results
    """
    extractor = get_unified_extractor()
    options = ExtractionOptions(
        tier=tier,
        enable_advanced_analysis=True,
        include_performance_metrics=True,
        **kwargs
    )
    return extractor.extract(filepath, options)


# ============================================================================
# Backward Compatibility Aliases
# ============================================================================

# These maintain compatibility with code using previous engine versions

def extract_metadata_enhanced(filepath: str, tier: str = "super", **kwargs) -> Dict[str, Any]:
    """Alias for extract_metadata (backward compatibility with v3.2)."""
    return extract_metadata(filepath, tier, **kwargs)

def extract_comprehensive_metadata(filepath: str, tier: str = "super", **kwargs) -> Dict[str, Any]:
    """Alias for extract_metadata (backward compatibility with v4.0)."""
    return extract_metadata(filepath, tier, extract_specialized=True, **kwargs)


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="MetaExtract Unified Engine v5.0 - Universal Metadata Extraction"
    )
    parser.add_argument("files", nargs="*", help="File(s) to extract metadata from")
    parser.add_argument("--tier", "-t", default="professional",
                       choices=["free", "professional", "forensic", "enterprise"])
    parser.add_argument("--output", "-o", help="Output JSON file")
    parser.add_argument("--advanced", "-a", action="store_true",
                       help="Enable advanced forensic analysis")
    parser.add_argument("--batch", "-b", action="store_true",
                       help="Process files in batch mode")
    parser.add_argument("--compare", "-c", action="store_true",
                       help="Compare metadata between files")
    parser.add_argument("--engines", action="store_true",
                       help="Show available extraction engines")
    parser.add_argument("--performance", action="store_true",
                       help="Include performance metrics")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="JSON only output")

    args = parser.parse_args()

    extractor = get_unified_extractor()

    # Show available engines
    if args.engines:
        engines = extractor.get_available_engines()
        print(json.dumps(engines, indent=2))
        return

    # Validate files provided
    if not args.files:
        parser.error("No files specified. Use --engines to see available extraction engines.")

    options = ExtractionOptions(
        tier=args.tier,
        enable_advanced_analysis=args.advanced,
        include_performance_metrics=args.performance
    )

    if not args.quiet:
        print(f"MetaExtract Unified v5.0.0 - Tier: {args.tier}", file=sys.stderr)

    # Process files
    if args.compare and len(args.files) > 1:
        result = extractor.extract_with_comparison(args.files, options)
    elif args.batch or len(args.files) > 1:
        result = asyncio.run(extractor.extract_batch(args.files, options))
    else:
        result = extractor.extract(args.files[0], options)

    # Output
    json_output = json.dumps(result, indent=2, default=str)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(json_output)
        if not args.quiet:
            print(f"Saved to: {args.output}", file=sys.stderr)
    else:
        print(json_output)


if __name__ == "__main__":
    main()
