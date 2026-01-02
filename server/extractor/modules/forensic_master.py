#!/usr/bin/env python3
"""
Forensic Master - Consolidated Forensic Metadata Extraction

Primary entry point for all forensic metadata extraction.
Consolidates multiple specialized forensic modules.

Modules Integrated:
- forensic_metadata.py: Basic forensic analysis (~258 fields)
- forensic_complete.py: Complete forensic analysis (~253 fields)
- forensic_digital_advanced.py: Digital forensics (~263 fields)
- forensic_security_advanced.py: Security forensics (~86 fields)
- forensic_security_comprehensive_advanced.py: Comprehensive security (~400 fields)
- forensic_security_extended.py: Extended security (~116 fields)
- forensic_security_ultimate_advanced.py: Ultimate security (~425 fields)

Author: MetaExtract Team
Version: 1.0.0
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

FORENSIC_MODULES = {}

def _load_module(name):
    try:
        module = __import__(name)
        FORENSIC_MODULES[name] = {'available': True, 'module': module}
        return module
    except Exception as e:
        FORENSIC_MODULES[name] = {'available': False, 'error': str(e)}
        logger.warning(f"Module {name} not available: {e}")
        return None

# Load all forensic modules
_forensic_basic = _load_module('forensic_metadata')
_forensic_complete = _load_module('forensic_complete')
_forensic_digital = _load_module('forensic_digital_advanced')
_forensic_security = _load_module('forensic_security_advanced')
_forensic_security_comp = _load_module('forensic_security_comprehensive_advanced')
_forensic_security_ext = _load_module('forensic_security_extended')
_forensic_security_ultimate = _load_module('forensic_security_ultimate_advanced')


def extract_forensic_master(filepath: str) -> Dict[str, Any]:
    """Extract comprehensive forensic metadata from all available modules"""
    result = {
        "forensic_master_available": True,
        "modules": {},
        "total_fields_extracted": 0
    }

    def _safe_extract(module_name, extract_func_name, result_key):
        try:
            module_data = FORENSIC_MODULES.get(module_name)
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
    fields_count += _safe_extract('forensic_metadata', 'extract_forensic_metadata', 'forensic_basic')
    fields_count += _safe_extract('forensic_complete', 'extract_forensic_complete', 'forensic_complete')
    fields_count += _safe_extract('forensic_digital_advanced', 'extract_forensic_digital_advanced', 'forensic_digital')
    fields_count += _safe_extract('forensic_security_advanced', 'extract_forensic_security_advanced', 'forensic_security')
    fields_count += _safe_extract('forensic_security_comprehensive_advanced', 'extract_forensic_security_comprehensive_advanced', 'forensic_security_comp')
    fields_count += _safe_extract('forensic_security_extended', 'extract_forensic_security_extended', 'forensic_security_ext')
    fields_count += _safe_extract('forensic_security_ultimate_advanced', 'extract_forensic_security_ultimate_advanced', 'forensic_security_ultimate')

    result["total_fields_extracted"] = fields_count
    return result


def get_forensic_master_field_count() -> int:
    """Return total number of forensic metadata fields across all modules"""
    total = 0

    for name, module_data in FORENSIC_MODULES.items():
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

    return total if total > 0 else 425  # Fallback to ultimate_advanced


def get_forensic_master_module_status() -> Dict[str, bool]:
    """Get availability status of all forensic modules"""
    return {name: data['available'] for name, data in FORENSIC_MODULES.items()}


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        result = extract_forensic_master(filepath)
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Forensic Master - Consolidated Forensic Metadata Extraction")
        print(f"\nTotal Fields: {get_forensic_master_field_count()}")
        print("\nModule Status:")
        for module, available in get_forensic_master_module_status().items():
            status = "✓ Available" if available else "✗ Not Available"
            print(f"  {module:50s} {status}")
        print("\nUsage: python forensic_master.py <any_file>")
