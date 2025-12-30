"""
Mobile/Smartphone Metadata Extraction
Apple iPhone, Android (Google Pixel, Samsung, Huawei, Xiaomi)
"""

import re
from typing import Dict, Any, Optional


APPLE_MAKERNOTE_TAGS = {
    # Device Info
    "Apple_RunTime_Flags": "apple_runtime_flags",
    "Apple_RunTime_Epoch": "apple_runtime_epoch",
    "Apple_RunTime_Scale": "apple_runtime_scale",
    "Apple_RunTime_Value": "apple_runtime_value",
    "Apple_Acceleration_Vector": "apple_acceleration_vector",
    "Apple_HDR_ImageType": "apple_hdr_image_type",
    "Apple_BurstUUID": "apple_burst_uuid",
    "Apple_ImageUniqueID": "apple_image_unique_id",
    "Apple_MediaGroupUUID": "apple_media_group_uuid",
    # Photo Features
    "Apple_LivePhoto": "apple_live_photo",
    "Apple_LivePhotoVideoIndex": "apple_live_photo_video_index",
    "Apple_ContentIdentifier": "apple_content_identifier",
    "Apple_ImageCaptureType": "apple_image_capture_type",
    "Apple_PhotoIdentifier": "apple_photo_identifier",
    # Portrait Mode
    "Apple_PortraitEffectStrength": "apple_portrait_effect_strength",
    "Apple_DepthData": "apple_depth_data",
    "Apple_FocusDistanceRange": "apple_focus_distance_range",
    "Apple_PortraitLightingEffectStrength": "apple_portrait_lighting_effect_strength",
    # Computational Photography
    "Apple_SemanticStyle": "apple_semantic_style",
    "Apple_SemanticStyleRenderingVersion": "apple_semantic_style_rendering_version",
    "Apple_SemanticStylePreset": "apple_semantic_style_preset",
    "Apple_SmartHDR": "apple_smart_hdr",
    "Apple_FrontFacingCamera": "apple_front_facing_camera",
    "Apple_AFConfidence": "apple_af_confidence",
    "Apple_SceneFlags": "apple_scene_flags",
    # Location/Motion
    "Apple_GPSHPositioningError": "apple_gps_horizontal_error",
    "Apple_RegionInfo": "apple_region_info",
    "Apple_DetectedFaces": "apple_detected_faces",
    "Apple_CameraOrientation": "apple_camera_orientation",
    # Video
    "Apple_VideoMetadata": "apple_video_metadata",
    "Apple_CinematicVideoEnabled": "apple_cinematic_video_enabled",
    "Apple_TemporalScalabilityEnabled": "apple_temporal_scalability_enabled",
    # ProRAW
    "Apple_ProRAW": "apple_pro_raw",
    "Apple_ColorMatrix": "apple_color_matrix",
    "Apple_MakerApple": "apple_maker_data",
}

ANDROID_TAGS = {
    # Device Info
    "Android_Manufacturer": "android_manufacturer",
    "Android_Model": "android_model",
    "Android_CaptureFPS": "android_capture_fps",
    "Android_HDR_Mode": "android_hdr_mode",
    # Photography Features
    "Android_NightSight": "android_night_sight",
    "Android_PortraitMode": "android_portrait_mode",
    "Android_PortraitBlurStrength": "android_portrait_blur_strength",
    "Android_DepthFormat": "android_depth_format",
    "Android_DepthNear": "android_depth_near",
    "Android_DepthFar": "android_depth_far",
    "Android_DepthMimeType": "android_depth_mime_type",
    # Motion Photo
    "Android_MotionPhoto": "android_motion_photo",
    "Android_MotionPhotoVersion": "android_motion_photo_version",
    "Android_MotionPhotoPresentationTimestampUs": "android_motion_photo_timestamp",
    # Special Modes
    "Android_TopShot": "android_top_shot",
    "Android_PhotoBoothSetting": "android_photo_booth_setting",
    # Google Specific
    "Google_DepthMap": "google_depth_map",
    "Google_Image": "google_image_metadata",
    "Google_DeviceName": "google_device_name",
}

SAMSUNG_TAGS = {
    "Samsung_ImageType": "samsung_image_type",
    "Samsung_DeviceName": "samsung_device_name",
    "Samsung_Processing": "samsung_processing",
    "Samsung_CustomRendered": "samsung_custom_rendered",
    "Samsung_ExposureProgram": "samsung_exposure_program",
    "Samsung_ISOSpeedRatings": "samsung_iso_speed_ratings",
    "Samsung_ExposureTime": "samsung_exposure_time",
    "Samsung_FNumber": "samsung_f_number",
    "Samsung_FocalLength": "samsung_focal_length",
    "Samsung_Flash": "samsung_flash",
    "Samsung_WhiteBalance": "samsung_white_balance",
    "Samsung_Orientation": "samsung_orientation",
    "Samsung_Width": "samsung_width",
    "Samsung_Height": "samsung_height",
    "Samsung_GPSLatitude": "samsung_gps_latitude",
    "Samsung_GPSLongitude": "samsung_gps_longitude",
}

HUAWEI_TAGS = {
    "Huawei_ImageType": "huawei_image_type",
    "Huawei_RecMode": "huawei_rec_mode",
    "Huawei_AFMode": "huawei_af_mode",
    "Huawei_FaceDetectMode": "huawei_face_detect_mode",
    "Huawei_AntiBanding": "huawei_anti_banding",
    "Huawei_EngineerMode": "huawei_engineer_mode",
    "Huawei_LensType": "huawei_lens_type",
    "Huawei_ColorCorrectionMode": "huawei_color_correction_mode",
    "Huawei_NoiseReductionMode": "huawei_noise_reduction_mode",
    "Huawei_FocusMode": "huawei_focus_mode",
    "Huawei_AE_Mode": "huawei_ae_mode",
    "Huawei_AF_Area_Mode": "huawei_af_area_mode",
    "Huawei_FlashMode": "huawei_flash_mode",
    "Huawei_WB_Mode": "huawei_wb_mode",
    "Huawei_PictureSize": "huawei_picture_size",
    "Huawei_ExposureTime": "huawei_exposure_time",
    "Huawei_FNumber": "huawei_f_number",
    "Huawei_ISO": "huawei_iso",
}

XIAOMI_TAGS = {
    "Xiaomi_ImageType": "xiaomi_image_type",
    "Xiaomi_FocalLength": "xiaomi_focal_length",
    "Xiaomi_SubjectDistance": "xiaomi_subject_distance",
    "Xiaomi_ExposureBias": "xiaomi_exposure_bias",
    "Xiaomi_FlashMode": "xiaomi_flash_mode",
    "Xiaomi_MeteringMode": "xiaomi_metering_mode",
    "Xiaomi_WhiteBalance": "xiaomi_white_balance",
    "Xiaomi_Sharpness": "xiaomi_sharpness",
    "Xiaomi_Contrast": "xiaomi_contrast",
    "Xiaomi_Saturation": "xiaomi_saturation",
    "Xiaomi_ISO": "xiaomi_iso",
    "Xiaomi_FNumber": "xiaomi_f_number",
    "Xiaomi_ExposureTime": "xiaomi_exposure_time",
}

GCAMERA_XMP_TAGS = {
    "MotionPhoto": "android_motion_photo",
    "MotionPhotoVersion": "android_motion_photo_version",
    "MotionPhotoPresentationTimestampUs": "android_motion_photo_timestamp",
    "MicroVideo": "android_micro_video",
    "MicroVideoVersion": "android_micro_video_version",
    "MicroVideoOffset": "android_micro_video_offset",
    "MicroVideoPresentationTimestampUs": "android_micro_video_timestamp",
    "MicroVideoPresentationDurationUs": "android_micro_video_duration",
    "PortraitMode": "android_portrait_mode",
    "PortraitBlurStrength": "android_portrait_blur_strength",
    "HdrPlusEnabled": "android_hdr_plus_enabled",
    "NightSight": "android_night_sight",
    "TopShot": "android_top_shot",
    "CaptureMode": "android_capture_mode",
}

GDEPTH_XMP_TAGS = {
    "Format": "android_depth_format",
    "Near": "android_depth_near",
    "Far": "android_depth_far",
    "Mime": "android_depth_mime_type",
    "Confidence": "android_depth_confidence",
    "Data": "android_depth_data",
}

GIMAGE_XMP_TAGS = {
    "Mime": "android_image_mime_type",
    "Data": "android_image_data",
}

GPANO_XMP_TAGS = {
    "ProjectionType": "android_panorama_projection_type",
    "UsePanoramaViewer": "android_panorama_viewer",
    "CroppedAreaImageWidthPixels": "android_panorama_cropped_width",
    "CroppedAreaImageHeightPixels": "android_panorama_cropped_height",
    "CroppedAreaLeftPixels": "android_panorama_cropped_left",
    "CroppedAreaTopPixels": "android_panorama_cropped_top",
    "FullPanoWidthPixels": "android_panorama_full_width",
    "FullPanoHeightPixels": "android_panorama_full_height",
    "InitialViewHeadingDegrees": "android_panorama_heading",
    "InitialViewPitchDegrees": "android_panorama_pitch",
    "InitialViewRollDegrees": "android_panorama_roll",
}


def extract_mobile_metadata(
    filepath: str,
    exiftool_data: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Extract mobile/smartphone-specific metadata.
    
    Args:
        filepath: Path to image file
        exiftool_data: Optional exiftool-based metadata for richer tags
    
    Returns:
        Dictionary with mobile metadata organized by vendor
    """
    result = {
        "mobile": {
            "apple": {},
            "android": {},
            "samsung": {},
            "huawei": {},
            "xiaomi": {}
        },
        "detection": {
            "is_mobile": False,
            "detected_vendors": [],
            "confidence": 0.0
        },
        "fields_extracted": 0
    }
    
    def normalize_tag(tag: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", tag.lower())

    def normalize_map(tag_map: Dict[str, str]) -> Dict[str, str]:
        return {normalize_tag(k): v for k, v in tag_map.items()}

    apple_map = normalize_map(APPLE_MAKERNOTE_TAGS)
    android_map = normalize_map(ANDROID_TAGS)
    samsung_map = normalize_map(SAMSUNG_TAGS)
    huawei_map = normalize_map(HUAWEI_TAGS)
    xiaomi_map = normalize_map(XIAOMI_TAGS)

    gcamera_map = normalize_map(GCAMERA_XMP_TAGS)
    gdepth_map = normalize_map(GDEPTH_XMP_TAGS)
    gimage_map = normalize_map(GIMAGE_XMP_TAGS)
    gpano_map = normalize_map(GPANO_XMP_TAGS)

    def apply_map(tag_map: Dict[str, str], tag: str, value: Any, vendor: str) -> bool:
        mapped = tag_map.get(normalize_tag(tag))
        if mapped:
            result["mobile"][vendor][mapped] = str(value)
            return True
        return False

    detected_any = False
    detected_vendors = set()

    try:
        if exiftool_data and any(exiftool_data.get(key) for key in ("exif", "xmp", "xmp_namespaces", "makernote")):
            exif_tags = exiftool_data.get("exif", {}) if isinstance(exiftool_data, dict) else {}
            makernote = exiftool_data.get("makernote", {}) if isinstance(exiftool_data, dict) else {}
            xmp_tags = exiftool_data.get("xmp", {}) if isinstance(exiftool_data, dict) else {}
            xmp_namespaces = exiftool_data.get("xmp_namespaces", {}) if isinstance(exiftool_data, dict) else {}

            if isinstance(makernote, dict):
                for vendor_key, fields in makernote.items():
                    if not isinstance(fields, dict):
                        continue
                    vendor = vendor_key.lower()
                    if vendor == "apple":
                        for tag, value in fields.items():
                            if apply_map(apple_map, tag, value, "apple"):
                                detected_any = True
                                detected_vendors.add("apple")
                    elif vendor == "samsung":
                        for tag, value in fields.items():
                            if apply_map(samsung_map, tag, value, "samsung"):
                                detected_any = True
                                detected_vendors.add("samsung")
                    elif vendor == "huawei":
                        for tag, value in fields.items():
                            if apply_map(huawei_map, tag, value, "huawei"):
                                detected_any = True
                                detected_vendors.add("huawei")
                    elif vendor == "xiaomi":
                        for tag, value in fields.items():
                            if apply_map(xiaomi_map, tag, value, "xiaomi"):
                                detected_any = True
                                detected_vendors.add("xiaomi")

            def apply_xmp_namespace(namespace_key: str, tag_map: Dict[str, str]) -> None:
                namespace = {}
                if isinstance(xmp_namespaces, dict):
                    namespace = xmp_namespaces.get(namespace_key, {})
                if isinstance(namespace, dict) and namespace:
                    for tag, value in namespace.items():
                        if apply_map(tag_map, tag, value, "android"):
                            detected_vendors.add("android")
                elif isinstance(xmp_tags, dict):
                    prefix = f"XMP-{namespace_key}:" if namespace_key != "gPano" else "XMP-GPano:"
                    if namespace_key == "gCamera":
                        prefix = "XMP-GCamera:"
                    elif namespace_key == "gDepth":
                        prefix = "XMP-GDepth:"
                    elif namespace_key == "gImage":
                        prefix = "XMP-GImage:"
                    elif namespace_key == "gPano":
                        prefix = "XMP-GPano:"
                    for key, value in xmp_tags.items():
                        if key.startswith(prefix):
                            tag = key.split(":", 1)[1]
                            if apply_map(tag_map, tag, value, "android"):
                                detected_vendors.add("android")

            apply_xmp_namespace("gCamera", gcamera_map)
            apply_xmp_namespace("gDepth", gdepth_map)
            apply_xmp_namespace("gImage", gimage_map)
            apply_xmp_namespace("gPano", gpano_map)

            if isinstance(xmp_tags, dict):
                for key, value in xmp_tags.items():
                    if apply_map(android_map, key, value, "android"):
                        detected_vendors.add("android")
                    elif apply_map(samsung_map, key, value, "samsung"):
                        detected_vendors.add("samsung")
                    elif apply_map(huawei_map, key, value, "huawei"):
                        detected_vendors.add("huawei")
                    elif apply_map(xiaomi_map, key, value, "xiaomi"):
                        detected_vendors.add("xiaomi")

            if detected_vendors:
                detected_any = True

            if isinstance(exif_tags, dict):
                make_value = exif_tags.get("Make") or exif_tags.get("CameraMake") or ""
                make_lower = str(make_value).lower()
                if "apple" in make_lower or "iphone" in make_lower:
                    detected_vendors.add("apple")
                if "samsung" in make_lower:
                    detected_vendors.add("samsung")
                if "huawei" in make_lower:
                    detected_vendors.add("huawei")
                if "xiaomi" in make_lower:
                    detected_vendors.add("xiaomi")
                if "google" in make_lower or "pixel" in make_lower or "android" in make_lower:
                    detected_vendors.add("android")
        else:
            from .exif import extract_exif_metadata
            exif_data = extract_exif_metadata(filepath)

            if not exif_data or "error" in exif_data:
                return result

            all_tags = {}
            for category in ["image", "photo", "gps", "interoperability"]:
                if category in exif_data and isinstance(exif_data[category], dict):
                    all_tags.update(exif_data[category])

            for tag, value in all_tags.items():
                tag_str = str(tag)
                if apply_map(apple_map, tag_str, value, "apple"):
                    detected_vendors.add("apple")
                    detected_any = True
                elif apply_map(android_map, tag_str, value, "android"):
                    detected_vendors.add("android")
                    detected_any = True
                elif apply_map(samsung_map, tag_str, value, "samsung"):
                    detected_vendors.add("samsung")
                    detected_any = True
                elif apply_map(huawei_map, tag_str, value, "huawei"):
                    detected_vendors.add("huawei")
                    detected_any = True
                elif apply_map(xiaomi_map, tag_str, value, "xiaomi"):
                    detected_vendors.add("xiaomi")
                    detected_any = True

        if detected_any or detected_vendors:
            result["detection"]["is_mobile"] = True
            vendors = sorted(detected_vendors)
            result["detection"]["detected_vendors"] = vendors
            result["detection"]["confidence"] = min(1.0, max(1, len(vendors)) / 3.0)

        total_fields = (
            len(result["mobile"]["apple"]) +
            len(result["mobile"]["android"]) +
            len(result["mobile"]["samsung"]) +
            len(result["mobile"]["huawei"]) +
            len(result["mobile"]["xiaomi"])
        )
        result["fields_extracted"] = total_fields

        return result

    except Exception as e:
        return {"error": f"Failed to extract mobile metadata: {str(e)}"}


def detect_apple_live_photo(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Detect and extract Apple Live Photo metadata.
    
    Args:
        filepath: Path to image file
    
    Returns:
        Dictionary with Live Photo information
    """
    result = {
        "is_live_photo": False,
        "has_video": False,
        "video_index": None,
        "content_identifier": None,
        "burst_group": None
    }
    
    try:
        from .exif import extract_exif_metadata
        exif_data = extract_exif_metadata(filepath)
        
        if not exif_data or "error" in exif_data:
            return result
        
        photo = exif_data.get("photo", {})
        
        if photo.get("apple_live_photo", "").lower() in ["true", "yes", "1"]:
            result["is_live_photo"] = True
            
            video_index = photo.get("apple_live_photo_video_index")
            if video_index:
                result["video_index"] = int(video_index)
                result["has_video"] = True
            
            content_id = photo.get("apple_content_identifier")
            if content_id:
                result["content_identifier"] = str(content_id)
            
            burst_uuid = photo.get("apple_burst_uuid")
            if burst_uuid:
                result["burst_group"] = str(burst_uuid)
        
        return result
        
    except Exception as e:
        return result


def detect_portrait_mode(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Detect portrait mode and depth data.
    
    Args:
        filepath: Path to image file
    
    Returns:
        Dictionary with portrait mode information
    """
    result = {
        "is_portrait_mode": False,
        "has_depth_data": False,
        "portrait_strength": None,
        "lighting_effect": None,
        "focus_distance_range": None
    }
    
    try:
        from .exif import extract_exif_metadata
        exif_data = extract_exif_metadata(filepath)
        
        if not exif_data or "error" in exif_data:
            return result
        
        photo = exif_data.get("photo", {})
        
        portrait_strength = photo.get("apple_portrait_effect_strength")
        if portrait_strength:
            try:
                result["portrait_strength"] = float(portrait_strength)
                result["is_portrait_mode"] = True
            except ValueError:
                pass
        
        depth_data = photo.get("apple_depth_data")
        if depth_data and depth_data.lower() in ["true", "yes", "1"]:
            result["has_depth_data"] = True
        
        lighting = photo.get("apple_portrait_lighting_effect_strength")
        if lighting:
            try:
                result["lighting_effect"] = float(lighting)
            except ValueError:
                pass
        
        focus_range = photo.get("apple_focus_distance_range")
        if focus_range:
            result["focus_distance_range"] = str(focus_range)
        
        android_portrait = photo.get("android_portrait_mode")
        if android_portrait and android_portrait.lower() in ["true", "yes", "1"]:
            result["is_portrait_mode"] = True
        
        return result
        
    except Exception as e:
        return result


def get_mobile_field_count() -> int:
    """Return approximate number of mobile fields."""
    return 110
