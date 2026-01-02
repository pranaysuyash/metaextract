# Audio Analysis Plugin for MetaExtract

## 🎵 Overview

The **Audio Analysis Plugin** provides comprehensive audio metadata extraction and analysis capabilities for MetaExtract. It extends the core system with advanced audio-specific features including format detection, quality analysis, and content characterization.

## 📁 Plugin Structure

```
audio_analysis_plugin/
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
PLUGIN_DESCRIPTION = "Advanced audio analysis and metadata extraction"
PLUGIN_LICENSE = "MIT"

# Dynamic metadata function
def get_plugin_metadata():
    return {
        "version": PLUGIN_VERSION,
        "author": PLUGIN_AUTHOR,
        "description": PLUGIN_DESCRIPTION,
        "license": PLUGIN_LICENSE,
        "website": "https://metaextract.com",
        "documentation": "https://metaextract.com/docs/plugins/audio-analysis"
    }
```

## 🔧 Extraction Functions

### 1. `extract_audio_metadata()`

Extracts comprehensive audio metadata:
- **File information**: Size, extension, name
- **Audio format**: Detailed format identification
- **Format-specific metadata**: Codec details, compression type
- **Processing information**: Timestamp, plugin version

**Supported formats**: MP3, WAV, AAC, FLAC, OGG, M4A, WMA, AIFF, ALAC

### 2. `analyze_audio_quality()`

Performs audio quality analysis:
- **Quality score**: 0.0 to 1.0 rating
- **Bitrate estimation**: Based on file size and format
- **Sample rate estimation**: 22.05kHz to 44.1kHz+ detection
- **Channel estimation**: Mono, stereo, or multi-channel
- **Compression quality**: Uncompressed, lossless, or lossy

### 3. `detect_audio_features()`

Detects audio content and features:
- **Content detection**: Music, speech, sound effects, test content
- **Format-specific features**: Metadata support, cover art, chapters
- **Feature flags**: Metadata presence, quality info, processing status

## 🔗 Dependencies

```python
MODULE_DEPENDENCIES = ["base_metadata", "audio"]
```

This plugin depends on:
- **base_metadata**: For core file metadata
- **audio**: For basic audio metadata extraction

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

# Extract metadata from an audio file (includes plugin results)
result = extractor.extract_comprehensive_metadata("test.mp3", "super")

# Access plugin results
audio_data = result.get("audio_analysis", {})
audio_quality = result.get("audio_quality", {})
audio_features = result.get("audio_features", {})

print(f"Audio format: {audio_data.get('audio_format')}")
print(f"Quality score: {audio_quality.get('quality_score')}")
print(f"Likely contains: {audio_features.get('likely_contains')}")
```

## 📈 Expected Output

When processing an audio file, the plugin adds metadata like:

```json
{
  "audio_analysis": {
    "processed": true,
    "timestamp": 1712345678.9,
    "file_size": 3584000,
    "file_extension": ".mp3",
    "file_name": "test.mp3",
    "plugin_version": "1.0.0",
    "processing_time_ms": 15.2,
    "audio_format": "MPEG Audio Layer III",
    "mp3_specific": {
      "likely_has_id3_tags": true,
      "supports_metadata": true,
      "compression_type": "lossy"
    }
  },
  "audio_quality": {
    "quality_score": 0.75,
    "bitrate_estimate": "medium",
    "sample_rate_estimate": "44.1kHz",
    "channels_estimate": "stereo",
    "compression_quality": "lossy"
  },
  "audio_features": {
    "has_metadata": true,
    "has_quality_info": true,
    "is_processed": true,
    "plugin_compatible": true,
    "likely_contains": ["music"],
    "format_specific": {
      "supports_id3_tags": true,
      "supports_cover_art": true,
      "supports_chapters": false
    }
  }
}
```

## 🎯 Supported Audio Formats

| Extension | Format Name | Compression Type |
|-----------|-------------|------------------|
| `.mp3` | MPEG Audio Layer III | Lossy |
| `.wav` | Waveform Audio File Format | Uncompressed |
| `.aac` | Advanced Audio Coding | Lossy |
| `.flac` | Free Lossless Audio Codec | Lossless |
| `.ogg` | Ogg Vorbis | Lossy |
| `.m4a` | MPEG-4 Audio | Lossy/Lossless |
| `.wma` | Windows Media Audio | Lossy |
| `.aiff` | Audio Interchange File Format | Uncompressed |
| `.alac` | Apple Lossless Audio Codec | Lossless |

## 🔧 Customization

To extend this plugin:

1. **Add more format detection** - Expand the audio_formats dictionary
2. **Enhance quality analysis** - Add actual audio processing libraries
3. **Improve content detection** - Use machine learning for content classification
4. **Add audio fingerprinting** - Implement audio hashing algorithms
5. **Support more metadata standards** - Add support for additional audio metadata formats

## 📚 Best Practices

1. **Follow naming conventions** - Use `extract_*`, `analyze_*`, `detect_*` patterns
2. **Include comprehensive metadata** - Helps with plugin management
3. **Declare dependencies** - Ensures correct execution order
4. **Handle errors gracefully** - Prevents plugin failures from crashing the system
5. **Document your plugin** - Helps other developers understand its purpose

## 🎯 Benefits

- **Extensibility** - Add custom audio functionality without modifying core
- **Isolation** - Plugins run in their own context
- **Maintainability** - Easy to update and replace
- **Performance** - Integrates with parallel execution
- **Compatibility** - Works with all MetaExtract features

## 🔮 Future Enhancements

This plugin can be extended with:
- **Actual audio decoding** using libraries like librosa or pydub
- **Spectral analysis** for frequency content
- **Beat detection** and tempo analysis
- **Audio fingerprinting** for content identification
- **Speech recognition** integration
- **Machine learning** based content classification