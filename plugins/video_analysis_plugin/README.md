# Video Analysis Plugin for MetaExtract

## 🎬 Overview

The **Video Analysis Plugin** provides comprehensive video metadata extraction and analysis capabilities for MetaExtract. It extends the core system with advanced video-specific features including format detection, quality analysis, and content characterization.

## 📁 Plugin Structure

```
video_analysis_plugin/
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
PLUGIN_DESCRIPTION = "Advanced video analysis and metadata extraction"
PLUGIN_LICENSE = "MIT"

# Dynamic metadata function
def get_plugin_metadata():
    return {
        "version": PLUGIN_VERSION,
        "author": PLUGIN_AUTHOR,
        "description": PLUGIN_DESCRIPTION,
        "license": PLUGIN_LICENSE,
        "website": "https://metaextract.com",
        "documentation": "https://metaextract.com/docs/plugins/video-analysis"
    }
```

## 🔧 Extraction Functions

### 1. `extract_video_metadata()`

Extracts comprehensive video metadata:
- **File information**: Size, extension, name
- **Video format**: Detailed format identification
- **Container format**: Container type detection
- **Format-specific metadata**: Codec details, feature support
- **Processing information**: Timestamp, plugin version

**Supported formats**: MP4, MOV, AVI, MKV, WEBM, FLV, WMV, MPEG, 3GP, TS, M2TS

### 2. `analyze_video_quality()`

Performs video quality analysis:
- **Quality score**: 0.0 to 1.0 rating
- **Bitrate estimation**: Based on file size and format
- **Resolution estimation**: 480p to 1080p+ detection
- **Framerate estimation**: 24fps to 30fps+ detection
- **Compression quality**: High, medium, or variable
- **Aspect ratio estimation**: 4:3 or 16:9 detection

### 3. `detect_video_features()`

Detects video content and features:
- **Content detection**: Movies, clips, home videos, screen recordings
- **Production quality**: Professional, semi-professional, consumer, test
- **Format-specific features**: Metadata support, multiple tracks, chapters, subtitles
- **Feature flags**: Metadata presence, quality info, processing status

## 🔗 Dependencies

```python
MODULE_DEPENDENCIES = ["base_metadata", "video"]
```

This plugin depends on:
- **base_metadata**: For core file metadata
- **video**: For basic video metadata extraction

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

# Extract metadata from a video file (includes plugin results)
result = extractor.extract_comprehensive_metadata("test.mp4", "super")

# Access plugin results
video_data = result.get("video_analysis", {})
video_quality = result.get("video_quality", {})
video_features = result.get("video_features", {})

print(f"Video format: {video_data.get('video_format')}")
print(f"Container format: {video_data.get('container_format')}")
print(f"Quality score: {video_quality.get('quality_score')}")
print(f"Resolution estimate: {video_quality.get('resolution_estimate')}")
print(f"Production quality: {video_features.get('production_quality')}")
```

## 📈 Expected Output

When processing a video file, the plugin adds metadata like:

```json
{
  "video_analysis": {
    "processed": true,
    "timestamp": 1712345678.9,
    "file_size": 58400000,
    "file_extension": ".mp4",
    "file_name": "test.mp4",
    "plugin_version": "1.0.0",
    "processing_time_ms": 20.5,
    "video_format": "MPEG-4 Part 14",
    "container_format": "MP4",
    "mp4_specific": {
      "likely_has_moov_atom": true,
      "supports_metadata": true,
      "supports_multiple_tracks": true,
      "common_codecs": ["H.264", "H.265", "AAC"]
    }
  },
  "video_quality": {
    "quality_score": 0.9,
    "bitrate_estimate": "high",
    "resolution_estimate": "1080p or higher",
    "framerate_estimate": "30fps or higher",
    "compression_quality": "medium",
    "aspect_ratio_estimate": "16:9 (widescreen)"
  },
  "video_features": {
    "has_metadata": true,
    "has_quality_info": true,
    "is_processed": true,
    "plugin_compatible": true,
    "likely_contains": ["movie"],
    "production_quality": "professional",
    "format_specific": {
      "supports_metadata": true,
      "supports_multiple_tracks": true,
      "supports_chapters": true,
      "supports_subtitles": true,
      "common_use": "web and general purpose"
    }
  }
}
```

## 🎥 Supported Video Formats

| Extension | Format Name | Container Type |
|-----------|-------------|----------------|
| `.mp4` | MPEG-4 Part 14 | MP4 |
| `.mov` | QuickTime File Format | QuickTime |
| `.avi` | Audio Video Interleave | AVI |
| `.mkv` | Matroska Video | Matroska |
| `.webm` | WebM Video | WebM |
| `.flv` | Flash Video | FLV |
| `.wmv` | Windows Media Video | WMV |
| `.mpeg` | MPEG Video | MPEG |
| `.mpg` | MPEG Video | MPEG |
| `.3gp` | 3GPP Video | 3GPP |
| `.ts` | MPEG Transport Stream | TS |
| `.m2ts` | MPEG-2 Transport Stream | M2TS |

## 🔧 Customization

To extend this plugin:

1. **Add more format detection** - Expand the video_formats dictionary
2. **Enhance quality analysis** - Add actual video processing libraries
3. **Improve content detection** - Use machine learning for content classification
4. **Add video fingerprinting** - Implement video hashing algorithms
5. **Support more metadata standards** - Add support for additional video metadata formats
6. **Add actual video decoding** - Use libraries like OpenCV or FFmpeg

## 📚 Best Practices

1. **Follow naming conventions** - Use `extract_*`, `analyze_*`, `detect_*` patterns
2. **Include comprehensive metadata** - Helps with plugin management
3. **Declare dependencies** - Ensures correct execution order
4. **Handle errors gracefully** - Prevents plugin failures from crashing the system
5. **Document your plugin** - Helps other developers understand its purpose

## 🎯 Benefits

- **Extensibility** - Add custom video functionality without modifying core
- **Isolation** - Plugins run in their own context
- **Maintainability** - Easy to update and replace
- **Performance** - Integrates with parallel execution
- **Compatibility** - Works with all MetaExtract features

## 🔮 Future Enhancements

This plugin can be extended with:
- **Actual video decoding** using libraries like OpenCV or FFmpeg
- **Frame-by-frame analysis** for scene detection
- **Object detection** and recognition
- **Facial recognition** integration
- **Optical character recognition** (OCR) for text in videos
- **Video fingerprinting** for content identification
- **Machine learning** based content classification
- **Quality metrics** using structural similarity (SSIM) or PSNR