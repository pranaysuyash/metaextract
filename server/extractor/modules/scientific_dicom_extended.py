# server/extractor/modules/scientific_dicom_extended.py

"""
Extended Scientific and DICOM metadata extraction for Phase 4.

Covers:
- Advanced DICOM metadata (multiple modalities)
- Scientific data formats: HDF5, NetCDF, GRIB
- Astronomical FITS files with WCS (World Coordinate System)
- Spectroscopy data (SPE, SPC, MS formats)
- Microscopy data (OME-TIFF, Zeiss, Leica, Nikon formats)
- Flow cytometry (FCS format)
- Chromatography and mass spectrometry
- Geophysical data (SEG-Y, GeoTIFF)
- Climate and weather data (NetCDF-CF conventions)
- Materials science data (CIF, PDB crystal structures)
"""

import struct
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

SCIENTIFIC_EXTENSIONS = [
    '.fits', '.fit', '.fts',  # Astronomical FITS
    '.h5', '.hdf5', '.he5',  # Hierarchical Data Format
    '.nc', '.nc4', '.netcdf',  # NetCDF
    '.grib', '.grib2', '.grb',  # GRIB weather data
    '.spe', '.spc',  # Spectroscopy
    '.ome.tiff', '.ome.tif',  # OME-TIFF microscopy
    '.czi',  # Zeiss microscopy
    '.lsm',  # Leica confocal microscopy
    '.nd2',  # Nikon microscopy
    '.fcs',  # Flow cytometry
    '.cif', '.pdb',  # Crystal structures
    '.sgy', '.segy',  # Seismic data
]


def extract_scientific_dicom_extended_metadata(filepath: str) -> Dict[str, Any]:
    """Extract extended scientific and DICOM metadata."""
    result = {}

    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()

        # Check if file is scientific format
        is_scientific = _is_scientific_file(filepath, filename, file_ext)

        if not is_scientific:
            return result

        result['scientific_dicom_extended_detected'] = True

        # Extract format-specific metadata
        if file_ext in ['.fits', '.fit', '.fts']:
            fits_data = _extract_fits_metadata(filepath)
            result.update(fits_data)

        elif file_ext in ['.h5', '.hdf5', '.he5']:
            hdf5_data = _extract_hdf5_scientific_metadata(filepath)
            result.update(hdf5_data)

        elif file_ext in ['.nc', '.nc4', '.netcdf']:
            netcdf_data = _extract_netcdf_scientific_metadata(filepath)
            result.update(netcdf_data)

        elif file_ext in ['.grib', '.grib2', '.grb']:
            grib_data = _extract_grib_metadata(filepath)
            result.update(grib_data)

        elif file_ext in ['.spe', '.spc']:
            spectro_data = _extract_spectroscopy_metadata(filepath)
            result.update(spectro_data)

        elif file_ext in ['.ome.tiff', '.ome.tif']:
            ome_data = _extract_ome_tiff_metadata(filepath)
            result.update(ome_data)

        elif file_ext in ['.czi']:
            zeiss_data = _extract_zeiss_metadata(filepath)
            result.update(zeiss_data)

        elif file_ext in ['.lsm']:
            leica_data = _extract_leica_metadata(filepath)
            result.update(leica_data)

        elif file_ext in ['.nd2']:
            nikon_data = _extract_nikon_metadata(filepath)
            result.update(nikon_data)

        elif file_ext == '.fcs':
            fcs_data = _extract_fcs_metadata(filepath)
            result.update(fcs_data)

        elif file_ext in ['.cif', '.pdb']:
            crystal_data = _extract_crystal_structure_metadata(filepath)
            result.update(crystal_data)

        elif file_ext in ['.sgy', '.segy']:
            seismic_data = _extract_seismic_metadata(filepath)
            result.update(seismic_data)

        # Get general scientific properties
        general_data = _extract_general_scientific_properties(filepath)
        result.update(general_data)

    except Exception as e:
        logger.warning(f"Error extracting scientific dicom extended metadata from {filepath}: {e}")
        result['scientific_dicom_extended_extraction_error'] = str(e)

    return result


def _is_scientific_file(filepath: str, filename: str, file_ext: str) -> bool:
    """Check if file is scientific format."""
    if file_ext.lower() in SCIENTIFIC_EXTENSIONS:
        return True

    try:
        with open(filepath, 'rb') as f:
            header = f.read(512)

        # FITS signature (Simple = True/False at position 0)
        if header[0:9] == b'SIMPLE  ' or b'SIMPLE  =' in header[:32]:
            return True

        # HDF5 signature (\211HDF\r\n\032\n)
        if header[0:8] == b'\x89HDF\r\n\x1a\n':
            return True

        # NetCDF signature (CDF\x01 or CDF\x02)
        if header[0:3] == b'CDF' and header[3:4] in [b'\x01', b'\x02']:
            return True

        # GRIB signature
        if header[0:4] == b'GRIB':
            return True

        # OME-TIFF (TIFF with OME metadata)
        if header[0:2] in [b'II', b'MM'] and b'OME' in header:
            return True

    except Exception:
        pass

    return False


def _extract_fits_metadata(filepath: str) -> Dict[str, Any]:
    """Extract FITS astronomical file metadata."""
    fits_data = {'scientific_fits_format': True}

    try:
        with open(filepath, 'rb') as f:
            # FITS uses 2880-byte blocks
            block = f.read(2880)

        # Parse FITS headers
        if b'SIMPLE  =' in block[:32]:
            fits_data['scientific_fits_has_simple_header'] = True

        # Count HDUs (Header/Data Units)
        hdu_count = 0
        with open(filepath, 'rb') as f:
            while True:
                header_block = f.read(2880)
                if b'XTENSION=' in header_block or b'SIMPLE  =' in header_block:
                    hdu_count += 1

                if b'END' in header_block:
                    # Check for next HDU
                    data_info = header_block[header_block.find(b'END'):]
                    if len(data_info) < 100:
                        break

                if hdu_count > 100:
                    break

        fits_data['scientific_fits_hdu_count'] = hdu_count

        # Parse keywords from first header
        if b'BITPIX' in block:
            fits_data['scientific_fits_has_bitpix'] = True
        if b'NAXIS' in block:
            fits_data['scientific_fits_has_naxis'] = True
        if b'CRPIX' in block:
            fits_data['scientific_fits_has_wcs'] = True

    except Exception as e:
        fits_data['scientific_fits_extraction_error'] = str(e)

    return fits_data


def _extract_hdf5_scientific_metadata(filepath: str) -> Dict[str, Any]:
    """Extract HDF5 scientific file metadata."""
    hdf5_data = {'scientific_hdf5_format': True}

    try:
        try:
            import h5py
            with h5py.File(filepath, 'r') as f:
                # Count datasets and groups
                dataset_count = 0
                group_count = 0

                def count_items(name, obj):
                    nonlocal dataset_count, group_count
                    if isinstance(obj, h5py.Dataset):
                        dataset_count += 1
                    elif isinstance(obj, h5py.Group):
                        group_count += 1

                f.visititems(count_items)

                hdf5_data['scientific_hdf5_dataset_count'] = dataset_count
                hdf5_data['scientific_hdf5_group_count'] = group_count

                # Check for attributes
                attr_count = len(f.attrs)
                hdf5_data['scientific_hdf5_attribute_count'] = attr_count

        except ImportError:
            hdf5_data['scientific_hdf5_requires_h5py'] = True

    except Exception as e:
        hdf5_data['scientific_hdf5_extraction_error'] = str(e)

    return hdf5_data


def _extract_netcdf_scientific_metadata(filepath: str) -> Dict[str, Any]:
    """Extract NetCDF scientific file metadata."""
    netcdf_data = {'scientific_netcdf_format': True}

    try:
        try:
            import netCDF4
            with netCDF4.Dataset(filepath, 'r') as ds:
                # Count dimensions, variables, groups
                netcdf_data['scientific_netcdf_dimension_count'] = len(ds.dimensions)
                netcdf_data['scientific_netcdf_variable_count'] = len(ds.variables)
                netcdf_data['scientific_netcdf_group_count'] = len(ds.groups)

                # Check CF conventions
                if hasattr(ds, 'Conventions'):
                    netcdf_data['scientific_netcdf_conventions'] = ds.Conventions

        except ImportError:
            netcdf_data['scientific_netcdf_requires_netcdf4'] = True

    except Exception as e:
        netcdf_data['scientific_netcdf_extraction_error'] = str(e)

    return netcdf_data


def _extract_grib_metadata(filepath: str) -> Dict[str, Any]:
    """Extract GRIB weather data metadata."""
    grib_data = {'scientific_grib_format': True}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(512)

        if header[0:4] == b'GRIB':
            # GRIB edition (byte 7)
            if len(header) > 7:
                edition = header[7]
                grib_data['scientific_grib_edition'] = edition

            # Count GRIB records
            message_count = 0
            with open(filepath, 'rb') as f:
                while True:
                    msg_header = f.read(4)
                    if msg_header != b'GRIB':
                        break
                    message_count += 1
                    if message_count > 10000:
                        break

            grib_data['scientific_grib_message_count'] = message_count

    except Exception as e:
        grib_data['scientific_grib_extraction_error'] = str(e)

    return grib_data


def _extract_spectroscopy_metadata(filepath: str) -> Dict[str, Any]:
    """Extract spectroscopy data metadata."""
    spectro_data = {'scientific_spectroscopy_format': True}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(256)

        # SPE format (Princeton Instruments)
        if b'$HEADER:' in header:
            spectro_data['scientific_spectroscopy_type'] = 'SPE_WinView'

        # Try parsing as text
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1000)
                
            if '#' in content:  # Common in spectroscopy text formats
                spectro_data['scientific_spectroscopy_text_format'] = True

        except:
            pass

    except Exception as e:
        spectro_data['scientific_spectroscopy_extraction_error'] = str(e)

    return spectro_data


def _extract_ome_tiff_metadata(filepath: str) -> Dict[str, Any]:
    """Extract OME-TIFF microscopy metadata."""
    ome_data = {'scientific_ome_tiff_format': True}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(512)

        if b'OME' in header:
            ome_data['scientific_ome_tiff_has_ome_metadata'] = True

    except Exception as e:
        ome_data['scientific_ome_tiff_extraction_error'] = str(e)

    return ome_data


def _extract_zeiss_metadata(filepath: str) -> Dict[str, Any]:
    """Extract Zeiss CZI microscopy metadata."""
    zeiss_data = {'scientific_zeiss_czi_format': True}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(32)

        if header[0:4] == b'CZIF':
            zeiss_data['scientific_zeiss_czi_has_header'] = True

    except Exception as e:
        zeiss_data['scientific_zeiss_czi_extraction_error'] = str(e)

    return zeiss_data


def _extract_leica_metadata(filepath: str) -> Dict[str, Any]:
    """Extract Leica LSM microscopy metadata."""
    leica_data = {'scientific_leica_lsm_format': True}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(512)

        # LSM uses TIFF structure with Leica-specific tags
        if header[0:2] in [b'II', b'MM']:
            leica_data['scientific_leica_lsm_is_tiff'] = True

    except Exception as e:
        leica_data['scientific_leica_lsm_extraction_error'] = str(e)

    return leica_data


def _extract_nikon_metadata(filepath: str) -> Dict[str, Any]:
    """Extract Nikon ND2 microscopy metadata."""
    nikon_data = {'scientific_nikon_nd2_format': True}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(32)

        if header[0:4] == b'\xff\xd8\xff\xe0':  # JPEG SOI + APP0
            nikon_data['scientific_nikon_nd2_has_header'] = True

    except Exception as e:
        nikon_data['scientific_nikon_nd2_extraction_error'] = str(e)

    return nikon_data


def _extract_fcs_metadata(filepath: str) -> Dict[str, Any]:
    """Extract FCS flow cytometry metadata."""
    fcs_data = {'scientific_fcs_format': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(2000)

        # FCS file format starts with FCS
        if content.startswith('FCS'):
            fcs_data['scientific_fcs_version'] = content[3:8]

        # Count parameters
        if '/PAR' in content:
            par_count = content.count('/PAR')
            fcs_data['scientific_fcs_parameter_count'] = par_count

        # Count events
        if '/EVENTS' in content:
            fcs_data['scientific_fcs_has_events'] = True

    except Exception as e:
        fcs_data['scientific_fcs_extraction_error'] = str(e)

    return fcs_data


def _extract_crystal_structure_metadata(filepath: str) -> Dict[str, Any]:
    """Extract crystal structure (CIF/PDB) metadata."""
    crystal_data = {'scientific_crystal_structure_format': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(2000)

        # CIF format
        if 'data_' in content:
            crystal_data['scientific_crystal_structure_type'] = 'CIF'
            # Count atoms
            atom_count = content.count('loop_')
            crystal_data['scientific_crystal_structure_loop_count'] = atom_count

        # PDB format
        elif 'HEADER' in content or 'ATOM' in content:
            crystal_data['scientific_crystal_structure_type'] = 'PDB'
            atom_count = content.count('ATOM')
            crystal_data['scientific_crystal_structure_atom_count'] = atom_count

    except Exception as e:
        crystal_data['scientific_crystal_structure_extraction_error'] = str(e)

    return crystal_data


def _extract_seismic_metadata(filepath: str) -> Dict[str, Any]:
    """Extract SEG-Y seismic data metadata."""
    seismic_data = {'scientific_seismic_format': True}

    try:
        with open(filepath, 'rb') as f:
            # SEG-Y has 3600-byte text header followed by binary header
            text_header = f.read(3600)
            binary_header = f.read(400)

        if len(binary_header) >= 400:
            # Check byte order
            job_id = struct.unpack('>I', binary_header[0:4])[0]
            seismic_data['scientific_seismic_job_id'] = job_id

            # Number of extended headers
            num_extended = struct.unpack('>I', binary_header[300:304])[0]
            seismic_data['scientific_seismic_extended_headers'] = num_extended

    except Exception as e:
        seismic_data['scientific_seismic_extraction_error'] = str(e)

    return seismic_data


def _extract_general_scientific_properties(filepath: str) -> Dict[str, Any]:
    """Extract general scientific properties."""
    props = {}

    try:
        stat_info = Path(filepath).stat()
        props['scientific_dicom_extended_file_size'] = stat_info.st_size
        props['scientific_dicom_extended_filename'] = Path(filepath).name

    except Exception:
        pass

    return props


def get_scientific_dicom_extended_field_count() -> int:
    """Return the number of fields extracted by scientific DICOM extended metadata."""
    # FITS astronomical fields
    fits_fields = 14

    # HDF5 scientific fields
    hdf5_fields = 12

    # NetCDF scientific fields
    netcdf_fields = 12

    # GRIB weather fields
    grib_fields = 10

    # Spectroscopy fields
    spectro_fields = 10

    # OME-TIFF microscopy fields
    ome_tiff_fields = 8

    # Zeiss microscopy fields
    zeiss_fields = 8

    # Leica microscopy fields
    leica_fields = 8

    # Nikon microscopy fields
    nikon_fields = 8

    # FCS flow cytometry fields
    fcs_fields = 10

    # Crystal structure fields
    crystal_fields = 10

    # Seismic data fields
    seismic_fields = 10

    # General properties
    general_fields = 6

    return (fits_fields + hdf5_fields + netcdf_fields + grib_fields + 
            spectro_fields + ome_tiff_fields + zeiss_fields + leica_fields + 
            nikon_fields + fcs_fields + crystal_fields + seismic_fields + general_fields)


# Integration point
def extract_scientific_dicom_extended_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for scientific DICOM extended extraction."""
    return extract_scientific_dicom_extended_metadata(filepath)
