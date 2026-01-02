# Image Analysis Plugin for MetaExtract

## 🖼️ Overview

The **Image Analysis Plugin** provides comprehensive image metadata extraction and analysis capabilities for MetaExtract. It extends the core system with advanced image-specific features including format detection, quality analysis, and content characterization.

## 📁 Plugin Structure

```
image_analysis_plugin/
├── __init__.py          # Main plugin file
└── README.md           # This documentation
```

## 🔧 Installation

1. **Place the plugin** in one of the plugin directories:
   - `plugins/` (default)
   - `external_plugins/` (alternative)
   - Or any custom path configured in your system

2. **Enable plugins** in your code:
   ```python
   from server.extractor.module_discovery import enable_plugins_global
   enable_plugins_global(True)
   ```

3. **Load plugins** automatically:
   ```python
   from server.extractor.module_discovery import discover_and_load_plugins_global
   discover_and_load_plugins_global()
   ```

## 📋 Plugin Metadata

```python
# Static metadata
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "MetaExtract Team"
PLUGIN_DESCRIPTION = "Advanced image analysis and metadata extraction"
PLUGIN_LICENSE = "MIT"

# Dynamic metadata function
def get_plugin_metadata():
    return {
        "version": PLUGIN_VERSION,
        "author": PLUGIN_AUTHOR,
        "description": PLUGIN_DESCRIPTION,
        "license": PLUGIN_LICENSE,
        "website": "https://metaextract.com",
        "documentation": "https://metaextract.com/docs/plugins/image-analysis"
    }
```

## 🔧 Extraction Functions

### 1. `extract_image_metadata()`

Extracts comprehensive image metadata:
- **File information**: Size, extension, name
- **Image format**: Detailed format identification
- **Color space**: RGB, RGBA, CMYK, or Indexed
- **Format-specific metadata**: Feature support, compression type
- **Processing information**: Timestamp, plugin version

**Supported formats**: JPEG, PNG, GIF, BMP, TIFF, WEBP, HEIC, SVG, RAW (CR2, NEF, DNG), PSD

### 2. `analyze_image_quality()`

Performs image quality analysis:
- **Quality score**: 0.0 to 1.0 rating
- **Resolution estimation**: Very Small to High (2000px+)
- **Compression estimation**: Lossy or lossless detection
- **Color depth estimation**: 1-8 bit to 8-16 bit
- **Aspect ratio estimation**: Common aspect ratios
- **File size category**: Very small to large

### 3. `detect_image_features()`

Detects image content and features:
- **Content detection**: Photographs, screenshots, logos, charts, artwork
- **Image type**: Photograph, screenshot, logo, chart, artwork, test
- **Usage context**: General, technical, branding, data visualization, creative
- **Format-specific features**: EXIF support, transparency, animation, metadata
- **Feature flags**: Metadata presence, quality info, processing status

## 🔗 Dependencies

```python
MODULE_DEPENDENCIES = ["base_metadata", "image"]
```

This plugin depends on:
- **base_metadata**: For core file metadata
- **image**: For basic image metadata extraction

## 📊 Integration

The plugin integrates seamlessly with MetaExtract:

- **Automatic discovery** during system initialization
- **Dependency-aware execution** respecting module dependencies
- **Parallel execution** support for performance
- **Hot reloading** for development
- **Statistics tracking** and monitoring

## 🚀 Usage Example

```python
from server.extractor.comprehensive_metadata_engine import ComprehensiveMetadataExtractor

# Create extractor (automatically loads plugins)
extractor = ComprehensiveMetadataExtractor()

# Extract metadata from an image file (includes plugin results)
result = extractor.extract_comprehensive_metadata("test.jpg", "super")

# Access plugin results
image_data = result.get("image_analysis", {})
image_quality = result.get("image_quality", {})
image_features = result.get("image_features", {})

print(f"Image format: {image_data.get('image_format')}")
print(f"Color space: {image_data.get('color_space')}")
print(f"Quality score: {image_quality.get('quality_score')}")
print(f"Resolution estimate: {image_quality.get('resolution_estimate')}")
print(f"Image type: {image_features.get('image_type')}")
```

## 📈 Expected Output

When processing an image file, the plugin adds metadata like:

```json
{
  "image_analysis": {
    "processed": true,
    "timestamp": 1712345678.9,
    "file_size": 2584000,
    "file_extension": ".jpg",
    "file_name": "test.jpg",
    "plugin_version": "1.0.0",
    "processing_time_ms": 12.8,
    "image_format": "JPEG",
    "color_space": "RGB",
    "jpeg_specific": {
      "likely_has_exif": true,
      "supports_metadata": true,
      "compression_type": "lossy",
      "common_quality_range": "75-95"
    }
  },
  "image_quality": {
    "quality_score": 0.7,
    "resolution_estimate": "Medium (1000-2000px)",
    "compression_estimate": "lossy",
    "color_depth_estimate": "8 bit",
    "aspect_ratio_estimate": "Variable (common: 4:3, 16:9, 1:1)",
    "file_size_category": "medium"
  },
  "image_features": {
    "has_metadata": true,
    "has_quality_info": true,
    "is_processed": true,
    "plugin_compatible": true,
    "likely_contains": ["photograph"],
    "image_type": "photograph",
    "usage_context": "general",
    "format_specific": {
      "supports_exif": true,
      "supports_icc_profiles": true,
      "supports_thumbnails": true,
      "common_use": "photography and web",
      "transparency_support": false
    }
  }
}
```

## 🖼️ Supported Image Formats

| Extension | Format Name | Color Space |
|-----------|-------------|-------------|
| `.jpg` | JPEG | RGB |
| `.jpeg` | JPEG | RGB |
| `.png` | Portable Network Graphics | RGBA |
| `.gif` | Graphics Interchange Format | Indexed |
| `.bmp` | Bitmap | RGB |
| `.tiff` | Tagged Image File Format | RGB/CMYK |
| `.tif` | Tagged Image File Format | RGB/CMYK |
| `.webp` | WebP | RGB/RGBA |
| `.heic` | High Efficiency Image Format | RGB |
| `.heif` | High Efficiency Image Format | RGB |
| `.svg` | Scalable Vector Graphics | RGB |
| `.raw` | RAW Image | RGB |
| `.cr2` | Canon RAW | RGB |
| `.nef` | Nikon Electronic Format | RGB |
| `.dng` | Digital Negative | RGB |
| `.psd` | Photoshop Document | RGB/CMYK |

## 🔧 Customization

To extend this plugin:

1. **Add more format detection** - Expand the image_formats dictionary
2. **Enhance quality analysis** - Add actual image processing libraries
3. **Improve content detection** - Use machine learning for content classification
4. **Add image fingerprinting** - Implement image hashing algorithms
5. **Support more metadata standards** - Add support for additional image metadata formats
6. **Add actual image decoding** - Use libraries like PIL/Pillow or OpenCV

## 📚 Best Practices

1. **Follow naming conventions** - Use `extract_*`, `analyze_*`, `detect_*` patterns
2. **Include comprehensive metadata** - Helps with plugin management
3. **Declare dependencies** - Ensures correct execution order
4. **Handle errors gracefully** - Prevents plugin failures from crashing the system
5. **Document your plugin** - Helps other developers understand its purpose

## 🎯 Benefits

- **Extensibility** - Add custom image functionality without modifying core
- **Isolation** - Plugins run in their own context
- **Maintainability** - Easy to update and replace
- **Performance** - Integrates with parallel execution
- **Compatibility** - Works with all MetaExtract features

## 🔮 Future Enhancements

This plugin can be extended with:
- **Actual image decoding** using libraries like PIL/Pillow or OpenCV
- **EXIF data extraction** for detailed camera information
- **Image fingerprinting** using perceptual hashing
- **Object detection** and recognition
- **Facial recognition** integration
- **Optical character recognition** (OCR) for text in images
- **Image similarity** comparison
- **Machine learning** based content classification
- **Quality metrics** using structural similarity (SSIM) or PSNR
- **Color analysis** and palette extraction
- **Image forensics** for manipulation detection