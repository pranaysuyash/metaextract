#!/usr/bin/env python3
"""
Climate/Environmental Data Extractor for MetaExtract.
Extracts metadata from NetCDF, GRIB, HDF5 climate datasets, and satellite products.
"""

import os
import sys
import json
import struct
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List, Union, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import mimetypes

logger = logging.getLogger(__name__)

NETCDF4_AVAILABLE = True
try:
    import netCDF4
except ImportError:
    NETCDF4_AVAILABLE = False
    logger.warning("netCDF4 not available - climate extraction limited")

H5PY_AVAILABLE = True
try:
    import h5py
except ImportError:
    H5PY_AVAILABLE = False
    logger.debug("h5py not available")

NUMPY_AVAILABLE = True
try:
    import numpy as np
except ImportError:
    NUMPY_AVAILABLE = False


class ClimateDataFormat(Enum):
    NETCDF = "netcdf"
    HDF5 = "hdf5"
    GRIB = "grib"
    BUFR = "bufr"
    GEOTIFF = "geotiff"
    ASCII_GRID = "ascii_grid"
    UNKNOWN = "unknown"


@dataclass
class ClimateVariable:
    name: str = ""
    standard_name: Optional[str] = None
    long_name: Optional[str] = None
    units: Optional[str] = None
    shape: Tuple[int, ...] = ()
    dtype: str = ""
    valid_min: Optional[float] = None
    valid_max: Optional[float] = None
    scale_factor: Optional[float] = None
    add_offset: Optional[float] = None
    missing_value: Optional[float] = None
    coordinates: Optional[str] = None
    cell_methods: Optional[str] = None
    comment: Optional[str] = None


@dataclass
class ClimateDataset:
    format_type: str = ""
    title: Optional[str] = None
    institution: Optional[str] = None
    source: Optional[str] = None
    history: Optional[str] = None
    references: Optional[str] = None
    comment: Optional[str] = None
    Conventions: Optional[str] = None
    time_coverage_start: Optional[str] = None
    time_coverage_end: Optional[str] = None
    time_coverage_duration: Optional[str] = None
    geospatial_lat_min: Optional[float] = None
    geospatial_lat_max: Optional[float] = None
    geospatial_lon_min: Optional[float] = None
    geospatial_lon_max: Optional[float] = None
    geospatial_vertical_min: Optional[float] = None
    geospatial_vertical_max: Optional[float] = None
    geospatial_vertical_units: Optional[str] = None
    geospatial_vertical_resolution: Optional[float] = None
    variables: List[ClimateVariable] = field(default_factory=list)
    dimensions: Dict[str, int] = field(default_factory=dict)
    global_attributes: Dict[str, Any] = field(default_factory=dict)


class ClimateExtractor:
    """Extract climate/environmental data metadata from various formats."""

    def __init__(self):
        self.supported_formats = [
            ClimateDataFormat.NETCDF,
            ClimateDataFormat.HDF5,
            ClimateDataFormat.GEOTIFF,
        ]

    def _is_ascii_grid(self, filepath: str) -> bool:
        """Check if file is an ASCII grid by examining content."""
        try:
            with open(filepath, 'r') as f:
                first_lines = []
                for i, line in enumerate(f):
                    if i >= 10:
                        break
                    first_lines.append(line.strip())
            
            # Check for ASCII grid header keywords
            has_ncols = any('ncols' in line.lower() for line in first_lines)
            has_nrows = any('nrows' in line.lower() for line in first_lines)
            has_cellsize = any('cellsize' in line.lower() for line in first_lines)
            
            return has_ncols and has_nrows and has_cellsize
        except:
            return False

    def detect_format(self, filepath: str) -> ClimateDataFormat:
        """Detect climate data format from file header or content."""
        with open(filepath, 'rb') as f:
            header = f.read(8)

        if header[:3] == b'CDF':
            return ClimateDataFormat.NETCDF
        elif header[:4] == b'\x89HDF':
            return ClimateDataFormat.HDF5
        elif header[:4] == b'GRIB':
            return ClimateDataFormat.GRIB
        elif header[:4] == b'BUFR':
            return ClimateDataFormat.BUFR
        elif header[:2] == b'\x89II':
            return ClimateDataFormat.GEOTIFF
        elif self._is_ascii_grid(filepath):
            return ClimateDataFormat.ASCII_GRID
        else:
            return ClimateDataFormat.UNKNOWN

    def extract_netcdf_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extract NetCDF CF-compliant metadata."""
        if not NETCDF4_AVAILABLE:
            return {"error": "netCDF4 library not available"}

        try:
            with netCDF4.Dataset(filepath, 'r') as nc:
                dataset = ClimateDataset(
                    format_type="netcdf4",
                    title=getattr(nc, 'title', None),
                    institution=getattr(nc, 'institution', None),
                    source=getattr(nc, 'source', None),
                    history=getattr(nc, 'history', None),
                    references=getattr(nc, 'references', None),
                    comment=getattr(nc, 'comment', None),
                    Conventions=getattr(nc, 'Conventions', None),
                    time_coverage_start=getattr(nc, 'time_coverage_start', None),
                    time_coverage_end=getattr(nc, 'time_coverage_end', None),
                    time_coverage_duration=getattr(nc, 'time_coverage_duration', None),
                    geospatial_lat_min=getattr(nc, 'geospatial_lat_min', None),
                    geospatial_lat_max=getattr(nc, 'geospatial_lat_max', None),
                    geospatial_lon_min=getattr(nc, 'geospatial_lon_min', None),
                    geospatial_lon_max=getattr(nc, 'geospatial_lon_max', None),
                    geospatial_vertical_min=getattr(nc, 'geospatial_vertical_min', None),
                    geospatial_vertical_max=getattr(nc, 'geospatial_vertical_max', None),
                    geospatial_vertical_units=getattr(nc, 'geospatial_vertical_units', None),
                    geospatial_vertical_resolution=getattr(nc, 'geospatial_vertical_resolution', None),
                )

                dataset.dimensions = dict(nc.dimensions)

                ncattrs = []
                if hasattr(nc, 'ncattrs'):
                    ncattrs = nc.ncattrs()
                dataset.global_attributes = {k: nc.getncattr(k) for k in ncattrs}

                for var_name in nc.variables:
                    var = nc.variables[var_name]
                    var_ncattrs = []
                    if hasattr(var, 'ncattrs'):
                        var_ncattrs = var.ncattrs()

                    climate_var = ClimateVariable(
                        name=var_name,
                        standard_name=var.getncattr('standard_name') if 'standard_name' in var_ncattrs else None,
                        long_name=var.getncattr('long_name') if 'long_name' in var_ncattrs else None,
                        units=var.getncattr('units') if 'units' in var_ncattrs else None,
                        shape=var.shape,
                        dtype=str(var.dtype),
                        valid_min=var.getncattr('valid_min') if 'valid_min' in var_ncattrs else None,
                        valid_max=var.getncattr('valid_max') if 'valid_max' in var_ncattrs else None,
                        scale_factor=var.getncattr('scale_factor') if 'scale_factor' in var_ncattrs else None,
                        add_offset=var.getncattr('add_offset') if 'add_offset' in var_ncattrs else None,
                        missing_value=var.getncattr('missing_value') if 'missing_value' in var_ncattrs else None,
                        coordinates=var.getncattr('coordinates') if 'coordinates' in var_ncattrs else None,
                        cell_methods=var.getncattr('cell_methods') if 'cell_methods' in var_ncattrs else None,
                        comment=var.getncattr('comment') if 'comment' in var_ncattrs else None,
                    )
                    dataset.variables.append(climate_var)

                result = {
                    "format_type": dataset.format_type,
                    "title": dataset.title,
                    "institution": dataset.institution,
                    "source": dataset.source,
                    "history": dataset.history,
                    "Conventions": dataset.Conventions,
                    "time_coverage_start": dataset.time_coverage_start,
                    "time_coverage_end": dataset.time_coverage_end,
                    "geospatial_lat_min": dataset.geospatial_lat_min,
                    "geospatial_lat_max": dataset.geospatial_lat_max,
                    "geospatial_lon_min": dataset.geospatial_lon_min,
                    "geospatial_lon_max": dataset.geospatial_lon_max,
                    "dimensions": dataset.dimensions,
                    "variable_count": len(dataset.variables),
                    "dimension_count": len(dataset.dimensions),
                    "attribute_count": len(dataset.global_attributes),
                    "global_attributes": dataset.global_attributes,
                }

                variables_list = []
                for v in dataset.variables:
                    variables_list.append({
                        "name": v.name,
                        "standard_name": v.standard_name,
                        "long_name": v.long_name,
                        "units": v.units,
                        "shape": list(v.shape),
                        "dtype": v.dtype,
                    })
                result["variables"] = variables_list

                return result

        except Exception as e:
            logger.error(f"Error extracting NetCDF metadata: {e}")
            return {"error": str(e)}

    def extract_hdf5_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extract HDF5 climate dataset metadata."""
        if not H5PY_AVAILABLE:
            return {"error": "h5py library not available"}

        try:
            with h5py.File(filepath, 'r') as f:
                result = {
                    "format": "hdf5",
                    "file_id": str(f.id.id) if hasattr(f.id, 'id') else None,
                    "file_signature": "HDF5",
                    "root_group": f.name,
                    "attributes": dict(f.attrs),
                }

                def extract_items(group, prefix=""):
                    items = {}
                    for name in group:
                        item = group[name]
                        path = f"{prefix}/{name}" if prefix else name
                        if isinstance(item, h5py.Dataset):
                            shape = None
                            if hasattr(item, 'shape'):
                                shape = item.shape
                            items[path] = {
                                "type": "dataset",
                                "shape": shape,
                                "dtype": str(item.dtype),
                                "attrs": dict(item.attrs),
                            }
                        elif isinstance(item, h5py.Group):
                            items[path] = {
                                "type": "group",
                                "attrs": dict(item.attrs),
                            }
                    return items

                result["contents"] = extract_items(f)

                climate_vars = []
                for name in f:
                    if hasattr(f[name], 'attrs'):
                        attrs = dict(f[name].attrs)
                        if any(k in attrs for k in ['standard_name', 'units', 'long_name']):
                            shape = None
                            if hasattr(f[name], 'shape'):
                                shape = f[name].shape
                            climate_vars.append({
                                "name": name,
                                "shape": shape,
                                "attrs": attrs,
                            })

                result["climate_variables"] = climate_vars
                result["climate_variable_count"] = len(climate_vars)

                return result

        except Exception as e:
            logger.error(f"Error extracting HDF5 metadata: {e}")
            return {"error": str(e)}

    def extract_ascii_grid(self, filepath: str) -> Dict[str, Any]:
        """Extract ESRI ASCII Grid metadata."""
        result = {
            "format": "ascii_grid",
            "ncols": None,
            "nrows": None,
            "xllcorner": None,
            "yllcorner": None,
            "cellsize": None,
            "nodata_value": None,
            "min_value": None,
            "max_value": None,
        }

        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()

            header = {}
            data_values = []

            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) == 2:
                    key = parts[0].lower()
                    try:
                        if key in ['ncols', 'nrows']:
                            header[key] = int(parts[1])
                        else:
                            header[key] = float(parts[1])
                    except ValueError:
                        pass
                elif len(parts) > 2:
                    try:
                        data_values.extend([float(x) for x in parts])
                    except ValueError:
                        pass

            result.update(header)

            if data_values:
                result["min_value"] = min(data_values)
                result["max_value"] = max(data_values)

            result["header_line_count"] = len(header)

        except Exception as e:
            logger.error(f"Error extracting ASCII grid metadata: {e}")
            return {"error": str(e)}

        return result

    def extract(self, filepath: str) -> Dict[str, Any]:
        """Extract climate/environmental metadata from a file."""
        result = {
            "source": "metaextract_climate_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "climate_metadata": {},
        }

        if not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        format_type = self.detect_format(filepath)
        result["format_detected"] = format_type.value

        if format_type == ClimateDataFormat.NETCDF:
            result["climate_metadata"] = self.extract_netcdf_metadata(filepath)
            result["extraction_success"] = "error" not in result["climate_metadata"]

        elif format_type == ClimateDataFormat.HDF5:
            result["climate_metadata"] = self.extract_hdf5_metadata(filepath)
            result["extraction_success"] = "error" not in result["climate_metadata"]

        elif format_type == ClimateDataFormat.GEOTIFF:
            result["climate_metadata"] = {"format": "geotiff", "note": "Basic extraction"}
            result["extraction_success"] = True

        elif format_type == ClimateDataFormat.ASCII_GRID:
            result["climate_metadata"] = self.extract_ascii_grid(filepath)
            result["extraction_success"] = True

        else:
            result["climate_metadata"] = {"message": "Unsupported climate format"}
            result["extraction_success"] = False

        return result


def extract_climate_metadata(filepath: str) -> Dict[str, Any]:
    """Convenience function to extract climate metadata."""
    extractor = ClimateExtractor()
    return extractor.extract(filepath)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python climate_extractor.py <file.nc>")
        sys.exit(1)

    filepath = sys.argv[1]
    result = extract_climate_metadata(filepath)
    print(json.dumps(result, indent=2, default=str))
