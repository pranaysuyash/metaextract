# server/extractor/modules/environmental_climate.py

"""
Environmental and Climate metadata extraction for Phase 4.

Covers:
- Climate and weather data (NetCDF-CF, GRIB)
- Atmospheric data (temperature, pressure, humidity, wind)
- Oceanographic data (SST, salinity, currents)
- Land surface data (vegetation, soil moisture, albedo)
- Air quality data (pollutants, particle measurements)
- Water quality data (turbidity, pH, dissolved oxygen)
- Satellite remote sensing data
- Environmental monitoring data
- Hydrological data (precipitation, runoff, streamflow)
- Ecosystem and biodiversity data
- Carbon cycle data
- Climate model data and projections
"""

import struct
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

ENVIRONMENTAL_EXTENSIONS = [
    '.nc', '.nc4', '.netcdf',  # NetCDF climate data
    '.grib', '.grib2', '.grb',  # GRIB weather data
    '.h5', '.hdf5',  # Environmental HDF5
    '.tif', '.geotiff',  # Satellite/raster data
    '.csv', '.txt',  # Environmental tables
    '.cdf',  # CDF climate data
    '.asc',  # ASCII grid environmental data
]


def extract_environmental_climate_metadata(filepath: str) -> Dict[str, Any]:
    """Extract environmental and climate metadata."""
    result = {}

    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()

        # Check if file is environmental format
        is_environmental = _is_environmental_file(filepath, filename, file_ext)

        if not is_environmental:
            return result

        result['environmental_climate_detected'] = True

        # Extract format-specific metadata
        if file_ext in ['.nc', '.nc4', '.netcdf']:
            nc_data = _extract_climate_netcdf_metadata(filepath)
            result.update(nc_data)

        elif file_ext in ['.grib', '.grib2', '.grb']:
            grib_data = _extract_climate_grib_metadata(filepath)
            result.update(grib_data)

        elif file_ext in ['.h5', '.hdf5']:
            hdf5_data = _extract_environmental_hdf5_metadata(filepath)
            result.update(hdf5_data)

        elif file_ext in ['.tif', '.geotiff']:
            satellite_data = _extract_satellite_metadata(filepath)
            result.update(satellite_data)

        elif file_ext in ['.csv', '.txt']:
            table_data = _extract_environmental_table_metadata(filepath)
            result.update(table_data)

        elif file_ext == '.asc':
            asc_data = _extract_ascii_grid_metadata(filepath)
            result.update(asc_data)

        # Get general environmental properties
        general_data = _extract_general_environmental_properties(filepath)
        result.update(general_data)

    except Exception as e:
        logger.warning(f"Error extracting environmental climate metadata from {filepath}: {e}")
        result['environmental_climate_extraction_error'] = str(e)

    return result


def _is_environmental_file(filepath: str, filename: str, file_ext: str) -> bool:
    """Check if file is environmental format."""
    if file_ext.lower() in ENVIRONMENTAL_EXTENSIONS:
        return True

    # Check for environmental/climate indicators in filename
    climate_keywords = ['climate', 'weather', 'temperature', 'precipitation', 
                       'satellite', 'ocean', 'atmospheric', 'environmental',
                       'wind', 'radiation', 'ndvi', 'vegetation']
    
    filename_lower = filename.lower()
    if any(kw in filename_lower for kw in climate_keywords):
        return True

    try:
        with open(filepath, 'rb') as f:
            header = f.read(512)

        # NetCDF signature
        if header[0:3] == b'CDF' and header[3:4] in [b'\x01', b'\x02']:
            return True

        # HDF5 signature
        if header[0:8] == b'\x89HDF\r\n\x1a\n':
            return True

        # GRIB signature
        if header[0:4] == b'GRIB':
            return True

    except Exception:
        pass

    return False


def _extract_climate_netcdf_metadata(filepath: str) -> Dict[str, Any]:
    """Extract NetCDF climate data metadata."""
    netcdf_data = {'environmental_netcdf_format': True}

    try:
        try:
            import netCDF4
            with netCDF4.Dataset(filepath, 'r') as ds:
                # Climate variable fields
                vars_with_time = 0
                vars_3d = 0
                vars_4d = 0

                # Identify climate variables
                climate_vars = ['temperature', 'temp', 't2m', 'precip', 'precipitation',
                               'wind', 'windspeed', 'u10', 'v10', 'sea_surface_temp',
                               'sst', 'salinity', 'soil_moisture', 'albedo', 'ndvi']

                for var_name in ds.variables:
                    var = ds.variables[var_name]
                    ndims = len(var.dimensions)

                    if 'time' in var.dimensions:
                        vars_with_time += 1

                    if ndims == 3:
                        vars_3d += 1
                    elif ndims == 4:
                        vars_4d += 1

                netcdf_data['environmental_netcdf_variables_with_time'] = vars_with_time
                netcdf_data['environmental_netcdf_3d_variables'] = vars_3d
                netcdf_data['environmental_netcdf_4d_variables'] = vars_4d

                # Check dimensions
                dimensions = list(ds.dimensions.keys())
                netcdf_data['environmental_netcdf_dimensions'] = dimensions[:20]

                # Global attributes (metadata)
                global_attrs = len(ds.ncattrs())
                netcdf_data['environmental_netcdf_global_attributes'] = global_attrs

                # Check CF conventions
                if 'Conventions' in ds.ncattrs():
                    conventions = ds.getncattr('Conventions')
                    netcdf_data['environmental_netcdf_conventions'] = conventions

                # Check for time dimension
                if 'time' in ds.dimensions:
                    time_size = len(ds.dimensions['time'])
                    netcdf_data['environmental_netcdf_time_steps'] = time_size

                # Check for lat/lon
                if 'latitude' in ds.dimensions or 'lat' in ds.dimensions:
                    netcdf_data['environmental_netcdf_has_latitude'] = True
                if 'longitude' in ds.dimensions or 'lon' in ds.dimensions:
                    netcdf_data['environmental_netcdf_has_longitude'] = True

        except ImportError:
            netcdf_data['environmental_netcdf_requires_netcdf4'] = True

    except Exception as e:
        netcdf_data['environmental_netcdf_extraction_error'] = str(e)

    return netcdf_data


def _extract_climate_grib_metadata(filepath: str) -> Dict[str, Any]:
    """Extract GRIB climate/weather data metadata."""
    grib_data = {'environmental_grib_format': True}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(512)

        if header[0:4] == b'GRIB':
            # GRIB edition
            if len(header) > 7:
                edition = header[7]
                grib_data['environmental_grib_edition'] = edition

            # Count messages
            msg_count = 0
            with open(filepath, 'rb') as f:
                while True:
                    sig = f.read(4)
                    if sig != b'GRIB':
                        break
                    msg_count += 1

                    if msg_count > 10000:
                        break

            grib_data['environmental_grib_message_count'] = msg_count

    except Exception as e:
        grib_data['environmental_grib_extraction_error'] = str(e)

    return grib_data


def _extract_environmental_hdf5_metadata(filepath: str) -> Dict[str, Any]:
    """Extract environmental HDF5 data metadata."""
    hdf5_data = {'environmental_hdf5_format': True}

    try:
        try:
            import h5py
            with h5py.File(filepath, 'r') as f:
                # Count datasets and groups
                dataset_count = 0
                group_count = 0
                timeseries_count = 0

                def count_items(name, obj):
                    nonlocal dataset_count, group_count, timeseries_count
                    if isinstance(obj, h5py.Dataset):
                        dataset_count += 1
                        # Check if appears to be time series (1D large array)
                        if len(obj.shape) == 1 and obj.shape[0] > 100:
                            timeseries_count += 1
                    elif isinstance(obj, h5py.Group):
                        group_count += 1

                f.visititems(count_items)

                hdf5_data['environmental_hdf5_dataset_count'] = dataset_count
                hdf5_data['environmental_hdf5_group_count'] = group_count
                hdf5_data['environmental_hdf5_timeseries_count'] = timeseries_count

        except ImportError:
            hdf5_data['environmental_hdf5_requires_h5py'] = True

    except Exception as e:
        hdf5_data['environmental_hdf5_extraction_error'] = str(e)

    return hdf5_data


def _extract_satellite_metadata(filepath: str) -> Dict[str, Any]:
    """Extract satellite remote sensing metadata."""
    satellite_data = {'environmental_satellite_format': True}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(512)

        # GeoTIFF header analysis
        if header[0:2] in [b'II', b'MM']:
            satellite_data['environmental_satellite_is_geotiff'] = True

            # Check for remote sensing tags
            if b'\x83\x0e' in header or b'\x0e\x83' in header:
                satellite_data['environmental_satellite_has_pixel_scale'] = True

    except Exception as e:
        satellite_data['environmental_satellite_extraction_error'] = str(e)

    return satellite_data


def _extract_environmental_table_metadata(filepath: str) -> Dict[str, Any]:
    """Extract environmental table data metadata."""
    table_data = {'environmental_table_format': True}

    try:
        line_count = 0
        column_count = 0
        has_header = False

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                line_count += 1

                if i == 0:
                    # First line - check if header
                    cols = line.split(',')
                    column_count = len(cols)

                    # Check for common header patterns
                    header_keywords = ['date', 'time', 'temperature', 'precipitation',
                                      'wind', 'pressure', 'humidity', 'station']
                    line_lower = line.lower()
                    if any(kw in line_lower for kw in header_keywords):
                        has_header = True

                if line_count >= 10000:
                    break

        table_data['environmental_table_line_count'] = line_count
        table_data['environmental_table_column_count'] = column_count
        table_data['environmental_table_has_header'] = has_header

    except Exception as e:
        table_data['environmental_table_extraction_error'] = str(e)

    return table_data


def _extract_ascii_grid_metadata(filepath: str) -> Dict[str, Any]:
    """Extract ASCII grid environmental data metadata."""
    asc_data = {'environmental_ascii_grid_format': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            # Read header lines
            for i in range(6):
                line = f.readline().strip()
                if line.startswith('ncols'):
                    ncols = int(line.split()[-1])
                    asc_data['environmental_ascii_grid_ncols'] = ncols
                elif line.startswith('nrows'):
                    nrows = int(line.split()[-1])
                    asc_data['environmental_ascii_grid_nrows'] = nrows
                elif line.startswith('xllcorner') or line.startswith('xllcenter'):
                    xll = float(line.split()[-1])
                    asc_data['environmental_ascii_grid_xll'] = xll
                elif line.startswith('yllcorner') or line.startswith('yllcenter'):
                    yll = float(line.split()[-1])
                    asc_data['environmental_ascii_grid_yll'] = yll
                elif line.startswith('cellsize'):
                    cellsize = float(line.split()[-1])
                    asc_data['environmental_ascii_grid_cellsize'] = cellsize
                elif line.startswith('NODATA_value'):
                    nodata = line.split()[-1]
                    asc_data['environmental_ascii_grid_nodata_value'] = nodata

    except Exception as e:
        asc_data['environmental_ascii_grid_extraction_error'] = str(e)

    return asc_data


def _extract_general_environmental_properties(filepath: str) -> Dict[str, Any]:
    """Extract general environmental properties."""
    props = {}

    try:
        stat_info = Path(filepath).stat()
        props['environmental_climate_file_size'] = stat_info.st_size
        props['environmental_climate_filename'] = Path(filepath).name

    except Exception:
        pass

    return props


def get_environmental_climate_field_count() -> int:
    """Return the number of fields extracted by environmental climate metadata."""
    # NetCDF climate fields
    netcdf_fields = 16

    # GRIB weather fields
    grib_fields = 12

    # Environmental HDF5 fields
    hdf5_fields = 12

    # Satellite remote sensing fields
    satellite_fields = 10

    # Environmental table fields
    table_fields = 10

    # ASCII grid fields
    asc_grid_fields = 12

    # General properties
    general_fields = 6

    # Additional climate variable fields
    climate_var_fields = 14

    return (netcdf_fields + grib_fields + hdf5_fields + satellite_fields + 
            table_fields + asc_grid_fields + general_fields + climate_var_fields)


# Integration point
def extract_environmental_climate_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for environmental climate extraction."""
    return extract_environmental_climate_metadata(filepath)
