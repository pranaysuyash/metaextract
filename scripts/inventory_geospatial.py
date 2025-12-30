#!/usr/bin/env python3
"""Geospatial Metadata Fields Inventory

This script documents metadata fields available in geospatial formats
including GeoTIFF, KML, Shapefile, NetCDF, GML, and other GIS formats.

Reference:
- GeoTIFF specification
- OGC KML 2.3
- ESRI Shapefile Technical Specification
- OGC GML 3.2.1
- NetCDF Climate and Forecast (CF) Conventions
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any


GEOSPATIAL_INVENTORY = {
    "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "source": "GeoTIFF, OGC KML, ESRI Shapefile, OGC GML, CF Conventions",
    "description": "Geospatial metadata fields for GIS and remote sensing",
    "categories": {
        "geotiff_tags": {
            "description": "GeoTIFF primary tags",
            "fields": [
                "TagID", "GDAL_NODATA", "GDAL_DATA_TYPE", "GDAL_PIXEL_TYPE",
                "GDAL_SCALE", "GDAL_OFFSET", "INTERLEAVE", "COMPRESSION",
                "PHOTOMETRIC", "PLANARCONFIG", "BITDEPTH", "SAMPLEFORMAT",
                "ROWSPERSTRIP", "STRIPOFFSETS", "STRIPBYTECOUNTS", "TILEWIDTH",
                "TILELENGTH", "TILEOFFSETS", "TILEBYTECOUNTS", "EXTRASAMPLES",
                "SAMPLESPERPIXEL", "DATATYPE", "BITSPERSAMPLE", "PREDICTOR",
                "WHITELEVEL", "TARGETPRINTERSRESOLUTION", "NUMBEROFFIRS",
                "FIRSTOR", "LASTOR", "COLORMAPENTRIES", "RESOLUTIONUNIT",
                "XRESOLUTION", "YRESOLUTION", "XPOSITION", "YPOSITION",
                "ZPOSITION", "TIEPOINTS", "PIXELSCALE", "MODELTRANSFORMATION",
                "WMS_METADATA", "JPEGTABLES", "JPEGDCTABLES", "JPEGACTABLES",
                "YCBCRCOEFFICIENTS", "YCBCRSUBSAMPLING", "YCBCRPOSITIONING",
                "REFERENCEBLACKWHITE", "EXIFIFD", "GPSINFO", "PHOTOSHOP",
                "ICCPROFILE", "IPTCDATA", "XMP", "GDAL_AREA_OR_POINT",
                "GDAL_UCRLF", "GDAL_JSON_MD", "GDAL_METADATA", "GDAL_NCORES",
                "GDAL_OVERVIEWS", "GDAL_NODATA_FOR_GRAY", "GDAL_THUMBNAIL",
                "GDAL_IMPLICIT_NODATA", "GDAL_XMP_BOX", "GDAL_NODATA_EXCEPTIONAL",
                "INTERNAL_GEOKEY", "GDAL_MD_CPANEL", "GDAL_TE_DENSITY",
                "GDAL_TE_UNIT", "GTIFF_METADATA", "GTIFF_NUM_THREADS",
                "GTIFF_REUSE_EXTERNAL_OVERVIEWS", "GTIFF_JPEG_QUALITY",
                "GTIFF_JPEG_OVERVIEW_QUALITY", "GTIFF_PREDICTOR",
                "GTIFF_SKIP_PIXELS", "GTIFF_SKIP_LAST_EOL", "GTIFF_DIRECT_IO",
                "GTIFF_ACCURATE_GEOKEY", "GTIFF_TILING_SCHEME",
                "GTIFF_READ_GEO_KEYS", "GTIFF_INLINE_GEO_KEY",
                "GTIFF_GEO_KEYS", "GTIFF_GEO_KEYS_VERSION", "GTIFF_RCS",
                "GEOSTANDARD_METADATA", "PROXY", "RPC", "BOTTOM_CF",
                "GDAL_METADATA_ADA", "GDAL_NODATA_MASK",
            ],
            "count": 80,
            "reference": "GeoTIFF Specification 1.0"
        },
        "geokey_directory": {
            "description": "GeoTIFF GeoKey directory tags",
            "fields": [
                "GTModelTypeGeoKey", "GTRasterTypeGeoKey", "GTCitationGeoKey",
                "GeographicTypeGeoKey", "GeogCitationGeoKey", "GeogAngularUnitsGeoKey",
                "GeogAzimuthUnitsGeoKey", "GeogCitationGeoKey", "GeogPrimeMeridianGeoKey",
                "GeogPrimeMeridianLongGeoKey", "GeogToEMSphereGeoKey",
                "GeogLongitudeOfPrimeMeridian", "GeogGreenwichLongitude",
                "GeogEquatorialRadius", "GeogSemiMajorAxis", "GeogSemiMinorAxis",
                "GeogInverseFlattening", "GeogAzimuthUnitSize", "GeogAngularUnitSize",
                "GeogPlanarDistanceUnit", "GeogLinearUnitSize", "GeographicTypeGeoKey",
                "GeogCSUnit", "GeogCoLatitudeAxis", "GeogLongitudeAxis",
                "GeogUTMCitationGeoKey", "ProjectedCSTypeGeoKey", "ProjCitationGeoKey",
                "ProjLinearUnitsGeoKey", "ProjLinearUnitSize", "ProjStdParallel1GeoKey",
                "ProjStdParallel2GeoKey", "ProjNatOriginLatGeoKey", "ProjNatOriginLongGeoKey",
                "ProjFalseEastingGeoKey", "ProjFalseNorthingGeoKey", "ProjFalseOriginLatGeoKey",
                "ProjFalseOriginLongGeoKey", "ProjFalseOriginEastingGeoKey",
                "ProjFalseOriginNorthingGeoKey", "ProjCenterLatGeoKey", "ProjCenterLongGeoKey",
                "ProjCenterEastingGeoKey", "ProjCenterNorthingGeoKey", "ProjAzimuthAngleGeoKey",
                "ProjStraightVertPoleLongGeoKey", "ProjRectifiedGridAngleGeoKey",
                "VerticalCSTypeGeoKey", "VertCitationGeoKey", "VertDatumGeoKey",
                "VertUnitsGeoKey", "VerticalUnitsGeoKey", "AuxiliaryCloudCover",
                "ReferenceRasterGeoKey", "PointAndPathImageGeoKey", "GDAL_NODATA",
                "GDAL_DATA_TYPE", "GDAL_IMPLICIT_NODATA", "GDAL_NODATA_MASK",
                "ModelPixelScaleGeoKey", "ModelTiepointGeoKey", "ModelTransformationGeoKey",
                "IntergraphMatrixGeoKey", "JPCodeSpaceGeoKey", "JPEGDCTablesGeoKey",
                "JPEGACTablesGeoKey", "YCbCrCoefficientsGeoKey", "YCbCrSubsamplingGeoKey",
                "YCbCrPositioningGeoKey", "ReferenceBlackWhiteGeoKey", "ColorProfileGamma",
                "ColorProfileFilename", "ColorProfileApplication", "ColorProfileEmbedded",
                "INFINITY_W", "INFINITY_POINT_W", "NAD83", "WGS84", "NAD27",
            ],
            "count": 75,
            "reference": "GeoTIFF GeoKey Directory"
        },
        "kml_ogc": {
            "description": "KML (Keyhole Markup Language) elements",
            "fields": [
                "kml", "Document", "Folder", "Placemark", "Point", "LineString",
                "Polygon", "MultiGeometry", "Style", "StyleMap", "NetworkLink",
                "GroundOverlay", "ScreenOverlay", "PhotoOverlay", "Model", "TimePrimitive",
                "TimeStamp", "TimeSpan", "LookAt", "Camera", "gx:Track", "gx:MultiTrack",
                "gx:Tour", "gx:AnimatedUpdate", "gx:LatLonQuad", "ExtendedData",
                "SchemaData", "SimpleData", "Data", "value", "name", "description",
                "visibility", "open", "address", "phoneNumber", "Snippet", "atom:link",
                "StyleSelector", "Pair", "Key", "styleUrl", "color", "colorMode",
                "Icon", "href", "gx:horizFov", "altitudeMode", "clampedToGround",
                "relativeToGround", "absolute", "extrude", "tessellate", "altitude",
                "latLonAltBox", "north", "south", "east", "west", "minAltitude",
                "maxAltitude", "gx:balloonVisibility", "Region", "Lod", "minLodPixels",
                "maxLodPixels", "minFadeExtent", "maxFadeExtent", "expires",
                "Link", "ViewRefreshMode", "ViewRefreshTime", "FlyToMode",
                "AbstractView", "TimeStamp", "when", "gx:interpolate", "coordinates",
                "outerBoundaryIs", "innerBoundaryIs", "LinearRing", "boundaryIs",
                "gx:latLonQuad", "altitudeMode", "ResourceMap", "Location", "Orientation",
                "Scale", "Link", "viewFormat", "httpQuery", "refreshMode", "refreshInterval",
                "ViewVolume", "near", "farLeft", "farRight", "leftFov", "rightFov",
                "topFov", "bottomFov", "gx:ViewerOptions", "gx:option", "enabled",
                "name", "turnAngle", "floorHeight", "range", "altitudeMode",
                "begin", "end", "TimePeriod", "TimeInstant", "gx:TimeRange",
                "Schema", "SimpleField", "name", "type", "DisplayName", "Default",
                "atom:author", "atom:name", "atom:uri", "atom:generator", "generator",
                "NetworkLinkControl", "minRefreshPeriod", "maxSessionDuration",
                "cookie", "message", "name", "linkDescription", "linkSnippet",
                "links", "expires", "update", "targetHref", "Create", "Delete",
                "Change", "Update", "targetId", "when", "Track", "coord",
                "Interpolate", "Tour", "Playlist", "gx:PlaybackMode", "gx:Wait",
                "gx:FlyTo", "gx:TourPrimitive", "gx:Control", "gx:PlayMode",
            ],
            "count": 128,
            "reference": "OGC KML 2.3"
        },
        "esri_shapefile": {
            "description": "ESRI Shapefile metadata fields",
            "fields": [
                "ShapeType", "BoundingBox", "ZMin", "ZMax", "ZRange", "MMin", "MMax",
                "MRange", "Point", "MultiPoint", "PolyLine", "Polygon", "MultiPatch",
                "NullShape", "PointZ", "PointM", "PolyLineZ", "PolygonZ", "MultiPointZ",
                "PointRecord", "PointRecordLength", "PolyLineRecord", "PolyLineRecordLength",
                "PolygonRecord", "PolygonRecordLength", "MultiPointRecord", "MultiPointRecordLength",
                "DBFFieldName", "DBFFieldType", "DBFFieldLength", "DBFDecimalCount",
                "ShxRecord", "ShxRecordLength", "FileCode", "FileLength", "Version",
                "ShapeType", "BoundingBox", "SHP", "SHX", "DBF", "PRJ", "CPG",
                "SBN", "SBX", "FBN", "FBX", "ATA", "ATX", "IXS", "IXG", "MXS",
                "MXY", "LOG", "LYR", "SDE", "Column", "DataType", "Width", "Precision",
                "Scale", "Nullable", "CaseSensitive", "Required", "Domain",
                "DomainName", "DomainType", "CodedValue", "Range", "Description",
                "DefaultValue", "SplitPolicy", "MergePolicy", "FieldIndex", "Alias",
                "IsNullable", "IsRequired", "DomainFixed", "GeometryType", "HasM",
                "HasZ", "HasSpatialIndex", "SpatialReference", "SRID", "AuthName",
                "AuthSrid", "WKT", "PROJCS", "GEOGCS", "DATUM", "SPHEROID", "PRIMEM",
                "UNIT", "EXTENSION", "PARAMETER", "TOLERANCE", "COORDINATE_PRECISION",
                "XY_TOLERANCE", "Z_TOLERANCE", "M_TOLERANCE", "UPGRADE_COPLANARITY",
                "MAINTENANCE_FLAG", "CONCEPTUALIZATIONS", "END_DELAY", "BEGIN_DELAY",
                "TIME_OF_DAY", "START_FIELD", "END_FIELD", "ELIGIBLE_FOR_CACHING",
                "STORAGE_TYPE", "SPATIAL_REFERENCE", "CLUSTER_TOLERANCE", "ALIASES",
            ],
            "count": 95,
            "reference": "ESRI Shapefile Technical Specification"
        },
        "netcdf_cf": {
            "description": "NetCDF Climate and Forecast (CF) metadata",
            "fields": [
                "long_name", "standard_name", "units", "calendar", "axis", "positive",
                "bounds", "climatology", "comment", "coordinates", "cube_elements",
                "external_variables", "flag_meanings", "flag_values", "grid_mapping",
                "institution", "references", "source", "title", "history", "Conventions",
                "featureType", "cdm_data_type", "cdm_timeseries_variables",
                "original_name", "original_units", "original_precision", "ancillary_variables",
                "associated_variables", "commentary", "instrument", "instrument_type",
                "measurement_method", "platform", "platform_type", "processing_level",
                "product_version", "program", "project", "realization", "sensor",
                "sensor_type", "source_type", "spatial_representation", "spatial_resolution",
                "time_coverage_duration", "time_coverage_end", "time_coverage_resolution",
                "time_coverage_start", "time_mean", "valid_max", "valid_min", "valid_range",
                "missing_value", "_FillValue", "ancillary_variable", "scale_factor",
                "add_offset", "compress", "contiguous", "chunk_sizes", "deflate",
                "deflate_level", "fletcher32", "shuffle", "storage_mode", "chunk_dimensions",
                "id", "naming_authority", "title", "institution", "source",
                "history", "references", "comment", "featureType", "cdm_data_type",
                "latitude", "longitude", "vertical", "time", "latitude_longitude",
                "latitude_projection", "longitude_projection", "projection",
                "longitude_of_projection_origin", "latitude_of_projection_origin",
                "straight_vertical_longitude_from_pole", "scale_factor_at_projection_origin",
                "scale_factor_at_central_pivot", "pivot_latitude", "pivot_longitude",
                "semi_major_axis", "semi_minor_axis", "inverse_flattening", "false_easting",
                "false_northing", "latitude_of_projection_origin", "longitude_of_projection_origin",
                "longitude_of_central_meridian", "latitude_of_standard_parallel",
                "scale_factor_at_central_meridian", "sweep_angle_axis", "crs_wkt",
            ],
            "count": 106,
            "reference": "CF Conventions 1.10"
        },
        "gml_ogc": {
            "description": "OGC GML (Geography Markup Language) elements",
            "fields": [
                "gml:FeatureCollection", "gml:FeatureMember", "gml:AbstractFeature",
                "gml:AbstractGeometry", "gml:Point", "gml:LineString", "gml:Polygon",
                "gml:MultiPoint", "gml:MultiLineString", "gml:MultiPolygon",
                "gml:MultiSurface", "gml:MultiCurve", "gml:GeometryCollection",
                "gml:Curve", "gml:Surface", "gml:LinearRing", "gml:Ring",
                "gml:Envelope", "gml:Box", "gml:Coord", "gml:coordinates",
                "gml:pos", "gml:posList", "gml:lowerCorner", "gml:upperCorner",
                "gml:id", "gml:identifier", "gml:name", "gml:description",
                "gml:descriptionReference", "gml:metaDataProperty", "gml:boundedBy",
                "gml:location", "gml:exterior", "gml:interior", "gml:interpolation",
                "gml:numPoints", "gml:startPoint", "gml:endPoint", "gml:arithmetic",
                "gml:coefficients", "gml:constant", "gml:definition", "gml:horizontalCS",
                "gml:verticalCS", "gml:CartesianCS", "gml:EllipsoidalCS",
                "gml:LinearCS", "gml:ObliqueCartesianCS", "gml:PolarCS",
                "gml:SphericalCS", "gml:UserDefinedCS", "gml:verticalDatum",
                "gml:TemporalCS", "gml:CoordinateSystemAxis", "gml:axisDirection",
                "gml:axisAbbrev", "gml:uom", "gml:unitOfMeasure", "gml:meridian",
                "gml:origin", "gml:secondDefiningParameter", "gml:semiMajorAxis",
                "gml:semiMinorAxis", "gml:inverseFlattening", "gml:unitVector",
                "gml:AffinePlacement", "gml:Object", "gml:DomainSet", "gml:RangeSet",
                "gml:File", "gml:rangeParameters", "gml:fileName", "gml:fileStructure",
                "gml:compression", "gml:applicationSchema", "gml:referenceSystem",
                "gml:CRS", "gml:GeodeticCRS", "gml:ProjectedCRS", "gml:VerticalCRS",
                "gml:CompoundCRS", "gml:CoordinateReferenceSystem", "gml:Identifier",
                "gml:code", "gml:codeSpace", "gml:name", "gml:remarks",
                "gml:coordinateOperation", "gml:AbstractCoordinateOperation",
                "gml:Transformation", "gml:Conversion", "gml:Method", "gml:Parameter",
                "gml:UsesValue", "gml:Value", "gml:Interval", "gml:Quantity",
                "gml:MeasureType", "gml:Length", "gml:Angle", "gml:Distance",
                "gml:Speed", "gml:Velocity", "gml:TimeInterval", "gml:Decimal",
            ],
            "count": 98,
            "reference": "OGC GML 3.2.1"
        },
        "hdf5_attributes": {
            "description": "HDF5 attributes and metadata fields",
            "fields": [
                "NAME", "DATASPACE", "MAXDIMENSION", "CURRENTDIMENSION", "DATATYPE",
                "FLOATP", "SCHEMA_NAME", "SCHEMA_VERSION", "ISO_METADATA",
                "XML_METADATA", "NCI_METADATA", "NC_GLOBAL", "DATASET_NAMES",
                "GROUP_NAMES", "DIMENSION_LIST", "REFERENCE_LIST", "ATTRIBUTE_LIST",
                "FILL_VALUE", "COMPRESS", "CHUNKING", "SHUFFLE", "DEFLATE",
                "SZIP", "NBIT", "FLETCHER32", "CONTIGUOUS", "EXTERNAL_PREFIX",
                "SOFT_LINK", "HARD_LINK", "OBJECT_HEADER", "OBJECT_TYPE",
                "CREATION_ORDER", "ATTRIBUTE", "DATASET", "GROUP", "COMMITTED_TYPE",
                "SOFT_LINK", "EXTERNAL_LINK", "USER_BLOCK", "FILE_SPACE_INFO",
                "FILE_SPACE_STRATEGY", "FILE_SPACE_PAGE_SIZE", "PAGE_SIZE",
                "DIR_BITMAP", "INDEX_BITMAP", "INDEX_BLOCK", "SMALL_RAW_DATA",
                "LARGE_RAW_DATA", "HEAP", "GLOBAL_HEAP", "LOCAL_HEAP", "OBJECT_HEAP",
                "BLOOM_FILTER", "FILTER_PIPELINE", "FILTER_CONFIG", "CD_NELMTS",
                "CD_VALUES", "FILTER_ID", "FILTER_FLAGS", "FILTER_TYPE",
                "ENABLE", "CURRENT_NBYTES", "TOTAL_NBYTES", "FILTER_DENOMINATOR",
                "FILTER_NUM_PROGRESS", "FILTER_PROGRESS", "FILTER_CALLBACK",
                "FILTER_CLEANUP", "VLEN_FILL", "VLEN_DATATYPE", "COMPOUND_FILL",
                "ENCODE_VERSION", "DECODE_VERSION", "H5LT_MAX_DSETNAME",
                "H5LT_MAX_FIELDNAME", "H5LT_MAX_NUM_DS_ATTRS", "H5LT_NUM_DS_ATTRS",
                "H5LT_ATTR_NAME_LEN", "H5LT_ATTR_CYCLE", "H5LT_ATTR_CYCLE_LARGE",
                "H5_VERSION", "H5DRIVER", "H5FILESIZE", "H5STORAGE_TYPE",
                "H5FREE_PAGE_PHY", "H5FREE_META_PHY", "H5SZERO_PHY", "H5PHYRANGES",
            ],
            "count": 92,
            "reference": "HDF5 Specification"
        },
        "raster_band_properties": {
            "description": "Raster band and pixel properties",
            "fields": [
                "NoDataValue", "FillValue", "MissingValue", "Scale", "Offset",
                "Units", "CategoryNames", "CategoryCounts", "Histogram",
                "MinValue", "MaxValue", "MinMax", "StatMean", "StatStdDev",
                "StatVariance", "StatSum", "StatSumSquares", "StatEntropy",
                "StatSkewness", "StatKurtosis", "ValidRange", "ActualRange",
                "DisplayMax", "DisplayMin", "ColorInterp", "ColorTable",
                "GDAL_NODATA", "GDAL_MD", "GDAL_HAS_NODATA", "GDAL_OVERVIEW",
                "GDAL_OVERVIEW_COUNT", "GDAL_OVERVIEW_0", "GDAL_OVERVIEW_1",
                "GDAL_OVERVIEW_2", "GDAL_OVERVIEW_3", "GDAL_OVERVIEW_4",
                "GDAL_OVERVIEW_5", "GDAL_OVERVIEW_6", "GDAL_OVERVIEW_7",
                "GDAL_RESAMPLE", "GDAL_SRS_WKT", "GDAL_SRS_PROJ", "GDAL_DCAP",
                "GDAL_DCAP_RASTER", "GDAL_DCAP_CREATE", "GDAL_DCAP_CREATECOPY",
                "GDAL_DCAP_VIRTUALIO", "GDAL_DMD", "GDAL_DMD_LONGNAME",
                "GDAL_DMD_MIMETYPE", "GDAL_DMD_EXTENSION", "GDAL_DMD_HELPTOPIC",
                "GDAL_DMD_CREATIONOPTIONLIST", "GDAL_DMD_CREATIONDATATYPES",
                "GDAL_DMD_OPENOPTIONLIST", "GDAL_DMD_SUBDATASETS", "GDAL_DMD_ZIP",
                "GDAL_DCAP_LAYERS", "GDAL_DCAP_SPATIAL_REF_SYS_TABLES",
                "GDAL_DCAP_CRS_ANGULARUnits", "GDAL_DCAP_CRS_DATUM_ELLIPSOID",
                "GDAL_DCAP_NON_SPHERICAL_EXTENT", "GDAL_DCAP_MEASURED_GEOMETRIES",
                "GDAL_DCAP_VIRTUALIO", "GDAL_CMD_LINE", "GDAL_DMD_NUM_DIMENSIONS",
                "GDAL_DMD_DIMENSION_LIST", "TILE_SIZE", "BLOCK_SIZE", "INTERLEAVE",
                "COMPRESSION", "QUALITY", "PHOTOMETRIC_INTERPRETATION",
                "PLANAR_CONFIG", "BAND_STORAGE_TYPE", "SAMPLE_FORMAT",
                "BIT_DEPTH", "JB2K_QFACTOR", "JPEG_QUALITY", "JPEG_PROGRESSIVE",
                "JPEG_OVERVIEW_QUALITY", "DEFLATE_LEVEL", "ZLEVEL", "LZMA_PRESET",
                "NUM_THREADS", "TARGET_PERCENT", "GDAL_DCAP_SEQ_NUM_LAYERS",
            ],
            "count": 82,
            "reference": "GDAL Raster Band"
        },
        "coordinate_reference_systems": {
            "description": "Coordinate Reference System definitions",
            "fields": [
                "WKT", "PROJJSON", "PROJ4", "EPSG", "ESRI", "SRID", "AUTHNAME",
                "CODE", "NAME", "DEFINITION", "TYPE", "CATEGORY", "SCOPE",
                "AREA", "BBOX", "COUNTRY", "EXTENSION", "DEPRECATED",
                "COORD_DM_CODE", "COORD_DM_OPERATION", "COORD_OP_CODE",
                "COORD_OP_NAME", "COORD_OP_TYPE", "SRC_CRS_CODE", "SRC_CRS_NAME",
                "TGT_CRS_CODE", "TGT_CRS_NAME", "METHOD_CODE", "METHOD_NAME",
                "PARAM_CODE", "PARAM_NAME", "PARAM_VALUE", "PARAM_UNIT",
                "OPERATION_VERSION", "ACCURACY", "COORDSYS_CODE", "COORDSYS_NAME",
                "COORD_AXIS_CODE", "COORD_AXIS_NAME", "COORD_AXIS_ABBREV",
                "COORD_AXIS_DIRECTION", "COORD_AXIS_UNIT", "COORD_DM_OPERATION_VIEW",
                "COORD_DM_OPERATION_MATH", "COORD_DM_OPERATION_PARAM",
                "ELLIPSOID_CODE", "ELLIPSOID_NAME", "SEMI_MAJOR", "SEMI_MINOR",
                "INV_FLATTENING", "PRIME_MERIDIAN_CODE", "PRIME_MERIDIAN_NAME",
                "GREENWICH_LONGITUDE", "UNIT_CODE", "UNIT_NAME", "UNIT_FACTOR",
                "ANGULAR_UNIT", "LINEAR_UNIT", "TIME_UNIT", "SCALE_UNIT",
                "AREA_CODE", "AREA_NAME", "AREA_SRS", "REMARKS", "SUBTYPE",
                "VERT_DATUM_CODE", "VERT_DATUM_NAME", "VERT_DATUM_TYPE",
                "COMPOUND_CRS_CODE", "COMPOUND_CRS_NAME", "HORIZONTAL_CRS",
                "VERTICAL_CRS", "TEMPORAL_CRS", "DATUM_CODE", "DATUM_NAME",
                "DATUM_TYPE", "DATUM_CATEGORY", "SPHEROID_CODE", "SPHEROID_NAME",
                "MERCATOR", "LAMBERT_CONFORMAL", "POLAR_STEREO", "OBLIQUE_MERCATOR",
                "HOTINE_OBLIQUE", "KROVAK", "CASSINI", "ECKERT", "MOLLWEIDE",
                "ROBINSON", "Stereographic", "Lambert_Azimuthal", "Sinusoidal",
                "Gnomonic", "Orthographic", "Perspective", "VanDerGrinten",
            ],
            "count": 82,
            "reference": "EPSG/OGC CRS Registry"
        },
        "time_series_observation": {
            "description": "Time series and observation metadata",
            "fields": [
                "observationID", "phenomenonTime", "resultTime", "validTime",
                "procedure", "procedureType", "procedureDescription", "procedureID",
                "observedProperty", "observedPropertyType", "featureOfInterest",
                "featureOfInterestType", "result", "resultQuality", "value",
                "uom", "valueType", "metadata", "samplingTime", "samplingProtocol",
                "samplingSize", "samplingMethod", "aggregatedObservation",
                "compositeObservation", "湖区观测观测", "directObservation",
                "surveyObservation", "collectionObservation", "imageObservation",
                "trajectoryObservation", "pointObservation", "profileObservation",
                "timeSeriesObservation", "memberObservation", "resultObservation",
                "Parameter", "AbstractFeature", "ObservableProperty", "Sensor",
                "Actuator", "Platform", "Procedure", "Observation", "ObservationCollection",
                "ObservationProcess", "Sensors", "Actuators", "System", "Thing",
                "Location", "HistoricalLocation", "FeatureOfInterest", "Datastream",
                "MultiDatastream", "SensorOutput", "ObservedProperty", "unitOfMeasurement",
                "Measurement", "Category", "Count", "Text", "Boolean", "ObservationType",
                "DatastreamType", "MultiDatastreamType", "EncodingType", "ResultType",
                "IObservation", "IDatastream", "IThing", "ILocation", "IHistoricalLocation",
                "IFeatureOfInterest", "IObservedProperty", "IProcedure", "ISensor",
                "IActuator", "IPlatform", "IDatastream", "ITimeSeries",
                "IDataArray", "Observations", "Observers", "Features", "Properties",
                "Processes", "Systems", "Things", "Locations", "Stream",
                "TimeArray", "DataArray", "ComponentArray", "MemberArray",
                "LabelArray", "QualityArray", "ValueCount", "ValueArray",
            ],
            "count": 98,
            "reference": "OGC/ISO Observations and Measurements"
        }
    },
    "totals": {
        "categories": 10,
        "total_fields": 936
    }
}


def main():
    output_dir = Path("dist/geospatial_inventory")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "geospatial_inventory.json"
    output_file.write_text(json.dumps(GEOSPATIAL_INVENTORY, indent=2, sort_keys=True), encoding="utf-8")
    
    summary = {
        "generated_at": GEOSPATIAL_INVENTORY["generated_at"],
        "source": GEOSPATIAL_INVENTORY["source"],
        "categories": GEOSPATIAL_INVENTORY["totals"]["categories"],
        "total_fields": GEOSPATIAL_INVENTORY["totals"]["total_fields"],
        "field_counts_by_category": {}
    }
    
    for cat, data in GEOSPATIAL_INVENTORY["categories"].items():
        summary["field_counts_by_category"][cat] = {
            "description": data["description"],
            "count": data["count"],
            "reference": data.get("reference", "N/A")
        }
    
    summary_file = output_dir / "geospatial_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    
    print("=" * 70)
    print("GEOSPATIAL METADATA FIELD INVENTORY")
    print("=" * 70)
    print()
    print(f"Generated: {GEOSPATIAL_INVENTORY['generated_at']}")
    print(f"Categories: {GEOSPATIAL_INVENTORY['totals']['categories']}")
    print(f"Total Fields: {GEOSPATIAL_INVENTORY['totals']['total_fields']:,}")
    print()
    print("FIELD COUNTS BY CATEGORY:")
    print("-" * 50)
    for cat, data in sorted(GEOSPATIAL_INVENTORY["categories"].items(), key=lambda x: x[1]["count"], reverse=True):
        ref = data.get("reference", "")[:35]
        print(f"  {cat:35s}: {data['count']:>3}  [{ref}]")
    print()
    print(f"Wrote: {output_file}")
    print(f"Wrote: {summary_file}")


if __name__ == "__main__":
    main()
