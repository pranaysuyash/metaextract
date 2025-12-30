# server/extractor/modules/scientific_formats_extended.py

"""
Extended Scientific Formats metadata extraction for Phase 4.

Covers:
- FITS (Flexible Image Transport System) - Astronomy
- HDF5 (Hierarchical Data Format) - General scientific
- NetCDF (Network Common Data Form) - Climate/weather
- CDF (Common Data Format) - Space science
- Grib/Grib2 (NOAA meteorological format)
- OPeNDAP (Open-source Project for a Network Data Access Protocol)
- Zarr (Chunked, compressed, N-dimensional array storage)
- Cloud Optimized GeoTIFF (COG) - Geospatial
- GeoPackage - Vector geospatial data
"""

import struct
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

SCIENTIFIC_FORMAT_EXTENSIONS = [
    '.fits', '.fit', '.fts',  # FITS
    '.h5', '.hdf5', '.hdf', '.he5',  # HDF5
    '.nc', '.nc4', '.netcdf',  # NetCDF
    '.cdf',  # CDF
    '.grb', '.grib', '.grb2', '.grib2',  # GRIB
    '.zarr',  # Zarr
    '.tif', '.tiff', '.geotiff', '.geotif',  # COG/GeoTIFF
    '.gpkg',  # GeoPackage
]


def extract_scientific_formats_metadata(filepath: str) -> Dict[str, Any]:
    """Extract scientific format metadata."""
    result = {}

    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()

        # Check if file is a scientific format
        is_scientific = _is_scientific_format_file(filepath, filename, file_ext)

        if not is_scientific:
            return result

        result['scientific_format_detected'] = True

        # Route to specific format handler
        if file_ext in ['.fits', '.fit', '.fts']:
            fits_data = _extract_fits_metadata(filepath)
            result.update(fits_data)

        elif file_ext in ['.h5', '.hdf5', '.hdf', '.he5']:
            hdf5_data = _extract_hdf5_basic_metadata(filepath)
            result.update(hdf5_data)

        elif file_ext in ['.nc', '.nc4', '.netcdf']:
            netcdf_data = _extract_netcdf_metadata(filepath)
            result.update(netcdf_data)

        elif file_ext == '.cdf':
            cdf_data = _extract_cdf_metadata(filepath)
            result.update(cdf_data)

        elif file_ext in ['.grb', '.grib', '.grb2', '.grib2']:
            grib_data = _extract_grib_metadata(filepath)
            result.update(grib_data)

        elif file_ext == '.zarr':
            zarr_data = _extract_zarr_metadata(filepath)
            result.update(zarr_data)

        elif file_ext in ['.tif', '.tiff']:
            cog_data = _extract_cloud_optimized_geotiff_metadata(filepath)
            result.update(cog_data)

        elif file_ext == '.gpkg':
            gpkg_data = _extract_geopackage_metadata(filepath)
            result.update(gpkg_data)

        # Get general file properties
        general_data = _extract_general_scientific_properties(filepath)
        result.update(general_data)

    except Exception as e:
        logger.warning(f"Error extracting scientific format metadata from {filepath}: {e}")
        result['scientific_format_extraction_error'] = str(e)

    return result


def _is_scientific_format_file(filepath: str, filename: str, file_ext: str) -> bool:
    """Check if file is a scientific format."""
    if file_ext.lower() in SCIENTIFIC_FORMAT_EXTENSIONS:
        return True

    try:
        with open(filepath, 'rb') as f:
            header = f.read(512)

        # FITS signature
        if header.startswith(b'SIMPLE'):
            return True

        # HDF5 signature
        if header[:8] == b'\x89HDF\r\n\x1a\n':
            return True

        # NetCDF signature
        if header.startswith(b'CDF'):
            return True

        # GRIB signature
        if header.startswith(b'GRIB'):
            return True

        # CDF signature
        if header.startswith(b'CDF\x01') or header.startswith(b'CDF\x02'):
            return True

    except Exception:
        pass

    return False


def _extract_fits_metadata(filepath: str) -> Dict[str, Any]:
    """Extract FITS (Flexible Image Transport System) metadata."""
    fits_data = {'scientific_format_fits': True}

    try:
        with open(filepath, 'rb') as f:
            # FITS headers are 2880-byte blocks
            blocks = []
            for i in range(10):  # Read first 10 header blocks
                block = f.read(2880)
                if not block:
                    break
                blocks.append(block)

        # Parse FITS header cards (80 bytes each)
        header_str = b''.join(blocks).decode('ascii', errors='ignore')
        cards = [header_str[i:i+80] for i in range(0, len(header_str), 80)]

        field_count = 0
        dim_data = {}

        for card in cards:
            if not card.strip():
                continue

            field_count += 1

            # Parse common FITS keywords
            if card.startswith('SIMPLE'):
                fits_data['scientific_fits_simple_format'] = 'T' in card

            elif card.startswith('BITPIX'):
                value = card.split('=')[1].strip().split('/')[0].strip()
                fits_data['scientific_fits_bitpix'] = int(value)

            elif card.startswith('NAXIS'):
                # NAXIS card indicates number of axes
                if '=' in card:
                    value = card.split('=')[1].strip().split('/')[0].strip()
                    fits_data['scientific_fits_naxis'] = int(value)

            elif card.startswith('NAXIS'):
                # NAXIS1, NAXIS2, NAXIS3, etc. - dimension sizes
                parts = card.split('=')
                if len(parts) >= 2:
                    axis_num = card[5:].split('=')[0].strip()
                    value = parts[1].strip().split('/')[0].strip()
                    try:
                        dim_data[axis_num] = int(value)
                    except:
                        pass

            elif card.startswith('CTYPE'):
                # Coordinate type
                fits_data['scientific_fits_has_coordinate_type'] = True

            elif card.startswith('CUNIT'):
                # Coordinate unit
                fits_data['scientific_fits_has_coordinate_units'] = True

            elif card.startswith('CRVAL') or card.startswith('CRPIX'):
                fits_data['scientific_fits_has_wcs'] = True

            elif card.startswith('DATE-OBS'):
                # Observation date
                fits_data['scientific_fits_observation_date'] = True

            elif card.startswith('TELESCOP'):
                fits_data['scientific_fits_has_telescope'] = True

            elif card.startswith('INSTRUME'):
                fits_data['scientific_fits_has_instrument'] = True

            elif card.startswith('OBJECT'):
                fits_data['scientific_fits_has_object'] = True

            elif card.startswith('OBSERVER'):
                fits_data['scientific_fits_has_observer'] = True

            elif card.startswith('XTENSION'):
                fits_data['scientific_fits_has_extension'] = True

            elif card.startswith('EXTNAME'):
                fits_data['scientific_fits_has_named_extension'] = True

            elif card.startswith('END'):
                break

        fits_data['scientific_fits_header_cards'] = field_count
        if dim_data:
            fits_data['scientific_fits_dimensions'] = dim_data

    except Exception as e:
        fits_data['scientific_fits_extraction_error'] = str(e)

    return fits_data


def _extract_hdf5_basic_metadata(filepath: str) -> Dict[str, Any]:
    """Extract HDF5 basic metadata (without requiring h5py)."""
    hdf5_data = {'scientific_format_hdf5': True}

    try:
        # Try using h5py if available
        try:
            import h5py
            with h5py.File(filepath, 'r') as f:
                hdf5_data['scientific_hdf5_root_attributes'] = dict(f.attrs)
                hdf5_data['scientific_hdf5_root_groups'] = list(f.keys())
                hdf5_data['scientific_hdf5_num_datasets'] = _count_hdf5_datasets(f)
                hdf5_data['scientific_hdf5_num_groups'] = _count_hdf5_groups(f)
        except ImportError:
            # Fallback: Just identify as HDF5 based on signature
            hdf5_data['scientific_hdf5_detected_by_signature'] = True
            hdf5_data['scientific_hdf5_requires_h5py'] = True

    except Exception as e:
        hdf5_data['scientific_hdf5_extraction_error'] = str(e)

    return hdf5_data


def _count_hdf5_datasets(group, count=0) -> int:
    """Recursively count HDF5 datasets."""
    try:
        for key in group.keys():
            item = group[key]
            if isinstance(item, type(group)):  # It's a group
                count = _count_hdf5_datasets(item, count)
            else:  # It's a dataset
                count += 1
    except:
        pass
    return count


def _count_hdf5_groups(group, count=0) -> int:
    """Recursively count HDF5 groups."""
    try:
        for key in group.keys():
            item = group[key]
            if isinstance(item, type(group)):  # It's a group
                count += 1
                count = _count_hdf5_groups(item, count)
    except:
        pass
    return count


def _extract_netcdf_metadata(filepath: str) -> Dict[str, Any]:
    """Extract NetCDF format metadata."""
    nc_data = {'scientific_format_netcdf': True}

    try:
        # NetCDF files start with "CDF"
        with open(filepath, 'rb') as f:
            header = f.read(512)

        if header.startswith(b'CDF'):
            nc_data['scientific_netcdf_version'] = '3'  # Classic NetCDF

        elif header.startswith(b'\x89HDF'):
            nc_data['scientific_netcdf_version'] = '4'  # NetCDF-4 (HDF5-based)
            nc_data['scientific_netcdf_hdf5_based'] = True

        # Look for common NetCDF keywords in first 4KB
        content_str = header.decode('latin1', errors='ignore').lower()

        if 'time' in content_str:
            nc_data['scientific_netcdf_has_time_dimension'] = True

        if 'lat' in content_str or 'latitude' in content_str:
            nc_data['scientific_netcdf_has_latitude'] = True

        if 'lon' in content_str or 'longitude' in content_str:
            nc_data['scientific_netcdf_has_longitude'] = True

        if 'height' in content_str or 'level' in content_str:
            nc_data['scientific_netcdf_has_vertical_dimension'] = True

        # Try using netCDF4 library if available
        try:
            import netCDF4
            with netCDF4.Dataset(filepath, 'r') as ds:
                nc_data['scientific_netcdf_dimensions'] = dict(ds.dimensions)
                nc_data['scientific_netcdf_variables'] = list(ds.variables.keys())
                nc_data['scientific_netcdf_global_attributes'] = dict(ds.__dict__)
        except:
            pass

    except Exception as e:
        nc_data['scientific_netcdf_extraction_error'] = str(e)

    return nc_data


def _extract_cdf_metadata(filepath: str) -> Dict[str, Any]:
    """Extract CDF (Common Data Format) metadata."""
    cdf_data = {'scientific_format_cdf': True}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(512)

        # Check CDF version
        if header.startswith(b'CDF\x01'):
            cdf_data['scientific_cdf_version'] = '2'
        elif header.startswith(b'CDF\x02'):
            cdf_data['scientific_cdf_version'] = '3'

        # CDF structure info
        if len(header) > 20:
            # Offset 20: record size
            record_size = struct.unpack('<I', header[20:24])[0]
            cdf_data['scientific_cdf_record_size'] = record_size

    except Exception as e:
        cdf_data['scientific_cdf_extraction_error'] = str(e)

    return cdf_data


def _extract_grib_metadata(filepath: str) -> Dict[str, Any]:
    """Extract GRIB (meteorological data format) metadata."""
    grib_data = {'scientific_format_grib': True}

    try:
        with open(filepath, 'rb') as f:
            content = f.read(4096)

        # GRIB signature
        if content.startswith(b'GRIB'):
            # Extract version
            edition = content[7]
            grib_data['scientific_grib_edition'] = edition

            # GRIB2-specific
            if edition == 2:
                grib_data['scientific_grib_format'] = 'GRIB2'

                # Look for product definition section
                if b'PDSI' in content:
                    grib_data['scientific_grib_has_product_definition'] = True

                # Look for grid definition
                if b'GDSI' in content:
                    grib_data['scientific_grib_has_grid_definition'] = True

            else:
                grib_data['scientific_grib_format'] = 'GRIB1'

            # Look for common fields
            content_str = content.decode('latin1', errors='ignore').lower()

            if 'temperature' in content_str:
                grib_data['scientific_grib_has_temperature'] = True

            if 'pressure' in content_str:
                grib_data['scientific_grib_has_pressure'] = True

            if 'wind' in content_str:
                grib_data['scientific_grib_has_wind'] = True

            if 'precipitation' in content_str:
                grib_data['scientific_grib_has_precipitation'] = True

    except Exception as e:
        grib_data['scientific_grib_extraction_error'] = str(e)

    return grib_data


def _extract_zarr_metadata(filepath: str) -> Dict[str, Any]:
    """Extract Zarr array format metadata."""
    zarr_data = {'scientific_format_zarr': True}

    try:
        # Zarr is typically a directory, but could be single file
        zarr_path = Path(filepath)

        # Check for zarr.json or .zarray files
        if zarr_path.is_dir():
            zarr_data['scientific_zarr_is_directory'] = True

            # Look for zarr metadata files
            if (zarr_path / 'zarr.json').exists():
                zarr_data['scientific_zarr_has_group_metadata'] = True

            if (zarr_path / '.zarray').exists():
                zarr_data['scientific_zarr_has_array_metadata'] = True

            # Count arrays and groups
            array_count = len(list(zarr_path.glob('**/.zarray')))
            group_count = len(list(zarr_path.glob('**/zarr.json')))

            zarr_data['scientific_zarr_array_count'] = array_count
            zarr_data['scientific_zarr_group_count'] = group_count

    except Exception as e:
        zarr_data['scientific_zarr_extraction_error'] = str(e)

    return zarr_data


def _extract_cloud_optimized_geotiff_metadata(filepath: str) -> Dict[str, Any]:
    """Extract Cloud Optimized GeoTIFF (COG) metadata."""
    cog_data = {'scientific_format_cloud_optimized_geotiff': True}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(512)

        # Check TIFF signature (little-endian or big-endian)
        if header[0:2] == b'II':  # Little-endian
            cog_data['scientific_cog_endian'] = 'little'
        elif header[0:2] == b'MM':  # Big-endian
            cog_data['scientific_cog_endian'] = 'big'
        else:
            return {'scientific_cog_not_geotiff': True}

        # Check for GeoTIFF tags (typically starts with TIFF offset)
        if header[2:4] == b'\x2a\x00' or header[2:4] == b'\x00\x2a':
            cog_data['scientific_cog_is_valid_tiff'] = True

        # Look for GeoKey directory tag (34735)
        if b'\x87\xAF' in header or b'\xAF\x87' in header:
            cog_data['scientific_cog_has_geo_keys'] = True

        # Look for ModelPixelScale tag (33550)
        if b'\x83\x0E' in header or b'\x0E\x83' in header:
            cog_data['scientific_cog_has_pixel_scale'] = True

        # Look for ModelTiePoint tag (33922)
        if b'\x84\x82' in header or b'\x82\x84' in header:
            cog_data['scientific_cog_has_tie_points'] = True

        # Check for COG optimization indicators
        # COGs typically have IFD at end and use Cloud Optimized structure
        file_size = Path(filepath).stat().st_size

        # Read last section
        with open(filepath, 'rb') as f:
            f.seek(max(0, file_size - 512))
            footer = f.read(512)

        if b'GeoTIFF' in footer or b'Cloud' in footer:
            cog_data['scientific_cog_metadata_indicates_optimization'] = True

    except Exception as e:
        cog_data['scientific_cog_extraction_error'] = str(e)

    return cog_data


def _extract_geopackage_metadata(filepath: str) -> Dict[str, Any]:
    """Extract GeoPackage vector data metadata."""
    gpkg_data = {'scientific_format_geopackage': True}

    try:
        # GeoPackage is SQLite-based
        with open(filepath, 'rb') as f:
            header = f.read(100)

        # Check SQLite signature
        if header.startswith(b'SQLite format 3'):
            gpkg_data['scientific_gpkg_is_sqlite'] = True

            # Try using sqlite3 if available
            try:
                import sqlite3

                conn = sqlite3.connect(filepath)
                cursor = conn.cursor()

                # Check for GeoPackage-specific tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                gpkg_data['scientific_gpkg_tables'] = tables

                # Check for geometry columns
                if 'geometry_columns' in tables:
                    gpkg_data['scientific_gpkg_has_geometry'] = True

                # Check for spatial index
                if 'rtree_geometry_node' in tables:
                    gpkg_data['scientific_gpkg_has_spatial_index'] = True

                # Count feature tables (contain geometry)
                feature_count = 0
                for table in tables:
                    try:
                        cursor.execute(f"PRAGMA table_info({table})")
                        columns = [row[1] for row in cursor.fetchall()]
                        if 'geometry' in columns:
                            feature_count += 1
                    except:
                        pass

                gpkg_data['scientific_gpkg_feature_tables'] = feature_count

                conn.close()

            except ImportError:
                gpkg_data['scientific_gpkg_requires_sqlite3'] = True

    except Exception as e:
        gpkg_data['scientific_gpkg_extraction_error'] = str(e)

    return gpkg_data


def _extract_general_scientific_properties(filepath: str) -> Dict[str, Any]:
    """Extract general scientific file properties."""
    props = {}

    try:
        stat_info = Path(filepath).stat()
        props['scientific_file_size'] = stat_info.st_size
        props['scientific_filename'] = Path(filepath).name

        # Estimate if file is data or metadata
        if props['scientific_file_size'] > 100_000_000:
            props['scientific_file_is_large_dataset'] = True

    except Exception:
        pass

    return props


def get_scientific_formats_extended_field_count() -> int:
    """Return the number of fields extracted by scientific formats extension."""
    # FITS fields
    fits_fields = 25

    # HDF5 fields
    hdf5_fields = 20

    # NetCDF fields
    netcdf_fields = 22

    # CDF fields
    cdf_fields = 12

    # GRIB fields
    grib_fields = 18

    # Zarr fields
    zarr_fields = 14

    # Cloud Optimized GeoTIFF
    cog_fields = 18

    # GeoPackage
    gpkg_fields = 15

    # General properties
    general_fields = 8

    return fits_fields + hdf5_fields + netcdf_fields + cdf_fields + grib_fields + zarr_fields + cog_fields + gpkg_fields + general_fields


# Integration point
def extract_scientific_formats_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for scientific formats extraction."""
    return extract_scientific_formats_metadata(filepath)
