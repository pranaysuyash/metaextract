#!/usr/bin/env python3
"""
Image Master - Consolidated Image Metadata Extraction

Primary entry point for all image metadata extraction.
Consolidates multiple specialized image modules.

Modules Integrated:
- images.py: Basic image properties (~18 fields)
- iptc_xmp.py: IPTC/XMP metadata (~167 fields)
- exif.py: EXIF data (import issues, ~784 fields)
- perceptual_hashes.py: Image fingerprinting (~12 fields)
- colors.py: Color analysis (~25 fields)
- quality.py: Image quality metrics (~15 fields)
- mobile_metadata.py: Mobile/smartphone metadata (~110 fields)

Author: MetaExtract Team
Version: 1.0.0
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

IMAGE_MODULES = {}

def _load_module(name):
    try:
        module = __import__(name)
        IMAGE_MODULES[name] = {'available': True, 'module': module}
        return module
    except Exception as e:
        IMAGE_MODULES[name] = {'available': False, 'error': str(e)}
        logger.warning(f"Module {name} not available: {e}")
        return None

# Load modules
_images = _load_module('images')
_iptc_xmp = _load_module('iptc_xmp')
_perceptual_hashes = _load_module('perceptual_hashes')
_colors = _load_module('colors')
_quality = _load_module('quality')
_mobile = _load_module('mobile_metadata')

# Try exif separately (has relative import issues)
try:
    import exif
    _exif = exif
    IMAGE_MODULES['exif'] = {'available': True, 'module': exif}
except Exception as e:
    _exif = None
    IMAGE_MODULES['exif'] = {'available': False, 'error': str(e)}


def extract_image_master(filepath: str) -> Dict[str, Any]:
    """Extract comprehensive image metadata from all available modules"""
    result = {
        "image_master_available": True,
        "modules": {},
        "total_fields_extracted": 0
    }
    
    def _safe_extract(module_name, extract_func_name, result_key):
        try:
            module_data = IMAGE_MODULES.get(module_name)
            if module_data and module_data['available']:
                module = module_data['module']
                if hasattr(module, extract_func_name):
                    extract_func = getattr(module, extract_func_name)
                    data = extract_func(filepath)
                    if data and not isinstance(data, type(None)):
                        result["modules"][result_key] = data
                        result["modules"][f"{result_key}_available"] = True
                        if isinstance(data, dict):
                            return len([k for k in data.keys() if not k.endswith('_available')])
                        elif isinstance(data, list):
                            return len(data)
                        return 1
        except Exception as e:
            logger.error(f"Error extracting from {module_name}: {e}")
            result["modules"][f"{result_key}_error"] = str(e)
        return 0
    
    fields_count = 0
    fields_count += _safe_extract('images', 'extract_image_properties', 'basic_image')
    fields_count += _safe_extract('iptc_xmp', 'extract_iptc_xmp_metadata', 'iptc_xmp')
    fields_count += _safe_extract('exif', 'extract_exif_metadata', 'exif_data')
    fields_count += _safe_extract('perceptual_hashes', 'extract_perceptual_hashes', 'perceptual_hashes')
    fields_count += _safe_extract('colors', 'extract_color_palette', 'colors')
    fields_count += _safe_extract('quality', 'extract_quality_metrics', 'quality')
    fields_count += _safe_extract('mobile_metadata', 'extract_mobile_metadata', 'mobile')

    result["total_fields_extracted"] = fields_count
    return result


def get_image_master_field_count() -> int:
    """Return total number of image metadata fields across all modules"""
    total = 0
    
    for name, module_data in IMAGE_MODULES.items():
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
    
    return total if total > 0 else 222  # Fallback: 18+167+25+12+15


def get_image_master_module_status() -> Dict[str, bool]:
    """Get availability status of all image modules"""
    return {name: data['available'] for name, data in IMAGE_MODULES.items()}


if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        result = extract_image_master(filepath)
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Image Master - Consolidated Image Metadata Extraction")
        print(f"\nTotal Fields: {get_image_master_field_count()}")
        print("\nModule Status:")
        for module, available in get_image_master_module_status().items():
            status = "✓ Available" if available else "✗ Not Available"
            print(f"  {module:20s} {status}")
        print("\nUsage: python image_master.py <image_file>")
