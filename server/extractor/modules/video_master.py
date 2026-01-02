#!/usr/bin/env python3
"""
Video Master - Consolidated Video Metadata Extraction

Primary entry point for all video metadata extraction.
Consolidates multiple specialized video modules.

Modules Integrated:
- video.py: Basic video extraction (~120 fields)
- video_codec_details.py: Codec analysis (~650 fields)
- video_keyframes.py: Keyframe extraction (~20 fields)
- video_telemetry.py: Drone/action camera (~200 fields)
- advanced_video_ultimate.py: Professional broadcast (180 fields)

Author: MetaExtract Team
Version: 2.0.0
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Modules status
VIDEO_MODULES = {}

def _load_module(name):
    """Safely load a module and track its status"""
    try:
        module = __import__(name)
        VIDEO_MODULES[name] = {'available': True, 'module': module}
        return module
    except Exception as e:
        VIDEO_MODULES[name] = {'available': False, 'error': str(e)}
        logger.warning(f"Module {name} not available: {e}")
        return None

# Load all video modules
_video = _load_module('video')
_video_codec = _load_module('video_codec_details')
_video_keyframes = _load_module('video_keyframes')
_video_telemetry = _load_module('video_telemetry')
_video_advanced = _load_module('advanced_video_ultimate')
_drone = _load_module('drone_metadata')


def extract_video_master(filepath: str) -> Dict[str, Any]:
    """Extract comprehensive video metadata from all available modules"""
    result = {
        "video_master_available": True,
        "modules": {},
        "total_fields_extracted": 0
    }
    
    def _safe_extract(module_name, extract_func_name, result_key):
        try:
            module_data = VIDEO_MODULES.get(module_name)
            if module_data and module_data['available']:
                module = module_data['module']
                if hasattr(module, extract_func_name):
                    extract_func = getattr(module, extract_func_name)
                    data = extract_func(filepath)
                    if data and not isinstance(data, type(None)):
                        result["modules"][result_key] = data
                        result["modules"][f"{result_key}_available"] = True
                        return len([k for k in data.keys() if not k.endswith('_available')])
        except Exception as e:
            logger.error(f"Error extracting from {module_name}: {e}")
            result["modules"][f"{result_key}_error"] = str(e)
        return 0
    
    fields_count = 0
    fields_count += _safe_extract('video', 'extract_video_metadata', 'basic_video')
    fields_count += _safe_extract('video_codec_details', 'extract_video_codec_details', 'codec_details')
    fields_count += _safe_extract('video_keyframes', 'extract_keyframe_metadata', 'keyframes')
    fields_count += _safe_extract('video_telemetry', 'extract_video_telemetry', 'telemetry')
    fields_count += _safe_extract('advanced_video_ultimate', 'extract_advanced_video_metadata', 'advanced_analysis')
    fields_count += _safe_extract('drone_metadata', 'extract_drone_metadata', 'drone')

    result["total_fields_extracted"] = fields_count
    return result


def get_video_master_field_count() -> int:
    """Return total number of video metadata fields across all modules"""
    total = 0
    
    for name, module_data in VIDEO_MODULES.items():
        if module_data['available']:
            module = module_data['module']
            for attr_name in dir(module):
                if 'field_count' in attr_name.lower() and callable(getattr(module, attr_name)):
                    try:
                        field_count_func = getattr(module, attr_name)
                        count = field_count_func()
                        total += count
                    except:
                        pass
                    break
    
    return total if total > 0 else 180  # Fallback


def get_video_master_module_status() -> Dict[str, bool]:
    """Get availability status of all video modules"""
    return {name: data['available'] for name, data in VIDEO_MODULES.items()}


if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) > 1:
        result = extract_video_master(sys.argv[1])
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Video Master - Consolidated Video Metadata Extraction")
        print(f"\nTotal Fields: {get_video_master_field_count()}")
        print("\nModule Status:")
        for module, available in get_video_master_module_status().items():
            status = "✓ Available" if available else "✗ Not Available"
            print(f"  {module:30s} {status}")
        print("\nUsage: python video_master.py <video_file>")
