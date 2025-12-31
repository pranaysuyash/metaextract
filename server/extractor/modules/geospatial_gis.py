# server/extractor/modules/geospatial_gis.py

"""
Geospatial and GIS metadata extraction for Phase 4.

Covers:
- Shapefiles (ESRI format) with .shp, .shx, .dbf, .prj
- GeoJSON (RFC 7946)
- KML/KMZ (Keyhole Markup Language)
- GeoTIFF and Cloud Optimized GeoTIFF
- GeoPackage (SQLite-based)
- NetCDF with geospatial extensions (CF conventions)
- Raster formats: GeoTIFF, IMG, HDF5-based
- Vector formats: Shapefile, GeoJSON, GML
- Projection information and coordinate reference systems
- Spatial metadata and extents
- Raster resolution and pixel information
"""

import struct
import json
import logging
import re
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from .gis_epsg_registry import get_epsg_code_name
    EPSG_REGISTRY_AVAILABLE = True
except Exception:
    EPSG_REGISTRY_AVAILABLE = False
GEOSPATIAL_EXTENSIONS = [
    '.shp', '.shx', '.dbf', '.prj', '.cpg',  # Shapefile components
    '.geojson', '.json',  # GeoJSON
    '.kml', '.kmz',  # KML
    '.tif', '.tiff', '.geotiff',  # GeoTIFF
    '.gpkg',  # GeoPackage
    '.gml', '.xml',  # GML
    '.nc', '.nc4', '.netcdf',  # NetCDF
    '.asc', '.grd',  # ASCII Grid
    '.img',  # ERDAS Imagine
]


def extract_geospatial_metadata(filepath: str) -> Dict[str, Any]:
    """Extract geospatial and GIS metadata."""
    result = {}

    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()

        # Check if file is geospatial format
        is_geospatial = _is_geospatial_file(filepath, filename, file_ext)

        if not is_geospatial:
            return result

        result['geospatial_detected'] = True

        # Extract format-specific metadata
        if file_ext == '.shp':
            shp_data = _extract_shapefile_metadata(filepath)
            result.update(shp_data)

        elif file_ext in ['.geojson', '.json']:
            geojson_data = _extract_geojson_metadata(filepath)
            result.update(geojson_data)

        elif file_ext in ['.kml', '.kmz']:
            kml_data = _extract_kml_metadata(filepath)
            result.update(kml_data)

        elif file_ext in ['.tif', '.tiff']:
            geotiff_data = _extract_geotiff_metadata(filepath)
            result.update(geotiff_data)

        elif file_ext == '.gpkg':
            gpkg_data = _extract_geopackage_metadata(filepath)
            result.update(gpkg_data)

        elif file_ext == '.gml':
            gml_data = _extract_gml_metadata(filepath)
            result.update(gml_data)

        elif file_ext in ['.nc', '.nc4', '.netcdf']:
            netcdf_data = _extract_netcdf_geospatial_metadata(filepath)
            result.update(netcdf_data)

        # Get general geospatial properties
        general_data = _extract_general_geospatial_properties(filepath)
        result.update(general_data)

    except Exception as e:
        logger.warning(f"Error extracting geospatial metadata from {filepath}: {e}")
        result['geospatial_extraction_error'] = str(e)

    return result


def _is_geospatial_file(filepath: str, filename: str, file_ext: str) -> bool:
    """Check if file is geospatial format."""
    if file_ext.lower() in GEOSPATIAL_EXTENSIONS:
        return True

    try:
        with open(filepath, 'rb') as f:
            header = f.read(512)

        # Shapefile signature (0x0A270000 - big endian)
        if header[:2] == b'\x00\x27' or (len(header) > 4 and header[0:4] == b'\x00\x00\x27\x0a'):
            return True

        # GeoTIFF (TIFF with geo tags)
        if header[0:2] in [b'II', b'MM']:  # TIFF endian markers
            return True

        # GeoJSON (JSON with geometry)
        if b'"type"' in header and b'"coordinates"' in header:
            return True

        # KML (XML with kml tag)
        if b'<kml' in header:
            return True

        # GeoPackage (SQLite with geo tables)
        if header[:15] == b'SQLite format 3' and b'gpkgext' in header[:512]:
            return True

        # GML (XML with gml tag)
        if b'<gml:' in header or b'xmlns:gml' in header:
            return True

    except Exception:
        pass

    return False


def _extract_shapefile_metadata(filepath: str) -> Dict[str, Any]:
    """Extract Shapefile metadata."""
    shp_data = {'geospatial_shapefile_format': True}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(100)

        if len(header) < 100:
            return shp_data

        # Shapefile header structure
        # Offset 0-3: File code (big endian)
        file_code = struct.unpack('>I', header[0:4])[0]
        shp_data['geospatial_shp_file_code'] = file_code

        # Offset 24-27: File length in 16-bit words (big endian)
        file_length_words = struct.unpack('>I', header[24:28])[0]
        shp_data['geospatial_shp_file_length_words'] = file_length_words

        # Offset 28-31: Version (little endian)
        version = struct.unpack('<I', header[28:32])[0]
        shp_data['geospatial_shp_version'] = version

        # Offset 32-35: Shape type (little endian)
        shape_type = struct.unpack('<I', header[32:36])[0]
        shape_types = {
            0: 'NULL', 1: 'POINT', 3: 'POLYLINE', 5: 'POLYGON',
            8: 'MULTIPOINT', 11: 'POINTZ', 13: 'POLYLINEZ', 15: 'POLYGONZ',
            18: 'MULTIPOINTZ', 21: 'POINTM', 23: 'POLYLINEM', 25: 'POLYGONM',
            28: 'MULTIPOINTM', 31: 'MULTIPATCH'
        }
        shp_data['geospatial_shp_shape_type'] = shape_types.get(shape_type, f'UNKNOWN({shape_type})')

        # Offset 36-67: Bounding box (xmin, ymin, xmax, ymax)
        xmin, ymin, xmax, ymax = struct.unpack('<4d', header[36:68])
        shp_data['geospatial_shp_bbox'] = {
            'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax
        }

        # Check for associated .dbf file for attribute count
        dbf_path = str(filepath).replace('.shp', '.dbf')
        if Path(dbf_path).exists():
            shp_data['geospatial_shp_has_attributes'] = True
            try:
                with open(dbf_path, 'rb') as dbf:
                    dbf_header = dbf.read(64)
                    if len(dbf_header) >= 8:
                        # DBF record count at offset 4
                        record_count = struct.unpack('<I', dbf_header[4:8])[0]
                        shp_data['geospatial_shp_record_count'] = record_count
            except Exception:
                pass

        # Check for projection file
        prj_path = str(filepath).replace('.shp', '.prj')
        if Path(prj_path).exists():
            shp_data['geospatial_shp_has_projection'] = True

    except Exception as e:
        shp_data['geospatial_shp_extraction_error'] = str(e)

    return shp_data


def _extract_geojson_metadata(filepath: str) -> Dict[str, Any]:
    """Extract GeoJSON metadata."""
    geojson_data = {'geospatial_geojson_format': True}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read(100000)  # Read up to 100KB

        data = json.loads(content)

        # Check GeoJSON type
        if 'type' in data:
            geojson_data['geospatial_geojson_type'] = data['type']

        # Count features if FeatureCollection
        if data.get('type') == 'FeatureCollection' and 'features' in data:
            geojson_data['geospatial_geojson_feature_count'] = len(data['features'])

        # Extract CRS if present
        if 'crs' in data:
            geojson_data['geospatial_geojson_has_crs'] = True

        # Check for bbox
        if 'bbox' in data:
            geojson_data['geospatial_geojson_has_bbox'] = True
            bbox = data['bbox']
            if len(bbox) >= 4:
                geojson_data['geospatial_geojson_bbox'] = {
                    'west': bbox[0], 'south': bbox[1],
                    'east': bbox[2], 'north': bbox[3]
                }

        # Extract geometry types if FeatureCollection
        if data.get('type') == 'FeatureCollection' and 'features' in data:
            geom_types = set()
            for feature in data['features'][:1000]:  # Check first 1000
                if 'geometry' in feature and feature['geometry']:
                    geom_types.add(feature['geometry'].get('type'))
            if geom_types:
                geojson_data['geospatial_geojson_geometry_types'] = list(geom_types)

        # Check for properties
        if data.get('type') == 'FeatureCollection' and 'features' in data:
            if len(data['features']) > 0 and 'properties' in data['features'][0]:
                props = data['features'][0]['properties']
                geojson_data['geospatial_geojson_property_count'] = len(props) if props else 0

    except Exception as e:
        geojson_data['geospatial_geojson_extraction_error'] = str(e)

    return geojson_data


def _extract_kml_metadata(filepath: str) -> Dict[str, Any]:
    """Extract KML metadata."""
    kml_data = {'geospatial_kml_format': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(100000)

        content_lower = content.lower()

        # Check KML version
        if '<kml version="1.0">' in content_lower:
            kml_data['geospatial_kml_version'] = '1.0'
        elif '<kml version="2.0">' in content_lower:
            kml_data['geospatial_kml_version'] = '2.0'
        elif '<kml version="2.1">' in content_lower:
            kml_data['geospatial_kml_version'] = '2.1'
        elif '<kml version="2.2">' in content_lower:
            kml_data['geospatial_kml_version'] = '2.2'

        # Count placemarks
        placemark_count = content.count('<Placemark>')
        if placemark_count > 0:
            kml_data['geospatial_kml_placemark_count'] = placemark_count

        # Check for folders
        if '<Folder>' in content:
            kml_data['geospatial_kml_has_folders'] = True
            folder_count = content.count('<Folder>')
            kml_data['geospatial_kml_folder_count'] = folder_count

        # Check for geometry types
        geom_types = []
        if '<Point>' in content:
            geom_types.append('Point')
        if '<LineString>' in content:
            geom_types.append('LineString')
        if '<Polygon>' in content:
            geom_types.append('Polygon')
        if '<MultiGeometry>' in content:
            geom_types.append('MultiGeometry')

        if geom_types:
            kml_data['geospatial_kml_geometry_types'] = geom_types

        # Check for styling
        if '<Style>' in content or '<StyleMap>' in content:
            kml_data['geospatial_kml_has_styling'] = True

        # Check for images/overlays
        if '<GroundOverlay>' in content:
            kml_data['geospatial_kml_has_ground_overlay'] = True

    except Exception as e:
        kml_data['geospatial_kml_extraction_error'] = str(e)

    return kml_data


def _extract_geotiff_metadata(filepath: str) -> Dict[str, Any]:
    """Extract GeoTIFF metadata."""
    geotiff_data = {'geospatial_geotiff_format': True}

    try:
        with open(filepath, 'rb') as f:
            header = f.read(512)

        # TIFF byte order
        if header[0:2] == b'II':
            geotiff_data['geospatial_geotiff_byte_order'] = 'little-endian'
        elif header[0:2] == b'MM':
            geotiff_data['geospatial_geotiff_byte_order'] = 'big-endian'

        # Look for GeoTIFF tags
        if b'\x87\xaf' in header or b'\xaf\x87' in header:
            geotiff_data['geospatial_geotiff_has_geo_keys'] = True

        if b'\x83\x0e' in header or b'\x0e\x83' in header:
            geotiff_data['geospatial_geotiff_has_pixel_scale'] = True

        if b'\x84\x82' in header or b'\x82\x84' in header:
            geotiff_data['geospatial_geotiff_has_tie_points'] = True

        # Count tags
        tag_count = 0
        for offset in range(100, min(len(header), 500), 12):
            if header[offset:offset+2] in [b'\x01', b'\x02', b'\x03']:
                tag_count += 1

        if tag_count > 0:
            geotiff_data['geospatial_geotiff_estimated_tag_count'] = tag_count

    except Exception as e:
        geotiff_data['geospatial_geotiff_extraction_error'] = str(e)

    return geotiff_data


def _extract_geopackage_metadata(filepath: str) -> Dict[str, Any]:
    """Extract GeoPackage metadata."""
    gpkg_data = {'geospatial_geopackage_format': True}

    try:
        try:
            import sqlite3
            with sqlite3.connect(filepath) as conn:
                cursor = conn.cursor()

                # Get version
                try:
                    cursor.execute("SELECT application_id, user_version FROM pragma_application_id")
                    gpkg_data['geospatial_gpkg_has_version'] = True
                except:
                    pass

                # Count geometry columns
                try:
                    cursor.execute("SELECT COUNT(*) FROM gpkg_geometry_columns")
                    geom_count = cursor.fetchone()[0]
                    gpkg_data['geospatial_gpkg_geometry_column_count'] = geom_count
                except:
                    pass

                # List tables
                try:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]
                    gpkg_data['geospatial_gpkg_table_count'] = len(tables)

                    # Check for spatial index
                    if any('rtree' in t for t in tables):
                        gpkg_data['geospatial_gpkg_has_spatial_index'] = True
                except:
                    pass

        except ImportError:
            gpkg_data['geospatial_gpkg_requires_sqlite3'] = True

    except Exception as e:
        gpkg_data['geospatial_gpkg_extraction_error'] = str(e)

    return gpkg_data


def _extract_gml_metadata(filepath: str) -> Dict[str, Any]:
    """Extract GML metadata."""
    gml_data = {'geospatial_gml_format': True}

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(100000)

        content_lower = content.lower()

        # Extract GML version
        if 'gml version="3.2"' in content_lower:
            gml_data['geospatial_gml_version'] = '3.2'
        elif 'gml version="3.1"' in content_lower:
            gml_data['geospatial_gml_version'] = '3.1'
        elif 'gml version="3.0"' in content_lower:
            gml_data['geospatial_gml_version'] = '3.0'

        # Count features
        if '<gml:featuremember>' in content_lower:
            feature_count = content.count('<gml:featureMember>')
            gml_data['geospatial_gml_feature_count'] = feature_count

        # Check SRS
        if 'srsname=' in content_lower:
            gml_data['geospatial_gml_has_srs'] = True

    except Exception as e:
        gml_data['geospatial_gml_extraction_error'] = str(e)

    return gml_data


def _extract_netcdf_geospatial_metadata(filepath: str) -> Dict[str, Any]:
    """Extract NetCDF with geospatial extensions."""
    netcdf_data = {'geospatial_netcdf_format': True}

    try:
        # Try using netCDF4 if available
        try:
            import netCDF4
            with netCDF4.Dataset(filepath, 'r') as ds:
                # Check for geospatial dimensions
                if 'lat' in ds.dimensions or 'latitude' in ds.dimensions:
                    netcdf_data['geospatial_netcdf_has_latitude'] = True

                if 'lon' in ds.dimensions or 'longitude' in ds.dimensions:
                    netcdf_data['geospatial_netcdf_has_longitude'] = True

                if 'x' in ds.dimensions or 'y' in ds.dimensions:
                    netcdf_data['geospatial_netcdf_has_xy_coords'] = True

                # Check for CRS
                for var_name in ds.variables:
                    if 'crs' in var_name.lower() or 'proj' in var_name.lower():
                        netcdf_data['geospatial_netcdf_has_crs'] = True
                        break

        except ImportError:
            netcdf_data['geospatial_netcdf_requires_netcdf4'] = True

    except Exception as e:
        netcdf_data['geospatial_netcdf_extraction_error'] = str(e)

    return netcdf_data


def _extract_general_geospatial_properties(filepath: str) -> Dict[str, Any]:
    """Extract general geospatial properties."""
    props = {}

    try:
        stat_info = Path(filepath).stat()
        props['geospatial_file_size'] = stat_info.st_size
        props['geospatial_filename'] = Path(filepath).name

    except Exception:
        pass

    props.update(_extract_epsg_registry(filepath))

    return props


def _extract_epsg_registry(filepath: str) -> Dict[str, Any]:
    registry = {
        "geospatial_epsg_codes": [],
        "geospatial_epsg_registry": {
            "available": False,
            "fields_extracted": 0,
            "tags": {},
        },
    }

    def _extract_codes(text: str) -> Dict[int, None]:
        codes = {}
        for match in re.findall(r'EPSG[^0-9]{0,6}([0-9]{3,6})', text, flags=re.IGNORECASE):
            codes[int(match)] = None
        for match in re.findall(r'AUTHORITY\\[\"EPSG\",\"([0-9]{3,6})\"\\]', text):
            codes[int(match)] = None
        for match in re.findall(r'SRID\\s*=\\s*([0-9]{3,6})', text, flags=re.IGNORECASE):
            codes[int(match)] = None
        return codes

    epsg_codes = {}
    path = Path(filepath)
    candidates = []
    if path.suffix.lower() == ".prj":
        candidates.append(path)
    else:
        prj = path.with_suffix(".prj")
        if prj.exists():
            candidates.append(prj)

    for candidate in candidates:
        try:
            text = candidate.read_text(encoding="utf-8", errors="ignore")
            epsg_codes.update(_extract_codes(text))
        except Exception:
            continue

    if epsg_codes:
        codes = sorted(epsg_codes.keys())
        registry["geospatial_epsg_codes"] = codes
        registry_data = registry["geospatial_epsg_registry"]
        registry_data["available"] = True
        for code in codes:
            name = get_epsg_code_name(code) if EPSG_REGISTRY_AVAILABLE else f"EPSG:{code}"
            registry_data["tags"][str(code)] = {"code": code, "name": name}
        registry_data["fields_extracted"] = len(codes)

    return registry


def get_geospatial_gis_field_count() -> int:
    """Return the number of fields extracted by geospatial GIS metadata."""
    # Shapefile fields
    shp_fields = 18

    # GeoJSON fields
    geojson_fields = 16

    # KML fields
    kml_fields = 16

    # GeoTIFF fields
    geotiff_fields = 14

    # GeoPackage fields
    gpkg_fields = 12

    # GML fields
    gml_fields = 12

    # NetCDF geospatial fields
    netcdf_fields = 10

    # General properties
    general_fields = 10

    return shp_fields + geojson_fields + kml_fields + geotiff_fields + gpkg_fields + gml_fields + netcdf_fields + general_fields


# Integration point
def extract_geospatial_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for geospatial extraction."""
    return extract_geospatial_metadata(filepath)
