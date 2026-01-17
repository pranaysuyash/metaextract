"""
HDF5 Parser
===========

Extracts metadata from HDF5 (Hierarchical Data Format) files.
Used for climate data, simulations, sensor data, and scientific datasets.

HDF5 Structure:
- Root group (/)
- Groups (like directories)
- Datasets (like arrays)
- Attributes (metadata on groups/datasets)
- Datatypes
- References
"""

from . import ScientificParser, logger
from typing import Dict, Any, Optional
import struct


class Hdf5Parser(ScientificParser):
    """HDF5-specific metadata parser."""
    
    FORMAT_NAME = "HDF5"
    SUPPORTED_EXTENSIONS = ['.h5', '.hdf5', '.he5']
    
    def parse(self, filepath: str) -> Dict[str, Any]:
        """Extract HDF5 metadata."""
        result = {}
        
        try:
            import h5py
            
            with h5py.File(filepath, 'r') as hdf:
                result = self._extract_hdf5_metadata(hdf)
                
        except ImportError:
            result = self._parse_basic_hdf5(filepath)
        except Exception as e:
            logger.warning(f"HDF5 parsing failed: {e}")
            result = {"error": str(e)[:200]}
        
        return result
    
    def _extract_hdf5_metadata(self, hdf) -> Dict[str, Any]:
        """Extract HDF5 metadata using h5py."""
        metadata = {}
        
        metadata['file_type'] = 'HDF5'
        metadata['hdf5_version'] = hdf.filename
        metadata['driver'] = hdf.driver
        metadata['external_direct_links'] = len(hdf.external)
        
        root = hdf['/']
        
        metadata['file_info'] = {
            'filename': hdf.filename,
            'size_bytes': self._get_file_size(hdf.filename),
            'lib_version': h5py.__version__,
        }
        
        metadata['structure'] = self._extract_structure(hdf)
        metadata['root_attributes'] = self._extract_attributes(root)
        metadata['datasets'] = self._extract_datasets_summary(hdf)
        metadata['groups'] = self._extract_groups_summary(hdf)
        
        return metadata
    
    def _extract_structure(self, hdf) -> Dict[str, Any]:
        """Extract overall HDF5 structure info."""
        datasets_count = 0
        groups_count = 0
        soft_links = 0
        external_links = 0
        
        def count_items(name, obj):
            nonlocal datasets_count, groups_count, soft_links, external_links
            if isinstance(obj, h5py.Dataset):
                datasets_count += 1
            elif isinstance(obj, h5py.Group):
                groups_count += 1
        
        hdf.visititems(count_items)
        
        return {
            'total_datasets': datasets_count,
            'total_groups': groups_count,
            'total_items': datasets_count + groups_count,
        }
    
    def _extract_attributes(self, obj) -> Dict[str, Any]:
        """Extract attributes from an HDF5 object."""
        attrs = {}
        for key in obj.attrs.keys():
            value = obj.attrs[key]
            if isinstance(value, bytes):
                value = value.decode('utf-8', errors='replace')
            elif isinstance(value, (list, tuple)):
                value = [v.decode('utf-8', errors='replace') if isinstance(v, bytes) else v for v in value]
            attrs[key] = value
        return attrs
    
    def _extract_datasets_summary(self, hdf) -> Dict[str, Any]:
        """Extract summary of all datasets."""
        datasets = []
        max_datasets = 50
        
        def collect_dataset(name, obj):
            if len(datasets) >= max_datasets:
                return
            if isinstance(obj, h5py.Dataset):
                dataset_info = {
                    'path': name,
                    'shape': list(obj.shape) if obj.shape else None,
                    'dtype': str(obj.dtype),
                    'size_bytes': obj.nbytes if hasattr(obj, 'nbytes') else None,
                    'compression': obj.compression if obj.compression else None,
                    'chunks': list(obj.chunks) if obj.chunks else None,
                }
                if obj.attrs:
                    dataset_info['num_attributes'] = len(obj.attrs)
                datasets.append(dataset_info)
        
        hdf.visititems(collect_dataset)
        
        total_size = sum(d.get('size_bytes', 0) or 0 for d in datasets)
        
        return {
            'count': len(datasets),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024*1024), 2),
            'datasets': datasets,
        }
    
    def _extract_groups_summary(self, hdf) -> Dict[str, Any]:
        """Extract summary of groups."""
        groups = []
        max_groups = 30
        
        def collect_group(name, obj):
            if len(groups) >= max_groups:
                return
            if isinstance(obj, h5py.Group) and name != '/':
                group_info = {
                    'path': name,
                    'num_children': len(obj),
                    'num_attributes': len(obj.attrs),
                }
                groups.append(group_info)
        
        hdf.visititems(collect_group)
        
        return {
            'count': len(groups),
            'groups': groups,
        }
    
    def _get_file_size(self, filepath: str) -> Optional[int]:
        """Get file size in bytes."""
        try:
            from pathlib import Path
            return Path(filepath).stat().st_size
        except:
            return None
    
    def _parse_basic_hdf5(self, filepath: str) -> Dict[str, Any]:
        """Parse HDF5 without h5py - magic byte detection."""
        try:
            with open(filepath, 'rb') as f:
                signature = f.read(8)
                if signature[:4] == b'\x89HDF\r\n\x1a\n':
                    return {
                        "file_type": "HDF5",
                        "parsing_mode": "basic",
                        "signature_valid": True,
                        "format_detected": "HDF5",
                    }
                else:
                    return {"error": "Not a valid HDF5 file"}
        except Exception as e:
            return {"error": str(e)[:200], "parsing_mode": "failed"}
    
    def get_real_field_count(self, metadata: Dict[str, Any]) -> int:
        """Count real HDF5 metadata fields."""
        return self._count_real_fields(metadata)
    
    def can_parse(self, filepath: str) -> bool:
        """Check if file is HDF5."""
        ext = Path(filepath).suffix.lower()
        if ext not in ['.h5', '.hdf5', '.he5']:
            return False
        
        try:
            with open(filepath, 'rb') as f:
                signature = f.read(8)
                return signature[:4] == b'\x89HDF\r\n\x1a\n'
        except:
            return False


def parse_hdf5(filepath: str) -> Dict[str, Any]:
    """Parse HDF5 file and return metadata."""
    parser = Hdf5Parser()
    return parser.parse(filepath)


"""
NetCDF Parser
=============

Extracts metadata from NetCDF (Network Common Data Form) files.
Used for climate, atmospheric, and oceanographic data.

NetCDF Structure:
- Dimensions
- Variables
- Global attributes
- Coordinate variables
"""

from typing import Dict, Any, Optional
import struct


class NetcdfParser(ScientificParser):
    """NetCDF-specific metadata parser."""
    
    FORMAT_NAME = "NetCDF"
    SUPPORTED_EXTENSIONS = ['.nc', '.cdf']
    
    def parse(self, filepath: str) -> Dict[str, Any]:
        """Extract NetCDF metadata."""
        result = {}
        
        try:
            import netCDF4
            
            with netCDF4.Dataset(filepath, 'r') as nc:
                result = self._extract_netcdf_metadata(nc, filepath)
                
        except ImportError:
            result = self._parse_basic_netcdf(filepath)
        except Exception as e:
            logger.warning(f"NetCDF parsing failed: {e}")
            result = {"error": str(e)[:200]}
        
        return result
    
    def _extract_netcdf_metadata(self, nc, filepath: str) -> Dict[str, Any]:
        """Extract NetCDF metadata using netCDF4."""
        metadata = {}
        
        metadata['file_type'] = 'NetCDF'
        metadata['netcdf_version'] = nc.version
        metadata['format'] = nc.file_format
        
        metadata['dimensions'] = {
            dim: len(nc.dimensions[dim]) for dim in nc.dimensions.keys()
        }
        
        metadata['variables'] = self._extract_variables(nc)
        
        metadata['global_attributes'] = self._extract_global_attributes(nc)
        
        metadata['data_analysis'] = self._analyze_data(nc)
        
        metadata['file_info'] = {
            'filename': filepath,
            'size_bytes': self._get_file_size(filepath),
        }
        
        return metadata
    
    def _extract_variables(self, nc) -> Dict[str, Any]:
        """Extract variable information."""
        variables = {}
        
        for var_name in nc.variables.keys():
            var = nc.variables[var_name]
            var_info = {
                'dimensions': list(var.dimensions),
                'dtype': str(var.dtype),
                'shape': [len(nc.dimensions[d]) for d in var.dimensions],
                'chunking': var.chunking() if hasattr(var, 'chunking') else None,
                'compression': var.compression_type() if hasattr(var, 'compression_type') else None,
            }
            
            if hasattr(var, 'ncattrs'):
                attrs = {attr: str(getattr(var, attr)) for attr in var.ncattrs()}
                var_info['attributes'] = attrs
            
            variables[var_name] = var_info
        
        return variables
    
    def _extract_global_attributes(self, nc) -> Dict[str, Any]:
        """Extract global attributes."""
        attrs = {}
        if hasattr(nc, 'ncattrs'):
            for attr in nc.ncattrs():
                value = getattr(nc, attr)
                if isinstance(value, bytes):
                    value = value.decode('utf-8', errors='replace')
                attrs[attr] = value
        return attrs
    
    def _analyze_data(self, nc) -> Dict[str, Any]:
        """Analyze NetCDF data for scientific context."""
        analysis = {}
        
        var_names = list(nc.variables.keys())
        
        time_vars = [v for v in var_names if 'time' in v.lower()]
        spatial_vars = [v for v in var_names if any(c in v.lower() for c in ['lat', 'lon', 'x', 'y', 'z'])]
        
        analysis['has_temporal_data'] = len(time_vars) > 0
        analysis['has_spatial_data'] = len(spatial_vars) > 0
        analysis['time_variables'] = time_vars[:5]
        analysis['spatial_variables'] = spatial_vars[:5]
        
        analysis['variable_count'] = len(var_names)
        analysis['dimension_count'] = len(nc.dimensions)
        
        global_attrs = getattr(nc, 'ncattrs', lambda: [])()
        title = str(getattr(nc, 'title', '')).lower()
        institution = str(getattr(nc, 'institution', '')).lower()
        
        if 'climate' in title or 'climate' in institution:
            analysis['data_domain'] = 'climate'
        elif 'ocean' in title or 'ocean' in institution:
            analysis['data_domain'] = 'oceanographic'
        elif 'atmospher' in title or 'atmospher' in institution:
            analysis['data_domain'] = 'atmospheric'
        elif 'weather' in title or 'weather' in institution:
            analysis['data_domain'] = 'weather'
        else:
            analysis['data_domain'] = 'scientific'
        
        analysis['data_complexity'] = 'high' if len(var_names) > 50 else 'medium' if len(var_names) > 10 else 'low'
        
        return analysis
    
    def _get_file_size(self, filepath: str) -> Optional[int]:
        """Get file size in bytes."""
        try:
            from pathlib import Path
            return Path(filepath).stat().st_size
        except:
            return None
    
    def _parse_basic_netcdf(self, filepath: str) -> Dict[str, Any]:
        """Parse NetCDF without netCDF4 - magic byte detection."""
        try:
            with open(filepath, 'rb') as f:
                header = f.read(4)
                if header == b'CDF\x01' or header == b'CDF\x02':
                    return {
                        "file_type": "NetCDF",
                        "parsing_mode": "basic",
                        "version": header,
                        "format_detected": "NetCDF",
                    }
                else:
                    return {"error": "Not a valid NetCDF file"}
        except Exception as e:
            return {"error": str(e)[:200], "parsing_mode": "failed"}
    
    def get_real_field_count(self, metadata: Dict[str, Any]) -> int:
        """Count real NetCDF metadata fields."""
        return self._count_real_fields(metadata)
    
    def can_parse(self, filepath: str) -> bool:
        """Check if file is NetCDF."""
        ext = Path(filepath).suffix.lower()
        if ext not in ['.nc', '.cdf']:
            return False
        
        try:
            with open(filepath, 'rb') as f:
                header = f.read(4)
                return header in [b'CDF\x01', b'CDF\x02']
        except:
            return False


def parse_netcdf(filepath: str) -> Dict[str, Any]:
    """Parse NetCDF file and return metadata."""
    parser = NetcdfParser()
    return parser.parse(filepath)
