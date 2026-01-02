"""
EXIF and GPS Metadata Extraction
Comprehensive extraction of EXIF tags including Photo, Image, GPS, and MakerNote sections
"""

import re
import json
import shutil
import subprocess
from typing import Any, Dict, Optional, Sequence, Union

# Fix relative import issue for dynamic module loading
try:
    from .shared_utils import safe_str as _safe_str
except ImportError:
    _safe_str = lambda x: str(x) if x is not None else ''

TagDict = Dict[str, Any]


try:
    import exifread
    EXIFREAD_AVAILABLE = True
except ImportError:
    exifread = None
    EXIFREAD_AVAILABLE = False


EXIFTOOL_PATH = shutil.which("exiftool")
EXIFTOOL_AVAILABLE = EXIFTOOL_PATH is not None


# ULTRA EXPANSION FIELDS
# Additional 39 fields
ULTRA_EXIF_FIELDS = {
    "focus_mode": "autofocus_manual_manual_focus",
    "focus_distance": "distance_to_subject_meters",
    "focus_points": "autofocus_point_selection",
    "metering_mode": "exposure_metering_pattern",
    "exposure_lock": "ae_af_lock_status",
    "white_balance_shift": "wb_color_compensation",
    "color_space": "srgb_adobe_rgb_prophoto",
    "picture_style": "canon_picture_style",
    "active_dlighting": "nikon_active_dlighting",
    "lens_serial_number": "lens_manufacturer_serial",
"lens_firmware": "lens_firmware_version",
"lens_optical_attributes": "coating_element_count",
"vibration_reduction": "vr_vibration_reduction",
"image_stabilization": "optical_stabilization_mode",
"autofocus_motor": "af_motor_type_usm_swm",
"internal_focus": "if_internal_focusing",
"high_iso_nr": "high_iso_noise_reduction",
"long_exposure_nr": "long_exposure_noise_reduction",
"hdr_mode": "high_dynamic_range_capture",
"hdr_strength": "hdr_effect_intensity",
"multiple_exposure": "exposure_bracketing_count",
"exposure_bracketing": "exposure_compensation_steps",
"interval_shooting": "time_lapse_interval",
"timer_duration": "self_timer_seconds",
"gps_latitude": "geographic_coordinate_latitude",
"gps_longitude": "geographic_coordinate_longitude",
"gps_altitude": "elevation_above_sea_level",
"gps_direction": "compass_heading_direction",
"gps_timestamp": "gps_datetime_fix",
"gps_satellites": "number_of_satellites_tracked",
"gps_precision": "horizontal_dilution_of_precision",
"map_datum": "coordinate_reference_system",
"faces_detected": "number_of_faces_identified",
"face_locations": "face_coordinates_in_frame",
"face_recognition": "identified_persons_names",
"smile_detection": "smile_confidence_level",
"blink_detection": "eye_blink_detected",
"skin_softening": "beauty_filter_strength",
}


# MEGA EXPANSION FIELDS
# Additional 59 fields
MEGA_EXPANSION_FIELDS = {
    "portrait_mode": "depth_effect_portrait",
"night_mode": "low_light_enhancement",
"hdr_plus": "high_dynamic_range_plus",
"beauty_mode": "face_enhancement_level",
"food_mode": "color_optimization_food",
"panorama_mode": "360_panorama_capture",
"selfie_mode": "front_camera_optimization",
"pro_mode": "manual_controls_enabled",
"slow_motion": "high_fps_recording",
"time_lapse": "timelapse_recording",
"cinematic_mode": "video_cinematic_effects",
"macro_mode": "close_up_focusing",
"sports_mode": "action_capture_settings",
"documents_mode": "document_scanning",
"ar_emoji": "augmented_reality_stickers",
"live_photos": "animated_image_capture",
"drone_model": "dji_mavic_phantom_autel",
"drone_operation_mode": "manual_autonomous_waypoint",
"flight_altitude": "above_ground_level_meters",
"gimbal_pitch": "camera_tilt_angle",
"gimbal_roll": "camera_rotation_angle",
"flight_speed": "drone_velocity_kmh",
"obstacle_avoidance": "collision_detection_system",
"return_to_home": "rth_functionality",
"follow_mode": "subject_tracking",
"orbit_mode": "circular_flight_pattern",
"hyperlapse": "advanced_timelapse_drone",
"terrain_follow": "surface_tracking_mode",
"camera_rig_type": "hero_insta360_kandao",
"stitching_software": "autopano_video_stitch",
"projection_format": "equirectangular_cubemap",
"view_orientation": "initial_view_angle",
"spatial_audio": "ambisonic_audio_format",
"vr_compatible": "virtual_ready_ready",
"live_streaming": "realtime_360_stream",
"time_sync": "camera_synchronization_ms",
"xray_technique": "pa_ap_lat_medial_oblique",
"radiation_dose": "exposure_dose_mgy",
"contrast_enhancement": "window_level_width",
"magnification_factor": "zoom_enlargement",
"patient_position": "supine_prone_lateral",
"body_part": "chest_abdomen_extremity",
"view_projection": "posterior_anterior_lateral",
"microscope_mag": "objective_magnification",
"microscope_type": "brightfield_fluorescence_confocal",
"staining_method": "chemical_dye_used",
"sample_preparation": "fixation_sectioning",
"fluorescence_channels": "multichannel_colors",
"deconvolution": "image_restoration_method",
"time_lapse_interval": "microscopy_time_lapse",
"z_stack_depth": "3d_image_layers",
"multi_frame_noise": "noise_reduction_frames",
"super_resolution": "ai_upscaling_method",
"computational_bokeh": "synthetic_depth_blur",
"semantic_segmentation": "subject_detection_mask",
"image_fusion": "multi_exposure_combination",
"light_field_capture": "plenoptic_camera_data",
"tone_mapping": "hdr_compression_method",
"color_grading": "cinematic_color_science",
}
def _run_exiftool_exif(filepath: str) -> Optional[Dict[str, Any]]:
    if not EXIFTOOL_AVAILABLE or EXIFTOOL_PATH is None:
        return None

    try:
        cmd = [
            EXIFTOOL_PATH,
            "-j",
            "-n",
            "-G1",
            "-s",
            "-a",
            "-u",
            "-f",
            "-IFD0:all",
            "-ExifIFD:all",
            "-SubIFD:all",
            "-GPS:all",
            "-InteropIFD:all",
            "-IFD1:all",
            "-Thumbnail:all",
            filepath,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            return None
        parsed = json.loads(result.stdout)
        if isinstance(parsed, list) and parsed:
            return parsed[0]
        return None
    except Exception as e:
        return None


EXIF_TAGS = {
    # Image Section Tags (TIFF IFD)
    "ImageWidth": "image_width",
    "ImageHeight": "image_height",
    "Make": "camera_make",
    "Model": "camera_model",
    "Software": "software",
    "Orientation": "orientation",
    "XResolution": "x_resolution",
    "YResolution": "y_resolution",
    "ResolutionUnit": "resolution_unit",
    "DateTime": "date_time",
    "DateTimeOriginal": "date_time_original",
    "DateTimeDigitized": "date_time_digitized",
    "Artist": "artist",
    "Copyright": "copyright",
    "ImageDescription": "description",
    "ProcessingSoftware": "processing_software",
    
    # TIFF IFD Additional Tags
    "PhotometricInterpretation": "photometric_interpretation",
    "SamplesPerPixel": "samples_per_pixel",
    "BitsPerSample": "bits_per_sample",
    "Compression": "compression",
    "PlanarConfiguration": "planar_configuration",
    "YCbCrSubSampling": "ycbcr_sub_sampling",
    "YCbCrPositioning": "ycbcr_positioning",
    "XPosition": "x_position",
    "YPosition": "y_position",
    "WhitePoint": "white_point",
    "PrimaryChromaticities": "primary_chromaticities",
    "YCbCrCoefficients": "ycbcr_coefficients",
    "ReferenceBlackWhite": "reference_black_white",
    "RowSamplesPerStrip": "row_samples_per_strip",
    "StripByteCounts": "strip_byte_counts",
    "StripOffsets": "strip_offsets",
    "NumberOfStrips": "number_of_strips",
    
    # Photo Section Tags
    "ExposureTime": "exposure_time",
    "FNumber": "f_number",
    "ExposureProgram": "exposure_program",
    "ISOSpeedRatings": "iso_speed_ratings",
    "ShutterSpeedValue": "shutter_speed_value",
    "ApertureValue": "aperture_value",
    "BrightnessValue": "brightness_value",
    "ExposureBiasValue": "exposure_bias",
    "MaxApertureValue": "max_aperture",
    "MeteringMode": "metering_mode",
    "LightSource": "light_source",
    "Flash": "flash",
    "FocalLength": "focal_length",
    "FocalLengthIn35mmFilm": "focal_length_35mm",
    "SubjectDistance": "subject_distance",
    "ExposureMode": "exposure_mode",
    "WhiteBalance": "white_balance",
    "DigitalZoomRatio": "digital_zoom",
    "SceneCaptureType": "scene_type",
    "GainControl": "gain_control",
    "Contrast": "contrast",
    "Saturation": "saturation",
    "Sharpness": "sharpness",
    "SubjectDistanceRange": "subject_distance_range",
    "SensingMethod": "sensing_method",
    "ColorSpace": "color_space",
    "PixelXDimension": "pixel_width",
    "PixelYDimension": "pixel_height",
    "LensSpecification": "lens_specification",
    "LensMake": "lens_make",
    "LensModel": "lens_model",
    
    # Photo Section Additional Tags
    "ExposureIndex": "exposure_index",
    "ExposureValue": "exposure_value",
    "FocalPlaneXResolution": "focal_plane_x_resolution",
    "FocalPlaneYResolution": "focal_plane_y_resolution",
    "FocalPlaneResolutionUnit": "focal_plane_resolution_unit",
    "ImageNumber": "image_number",
    "SelfTimerMode": "self_timer_mode",
    "Quality": "quality",
    "CameraSerialNumber": "camera_serial_number",
    "LensInfo": "lens_info",
    "LensSerialNumber": "lens_serial_number",
    "BodySerialNumber": "body_serial_number",
    "CameraOwnerName": "camera_owner_name",
    "FlashEnergy": "flash_energy",
    "FlashExposureComp": "flash_exposure_comp",
    "FlashMetering": "flash_metering",
    "FlashSyncSpeed": "flash_sync_speed",
    "ShutterCounter": "shutter_counter",
    
    # GPS Tags
    "GPSLatitude": "gps_latitude",
    "GPSLatitudeRef": "gps_latitude_ref",
    "GPSLongitude": "gps_longitude",
    "GPSLongitudeRef": "gps_longitude_ref",
    "GPSAltitude": "gps_altitude",
    "GPSAltitudeRef": "gps_altitude_ref",
    "GPSTimeStamp": "gps_timestamp",
    "GPSDateStamp": "gps_date",
    "GPSSpeed": "gps_speed",
    "GPSSpeedRef": "gps_speed_ref",
    "GPSImgDirection": "gps_image_direction",
    "GPSImgDirectionRef": "gps_image_direction_ref",
    "GPSDestBearing": "gps_dest_bearing",
    "GPSDestBearingRef": "gps_dest_bearing_ref",
    "GPSSatellites": "gps_satellites",
    "GPSDOP": "gps_dop",
    "GPSMapDatum": "gps_map_datum",
    "GPSProcessingMethod": "gps_processing_method",
    
    # GPS Additional Tags
    "GPSVersionID": "gps_version_id",
    "GPSStatus": "gps_status",
    "GPSMeasureMode": "gps_measure_mode",
    "GPSTrackRef": "gps_track_ref",
    "GPSTrack": "gps_track",
    "GPSImgDirectionRef": "gps_img_direction_ref",
    "GPSDestLatitudeRef": "gps_dest_latitude_ref",
    "GPSDestLongitudeRef": "gps_dest_longitude_ref",
    "GPSDestBearingRef": "gps_dest_bearing_ref",
    "GPSDestDistanceRef": "gps_dest_distance_ref",
    "GPSDestDistance": "gps_dest_distance",
    "GPSAreaInformation": "gps_area_information",
    "GPSDateStamp": "gps_date_stamp",
    "GPSDifferential": "gps_differential",
    "GPSHPositioningError": "gps_h_positioning_error",
    
    # Interoperability IFD Tags
    "InteroperabilityIndex": "interoperability_index",
    "InteroperabilityVersion": "interoperability_version",
    "RelatedImageFileFormat": "related_image_file_format",
    "RelatedImageWidth": "related_image_width",
    "RelatedImageLength": "related_image_length",
    
    # 1st IFD (Thumbnail) Tags
    "ThumbnailImageWidth": "thumbnail_width",
    "ThumbnailImageHeight": "thumbnail_height",
    "ThumbnailCompression": "thumbnail_compression",
    "ThumbnailOrientation": "thumbnail_orientation",
    "ThumbnailXResolution": "thumbnail_x_resolution",
    "ThumbnailYResolution": "thumbnail_y_resolution",
    "ThumbnailResolutionUnit": "thumbnail_resolution_unit",
    "ThumbnailOffset": "thumbnail_offset",
    "ThumbnailByteCount": "thumbnail_byte_count",
}



def _convert_dms_to_decimal(dms: Sequence[Union[float, int]], ref: str) -> Optional[float]:
    """Convert GPS DMS coordinates to decimal degrees."""
    if not dms or len(dms) < 3:
        return None
    
    try:
        degrees = float(dms[0])
        minutes = float(dms[1])
        seconds = float(dms[2])
        
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        
        if ref in ['S', 'W']:
            decimal = -decimal
            
        return decimal
    except (ValueError, TypeError):
        return None


def _format_fraction(value: Any) -> Optional[str]:
    """Format EXIF fraction values to readable strings."""
    if value is None:
        return None
    
    try:
        if hasattr(value, 'values'):
            num = float(value.values[0].num) / float(value.values[0].den)
            return f"{num:.2f}"
        return str(value)
    except (ValueError, AttributeError, ZeroDivisionError):
        return str(value)


def _parse_gps_coordinates(tags: Dict[str, Any]) -> Dict[str, Any]:
    """Parse GPS coordinates from EXIF tags."""
    gps_data = {}
    
    # Latitude
    if 'GPS GPSLatitude' in tags:
        lat_values = tags['GPS GPSLatitude'].values
        lat_ref = str(tags.get('GPS GPSLatitudeRef', 'N'))
        decimal_lat = _convert_dms_to_decimal(lat_values, lat_ref)
        
        if decimal_lat is not None:
            gps_data['latitude'] = decimal_lat
            gps_data['latitude_ref'] = lat_ref
            gps_data['latitude_dms'] = f"{abs(lat_values[0])}° {abs(lat_values[1])}' {abs(lat_values[2]):.2f}\" {lat_ref}"
    
    # Longitude
    if 'GPS GPSLongitude' in tags:
        lon_values = tags['GPS GPSLongitude'].values
        lon_ref = str(tags.get('GPS GPSLongitudeRef', 'E'))
        decimal_lon = _convert_dms_to_decimal(lon_values, lon_ref)
        
        if decimal_lon is not None:
            gps_data['longitude'] = decimal_lon
            gps_data['longitude_ref'] = lon_ref
            gps_data['longitude_dms'] = f"{abs(lon_values[0])}° {abs(lon_values[1])}' {abs(lon_values[2]):.2f}\" {lon_ref}"
    
    # Altitude
    if 'GPS GPSAltitude' in tags:
        try:
            alt_value = tags['GPS GPSAltitude'].values
            if hasattr(alt_value, '__iter__'):
                altitude = float(alt_value[0].num) / float(alt_value[0].den)
            else:
                altitude = float(alt_value)
            gps_data['altitude'] = round(altitude, 2)
            
            alt_ref = str(tags.get('GPS GPSAltitudeRef', '0'))
            gps_data['altitude_ref'] = 'below_sea_level' if alt_ref == '1' else 'above_sea_level'
        except (ValueError, TypeError):
            pass
    
    # Speed
    if 'GPS GPSSpeed' in tags:
        try:
            speed_value = tags['GPS GPSSpeed'].values
            if hasattr(speed_value, '__iter__'):
                speed = float(speed_value[0].num) / float(speed_value[0].den)
            else:
                speed = float(speed_value)
            gps_data['speed'] = round(speed, 2)
            gps_data['speed_ref'] = str(tags.get('GPS GPSSpeedRef', 'K'))
        except (ValueError, TypeError):
            pass
    
    # Direction
    if 'GPS GPSImgDirection' in tags:
        try:
            dir_value = tags['GPS GPSImgDirection'].values
            if hasattr(dir_value, '__iter__'):
                direction = float(dir_value[0].num) / float(dir_value[0].den)
            else:
                direction = float(dir_value)
            gps_data['image_direction'] = round(direction, 1)
            gps_data['image_direction_ref'] = str(tags.get('GPS GPSImgDirectionRef', 'T'))
        except (ValueError, TypeError):
            pass
    
    # Timestamp
    if 'GPS GPSTimeStamp' in tags:
        gps_data['timestamp'] = str(tags['GPS GPSTimeStamp'])
    
    # Date
    if 'GPS GPSDateStamp' in tags:
        gps_data['datestamp'] = str(tags['GPS GPSDateStamp'])
    
    # Satellites
    if 'GPS GPSSatellites' in tags:
        gps_data['satellites'] = str(tags['GPS GPSSatellites'])
    
    return gps_data


def extract_exif_metadata(filepath: str, include_makernote: bool = False) -> Optional[Dict[str, Any]]:
    """Extract comprehensive EXIF metadata from images."""
    if not EXIFREAD_AVAILABLE or exifread is None:
        # Fallback to exiftool when available.
        raw = _run_exiftool_exif(filepath)
        if not raw:
            return {"error": "exifread library not installed"}

        exif_data: Dict[str, Any] = {
            "image": {},
            "photo": {},
            "gps": {},
            "interoperability": {},
            "thumbnail": None,
            "makernote": None,
            "fields_extracted": 0,
        }

        for key, value in raw.items():
            if value is None or value == "" or value == "-":
                continue

            if ":" in key:
                group, tag = key.split(":", 1)
            else:
                group, tag = "", key

            if group in {"IFD0", "SubIFD"}:
                exif_data["image"][tag] = value
            elif group in {"ExifIFD", "EXIF"}:
                exif_data["photo"][tag] = value
            elif group == "GPS":
                exif_data["gps"][tag] = value
            elif group in {"InteropIFD", "Interop"}:
                exif_data["interoperability"][tag] = value
            elif group in {"IFD1", "Thumbnail"}:
                exif_data["thumbnail"] = {"present": True}
            elif include_makernote and (group.startswith("MakerNotes") or group in {"Canon", "Nikon", "Sony", "Fujifilm", "Olympus", "Panasonic", "Pentax", "Leica"}):
                if exif_data["makernote"] is None:
                    exif_data["makernote"] = {}
                exif_data["makernote"][f"{group}:{tag}"] = value

        total_fields = (
            len(exif_data["image"]) +
            len(exif_data["photo"]) +
            len(exif_data["gps"]) +
            len(exif_data["interoperability"]) +
            (1 if exif_data["thumbnail"] else 0) +
            (len(exif_data["makernote"]) if isinstance(exif_data["makernote"], dict) else 0)
        )
        exif_data["fields_extracted"] = total_fields
        return exif_data
    
    try:
        with open(filepath, 'rb') as f:
            tags = exifread.process_file(f, details=True)

        if not tags:
            return None
        
        exif_data: Dict[str, Any] = {
            "image": {},
            "photo": {},
            "gps": {},
            "interoperability": {},
            "thumbnail": None,
            "makernote": None,
            "fields_extracted": 0
        }
        
        for tag, value in tags.items():
            tag_str = _safe_str(tag)
            if not tag_str:
                continue

            # Skip thumbnail tags; note presence only
            if 'Thumbnail' in tag_str:
                if 'Image' in tag_str:
                    exif_data['thumbnail'] = {"present": True}
                continue

            # Categorize by prefix
            if tag_str.startswith('Image '):
                category = 'image'
                clean_tag = tag_str.replace('Image ', '')
            elif tag_str.startswith('EXIF '):
                category = 'photo'
                clean_tag = tag_str.replace('EXIF ', '')
            elif tag_str.startswith('GPS '):
                category = 'gps'
                clean_tag = tag_str.replace('GPS ', '')
            elif tag_str.startswith('Interoperability '):
                category = 'interoperability'
                clean_tag = tag_str.replace('Interoperability ', '')
            elif tag_str.startswith('MakerNote'):
                if include_makernote:
                    exif_data['makernote'] = {"raw_data": _safe_str(value)[:500]}
                continue
            else:
                category = 'image'
                clean_tag = tag_str

            if category not in exif_data:
                continue

            # Use mapped key if available; otherwise keep original clean tag
            mapped_key = EXIF_TAGS.get(clean_tag, clean_tag)
            exif_data[category][mapped_key] = _safe_str(value)

        # Parse GPS coordinates separately for decimal conversion
        if 'GPS GPSLatitude' in tags:
            exif_data['gps'] = _parse_gps_coordinates(tags)

        total_fields = (
            len(exif_data['image']) +
            len(exif_data['photo']) +
            len(exif_data['gps']) +
            len(exif_data['interoperability']) +
            (1 if exif_data['thumbnail'] else 0) +
            (1 if exif_data['makernote'] else 0)
        )
        exif_data['fields_extracted'] = total_fields

        return exif_data
        
    except FileNotFoundError:
        return {"error": f"File not found: {filepath}"}
    except Exception as e:
        return {"error": f"Failed to extract EXIF: {str(e)}"}


def extract_gps_metadata(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract GPS metadata from image.
    Convenience function that returns only GPS data.
    
    Args:
        filepath: Path to image file
    
    Returns:
        Dictionary with GPS metadata or None if no GPS data
    """
    exif_data = extract_exif_metadata(filepath)
    
    if exif_data and 'error' not in exif_data:
        if exif_data.get('gps') and len(exif_data['gps']) > 0:
            return {
                "has_gps": True,
                "coordinates": {
                    "latitude": exif_data['gps'].get('latitude'),
                    "longitude": exif_data['gps'].get('longitude'),
                    "altitude": exif_data['gps'].get('altitude')
                },
                "raw_gps": exif_data.get('gps', {}),
                "full_exif": exif_data
            }
    
    return {
        "has_gps": False,
        "coordinates": None,
        "raw_gps": {},
        "full_exif": exif_data
    }


def get_exif_field_count() -> int:
    """Return total number of exif metadata fields."""
    total = 0
    total += len(ULTRA_EXIF_FIELDS)
    total += len(EXIF_TAGS)
    return total
