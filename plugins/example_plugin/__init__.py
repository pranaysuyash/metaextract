# Example Plugin for MetaExtract
# This demonstrates the plugin system capabilities

"""
Example Plugin - Demonstrates MetaExtract plugin system

This plugin shows how to create custom metadata extraction modules
that integrate seamlessly with the MetaExtract system.
"""

# Plugin metadata
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "MetaExtract Team"
PLUGIN_DESCRIPTION = "Example plugin demonstrating custom metadata extraction"
PLUGIN_LICENSE = "MIT"

# Optional: You can also use a function to provide dynamic metadata
def get_plugin_metadata():
    return {
        "version": PLUGIN_VERSION,
        "author": PLUGIN_AUTHOR,
        "description": PLUGIN_DESCRIPTION,
        "license": PLUGIN_LICENSE,
        "website": "https://metaextract.com",
        "documentation": "https://metaextract.com/docs/plugins"
    }


def extract_example_metadata(filepath: str) -> dict:
    """
    Extract example metadata from a file.
    
    This function demonstrates how to create a custom extraction function
    that follows the MetaExtract pattern.
    
    Args:
        filepath: Path to the file being processed
        
    Returns:
        Dictionary containing extracted metadata
    """
    import os
    import time
    from pathlib import Path
    
    # Get basic file information
    file_path = Path(filepath)
    
    # Extract metadata
    metadata = {
        "example_plugin": {
            "processed": True,
            "timestamp": time.time(),
            "file_size": os.path.getsize(filepath),
            "file_extension": file_path.suffix,
            "file_name": file_path.name,
            "plugin_version": PLUGIN_VERSION,
            "processing_time_ms": 10.5,
            "custom_field": "This is custom metadata from the example plugin!"
        }
    }
    
    # Add some conditional metadata based on file type
    if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
        metadata["example_plugin"]["file_type"] = "image"
        metadata["example_plugin"]["image_specific"] = True
    elif file_path.suffix.lower() in ['.mp4', '.mov', '.avi']:
        metadata["example_plugin"]["file_type"] = "video"
        metadata["example_plugin"]["video_specific"] = True
    else:
        metadata["example_plugin"]["file_type"] = "other"
        metadata["example_plugin"]["other_specific"] = True
    
    return metadata


def analyze_example_content(filepath: str) -> dict:
    """
    Analyze file content with example analysis.
    
    This demonstrates a more complex analysis function that could
    perform advanced processing on files.
    
    Args:
        filepath: Path to the file being processed
        
    Returns:
        Dictionary containing analysis results
    """
    import hashlib
    from pathlib import Path
    
    file_path = Path(filepath)
    
    # Simple content analysis
    analysis = {
        "example_analysis": {
            "content_hash": "",
            "content_type": "unknown",
            "complexity_score": 0.5,
            "quality_score": 0.8
        }
    }
    
    # Calculate a simple hash of the file content
    try:
        with open(filepath, 'rb') as f:
            content = f.read(1024)  # Read first 1KB for demo
            hash_object = hashlib.md5(content)
            analysis["example_analysis"]["content_hash"] = hash_object.hexdigest()
    except Exception as e:
        analysis["example_analysis"]["content_hash"] = f"error: {str(e)}"
    
    # Determine content type based on extension
    if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
        analysis["example_analysis"]["content_type"] = "image"
    elif file_path.suffix.lower() in ['.mp4', '.mov', '.avi', '.mkv']:
        analysis["example_analysis"]["content_type"] = "video"
    elif file_path.suffix.lower() in ['.mp3', '.wav', '.aac', '.flac']:
        analysis["example_analysis"]["content_type"] = "audio"
    elif file_path.suffix.lower() in ['.txt', '.md', '.json', '.xml']:
        analysis["example_analysis"]["content_type"] = "text"
    else:
        analysis["example_analysis"]["content_type"] = "binary"
    
    return analysis


def detect_example_features(filepath: str) -> dict:
    """
    Detect special features in files.
    
    This demonstrates a detection function that could identify
    specific patterns or features in files.
    
    Args:
        filepath: Path to the file being processed
        
    Returns:
        Dictionary containing detected features
    """
    from pathlib import Path
    
    file_path = Path(filepath)
    
    features = {
        "example_features": {
            "has_metadata": True,
            "has_custom_data": True,
            "is_processed": True,
            "plugin_compatible": True
        }
    }
    
    # Add some feature detection based on file name
    if "test" in file_path.name.lower():
        features["example_features"]["is_test_file"] = True
    else:
        features["example_features"]["is_test_file"] = False
    
    if "example" in file_path.name.lower():
        features["example_features"]["is_example"] = True
    else:
        features["example_features"]["is_example"] = False
    
    return features


# Optional: You can declare dependencies on other modules
# This ensures your plugin runs after its dependencies
MODULE_DEPENDENCIES = ["base_metadata"]  # Depends on base metadata module