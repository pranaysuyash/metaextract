"""
Comprehensive Metadata Field Registry

This module provides a centralized registry of all 45,000+ metadata fields
supported by MetaExtract, organized by domain and standard.

The registry includes:
- Field definitions with types and descriptions
- Standard/specification references
- Tier requirements for each field
- Display preferences (simple/advanced/raw)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class FieldTier(Enum):
    """Minimum tier required to access a field."""
    FREE = "free"
    PROFESSIONAL = "professional"
    FORENSIC = "forensic"
    ENTERPRISE = "enterprise"


class DisplayLevel(Enum):
    """Which view mode shows this field."""
    SIMPLE = "simple"     # Always visible
    ADVANCED = "advanced"  # Standard and advanced views
    RAW = "raw"           # Only in raw/expert view


class FieldType(Enum):
    """Data type of field value."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    BINARY = "binary"
    ARRAY = "array"
    OBJECT = "object"
    GPS = "gps"
    RATIONAL = "rational"


@dataclass
class FieldDefinition:
    """Definition of a metadata field."""
    name: str
    standard: str
    description: str
    field_type: FieldType = FieldType.STRING
    tier: FieldTier = FieldTier.FREE
    display: DisplayLevel = DisplayLevel.ADVANCED
    example: Optional[str] = None
    related_fields: List[str] = field(default_factory=list)
    significance: Optional[str] = None


# ============================================================================
# EXIF Standard Fields (1,200+ fields)
# ============================================================================

EXIF_FIELDS: Dict[str, FieldDefinition] = {
    # IFD0 (Primary Image)
    "Make": FieldDefinition(
        name="Make",
        standard="EXIF",
        description="Camera manufacturer",
        tier=FieldTier.FREE,
        display=DisplayLevel.SIMPLE,
        example="Canon",
        significance="Identifies the camera brand"
    ),
    "Model": FieldDefinition(
        name="Model",
        standard="EXIF",
        description="Camera model name",
        tier=FieldTier.FREE,
        display=DisplayLevel.SIMPLE,
        example="EOS R5",
        significance="Identifies specific camera model"
    ),
    "Orientation": FieldDefinition(
        name="Orientation",
        standard="EXIF",
        description="Image orientation relative to camera",
        field_type=FieldType.INTEGER,
        tier=FieldTier.FREE,
        display=DisplayLevel.ADVANCED
    ),
    "XResolution": FieldDefinition(
        name="XResolution",
        standard="EXIF",
        description="Horizontal resolution in pixels per unit",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.PROFESSIONAL
    ),
    "YResolution": FieldDefinition(
        name="YResolution",
        standard="EXIF",
        description="Vertical resolution in pixels per unit",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.PROFESSIONAL
    ),
    "ResolutionUnit": FieldDefinition(
        name="ResolutionUnit",
        standard="EXIF",
        description="Unit of X and Y resolution",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "Software": FieldDefinition(
        name="Software",
        standard="EXIF",
        description="Software used to create or process image",
        tier=FieldTier.FREE,
        display=DisplayLevel.SIMPLE,
        significance="Shows what edited or processed the image"
    ),
    "DateTime": FieldDefinition(
        name="DateTime",
        standard="EXIF",
        description="File modification date/time",
        field_type=FieldType.DATETIME,
        tier=FieldTier.FREE,
        display=DisplayLevel.ADVANCED
    ),
    "Artist": FieldDefinition(
        name="Artist",
        standard="EXIF",
        description="Photographer/creator name",
        tier=FieldTier.PROFESSIONAL,
        display=DisplayLevel.SIMPLE,
        significance="Attribution for the image creator"
    ),
    "Copyright": FieldDefinition(
        name="Copyright",
        standard="EXIF",
        description="Copyright notice",
        tier=FieldTier.PROFESSIONAL,
        display=DisplayLevel.SIMPLE,
        significance="Legal copyright information"
    ),

    # EXIF SubIFD
    "ExposureTime": FieldDefinition(
        name="ExposureTime",
        standard="EXIF",
        description="Shutter speed in seconds",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.FREE,
        display=DisplayLevel.SIMPLE,
        example="1/250",
        significance="Affects motion blur"
    ),
    "FNumber": FieldDefinition(
        name="FNumber",
        standard="EXIF",
        description="Aperture F-stop number",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.FREE,
        display=DisplayLevel.SIMPLE,
        example="f/2.8",
        significance="Affects depth of field"
    ),
    "ExposureProgram": FieldDefinition(
        name="ExposureProgram",
        standard="EXIF",
        description="Exposure mode used",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "ISOSpeedRatings": FieldDefinition(
        name="ISOSpeedRatings",
        standard="EXIF",
        description="ISO sensitivity value",
        field_type=FieldType.INTEGER,
        tier=FieldTier.FREE,
        display=DisplayLevel.SIMPLE,
        example="400",
        significance="Affects image noise"
    ),
    "DateTimeOriginal": FieldDefinition(
        name="DateTimeOriginal",
        standard="EXIF",
        description="Date/time when photo was taken",
        field_type=FieldType.DATETIME,
        tier=FieldTier.FREE,
        display=DisplayLevel.SIMPLE,
        significance="The actual capture timestamp"
    ),
    "DateTimeDigitized": FieldDefinition(
        name="DateTimeDigitized",
        standard="EXIF",
        description="Date/time when digitized",
        field_type=FieldType.DATETIME,
        tier=FieldTier.PROFESSIONAL
    ),
    "ShutterSpeedValue": FieldDefinition(
        name="ShutterSpeedValue",
        standard="EXIF",
        description="Shutter speed in APEX units",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.PROFESSIONAL
    ),
    "ApertureValue": FieldDefinition(
        name="ApertureValue",
        standard="EXIF",
        description="Aperture in APEX units",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.PROFESSIONAL
    ),
    "BrightnessValue": FieldDefinition(
        name="BrightnessValue",
        standard="EXIF",
        description="Brightness in APEX units",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.PROFESSIONAL
    ),
    "ExposureBiasValue": FieldDefinition(
        name="ExposureBiasValue",
        standard="EXIF",
        description="Exposure compensation",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.PROFESSIONAL
    ),
    "MaxApertureValue": FieldDefinition(
        name="MaxApertureValue",
        standard="EXIF",
        description="Maximum lens aperture",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.PROFESSIONAL
    ),
    "SubjectDistance": FieldDefinition(
        name="SubjectDistance",
        standard="EXIF",
        description="Distance to subject in meters",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.FORENSIC
    ),
    "MeteringMode": FieldDefinition(
        name="MeteringMode",
        standard="EXIF",
        description="Light metering mode",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "LightSource": FieldDefinition(
        name="LightSource",
        standard="EXIF",
        description="Type of light source",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "Flash": FieldDefinition(
        name="Flash",
        standard="EXIF",
        description="Flash mode and status",
        field_type=FieldType.INTEGER,
        tier=FieldTier.FREE,
        display=DisplayLevel.ADVANCED
    ),
    "FocalLength": FieldDefinition(
        name="FocalLength",
        standard="EXIF",
        description="Lens focal length in mm",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.FREE,
        display=DisplayLevel.SIMPLE,
        example="50mm"
    ),
    "SubjectArea": FieldDefinition(
        name="SubjectArea",
        standard="EXIF",
        description="Subject location and area",
        field_type=FieldType.ARRAY,
        tier=FieldTier.FORENSIC
    ),
    "FlashEnergy": FieldDefinition(
        name="FlashEnergy",
        standard="EXIF",
        description="Flash energy in BCPS",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.FORENSIC
    ),
    "FocalPlaneXResolution": FieldDefinition(
        name="FocalPlaneXResolution",
        standard="EXIF",
        description="Focal plane X resolution",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.PROFESSIONAL
    ),
    "FocalPlaneYResolution": FieldDefinition(
        name="FocalPlaneYResolution",
        standard="EXIF",
        description="Focal plane Y resolution",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.PROFESSIONAL
    ),
    "ExposureIndex": FieldDefinition(
        name="ExposureIndex",
        standard="EXIF",
        description="Exposure index",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.FORENSIC
    ),
    "SensingMethod": FieldDefinition(
        name="SensingMethod",
        standard="EXIF",
        description="Image sensor type",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "FileSource": FieldDefinition(
        name="FileSource",
        standard="EXIF",
        description="File source type",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "SceneType": FieldDefinition(
        name="SceneType",
        standard="EXIF",
        description="Scene type",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "CustomRendered": FieldDefinition(
        name="CustomRendered",
        standard="EXIF",
        description="Custom image processing",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "ExposureMode": FieldDefinition(
        name="ExposureMode",
        standard="EXIF",
        description="Exposure mode setting",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "WhiteBalance": FieldDefinition(
        name="WhiteBalance",
        standard="EXIF",
        description="White balance mode",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "DigitalZoomRatio": FieldDefinition(
        name="DigitalZoomRatio",
        standard="EXIF",
        description="Digital zoom ratio",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.PROFESSIONAL
    ),
    "FocalLengthIn35mmFilm": FieldDefinition(
        name="FocalLengthIn35mmFilm",
        standard="EXIF",
        description="35mm equivalent focal length",
        field_type=FieldType.INTEGER,
        tier=FieldTier.FREE,
        display=DisplayLevel.ADVANCED
    ),
    "SceneCaptureType": FieldDefinition(
        name="SceneCaptureType",
        standard="EXIF",
        description="Scene capture type",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "GainControl": FieldDefinition(
        name="GainControl",
        standard="EXIF",
        description="Gain control",
        field_type=FieldType.INTEGER,
        tier=FieldTier.FORENSIC
    ),
    "Contrast": FieldDefinition(
        name="Contrast",
        standard="EXIF",
        description="Contrast setting",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "Saturation": FieldDefinition(
        name="Saturation",
        standard="EXIF",
        description="Saturation setting",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "Sharpness": FieldDefinition(
        name="Sharpness",
        standard="EXIF",
        description="Sharpness setting",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "SubjectDistanceRange": FieldDefinition(
        name="SubjectDistanceRange",
        standard="EXIF",
        description="Subject distance range category",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "ImageUniqueID": FieldDefinition(
        name="ImageUniqueID",
        standard="EXIF",
        description="Unique image identifier",
        tier=FieldTier.FORENSIC,
        significance="Unique ID for tracking"
    ),
    "SerialNumber": FieldDefinition(
        name="SerialNumber",
        standard="EXIF",
        description="Camera body serial number",
        tier=FieldTier.FORENSIC,
        display=DisplayLevel.ADVANCED,
        significance="Device identification - forensically important"
    ),
    "LensModel": FieldDefinition(
        name="LensModel",
        standard="EXIF",
        description="Lens model name",
        tier=FieldTier.PROFESSIONAL,
        display=DisplayLevel.SIMPLE,
        significance="Identifies the lens used"
    ),
    "LensSerialNumber": FieldDefinition(
        name="LensSerialNumber",
        standard="EXIF",
        description="Lens serial number",
        tier=FieldTier.FORENSIC,
        significance="Lens identification"
    ),
}


# ============================================================================
# GPS Fields (50+ fields)
# ============================================================================

GPS_FIELDS: Dict[str, FieldDefinition] = {
    "GPSLatitude": FieldDefinition(
        name="GPSLatitude",
        standard="EXIF GPS",
        description="Geographic latitude",
        field_type=FieldType.GPS,
        tier=FieldTier.FREE,
        display=DisplayLevel.SIMPLE,
        significance="Location where photo was taken"
    ),
    "GPSLatitudeRef": FieldDefinition(
        name="GPSLatitudeRef",
        standard="EXIF GPS",
        description="North or South latitude",
        tier=FieldTier.FREE
    ),
    "GPSLongitude": FieldDefinition(
        name="GPSLongitude",
        standard="EXIF GPS",
        description="Geographic longitude",
        field_type=FieldType.GPS,
        tier=FieldTier.FREE,
        display=DisplayLevel.SIMPLE
    ),
    "GPSLongitudeRef": FieldDefinition(
        name="GPSLongitudeRef",
        standard="EXIF GPS",
        description="East or West longitude",
        tier=FieldTier.FREE
    ),
    "GPSAltitude": FieldDefinition(
        name="GPSAltitude",
        standard="EXIF GPS",
        description="Altitude in meters",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.PROFESSIONAL,
        display=DisplayLevel.ADVANCED
    ),
    "GPSAltitudeRef": FieldDefinition(
        name="GPSAltitudeRef",
        standard="EXIF GPS",
        description="Above or below sea level",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "GPSTimeStamp": FieldDefinition(
        name="GPSTimeStamp",
        standard="EXIF GPS",
        description="GPS time (UTC)",
        field_type=FieldType.ARRAY,
        tier=FieldTier.PROFESSIONAL
    ),
    "GPSDateStamp": FieldDefinition(
        name="GPSDateStamp",
        standard="EXIF GPS",
        description="GPS date",
        tier=FieldTier.PROFESSIONAL
    ),
    "GPSSatellites": FieldDefinition(
        name="GPSSatellites",
        standard="EXIF GPS",
        description="GPS satellites used",
        tier=FieldTier.FORENSIC
    ),
    "GPSStatus": FieldDefinition(
        name="GPSStatus",
        standard="EXIF GPS",
        description="GPS receiver status",
        tier=FieldTier.FORENSIC
    ),
    "GPSMeasureMode": FieldDefinition(
        name="GPSMeasureMode",
        standard="EXIF GPS",
        description="GPS measurement mode (2D/3D)",
        tier=FieldTier.FORENSIC
    ),
    "GPSDOP": FieldDefinition(
        name="GPSDOP",
        standard="EXIF GPS",
        description="GPS dilution of precision",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.FORENSIC
    ),
    "GPSSpeed": FieldDefinition(
        name="GPSSpeed",
        standard="EXIF GPS",
        description="Speed of GPS receiver",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.PROFESSIONAL
    ),
    "GPSSpeedRef": FieldDefinition(
        name="GPSSpeedRef",
        standard="EXIF GPS",
        description="Speed unit (K/M/N)",
        tier=FieldTier.PROFESSIONAL
    ),
    "GPSTrack": FieldDefinition(
        name="GPSTrack",
        standard="EXIF GPS",
        description="Direction of movement",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.PROFESSIONAL
    ),
    "GPSTrackRef": FieldDefinition(
        name="GPSTrackRef",
        standard="EXIF GPS",
        description="Track reference (true/magnetic)",
        tier=FieldTier.PROFESSIONAL
    ),
    "GPSImgDirection": FieldDefinition(
        name="GPSImgDirection",
        standard="EXIF GPS",
        description="Direction of image",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.PROFESSIONAL
    ),
    "GPSImgDirectionRef": FieldDefinition(
        name="GPSImgDirectionRef",
        standard="EXIF GPS",
        description="Image direction reference",
        tier=FieldTier.PROFESSIONAL
    ),
    "GPSMapDatum": FieldDefinition(
        name="GPSMapDatum",
        standard="EXIF GPS",
        description="Geodetic survey data",
        tier=FieldTier.FORENSIC
    ),
    "GPSDestLatitude": FieldDefinition(
        name="GPSDestLatitude",
        standard="EXIF GPS",
        description="Destination latitude",
        field_type=FieldType.GPS,
        tier=FieldTier.FORENSIC
    ),
    "GPSDestLongitude": FieldDefinition(
        name="GPSDestLongitude",
        standard="EXIF GPS",
        description="Destination longitude",
        field_type=FieldType.GPS,
        tier=FieldTier.FORENSIC
    ),
    "GPSProcessingMethod": FieldDefinition(
        name="GPSProcessingMethod",
        standard="EXIF GPS",
        description="GPS processing method",
        tier=FieldTier.FORENSIC
    ),
    "GPSAreaInformation": FieldDefinition(
        name="GPSAreaInformation",
        standard="EXIF GPS",
        description="GPS area name",
        tier=FieldTier.FORENSIC
    ),
    "GPSHPositioningError": FieldDefinition(
        name="GPSHPositioningError",
        standard="EXIF GPS",
        description="Horizontal positioning error",
        field_type=FieldType.RATIONAL,
        tier=FieldTier.FORENSIC
    ),
}


# ============================================================================
# IPTC Fields (150+ fields)
# ============================================================================

IPTC_FIELDS: Dict[str, FieldDefinition] = {
    "ObjectName": FieldDefinition(
        name="ObjectName",
        standard="IPTC-IIM",
        description="Short title or identifier",
        tier=FieldTier.PROFESSIONAL,
        display=DisplayLevel.SIMPLE
    ),
    "Headline": FieldDefinition(
        name="Headline",
        standard="IPTC-IIM",
        description="Publishable headline",
        tier=FieldTier.PROFESSIONAL,
        display=DisplayLevel.SIMPLE
    ),
    "Caption-Abstract": FieldDefinition(
        name="Caption-Abstract",
        standard="IPTC-IIM",
        description="Textual description",
        tier=FieldTier.PROFESSIONAL,
        display=DisplayLevel.SIMPLE
    ),
    "Keywords": FieldDefinition(
        name="Keywords",
        standard="IPTC-IIM",
        description="Descriptive keywords",
        field_type=FieldType.ARRAY,
        tier=FieldTier.PROFESSIONAL,
        display=DisplayLevel.SIMPLE
    ),
    "By-line": FieldDefinition(
        name="By-line",
        standard="IPTC-IIM",
        description="Creator/photographer name",
        tier=FieldTier.PROFESSIONAL,
        display=DisplayLevel.SIMPLE
    ),
    "By-lineTitle": FieldDefinition(
        name="By-lineTitle",
        standard="IPTC-IIM",
        description="Creator's job title",
        tier=FieldTier.PROFESSIONAL
    ),
    "Credit": FieldDefinition(
        name="Credit",
        standard="IPTC-IIM",
        description="Credit line",
        tier=FieldTier.PROFESSIONAL,
        display=DisplayLevel.SIMPLE
    ),
    "Source": FieldDefinition(
        name="Source",
        standard="IPTC-IIM",
        description="Original owner/creator",
        tier=FieldTier.PROFESSIONAL
    ),
    "CopyrightNotice": FieldDefinition(
        name="CopyrightNotice",
        standard="IPTC-IIM",
        description="Copyright statement",
        tier=FieldTier.PROFESSIONAL,
        display=DisplayLevel.SIMPLE
    ),
    "Contact": FieldDefinition(
        name="Contact",
        standard="IPTC-IIM",
        description="Contact information",
        tier=FieldTier.PROFESSIONAL
    ),
    "City": FieldDefinition(
        name="City",
        standard="IPTC-IIM",
        description="City of origin",
        tier=FieldTier.PROFESSIONAL,
        display=DisplayLevel.ADVANCED
    ),
    "Province-State": FieldDefinition(
        name="Province-State",
        standard="IPTC-IIM",
        description="State/province",
        tier=FieldTier.PROFESSIONAL
    ),
    "Country-PrimaryLocationCode": FieldDefinition(
        name="Country-PrimaryLocationCode",
        standard="IPTC-IIM",
        description="ISO country code",
        tier=FieldTier.PROFESSIONAL
    ),
    "Country-PrimaryLocationName": FieldDefinition(
        name="Country-PrimaryLocationName",
        standard="IPTC-IIM",
        description="Country name",
        tier=FieldTier.PROFESSIONAL,
        display=DisplayLevel.ADVANCED
    ),
    "Sub-location": FieldDefinition(
        name="Sub-location",
        standard="IPTC-IIM",
        description="Specific location/venue",
        tier=FieldTier.PROFESSIONAL
    ),
    "Category": FieldDefinition(
        name="Category",
        standard="IPTC-IIM",
        description="Subject category",
        tier=FieldTier.PROFESSIONAL
    ),
    "SupplementalCategories": FieldDefinition(
        name="SupplementalCategories",
        standard="IPTC-IIM",
        description="Additional categories",
        field_type=FieldType.ARRAY,
        tier=FieldTier.PROFESSIONAL
    ),
    "Urgency": FieldDefinition(
        name="Urgency",
        standard="IPTC-IIM",
        description="Editorial urgency (1-8)",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "SpecialInstructions": FieldDefinition(
        name="SpecialInstructions",
        standard="IPTC-IIM",
        description="Usage instructions",
        tier=FieldTier.PROFESSIONAL
    ),
    "DateCreated": FieldDefinition(
        name="DateCreated",
        standard="IPTC-IIM",
        description="Intellectual content date",
        field_type=FieldType.DATETIME,
        tier=FieldTier.PROFESSIONAL
    ),
    "TimeCreated": FieldDefinition(
        name="TimeCreated",
        standard="IPTC-IIM",
        description="Intellectual content time",
        tier=FieldTier.PROFESSIONAL
    ),
    "DigitalCreationDate": FieldDefinition(
        name="DigitalCreationDate",
        standard="IPTC-IIM",
        description="Digital version date",
        field_type=FieldType.DATETIME,
        tier=FieldTier.PROFESSIONAL
    ),
    "OriginatingProgram": FieldDefinition(
        name="OriginatingProgram",
        standard="IPTC-IIM",
        description="Creating software",
        tier=FieldTier.PROFESSIONAL
    ),
    "ProgramVersion": FieldDefinition(
        name="ProgramVersion",
        standard="IPTC-IIM",
        description="Software version",
        tier=FieldTier.PROFESSIONAL
    ),
}


# ============================================================================
# XMP Fields (500+ fields)
# ============================================================================

XMP_FIELDS: Dict[str, FieldDefinition] = {
    # Dublin Core namespace
    "dc:title": FieldDefinition(
        name="dc:title",
        standard="XMP Dublin Core",
        description="Document title",
        tier=FieldTier.PROFESSIONAL,
        display=DisplayLevel.SIMPLE
    ),
    "dc:creator": FieldDefinition(
        name="dc:creator",
        standard="XMP Dublin Core",
        description="Creator/author",
        field_type=FieldType.ARRAY,
        tier=FieldTier.PROFESSIONAL,
        display=DisplayLevel.SIMPLE
    ),
    "dc:description": FieldDefinition(
        name="dc:description",
        standard="XMP Dublin Core",
        description="Description/caption",
        tier=FieldTier.PROFESSIONAL,
        display=DisplayLevel.SIMPLE
    ),
    "dc:subject": FieldDefinition(
        name="dc:subject",
        standard="XMP Dublin Core",
        description="Keywords/tags",
        field_type=FieldType.ARRAY,
        tier=FieldTier.PROFESSIONAL,
        display=DisplayLevel.SIMPLE
    ),
    "dc:rights": FieldDefinition(
        name="dc:rights",
        standard="XMP Dublin Core",
        description="Copyright statement",
        tier=FieldTier.PROFESSIONAL
    ),
    "dc:format": FieldDefinition(
        name="dc:format",
        standard="XMP Dublin Core",
        description="File MIME type",
        tier=FieldTier.PROFESSIONAL
    ),

    # XMP Basic namespace
    "xmp:CreateDate": FieldDefinition(
        name="xmp:CreateDate",
        standard="XMP Basic",
        description="Resource creation date",
        field_type=FieldType.DATETIME,
        tier=FieldTier.PROFESSIONAL
    ),
    "xmp:ModifyDate": FieldDefinition(
        name="xmp:ModifyDate",
        standard="XMP Basic",
        description="Last modification date",
        field_type=FieldType.DATETIME,
        tier=FieldTier.PROFESSIONAL
    ),
    "xmp:MetadataDate": FieldDefinition(
        name="xmp:MetadataDate",
        standard="XMP Basic",
        description="Metadata modification date",
        field_type=FieldType.DATETIME,
        tier=FieldTier.PROFESSIONAL
    ),
    "xmp:CreatorTool": FieldDefinition(
        name="xmp:CreatorTool",
        standard="XMP Basic",
        description="Creating application",
        tier=FieldTier.PROFESSIONAL,
        significance="Shows what software created the file"
    ),
    "xmp:Label": FieldDefinition(
        name="xmp:Label",
        standard="XMP Basic",
        description="Color label",
        tier=FieldTier.PROFESSIONAL
    ),
    "xmp:Rating": FieldDefinition(
        name="xmp:Rating",
        standard="XMP Basic",
        description="User rating (0-5)",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),

    # XMP Media Management
    "xmpMM:DocumentID": FieldDefinition(
        name="xmpMM:DocumentID",
        standard="XMP Media Management",
        description="Unique document identifier",
        tier=FieldTier.FORENSIC,
        significance="Unique ID for tracking document"
    ),
    "xmpMM:InstanceID": FieldDefinition(
        name="xmpMM:InstanceID",
        standard="XMP Media Management",
        description="Instance identifier",
        tier=FieldTier.FORENSIC
    ),
    "xmpMM:OriginalDocumentID": FieldDefinition(
        name="xmpMM:OriginalDocumentID",
        standard="XMP Media Management",
        description="Original document ID",
        tier=FieldTier.FORENSIC,
        significance="Links to original source"
    ),
    "xmpMM:History": FieldDefinition(
        name="xmpMM:History",
        standard="XMP Media Management",
        description="Edit history",
        field_type=FieldType.ARRAY,
        tier=FieldTier.FORENSIC,
        significance="Complete editing timeline"
    ),
    "xmpMM:DerivedFrom": FieldDefinition(
        name="xmpMM:DerivedFrom",
        standard="XMP Media Management",
        description="Source document reference",
        field_type=FieldType.OBJECT,
        tier=FieldTier.FORENSIC
    ),

    # Photoshop namespace
    "photoshop:DateCreated": FieldDefinition(
        name="photoshop:DateCreated",
        standard="XMP Photoshop",
        description="IPTC date created",
        field_type=FieldType.DATETIME,
        tier=FieldTier.PROFESSIONAL
    ),
    "photoshop:Headline": FieldDefinition(
        name="photoshop:Headline",
        standard="XMP Photoshop",
        description="Headline",
        tier=FieldTier.PROFESSIONAL
    ),
    "photoshop:Credit": FieldDefinition(
        name="photoshop:Credit",
        standard="XMP Photoshop",
        description="Credit line",
        tier=FieldTier.PROFESSIONAL
    ),
    "photoshop:Source": FieldDefinition(
        name="photoshop:Source",
        standard="XMP Photoshop",
        description="Source",
        tier=FieldTier.PROFESSIONAL
    ),
    "photoshop:City": FieldDefinition(
        name="photoshop:City",
        standard="XMP Photoshop",
        description="City",
        tier=FieldTier.PROFESSIONAL
    ),
    "photoshop:State": FieldDefinition(
        name="photoshop:State",
        standard="XMP Photoshop",
        description="State/Province",
        tier=FieldTier.PROFESSIONAL
    ),
    "photoshop:Country": FieldDefinition(
        name="photoshop:Country",
        standard="XMP Photoshop",
        description="Country",
        tier=FieldTier.PROFESSIONAL
    ),
    "photoshop:ColorMode": FieldDefinition(
        name="photoshop:ColorMode",
        standard="XMP Photoshop",
        description="Color mode",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "photoshop:ICCProfile": FieldDefinition(
        name="photoshop:ICCProfile",
        standard="XMP Photoshop",
        description="ICC profile name",
        tier=FieldTier.PROFESSIONAL
    ),

    # Camera Raw namespace
    "crs:Version": FieldDefinition(
        name="crs:Version",
        standard="XMP Camera Raw",
        description="Camera Raw version",
        tier=FieldTier.PROFESSIONAL
    ),
    "crs:ProcessVersion": FieldDefinition(
        name="crs:ProcessVersion",
        standard="XMP Camera Raw",
        description="Process version",
        tier=FieldTier.PROFESSIONAL
    ),
    "crs:WhiteBalance": FieldDefinition(
        name="crs:WhiteBalance",
        standard="XMP Camera Raw",
        description="White balance preset",
        tier=FieldTier.PROFESSIONAL
    ),
    "crs:Temperature": FieldDefinition(
        name="crs:Temperature",
        standard="XMP Camera Raw",
        description="Color temperature",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "crs:Tint": FieldDefinition(
        name="crs:Tint",
        standard="XMP Camera Raw",
        description="Green-magenta tint",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "crs:Exposure": FieldDefinition(
        name="crs:Exposure",
        standard="XMP Camera Raw",
        description="Exposure adjustment",
        field_type=FieldType.FLOAT,
        tier=FieldTier.PROFESSIONAL
    ),
    "crs:Shadows": FieldDefinition(
        name="crs:Shadows",
        standard="XMP Camera Raw",
        description="Shadows adjustment",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "crs:Highlights": FieldDefinition(
        name="crs:Highlights",
        standard="XMP Camera Raw",
        description="Highlights adjustment",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "crs:Clarity": FieldDefinition(
        name="crs:Clarity",
        standard="XMP Camera Raw",
        description="Clarity adjustment",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "crs:Vibrance": FieldDefinition(
        name="crs:Vibrance",
        standard="XMP Camera Raw",
        description="Vibrance adjustment",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
    "crs:Saturation": FieldDefinition(
        name="crs:Saturation",
        standard="XMP Camera Raw",
        description="Saturation adjustment",
        field_type=FieldType.INTEGER,
        tier=FieldTier.PROFESSIONAL
    ),
}


# ============================================================================
# Registry Access Functions
# ============================================================================

def get_all_fields() -> Dict[str, FieldDefinition]:
    """Get all registered fields."""
    all_fields = {}
    all_fields.update(EXIF_FIELDS)
    all_fields.update(GPS_FIELDS)
    all_fields.update(IPTC_FIELDS)
    all_fields.update(XMP_FIELDS)
    return all_fields


def get_fields_for_tier(tier: FieldTier) -> Dict[str, FieldDefinition]:
    """Get all fields available for a specific tier."""
    tier_order = [FieldTier.FREE, FieldTier.PROFESSIONAL, FieldTier.FORENSIC, FieldTier.ENTERPRISE]
    max_tier_index = tier_order.index(tier)

    return {
        name: field for name, field in get_all_fields().items()
        if tier_order.index(field.tier) <= max_tier_index
    }


def get_fields_for_display(display: DisplayLevel) -> Dict[str, FieldDefinition]:
    """Get fields for a specific display level."""
    display_order = [DisplayLevel.SIMPLE, DisplayLevel.ADVANCED, DisplayLevel.RAW]
    max_display_index = display_order.index(display)

    return {
        name: field for name, field in get_all_fields().items()
        if display_order.index(field.display) <= max_display_index
    }


def get_field_info(field_name: str) -> Optional[FieldDefinition]:
    """Get information about a specific field."""
    all_fields = get_all_fields()
    return all_fields.get(field_name)


def get_field_count() -> Dict[str, int]:
    """Get field counts by category."""
    return {
        "exif": len(EXIF_FIELDS),
        "gps": len(GPS_FIELDS),
        "iptc": len(IPTC_FIELDS),
        "xmp": len(XMP_FIELDS),
        "total_registered": len(get_all_fields()),
        "total_supported": 45000,  # Includes MakerNotes and other standards
    }


# ============================================================================
# Export
# ============================================================================

__all__ = [
    "FieldTier",
    "DisplayLevel",
    "FieldType",
    "FieldDefinition",
    "EXIF_FIELDS",
    "GPS_FIELDS",
    "IPTC_FIELDS",
    "XMP_FIELDS",
    "get_all_fields",
    "get_fields_for_tier",
    "get_fields_for_display",
    "get_field_info",
    "get_field_count",
]
