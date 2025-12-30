# MetaExtract - Comprehensive Metadata Extraction Engine
#
# This package provides unified metadata extraction across multiple engines:
# - metadata_engine.py (v3.0) - Base extraction
# - metadata_engine_enhanced.py (v3.2) - Performance optimizations
# - comprehensive_metadata_engine.py (v4.0) - Specialized engines
# - unified_engine.py (v5.0) - Consolidated interface

from typing import Dict, Any, List, Optional

# Primary exports - Unified Engine (v5.0)
try:
    from .unified_engine import (
        UnifiedMetadataExtractor,
        ExtractionOptions,
        UnifiedTier,
        get_unified_extractor,
        extract_metadata,
        extract_batch,
        extract_with_advanced_analysis,
    )
    UNIFIED_ENGINE_AVAILABLE = True
except ImportError:
    UNIFIED_ENGINE_AVAILABLE = False

# Base Engine exports (v3.0) - for backward compatibility
try:
    from .metadata_engine import (
        extract_metadata as extract_metadata_base,
        Tier,
        TierConfig,
        TIER_CONFIGS,
    )
    BASE_ENGINE_AVAILABLE = True
except ImportError:
    BASE_ENGINE_AVAILABLE = False

# Enhanced Engine exports (v3.2) - for backward compatibility
try:
    from .metadata_engine_enhanced import (
        EnhancedMetadataExtractor,
        extract_metadata_enhanced,
        extract_batch_metadata,
        get_enhanced_extractor,
    )
    ENHANCED_ENGINE_AVAILABLE = True
except ImportError:
    ENHANCED_ENGINE_AVAILABLE = False

# Comprehensive Engine exports (v4.0) - for backward compatibility
try:
    from .comprehensive_metadata_engine import (
        ComprehensiveMetadataExtractor,
        extract_comprehensive_metadata,
        extract_comprehensive_batch,
        get_comprehensive_extractor,
        ComprehensiveTierConfig,
        COMPREHENSIVE_TIER_CONFIGS,
    )
    COMPREHENSIVE_ENGINE_AVAILABLE = True
except ImportError:
    COMPREHENSIVE_ENGINE_AVAILABLE = False

# Convenience function that automatically uses the best available engine
def extract(filepath: str, tier: str = "professional", **kwargs) -> Dict[str, Any]:
    """
    Extract metadata using the best available engine.

    This is the recommended entry point for metadata extraction.

    Args:
        filepath: Path to the file to extract metadata from
        tier: Extraction tier (free, professional, forensic, enterprise)
        **kwargs: Additional options passed to the extractor

    Returns:
        Dictionary containing extracted metadata
    """
    if UNIFIED_ENGINE_AVAILABLE:
        return extract_metadata(filepath, tier, **kwargs)
    elif COMPREHENSIVE_ENGINE_AVAILABLE:
        # Map tiers
        tier_map = {
            "free": "free", "professional": "starter",
            "forensic": "premium", "enterprise": "super"
        }
        internal_tier = tier_map.get(tier, tier)
        return extract_comprehensive_metadata(filepath, internal_tier)
    elif ENHANCED_ENGINE_AVAILABLE:
        tier_map = {
            "free": "free", "professional": "starter",
            "forensic": "premium", "enterprise": "super"
        }
        internal_tier = tier_map.get(tier, tier)
        return extract_metadata_enhanced(filepath, internal_tier)
    elif BASE_ENGINE_AVAILABLE:
        tier_map = {
            "free": "free", "professional": "starter",
            "forensic": "premium", "enterprise": "super"
        }
        internal_tier = tier_map.get(tier, tier)
        return extract_metadata_base(filepath, internal_tier)
    else:
        return {"error": "No metadata extraction engine available"}


# Version info
__version__ = "5.0.0"
__engines__ = {
    "unified": UNIFIED_ENGINE_AVAILABLE,
    "comprehensive": COMPREHENSIVE_ENGINE_AVAILABLE,
    "enhanced": ENHANCED_ENGINE_AVAILABLE,
    "base": BASE_ENGINE_AVAILABLE,
}

__all__ = [
    # Main entry points
    "extract",
    "extract_metadata",
    "extract_batch",
    "extract_with_advanced_analysis",

    # Unified Engine
    "UnifiedMetadataExtractor",
    "ExtractionOptions",
    "UnifiedTier",
    "get_unified_extractor",

    # Comprehensive Engine (v4.0)
    "ComprehensiveMetadataExtractor",
    "extract_comprehensive_metadata",
    "extract_comprehensive_batch",
    "get_comprehensive_extractor",

    # Enhanced Engine (v3.2)
    "EnhancedMetadataExtractor",
    "extract_metadata_enhanced",
    "extract_batch_metadata",
    "get_enhanced_extractor",

    # Base Engine (v3.0)
    "extract_metadata_base",
    "Tier",
    "TierConfig",
    "TIER_CONFIGS",

    # Config classes
    "ComprehensiveTierConfig",
    "COMPREHENSIVE_TIER_CONFIGS",

    # Availability flags
    "UNIFIED_ENGINE_AVAILABLE",
    "COMPREHENSIVE_ENGINE_AVAILABLE",
    "ENHANCED_ENGINE_AVAILABLE",
    "BASE_ENGINE_AVAILABLE",

    # Version info
    "__version__",
    "__engines__",
]
