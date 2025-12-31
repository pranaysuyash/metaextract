
# ARRI RAW Metadata Registry
# Covers metadata for ARRI Alexa, Amira, and Mini cameras (ARI, ARX, MXF).
# Based on ARRI SMPTE RDD 32 and manufacturer documentation.

def get_arri_raw_registry_fields():
    return {
        # --- Exposure & Color ---
        "arri.exposure_index": "Exposure Index (EI)",
        "arri.white_balance_kelvin": "White Balance (Kelvin)",
        "arri.white_balance_tint": "White Balance (Tint)",
        "arri.shutter_angle": "Shutter Angle",
        "arri.shutter_speed": "Shutter Speed",
        "arri.neutral_density_filter": "ND Filter",
        "arri.look_name": "Look Name",
        "arri.look_filename": "Look File Name",
        "arri.cdl.sop": "CDL SOP",
        "arri.cdl.saturation": "CDL Saturation",
        "arri.lut_3d_file": "3D LUT File",
        "arri.color_space": "Color Space",
        
        # --- Camera Info ---
        "arri.camera_model": "Camera Model",
        "arri.camera_serial": "Camera Serial Number",
        "arri.camera_id": "Camera ID",
        "arri.camera_clip_name": "Clip Name",
        "arri.reel_name": "Reel Name",
        "arri.recording_date": "Recording Date",
        "arri.recording_time": "Recording Time",
        "arri.system_version": "System Version",
        "arri.sensor_fps": "Sensor FPS",
        "arri.project_fps": "Project FPS",
        "arri.master_status": "Master/Slave Status",
        
        # --- Lens Data System (LDS) ---
        "arri.lens.model": "Lens Model",
        "arri.lens.serial": "Lens Serial Number",
        "arri.lens.focal_length": "Focal Length",
        "arri.lens.focus_distance": "Focus Distance",
        "arri.lens.iris": "Iris (T-Stop)",
        "arri.lens.entrance_pupil": "Entrance Pupil",
        "arri.lens.linear_iris": "Linear Iris",
        "arri.lens.squeeze_factor": "Lens Squeeze Factor",
        
        # --- System & Media ---
        "arri.media.serial": "Media Serial Number",
        "arri.media.uuid": "Media UUID",
        "arri.uuid": "Clip UUID",
        "arri.production.company": "Production Company",
        "arri.production.director": "Director",
        "arri.production.cinematographer": "Cinematographer",
        "arri.production.location": "Location",
        "arri.scene": "Scene",
        "arri.take": "Take",
        
        # --- Image Content ---
        "arri.image.width": "Image Width",
        "arri.image.height": "Image Height",
        "arri.image.orientation": "Image Orientation",
        "arri.image.aspect_ratio": "Aspect Ratio",
        "arri.tilt_angle": "Tilt Angle",
        "arri.roll_angle": "Roll Angle",
        
        # --- Sound ---
        "arri.sound.scene": "Sound Scene",
        "arri.sound.take": "Sound Take",
        "arri.sound.roll": "Sound Roll",
    }

def get_arri_raw_registry_field_count() -> int:
    return 300 # Estimated ARRI fields

def extract_arri_raw_registry_metadata(filepath: str) -> dict:
    # Placeholder for ARRI RAW extraction logic
    return {}
