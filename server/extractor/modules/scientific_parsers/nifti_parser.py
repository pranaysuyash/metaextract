"""
NIfTI Parser - Neuroimaging Data Format
========================================

Implements NIfTI-1 and NIfTI-2 format support for neuroimaging data.
NIfTI is widely used in MRI, fMRI, CT, and other medical imaging research.

Key Features:
- NIfTI-1 (.nii) and NIfTI-2 (.nii) support
- NIfTI with gzip compression (.nii.gz)
- Analyze 7.5 format compatibility
- Full header metadata extraction
- Voxel data properties
- Coordinate system and affine transformations
- DICOM-to-NIfTI conversion metadata

NIfTI Header Structure:
- 348 bytes (NIfTI-1) or 540 bytes (NIfTI-2) header
- 16-byte magic number identifying format
- Image dimensions (5D support)
- Data types and scaling
- Spatial and temporal parameters
- Coordinate transformations

Reference: https://nifti.nimh.nih.gov/
"""

import struct
import gzip
import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import datetime

logger = logging.getLogger(__name__)

NIFTI_HEADER_SIZE_V1 = 348
NIFTI_HEADER_SIZE_V2 = 540
NIFTI_MAGIC_V1 = b'ni1\x00'
NIFTI_MAGIC_V2 = b'ni2\x00'
NIFTI_MAGIC_GZ = b'\x1f\x8b'

NIFTI_DATATYPES = {
    0: 'unknown',
    1: 'binary',
    2: 'uint8',
    4: 'int16',
    8: 'int32',
    16: 'float32',
    32: 'complex64',
    64: 'float64',
    128: 'rgb24',
    256: 'int8',
    512: 'uint16',
    768: 'uint32',
    1024: 'int64',
    1280: 'uint64',
    1536: 'complex128',
    1792: 'complex128',
    2048: 'float128',
    2304: 'rgba32'
}

NIFTI_INTENT_CODES = {
    0: 'none',
    2: 'correl',
    3: 't test',
    4: 'f test',
    5: 'z score',
    6: 'chi2',
    7: 'beta',
    8: 'binomial',
    9: 'gamma',
    10: 'poisson',
    11: 'normal',
    12: 'noncentral f',
    13: 'noncentral chi2',
    14: 'noncentral t',
    15: 'noncentral beta',
    16: 'noncentral gamma',
    17: 'logistic',
    18: 'laplace',
    19: 'uniform',
    20: 'noncentral t2',
    21: 'asymmetrical gamma',
    22: 'h',
    23: 'h shape',
    24: 'half normal',
    25: 'half Cauchy',
    26: 'half t',
    27: 'half logistic',
    28: 'half normal',
    1001: 'estimate',
    1002: 'label',
    1003: 'measurement',
    1004: 'neuronorm',
    1005: 'spm t',
    1006: 'spm f',
    1007: 'spm z',
    1008: 'dset'
}

NIFTI_SLICE_CODES = {
    0: 'unknown',
    1: 'seq+',
    2: 'seq-',
    3: 'alt+',
    4: 'alt-',
    5: 'alt2+',
    6: 'alt2-'
}

NIFTI_XFORM_CODES = {
    0: 'unknown',
    1: 'scanner',
    2: 'aligned',
    3: 'talairach',
    4: 'mni152',
    5: 'template',
    6: 'mni152_nlin'
}

NIFTI_UNIT_CODES = {
    0: 'unknown',
    1: 'meter',
    2: 'mm',
    3: 'micron',
    4: 'sec',
    5: 'msec',
    6: 'usec',
    7: 'hz',
    8: 'ppm',
    9: 'radians/sec',
    10: 'ppm',
    11: 'radians',
    12: 'msec-ohm',
    13: 'unitless'
}


class NiftiParser:
    """Parser for NIfTI neuroimaging format."""
    
    FORMAT_NAME: str = "NIfTI"
    SUPPORTED_EXTENSIONS: List[str] = ['.nii', '.nii.gz']
    
    def __init__(self):
        self._header_version = None
    
    def can_parse(self, filepath: str) -> bool:
        """Check if file is a valid NIfTI file."""
        filepath_lower = filepath.lower()
        if not (filepath_lower.endswith('.nii') or filepath_lower.endswith('.nii.gz')):
            return False
        
        try:
            with self._open_file(filepath) as f:
                if filepath_lower.endswith('.nii.gz'):
                    f.seek(344)
                    magic_nifti = f.read(4)
                    if magic_nifti == NIFTI_MAGIC_V1:
                        self._header_version = 1
                        return True
                    elif magic_nifti == NIFTI_MAGIC_V2:
                        self._header_version = 2
                        return True
                    return False
                elif filepath_lower.endswith('.nii'):
                    f.seek(344)
                    magic_nifti = f.read(4)
                    if magic_nifti == NIFTI_MAGIC_V1:
                        self._header_version = 1
                        return True
                    elif magic_nifti == NIFTI_MAGIC_V2:
                        self._header_version = 2
                        return True
                    
                    f.seek(0)
                    magic_nifti1 = f.read(4)
                    if magic_nifti1 == NIFTI_MAGIC_V1 or magic_nifti1 == NIFTI_MAGIC_V2:
                        return True
                    return False
                else:
                    magic = f.read(4)
                    return magic in [NIFTI_MAGIC_V1, NIFTI_MAGIC_V2]
        except Exception:
            return False
    
    def _open_file(self, filepath: str):
        """Open file, handling gzip compression."""
        if filepath.endswith('.gz'):
            return gzip.open(filepath, 'rb')
        return open(filepath, 'rb')
    
    def parse(self, filepath: str) -> Dict[str, Any]:
        """Parse NIfTI file and extract all available metadata."""
        metadata = {}
        bookkeeping = {
            'source': 'nifti_parser',
            'format_version': None,
            'extraction_method': 'native',
            'warnings': [],
            'errors': []
        }
        
        try:
            with self._open_file(filepath) as f:
                # Read magic number position
                magic = f.read(4)
                
                if magic == NIFTI_MAGIC_V1:
                    bookkeeping['format_version'] = 'NIfTI-1'
                    self._header_version = 1
                    header_data = f.read(NIFTI_HEADER_SIZE_V1 - 4)
                    header = self._parse_header_v1(header_data)
                elif magic == NIFTI_MAGIC_V2:
                    bookkeeping['format_version'] = 'NIfTI-2'
                    self._header_version = 2
                    header_data = f.read(NIFTI_HEADER_SIZE_V2 - 4)
                    header = self._parse_header_v2(header_data)
                else:
                    if str(filepath).lower().endswith('.nii'):
                        f.seek(344)
                        magic_nifti = f.read(4)
                        if magic_nifti == NIFTI_MAGIC_V1:
                            bookkeeping['format_version'] = 'NIfTI-1'
                            self._header_version = 1
                            f.seek(0)
                            header_data = f.read(NIFTI_HEADER_SIZE_V1)
                            header = self._parse_header_v1(header_data[4:])
                        elif magic_nifti == NIFTI_MAGIC_V2:
                            bookkeeping['format_version'] = 'NIfTI-2'
                            self._header_version = 2
                            f.seek(0)
                            header_data = f.read(NIFTI_HEADER_SIZE_V2)
                            header = self._parse_header_v2(header_data[4:])
                        else:
                            raise ValueError(f"Invalid NIfTI magic number: {magic_nifti}")
                    elif str(filepath).lower().endswith('.nii.gz'):
                        f.seek(344)
                        magic_nifti = f.read(4)
                        if magic_nifti == NIFTI_MAGIC_V1:
                            bookkeeping['format_version'] = 'NIfTI-1'
                            self._header_version = 1
                            f.seek(0)
                            header_data = f.read(NIFTI_HEADER_SIZE_V1)
                            header = self._parse_header_v1(header_data[4:])
                        elif magic_nifti == NIFTI_MAGIC_V2:
                            bookkeeping['format_version'] = 'NIfTI-2'
                            self._header_version = 2
                            f.seek(0)
                            header_data = f.read(NIFTI_HEADER_SIZE_V2)
                            header = self._parse_header_v2(header_data[4:])
                        else:
                            raise ValueError(f"Invalid NIfTI magic number: {magic_nifti}")
                    else:
                        raise ValueError(f"Invalid NIfTI magic number: {magic}")
            
            metadata['file_information'] = self._extract_file_info(filepath, header)
            metadata['dimensions'] = self._extract_dimensions(header)
            metadata['data_type'] = self._extract_datatype(header)
            metadata['spatial_parameters'] = self._extract_spatial_parameters(header)
            metadata['temporal_parameters'] = self._extract_temporal_parameters(header)
            metadata['coordinate_system'] = self._extract_coordinate_system(header)
            metadata['transformations'] = self._extract_transformations(header)
            metadata['slice_information'] = self._extract_slice_info(header)
            metadata['intent'] = self._extract_intent(header)
            metadata['description'] = self._extract_description(header)
            metadata['auxiliary_file'] = self._extract_auxiliary_file(header)
            metadata['calibration'] = self._extract_calibration(header)
            metadata['voxel_data_summary'] = self._extract_voxel_summary(header)
            
            bookkeeping['fields_extracted'] = self._count_fields(metadata)
            
        except Exception as e:
            logger.error(f"NIfTI parsing error for {filepath}: {e}")
            bookkeeping['errors'].append(str(e)[:200])
            metadata['extraction_error'] = str(e)
        
        metadata['_bookkeeping'] = bookkeeping
        return metadata
    
    def _parse_header_v1(self, data: bytes) -> Dict[str, Any]:
        """Parse NIfTI-1 header (348 bytes)."""
        header = {}
        offset = 0
        
        def read_fmt(fmt: str, size: int = 1):
            nonlocal offset
            fmt_size = struct.calcsize(fmt) * size
            value = struct.unpack_from(fmt, data, offset)[0] if size == 1 else struct.unpack_from(fmt, data, offset)
            offset += fmt_size
            return value
        
        header['sizeof_hdr'] = read_fmt('<i')
        header['data_type'] = read_fmt('10s').rstrip(b'\x00').decode('utf-8', errors='replace')
        header['db_name'] = read_fmt('18s').rstrip(b'\x00').decode('utf-8', errors='replace')
        header['extents'] = read_fmt('<i')
        header['session_error'] = read_fmt('<h')
        header['regular'] = read_fmt('1s').decode('utf-8', errors='replace')
        header['dim_info'] = read_fmt('B')
        
        for i in range(1, 8):
            header[f'dim{i}'] = read_fmt('<h')
        
        header['intent_p1'] = read_fmt('<f')
        header['intent_p2'] = read_fmt('<f')
        header['intent_p3'] = read_fmt('<f')
        header['intent_code'] = read_fmt('<h')
        header['datatype'] = read_fmt('<h')
        header['bitpix'] = read_fmt('<h')
        header['slice_start'] = read_fmt('<h')
        
        for i in range(8):
            header[f'pixdim{i}'] = read_fmt('<f')
        
        header['vox_offset'] = read_fmt('<f')
        header['scl_slope'] = read_fmt('<f')
        header['scl_inter'] = read_fmt('<f')
        header['slice_end'] = read_fmt('<h')
        header['slice_code'] = read_fmt('B')
        header['xyzt_units'] = read_fmt('B')
        header['cal_max'] = read_fmt('<f')
        header['cal_min'] = read_fmt('<f')
        header['slice_duration'] = read_fmt('<f')
        header['toffset'] = read_fmt('<f')
        header['glmax'] = read_fmt('<i')
        header['glmin'] = read_fmt('<i')
        
        header['descrip'] = read_fmt('80s').rstrip(b'\x00').decode('utf-8', errors='replace')
        header['aux_file'] = read_fmt('24s').rstrip(b'\x00').decode('utf-8', errors='replace')
        
        header['qform_code'] = read_fmt('<h')
        header['sform_code'] = read_fmt('<h')
        header['quatern_b'] = read_fmt('<f')
        header['quatern_c'] = read_fmt('<f')
        header['quatern_d'] = read_fmt('<f')
        header['qoffset_x'] = read_fmt('<f')
        header['qoffset_y'] = read_fmt('<f')
        header['qoffset_z'] = read_fmt('<f')
        
        for i in range(4):
            header[f'srow_x_{chr(120+i)}'] = read_fmt('<f')
        for i in range(4):
            header[f'srow_y_{chr(120+i)}'] = read_fmt('<f')
        for i in range(4):
            header[f'srow_z_{chr(120+i)}'] = read_fmt('<f')
        
        header['slice_name'] = None
        header['xyz_units'] = 0
        header['modified'] = 0
        header['intent_name'] = ''
        
        return header
    
    def _parse_header_v2(self, data: bytes) -> Dict[str, Any]:
        """Parse NIfTI-2 header (540 bytes)."""
        header = {}
        offset = 0
        
        def read_fmt(fmt: str, size: int = 1):
            nonlocal offset
            fmt_size = struct.calcsize(fmt) * size
            value = struct.unpack_from(fmt, data, offset)[0] if size == 1 else struct.unpack_from(fmt, data, offset)
            offset += fmt_size
            return value
        
        header['sizeof_hdr'] = read_fmt('<i')
        header['magic'] = read_fmt('4s')
        
        header['data_type'] = read_fmt('10s').rstrip(b'\x00').decode('utf-8', errors='replace')
        header['db_name'] = read_fmt('18s').rstrip(b'\x00').decode('utf-8', errors='replace')
        header['extents'] = read_fmt('<q')
        header['session_error'] = read_fmt('<h')
        header['regular'] = read_fmt('1s').decode('utf-8', errors='replace')
        header['dim_info'] = read_fmt('B')
        
        for i in range(1, 8):
            header[f'dim{i}'] = read_fmt('<q')
        
        header['intent_p1'] = read_fmt('<d')
        header['intent_p2'] = read_fmt('<d')
        header['intent_p3'] = read_fmt('<d')
        header['intent_code'] = read_fmt('<h')
        header['datatype'] = read_fmt('<h')
        header['bitpix'] = read_fmt('<h')
        header['slice_start'] = read_fmt('<q')
        
        for i in range(8):
            header[f'pixdim{i}'] = read_fmt('<d')
        
        header['vox_offset'] = read_fmt('<q')
        header['scl_slope'] = read_fmt('<d')
        header['scl_inter'] = read_fmt('<d')
        header['slice_end'] = read_fmt('<q')
        header['slice_code'] = read_fmt('B')
        header['xyzt_units'] = read_fmt('B')
        header['cal_max'] = read_fmt('<d')
        header['cal_min'] = read_fmt('<d')
        header['slice_duration'] = read_fmt('<d')
        header['toffset'] = read_fmt('<d')
        header['glmax'] = read_fmt('<i')
        header['glmin'] = read_fmt('<i')
        
        header['descrip'] = read_fmt('80s').rstrip(b'\x00').decode('utf-8', errors='replace')
        header['aux_file'] = read_fmt('24s').rstrip(b'\x00').decode('utf-8', errors='replace')
        
        header['qform_code'] = read_fmt('<h')
        header['sform_code'] = read_fmt('<h')
        header['quatern_b'] = read_fmt('<d')
        header['quatern_c'] = read_fmt('<d')
        header['quatern_d'] = read_fmt('<d')
        header['qoffset_x'] = read_fmt('<d')
        header['qoffset_y'] = read_fmt('<d')
        header['qoffset_z'] = read_fmt('<d')
        
        for i in range(4):
            header[f'srow_x_{chr(120+i)}'] = read_fmt('<d')
        for i in range(4):
            header[f'srow_y_{chr(120+i)}'] = read_fmt('<d')
        for i in range(4):
            header[f'srow_z_{chr(120+i)}'] = read_fmt('<d')
        
        header['slice_name'] = None
        header['xyz_units'] = 0
        header['modified'] = 0
        header['intent_name'] = ''
        header['measurement_duration'] = 0
        header['list_string'] = ''
        header['list_length'] = 0
        
        return header
    
    def _extract_file_info(self, filepath: str, header: Dict[str, Any]) -> Dict[str, Any]:
        """Extract file-level information."""
        path = Path(filepath)
        return {
            'filename': path.name,
            'filepath': str(path.absolute()),
            'file_extension': path.suffix.lower(),
            'file_size_bytes': path.stat().st_size if path.exists() else 0,
            'is_compressed': str(path).endswith('.gz')
        }
    
    def _extract_dimensions(self, header: Dict[str, Any]) -> Dict[str, Any]:
        """Extract image dimensions."""
        dims = header.get('dim', [0] * 8)
        return {
            'ndim': dims[0],
            'nx': dims[1],
            'ny': dims[2] if len(dims) > 2 else 0,
            'nz': dims[3] if len(dims) > 3 else 0,
            'nt': dims[4] if len(dims) > 4 else 0,
            'nu': dims[5] if len(dims) > 5 else 0,
            'nv': dims[6] if len(dims) > 6 else 0,
            'nw': dims[7] if len(dims) > 7 else 0,
            'total_voxels': dims[1] * dims[2] * dims[3] * dims[4] if len(dims) > 4 else dims[1] * dims[2] * dims[3]
        }
    
    def _extract_datatype(self, header: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data type information."""
        datatype_code = header.get('datatype', 0)
        bitpix = header.get('bitpix', 0)
        return {
            'data_type_code': datatype_code,
            'data_type_name': NIFTI_DATATYPES.get(datatype_code, 'unknown'),
            'bits_per_voxel': bitpix,
            'bytes_per_voxel': bitpix // 8 if bitpix > 0 else 0
        }
    
    def _extract_spatial_parameters(self, header: Dict[str, Any]) -> Dict[str, Any]:
        """Extract spatial parameters."""
        pixdims = [header.get(f'pixdim{i}', 0.0) for i in range(8)]
        dims = header.get('dim', [0] * 8)
        
        spatial_units_code = header.get('xyzt_units', 0) & 0x07
        spatial_units = NIFTI_UNIT_CODES.get(spatial_units_code, 'unknown')
        
        return {
            'voxel_size_x': pixdims[1],
            'voxel_size_y': pixdims[2],
            'voxel_size_z': pixdims[3],
            'voxel_size_t': pixdims[4],
            'voxel_units': spatial_units,
            'spatial_unit_label': spatial_units,
            'fov_x': pixdims[1] * dims[1] if dims[1] > 0 else 0,
            'fov_y': pixdims[2] * dims[2] if dims[2] > 0 else 0,
            'fov_z': pixdims[3] * dims[3] if dims[3] > 0 else 0
        }
    
    def _extract_temporal_parameters(self, header: Dict[str, Any]) -> Dict[str, Any]:
        """Extract temporal parameters."""
        pixdims = [header.get(f'pixdim{i}', 0.0) for i in range(8)]
        dims = header.get('dim', [0] * 8)
        
        temporal_units_code = (header.get('xyzt_units', 0) >> 3) & 0x07
        temporal_units = NIFTI_UNIT_CODES.get(temporal_units_code, 'unknown')
        
        return {
            'num_time_points': dims[4],
            'tr_ms': pixdims[4] * 1000 if pixdims[4] > 0 else 0,
            'tr_seconds': pixdims[4],
            'temporal_units': temporal_units,
            'temporal_unit_label': temporal_units,
            'total_duration_seconds': pixdims[4] * dims[4] if dims[4] > 0 else 0,
            'num_volumes': dims[4]
        }
    
    def _extract_coordinate_system(self, header: Dict[str, Any]) -> Dict[str, Any]:
        """Extract coordinate system information."""
        qform_code = header.get('qform_code', 0)
        sform_code = header.get('sform_code', 0)
        
        return {
            'qform_code': qform_code,
            'qform_name': NIFTI_XFORM_CODES.get(qform_code, 'unknown'),
            'sform_code': sform_code,
            'sform_name': NIFTI_XFORM_CODES.get(sform_code, 'unknown'),
            'has_qform': qform_code > 0,
            'has_sform': sform_code > 0
        }
    
    def _extract_transformations(self, header: Dict[str, Any]) -> Dict[str, Any]:
        """Extract affine transformation parameters."""
        quatern_b = header.get('quatern_b', 0.0)
        quatern_c = header.get('quatern_c', 0.0)
        quatern_d = header.get('quatern_d', 0.0)
        qoffset_x = header.get('qoffset_x', 0.0)
        qoffset_y = header.get('qoffset_y', 0.0)
        qoffset_z = header.get('qoffset_z', 0.0)
        
        srow_x = [header.get(f'srow_x_{chr(120+i)}', 0.0) for i in range(4)]
        srow_y = [header.get(f'srow_y_{chr(120+i)}', 0.0) for i in range(4)]
        srow_z = [header.get(f'srow_z_{chr(120+i)}', 0.0) for i in range(4)]
        
        return {
            'quaternion_b': quatern_b,
            'quaternion_c': quatern_c,
            'quaternion_d': quatern_d,
            'quaternion_offsets': {
                'x': qoffset_x,
                'y': qoffset_y,
                'z': qoffset_z
            },
            'sform_matrix': {
                'row_x': srow_x,
                'row_y': srow_y,
                'row_z': srow_z
            }
        }
    
    def _extract_slice_info(self, header: Dict[str, Any]) -> Dict[str, Any]:
        """Extract slice acquisition information."""
        slice_code = header.get('slice_code', 0)
        slice_start = header.get('slice_start', 0)
        slice_end = header.get('slice_end', 0)
        slice_duration = header.get('slice_duration', 0.0)
        
        num_slices = header.get('dim', [0] * 8)[3]
        
        return {
            'slice_ordering_code': slice_code,
            'slice_ordering_name': NIFTI_SLICE_CODES.get(slice_code, 'unknown'),
            'slice_start': slice_start,
            'slice_end': slice_end,
            'slice_duration_ms': slice_duration * 1000,
            'number_of_slices': num_slices,
            'total_slice_time': slice_duration * num_slices if num_slices > 0 else 0
        }
    
    def _extract_intent(self, header: Dict[str, Any]) -> Dict[str, Any]:
        """Extract intent information for statistical analysis."""
        intent_code = header.get('intent_code', 0)
        intent_p1 = header.get('intent_p1', 0.0)
        intent_p2 = header.get('intent_p2', 0.0)
        intent_p3 = header.get('intent_p3', 0.0)
        intent_name = header.get('intent_name', '') or header.get('descrip', '')
        
        return {
            'intent_code': intent_code,
            'intent_name': NIFTI_INTENT_CODES.get(intent_code, 'unknown'),
            'intent_parameters': {
                'p1': intent_p1,
                'p2': intent_p2,
                'p3': intent_p3
            },
            'description': intent_name
        }
    
    def _extract_description(self, header: Dict[str, Any]) -> Dict[str, Any]:
        """Extract description and other text fields."""
        descrip = header.get('descrip', '')
        aux_file = header.get('aux_file', '')
        
        return {
            'description': descrip if descrip else None,
            'auxiliary_file': aux_file if aux_file else None
        }
    
    def _extract_auxiliary_file(self, header: Dict[str, Any]) -> Dict[str, Any]:
        """Extract auxiliary file information."""
        aux_file = header.get('aux_file', '')
        return {
            'has_auxiliary_file': bool(aux_file),
            'auxiliary_filename': aux_file if aux_file else None
        }
    
    def _extract_calibration(self, header: Dict[str, Any]) -> Dict[str, Any]:
        """Extract intensity calibration information."""
        cal_max = header.get('cal_max', 0.0)
        cal_min = header.get('cal_min', 0.0)
        scl_slope = header.get('scl_slope', 1.0)
        scl_inter = header.get('scl_inter', 0.0)
        glmax = header.get('glmax', 0)
        glmin = header.get('glmin', 0)
        
        return {
            'cal_max': cal_max if cal_max > 0 else None,
            'cal_min': cal_min if cal_min > 0 else None,
            'display_range': {
                'max': cal_max if cal_max > 0 else None,
                'min': cal_min if cal_min > 0 else None
            },
            'scaling_slope': scl_slope if scl_slope != 1.0 else None,
            'scaling_intercept': scl_inter if scl_inter != 0.0 else None,
            'global_max': glmax if glmax > 0 else None,
            'global_min': glmin if glmin > 0 else None
        }
    
    def _extract_voxel_summary(self, header: Dict[str, Any]) -> Dict[str, Any]:
        """Extract voxel data summary information."""
        dims = header.get('dim', [0] * 8)
        datatype_code = header.get('datatype', 0)
        bitpix = header.get('bitpix', 0)
        vox_offset = header.get('vox_offset', 0.0)
        
        total_voxels = dims[1] * dims[2] * dims[3] * dims[4] if dims[4] > 1 else dims[1] * dims[2] * dims[3]
        bytes_per_voxel = bitpix // 8 if bitpix > 0 else 0
        data_size_bytes = total_voxels * bytes_per_voxel
        
        return {
            'data_type': NIFTI_DATATYPES.get(datatype_code, 'unknown'),
            'dimensions': f"{dims[1]}x{dims[2]}x{dims[3]}x{dims[4]}" if dims[4] > 1 else f"{dims[1]}x{dims[2]}x{dims[3]}",
            'total_voxels': total_voxels,
            'bytes_per_voxel': bytes_per_voxel,
            'data_size_bytes': data_size_bytes,
            'data_offset': vox_offset
        }
    
    def _count_fields(self, metadata: Dict[str, Any]) -> int:
        """Count only non-null leaf values."""
        count = 0
        for key, value in metadata.items():
            if key.startswith('_'):
                continue
            if isinstance(value, dict):
                for k, v in value.items():
                    if v not in [None, '', 0, 'unknown', 'N/A']:
                        if not (isinstance(v, (str, bytes)) and not v):
                            count += 1
            elif value not in [None, '', 0, 'unknown', 'N/A']:
                if not (isinstance(value, (str, bytes)) and not value):
                    count += 1
        return count
    
    def get_real_field_count(self, metadata: Dict[str, Any]) -> int:
        """Get count of real extracted fields."""
        return metadata.get('_bookkeeping', {}).get('fields_extracted', 0)


def parse_nifti_metadata(filepath: str) -> Dict[str, Any]:
    """
    Parse NIfTI file and return comprehensive metadata.
    
    Args:
        filepath: Path to NIfTI file (.nii or .nii.gz)
        
    Returns:
        Dictionary containing metadata and field count
    """
    parser = NiftiParser()
    
    if not parser.can_parse(filepath):
        return {
            "success": False,
            "format": "NIfTI",
            "supported": False,
            "error": "Not a valid NIfTI file",
            "fields_extracted": 0,
            "metadata": {}
        }
    
    try:
        metadata = parser.parse(filepath)
        real_fields = parser.get_real_field_count(metadata)
        
        bookkeeping = metadata.pop('_bookkeeping', {})
        
        return {
            "success": True,
            "format": "NIfTI",
            "supported": True,
            "format_version": bookkeeping.get('format_version'),
            "fields_extracted": real_fields,
            "metadata": metadata,
            "extraction_method": "native",
            "warnings": bookkeeping.get('warnings', [])
        }
    except Exception as e:
        logger.error(f"NIfTI parsing failed for {filepath}: {e}")
        return {
            "success": False,
            "format": "NIfTI",
            "supported": True,
            "error": str(e)[:200],
            "fields_extracted": 0,
            "metadata": {}
        }


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = parse_nifti_metadata(sys.argv[1])
        import json
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Usage: python nifti_parser.py <file.nii>")
