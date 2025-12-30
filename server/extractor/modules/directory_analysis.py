"""
Directory and Batch Analysis
Statistics and smart change detection for directories of media files
"""

import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import json


SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.heic', '.heif', '.raw', '.cr2', '.nef', '.arw', '.dng'}
SUPPORTED_VIDEO_FORMATS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.wmv', '.flv', '.m4v', '.3gp'}
SUPPORTED_AUDIO_FORMATS = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac', '.wma', '.aiff'}
SUPPORTED_FORMATS = SUPPORTED_IMAGE_FORMATS | SUPPORTED_VIDEO_FORMATS | SUPPORTED_AUDIO_FORMATS


def scan_directory(
    directory: str,
    recursive: bool = True,
    max_files: int = 10000
) -> Dict[str, Any]:
    """
    Scan a directory and collect statistics about media files.
    
    Args:
        directory: Path to directory
        recursive: Whether to scan subdirectories
        max_files: Maximum files to process
    
    Returns:
        Dictionary with directory statistics
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")
    
    result = {
        "directory": str(dir_path.absolute()),
        "scan_time": datetime.now().isoformat(),
        "recursive": recursive,
        "summary": {
            "total_files": 0,
            "total_size_bytes": 0,
            "by_format": {},
            "by_type": {"image": 0, "video": 0, "audio": 0, "other": 0}
        },
        "format_details": [],
        "oldest_file": None,
        "newest_file": None,
        "errors": []
    }
    
    files_data = []
    
    pattern = "**/*" if recursive else "*"
    
    file_count = 0
    for file_path in dir_path.glob(pattern):
        if file_count >= max_files:
            break
        
        if file_path.is_file():
            ext = file_path.suffix.lower()
            
            if ext not in SUPPORTED_FORMATS:
                continue
            
            try:
                stat = file_path.stat()
                file_type = categorize_format(ext)
                
                file_info = {
                    "path": str(file_path.absolute()),
                    "name": file_path.name,
                    "format": ext,
                    "type": file_type,
                    "size_bytes": stat.st_size,
                    "modified": stat.st_mtime
                }
                
                files_data.append(file_info)
                file_count += 1
                
            except Exception as e:
                result["errors"].append({
                    "file": str(file_path),
                    "error": str(e)
                })
    
    for f in files_data:
        result["summary"]["total_files"] += 1
        result["summary"]["total_size_bytes"] += f["size_bytes"]
        
        fmt = f["format"]
        if fmt not in result["summary"]["by_format"]:
            result["summary"]["by_format"][fmt] = {"count": 0, "size_bytes": 0}
        result["summary"]["by_format"][fmt]["count"] += 1
        result["summary"]["by_format"][fmt]["size_bytes"] += f["size_bytes"]
        
        result["summary"]["by_type"][f["type"]] += 1
    
    if files_data:
        oldest = min(files_data, key=lambda x: x["modified"])
        newest = max(files_data, key=lambda x: x["modified"])
        
        result["oldest_file"] = {
            "path": oldest["path"],
            "modified": datetime.fromtimestamp(oldest["modified"]).isoformat(),
            "age_days": (datetime.now() - datetime.fromtimestamp(oldest["modified"])).days
        }
        
        result["newest_file"] = {
            "path": newest["path"],
            "modified": datetime.fromtimestamp(newest["modified"]).isoformat()
        }
    
    for fmt, data in result["summary"]["by_format"].items():
        result["format_details"].append({
            "format": fmt,
            "count": data["count"],
            "size_bytes": data["size_bytes"],
            "size_human": format_bytes(data["size_bytes"])
        })
    
    result["summary"]["size_human"] = format_bytes(result["summary"]["total_size_bytes"])
    
    return result


def categorize_format(ext: str) -> str:
    """Categorize file format by type."""
    if ext in SUPPORTED_IMAGE_FORMATS:
        return "image"
    elif ext in SUPPORTED_VIDEO_FORMATS:
        return "video"
    elif ext in SUPPORTED_AUDIO_FORMATS:
        return "audio"
    else:
        return "other"


def format_bytes(size_bytes: float) -> str:
    """Format bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def detect_changes(
    directory: str,
    previous_state: Optional[Dict[str, Any]] = None,
    recursive: bool = True
) -> Dict[str, Any]:
    """
    Detect changes in a directory compared to a previous state.
    
    Args:
        directory: Path to directory
        previous_state: Previous scan result to compare against
        recursive: Whether to scan subdirectories
    
    Returns:
        Dictionary with change detection results
    """
    current_state = scan_directory(directory, recursive=recursive)
    
    if not previous_state:
        return {
            "directory": directory,
            "change_type": "initial_scan",
            "current_state": current_state,
            "added": current_state["summary"]["total_files"],
            "removed": 0,
            "modified": 0,
            "unchanged": 0,
            "changed_files": []
        }
    
    current_files = {f["path"]: f for f in current_state.get("format_details", [])}
    
    previous_files = {}
    if isinstance(previous_state.get("format_details"), list):
        for f in previous_state["format_details"]:
            previous_files[f["path"]] = f
    
    added = []
    removed = []
    modified = []
    
    current_paths = set(current_files.keys())
    previous_paths = set(previous_files.keys())
    
    for path in current_paths - previous_paths:
        added.append(current_files[path])
    
    for path in previous_paths - current_paths:
        removed.append(previous_files[path])
    
    for path in current_paths & previous_paths:
        current = current_files[path]
        previous = previous_files[path]
        
        if current.get("size_bytes") != previous.get("size_bytes"):
            modified.append({
                "path": path,
                "previous_size": previous.get("size_bytes"),
                "current_size": current.get("size_bytes"),
                "size_change": current.get("size_bytes", 0) - previous.get("size_bytes", 0)
            })
    
    result = {
        "directory": directory,
        "scan_time": datetime.now().isoformat(),
        "change_type": "incremental",
        "previous_scan": previous_state.get("scan_time"),
        "added_count": len(added),
        "removed_count": len(removed),
        "modified_count": len(modified),
        "unchanged_count": current_state["summary"]["total_files"] - len(modified),
        "added": added[:100],
        "removed": removed[:100],
        "modified": modified[:100]
    }
    
    return result


def get_directory_field_count() -> int:
    """Return approximate number of directory analysis fields."""
    return 30


def get_directory_stats() -> Dict[str, Any]:
    """Return directory analysis helper info."""
    return {
        "supported_image_formats": sorted(SUPPORTED_IMAGE_FORMATS),
        "supported_video_formats": sorted(SUPPORTED_VIDEO_FORMATS),
        "supported_audio_formats": sorted(SUPPORTED_AUDIO_FORMATS),
        "total_supported_formats": len(SUPPORTED_FORMATS)
    }


def batch_extract_preview(
    directory: str,
    output_dir: Optional[str] = None,
    recursive: bool = True,
    max_files: int = 100
) -> Dict[str, Any]:
    """
    Generate preview thumbnails for files in a directory.
    
    Args:
        directory: Path to directory
        output_dir: Output directory for previews
        recursive: Whether to process subdirectories
        max_files: Maximum files to process
    
    Returns:
        Dictionary with preview generation results
    """
    try:
        from .perceptual_hashes import generate_thumbnail
    except ImportError:
        generate_thumbnail = None

    dir_path = Path(directory)
    output_path = Path(output_dir) if output_dir else dir_path / "previews"

    results = {
        "directory": str(dir_path.absolute()),
        "output_directory": str(output_path.absolute()),
        "processed": 0,
        "successful": 0,
        "failed": 0,
        "previews": []
    }

    if generate_thumbnail is None:
        results["error"] = "perceptual_hashes module not available"
        return results
    
    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        results["error"] = f"Failed to create output directory: {str(e)}"
        return results
    
    pattern = "**/*" if recursive else "*"
    
    for file_path in dir_path.glob(pattern):
        if results["processed"] >= max_files:
            break
        
        if not file_path.is_file():
            continue
        
        ext = file_path.suffix.lower()
        if ext not in SUPPORTED_IMAGE_FORMATS:
            continue
        
        try:
            thumbnail = generate_thumbnail(str(file_path), (256, 256))
            
            if thumbnail:
                output_file = output_path / f"{file_path.stem}_preview.jpg"
                
                with open(output_file, 'wb') as f:
                    f.write(thumbnail)
                
                results["successful"] += 1
                results["previews"].append({
                    "input": str(file_path.absolute()),
                    "output": str(output_file.absolute()),
                    "size_bytes": len(thumbnail)
                })
            else:
                results["failed"] += 1
                
        except Exception as e:
            results["failed"] += 1
            results.setdefault("errors", []).append({
                "file": str(file_path),
                "error": str(e)
            })
        
        results["processed"] += 1
    
    return results
