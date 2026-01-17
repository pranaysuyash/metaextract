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
                                   file_size: Optional[int] = None) -> Dict[str, Any]:
    """Extract image quality metrics."""
    
    # Calculate megapixels
    megapixels = round(width * height / 1_000_000, 2)
    
    # Resolution quality assessment
    total_pixels = width * height
    if total_pixels >= 20_000_000:
        resolution_quality = "excellent"
    elif total_pixels >= 12_000_000:
        resolution_quality = "high"
    elif total_pixels >= 8_000_000:
        resolution_quality = "good"
    elif total_pixels >= 4_000_000:
        resolution_quality = "medium"
    else:
        resolution_quality = "basic"
    
    # File size optimization
    file_size_optimized = False
    if file_size and total_pixels > 0:
        bytes_per_pixel = file_size / total_pixels
        file_size_optimized = 0.5 <= bytes_per_pixel <= 5.0
    
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
    
    return {
        'resolution_quality': resolution_quality,
        'file_size_optimized': file_size_optimized,
        'color_depth': color_depth,
        'compression_estimated': compression
    }


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
        filepath, width, height, format_name, mode, file_size
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
