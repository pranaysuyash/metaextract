#!/usr/bin/env python3
"""
GIS/Geospatial Extractor for MetaExtract.
Extracts metadata from GeoJSON, Shapefile, KML, and other geospatial formats.
"""

import os
import sys
import json
import struct
import zipfile
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib

logger = logging.getLogger(__name__)

FIONA_AVAILABLE = True
try:
    import fiona
except ImportError:
    FIONA_AVAILABLE = False
    logger.warning("fiona not available - geospatial extraction limited")

RASTERIO_AVAILABLE = True
try:
    import rasterio
    from rasterio.crs import CRS
except ImportError:
    RASTERIO_AVAILABLE = False
    logger.warning("rasterio not available - raster extraction limited")


class GeoJSONExtractor:
    """Extract metadata from GeoJSON files."""

    def extract(self, filepath: str) -> Dict[str, Any]:
        result = {
            "source": "metaextract_geojson_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "geojson_metadata": {},
        }

        if not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            result["format_detected"] = "geojson"

            metadata = {
                "type": data.get("type"),
                "crs": data.get("crs"),
                "total_features": 0,
                "geometry_types": set(),
                "bbox": None,
                "properties_fields": set(),
            }

            features = data.get("features", [])
            if not features and data.get("type") == "Feature":
                features = [data]

            metadata["total_features"] = len(features)

            for feature in features[:100]:
                geom = feature.get("geometry", {})
                geom_type = geom.get("type")
                if geom_type:
                    metadata["geometry_types"].add(geom_type)

                props = feature.get("properties", {})
                if props:
                    metadata["properties_fields"].update(props.keys())

            if metadata["geometry_types"]:
                metadata["geometry_types"] = list(metadata["geometry_types"])

            if "bbox" in data:
                metadata["bbox"] = data["bbox"]
            else:
                coords = []
                for feature in features:
                    geom = feature.get("geometry", {})
                    if geom.get("type") == "Point":
                        coords.append(geom.get("coordinates", []))
                    elif geom.get("type") in ["LineString", "Polygon"]:
                        coords.extend(self._extract_coords(geom.get("coordinates", [])))
                if coords:
                    metadata["bbox"] = self._calc_bbox(coords)

            result["geojson_metadata"] = metadata
            result["extraction_success"] = True

        except json.JSONDecodeError as e:
            result["geojson_metadata"] = {"error": f"Invalid JSON: {e}"}
        except Exception as e:
            result["geojson_metadata"] = {"error": str(e)}

        return result

    def _extract_coords(self, coords: List) -> List:
        """Recursively extract coordinates from geometry."""
        result = []
        if not coords:
            return result
        if isinstance(coords[0], (int, float)):
            return [coords]
        for item in coords:
            result.extend(self._extract_coords(item))
        return result

    def _calc_bbox(self, coords: List) -> Optional[List]:
        """Calculate bounding box from coordinates."""
        if not coords:
            return None
        lons = [c[0] for c in coords if len(c) >= 1]
        lats = [c[1] for c in coords if len(c) >= 2]
        if not lons or not lats:
            return None
        return [min(lons), min(lats), max(lons), max(lats)]


class ShapefileExtractor:
    """Extract metadata from ESRI Shapefile files."""

    def detect_shapefile(self, filepath: str) -> bool:
        """Check if file is a valid shapefile."""
        if filepath.endswith('.shp'):
            return os.path.exists(filepath)
        if filepath.endswith('.zip'):
            return True
        base = filepath.replace('.zip', '')
        return os.path.exists(base + '.shp')

    def extract(self, filepath: str) -> Dict[str, Any]:
        result = {
            "source": "metaextract_shapefile_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "shapefile_metadata": {},
        }

        if not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        try:
            if FIONA_AVAILABLE:
                result["shapefile_metadata"] = self._extract_with_fiona(filepath)
            else:
                result["shapefile_metadata"] = self._extract_basic(filepath)

            result["format_detected"] = "shapefile"
            result["extraction_success"] = "error" not in result["shapefile_metadata"]

        except Exception as e:
            result["shapefile_metadata"] = {"error": str(e)}

        return result

    def _extract_with_fiona(self, filepath: str) -> Dict[str, Any]:
        """Extract shapefile metadata using fiona."""
        try:
            with fiona.open(filepath) as src:
                metadata = {
                    "driver": src.driver,
                    "crs": str(src.crs) if src.crs else None,
                    "bounds": list(src.bounds) if src.bounds else None,
                    "schema": src.schema,
                    "count": len(src),
                    "encoding": src.encoding,
                }

                geom_types = set()
                for feature in src:
                    geom_types.add(feature["geometry"]["type"])
                metadata["geometry_types"] = list(geom_types)

                return metadata
        except Exception as e:
            logger.error(f"Error extracting shapefile with fiona: {e}")
            return self._extract_basic(filepath)

    def _extract_basic(self, filepath: str) -> Dict[str, Any]:
        """Basic shapefile extraction without fiona."""
        result = {
            "format": "shapefile",
            "basic_info": {},
        }

        try:
            if filepath.endswith('.zip'):
                with zipfile.ZipFile(filepath, 'r') as z:
                    names = z.namelist()
                    shp_files = [n for n in names if n.endswith('.shp')]
                    if shp_files:
                        result["shp_in_zip"] = shp_files[0]
                    dbf_files = [n for n in names if n.endswith('.dbf')]
                    if dbf_files:
                        result["dbf_in_zip"] = dbf_files[0]
            else:
                base = filepath.replace('.shp', '')
                for ext in ['.shp', '.shx', '.dbf', '.prj']:
                    path = base + ext
                    if os.path.exists(path):
                        result[f"{ext[1:]}_exists"] = True
                        result[f"{ext[1:]}_size"] = os.path.getsize(path)

            result["basic_info"] = {"extracted": "basic metadata only (install fiona for full extraction)"}

        except Exception as e:
            return {"error": str(e)}

        return result


class KMLExtractor:
    """Extract metadata from KML/KMZ files."""

    def detect_kml(self, filepath: str) -> bool:
        """Check if file is a valid KML file."""
        if filepath.endswith('.kml') or filepath.endswith('.kmz'):
            return True
        if filepath.endswith('.zip'):
            with open(filepath, 'rb') as f:
                header = f.read(4)
                return header[:4] != b'PK\x03\x04'
        try:
            with open(filepath, 'r') as f:
                content = f.read(100).lower()
                return '<kml' in content or 'kml xmlns' in content
        except:
            return False

    def extract(self, filepath: str) -> Dict[str, Any]:
        result = {
            "source": "metaextract_kml_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "kml_metadata": {},
        }

        if not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        try:
            if filepath.endswith('.kmz'):
                result["kml_metadata"] = self._extract_kmz(filepath)
            else:
                result["kml_metadata"] = self._extract_kml(filepath)

            result["format_detected"] = "kml"
            result["extraction_success"] = "error" not in result["kml_metadata"]

        except Exception as e:
            result["kml_metadata"] = {"error": str(e)}

        return result

    def _extract_kml(self, filepath: str) -> Dict[str, Any]:
        """Extract KML metadata."""
        try:
            with open(filepath, 'r') as f:
                content = f.read()

            metadata = {
                "format": "kml",
                "file_size": os.path.getsize(filepath),
            }

            import re
            name_match = re.search(r'<name><!\[CDATA\[(.*?)\]\]></name>', content, re.DOTALL)
            if not name_match:
                name_match = re.search(r'<name>(.*?)</name>', content)
            metadata["name"] = name_match.group(1).strip() if name_match else None

            desc_match = re.search(r'<description><!\[CDATA\[(.*?)\]\]></description>', content, re.DOTALL)
            if not desc_match:
                desc_match = re.search(r'<description>(.*?)</description>', content)
            metadata["description"] = desc_match.group(1).strip()[:500] if desc_match else None

            folders = content.count('<Folder>')
            placemarks = content.count('<Placemark>')
            metadata["folder_count"] = folders
            metadata["placemark_count"] = placemarks

            coordinates = re.findall(r'<coordinates>(.*?)</coordinates>', content, re.DOTALL)
            if coordinates:
                coords = []
                for coord_str in coordinates[:100]:
                    for coord in coord_str.strip().split():
                        parts = coord.split(',')
                        if len(parts) >= 2:
                            try:
                                coords.append((float(parts[0]), float(parts[1])))
                            except:
                                pass
                if coords:
                    lons = [c[0] for c in coords]
                    lats = [c[1] for c in coords]
                    metadata["bounds"] = [min(lons), min(lats), max(lons), max(lats)]
                    metadata["point_count"] = len(coords)

            styles = len(re.findall(r'<Style>', content))
            metadata["style_count"] = styles

            return metadata

        except Exception as e:
            return {"error": str(e)}

    def _extract_kmz(self, filepath: str) -> Dict[str, Any]:
        """Extract KMZ (zipped KML) metadata."""
        try:
            with zipfile.ZipFile(filepath, 'r') as z:
                kml_files = [n for n in z.namelist() if n.lower().endswith('.kml')]

                metadata = {
                    "format": "kmz",
                    "zip_contents": z.namelist()[:20],
                    "kml_files": kml_files,
                }

                if kml_files:
                    kml_content = z.read(kml_files[0]).decode('utf-8', errors='replace')
                    metadata["kml_size"] = len(kml_content)
                    metadata["has_kml"] = len(kml_content) > 0

                return metadata

        except Exception as e:
            return {"error": str(e)}


class GeoTIFFExtractor:
    """Extract metadata from GeoTIFF files."""

    def detect_geotiff(self, filepath: str) -> bool:
        """Check if file is a valid GeoTIFF."""
        try:
            with open(filepath, 'rb') as f:
                header = f.read(4)
                return header[:2] == b'\x49\x49' or header[:2] == b'\x4D\x4D'
        except:
            return False

    def extract(self, filepath: str) -> Dict[str, Any]:
        result = {
            "source": "metaextract_geotiff_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "geotiff_metadata": {},
        }

        if not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        try:
            if RASTERIO_AVAILABLE:
                result["geotiff_metadata"] = self._extract_with_rasterio(filepath)
            else:
                result["geotiff_metadata"] = self._extract_basic(filepath)

            result["format_detected"] = "geotiff"
            result["extraction_success"] = "error" not in result["geotiff_metadata"]

        except Exception as e:
            result["geotiff_metadata"] = {"error": str(e)}

        return result

    def _extract_with_rasterio(self, filepath: str) -> Dict[str, Any]:
        """Extract GeoTIFF metadata using rasterio."""
        try:
            with rasterio.open(filepath) as src:
                metadata = {
                    "driver": src.driver,
                    "width": src.width,
                    "height": src.height,
                    "count": src.count,
                    "dtype": str(src.dtype),
                    "crs": str(src.crs) if src.crs else None,
                    "transform": list(src.transform) if src.transform else None,
                    "bounds": list(src.bounds) if src.bounds else None,
                    "nodata": src.nodata,
                    "compression": src.compression if hasattr(src, 'compression') else None,
                }

                if src.crs:
                    try:
                        epsg = src.crs.to_epsg()
                        metadata["epsg"] = epsg
                    except:
                        pass

                return metadata

        except Exception as e:
            logger.error(f"Error extracting GeoTIFF with rasterio: {e}")
            return self._extract_basic(filepath)

    def _extract_basic(self, filepath: str) -> Dict[str, Any]:
        """Basic GeoTIFF extraction."""
        result = {
            "format": "geotiff",
            "file_size": os.path.getsize(filepath),
        }

        try:
            with open(filepath, 'rb') as f:
                header = f.read(8)
                is_little = header[0] == 0x49
                byte_order = '<' if is_little else '>'

                f.seek(4)
                ifd_offset = struct.unpack(byte_order + 'I', f.read(4))[0]

                tags = {}
                for _ in range(10):
                    f.seek(ifd_offset)
                    num_entries = struct.unpack(byte_order + 'H', f.read(2))[0]
                    ifd_offset += 2

                    for _ in range(num_entries):
                        tag = struct.unpack(byte_order + 'H', f.read(2))[0]
                        type_ = struct.unpack(byte_order + 'H', f.read(2))[0]
                        count = struct.unpack(byte_order + 'I', f.read(4))[0]
                        value = f.read(4)

                        if tag == 256:
                            result["width"] = struct.unpack(byte_order + 'I', value)[0]
                        elif tag == 257:
                            result["height"] = struct.unpack(byte_order + 'I', value)[0]
                        elif tag == 305:
                            result["software"] = value.rstrip(b'\x00').decode('ascii', errors='replace')

                    next_ifd = struct.unpack(byte_order + 'I', f.read(4))[0]
                    if next_ifd == 0:
                        break

        except Exception as e:
            return {"error": str(e)}

        return result


class GeospatialExtractor:
    """Main geospatial extractor that dispatches to specific format extractors."""

    def __init__(self):
        self.geojson = GeoJSONExtractor()
        self.shapefile = ShapefileExtractor()
        self.kml = KMLExtractor()
        self.geotiff = GeoTIFFExtractor()

    def extract(self, filepath: str) -> Dict[str, Any]:
        """Extract geospatial metadata from file."""
        ext = Path(filepath).suffix.lower()

        if ext == '.geojson':
            return self.geojson.extract(filepath)
        elif ext in ['.shp', '.zip']:
            return self.shapefile.extract(filepath)
        elif ext in ['.kml', '.kmz']:
            return self.kml.extract(filepath)
        elif ext in ['.tif', '.tiff', '.geo']:
            if self.geotiff.detect_geotiff(filepath):
                return self.geotiff.extract(filepath)

        for extractor in [self.geojson, self.shapefile, self.kml, self.geotiff]:
            if hasattr(extractor, 'detect_' + extractor.__class__.__name__.lower().replace('extractor', '')):
                detect_method = getattr(extractor, 'detect_' + extractor.__class__.__name__.lower().replace('extractor', ''))
                if detect_method(filepath):
                    return extractor.extract(filepath)

        return {
            "source": "metaextract_geospatial_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "error": "Unknown geospatial format",
        }


def extract_geospatial_metadata(filepath: str) -> Dict[str, Any]:
    """Convenience function to extract geospatial metadata."""
    extractor = GeospatialExtractor()
    return extractor.extract(filepath)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python geospatial_extractor.py <file.geojson|shp|kml|tiff>")
        sys.exit(1)

    filepath = sys.argv[1]
    result = extract_geospatial_metadata(filepath)
    print(json.dumps(result, indent=2, default=str))
