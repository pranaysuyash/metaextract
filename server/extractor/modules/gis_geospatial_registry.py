
# Geospatial Metadata Registry
# Covers GeoTIFF (GeoKeys), LAS (Lidar), and open geospatial standards.

from __future__ import annotations

from functools import lru_cache
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, Dict, List

FALLBACK_GIS_FIELDS = {
    # --- GeoTIFF GeoKeys (Standard) ---
    "geotiff.GTModelTypeGeoKey": "Model Type (Projected/Geographic)",
    "geotiff.GTRasterTypeGeoKey": "Raster Type (Area/Point)",
    "geotiff.GeographicTypeGeoKey": "Geographic CRS Code",
    "geotiff.GeogCitationGeoKey": "Geographic Citation",
    "geotiff.GeogGeodeticDatumGeoKey": "Geodetic Datum",
    "geotiff.GeogPrimeMeridianGeoKey": "Prime Meridian",
    "geotiff.GeogLinearUnitsGeoKey": "Linear Units",
    "geotiff.GeogAngularUnitsGeoKey": "Angular Units",
    "geotiff.GeogEllipsoidGeoKey": "Ellipsoid",
    "geotiff.GeogSemiMajorAxisGeoKey": "Semi-Major Axis",
    "geotiff.GeogSemiMinorAxisGeoKey": "Semi-Minor Axis",
    "geotiff.ProjectedCSTypeGeoKey": "Projected CRS Code",
    "geotiff.PCSCitationGeoKey": "Projection Citation",
    "geotiff.ProjectionGeoKey": "Projection Method",
    "geotiff.ProjCoordTransGeoKey": "Coordinate Transformation",
    "geotiff.ProjLinearUnitsGeoKey": "Projection Linear Units",
    "geotiff.ProjStdParallel1GeoKey": "Standard Parallel 1",
    "geotiff.ProjStdParallel2GeoKey": "Standard Parallel 2",
    "geotiff.ProjNatOriginLongGeoKey": "Origin Longitude",
    "geotiff.ProjNatOriginLatGeoKey": "Origin Latitude",
    "geotiff.ProjFalseEastingGeoKey": "False Easting",
    "geotiff.ProjFalseNorthingGeoKey": "False Northing",
    # --- LAS (Lidar) Header ---
    "las.file_signature": "File Signature (LASF)",
    "las.file_source_id": "File Source ID",
    "las.global_encoding": "Global Encoding",
    "las.project_id_guid": "Project ID GUID",
    "las.version_major": "Version Major",
    "las.version_minor": "Version Minor",
    "las.system_identifier": "System Identifier",
    "las.generating_software": "Generating Software",
    "las.creation_day": "Creation Day",
    "las.creation_year": "Creation Year",
    "las.header_size": "Header Size",
    "las.offset_to_point_data": "Offset to Point Data",
    "las.number_of_variable_length_records": "Num VLRs",
    "las.point_data_format_id": "Point Data Format ID",
    "las.point_data_record_length": "Point Data Record Length",
    "las.number_of_point_records": "Num Point Records",
    "las.x_scale_factor": "X Scale Factor",
    "las.y_scale_factor": "Y Scale Factor",
    "las.z_scale_factor": "Z Scale Factor",
    "las.x_offset": "X Offset",
    "las.y_offset": "Y Offset",
    "las.z_offset": "Z Offset",
    "las.max_x": "Max X",
    "las.min_x": "Min X",
    "las.max_y": "Max Y",
    "las.min_y": "Min Y",
    "las.max_z": "Max Z",
    "las.min_z": "Min Z",
    # --- Metadata (XML in LAS VLR) ---
    "las.metadata.xml": "Embedded XML Metadata",
    "las.crs.wkt": "CRS WKT String",
    "las.classification.stats": "Classification Statistics",
}


@lru_cache(maxsize=1)
def _load_geospatial_inventory_fields() -> Dict[str, str]:
    root = Path(__file__).resolve().parents[3]
    inventory_path = root / "scripts" / "inventory_geospatial.py"
    if inventory_path.exists():
        try:
            spec = spec_from_file_location("inventory_geospatial", inventory_path)
            if spec and spec.loader:
                module = module_from_spec(spec)
                spec.loader.exec_module(module)
                inventory = getattr(module, "GEOSPATIAL_INVENTORY", None)
                if isinstance(inventory, dict):
                    fields: Dict[str, str] = {}
                    for category in inventory.get("categories", {}).values():
                        for field in category.get("fields", []) or []:
                            fields[str(field)] = str(field)
                    if fields:
                        return fields
        except Exception:
            pass
    return {}


def get_gis_geospatial_registry_fields() -> Dict[str, str]:
    fields = dict(FALLBACK_GIS_FIELDS)
    fields.update(_load_geospatial_inventory_fields())
    return fields


def get_gis_geospatial_registry_field_count() -> int:
    fields = get_gis_geospatial_registry_fields()
    return len(fields) if fields else 300


def extract_gis_geospatial_registry_metadata(filepath: str) -> Dict[str, Any]:
    metadata: Dict[str, Any] = {}
    registry = {
        "available": False,
        "fields_extracted": 0,
        "tags": {},
        "unknown_tags": {},
    }
    result = {
        "metadata": metadata,
        "fields_extracted": 0,
        "is_valid_gis_geospatial_registry": False,
        "extraction_method": "geospatial_gis",
        "registry": registry,
    }

    try:
        from .geospatial_gis import extract_geospatial_metadata
        geo = extract_geospatial_metadata(filepath)
        if geo:
            metadata.update(geo)
            registry["available"] = True
            for key, value in geo.items():
                registry["tags"][key] = {"name": key, "value": value}
            registry["fields_extracted"] = len(registry["tags"])
            result["fields_extracted"] = len(metadata)
            result["is_valid_gis_geospatial_registry"] = True
    except Exception as e:
        result["error"] = f"gis_geospatial_registry extraction failed: {str(e)[:200]}"

    return result
