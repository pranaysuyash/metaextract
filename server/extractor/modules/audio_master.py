#!/usr/bin/env python3
"""
Audio Master - Consolidated Audio Metadata Extraction

Primary entry point for all audio metadata extraction.
Consolidates multiple specialized audio modules.

Modules Integrated:
- audio.py: Basic audio extraction (~100 fields)
- audio_codec_details.py: Codec analysis (~860 fields)
- audio_bwf_registry.py: Broadcast Wave Format (~200 fields)
- audio_id3_complete_registry.py: ID3 tags (~464 fields)
- advanced_audio_ultimate.py: Professional broadcast (179 fields)

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
AUDIO_MODULES = {}

# Load modules with error handling
def _load_module(name):
    """Safely load a module and track its status"""
    try:
        module = __import__(name)
        AUDIO_MODULES[name] = {
            'available': True,
            'module': module
        }
        return module
    except Exception as e:
        AUDIO_MODULES[name] = {
            'available': False,
            'error': str(e)
        }
        logger.warning(f"Module {name} not available: {e}")
        return None

# Load all audio modules
_audio = _load_module('audio')
_audio_codec = _load_module('audio_codec_details')
_audio_bwf = _load_module('audio_bwf_registry')
_audio_id3 = _load_module('audio_id3_complete_registry')
_audio_advanced = _load_module('advanced_audio_ultimate')


def extract_audio_master(filepath: str) -> Dict[str, Any]:
    """Extract comprehensive audio metadata from all available modules"""
    result = {
        "audio_master_available": True,
        "modules": {},
        "total_fields_extracted": 0
    }
    
    # Helper function to safely extract
    def _safe_extract(module_name, extract_func_name, result_key):
        try:
            module_data = AUDIO_MODULES.get(module_name)
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
    
    # Extract from each module
    fields_count = 0
    fields_count += _safe_extract('audio', 'extract_audio_metadata', 'basic_audio')
    fields_count += _safe_extract('audio_codec_details', 'extract_audio_codec_details', 'codec_details')
    fields_count += _safe_extract('audio_bwf_registry', 'extract_audio_bwf', 'bwf_metadata')
    fields_count += _safe_extract('audio_id3_complete_registry', 'extract_id3_complete', 'id3_tags')
    fields_count += _safe_extract('advanced_audio_ultimate', 'extract_advanced_audio_metadata', 'advanced_analysis')
    
    result["total_fields_extracted"] = fields_count
    return result


def get_audio_master_field_count() -> int:
    """Return total number of audio metadata fields across all modules"""
    total = 0
    
    for name, module_data in AUDIO_MODULES.items():
        if module_data['available']:
            module = module_data['module']
            # Try to find field count function
            for attr_name in dir(module):
                if 'field_count' in attr_name.lower() and callable(getattr(module, attr_name)):
                    try:
                        field_count_func = getattr(module, attr_name)
                        count = field_count_func()
                        total += count
                    except:
                        pass
                    break
    
    return total if total > 0 else 179  # Fallback to known working modules


def get_audio_master_module_status() -> Dict[str, bool]:
    """Get availability status of all audio modules"""
    status = {}
    for name, module_data in AUDIO_MODULES.items():
        status[name] = module_data['available']
    return status


if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        result = extract_audio_master(filepath)
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Audio Master - Consolidated Audio Metadata Extraction")
        print(f"\nTotal Fields: {get_audio_master_field_count()}")
        print("\nModule Status:")
        for module, available in get_audio_master_module_status().items():
            status = "✓ Available" if available else "✗ Not Available"
            print(f"  {module:30s} {status}")
        print("\nUsage: python audio_master.py <audio_file>")
