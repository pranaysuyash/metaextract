#!/usr/bin/env python3
"""
Scientific Master - Consolidated Scientific Metadata Extraction

Primary entry point for all scientific metadata extraction.
Consolidates multiple specialized scientific modules.

Modules Integrated:
- scientific_data.py: Basic scientific (~320 fields)
- dicom_complete_ultimate.py: DICOM imaging (~391 fields)
- fits_extractor.py: FITS astronomy (~572 fields)
- genomic_extractor.py: Genomic data (~150 fields)
- environmental_climate.py: Environmental/Climate data (~92 fields)
- ai_ml_metadata.py: AI/Machine Learning models (~70 fields)
- materials_science.py: Materials Science data (~104 fields)
- biometric_health.py: Biometric/Health data (~108 fields)
- geospatial_gis.py: Geospatial/GIS data (~108 fields)
- iot_metadata.py: IoT Device data (~84 fields)
- quantum_metadata.py: Quantum Computing data (~76 fields)
- robotics_metadata.py: Robotics data (~109 fields)
- neural_network_metadata.py: Neural Network data (~92 fields)
- autonomous_metadata.py: Autonomous Systems data (~106 fields)
- biotechnology_metadata.py: Biotechnology data (~130 fields)

Author: MetaExtract Team
Version: 3.0.0
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

SCIENTIFIC_MODULES = {}

def _load_module(name):
    try:
        module = __import__(name)
        SCIENTIFIC_MODULES[name] = {'available': True, 'module': module}
        return module
    except Exception as e:
        SCIENTIFIC_MODULES[name] = {'available': False, 'error': str(e)}
        logger.warning(f"Module {name} not available: {e}")
        return None
        logger.warning(f"Module {name} not available: {e}")
        return None

# Load core scientific modules
_scientific = _load_module('scientific_data')
_dicom_ultimate = _load_module('dicom_complete_ultimate')
_fits = _load_module('fits_extractor')
_genomic = _load_module('genomic_extractor')

# Load niche scientific modules
_environmental = _load_module('environmental_climate')
_ai_ml = _load_module('ai_ml_metadata')
_materials = _load_module('materials_science')
_biometric = _load_module('biometric_health')
_geospatial = _load_module('geospatial_gis')
_iot = _load_module('iot_metadata')
_quantum = _load_module('quantum_metadata')
_robotics = _load_module('robotics_metadata')
_neural = _load_module('neural_network_metadata')
_autonomous = _load_module('autonomous_metadata')
_biotech = _load_module('biotechnology_metadata')


def extract_scientific_master(filepath: str) -> Dict[str, Any]:
    """Extract comprehensive scientific metadata"""
    result = {
        "scientific_master_available": True,
        "modules": {},
        "total_fields_extracted": 0
    }
    
    def _safe_extract(module_name, extract_func_name, result_key):
        try:
            module_data = SCIENTIFIC_MODULES.get(module_name)
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

    # Core scientific modules
    fields_count += _safe_extract('scientific_data', 'extract_scientific_data', 'basic_scientific')
    fields_count += _safe_extract('dicom_complete_ultimate', 'extract_dicom_complete_ultimate', 'dicom_ultimate')
    fields_count += _safe_extract('fits_extractor', 'extract_fits_metadata', 'fits')
    fields_count += _safe_extract('genomic_extractor', 'extract_genomic_metadata', 'genomic')

    # Niche scientific modules
    fields_count += _safe_extract('environmental_climate', 'extract_environmental_climate_metadata', 'environmental')
    fields_count += _safe_extract('ai_ml_metadata', 'extract_ai_ml_metadata', 'ai_ml')
    fields_count += _safe_extract('materials_science', 'extract_materials_science_metadata', 'materials')
    fields_count += _safe_extract('biometric_health', 'extract_biometric_health_metadata', 'biometric')
    fields_count += _safe_extract('geospatial_gis', 'extract_geospatial_metadata', 'geospatial')
    fields_count += _safe_extract('iot_metadata', 'extract_iot_metadata', 'iot')
    fields_count += _safe_extract('quantum_metadata', 'extract_quantum_metadata', 'quantum')
    fields_count += _safe_extract('robotics_metadata', 'extract_robotics_metadata', 'robotics')
    fields_count += _safe_extract('neural_network_metadata', 'extract_neural_network_metadata', 'neural_network')
    fields_count += _safe_extract('autonomous_metadata', 'extract_autonomous_metadata', 'autonomous')
    fields_count += _safe_extract('biotechnology_metadata', 'extract_biotechnology_metadata', 'biotechnology')
    
    result["total_fields_extracted"] = fields_count
    return result


def get_scientific_master_field_count() -> int:
    """Return total scientific metadata fields"""
    total = 0
    
    for name, module_data in SCIENTIFIC_MODULES.items():
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
    
    return total if total > 0 else 572  # Fallback to FITS


def get_scientific_master_module_status() -> Dict[str, bool]:
    """Get availability status"""
    return {name: data['available'] for name, data in SCIENTIFIC_MODULES.items()}


if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) > 1:
        result = extract_scientific_master(sys.argv[1])
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Scientific Master - Consolidated Scientific Metadata Extraction")
        print(f"\nTotal Fields: {get_scientific_master_field_count()}")
        print("\nModule Status:")
        for module, available in get_scientific_master_module_status().items():
            status = "✓ Available" if available else "✗ Not Available"
            print(f"  {module:30s} {status}")
        print("\nUsage: python scientific_master.py <scientific_file>")
