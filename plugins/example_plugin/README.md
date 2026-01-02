# Example Plugin for MetaExtract

## 🌟 Overview

This is an **example plugin** that demonstrates how to create custom metadata extraction modules for MetaExtract. It shows the complete plugin structure, metadata declaration, and integration with the core system.

## 📁 Plugin Structure

```
example_plugin/
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

The plugin includes comprehensive metadata that helps with identification and management:

```python
# Static metadata
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "MetaExtract Team"
PLUGIN_DESCRIPTION = "Example plugin demonstrating custom metadata extraction"
PLUGIN_LICENSE = "MIT"

# Dynamic metadata function
def get_plugin_metadata():
    return {
        "version": PLUGIN_VERSION,
        "author": PLUGIN_AUTHOR,
        "description": PLUGIN_DESCRIPTION,
        "license": PLUGIN_LICENSE,
        "website": "https://metaextract.com",
        "documentation": "https://metaextract.com/docs/plugins"
    }
```

## 🔧 Extraction Functions

The plugin provides three extraction functions that follow the MetaExtract pattern:

### 1. `extract_example_metadata()`

Extracts basic metadata with custom fields:
- File information (size, extension, name)
- Processing timestamp
- Plugin version
- Custom metadata fields
- File type detection

### 2. `analyze_example_content()`

Performs content analysis:
- Content hash calculation
- Content type detection
- Complexity and quality scores

### 3. `detect_example_features()`

Detects special features:
- Test file detection
- Example file detection
- Custom feature flags

## 🔗 Dependencies

The plugin can declare dependencies on other modules:

```python
MODULE_DEPENDENCIES = ["base_metadata"]
```

This ensures the plugin runs **after** its dependencies, maintaining correct execution order.

## 📊 Integration

Once loaded, the plugin integrates seamlessly with MetaExtract:

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

# Extract metadata (includes plugin results)
result = extractor.extract_comprehensive_metadata("test.jpg", "super")

# Access plugin results
plugin_data = result.get("example_plugin", {})
print(f"Plugin processed: {plugin_data.get('processed')}")
print(f"File type: {plugin_data.get('file_type')}")
```

## 📈 Expected Output

When processing a file, the plugin adds metadata like:

```json
{
  "example_plugin": {
    "processed": true,
    "timestamp": 1712345678.9,
    "file_size": 1024,
    "file_extension": ".jpg",
    "file_name": "test.jpg",
    "plugin_version": "1.0.0",
    "processing_time_ms": 10.5,
    "custom_field": "This is custom metadata from the example plugin!",
    "file_type": "image",
    "image_specific": true
  },
  "example_analysis": {
    "content_hash": "d41d8cd98f00b204e9800998ecf8427e",
    "content_type": "image",
    "complexity_score": 0.5,
    "quality_score": 0.8
  },
  "example_features": {
    "has_metadata": true,
    "has_custom_data": true,
    "is_processed": true,
    "plugin_compatible": true,
    "is_test_file": false,
    "is_example": true
  }
}
```

## 🔧 Customization

To create your own plugin:

1. **Copy this structure** to a new directory
2. **Modify the functions** with your custom logic
3. **Update metadata** with your plugin information
4. **Add dependencies** if needed
5. **Place in plugin directory**

## 📚 Best Practices

1. **Follow naming conventions** - Use `extract_*`, `analyze_*`, `detect_*` patterns
2. **Include comprehensive metadata** - Helps with plugin management
3. **Declare dependencies** - Ensures correct execution order
4. **Handle errors gracefully** - Prevents plugin failures from crashing the system
5. **Document your plugin** - Helps other developers understand its purpose

## 🎯 Benefits

- **Extensibility** - Add custom functionality without modifying core
- **Isolation** - Plugins run in their own context
- **Maintainability** - Easy to update and replace
- **Performance** - Integrates with parallel execution
- **Compatibility** - Works with all MetaExtract features

## 🔮 Future Enhancements

This example plugin can be extended with:
- **Machine learning** analysis
- **Computer vision** processing
- **Natural language** understanding
- **Custom file formats** support
- **Advanced metadata** extraction

The plugin system provides a **powerful foundation** for extending MetaExtract's capabilities!