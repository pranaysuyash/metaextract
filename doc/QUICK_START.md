# 🚀 MetaExtract Plugin System - Quick Start Guide

## 🎯 Get Started in 5 Minutes

This guide will help you get the MetaExtract Plugin System up and running quickly.

## 📋 Prerequisites

- Python 3.8+
- MetaExtract installed
- Basic Python knowledge

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/metaextract.git
cd metaextract
```

### 2. Set Up Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 🚀 Using the Plugin System

### 1. List Available Plugins

```bash
python scripts/manage_plugins.py list
```

### 2. Test a Plugin

```bash
python scripts/manage_plugins.py test audio_analysis_plugin test.mp3
```

### 3. Extract Metadata with Plugins

```python
from server.extractor.comprehensive_metadata_engine import ComprehensiveMetadataExtractor

# Create extractor (automatically loads plugins)
extractor = ComprehensiveMetadataExtractor()

# Extract metadata (includes all plugin results)
result = extractor.extract_comprehensive_metadata("test.mp3", "super")

# Access plugin results
audio_data = result.get("audio_analysis", {})
print(f"Audio format: {audio_data.get('audio_format')}")
```

## 📚 Learning Resources

### Documentation
- `docs/PLUGIN_DEVELOPMENT_GUIDE.md` - Complete development guide
- `docs/PLUGIN_API.md` - API reference
- `PLUGINS_SUMMARY.md` - Plugin overview

### Examples
- `plugins/example_plugin/` - Reference implementation
- `tests/test_audio_plugin.py` - Test examples

## 🛠️ Creating Your First Plugin

```bash
# Create plugin skeleton
python scripts/manage_plugins.py create my_plugin --author "Your Name" --description "My custom plugin"

# Edit the plugin
# plugins/my_plugin/__init__.py

# Test your plugin
python scripts/manage_plugins.py test my_plugin test_file.ext
```

## 🎯 Common Tasks

### Enable/Disable Plugins

```bash
# Enable a plugin
python scripts/manage_plugins.py enable audio_analysis_plugin

# Disable a plugin
python scripts/manage_plugins.py disable audio_analysis_plugin
```

### Reload Plugins

```bash
# Reload a plugin (useful during development)
python scripts/manage_plugins.py reload audio_analysis_plugin
```

### Check Plugin Stats

```bash
# Show plugin statistics
python scripts/manage_plugins.py stats
```

## 🐛 Troubleshooting

### Plugin Not Found

```bash
# Ensure plugin is in plugins/ directory
# Check __init__.py exists
# Verify plugin follows naming conventions
```

### Plugin Loads But Functions Don't Work

```bash
# Check function signatures
# Verify functions return dictionaries
# Ensure all required fields are present
```

### Dependency Issues

```bash
# Check MODULE_DEPENDENCIES are correct
# Ensure dependencies are available
# Verify dependency order
```

## 📈 Performance Tips

- **Use appropriate test files** for each plugin type
- **Test functions individually** before integration
- **Monitor memory usage** with large files
- **Optimize file I/O** operations

## 🎉 Next Steps

1. **Explore existing plugins** - Try audio, video, image, document plugins
2. **Create your own plugins** - Extend functionality for your needs
3. **Contribute plugins** - Share with the community
4. **Report issues** - Help improve the system

## 📚 Additional Resources

- **Plugin Development Guide**: Complete guide in `docs/`
- **API Documentation**: Detailed API reference
- **Source Code**: Study existing plugins for inspiration
- **Community**: Join MetaExtract developer community

**You're now ready to use the MetaExtract Plugin System! 🎉**

---

*Need help? Check the documentation or ask the community.*

*Found an issue? Report it to help improve the system.*

*Want to contribute? Create plugins and share with others.*