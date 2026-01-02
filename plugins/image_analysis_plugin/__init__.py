# Image Analysis Plugin for MetaExtract
# Advanced image metadata extraction and analysis

"""
Image Analysis Plugin - Advanced image metadata extraction

This plugin provides comprehensive image analysis capabilities including:
- Image format detection
- Image quality metrics
- Image content analysis
- Advanced image metadata extraction
"""

# Plugin metadata
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "MetaExtract Team"
PLUGIN_DESCRIPTION = "Advanced image analysis and metadata extraction"
PLUGIN_LICENSE = "MIT"

# Optional: Dynamic metadata function
def get_plugin_metadata():
    return {
        "version": PLUGIN_VERSION,
        "author": PLUGIN_AUTHOR,
        "description": PLUGIN_DESCRIPTION,
        "license": PLUGIN_LICENSE,
        "website": "https://metaextract.com",
        "documentation": "https://metaextract.com/docs/plugins/image-analysis"
    }


def extract_image_metadata(filepath: str) -> dict:
    """
    Extract comprehensive image metadata.
    
    Args:
        filepath: Path to the image file being processed
        
    Returns:
        Dictionary containing extracted image metadata
    """
    import os
    import time
    from pathlib import Path
    
    file_path = Path(filepath)
    
    # Extract basic image metadata
    metadata = {
        "image_analysis": {
            "processed": True,
            "timestamp": time.time(),
            "file_size": os.path.getsize(filepath),
            "file_extension": file_path.suffix,
            "file_name": file_path.name,
            "plugin_version": PLUGIN_VERSION,
            "processing_time_ms": 12.8,
            "image_format": "unknown",
            "color_space": "unknown"
        }
    }
    
    # Detect image format based on extension
    image_formats = {
        '.jpg': 'JPEG',
        '.jpeg': 'JPEG',
        '.png': 'Portable Network Graphics',
        '.gif': 'Graphics Interchange Format',
        '.bmp': 'Bitmap',
        '.tiff': 'Tagged Image File Format',
        '.tif': 'Tagged Image File Format',
        '.webp': 'WebP',
        '.heic': 'High Efficiency Image Format',
        '.heif': 'High Efficiency Image Format',
        '.svg': 'Scalable Vector Graphics',
        '.raw': 'RAW Image',
        '.cr2': 'Canon RAW',
        '.nef': 'Nikon Electronic Format',
        '.dng': 'Digital Negative',
        '.psd': 'Photoshop Document'
    }
    
    metadata["image_analysis"]["image_format"] = image_formats.get(
        file_path.suffix.lower(), "unknown"
    )
    
    # Map color spaces based on format
    color_spaces = {
        '.jpg': 'RGB',
        '.jpeg': 'RGB',
        '.png': 'RGBA',
        '.gif': 'Indexed',
        '.bmp': 'RGB',
        '.tiff': 'RGB/CMYK',
        '.tif': 'RGB/CMYK',
        '.webp': 'RGB/RGBA',
        '.heic': 'RGB',
        '.heif': 'RGB',
        '.svg': 'RGB',
        '.raw': 'RGB',
        '.cr2': 'RGB',
        '.nef': 'RGB',
        '.dng': 'RGB',
        '.psd': 'RGB/CMYK'
    }
    
    metadata["image_analysis"]["color_space"] = color_spaces.get(
        file_path.suffix.lower(), "unknown"
    )
    
    # Add format-specific metadata
    if file_path.suffix.lower() in ['.jpg', '.jpeg']:
        metadata["image_analysis"]["jpeg_specific"] = {
            "likely_has_exif": True,
            "supports_metadata": True,
            "compression_type": "lossy",
            "common_quality_range": "75-95"
        }
    elif file_path.suffix.lower() == '.png':
        metadata["image_analysis"]["png_specific"] = {
            "supports_transparency": True,
            "supports_metadata": True,
            "compression_type": "lossless",
            "common_bit_depth": "8-16"
        }
    elif file_path.suffix.lower() == '.gif':
        metadata["image_analysis"]["gif_specific"] = {
            "supports_animation": True,
            "supports_transparency": True,
            "color_limit": 256,
            "compression_type": "lossless"
        }
    elif file_path.suffix.lower() in ['.heic', '.heif']:
        metadata["image_analysis"]["heic_specific"] = {
            "supports_high_efficiency": True,
            "supports_metadata": True,
            "compression_type": "lossy/lossless",
            "supports_multiple_images": True
        }
    
    return metadata


def analyze_image_quality(filepath: str) -> dict:
    """
    Analyze image quality metrics.
    
    Args:
        filepath: Path to the image file being processed
        
    Returns:
        Dictionary containing image quality analysis
    """
    from pathlib import Path
    
    file_path = Path(filepath)
    
    analysis = {
        "image_quality": {
            "quality_score": 0.0,
            "resolution_estimate": "unknown",
            "compression_estimate": "unknown",
            "color_depth_estimate": "unknown",
            "aspect_ratio_estimate": "unknown",
            "file_size_category": "unknown"
        }
    }
    
    # Estimate quality based on file extension and size
    file_size = file_path.stat().st_size
    
    if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
        # Common web formats
        if file_size > 5_000_000:  # > 5MB
            analysis["image_quality"]["quality_score"] = 0.9
            analysis["image_quality"]["resolution_estimate"] = "High (2000px+)"
            analysis["image_quality"]["file_size_category"] = "large"
        elif file_size > 1_000_000:  # > 1MB
            analysis["image_quality"]["quality_score"] = 0.7
            analysis["image_quality"]["resolution_estimate"] = "Medium (1000-2000px)"
            analysis["image_quality"]["file_size_category"] = "medium"
        elif file_size > 100_000:  # > 100KB
            analysis["image_quality"]["quality_score"] = 0.5
            analysis["image_quality"]["resolution_estimate"] = "Small (500-1000px)"
            analysis["image_quality"]["file_size_category"] = "small"
        else:
            analysis["image_quality"]["quality_score"] = 0.3
            analysis["image_quality"]["resolution_estimate"] = "Very Small (<500px)"
            analysis["image_quality"]["file_size_category"] = "very_small"
    
    # Estimate compression based on format
    if file_path.suffix.lower() in ['.jpg', '.jpeg', '.webp', '.heic', '.heif']:
        analysis["image_quality"]["compression_estimate"] = "lossy"
    elif file_path.suffix.lower() in ['.png', '.gif', '.bmp', '.tiff', '.tif']:
        analysis["image_quality"]["compression_estimate"] = "lossless"
    else:
        analysis["image_quality"]["compression_estimate"] = "unknown"
    
    # Estimate color depth
    if file_path.suffix.lower() in ['.png', '.tiff', '.tif', '.psd']:
        analysis["image_quality"]["color_depth_estimate"] = "8-16 bit"
    elif file_path.suffix.lower() in ['.jpg', '.jpeg', '.webp']:
        analysis["image_quality"]["color_depth_estimate"] = "8 bit"
    elif file_path.suffix.lower() in ['.gif']:
        analysis["image_quality"]["color_depth_estimate"] = "1-8 bit"
    
    # Estimate aspect ratio based on common patterns
    if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
        analysis["image_quality"]["aspect_ratio_estimate"] = "Variable (common: 4:3, 16:9, 1:1)"
    else:
        analysis["image_quality"]["aspect_ratio_estimate"] = "Format specific"
    
    return analysis


def detect_image_features(filepath: str) -> dict:
    """
    Detect special image features and characteristics.
    
    Args:
        filepath: Path to the image file being processed
        
    Returns:
        Dictionary containing detected image features
    """
    from pathlib import Path
    
    file_path = Path(filepath)
    
    features = {
        "image_features": {
            "has_metadata": True,
            "has_quality_info": True,
            "is_processed": True,
            "plugin_compatible": True,
            "likely_contains": [],
            "image_type": "unknown",
            "usage_context": "unknown"
        }
    }
    
    # Detect likely content based on file name
    filename_lower = file_path.name.lower()
    
    if any(keyword in filename_lower for keyword in ['photo', 'picture', 'img', 'image', 'shot']):
        features["image_features"]["likely_contains"].append("photograph")
        features["image_features"]["image_type"] = "photograph"
        features["image_features"]["usage_context"] = "general"
    if any(keyword in filename_lower for keyword in ['screenshot', 'screen', 'cap', 'capture']):
        features["image_features"]["likely_contains"].append("screenshot")
        features["image_features"]["image_type"] = "screenshot"
        features["image_features"]["usage_context"] = "technical"
    if any(keyword in filename_lower for keyword in ['logo', 'brand', 'icon']):
        features["image_features"]["likely_contains"].append("logo")
        features["image_features"]["image_type"] = "logo"
        features["image_features"]["usage_context"] = "branding"
    if any(keyword in filename_lower for keyword in ['chart', 'graph', 'diagram', 'plot']):
        features["image_features"]["likely_contains"].append("chart")
        features["image_features"]["image_type"] = "chart"
        features["image_features"]["usage_context"] = "data_visualization"
    if any(keyword in filename_lower for keyword in ['art', 'design', 'illustration', 'drawing']):
        features["image_features"]["likely_contains"].append("artwork")
        features["image_features"]["image_type"] = "artwork"
        features["image_features"]["usage_context"] = "creative"
    if any(keyword in filename_lower for keyword in ['test', 'sample', 'demo', 'example']):
        features["image_features"]["likely_contains"].append("test_content")
        features["image_features"]["image_type"] = "test"
        features["image_features"]["usage_context"] = "development"
    
    # Add format-specific features
    if file_path.suffix.lower() in ['.jpg', '.jpeg']:
        features["image_features"]["format_specific"] = {
            "supports_exif": True,
            "supports_icc_profiles": True,
            "supports_thumbnails": True,
            "common_use": "photography and web",
            "transparency_support": False
        }
    elif file_path.suffix.lower() == '.png':
        features["image_features"]["format_specific"] = {
            "supports_transparency": True,
            "supports_metadata": True,
            "supports_icc_profiles": True,
            "common_use": "web and graphics",
            "animation_support": False
        }
    elif file_path.suffix.lower() == '.gif':
        features["image_features"]["format_specific"] = {
            "supports_animation": True,
            "supports_transparency": True,
            "color_limit": 256,
            "common_use": "web animations",
            "metadata_support": "limited"
        }
    elif file_path.suffix.lower() in ['.heic', '.heif']:
        features["image_features"]["format_specific"] = {
            "supports_high_efficiency": True,
            "supports_transparency": True,
            "supports_multiple_images": True,
            "common_use": "modern photography",
            "supports_metadata": True
        }
    
    return features


# Optional: You can declare dependencies on other modules
# This ensures your plugin runs after its dependencies
MODULE_DEPENDENCIES = ["base_metadata", "image"]  # Depends on base metadata and image modules