"""
Context Profiles Registry

Defines UI templates, priority fields, and special components for each detected context.
This drives the dynamic UI adaptation based on file type and content.
"""

from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field


@dataclass
class ContextProfile:
    """Configuration for a specific file context"""
    context_type: str
    display_name: str
    description: str
    ui_template: str
    priority_fields: List[str]
    special_components: List[str]
    field_groups: Dict[str, List[str]]
    relevance_rules: Dict[str, str] = field(default_factory=dict)
    icon: str = "file"
    color: str = "slate"


# Context Profiles Registry
CONTEXT_PROFILES: Dict[str, ContextProfile] = {

    # =========================================================================
    # PHOTOGRAPHY CONTEXTS
    # =========================================================================

    "smartphone_photo": ContextProfile(
        context_type="smartphone_photo",
        display_name="Smartphone Photo",
        description="Photo taken with a smartphone camera, potentially with computational photography",
        ui_template="computational_photography",
        icon="smartphone",
        color="blue",
        priority_fields=[
            "Make", "Model", "DateTimeOriginal", "GPSLatitude", "GPSLongitude",
            "LensModel", "ExposureTime", "FNumber", "ISO", "FocalLength",
            "Software", "ImageWidth", "ImageHeight"
        ],
        special_components=[
            "depth_map_viewer",
            "live_photo_timeline",
            "golden_hour_indicator",
            "computational_photography_badge",
            "gps_map_mini"
        ],
        field_groups={
            "Camera": ["Make", "Model", "LensModel", "Software"],
            "Exposure": ["ExposureTime", "FNumber", "ISO", "ExposureCompensation"],
            "Location": ["GPSLatitude", "GPSLongitude", "GPSAltitude"],
            "Computational": ["DepthData", "HDRGain", "PortraitMode", "NightMode"],
            "Time": ["DateTimeOriginal", "DateTimeDigitized", "TimeZone"]
        },
        relevance_rules={
            "show_depth_map": "has_depth_data",
            "show_live_photo": "has_live_photo",
            "show_gps_map": "has_gps",
            "show_computational_badge": "has_computational_photography"
        }
    ),

    "dslr_photo": ContextProfile(
        context_type="dslr_photo",
        display_name="DSLR/Mirrorless Photo",
        description="Photo taken with a professional or prosumer camera",
        ui_template="exposure_triangle",
        icon="camera",
        color="purple",
        priority_fields=[
            "Make", "Model", "LensModel", "ShutterCount", "SerialNumber",
            "ExposureTime", "FNumber", "ISO", "FocalLength", "ApertureValue",
            "MeteringMode", "ExposureMode", "WhiteBalance", "Flash"
        ],
        special_components=[
            "exposure_triangle_diagram",
            "lens_profile_viewer",
            "shutter_count_analysis",
            "histogram_viewer",
            "color_profile_info"
        ],
        field_groups={
            "Camera Body": ["Make", "Model", "SerialNumber", "ShutterCount", "FirmwareVersion"],
            "Lens": ["LensModel", "LensSerialNumber", "FocalLength", "MaxApertureValue"],
            "Exposure": ["ExposureTime", "FNumber", "ISO", "ExposureCompensation", "MeteringMode"],
            "Settings": ["WhiteBalance", "Flash", "ExposureMode", "FocusMode"],
            "Color": ["ColorSpace", "ICCProfile", "WhitePoint"]
        },
        relevance_rules={
            "show_lens_diagram": "has_lens_model",
            "show_shutter_analysis": "has_shutter_count",
            "show_serial_forensics": "has_serial_number"
        }
    ),

    "drone_photo": ContextProfile(
        context_type="drone_photo",
        display_name="Drone/Aerial Photo",
        description="Aerial photograph taken from a drone or UAV",
        ui_template="map_centered",
        icon="plane",
        color="cyan",
        priority_fields=[
            "GPSLatitude", "GPSLongitude", "GPSAltitude", "RelativeAltitude",
            "FlightSpeed", "GimbalRoll", "GimbalPitch", "GimbalYaw",
            "Make", "Model", "DateTimeOriginal"
        ],
        special_components=[
            "flight_path_visualization",
            "altitude_chart",
            "gimbal_orientation_3d",
            "aerial_map_overlay",
            "drone_model_info"
        ],
        field_groups={
            "Flight Data": ["GPSAltitude", "RelativeAltitude", "FlightSpeed", "FlightDirection"],
            "Gimbal": ["GimbalRoll", "GimbalPitch", "GimbalYaw"],
            "Location": ["GPSLatitude", "GPSLongitude", "GPSSpeed"],
            "Aircraft": ["Make", "Model", "SerialNumber", "FirmwareVersion"],
            "Camera": ["CameraModel", "FocalLength", "FNumber", "ISO"]
        },
        relevance_rules={
            "show_flight_path": "has_gps_track",
            "show_gimbal_animation": "has_gimbal_data",
            "show_altitude_chart": "has_altitude"
        }
    ),

    "action_camera_photo": ContextProfile(
        context_type="action_camera_photo",
        display_name="Action Camera",
        description="Photo from an action camera (GoPro, DJI Action, etc.)",
        ui_template="action_sports",
        icon="video",
        color="orange",
        priority_fields=[
            "Make", "Model", "DateTimeOriginal", "GPSLatitude", "GPSLongitude",
            "GPSSpeed", "Accelerometer", "Gyroscope", "FieldOfView"
        ],
        special_components=[
            "motion_track_viewer",
            "speed_graph",
            "orientation_indicator",
            "waterproof_depth_indicator"
        ],
        field_groups={
            "Device": ["Make", "Model", "FirmwareVersion"],
            "Motion": ["GPSSpeed", "Accelerometer", "Gyroscope"],
            "Location": ["GPSLatitude", "GPSLongitude", "GPSAltitude"],
            "Settings": ["FieldOfView", "VideoMode", "ProtuneSettings"]
        },
        relevance_rules={
            "show_motion_data": "has_accelerometer",
            "show_speed_graph": "has_gps_speed"
        }
    ),

    # =========================================================================
    # SPECIALIZED DOMAINS
    # =========================================================================

    "dicom_medical": ContextProfile(
        context_type="dicom_medical",
        display_name="Medical Image (DICOM)",
        description="Medical imaging file in DICOM format",
        ui_template="medical_context",
        icon="heart-pulse",
        color="red",
        priority_fields=[
            "PatientID", "StudyDate", "Modality", "BodyPartExamined",
            "Manufacturer", "InstitutionName", "Exposure", "KVP",
            "StudyDescription", "SeriesDescription"
        ],
        special_components=[
            "body_part_diagram",
            "dose_meter",
            "modality_icon",
            "anonymization_warning",
            "dicom_viewer_link"
        ],
        field_groups={
            "Study": ["StudyDate", "StudyTime", "StudyDescription", "AccessionNumber"],
            "Patient": ["PatientID", "PatientAge", "PatientSex", "BodyPartExamined"],
            "Equipment": ["Manufacturer", "ManufacturerModelName", "InstitutionName"],
            "Acquisition": ["Modality", "Exposure", "KVP", "XRayTubeCurrent"],
            "Image": ["Rows", "Columns", "BitsAllocated", "PhotometricInterpretation"]
        },
        relevance_rules={
            "show_dose_info": "has_radiation_data",
            "show_body_diagram": "has_body_part",
            "show_anonymization_warning": "has_patient_data"
        }
    ),

    "astronomy_fits": ContextProfile(
        context_type="astronomy_fits",
        display_name="Astronomical Data (FITS)",
        description="Astronomical observation in FITS format",
        ui_template="astronomy_context",
        icon="star",
        color="indigo",
        priority_fields=[
            "OBJECT", "RA", "DEC", "EXPTIME", "FILTER", "TELESCOP",
            "INSTRUME", "DATE-OBS", "OBSERVER", "AIRMASS"
        ],
        special_components=[
            "celestial_coordinate_overlay",
            "star_chart_viewer",
            "exposure_calculator",
            "target_identification",
            "fits_header_viewer"
        ],
        field_groups={
            "Target": ["OBJECT", "RA", "DEC", "EQUINOX"],
            "Observation": ["DATE-OBS", "EXPTIME", "FILTER", "AIRMASS"],
            "Equipment": ["TELESCOP", "INSTRUME", "DETECTOR", "FOCALLEN"],
            "Observer": ["OBSERVER", "OBSERVAT", "SITENAME"],
            "Calibration": ["BIAS", "DARK", "FLAT", "GAIN"]
        },
        relevance_rules={
            "show_star_chart": "has_coordinates",
            "show_target_id": "has_object_name"
        }
    ),

    "geospatial": ContextProfile(
        context_type="geospatial",
        display_name="Geospatial Image",
        description="Satellite or GIS imagery with geographic metadata",
        ui_template="geospatial_context",
        icon="globe",
        color="green",
        priority_fields=[
            "GeoTransform", "Projection", "EPSG", "BoundingBox",
            "AcquisitionDate", "SatelliteName", "SensorType", "Resolution"
        ],
        special_components=[
            "map_bounds_overlay",
            "coordinate_system_info",
            "band_selector",
            "resolution_indicator",
            "coverage_preview"
        ],
        field_groups={
            "Geographic": ["GeoTransform", "Projection", "EPSG", "BoundingBox"],
            "Acquisition": ["AcquisitionDate", "SatelliteName", "SensorType"],
            "Image": ["Resolution", "BandCount", "DataType", "NoDataValue"],
            "Processing": ["ProcessingLevel", "CloudCover", "SunElevation"]
        },
        relevance_rules={
            "show_map_overlay": "has_geotransform",
            "show_band_info": "has_multiple_bands"
        }
    ),

    # =========================================================================
    # CONTENT-BASED CONTEXTS
    # =========================================================================

    "ai_generated": ContextProfile(
        context_type="ai_generated",
        display_name="AI-Generated Image",
        description="Image created by AI (Midjourney, DALL-E, Stable Diffusion, etc.)",
        ui_template="ai_generated",
        icon="sparkles",
        color="pink",
        priority_fields=[
            "Software", "Creator", "Prompt", "Model", "Seed",
            "Steps", "CFGScale", "Sampler", "DateTimeOriginal"
        ],
        special_components=[
            "ai_model_badge",
            "generation_parameters",
            "prompt_viewer",
            "authenticity_warning"
        ],
        field_groups={
            "Generation": ["Software", "Model", "Prompt", "NegativePrompt"],
            "Parameters": ["Seed", "Steps", "CFGScale", "Sampler"],
            "Output": ["ImageWidth", "ImageHeight", "ColorSpace"],
            "Source": ["Creator", "DateTimeOriginal"]
        },
        relevance_rules={
            "show_prompt": "has_prompt",
            "show_generation_params": "has_ai_parameters"
        }
    ),

    "edited_image": ContextProfile(
        context_type="edited_image",
        display_name="Edited Image",
        description="Image that has been edited in software like Photoshop or Lightroom",
        ui_template="editing_history",
        icon="wand",
        color="amber",
        priority_fields=[
            "Software", "HistoryAction", "HistoryWhen", "OriginalDocumentID",
            "DerivedFrom", "EditingTime", "Make", "Model"
        ],
        special_components=[
            "edit_history_timeline",
            "software_chain_viewer",
            "original_vs_edited",
            "manipulation_indicators"
        ],
        field_groups={
            "Edit History": ["Software", "HistoryAction", "HistoryWhen", "EditingTime"],
            "Original": ["OriginalDocumentID", "DerivedFrom", "DateTimeOriginal"],
            "Camera": ["Make", "Model", "LensModel"],
            "Modifications": ["CropApplied", "ToneCurve", "WhiteBalance"]
        },
        relevance_rules={
            "show_edit_timeline": "has_edit_history",
            "show_original_link": "has_original_id"
        }
    ),

    "screenshot": ContextProfile(
        context_type="screenshot",
        display_name="Screenshot",
        description="Screen capture from a device",
        ui_template="screenshot_context",
        icon="monitor",
        color="slate",
        priority_fields=[
            "Software", "ImageWidth", "ImageHeight", "ColorSpace",
            "DateTimeOriginal", "DeviceModel", "OperatingSystem"
        ],
        special_components=[
            "device_info_badge",
            "resolution_indicator",
            "os_version_info"
        ],
        field_groups={
            "Device": ["DeviceModel", "OperatingSystem", "Software"],
            "Image": ["ImageWidth", "ImageHeight", "ColorSpace", "BitDepth"],
            "Time": ["DateTimeOriginal", "TimeZone"]
        },
        relevance_rules={
            "show_device_info": "has_device_model"
        }
    ),

    # =========================================================================
    # FALLBACK CONTEXTS
    # =========================================================================

    "generic_photo": ContextProfile(
        context_type="generic_photo",
        display_name="Photo",
        description="Standard photograph",
        ui_template="default_photo",
        icon="image",
        color="slate",
        priority_fields=[
            "Make", "Model", "DateTimeOriginal", "ImageWidth", "ImageHeight",
            "ExposureTime", "FNumber", "ISO", "FocalLength"
        ],
        special_components=[
            "basic_exif_view",
            "gps_map_mini"
        ],
        field_groups={
            "Camera": ["Make", "Model", "LensModel"],
            "Exposure": ["ExposureTime", "FNumber", "ISO"],
            "Image": ["ImageWidth", "ImageHeight", "ColorSpace"],
            "Location": ["GPSLatitude", "GPSLongitude"]
        },
        relevance_rules={}
    ),

    "generic_video": ContextProfile(
        context_type="generic_video",
        display_name="Video",
        description="Video file",
        ui_template="default_video",
        icon="video",
        color="slate",
        priority_fields=[
            "Duration", "VideoCodec", "AudioCodec", "Resolution",
            "FrameRate", "Bitrate", "Make", "Model"
        ],
        special_components=[
            "video_info_panel",
            "codec_details",
            "timeline_preview"
        ],
        field_groups={
            "Video": ["VideoCodec", "Resolution", "FrameRate", "Bitrate"],
            "Audio": ["AudioCodec", "AudioChannels", "SampleRate"],
            "File": ["Duration", "FileSize", "Format"],
            "Device": ["Make", "Model", "Software"]
        },
        relevance_rules={}
    ),

    "generic_document": ContextProfile(
        context_type="generic_document",
        display_name="Document",
        description="Document file (PDF, Office, etc.)",
        ui_template="default_document",
        icon="file-text",
        color="slate",
        priority_fields=[
            "Title", "Author", "Creator", "Producer", "CreationDate",
            "ModificationDate", "PageCount", "Subject"
        ],
        special_components=[
            "document_info_panel"
        ],
        field_groups={
            "Document": ["Title", "Subject", "Author", "Keywords"],
            "Creation": ["Creator", "Producer", "CreationDate"],
            "Modification": ["ModificationDate", "ModifyingApplication"],
            "Stats": ["PageCount", "WordCount", "CharacterCount"]
        },
        relevance_rules={}
    ),

    "generic_file": ContextProfile(
        context_type="generic_file",
        display_name="File",
        description="Generic file type",
        ui_template="default",
        icon="file",
        color="slate",
        priority_fields=[
            "FileName", "FileSize", "FileType", "MIMEType",
            "FileModifyDate", "FileAccessDate"
        ],
        special_components=[
            "file_info_panel"
        ],
        field_groups={
            "File": ["FileName", "FileSize", "FileType", "MIMEType"],
            "Dates": ["FileModifyDate", "FileAccessDate", "FileCreateDate"]
        },
        relevance_rules={}
    )
}


def get_profile_for_context(context_type: str) -> ContextProfile:
    """Get the profile for a given context type, with fallback to generic"""
    return CONTEXT_PROFILES.get(context_type, CONTEXT_PROFILES["generic_file"])


def get_all_contexts() -> List[str]:
    """Get list of all available context types"""
    return list(CONTEXT_PROFILES.keys())


def get_contexts_by_category() -> Dict[str, List[str]]:
    """Group contexts by category for UI display"""
    return {
        "Photography": [
            "smartphone_photo", "dslr_photo", "drone_photo", "action_camera_photo"
        ],
        "Specialized": [
            "dicom_medical", "astronomy_fits", "geospatial"
        ],
        "Content-Based": [
            "ai_generated", "edited_image", "screenshot"
        ],
        "Generic": [
            "generic_photo", "generic_video", "generic_document", "generic_file"
        ]
    }
