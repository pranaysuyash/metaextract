#!/usr/bin/env python3
"""
Comprehensive metadata extraction using Python libraries.
Used as fallback/supplement to Node.js ExifTool extraction.
"""

import sys
import json
import hashlib
import os
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import mutagen
    from mutagen.easyid3 import EasyID3
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.mp4 import MP4
    from mutagen.oggvorbis import OggVorbis
    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False

try:
    from PyPDF2 import PdfReader
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False


def extract_image_metadata(filepath: str) -> dict:
    """Extract metadata from images using Pillow."""
    if not HAS_PIL:
        return {"error": "Pillow not installed"}
    
    result = {
        "source": "python_pillow",
        "basic": {},
        "exif": {},
        "gps": {},
        "icc_profile": {}
    }
    
    try:
        with Image.open(filepath) as img:
            result["basic"] = {
                "format": img.format,
                "mode": img.mode,
                "width": img.width,
                "height": img.height,
                "aspect_ratio": round(img.width / img.height, 4) if img.height > 0 else None,
                "megapixels": round((img.width * img.height) / 1_000_000, 2),
                "is_animated": getattr(img, "is_animated", False),
                "n_frames": getattr(img, "n_frames", 1),
            }
            
            exif_data = img._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8', errors='ignore')
                        except:
                            value = str(value)[:100] + "..."
                    
                    if tag == "GPSInfo":
                        gps_data = {}
                        for gps_tag_id, gps_value in value.items():
                            gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                            gps_data[str(gps_tag)] = str(gps_value)
                        result["gps"] = gps_data
                    else:
                        result["exif"][str(tag)] = str(value) if not isinstance(value, (int, float, bool)) else value
            
            if "icc_profile" in img.info:
                result["icc_profile"]["present"] = True
                result["icc_profile"]["size_bytes"] = len(img.info["icc_profile"])
                
    except Exception as e:
        result["error"] = str(e)
    
    return result


def extract_audio_metadata(filepath: str) -> dict:
    """Extract metadata from audio files using mutagen."""
    if not HAS_MUTAGEN:
        return {"error": "Mutagen not installed"}
    
    result = {
        "source": "python_mutagen",
        "basic": {},
        "tags": {},
        "technical": {}
    }
    
    try:
        audio = mutagen.File(filepath)
        if audio is None:
            return {"error": "Unsupported audio format"}
        
        result["basic"]["length_seconds"] = round(audio.info.length, 2) if hasattr(audio.info, 'length') else None
        result["basic"]["bitrate"] = getattr(audio.info, 'bitrate', None)
        result["basic"]["sample_rate"] = getattr(audio.info, 'sample_rate', None)
        result["basic"]["channels"] = getattr(audio.info, 'channels', None)
        
        if hasattr(audio.info, 'bits_per_sample'):
            result["technical"]["bits_per_sample"] = audio.info.bits_per_sample
        
        if isinstance(audio, MP3):
            result["technical"]["encoder"] = getattr(audio.info, 'encoder_info', None)
            result["technical"]["mode"] = str(audio.info.mode) if hasattr(audio.info, 'mode') else None
        
        if audio.tags:
            for key in audio.tags.keys():
                try:
                    value = audio.tags[key]
                    if isinstance(value, list):
                        value = [str(v) for v in value]
                    result["tags"][str(key)] = str(value) if not isinstance(value, (list, int, float)) else value
                except:
                    pass
                    
    except Exception as e:
        result["error"] = str(e)
    
    return result


def extract_pdf_metadata(filepath: str) -> dict:
    """Extract metadata from PDF files using PyPDF2."""
    if not HAS_PYPDF2:
        return {"error": "PyPDF2 not installed"}
    
    result = {
        "source": "python_pypdf2",
        "basic": {},
        "document_info": {},
        "security": {}
    }
    
    try:
        reader = PdfReader(filepath)
        
        result["basic"]["num_pages"] = len(reader.pages)
        result["basic"]["is_encrypted"] = reader.is_encrypted
        
        if reader.metadata:
            for key, value in reader.metadata.items():
                clean_key = key.replace("/", "")
                result["document_info"][clean_key] = str(value) if value else None
        
        result["security"]["is_encrypted"] = reader.is_encrypted
        
        if len(reader.pages) > 0:
            page = reader.pages[0]
            if page.mediabox:
                width = float(page.mediabox.width)
                height = float(page.mediabox.height)
                result["basic"]["page_width_points"] = width
                result["basic"]["page_height_points"] = height
                result["basic"]["page_width_inches"] = round(width / 72, 2)
                result["basic"]["page_height_inches"] = round(height / 72, 2)
                
    except Exception as e:
        result["error"] = str(e)
    
    return result


def compute_hashes(filepath: str) -> dict:
    """Compute file integrity hashes."""
    result = {}
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
            result["md5"] = hashlib.md5(data).hexdigest()
            result["sha256"] = hashlib.sha256(data).hexdigest()
            result["sha1"] = hashlib.sha1(data).hexdigest()
            result["file_size_bytes"] = len(data)
    except Exception as e:
        result["error"] = str(e)
    return result


def get_filesystem_metadata(filepath: str) -> dict:
    """Get filesystem metadata."""
    result = {}
    try:
        stat = os.stat(filepath)
        result["size_bytes"] = stat.st_size
        result["created_timestamp"] = stat.st_ctime
        result["modified_timestamp"] = stat.st_mtime
        result["accessed_timestamp"] = stat.st_atime
        result["created_iso"] = datetime.fromtimestamp(stat.st_ctime).isoformat()
        result["modified_iso"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        result["permissions_octal"] = oct(stat.st_mode)[-3:]
    except Exception as e:
        result["error"] = str(e)
    return result


def extract_all(filepath: str, mime_type: str = "") -> dict:
    """Main extraction function."""
    result = {
        "python_extraction": True,
        "libraries_available": {
            "pillow": HAS_PIL,
            "mutagen": HAS_MUTAGEN,
            "pypdf2": HAS_PYPDF2
        },
        "hashes": compute_hashes(filepath),
        "filesystem": get_filesystem_metadata(filepath)
    }
    
    if mime_type.startswith("image/") or filepath.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.tiff', '.bmp')):
        result["image"] = extract_image_metadata(filepath)
    
    if mime_type.startswith("audio/") or filepath.lower().endswith(('.mp3', '.flac', '.ogg', '.m4a', '.wav', '.aac')):
        result["audio"] = extract_audio_metadata(filepath)
    
    if mime_type == "application/pdf" or filepath.lower().endswith('.pdf'):
        result["pdf"] = extract_pdf_metadata(filepath)
    
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No file path provided"}))
        sys.exit(1)
    
    filepath = sys.argv[1]
    mime_type = sys.argv[2] if len(sys.argv) > 2 else ""
    
    if not os.path.exists(filepath):
        print(json.dumps({"error": f"File not found: {filepath}"}))
        sys.exit(1)
    
    result = extract_all(filepath, mime_type)
    print(json.dumps(result, default=str))
