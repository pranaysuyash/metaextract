"""
Scientific Format Parsers - Unified Architecture
==================================================

Format-specific parsers for scientific/medical imaging formats:
- DICOM: Medical imaging (CT, MRI, X-Ray, Ultrasound, etc.)
- FITS: Astronomical imaging (astronomy research data)
- HDF5: Scientific data (climate, simulation, sensor data)
- NetCDF: Climate/atmospheric data
- NIfTI: Neuroimaging data (MRI, fMRI, brain imaging)

Key Principles:
1. Each parser extracts ONLY what the format supports
2. No synthetic/placeholder modules
3. Proper field counting (non-null leaf values only)
4. Native library support (pydicom, astropy, h5py, netCDF4, nibabel)

DICOM Tags Reference: NEMA PS3.6 (DICOM Data Elements)
FITS Standard: FITS 4.0 (IAU)
NIfTI Reference: https://nifti.nimh.nih.gov/
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path
import struct
import datetime

logger = logging.getLogger(__name__)


class ScientificParser(ABC):
    """Base class for all scientific format parsers."""
    
    FORMAT_NAME: str = "base"
    SUPPORTED_EXTENSIONS: List[str] = []
    
    @abstractmethod
    def parse(self, filepath: str) -> Dict[str, Any]:
        """Parse the scientific file and return metadata dict."""
        pass
    
    @abstractmethod
    def get_real_field_count(self, metadata: Dict[str, Any]) -> int:
        """Count only non-null leaf values."""
        pass
    
    @abstractmethod
    def can_parse(self, filepath: str) -> bool:
        """Check if this parser can handle the file."""
        pass
    
    def _count_real_fields(self, data: Any, depth: int = 0, max_depth: int = 10) -> int:
        """Count only non-null leaf values."""
        if depth > max_depth:
            return 0
            
        bookkeeping_keys = {
            'source', 'errors', 'warnings', 'performance', 'extraction_info',
            'fields_extracted', 'available', 'analysis_type', 'optimized_mode',
            'fallback_mode', 'status', 'duration_seconds'
        }
        
        if isinstance(data, dict):
            count = 0
            for key, value in data.items():
                if key in bookkeeping_keys:
                    continue
                if key.startswith('_'):
                    continue
                count += self._count_real_fields(value, depth + 1, max_depth)
            return count
            
        elif isinstance(data, list):
            count = 0
            for item in data:
                count += self._count_real_fields(item, depth + 1, max_depth)
            return count
            
        else:
            if data is None:
                return 0
            if isinstance(data, (str, bytes)):
                if not data or data in ['', b'', 'unknown', 'N/A', 'none', 'null']:
                    return 0
                return 1
            if isinstance(data, (int, float)):
                if data == 0:
                    return 0
                return 1
            if isinstance(data, bool):
                return 1 if data else 0
            return 0


class ScientificParserRegistry:
    """Registry of all available scientific format parsers."""
    
    def __init__(self):
        self._parsers: Dict[str, ScientificParser] = {}
        self._register_default_parsers()
    
    def _register_default_parsers(self):
        """Register all default format parsers."""
        from .dicom_parser import DicomParser
        from .fits_parser import FitsParser
        from .hdf5_netcdf_parser import Hdf5Parser, NetcdfParser
        from .nifti_parser import NiftiParser
        
        self.register(DicomParser())
        self.register(FitsParser())
        self.register(Hdf5Parser())
        self.register(NetcdfParser())
        self.register(NiftiParser())
    
    def register(self, parser: ScientificParser):
        """Register a format parser."""
        for ext in parser.SUPPORTED_EXTENSIONS:
            self._parsers[ext.lower()] = parser
    
    def get_parser(self, filepath: str) -> Optional[ScientificParser]:
        """Get the appropriate parser for a file."""
        filepath_lower = filepath.lower()
        if filepath_lower.endswith('.nii.gz'):
            return self._parsers.get('.nii.gz')
        ext = Path(filepath).suffix.lower()
        return self._parsers.get(ext)
    
    def get_all_parsers(self) -> List[ScientificParser]:
        """Get all registered parsers."""
        return list(self._parsers.values())
    
    def get_supported_extensions(self) -> List[str]:
        """Get all supported file extensions."""
        return list(self._parsers.keys())


_registry: Optional[ScientificParserRegistry] = None


def get_parser_registry() -> ScientificParserRegistry:
    """Get the global parser registry."""
    global _registry
    if _registry is None:
        _registry = ScientificParserRegistry()
    return _registry


def parse_scientific_metadata(filepath: str) -> Dict[str, Any]:
    """
    Unified entry point for parsing scientific metadata.
    
    Args:
        filepath: Path to the scientific file
        
    Returns:
        Dictionary containing:
        - format: Format name
        - metadata: Extracted metadata
        - fields_extracted: Count of real fields
        - supported: Whether format is supported
    """
    registry = get_parser_registry()
    parser = registry.get_parser(filepath)
    
    if not parser:
        return {
            "success": False,
            "format": "unknown",
            "supported": False,
            "error": f"Unsupported format: {Path(filepath).suffix}",
            "fields_extracted": 0,
            "metadata": {}
        }
    
    if not Path(filepath).exists():
        return {
            "success": False,
            "format": parser.FORMAT_NAME,
            "supported": True,
            "error": "File not found",
            "fields_extracted": 0,
            "metadata": {}
        }
    
    try:
        metadata = parser.parse(filepath)
        real_fields = parser.get_real_field_count(metadata)
        
        return {
            "success": True,
            "format": parser.FORMAT_NAME,
            "supported": True,
            "fields_extracted": real_fields,
            "metadata": metadata,
            "extraction_method": "native"
        }
    except Exception as e:
        logger.error(f"Parsing failed for {filepath}: {e}")
        return {
            "success": False,
            "format": parser.FORMAT_NAME if parser else "unknown",
            "supported": True,
            "error": str(e)[:200],
            "fields_extracted": 0,
            "metadata": {}
        }
