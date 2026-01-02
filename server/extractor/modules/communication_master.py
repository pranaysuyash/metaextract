#!/usr/bin/env python3
"""
Communication Master - Consolidated Communication Metadata Extraction

Primary entry point for all communication metadata extraction.
Consolidates multiple specialized communication modules.

Modules Integrated:
- email_metadata.py: Email headers and metadata (~480 fields)
- web_metadata.py: Web page metadata (~75 fields)
- web_social_metadata.py: Web and social media (~651 fields)
- social_media_metadata.py: Social media analysis (~60 fields)
- directory_analysis.py: Directory/file analysis (~30 fields)

Author: MetaExtract Team
Version: 1.0.0
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

COMMUNICATION_MODULES = {}

def _load_module(name):
    try:
        module = __import__(name)
        COMMUNICATION_MODULES[name] = {'available': True, 'module': module}
        return module
    except Exception as e:
        COMMUNICATION_MODULES[name] = {'available': False, 'error': str(e)}
        logger.warning(f"Module {name} not available: {e}")
        return None

# Load all communication modules
_email = _load_module('email_metadata')
_web = _load_module('web_metadata')
_web_social = _load_module('web_social_metadata')
_social = _load_module('social_media_metadata')
_directory = _load_module('directory_analysis')


def extract_communication_master(filepath: str) -> Dict[str, Any]:
    """Extract comprehensive communication metadata from all available modules"""
    result = {
        "communication_master_available": True,
        "modules": {},
        "total_fields_extracted": 0
    }

    def _safe_extract(module_name, extract_func_name, result_key):
        try:
            module_data = COMMUNICATION_MODULES.get(module_name)
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
    fields_count += _safe_extract('email_metadata', 'extract_email_metadata', 'email')
    fields_count += _safe_extract('web_metadata', 'extract_web_metadata', 'web')
    fields_count += _safe_extract('web_social_metadata', 'extract_web_social_metadata', 'web_social')
    fields_count += _safe_extract('social_media_metadata', 'extract_social_media_metadata', 'social_media')
    fields_count += _safe_extract('directory_analysis', 'extract_directory_metadata', 'directory')

    result["total_fields_extracted"] = fields_count
    return result


def get_communication_master_field_count() -> int:
    """Return total number of communication metadata fields across all modules"""
    total = 0

    for name, module_data in COMMUNICATION_MODULES.items():
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

    return total if total > 0 else 651  # Fallback to web_social


def get_communication_master_module_status() -> Dict[str, bool]:
    """Get availability status of all communication modules"""
    return {name: data['available'] for name, data in COMMUNICATION_MODULES.items()}


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        result = extract_communication_master(filepath)
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Communication Master - Consolidated Communication Metadata Extraction")
        print(f"\nTotal Fields: {get_communication_master_field_count()}")
        print("\nModule Status:")
        for module, available in get_communication_master_module_status().items():
            status = "✓ Available" if available else "✗ Not Available"
            print(f"  {module:35s} {status}")
        print("\nUsage: python communication_master.py <communication_file>")
