# Example Plugin for MetaExtract
# Enhanced with comprehensive error handling and health monitoring

"""
Example Plugin - Demonstrates Enhanced MetaExtract Plugin System

This plugin shows how to create robust, production-ready metadata extraction modules
with comprehensive error handling, health monitoring, and integration with the
MetaExtract system.
"""

# Plugin metadata
PLUGIN_VERSION = "2.0.0"
PLUGIN_AUTHOR = "MetaExtract Team"
PLUGIN_DESCRIPTION = "Enhanced example plugin with comprehensive error handling and health monitoring"
PLUGIN_LICENSE = "MIT"
PLUGIN_REQUIRED_LIBRARIES = ["hashlib"]  # Optional: List required libraries
PLUGIN_COMPATIBILITY = "metaextract>=4.0.0"  # Optional: Compatibility information

# Optional: Enhanced metadata function with error handling
def get_plugin_metadata():
    try:
        return {
            "version": PLUGIN_VERSION,
            "author": PLUGIN_AUTHOR,
            "description": PLUGIN_DESCRIPTION,
            "license": PLUGIN_LICENSE,
            "website": "https://metaextract.com",
            "documentation": "https://metaextract.com/docs/plugins",
            "required_libraries": PLUGIN_REQUIRED_LIBRARIES,
            "compatibility": PLUGIN_COMPATIBILITY,
            "health_status": "healthy",
            "last_updated": "2024-01-06",
            "features": [
                "comprehensive_error_handling",
                "health_monitoring_integration",
                "file_analysis",
                "content_detection",
                "feature_extraction"
            ]
        }
    except Exception as e:
        # Fallback metadata if something goes wrong
        return {
            "version": PLUGIN_VERSION,
            "author": PLUGIN_AUTHOR,
            "description": PLUGIN_DESCRIPTION,
            "license": PLUGIN_LICENSE,
            "status": "degraded",
            "error": str(e)
        }


def extract_example_metadata(filepath: str) -> dict:
    """
    Extract example metadata from a file with comprehensive error handling.
    
    This function demonstrates how to create a robust, production-ready extraction function
    with proper error handling, validation, and integration with the MetaExtract system.
    
    Args:
        filepath: Path to the file being processed
        
    Returns:
        Dictionary containing extracted metadata
        
    Raises:
        FileNotFoundError: If file does not exist
        PermissionError: If file cannot be accessed
        ValueError: If file is invalid or corrupted
    """
    import os
    import time
    from pathlib import Path
    import traceback
    
    # Start timing for performance monitoring
    start_time = time.time()
    
    try:
        # Validate file existence and accessibility
        file_path = Path(filepath)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {filepath}")
        
        if not os.access(filepath, os.R_OK):
            raise PermissionError(f"No read permission for file: {filepath}")
        
        # Get file statistics
        try:
            file_size = os.path.getsize(filepath)
            file_modified = os.path.getmtime(filepath)
            file_created = os.path.getctime(filepath)
        except OSError as e:
            raise ValueError(f"Cannot access file statistics: {str(e)}")
        
        # Extract metadata with comprehensive error handling
        metadata = {
            "example_plugin": {
                "processed": True,
                "timestamp": time.time(),
                "file_size": file_size,
                "file_extension": file_path.suffix,
                "file_name": file_path.name,
                "plugin_version": PLUGIN_VERSION,
                "processing_time_ms": 10.5,
                "custom_field": "This is custom metadata from the enhanced example plugin!",
                "file_statistics": {
                    "modified_time": file_modified,
                    "created_time": file_created,
                    "access_time": os.path.getatime(filepath)
                },
                "health_status": "healthy",
                "error_count": 0
            }
        }
        
        # Add enhanced conditional metadata based on file type
        file_type = file_path.suffix.lower()
        
        if file_type in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
            metadata["example_plugin"]["file_type"] = "image"
            metadata["example_plugin"]["image_specific"] = True
            metadata["example_plugin"]["content_category"] = "visual"
            
        elif file_type in ['.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv']:
            metadata["example_plugin"]["file_type"] = "video"
            metadata["example_plugin"]["video_specific"] = True
            metadata["example_plugin"]["content_category"] = "motion"
            
        elif file_type in ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a']:
            metadata["example_plugin"]["file_type"] = "audio"
            metadata["example_plugin"]["audio_specific"] = True
            metadata["example_plugin"]["content_category"] = "sound"
            
        elif file_type in ['.txt', '.md', '.json', '.xml', '.html', '.htm', '.csv']:
            metadata["example_plugin"]["file_type"] = "text"
            metadata["example_plugin"]["text_specific"] = True
            metadata["example_plugin"]["content_category"] = "document"
            
        elif file_type in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
            metadata["example_plugin"]["file_type"] = "document"
            metadata["example_plugin"]["document_specific"] = True
            metadata["example_plugin"]["content_category"] = "office"
            
        else:
            metadata["example_plugin"]["file_type"] = "other"
            metadata["example_plugin"]["other_specific"] = True
            metadata["example_plugin"]["content_category"] = "unknown"
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        metadata["example_plugin"]["processing_time_ms"] = round(processing_time, 2)
        
        return metadata
        
    except FileNotFoundError as e:
        # Return error metadata for file not found
        return {
            "example_plugin": {
                "processed": False,
                "timestamp": time.time(),
                "error": str(e),
                "error_type": "file_not_found",
                "error_code": "PLUGIN_FILE_NOT_FOUND",
                "severity": "high",
                "suggested_action": "Verify file path and existence",
                "file_path": str(filepath),
                "health_status": "unhealthy",
                "error_count": 1
            }
        }
        
    except PermissionError as e:
        # Return error metadata for permission issues
        return {
            "example_plugin": {
                "processed": False,
                "timestamp": time.time(),
                "error": str(e),
                "error_type": "permission_denied",
                "error_code": "PLUGIN_PERMISSION_DENIED",
                "severity": "high",
                "suggested_action": "Check file permissions and access rights",
                "file_path": str(filepath),
                "health_status": "unhealthy",
                "error_count": 1
            }
        }
        
    except ValueError as e:
        # Return error metadata for validation issues
        return {
            "example_plugin": {
                "processed": False,
                "timestamp": time.time(),
                "error": str(e),
                "error_type": "validation_error",
                "error_code": "PLUGIN_VALIDATION_ERROR",
                "severity": "medium",
                "suggested_action": "Verify file integrity and format",
                "file_path": str(filepath),
                "health_status": "unhealthy",
                "error_count": 1
            }
        }
        
    except Exception as e:
        # Return error metadata for unexpected errors
        return {
            "example_plugin": {
                "processed": False,
                "timestamp": time.time(),
                "error": str(e),
                "error_type": "unexpected_error",
                "error_code": "PLUGIN_UNEXPECTED_ERROR",
                "severity": "critical",
                "suggested_action": "Check plugin logs and report to support",
                "file_path": str(filepath),
                "stack_trace": traceback.format_exc(),
                "health_status": "unhealthy",
                "error_count": 1
            }
        }


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