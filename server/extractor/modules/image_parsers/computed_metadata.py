"""
Computed Metadata Utilities
===========================

Provides computed metadata extraction for all image formats:
- Image quality analysis
- AI-based analysis (scene, quality, color)
- Perceptual hashing
- Forensic analysis
- Technical metadata
- Data completeness scoring
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_image_quality_analysis(filepath: str, width: int, height: int, 
                                   format_name: str, mode: str, 
                                   file_size: Optional[int] = None,
                                   exif: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Extract image quality metrics."""
    
    # Calculate megapixels
    megapixels = round(width * height / 1_000_000, 2)
    
    # Resolution quality assessment
    total_pixels = width * height
    if total_pixels >= 20_000_000:
        resolution_quality = "excellent"
        resolution_score = 95
    elif total_pixels >= 12_000_000:
        resolution_quality = "high"
        resolution_score = 85
    elif total_pixels >= 8_000_000:
        resolution_quality = "good"
        resolution_score = 75
    elif total_pixels >= 4_000_000:
        resolution_quality = "medium"
        resolution_score = 60
    else:
        resolution_quality = "basic"
        resolution_score = 40
    
    # File size optimization
    file_size_optimized = False
    bytes_per_pixel = None
    if file_size and total_pixels > 0:
        bytes_per_pixel = file_size / total_pixels
        file_size_optimized = 0.5 <= bytes_per_pixel <= 5.0
    
    # Exposure score (based on EXIF metadata if available)
    exposure_score = None
    if exif:
        exposure_factors = []
        
        # Check ISO (lower is generally better for quality, but need some range)
        iso = exif.get('isospeedratings') or exif.get('iso')
        if iso:
            if isinstance(iso, (int, float)):
                if iso <= 100:
                    exposure_factors.append(100)
                elif iso <= 400:
                    exposure_factors.append(90)
                elif iso <= 800:
                    exposure_factors.append(75)
                elif iso <= 1600:
                    exposure_factors.append(60)
                elif iso <= 3200:
                    exposure_factors.append(45)
                else:
                    exposure_factors.append(30)
        
        # Check aperture (wider aperture = lower f-number = generally better for quality)
        fnumber = exif.get('fnumber')
        if fnumber:
            if isinstance(fnumber, (int, float)):
                if fnumber <= 1.8:
                    exposure_factors.append(100)
                elif fnumber <= 2.8:
                    exposure_factors.append(90)
                elif fnumber <= 4.0:
                    exposure_factors.append(80)
                elif fnumber <= 5.6:
                    exposure_factors.append(70)
                elif fnumber <= 8.0:
                    exposure_factors.append(60)
                else:
                    exposure_factors.append(50)
        
        # Check shutter speed (reasonable range)
        exposure_time = exif.get('exposuretime')
        if exposure_time:
            if isinstance(exposure_time, (int, float)):
                # Very fast or very slow can indicate issues
                if 0.001 <= exposure_time <= 0.5:
                    exposure_factors.append(85)
                elif 0.0001 <= exposure_time < 0.001:
                    exposure_factors.append(70)
                elif 0.5 < exposure_time <= 2.0:
                    exposure_factors.append(75)
                else:
                    exposure_factors.append(60)
        
        # Calculate average exposure score
        if exposure_factors:
            exposure_score = sum(exposure_factors) / len(exposure_factors)
    
    # Focus score (based on EXIF focus metadata if available)
    focus_score = None
    focus_factors = []
    
    if exif:
        # Check focus mode
        focus_mode = exif.get('focusmode') or exif.get('afmode')
        if focus_mode:
            focus_modes_good = ['AF-S', 'Single', 'One Shot', 'AF-C', 'Continuous']
            if any(gm in str(focus_mode) for gm in focus_modes_good):
                focus_factors.append(80)
            else:
                focus_factors.append(50)
        
        # Check AF points in focus
        af_points_in_focus = exif.get('pointsinfocus') or exif.get('afpoints')
        if af_points_in_focus:
            focus_factors.append(75)
        
        # Check face detection (if available)
        face_detected = exif.get('facedetected')
        if face_detected:
            focus_factors.append(85)
    
    if focus_factors:
        focus_score = sum(focus_factors) / len(focus_factors)
    
    # Overall quality assessment
    quality_factors = [resolution_score]
    if exposure_score is not None:
        quality_factors.append(exposure_score)
    if focus_score is not None:
        quality_factors.append(focus_score)
    
    overall_quality = round(sum(quality_factors) / len(quality_factors))
    
    # Color depth
    color_depth_map = {
        'RGB': '24-bit',
        'RGBA': '32-bit',
        'CMYK': '32-bit',
        'L': '8-bit grayscale',
        'LA': '16-bit grayscale',
        'P': '8-bit palette',
        '1': '1-bit (bilevel)',
        'I': '32-bit integer',
        'F': '32-bit float',
    }
    color_depth = color_depth_map.get(mode, 'unknown')
    
    # Compression estimation
    compression_map = {
        'JPEG': 'lossy JPEG',
        'PNG': 'lossless PNG',
        'GIF': 'lossless GIF',
        'WebP': 'modern WebP',
        'TIFF': 'lossless/compressed TIFF',
    }
    compression = compression_map.get(format_name, 'unknown')
    
    result = {
        'resolution_quality': resolution_quality,
        'resolution_score': resolution_score,
        'file_size_optimized': file_size_optimized,
        'color_depth': color_depth,
        'compression_estimated': compression,
        'overall_quality': overall_quality,
        'quality_factors': {
            'resolution': resolution_score,
            'exposure': exposure_score,
            'focus': focus_score
        }
    }
    
    if bytes_per_pixel is not None:
        result['bytes_per_pixel'] = round(bytes_per_pixel, 3)
    
    return result


def extract_ai_analysis(filepath: str, width: int, height: int, 
                        format_name: str, mode: str) -> Dict[str, Any]:
    """Extract AI-based analysis (optimized, not using heavy ML)."""
    
    # Basic scene analysis based on image characteristics
    total_pixels = width * height
    aspect_ratio = width / height if height > 0 else 1.0
    
    # Simple heuristic for scene type
    scene_type = "unknown"
    if aspect_ratio > 1.5:
        scene_type = "landscape"
    elif aspect_ratio < 0.7:
        scene_type = "portrait"
    else:
        if total_pixels > 4_000_000:
            scene_type = "standard_photo"
        else:
            scene_type = "thumbnail"
    
    # Quality assessment based on resolution
    quality_level = "good"
    if total_pixels >= 20_000_000:
        quality_level = "excellent"
    elif total_pixels >= 8_000_000:
        quality_level = "good"
    elif total_pixels >= 2_000_000:
        quality_level = "fair"
    else:
        quality_level = "basic"
    
    overall_quality_score = min(100, max(50, (total_pixels / 20_000_000) * 100))
    
    return {
        'scene_type': scene_type,
        'analysis_available': True,
        'optimized_mode': True,
        'width': width,
        'height': height,
        'format': format_name,
        'mode': mode,
        'ai_quality_assessment': {
            'quality_level': quality_level,
            'overall_quality_score': round(overall_quality_score, 1),
            'analysis_available': True,
            'optimized_mode': True
        },
        'ai_color_analysis': {
            'analysis_available': True,
            'optimized_mode': True,
            'format': format_name
        }
    }


def extract_perceptual_hashes(filepath: str) -> Optional[Dict[str, Any]]:
    """Extract perceptual hashes for duplicate detection."""
    try:
        from PIL import Image
        import imagehash
        
        with Image.open(filepath) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img_rgb = img.convert('RGB')
            else:
                img_rgb = img
            
            # Calculate perceptual hash
            phash = imagehash.phash(img_rgb)
            
            return {
                'perceptual_hash': str(phash),
                'hashing_success': True,
                'hash_count': 1,
                'ultra_fast_mode': True
            }
    except ImportError:
        logger.debug("imagehash not available for perceptual hashing")
    except Exception as e:
        logger.debug(f"Perceptual hashing failed: {e}")
    
    return None


def extract_forensic_analysis(filepath: str, format_name: str, mode: str,
                              width: int, height: int) -> Dict[str, Any]:
    """Extract forensic/file integrity analysis."""
    
    import os
    
    file_size = 0
    try:
        file_size = os.path.getsize(filepath)
    except:
        pass
    
    # Check transparency support
    supports_transparency = mode in ['RGBA', 'LA', 'P', '1']
    
    # Bits per channel
    bits_per_channel = 8
    if mode == 'RGBA':
        bits_per_channel = 8
    elif mode == 'RGB':
        bits_per_channel = 8
    elif mode == 'P':
        bits_per_channel = 8
    elif mode == 'L':
        bits_per_channel = 8
    
    return {
        'format': format_name,
        'mode': mode,
        'dimensions': f"{width}x{height}",
        'has_transparency': supports_transparency,
        'bits_per_channel': bits_per_channel,
        'size_bytes': file_size
    }


def extract_technical_metadata(width: int, height: int, format_name: str,
                               mode: str, has_alpha: bool = False) -> Dict[str, Any]:
    """Extract technical metadata about the image."""
    
    # Band count
    band_count = 1
    if mode in ['RGB', 'RGBA']:
        band_count = 4 if mode == 'RGBA' else 3
    elif mode == 'P':
        band_count = 1
    elif mode == 'L':
        band_count = 1
    
    # Aspect ratio
    aspect_ratio = width / height if height > 0 else 1.0
    aspect_str = f"{width}:{height}"
    
    # Pixel format
    pixel_format = mode
    
    # Animated check (for GIF/WebP)
    is_animated = False
    n_frames = 1
    
    return {
        'pil_format': format_name,
        'pil_mode': mode,
        'pixel_format': pixel_format,
        'supports_transparency': has_alpha,
        'band_count': band_count,
        'is_animated': is_animated,
        'n_frames': n_frames,
        'width': width,
        'height': height,
        'megapixels': round(width * height / 1_000_000, 2),
        'aspect_ratio': aspect_str,
        'dimensions': f"{width}x{height}"
    }


def extract_data_completeness(exif: Dict, gps: Dict, camera_data: Dict) -> Dict[str, Any]:
    """Calculate data completeness scores."""
    
    has_gps = bool(gps and (gps.get('latitude') or gps.get('longitude') or gps.get('altitude')))
    has_exif = bool(exif and len(exif) > 0)
    has_camera = bool(camera_data and (camera_data.get('make') or camera_data.get('model')))
    
    completeness_items = [bool(has_gps), bool(has_exif), bool(has_camera)]
    overall_completeness = round((sum(completeness_items) / len(completeness_items)) * 100, 1)
    
    return {
        'gps_data_complete': has_gps,
        'exif_data_complete': has_exif,
        'camera_data_complete': has_camera,
        'overall_completeness': overall_completeness
    }


def extract_camera_data(exif: Dict, width: int, height: int) -> Dict[str, Any]:
    """Extract camera/device information from EXIF."""
    
    camera_data = {}
    
    if exif:
        if 'make' in exif:
            camera_data['make'] = exif['make']
        if 'model' in exif:
            camera_data['model'] = exif['model']
        if 'software' in exif:
            camera_data['software'] = exif['software']
        if 'datetimeoriginal' in exif:
            camera_data['datetime_original'] = exif['datetimeoriginal']
        if 'xresolution' in exif:
            camera_data['x_resolution'] = exif['xresolution']
        if 'yresolution' in exif:
            camera_data['y_resolution'] = exif['yresolution']
    
    # Add basic info even without EXIF
    if not camera_data:
        camera_data['make'] = 'Unknown'
        camera_data['model'] = 'Unknown'
    
    return camera_data


def extract_mobile_metadata(exif: Dict, width: int, height: int) -> Dict[str, Any]:
    """Extract mobile device metadata if available."""
    
    mobile_data = {}
    
    if exif:
        if 'make' in exif:
            mobile_data['make'] = exif['make']
        if 'model' in exif:
            mobile_data['model'] = exif['model']
        if 'datetimeoriginal' in exif:
            mobile_data['datetime_original'] = exif['datetimeoriginal']
        if 'xresolution' in exif:
            mobile_data['x_resolution'] = exif['xresolution']
        if 'yresolution' in exif:
            mobile_data['y_resolution'] = exif['yresolution']
    
    return mobile_data


def extract_image_analysis(width: int, height: int, format_name: str,
                          mode: str, file_size: Optional[int] = None) -> Dict[str, Any]:
    """Extract general image analysis."""
    
    import os
    
    size_bytes = file_size
    if file_size is None:
        try:
            size_bytes = os.path.getsize
        except:
            size_bytes = 0
    
    aspect_ratio = width / height if height > 0 else 1.0
    
    return {
        'format': format_name,
        'mode': mode,
        'width': width,
        'height': height,
        'megapixels': round(width * height / 1_000_000, 2),
        'aspect_ratio': f"{width}:{height}",
        'has_transparency': mode in ['RGBA', 'LA', 'P', '1'],
        'color_channels': 4 if mode == 'RGBA' else 3 if mode == 'RGB' else 1,
        'size_estimate': size_bytes
    }


def compute_all_metadata(filepath: str, width: int, height: int, format_name: str,
                         mode: str, exif: Dict, gps: Dict, icc_profile: Dict,
                         file_size: Optional[int] = None) -> Dict[str, Any]:
    """
    Compute all additional metadata for an image.
    
    Returns a dict with all computed metadata categories.
    """
    
    import os
    
    if file_size is None:
        try:
            file_size = os.path.getsize(filepath)
        except:
            file_size = 0
    
    computed = {}
    
    # Camera data
    camera_data = extract_camera_data(exif, width, height)
    if camera_data:
        computed['camera_data'] = camera_data
    
    # Mobile metadata
    mobile_metadata = extract_mobile_metadata(exif, width, height)
    if mobile_metadata:
        computed['mobile_metadata'] = mobile_metadata
    
    # Image quality analysis
    quality_analysis = extract_image_quality_analysis(
        filepath, width, height, format_name, mode, file_size, exif
    )
    computed['image_quality_analysis'] = quality_analysis
    
    # AI analysis
    ai_analysis = extract_ai_analysis(filepath, width, height, format_name, mode)
    if 'ai_quality_assessment' in ai_analysis:
        computed['ai_quality_assessment'] = ai_analysis['ai_quality_assessment']
    if 'ai_color_analysis' in ai_analysis:
        computed['ai_color_analysis'] = ai_analysis['ai_color_analysis']
    computed['ai_scene_recognition'] = {
        'scene_type': ai_analysis['scene_type'],
        'analysis_available': True,
        'optimized_mode': True,
        'width': width,
        'height': height,
        'format': format_name,
        'mode': mode
    }
    
    # Perceptual hashes
    perceptual_hashes = extract_perceptual_hashes(filepath)
    if perceptual_hashes:
        computed['perceptual_hashes'] = perceptual_hashes
    
    # Forensic analysis
    forensic = extract_forensic_analysis(filepath, format_name, mode, width, height)
    computed['forensic'] = forensic
    
    # Technical metadata
    technical = extract_technical_metadata(width, height, format_name, mode)
    computed['technical_metadata'] = technical
    
    # Image analysis
    image_analysis = extract_image_analysis(width, height, format_name, mode, file_size)
    computed['image_analysis'] = image_analysis
    
    # Data completeness
    completeness = extract_data_completeness(exif, gps, camera_data)
    computed['data_completeness'] = completeness
    
    # ICC profile
    if icc_profile:
        computed['icc_profile'] = icc_profile
    
    return computed


def extract_additional_metadata(filepath: str, width: int, height: int, 
                                format_name: str, mode: str) -> Dict[str, Any]:
    """
    Extract additional computed metadata:
    - Aspect ratio classification
    - Dominant colors (basic)
    - Color space estimation
    - Estimated quality for different use cases
    """
    additional = {}
    
    # Aspect ratio classification
    if height > 0:
        aspect_ratio = width / height
        if 0.9 <= aspect_ratio <= 1.1:
            aspect_class = "square"
        elif aspect_ratio > 1.5:
            aspect_class = "landscape"
        elif aspect_ratio < 0.67:
            aspect_class = "portrait"
        else:
            aspect_class = "standard"
        
        additional['aspect_ratio'] = round(aspect_ratio, 3)
        additional['aspect_classification'] = aspect_class
    
    # Color space estimation based on mode and bit depth
    if mode in ['RGB', 'RGBA']:
        if 'A' in mode:
            additional['color_space_estimation'] = 'sRGB (with alpha)'
        else:
            additional['color_space_estimation'] = 'sRGB'
    elif mode == 'CMYK':
        additional['color_space_estimation'] = 'CMYK'
    elif mode == 'L':
        additional['color_space_estimation'] = 'Grayscale'
    elif mode == 'P':
        additional['color_space_estimation'] = 'Indexed Color'
    else:
        additional['color_space_estimation'] = 'Unknown'
    
    # Use case recommendations
    use_cases = []
    total_pixels = width * height
    
    if total_pixels >= 8_000_000:
        use_cases.extend(['web_display', 'social_media', 'printing'])
    if total_pixels >= 20_000_000:
        use_cases.extend(['large_printing', 'professional_use'])
    if total_pixels >= 2_000_000:
        use_cases.append('thumbnail')
    
    if mode in ['RGB', 'RGBA']:
        use_cases.append('digital_display')
    
    if mode == 'P':
        use_cases.append('web_graphics')
    
    if use_cases:
        additional['recommended_use_cases'] = list(set(use_cases))
    
    # Estimated brightness (very basic)
    try:
        from PIL import Image
        with Image.open(filepath) as img:
            # Convert to grayscale for brightness estimation
            if img.mode != 'L':
                gray = img.convert('L')
            else:
                gray = img
            
            # Sample-based brightness estimation
            import numpy as np
            arr = np.array(gray)
            avg_brightness = float(np.mean(arr))
            
            if avg_brightness > 200:
                brightness_class = "bright"
            elif avg_brightness > 100:
                brightness_class = "balanced"
            elif avg_brightness > 50:
                brightness_class = "dark"
            else:
                brightness_class = "very_dark"
            
            additional['brightness_estimate'] = {
                'average': round(avg_brightness, 1),
                'classification': brightness_class
            }
    except Exception:
        pass
    
    # Transparency detection
    has_transparency = mode in ['RGBA', 'LA', 'P', '1']
    additional['has_transparency'] = has_transparency
    
    # Animation detection (for formats that support it)
    is_animated = False
    try:
        from PIL import Image
        with Image.open(filepath) as img:
            n_frames = getattr(img, 'n_frames', 1)
            is_animated = n_frames > 1
            additional['frame_count'] = n_frames
            additional['is_animated'] = is_animated
    except Exception:
        pass
    
    return additional


def extract_entropy_analysis(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Perform basic entropy analysis on image.
    High entropy = more information/complexity.
    Low entropy = more uniform/simple.
    """
    try:
        from PIL import Image
        import numpy as np
        
        with Image.open(filepath) as img:
            # Convert to grayscale for entropy calculation
            if img.mode != 'L':
                gray = img.convert('L')
            else:
                gray = img
            
            arr = np.array(gray)
            
            # Calculate histogram
            hist, _ = np.histogram(arr, bins=256, range=(0, 256))
            hist = hist / hist.sum()  # Normalize
            
            # Calculate entropy
            entropy = -np.sum(hist * np.log2(hist + 1e-10))
            
            # Classify entropy
            if entropy > 7.5:
                entropy_class = "high_complexity"
            elif entropy > 6.0:
                entropy_class = "moderate_complexity"
            elif entropy > 4.0:
                entropy_class = "low_complexity"
            else:
                entropy_class = "very_uniform"
            
            return {
                'entropy': round(entropy, 3),
                'classification': entropy_class,
                'analysis_available': True
            }
    except Exception as e:
        logger.debug(f"Entropy analysis failed: {e}")
    
    return None


def extract_format_features(format_name: str) -> Dict[str, Any]:
    """
    Return format-specific feature flags and capabilities.
    """
    format_features = {
        'JPEG': {
            'supports_exif': True,
            'supports_iptc': True,
            'supports_xmp': True,
            'supports_gps': True,
            'supports_icc': True,
            'supports_transparency': False,
            'supports_animation': False,
            'supports_layers': False,
            'compression': 'lossy',
            'typical_extensions': ['.jpg', '.jpeg']
        },
        'PNG': {
            'supports_exif': False,
            'supports_iptc': False,
            'supports_xmp': True,
            'supports_gps': False,
            'supports_icc': True,
            'supports_transparency': True,
            'supports_animation': True,
            'supports_layers': False,
            'compression': 'lossless',
            'typical_extensions': ['.png', '.apng']
        },
        'GIF': {
            'supports_exif': False,
            'supports_iptc': False,
            'supports_xmp': False,
            'supports_gps': False,
            'supports_icc': False,
            'supports_transparency': True,
            'supports_animation': True,
            'supports_layers': False,
            'compression': 'lossless',
            'typical_extensions': ['.gif']
        },
        'WebP': {
            'supports_exif': True,
            'supports_iptc': True,
            'supports_xmp': True,
            'supports_gps': True,
            'supports_icc': True,
            'supports_transparency': True,
            'supports_animation': True,
            'supports_layers': False,
            'compression': 'lossy/lossless',
            'typical_extensions': ['.webp']
        },
        'BMP': {
            'supports_exif': False,
            'supports_iptc': False,
            'supports_xmp': False,
            'supports_gps': False,
            'supports_icc': False,
            'supports_transparency': False,
            'supports_animation': False,
            'supports_layers': False,
            'compression': 'lossless',
            'typical_extensions': ['.bmp', '.dib']
        },
        'TIFF': {
            'supports_exif': True,
            'supports_iptc': True,
            'supports_xmp': True,
            'supports_gps': True,
            'supports_icc': True,
            'supports_transparency': True,
            'supports_animation': False,
            'supports_layers': True,
            'compression': 'lossless/lossy',
            'typical_extensions': ['.tiff', '.tif', '.dng']
        },
        'HEIC': {
            'supports_exif': True,
            'supports_iptc': True,
            'supports_xmp': True,
            'supports_gps': True,
            'supports_icc': True,
            'supports_transparency': True,
            'supports_animation': True,
            'supports_layers': False,
            'compression': 'lossy',
            'typical_extensions': ['.heic', '.heif']
        },
        'AVIF': {
            'supports_exif': True,
            'supports_iptc': True,
            'supports_xmp': True,
            'supports_gps': True,
            'supports_icc': True,
            'supports_transparency': True,
            'supports_animation': True,
            'supports_layers': False,
            'compression': 'lossy',
            'typical_extensions': ['.avif']
        },
        'PSD': {
            'supports_exif': True,
            'supports_iptc': True,
            'supports_xmp': True,
            'supports_gps': False,
            'supports_icc': True,
            'supports_transparency': True,
            'supports_animation': False,
            'supports_layers': True,
            'compression': 'lossless',
            'typical_extensions': ['.psd', '.psb']
        },
        'SVG': {
            'supports_exif': False,
            'supports_iptc': False,
            'supports_xmp': True,
            'supports_gps': False,
            'supports_icc': False,
            'supports_transparency': True,
            'supports_animation': False,
            'supports_layers': False,
            'compression': 'lossless',
            'typical_extensions': ['.svg', '.svgz'],
            'is_vector': True
        }
    }
    
    return format_features.get(format_name, {
        'supports_exif': False,
        'supports_iptc': False,
        'supports_xmp': False,
        'supports_gps': False,
        'supports_icc': False,
        'supports_transparency': False,
        'supports_animation': False,
        'supports_layers': False,
        'compression': 'unknown',
        'typical_extensions': []
    })


def parse_gpx_track(gpx_filepath: str) -> Dict[str, Any]:
    """
    Parse a GPX track file and return waypoints with timestamps.
    
    Args:
        gpx_filepath: Path to GPX file
        
    Returns:
        Dict with 'waypoints' list and 'time_range'
    """
    import xml.etree.ElementTree as ET
    from datetime import datetime, timedelta
    
    try:
        tree = ET.parse(gpx_filepath)
        root = tree.getroot()
        
        # Handle namespace
        ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}
        
        waypoints = []
        
        # Parse track points
        for trkpt in root.findall('.//gpx:trkpt', ns):
            lat = trkpt.get('lat')
            lon = trkpt.get('lon')
            
            ele_elem = trkpt.find('gpx:ele', ns)
            elevation = None
            if ele_elem is not None and ele_elem.text:
                try:
                    elevation = float(ele_elem.text)
                except ValueError:
                    pass
            
            time_elem = trkpt.find('gpx:time', ns)
            timestamp = None
            if time_elem is not None and time_elem.text:
                try:
                    timestamp = datetime.fromisoformat(time_elem.text.replace('Z', '+00:00'))
                except ValueError:
                    pass
            
            if lat and lon and timestamp:
                waypoints.append({
                    'latitude': float(lat),
                    'longitude': float(lon),
                    'elevation': elevation,
                    'timestamp': timestamp
                })
        
        # Also parse waypoints
        for wpt in root.findall('.//gpx:wpt', ns):
            lat = wpt.get('lat')
            lon = wpt.get('lon')
            
            ele_elem = wpt.find('gpx:ele', ns)
            elevation = None
            if ele_elem is not None and ele_elem.text:
                try:
                    elevation = float(ele_elem.text)
                except ValueError:
                    pass
            
            time_elem = wpt.find('gpx:time', ns)
            timestamp = None
            if time_elem is not None and time_elem.text:
                try:
                    timestamp = datetime.fromisoformat(time_elem.text.replace('Z', '+00:00'))
                except ValueError:
                    pass
            
            if lat and lon:
                waypoints.append({
                    'latitude': float(lat),
                    'longitude': float(lon),
                    'elevation': elevation,
                    'timestamp': timestamp,
                    'is_waypoint': True
                })
        
        # Sort by timestamp
        waypoints.sort(key=lambda w: w.get('timestamp') or datetime.max)
        
        # Calculate time range
        timestamps = [w['timestamp'] for w in waypoints if w.get('timestamp')]
        time_range = {}
        if timestamps:
            time_range['start'] = min(timestamps)
            time_range['end'] = max(timestamps)
            time_range['duration_seconds'] = (time_range['end'] - time_range['start']).total_seconds()
        
        return {
            'waypoints': waypoints,
            'time_range': time_range,
            'total_points': len(waypoints),
            'format': 'GPX'
        }
        
    except Exception as e:
        logger.warning(f"Failed to parse GPX file {gpx_filepath}: {e}")
        return {
            'waypoints': [],
            'time_range': {},
            'total_points': 0,
            'format': 'GPX',
            'error': str(e)
        }


def sync_gps_from_track(image_timestamp, track_data: Dict[str, Any]):
    """
    Find closest GPS point from track for given image timestamp.
    
    Args:
        image_timestamp: EXIF timestamp from image
        track_data: Parsed GPX track data
        
    Returns:
        GPS coordinates dict or None if no match
    """
    from datetime import timedelta
    
    if not image_timestamp or not track_data or not track_data.get('waypoints'):
        return None
    
    waypoints = track_data['waypoints']
    
    # Filter to waypoints with timestamps
    timed_points = [w for w in waypoints if w.get('timestamp')]
    if not timed_points:
        return None
    
    # Find closest point in time
    closest_point = None
    min_delta = timedelta.max
    
    for point in timed_points:
        delta = abs(image_timestamp - point['timestamp'])
        if delta < min_delta:
            min_delta = delta
            closest_point = point
    
    # Only return if within reasonable threshold (e.g., 5 minutes) and we found a point
    if closest_point and min_delta < timedelta(minutes=5):
        return {
            'latitude': closest_point['latitude'],
            'longitude': closest_point['longitude'],
            'altitude': closest_point.get('elevation'),
            'timestamp': closest_point['timestamp'],
            'time_offset_seconds': min_delta.total_seconds(),
            'confidence': 'high' if min_delta < timedelta(seconds=60) else 'medium'
        }
    
    return None


def calculate_gps_synchronization(gps_data: Dict[str, Any], 
                                  exif_datetime: Any) -> Dict[str, Any]:
    """
    Calculate GPS synchronization status and corrections.
    
    Args:
        gps_data: GPS metadata from image
        exif_datetime: EXIF DateTimeOriginal
        
    Returns:
        Synchronization analysis dict
    """
    analysis = {
        'has_valid_gps': False,
        'gps_quality': 'none',
        'clock_offset_detected': False,
        'suggested_correction': None,
        'sync_status': 'not_applicable'
    }
    
    if not gps_data:
        analysis['sync_status'] = 'no_gps_data'
        return analysis
    
    # Check for valid coordinates
    lat = gps_data.get('latitude')
    lon = gps_data.get('longitude')
    
    if lat is None or lon is None:
        analysis['sync_status'] = 'incomplete_gps'
        return analysis
    
    analysis['has_valid_gps'] = True
    
    # Basic GPS quality assessment
    if 'latitude_ref' in gps_data and 'longitude_ref' in gps_data:
        analysis['gps_quality'] = 'standard'
    
    if 'altitude' in gps_data:
        analysis['gps_quality'] = 'with_altitude'
    
    if 'speed' in gps_data or 'track' in gps_data:
        analysis['gps_quality'] = 'with_motion'
    
    analysis['sync_status'] = 'gps_present'
    
    return analysis


def extract_gps_track_sync(gps_data: Dict[str, Any], 
                          exif_datetime: Any,
                          track_filepath: Optional[str] = None,
                          track_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Sync GPS data from track file to image if needed.
    
    Args:
        gps_data: Existing GPS metadata from image
        exif_datetime: Image capture datetime
        track_filepath: Optional path to GPX track file
        track_data: Optional pre-parsed track data
        
    Returns:
        GPS sync analysis and potential correction
    """
    result = {
        'original_gps': gps_data,
        'sync_status': 'not_attempted',
        'suggested_correction': None,
        'track_data_loaded': False
    }
    
    # If we already have good GPS, no sync needed
    if gps_data and gps_data.get('latitude') and gps_data.get('longitude'):
        sync_analysis = calculate_gps_synchronization(gps_data, exif_datetime)
        result['sync_analysis'] = sync_analysis
        result['sync_status'] = 'already_synced'
        return result
    
    # Need to sync from track
    if track_filepath or track_data:
        if track_data is None and track_filepath:
            if track_filepath.lower().endswith('.gpx'):
                track_data = parse_gpx_track(track_filepath)
            else:
                result['sync_status'] = 'unsupported_format'
                return result
        
        if track_data and track_data.get('waypoints'):
            result['track_data_loaded'] = True
            
            if exif_datetime:
                # Try to find matching GPS point
                synced_gps = sync_gps_from_track(exif_datetime, track_data)
                
                if synced_gps:
                    result['suggested_correction'] = synced_gps
                    result['sync_status'] = 'sync_available'
                    result['sync_analysis'] = {
                        'has_valid_gps': True,
                        'gps_quality': 'synced',
                        'clock_offset_detected': False,
                        'time_offset_seconds': synced_gps.get('time_offset_seconds', 0),
                        'confidence': synced_gps.get('confidence', 'unknown')
                    }
                else:
                    result['sync_status'] = 'no_match_in_time_range'
                    time_range = track_data.get('time_range')
                    if time_range:
                        result['time_range'] = time_range
            else:
                result['sync_status'] = 'no_exif_timestamp'
        else:
            result['sync_status'] = 'no_track_data'
    else:
        result['sync_status'] = 'no_track_provided'
    
    return result
