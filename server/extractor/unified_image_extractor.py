#!/usr/bin/env python3
"""
Unified Image Extraction System
Combines the comprehensive original system with the new registry architecture
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import comprehensive engine first
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from comprehensive_metadata_engine import extract_comprehensive_metadata
    COMPREHENSIVE_AVAILABLE = True
    logger.info("Successfully loaded comprehensive engine")
except ImportError as e:
    COMPREHENSIVE_AVAILABLE = False
    logger.warning(f"Could not load comprehensive engine: {e}")

# Then import registry system
try:
    modules_dir = Path(__file__).parent / 'modules'
    sys.path.insert(0, str(modules_dir))

    from image_extensions import get_global_registry
    from image_extraction_manager import get_image_manager

    REGISTRY_AVAILABLE = True
    logger.info("Successfully loaded registry system")
except ImportError as e:
    REGISTRY_AVAILABLE = False
    logger.warning(f"Could not load registry system: {e}")


def extract_unified_metadata(
    filepath: str,
    tier: str = "comprehensive",
    performance_tracking: bool = True
) -> Dict[str, Any]:
    """
    Extract metadata using unified approach.

    Args:
        filepath: Path to image file
        tier: Extraction tier ('comprehensive', 'enhanced', 'advanced', 'basic')
        performance_tracking: Whether to include performance metrics

    Returns:
        Dictionary containing unified extraction results
    """
    start_time = time.time()
    results = {
        "unified_extraction": True,
        "source_file": filepath,
        "tier_requested": tier,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        # For comprehensive tier, use comprehensive engine for maximum coverage
        if tier == "comprehensive" and COMPREHENSIVE_AVAILABLE:
            logger.info(f"Using comprehensive engine for {filepath}")
            comprehensive_result = extract_comprehensive_metadata(
                filepath=filepath,
                tier='super'
            )

            if comprehensive_result and "error" not in comprehensive_result:
                results.update(comprehensive_result)
                results["extraction_source"] = "comprehensive_engine"
                results["extraction_success"] = True
                results["extraction_strategy"] = "comprehensive_primary"
            else:
                results["extraction_success"] = False
                results["error"] = comprehensive_result.get("error", "Unknown comprehensive error")

        # For enhanced/advanced, try registry with comprehensive fallback
        elif tier in ["enhanced", "advanced"] and REGISTRY_AVAILABLE:
            logger.info(f"Using registry system for {filepath}")

            try:
                manager = get_image_manager()
                registry_result = manager.extract_image_metadata(
                    filepath,
                    tier="enhanced_basic" if tier == "enhanced" else "advanced",
                    performance_tracking=True
                )

                if registry_result and registry_result.get("success", False):
                    results.update(registry_result)
                    results["extraction_source"] = f"registry_{tier}"
                    results["extraction_strategy"] = "registry_enhanced"

                    # Check if we need to supplement with comprehensive data
                    if _missing_critical_fields(results):
                        logger.warning("Registry missing critical fields, supplementing with comprehensive")
                        if COMPREHENSIVE_AVAILABLE:
                            comprehensive_supplement = extract_comprehensive_metadata(
                                filepath=filepath,
                                tier='super'
                            )
                            results["comprehensive_supplement"] = comprehensive_supplement
                else:
                    # Fall back to comprehensive
                    if COMPREHENSIVE_AVAILABLE:
                        logger.info("Registry failed, falling back to comprehensive")
                        comprehensive_result = extract_comprehensive_metadata(
                            filepath=filepath,
                            tier='super'
                        )
                        results.update(comprehensive_result)
                        results["extraction_source"] = "comprehensive_fallback"
                        results["extraction_strategy"] = "registry_fallback_comprehensive"
                    else:
                        results["extraction_success"] = False
                        results["error"] = "Registry failed and comprehensive unavailable"

            except Exception as e:
                logger.error(f"Registry extraction failed: {e}")
                # Fall back to comprehensive
                if COMPREHENSIVE_AVAILABLE:
                    comprehensive_result = extract_comprehensive_metadata(
                        filepath=filepath,
                        tier='super'
                    )
                    results.update(comprehensive_result)
                    results["extraction_source"] = "comprehensive_fallback"
                else:
                    results["extraction_success"] = False
                    results["error"] = f"Registry failed: {str(e)[:200]}"

        # For basic tier, use simple approach
        else:
            if COMPREHENSIVE_AVAILABLE:
                logger.info(f"Using comprehensive engine for basic tier {filepath}")
                comprehensive_result = extract_comprehensive_metadata(
                    filepath=filepath,
                    tier='basic'
                )
                results.update(comprehensive_result)
                results["extraction_source"] = "comprehensive_basic"
            else:
                results["extraction_success"] = False
                results["error"] = "No extraction system available"

        # Add unified performance metrics
        if performance_tracking:
            total_time = time.time() - start_time
            results["total_processing_time"] = total_time
            results["unified_timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

        return results

    except Exception as e:
        logger.error(f"Unified extraction failed: {e}")
        return {
            "unified_extraction": False,
            "extraction_success": False,
            "error": f"Unified extraction failed: {str(e)[:200]}",
            "source_file": filepath,
            "tier_requested": tier
        }


def _missing_critical_fields(result: Dict[str, Any]) -> bool:
    """Check if result is missing critical fields"""
    # Check for GPS data (critical for GPS Map Camera images)
    has_gps = (
        "gps" in result and
        result["gps"] and
        isinstance(result["gps"], dict) and
        len(result["gps"]) > 0
    )

    # Check for comprehensive EXIF
    has_comprehensive_exif = (
        "exif" in result and
        result["exif"] and
        isinstance(result["exif"], dict) and
        len(result["exif"]) > 20
    )

    return not (has_gps and has_comprehensive_exif)


def get_system_status() -> Dict[str, Any]:
    """Get status of unified extraction system"""
    return {
        "registry_available": REGISTRY_AVAILABLE,
        "comprehensive_available": COMPREHENSIVE_AVAILABLE,
        "extraction_strategies": [
            "comprehensive_primary",
            "registry_enhanced",
            "comprehensive_fallback"
        ],
        "recommended_tier": "comprehensive" if COMPREHENSIVE_AVAILABLE else "basic"
    }


def main():
    """Main entry point for command-line usage"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No file path provided"}))
        sys.exit(1)

    filepath = sys.argv[1]
    tier = sys.argv[2] if len(sys.argv) > 2 else "comprehensive"

    if not Path(filepath).exists():
        print(json.dumps({"error": f"File not found: {filepath}"}))
        sys.exit(1)

    result = extract_unified_metadata(filepath, tier)
    print(json.dumps(result, default=str, indent=2))


if __name__ == "__main__":
    main()