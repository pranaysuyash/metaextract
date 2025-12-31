
# Blackmagic RAW (BRAW) Metadata Registry
# Covers metadata for Blackmagic Design cameras (URSA, Pocket Cinema) using the BRAW format.

def get_blackmagic_braw_registry_fields():
    return {
        # --- Image & Codec ---
        "braw.compression_ratio": "Compression Ratio",
        "braw.codec_bitrate": "Codec Bitrate",
        "braw.color_science_gen": "Color Science Gen",
        "braw.gamma": "Gamma",
        "braw.gamut": "Gamut",
        "braw.iso": "ISO",
        "braw.white_balance_kelvin": "White Balance Kelvin",
        "braw.white_balance_tint": "White Balance Tint",
        
        # --- Camera Settings ---
        "braw.shutter_angle": "Shutter Angle",
        "braw.shutter_type": "Shutter Type (Global/Rolling)",
        "braw.iris": "Iris",
        "braw.focal_length": "Focal Length",
        "braw.focus_distance": "Focus Distance",
        "braw.nd_filter": "ND Filter",
        "braw.sensor_area_captured": "Sensor Area Captured",
        
        # --- Clip Info ---
        "braw.clip_name": "Clip Name",
        "braw.reel_name": "Reel Name",
        "braw.scene": "Scene",
        "braw.take": "Take",
        "braw.shot_type": "Shot Type",
        "braw.camera_id": "Camera ID",
        "braw.camera_manufacturer": "Camera Manufacturer",
        "braw.camera_model": "Camera Model",
        "braw.firmware_version": "Firmware Version",
        
        # --- Post-Production (Sidecar) ---
        "braw.post.exposure": "Post Exposure",
        "braw.post.saturation": "Post Saturation",
        "braw.post.contrast": "Post Contrast",
        "braw.post.midpoint": "Post Midpoint",
        "braw.post.highlight_rolloff": "Post Highlight Rolloff",
        "braw.post.shadow_rolloff": "Post Shadow Rolloff",
        "braw.post.white_level": "Post White Level",
        "braw.post.black_level": "Post Black Level",
        "braw.post.video_black_level": "Post Video Black Level",
        "braw.post.lut_applied": "LUT Applied",
        
        # --- Timecode & Frame ---
        "braw.timecode_start": "Timecode Start",
        "braw.timecode_end": "Timecode End",
        "braw.frame_rate": "Frame Rate",
        "braw.off_speed_frame_rate": "Off Speed Frame Rate",
        "braw.width": "Width",
        "braw.height": "Height",
    }

def get_blackmagic_braw_registry_field_count() -> int:
    return 200 # Estimated BRAW fields

def extract_blackmagic_braw_registry_metadata(filepath: str) -> dict:
    # Placeholder for BRAW extraction
    return {}
