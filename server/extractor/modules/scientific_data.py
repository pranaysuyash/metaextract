"""
Scientific Data Metadata
Extract metadata from HDF5 and NetCDF files.
"""

from typing import Any, Dict, Optional
import logging
import os


logger = logging.getLogger(__name__)

try:
    import h5py
    HDF5_AVAILABLE = True
except Exception:
    HDF5_AVAILABLE = False
    h5py = None  # type: ignore[assignment]

try:
    import netCDF4
    NETCDF_AVAILABLE = True
except Exception:
    NETCDF_AVAILABLE = False
    netCDF4 = None  # type: ignore[assignment]


def _normalize_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    if hasattr(value, "tolist"):
        try:
            return value.tolist()
        except Exception:
            return str(value)
    if isinstance(value, dict):
        return {k: _normalize_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize_value(v) for v in value]
    return value


def _normalize_attrs(attrs) -> Dict[str, Any]:
    return {key: _normalize_value(value) for key, value in attrs.items()}


def extract_hdf5_metadata(filepath: str) -> Optional[Dict[str, Any]]:
    if not HDF5_AVAILABLE:
        return {"available": False, "reason": "h5py not installed"}

    try:
        with h5py.File(filepath, "r") as hdf:
            result = {
                "available": True,
                "file_info": {},
                "groups": {},
                "datasets": {},
                "attributes": {},
            }

            result["file_info"] = {
                "hdf5_version": getattr(hdf, "libver", None),
                "file_size": os.path.getsize(filepath),
            }

            result["attributes"] = _normalize_attrs(hdf.attrs)

            def explore_group(group, path=""):
                group_info = {
                    "path": path,
                    "attributes": _normalize_attrs(group.attrs),
                    "subgroups": [],
                    "datasets": [],
                }

                for key in group.keys():
                    item = group[key]
                    item_path = f"{path}/{key}" if path else key

                    if isinstance(item, h5py.Group):
                        group_info["subgroups"].append(key)
                        result["groups"][item_path] = explore_group(item, item_path)
                    elif isinstance(item, h5py.Dataset):
                        dataset_info = {
                            "path": item_path,
                            "shape": _normalize_value(item.shape),
                            "dtype": str(item.dtype),
                            "size": int(item.size),
                            "attributes": _normalize_attrs(item.attrs),
                            "chunks": _normalize_value(item.chunks),
                            "compression": item.compression,
                            "compression_opts": _normalize_value(item.compression_opts),
                        }
                        group_info["datasets"].append(key)
                        result["datasets"][item_path] = dataset_info

                return group_info

            result["groups"]["/"] = explore_group(hdf)
            result["file_info"]["total_groups"] = len(result["groups"])
            result["file_info"]["total_datasets"] = len(result["datasets"])
            result["file_info"]["total_attributes"] = (
                sum(len(group.get("attributes", {})) for group in result["groups"].values())
                + sum(len(dataset.get("attributes", {})) for dataset in result["datasets"].values())
            )

            return result
    except Exception as exc:
        logger.error(f"Error extracting HDF5 metadata: {exc}")
        return {"available": False, "error": str(exc)}


def extract_netcdf_metadata(filepath: str) -> Optional[Dict[str, Any]]:
    if not NETCDF_AVAILABLE:
        return {"available": False, "reason": "netCDF4 not installed"}

    try:
        with netCDF4.Dataset(filepath, "r") as nc:
            result = {
                "available": True,
                "file_info": {},
                "dimensions": {},
                "variables": {},
                "global_attributes": {},
            }

            result["file_info"] = {
                "format": nc.data_model,
                "file_format": nc.file_format,
                "disk_format": nc.disk_format,
            }

            result["global_attributes"] = {
                attr: _normalize_value(getattr(nc, attr)) for attr in nc.ncattrs()
            }

            for dim_name, dim in nc.dimensions.items():
                result["dimensions"][dim_name] = {
                    "size": len(dim),
                    "unlimited": dim.isunlimited(),
                }

            for var_name, var in nc.variables.items():
                attributes = {
                    attr: _normalize_value(getattr(var, attr)) for attr in var.ncattrs()
                }
                cf_attrs = [
                    "units",
                    "long_name",
                    "standard_name",
                    "valid_range",
                    "scale_factor",
                    "add_offset",
                    "_FillValue",
                ]
                result["variables"][var_name] = {
                    "dimensions": _normalize_value(var.dimensions),
                    "shape": _normalize_value(var.shape),
                    "dtype": str(var.dtype),
                    "attributes": attributes,
                    "cf_attributes": {attr: attributes[attr] for attr in cf_attrs if attr in attributes},
                }

            result["file_info"]["num_dimensions"] = len(result["dimensions"])
            result["file_info"]["num_variables"] = len(result["variables"])
            result["file_info"]["num_global_attributes"] = len(result["global_attributes"])

            return result
    except Exception as exc:
        logger.error(f"Error extracting NetCDF metadata: {exc}")
        return {"available": False, "error": str(exc)}
