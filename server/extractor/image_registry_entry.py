#!/usr/bin/env python3
"""
Image Registry Entry Point
New unified entry point for image metadata extraction using the registry system
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

# Import the new registry system
try:
    # Add modules directory to path
    modules_dir = Path(__file__).parent / 'modules'
    sys.path.insert(0, str(modules_dir))

    from image_extraction_manager import (
        get_image_manager,
        extract_image_metadata
    )

    REGISTRY_AVAILABLE = True
    logger.info("Successfully loaded image registry system")
except ImportError as e:
    REGISTRY_AVAILABLE = False
    logger.warning(f"Could not load image registry system: {e}")


def extract_image_with_registry(
    filepath: str,
    tier: str = "advanced",
    performance_tracking: bool = True
) -> Dict[str, Any]:
    """
    Extract image metadata using the new registry system.

    Args:
        filepath: Path to image file
        tier: Extraction tier ('basic', 'advanced', 'universal')
        performance_tracking: Whether to include performance metrics

    Returns:
        Dictionary compatible with existing metadata response format
    """
    if not REGISTRY_AVAILABLE:
        return {
            "error": "Image registry system not available",
            "fallback_required": True
        }

    try:
        start_time = time.time()

        # Use the new registry system
        manager = get_image_manager()
        result = manager.extract_image_metadata(
            filepath,
            tier=tier,
            performance_tracking=performance_tracking
        )

        # Transform to match existing response format
        transformed_result = {
            "extraction_info": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "tier": tier,
                "engine_version": "1.0.0-registry",
                "libraries": {
                    "registry_system": True,
                    "pillow": True,
                    "image_master": "advanced" in result.get("source", "")
                },
                "fields_extracted": result.get("fields_extracted", 0),
                "processing_ms": result.get("total_processing_time", 0) * 1000,
                "extraction_source": result.get("source", "unknown"),
                "extraction_success": result.get("success", False)
            },
            "image": {
                "registry_based": True,
                "extraction_source": result.get("source", "unknown"),
                "requested_tier": result.get("requested_tier", tier),
                "actual_tier": result.get("actual_tier", tier),
                "fields_extracted": result.get("fields_extracted", 0),
                "extraction_time": result.get("extraction_time", 0.0),
                "total_processing_time": result.get("total_processing_time", 0.0),
                **result.get("metadata", {})
            },
            "registry_metadata": {
                "available_extensions": manager.get_available_extensions(),
                "performance_stats": result.get("performance_stats", {}),
                "system_status": manager.get_system_status()
            }
        }

        # Add errors/warnings if present
        if result.get("errors"):
            transformed_result["extraction_info"]["errors"] = result["errors"]
        if result.get("warnings"):
            transformed_result["extraction_info"]["warnings"] = result["warnings"]

        # Add file info
        file_info = result.get("metadata", {}).get("file_info", {})
        if file_info:
            transformed_result["file"] = {
                "path": filepath,
                "name": Path(filepath).name,
                "extension": file_info.get("extension", ""),
                "size_bytes": file_info.get("size_bytes", 0),
                "size_mb": file_info.get("size_mb", 0.0)
            }
            transformed_result["filesystem"] = {
                "size_bytes": file_info.get("size_bytes", 0),
                "size_human": f"{file_info.get('size_mb', 0.0)} MB"
            }

        return transformed_result

    except Exception as e:
        logger.error(f"Registry extraction failed: {e}")
        return {
            "error": f"Registry extraction failed: {str(e)[:200]}",
            "fallback_required": True
        }


def main():
    """Main entry point for command-line usage"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No file path provided"}))
        sys.exit(1)

    filepath = sys.argv[1]
    tier = sys.argv[2] if len(sys.argv) > 2 else "advanced"

    if not Path(filepath).exists():
        print(json.dumps({"error": f"File not found: {filepath}"}))
        sys.exit(1)

    result = extract_image_with_registry(filepath, tier)
    print(json.dumps(result, default=str, indent=2))


if __name__ == "__main__":
    main()