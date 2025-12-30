"""
Image Properties Extraction
Basic image properties using Pillow: dimensions, format, DPI, color space, etc.
"""

from typing import Dict, Any, Optional


try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def extract_image_properties(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract basic image properties.
    
    Args:
        filepath: Path to image file
    
    Returns:
        Dictionary with image properties
    """
    if not PIL_AVAILABLE:
        return {"error": "Pillow not installed"}
    
    try:
        with Image.open(filepath) as img:
            properties = {
                "format": img.format,
                "mode": img.mode,
                "width": img.width,
                "height": img.height,
                "has_transparency": img.mode in ('RGBA', 'LA', 'PA'),
                "is_animated": getattr(img, "is_animated", False),
                "n_frames": getattr(img, "n_frames", 1),
            }
            
            # DPI information
            dpi = img.info.get('dpi', None)
            if dpi:
                if isinstance(dpi, tuple):
                    properties["dpi_x"] = dpi[0]
                    properties["dpi_y"] = dpi[1]
                else:
                    properties["dpi_x"] = dpi
                    properties["dpi_y"] = dpi
            else:
                properties["dpi_x"] = None
                properties["dpi_y"] = None
            
            # ICC Profile
            if 'icc_profile' in img.info:
                properties["has_icc_profile"] = True
                properties["icc_profile_size"] = len(img.info['icc_profile'])
            else:
                properties["has_icc_profile"] = False
                properties["icc_profile_size"] = 0
            
            # Aspect ratio
            if img.height > 0:
                aspect = img.width / img.height
                properties["aspect_ratio"] = round(aspect, 4)
                properties["aspect_ratio_string"] = f"{img.width}:{img.height}"
            else:
                properties["aspect_ratio"] = 0
                properties["aspect_ratio_string"] = "0:0"
            
            # Megapixels
            megapixels = (img.width * img.height) / 1000000
            properties["megapixels"] = round(megapixels, 2)
            
            # Bits per pixel
            if img.mode == 'L':
                properties["bits_per_pixel"] = 8
            elif img.mode == 'RGB':
                properties["bits_per_pixel"] = 24
            elif img.mode == 'RGBA':
                properties["bits_per_pixel"] = 32
            elif img.mode == '1':
                properties["bits_per_pixel"] = 1
            elif img.mode == 'P':
                properties["bits_per_pixel"] = 8  # Indexed color
            else:
                properties["bits_per_pixel"] = len(img.getbands()) * 8
            
            # Orientation (check for EXIF orientation)
            exif_orientation = img.info.get('Orientation', None)
            if exif_orientation:
                properties["exif_orientation"] = exif_orientation
            
            return properties
            
    except FileNotFoundError:
        return {"error": f"File not found: {filepath}"}
    except Exception as e:
        return {"error": f"Failed to extract image properties: {str(e)}"}


def extract_thumbnail_properties(filepath: str, max_size: int = 160) -> Optional[Dict[str, Any]]:
    """
    Extract thumbnail properties from image.
    
    Args:
        filepath: Path to image file
        max_size: Maximum thumbnail dimension
    
    Returns:
        Dictionary with thumbnail information
    """
    if not PIL_AVAILABLE:
        return {"error": "Pillow not installed"}
    
    try:
        with Image.open(filepath) as img:
            has_embedded = hasattr(img, '_getexif') and img._getexif() is not None
            
            thumb = img.copy()
            thumb.thumbnail((max_size, max_size))
            
            return {
                "has_embedded": has_embedded,
                "width": thumb.width,
                "height": thumb.height,
                "format": thumb.format or img.format,
                "max_size": max_size
            }
            
    except Exception as e:
        return {"error": f"Failed to extract thumbnail: {str(e)}"}


def get_image_field_count() -> int:
    """Return approximate number of image property fields."""
    return 18
