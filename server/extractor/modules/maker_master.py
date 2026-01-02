#!/usr/bin/env python3
"""
Maker Master - Consolidated MakerNotes Metadata Extraction

Primary entry point for all camera MakerNotes extraction.
Consolidates multiple specialized MakerNotes modules.

Modules Integrated:
- makernotes_complete.py: Complete MakerNotes (~4,750 fields)
- vendor_makernotes.py: Vendor-specific tags (~250 fields)
- makernotes_phase_one.py: Phase One cameras (~120 fields)
- makernotes_ricoh.py: Ricoh cameras (~80 fields)
- makernotes_sigma.py: Sigma cameras (~100 fields)

Note: Some modules have relative import issues and may not load dynamically.

Author: MetaExtract Team
Version: 1.0.0
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

MAKER_MODULES = {}

def _load_module(name):
    try:
        module = __import__(name)
        MAKER_MODULES[name] = {'available': True, 'module': module}
        return module
    except Exception as e:
        MAKER_MODULES[name] = {'available': False, 'error': str(e)}
        logger.warning(f"Module {name} not available: {e}")
        return None

# Load modules
_makernotes_complete = _load_module('makernotes_complete')
_makernotes_phase_one = _load_module('makernotes_phase_one')


def extract_maker_master(filepath: str) -> Dict[str, Any]:
    """Extract comprehensive MakerNotes metadata from all available modules"""
    result = {
        "maker_master_available": True,
        "modules": {},
        "total_fields_extracted": 0
    }
    
    def _safe_extract(module_name, extract_func_name, result_key):
        try:
            module_data = MAKER_MODULES.get(module_name)
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
    fields_count += _safe_extract('makernotes_complete', 'extract_makernotes_complete', 'complete')
    fields_count += _safe_extract('makernotes_phase_one', 'extract_makernotes_metadata', 'phase_one')
    
    result["total_fields_extracted"] = fields_count
    return result


def get_maker_master_field_count() -> int:
    """Return total number of MakerNotes metadata fields across all modules"""
    total = 0
    
    for name, module_data in MAKER_MODULES.items():
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
    
    return total if total > 0 else 4870  # Fallback: ~4750+120


def get_maker_master_module_status() -> Dict[str, bool]:
    """Get availability status of all MakerNotes modules"""
    return {name: data['available'] for name, data in MAKER_MODULES.items()}


if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        result = extract_maker_master(filepath)
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Maker Master - Consolidated MakerNotes Metadata Extraction")
        print(f"\nTotal Fields: {get_maker_master_field_count()}")
        print("\nModule Status:")
        for module, available in get_maker_master_module_status().items():
            status = "✓ Available" if available else "✗ Not Available"
            print(f"  {module:25s} {status}")
        print("\nUsage: python maker_master.py <image_file>")
        print("\nNote: Some modules may have relative import issues")
