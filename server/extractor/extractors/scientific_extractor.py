"""
Scientific Extractor - Phase 2.4 Implementation
Handles DICOM, FITS, HDF5, NetCDF, GeoTIFF with streaming optimization
Built with performance optimization recommendations from parallel agents
"""

import logging
import struct
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Iterator, List, Union
from datetime import datetime
import json
import base64

from ..core.base_engine import BaseExtractor, ExtractionContext
from ..streaming import StreamingMetadataExtractor, ProcessingChunk, StreamingConfig

logger = logging.getLogger(__name__)


@dataclass
class ScientificMetadata:
    """Scientific format metadata structure"""
    format_type: str
    headers: Dict[str, Any]
    properties: Dict[str, Any]
    statistics: Dict[str, Any]
    dimensions: Optional[Dict[str, int]] = None
    coordinate_system: Optional[Dict[str, Any]] = None
    instrument_info: Optional[Dict[str, Any]] = None
    processing_history: Optional[List[Dict[str, Any]]] = None


class Category:
    """Registry categories for scientific formats"""
    MEDICAL_IMAGING = "medical_imaging"
    ASTRONOMY = "astronomy"
    SCIENTIFIC_DATA = "scientific_data"
    CLIMATE_DATA = "climate_data"
    GEOSPATIAL = "geospatial"


class ScientificExtractor(BaseExtractor):
    """
    Scientific data format extractor with streaming support
    Handles: DICOM (medical), FITS (astronomy), HDF5 (scientific), 
    NetCDF (climate), GeoTIFF (geospatial)
    """
    
    # Supported scientific formats
    supported_formats = [
        # Medical Imaging (DICOM)
        '.dcm', '.dicom', '.ima',
        
        # Astronomy (FITS)
        '.fits', '.fit', '.fts',
        
        # Scientific Data (HDF5)
        '.h5', '.hdf5', '.he5', '.hdf',
        
        # Climate/Scientific (NetCDF)
        '.nc', '.nc4', '.cdf',
        
        # Geospatial (GeoTIFF)
        '.tif', '.tiff', '.geotiff', '.gtiff'
    ]
    
    # Registry categories for scientific formats
    registry_categories = {
        'dicom': Category.MEDICAL_IMAGING,
        'fits': Category.ASTRONOMY,
        'hdf5': Category.SCIENTIFIC_DATA,
        'netcdf': Category.CLIMATE_DATA,
        'geotiff': Category.GEOSPATIAL
    }
    
    # Default streaming setting
    _streaming_enabled = True
    streaming_extractor = None  # Default to None
    
    def __init__(self):
        super().__init__(name="scientific", supported_formats=self.supported_formats)

        # Initialize streaming components
        self._streaming_enabled = True  # Enable streaming by default for large files
        try:
            streaming_config = StreamingConfig(chunk_size=5_000_000)
            self.streaming_extractor = StreamingMetadataExtractor(streaming_config)
        except Exception as e:
            logger.warning(f"Failed to initialize streaming extractor: {e}")
            self.streaming_extractor = None
        
    def _extract_metadata(self, context: ExtractionContext) -> Dict[str, Any]:
        """
        Extract metadata from scientific files using streaming when beneficial
        """
        file_path = context.filepath
        file_size = context.file_size
        
        # Determine format and extraction strategy
        file_ext = Path(file_path).suffix.lower()
        format_type = self._detect_format(file_ext, file_path)
        
        # Use streaming for files >50MB or known problematic formats
        use_streaming = self._streaming_enabled and self.streaming_extractor is not None and (
            file_size > 50_000_000 or  # 50MB threshold
            format_type in ['fits', 'hdf5'] or  # Known large formats
            file_size > 500_000_000  # Always stream 500MB+
        )
        
        logger.info(f"Extracting {format_type.upper()} from {file_path} "
                   f"({file_size / 1_000_000:.1f}MB) - "
                   f"{'streaming' if use_streaming else 'standard'} mode")
        
        try:
            if use_streaming:
                return self._extract_with_streaming(file_path, format_type, context)
            else:
                return self._extract_standard(file_path, format_type, context)
                
        except Exception as e:
            logger.error(f"Failed to extract {format_type} from {file_path}: {e}")
            return self._build_error_result(file_path, format_type, str(e))
    
    def _detect_format(self, file_ext: str, file_path: str) -> str:
        """Detect scientific format from extension and file content"""
        format_map = {
            '.dcm': 'dicom', '.dicom': 'dicom', '.ima': 'dicom',
            '.fits': 'fits', '.fit': 'fits', '.fts': 'fits',
            '.h5': 'hdf5', '.hdf5': 'hdf5', '.he5': 'hdf5', '.hdf': 'hdf5',
            '.nc': 'netcdf', '.nc4': 'netcdf', '.cdf': 'netcdf',
            '.tif': 'geotiff', '.tiff': 'geotiff', '.geotiff': 'geotiff', '.gtiff': 'geotiff'
        }
        
        base_format = format_map.get(file_ext, 'unknown')
        
        # Validate with file signature for ambiguous extensions
        if base_format == 'geotiff' or base_format == 'unknown':
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(8)
                    if header[:4] == b'II*\x00' or header[:4] == b'MM\x00*':
                        # TIFF signature, check for GeoTIFF tags
                        if self._has_geotiff_tags(file_path):
                            return 'geotiff'
            except Exception:
                pass
                
        return base_format
    
    def _extract_with_streaming(self, file_path: str, format_type: str, context: ExtractionContext) -> Dict[str, Any]:
        """Extract metadata using streaming for large files"""
        metadata = ScientificMetadata(
            format_type=format_type,
            headers={},
            properties={},
            statistics={},
            dimensions=None,
            coordinate_system=None,
            instrument_info=None,
            processing_history=None
        )
        
        # Format-specific streaming extraction
        if format_type == 'dicom':
            metadata = self._stream_dicom(file_path, metadata)
        elif format_type == 'fits':
            metadata = self._stream_fits(file_path, metadata)
        elif format_type == 'hdf5':
            metadata = self._stream_hdf5(file_path, metadata)
        elif format_type == 'netcdf':
            metadata = self._stream_netcdf(file_path, metadata)
        elif format_type == 'geotiff':
            metadata = self._stream_geotiff(file_path, metadata)
        else:
            # Fallback to standard extraction
            return self._extract_standard(file_path, format_type, context)
        
        # Build registry summary
        registry_summary = self._build_registry_summary(metadata, format_type)
        
        return {
            'scientific_format': format_type,
            'metadata': metadata.__dict__,
            'registry_summary': registry_summary,
            'extraction_method': 'streaming',
            'file_size': Path(file_path).stat().st_size,
            'processing_stats': {
                'chunks_processed': self.streaming_extractor.processed_bytes // self.streaming_extractor.config.chunk_size,
                'bytes_processed': self.streaming_extractor.processed_bytes
            }
        }
    
    def _extract_standard(self, file_path: str, format_type: str, context: ExtractionContext) -> Dict[str, Any]:
        """Standard extraction for smaller files"""
        metadata = ScientificMetadata(
            format_type=format_type,
            headers={},
            properties={},
            statistics={}
        )
        
        # Format-specific standard extraction
        if format_type == 'dicom':
            metadata = self._extract_dicom(file_path, metadata)
        elif format_type == 'fits':
            metadata = self._extract_fits(file_path, metadata)
        elif format_type == 'hdf5':
            metadata = self._extract_hdf5(file_path, metadata)
        elif format_type == 'netcdf':
            metadata = self._extract_netcdf(file_path, metadata)
        elif format_type == 'geotiff':
            metadata = self._extract_geotiff(file_path, metadata)
        
        # Build registry summary
        registry_summary = self._build_registry_summary(metadata, format_type)
        
        return {
            'scientific_format': format_type,
            'metadata': metadata.__dict__,
            'registry_summary': registry_summary,
            'extraction_method': 'standard',
            'file_size': Path(file_path).stat().st_size
        }
    
    def _stream_dicom(self, file_path: str, metadata: ScientificMetadata) -> ScientificMetadata:
        """Stream DICOM file extraction"""
        try:
            # Import pydicom if available
            try:
                import pydicom
                from pydicom import dcmread
                from pydicom.errors import InvalidDicomError
            except ImportError:
                logger.warning("pydicom not available, using fallback parser")
                return self._stream_dicom_fallback(file_path, metadata)
            
            # Use pydicom's streaming capabilities
            ds = dcmread(file_path, stop_before_pixels=True)  # Only read metadata
            
            metadata.headers = {
                'patient_id': getattr(ds, 'PatientID', None),
                'study_id': getattr(ds, 'StudyID', None),
                'series_id': getattr(ds, 'SeriesInstanceUID', None),
                'instance_id': getattr(ds, 'SOPInstanceUID', None),
                'modality': getattr(ds, 'Modality', None),
                'study_date': getattr(ds, 'StudyDate', None),
                'manufacturer': getattr(ds, 'Manufacturer', None),
                'model_name': getattr(ds, 'ManufacturerModelName', None)
            }
            
            metadata.properties = {
                'bits_allocated': getattr(ds, 'BitsAllocated', None),
                'bits_stored': getattr(ds, 'BitsStored', None),
                'samples_per_pixel': getattr(ds, 'SamplesPerPixel', None),
                'photometric_interpretation': getattr(ds, 'PhotometricInterpretation', None),
                'rows': getattr(ds, 'Rows', None),
                'columns': getattr(ds, 'Columns', None),
                'pixel_spacing': getattr(ds, 'PixelSpacing', None),
                'slice_thickness': getattr(ds, 'SliceThickness', None)
            }
            
            metadata.dimensions = {
                'rows': getattr(ds, 'Rows', 0),
                'columns': getattr(ds, 'Columns', 0),
                'slices': getattr(ds, 'NumberOfFrames', 1)
            }
            
            metadata.instrument_info = {
                'manufacturer': getattr(ds, 'Manufacturer', None),
                'model': getattr(ds, 'ManufacturerModelName', None),
                'software_versions': getattr(ds, 'SoftwareVersions', None)
            }
            
        except Exception as e:
            logger.error(f"DICOM streaming failed: {e}")
            return self._stream_dicom_fallback(file_path, metadata)
        
        return metadata
    
    def _stream_dicom_fallback(self, file_path: str, metadata: ScientificMetadata) -> ScientificMetadata:
        """Fallback DICOM parser using streaming"""
        try:
            with open(file_path, 'rb') as f:
                # Read DICOM header (first 132 bytes minimum)
                header = f.read(132)
                
                if len(header) < 132:
                    raise ValueError("File too small for DICOM")
                
                # Check for DICOM preamble and prefix
                if header[128:132] == b'DICM':
                    metadata.headers['format'] = 'DICOM with preamble'
                else:
                    metadata.headers['format'] = 'DICOM without preamble'
                
                # Basic metadata extraction through streaming
                # This is a simplified version - real implementation would parse DICOM tags
                metadata.properties['file_size'] = Path(file_path).stat().st_size
                metadata.properties['has_preamble'] = header[128:132] == b'DICM'
                
        except Exception as e:
            logger.error(f"DICOM fallback streaming failed: {e}")
            
        return metadata
    
    def _stream_fits(self, file_path: str, metadata: ScientificMetadata) -> ScientificMetadata:
        """Stream FITS file extraction with memory optimization"""
        try:
            # Try astropy first, fallback to custom parser
            try:
                from astropy.io import fits
                # Use memmap for large FITS files
                with fits.open(file_path, memmap=True) as hdul:
                    metadata = self._extract_fits_headers(hdul, metadata)
                    return metadata
            except ImportError:
                logger.warning("astropy not available, using FITS streaming parser")
                
        except Exception as e:
            logger.error(f"FITS astropy extraction failed: {e}")
        
        # Fallback to streaming parser
        return self._stream_fits_custom(file_path, metadata)
    
    def _stream_fits_custom(self, file_path: str, metadata: ScientificMetadata) -> ScientificMetadata:
        """Custom FITS streaming parser for memory efficiency"""
        try:
            with open(file_path, 'rb') as f:
                # Read primary HDU header
                header_data = bytearray()
                while True:
                    chunk = f.read(2880)  # FITS standard block size
                    if not chunk:
                        break
                    
                    header_data.extend(chunk)
                    
                    # Check for END keyword
                    if b'END     ' in chunk:
                        break
                
                # Parse FITS header cards
                header_text = header_data.decode('ascii', errors='ignore')
                cards = [header_text[i:i+80] for i in range(0, len(header_text), 80)]
                
                headers = {}
                for card in cards:
                    if card.startswith('END'):
                        break
                    if '=' in card:
                        key, value = card.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip("'\" ")
                        if key and value:
                            headers[key] = value
                
                metadata.headers = headers
                metadata.properties['format'] = 'FITS'
                metadata.properties['streaming_parser'] = 'custom'
                
                # Extract key FITS information
                if 'BITPIX' in headers:
                    metadata.properties['bitpix'] = int(headers['BITPIX'])
                if 'NAXIS' in headers:
                    metadata.properties['naxis'] = int(headers['NAXIS'])
                if 'NAXIS1' in headers:
                    metadata.properties['naxis1'] = int(headers['NAXIS1'])
                if 'NAXIS2' in headers:
                    metadata.properties['naxis2'] = int(headers['NAXIS2'])
                
                # Dimensions
                naxis = metadata.properties.get('naxis', 0)
                if naxis > 0:
                    metadata.dimensions = {}
                    for i in range(1, naxis + 1):
                        axis_key = f'NAXIS{i}'
                        if axis_key in headers:
                            metadata.dimensions[f'axis_{i}'] = int(headers[axis_key])
                
        except Exception as e:
            logger.error(f"FITS custom streaming failed: {e}")
            
        return metadata
    
    def _stream_hdf5(self, file_path: str, metadata: ScientificMetadata) -> ScientificMetadata:
        """Stream HDF5 file extraction"""
        try:
            import h5py
            
            # Use h5py with chunking for large files
            with h5py.File(file_path, 'r') as hdf_file:
                metadata = self._extract_hdf5_structure(hdf_file, metadata)
                
        except ImportError:
            logger.warning("h5py not available, using fallback")
            return self._stream_hdf5_fallback(file_path, metadata)
        except Exception as e:
            logger.error(f"HDF5 streaming failed: {e}")
            return self._stream_hdf5_fallback(file_path, metadata)
            
        return metadata
    
    def _extract_hdf5_structure(self, hdf_file: Any, metadata: ScientificMetadata) -> ScientificMetadata:
        """Extract HDF5 structure and metadata"""
        def collect_group_info(name: str, obj: Any) -> None:
            """Collect information about HDF5 groups and datasets"""
            if isinstance(obj, h5py.Dataset):
                dataset_info = {
                    'name': name,
                    'shape': obj.shape,
                    'dtype': str(obj.dtype),
                    'size': obj.size
                }
                metadata.properties.setdefault('datasets', []).append(dataset_info)
            elif isinstance(obj, h5py.Group):
                group_info = {
                    'name': name,
                    'items': len(list(obj.keys()))
                }
                metadata.properties.setdefault('groups', []).append(group_info)
        
        # Traverse HDF5 structure
        hdf_file.visititems(collect_group_info)
        
        # Extract file-level attributes
        for attr_name, attr_value in hdf_file.attrs.items():
            metadata.headers[attr_name] = str(attr_value)
        
        # Basic file properties
        metadata.properties['format'] = 'HDF5'
        metadata.properties['version'] = hdf_file.libver
        metadata.properties['num_objects'] = len(list(hdf_file.keys()))
        
        return metadata
    
    def _stream_hdf5_fallback(self, file_path: str, metadata: ScientificMetadata) -> ScientificMetadata:
        """Fallback HDF5 parser using basic file reading"""
        try:
            with open(file_path, 'rb') as f:
                # Read HDF5 signature (first 8 bytes)
                signature = f.read(8)
                
                if signature == b'\x89HDF\r\n\x1a\n':
                    metadata.headers['format'] = 'HDF5'
                    metadata.headers['signature_valid'] = True
                else:
                    metadata.headers['format'] = 'Unknown'
                    metadata.headers['signature_valid'] = False
                
                # Basic file properties
                metadata.properties['file_size'] = Path(file_path).stat().st_size
                metadata.properties['has_hdf_signature'] = signature == b'\x89HDF\r\n\x1a\n'
                
        except Exception as e:
            logger.error(f"HDF5 fallback failed: {e}")
            
        return metadata
    
    def _stream_netcdf(self, file_path: str, metadata: ScientificMetadata) -> ScientificMetadata:
        """Stream NetCDF file extraction"""
        try:
            import netCDF4 as nc
            
            # Use netCDF4 for efficient reading
            with nc.Dataset(file_path, 'r') as dataset:
                metadata = self._extract_netcdf_metadata(dataset, metadata)
                
        except ImportError:
            logger.warning("netCDF4 not available, using fallback")
            return self._stream_netcdf_fallback(file_path, metadata)
        except Exception as e:
            logger.error(f"NetCDF streaming failed: {e}")
            return self._stream_netcdf_fallback(file_path, metadata)
            
        return metadata
    
    def _extract_netcdf_metadata(self, dataset: Any, metadata: ScientificMetadata) -> ScientificMetadata:
        """Extract NetCDF metadata"""
        # Global attributes
        for attr_name in dataset.ncattrs():
            metadata.headers[attr_name] = str(getattr(dataset, attr_name))
        
        # Variables
        variables_info = []
        for var_name, variable in dataset.variables.items():
            var_info = {
                'name': var_name,
                'dimensions': list(variable.dimensions),
                'shape': variable.shape,
                'dtype': str(variable.dtype),
                'attributes': {}
            }
            
            # Variable attributes
            for attr_name in variable.ncattrs():
                var_info['attributes'][attr_name] = str(getattr(variable, attr_name))
            
            variables_info.append(var_info)
        
        metadata.properties['variables'] = variables_info
        # Extract dimensions safely
        dimensions_info = {}
        for dim_name, dimension in dataset.dimensions.items():
            try:
                dimensions_info[dim_name] = len(dimension)
            except:
                dimensions_info[dim_name] = str(dimension)
        metadata.properties['dimensions'] = dimensions_info
        metadata.properties['format'] = 'NetCDF'
        metadata.properties['version'] = dataset.data_model
        
        return metadata
    
    def _stream_netcdf_fallback(self, file_path: str, metadata: ScientificMetadata) -> ScientificMetadata:
        """Fallback NetCDF parser"""
        try:
            with open(file_path, 'rb') as f:
                # Check for NetCDF signature variants
                header = f.read(4)
                
                netcdf_signatures = {
                    b'CDF\x01': 'NetCDF classic format',
                    b'CDF\x02': 'NetCDF 64-bit format',
                    b'\x89HDF': 'NetCDF-4 (HDF5 based)'
                }
                
                if header in netcdf_signatures:
                    metadata.headers['format'] = netcdf_signatures[header]
                    metadata.headers['signature_valid'] = True
                else:
                    metadata.headers['format'] = 'Unknown'
                    metadata.headers['signature_valid'] = False
                
                metadata.properties['file_size'] = Path(file_path).stat().st_size
                metadata.properties['detected_signature'] = header.hex()
                
        except Exception as e:
            logger.error(f"NetCDF fallback failed: {e}")
            
        return metadata
    
    def _stream_geotiff(self, file_path: str, metadata: ScientificMetadata) -> ScientificMetadata:
        """Stream GeoTIFF extraction"""
        try:
            try:
                import rasterio
                with rasterio.open(file_path) as dataset:
                    metadata = self._extract_geotiff_metadata(dataset, metadata)
                    return metadata
            except ImportError:
                logger.warning("rasterio not available, using fallback")
                
        except Exception as e:
            logger.error(f"GeoTIFF rasterio extraction failed: {e}")
        
        # Fallback to streaming parser
        return self._stream_geotiff_custom(file_path, metadata)
    
    def _extract_geotiff_metadata(self, dataset: Any, metadata: ScientificMetadata) -> ScientificMetadata:
        """Extract GeoTIFF metadata using rasterio"""
        # Basic raster properties
        metadata.properties.update({
            'width': dataset.width,
            'height': dataset.height,
            'count': dataset.count,
            'dtype': dataset.dtypes[0] if dataset.dtypes else None,
            'crs': str(dataset.crs) if dataset.crs else None,
            'transform': list(dataset.transform) if dataset.transform else None,
            'format': 'GeoTIFF'
        })
        
        # Coordinate system
        if dataset.crs:
            metadata.coordinate_system = {
                'crs': str(dataset.crs),
                'units': dataset.crs.linear_units if hasattr(dataset.crs, 'linear_units') else None
            }
        
        # Bounds and dimensions
        if dataset.bounds:
            metadata.dimensions = {
                'width': dataset.width,
                'height': dataset.height,
                'bounds': list(dataset.bounds)
            }
        
        # Tags/metadata
        if dataset.tags():
            metadata.headers = dict(dataset.tags())
        
        return metadata
    
    def _stream_geotiff_custom(self, file_path: str, metadata: ScientificMetadata) -> ScientificMetadata:
        """Custom GeoTIFF streaming parser"""
        try:
            with open(file_path, 'rb') as f:
                # Read TIFF header
                header = f.read(8)
                
                # Check byte order
                if header[:2] == b'II':
                    byte_order = 'little'
                elif header[:2] == b'MM':
                    byte_order = 'big'
                else:
                    raise ValueError("Invalid TIFF signature")
                
                # Version and IFD offset
                version = struct.unpack('<H' if byte_order == 'little' else '>H', header[2:4])[0]
                ifd_offset = struct.unpack('<I' if byte_order == 'little' else '>I', header[4:8])[0]
                
                metadata.headers.update({
                    'byte_order': byte_order,
                    'version': version,
                    'ifd_offset': ifd_offset
                })
                
                metadata.properties.update({
                    'format': 'TIFF/GeoTIFF',
                    'streaming_parser': 'custom',
                    'has_geotiff_tags': self._has_geotiff_tags(file_path)
                })
                
        except Exception as e:
            logger.error(f"GeoTIFF custom streaming failed: {e}")
            
        return metadata
    
    def _has_geotiff_tags(self, file_path: str) -> bool:
        """Check if TIFF file contains GeoTIFF tags"""
        try:
            with open(file_path, 'rb') as f:
                # Simple check for common GeoTIFF tags in first part of file
                chunk = f.read(10000)
                geotiff_keys = [b'GeoKey', b'ModelPixelScale', b'ModelTiepoint', b'GTiff']
                return any(key in chunk for key in geotiff_keys)
        except Exception:
            return False
    
    def _extract_dicom(self, file_path: str, metadata: ScientificMetadata) -> ScientificMetadata:
        """Standard DICOM extraction (non-streaming)"""
        try:
            import pydicom
            ds = pydicom.dcmread(file_path, stop_before_pixels=True)
            return self._extract_dicom_metadata(ds, metadata)
        except Exception as e:
            logger.error(f"Standard DICOM extraction failed: {e}")
            return metadata
    
    def _extract_dicom_metadata(self, ds: Any, metadata: ScientificMetadata) -> ScientificMetadata:
        """Extract DICOM metadata from dataset"""
        # Implementation same as streaming version
        metadata.headers = {
            'patient_id': getattr(ds, 'PatientID', None),
            'study_id': getattr(ds, 'StudyID', None),
            'modality': getattr(ds, 'Modality', None),
            'study_date': getattr(ds, 'StudyDate', None),
            'manufacturer': getattr(ds, 'Manufacturer', None)
        }
        
        metadata.properties = {
            'bits_allocated': getattr(ds, 'BitsAllocated', None),
            'rows': getattr(ds, 'Rows', None),
            'columns': getattr(ds, 'Columns', None)
        }
        
        return metadata
    
    def _extract_fits(self, file_path: str, metadata: ScientificMetadata) -> ScientificMetadata:
        """Standard FITS extraction (non-streaming)"""
        try:
            from astropy.io import fits
            with fits.open(file_path) as hdul:
                return self._extract_fits_headers(hdul, metadata)
        except Exception as e:
            logger.error(f"Standard FITS extraction failed: {e}")
            return metadata
    
    def _extract_fits_headers(self, hdul: Any, metadata: ScientificMetadata) -> ScientificMetadata:
        """Extract FITS headers from HDUList"""
        primary_header = hdul[0].header
        
        # Convert header to dict
        headers = {}
        for key in primary_header.keys():
            if key:
                headers[key] = str(primary_header[key])
        
        metadata.headers = headers
        metadata.properties['num_hdu'] = len(hdul)
        metadata.properties['format'] = 'FITS'
        
        # Extract dimensions
        if 'NAXIS' in primary_header:
            naxis = primary_header['NAXIS']
            metadata.dimensions = {}
            for i in range(1, naxis + 1):
                axis_key = f'NAXIS{i}'
                if axis_key in primary_header:
                    metadata.dimensions[f'axis_{i}'] = primary_header[axis_key]
        
        return metadata
    
    def _extract_hdf5(self, file_path: str, metadata: ScientificMetadata) -> ScientificMetadata:
        """Standard HDF5 extraction (non-streaming)"""
        try:
            import h5py
            with h5py.File(file_path, 'r') as hdf_file:
                return self._extract_hdf5_structure(hdf_file, metadata)
        except Exception as e:
            logger.error(f"Standard HDF5 extraction failed: {e}")
            return metadata
    
    def _extract_netcdf(self, file_path: str, metadata: ScientificMetadata) -> ScientificMetadata:
        """Standard NetCDF extraction (non-streaming)"""
        try:
            import netCDF4 as nc
            with nc.Dataset(file_path, 'r') as dataset:
                return self._extract_netcdf_metadata(dataset, metadata)
        except Exception as e:
            logger.error(f"Standard NetCDF extraction failed: {e}")
            return metadata
    
    def _extract_geotiff(self, file_path: str, metadata: ScientificMetadata) -> ScientificMetadata:
        """Standard GeoTIFF extraction (non-streaming)"""
        try:
            import rasterio
            with rasterio.open(file_path) as dataset:
                return self._extract_geotiff_metadata(dataset, metadata)
        except Exception as e:
            logger.error(f"Standard GeoTIFF extraction failed: {e}")
            return metadata
    
    def _build_registry_summary(self, metadata: ScientificMetadata, format_type: str) -> Dict[str, Any]:
        """Build registry summary for scientific format"""
        category = self.registry_categories.get(format_type, Category.SCIENTIFIC_DATA)
        
        # Count fields by category
        field_counts = {}
        
        # Headers count
        field_counts['headers'] = len(metadata.headers)
        
        # Properties count
        field_counts['properties'] = len(metadata.properties)
        
        # Special categories for scientific data
        field_counts['dimensions'] = 1 if metadata.dimensions else 0
        field_counts['coordinates'] = 1 if metadata.coordinate_system else 0
        field_counts['instrument'] = 1 if metadata.instrument_info else 0
        field_counts['processing'] = len(metadata.processing_history) if metadata.processing_history else 0
        
        return {
            'category': category,
            'field_counts': field_counts,
            'total_fields': sum(field_counts.values()),
            'locked_fields': 0,  # Will be set by tier system
            'format_type': format_type
        }
    
    def _build_error_result(self, file_path: str, format_type: str, error: str) -> Dict[str, Any]:
        """Build error result for failed extraction"""
        return {
            'scientific_format': format_type,
            'metadata': {
                'format_type': format_type,
                'headers': {},
                'properties': {},
                'statistics': {},
                'error': error
            },
            'registry_summary': {
                'category': self.registry_categories.get(format_type, Category.SCIENTIFIC_DATA),
                'field_counts': {},
                'total_fields': 0,
                'locked_fields': 0,
                'format_type': format_type,
                'error': True
            },
            'extraction_method': 'error',
            'file_size': Path(file_path).stat().st_size if Path(file_path).exists() else 0,
            'error': error
        }
    def __init__(self):
        super().__init__(name="scientific", supported_formats=self.supported_formats)
        
        # Initialize expanded scientific formats
        self.expanded_formats = self._define_expanded_scientific_formats()
        
        # Add expanded formats to supported formats
        for format_def in self.expanded_formats:
            for ext in format_def.extensions:
                if ext not in self.supported_formats:
                    self.supported_formats.append(ext)
    
    def _define_expanded_scientific_formats(self):
        """Define comprehensive scientific format catalog"""
        # This would contain all the expanded format definitions
        # For now, return empty list to avoid breaking existing functionality
        return []
    
    def get_expanded_scientific_formats(self):
        """Get all expanded scientific format definitions"""
        return self.expanded_formats
    
    def get_formats_by_category(self, category):
        """Get formats by scientific category"""
        return [fmt for fmt in self.expanded_formats if fmt.category == category]
    
    def get_large_file_formats(self, size_threshold_mb=50):
        """Get formats that typically exceed size threshold"""
        return [fmt for fmt in self.expanded_formats if fmt.typical_size_mb > size_threshold_mb]
    
    def get_streaming_recommended_formats(self):
        """Get formats that benefit from streaming extraction"""
        return [fmt for fmt in self.expanded_formats if fmt.streaming_recommended]
    
    def get_gpu_accelerated_formats(self):
        """Get formats that support GPU acceleration"""
        return [fmt for fmt in self.expanded_formats if fmt.gpu_accelerated]
    
    def get_parallel_capable_formats(self):
        """Get formats that support parallel processing"""
        return [fmt for fmt in self.expanded_formats if fmt.parallel_capable]
