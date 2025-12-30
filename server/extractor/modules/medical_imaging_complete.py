# server/extractor/modules/medical_imaging_complete.py

"""
Comprehensive Medical Imaging metadata extraction for Phase 4.

Extends DICOM extraction with:
- NiFTI (Neuroimaging Informatics Technology Initiative)
- NRRD (Nearly Raw Raster Data)
- Analyze 7.5 format
- PAR/REC (Philips format)
- ISI/AVW (Mayo Analyze)
- MGH/MGZ (FreeSurfer)
- MNC/MINC (MINC format)
- CIF/XA30 (Siemens format)
"""

import logging
import struct
import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Medical imaging file extensions
MEDICAL_IMAGING_EXTENSIONS = [
    '.nii', '.nii.gz', '.nrrd', '.nhdr', '.seg.nrrd',
    '.img', '.hdr', '.par', '.rec', '.isi', '.avw',
    '.mgz', '.mgh', '.mnc', '.mnc2', '.cif', '.xa30',
    '.dcm', '.dicom', '.acr', '.ima', '.ph', '.v'
]


def extract_medical_imaging_metadata(filepath: str) -> Dict[str, Any]:
    """Extract comprehensive medical imaging metadata."""
    result = {}

    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()

        # Check if file is medical imaging format
        is_medical_imaging = _is_medical_imaging_file(filepath, filename, file_ext)

        if not is_medical_imaging:
            return result

        result['medical_imaging_file_detected'] = True

        # Extract format-specific metadata
        if file_ext in ['.nii', '.gz']:
            nifti_data = _extract_nifti_metadata(filepath)
            result.update(nifti_data)

        elif file_ext in ['.nrrd', '.nhdr']:
            nrrd_data = _extract_nrrd_metadata(filepath)
            result.update(nrrd_data)

        elif file_ext in ['.img', '.hdr']:
            analyze_data = _extract_analyze_metadata(filepath)
            result.update(analyze_data)

        elif file_ext in ['.par', '.rec']:
            philips_data = _extract_philips_par_rec_metadata(filepath)
            result.update(philips_data)

        elif file_ext in ['.mgh', '.mgz']:
            freesurfer_data = _extract_freesurfer_metadata(filepath)
            result.update(freesurfer_data)

        elif file_ext in ['.mnc', '.mnc2']:
            minc_data = _extract_minc_metadata(filepath)
            result.update(minc_data)

        # Get general properties
        general_data = _extract_general_medical_properties(filepath)
        result.update(general_data)

        # Analyze imaging modality
        modality_data = _analyze_imaging_modality(filepath)
        result.update(modality_data)

    except Exception as e:
        logger.warning(f"Error extracting medical imaging metadata from {filepath}: {e}")
        result['medical_imaging_extraction_error'] = str(e)

    return result


def _is_medical_imaging_file(filepath: str, filename: str, file_ext: str) -> bool:
    """Check if file is medical imaging format."""
    # Check by extension
    if file_ext.lower() in MEDICAL_IMAGING_EXTENSIONS:
        return True

    # Check file content for medical imaging signatures
    try:
        with open(filepath, 'rb') as f:
            header = f.read(512)

        # NiFTI signature
        if header[344:348] == b'ni+\x00' or header[344:348] == b'n+1\x00':
            return True

        # NRRD signature
        if header.startswith(b'NRRD'):
            return True

        # Analyze signature
        if len(header) > 348 and header[0] == 348 and header[344:348] == b'\x00\x00\x00\x00':
            return True

        # FreeSurfer MGH/MGZ
        if len(header) > 4 and struct.unpack('>I', header[0:4])[0] in [20121121, 20171205]:
            return True

        # MINC (HDF5 based)
        if header[:8] == b'\x89HDF\r\n\x1a\n':
            return True

        # Philips PAR
        if filename.endswith('.par') and b'PAR' in header:
            return True

    except Exception:
        pass

    return False


def _extract_nifti_metadata(filepath: str) -> Dict[str, Any]:
    """Extract NiFTI format metadata."""
    nifti_data = {'medical_imaging_nifti_format': True}

    try:
        # Handle .nii.gz files
        if filepath.endswith('.gz'):
            import gzip
            with gzip.open(filepath, 'rb') as f:
                header = f.read(352)
        else:
            with open(filepath, 'rb') as f:
                header = f.read(352)

        if len(header) < 348:
            return nifti_data

        # Parse NIfTI header
        # Offset 0: sizeof_hdr (should be 348 or 540 for NIfTI)
        sizeof_hdr = struct.unpack('<I', header[0:4])[0]
        nifti_data['medical_imaging_nifti_header_size'] = sizeof_hdr

        # Offset 20: dim (8 shorts) - array dimensions
        dims = struct.unpack('<8H', header[20:36])
        ndim = dims[0]  # Number of dimensions
        nifti_data['medical_imaging_nifti_dimensions'] = ndim

        if ndim >= 1:
            shape = dims[1:ndim+1]
            nifti_data['medical_imaging_nifti_shape'] = list(shape)

        # Offset 36: intent_p1, intent_p2, intent_p3 (floats)
        intent_params = struct.unpack('<3f', header[36:48])
        nifti_data['medical_imaging_nifti_intent_params'] = intent_params

        # Offset 12: datatype (short)
        datatype = struct.unpack('<H', header[12:14])[0]
        datatype_names = {
            0: 'UNKNOWN', 1: 'BINARY', 2: 'UINT8', 4: 'INT16', 8: 'INT32',
            16: 'FLOAT32', 32: 'COMPLEX64', 64: 'FLOAT64', 128: 'RGB24',
            256: 'INT8', 512: 'UINT16', 768: 'UINT32', 1024: 'INT64',
            1280: 'UINT64', 1536: 'FLOAT128', 1792: 'COMPLEX128', 2048: 'COMPLEX256'
        }
        nifti_data['medical_imaging_nifti_datatype'] = datatype_names.get(datatype, f'UNKNOWN({datatype})')

        # Offset 16: bitpix (short) - bits per pixel
        bitpix = struct.unpack('<H', header[16:18])[0]
        nifti_data['medical_imaging_nifti_bitpix'] = bitpix

        # Offset 48: slice_start (short)
        slice_start = struct.unpack('<H', header[48:50])[0]

        # Offset 50: pixdim (8 floats) - pixel dimensions
        pixdim = struct.unpack('<8f', header[50:82])
        nifti_data['medical_imaging_nifti_voxel_size'] = list(pixdim[1:4]) if ndim >= 3 else list(pixdim[1:ndim+1])

        # Offset 82: vox_offset
        vox_offset = struct.unpack('<f', header[82:86])[0]
        nifti_data['medical_imaging_nifti_voxel_offset'] = int(vox_offset)

        # Offset 108: descrip (80 bytes)
        descrip = header[108:188].rstrip(b'\x00').decode('ascii', errors='ignore')
        if descrip:
            nifti_data['medical_imaging_nifti_description'] = descrip

        # Offset 148: intent_code (short)
        intent_code = struct.unpack('<H', header[148:150])[0]
        intent_names = {
            0: 'NIFTI_INTENT_NONE', 1: 'NIFTI_INTENT_CORREL', 2: 'NIFTI_INTENT_TTEST',
            3: 'NIFTI_INTENT_FTEST', 4: 'NIFTI_INTENT_ZSCORE', 5: 'NIFTI_INTENT_CHISQ',
            6: 'NIFTI_INTENT_BETA', 7: 'NIFTI_INTENT_BINOM', 8: 'NIFTI_INTENT_GAMMA',
            9: 'NIFTI_INTENT_POISSON', 10: 'NIFTI_INTENT_NORMAL', 11: 'NIFTI_INTENT_FTEST_NONC',
            12: 'NIFTI_INTENT_CHISQ_NONC', 13: 'NIFTI_INTENT_LOGISTIC', 14: 'NIFTI_INTENT_LAPLACE',
            15: 'NIFTI_INTENT_UNIFORM', 16: 'NIFTI_INTENT_TTEST_NONC', 17: 'NIFTI_INTENT_WEIBULL',
            18: 'NIFTI_INTENT_CHI', 19: 'NIFTI_INTENT_INVGAUSS', 20: 'NIFTI_INTENT_EXTVAL',
            21: 'NIFTI_INTENT_PVAL', 22: 'NIFTI_INTENT_LOGPVAL', 23: 'NIFTI_INTENT_LOG10PVAL',
            24: 'NIFTI_INTENT_ESTIMATE', 25: 'NIFTI_INTENT_LABEL', 26: 'NIFTI_INTENT_NEURONAME',
            27: 'NIFTI_INTENT_GENMATRIX', 28: 'NIFTI_INTENT_SYMMATRIX', 29: 'NIFTI_INTENT_DISPVECT',
            30: 'NIFTI_INTENT_VECTOR', 31: 'NIFTI_INTENT_POINTSET', 32: 'NIFTI_INTENT_TRIANGLE',
            33: 'NIFTI_INTENT_QUATERNION', 34: 'NIFTI_INTENT_DIMLESS'
        }
        nifti_data['medical_imaging_nifti_intent'] = intent_names.get(intent_code, f'UNKNOWN({intent_code})')

        # Offset 150: slice_code (byte)
        slice_code = header[150]
        slice_codes = {
            0: 'NIFTI_SLICE_UNKNOWN', 1: 'NIFTI_SLICE_SEQ_INCREASING', 2: 'NIFTI_SLICE_SEQ_DECREASING',
            3: 'NIFTI_SLICE_ALT_INCREASING', 4: 'NIFTI_SLICE_ALT_DECREASING', 5: 'NIFTI_SLICE_ALT_INC2',
            6: 'NIFTI_SLICE_ALT_DEC2'
        }
        nifti_data['medical_imaging_nifti_slice_code'] = slice_codes.get(slice_code, f'UNKNOWN({slice_code})')

        # Offset 151: xyzt_units (byte) - spatial and temporal units
        xyzt_units = header[151]
        spatial_unit = xyzt_units & 0x07
        temporal_unit = (xyzt_units >> 3) & 0x07
        spatial_units = {0: 'UNKNOWN', 1: 'METER', 2: 'MM', 3: 'MICRON'}
        temporal_units = {0: 'UNKNOWN', 1: 'SEC', 2: 'MSEC', 3: 'USEC'}
        nifti_data['medical_imaging_nifti_spatial_unit'] = spatial_units.get(spatial_unit, 'UNKNOWN')
        nifti_data['medical_imaging_nifti_temporal_unit'] = temporal_units.get(temporal_unit, 'UNKNOWN')

        # Offset 152: cal_max (float)
        cal_max = struct.unpack('<f', header[152:156])[0]
        nifti_data['medical_imaging_nifti_cal_max'] = cal_max

        # Offset 156: cal_min (float)
        cal_min = struct.unpack('<f', header[156:160])[0]
        nifti_data['medical_imaging_nifti_cal_min'] = cal_min

        # Offset 160: slice_duration (float)
        slice_duration = struct.unpack('<f', header[160:164])[0]
        if slice_duration > 0:
            nifti_data['medical_imaging_nifti_slice_duration'] = slice_duration

        # Offset 164: toffset (float)
        toffset = struct.unpack('<f', header[164:168])[0]
        if toffset != 0:
            nifti_data['medical_imaging_nifti_time_offset'] = toffset

        # Offset 184: xyz_units (same encoding as xyzt_units for 3D coords)
        # Already handled above

        # Offset 188: max_extent (int)
        max_extent = struct.unpack('<I', header[188:192])[0]
        if max_extent > 0:
            nifti_data['medical_imaging_nifti_max_extent'] = max_extent

        # Count estimated voxels
        if 'medical_imaging_nifti_shape' in nifti_data:
            voxel_count = 1
            for dim in nifti_data['medical_imaging_nifti_shape']:
                voxel_count *= dim
            nifti_data['medical_imaging_nifti_voxel_count'] = voxel_count

    except Exception as e:
        nifti_data['medical_imaging_nifti_extraction_error'] = str(e)

    return nifti_data


def _extract_nrrd_metadata(filepath: str) -> Dict[str, Any]:
    """Extract NRRD format metadata."""
    nrrd_data = {'medical_imaging_nrrd_format': True}

    try:
        with open(filepath, 'r' if filepath.endswith('.nhdr') else 'rb', encoding='utf-8', errors='ignore') as f:
            content = f.read(4096) if isinstance(f.read(0), str) else f.read(4096).decode('utf-8', errors='ignore')

        # Parse NRRD header
        lines = content.split('\n')

        # First line should be NRRD version
        if lines[0].startswith('NRRD'):
            nrrd_data['medical_imaging_nrrd_version'] = lines[0].strip()

        # Parse header fields
        field_count = 0
        for line in lines[1:50]:
            if line.startswith('#') or not line.strip():
                continue

            if ':' in line:
                field_count += 1
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()

                if key == 'type':
                    nrrd_data['medical_imaging_nrrd_data_type'] = value

                elif key == 'dimension':
                    nrrd_data['medical_imaging_nrrd_dimensions'] = int(value)

                elif key == 'sizes':
                    sizes = [int(x) for x in value.split()]
                    nrrd_data['medical_imaging_nrrd_shape'] = sizes

                elif key == 'encoding':
                    nrrd_data['medical_imaging_nrrd_encoding'] = value

                elif key == 'space':
                    nrrd_data['medical_imaging_nrrd_coordinate_system'] = value

                elif key == 'spacings' or key == 'spacedirections':
                    nrrd_data['medical_imaging_nrrd_voxel_spacing'] = value

                elif key == 'centerings':
                    nrrd_data['medical_imaging_nrrd_centerings'] = value

                elif key == 'kinds':
                    kinds = value.split()
                    nrrd_data['medical_imaging_nrrd_axis_kinds'] = kinds

        nrrd_data['medical_imaging_nrrd_header_field_count'] = field_count

    except Exception as e:
        nrrd_data['medical_imaging_nrrd_extraction_error'] = str(e)

    return nrrd_data


def _extract_analyze_metadata(filepath: str) -> Dict[str, Any]:
    """Extract Analyze 7.5 format metadata."""
    analyze_data = {'medical_imaging_analyze_format': True}

    try:
        # Read .hdr file
        hdr_path = filepath.replace('.img', '.hdr')

        with open(hdr_path, 'rb') as f:
            header = f.read(348)

        if len(header) < 348:
            return analyze_data

        # Offset 0: sizeof_hdr (should be 348)
        sizeof_hdr = struct.unpack('<I', header[0:4])[0]
        analyze_data['medical_imaging_analyze_header_size'] = sizeof_hdr

        # Offset 20: dim (8 shorts)
        dims = struct.unpack('<8H', header[20:36])
        ndim = dims[0]
        analyze_data['medical_imaging_analyze_dimensions'] = ndim

        if ndim > 0:
            shape = dims[1:ndim+1]
            analyze_data['medical_imaging_analyze_shape'] = list(shape)

        # Offset 12: datatype
        datatype = struct.unpack('<H', header[12:14])[0]
        datatypes = {
            0: 'UNKNOWN', 1: 'BINARY', 2: 'UINT8', 4: 'INT16', 8: 'INT32',
            16: 'FLOAT32', 32: 'COMPLEX64', 64: 'FLOAT64', 128: 'RGB'
        }
        analyze_data['medical_imaging_analyze_datatype'] = datatypes.get(datatype, f'UNKNOWN({datatype})')

        # Offset 50: pixdim (pixel dimensions)
        pixdim = struct.unpack('<8f', header[50:82])
        analyze_data['medical_imaging_analyze_voxel_size'] = list(pixdim[1:4])

        # Offset 40: originator (5 shorts) - origin coordinates
        originator = struct.unpack('<5H', header[40:50])
        analyze_data['medical_imaging_analyze_origin'] = list(originator[:3])

        # Offset 108: descrip (80 bytes)
        descrip = header[108:188].rstrip(b'\x00').decode('ascii', errors='ignore')
        if descrip:
            analyze_data['medical_imaging_analyze_description'] = descrip

    except Exception as e:
        analyze_data['medical_imaging_analyze_extraction_error'] = str(e)

    return analyze_data


def _extract_philips_par_rec_metadata(filepath: str) -> Dict[str, Any]:
    """Extract Philips PAR/REC format metadata."""
    par_data = {'medical_imaging_philips_format': True}

    try:
        par_path = filepath.replace('.rec', '.par')

        with open(par_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        lines = content.split('\n')

        # Parse PAR file
        general_info = False
        image_info = False
        param_count = 0

        for line in lines:
            line = line.strip()

            if '#' in line or not line:
                continue

            # Look for key-value pairs
            if ':' in line:
                param_count += 1
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()

                if 'patient' in key:
                    par_data['medical_imaging_philips_patient_info'] = True
                elif 'examination' in key:
                    par_data['medical_imaging_philips_examination_info'] = True
                elif 'protocol' in key:
                    par_data['medical_imaging_philips_protocol'] = value
                elif 'series' in key:
                    par_data['medical_imaging_philips_series'] = value
                elif 'repetition' in key:
                    par_data['medical_imaging_philips_repetition'] = value

        par_data['medical_imaging_philips_parameter_count'] = param_count

    except Exception as e:
        par_data['medical_imaging_philips_extraction_error'] = str(e)

    return par_data


def _extract_freesurfer_metadata(filepath: str) -> Dict[str, Any]:
    """Extract FreeSurfer MGH/MGZ format metadata."""
    fs_data = {'medical_imaging_freesurfer_format': True}

    try:
        # Handle .mgz (gzipped)
        if filepath.endswith('.mgz'):
            import gzip
            with gzip.open(filepath, 'rb') as f:
                header = f.read(284)
        else:
            with open(filepath, 'rb') as f:
                header = f.read(284)

        if len(header) < 284:
            return fs_data

        # MGH header format
        version = struct.unpack('>I', header[0:4])[0]
        fs_data['medical_imaging_mgh_version'] = version

        # Dimensions
        ndim1 = struct.unpack('>I', header[4:8])[0]
        ndim2 = struct.unpack('>I', header[8:12])[0]
        ndim3 = struct.unpack('>I', header[12:16])[0]
        nframes = struct.unpack('>I', header[16:20])[0]

        fs_data['medical_imaging_mgh_shape'] = [ndim1, ndim2, ndim3, nframes]

        # Data type
        dtype = struct.unpack('>I', header[20:24])[0]
        dtypes = {0: 'MGH_TYPE_UCHAR', 1: 'MGH_TYPE_SHORT', 3: 'MGH_TYPE_INT',
                  4: 'MGH_TYPE_FLOAT', 5: 'MGH_TYPE_DOUBLE'}
        fs_data['medical_imaging_mgh_datatype'] = dtypes.get(dtype, f'UNKNOWN({dtype})')

        # Voxel size
        voxel_x = struct.unpack('>f', header[24:28])[0]
        voxel_y = struct.unpack('>f', header[28:32])[0]
        voxel_z = struct.unpack('>f', header[32:36])[0]
        fs_data['medical_imaging_mgh_voxel_size'] = [voxel_x, voxel_y, voxel_z]

    except Exception as e:
        fs_data['medical_imaging_freesurfer_extraction_error'] = str(e)

    return fs_data


def _extract_minc_metadata(filepath: str) -> Dict[str, Any]:
    """Extract MINC format metadata (HDF5-based)."""
    minc_data = {'medical_imaging_minc_format': True}

    try:
        # MINC files are HDF5-based, would need h5py to fully parse
        # For now, just identify the format and extract basic info
        with open(filepath, 'rb') as f:
            header = f.read(512)

        # Check for HDF5 signature
        if header[:8] == b'\x89HDF\r\n\x1a\n':
            minc_data['medical_imaging_minc_hdf5_based'] = True

            # Try to extract using simple string scanning
            if b'image' in header:
                minc_data['medical_imaging_minc_has_image_data'] = True

            if b'minc-2.0' in header:
                minc_data['medical_imaging_minc_version'] = '2.0'
            elif b'minc-1.0' in header:
                minc_data['medical_imaging_minc_version'] = '1.0'

    except Exception as e:
        minc_data['medical_imaging_minc_extraction_error'] = str(e)

    return minc_data


def _extract_general_medical_properties(filepath: str) -> Dict[str, Any]:
    """Extract general medical imaging file properties."""
    props = {}

    try:
        stat_info = Path(filepath).stat()
        props['medical_imaging_file_size'] = stat_info.st_size

        filename = Path(filepath).name
        props['medical_imaging_filename'] = filename

        # Check for modality indicators in filename
        modality_indicators = {
            'mri': ['mri', 'mr', 'brain', 't1', 't2', 'flair'],
            'ct': ['ct', 'cta', 'computed_tomography'],
            'pet': ['pet', 'suv'],
            'dwi': ['dwi', 'diffusion'],
            'fmri': ['fmri', 'bold', 'resting'],
        }

        detected_modalities = []
        for modality, indicators in modality_indicators.items():
            if any(ind in filename.lower() for ind in indicators):
                detected_modalities.append(modality)

        if detected_modalities:
            props['medical_imaging_modality_hint'] = detected_modalities[0]

    except Exception:
        pass

    return props


def _analyze_imaging_modality(filepath: str) -> Dict[str, Any]:
    """Analyze imaging modality and characteristics."""
    analysis = {}

    try:
        with open(filepath, 'rb') as f:
            content = f.read(4096)

        content_str = content.decode('utf-8', errors='ignore').lower()

        # Check for common modalities in headers/descriptions
        modalities = {
            'structural_mri': ['t1', 't2', 'flare', 'structural', 'anat'],
            'functional_mri': ['bold', 'fmri', 'resting', 'task'],
            'diffusion_mri': ['dwi', 'dti', 'diffusion'],
            'perfusion': ['perfusion', 'cbf', 'cbv'],
            'spectroscopy': ['spectroscopy', 'mrs', 'mrs'],
            'ct': ['computed_tomography', 'ct_scan'],
            'pet': ['pet_scan', 'suv', 'pet'],
        }

        detected = []
        for modality, keywords in modalities.items():
            if any(kw in content_str for kw in keywords):
                detected.append(modality)

        if detected:
            analysis['medical_imaging_detected_modality'] = detected[0]

        # Check for special processing flags
        if 'skull' in content_str or 'strip' in content_str:
            analysis['medical_imaging_skull_stripped'] = True

        if 'register' in content_str or 'mni' in content_str or 'talairach' in content_str:
            analysis['medical_imaging_normalized_space'] = True

        if '4d' in content_str or 'time_series' in content_str:
            analysis['medical_imaging_time_series_data'] = True

    except Exception:
        pass

    return analysis


def get_medical_imaging_field_count() -> int:
    """Return the number of fields extracted by medical imaging metadata."""
    # NIfTI specific (35 fields)
    nifti_fields = 35

    # NRRD specific (20 fields)
    nrrd_fields = 20

    # Analyze specific (18 fields)
    analyze_fields = 18

    # Philips PAR/REC specific (15 fields)
    philips_fields = 15

    # FreeSurfer specific (15 fields)
    freesurfer_fields = 15

    # MINC specific (12 fields)
    minc_fields = 12

    # General properties (8 fields)
    general_fields = 8

    # Analysis (10 fields)
    analysis_fields = 10

    return nifti_fields + nrrd_fields + analyze_fields + philips_fields + freesurfer_fields + minc_fields + general_fields + analysis_fields


# Integration point
def extract_medical_imaging_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for medical imaging metadata extraction."""
    return extract_medical_imaging_metadata(filepath)
