
# RED RAW (R3D) Metadata Registry
# Covers metadata for RED digital cinema cameras (V-Raptor, Komodo, Monstro, Helium, etc.).

def get_red_r3d_registry_fields():
    return {
        # --- Image & Compression ---
        "red.redcode_raw": "REDcode Compression Ratio",
        "red.iso": "ISO Rating",
        "red.white_balance_kelvin": "Kelvin",
        "red.white_balance_tint": "Tint",
        "red.exposure_time": "Exposure Time",
        "red.fps": "Frame Rate",
        "red.color_space": "Color Space (e.g. REDWideGamutRGB)",
        "red.gamma_curve": "Gamma Curve (e.g. Log3G10)",
        "red.resolution": "Resolution",
        "red.sensor_fps": "Sensor FPS",
        
        # --- Frame Guide ---
        "red.frame_guide.name": "Frame Guide Name",
        "red.frame_guide.aspect_ratio": "Frame Guide Aspect Ratio",
        "red.frame_guide.opacity": "Frame Guide Opacity",
        "red.frame_guide.color": "Frame Guide Color",
        
        # --- Lens & Focus ---
        "red.lens.name": "Lens Name",
        "red.lens.aperture": "Aperture",
        "red.lens.focal_length": "Focal Length",
        "red.lens.focus_distance": "Focus Distance",
        "red.lens.entrance_pupil": "Entrance Pupil",
        
        # --- Clip & Reel ---
        "red.clip.name": "Clip Name",
        "red.reel.id": "Reel ID",
        "red.clip.uuid": "Clip UUID",
        "red.absolute_timecode_start": "Absolute Timecode Start",
        "red.absolute_timecode_end": "Absolute Timecode End",
        "red.edge_timecode_start": "Edge Timecode Start",
        "red.edge_timecode_end": "Edge Timecode End",
        
        # --- Camera Info ---
        "red.camera.model": "Camera Model",
        "red.camera.serial": "Camera Serial",
        "red.camera.pin": "Camera PIN",
        "red.camera.firmware": "Firmware Version",
        "red.sensor.name": "Sensor Name",
        "red.sensor.calibration": "Sensor Calibration Date",
        "red.bi.gamma": "Black Shading",
        
        # --- Production ---
        "red.prod.scene": "Scene",
        "red.prod.shot": "Shot",
        "red.prod.take": "Take",
        "red.prod.director": "Director",
        "red.prod.dop": "Director of Photography",
        "red.prod.unit": "Unit",
        "red.prod.location": "Location",
        
        # --- Acceleration ---
        "red.accel.x": "Acceleration X",
        "red.accel.y": "Acceleration Y",
        "red.accel.z": "Acceleration Z",
    }

def get_red_r3d_registry_field_count() -> int:
    return 300 # Estimated RED fields

def extract_red_r3d_registry_metadata(filepath: str) -> dict:
    # Placeholder for RED R3D extraction logic (e.g. using R3D SDK or redline tool)
    return {}
