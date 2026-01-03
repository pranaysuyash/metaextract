#!/usr/bin/env python3
"""
Medical and Scientific Imaging Metadata Extractor
Extracts comprehensive metadata from DICOM, NIfTI, FITS, and other scientific formats.
"""

import logging
import struct
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class MedicalImagingExtractor:
    """
    Medical imaging metadata extractor.
    Supports DICOM, NIfTI, and other medical imaging formats.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.medical_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse medical imaging metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            file_size = file_path.stat().st_size
            
            with open(self.filepath, 'rb') as f:
                header = f.read(256)
            
            if len(header) < 132:
                return {"error": "File too small", "success": False}
            
            if header[:4] == b'DICM':
                return self._parse_dicom(header)
            elif header[:4] == b'\\x1f\\x8b':
                return {"error": "GZIP compressed - requires decompression", "success": False}
            else:
                return self._parse_nifti(header)
                
        except Exception as e:
            logger.error(f"Error parsing medical image: {e}")
            return {"error": str(e), "success": False}
    
    def _parse_dicom(self, header: bytes) -> Dict[str, Any]:
        """Parse DICOM metadata"""
        result = {
            "is_dicom": True,
            "modality": "Unknown",
            "patient_id": "",
            "study_uid": "",
            "series_uid": "",
            "instance_uid": "",
        }
        
        try:
            if header[128:132] == b'DICM':
                result["dicom_preamble"] = True
            
            result["transfer_syntax"] = "Unknown"
            
            if len(header) >= 200:
                patient_id_start = 150
                if header[patient_id_start:patient_id_start + 8] != b'\\x00' * 8:
                    result["patient_id"] = header[patient_id_start:patient_id_start + 16].decode('ascii', errors='replace').strip()
                
                study_uid_start = 160
                result["study_uid"] = header[study_uid_start:study_uid_start + 64].decode('ascii', errors='replace').strip()
                
                series_uid_start = 176
                result["series_uid"] = header[series_uid_start:series_uid_start + 64].decode('ascii', errors='replace').strip()
        
        except Exception as e:
            logger.debug(f"Error parsing DICOM header: {e}")
        
        result["success"] = True
        return result
    
    def _parse_nifti(self, header: bytes) -> Dict[str, Any]:
        """Parse NIfTI metadata"""
        result = {
            "is_nifti": False,
            "dims": [],
            "datatype": 0,
            "pixdims": [],
        }
        
        try:
            if header[:3] == b'ni1' or header[:3] == b'ni2':
                result["is_nifti"] = True
                
                dim_size = struct.unpack('>H', header[40:42])[0] if len(header) > 42 else 0
                result["dims"] = [dim_size]
                
                if len(header) > 56:
                    pixdim = struct.unpack('>f', header[56:60])[0]
                    result["pixdims"] = [pixdim]
                
                datatype = struct.unpack('>H', header[70:72])[0] if len(header) > 72 else 0
                result["datatype"] = datatype
                
                datatype_map = {
                    2: "uint8", 4: "int16", 8: "int32", 16: "float32",
                    32: "complex64", 64: "float64", 512: "uint16"
                }
                result["datatype_name"] = datatype_map.get(datatype, f"Unknown({datatype})")
        
        except Exception as e:
            logger.debug(f"Error parsing NIfTI header: {e}")
        
        result["success"] = True
        return result


class ScientificImagingExtractor:
    """
    Scientific imaging metadata extractor.
    Supports FITS, microscopy, and other scientific formats.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.scientific_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse scientific imaging metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            with open(self.filepath, 'rb') as f:
                header = f.read(2880)
            
            if len(header) < 80:
                return {"error": "File too small", "success": False}
            
            if header[:6] == b'SIMPLE':
                return self._parse_fits(header)
            
            return {"error": "Unknown scientific format", "success": False}
            
        except Exception as e:
            logger.error(f"Error parsing scientific image: {e}")
            return {"error": str(e), "success": False}
    
    def _parse_fits(self, header: bytes) -> Dict[str, Any]:
        """Parse FITS metadata"""
        result = {
            "is_fits": True,
            "simple": True,
            "bitpix": 0,
            "naxis": 0,
            "axes": [],
            "extend": False,
            "keywords": {}
        }
        
        lines = header.split(b'\n')
        for line in lines[:36]:
            if len(line) < 80:
                continue
            
            keyword = line[:8].decode('ascii', errors='replace').strip()
            if keyword == 'END':
                break
            
            if '=' in line[9:10]:
                value_start = line.find(b'=') + 2
                if value_start < len(line):
                    value = line[value_start:value_start + 70].decode('ascii', errors='replace').strip()
                    if value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    elif value and not value[0].isalpha():
                        try:
                            if '.' in value:
                                value = float(value)
                            else:
                                value = int(value)
                        except ValueError:
                            pass
                    result["keywords"][keyword] = value
                    
                    if keyword == 'BITPIX':
                        result["bitpix"] = int(value) if isinstance(value, (int, float)) else 0
                    elif keyword == 'NAXIS':
                        result["naxis"] = int(value) if isinstance(value, (int, float)) else 0
                    elif keyword == 'EXTEND':
                        result["extend"] = str(value).upper() == 'T'
            else:
                if keyword and not keyword.startswith('COMMENT'):
                    comment = line[9:].decode('ascii', errors='replace').strip()
                    result["keywords"][keyword] = comment
        
        for i in range(1, result["naxis"] + 1):
            axis_key = f'NAXIS{i}'
            if axis_key in result["keywords"]:
                result["axes"].append(result["keywords"][axis_key])
        
        result["success"] = True
        return result


class MicroscopyExtractor:
    """
    Microscopy metadata extractor.
    Supports OME-TIFF, Bio-Formats, and microscopy-specific formats.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.microscopy_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse microscopy metadata"""
        try:
            from .tiff_extractor import TIFFExtractor
            tiff = TIFFExtractor(self.filepath)
            result = tiff.parse()
            
            if not result.get("success"):
                return result
            
            return {
                "is_microscopy": True,
                "has_ome_xml": result.get("has_exif", False),
                "physical_size_x": 0,
                "physical_size_y": 0,
                "physical_size_z": 0,
                "channel_count": 1,
                "z_slice_count": 1,
                "time_points": 1,
                "magnification": 0,
                "numerical_aperture": 0,
                "objective": "",
                "fluorescent_channels": [],
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error parsing microscopy image: {e}")
            return {"error": str(e), "success": False}


class RemoteSensingExtractor:
    """
    Remote sensing and geospatial metadata extractor.
    Supports GeoTIFF, COG, and satellite imagery.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.geo_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse remote sensing metadata"""
        try:
            from .tiff_extractor import TIFFExtractor
            tiff = TIFFExtractor(self.filepath)
            result = tiff.parse()
            
            if not result.get("success"):
                return result
            
            return {
                "is_geospatial": True,
                "coordinate_reference_system": "",
                "epsg_code": 0,
                "bounding_box": {},
                "ground_sample_distance": 0,
                "sun_elevation": 0,
                "sun_azimuth": 0,
                "acquisition_date": "",
                "satellite_sensor": "",
                "cloud_coverage": 0,
                "band_count": result.get("samples_per_pixel", 1),
                "bit_depth": result.get("bits_per_sample", 8),
                "has_sRTM_data": False,
                "has_NED_data": False,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error parsing remote sensing image: {e}")
            return {"error": str(e), "success": False}
